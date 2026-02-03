/*************************************************
 * ClassLink Audio System - Smart Glasses
 *
 * MODIFIED: Single Button Control (GPIO 32)
 * Mode Cycle: Class → Private → AI Assistant → Class ...
 *
 * Phần cứng:
 * - ESP32
 * - INMP441 I2S Microphone
 * - OLED Display (SSD1306)
 * - Nút (GPIO 32): Cycle qua 3 chế độ
 *
 * Kết nối WiFi tới ESP32 Box (CLASS-BOX)
 *************************************************/

#include "../include/wifi_config.h"
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <driver/i2s.h>


// ====== WiFi Multi-Network Support ======
WiFiNetwork wifi_list[MAX_WIFI_NETWORKS];
Preferences wifi_prefs;

// ====== MQTT Config - Raspberry Pi ======
// Default IP, can be overridden via Preferences
const char *MQTT_SERVER = "192.168.4.1";
const int MQTT_PORT = 1883;
const int MQTT_MAX_RETRIES = 5;  // Increased from 3
const int MQTT_RETRY_DELAY_BASE = 1000;  // Base delay for exponential backoff

// ====== Audio Config ======
const char *BOX_IP = "192.168.4.1";
const int AUDIO_PORT = 12345;

// ====== I2S Microphone Pins ======
#define I2S_WS 25
#define I2S_SD 34
#define I2S_SCK 26
#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE 16000
#define BUFFER_LEN 512
#define MAX_WORDS 100  // Maximum words for display parsing

// ====== Single Button Pin ======
#define BTN_PIN 32 // Nút duy nhất: Cycle qua Class → Private → AI

// ====== OLED Config ======
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_I2C_ADDR 0x3C

// ====== LED Status ======
#define LED_STATUS_PIN 2 // Built-in LED

// ====== Objects ======
WiFiClient espClient;
PubSubClient mqtt(espClient);
WiFiUDP udp;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ====== Mode State Machine ======
enum OperatingMode {
  MODE_CLASS = 0,       // Chế độ lớp học - Nhận text từ GV
  MODE_PRIVATE = 1,     // Chế độ riêng tư - Im lặng
  MODE_AI_ASSISTANT = 2 // Chế độ AI - Hỏi đáp AI
};

OperatingMode currentMode = MODE_CLASS; // Mặc định: Class mode
bool isRecording = true;                // Đang ghi âm
uint32_t packetSequence = 0;

// ====== Message Queue for Text Display ======
#define MESSAGE_QUEUE_SIZE 20
String messageQueue[MESSAGE_QUEUE_SIZE];
int queueHead = 0;
int queueTail = 0;
bool isDisplayingText = false;

// Queue functions
bool queueIsEmpty() { return queueHead == queueTail; }
bool queueIsFull() {
  return ((queueTail + 1) % MESSAGE_QUEUE_SIZE) == queueHead;
}

void queuePush(String msg) {
  if (!queueIsFull()) {
    messageQueue[queueTail] = msg;
    queueTail = (queueTail + 1) % MESSAGE_QUEUE_SIZE;
    Serial.printf("[QUEUE] Added message. Queue size: %d\n",
                  (queueTail - queueHead + MESSAGE_QUEUE_SIZE) %
                      MESSAGE_QUEUE_SIZE);
  } else {
    Serial.println("[QUEUE] Queue full! Message dropped.");
  }
}

String queuePop() {
  if (!queueIsEmpty()) {
    String msg = messageQueue[queueHead];
    queueHead = (queueHead + 1) % MESSAGE_QUEUE_SIZE;
    return msg;
  }
  return "";
}

// ====== Button Debouncing ======
unsigned long lastBtnPress = 0;
const unsigned long DEBOUNCE_DELAY = 300;

// ====== Audio Buffer ======
uint8_t audioBuffer[BUFFER_LEN];

// ====== Function Prototypes ======
void setupWiFi();
void setupMQTT();
void setupI2S();
void setupOLED();
void mqttCallback(char *topic, byte *payload, unsigned int length);
void reconnectMQTT();
void handleButton();
void sendAudioPacket();
void updateDisplay();
void displayText(const char *text);
void processMessageQueue();
const char *getModeString(OperatingMode mode);

