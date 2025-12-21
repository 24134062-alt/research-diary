# ClassLink Raspberry Pi Setup

Hướng dẫn cài đặt và cấu hình Raspberry Pi cho hệ thống ClassLink Audio System.

## 🌐 Truy cập nhanh

Sau khi cài đặt, kết nối WiFi **"ClassLink-Setup"** (password: `classlink2024`) và truy cập:

> **http://classlink.local:8000**

## Mục lục

- [Yêu cầu phần cứng](#yêu-cầu-phần-cứng)
- [Chuẩn bị](#chuẩn-bị)
- [Cài đặt](#cài-đặt)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Quản lý mạng](#quản-lý-mạng)
- [Services](#services)
- [Troubleshooting](#troubleshooting)

---

## Yêu cầu phần cứng

| Thành phần | Yêu cầu | Khuyến nghị |
|------------|---------|------------|
| Raspberry Pi | Pi 3B+ trở lên | Pi 4 (2GB RAM) |
| SD Card | 8GB Class 10 | 16GB+ |
| Nguồn | 5V 2.5A | 5V 3A (Pi 4) |
| WiFi | Built-in | Built-in |

## Chuẩn bị

### 1. Flash Raspberry Pi OS

1. Tải [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Chọn **Raspberry Pi OS Lite (64-bit)**
3. Nhấn ⚙️ (Settings) để cấu hình:
   - **Hostname**: `classlink`
   - **Enable SSH**: ✅ (Use password authentication)
   - **Username/Password**: `pi` / `<your-password>`
   - **Locale**: Asia/Ho_Chi_Minh
4. Flash vào SD Card

### 2. Kết nối lần đầu

```bash
# Tìm IP của Raspberry Pi (qua router hoặc dùng nmap)
nmap -sn 192.168.1.0/24 | grep -i raspberry

# SSH vào
ssh pi@classlink.local
# hoặc
ssh pi@<IP_ADDRESS>
```

---

## Cài đặt

### Cài đặt tự động (Khuyến nghị)

```bash
# Clone repository
git clone https://github.com/yourusername/research-diary.git
cd "research-diary/ClassLink Audio System/box/raspberry"

# Chạy script cài đặt
chmod +x install.sh
sudo ./install.sh
```

### Cài đặt thủ công

#### 1. Cài đặt dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    python3-pip python3-venv \
    network-manager \
    git
```

#### 2. Cấu hình NetworkManager

```bash
# Tắt dhcpcd, dùng NetworkManager
sudo systemctl stop dhcpcd
sudo systemctl disable dhcpcd
sudo systemctl enable NetworkManager
sudo systemctl start NetworkManager
```

#### 3. Copy files

```bash
# Tạo thư mục
sudo mkdir -p /opt/classlink/{net,api}

# Copy scripts
sudo cp net/* /opt/classlink/net/
sudo chmod +x /opt/classlink/net/*

# Copy services
sudo cp services/*.service /etc/systemd/system/
sudo cp services/*.timer /etc/systemd/system/
```

#### 4. Thiết lập Python environment

```bash
# Tạo virtual environment
python3 -m venv /opt/classlink/venv

# Cài packages
/opt/classlink/venv/bin/pip install \
    fastapi uvicorn pydantic pyyaml
```

#### 5. Enable services

```bash
sudo systemctl daemon-reload
sudo systemctl enable box-net.service
sudo systemctl enable box-api.service
sudo systemctl enable box-watchdog.timer
sudo reboot
```

---

## Cấu trúc thư mục

```
/opt/classlink/
├── net/                    # Network scripts
│   ├── box-ap-on          # Bật Access Point mode
│   ├── box-ap-off         # Tắt Access Point mode
│   ├── box-wifi-scan      # Quét WiFi
│   ├── box-wifi-connect   # Kết nối WiFi
│   ├── box-net-boot       # Boot script
│   ├── box-net-reset      # Reset network config
│   └── box-wifi-watchdog  # Giám sát kết nối
├── api/                    # Web Dashboard (FastAPI)
│   └── app/
└── venv/                   # Python virtual environment
```

---

## Quản lý mạng

### Chế độ hoạt động

Raspberry Pi có 2 chế độ mạng:

| Chế độ | Mô tả | Khi nào sử dụng |
|--------|-------|-----------------|
| **AP Mode** | Phát WiFi "ClassLink-Setup" | Cấu hình lần đầu, mất kết nối |
| **Client Mode** | Kết nối vào WiFi người dùng | Hoạt động bình thường |

### Các lệnh thường dùng

```bash
# Bật Access Point
sudo /opt/classlink/net/box-ap-on

# Tắt Access Point
sudo /opt/classlink/net/box-ap-off

# Quét WiFi
/opt/classlink/net/box-wifi-scan

# Kết nối WiFi
sudo /opt/classlink/net/box-wifi-connect "SSID" "password"

# Reset về AP mode (xóa tất cả WiFi đã lưu)
sudo /opt/classlink/net/box-net-reset
```

### Luồng khởi động

```
Power On
    │
    ▼
box-net-boot
    │
    ├── Có WiFi đã lưu?
    │       │
    │       ├── Có → Kết nối → Thành công? ─► Client Mode
    │       │                       │
    │       │                       └── Thất bại ─┐
    │       │                                      │
    │       └── Không ────────────────────────────┤
    │                                              │
    │ ◄────────────────────────────────────────────┘
    ▼
AP Mode (ClassLink-Setup)
```

---

## Services

### Danh sách services

| Service | Mô tả | Port |
|---------|-------|------|
| `box-net.service` | Quản lý mạng khi boot | - |
| `box-api.service` | Web Dashboard | 8000 |
| `box-watchdog.timer` | Giám sát WiFi | - |
| `box-uart.service` | Giao tiếp ESP32 | - |

### Quản lý services

```bash
# Xem status
sudo systemctl status box-api

# Xem logs
sudo journalctl -u box-api -f

# Restart service
sudo systemctl restart box-api

# Stop service
sudo systemctl stop box-api
```

---

## Troubleshooting

### Không tìm thấy WiFi "ClassLink-Setup"

```bash
# Kiểm tra hostapd/NetworkManager
sudo systemctl status NetworkManager

# Kiểm tra WiFi interface
nmcli device status

# Kiểm tra rfkill
rfkill list
sudo rfkill unblock wifi
```

### Không kết nối được WiFi

```bash
# Quét lại WiFi
nmcli device wifi rescan

# Xem danh sách
nmcli device wifi list

# Kiểm tra log
sudo journalctl -u NetworkManager -n 50
```

### Web Dashboard không truy cập được

```bash
# Kiểm tra service
sudo systemctl status box-api

# Kiểm tra port
ss -tlnp | grep 8000

# Xem log
sudo journalctl -u box-api -n 50
```

### Reset hoàn toàn

```bash
# Reset network và quay về AP mode
sudo /opt/classlink/net/box-net-reset -y

# Hoặc cài đặt lại từ đầu
sudo rm -rf /opt/classlink
# Chạy lại install.sh
```

---

## Thông tin kết nối mặc định

| Thông tin | Giá trị |
|-----------|---------|
| AP SSID | ClassLink-Setup |
| AP Password | classlink2024 |
| AP IP | 192.168.4.1 |
| Web Dashboard | http://192.168.4.1:8000 |

---

**Created**: 2025-12-21  
**Last Updated**: 2025-12-21
