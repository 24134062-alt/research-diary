"""
WiFi Monitor Service
Monitors WiFi signal strength and emits alerts when thresholds are crossed
"""

import asyncio
import subprocess
from enum import Enum
from typing import Optional, Callable
import time

class SignalLevel(Enum):
    STRONG = "strong"      # > 70%
    MEDIUM = "medium"      # 30-70%
    WEAK = "weak"          # 10-30%
    CRITICAL = "critical"  # < 10%

class WiFiMonitor:
    def __init__(self):
        self.current_signal = 0
        self.current_ssid = None
        self.is_connected = False
        self.previous_level = None
        
        # Callbacks for signal events
        self.on_weak_signal: Optional[Callable] = None
        self.on_critical_signal: Optional[Callable] = None
        self.on_signal_restored: Optional[Callable] = None
        
    async def start_monitoring(self):
        """Start monitoring WiFi signal in background"""
        print("📡 WiFi Monitor started")
        
        while True:
            try:
                await self.check_signal()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"[WiFi Monitor] Error: {e}")
                await asyncio.sleep(10)
    
    async def check_signal(self):
        """Check current WiFi signal strength"""
        try:
            # Get current connection info
            result = subprocess.run(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL", "device", "wifi", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                self.is_connected = False
                return
            
            # Parse output - find the connected network (marked with *)
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] == '*':
                    # This is the active connection
                    self.current_ssid = parts[1]
                    try:
                        self.current_signal = int(parts[2])
                    except:
                        self.current_signal = 0
                    
                    self.is_connected = True
                    await self.evaluate_signal_level()
                    return
            
            # Not connected to any network
            self.is_connected = False
            self.current_signal = 0
            self.current_ssid = None
            
        except subprocess.TimeoutExpired:
            print("[WiFi Monitor] nmcli timeout")
        except Exception as e:
            print(f"[WiFi Monitor] Check error: {e}")
    
    async def evaluate_signal_level(self):
        """Evaluate signal level and trigger callbacks"""
        current_level = self.get_signal_level(self.current_signal)
        
        # Only trigger if level changed
        if current_level == self.previous_level:
            return
        
        print(f"📶 Signal: {self.current_signal}% ({current_level.value}) - {self.current_ssid}")
        
        # Trigger appropriate callbacks
        if current_level == SignalLevel.CRITICAL:
            if self.on_critical_signal:
                await self.on_critical_signal(self.current_signal, self.current_ssid)
        
        elif current_level == SignalLevel.WEAK:
            if self.on_weak_signal:
                await self.on_weak_signal(self.current_signal, self.current_ssid)
        
        elif current_level in [SignalLevel.MEDIUM, SignalLevel.STRONG]:
            # Signal restored from weak/critical
            if self.previous_level in [SignalLevel.WEAK, SignalLevel.CRITICAL]:
                if self.on_signal_restored:
                    await self.on_signal_restored(self.current_signal, self.current_ssid)
        
        self.previous_level = current_level
    
    def get_signal_level(self, signal: int) -> SignalLevel:
        """Determine signal level from percentage"""
        if signal > 70:
            return SignalLevel.STRONG
        elif signal >= 30:
            return SignalLevel.MEDIUM
        elif signal >= 10:
            return SignalLevel.WEAK
        else:
            return SignalLevel.CRITICAL
    
    def get_status(self) -> dict:
        """Get current WiFi status"""
        return {
            "connected": self.is_connected,
            "ssid": self.current_ssid,
            "signal": self.current_signal,
            "level": self.get_signal_level(self.current_signal).value if self.is_connected else None
        }
