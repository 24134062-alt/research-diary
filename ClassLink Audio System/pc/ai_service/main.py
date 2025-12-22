import asyncio
import socket
import struct
import logging
import json
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from ai_assistant import AITeachingAssistant
from document_processor import DocumentProcessor
import os
import wave
import io
import time
import paho.mqtt.client as mqtt
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        """
        self.listen_port = listen_port
        self.max_concurrent = max_concurrent
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        
        # AI components
        self.ai_assistant = AITeachingAssistant()
        self.recognizer = sr.Recognizer()
        
        # Socket for receiving audio
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", listen_port))
        
        # Audio buffer per device
        self.audio_buffers = {}
        
        # Active requests tracking
        self.active_requests = {}  # {device_id: task}
        
        # Subject Mode (Default: Math/Science)
        self.current_subject = "math" 
        
        # MQTT Client for Teacher Controls
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # Read MQTT settings from .env file
        mqtt_host = os.getenv("MQTT_HOST", "localhost")
        mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
        
        try:
            logger.info(f"Connecting to MQTT Broker at {mqtt_host}:{mqtt_port}")
            self.mqtt_client.connect(mqtt_host, mqtt_port, 60)
            self.mqtt_client.loop_start()
            logger.info(f"Connected to MQTT Broker at {mqtt_host}:{mqtt_port}")
        except Exception as e:
            logger.warning(f"MQTT Connection failed: {e}")
        
        logger.info(f"AI Service listening on port {listen_port}")
        logger.info(f"Max concurrent requests: {max_concurrent}")

    def on_mqtt_connect(self, client, userdata, flags, rc):
        logger.info("Subscribing to teacher/subject and teacher/chat/request")
        client.subscribe("teacher/subject")
        client.subscribe("teacher/chat/request")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            if msg.topic == "teacher/subject":
                self.current_subject = msg.payload.decode()
                logger.info(f"📚 SUBJECT MODE CHANGED TO: {self.current_subject.upper()}")
            
            elif msg.topic == "teacher/chat/request":
                # Handle Teacher Chat
                data = json.loads(msg.payload.decode())
                text = data.get("text", "")
                if text:
                    asyncio.run_coroutine_threadsafe(self.process_teacher_chat(text), asyncio.get_event_loop())

        except Exception as e:
            logger.error(f"MQTT Message Error: {e}")

    async def process_teacher_chat(self, text: str):
        """Process text from Teacher Chatbot"""
        logger.info(f"[TEACHER] Chat Request: {text}")
        
        # Ask AI
        loop = asyncio.get_event_loop()
        answer_data = await loop.run_in_executor(
            self.executor,
            self.ai_assistant.ask_question_with_visual,
            text, # Teacher text
            "TEACHER"
        )
        
        # Send response back to MQTT
        response = {
            "text": answer_data['text'],
            "visual": answer_data['visual_param'] if answer_data['has_visual'] else None
        }
        self.mqtt_client.publish("teacher/chat/response", json.dumps(response))

    def normalize_text_by_mode(self, text: str) -> str:
        """
        Normalize text based on current subject mode.
        """
        if self.current_subject == "math":  # Consolidating 'science' under 'math' key for now or renaming? User said "môn toán... lý hóa"
            return self.format_for_science(text)
        elif self.current_subject == "literature": # mapping 'social' to 'literature' key
            return self.format_for_social(text)
        return text

    def format_for_science(self, text: str) -> str:
        """
        Format for Logic/Calculation subjects (Math, Phy, Chem, Geo-Calc).
        "ba cộng hai" -> "3 + 2"
        """
        text = text.lower()
        
        # 1. Basic Math Map
        math_map = {
            'cộng': '+', 'trừ': '-', 'nhân': '*', 'chia': '/', 'bằng': '=',
            'phẩy': '.', 'mũ': '^', 'căn': '√'
        }
        for word, symbol in math_map.items():
            text = text.replace(f" {word} ", f" {symbol} ") 
            text = text.replace(word, symbol)

        # 2. Convert common number words to digits
        num_map = {
            'không': '0', 'một': '1', 'hai': '2', 'ba': '3', 'bốn': '4', 
            'năm': '5', 'lăm': '5', 'sáu': '6', 'bảy': '7', 'tám': '8', 'chín': '9', 'mười': '10'
        }
        for word, digit in num_map.items():
            text = re.sub(r'\b' + word + r'\b', digit, text)

        # 3. Cleanup spacing
        text = re.sub(r'\s*([+\-*/=^√])\s*', r' \1 ', text)
        return text.strip()

    def format_for_social(self, text: str) -> str:
        """
        Format for History/Social subjects.
        "năm một chín bốn lăm" -> "năm 1945"
        """
        text = text.lower()
        
        num_map = {
            'không': '0', 'một': '1', 'hai': '2', 'ba': '3', 'bốn': '4', 
            'năm': '5', 'lăm': '5', 'sáu': '6', 'bảy': '7', 'tám': '8', 'chín': '9'
        }
        
        words = text.split()
        new_words = []
        for w in words:
            if w in num_map:
                new_words.append(num_map[w])
            else:
                new_words.append(w)
        
        processed = " ".join(new_words)
        processed = re.sub(r'(\d)\s+(?=\d)', r'\1', processed)
        return processed
    
    async def process_audio_packet(self, data: bytes, addr: tuple):
        """
        Process incoming audio packet.
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
        
        # Simple end detection: if buffer > 3 seconds worth of audio
        if len(self.audio_buffers[device_id]) > 96000:
            # Check capacity
            if len(self.active_requests) >= self.max_concurrent:
                logger.warning(f"At capacity ({self.max_concurrent}), student {device_id} must wait")
                await self.send_response(addr, "He thong dang ban. Xin cho 10s")
                self.audio_buffers[device_id] = bytearray()
                return
            
            # Process in parallel
            audio_copy = bytes(self.audio_buffers[device_id])
            self.audio_buffers[device_id] = bytearray()
            
            task = asyncio.create_task(self.process_question(device_id, audio_copy, addr))
            self.active_requests[device_id] = task
            
            task.add_done_callback(lambda t: self.active_requests.pop(device_id, None))
    
    async def process_question(self, device_id: str, audio_bytes: bytes, addr: tuple):
        """
        Process complete question audio.
        """
        start_time = time.time()
        logger.info(f"[{device_id}] Processing AI question")
        
        try:
            # Convert PCM to WAV
            wav_data = self.pcm_to_wav(audio_bytes, sample_rate=16000, channels=1, sample_width=2)
            
            # STT
            loop = asyncio.get_event_loop()
            audio_source = sr.AudioFile(io.BytesIO(wav_data))
            with audio_source as source:
                audio = self.recognizer.record(source)
            
            # Google STT
            raw_text = await loop.run_in_executor(
                self.executor,
                self.recognizer.recognize_google,
                audio,
                'vi-VN'
            )
            
            # 🧮 APPLY SUBJECT MODE FORMATTING
            processed_text = self.normalize_text_by_mode(raw_text)
            logger.info(f"[{device_id}] Question ({self.current_subject}): {processed_text}")
            
            # Ask AI
            answer_data = await loop.run_in_executor(
                self.executor,
                self.ai_assistant.ask_question_with_visual,
                processed_text,
                device_id
            )
            
            answer_text = answer_data['text']
            has_visual = answer_data['has_visual']
            visual_type = answer_data['visual_type']
            visual_param = answer_data['visual_param']
            
            logger.info(f"[{device_id}] Answer: {answer_text}")
            if has_visual:
                logger.info(f"[{device_id}] Visual: {visual_type}/{visual_param}")
            
            # PUBLISH LOG FOR TEACHER DASHBOARD
            log_payload = {
                "student": device_id,
                "question": processed_text,
                "answer": answer_text
            }
            self.mqtt_client.publish("student/query/log", json.dumps(log_payload))

            await self.send_response(addr, answer_text, visual_type, visual_param)
            
            elapsed = time.time() - start_time
            logger.info(f"[{device_id}] Completed in {elapsed:.2f}s")
            
        except sr.UnknownValueError:
            logger.warning(f"[{device_id}] Could not understand audio")
            await self.send_response(addr, "Xin loi, em noi lai duoc khong?", None, None)
        except Exception as e:
            logger.error(f"[{device_id}] Error processing question: {e}")
            await self.send_response(addr, "Xin loi, co loi xay ra", None, None)
    
    async def send_response(self, addr: tuple, text: str, 
                           visual_type: str = None, visual_param: str = None):
        """Send response back to device."""
        # TODO: Implement response protocol via MQTT
        logger.info(f"Sending response to {addr}: {text}")
        if visual_type:
            logger.info(f"  Visual: {visual_type}/{visual_param}")
    
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
        content = DocumentProcessor.extract_text(file_path)
        if content:
            self.ai_assistant.load_lecture(content)
            logger.info(f"Loaded document: {file_path}")
        else:
            logger.error(f"Failed to load document: {file_path}")


async def main():
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY environment variable not set!")
        return
    
    service = AIService(listen_port=12346)
    
    lectures_dir = "data/lectures"
    if os.path.exists(lectures_dir):
        for filename in os.listdir(lectures_dir):
            if filename.endswith(('.pdf', '.docx', '.txt')):
                service.load_document(os.path.join(lectures_dir, filename))
    
    await service.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("AI Service stopped by user")
