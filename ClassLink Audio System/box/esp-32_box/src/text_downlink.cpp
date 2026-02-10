/*************************************************
 * File: text_downlink.cpp
 *
 * Vai trò:
 * - Nhận text từ Raspberry Pi qua UART
 * - Forward text đến Glasses/Mic Remote qua MQTT
 *
 * Flow:
 * Raspberry Pi → UART → ESP32 Box → MQTT → Glasses OLED
 *************************************************/

#include "../include/wifi_config.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>

// ====== MQTT Config ======
static const char *MQTT_SERVER = "192.168.4.1"; // Raspberry Pi IP (AP mode)
static const int MQTT_PORT = 1883;

// ====== Forward declarations ======
extern WiFiClient espClient; // Declared in main.cpp
static PubSubClient *mqttClient = nullptr;

// ====== Message buffer ======
#define TEXT_BUFFER_SIZE 512
static char textBuffer[TEXT_BUFFER_SIZE];
static int bufferPos = 0;

// ====== Forward declarations ======
void text_downlink_parse_and_publish(const String &line);
void mqtt_callback(char *topic, byte *payload, unsigned int length);

// ====== Public API ======
void text_downlink_init() {
  Serial.println("[TEXT_DOWNLINK] Initializing MQTT client...");

  // Create MQTT client instance
  static WiFiClient mqttWifiClient;
  mqttClient = new PubSubClient(mqttWifiClient);

  mqttClient->setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient->setCallback(mqtt_callback);

  // Try to connect
  int attempts = 0;
  while (!mqttClient->connected() && attempts < 3) {
    Serial.print("[TEXT_DOWNLINK] Connecting to MQTT...");

    if (mqttClient->connect("ESP32_Box_TextDownlink")) {
      Serial.println(" Connected!");

      // Subscribe to WiFi config topic for OTA updates
      if (mqttClient->subscribe("classlink/config/wifi")) {
        Serial.println(
            "[TEXT_DOWNLINK] ✅ Subscribed to classlink/config/wifi");
      } else {
        Serial.println(
            "[TEXT_DOWNLINK][WARN] Failed to subscribe to WiFi config topic");
      }
    } else {
      Serial.printf(" Failed (rc=%d)\n", mqttClient->state());
      attempts++;
      delay(1000);
    }
  }

  if (mqttClient->connected()) {
    Serial.println("[TEXT_DOWNLINK] MQTT ready for text forwarding");
  } else {
    Serial.println(
        "[TEXT_DOWNLINK][WARN] MQTT not connected, will retry later");
  }
}

void text_downlink_loop() {
  // Maintain MQTT connection
  if (mqttClient && !mqttClient->connected()) {
    // Try to reconnect (non-blocking, only 1 attempt per loop)
    if (mqttClient->connect("ESP32_Box_TextDownlink")) {
      Serial.println("[TEXT_DOWNLINK] MQTT reconnected");

      // Re-subscribe after reconnect
      mqttClient->subscribe("classlink/config/wifi");
    }
  }

  if (mqttClient) {
    mqttClient->loop();
  }
}

