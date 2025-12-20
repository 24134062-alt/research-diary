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

#include "i2s_mic.h"
#include "uplink_audio.h"
#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>


// ====== WiFi Config - Kết nối tới ESP32 Box ======
const char *WIFI_SSID = "CLASS-BOX";
const char *WIFI_PASS = "12345678";

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
  }
}

// ====== WiFi Connect ======
void connectWiFi() {
  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    // Blink LED while connecting
    digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" Connected!");
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(LED_STATUS_PIN, HIGH); // LED on when connected
  } else {
    Serial.println(" Failed!");
    digitalWrite(LED_STATUS_PIN, LOW);
  }
}

// ====== MQTT Reconnect ======
void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("[MQTT] Connecting...");
    if (mqtt.connect("MicRemote")) {
      Serial.println(" Connected!");
      mqtt.subscribe("audio/control");
      mqtt.subscribe("device/mic_remote/mode");
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
      uplink.sendAudioPacket(audioBuffer, bytesRead, aiModeActive);
    }
  }

  delay(10); // Prevent watchdog reset
}
