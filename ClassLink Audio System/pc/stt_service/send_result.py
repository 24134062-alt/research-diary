"""
File: send_result.py
Path: C:\\Users\\DELL\\project\\pc\\stt_service\\send_result.py

Vai trò:
- Gửi kết quả STT (text) về Raspberry BOX
- Hỗ trợ MOCK_MODE khi Raspberry chưa chạy

Ghi chú:
- Giao thức JSON line đơn giản
- Không block pipeline audio
"""

import time
import json
from typing import Optional

try:
    import requests
except ImportError:
    requests = None


# ====== Config ======
MOCK_MODE = True  # <- đổi sang False khi Raspberry sẵn sàng

RASPBERRY_URL = "http://127.0.0.1:8000/api/stt"  # endpoint dự kiến
HTTP_TIMEOUT = 0.5  # giây


def send_text(
    text: str,
    mode: str = "CLASS",
    target: str = "ALL"
) -> bool:
    """
    Gửi text về Raspberry (hoặc mock)

    Returns:
        True  : gửi (hoặc mock) OK
        False : lỗi
    """
    payload = {
        "type": "STT_TEXT",
        "mode": mode,
        "target": target,
        "text": text,
        "ts": time.time()
    }

    if MOCK_MODE or requests is None:
        print("[SEND][MOCK]", json.dumps(payload, ensure_ascii=False))
        return True

    try:
        resp = requests.post(
            RASPBERRY_URL,
            json=payload,
            timeout=HTTP_TIMEOUT
        )
        if resp.status_code == 200:
            print("[SEND][OK]", text)
            return True
        else:
            print("[SEND][ERR] HTTP", resp.status_code)
            return False

    except Exception as e:
        print("[SEND][EXC]", e)
        return False

