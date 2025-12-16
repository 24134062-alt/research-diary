from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
from services.mqtt import MQTTService

app = FastAPI()
mqtt_service = MQTTService()

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    # Start MQTT Client in background
    asyncio.create_task(mqtt_service.start())

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
