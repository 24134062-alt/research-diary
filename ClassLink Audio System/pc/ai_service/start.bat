@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          ClassLink AI Service - Khởi Động                        ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check venv
if not exist "venv" (
    echo ❌ Chưa cài đặt! Chạy install.bat trước.
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Check config
if not exist "config.env" (
    echo ❌ Chưa có file config.env!
    echo    Chạy install.bat để tạo file config.
    pause
    exit /b 1
)

:: Check API key
findstr /c:"paste_your_api_key_here" config.env >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Chưa cấu hình GEMINI_API_KEY trong config.env!
    echo.
    echo    Mở file config.env và thay "paste_your_api_key_here" bằng API key của bạn.
    echo    Lấy API key miễn phí tại: https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

echo ✅ Kết nối MQTT broker tại Raspberry Pi...
echo.
echo 📡 Gửi audio đến port UDP 12346
echo 🤖 Nhận lệnh từ MQTT
echo.
echo Nhấn Ctrl+C để dừng
echo ─────────────────────────────────────────────────────────
echo.

python main.py

pause
