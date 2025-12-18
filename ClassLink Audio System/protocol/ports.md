# Network Ports

Danh sách các port được sử dụng trong hệ thống ClassLink.

## Port Allocation

| Port | Protocol | Direction | Component | Description |
|------|----------|-----------|-----------|-------------|
| **12345** | UDP | Glasses → PC | STT Service | Audio streaming |
| **1883** | TCP | All ↔ Broker | MQTT | Control & messaging |
| **8000** | HTTP | Client → RPi | Web Dashboard | Teacher interface |
| **8080** | HTTP | Internal | AI Service | AI API (optional) |

---

## Detailed Specifications

### UDP 12345 - Audio Streaming
- **Source**: Glasses ESP32, Mic Remote ESP32
- **Destination**: PC STT Service
- **Packet Size**: 4 + 512 bytes (header + audio)
- **Rate**: ~31 packets/second (16kHz / 512 samples)

### MQTT 1883 - Control Plane
- **Broker**: test.mosquitto.org (dev) hoặc local broker (prod)
- **QoS**: 0 (fire-and-forget cho tốc độ)
- **Topics**: Xem [topics.md](topics.md)

### HTTP 8000 - Web Dashboard
- **Server**: Raspberry Pi (FastAPI)
- **Endpoints**:
  - `GET /` - Dashboard UI
  - `GET /api/status` - System status
  - `POST /api/wifi/scan` - Scan WiFi networks
  - `POST /api/wifi/connect` - Connect to WiFi

---

## Firewall Rules

Nếu deploy trên mạng có firewall, cần mở các port sau:

```bash
# Raspberry Pi
sudo ufw allow 8000/tcp   # Web Dashboard
sudo ufw allow 1883/tcp   # MQTT (nếu local broker)

# PC
sudo ufw allow 12345/udp  # Audio reception
```
