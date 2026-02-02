import asyncio
import socket
from .router import AudioRouter
from .registry import DeviceRegistry

class UDPGateway:
    """
    Listens for UDP audio packets from ESP32 hardware (Port 12345)
    and relays them to PC services (STT or AI) based on routing logic.
    """
    def __init__(self, registry: DeviceRegistry, router: AudioRouter, port=12345):
        self.registry = registry
        self.router = router
        self.port = port
        self.sock = None
        self.running = False

    async def start(self):
        """Starts the UDP server on all interfaces"""
        self.running = True
        
        # We use standard socket with asyncio loop for portability
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.sock.bind(("0.0.0.0", self.port))
        
        print(f"🔊 [Gateway] UDP Audio Gateway listening on port {self.port}")
        
        loop = asyncio.get_event_loop()
        while self.running:
            try:
                # Receive packet
                data, addr = await loop.run_in_executor(None, self.sock.recvfrom, 2048)
                source_ip = addr[0]
                
                # Identify source device if possible
                source_device_id = None
                for did, device in self.registry.get_all_devices().items():
                    if device.ip == source_ip:
                        source_device_id = did
                        break
                
                # Default source ID if not registered (fallback)
                source_device_id = source_device_id or f"raw_{source_ip}"
                
                # Use Router to find where to send this data
                destinations = self.router.route_audio_packet(data, source_device_id)
                
                # Relay to all destinations
                for dest_ip, dest_port in destinations:
                    try:
                        # Prepend device ID (16 bytes) so PC knows who sent it
                        # Format: [Device ID (16)] + [Original Packet (Flag + Seq + Audio)]
                        id_header = source_device_id.encode().ljust(16, b'\x00')
                        self.sock.sendto(id_header + data, (dest_ip, dest_port))
                        # print(f"[Gateway] Relayed to {dest_ip}:{dest_port} from {source_device_id}")
                    except Exception as e:
                        print(f"[Gateway] Relay error: {e}")
                        
            except Exception as e:
                if self.running:
                    # Suppress "Resource temporarily unavailable" spam (errno 11 = EAGAIN, normal when no data)
                    if "Resource temporarily unavailable" not in str(e):
                        print(f"[Gateway] Error in loop: {e}")
                await asyncio.sleep(0.01)


    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
