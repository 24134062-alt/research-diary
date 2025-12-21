# ClassLink - PC Services

Các dịch vụ chạy trên máy tính giáo viên: STT (Speech-to-Text) và AI Assistant.

## Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                       PC Giáo viên                               │
│                                                                   │
│  ┌─────────────────┐         ┌─────────────────────────────────┐ │
│  │   STT Service   │         │        AI Service               │ │
│  │                 │         │                                 │ │
│  │  UDP 12345 ◄────┼─────────┼─ Audio từ Glasses/Mic           │ │
│  │       │         │         │                                 │ │
│  │       ▼         │  MQTT   │  ┌───────────────────────────┐  │ │
│  │  Whisper/Vosk   │ -------►│  │ AI Hỗ Trợ Giáo Viên      │  │ │
│  │       │         │         │  │ - Sửa lỗi STT            │  │ │
│  │       ▼         │         │  │ - Chuẩn hóa số/ký hiệu    │  │ │
│  │  Text Output    │         │  └───────────────────────────┘  │ │
│  │       │         │         │                                 │ │
│  │       ▼         │         │  ┌───────────────────────────┐  │ │
│  │     MQTT        │         │  │ AI Trợ Giảng (Optional)   │  │ │
│  │  glasses/text   │         │  │ - Trả lời câu hỏi học sinh│  │ │
│  └─────────────────┘         │  └───────────────────────────┘  │ │
│                               └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Cấu trúc

```
pc/
├── stt_service/        # Speech-to-Text
│   ├── server.py       # Main STT server
│   ├── stt_engine.py   # Whisper/Vosk wrapper
│   ├── receiver_udp.py # Nhận audio UDP
│   ├── jitter_buffer.py # Buffer xử lý jitter
│   └── send_result.py  # Gửi kết quả MQTT
│
├── ai_service/         # AI Processing
│   ├── main.py         # Main AI service
│   ├── ai_assistant.py # AI logic (Gemini/OpenAI)
│   └── document_processor.py # Xử lý tài liệu
│
└── installer/          # Scripts cài đặt
```

---

## STT Service

### Chức năng
- Nhận audio từ UDP port 12345
- Chuyển đổi giọng nói → văn bản
- Gửi text qua MQTT

### Engine hỗ trợ
| Engine | Ưu điểm | Nhược điểm |
|--------|---------|------------|
| **Whisper** | Chính xác cao | Cần GPU, chậm hơn |
| **Vosk** | Nhanh, offline | Ít chính xác hơn |

### Cài đặt

```bash
cd pc/stt_service
pip install -r requirements.txt

# Chạy server
python server.py
```

### Cấu hình

Sửa file `config.yaml`:
```yaml
udp_port: 12345
mqtt_host: "192.168.4.1"
mqtt_port: 1883
engine: "whisper"  # hoặc "vosk"
model: "base"      # tiny, base, small, medium, large
```

---

## AI Service

### Chức năng

1. **AI Hỗ Trợ Giáo Viên** (luôn bật)
   - Sửa lỗi STT (ví dụ: "chinh tri" → "chính trị")
   - Chuẩn hóa số (ví dụ: "ba cộng hai" → "3 + 2" cho môn Toán)
   - Lọc nội dung không phù hợp

2. **AI Trợ Giảng** (bật/tắt)
   - Trả lời câu hỏi học sinh
   - Giải thích khái niệm
   - Có thể dùng tài liệu bài giảng

### Cài đặt

```bash
cd pc/ai_service

# Copy config
cp .env.example config.env
# Sửa API key trong config.env

pip install -r requirements.txt

# Chạy service
python main.py
```

### Cấu hình (`config.env`)

```env
# API Keys (chọn 1)
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# MQTT
MQTT_HOST=192.168.4.1
MQTT_PORT=1883

# Subject mode
SUBJECT_MODE=math   # math hoặc literature
```

### MQTT Topics

| Topic | Direction | Mô tả |
|-------|-----------|-------|
| `audio/transcription` | ← Nhận | Text từ STT Service |
| `glasses/text` | → Gửi | Text đã xử lý đến Glasses |
| `ai/question` | ← Nhận | Câu hỏi từ học sinh |
| `ai/answer` | → Gửi | Trả lời cho học sinh |
| `ai/mode` | ← Nhận | `math` hoặc `literature` |

---

## Yêu cầu hệ thống

| Thành phần | Yêu cầu tối thiểu | Khuyến nghị |
|------------|-------------------|-------------|
| OS | Windows 10 / Linux | Windows 11 |
| RAM | 4GB | 8GB+ |
| GPU | Không bắt buộc | NVIDIA (cho Whisper) |
| Python | 3.9+ | 3.10+ |
| Network | Cùng mạng với Raspberry Pi | LAN |

---

## Khởi động dịch vụ

### Windows

```powershell
# Terminal 1: STT Service
cd pc/stt_service
python server.py

# Terminal 2: AI Service
cd pc/ai_service
python main.py
```

### Chạy như Service (Advanced)

Xem file `SETUP_SERVICE.md` trong thư mục gốc.

---

**Last Updated**: 2025-12-21
