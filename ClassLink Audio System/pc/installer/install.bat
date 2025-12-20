@echo off
chcp 65001 >nul
title ClassLink AI Service Installer
color 0A

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║        CLASSLINK AI SERVICE - INSTALLER                ║
echo ╠════════════════════════════════════════════════════════╣
echo ║  Installing AI service for ClassLink Audio System...   ║
echo ╚════════════════════════════════════════════════════════╝
echo.

:: Check Python
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.11+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python OK!

:: Create install directory
echo [2/5] Creating install directory...
set INSTALL_DIR=%USERPROFILE%\ClassLinkAI
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo       Directory: %INSTALL_DIR%

:: Copy files
echo [3/5] Copying service files...
copy /Y "%~dp0classlink_service.py" "%INSTALL_DIR%\" >nul
copy /Y "%~dp0config.env" "%INSTALL_DIR%\" >nul
echo       Files copied!

:: Install dependencies
echo [4/5] Installing Python packages...
echo       This may take 1-2 minutes...
pip install google-genai paho-mqtt speechrecognition python-dotenv --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install packages!
    pause
    exit /b 1
)
echo       Packages installed!

:: Create startup shortcut
echo [5/5] Creating startup entry...
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
echo @echo off > "%STARTUP_DIR%\ClassLinkAI.bat"
echo cd /d "%INSTALL_DIR%" >> "%STARTUP_DIR%\ClassLinkAI.bat"
echo start /min pythonw classlink_service.py >> "%STARTUP_DIR%\ClassLinkAI.bat"
echo       Auto-start enabled!

:: Start service now
echo.
echo Starting ClassLink AI Service...
cd /d "%INSTALL_DIR%"
start /min pythonw classlink_service.py

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                INSTALLATION COMPLETE!                  ║
echo ╠════════════════════════════════════════════════════════╣
echo ║  ClassLink AI Service is now running!                  ║
echo ║                                                        ║
echo ║  - Service runs in background                          ║
echo ║  - Auto-starts when PC boots                           ║
echo ║  - Open ClassLink web dashboard to use                 ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Press any key to close...
pause >nul
