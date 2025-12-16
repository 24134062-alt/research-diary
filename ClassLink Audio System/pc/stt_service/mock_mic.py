import socket
import struct
import time
import math

# Config
TARGET_IP = "127.0.0.1"
TARGET_PORT = 12345
SAMPLE_RATE = 16000
PACKET_SIZE = 1024 # Payload size

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[MockMic] Sending audio to {TARGET_IP}:{TARGET_PORT}")

sequence = 0
try:
    while True:
        # Create Header: Sequence (4 bytes)
        header = struct.pack('<I', sequence)
        
        # Create Dummy Audio Data (Sine wave)
        # Just filling bytes for simplicity
        payload = bytes([sequence % 255] * PACKET_SIZE)
        
        packet = header + payload
        
        sock.sendto(packet, (TARGET_IP, TARGET_PORT))
        print(f"[MockMic] Sent Seq: {sequence}")
        
        sequence += 1
        time.sleep(0.02) # approx 20ms
        
        if sequence > 50: # Send 50 packets then stop for test
            break
            
except KeyboardInterrupt:
    print("Stopped")
