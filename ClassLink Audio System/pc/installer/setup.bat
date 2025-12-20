@echo off
chcp 65001 >nul
title ClassLink AI Service - One-Click Installer

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   CLASSLINK AI SERVICE - CAI DAT TU DONG               ║
echo ║                                                        ║
echo ║   Chi can nhap API Key - moi thu se duoc tu dong!      ║
echo ╚════════════════════════════════════════════════════════╝
echo.

:: Get current directory
set CURRENT_DIR=%~dp0
set EXE_PATH=%CURRENT_DIR%ClassLink-AI-Service.exe
set CONFIG_PATH=%CURRENT_DIR%config.env

:: Check if exe exists
if not exist "%EXE_PATH%" (
    echo [ERROR] File ClassLink-AI-Service.exe khong tim thay!
    pause
    exit /b 1
)

echo [INFO] Tim thay file: ClassLink-AI-Service.exe
echo.

:: Ask for API Key
echo ════════════════════════════════════════════════════════
echo   Vui long nhap GEMINI_API_KEY cua ban
echo   (Lay tu: https://aistudio.google.com/app/apikey)
echo ════════════════════════════════════════════════════════
echo.
set /p API_KEY="Nhap API Key: "

:: Validate API Key
if "%API_KEY%"=="" (
    echo [ERROR] Ban chua nhap API Key!
    pause
    exit /b 1
)

:: Check API Key format (should start with "AIza")
echo %API_KEY% | findstr /b "AIza" >nul
if errorlevel 1 (
    echo [WARNING] API Key co ve khong dung dinh dang.
    echo           API Key hop le thuong bat dau voi "AIza"
    set /p CONFIRM="Ban co muon tiep tuc khong? (Y/N): "
    if /i not "!CONFIRM!"=="Y" exit /b 1
)

echo.
echo [1/4] Tao file config.env...
(
    echo # ClassLink AI Service Configuration
    echo GEMINI_API_KEY=%API_KEY%
    echo MQTT_HOST=192.168.4.1
    echo MQTT_PORT=1883
) > "%CONFIG_PATH%"
echo       config.env da tao thanh cong!

:: Create startup shortcut
echo [2/4] Tao shortcut trong Windows Startup...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_PATH=%STARTUP_DIR%\ClassLink-AI-Service.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%CURRENT_DIR%'; $s.Description = 'ClassLink AI Service'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo       Shortcut da tao - Tu dong chay khi bat PC!
) else (
    echo [ERROR] Khong the tao shortcut!
)

:: Create desktop shortcut
echo [3/4] Tao shortcut tren Desktop...
set DESKTOP=%USERPROFILE%\Desktop
set DESKTOP_SHORTCUT=%DESKTOP%\ClassLink AI Service.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_SHORTCUT%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%CURRENT_DIR%'; $s.Description = 'ClassLink AI Service'; $s.Save()"

if exist "%DESKTOP_SHORTCUT%" (
    echo       Shortcut Desktop da tao!
)

:: Start service
echo [4/4] Khoi dong ClassLink AI Service...
start "" "%EXE_PATH%"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║           CAI DAT HOAN TAT THANH CONG!                 ║
echo ╠════════════════════════════════════════════════════════╣
echo ║                                                        ║
echo ║  [OK] Config da luu voi API Key cua ban                ║
echo ║  [OK] Tu dong chay khi bat PC                          ║
echo ║  [OK] Shortcut tren Desktop                            ║
echo ║  [OK] Service dang chay!                               ║
echo ║                                                        ║
echo ║  Bay gio ban co the:                                   ║
echo ║  - Tat may tinh va bat lai - service se tu chay        ║
echo ║  - Mo web ClassLink de su dung                         ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Nhan phim bat ky de dong...
pause >nul
