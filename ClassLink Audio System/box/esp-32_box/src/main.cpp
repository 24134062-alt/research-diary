/*************************************************
 * File: main.cpp
 * Path: C:\Users\DELL\project\box\esp32_box\src\main.cpp
 *
 * Vai trò:
 * - Entry point của ESP32 BOX
 * - Khởi tạo hệ thống
 * - Gọi các module con (wifi, uart, gateway, audio)
 *
 * Ghi chú:
 * - Chưa làm logic chi tiết
 * - Chỉ để đảm bảo ESP32 boot OK
 *************************************************/

#include <Arduino.h>

// ====== Forward declarations (sẽ code sau) ======
void wifi_init();          // wifi_ap_sta.cpp
void uart_ctrl_init();     // uart_ctrl.cpp
void dev_gateway_init();   // dev_gateway.cpp
void audio_forward_init(); // audio_forward.cpp

void uart_ctrl_loop();
void dev_gateway_loop();
void audio_forward_loop();

// =================================================

void setup() {
    // 1. Serial debug
    Serial.begin(115200);
    delay(1000);

    Serial.println();
    Serial.println("=================================");
    Serial.println(" ESP32 BOX BOOTING...");
    Serial.println("=================================");

    // 2. Init modules
    Serial.println("[INIT] WiFi");
    wifi_init();

    Serial.println("[INIT] UART control");
    uart_ctrl_init();

    Serial.println("[INIT] Device gateway");
    dev_gateway_init();

    Serial.println("[INIT] Audio forward");
    audio_forward_init();

    Serial.println("[OK] ESP32 BOX READY");
}

void loop() {
    // Loop từng module (non-blocking)
    uart_ctrl_loop();
    dev_gateway_loop();
    audio_forward_loop();

    // Nhẹ CPU
    delay(1);
}

