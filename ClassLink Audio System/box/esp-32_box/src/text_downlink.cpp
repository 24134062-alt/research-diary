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

#include <Arduino.h>
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

// ====== Public API ======
void text_downlink_init() {
  Serial.println("[TEXT_DOWNLINK] Initializing MQTT client...");

  // Create MQTT client instance
  static WiFiClient mqttWifiClient;
  mqttClient = new PubSubClient(mqttWifiClient);

  mqttClient->setServer(MQTT_SERVER, MQTT_PORT);

  // Try to connect
  int attempts = 0;
  while (!mqttClient->connected() && attempts < 3) {
    Serial.print("[TEXT_DOWNLINK] Connecting to MQTT...");

    if (mqttClient->connect("ESP32_Box_TextDownlink")) {
      Serial.println(" Connected!");
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
