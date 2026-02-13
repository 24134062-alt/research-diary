import serial
import json
import asyncio
import threading

class UARTService:
    def __init__(self, port='/dev/ttyS0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.on_message_callback = None
        self.running = False

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"[UART] Connected to {self.port} at {self.baudrate}")
        except Exception as e:
            print(f"[WARN] UART initialization failed on {self.port}: {e}. Running in MOCK mode.")

    def set_callback(self, callback):
        """Set callback function for received JSON messages"""
        self.on_message_callback = callback

    def send(self, data: dict):
        """Send JSON data over UART"""
        if self.ser and self.ser.is_open:
            try:
                msg = json.dumps(data) + "\n"
                self.ser.write(msg.encode('utf-8'))
                # print(f"[UART] Sent: {msg.strip()}")
            except Exception as e:
                print(f"[ERROR] UART send error: {e}")
        else:
            print(f"[MOCK-UART] Sending: {data}")

    async def start(self):
        """Start reading background logic"""
        self.running = True
        print("[UART] Reader loop started")
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    # Non-blocking read (using in_waiting)
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('utf-8').strip()
                        if line:
                            # print(f"[UART][RX] {line}")
                            self._handle_line(line)
                except Exception as e:
                    print(f"[ERROR] UART read error: {e}")
                    # If I/O error, usually means port is dead or disconnected on Pi
                    if "Input/output error" in str(e):
                        print("[UART] Critical I/O error. Switching to MOCK mode to avoid log spam.")
                        try: self.ser.close()
                        except: pass
                        self.ser = None # Fallback to MOCK mode
            
            await asyncio.sleep(0.1 if self.ser else 5.0) # Slow down if in MOCK mode

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

    def _handle_line(self, line):
        try:
            data = json.loads(line)
            if self.on_message_callback:
                self.on_message_callback(data)
        except json.JSONDecodeError:
            # Not a JSON message, maybe a log from ESP32
            if "[GATEWAY]" in line or "[READY]" in line:
                print(f"[ESP32-LOG] {line}")
            pass
