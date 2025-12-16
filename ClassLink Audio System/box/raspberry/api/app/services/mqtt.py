import asyncio
import json
import paho.mqtt.client as mqtt
from .registry import DeviceRegistry
from .router import AudioRouter

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = "test.mosquitto.org" # Or local "localhost"
        self.port = 1883
        
        self.registry = DeviceRegistry()
        self.router = AudioRouter(self.registry)

    async def start(self):
        print(f"Connecting to MQTT Broker {self.broker}...")
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT Connection Failed: {e}")

    def on_connect(self, client, userdata, flags, rc):
        print(f"Box MQTT Connected with result code {rc}")
        # Subscribe to all relevant topics
        client.subscribe("glasses/status")
        client.subscribe("glasses/text")
        client.subscribe("audio/control")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            print(f"Box Received [{topic}]: {payload_str}")
            
            data = json.loads(payload_str) if payload_str.strip() else {}

            if topic == "glasses/status":
                # Assuming payload has device_id, for now we infer it or use a field
                # Example: {"id": "glass1", "battery": 80, "mode": "class"}
                device_id = data.get("id", "glass_default") 
                mode = data.get("mode", "class")
                self.registry.register_or_update(
                    device_id, 
                    "glasses", 
                    status="online",
                    mode=mode,
                    battery=data.get("battery")
                )
                
                # Check routing
                dests = self.router.get_audio_destination(device_id)
                if dests:
                    print(f"Audio should route to: {dests}")

        except json.JSONDecodeError:
            print("Failed to decode JSON payload")
        except Exception as e:
            print(f"Error processing message: {e}")

    def publish(self, topic, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        self.client.publish(topic, message)

    def set_mode(self, device_id, mode):
        self.publish("audio/control", {"target": device_id, "command": "set_mode", "mode": mode})
        self.registry.set_mode(device_id, mode)
