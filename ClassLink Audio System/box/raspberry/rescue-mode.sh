#!/bin/bash
###############################################
# ClassLink - Rescue Mode Script
# 
# Script này đảm bảo luôn có đường kết nối vào Pi:
# - Giữ SSH luôn hoạt động
# - Tự động bật AP mode nếu mất WiFi
# - Chạy như cron job để giám sát
###############################################

# Config
AP_SSID="ClassLink-Setup"
AP_PASS="classlink2024"
AP_CON_NAME="ClassLink-Hotspot"
LOG_FILE="/var/log/classlink-rescue.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Ensure SSH is running
ensure_ssh() {
    if ! systemctl is-active --quiet ssh; then
        log "SSH not running, starting..."
        systemctl start ssh
    fi
}

# Check network connectivity
check_network() {
    # Check if wlan0 has an IP
    IP=$(ip -4 addr show wlan0 2>/dev/null | grep -oP '(?<=inet\s)\d+\.\d+\.\d+\.\d+' | head -1)
    
    if [ -z "$IP" ]; then
        return 1  # No IP
    fi
    return 0  # Has IP
}

# Enable AP mode as fallback
enable_ap_mode() {
    log "Enabling AP mode as fallback..."
    
    # Delete old hotspot
    nmcli connection delete "$AP_CON_NAME" 2>/dev/null || true
    
    # Create hotspot
    nmcli connection add \
        type wifi \
        ifname wlan0 \
        con-name "$AP_CON_NAME" \
        autoconnect no \
        ssid "$AP_SSID" \
        wifi.mode ap \
        wifi.band bg \
        wifi.channel 7 \
        ipv4.method shared \
        ipv4.addresses "192.168.4.1/24" \
        wifi-sec.key-mgmt wpa-psk \
        wifi-sec.psk "$AP_PASS" 2>/dev/null || true
    
    # Activate
    nmcli connection up "$AP_CON_NAME" 2>/dev/null
    
    log "AP mode enabled: $AP_SSID"
}

# Main rescue logic
main() {
    # Always ensure SSH is running
    ensure_ssh
    
    # Check network
    if ! check_network; then
        log "No network connection detected"
        
        # Wait 10 seconds and check again
        sleep 10
        
        if ! check_network; then
            log "Still no network, enabling AP mode"
            enable_ap_mode
        fi
    fi
}

# Run main
main
