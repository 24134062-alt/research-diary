# Text Downlink Module - ESP32 Box

## 📥 Chức năng

Module `text_downlink.cpp` cho phép ESP32 Box **nhận text từ Raspberry Pi qua UART** và **forward đến Glasses/Mic Remote qua MQTT**.

## 🔄 Luồng dữ liệu

```
AI Service
   ↓
Raspberry Pi
   ↓ UART (JSON)
ESP32 Box (text_downlink.cpp)
   ↓ MQTT
Glasses OLED Display
```

---

## 📝 Message Format

### Input từ Raspberry Pi (UART)

```json
{
  "type": "TEXT_DOWNLINK",
  "target": "glasses_01",
  "text": "Câu trả lời từ AI Trợ Giảng"
}
```

| Field | Required | Mô tả |
|-------|----------|-------|
| `type` | ✅ Yes | Phải là `"TEXT_DOWNLINK"` |
| `target` | ❌ No | Device ID (nếu không có → broadcast) |
| `text` | ✅ Yes | Nội dung text cần hiển thị |

### Output qua MQTT

**Topic broadcast** (nếu không có target):
- Topic: `glasses/text`
- Payload: `"Câu trả lời từ AI Trợ Giảng"`

**Topic specific device** (nếu có target):
- Topic: `glasses/glasses_01/text`
- Payload: `"Câu trả lời từ AI Trợ Giảng"`

---

## 🔧 API Functions

### 1. Initialization

```cpp
void text_downlink_init()
```

- Khởi tạo MQTT client
- Kết nối đến MQTT broker (192.168.4.1:1883)
- Tự động reconnect nếu mất kết nối

**Gọi trong:** `main.cpp::setup()`

### 2. Loop Maintenance

```cpp
void text_downlink_loop()
```

- Duy trì kết nối MQTT
- Tự động reconnect khi ngắt kết nối

**Gọi trong:** `main.cpp::loop()`

### 3. Handle Text from UART

```cpp
void text_downlink_handle(const String &jsonMessage)
```

- Parse JSON message từ UART
- Extract `target` và `text` fields
- Publish text lên MQTT topic tương ứng

**Gọi trong:** `uart_ctrl.cpp::handle_uart_line()`

### 4. Direct Send (Alternative API)

```cpp
void text_downlink_send(const char* deviceId, const char* text)
```

- API đơn giản để gửi text trực tiếp
- `deviceId`: NULL để broadcast, hoặc ID cụ thể
- `text`: Nội dung text

---

## 📊 Serial Log Output

### Khi khởi động:
```
[TEXT_DOWNLINK] Initializing MQTT client...
[TEXT_DOWNLINK] Connecting to MQTT... Connected!
[TEXT_DOWNLINK] MQTT ready for text forwarding
```

### Khi nhận text từ UART:
```
[UART][RX] {"type":"TEXT_DOWNLINK","target":"glasses_01","text":"Hello"}
[UART] Forwarding text to glasses...
[TEXT_DOWNLINK] Received: {"type":"TEXT_DOWNLINK","target":"glasses_01","text":"Hello"}
[TEXT_DOWNLINK][OK] Published to 'glasses/glasses_01/text': Hello
```

### Khi MQTT reconnect:
```
[TEXT_DOWNLINK] MQTT reconnected
```

---

## ⚙️ Configuration

### MQTT Broker

```cpp
// text_downlink.cpp
static const char* MQTT_SERVER = "192.168.4.1";  // IP của Raspberry Pi
static const int MQTT_PORT = 1883;
```

Sửa `MQTT_SERVER` nếu Raspberry Pi dùng IP khác.

### MQTT Client ID

```cpp
mqttClient->connect("ESP32_Box_TextDownlink")
```

ID này phải **unique** trên broker.

---

## 🧪 Testing

### Test 1: Từ Raspberry Pi

Gửi JSON qua UART (Serial):

```bash
# Trên Raspberry Pi
echo '{"type":"TEXT_DOWNLINK","text":"Test message"}' > /dev/serial0
```

### Test 2: Monitor MQTT

```bash
# Subscribe MQTT topic
mosquitto_sub -h 192.168.4.1 -t "glasses/text" -v
```

### Test 3: Từ code Raspberry Pi

```python
import serial

ser = serial.Serial('/dev/serial0', 115200)
msg = '{"type":"TEXT_DOWNLINK","target":"glasses_01","text":"Hello from Pi"}\n'
ser.write(msg.encode())
ser.close()
```

---

## 🚨 Troubleshooting

### "MQTT not connected, message dropped"

**Nguyên nhân:**
- ESP32 chưa kết nối được MQTT broker
- Raspberry Pi chưa chạy MQTT broker (Mosquitto)

**Giải pháp:**
```bash
# Kiểm tra Mosquitto đang chạy
sudo systemctl status mosquitto

# Khởi động Mosquitto
sudo systemctl start mosquitto

# Kiểm tra ESP32 có ping được Pi không
ping 192.168.4.1
```

### "No text content found in message"

**Nguyên nhân:**
- JSON message không có field `"text"`
- JSON format sai

**Giải pháp:**
- Đảm bảo JSON có field `"text"` với nội dung hợp lệ
- Kiểm tra escape characters (`\"`)

### MQTT publish failed

**Nguyên nhân:**
- Text quá dài (> 128 bytes)
- MQTT buffer full

**Giải pháp:**
- Giới hạn độ dài text trong Python/Raspberry Pi
- Tăng MQTT buffer size trong `platformio.ini`:

```ini
[env:esp32box]
build_flags =
    -D MQTT_MAX_PACKET_SIZE=512
```

---

## 📈 Future Improvements

- [ ] Support JSON format cho MQTT payload (hiện tại chỉ plain text)
- [ ] Add QoS level configuration
- [ ] Add message queue khi MQTT offline
- [ ] Support multi-broker failover
- [ ] Add encryption cho sensitive messages

---

**Created**: 2026-01-19  
**Last Updated**: 2026-01-19  
**Status**: ✅ Hoàn thành và sẵn sàng sử dụng