// WiFi management functions
void wifi_load_list();
void wifi_save_list();
bool wifi_connect();
void wifi_add_network(const char *ssid, const char *password, uint8_t priority);
void wifi_ota_update(const char *new_ssid, const char *new_password);

// ====== Setup ======
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=========================================");
  Serial.println("   ClassLink - Smart Glasses (1 Button)  ");
  Serial.println("=========================================");

  // GPIO Setup
  pinMode(BTN_PIN, INPUT_PULLUP);
  pinMode(LED_STATUS_PIN, OUTPUT);

  // OLED Setup
  setupOLED();
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(20, 20);
  display.println("ClassLink");
  display.display();
  delay(1500);

  // WiFi Setup
  setupWiFi();

  // MQTT Setup
  setupMQTT();

  // I2S Microphone Setup
  setupI2S();

  // Show initial status
  updateDisplay();

  Serial.println("-----------------------------------------");
  Serial.println("[READY] Glasses is running!");
  Serial.printf("[MODE] Current: %s\n", getModeString(currentMode));
  Serial.println("-----------------------------------------");
}

// ====== Loop ======
void loop() {
  // WiFi reconnect
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }

  // MQTT reconnect
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();

  // Handle button press
  handleButton();

  // Process message queue (non-blocking)
  processMessageQueue();

  // Audio recording & sending
  if (isRecording && currentMode != MODE_PRIVATE) {
    sendAudioPacket();
  }

  delay(10);
}

// ====== Get Mode String ======
const char *getModeString(OperatingMode mode) {
  switch (mode) {
  case MODE_CLASS:
    return "CLASS";
  case MODE_PRIVATE:
    return "PRIVATE";
  case MODE_AI_ASSISTANT:
    return "AI ASSISTANT";
  default:
    return "UNKNOWN";
  }
}

// ====== WiFi Setup with Multi-Network Support ======
void setupWiFi() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  Serial.println("[WiFi] Initializing multi-network support...");

  // Load WiFi list from Preferences
  wifi_load_list();

  // Try to connect using priority list
  if (wifi_connect()) {
    Serial.println(" Connected!");
    Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(LED_STATUS_PIN, HIGH);

    display.setCursor(0, 20);
    display.println("WiFi OK!");
    display.display();
  } else {
    Serial.println(" Failed!");
    digitalWrite(LED_STATUS_PIN, LOW);

    display.setCursor(0, 20);
    display.println("WiFi FAILED!");
    display.display();
  }
  delay(1000);
}

// ====== WiFi Load List ======
void wifi_load_list() {
  wifi_prefs.begin(WIFI_PREFS_NAMESPACE, false);

  // Priority 0: Always set CLASS-BOX as default
  strcpy(wifi_list[0].ssid, DEFAULT_WIFI_SSID);
  strcpy(wifi_list[0].password, DEFAULT_WIFI_PASS);
  wifi_list[0].priority = 0;

  // Load other networks from Preferences
  for (int i = 1; i < MAX_WIFI_NETWORKS; i++) {
    String key_ssid = "ssid_" + String(i);
    String key_pass = "pass_" + String(i);

    String ssid = wifi_prefs.getString(key_ssid.c_str(), "");
    String pass = wifi_prefs.getString(key_pass.c_str(), "");

    if (ssid.length() > 0) {
      strcpy(wifi_list[i].ssid, ssid.c_str());
      strcpy(wifi_list[i].password, pass.c_str());
      wifi_list[i].priority = i;
      Serial.printf("[WiFi] Loaded network %d: %s\n", i, ssid.c_str());
    } else {
      wifi_list[i].ssid[0] = '\0';
      wifi_list[i].priority = 255;
    }
  }

  wifi_prefs.end();
}

// ====== WiFi Save List ======
void wifi_save_list() {
  wifi_prefs.begin(WIFI_PREFS_NAMESPACE, false);

  // Skip index 0 (CLASS-BOX default)
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
  Serial.println("[WiFi] List saved to Preferences");
}

