#include "uplink_audio.h"
#include <WiFi.h>
#include <WiFiUdp.h>


WiFiUDP udp;

void UplinkAudio::begin(const char *host, int port) {
  _host = host;
  _port = port;
  _sequence = 0;
  udp.begin(_port); // Bind to local port if needed, or just begin
  Serial.printf("Uplink Audio initialized targeting %s:%d\n", _host, _port);
}

void UplinkAudio::sendAudioPacket(uint8_t *data, size_t len, bool aiMode) {
  if (WiFi.status() == WL_CONNECTED) {
    udp.beginPacket(_host, _port);

    // Byte 0: Flags (bit 0 = AI mode)
    uint8_t flags = aiMode ? 0x01 : 0x00;
    udp.write(&flags, 1);

    // Bytes 1-4: Sequence Number (4 bytes)
    udp.write((uint8_t *)&_sequence, sizeof(_sequence));

    // Bytes 5+: Audio Data
    udp.write(data, len);

    udp.endPacket();

    _sequence++;
  }
}
