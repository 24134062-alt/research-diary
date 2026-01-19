"""
File: send_result.py
Path: C:\\Users\\DELL\\project\\pc\\stt_service\\send_result.py

Vai trò:
- Gửi kết quả STT (text) về Raspberry BOX
- Hỗ trợ MOCK_MODE khi Raspberry chưa chạy
"""

import time
import json
import os
from typing import Optional
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

# ====== Load Config ======
CONFIG_PATH = Path(__file__).parent / "config.json"
MOCK_MODE = False  # Set to False for production
RASPBERRY_URL = "http://192.168.4.1:8002/api/stt"

if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config_data = json.load(f)
            RASPBERRY_URL = config_data.get("stt", {}).get("box_url", RASPBERRY_URL)
            print(f"[CONFIG] Loaded Box URL: {RASPBERRY_URL}")
    except Exception as e:
        print(f"[WARN] Failed to load config.json: {e}")

HTTP_TIMEOUT = 1.0 # Increase timeout slightly

def send_text(
    text: str,
    mode: str = "CLASS",
    target: str = "ALL"
) -> bool:
    """
    Gửi text về Raspberry (hoặc mock)
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
