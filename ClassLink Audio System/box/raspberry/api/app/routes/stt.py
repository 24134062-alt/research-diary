"""
File: stt.py
Path: C:\Users\DELL\project\box\raspberry\api\app\routes\stt.py

Vai trò:
- Nhận kết quả STT từ PC
- In log kiểm tra pipeline PC -> Raspberry
- Gọi router xử lý class / private (sau)

Ghi chú:
- MVP: chưa gửi text xuống ESP32
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

router = APIRouter()


# ====== Data model ======
class STTText(BaseModel):
    type: str
    mode: str
    target: str
    text: str
    ts: float | None = None


# ====== Route ======
@router.post("/stt")
async def receive_stt(data: STTText):
    if data.type != "STT_TEXT":
        raise HTTPException(status_code=400, detail="Invalid type")

    ts = data.ts or time.time()

    print(
        f"[STT] mode={data.mode} "
        f"target={data.target} "
        f"text='{data.text}' "
        f"ts={ts}"
    )

    # TODO: gọi router.class_text() hoặc router.private_text()
    # router.route_text(data.mode, data.target, data.text)

    return {"status": "ok"}

