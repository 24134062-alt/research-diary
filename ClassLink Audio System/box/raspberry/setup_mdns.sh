#!/bin/bash
#
# ClassLink mDNS Setup Script
# 
# This script configures Avahi (mDNS) so you can access the Pi via:
#   http://classlink.local:8000
# instead of remembering IP addresses like 192.168.4.1
#
# Usage: sudo bash setup_mdns.sh

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   ClassLink - mDNS Setup Script                        ║"
echo "║   Access via: http://classlink.local:8000              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "[ERROR] Please run as root: sudo bash setup_mdns.sh"
    exit 1
fi

echo "[1/4] Installing Avahi daemon..."
apt-get update -qq
apt-get install -y avahi-daemon avahi-utils

echo "[2/4] Setting hostname to 'classlink'..."
hostnamectl set-hostname classlink

# Update /etc/hosts
sed -i 's/raspberrypi/classlink/g' /etc/hosts

echo "[3/4] Enabling and starting Avahi service..."
systemctl enable avahi-daemon
systemctl restart avahi-daemon

echo "[4/4] Testing mDNS resolution..."
sleep 2

# Test if mDNS is working
if avahi-resolve-host-name classlink.local &>/dev/null; then
    RESOLVED_IP=$(avahi-resolve-host-name classlink.local | awk '{print $2}')
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║              mDNS SETUP SUCCESSFUL! ✅                 ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║                                                        ║"
    echo "║  Hostname:     classlink                               ║"
    echo "║  mDNS Name:    classlink.local                         ║"
    echo "║  Current IP:   $RESOLVED_IP                        ║"
    echo "║                                                        ║"
    echo "║  Access dashboard at:                                  ║"
    echo "║  👉 http://classlink.local:8000                        ║"
    echo "║                                                        ║"
    echo "║  📱 Works on:                                          ║"
    echo "║     - Mac/Linux: ✅ Built-in support                  ║"
    echo "║     - Windows: ⚠️  Needs Bonjour (iTunes)             ║"
    echo "║     - Android/iOS: ✅ Built-in support                ║"
    echo "║                                                        ║"
    echo "║  ⚠️  IMPORTANT: Reboot required to apply hostname      ║"
    echo "║                                                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Run: sudo reboot"
else
    echo ""
    echo "[WARNING] mDNS test failed. Please check:"
    echo "  1. Is avahi-daemon running? systemctl status avahi-daemon"
    echo "  2. Try rebooting: sudo reboot"
fi
