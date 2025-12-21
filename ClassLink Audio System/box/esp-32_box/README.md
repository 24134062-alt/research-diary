# ClassLink - ESP32 Box Controller

Hub trung tâm phát WiFi riêng cho hệ thống kính và mic kết nối.

## Vai trò

```
┌─────────────┐     WiFi "CLASS-BOX"     ┌─────────────────┐
│   Glasses   │ ◄──────────────────────► │                 │
│   (ESP32)   │     UDP Audio            │   ESP32 Box     │
└─────────────┘                          │                 │
                                         │    ┌──────┐     │
┌─────────────┐     WiFi "CLASS-BOX"     │    │ WiFi │     │
│ Mic Remote  │ ◄──────────────────────► │    │  AP  │     │
│   (ESP32)   │     UDP Audio            │    └──────┘     │
└─────────────┘                          │        │        │
                                         │        │ UART   │
                                         │        ▼        │
                                         │  ┌──────────┐   │
                                         │  │ TX/RX    │   │
                                         │  └──────────┘   │
                                         └────────│────────┘
                                                  │
                                                  ▼ USB/UART
                                         ┌─────────────────┐
                                         │  Raspberry Pi   │
                                         └─────────────────┘
```

## Phần cứng

| Linh kiện | Model | Chức năng |
|-----------|-------|-----------|
| MCU | ESP32-DevKitC (ESP32-D0WD-V3) | Xử lý chính |
| LED | Built-in GPIO 2 | Báo trạng thái |

> **Lưu ý**: Đây là ESP32 thường (KHÔNG phải ESP32-S3)

## Sơ đồ chân

### UART với Raspberry Pi
| Pin ESP32 | Raspberry Pi | Mô tả |
|-----------|--------------|-------|
| TX (GPIO 1) | RX (GPIO 15) | ESP32 → Pi |
| RX (GPIO 3) | TX (GPIO 14) | Pi → ESP32 |
| GND | GND | Mass chung |

### Status LED
| Pin | GPIO | Mô tả |
|-----|------|-------|
| LED | 2 | Nhấp nháy = đang chạy |

## Chức năng

### 1. WiFi Access Point
- **SSID**: `CLASS-BOX`
- **Password**: `12345678`
- **IP**: `192.168.4.1`

### 2. Audio Forward
- Nhận audio UDP từ Glasses/Mic (port 12345)
- Forward qua UART đến Raspberry Pi

### 3. Device Gateway
- Quản lý các thiết bị kết nối
- Theo dõi online/offline

### 4. UART Control
- Giao tiếp với Raspberry Pi
- Baud rate: 115200

## Cấu trúc file

```
box/esp-32_box/
├── platformio.ini       # Config (ESP32-DevKitC)
├── include/
│   └── .gitkeep
└── src/
    ├── main.cpp           # Entry point
    ├── wifi_ap_sta.cpp    # WiFi AP mode
    ├── uart_ctrl.cpp      # UART với Raspberry Pi
    ├── audio_forward.cpp  # Forward audio
    └── dev_gateway.cpp    # Quản lý thiết bị
```

## Build & Flash

```bash
cd box/esp-32_box
pio run -t upload
pio device monitor
```

## Lưu ý quan trọng

1. **Nguồn điện**: ESP32 Box cấp nguồn qua USB từ Raspberry Pi
2. **UART**: TX/RX nối chéo với Raspberry Pi
3. **Không có MQTT client**: ESP32 Box chỉ forward dữ liệu, không xử lý MQTT

---

**Last Updated**: 2025-12-21
