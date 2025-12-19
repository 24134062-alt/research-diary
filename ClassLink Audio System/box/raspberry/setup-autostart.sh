#!/bin/bash
###############################################
# ClassLink - Auto-Start Web Server Setup
# 
# Script này tạo systemd service để web server
# tự động chạy khi Raspberry Pi bật điện
###############################################

set -e

SERVICE_NAME="classlink-web"
VENV_PATH="/home/pi/classlink-env"
API_PATH="/home/pi/research-diary/ClassLink Audio System/box/raspberry/api"

echo "=================================="
echo " ClassLink Auto-Start Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Vui lòng chạy với sudo:"
    echo "   sudo bash $0"
    exit 1
fi

echo "[1/3] Tạo systemd service file..."

cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=ClassLink Web Dashboard
After=network.target hostapd.service
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=${API_PATH}
Environment="PATH=${VENV_PATH}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${VENV_PATH}/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "[2/3] Reload systemd và enable service..."
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}.service

echo "[3/3] Khởi động service..."
systemctl start ${SERVICE_NAME}.service

# Check status
sleep 2
if systemctl is-active --quiet ${SERVICE_NAME}.service; then
    echo ""
    echo "=================================="
    echo " HOÀN TẤT!"
    echo "=================================="
    echo ""
    echo "✅ Web server sẽ TỰ ĐỘNG CHẠY khi bật điện!"
    echo ""
    echo "📋 Các lệnh hữu ích:"
    echo "   Xem status:  sudo systemctl status ${SERVICE_NAME}"
    echo "   Xem log:     sudo journalctl -u ${SERVICE_NAME} -f"
    echo "   Restart:     sudo systemctl restart ${SERVICE_NAME}"
    echo "   Stop:        sudo systemctl stop ${SERVICE_NAME}"
    echo ""
else
    echo ""
    echo "⚠️  Service chưa chạy. Kiểm tra log:"
    echo "   sudo journalctl -u ${SERVICE_NAME} -n 20"
fi
