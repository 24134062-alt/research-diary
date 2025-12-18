/**
 * Configuration File Template for ClassLink Glasses
 *
 * INSTRUCTIONS:
 * 1. Copy this file to 'config.h' in the same directory
 * 2. Edit the values below with your actual credentials
 * 3. config.h is ignored by git - DO NOT commit it
 */

#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "Your_WiFi_Name"
#define WIFI_PASSWORD "Your_WiFi_Password"

// MQTT Broker Configuration
#define MQTT_HOST "test.mosquitto.org"
#define MQTT_PORT 1883

// Target PC for audio streaming
#define PC_IP "192.168.1.100"
#define PC_UDP_PORT 12345

// Voice Activity Detection
// Higher value = less sensitive (300-500 recommended)
#define VAD_THRESHOLD 300

// Device ID (unique for each glasses pair)
#define DEVICE_ID "glasses_01"

#endif // CONFIG_H
