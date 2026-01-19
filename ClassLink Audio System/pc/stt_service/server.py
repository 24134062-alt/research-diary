import asyncio
import logging
import json
import struct
import argparse
import os
from typing import Optional

# 3rd party
# pip install paho-mqtt
import paho.mqtt.client as mqtt

from stt_engine import STTEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PCService")

# Load Configuration
CONFIG_PATH = "config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
else:
    # We can't use logger yet if it depends on basicConfig, but here basicConfig is called already
    config = {
        "mqtt": {"broker": "192.168.4.1", "port": 1883, "topics": {"text": "glasses/text", "control": "audio/control"}},
        "udp": {"ip": "0.0.0.0", "port": 12345},
        "stt": {"language": "vi-VN", "buffer_seconds": 3}
    }
    logger.warning("config.json not found, using defaults")

UDP_IP = config["udp"]["ip"]
UDP_PORT = config["udp"]["port"]
MQTT_BROKER = config["mqtt"]["broker"]
MQTT_PORT = config["mqtt"]["port"]
TOPIC_TEXT = config["mqtt"]["topics"]["text"]
TOPIC_CONTROL = config["mqtt"]["topics"]["control"]

class AudioUDPServer:
    def __init__(self, stt_engine: STTEngine, mqtt_client: mqtt.Client):
        self.stt_engine = stt_engine
        self.mqtt_client = mqtt_client
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"UDP Server started on {UDP_PORT}")

    def datagram_received(self, data, addr):
        # Parse Protocol (Matches ESP32 hardware header)
        # Header: Sequence Number (4 bytes) + Flags (1 byte)
        if len(data) < 5:
            return
        
        seq_num = struct.unpack('<I', data[:4])[0]
        flags = data[4]
        ai_mode = (flags & 0x01) != 0
        audio_payload = data[5:]
        
        # Dispatching logic:
        # If AI mode is active, forward audio to AI Service (port 12346)
        if ai_mode:
            ai_service_addr = (UDP_IP, 12346)
            self.transport.sendto(data, ai_service_addr)
            # We don't transcribe logic here to save CPU, AI service handles it
            return

        # Forward to STT loop for teaching transcription
        text = self.stt_engine.process_audio(audio_payload)
        
        if text:
            logger.info(f"STT Result: {text}")
            self.broadcast_text(text)

    def broadcast_text(self, text: str):
        if not self.mqtt_client.is_connected():
            logger.warn("MQTT not connected, skipping publish")
            return

        payload = json.dumps({
            "text": text,
            "duration": 5000,
            "clear": False
        })
        self.mqtt_client.publish(TOPIC_TEXT, payload)
        logger.info(f"Published to {TOPIC_TEXT}: {text}")

    def error_received(self, exc):
        logger.error(f"UDP Error: {exc}")

def on_mqtt_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT Broker (rc={rc})")
    client.subscribe(TOPIC_CONTROL)

def on_mqtt_message(client, userdata, msg):
    logger.info(f"MQTT Msg: {msg.topic} {msg.payload}")

async def main():
    # 1. Setup STT
    stt = STTEngine(
        language=config["stt"]["language"],
        buffer_seconds=config["stt"]["buffer_seconds"]
    )

    # 2. Setup MQTT
    client = mqtt.Client()
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    
    try:
        logger.info(f"Connecting to MQTT {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT: {e}")
        return

    # 3. Setup UDP
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: AudioUDPServer(stt, client),
        local_addr=(UDP_IP, UDP_PORT)
    )

    try:
        await asyncio.Event().wait()  # Run forever
    except asyncio.CancelledError:
        pass
    finally:
        transport.close()
        client.loop_stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
