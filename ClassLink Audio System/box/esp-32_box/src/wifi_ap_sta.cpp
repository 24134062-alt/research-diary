/*************************************************
 * File: wifi_ap_sta.cpp
 *
 * Enhanced WiFi AP Management with OTA Updates
 *
 * Features:
 * - Dynamic WiFi credentials (SSID/Password)
 * - Persistent storage using Preferences
 * - OTA config updates via MQTT
 * - Automatic AP restart on config change
 *************************************************/

#include "../include/wifi_config.h"
#include <Arduino.h>
#include <Preferences.h>
#include <WiFi.h>

// ====== Default Configuration ======
static const char *DEFAULT_SSID = "CLASS-BOX";
static const char *DEFAULT_PASSWORD = "12345678";
static const uint8_t AP_CHANNEL = 6;
static const uint8_t AP_MAX_CONN = 6;

// ====== State ======
static bool wifi_started = false;
static WiFiCredentials current_creds;
static Preferences prefs;

// ====== Private Functions ======

/**
 * Load WiFi credentials from Preferences
 * Falls back to default if no stored credentials
 */
static void load_credentials() {
  prefs.begin(WIFI_PREFS_NAMESPACE, false); // Read-write mode

  String stored_ssid = prefs.getString("ssid", "");
  String stored_pass = prefs.getString("password", "");

  if (stored_ssid.length() > 0 && stored_pass.length() >= 8) {
    // Use stored credentials
    strncpy(current_creds.ssid, stored_ssid.c_str(), WIFI_SSID_MAX_LEN);
    strncpy(current_creds.password, stored_pass.c_str(), WIFI_PASS_MAX_LEN);
    current_creds.ssid[WIFI_SSID_MAX_LEN] = '\0';
    current_creds.password[WIFI_PASS_MAX_LEN] = '\0';
    current_creds.isValid = true;

    Serial.println("[WIFI] Loaded credentials from storage");
    Serial.printf("[WIFI]   SSID: %s\n", current_creds.ssid);
  } else {
    // Use default credentials
    strncpy(current_creds.ssid, DEFAULT_SSID, WIFI_SSID_MAX_LEN);
    strncpy(current_creds.password, DEFAULT_PASSWORD, WIFI_PASS_MAX_LEN);
    current_creds.isValid = true;

    Serial.println("[WIFI] Using default credentials (not stored)");
  }

  prefs.end();
}

/**
 * Save WiFi credentials to Preferences
 */
static bool save_credentials(const char *ssid, const char *password) {
  prefs.begin(WIFI_PREFS_NAMESPACE, false);

  bool ok = prefs.putString("ssid", ssid) > 0;
  ok &= prefs.putString("password", password) > 0;

  prefs.end();

  if (ok) {
    Serial.println("[WIFI] Credentials saved to storage");
  } else {
    Serial.println("[WIFI][ERROR] Failed to save credentials");
  }

  return ok;
}

/**
 * Start WiFi AP with given credentials
 */
static bool start_ap(const char *ssid, const char *password) {
  Serial.printf("[WIFI] Starting AP: %s\n", ssid);

  WiFi.mode(WIFI_AP);

  bool ok = WiFi.softAP(ssid, password, AP_CHANNEL,
                        false, // not hidden
                        AP_MAX_CONN);

  if (!ok) {
    Serial.println("[WIFI][ERROR] Failed to start AP");
    return false;
  }

  IPAddress ip = WiFi.softAPIP();
  Serial.println("[WIFI][OK] AP started successfully");
  Serial.printf("[WIFI]   SSID: %s\n", ssid);
  Serial.printf("[WIFI]   IP: %s\n", ip.toString().c_str());
  Serial.printf("[WIFI]   Max connections: %d\n", AP_MAX_CONN);

  return true;
}

// ====== Public API Implementation ======

