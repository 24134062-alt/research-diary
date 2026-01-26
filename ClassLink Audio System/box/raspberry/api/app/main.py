from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
from pathlib import Path
import time
from .services.mqtt import MQTTService
from .services.uart import UARTService
from .services.wifi_monitor import WiFiMonitor
from .services.hotspot import HotspotController
from .services.gateway import UDPGateway
from .routes import health, setup_wifi, stt, wifi_manager, system, document

app = FastAPI()
mqtt_service = MQTTService()
uart_service = UARTService() # Default to /dev/ttyS0
wifi_monitor = WiFiMonitor()
hotspot_controller = HotspotController()

# Initialize UDP Audio Gateway
audio_gateway = UDPGateway(mqtt_service.registry, mqtt_service.router)

# In-memory activity log
activity_log = []

# In-memory transcription storage (Teacher speech & AI answers)
transcription_history = []

def add_activity(message, icon="info-circle"):
    global activity_log
    activity_log.insert(0, {"time": time.strftime("%H:%M:%S"), "message": message, "icon": icon})
    activity_log = activity_log[:20] # Keep last 20

def add_transcription(text, sender="teacher"):
    """Adds a transcription entry to history"""
    global transcription_history
    entry = {
        "time": time.strftime("%H:%M:%S"),
        "text": text,
        "sender": sender
    }
    transcription_history.insert(0, entry)
    transcription_history = transcription_history[:30] # Keep last 30

# Set services for wifi_manager router
wifi_manager.set_services(wifi_monitor, hotspot_controller)

# Set MQTT service for document router (để gửi tài liệu đến PC AI Service)
document.set_mqtt_service(mqtt_service)

# Link MQTT and UART for bi-directional bridge
mqtt_service.set_uart_service(uart_service)

# --- Hardware Bridge Configuration ---
def bridge_uart_to_mqtt(data):
    """Callback for UART messages -> Publish to MQTT"""
    msg_type = data.get("type")
    if msg_type in ["DEV_JOIN", "DEV_LEAVE"]:
        # Bridge to hardware status topic (Update: standardize keys)
        mqtt_service.publish("hardware/event", data)
        print(f"[BRIDGE] UART -> MQTT: {data}")
        action = "đã gia nhập" if msg_type == "DEV_JOIN" else "đã rời mạng"
        add_activity(f"Thiết bị {data.get('device_id', 'unknown')} {action}", "microchip")
    elif msg_type == "AUDIO_DATA":
        # Specific bridging for high-speed audio data if needed
        pass

uart_service.set_callback(bridge_uart_to_mqtt)
# -------------------------------------

# Get absolute path to static directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Mount Static Files with absolute path
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(setup_wifi.router, prefix="/api/wifi", tags=["WiFi Scan"])
app.include_router(wifi_manager.router, prefix="/api/wifi-manager", tags=["WiFi Manager"])
app.include_router(stt.router, prefix="/api", tags=["STT"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(document.router, prefix="/api/document", tags=["Document"])

@app.on_event("startup")
async def startup_event():
    # Start MQTT Client in background
    asyncio.create_task(mqtt_service.start())
    
    # Start UART Service in background
    asyncio.create_task(uart_service.start())
    
    # Start WiFi monitor in background
    asyncio.create_task(wifi_monitor.start_monitoring())

    # Start UDP Audio Gateway
    asyncio.create_task(audio_gateway.start())

@app.get("/")
async def read_root():
    return FileResponse(str(STATIC_DIR / 'index.html'))

@app.get("/api/devices")
def get_devices():
    # Helper to convert devices to dict
    devices = mqtt_service.registry.get_all_devices()
    return {k: v.dict() for k, v in devices.items()}

@app.post("/control/record/start")
async def start_record():
    mqtt_service.publish("audio/control", "start")
    return {"status": "Command Sent"}

@app.post("/control/record/stop")
async def stop_record():
    mqtt_service.publish("audio/control", "stop")
    return {"status": "Command Sent"}

@app.post("/control/mode/{device_id}/{mode}")
async def set_mode(device_id: str, mode: str):
    mqtt_service.set_mode(device_id, mode)
    return {"status": "Mode Updated", "device": device_id, "mode": mode}

@app.post("/control/subject/{subject}")
async def set_subject(subject: str):
    # Subject: 'math' or 'literature'
    mqtt_service.publish("teacher/subject", subject)
    return {"status": "Subject Updated", "subject": subject}


# WiFi routes moved to routes/setup_wifi.py
# Chat routes below

@app.post("/api/chat/send")
async def send_chat(data: dict):
    """Teacher sending message to AI"""
    text = data.get("text")
    session_id = data.get("session_id", "broadcast")
    
    if text:
        mqtt_service.send_chat_to_ai(text, session_id)
        return {"status": "sent", "text": text, "session_id": session_id}
    return {"status": "error", "message": "No text provided"}

@app.get("/api/chat/history")
async def get_chat_history():
    """Get recent chat logs (organized by session)"""
    return mqtt_service.sessions

@app.post("/api/broadcast")
async def broadcast_tts(data: dict):
    """Send TTS broadcast directly to all connected glasses"""
    text = data.get("text", "").strip()
    
    if not text:
        return {"status": "error", "message": "No text provided"}
    
    # Check if any glasses are connected
    glasses_devices = [d for d in mqtt_service.registry.get_all_devices().values() 
                       if d.get("type") == "glasses" and d.get("status") == "online"]
    
    if not glasses_devices:
        return {"status": "no_glasses", "message": "Chưa có kính nào kết nối"}
    
    # Send TTS to all glasses via MQTT
    mqtt_service.publish("glasses/tts", {
        "text": text,
        "source": "teacher_broadcast"
    })
    
    # Log to broadcast channel
    mqtt_service.add_chat_log("broadcast", "teacher", f"📢 Broadcast: {text}")
    
    return {
        "status": "sent",
        "text": text,
        "glasses_count": len(glasses_devices)
    }

@app.get("/api/activity-log")
async def get_activity_log():
    return activity_log

# WiFi connect route moved to routes/setup_wifi.py

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
