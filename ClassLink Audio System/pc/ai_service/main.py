import asyncio
import socket
import struct
import logging
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from ai_assistant import AITeachingAssistant
from document_processor import DocumentProcessor
from tts_service import TTSService
import os
import wave
import io
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """
    Main AI Service that listens for AI-mode audio packets,
    processes questions, and sends responses back.
    """
    
    def __init__(self, listen_port: int = 12346, max_concurrent: int = 6):
        """
        Initialize AI Service.
        
        Args:
            listen_port: UDP port to listen for AI requests
            max_concurrent: Maximum concurrent AI requests (default 6)
        """
        self.listen_port = listen_port
        self.max_concurrent = max_concurrent
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
        # AI components
        self.ai_assistant = AITeachingAssistant()
        self.tts_service = TTSService()
        self.recognizer = sr.Recognizer()
        
        # Socket for receiving audio
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", listen_port))
        
        # Audio buffer per device
        self.audio_buffers = {}
        
        # Active requests tracking
        self.active_requests = {}  # {device_id: task}
        
        logger.info(f"AI Service listening on port {listen_port}")
        logger.info(f"Max concurrent requests: {max_concurrent}")
    
    async def process_audio_packet(self, data: bytes, addr: tuple):
        """
        Process incoming audio packet.
        
        Packet format:
        [1 byte flags][4 bytes sequence][N bytes audio]
        """
        if len(data) < 5:
            return
        
        flags = data[0]
        ai_mode = (flags & 0x01) != 0
        
        if not ai_mode:
            return  # Not an AI request
        
        sequence = struct.unpack('<I', data[1:5])[0]
        audio_data = data[5:]
        
        device_id = f"{addr[0]}:{addr[1]}"
        
        # Buffer audio until we detect silence/end
        if device_id not in self.audio_buffers:
            self.audio_buffers[device_id] = bytearray()
        
        self.audio_buffers[device_id].extend(audio_data)
        
        # Simple end detection: if buffer > 3 seconds worth of audio (16kHz * 2 bytes * 3s)
        if len(self.audio_buffers[device_id]) > 96000:
            # Check if we're at capacity
            if len(self.active_requests) >= self.max_concurrent:
                logger.warning(f"At capacity ({self.max_concurrent}), student {device_id} must wait")
                # Send "please wait" message
                await self.send_response(addr, "He thong dang ban. Xin cho 10s", None)
                self.audio_buffers[device_id] = bytearray()
                return
            
            # Process in parallel (non-blocking)
            audio_copy = bytes(self.audio_buffers[device_id])
            self.audio_buffers[device_id] = bytearray()
            
            # Create async task
            task = asyncio.create_task(self.process_question(device_id, audio_copy, addr))
            self.active_requests[device_id] = task
            
            # Cleanup task when done
            task.add_done_callback(lambda t: self.active_requests.pop(device_id, None))
    
    async def process_question(self, device_id: str, audio_bytes: bytes, addr: tuple):
        """
        Process complete question audio (runs in parallel).
        
        Args:
            device_id: Device identifier
            audio_bytes: Raw PCM audio (16kHz, 16-bit, mono)
            addr: Device address for sending response
        """
        start_time = time.time()
        logger.info(f"[{device_id}] Processing AI question (active: {len(self.active_requests)}/{self.max_concurrent})")
        
        try:
            # Convert raw PCM to WAV for speech recognition
            wav_data = self.pcm_to_wav(audio_bytes, sample_rate=16000, channels=1, sample_width=2)
            
            # STT: Audio -> Text (run in executor to avoid blocking)
            loop = asyncio.get_event_loop()
            audio_source = sr.AudioFile(io.BytesIO(wav_data))
            with audio_source as source:
                audio = self.recognizer.record(source)
            
            # Run Google STT in executor thread (blocking operation)
            question_text = await loop.run_in_executor(
                self.executor,
                self.recognizer.recognize_google,
                audio,
                'vi-VN'
            )
            logger.info(f"[{device_id}] Question: {question_text}")
            
            # Ask AI (run in executor thread - Gemini API is blocking)
            answer_text = await loop.run_in_executor(
                self.executor,
                self.ai_assistant.ask_question,
                question_text,
                device_id
            )
            logger.info(f"[{device_id}] Answer: {answer_text}")
            
            # TTS: Text -> Audio (run in executor thread)
            audio_file = await loop.run_in_executor(
                self.executor,
                self.tts_service.text_to_speech,
                answer_text,
                f"{device_id.replace(':', '_')}_response.mp3"
            )
            
            # Send response back to device
            await self.send_response(addr, answer_text, audio_file)
            
            elapsed = time.time() - start_time
            logger.info(f"[{device_id}] Completed in {elapsed:.2f}s")
            
        except sr.UnknownValueError:
            logger.warning(f"[{device_id}] Could not understand audio")
            await self.send_response(addr, "Xin loi, em noi lai duoc khong?", None)
        except Exception as e:
            logger.error(f"[{device_id}] Error processing question: {e}")
            await self.send_response(addr, "Xin loi, co loi xay ra", None)
    
    async def send_response(self, addr: tuple, text: str, audio_file: str = None):
        """
        Send AI response back to device.
        
        Args:
            addr: Device address
            text: Response text (for OLED display)
            audio_file: Path to audio file (optional)
        """
        # TODO: Implement response protocol
        # For now, just log
        logger.info(f"Sending response to {addr}: {text}")
        
        # Response packet format (to be implemented):
        # [1 byte type=AI_RESPONSE][N bytes text]
        # Followed by audio packets if available
    
    @staticmethod
    def pcm_to_wav(pcm_data: bytes, sample_rate: int, channels: int, sample_width: int) -> bytes:
        """Convert raw PCM to WAV format."""
        output = io.BytesIO()
        with wave.open(output, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        return output.getvalue()
    
    async def run(self):
        """Main service loop."""
        logger.info("AI service started. Waiting for requests...")
        
        while True:
            try:
                data, addr = await asyncio.get_event_loop().run_in_executor(
                    None, self.sock.recvfrom, 2048
                )
                await self.process_audio_packet(data, addr)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
    
    def load_document(self, file_path: str):
        """Load lecture document."""
        content = DocumentProcessor.extract_text(file_path)
        if content:
            self.ai_assistant.load_lecture(content)
            logger.info(f"Loaded document: {file_path}")
        else:
            logger.error(f"Failed to load document: {file_path}")


async def main():
    """Entry point."""
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set!")
        logger.info("Get your free API key at: https://makersuite.google.com/app/apikey")
        return
    
    service = AIService(listen_port=12346)
    
    # Auto-load any documents in /data/lectures/ if exists
    lectures_dir = "data/lectures"
    if os.path.exists(lectures_dir):
        for filename in os.listdir(lectures_dir):
            if filename.endswith(('.pdf', '.docx', '.txt')):
                service.load_document(os.path.join(lectures_dir, filename))
    
    # Run service
    await service.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AI Service stopped by user")
    finally:
        # Cleanup executor
        logger.info("Shutting down thread pool...")
