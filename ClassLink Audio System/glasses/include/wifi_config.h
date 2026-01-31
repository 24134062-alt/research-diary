/*************************************************
 * WiFi Configuration Management for Glasses
 *
 * Purpose:
 * - Multi-WiFi network support (up to 5 networks)
 * - Priority-based connection (CLASS-BOX always priority 0)
 * - OTA config updates via MQTT
 * - Persistent storage using Preferences
 *************************************************/

#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#include <Arduino.h>
#include <Preferences.h>

// ====== Constants ======
#define WIFI_SSID_MAX_LEN 32
#define WIFI_PASS_MAX_LEN 64
#define MAX_WIFI_NETWORKS 5
#define WIFI_PREFS_NAMESPACE "wifi"

// Default WiFi (ALWAYS priority 0 - highest)
#define DEFAULT_WIFI_SSID "CLASS-BOX"
#define DEFAULT_WIFI_PASS "12345678"

// ====== WiFi Network Structure ======
struct WiFiNetwork {
  char ssid[WIFI_SSID_MAX_LEN + 1];
  char password[WIFI_PASS_MAX_LEN + 1];
  uint8_t priority; // 0 = highest priority
};

// ====== Public API ======

/**
 * Initialize WiFi with priority-based connection
 * Tries networks from priority 0 to 4, connects to first available
 */
void wifi_init();

/**
 * Connect to WiFi using priority list
 * Scans for available networks and connects to highest priority one
 * @return true if connected
 */
bool wifi_connect();

/**
 * Add/update WiFi network in list
 * @param ssid Network SSID
 * @param password Network password
 * @param priority Priority (0-4, 0 is highest, 0 is reserved for DEFAULT)
 */
void wifi_add_network(const char *ssid, const char *password, uint8_t priority);

/**
 * Load WiFi list from Preferences
 */
void wifi_load_list();

/**
 * Save WiFi list to Preferences
 */
void wifi_save_list();

/**
 * Handle WiFi OTA config update from MQTT
 * @param new_ssid New WiFi SSID
 * @param new_password New WiFi password
 */
void wifi_ota_update(const char *new_ssid, const char *new_password);

#endif // WIFI_CONFIG_H
