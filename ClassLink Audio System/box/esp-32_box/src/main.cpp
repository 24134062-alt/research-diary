/*************************************************
 * ClassLink Audio System - ESP32 Box Controller
 *
 * Kiến trúc:
 * - ESP32 phát WiFi AP "CLASS-BOX" -> Kính/Mic kết nối vào
 * - ESP32 <-> Raspberry Pi qua UART (dây serial)
 *************************************************/

#include <Arduino.h>

// ====== Function declarations from other files ======
extern void wifi_init();
extern void uart_ctrl_init();
extern void uart_ctrl_loop();
extern void audio_forward_init();
extern void audio_forward_loop();
extern void dev_gateway_init();
extern void dev_gateway_loop();

// ====== Pin Definitions ======
#define LED_PIN 2 // Status LED

// ====== State ======
bool ledState = false;
unsigned long lastBlink = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(LED_PIN, OUTPUT);

  Serial.println();
  Serial.println("=========================================");
  Serial.println("   ClassLink Audio System - ESP32 Box    ");
  Serial.println("=========================================");

  // Khởi tạo WiFi AP mode - Phát WiFi riêng
  wifi_init();

  // Khởi tạo các module
  uart_ctrl_init();     // Giao tiếp với Raspberry Pi
  audio_forward_init(); // Forward audio
  dev_gateway_init();   // Quản lý thiết bị kết nối

  Serial.println("-----------------------------------------");
  Serial.println("[READY] Box Controller is running!");
  Serial.println();
  Serial.println("  WiFi AP Mode:");
  Serial.println("    SSID: CLASS-BOX");
  Serial.println("    Pass: 12345678");
  Serial.println();
  Serial.println("  Ket noi voi Raspberry Pi qua UART");
  Serial.println("-----------------------------------------");
}

void loop() {
  // Chạy các module loops
  uart_ctrl_loop();     // Xử lý UART với Raspberry
  audio_forward_loop(); // Forward audio
  dev_gateway_loop();   // Quản lý thiết bị

  // LED nhấp nháy để báo hiệu đang hoạt động
  if (millis() - lastBlink > 1000) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    lastBlink = millis();
  }

  delay(10); // Prevent watchdog reset
}
