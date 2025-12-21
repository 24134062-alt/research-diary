# ClassLink - Mic Remote Controller

Microphone từ xa cho giáo viên, thu âm và gửi đến hệ thống.

## Phần cứng

| Linh kiện | Model | Chức năng |
|-----------|-------|-----------|
| MCU | ESP32-DevKitC | Xử lý chính |
| Microphone | INMP441 (I2S) | Thu âm giọng nói |
| Button | 1 nút nhấn | Kích hoạt AI |
| LED | Built-in GPIO 2 | Báo trạng thái |
| Pin | Li-Po 3.7V | Nguồn di động |

> **KHÔNG CÓ OLED** - Chỉ dùng LED để báo trạng thái

## Sơ đồ chân (Pinout)

### I2S Microphone (INMP441)
| Pin INMP441 | ESP32 GPIO | Mô tả |
|-------------|------------|-------|
| WS | GPIO 25 | Word Select |
| SD | GPIO 32 | Serial Data |
| SCK | GPIO 33 | Serial Clock |
| VDD | 3.3V | Nguồn |
| GND | GND | Mass |
| L/R | GND | Kênh trái |

### Controls
| Chức năng | GPIO | Mô tả |
|-----------|------|-------|
| AI Button | 12 | Nhấn để hỏi AI |
| LED Status | 2 | Built-in LED |
| Battery | 34 | Đọc pin (ADC) |

## Chức năng

### Nút AI
- **Nhấn 1 lần**: Bật chế độ AI - audio gửi đến AI xử lý
- **Nhấn lần nữa**: Tắt chế độ AI

### LED Status
| Trạng thái LED | Ý nghĩa |
|----------------|---------|
| Nhấp nháy nhanh (200ms) | Đang ở chế độ AI |
| Sáng liên tục | Đã kết nối WiFi |
| Tắt | Mất kết nối |

### Battery
- Đọc qua ADC GPIO 34
- Range: 3.0V (0%) → 4.2V (100%)

## Kết nối

```
Mic Remote (ESP32)
    │
    ├── WiFi → "CLASS-BOX" (ESP32 Box)
    │          Password: 12345678
    │
    ├── UDP 12345 → Gửi audio đến Box
    │
    └── MQTT 1883 → Điều khiển từ Raspberry Pi
         Topics:
           - device/mic_remote/ai  (gửi start/stop)
           - audio/control         (nhận start/stop)
```

## Cấu trúc file

```
mic_remote/
├── platformio.ini      # PlatformIO config
├── include/
│   ├── i2s_mic.h        # I2S header
│   └── uplink_audio.h   # Audio uplink header
└── src/
    ├── main.cpp         # Code chính
    ├── i2s_mic.cpp      # I2S microphone driver
    └── uplink_audio.cpp # UDP audio sender
```

## Build & Flash

```bash
cd mic_remote
pio run -t upload
pio device monitor
```

## MQTT Topics

| Topic | Direction | Payload |
|-------|-----------|---------|
| `device/mic_remote/ai` | → Gửi | `"start"` hoặc `"stop"` |
| `audio/control` | ← Nhận | `"start"` hoặc `"stop"` |

## So sánh với Glasses

| Tính năng | Mic Remote | Glasses |
|-----------|------------|---------|
| OLED | ❌ Không có | ✅ Có |
| Số nút | 1 (AI) | 2 (Mode + AI) |
| Hiển thị text | ❌ | ✅ |
| Thu âm | ✅ | ✅ |
| Pin | ✅ Li-Po | Có thể có |

---

**Last Updated**: 2025-12-21
