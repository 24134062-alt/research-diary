"""
File: stt.py
Path: C:\\Users\\DELL\\project\\box\\raspberry\\api\\app\\routes\\stt.py

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

    # Add to global transcription history for dashboard
    try:
        from ..main import add_transcription
        add_transcription(data.text, sender="teacher")
    except Exception as e:
        print(f"Failed to add STT transcription: {e}")

    return {"status": "ok"}

@router.get("/stt/history")
async def get_stt_history():
    """Returns recent transcription history for the dashboard"""
    try:
        from ..main import transcription_history
        return transcription_history
    except Exception as e:
        return []

