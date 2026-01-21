# 🚀 Deploy Code to Raspberry Pi - Quick Guide

## 📋 Bước 1: SSH vào Raspberry Pi

```bash
# Kết nối SSH (thay <IP> bằng IP thực tế)
ssh pi@<IP>
# Ví dụ: ssh pi@192.168.4.1
# Hoặc: ssh pi@classlink.local

# Nhập password khi được hỏi (mặc định: raspberry)
```

---

## 🌐 Bước 1.5: Setup mDNS (KHUYẾN NGHỊ - Chỉ cần làm 1 lần)

**Vấn đề**: IP thay đổi mỗi khi đổi WiFi → Khó truy cập  
**Giải pháp**: Dùng tên miền `.local` cố định → Truy cập `http://classlink.local:8000`

### Cài đặt tự động:

```bash
# SSH vào Pi
ssh pi@<IP>

# Download và chạy script
cd /opt/classlink
sudo bash box/raspberry/setup_mdns.sh

# Sau khi setup xong, reboot Pi
sudo reboot
```

### Sau khi reboot:

✅ **Truy cập bằng tên miền** thay vì IP:
```
http://classlink.local:8000
```

✅ **Hoạt động với mọi WiFi** - không cần biết IP nữa!

> **Lưu ý Windows**: Cần cài [Bonjour](https://support.apple.com/kb/DL999) (hoặc iTunes có sẵn Bonjour)

---

## 📂 Bước 2: Copy file app.js mới lên Pi

### Cách 1: Dùng SCP (từ Windows PowerShell)

```powershell
# Mở PowerShell tại thư mục research-diary-1
cd "C:\Users\DELL\research-diary-1"

# Copy file app.js
scp "ClassLink Audio System\box\raspberry\api\app\static\app.js" pi@<IP>:/opt/classlink/api/app/static/app.js

# Ví dụ:
scp "ClassLink Audio System\box\raspberry\api\app\static\app.js" pi@192.168.4.1:/opt/classlink/api/app/static/app.js
```

### Cách 2: Dùng Git Pull (nếu Pi có git)

```bash
# SSH vào Pi trước
ssh pi@<IP>

# Di chuyển vào thư mục code
cd /opt/classlink/api

# Pull code mới từ GitHub
git pull origin main

# Hoặc clone lại nếu chưa có
# cd /opt/classlink
# git clone https://github.com/24134062-alt/research-diary.git
# cp -r research-diary/"ClassLink Audio System/box/raspberry/api/"* /opt/classlink/api/
```

---

## 🔄 Bước 3: Restart Web Service

```bash
# SSH vào Pi (nếu chưa SSH)
ssh pi@<IP>

# Restart service web dashboard
sudo systemctl restart box-api

# Hoặc nếu dùng tên service khác:
# sudo systemctl restart classlink-web

# Kiểm tra status
sudo systemctl status box-api

# Xem log nếu cần debug
sudo journalctl -u box-api -f
```

---

## ✅ Bước 4: Test

```bash
# Trên trình duyệt, truy cập:
http://<IP>:8000

# Ví dụ:
# http://192.168.4.1:8000
# http://classlink.local:8000
```

**Test auto-open tab:**
1. Vào tab "Cấu Hình WiFi"
2. Quét và kết nối WiFi mới
3. Xem countdown 3s và tab tự động mở!

---

## 🛠️ Troubleshooting

### Lỗi: Permission denied

```bash
# Fix quyền file
ssh pi@<IP>
sudo chown -R pi:pi /opt/classlink/api/app/static/
sudo chmod 644 /opt/classlink/api/app/static/app.js
```

### Lỗi: Service không restart

```bash
# Xem log lỗi
sudo journalctl -u box-api -n 50

# Restart lại service
sudo systemctl daemon-reload
sudo systemctl restart box-api
```

### Lỗi: Connection refused (SSH)

```bash
# Kiểm tra SSH service trên Pi
sudo systemctl status ssh

# Enable SSH nếu cần
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

## 📝 Quick Commands Summary

```bash
# 1. Copy file
scp "ClassLink Audio System\box\raspberry\api\app\static\app.js" pi@<IP>:/opt/classlink/api/app/static/app.js

# 2. SSH vào Pi
ssh pi@<IP>

# 3. Restart service
sudo systemctl restart box-api

# 4. Xem log
sudo journalctl -u box-api -f
```

---

## 🔐 Thông tin mặc định

| Item | Value |
|------|-------|
| **Username** | `pi` |
| **Password** | `raspberry` (hoặc password bạn đã đổi) |
| **SSH Port** | `22` |
| **Web Port** | `8000` |
| **Service Name** | `box-api` hoặc `classlink-web` |
| **Code Path** | `/opt/classlink/api/app/static/` |

---

**Hoàn thành!** 🎉
