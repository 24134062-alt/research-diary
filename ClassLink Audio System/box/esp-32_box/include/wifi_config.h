/*************************************************
 * WiFi Configuration Management
 *
 * Purpose:
 * - Manage WiFi AP credentials dynamically
 * - Support OTA config updates via MQTT
 * - Store credentials in persistent storage (Preferences)
 *************************************************/

#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <Arduino.h>

// ====== Constants ======
#define WIFI_SSID_MAX_LEN 32
#define WIFI_PASS_MAX_LEN 64
#define WIFI_PREFS_NAMESPACE "wifi"

// ====== WiFi Credentials Structure ======
struct WiFiCredentials {
  char ssid[WIFI_SSID_MAX_LEN + 1];
  char password[WIFI_PASS_MAX_LEN + 1];
  bool isValid;
};

// ====== Public API ======

/**
 * Initialize WiFi AP with stored or default credentials
 */
void wifi_init();

/**
 * Update WiFi credentials and restart AP
 * @param new_ssid New SSID (max 32 chars)
 * @param new_password New password (min 8, max 64 chars)
 * @return true if update successful
 */
bool wifi_update_credentials(const char *new_ssid, const char *new_password);

/**
 * Get current WiFi credentials
 * @return WiFiCredentials structure
 */
WiFiCredentials wifi_get_credentials();

/**
 * Restart WiFi AP with current credentials
 */
void wifi_restart_ap();

/**
 * Reset to default credentials (CLASS-BOX / 12345678)
 */
void wifi_reset_to_default();

#endif // WIFI_CONFIG_H
