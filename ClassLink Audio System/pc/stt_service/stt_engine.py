"""
STT Engine using Google Cloud Speech-to-Text API

NO MODEL DOWNLOAD NEEDED - Uses cloud API
"""

import speech_recognition as sr
import logging
import io
import wave

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STTEngine:
    def __init__(self):
        """Initialize STT engine with Google API"""
        self.recognizer = sr.Recognizer()
        self.audio_buffer = bytearray()
        
        # Audio config: 16kHz, 16-bit, mono
        self.SAMPLE_RATE = 16000
        self.SAMPLE_WIDTH = 2  # 16-bit = 2 bytes
        self.CHANNELS = 1
        
        # Buffer threshold: ~3 seconds of audio
        self.BUFFER_THRESHOLD = self.SAMPLE_RATE * self.SAMPLE_WIDTH * 3
        
        logger.info("STT Engine initialized (Google Cloud API - no model needed)")
    
    def process_audio(self, audio_data: bytes) -> str | None:
        """
        Process incoming audio data.
        
        Args:
            audio_data: Raw PCM audio bytes (16kHz, 16-bit, mono)
        
        Returns:
            Recognized text if buffer threshold met, else None
        """
        self.audio_buffer.extend(audio_data)
        
        # Check if we have enough audio to process
        if len(self.audio_buffer) >= self.BUFFER_THRESHOLD:
            logger.info(f"Processing {len(self.audio_buffer)} bytes of audio...")
            
            try:
                text = self._recognize_speech()
                self.audio_buffer.clear()
                return text
            except Exception as e:
                logger.error(f"STT error: {e}")
                self.audio_buffer.clear()
                return None
        
        return None
    
    def _recognize_speech(self) -> str:
        """
        Convert buffered audio to text using Google Cloud STT.
        NO MODEL DOWNLOAD - Uses cloud API!
        
        Returns:
            Recognized text in Vietnamese
        """
        # Convert raw PCM to WAV format (Google API needs WAV)
        wav_data = self._pcm_to_wav(bytes(self.audio_buffer))
        
        # Create AudioFile object
        audio_file = sr.AudioFile(io.BytesIO(wav_data))
        
        with audio_file as source:
            audio = self.recognizer.record(source)
        
        # Call Google Cloud STT API (NO MODEL - Internet required)
        try:
            text = self.recognizer.recognize_google(
                audio, 
                language='vi-VN'  # Vietnamese
            )
            logger.info(f"STT Result: {text}")
            return text
        
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return ""
        
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return ""
    
    def _pcm_to_wav(self, pcm_data: bytes) -> bytes:
        """Convert raw PCM to WAV format"""
        output = io.BytesIO()
        
        with wave.open(output, 'wb') as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.SAMPLE_WIDTH)
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(pcm_data)
        
        return output.getvalue()


# Test
if __name__ == "__main__":
    import numpy as np
    
    # Create fake audio data (3 seconds)
    fake_audio = np.random.randint(0, 256, 16000 * 2 * 3, dtype=np.uint8).tobytes()
    
    engine = STTEngine()
    result = engine.process_audio(fake_audio)
    
    if result:
        print(f"Recognized: {result}")
    else:
        print("No text recognized (expected with random audio)")
