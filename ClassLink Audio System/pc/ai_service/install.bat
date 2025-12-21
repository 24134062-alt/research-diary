@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║          ClassLink AI Service - Cài Đặt                          ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Chưa cài Python! Vui lòng cài Python 3.10+ từ python.org
    pause
    exit /b 1
)

echo ✅ Tìm thấy Python
echo.

:: Create venv
echo [1/4] Tạo môi trường ảo...
if not exist "venv" (
    python -m venv venv
)

:: Activate venv
echo [2/4] Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat

:: Install deps
echo [3/4] Cài đặt thư viện...
pip install -r requirements.txt --quiet

:: Setup config
echo [4/4] Cấu hình...
if not exist "config.env" (
    copy .env.example config.env >nul
    echo.
    echo ⚠️  Đã tạo file config.env
    echo     Vui lòng mở file và thêm GEMINI_API_KEY của bạn!
    echo.
    echo     Lấy API Key miễn phí tại:
    echo     https://aistudio.google.com/app/apikey
    echo.
    notepad config.env
)

echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║  ✅ Cài đặt hoàn tất!                                            ║
echo ║                                                                   ║
echo ║  📝 Tiếp theo:                                                   ║
echo ║  1. Thêm GEMINI_API_KEY vào file config.env                     ║
echo ║  2. Chạy: start.bat                                              ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
pause
