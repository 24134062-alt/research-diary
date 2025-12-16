#pragma once
#include <Arduino.h>

class UplinkAudio {
private:
  const char *_host;
  int _port;
  uint32_t _sequence;

public:
  void begin(const char *host, int port);
  void sendAudioPacket(uint8_t *data, size_t len, bool aiMode = false);
};