// ====== Handle text from UART ======
// Called from uart_ctrl.cpp when receiving TEXT_DOWNLINK message
void text_downlink_handle(const String &jsonMessage) {
  if (!mqttClient) {
    Serial.println("[TEXT_DOWNLINK][ERROR] MQTT client not initialized");
    return;
  }

  if (!mqttClient->connected()) {
    Serial.println("[TEXT_DOWNLINK][WARN] MQTT not connected, message dropped");
    return;
  }

  Serial.print("[TEXT_DOWNLINK] Received: ");
  Serial.println(jsonMessage);

  // Parse JSON manually (MVP - no ArduinoJson to save memory)
  // Expected format:
  // {"type":"TEXT_DOWNLINK","target":"glasses_01","text":"Hello from AI"}

  String target = "glasses/text"; // Default broadcast topic
  String text = "";

  // Extract target device (optional)
  int targetIdx = jsonMessage.indexOf("\"target\":\"");
  if (targetIdx >= 0) {
    int startIdx = targetIdx + 10;
    int endIdx = jsonMessage.indexOf("\"", startIdx);
    if (endIdx > startIdx) {
      String deviceId = jsonMessage.substring(startIdx, endIdx);
      target = "glasses/" + deviceId + "/text";
    }
  }

  // AI Answer logic: If message contains "ai" in sender/type, use ai/answer
  // topic This ensures Glasses correctly display it when aiAssistantActive is
  // true
  if (jsonMessage.indexOf("\"sender\":\"ai\"") >= 0 ||
      jsonMessage.indexOf("\"type\":\"AI_ANSWER\"") >= 0) {
    target = "ai/answer";
  }

  // Extract text content (required)
  int textIdx = jsonMessage.indexOf("\"text\":\"");
  if (textIdx >= 0) {
    int startIdx = textIdx + 8; // Length of "text":"
    int endIdx = jsonMessage.indexOf("\"", startIdx);
    if (endIdx > startIdx) {
      text = jsonMessage.substring(startIdx, endIdx);
    }
  }

  if (text.length() == 0) {
    Serial.println("[TEXT_DOWNLINK][ERROR] No text content found in message");
    return;
  }

  // Publish to MQTT
  bool success = mqttClient->publish(target.c_str(), text.c_str());

  if (success) {
    Serial.printf("[TEXT_DOWNLINK][OK] Published to '%s': %s\n", target.c_str(),
                  text.c_str());
  } else {
    Serial.printf("[TEXT_DOWNLINK][ERROR] Failed to publish to '%s'\n",
                  target.c_str());
  }
}

// ====== Alternative: Direct text publish (simple API) ======
void text_downlink_send(const char *deviceId, const char *text) {
  if (!mqttClient || !mqttClient->connected()) {
    Serial.println("[TEXT_DOWNLINK][WARN] Cannot send, MQTT not connected");
    return;
  }

  String topic = "glasses/text";
  if (deviceId != nullptr && strlen(deviceId) > 0) {
    topic = "glasses/" + String(deviceId) + "/text";
  }

  bool success = mqttClient->publish(topic.c_str(), text);

  if (success) {
    Serial.printf("[TEXT_DOWNLINK][OK] Sent to '%s': %s\n", topic.c_str(),
                  text);
  } else {
    Serial.println("[TEXT_DOWNLINK][ERROR] Send failed");
  }
}

// ====== MQTT Callback Handler ======
void mqtt_callback(char *topic, byte *payload, unsigned int length) {
  // Convert payload to string
  char message[512];
  if (length >= sizeof(message)) {
    Serial.println("[MQTT] Message too large, truncating");
    length = sizeof(message) - 1;
  }

  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.printf("[MQTT] Received on topic '%s': %s\n", topic, message);

  // Handle WiFi config updates
  if (strcmp(topic, "classlink/config/wifi") == 0) {
    Serial.println("[MQTT] 📡 WiFi OTA config update received!");

    // Parse JSON
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);

    if (error) {
      Serial.printf("[MQTT][ERROR] JSON parse failed: %s\n", error.c_str());
      return;
    }

    // Extract SSID and password
    const char *new_ssid = doc["ssid"];
    const char *new_password = doc["password"];

    if (new_ssid == nullptr || new_password == nullptr) {
      Serial.println("[MQTT][ERROR] Missing ssid or password in config");
      return;
    }

    Serial.printf("[MQTT] Updating WiFi AP to: %s\n", new_ssid);

    // ⏰ CRITICAL: Wait 10 seconds for other devices (Glasses, Micro) to
    // receive this message. All devices must save credentials before ESP32 Box
    // restarts AP. Increased from 3s to 10s to prevent race condition where
    // devices reconnect before AP is fully restarted.
    Serial.println(
        "[MQTT] ⏰ Waiting 10 seconds for other devices to receive config...");
    for (int i = 10; i > 0; i--) {
      Serial.printf("[MQTT]    Restarting WiFi AP in %d seconds...\n", i);
      delay(1000);
    }

    // Update WiFi credentials (will restart AP)
    if (wifi_update_credentials(new_ssid, new_password)) {
      Serial.println("[MQTT] ✅ WiFi config updated successfully!");
    } else {
      Serial.println("[MQTT][ERROR] Failed to update WiFi config");
    }
  }
}
