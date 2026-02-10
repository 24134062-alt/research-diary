#ifndef WEBSOCKET_CLIENT_H
#define WEBSOCKET_CLIENT_H

#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include <base64.h>


/**
 * WebSocket client for AudioGlasses ESP32
 * Compatible with Xiaozhi protocol for audio streaming
 */
class AudioWebSocketClient {
private:
  WebSocketsClient webSocket;
  String deviceId;
  bool connected = false;

  // Callback for AI response
  void (*onResponseCallback)(String text, bool hasVisual, String visualType,
                             String visualParam);

public:
  AudioWebSocketClient(String id) : deviceId(id), onResponseCallback(nullptr) {}

  /**
   * Initialize WebSocket connection
   */
  void begin(const char *host, uint16_t port = 8765) {
    webSocket.begin(host, port, "/");

    // Set event handler using lambda to capture 'this'
    webSocket.onEvent([this](WStype_t type, uint8_t *payload, size_t length) {
      this->handleEvent(type, payload, length);
    });

    webSocket.setReconnectInterval(5000); // Auto-reconnect every 5s
    Serial.printf("[WS] Configured for %s:%d\n", host, port);
  }

  /**
   * Must call in loop()
   */
  void loop() { webSocket.loop(); }

  /**
   * Send audio packet to PC
   */
  void sendAudio(uint8_t *audio, size_t len, uint8_t flags, uint32_t seq) {
    if (!connected) {
      Serial.println("[WS] Not connected, skipping audio");
      return;
    }

    // Create JSON document
    StaticJsonDocument<4096> doc;
    doc["type"] = "audio";
    doc["device_id"] = deviceId;
    doc["flags"] = flags;
    doc["sequence"] = seq;

    // Base64 encode audio data
    String audioB64 = base64::encode(audio, len);
    doc["audio"] = audioB64;

    // Serialize and send
    String output;
    serializeJson(doc, output);
    webSocket.sendTXT(output);

    Serial.printf("[WS] Sent audio: %d bytes (seq=%u)\n", len, seq);
  }

  /**
   * Send heartbeat
   */
  void sendHeartbeat() {
    if (!connected)
      return;

    StaticJsonDocument<128> doc;
    doc["type"] = "heartbeat";
    doc["timestamp"] = millis();

    String output;
    serializeJson(doc, output);
    webSocket.sendTXT(output);
  }

  /**
   * Set callback for AI response
   */
  void setResponseCallback(void (*callback)(String, bool, String, String)) {
    onResponseCallback = callback;
  }

  /**
   * Check if connected
   */
  bool isConnected() { return connected; }

private:
  /**
   * Handle WebSocket events
   */
  void handleEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("[WS] Disconnected!");
      connected = false;
      break;

    case WStype_CONNECTED:
      Serial.printf("[WS] Connected to server\n");
      connected = true;
      sendRegister();
      break;

    case WStype_TEXT:
      handleTextMessage(payload, length);
      break;

    case WStype_ERROR:
      Serial.println("[WS] Error occurred");
      break;

    default:
      break;
    }
  }

  /**
   * Send device registration
   */
  void sendRegister() {
    StaticJsonDocument<200> doc;
    doc["type"] = "register";
    doc["device_id"] = deviceId;

    String output;
    serializeJson(doc, output);
    webSocket.sendTXT(output);

    Serial.printf("[WS] Registered as: %s\n", deviceId.c_str());
  }

  /**
   * Handle text message from server
   */
  void handleTextMessage(uint8_t *payload, size_t length) {
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error) {
      Serial.printf("[WS] JSON parse error: %s\n", error.c_str());
      return;
    }

    String type = doc["type"] | "";

    if (type == "register_ack") {
      Serial.println("[WS] Registration acknowledged");
    } else if (type == "ai_response") {
      String text = doc["text"] | "";
      bool hasVisual = doc["has_visual"] | false;
      String visualType = doc["visual_type"] | "";
      String visualParam = doc["visual_param"] | "";

      Serial.printf("[WS] AI Response: %s\n", text.c_str());

      if (onResponseCallback) {
        onResponseCallback(text, hasVisual, visualType, visualParam);
      }
    } else if (type == "text_chunk") {
      // Streaming response chunk
      String chunk = doc["text"] | "";
      bool isFinal = doc["is_final"] | false;
      Serial.printf("[WS] Chunk: %s (final=%d)\n", chunk.c_str(), isFinal);
    } else if (type == "heartbeat_ack") {
      // Heartbeat acknowledged
    } else {
      Serial.printf("[WS] Unknown message type: %s\n", type.c_str());
    }
  }
};

#endif // WEBSOCKET_CLIENT_H
