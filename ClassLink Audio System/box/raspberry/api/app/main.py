from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
from pathlib import Path
from services.mqtt import MQTTService

app = FastAPI()
mqtt_service = MQTTService()

# Get absolute path to static directory
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Mount Static Files with absolute path
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
async def startup_event():
    # Start MQTT Client in background
    asyncio.create_task(mqtt_service.start())

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


@app.get("/api/wifi/scan")
async def scan_wifi():
    import subprocess
    import platform
    
    wifi_networks = []
    
    if platform.system() == "Windows":
        try:
            # Run the netsh command to get wifi networks
            result = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], stderr=subprocess.STDOUT)
            output = result.decode("utf-8", errors="ignore")
            
            current_ssid = None
            current_bssid = None
            current_signal = None
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("SSID"):
                    # Save previous if complete
                    if current_ssid:
                        wifi_networks.append({
                            "ssid": current_ssid,
                            "bssid": current_bssid,
                            "signal": current_signal or 0,
                            "secure": True 
                        })
                    current_ssid = line.split(":", 1)[1].strip()
                    current_bssid = None # Reset
                    current_signal = None
                elif line.startswith("Signal"):
                     try:
                        current_signal = int(line.split(":", 1)[1].strip().replace("%", ""))
                     except:
                        current_signal = 0
                
            # Add the last one
            if current_ssid:
                wifi_networks.append({
                    "ssid": current_ssid,
                    "signal": current_signal or 0,
                    "secure": True
                })
                
        except Exception as e:
            print(f"Error scanning wifi: {e}")
            # Fallback mock if scan fails
            return [
                {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
                {"ssid": "School_Guest", "signal": 60, "secure": False}
            ]
    else:
        # Mock for non-windows
        return [
             {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
             {"ssid": "School_Guest", "signal": 60, "secure": False}
        ]

    # Deduplicate by SSID
    unique_networks = {}
    for net in wifi_networks:
        if net["ssid"] and net["ssid"] not in unique_networks:
             unique_networks[net["ssid"]] = net
    
    return list(unique_networks.values())
    
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

@app.post("/api/wifi/connect")
async def connect_wifi(data: dict):
    ssid = data.get("ssid")
    password = data.get("password")
    print(f"[WiFi] Simulating connection to {ssid} with password {'*' * len(password) if password else 'OPEN'}")
    # Initialize connection simulation
    await asyncio.sleep(2) # Simulate delay
    return {"status": "success", "message": f"Connected to {ssid}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
