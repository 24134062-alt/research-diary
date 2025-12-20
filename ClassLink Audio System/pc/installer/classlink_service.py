# -*- coding: utf-8 -*-
"""
ClassLink AI Service - Background Service for PC
Runs in background, connects to Raspberry Pi via MQTT/HTTP
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from threading import Thread

# Setup logging
log_file = Path(__file__).parent / "classlink.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment
from dotenv import load_dotenv
config_path = Path(__file__).parent / "config.env"
if config_path.exists():
    load_dotenv(config_path)

# Import AI components
from google import genai
import paho.mqtt.client as mqtt

class ClassLinkService:
    """Background service for ClassLink AI processing"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found!")
            raise ValueError("GEMINI_API_KEY required")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"
        
        # MQTT client
        self.mqtt_client = mqtt.Client(client_id="classlink-pc-service")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # State
        self.running = False
        self.connected = False
        self.raspberry_ip = None
        
        logger.info("ClassLink Service initialized")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker")
            self.connected = True
            # Subscribe to topics
            client.subscribe("teacher/chat/request")
            client.subscribe("student/question")
            client.subscribe("pc/ping")
            # Announce PC is ready
            client.publish("pc/status", json.dumps({"status": "ready"}))
        else:
            logger.error(f"MQTT connection failed: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            if topic == "pc/ping":
                # Respond to ping
                client.publish("pc/pong", json.dumps({"status": "alive"}))
                
            elif topic == "teacher/chat/request":
                # Teacher chat request
                data = json.loads(payload)
                question = data.get("text", "")
                if question:
                    Thread(target=self.process_chat, args=(question,)).start()
                    
            elif topic == "student/question":
                # Student question from mic
                data = json.loads(payload)
                question = data.get("text", "")
                student_id = data.get("student_id", "unknown")
                if question:
                    Thread(target=self.process_question, args=(question, student_id)).start()
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def process_chat(self, question: str):
        """Process teacher chat request"""
        logger.info(f"[CHAT] Question: {question}")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"Tra loi ngan gon bang tieng Viet: {question}"
            )
            answer = response.text.strip()
            
            self.mqtt_client.publish("teacher/chat/response", json.dumps({
                "text": answer
            }))
            logger.info(f"[CHAT] Answer: {answer[:50]}...")
            
        except Exception as e:
            logger.error(f"[CHAT] Error: {e}")
            self.mqtt_client.publish("teacher/chat/response", json.dumps({
                "text": "Xin loi, AI dang ban. Vui long thu lai.",
                "error": str(e)
            }))
    
    def process_question(self, question: str, student_id: str):
        """Process student question"""
        logger.info(f"[STUDENT:{student_id}] Question: {question}")
        try:
            prompt = f"""Ban la tro giang thong minh. Tra loi CUC KY NGAN GON (toi da 40 tu):
            
Cau hoi: {question}

Tra loi:"""
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            answer = response.text.strip()
            
            # Limit length
            words = answer.split()
            if len(words) > 45:
                answer = " ".join(words[:45]) + "..."
            
            self.mqtt_client.publish("student/answer", json.dumps({
                "student_id": student_id,
                "text": answer
            }))
            logger.info(f"[STUDENT:{student_id}] Answer: {answer}")
            
        except Exception as e:
            logger.error(f"[STUDENT] Error: {e}")
    
    def connect_to_raspberry(self, ip: str, port: int = 1883):
        """Connect to Raspberry Pi MQTT broker"""
        try:
            logger.info(f"Connecting to Raspberry Pi at {ip}:{port}")
            self.mqtt_client.connect(ip, port, 60)
            self.raspberry_ip = ip
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def run(self):
        """Main service loop"""
        self.running = True
        logger.info("ClassLink Service starting...")
        
        # Try to connect to common Raspberry Pi IPs
        possible_ips = [
            "192.168.4.1",      # AP mode
            "192.168.0.107",    # LAN mode
            "classlink.local",  # mDNS
            "localhost"         # Local testing
        ]
        
        while self.running:
            if not self.connected:
                for ip in possible_ips:
                    if self.connect_to_raspberry(ip):
                        break
                    time.sleep(1)
            
            if self.connected:
                self.mqtt_client.loop(timeout=1.0)
            else:
                time.sleep(5)
    
    def stop(self):
        """Stop the service"""
        self.running = False
        self.mqtt_client.disconnect()
        logger.info("ClassLink Service stopped")


def main():
    logger.info("="*50)
    logger.info("ClassLink AI Service Starting...")
    logger.info("="*50)
    
    try:
        service = ClassLinkService()
        service.run()
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Service error: {e}")
        time.sleep(5)
        main()  # Restart on error


if __name__ == "__main__":
    main()
