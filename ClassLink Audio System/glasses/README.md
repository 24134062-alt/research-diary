# ClassLink - Smart Glasses (ESP32-S3)

Kính thông minh cho học sinh, hiển thị text từ giáo viên và AI.

## Phần cứng

| Linh kiện | Model | Chức năng |
|-----------|-------|-----------|
| MCU | ESP32-S3-DevKitC-1 | Xử lý chính |
| Microphone | INMP441 (I2S) | Thu âm giọng học sinh |
| Display | SSD1306 OLED 128x64 | Hiển thị text |
| Buttons | 2 nút nhấn | Điều khiển chế độ |

## Sơ đồ chân (Pinout)

### I2S Microphone (INMP441)
| Pin INMP441 | ESP32 GPIO | Mô tả |
|-------------|------------|-------|
| WS | GPIO 25 | Word Select |
| SD | GPIO 34 | Serial Data |
| SCK | GPIO 26 | Serial Clock |
| VDD | 3.3V | Nguồn |
| GND | GND | Mass |
| L/R | GND | Kênh trái |

### OLED Display (SSD1306)
| Pin OLED | ESP32 GPIO | Mô tả |
|----------|------------|-------|
| SDA | GPIO 21 | I2C Data |
| SCL | GPIO 22 | I2C Clock |
| VCC | 3.3V | Nguồn |
| GND | GND | Mass |

### Buttons
| Nút | GPIO | Chức năng |
|-----|------|-----------|
| Nút 1 | GPIO 32 | Toggle Class ↔ Private |
| Nút 2 | GPIO 33 | Toggle AI Trợ Giảng |

> **Lưu ý**: Nút nối từ GPIO xuống GND, sử dụng INPUT_PULLUP

## Chức năng

### Nút 1 - Mode Toggle
- **CLASS**: Phát audio cho cả lớp nghe (qua loa)
- **PRIVATE**: Chỉ hiển thị text trên kính (riêng tư)

### Nút 2 - AI Toggle  
- **ON**: Bật AI Trợ Giảng - trả lời câu hỏi học sinh
- **OFF**: Tắt AI Trợ Giảng

## Kết nối

```
Glasses (ESP32-S3)
    │
    ├── WiFi → "CLASS-BOX" (ESP32 Box)
    │          Password: 12345678
    │
    ├── UDP 12345 → Gửi audio đến Box
    │
    └── MQTT 1883 → Nhận text từ Raspberry Pi
         Topics:
           - glasses/text  (nhận text hiển thị)
           - glasses/mode  (gửi trạng thái mode)
           - glasses/ai    (gửi trạng thái AI)
```

## Cấu hình

1. Copy `include/config.example.h` → `include/config.h`
2. Sửa các giá trị theo môi trường của bạn
3. `config.h` được gitignore (không push lên Git)

## Build & Flash

```bash
# Cần PlatformIO
cd glasses
pio run -t upload
pio device monitor
```

## Cấu trúc file

```
glasses/
├── platformio.ini      # PlatformIO config
├── include/
│   ├── config.example.h  # Template cấu hình
│   └── vad.h            # Voice Activity Detection header
└── src/
    ├── main.cpp         # Code chính (tất cả logic)
    └── vad.cpp          # VAD implementation
```

## MQTT Topics

| Topic | Direction | Payload |
|-------|-----------|---------|
| `glasses/text` | ← Nhận | Text từ AI để hiển thị |
| `glasses/mode` | → Gửi | `"class"` hoặc `"private"` |
| `glasses/ai` | → Gửi | `"on"` hoặc `"off"` |
| `audio/control` | ← Nhận | `"start"` hoặc `"stop"` |

---

**Last Updated**: 2025-12-21
