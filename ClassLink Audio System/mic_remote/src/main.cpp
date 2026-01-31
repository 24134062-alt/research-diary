/*************************************************
 * ClassLink Audio System - Mic Remote Controller
 *
 * Phần cứng:
 * - ESP32
 * - INMP441 I2S Microphone
 * - Nút bấm AI
 * - LED trạng thái
 * - KHÔNG CÓ OLED
 *
 * Kết nối WiFi tới ESP32 Box (CLASS-BOX)
 *************************************************/

#include "../include/wifi_config.h"
#include "i2s_mic.h"
#include "uplink_audio.h"
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFi.h>


// ====== WiFi Multi-Network Support ======
WiFiNetwork wifi_list[MAX_WIFI_NETWORKS];
Preferences wifi_prefs;

// ====== MQTT Config - Raspberry Pi ======
const char *MQTT_SERVER = "192.168.4.1";
const int MQTT_PORT = 1883;

// ====== Audio Config ======
const char *BOX_IP = "192.168.4.1";
const int AUDIO_PORT = 12345;

// ====== GPIO Pins ======
#define AI_BUTTON_PIN 12
#define LED_STATUS_PIN 2 // LED trạng thái (built-in)
#define BATTERY_PIN 34

// ====== Objects ======
WiFiClient espClient;
PubSubClient mqtt(espClient);
I2SMic mic;
UplinkAudio uplink;

// ====== State ======
bool isRecording = false;
bool aiModeActive = false;
String currentMode = "class"; // "class" or "private"
uint8_t audioBuffer[1024];

// Button debouncing
unsigned long lastAIButtonPress = 0;
const unsigned long DEBOUNCE_DELAY = 300;

// LED blinking
unsigned long lastLedBlink = 0;
bool ledState = false;

// ====== MQTT Callback ======
void mqttCallback(char *topic, byte *payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.printf("[MQTT] Topic: %s, Msg: %s\n", topic, msg.c_str());

  if (String(topic) == "audio/control") {
    if (msg.indexOf("start") >= 0) {
      isRecording = true;
      Serial.println("[MIC] Recording Started");
    } else if (msg.indexOf("stop") >= 0) {
      isRecording = false;
      Serial.println("[MIC] Recording Stopped");
    }
  } else if (String(topic) == "device/mic_remote/mode") {
    currentMode = msg;
    Serial.printf("[MIC] Mode updated to: %s\n", currentMode.c_str());
  }

  // ====== NEW: WiFi OTA Update ======
  else if (String(topic) == "classlink/config/wifi") {
    Serial.println("[MQTT] 📡 WiFi OTA config update received!");

    // Parse JSON
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, msg);

    if (error) {
      Serial.printf("[MQTT][ERROR] JSON parse failed: %s\n", error.c_str());
      return;
    }

    const char *new_ssid = doc["ssid"];
    const char *new_password = doc["password"];

    if (new_ssid == nullptr || new_password == nullptr) {
      Serial.println("[MQTT][ERROR] Missing ssid or password");
      return;
    }

    // Handle OTA update
    wifi_ota_update(new_ssid, new_password);
  }
}

// ====== WiFi Functions ======
void wifi_load_list() {
  wifi_prefs.begin(WIFI_PREFS_NAMESPACE, false);

  strcpy(wifi_list[0].ssid, DEFAULT_WIFI_SSID);
  strcpy(wifi_list[0].password, DEFAULT_WIFI_PASS);
  wifi_list[0].priority = 0;

  for (int i = 1; i < MAX_WIFI_NETWORKS; i++) {
    String key_ssid = "ssid_" + String(i);
    String key_pass = "pass_" + String(i);

    String ssid = wifi_prefs.getString(key_ssid.c_str(), "");
    String pass = wifi_prefs.getString(key_pass.c_str(), "");

    if (ssid.length() > 0) {
      strcpy(wifi_list[i].ssid, ssid.c_str());
      strcpy(wifi_list[i].password, pass.c_str());
      wifi_list[i].priority = i;
    } else {
      wifi_list[i].ssid[0] = '\0';
      wifi_list[i].priority = 255;
    }
  }

  wifi_prefs.end();
}

void wifi_save_list() {
  wifi_prefs.begin(WIFI_PREFS_NAMESPACE, false);

  for (int i = 1; i < MAX_WIFI_NETWORKS; i++) {
    String key_ssid = "ssid_" + String(i);
    String key_pass = "pass_" + String(i);

    if (wifi_list[i].ssid[0] != '\0') {
      wifi_prefs.putString(key_ssid.c_str(), wifi_list[i].ssid);
      wifi_prefs.putString(key_pass.c_str(), wifi_list[i].password);
    } else {
      wifi_prefs.remove(key_ssid.c_str());
      wifi_prefs.remove(key_pass.c_str());
    }
  }

  wifi_prefs.end();
}

bool wifi_connect() {
  for (int i = 0; i < MAX_WIFI_NETWORKS; i++) {
    if (wifi_list[i].ssid[0] == '\0')
      continue;

    Serial.printf("[WiFi] Trying priority %d: %s", i, wifi_list[i].ssid);

    int n = WiFi.scanNetworks();
    bool found = false;

    for (int j = 0; j < n; j++) {
      if (WiFi.SSID(j) == String(wifi_list[i].ssid)) {
        found = true;
        break;
      }
    }

    if (!found) {
      Serial.println(" - Not available");
      continue;
    }

    WiFi.begin(wifi_list[i].ssid, wifi_list[i].password);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      delay(500);
      Serial.print(".");
      digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.printf("\n[WiFi] ✅ Connected to %s\n", wifi_list[i].ssid);
      digitalWrite(LED_STATUS_PIN, HIGH);
      return true;
    } else {
      Serial.println(" - Failed");
      WiFi.disconnect();
    }
  }

  Serial.println("[WiFi] ❌ No available networks");
  return false;
}

