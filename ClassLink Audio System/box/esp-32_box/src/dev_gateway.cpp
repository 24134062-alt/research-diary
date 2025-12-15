/*************************************************
 * File: dev_gateway.cpp
 * Path: C:\Users\DELL\project\box\esp32_box\src\dev_gateway.cpp
 *
 * Vai trò:
 * - Theo dõi thiết bị (glasses / mic) kết nối vào AP
 * - Phát hiện JOIN / LEAVE
 *
 * Ghi chú:
 * - MVP: chỉ log ra Serial
 * - Chưa gửi UART (sẽ làm sau)
 *************************************************/

#include <Arduino.h>
#include <WiFi.h>

// ====== State ======
static int last_station_count = 0;

// ====== Public API ======
void dev_gateway_init() {
    last_station_count = WiFi.softAPgetStationNum();
    Serial.print("[GATEWAY] Initial station count: ");
    Serial.println(last_station_count);
}

void dev_gateway_loop() {
    int current = WiFi.softAPgetStationNum();

    if (current != last_station_count) {
        if (current > last_station_count) {
            Serial.print("[GATEWAY] Device JOINED. Total: ");
            Serial.println(current);
        } else {
            Serial.print("[GATEWAY] Device LEFT. Total: ");
            Serial.println(current);
        }

        // Cập nhật state
        last_station_count = current;
    }
}

