import asyncio
import json
import paho.mqtt.client as mqtt
from .registry import DeviceRegistry
from .router import AudioRouter

    def set_mode(self, device_id, mode):
        self.publish("audio/control", {"target": device_id, "command": "set_mode", "mode": mode})
        self.registry.set_mode(device_id, mode)

    # --- Chatbot & Monitoring Extensions ---
    def on_connect(self, client, userdata, flags, rc):
        print(f"Box MQTT Connected with result code {rc}")
        # Subscribe to all relevant topics
        client.subscribe("glasses/status")
        client.subscribe("glasses/text")
        client.subscribe("audio/control")
        
        # New: Chat & Monitoring
        client.subscribe("teacher/chat/response") # Response from AI
        client.subscribe("student/query/log")     # Logs from student interactions

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = "test.mosquitto.org" # Or local "localhost"
        self.port = 1883
        
        self.registry = DeviceRegistry()
        self.router = AudioRouter(self.registry)
        
        # Chat Sessions (In-memory)
        # Structure: { "session_id": [ {msg}, {msg} ] }
        self.sessions = {
            "broadcast": [] # System/Broadcast channel
        }
        self.max_history_per_session = 50

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            # print(f"Box Received [{topic}]") # Reduced logging
            
            data = json.loads(payload_str) if payload_str.strip() else {}

            if topic == "glasses/status":
                device_id = data.get("id", "glass_default") 
                mode = data.get("mode", "class")
                self.registry.register_or_update(
                    device_id, 
                    "glasses", 
                    status="online",
                    mode=mode,
                    battery=data.get("battery")
                )
                
            elif topic == "teacher/chat/response":
                # AI answering. We assume the AI echoes the session_id or we default to broadcast for now
                session_id = data.get("session_id", "broadcast")
                self.add_chat_log(session_id, "ai", data.get("text", ""), data.get("visual", None))
                
            elif topic == "student/query/log":
                # Log student query to their specific session
                student_id = data.get("student", "Unknown")
                question = data.get("question", "")
                answer = data.get("answer", "")
                
                # Ensure session exists
                if student_id not in self.sessions:
                    self.sessions[student_id] = []
                    
                self.add_chat_log(student_id, "student_log", f"Q: {question}\nA: {answer}")

        except json.JSONDecodeError:
            print("Failed to decode JSON payload")
        except Exception as e:
            print(f"Error processing message: {e}")

    def add_chat_log(self, session_id, sender, message, meta=None):
        """Add message to specific session history"""
        import time
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        entry = {
            "id": int(time.time() * 1000),
            "sender": sender, 
            "text": message,
            "meta": meta,
            "timestamp": time.strftime("%H:%M")
        }
        self.sessions[session_id].append(entry)
        
        if len(self.sessions[session_id]) > self.max_history_per_session:
            self.sessions[session_id].pop(0)

    def send_chat_to_ai(self, text, session_id="broadcast"):
        """Send teacher message to AI with session context"""
        self.add_chat_log(session_id, "teacher", text)
        self.publish("teacher/chat/request", {
            "text": text, 
            "session_id": session_id,
            "source": "web_dashboard"
        })
