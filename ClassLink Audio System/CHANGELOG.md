# CHANGELOG

All notable changes to ClassLink Audio System will be documented in this file.

## [2024-12-19] - ESP32 Box & System Configuration

### TÓM TẮT KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLASSLINK AUDIO SYSTEM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [Glasses/Mic] ─── WiFi "CLASS-BOX" ──► [ESP32 Box]                       │
│         │                                     │                             │
│         │ UDP Audio (Port 12345)              │ UART (Serial)               │
│         ▼                                     ▼                             │
│   [Teacher PC] ◄─── MQTT (Port 1883) ───► [Raspberry Pi]                   │
│                        (cùng mạng LAN)                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### LUỒNG KHỞI ĐỘNG

1. **Ban đầu**: Raspberry Pi phát WiFi `ClassLink-Setup`
2. **Giáo viên kết nối**: Vào `http://192.168.4.1:8000` để cấu hình
3. **Cấu hình WiFi**: Chọn mạng trường/lớp học, Raspberry Pi tắt hotspot
4. **PC giáo viên**: Kết nối cùng mạng với Raspberry Pi
5. **Truy cập**: `http://classlink.local:8000` (tên cố định, dễ nhớ)

### Added
- **ESP32 Box AP Mode**: ESP32 phát WiFi "CLASS-BOX" (pass: 12345678) để Glasses/Mic kết nối
- **Hostname Setup Script**: `box/raspberry/setup-hostname.sh` - Đặt hostname `classlink.local`
- **Mic Remote**: Không có OLED (đã sửa documentation)

### Changed
- `box/esp-32_box/platformio.ini`: Sửa board từ `esp32-s3` thành `esp32dev` (đúng chip ESP32-D0WD-V3)
- `box/esp-32_box/src/main.cpp`: Chuyển sang AP mode, gọi wifi_init() thay vì kết nối WiFi ngoài
- `box/esp-32_box/src/uart_ctrl.cpp`: Thêm forward declaration
- `box/esp-32_box/src/audio_forward.cpp`: Thêm forward declaration
- `DEPLOYMENT_GUIDE.md`: Cập nhật URL thành `classlink.local`

### Kết nối các thành phần
| Thiết bị | Vai trò | Kết nối |
|----------|---------|---------|
| ESP32 Box | WiFi AP cho Glasses/Mic | UART với Raspberry Pi |
| Raspberry Pi | Web Dashboard (Port 8000), MQTT Bridge | Network với PC |
| Glasses/Mic | Thu audio, hiển thị text | WiFi vào ESP32 AP |
| Teacher PC | STT + AI Processing | Cùng mạng với Raspberry |

### HAI MẠNG WIFI KHÁC NHAU

| | **ESP32 Box** | **Raspberry Pi** |
|---|---|---|
| **Tên mạng** | `CLASS-BOX` | `ClassLink-Setup` |
| **Mật khẩu** | `12345678` | `classlink2024` |
| **Mục đích** | Cho **Kính/Mic** kết nối | Cho **Giáo viên** cấu hình |
| **Khi nào hoạt động** | **Luôn bật** | **Chỉ lúc ban đầu** (sau đó tắt) |
| **Thiết bị kết nối** | Glasses, Mic Remote | Laptop/Điện thoại giáo viên |

> ⚠️ **Lưu ý**: Hai mạng hoạt động **độc lập**, không liên quan đến nhau!

### Mật khẩu Admin
- **Code update**: `admin123` (file: `box/raspberry/api/app/routes/system.py`)
- **WiFi AP Raspberry**: `classlink2024` (file: `box/raspberry/config.example.yaml`)
- **WiFi AP ESP32**: `12345678` (file: `box/esp-32_box/src/wifi_ap_sta.cpp`)

## [2024-12-18] - Web Dashboard UI Update

### Added
- **Notification Badge**: Added notification badge to "Giám Sát & Trợ Lý AI" button
  - Shows count of new student messages when modal is closed
  - Badge clears when modal is opened
  - Badge animates with pulse effect for visibility

- **Mic Remote Panel**: New panel on dashboard showing teacher's mic transcription
  - Real-time display of teacher's voice-to-text from Mic Remote device
  - "Đang thu" status indicator
  - Clear transcription button
  - Broadcast TTS status tags

- **AI Processing Pipeline Documentation**: Updated ARCHITECTURE.md with detailed dual-AI system
  - AI Hỗ Trợ Giáo Viên: Text preprocessing (STT error correction, text normalization, content filtering)
  - AI Trợ Giảng: Question answering for students

### Changed
- `index.html`: Added chat-badge span, mic-transcription-area panel
- `app.js`: Added `updateChatBadge()`, `clearMicTranscription()`, `addMicTranscription()` functions

### Files Modified
- `box/raspberry/api/app/static/index.html`
- `box/raspberry/api/app/static/app.js`
- `ARCHITECTURE.md`
