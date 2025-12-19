/*************************************************
 * File: audio_forward.cpp
 * Path: C:\Users\DELL\project\box\esp32_box\src\audio_forward.cpp
 *
 * Vai trò:
 * - Gửi dữ liệu audio giả (fake PCM) sang PC bằng UDP
 * - Test đường truyền ESP32 -> PC
 *
 * Ghi chú:
 * - KHÔNG dùng mic thật
 * - KHÔNG dùng I2S
 * - Mỗi packet gửi định kỳ 20ms
 *************************************************/

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ====== Cấu hình UDP ======
static const char *PC_IP = "192.168.4.2"; // IP PC (sửa theo thực tế)
static const uint16_t PC_PORT = 50005;

// ====== Audio fake config ======
#define FRAME_SIZE 160 // số byte giả (nhẹ để test)
#define SEND_INTERVAL_MS 20

// ====== UDP ======
static WiFiUDP udp;

// ====== State ======
static unsigned long last_send_ms = 0;
static uint16_t seq = 0;

// ====== Forward declarations ======
void send_fake_audio();

// ====== Public API ======
void audio_forward_init() {
  Serial.println("[AUDIO] Init audio forward (FAKE)");

  udp.begin(PC_PORT); // mở UDP local port (không bắt buộc nhưng tốt)
  last_send_ms = millis();
}

void audio_forward_loop() {
  unsigned long now = millis();

  if (now - last_send_ms >= SEND_INTERVAL_MS) {
    last_send_ms = now;
    send_fake_audio();
  }
}

// ====== Internal ======
void send_fake_audio() {
  uint8_t buffer[FRAME_SIZE];

  // Tạo dữ liệu giả: pattern tăng dần
  for (int i = 0; i < FRAME_SIZE; i++) {
    buffer[i] = (uint8_t)(seq & 0xFF);
  }

  udp.beginPacket(PC_IP, PC_PORT);
  udp.write(buffer, FRAME_SIZE);
  udp.endPacket();

  Serial.print("[AUDIO] Sent fake frame seq=");
  Serial.println(seq);

  seq++;
}
