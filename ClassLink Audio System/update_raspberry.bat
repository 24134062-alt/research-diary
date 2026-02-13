@echo off
REM ==========================================
REM Update Raspberry Pi from GitHub
REM ==========================================

echo ==========================================
echo Updating Raspberry Pi Code from GitHub
echo ==========================================
echo.

echo [1/4] Connecting to Raspberry Pi...
ssh pi@192.168.4.1 "echo Connected successfully!"
if %errorlevel% neq 0 (
    echo ERROR: Cannot connect to Raspberry Pi
    pause
    exit /b 1
)

echo.
echo [2/4] Pulling latest code from GitHub...
ssh pi@192.168.4.1 "cd /home/pi/ClassLink && git pull origin main"
if %errorlevel% neq 0 (
    echo ERROR: Git pull failed
    pause
    exit /b 1
)

echo.
echo [3/4] Installing Python dependencies...
ssh pi@192.168.4.1 "cd '/home/pi/ClassLink/ClassLink Audio System/pc/ai_service' && pip3 install -r requirements.txt"

echo.
echo [4/4] Verifying update...
ssh pi@192.168.4.1 "cd /home/pi/ClassLink && git log --oneline -1"

echo.
echo ==========================================
echo Update completed successfully!
echo ==========================================
echo.
echo To restart AI service:
echo   ssh pi@192.168.4.1
echo   sudo systemctl restart ai-service
echo.

pause
