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
    import asyncio
    
    wifi_networks = []
    
    if platform.system() == "Linux":
        # Real WiFi scanning for Raspberry Pi using nmcli
        try:
            # Trigger fresh WiFi scan (may fail without sudo, that's OK)
            print("[WiFi Scan] Triggering rescan...")
            rescan_result = subprocess.run(
                ["nmcli", "device", "wifi", "rescan"],
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
            # Use nmcli to connect - this automatically saves the connection profile
            cmd = ["nmcli", "device", "wifi", "connect", ssid]
            
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
                return {
                    "status": "success",
                    "message": f"Connected to {ssid}. Password saved.",
                    "ssid": ssid
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
