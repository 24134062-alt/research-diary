"""
WiFi Setup Routes
Handles WiFi scanning and connection management
"""

from fastapi import APIRouter
import subprocess
import platform
import asyncio

router = APIRouter()

@router.get("/connected")
async def get_connected_wifi():
    """Get currently connected WiFi network"""
    if platform.system() == "Linux":
        try:
            # Get current connection using nmcli
            result = subprocess.check_output(
                ["nmcli", "-t", "-f", "ACTIVE,SSID", "device", "wifi"],
                stderr=subprocess.STDOUT,
                timeout=5
            )
            output = result.decode("utf-8", errors="ignore")
            
            for line in output.splitlines():
                parts = line.split(":")
                if len(parts) >= 2 and parts[0] == "yes":
                    return {"connected": True, "ssid": parts[1]}
            
            return {"connected": False, "ssid": None}
            
        except Exception as e:
            print(f"[WiFi] Error getting connected network: {e}")
            return {"connected": False, "ssid": None, "error": str(e)}
    else:
        # Windows demo
        return {"connected": True, "ssid": "Demo_Network"}

@router.get("/scan")
async def scan_wifi():
    """Scan available WiFi networks"""
    import subprocess
    import platform
    import asyncio
    
    wifi_networks = []
    
    if platform.system() == "Linux":
        # Real WiFi scanning for Raspberry Pi using nmcli
        try:
            # Trigger fresh WiFi scan (may fail without sudo, that's OK)
            print("[WiFi Scan] Triggering rescan...")
            rescan_result = subprocess.run(
                ["sudo", "nmcli", "device", "wifi", "rescan"],
                capture_output=True,
                timeout=5
            )
            
            # Check if rescan succeeded
            if rescan_result.returncode == 0:
                print("[WiFi Scan] Rescan triggered successfully, waiting for results...")
                await asyncio.sleep(3)  # Wait longer for fresh results
            else:
                print(f"[WiFi Scan] Rescan failed (code {rescan_result.returncode}), using cached results")
                # NetworkManager scans periodically anyway, so cached results are fine
            
            # Get WiFi list (includes both fresh and cached networks)
            result = subprocess.check_output(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                stderr=subprocess.STDOUT,
                timeout=10
            )
            output = result.decode("utf-8", errors="ignore")
            
            # DEBUG: Print raw output
            print(f"[WiFi Scan] Raw nmcli output:")
            print(output)
            print(f"[WiFi Scan] Total lines: {len(output.splitlines())}")
            
            seen_ssids = set()
            for line in output.splitlines():
                parts = line.split(":")
                if len(parts) >= 3:
                    ssid = parts[0].strip()
                    signal = parts[1].strip()
                    security = parts[2].strip()
                    
                    # Skip empty SSIDs and duplicates
                    if not ssid or ssid in seen_ssids:
                        continue
                    
                    seen_ssids.add(ssid)
                    
                    try:
                        signal_int = int(signal)
                    except:
                        signal_int = 0
                    
                    wifi_networks.append({
                        "ssid": ssid,
                        "signal": signal_int,
                        "secure": bool(security and security != "--")
                    })
            
            print(f"[WiFi Scan] Parsed {len(wifi_networks)} networks")
            
            # Sort by signal strength (highest first)
            wifi_networks.sort(key=lambda x: x["signal"], reverse=True)
            
        except subprocess.TimeoutExpired:
            print("[WiFi] Scan timeout")
            return [{"ssid": "⚠️ Scan timeout", "signal": 0, "secure": False}]
        except FileNotFoundError:
            print("[WiFi] nmcli not found - NetworkManager not installed")
            return [{"ssid": "❌ NetworkManager not installed", "signal": 0, "secure": False}]
        except Exception as e:
            print(f"[WiFi] Linux scan error: {e}")
            # Fallback mock for demo
            return [
                {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
                {"ssid": "School_Guest", "signal": 60, "secure": False}
            ]
    
    elif platform.system() == "Windows":
        # Windows WiFi scanning (for testing)
        try:
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "networks", "mode=bssid"], 
                stderr=subprocess.STDOUT
            )
            output = result.decode("utf-8", errors="ignore")
            
            current_ssid = None
            current_signal = None
            
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("SSID"):
                    if current_ssid:
                        wifi_networks.append({
                            "ssid": current_ssid,
                            "signal": current_signal or 0,
                            "secure": True 
                        })
                    current_ssid = line.split(":", 1)[1].strip()
                    current_signal = None
                elif line.startswith("Signal"):
                     try:
                        current_signal = int(line.split(":", 1)[1].strip().replace("%", ""))
                     except:
                        current_signal = 0
            
            if current_ssid:
                wifi_networks.append({
                    "ssid": current_ssid,
                    "signal": current_signal or 0,
                    "secure": True
                })
                
        except Exception as e:
            print(f"[WiFi] Windows scan error: {e}")
            return [
                {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
                {"ssid": "School_Guest", "signal": 60, "secure": False}
            ]
    else:
        # Unknown OS - return mock
        return [
             {"ssid": "ClassLink_Teacher", "signal": 90, "secure": True},
             {"ssid": "School_Guest", "signal": 60, "secure": False}
        ]

    # Return networks (already deduplicated in Linux parsing loop)
    return wifi_networks

@router.post("/connect")
async def connect_wifi(data: dict):
    """Connect to a WiFi network and save credentials"""
    import subprocess
    import platform
    
    ssid = data.get("ssid")
    password = data.get("password")
    
    if not ssid:
        return {"status": "error", "message": "SSID is required"}
    
    print(f"[WiFi] Attempting to connect to {ssid}")
    
    if platform.system() == "Linux":
        try:
            # Use sudo + nmcli to connect - needs root for WiFi operations
            cmd = ["sudo", "nmcli", "device", "wifi", "connect", ssid]
            
            if password:
                cmd.extend(["password", password])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # WiFi connection can take time
            )
            
            if result.returncode == 0:
                print(f"✅ Connected to {ssid}")
                
                # Wait for IP address to be assigned
                await asyncio.sleep(3)
                
                # Get new IP address
                new_ip = None
                try:
                    ip_result = subprocess.check_output(
                        ["ip", "-4", "addr", "show", "wlan0"],
                        stderr=subprocess.STDOUT,
                        timeout=5
                    )
                    ip_output = ip_result.decode("utf-8", errors="ignore")
                    # Parse IP from output like "inet 192.168.0.105/24"
                    import re
                    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', ip_output)
                    if match:
                        new_ip = match.group(1)
                except Exception as e:
                    print(f"[WiFi] Error getting new IP: {e}")
                
                new_url = f"http://{new_ip}:8000" if new_ip else None
                
                return {
                    "status": "success",
                    "message": f"Connected to {ssid}. Password saved.",
                    "ssid": ssid,
                    "new_ip": new_ip,
                    "new_url": new_url
                }
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                print(f"❌ Connection failed: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Failed to connect: {error_msg}",
                    "ssid": ssid
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Connection timeout after 30 seconds"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}"
            }
    else:
        # Non-Linux (testing on Windows)
        await asyncio.sleep(2)
        return {
            "status": "success",
            "message": f"[Demo] Connected to {ssid}",
            "ssid": ssid
        }

