import asyncio
import json
from .registry import DeviceRegistry
from .router import AudioRouter

# Optional MQTT dependency - allow API to run in demo mode without paho-mqtt
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️  paho-mqtt not installed - MQTT service running in DEMO mode")

class MQTTService:
    def set_mode(self, device_id, mode):
        if MQTT_AVAILABLE:
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
        # Initialize registry and router (always needed)
        self.registry = DeviceRegistry()
        self.router = AudioRouter(self.registry)
        
        # Chat Sessions (In-memory)
        # Structure: { "session_id": [ {msg}, {msg} ] }
        self.sessions = {
            "broadcast": [] # System/Broadcast channel
        }
        self.max_history_per_session = 50
        
        # Initialize MQTT client only if library is available
        if MQTT_AVAILABLE:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.broker = "test.mosquitto.org" # Or local "localhost"
            self.port = 1883
        else:
            self.client = None
            print("📡 MQTT features disabled - API running in standalone mode")

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
    
    def publish(self, topic, payload):
        """Publish message to MQTT broker (if available)"""
        if MQTT_AVAILABLE and self.client:
            try:
                self.client.publish(topic, json.dumps(payload))
            except Exception as e:
                print(f"⚠️  MQTT publish failed: {e}")
        # In demo mode, just log the action
        else:
            print(f"📤 [DEMO] Would publish to {topic}: {payload}")
    
    async def start(self):
        """Start MQTT service (connect and loop)"""
        if MQTT_AVAILABLE and self.client:
            try:
                print(f"🔌 Connecting to MQTT broker: {self.broker}:{self.port}")
                self.client.connect(self.broker, self.port, 60)
                # Run loop in background
                self.client.loop_start()
                print("✅ MQTT service started successfully")
            except Exception as e:
                print(f"⚠️  MQTT connection failed: {e}. Running in standalone mode.")
        else:
            print("📡 MQTT service running in DEMO mode - no broker connection")
