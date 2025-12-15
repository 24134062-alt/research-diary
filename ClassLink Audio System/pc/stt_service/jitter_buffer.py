"""
File: jitter_buffer.py
Path: C:\Users\DELL\project\pc\stt_service\jitter_buffer.py

Vai trò:
- Gom packet UDP
- Phát ra đều theo chu kỳ cố định
- Giảm giật trước khi đưa vào STT

Ghi chú:
- MVP: không reorder theo seq
- Chỉ dùng FIFO đơn giản
"""

import queue
import threading
import time


class JitterBuffer:
    def __init__(self, max_packets=50, interval_ms=20):
        """
        max_packets : số packet tối đa giữ trong buffer
        interval_ms : thời gian phát ra mỗi packet (ms)
        """
        self.buffer = queue.Queue(maxsize=max_packets)
        self.interval = interval_ms / 1000.0
        self.running = False

    def push(self, packet: bytes):
        """Nhận packet từ UDP"""
        if not self.buffer.full():
            self.buffer.put(packet)
        else:
            # Buffer đầy → drop packet cũ nhất
            try:
                self.buffer.get_nowait()
                self.buffer.put(packet)
            except queue.Empty:
                pass

    def start(self, on_packet):
        """
        on_packet(packet): callback xử lý packet đều đặn
        """
        self.running = True

        def run():
            while self.running:
                try:
                    packet = self.buffer.get(timeout=1)
                    on_packet(packet)
                except queue.Empty:
                    # Không có packet → chờ tiếp
                    pass

                time.sleep(self.interval)

        threading.Thread(target=run, daemon=True).start()

    def stop(self):
        self.running = False

