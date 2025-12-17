from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
from pathlib import Path
from services.mqtt import MQTTService
from services.wifi_monitor import WiFiMonitor
from services.hotspot import HotspotController
from routes import health, setup_wifi, stt, wifi_manager, system

app = FastAPI()
mqtt_service = MQTTService()
wifi_monitor = WiFiMonitor()
hotspot_controller = HotspotController()

# Set services for wifi_manager router
wifi_manager.set_services(wifi_monitor, hotspot_controller)

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

@app.on_event("startup")
async def startup_event():
    # Start MQTT Client in background
    asyncio.create_task(mqtt_service.start())
    
    # Start WiFi monitor in background
    asyncio.create_task(wifi_monitor.start_monitoring())

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

# WiFi connect route moved to routes/setup_wifi.py

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
