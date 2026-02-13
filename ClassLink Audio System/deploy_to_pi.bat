@echo off
REM ========================================
REM Script: Deploy Code to Raspberry Pi
REM IP: 192.168.1.85
REM ========================================

echo [1/4] Creating directories on Raspberry Pi...
ssh pi@192.168.1.85 "mkdir -p ~/classlink/box/raspberry/api"

echo.
echo [2/4] Syncing Raspberry Pi code...
scp -r "box\raspberry\api\*" pi@192.168.1.85:~/classlink/box/raspberry/api/

echo.
echo [3/4] Restarting API service...
ssh pi@192.168.1.85 "cd ~/classlink/box/raspberry/api && pkill -f uvicorn; sleep 2; nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/classlink-api.log 2>&1 &"

echo.
echo [4/4] Checking API status...
timeout /t 3 /nobreak >nul
ssh pi@192.168.1.85 "curl -s http://localhost:8000/health || echo API not ready yet"

echo.
echo ========================================
echo Deployment complete!
echo Check logs: ssh pi@192.168.1.85 "tail -f /tmp/classlink-api.log"
echo ========================================
pause
