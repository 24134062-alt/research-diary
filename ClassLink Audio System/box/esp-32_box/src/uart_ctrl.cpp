/*************************************************
 * File: uart_ctrl.cpp
 * Path: C:\Users\DELL\project\box\esp32_box\src\uart_ctrl.cpp
 *
 * Vai trò:
 * - Giao tiếp UART giữa ESP32 BOX và Raspberry
 * - Gửi event JOIN / LEAVE
 * - Nhận lệnh MODE_SET
 *
 * Ghi chú:
 * - JSON line-based (mỗi dòng 1 message)
 * - MVP: parse tay, không dùng thư viện JSON
 *************************************************/

#include <Arduino.h>

// ====== UART config ======
#define UART_BAUDRATE 115200

// ====== Buffer ======
static String rx_buffer;

// ====== Forward declarations ======
void handle_uart_line(const String &line);

// ====== Public API ======
void uart_ctrl_init() {
  Serial.println("[UART] Init UART control");
  rx_buffer.reserve(256);
}

void uart_ctrl_loop() {
  // Đọc UART không block
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      handle_uart_line(rx_buffer);
      rx_buffer = "";
    } else {
      rx_buffer += c;
    }
  }
}

// ====== Internal logic ======
void handle_uart_line(const String &line) {
  if (line.length() == 0)
    return;

  Serial.print("[UART][RX] ");
  Serial.println(line);

  // MVP: parse MODE_SET thủ công
  if (line.indexOf("\"type\":\"MODE_SET\"") >= 0) {
    if (line.indexOf("\"mode\":\"CLASS\"") >= 0) {
      Serial.println("[UART] MODE -> CLASS");
      // TODO: notify gateway / glasses
    } else if (line.indexOf("\"mode\":\"PRIVATE\"") >= 0) {
      Serial.println("[UART] MODE -> PRIVATE");
      // TODO: notify gateway / glasses
    }
  }
}

// ====== Event send API (ESP32 -> Raspberry) ======
void uart_send_dev_join(int total) {
  String msg = "{";
  msg += "\"type\":\"DEV_JOIN\",";
  msg += "\"total\":" + String(total);
  msg += "}\n";

  Serial.print(msg);
}

void uart_send_dev_leave(int total) {
  String msg = "{";
  msg += "\"type\":\"DEV_LEAVE\",";
  msg += "\"total\":" + String(total);
  msg += "}\n";

  Serial.print(msg);
}
