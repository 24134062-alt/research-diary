/*************************************************
 * ClassLink Audio System - Smart Glasses
 *
 * Phần cứng:
 * - ESP32
 * - INMP441 I2S Microphone
 * - OLED Display (SSD1306)
 * - Nút 1 (GPIO 32): Toggle Class ↔ Private
 * - Nút 2 (GPIO 33): Toggle AI Trợ Giảng
 *
 * Kết nối WiFi tới ESP32 Box (CLASS-BOX)
 *************************************************/

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <driver/i2s.h>

// ====== WiFi Config - Kết nối tới ESP32 Box ======
const char *WIFI_SSID = "CLASS-BOX";
const char *WIFI_PASS = "12345678";

// ====== MQTT Config - Raspberry Pi ======
const char *MQTT_SERVER = "192.168.4.1";
const int MQTT_PORT = 1883;

// ====== Audio Config ======
const char *BOX_IP = "192.168.4.1";
const int AUDIO_PORT = 12345;

// ====== I2S Microphone Pins ======
#define I2S_WS 25
#define I2S_SD 34 // Đổi từ 33 sang 34 để tránh xung đột với nút
#define I2S_SCK 26
#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE 16000
#define BUFFER_LEN 512

// ====== Button Pins (Nhấn-thả) ======
#define BTN_MODE_PIN 32 // Nút 1: Toggle Class ↔ Private
#define BTN_AI_PIN 33   // Nút 2: Toggle AI Trợ Giảng

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

// ====== State ======
bool classMode = true;          // true = Class, false = Private
bool aiAssistantActive = false; // AI trợ giảng bật/tắt
bool isRecording = true;        // Đang ghi âm
uint32_t packetSequence = 0;

// ====== Message Queue for Text Display ======
#define MESSAGE_QUEUE_SIZE 10
String messageQueue[MESSAGE_QUEUE_SIZE];
int queueHead = 0;             // Vị trí đọc
int queueTail = 0;             // Vị trí ghi
bool isDisplayingText = false; // Đang hiển thị text?

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
unsigned long lastBtnModePress = 0;
unsigned long lastBtnAIPress = 0;
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
void handleButtons();
void sendAudioPacket();
void updateDisplay();
void displayText(const char *text);
void processMessageQueue();

// ====== Setup ======
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=========================================");
  Serial.println("   ClassLink - Smart Glasses Controller  ");
  Serial.println("=========================================");

  // GPIO Setup
  pinMode(BTN_MODE_PIN, INPUT_PULLUP);
  pinMode(BTN_AI_PIN, INPUT_PULLUP);
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

  // Handle button presses
  handleButtons();

  // Process message queue (non-blocking)
  processMessageQueue();

  // Audio recording & sending
  if (isRecording) {
    sendAudioPacket();
  }

  delay(10);
}

// ====== WiFi Setup ======
void setupWiFi() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("Connecting WiFi...");
  display.display();

  Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    digitalWrite(LED_STATUS_PIN, !digitalRead(LED_STATUS_PIN));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
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

// ====== MQTT Setup ======
void setupMQTT() {
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
}

// ====== MQTT Reconnect ======
void reconnectMQTT() {
  int attempts = 0;
  while (!mqtt.connected() && attempts < 3) {
    Serial.print("[MQTT] Connecting...");
    if (mqtt.connect("SmartGlasses")) {
      Serial.println(" Connected!");
      mqtt.subscribe("glasses/text");  // Nhận text từ GV (khi AI off)
      mqtt.subscribe("ai/answer");     // Nhận câu trả lời từ AI (khi AI on)
      mqtt.subscribe("audio/control"); // Nhận lệnh điều khiển
    } else {
      Serial.printf(" Failed (rc=%d)\n", mqtt.state());
      attempts++;
      delay(2000);
    }
  }
}

