# MQTT Topics

## Broker Info
- **Host**: (Configurable, e.g., `test.mosquitto.org` or local IP)
- **Port**: 1883

## Topics

### 1. Control (Subscribed by Glasses)
- **Topic**: `audio/control`
- **Payload**: JSON
  ```json
  {
    "command": "start_record" | "stop_record" | "reboot"
  }
  ```

### 2. Text / Display (Subscribed by Glasses)
- **Topic**: `glasses/text`
- **Payload**: JSON
  ```json
  {
    "text": "Hello world",
    "duration": 5000,
    "clear": false
  }
  ```
- **Description**: Text to be displayed on the OLED screen.

### 3. Uplink Status (Published by Glasses)
- **Topic**: `glasses/status`
- **Payload**: JSON
  ```json
  {
    "battery": 85,
    "wifi_rssi": -60,
    "status": "recording" | "idle"
  }
  ```
