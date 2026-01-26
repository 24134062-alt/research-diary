@echo off
title AI Service Monitor
echo ======================================================
echo           AI SERVICE LIVE MONITOR (Logging)
echo ======================================================
echo [TIP] You can close this window at any time. 
echo       The AI Service will CONTINUE running in background.
echo.
echo Press Ctrl+C to stop viewing logs (or just close window).
echo ------------------------------------------------------
echo.

if not exist ai_service.log (
    echo [!] log file not found yet. Starting monitor soon...
    timeout /t 3 > nul
)

:: Use PowerShell to 'tail -f' the log file
powershell -Command "Get-Content ai_service.log -Wait -Tail 20"

pause