void wifi_init() {
  if (wifi_started) {
    Serial.println("[WIFI] Already initialized");
    return;
  }

  Serial.println("[WIFI] Initializing WiFi AP...");

  // Load credentials from storage or use defaults
  load_credentials();

  // Try to start AP with loaded credentials
  if (start_ap(current_creds.ssid, current_creds.password)) {
    wifi_started = true;
    Serial.println("[WIFI] Using stored/default credentials");
  } else {
    // Failover: If stored credentials fail, try DEFAULT
    Serial.println(
        "[WIFI][WARN] Failed with stored credentials, trying DEFAULT...");

    strncpy(current_creds.ssid, DEFAULT_SSID, WIFI_SSID_MAX_LEN);
    strncpy(current_creds.password, DEFAULT_PASSWORD, WIFI_PASS_MAX_LEN);
    current_creds.ssid[WIFI_SSID_MAX_LEN] = '\0';
    current_creds.password[WIFI_PASS_MAX_LEN] = '\0';

    if (start_ap(DEFAULT_SSID, DEFAULT_PASSWORD)) {
      wifi_started = true;
      Serial.println("[WIFI] ✅ Failover to DEFAULT successful");
    } else {
      Serial.println("[WIFI][ERROR] CRITICAL: Even DEFAULT failed!");
    }
  }
}

bool wifi_update_credentials(const char *new_ssid, const char *new_password) {
  if (!new_ssid || !new_password) {
    Serial.println("[WIFI][ERROR] Invalid credentials (NULL)");
    return false;
  }

  // Validate SSID length
  size_t ssid_len = strlen(new_ssid);
  if (ssid_len == 0 || ssid_len > WIFI_SSID_MAX_LEN) {
    Serial.printf("[WIFI][ERROR] Invalid SSID length: %d (max %d)\n", ssid_len,
                  WIFI_SSID_MAX_LEN);
    return false;
  }

  // Validate password length (WPA2 requires >= 8 chars)
  size_t pass_len = strlen(new_password);
  if (pass_len < 8 || pass_len > WIFI_PASS_MAX_LEN) {
    Serial.printf("[WIFI][ERROR] Invalid password length: %d (min 8, max %d)\n",
                  pass_len, WIFI_PASS_MAX_LEN);
    return false;
  }

  Serial.println("[WIFI] ========================================");
  Serial.println("[WIFI] OTA Config Update Received");
  Serial.printf("[WIFI]   Old SSID: %s\n", current_creds.ssid);
  Serial.printf("[WIFI]   New SSID: %s\n", new_ssid);
  Serial.println("[WIFI] ========================================");

  // Count connected devices
  uint8_t connected_count = WiFi.softAPgetStationNum();
  if (connected_count > 0) {
    Serial.printf(
        "[WIFI][WARN] %d devices currently connected will be disconnected\n",
        connected_count);
  }

  // Update credentials in memory
  strncpy(current_creds.ssid, new_ssid, WIFI_SSID_MAX_LEN);
  strncpy(current_creds.password, new_password, WIFI_PASS_MAX_LEN);
  current_creds.ssid[WIFI_SSID_MAX_LEN] = '\0';
  current_creds.password[WIFI_PASS_MAX_LEN] = '\0';

  // Save to persistent storage
  if (!save_credentials(new_ssid, new_password)) {
    Serial.println(
        "[WIFI][ERROR] Failed to save credentials, but will try to apply");
  }

  // Restart AP with new credentials
  wifi_restart_ap();

  return true;
}

WiFiCredentials wifi_get_credentials() { return current_creds; }

void wifi_restart_ap() {
  Serial.println("[WIFI] Restarting WiFi AP...");

  // Disconnect all clients
  WiFi.softAPdisconnect(true);
  delay(500);

  // Restart with current credentials
  if (start_ap(current_creds.ssid, current_creds.password)) {
    wifi_started = true;
    Serial.println("[WIFI] AP restart completed");
  } else {
    Serial.println("[WIFI][ERROR] AP restart failed");
    wifi_started = false;
  }
}

void wifi_reset_to_default() {
  Serial.println("[WIFI] Resetting to default credentials...");

  strncpy(current_creds.ssid, DEFAULT_SSID, WIFI_SSID_MAX_LEN);
  strncpy(current_creds.password, DEFAULT_PASSWORD, WIFI_PASS_MAX_LEN);

  save_credentials(DEFAULT_SSID, DEFAULT_PASSWORD);
  wifi_restart_ap();
}
