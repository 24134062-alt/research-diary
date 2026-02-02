@echo off
chcp 65001 >nul
title Test Gemini API Key
echo.
echo ==================================================================
echo          Test Gemini API Key - Kiểm Tra Kết Nối
echo ==================================================================
echo.

:: Check venv
if not exist "venv" (
    echo [!] Chưa cài đặt! Chạy install.bat trước.
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Check config
if not exist "config.env" (
    echo [X] Không tìm thấy file config.env!
    echo     Chạy install.bat để tạo config.
    pause
    exit /b 1
)

echo [*] Đang test kết nối với Gemini API...
echo.

:: Run test
python test_ai.py

if errorlevel 1 (
    echo.
    echo ==================================================================
    echo [X] API KEY LỖI hoặc HẾT QUOTA!
    echo.
    echo Giải pháp:
    echo 1. Kiểm tra API key trong config.env
    echo 2. Lấy API key mới tại: https://aistudio.google.com/app/apikey
    echo 3. Đợi 1-2 phút nếu vừa vượt quota
    echo ==================================================================
) else (
    echo.
    echo ==================================================================
    echo [OK] API KEY HOẠT ĐỘNG TÔT!
    echo     AI Service sẵn sàng để chạy.
    echo     Chạy start.bat để khởi động.
    echo ==================================================================
)

echo.
pause
