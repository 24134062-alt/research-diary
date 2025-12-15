/*************************************************
 * File: wifi_ap_sta.cpp
 * Path: C:\Users\DELL\project\box\esp32_box\src\wifi_ap_sta.cpp
 *
 * Vai trò:
 * - Khởi tạo Wi-Fi AP cho ESP32 BOX
 * - Cho glasses / mic kết nối vào
 *
 * Ghi chú:
 * - MVP: CHỈ AP mode
 * - STA (wifi ngoài) sẽ làm sau
 *************************************************/

#include <Arduino.h>
#include <WiFi.h>

// ====== Cấu hình AP ======
static const char* AP_SSID     = "CLASS-BOX";
static const char* AP_PASSWORD = "12345678";   // >= 8 ký tự
static const uint8_t AP_CHANNEL = 6;
static const uint8_t AP_MAX_CONN = 6;

// ====== State ======
static bool wifi_started = false;

// ====== Public API (được gọi từ main.cpp) ======
void wifi_init() {
    if (wifi_started) return;

    Serial.println("[WIFI] Starting AP mode...");

    WiFi.mode(WIFI_AP);

    bool ok = WiFi.softAP(
        AP_SSID,
        AP_PASSWORD,
        AP_CHANNEL,
        false,          // hidden SSID
        AP_MAX_CONN
    );

    if (!ok) {
        Serial.println("[WIFI][ERROR] Failed to start AP");
        return;
    }

    IPAddress ip = WiFi.softAPIP();

    Serial.println("[WIFI][OK] AP started");
    Serial.print("[WIFI] SSID: ");
    Serial.println(AP_SSID);
    Serial.print("[WIFI] IP: ");
    Serial.println(ip);

    wifi_started = true;
}

// (chưa cần loop cho wifi ở giai đoạn này)

