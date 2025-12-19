#!/bin/bash
###############################################
# ClassLink - Raspberry Pi WiFi AP Setup
# 
# Script này cấu hình Raspberry Pi phát WiFi hotspot
# SSID: ClassLink-Setup
# Password: classlink2024
###############################################

set -e

# Configuration
AP_SSID="ClassLink-Setup"
AP_PASS="classlink2024"
AP_CHANNEL="7"
AP_IP="192.168.4.1"

echo "=================================="
echo " ClassLink WiFi AP Setup"
echo "=================================="
echo ""
echo "SSID: $AP_SSID"
echo "Password: $AP_PASS"
echo "IP: $AP_IP"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Vui lòng chạy với sudo:"
    echo "   sudo bash $0"
    exit 1
fi

echo "[1/6] Dừng services..."
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

echo "[2/6] Cấu hình hostapd..."
cat > /etc/hostapd/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=$AP_SSID
hw_mode=g
channel=$AP_CHANNEL
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$AP_PASS
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Set hostapd config file location
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd 2>/dev/null || true

echo "[3/6] Cấu hình dnsmasq..."
# Backup original config
if [ ! -f /etc/dnsmasq.conf.orig ]; then
    cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
fi

cat > /etc/dnsmasq.conf << EOF
# ClassLink AP Config
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/classlink.local/$AP_IP
address=/setup.classlink/$AP_IP
EOF

echo "[4/6] Cấu hình IP tĩnh..."
# Check if already configured
if ! grep -q "# ClassLink AP" /etc/dhcpcd.conf 2>/dev/null; then
    cat >> /etc/dhcpcd.conf << EOF

# ClassLink AP Configuration
interface wlan0
static ip_address=$AP_IP/24
nohook wpa_supplicant
EOF
fi

echo "[5/6] Bật IP forwarding..."
if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
fi
sysctl -w net.ipv4.ip_forward=1 > /dev/null

echo "[6/6] Khởi động services..."
systemctl unmask hostapd 2>/dev/null || true
systemctl enable hostapd
systemctl enable dnsmasq
systemctl start hostapd
systemctl start dnsmasq

echo ""
echo "=================================="
echo " HOÀN TẤT!"
echo "=================================="
echo ""
echo "✅ WiFi AP đã được cấu hình!"
echo ""
echo "📶 Để kích hoạt, vui lòng reboot:"
echo "   sudo reboot"
echo ""
echo "Sau khi reboot, tìm WiFi:"
echo "   SSID: $AP_SSID"
echo "   Password: $AP_PASS"
echo ""
echo "Truy cập web:"
echo "   http://$AP_IP:8000"
echo "   hoặc http://classlink.local:8000"
echo ""
