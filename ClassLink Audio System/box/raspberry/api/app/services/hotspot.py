"""
Hotspot Controller
Manages Access Point (hotspot) mode on Raspberry Pi
"""

import subprocess
import time

class HotspotController:
    def __init__(self):
        self.hotspot_ssid = "ClassLink-Setup"
        self.hotspot_password = "12345678"
        self.connection_name = "ClassLink-Hotspot"
        self.is_ap_mode = False
    
    def enable_ap_mode(self) -> dict:
        """Enable Access Point mode"""
        try:
            print(f"📡 Enabling hotspot: {self.hotspot_ssid}")
            
            # Check if connection profile exists
            check_result = subprocess.run(
                ["nmcli", "connection", "show", self.connection_name],
                capture_output=True,
                timeout=5
            )
            
            if check_result.returncode != 0:
                # Create new hotspot connection
                create_result = subprocess.run(
                    [
                        "nmcli", "device", "wifi", "hotspot",
                        "ssid", self.hotspot_ssid,
                        "password", self.hotspot_password
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if create_result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Failed to create hotspot: {create_result.stderr}"
                    }
            else:
                # Activate existing connection
                activate_result = subprocess.run(
                    ["nmcli", "connection", "up", self.connection_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if activate_result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Failed to activate hotspot: {activate_result.stderr}"
                    }
            
            self.is_ap_mode = True
            print(f"✅ Hotspot enabled: {self.hotspot_ssid}")
            
            return {
                "success": True,
                "ssid": self.hotspot_ssid,
                "mode": "ap"
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def disable_ap_mode(self) -> dict:
        """Disable Access Point mode"""
        try:
            print("📡 Disabling hotspot mode")
            
            result = subprocess.run(
                ["nmcli", "connection", "down", self.connection_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to disable hotspot: {result.stderr}"
                }
            
            self.is_ap_mode = False
            print("✅ Hotspot disabled")
            
            return {
                "success": True,
                "mode": "client"
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> dict:
        """Get hotspot status"""
        return {
            "ap_mode": self.is_ap_mode,
            "ssid": self.hotspot_ssid if self.is_ap_mode else None
        }
