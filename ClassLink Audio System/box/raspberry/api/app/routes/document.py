"""
Document Upload API - Cầu nối nhẹ (Lightweight Bridge) cho Pi Zero 2 W
Nhận file từ Web và gửi thẳng sang PC qua MQTT để xử lý.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
import base64
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# MQTT service reference (được set từ main.py)
mqtt_service = None

# Lưu trạng thái tài liệu trong bộ nhớ
current_doc = {
    "filename": None,
    "content_length": 0,
    "status": "none"
}

def set_mqtt_service(service):
    global mqtt_service
    mqtt_service = service

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Nhận file và gửi sang PC. Giới hạn 10MB.
    """
    global current_doc
    # 1. Giới hạn 10MB để bảo vệ RAM của Pi
    MAX_SIZE = 10 * 1024 * 1024 
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File quá lớn. Tối đa 10MB.")

    try:
        # 2. Chuyển sang Base64 để gửi qua MQTT
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # 3. Gửi sang PC AI Service
        if mqtt_service:
            mqtt_service.publish("teacher/document", {
                "action": "load",
                "filename": file.filename,
                "base64_content": encoded_content,
                "is_raw": True
            })
            logger.info(f"🚀 Đã chuyển tiếp file {file.filename} sang PC qua MQTT")
            
            # Cập nhật trạng thái để Dashboard hiển thị
            current_doc["filename"] = file.filename
            current_doc["content_length"] = file_size
            current_doc["status"] = "loaded"

            # Lưu log hoạt động
            try:
                from ..main import add_activity
                add_activity(f"Đã tải lên tài liệu: {file.filename}", "file-medical")
            except: pass
        
        return {
            "status": "success", 
            "message": f"Đã gửi {file.filename} sang PC thành công.",
            "filename": file.filename,
            "content_length": file_size
        }
    except Exception as e:
        logger.error(f"Lỗi chuyển tiếp file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")

@router.get("/current")
async def get_current_document():
    """Lấy trạng thái tài liệu hiện tại"""
    if current_doc["status"] == "loaded":
        return {
            "status": "loaded",
            "filename": current_doc["filename"],
            "content_length": current_doc["content_length"]
        }
    return {
        "status": "ready",
        "message": "Sẵn sàng nhận tài liệu.",
        "mode": "bridge"
    }

@router.delete("/clear")
async def clear_document():
    """Xóa tài liệu trên PC"""
    global current_doc
    if mqtt_service:
        mqtt_service.publish("teacher/document", {"action": "clear"})
    
    current_doc["filename"] = None
    current_doc["content_length"] = 0
    current_doc["status"] = "none"
    
    return {"status": "success", "message": "Đã xóa dữ liệu tài liệu"}
