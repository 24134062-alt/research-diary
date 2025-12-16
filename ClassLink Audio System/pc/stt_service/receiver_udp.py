"""
UDP Receiver for Audio Packets
Receives audio from Box Raspberry Pi and processes with STT
"""

import socket
import struct
import logging
from stt_engine import STTEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
UDP_IP = "0.0.0.0"      # Listen on all interfaces
UDP_PORT = 12345        # STT service port (AI uses 12346)

# Initialize
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

stt_engine = STTEngine()

logger.info(f"[STT Service] Listening on port {UDP_PORT}")
logger.info("[STT Service] Using Google Cloud API - NO model download needed!")

# Main loop
packet_count = 0
last_seq = -1

while True:
    try:
        data, addr = sock.recvfrom(2048)
        packet_count += 1
        
        # NEW Packet Format: [1 byte flags][4 bytes seq][N bytes audio]
        if len(data) >= 5:
            flags = data[0]
            seq = struct.unpack('<I', data[1:5])[0]
            audio_payload = data[5:]
            
            # Check AI flag
            is_ai = (flags & 0x01) != 0
            if is_ai:
                logger.warning(f"AI packet received on STT port - should go to port 12346!")
                continue
            
            # Check for packet loss
            loss = 0
            if last_seq != -1:
                loss = seq - last_seq - 1
            last_seq = seq
            
            logger.debug(f"Packet #{packet_count} | Seq: {seq} | Loss: {loss} | Audio: {len(audio_payload)} bytes")
            
            # Process with STT
            text = stt_engine.process_audio(audio_payload)
            if text:
                logger.info(f"✅ STT Result: '{text}'")
                # TODO: Send result back to student via MQTT/WebSocket
        else:
            logger.warning(f"Invalid packet: {len(data)} bytes")
            
    except KeyboardInterrupt:
        logger.info("Shutting down STT service...")
        break
    except Exception as e:
        logger.error(f"Error: {e}")
