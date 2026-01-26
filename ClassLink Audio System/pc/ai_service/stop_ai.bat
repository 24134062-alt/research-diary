@echo off
title Stop AI Service
echo Closing AI Service instances...

:: Taskkill any python process running main.py if possible, 
:: but usually taskkill /F /IM python.exe is safest for a dedicated setup.
:: To be safe and not kill OTHER python apps, we can try to filter, 
:: but on Windows simple taskkill is often used.

taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq ClassLink AI Service*" > nul 2>&1
taskkill /F /IM python.exe /FI "MODULES eq main.py" > nul 2>&1

:: Simple but effective:
taskkill /F /IM python.exe > nul 2>&1

echo.
echo [OK] AI Service stopped.
timeout /t 2