// ====== WiFi Connect with Priority ======
bool wifi_connect() {
  // Try each network by priority
  for (int i = 0; i < MAX_WIFI_NETWORKS; i++) {
    if (wifi_list[i].ssid[0] == '\0')
      continue;

    Serial.printf("[WiFi] Trying priority %d: %s", i, wifi_list[i].ssid);

    // Scan for available networks
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

    // Try to connect
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

// ====== WiFi Add Network ======
void wifi_add_network(const char *ssid, const char *password,
                      uint8_t priority) {
  if (priority == 0 || priority >= MAX_WIFI_NETWORKS) {
    Serial.println("[WiFi] Invalid priority (0 is reserved, max is 4)");
    return;
  }

  // Check if already exists
  for (int i = 0; i < MAX_WIFI_NETWORKS; i++) {
    if (strcmp(wifi_list[i].ssid, ssid) == 0) {
      // Update password
      strcpy(wifi_list[i].password, password);
      wifi_list[i].priority = priority;
      wifi_save_list();
      Serial.printf("[WiFi] Updated network: %s\n", ssid);
      return;
    }
  }

  // Add new
  strcpy(wifi_list[priority].ssid, ssid);
  strcpy(wifi_list[priority].password, password);
  wifi_list[priority].priority = priority;
  wifi_save_list();
  Serial.printf("[WiFi] Added network: %s (priority %d)\n", ssid, priority);
}

// ====== WiFi OTA Update ======
void wifi_ota_update(const char *new_ssid, const char *new_password) {
  Serial.println("[WiFi] ========================================");
  Serial.println("[WiFi] OTA Config Update Received");
  Serial.printf("[WiFi]   New SSID: %s\n", new_ssid);
  Serial.println("[WiFi] ========================================");

  // Add to list (priority 1, right after CLASS-BOX)
  wifi_add_network(new_ssid, new_password, 1);

  // Wait for ESP32 Box to restart
  Serial.println("[WiFi] ⏰ Waiting 3 seconds for ESP32 Box to restart...");
  for (int i = 3; i > 0; i--) {
    Serial.printf("[WiFi]    Reconnecting in %d seconds...\n", i);
    delay(1000);
  }

  // Disconnect and reconnect
  Serial.println("[WiFi] Reconnecting...");
  WiFi.disconnect();
  delay(500);

  if (wifi_connect()) {
    Serial.println("[WiFi] ✅ Reconnected successfully!");
    updateDisplay();
  } else {
    Serial.println("[WiFi] ❌ Reconnect failed");
  }
}

// ====== MQTT Setup ======
void setupMQTT() {
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
}

// ====== MQTT Reconnect with Exponential Backoff ======
void reconnectMQTT() {
  int attempts = 0;
  int retryDelay = MQTT_RETRY_DELAY_BASE;
  
  while (!mqtt.connected() && attempts < MQTT_MAX_RETRIES) {
    Serial.printf("[MQTT] Connecting (attempt %d/%d)...", attempts + 1, MQTT_MAX_RETRIES);
    if (mqtt.connect("SmartGlasses")) {
      Serial.println(" Connected!");
      mqtt.subscribe("glasses/text");          // Nhận text từ GV
      mqtt.subscribe("ai/answer");             // Nhận câu trả lời từ AI
      mqtt.subscribe("audio/control");         // Nhận lệnh điều khiển
      mqtt.subscribe("classlink/config/wifi"); // WiFi OTA updates
      mqtt.subscribe("classlink/config/mqtt"); // MQTT server config updates
      Serial.println("[MQTT] ✅ Subscribed to all topics");
      return;
    } else {
      Serial.printf(" Failed (rc=%d), retry in %dms\n", mqtt.state(), retryDelay);
      attempts++;
      delay(retryDelay);
      retryDelay = min(retryDelay * 2, 10000);  // Exponential backoff, max 10s
    }
  }
  Serial.println("[MQTT] ❌ Max retries reached, will retry later");
}

// ====== MQTT Callback ======
void mqttCallback(char *topic, byte *payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.printf("[MQTT] %s: %s\n", topic, msg.c_str());

  // MODE_CLASS: Nhận text từ giáo viên
  if (String(topic) == "glasses/text" && currentMode == MODE_CLASS) {
    queuePush(msg);
  }

  // MODE_AI_ASSISTANT: Nhận câu trả lời từ AI
  if (String(topic) == "ai/answer" && currentMode == MODE_AI_ASSISTANT) {
    queuePush(msg);
  }

  // Nhận lệnh điều khiển
  if (String(topic) == "audio/control") {
    if (msg.indexOf("stop") >= 0) {
      isRecording = false;
    } else if (msg.indexOf("start") >= 0) {
      isRecording = true;
    }
  }

  // ====== NEW: WiFi OTA Update ======
  if (String(topic) == "classlink/config/wifi") {
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

// ====== I2S Microphone Setup ======
void setupI2S() {
  i2s_config_t i2s_config = {.mode =
                                 (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
                             .sample_rate = SAMPLE_RATE,
                             .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
                             .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
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

  esp_err_t result = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  if (result != ESP_OK) {
    Serial.printf("[I2S] ERROR: Driver install failed with code %d\n", result);
    return;
  }
  
  result = i2s_set_pin(I2S_PORT, &pin_config);
  if (result != ESP_OK) {
    Serial.printf("[I2S] ERROR: Pin config failed with code %d\n", result);
    return;
  }
  
  Serial.println("[I2S] Microphone initialized successfully");
}

// ====== OLED Setup ======
void setupOLED() {
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("[OLED] SSD1306 failed!");
    return;
  }
  display.clearDisplay();
  display.display();
  Serial.println("[OLED] Display initialized");
}

// ====== Handle Single Button Press ======
void handleButton() {
  if (digitalRead(BTN_PIN) == LOW) {
    if (millis() - lastBtnPress > DEBOUNCE_DELAY) {
      // Cycle to next mode
      currentMode = (OperatingMode)((currentMode + 1) % 3);

      Serial.printf("[BUTTON] Mode changed to: %s\n",
                    getModeString(currentMode));

      // Publish mode to MQTT
      const char *modeStr = "";
      switch (currentMode) {
      case MODE_CLASS:
        modeStr = "class";
        break;
      case MODE_PRIVATE:
        modeStr = "private";
        break;
      case MODE_AI_ASSISTANT:
        modeStr = "ai";
        break;
      }
      mqtt.publish("glasses/mode", modeStr);

      // Update display
      updateDisplay();

      lastBtnPress = millis();
    }
  }
}

// ====== Update OLED Display ======
void updateDisplay() {
  display.clearDisplay();

  // Header - Mode name (Large text)
  display.setTextSize(2);
  display.setCursor(0, 0);

  switch (currentMode) {
  case MODE_CLASS:
    display.println("CLASS");
    break;
  case MODE_PRIVATE:
    display.println("PRIVATE");
    break;
  case MODE_AI_ASSISTANT:
    display.println("AI MODE");
    break;
  }

  // Divider
  display.drawLine(0, 20, 128, 20, SSD1306_WHITE);

  // Status icons (Small text)
  display.setTextSize(1);
  display.setCursor(0, 26);
  display.print("WiFi: ");
  display.println(WiFi.status() == WL_CONNECTED ? "OK" : "X");

  display.setCursor(0, 38);
  display.print("MQTT: ");
  display.println(mqtt.connected() ? "OK" : "X");

  // Recording indicator
  if (isRecording && currentMode != MODE_PRIVATE) {
    display.fillCircle(120, 56, 5, SSD1306_WHITE);
  }

  display.display();
}

// ====== Display Text with Typewriter Scroll Effect ======
#define TEXT_SIZE 2
#define CHAR_WIDTH_PX (6 * TEXT_SIZE)
#define CHARS_PER_LINE (SCREEN_WIDTH / CHAR_WIDTH_PX)
#define LINE_HEIGHT_PX (8 * TEXT_SIZE)
#define LINES_PER_SCREEN (SCREEN_HEIGHT / LINE_HEIGHT_PX)
#define CHAR_DELAY_MS 50
#define END_DISPLAY_DELAY_MS 3000

String displayLines[LINES_PER_SCREEN];
int currentLineIdx = 0;
String currentLineBuffer = "";

void clearDisplayBuffer() {
  for (int i = 0; i < LINES_PER_SCREEN; i++) {
    displayLines[i] = "";
  }
  currentLineIdx = 0;
  currentLineBuffer = "";
}

void scrollUpDisplay() {
  for (int i = 0; i < LINES_PER_SCREEN - 1; i++) {
    displayLines[i] = displayLines[i + 1];
  }
  displayLines[LINES_PER_SCREEN - 1] = "";
}

void refreshDisplayText() {
  display.clearDisplay();
  display.setTextSize(TEXT_SIZE);
  display.setCursor(0, 0);

  for (int i = 0; i < LINES_PER_SCREEN; i++) {
    display.println(displayLines[i]);
  }

  display.display();
}

void displayText(const char *text) {
  String textStr = String(text);

  Serial.printf("[DISPLAY] Text: %s\n", text);

  clearDisplayBuffer();
  refreshDisplayText();

  // Tách thành các từ (with bounds check)
  int wordCount = 0;
  String words[MAX_WORDS];

  int startIdx = 0;
  for (int i = 0; i <= textStr.length() && wordCount < MAX_WORDS; i++) {
    if (i == textStr.length() || textStr[i] == ' ') {
      if (i > startIdx) {
        words[wordCount++] = textStr.substring(startIdx, i);
      }
      startIdx = i + 1;
    }
  }
  
  if (wordCount >= MAX_WORDS) {
    Serial.println("[DISPLAY] WARNING: Text truncated, too many words");
  }

  // Hiển thị từng từ với typewriter effect
  for (int w = 0; w < wordCount; w++) {
    String word = words[w];

    String testLine =
        currentLineBuffer.length() == 0 ? word : currentLineBuffer + " " + word;

    if (testLine.length() > CHARS_PER_LINE) {
      displayLines[currentLineIdx] = currentLineBuffer;
      currentLineIdx++;

      if (currentLineIdx >= LINES_PER_SCREEN) {
        scrollUpDisplay();
        currentLineIdx = LINES_PER_SCREEN - 1;
      }

      currentLineBuffer = "";
    }

    if (currentLineBuffer.length() > 0) {
      currentLineBuffer += " ";
      displayLines[currentLineIdx] = currentLineBuffer;
      refreshDisplayText();
      delay(CHAR_DELAY_MS);
    }

    for (int c = 0; c < word.length(); c++) {
      currentLineBuffer += word[c];
      displayLines[currentLineIdx] = currentLineBuffer;
      refreshDisplayText();
      delay(CHAR_DELAY_MS);
    }
  }

  delay(END_DISPLAY_DELAY_MS);

  // Quay về màn hình status
  updateDisplay();
}

// ====== Send Audio Packet ======
void sendAudioPacket() {
  size_t bytesRead = 0;

  i2s_read(I2S_PORT, audioBuffer, BUFFER_LEN, &bytesRead, portMAX_DELAY);

  if (bytesRead > 0) {
    // Header: 4 bytes sequence + 1 byte flags
    // Flags: bit 0 = AI mode, bit 1-2 = mode type
    uint8_t packet[5 + BUFFER_LEN];
    memcpy(packet, &packetSequence, 4);

    // Encode mode in flags
    uint8_t flags = 0;
    if (currentMode == MODE_AI_ASSISTANT) {
      flags |= 0x01; // AI mode bit
    }
    flags |= (currentMode << 1); // Encode mode in bits 1-2

    packet[4] = flags;
    memcpy(packet + 5, audioBuffer, bytesRead);

    // Send UDP
    udp.beginPacket(BOX_IP, AUDIO_PORT);
    udp.write(packet, 5 + bytesRead);
    udp.endPacket();

    packetSequence++;
  }
}

// ====== Process Message Queue ======
void processMessageQueue() {
  if (isDisplayingText || queueIsEmpty()) {
    return;
  }

  String msg = queuePop();
  if (msg.length() > 0) {
    isDisplayingText = true;
    Serial.printf("[QUEUE] Processing message: %s\n", msg.c_str());
    displayText(msg.c_str());
    isDisplayingText = false;
  }
}
