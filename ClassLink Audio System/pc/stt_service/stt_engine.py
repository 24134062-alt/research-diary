"""
File: stt_engine.py
Path: C:\Users\DELL\project\pc\stt_service\stt_engine.py

Vai trò:
- Nhận audio frame từ jitter buffer
- Chuyển audio -> text (FAKE)
- Gọi callback khi có text

Ghi chú:
- MVP: giả lập STT
- STT thật (Whisper/Vosk) sẽ thay thế hàm recognize()
"""

import time


class STTEngine:
    def __init__(self, min_frames=20):
        """
        min_frames: số frame audio gom lại trước khi sinh text
        """
        self.min_frames = min_frames
        self.frames = []
        self.last_emit = time.time()

    def push_audio(self, frame: bytes):
        """
        Nhận 1 frame audio (bytes)
        """
        self.frames.append(frame)

        if len(self.frames) >= self.min_frames:
            text = self.recognize(self.frames)
            self.frames.clear()
            return text

        return None

    def recognize(self, frames):
        """
        FAKE STT:
        - sau N frame thì trả về text mẫu
        """
        # Giả lập độ trễ xử lý
        time.sleep(0.05)

        return "xin chào (fake stt)"

