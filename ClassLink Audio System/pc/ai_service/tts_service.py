from gtts import gTTS
import os
import logging

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service for AI responses."""
    
    def __init__(self, output_dir: str = "/tmp/ai_audio"):
        """
        Initialize TTS service.
        
        Args:
            output_dir: Directory to save audio files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"TTS Service initialized. Output dir: {output_dir}")
    
    def text_to_speech(self, text: str, filename: str = "response.mp3", lang: str = 'vi') -> str:
        """
        Convert text to speech audio file.
        
        Args:
            text: Text to convert
            filename: Output filename
            lang: Language code ('vi' for Vietnamese)
        
        Returns:
            Path to generated audio file
        """
        try:
            output_path = os.path.join(self.output_dir, filename)
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_path)
            
            logger.info(f"Generated TTS audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return ""
    
    def cleanup_old_files(self, max_age_seconds: int = 3600):
        """
        Remove old audio files to save disk space.
        
        Args:
            max_age_seconds: Remove files older than this
        """
        import time
        
        now = time.time()
        removed = 0
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    removed += 1
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} old TTS files")


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    tts = TTSService()
    
    # Test Vietnamese TTS
    audio_path = tts.text_to_speech(
        "Để giải phương trình 2x + 4 = 0, ta chuyển vế: 2x = -4, rồi chia cả 2 vế cho 2: x = -2",
        "test_response.mp3"
    )
    
    print(f"Audio saved to: {audio_path}")
    print(f"File size: {os.path.getsize(audio_path)} bytes")
