@echo off
chcp 65001 >nul
title Check AI Service Status
echo.
echo ==================================================================
echo          ClassLink AI Service - Kiểm Tra Trạng Thái
echo ==================================================================
echo.

:: Check if AI service is running
tasklist /FI "WINDOWTITLE eq ClassLink AI Service" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [✓] AI Service: ĐANG CHẠY
) else (
    echo [✗] AI Service: CHƯA KHỞI ĐỘNG
    echo     ^ Chạy start.bat để khởi động
)

:: Check MQTT connection (ping Raspberry Pi)
echo.
echo [*] Kiểm tra kết nối Raspberry Pi...
ping -n 1 -w 1000 192.168.4.1 >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo [✓] Raspberry Pi: ONLINE (192.168.4.1)
) else (
    echo [✗] Raspberry Pi: OFFLINE
    echo     ^ Kiểm tra:
    echo       1. Raspberry Pi đã bật chưa?
    echo       2. PC đã kết nối WiFi CLASS-BOX chưa?
    echo       3. Hoặc cùng mạng với Pi?
)

:: Check if vector DB exists
echo.
if exist "data\vector_db" (
    echo [✓] Vector DB: ĐÃ KHỞI TẠO
    
    :: Count chunks (approximate)
    for /f %%a in ('dir /b /s "data\vector_db\*.parquet" 2^>nul ^| find /c /v ""') do set chunk_count=%%a
    if defined chunk_count (
        if %chunk_count% GTR 0 (
            echo     ^ Đã có %chunk_count% file dữ liệu
        )
    )
) else (
    echo [i] Vector DB: CHƯA CÓ DỮ LIỆU
    echo     ^ Upload tài liệu qua Dashboard để thêm
)

:: Check log file
echo.
if exist "ai_service.log" (
    echo [✓] Log File: ai_service.log
    
    :: Get last 3 lines
    echo.
    echo ---- LOG GẦN NHẤT ----
    powershell -Command "Get-Content ai_service.log -Tail 3 -Encoding UTF8"
    echo ----------------------
) else (
    echo [i] Chưa có log file (chưa chạy lần nào)
)

echo.
echo ==================================================================
echo.

:: Summary
tasklist /FI "WINDOWTITLE eq ClassLink AI Service" 2>NUL | find /I /N "python.exe">NUL
ping -n 1 -w 1000 192.168.4.1 >nul 2>&1

if "%ERRORLEVEL%"=="0" (
    tasklist /FI "WINDOWTITLE eq ClassLink AI Service" 2>NUL | find /I /N "python.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo [OK] HỆ THỐNG SẴN SÀNG!
        echo      Mở web: http://192.168.4.1:8000
    ) else (
        echo [!] Raspberry Pi online nhưng AI Service chưa chạy
        echo     Chạy start.bat để khởi động
    )
) else (
    echo [!] CHƯA KẾT NỐI ĐƯỢC RASPBERRY PI
    echo     Kiểm tra kết nối trước khi chạy AI Service
)

echo.
pause
