@echo off
echo.
title ClassLink AI Service
echo ==================================================================
echo          ClassLink AI Service - Khoi Dong
echo ==================================================================
echo.

:: Check venv
if not exist "venv" (
    echo [!] Chua cai dat! Chay install.bat truoc.
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Check config
if not exist "config.env" (
    echo [!] Chua co file config.env!
    echo    Chay install.bat de tao file config.
    pause
    exit /b 1
)

:: Check API key
findstr /c:"paste_your_api_key_here" config.env >nul 2>&1
if not errorlevel 1 (
    echo [!] Chua cau hinh GEMINI_API_KEY trong config.env!
    echo.
    echo    Mo file config.env va thay "paste_your_api_key_here" bang API key cua ban.
    echo    Lay API key mien phi tai: https://aistudio.google.com/app/apikey
    echo.
    pause
    exit /b 1
)

echo [OK] Ket noi MQTT broker tai Raspberry Pi...
echo.
echo [*] Gui audio den port UDP 12346
echo [*] Nhan lenh tu MQTT
echo.
echo Nhan Ctrl+C de dung
echo ----------------------------------------------------------
echo.

python main.py

pause
