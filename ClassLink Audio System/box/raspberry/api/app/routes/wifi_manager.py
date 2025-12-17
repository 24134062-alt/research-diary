"""
WiFi Manager Routes
API endpoints for WiFi failover and hotspot management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# These will be set by main.py
wifi_monitor = None
hotspot_controller = None

def set_services(monitor, hotspot):
    """Set service instances"""
    global wifi_monitor, hotspot_controller
    wifi_monitor = monitor
    hotspot_controller = hotspot

class SwitchRequest(BaseModel):
    confirm: bool = True

@router.get("/status")
async def get_wifi_status():
    """Get current WiFi connection status and signal strength"""
    if not wifi_monitor:
        return {"error": "WiFi monitor not initialized"}
    
    wifi_status = wifi_monitor.get_status()
    hotspot_status = hotspot_controller.get_status() if hotspot_controller else {"ap_mode": False}
    
    return {
        **wifi_status,
        **hotspot_status,
        "timestamp": int(__import__('time').time())
    }

@router.post("/switch-to-ap")
async def switch_to_ap(request: SwitchRequest):
    """Switch to Access Point (hotspot) mode"""
    if not hotspot_controller:
        raise HTTPException(status_code=500, detail="Hotspot controller not initialized")
    
    if not request.confirm:
        return {"status": "cancelled"}
    
    result = hotspot_controller.enable_ap_mode()
    
    if result.get("success"):
        return {
            "status": "success",
            "mode": "ap",
            "ssid": result.get("ssid"),
            "message": f"Hotspot '{result.get('ssid')}' enabled"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Unknown error")
        )

@router.post("/switch-to-client")
async def switch_to_client(request: SwitchRequest):
    """Switch back to client mode (disable hotspot)"""
    if not hotspot_controller:
        raise HTTPException(status_code=500, detail="Hotspot controller not initialized")
    
    if not request.confirm:
        return {"status": "cancelled"}
    
    result = hotspot_controller.disable_ap_mode()
    
    if result.get("success"):
        # Trigger WiFi rescan
        if wifi_monitor:
            await wifi_monitor.check_signal()
        
        return {
            "status": "success",
            "mode": "client",
            "message": "Switched back to client mode"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Unknown error")
        )
