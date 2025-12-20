@echo off
chcp 65001 >nul
title ClassLink AI Service - Setup

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║     CLASSLINK AI SERVICE - SETUP AUTO-START            ║
echo ╚════════════════════════════════════════════════════════╝
echo.

:: Get current directory
set CURRENT_DIR=%~dp0
set EXE_PATH=%CURRENT_DIR%ClassLink-AI-Service.exe
set CONFIG_PATH=%CURRENT_DIR%config.env

:: Check if exe exists
if not exist "%EXE_PATH%" (
    echo [ERROR] File ClassLink-AI-Service.exe khong tim thay!
    echo         Vui long dat file nay cung thu muc voi setup.bat
    pause
    exit /b 1
)

:: Check if config exists
if not exist "%CONFIG_PATH%" (
    echo [WARNING] File config.env khong tim thay!
    echo           Vui long tao file config.env voi GEMINI_API_KEY
    echo.
    echo           Vi du noi dung config.env:
    echo           GEMINI_API_KEY=AIzaSy...your_key_here
    echo.
    pause
    exit /b 1
)

echo [1/3] Kiem tra file...
echo       - ClassLink-AI-Service.exe: OK
echo       - config.env: OK

:: Create startup shortcut
echo [2/3] Tao shortcut trong Windows Startup...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\ClassLink-AI-Service.lnk

:: Use PowerShell to create shortcut
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%CURRENT_DIR%'; $s.Description = 'ClassLink AI Service'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo       Shortcut da tao thanh cong!
) else (
    echo [ERROR] Khong the tao shortcut!
    pause
    exit /b 1
)

:: Start service now
echo [3/3] Khoi dong ClassLink AI Service...
start "" "%EXE_PATH%"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              SETUP HOAN TAT!                           ║
echo ╠════════════════════════════════════════════════════════╣
echo ║  ClassLink AI Service da duoc cai dat!                 ║
echo ║                                                        ║
echo ║  - Tu dong chay khi bat PC                             ║
echo ║  - Ket noi voi Box qua mang WiFi                       ║
echo ║  - Xu ly AI cho hoc sinh                               ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Nhan phim bat ky de dong...
pause >nul