void wifi_add_network(const char *ssid, const char *password,
                      uint8_t priority) {
  if (priority == 0 || priority >= MAX_WIFI_NETWORKS)
    return;

  for (int i = 0; i < MAX_WIFI_NETWORKS; i++) {
    if (strcmp(wifi_list[i].ssid, ssid) == 0) {
      strcpy(wifi_list[i].password, password);
      wifi_list[i].priority = priority;
      wifi_save_list();
      return;
    }
  }

  strcpy(wifi_list[priority].ssid, ssid);
  strcpy(wifi_list[priority].password, password);
  wifi_list[priority].priority = priority;
  wifi_save_list();
}

void wifi_ota_update(const char *new_ssid, const char *new_password) {
  Serial.println("[WiFi] OTA Config Update Received");
  Serial.printf("[WiFi]   New SSID: %s\n", new_ssid);

  wifi_add_network(new_ssid, new_password, 1);

  Serial.println("[WiFi] ⏰ Waiting 3 seconds for ESP32 Box...");
  for (int i = 3; i > 0; i--) {
    Serial.printf("[WiFi]    Reconnecting in %d seconds...\n", i);
    delay(1000);
  }

  WiFi.disconnect();
  delay(500);

  if (wifi_connect()) {
    Serial.println("[WiFi] ✅ Reconnected successfully!");
  } else {
    Serial.println("[WiFi] ❌ Reconnect failed");
  }
}

// ====== WiFi Connect ======
void connectWiFi() {
  Serial.println("[WiFi] Initializing multi-network support...");
  wifi_load_list();

  if (wifi_connect()) {
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("[WiFi] Failed to connect!");
    digitalWrite(LED_STATUS_PIN, LOW);
  }
}

// ====== MQTT Reconnect ======
void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("[MQTT] Connecting...");
    if (mqtt.connect("MicRemote")) {
      Serial.println(" Connected!");

      // Thông báo IP cho Gateway
      String status = "{\"id\":\"mic_remote\",\"ip\":\"" +
                      WiFi.localIP().toString() + "\"}";
      mqtt.publish("glasses/status", status.c_str());

      mqtt.subscribe("audio/control");
      mqtt.subscribe("device/mic_remote/mode");
      mqtt.subscribe("classlink/config/wifi"); // ← NEW: WiFi OTA
      Serial.println("[MQTT] ✅ Subscribed to classlink/config/wifi");
    } else {
      Serial.printf(" Failed (rc=%d), retry in 5s\n", mqtt.state());
      delay(5000);
    }
  }
}

// ====== Get Battery Level ======
int getBatteryLevel() {
  int raw = analogRead(BATTERY_PIN);
  // Battery: 3.0V (0%) to 4.2V (100%)
  int percentage = map(raw, 2480, 3472, 0, 100);
  return constrain(percentage, 0, 100);
}

// ====== Setup ======
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=========================================");
  Serial.println("   ClassLink - Mic Remote Controller    ");
  Serial.println("=========================================");

  // GPIO Setup
  pinMode(AI_BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(BATTERY_PIN, INPUT);

  // Connect WiFi to ESP32 Box
  connectWiFi();

  // MQTT Setup
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);

  // Audio Setup
  mic.setup();
  uplink.begin(BOX_IP, AUDIO_PORT);

  Serial.println("-----------------------------------------");
  Serial.println("[READY] Mic Remote is running!");
  Serial.printf("  Battery: %d%%\n", getBatteryLevel());
  Serial.println("-----------------------------------------");
}

// ====== Loop ======
void loop() {
  // WiFi reconnect
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  // MQTT reconnect
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();

  // AI Button Handler - Nhấn để hỏi AI
  if (digitalRead(AI_BUTTON_PIN) == LOW) {
    if (millis() - lastAIButtonPress > DEBOUNCE_DELAY) {
      aiModeActive = !aiModeActive;

      if (aiModeActive) {
        Serial.println("[AI] Mode: ON - Recording for AI");
        digitalWrite(LED_STATUS_PIN, HIGH);
        // Notify server
        mqtt.publish("device/mic_remote/ai", "start");
      } else {
        Serial.println("[AI] Mode: OFF");
        // Notify server
        mqtt.publish("device/mic_remote/ai", "stop");
      }

      lastAIButtonPress = millis();
    }
  }

  // LED Blinking when AI mode active
  if (aiModeActive) {
    if (millis() - lastLedBlink > 200) {
      ledState = !ledState;
      digitalWrite(LED_STATUS_PIN, ledState);
      lastLedBlink = millis();
    }
  }

  // Audio Recording & Sending
  if (isRecording || aiModeActive) {
    size_t bytesRead = mic.read(audioBuffer, sizeof(audioBuffer));
    if (bytesRead > 0) {
      uplink.sendAudioPacket(audioBuffer, bytesRead, aiModeActive,
                             (currentMode == "class"));
    }
  }

  delay(10); // Prevent watchdog reset
}
