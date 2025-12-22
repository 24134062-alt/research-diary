#!/bin/bash
###############################################
# ClassLink - Raspberry Pi Installation Script
# 
# Script tự động cài đặt toàn bộ hệ thống
###############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INSTALL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[INSTALL]${NC} $1"
}

log_error() {
    echo -e "${RED}[INSTALL]${NC} $1"
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

# Get actual user (not root)
ACTUAL_USER="${SUDO_USER:-pi}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/classlink"

log_section "ClassLink Raspberry Pi Installer"
log_info "Script directory: $SCRIPT_DIR"
log_info "Install directory: $INSTALL_DIR"
log_info "User: $ACTUAL_USER"

# ============================================
log_section "1/6 - Cập nhật hệ thống"
# ============================================
log_info "Đang cập nhật packages..."
apt update
apt upgrade -y

# ============================================
log_section "2/6 - Cài đặt dependencies"
# ============================================
log_info "Đang cài đặt packages cần thiết..."
apt install -y \
    python3-pip python3-venv \
    network-manager \
    git

# ============================================
log_section "3/6 - Cấu hình NetworkManager"
# ============================================
log_info "Chuyển từ dhcpcd sang NetworkManager..."

# Disable dhcpcd
if systemctl is-active --quiet dhcpcd; then
    systemctl stop dhcpcd
fi
systemctl disable dhcpcd 2>/dev/null || true

# Enable NetworkManager
systemctl enable NetworkManager
systemctl start NetworkManager

# Wait for NetworkManager to be ready
sleep 3

log_info "NetworkManager đã được kích hoạt"

# ============================================
log_section "4/6 - Copy files"
# ============================================

# Create directories
log_info "Tạo thư mục $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"/{net,api,config}

# Copy network scripts
log_info "Copy network scripts..."
cp "$SCRIPT_DIR/net/"* "$INSTALL_DIR/net/"
chmod +x "$INSTALL_DIR/net/"*

# Copy API
log_info "Copy API files..."
cp -r "$SCRIPT_DIR/api/"* "$INSTALL_DIR/api/"

# Copy config example
if [ -f "$SCRIPT_DIR/config.example.yaml" ]; then
    cp "$SCRIPT_DIR/config.example.yaml" "$INSTALL_DIR/config/"
fi

# Copy PC AI Service (for download feature)
log_info "Copy PC AI Service files..."
mkdir -p "$INSTALL_DIR/pc"
cp -r "$SCRIPT_DIR/../../pc/"* "$INSTALL_DIR/pc/"

# Setup sudoers for WiFi control (allow pi to run nmcli without password)
log_info "Cấu hình quyền WiFi cho user pi..."
if [ -f "$SCRIPT_DIR/config/classlink-wifi-sudoers" ]; then
    cp "$SCRIPT_DIR/config/classlink-wifi-sudoers" /etc/sudoers.d/classlink-wifi
    chmod 440 /etc/sudoers.d/classlink-wifi
    log_info "Sudoers rule đã được cài đặt"
fi

# Set ownership
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR"

log_info "Files đã được copy"

# ============================================
log_section "5/6 - Thiết lập Python environment"
# ============================================
log_info "Tạo virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"

log_info "Cài đặt Python packages..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install \
    fastapi uvicorn pydantic pyyaml aiofiles

# Set ownership
chown -R "$ACTUAL_USER:$ACTUAL_USER" "$INSTALL_DIR/venv"

log_info "Python environment đã sẵn sàng"

# ============================================
log_section "6/6 - Thiết lập systemd services"
# ============================================
log_info "Copy service files..."
cp "$SCRIPT_DIR/services/"*.service /etc/systemd/system/
cp "$SCRIPT_DIR/services/"*.timer /etc/systemd/system/ 2>/dev/null || true

log_info "Reload systemd..."
systemctl daemon-reload

log_info "Enable services..."
systemctl enable box-net.service
systemctl enable box-api.service
systemctl enable box-watchdog.timer 2>/dev/null || true
systemctl enable box-rescue.timer 2>/dev/null || true

# ============================================
log_section "7/7 - Cài đặt MQTT Broker & WiFi Fixes"
# ============================================

# Install Mosquitto MQTT Broker
log_info "Cài đặt Mosquitto MQTT Broker..."
apt install -y mosquitto mosquitto-clients

# Configure Mosquitto
mkdir -p /etc/mosquitto/conf.d
cat > /etc/mosquitto/conf.d/classlink.conf << 'EOF'
listener 1883
allow_anonymous true
persistence true
persistence_location /var/lib/mosquitto/
EOF

systemctl enable mosquitto
systemctl restart mosquitto
log_info "Mosquitto MQTT Broker đã được cài đặt"

# Run WiFi fixes
log_info "Khắc phục cấu hình WiFi..."
if [ -f "$SCRIPT_DIR/fix-wifi.sh" ]; then
    chmod +x "$SCRIPT_DIR/fix-wifi.sh"
    bash "$SCRIPT_DIR/fix-wifi.sh" || true
fi

# Copy rescue script
log_info "Cài đặt Rescue Mode..."
if [ -f "$SCRIPT_DIR/rescue-mode.sh" ]; then
    cp "$SCRIPT_DIR/rescue-mode.sh" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/rescue-mode.sh"
fi

# ============================================
log_section "Hoàn tất!"
# ============================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       ✅ CÀI ĐẶT THÀNH CÔNG!             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "📁 Thư mục cài đặt: ${CYAN}$INSTALL_DIR${NC}"
echo ""
echo -e "🔧 Các lệnh hữu ích:"
echo -e "   ${CYAN}sudo /opt/classlink/net/box-ap-on${NC}     - Bật AP mode"
echo -e "   ${CYAN}sudo /opt/classlink/net/box-net-reset${NC} - Reset network"
echo ""
echo -e "🌐 Sau khi reboot:"
echo -e "   - Raspberry Pi sẽ phát WiFi: ${YELLOW}ClassLink-Setup${NC}"
echo -e "   - Password: ${YELLOW}classlink2024${NC}"
echo -e "   - Web Dashboard: ${YELLOW}http://192.168.4.1:8000${NC}"
echo ""
echo -e "${YELLOW}⚡ Khởi động lại để hoàn tất:${NC}"
echo -e "   ${CYAN}sudo reboot${NC}"
echo ""

exit 0
