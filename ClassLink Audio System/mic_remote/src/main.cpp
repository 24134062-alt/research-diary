#include "i2s_mic.h"
#include "oled_display.h"
#include "uplink_audio.h"
#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>


// Config (Should be in specific config file, but putting here for simplicity)
const char *ssid = "Wokwi-GUEST";
const char *password = "";
const char *mqtt_server = "test.mosquitto.org";
const char *box_ip = "192.168.1.100"; // Placeholder Box IP
const int audio_port = 12345;

// GPIO Pins
#define AI_BUTTON_PIN 12
#define MODE_BUTTON_PIN 13
#define BATTERY_PIN 34

WiFiClient espClient;
PubSubClient client(espClient);
I2SMic mic;
UplinkAudio uplink;
OLEDDisplay oled;

bool isRecording = false;
bool aiModeActive = false;
String currentMode = "class"; // "class" or "private"
uint8_t audioBuffer[1024];

// Button debouncing
unsigned long lastAIButtonPress = 0;
unsigned long lastModeButtonPress = 0;
const unsigned long debounceDelay = 300;

void callback(char *topic, byte *payload, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.printf("Message arrived [%s] %s\n", topic, msg.c_str());

  if (String(topic) == "audio/control") {
    if (msg.indexOf("start") >= 0) {
      isRecording = true;
      Serial.println("Recording Started");
    } else if (msg.indexOf("stop") >= 0) {
      isRecording = false;
      Serial.println("Recording Stopped");
    }
  }
}

void setup() {
  Serial.begin(115200);

  // GPIO Setup
  pinMode(AI_BUTTON_PIN, INPUT_PULLUP);
  pinMode(MODE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(BATTERY_PIN, INPUT);

  // OLED Setup
  oled.begin();
  oled.displayCentered("ClassLink", 20, 2);
  delay(2000);
  oled.showStatus(currentMode.c_str(), 100);

  // WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  // MQTT
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Audio
  mic.setup();
  uplink.begin(box_ip, audio_port);

  Serial.println("Setup complete!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("MicRemoteClient")) {
      Serial.println("connected");
      client.subscribe("audio/control");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // AI Button Handler
  if (digitalRead(AI_BUTTON_PIN) == LOW) {
    if (millis() - lastAIButtonPress > debounceDelay) {
      aiModeActive = !aiModeActive;

      if (aiModeActive) {
        oled.showAIListening();
        Serial.println("AI Mode: ON");
      } else {
        oled.showStatus(currentMode.c_str(), getBatteryLevel());
        Serial.println("AI Mode: OFF");
      }

      lastAIButtonPress = millis();
    }
  }

  // Mode Button Handler
  if (digitalRead(MODE_BUTTON_PIN) == LOW) {
    if (millis() - lastModeButtonPress > debounceDelay) {
      currentMode = (currentMode == "class") ? "private" : "class";
      oled.showStatus(currentMode.c_str(), getBatteryLevel());
      Serial.printf("Mode switched to: %s\n", currentMode.c_str());

      lastModeButtonPress = millis();
    }
  }

  // Audio Recording
  if (isRecording || aiModeActive) {
    size_t bytesRead = mic.read(audioBuffer, sizeof(audioBuffer));
    if (bytesRead > 0) {
      // Send with AI flag if in AI mode
      uplink.sendAudioPacket(audioBuffer, bytesRead, aiModeActive);
    }
  }
}

// Get battery level percentage
int getBatteryLevel() {
  int raw = analogRead(BATTERY_PIN);
  // Assuming 3.7V LiPo with voltage divider (adjust based on your circuit)
  // ADC range: 0-4095 for 0-3.3V
  // Battery: 3.0V (0%) to 4.2V (100%)
  int percentage = map(raw, 2480, 3472, 0, 100); // Approximate mapping
  return constrain(percentage, 0, 100);
}
