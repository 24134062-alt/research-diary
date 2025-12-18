#include "vad.h"
#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <driver/i2s.h>


// Include config file - copy config.example.h to config.h and edit
#if __has_include("config.h")
#include "config.h"
#else
#warning "config.h not found, using default values"

// --- Configuration (use config.h for actual values) ---
#ifndef WIFI_SSID
#define WIFI_SSID "YOUR_WIFI_SSID"
#endif
#ifndef WIFI_PASSWORD
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#endif
#ifndef MQTT_HOST
#define MQTT_HOST "test.mosquitto.org"
#endif
#ifndef MQTT_PORT
#define MQTT_PORT 1883
#endif
#ifndef PC_IP
#define PC_IP "192.168.1.100"
#endif
#ifndef PC_UDP_PORT
#define PC_UDP_PORT 12345
#endif
#ifndef VAD_THRESHOLD
#define VAD_THRESHOLD 300
#endif
#endif

// Audio Config
#define I2S_WS 5
#define I2S_SD 4
#define I2S_SCK 6
#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE 16000
#define BUFFER_LEN 512

// Globals
WiFiClient espClient;
PubSubClient mqttClient(espClient);
WiFiUDP udp;

uint32_t packetSequence = 0;
bool isRecording = true;

// VAD instance for voice activity detection
VAD vad(VAD_THRESHOLD);

// --- Function Prototypes ---
void setupWiFi();
void setupMQTT();
void setupI2S();
void callback(char *topic, byte *payload, unsigned int length);
void sendAudioPacket();

void setup() {
  Serial.begin(115200);

  setupWiFi();
  setupMQTT();
  setupI2S();

  Serial.println("System Ready. Stream starting...");
}

void loop() {
  if (!mqttClient.connected()) {
    // Reconnect logic would go here (simplified for MVP)
    if (mqttClient.connect("ESP32Glasses_UniqueId")) {
      mqttClient.subscribe("audio/control");
      mqttClient.subscribe("glasses/text");
      Serial.println("MQTT Reconnected");
    }
  }
  mqttClient.loop();

  if (isRecording) {
    sendAudioPacket();
  }
}

// --- Implementations ---

void setupWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");
}

void setupMQTT() {
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(callback);
}

void setupI2S() {
  i2s_config_t i2s_config = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT, // Or ONLY_RIGHT
      .communication_format = I2S_COMM_FORMAT_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8,
      .dma_buf_len = 64,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0};

  i2s_pin_config_t pin_config = {.bck_io_num = I2S_SCK,
                                 .ws_io_num = I2S_WS,
                                 .data_out_num = I2S_PIN_NO_CHANGE,
                                 .data_in_num = I2S_SD};

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
}

void callback(char *topic, byte *payload, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++)
    msg += (char)payload[i];

  Serial.printf("MQTT [%s]: %s\n", topic, msg.c_str());

  if (String(topic) == "audio/control") {
    // Handle control commands
    if (msg.indexOf("stop") >= 0)
      isRecording = false;
    if (msg.indexOf("start") >= 0)
      isRecording = true;
  }

  // Handle text display (stub)
  if (String(topic) == "glasses/text") {
    // Draw to OLED here
  }
}

void sendAudioPacket() {
  size_t bytesRead = 0;
  uint8_t i2sData[BUFFER_LEN];

  // Read from I2S
  i2s_read(I2S_PORT, &i2sData, BUFFER_LEN, &bytesRead, portMAX_DELAY);

  if (bytesRead > 0) {
    // Apply VAD - only send if voice activity detected
    int16_t *samples = (int16_t *)i2sData;
    size_t numSamples = bytesRead / 2; // 16-bit samples

    if (!vad.process(samples, numSamples)) {
      // No voice activity - skip sending to save bandwidth
      return;
    }

    // Voice detected - send UDP packet
    // Header: 4 bytes sequence number
    uint8_t packet[4 + BUFFER_LEN];
    memcpy(packet, &packetSequence, 4);
    memcpy(packet + 4, i2sData, bytesRead);

    // Send
    udp.beginPacket(PC_IP, PC_UDP_PORT);
    udp.write(packet, 4 + bytesRead);
    udp.endPacket();

    packetSequence++;
  }
}
