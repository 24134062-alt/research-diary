# Hướng Dẫn Cài Đặt Service Tự Động Khởi Động

## Mục đích
Cấu hình FastAPI web server tự động chạy khi Raspberry Pi khởi động, không cần chạy lệnh thủ công.

---

## Bước 1: Tạo Systemd Service File

```bash
sudo nano /etc/systemd/system/classlink-web.service
```

**Nội dung file:**

```ini
[Unit]
Description=ClassLink Audio Manager Web Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/research-diary/ClassLink Audio System/box/raspberry/api/app
Environment="PATH=/home/pi/research-diary/ClassLink Audio System/box/raspberry/api/venv/bin"
ExecStart=/home/pi/research-diary/ClassLink Audio System/box/raspberry/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Lưu file:** `Ctrl + X`, `Y`, `Enter`

---

## Bước 2: Kích Hoạt Service

```bash
# Reload systemd để nhận diện service mới
sudo systemctl daemon-reload

# Kích hoạt service tự động chạy khi boot
sudo systemctl enable classlink-web

# Khởi động service ngay lập tức
sudo systemctl start classlink-web
```

---

## Bước 3: Kiểm Tra Trạng Thái

```bash
# Xem trạng thái service
sudo systemctl status classlink-web

# Xem log realtime
sudo journalctl -u classlink-web -f

# Xem 50 dòng log gần nhất
sudo journalctl -u classlink-web -n 50
```

---

## Các Lệnh Quản Lý Service

```bash
# Khởi động service
sudo systemctl start classlink-web

# Dừng service
sudo systemctl stop classlink-web

# Khởi động lại service
sudo systemctl restart classlink-web

# Xem trạng thái
sudo systemctl status classlink-web

# Vô hiệu hóa tự động khởi động
sudo systemctl disable classlink-web

# Kích hoạt lại tự động khởi động
sudo systemctl enable classlink-web
```

---

## Kiểm Tra Sau Khi Cài Đặt

1. **Khởi động lại Raspberry Pi:**
   ```bash
   sudo reboot
   ```

2. **Sau khi boot xong (30-60s), kiểm tra:**
   ```bash
   sudo systemctl status classlink-web
   ```

3. **Truy cập web từ trình duyệt:**
   ```
   http://raspberrypi.local:8000
   ```

---

## Khắc Phục Sự Cố

### Service không khởi động

```bash
# Xem log lỗi chi tiết
sudo journalctl -u classlink-web -n 100 --no-pager

# Kiểm tra cú pháp file service
sudo systemd-analyze verify /etc/systemd/system/classlink-web.service
```

### Service bị crash liên tục

```bash
# Chạy thủ công để xem lỗi
cd "/home/pi/research-diary/ClassLink Audio System/box/raspberry/api/app"
source ../../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Lưu Ý Quan Trọng

1. **Đường dẫn phải chính xác:**
   - WorkingDirectory
   - Environment PATH
   - ExecStart
   
2. **User `pi` phải có quyền:**
   - Đọc/ghi thư mục dự án
   - Thực thi uvicorn

3. **Port 8000 phải khả dụng:**
   - Không có service nào khác dùng port 8000

---

**Hoàn tất!** Service giờ sẽ tự động chạy mỗi khi Raspberry Pi khởi động.
