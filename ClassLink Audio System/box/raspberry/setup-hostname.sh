#!/bin/bash
###############################################
# ClassLink - Raspberry Pi Hostname Setup
# 
# Script này đặt hostname cố định cho Raspberry Pi
# Sau khi chạy, truy cập web bằng: http://classlink.local:8000
###############################################

set -e

HOSTNAME="classlink"

echo "=================================="
echo " ClassLink Hostname Setup"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Vui lòng chạy với sudo:"
    echo "   sudo bash $0"
    exit 1
fi

echo "[1/4] Đặt hostname = $HOSTNAME..."
hostnamectl set-hostname $HOSTNAME

echo "[2/4] Cập nhật /etc/hosts..."
# Backup và cập nhật hosts file
cp /etc/hosts /etc/hosts.backup
sed -i "s/127.0.1.1.*/127.0.1.1\t$HOSTNAME/" /etc/hosts

# Nếu không có dòng 127.0.1.1, thêm vào
if ! grep -q "127.0.1.1" /etc/hosts; then
    echo "127.0.1.1	$HOSTNAME" >> /etc/hosts
fi

echo "[3/4] Cài đặt và kích hoạt avahi-daemon (mDNS)..."
apt-get update -qq
apt-get install -y avahi-daemon > /dev/null 2>&1

# Enable avahi-daemon
systemctl enable avahi-daemon
systemctl restart avahi-daemon

echo "[4/4] Kiểm tra..."
echo ""
echo "✅ Hostname hiện tại: $(hostname)"
echo "✅ mDNS service: $(systemctl is-active avahi-daemon)"
echo ""
echo "=================================="
echo " HOÀN TẤT!"
echo "=================================="
echo ""
echo "Sau khi reboot, bạn có thể truy cập web bằng:"
echo ""
echo "   👉 http://classlink.local:8000"
echo ""
echo "Khởi động lại Raspberry Pi? (y/n)"
read -r answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo "Đang reboot..."
    reboot
else
    echo "OK. Hãy reboot sau bằng lệnh: sudo reboot"
fi