// ====== MQTT Callback ======
void mqttCallback(char *topic, byte *payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.printf("[MQTT] %s: %s\n", topic, msg.c_str());

  // Nhận text từ GV - CHỈ khi AI mode TẮT
  // Khi AI mode BẬT, học sinh đang tập trung hỏi AI, không nhận text GV
  if (String(topic) == "glasses/text" && !aiAssistantActive) {
    queuePush(msg); // Thêm vào hàng đợi
  }

  // Nhận câu trả lời từ AI - LUÔN nhận (khi AI mode bật)
  if (String(topic) == "ai/answer" && aiAssistantActive) {
    queuePush(msg); // Hiển thị câu trả lời AI
  }

  // Nhận lệnh điều khiển
  if (String(topic) == "audio/control") {
    if (msg.indexOf("stop") >= 0) {
      isRecording = false;
    } else if (msg.indexOf("start") >= 0) {
      isRecording = true;
    }
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

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  Serial.println("[I2S] Microphone initialized");
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

// ====== Handle Button Presses ======
void handleButtons() {
  // Nút 1: Toggle Class ↔ Private
  if (digitalRead(BTN_MODE_PIN) == LOW) {
    if (millis() - lastBtnModePress > DEBOUNCE_DELAY) {
      classMode = !classMode;

      Serial.printf("[MODE] Switched to: %s\n",
                    classMode ? "CLASS" : "PRIVATE");

      // Publish mode change
      mqtt.publish("glasses/mode", classMode ? "class" : "private");

      // Update display
      updateDisplay();

      lastBtnModePress = millis();
    }
  }

  // Nút 2: Toggle AI Trợ Giảng
  if (digitalRead(BTN_AI_PIN) == LOW) {
    if (millis() - lastBtnAIPress > DEBOUNCE_DELAY) {
      aiAssistantActive = !aiAssistantActive;

      Serial.printf("[AI] Assistant: %s\n", aiAssistantActive ? "ON" : "OFF");

      // Publish AI state
      mqtt.publish("glasses/ai", aiAssistantActive ? "on" : "off");

      // Update display
      updateDisplay();

      lastBtnAIPress = millis();
    }
  }
}

// ====== Update OLED Display ======
void updateDisplay() {
  display.clearDisplay();

  // Header
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Mode: ");
  display.println(classMode ? "CLASS" : "PRIVATE");

  // AI Status
  display.setCursor(0, 12);
  display.print("AI: ");
  if (aiAssistantActive) {
    display.println("ACTIVE");
  } else {
    display.println("OFF");
  }

  // Divider
  display.drawLine(0, 24, 128, 24, SSD1306_WHITE);

  // Status icons
  display.setCursor(0, 28);
  display.print("WiFi: ");
  display.println(WiFi.status() == WL_CONNECTED ? "OK" : "X");

  display.setCursor(0, 40);
  display.print("MQTT: ");
  display.println(mqtt.connected() ? "OK" : "X");

  // Recording indicator
  if (isRecording) {
    display.fillCircle(120, 56, 5, SSD1306_WHITE);
  }

  display.display();
}

// ====== Display Text from AI (Large + Scrolling) ======
// TextSize 2: 12x16 px, ~10 ký tự/dòng, 4 dòng
// Auto-scroll cho text dài

#define TEXT_SIZE 2
#define CHARS_PER_LINE 10
#define LINES_PER_SCREEN 4
#define SCROLL_DELAY_MS 2000 // Thời gian hiển thị mỗi trang

void displayText(const char *text) {
  String textStr = String(text);
  int textLen = textStr.length();

  // Tính số ký tự tối đa mỗi màn hình
  int charsPerScreen = CHARS_PER_LINE * LINES_PER_SCREEN; // ~40 ký tự

  // Nếu text ngắn, hiển thị thẳng
  if (textLen <= charsPerScreen) {
    display.clearDisplay();
    display.setTextSize(TEXT_SIZE);
    display.setTextWrap(true);
    display.setCursor(0, 0);
    display.println(text);
    display.display();
    delay(5000); // Hiển thị 5 giây
    updateDisplay();
    return;
  }

  // Text dài - cuộn từng trang
  int totalPages = (textLen + charsPerScreen - 1) / charsPerScreen;

  for (int page = 0; page < totalPages; page++) {
    display.clearDisplay();
    display.setTextSize(TEXT_SIZE);
    display.setTextWrap(true);
    display.setCursor(0, 0);

    // Cắt đoạn text cho trang hiện tại
    int startIdx = page * charsPerScreen;
    int endIdx = min(startIdx + charsPerScreen, textLen);
    String pageText = textStr.substring(startIdx, endIdx);

    display.println(pageText);

    // Hiển thị indicator trang (góc dưới phải)
    display.setTextSize(1);
    display.setCursor(100, 56);
    display.print(page + 1);
    display.print("/");
    display.print(totalPages);

    display.display();
    delay(SCROLL_DELAY_MS);
  }

  // Quay về màn hình status
  updateDisplay();
}

// ====== Send Audio Packet ======
void sendAudioPacket() {
  size_t bytesRead = 0;

  // Read from I2S microphone
  i2s_read(I2S_PORT, audioBuffer, BUFFER_LEN, &bytesRead, portMAX_DELAY);

  if (bytesRead > 0) {
    // Create packet with header
    // Header: 4 bytes sequence + 1 byte flags
    // Flags: bit 0 = AI mode, bit 1 = class mode
    uint8_t packet[5 + BUFFER_LEN];
    memcpy(packet, &packetSequence, 4);
    packet[4] = (aiAssistantActive ? 0x01 : 0x00) | (classMode ? 0x02 : 0x00);
    memcpy(packet + 5, audioBuffer, bytesRead);

    // Send UDP
    udp.beginPacket(BOX_IP, AUDIO_PORT);
    udp.write(packet, 5 + bytesRead);
    udp.endPacket();

    packetSequence++;
  }
}

// ====== Process Message Queue ======
// Non-blocking: Kiểm tra và hiển thị message tiếp theo từ queue
void processMessageQueue() {
  // Nếu đang hiển thị hoặc queue rỗng thì bỏ qua
  if (isDisplayingText || queueIsEmpty()) {
    return;
  }

  // Lấy message tiếp theo từ queue
  String msg = queuePop();
  if (msg.length() > 0) {
    isDisplayingText = true;
    Serial.printf("[QUEUE] Processing message: %s\n", msg.c_str());
    displayText(msg.c_str());
    isDisplayingText = false;
  }
}
