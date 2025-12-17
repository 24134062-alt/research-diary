# ClassLink Audio System - Hướng Dẫn Triển Khai

**Phiên bản:** v2.0.1 (Premium)  
**Ngày cập nhật:** 2025-12-17

---

## 📋 Tổng Quan Hệ Thống

ClassLink Audio System là hệ thống quản lý âm thanh thông minh cho lớp học, bao gồm:
- **Web Dashboard**: Giao diện quản trị cho giáo viên
- **AI Trợ Giảng**: Hỗ trợ trả lời câu hỏi học sinh
- **Kính thông minh**: Thu âm và hiển thị thông tin

---

## 🚀 Hướng Dẫn Triển Khai Nhanh

### **Bước 1: Chuẩn Bị Phần Cứng**

- ✅ Raspberry Pi (đã cài sẵn hệ thống)
- ✅ Nguồn điện 5V/3A cho Raspberry Pi
- ✅ Thiết bị có WiFi (PC, điện thoại, máy tính bảng)

---

### **Bước 2: Khởi Động Raspberry Pi**

1. **Cắm nguồn** cho Raspberry Pi
2. **Đợi 30-60 giây** để hệ thống khởi động hoàn toàn
3. LED xanh trên Raspberry Pi sẽ nhấp nháy khi đang hoạt động
4. **Raspberry Pi sẽ tự động phát WiFi hotspot:** `ClassLink-Setup`

---

### **Bước 3: Kết Nối WiFi Hotspot**

1. **Trên thiết bị của bạn** (PC/điện thoại), mở danh sách WiFi
2. **Tìm và kết nối** WiFi: `ClassLink-Setup`
   - Password (nếu có): `classlink2024`
3. **Đợi kết nối thành công**

> **Lưu ý:** Một số thiết bị có thể báo "No Internet" - đây là bình thường vì đang kết nối WiFi setup, chưa có Internet.

---

### **Bước 4: Truy Cập Trang Cấu Hình**

1. **Mở trình duyệt** (Chrome, Edge, Firefox, Safari)
2. **Truy cập một trong các địa chỉ sau:**
   
   **Cách 1 (Tự động):**
   - Một số thiết bị sẽ tự động mở trang captive portal
   
   **Cách 2 (Thủ công):**
   ```
   http://192.168.4.1:8000
   ```
   
   **Cách 3 (Hostname):**
   ```
   http://classlink.local:8000
   ```

3. **Bạn sẽ thấy** trang **ClassLink Audio Manager** với giao diện màu đen/xanh lá

---

### **Bước 5: Cấu Hình WiFi Chính**

1. **Trên web dashboard**, click vào tab **"Cấu Hình WiFi"** (biểu tượng WiFi ở sidebar trái)

2. **Nhấn nút "Quét Mạng"** để tìm các WiFi xung quanh

3. **Chọn WiFi** mà bạn muốn Raspberry Pi kết nối (WiFi trường học/nhà/cơ quan)

4. **Nhập mật khẩu** WiFi (nếu có)

5. **Nhấn "Kết Nối"**

6. **Đợi 10-30 giây** - Raspberry Pi sẽ:
   - Kết nối WiFi mới
   - Tự động tắt hotspot `ClassLink-Setup` (hoặc giữ song song)
   - Khởi động lại web service

---

### **Bước 6: Kết Nối Lại Vào WiFi Chính**

1. **Trên thiết bị của bạn**, ngắt kết nối WiFi `ClassLink-Setup`
2. **Kết nối lại** WiFi chính (WiFi mà bạn vừa cấu hình cho Raspberry Pi)
3. **Truy cập dashboard** bằng:
   ```
   http://raspberrypi.local:8000
   ```
   
   Hoặc nếu không được, tìm IP của Raspberry Pi trên router

---

### **Bước 7: Hoàn Tất!**

Bây giờ bạn có thể:
- ✅ Quản lý thiết bị học sinh
- ✅ Giám sát AI Trợ Giảng
- ✅ Chuyển đổi chế độ giảng dạy (Tự Nhiên / Xã Hội)
- ✅ Xem log hoạt động

---

## ✅ Kiểm Tra Hệ Thống Hoạt Động

Sau khi truy cập web thành công, bạn sẽ thấy:

1. **Trang Chủ Quản Trị** với giao diện màu đen/xanh lá
2. **Mode Hiện Tại**: Tự Nhiên hoặc Xã Hội
3. **Thiết Bị Đang Kết Nối**: Danh sách kính thông minh
4. **AI Core / Box**: Trạng thái Online
5. **Hoạt Động Gần Đây**: Log các sự kiện

---

## 🔧 Khắc Phục Sự Cố

### **Vấn đề 1: Không truy cập được web**

**Triệu chứng:** Trình duyệt báo "can't reach this page"

**Giải pháp:**
1. Kiểm tra Raspberry Pi đã bật và LED nhấp nháy
2. Kiểm tra máy tính và Raspberry Pi cùng mạng WiFi
3. Thử truy cập bằng IP thay vì `raspberrypi.local`
4. Kiểm tra service: `sudo systemctl status classlink-web`

---

### **Vấn đề 2: Web hiển thị nhưng không có CSS**

**Triệu chứng:** Trang trắng, chỉ có văn bản

**Giải pháp:**
1. Hard refresh trình duyệt: `Ctrl + F5`
2. Xóa cache trình duyệt
3. Kiểm tra log server trên Raspberry Pi

---

### **Vấn đề 3: Service không tự động chạy khi khởi động**

**Giải pháp:**
```bash
# Kích hoạt lại service
sudo systemctl enable classlink-web
sudo systemctl start classlink-web
```

---

## 📞 Hỗ Trợ Kỹ Thuật

**Khi cần hỗ trợ, vui lòng cung cấp:**
1. Địa chỉ IP của Raspberry Pi (`hostname -I`)
2. Log service: `sudo journalctl -u classlink-web -n 50`
3. Screenshot lỗi trên trình duyệt

---

## 📚 Tài Liệu Kĩ Thuật Chi Tiết

- **Kiến trúc hệ thống**: Xem file `ARCHITECTURE.md`
- **Hướng dẫn cài đặt từng bước**: Xem file `SETUP_GUIDE.md`
- **API Documentation**: Xem folder `docs/api/`

---

## 🎓 Sử Dụng Cơ Bản

### **1. Chuyển đổi chế độ giảng dạy**
- Vào tab "Tổng Quan"
- Chọn "Tự Nhiên" (Toán, Lý, Hóa) hoặc "Xã Hội" (Văn, Sử, Địa)

### **2. Giám sát thiết bị học sinh**
- Xem danh sách thiết bị kết nối
- Kiểm tra pin kính thông minh
- Xem trạng thái kết nối

### **3. AI Trợ Giảng**
- Mở tab "Giám Sát & AI Trợ Giảng"
- Chọn kênh học sinh
- Gửi phản hồi TTS tới học sinh

---

## ⚙️ Thông Tin Hệ Thống

- **Control Plane:** MQTT (test.mosquitto.org hoặc local broker)
- **Data Plane:** UDP Audio streaming
- **Web Framework:** FastAPI (Python)
- **Database:** In-memory (session-based)

---

**© 2025 ClassLink Audio System. All rights reserved.**
