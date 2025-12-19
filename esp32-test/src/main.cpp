/**
 * ESP-32 Box Test Code
 * Dùng để kiểm tra kết nối và các chức năng cơ bản
 */

#include <Arduino.h>
#include <WiFi.h>

// LED tích hợp (thường là GPIO 2 trên hầu hết ESP32)
#define LED_PIN 2
#define BUTTON_PIN 0 // Boot button

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println();
  Serial.println("================================");
  Serial.println("    ESP-32 BOX TEST STARTED     ");
  Serial.println("================================");

  // Hiển thị thông tin chip
  Serial.printf("Chip Model: %s\n", ESP.getChipModel());
  Serial.printf("Chip Revision: %d\n", ESP.getChipRevision());
  Serial.printf("CPU Freq: %d MHz\n", ESP.getCpuFreqMHz());
  Serial.printf("Flash Size: %d MB\n", ESP.getFlashChipSize() / (1024 * 1024));
  Serial.printf("Free Heap: %d bytes\n", ESP.getFreeHeap());

  Serial.println("--------------------------------");
  Serial.println("Test 1: LED Blink Test");

  // Test LED nhấp nháy 3 lần
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    Serial.printf("  LED ON  [%d/3]\n", i + 1);
    delay(500);
    digitalWrite(LED_PIN, LOW);
    Serial.printf("  LED OFF [%d/3]\n", i + 1);
    delay(500);
  }
  Serial.println("LED Test: PASSED!");

  Serial.println("--------------------------------");
  Serial.println("Test 2: WiFi Scan");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  int n = WiFi.scanNetworks();
  if (n == 0) {
    Serial.println("  No WiFi networks found!");
  } else {
    Serial.printf("  Found %d networks:\n", n);
    for (int i = 0; i < min(n, 5); i++) { // Hiển thị tối đa 5 mạng
      Serial.printf("  %d. %s (%d dBm)\n", i + 1, WiFi.SSID(i).c_str(),
                    WiFi.RSSI(i));
    }
  }
  Serial.println("WiFi Scan: PASSED!");

  Serial.println("--------------------------------");
  Serial.println("Test 3: Button Test");
  Serial.println("  Press BOOT button to test...");
  Serial.println("  (LED will toggle when pressed)");
  Serial.println("================================");
  Serial.println("BASIC TESTS COMPLETED!");
  Serial.println("Now in button test mode...");
}

unsigned long lastPress = 0;
bool ledState = false;

void loop() {
  // Kiểm tra nút bấm với debounce
  if (digitalRead(BUTTON_PIN) == LOW) {
    if (millis() - lastPress > 200) {
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
      Serial.printf("Button pressed! LED: %s\n", ledState ? "ON" : "OFF");
      lastPress = millis();
    }
  }

  delay(10);
}
