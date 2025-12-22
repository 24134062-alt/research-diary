#!/bin/bash
###############################################
# ClassLink - WiFi Fix Script
# 
# Khắc phục các lỗi WiFi phổ biến:
# - Xung đột giữa hostapd/dnsmasq và NetworkManager
# - Thiếu WiFi Country Code
# - Sóng WiFi ẩn hiện (flapping)
# - Bị kẹt loading khi truy cập web
###############################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[FIX]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[FIX]${NC} $1"
}

log_error() {
    echo -e "${RED}[FIX]${NC} $1"
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

log_section "ClassLink WiFi Fix"
echo ""
echo "Script này sẽ khắc phục các lỗi WiFi phổ biến:"
echo "  - Xung đột dịch vụ mạng"
echo "  - Thiếu WiFi Country Code"
echo "  - Sóng WiFi ẩn hiện"
echo ""

# ============================================
log_section "1/5 - Dừng và vô hiệu hóa dịch vụ cũ"
# ============================================

log_info "Dừng hostapd..."
systemctl stop hostapd 2>/dev/null || true
systemctl disable hostapd 2>/dev/null || true
systemctl mask hostapd 2>/dev/null || true

log_info "Dừng dnsmasq độc lập..."
systemctl stop dnsmasq 2>/dev/null || true
systemctl disable dnsmasq 2>/dev/null || true
systemctl mask dnsmasq 2>/dev/null || true

log_info "Dừng dhcpcd..."
systemctl stop dhcpcd 2>/dev/null || true
systemctl disable dhcpcd 2>/dev/null || true
systemctl mask dhcpcd 2>/dev/null || true

log_info "✅ Đã vô hiệu hóa các dịch vụ cũ"

# ============================================
log_section "2/5 - Dọn dẹp cấu hình cũ"
# ============================================

# Remove wlan0 static config from dhcpcd.conf
if [ -f /etc/dhcpcd.conf ]; then
    log_info "Xóa cấu hình wlan0 trong dhcpcd.conf..."
    sed -i '/# ClassLink AP/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf 2>/dev/null || true
    sed -i '/interface wlan0/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf 2>/dev/null || true
fi

# Clean up old hostapd config
if [ -f /etc/hostapd/hostapd.conf ]; then
    log_info "Backup và xóa hostapd.conf cũ..."
    mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.bak 2>/dev/null || true
fi

# Clean up old dnsmasq PID files
log_info "Dọn dẹp PID files..."
rm -f /var/run/dnsmasq*.pid 2>/dev/null || true

log_info "✅ Đã dọn dẹp cấu hình cũ"

# ============================================
log_section "3/5 - Thiết lập WiFi Country Code"
# ============================================

WIFI_COUNTRY="VN"

# Set in wpa_supplicant
WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
if [ -f "$WPA_CONF" ]; then
    if ! grep -q "country=" "$WPA_CONF"; then
        log_info "Thêm country=$WIFI_COUNTRY vào wpa_supplicant.conf..."
        sed -i "1i country=$WIFI_COUNTRY" "$WPA_CONF"
    else
        log_info "Cập nhật country=$WIFI_COUNTRY trong wpa_supplicant.conf..."
        sed -i "s/^country=.*/country=$WIFI_COUNTRY/" "$WPA_CONF"
    fi
else
    log_info "Tạo wpa_supplicant.conf mới..."
    mkdir -p /etc/wpa_supplicant
    cat > "$WPA_CONF" << EOF
country=$WIFI_COUNTRY
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
EOF
fi

# Set via raspi-config (non-interactive)
log_info "Thiết lập WiFi region qua raspi-config..."
raspi-config nonint do_wifi_country $WIFI_COUNTRY 2>/dev/null || true

# Set via iw reg
log_info "Thiết lập regulatory domain..."
iw reg set $WIFI_COUNTRY 2>/dev/null || true

log_info "✅ Đã thiết lập WiFi Country: $WIFI_COUNTRY"

# ============================================
log_section "4/5 - Unblock WiFi và kích hoạt NetworkManager"
# ============================================

# Unblock WiFi
log_info "Unblock WiFi (rfkill)..."
rfkill unblock wifi 2>/dev/null || true

# Ensure NetworkManager is running
log_info "Đảm bảo NetworkManager đang chạy..."
systemctl unmask NetworkManager 2>/dev/null || true
systemctl enable NetworkManager
systemctl restart NetworkManager

# Wait for NetworkManager to be ready
sleep 3

# Check wlan0 status
log_info "Kiểm tra trạng thái wlan0..."
nmcli device status

log_info "✅ NetworkManager đã sẵn sàng"

# ============================================
log_section "5/5 - Kiểm tra và bật AP Mode"
# ============================================

# Check if there's a saved WiFi connection
SAVED_WIFI=$(nmcli -t -f NAME,TYPE connection show | grep ":802-11-wireless$" | grep -v "Hotspot" | head -1 | cut -d: -f1)

if [ -z "$SAVED_WIFI" ]; then
    log_info "Không có WiFi đã lưu, bật AP Mode..."
    
    # Delete old hotspot if exists
    nmcli connection delete "ClassLink-Hotspot" 2>/dev/null || true
    
    # Create new hotspot
    nmcli connection add \
        type wifi \
        ifname wlan0 \
        con-name "ClassLink-Hotspot" \
        autoconnect no \
        ssid "ClassLink-Setup" \
        wifi.mode ap \
        wifi.band bg \
        wifi.channel 7 \
        ipv4.method shared \
        ipv4.addresses "192.168.4.1/24" \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "classlink2024" 2>/dev/null || true
    
    # Activate hotspot
    nmcli connection up "ClassLink-Hotspot" 2>/dev/null || true
    
    log_info "✅ AP Mode đã được bật"
else
    log_info "Đã có WiFi lưu: $SAVED_WIFI"
    log_info "Giữ nguyên kết nối hiện tại"
fi

# ============================================
log_section "Hoàn tất!"
# ============================================

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✅ KHẮC PHỤC WIFI THÀNH CÔNG!        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "📋 Đã thực hiện:"
echo -e "   ✓ Vô hiệu hóa hostapd, dnsmasq, dhcpcd"
echo -e "   ✓ Dọn dẹp cấu hình cũ"
echo -e "   ✓ Thiết lập WiFi Country: VN"
echo -e "   ✓ Unblock WiFi và kích hoạt NetworkManager"
echo ""
echo -e "${YELLOW}⚡ Bước tiếp theo:${NC}"
echo -e "   ${CYAN}sudo reboot${NC}"
echo ""
echo -e "Sau khi reboot, tìm WiFi:"
echo -e "   📶 SSID: ${YELLOW}ClassLink-Setup${NC}"
echo -e "   🔑 Password: ${YELLOW}classlink2024${NC}"
echo -e "   🌐 Web: ${YELLOW}http://192.168.4.1:8000${NC}"
echo ""

exit 0
