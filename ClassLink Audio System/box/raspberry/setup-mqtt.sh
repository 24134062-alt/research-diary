#!/bin/bash
###############################################
# ClassLink - MQTT Broker Setup
# 
# Cài đặt Mosquitto MQTT Broker trên Raspberry Pi
# để các thiết bị có thể giao tiếp với nhau
###############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[MQTT]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[MQTT]${NC} $1"
}

log_error() {
    echo -e "${RED}[MQTT]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Vui lòng chạy với sudo: sudo $0"
    exit 1
fi

log_section "ClassLink MQTT Broker Setup"

# ============================================
log_section "1/3 - Cài đặt Mosquitto"
# ============================================

log_info "Cài đặt Mosquitto MQTT Broker..."
apt update
apt install -y mosquitto mosquitto-clients

log_info "✅ Mosquitto đã được cài đặt"

# ============================================
log_section "2/3 - Cấu hình Mosquitto"
# ============================================

log_info "Tạo cấu hình cho ClassLink..."

# Backup original config
if [ -f /etc/mosquitto/mosquitto.conf ] && [ ! -f /etc/mosquitto/mosquitto.conf.bak ]; then
    cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.bak
fi

# Create ClassLink config
cat > /etc/mosquitto/conf.d/classlink.conf << 'EOF'
# ClassLink MQTT Configuration
# ============================

# Listen on all interfaces
listener 1883

# Allow anonymous connections (for local network)
allow_anonymous true

# Persistence (store messages to disk)
persistence true
persistence_location /var/lib/mosquitto/

# Logging
log_dest syslog
log_type error
log_type warning
log_type notice
log_type information

# Connection limits
max_connections -1
EOF

log_info "✅ Cấu hình đã được tạo"

# ============================================
log_section "3/3 - Khởi động Mosquitto"
# ============================================

log_info "Khởi động và enable Mosquitto service..."
systemctl enable mosquitto
systemctl restart mosquitto

# Wait and verify
sleep 2
if systemctl is-active --quiet mosquitto; then
    log_info "✅ Mosquitto đang chạy!"
else
    log_error "❌ Mosquitto không khởi động được"
    log_error "Kiểm tra log: journalctl -u mosquitto -n 20"
    exit 1
fi

# Test connection
log_info "Kiểm tra kết nối..."
if mosquitto_pub -h localhost -t "test/classlink" -m "hello" 2>/dev/null; then
    log_info "✅ MQTT Broker hoạt động tốt!"
else
    log_warn "⚠️ Không thể test publish (có thể vẫn OK)"
fi

# ============================================
log_section "Hoàn tất!"
# ============================================

# Get IP addresses
IP_WLAN=$(ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\s)\d+\.\d+\.\d+\.\d+' | head -1)
IP_ETH=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+\.\d+\.\d+\.\d+' | head -1)

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ MQTT BROKER ĐÃ SẴN SÀNG!            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "📡 MQTT Broker đang chạy tại:"
if [ -n "$IP_WLAN" ]; then
    echo -e "   ${CYAN}mqtt://$IP_WLAN:1883${NC} (WiFi)"
fi
if [ -n "$IP_ETH" ]; then
    echo -e "   ${CYAN}mqtt://$IP_ETH:1883${NC} (Ethernet)"
fi
echo -e "   ${CYAN}mqtt://localhost:1883${NC} (Local)"
echo ""
echo -e "📋 Để test từ PC:"
echo -e "   ${YELLOW}mosquitto_sub -h $IP_WLAN -t '#' -v${NC}"
echo ""
echo -e "📋 Cấu hình thiết bị:"
echo -e "   Glasses/Mic: MQTT_SERVER = \"$IP_WLAN\""
echo -e "   PC AI: mqtt_client.connect(\"$IP_WLAN\", 1883)"
echo ""

exit 0
