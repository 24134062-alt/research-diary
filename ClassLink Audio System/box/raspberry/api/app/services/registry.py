import time
from typing import Dict, Optional
from pydantic import BaseModel

class DeviceInfo(BaseModel):
    device_id: str
    type: str  # "mic", "pc", "glasses"
    status: str = "offline"
    last_seen: float = 0.0
    mode: str = "class"  # "class" or "private"
    ip: Optional[str] = None

class DeviceRegistry:
    def __init__(self):
        self._devices: Dict[str, DeviceInfo] = {}

    def register_or_update(self, device_id: str, device_type: str, **kwargs):
        if device_id not in self._devices:
            self._devices[device_id] = DeviceInfo(device_id=device_id, type=device_type)
        
        device = self._devices[device_id]
        device.last_seen = time.time()
        device.status = "online"
        
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)
        
        print(f"[Registry] Device updated: {device}")
        return device

    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        return self._devices.get(device_id)

    def get_all_devices(self):
        return self._devices

    def set_mode(self, device_id: str, mode: str):
        if device_id in self._devices:
            self._devices[device_id].mode = mode
            print(f"[Registry] Device {device_id} switched to {mode} mode")

    def remove_inactive(self, timeout: int = 60):
        now = time.time()
        to_remove = [did for did, d in self._devices.items() if now - d.last_seen > timeout]
        for did in to_remove:
            print(f"[Registry] Removing inactive device: {did}")
            del self._devices[did]
