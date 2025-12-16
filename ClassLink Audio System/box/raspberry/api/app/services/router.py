from typing import List, Optional, Tuple
from .registry import DeviceRegistry

# AI Service configuration
AI_SERVICE_IP = "192.168.1.100"  # Same as STT PC
AI_SERVICE_PORT = 12346

class AudioRouter:
    def __init__(self, registry: DeviceRegistry):
        self.registry = registry
    
    def route_audio_packet(self, packet: bytes, source_device_id: str) -> List[Tuple[str, int]]:
        """
        Routes audio packet based on AI flag and device mode.
        
        Packet format: [1 byte flags][4 bytes seq][N bytes audio]
        
        Returns:
            List of (ip, port) tuples for destinations
        """
        if len(packet) < 5:
            return []
        
        # Extract flag byte
        flags = packet[0]
        is_ai_request = (flags & 0x01) != 0
        
        if is_ai_request:
            # AI request → route to AI service
            print(f"[Router] AI request from {source_device_id} → AI Service")
            return [(AI_SERVICE_IP, AI_SERVICE_PORT)]
        
        #Normal audio routing
        source = self.registry.get_device(source_device_id)
        if not source:
            return []
        
        if source.mode == "private":
            # Private mode: route to STT, response goes back to source only
            print(f"[Router] Private mode from {source_device_id} → STT (response only to source)")
            # TODO: Implement private mode routing (forward to STT, mark for single-device response)
            return []
        
        elif source.mode == "class":
            # Class mode: broadcast to all online PCs
            targets = []
            for did, device in self.registry.get_all_devices().items():
                if device.type == "pc" and device.status == "online" and device.ip:
                    # Assuming STT service on port 12345
                    targets.append((device.ip, 12345))
            
            print(f"[Router] Class mode from {source_device_id} → {len(targets)} PCs")
            return targets
        
        return []

    def get_audio_destination(self, source_device_id: str) -> List[str]:
        """
        Legacy method for backward compatibility.
        Determines where audio from a source should go based on its mode.
        Returns a list of target IP addresses.
        """
        source = self.registry.get_device(source_device_id)
        if not source:
            return []

        if source.mode == "private":
            print(f"[Router] Source {source_device_id} is in PRIVATE mode.")
            return []
        
        elif source.mode == "class":
            targets = []
            for did, device in self.registry.get_all_devices().items():
                if device.type == "pc" and device.status == "online" and device.ip:
                    targets.append(device.ip)
            
            print(f"[Router] Routing Class Audio from {source_device_id} to {targets}")
            return targets
            
        return []
