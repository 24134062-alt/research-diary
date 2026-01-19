"""
Document Upload API - Cho phép giáo viên upload tài liệu bài giảng
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
import uuid
import magic
from pathlib import Path

# Import document processor (optional - may not be available on Pi)
try:
    import sys
    # Add PC AI service path to import DocumentProcessor
    # c:\Users\DELL\research-diary-1\ClassLink Audio System\box\raspberry\api\app\routes\document.py
    # parents: 1:routes, 2:app, 3:api, 4:raspberry, 5:box, 6:ClassLink Audio System
    root_path = Path(__file__).parent.parent.parent.parent.parent.parent
    pc_service_path = root_path / "pc" / "ai_service"
    if pc_service_path.exists():
        sys.path.insert(0, str(pc_service_path))
    from document_processor import DocumentProcessor
    PROCESSOR_AVAILABLE = True
except Exception as e:
    PROCESSOR_AVAILABLE = False
    print(f"[WARN] DocumentProcessor not available: {e}")

logger = logging.getLogger(__name__)

router = APIRouter()

# Storage for current document
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory state
current_document = {
    "filename": None,
    "content": None,
    "uploaded_at": None
}

# MQTT service reference (will be set from main.py)
mqtt_service = None

def set_mqtt_service(service):
    """Set MQTT service for publishing document content"""
    global mqtt_service
    mqtt_service = service

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload tài liệu bài giảng (PDF, DOCX, TXT)
    Bảo mật: Kiểm tra MIME, giới hạn 10MB, Sanitize tên file
    """
    # 1. Giới hạn kích thước file (10MB)
    MAX_SIZE = 10 * 1024 * 1024 # 10MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File quá lớn. Tối đa 10MB.")

    # 2. Validate file type (Dựa trên Extension và MIME)
    allowed_extensions = ['.pdf', '.docx', '.txt']
    allowed_mimes = [
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # DOCX
        'text/plain'
    ]
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    # Kiểm tra MIME bằng python-magic
    mime_type = magic.from_buffer(content, mime=True)
    
    if file_ext not in allowed_extensions or mime_type not in allowed_mimes:
        logger.warning(f"Rejected malicious upload: {file.filename} (Extension: {file_ext}, MIME: {mime_type})")
        raise HTTPException(
            status_code=400, 
            detail="Loại file không hợp lệ hoặc không an toàn."
        )
    
    try:
        # 3. Sanitize filename (Dùng UUID để tránh Path Traversal)
        safe_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved secure file: {safe_filename} (original: {file.filename})")
        
        # Extract text content
        text_content = ""
        if PROCESSOR_AVAILABLE:
            try:
                text_content = DocumentProcessor.extract_text(str(file_path))
            except Exception as e:
                logger.error(f"Error extracting text with DocumentProcessor: {e}")
                text_content = f"Lỗi xử lý nội dung: {str(e)}"
        else:
            # Fallback: read as text if possible
            if file_ext == '.txt':
                text_content = content.decode('utf-8', errors='ignore')
            else:
                text_content = f"Không thể xử lý định dạng {file_ext} (Thiếu bộ xử lý tài liệu)"
        
        # Update current document state
        import time
        current_document["filename"] = file.filename
        current_document["content"] = text_content
        current_document["uploaded_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Send to PC AI Service via MQTT
        if mqtt_service:
            mqtt_service.publish("teacher/document", {
                "action": "load",
                "filename": file.filename,
                "content": text_content[:50000]  # Limit content size
            })
            logger.info(f"Sent document to PC AI Service: {file.filename}")
            
            # Add to activity log (dynamic display on dashboard)
            try:
                from ..main import add_activity
                add_activity(f"Giáo viên đã tải lên: {file.filename}", "file-alt")
            except Exception as e:
                logger.warning(f"Failed to log activity: {e}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Đã upload thành công: {file.filename}",
            "filename": file.filename,
            "content_length": len(text_content),
            "preview": text_content[:200] + "..." if len(text_content) > 200 else text_content
        })
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi upload: {str(e)}")


@router.get("/current")
async def get_current_document():
    """Lấy thông tin tài liệu hiện tại"""
    if not current_document["filename"]:
        return {"status": "empty", "message": "Chưa có tài liệu nào được upload"}
    
    return {
        "status": "loaded",
        "filename": current_document["filename"],
        "uploaded_at": current_document["uploaded_at"],
        "content_length": len(current_document["content"] or ""),
        "preview": (current_document["content"] or "")[:300]
    }


@router.delete("/clear")
async def clear_document():
    """Xóa tài liệu hiện tại"""
    global current_document
    
    old_filename = current_document["filename"]
    
    # Clear state
    current_document = {
        "filename": None,
        "content": None,
        "uploaded_at": None
    }
    
    # Notify PC AI Service to clear context
    if mqtt_service:
        mqtt_service.publish("teacher/document", {
            "action": "clear"
        })
    
    # Delete uploaded file
    if old_filename:
        # Chúng ta không nên xóa bằng filename của user truyền lên mà nên lưu mapping
        # Trong MVP này, chúng ta xóa tất cả file trong UPLOAD_DIR khi clear
        for f in UPLOAD_DIR.glob("*"):
            try:
                os.remove(f)
            except:
                pass
    
    # Add to activity log
    try:
        from ..main import add_activity
        add_activity("Giáo viên đã xóa tài liệu bài giảng", "trash")
    except Exception as e:
        logger.warning(f"Failed to log activity for document clear: {e}")
    
    return {"status": "success", "message": "Đã xóa tài liệu"}
