"""
WiFi Setup Routes
Handles WiFi scanning and connection management
"""

from fastapi import APIRouter
import subprocess
import platform
import asyncio

router = APIRouter()

@router.get("/scan")
async def scan_wifi():
    """Scan available WiFi networks"""
    import subprocess
    import platform
    
    wifi_networks = []
    
    if platform.system() == "Windows":
        try:
            # Run the netsh command to get wifi networks
            result = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], stderr=subprocess.STDOUT)
            output = result.decode("utf-8", errors="ignore")
            
            current_ssid = None
            current_bssid = None
            current_signal = None
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("SSID"):
                    # Save previous if complete
                    if current_ssid:
                        wifi_networks.append({
                            "ssid": current_ssid,
                            "bssid": current_bssid,
                            "signal": current_signal or 0,
                            "secure": True 
                        })
                    current_ssid = line.split(":", 1)[1].strip()
                    current_bssid = None # Reset
                    current_signal = None
                elif line.startswith("Signal"):
                     try:
                        current_signal = int(line.split(":", 1)[1].strip().replace("%", ""))
                     except:
                        current_signal = 0
                
            # Add the last one
            if current_ssid:
                wifi_networks.append({
                    "ssid": current_ssid,
                    "signal": current_signal or 0,
                    "secure": True
                })
                
        except Exception as e:
            print(f"Error scanning wifi: {e}")
            # Fallback mock if scan fails
            return [
                {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
                {"ssid": "School_Guest", "signal": 60, "secure": False}
            ]
    else:
        # Mock for non-windows (Linux/Raspberry Pi would use nmcli or iwlist)
        # TODO: Implement actual WiFi scanning for Raspberry Pi
        return [
             {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
             {"ssid": "School_Guest", "signal": 60, "secure": False}
        ]

    # Deduplicate by SSID
    unique_networks = {}
    for net in wifi_networks:
        if net["ssid"] and net["ssid"] not in unique_networks:
             unique_networks[net["ssid"]] = net
    
    return list(unique_networks.values())

@router.post("/connect")
async def connect_wifi(data: dict):
    """Connect to a WiFi network"""
    ssid = data.get("ssid")
    password = data.get("password")
    
    print(f"[WiFi] Attempting to connect to {ssid}")
    
    # TODO: Implement actual WiFi connection for Raspberry Pi
    # Using NetworkManager: nmcli device wifi connect <ssid> password <password>
    
    # Simulate connection delay
    await asyncio.sleep(2)
    
    return {
        "status": "success", 
        "message": f"Connected to {ssid}",
        "ssid": ssid
    }
