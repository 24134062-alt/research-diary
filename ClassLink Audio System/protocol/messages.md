# Message Formats

Định nghĩa format của tất cả messages trong hệ thống.

---

## 1. UDP Audio Packet

Binary format cho audio streaming.

```
┌──────────────────┬──────────────────────────────┐
│  Sequence (4B)   │       Audio Data (512B)      │
└──────────────────┴──────────────────────────────┘
```

| Field | Type | Size | Description |
|-------|------|------|-------------|
| sequence | uint32_t | 4 bytes | Incremental counter (little-endian) |
| audio_data | int16_t[] | 512 bytes | PCM 16-bit signed samples |

**Total**: 516 bytes per packet

---

## 2. MQTT Messages

Tất cả MQTT messages sử dụng JSON format.

### 2.1 Audio Control
**Topic**: `audio/control`
**Direction**: Dashboard → Device

```json
{
  "command": "start_record" | "stop_record" | "reboot",
  "device_id": "glasses_01"
}
```

### 2.2 Text Display
**Topic**: `glasses/text`
**Direction**: AI Service → Device

```json
{
  "text": "Câu trả lời từ AI...",
  "duration": 5000,
  "clear": false,
  "device_id": "glasses_01"
}
```

| Field | Type | Description |
|-------|------|-------------|
| text | string | Text to display on OLED |
| duration | int | Display time in milliseconds (0 = permanent) |
| clear | bool | Clear screen before displaying |
| device_id | string | Target device (optional, broadcast if omitted) |

### 2.3 Device Status
**Topic**: `glasses/status`
**Direction**: Device → Dashboard

```json
{
  "device_id": "glasses_01",
  "battery": 85,
  "wifi_rssi": -60,
  "status": "recording",
  "vad_energy": 450,
  "uptime": 3600
}
```

| Field | Type | Description |
|-------|------|-------------|
| device_id | string | Unique device identifier |
| battery | int | Battery percentage (0-100) |
| wifi_rssi | int | WiFi signal strength (dBm) |
| status | string | "idle", "recording", "error" |
| vad_energy | int | Current VAD energy level |
| uptime | int | Device uptime in seconds |

### 2.4 Subject Mode
**Topic**: `classlink/mode`
**Direction**: Dashboard → AI Service

```json
{
  "mode": "science" | "literature"
}
```

---

## 3. REST API Messages

### 3.1 WiFi Scan Response
**Endpoint**: `GET /api/wifi/scan`

```json
{
  "success": true,
  "networks": [
    {
      "ssid": "MyWiFi",
      "rssi": -45,
      "encryption": "WPA2"
    }
  ]
}
```

### 3.2 WiFi Connect Request
**Endpoint**: `POST /api/wifi/connect`

```json
{
  "ssid": "MyWiFi",
  "password": "secret123"
}
```

### 3.3 System Status Response
**Endpoint**: `GET /api/status`

```json
{
  "system": "online",
  "devices": [
    {
      "id": "glasses_01",
      "status": "connected",
      "battery": 85
    }
  ],
  "ai_core": "online",
  "current_mode": "science"
}
```
