import serial
import time

print('[TEST] Opening UART /dev/ttyS0...')
try:
    ser = serial.Serial('/dev/ttyS0', 115200, timeout=2)
    print('[TEST] UART opened successfully')
    
    # Send test command
    cmd = '{"cmd":"TEST"}\n'
    ser.write(cmd.encode())
    print(f'[TEST] Sent: {cmd.strip()}')
    
    # Read response
    time.sleep(0.5)
    if ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f'[TEST] Received: {response}')
    else:
        print('[TEST] No response from ESP32')
    
    ser.close()
    print('[TEST] UART test completed')
except Exception as e:
    print(f'[ERROR] {e}')
