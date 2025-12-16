#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// --- Configuration ---
const char* SSID = "YOUR_WIFI_SSID";
const char* PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_SERVER = "test.mosquitto.org"; 
const int MQTT_PORT = 1883;

// Pin Definitions
#define BUTTON_PIN 0 // Boot button on most ESP32 boards

// Globals
WiFiClient espClient;
PubSubClient mqttClient(espClient);
bool isRecording = false;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 200;

void setupWiFi();
void setupMQTT();

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  setupWiFi();
  setupMQTT();
  
  Serial.println("Box Controller Ready. Press Boot Button to Toggle Record.");
}

void loop() {
  if (!mqttClient.connected()) {
    if (mqttClient.connect("ESP32Box_Controller")) {
        Serial.println("MQTT Connected");
    }
  }
  mqttClient.loop();

  // Button Logic
  if (digitalRead(BUTTON_PIN) == LOW) {
    if ((millis() - lastDebounceTime) > debounceDelay) {
      isRecording = !isRecording;
      const char* msg = isRecording ? "start" : "stop";
      
      Serial.printf("Toggling Record: %s\n", msg);
      mqttClient.publish("audio/control", msg);
      
      lastDebounceTime = millis();
    }
  }
}

void setupWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
}

void setupMQTT() {
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
}
