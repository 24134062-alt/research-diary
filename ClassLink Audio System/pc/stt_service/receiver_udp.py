"""
File: receiver_udp.py
Path: C:\Users\DELL\project\pc\stt_service\receiver_udp.py

Vai trò:
- Nhận UDP audio (fake) từ ESP32 BOX
- In log để kiểm tra đường truyền

Ghi chú:
- Chưa xử lý audio
- Chưa STT
"""

import socket

# ====== Config ======
UDP_IP = "0.0.0.0"      # lắng nghe mọi IP
UDP_PORT = 50005       # phải trùng với ESP32

# ====== Init socket ======
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"[PC] UDP receiver listening on port {UDP_PORT}")

# ====== Loop ======
packet_count = 0

while True:
    data, addr = sock.recvfrom(2048)
    packet_count += 1

    print(f"[PC] recv #{packet_count} | {len(data)} bytes | from {addr}")

