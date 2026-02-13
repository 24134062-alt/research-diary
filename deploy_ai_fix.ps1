# Deploy AI fix to Raspberry Pi
$piUser = "pi"
$piHost = "192.168.1.95"
$piPath = "/home/pi/ClassLink/ClassLink Audio System/pc/ai_service/"

Write-Host "=== Deploying AI Service Fixes to Pi ===" -ForegroundColor Cyan

# Copy websocket_handler.py
Write-Host "Copying websocket_handler.py..." -ForegroundColor Yellow
scp "ClassLink Audio System\pc\ai_service\websocket_handler.py" "${piUser}@${piHost}:${piPath}"

# Copy main.py
Write-Host "Copying main.py..." -ForegroundColor Yellow
scp "ClassLink Audio System\pc\ai_service\main.py" "${piUser}@${piHost}:${piPath}"

Write-Host "`n=== Files Deployed! ===" -ForegroundColor Green
Write-Host "Now SSH to Pi and run:" -ForegroundColor Cyan
Write-Host "  cd ~/ClassLink/'ClassLink Audio System'/pc/ai_service" -ForegroundColor White
Write-Host "  source venv/bin/activate" -ForegroundColor White
Write-Host "  pkill -f 'python.*main.py'" -ForegroundColor White
Write-Host "  python main.py" -ForegroundColor White
