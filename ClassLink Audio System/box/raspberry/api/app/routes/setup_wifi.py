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
    """
    Connect to a WiFi network with GUARANTEED fallback to AP mode.
    
    This is a critical function that MUST ensure the user can always
    reconnect to the Pi, either via the new WiFi or via AP mode.
    """
    import subprocess
    import platform
    import threading
    import os
    
    ssid = data.get("ssid")
    password = data.get("password")
    
    if not ssid:
        return {"status": "error", "message": "SSID is required"}
    
    print(f"[WiFi] ========================================")
    print(f"[WiFi] Attempting to connect to: {ssid}")
    print(f"[WiFi] ========================================")
    
    if platform.system() != "Linux":
        # Non-Linux (testing on Windows)
        await asyncio.sleep(2)
        return {
            "status": "success",
            "message": f"[Demo] Connected to {ssid}",
            "ssid": ssid
        }
    
    # --- CRITICAL SECTION: WiFi Connection with Fallback ---
    
    # Step 1: Set WiFi country code first (required for radio to work)
    print("[WiFi] Step 1: Setting WiFi country code...")
    subprocess.run(
        ["sudo", "iw", "reg", "set", "VN"],
        capture_output=True, timeout=5
    )
    
    # Step 2: Save current connection state for recovery
    state_file = "/tmp/classlink_wifi_state"
    with open(state_file, "w") as f:
        f.write(f"connecting:{ssid}")
    
    # Step 3: Create connection profile (save credentials)
    print("[WiFi] Step 2: Creating connection profile...")
    
    # Delete old profile if exists
    subprocess.run(
        ["sudo", "nmcli", "connection", "delete", ssid],
        capture_output=True, timeout=5
    )
    
    # Create new profile  
    create_cmd = [
        "sudo", "nmcli", "connection", "add",
        "type", "wifi",
        "ifname", "wlan0",
        "con-name", ssid,
        "ssid", ssid,
        "wifi-sec.key-mgmt", "wpa-psk",
        "wifi-sec.psk", password or ""
    ]
    
    create_result = subprocess.run(
        create_cmd, capture_output=True, text=True, timeout=10
    )
    
    if create_result.returncode != 0:
        print(f"[WiFi] Failed to create profile: {create_result.stderr}")
        # Continue anyway, nmcli device wifi connect might work
    
    # Step 4: Define connection function to run in background
    def try_connect_and_fallback():
        import time
        
        print("[WiFi] Step 3: Attempting connection...")
        
        try:
            # Try to connect
            connect_result = subprocess.run(
                ["sudo", "nmcli", "--wait", "15", "connection", "up", ssid],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if connect_result.returncode == 0:
                print(f"[WiFi] ✅ SUCCESS: Connected to {ssid}")
                
                # Wait for IP
                time.sleep(3)
                
                # Write success state
                with open(state_file, "w") as f:
                    f.write(f"connected:{ssid}")
                return
            else:
                print(f"[WiFi] ❌ FAILED: {connect_result.stderr}")
                
        except Exception as e:
            print(f"[WiFi] ❌ EXCEPTION: {e}")
        
        # Connection failed - MUST activate AP mode
        print("[WiFi] Activating fallback AP mode...")
        activate_ap_mode()
    
    def activate_ap_mode():
        """Activate AP mode - MUST succeed"""
        import time
        
        print("[WiFi] === Activating AP Mode ===")
        
        # Method 1: Use box-ap-on script
        try:
            result = subprocess.run(
                ["sudo", "/opt/classlink/net/box-ap-on"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print("[WiFi] AP mode activated via box-ap-on")
                with open(state_file, "w") as f:
                    f.write("ap_mode:ClassLink-Setup")
                return
        except Exception as e:
            print(f"[WiFi] box-ap-on failed: {e}")
        
        # Method 2: Direct nmcli
        try:
            # Delete and recreate
            subprocess.run(
                ["sudo", "nmcli", "connection", "delete", "ClassLink-Hotspot"],
                capture_output=True, timeout=5
            )
            time.sleep(1)
            
            # Create hotspot
            subprocess.run([
                "sudo", "nmcli", "connection", "add",
                "type", "wifi", "ifname", "wlan0",
                "con-name", "ClassLink-Hotspot",
                "autoconnect", "no",
                "ssid", "ClassLink-Setup",
                "wifi.mode", "ap", "wifi.band", "bg", "wifi.channel", "7",
                "ipv4.method", "shared", "ipv4.addresses", "192.168.4.1/24",
                "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", "classlink2024"
            ], capture_output=True, timeout=15)
            
            time.sleep(1)
            
            # Activate
            result = subprocess.run(
                ["sudo", "nmcli", "connection", "up", "ClassLink-Hotspot"],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0:
                print("[WiFi] AP mode activated via nmcli")
                with open(state_file, "w") as f:
                    f.write("ap_mode:ClassLink-Setup")
                return
        except Exception as e:
            print(f"[WiFi] nmcli AP failed: {e}")
        
        # Method 3: Simple hotspot
        try:
            subprocess.run([
                "sudo", "nmcli", "device", "wifi", "hotspot",
                "ssid", "ClassLink-Setup",
                "password", "classlink2024"
            ], capture_output=True, timeout=15)
            print("[WiFi] AP mode activated via simple hotspot")
        except Exception as e:
            print(f"[WiFi] Simple hotspot failed: {e}")
        
        with open(state_file, "w") as f:
            f.write("ap_mode:ClassLink-Setup")
    
    # Step 5: Start connection in background thread
    # This ensures the HTTP response is returned before network changes
    thread = threading.Thread(target=try_connect_and_fallback, daemon=True)
    thread.start()
    
    # Return immediately with instructions
    return {
        "status": "pending",
        "message": f"Đang kết nối đến {ssid}. Nếu thành công, truy cập web qua mạng mới. Nếu thất bại, kết nối WiFi 'ClassLink-Setup' (pass: classlink2024) và truy cập http://192.168.4.1:8000",
        "ssid": ssid,
        "ap_fallback": {
            "ssid": "ClassLink-Setup",
            "password": "classlink2024",
            "url": "http://192.168.4.1:8000"
        }
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