@router.post("/disconnect")
async def disconnect_wifi():
    """Disconnect from current WiFi and switch to AP mode"""
    import platform
    
    if platform.system() != "Linux":
        await asyncio.sleep(1)
        return {
            "status": "success",
            "message": "[Demo] Disconnected and switched to AP mode",
            "ap_ssid": "ClassLink-Setup",
            "ap_url": "http://192.168.4.1:8000"
        }
    
    try:
        # Step 1: Disconnect from current WiFi
        print("[WiFi] Disconnecting from current WiFi...")
        subprocess.run(
            ["sudo", "nmcli", "device", "disconnect", "wlan0"],
            capture_output=True,
            timeout=10
        )
        
        await asyncio.sleep(1)
        
        # Step 2: Delete old hotspot if exists
        print("[WiFi] Removing old hotspot profile...")
        subprocess.run(
            ["sudo", "nmcli", "connection", "delete", "ClassLink-Hotspot"],
            capture_output=True,
            timeout=5
        )
        
        await asyncio.sleep(1)
        
        # Step 3: Try using box-ap-on script first
        print("[WiFi] Trying box-ap-on script...")
        ap_result = subprocess.run(
            ["sudo", "/opt/classlink/net/box-ap-on"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if ap_result.returncode == 0:
            return {
                "status": "success",
                "message": "Đã ngắt WiFi và bật AP mode",
                "ap_ssid": "ClassLink-Setup",
                "ap_password": "classlink2024", 
                "ap_url": "http://192.168.4.1:8000"
            }
        
        # Step 4: Fallback - create hotspot directly with nmcli
        print("[WiFi] box-ap-on failed, using fallback method...")
        
        # Create hotspot directly
        create_result = subprocess.run([
            "sudo", "nmcli", "connection", "add",
            "type", "wifi",
            "ifname", "wlan0",
            "con-name", "ClassLink-Hotspot",
            "autoconnect", "no",
            "ssid", "ClassLink-Setup",
            "wifi.mode", "ap",
            "wifi.band", "bg",
            "wifi.channel", "7",
            "ipv4.method", "shared",
            "ipv4.addresses", "192.168.4.1/24",
            "wifi-sec.key-mgmt", "wpa-psk",
            "wifi-sec.psk", "classlink2024"
        ], capture_output=True, text=True, timeout=15)
        
        if create_result.returncode != 0:
            # Try simpler hotspot command
            print("[WiFi] Trying simple hotspot command...")
            subprocess.run([
                "sudo", "nmcli", "device", "wifi", "hotspot",
                "ssid", "ClassLink-Setup",
                "password", "classlink2024"
            ], capture_output=True, text=True, timeout=15)
        
        # Activate hotspot
        await asyncio.sleep(1)
        activate_result = subprocess.run(
            ["sudo", "nmcli", "connection", "up", "ClassLink-Hotspot"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # Verify hotspot is active
        await asyncio.sleep(2)
        check_result = subprocess.run(
            ["nmcli", "connection", "show", "--active"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "ClassLink-Hotspot" in check_result.stdout or "Hotspot" in check_result.stdout:
            return {
                "status": "success",
                "message": "Đã ngắt WiFi và bật AP mode (fallback)",
                "ap_ssid": "ClassLink-Setup",
                "ap_password": "classlink2024", 
                "ap_url": "http://192.168.4.1:8000"
            }
        else:
            return {
                "status": "error",
                "message": "Không thể bật AP mode. Vui lòng chạy: sudo /opt/classlink/net/box-ap-on"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Timeout khi chuyển đổi mạng"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi: {str(e)}"
        }

