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

void UplinkAudio::sendAudioPacket(uint8_t *data, size_t len, bool aiMode,
                                  bool classMode) {
  if (WiFi.status() == WL_CONNECTED) {
    udp.beginPacket(_host, _port);

    // Header: 1 byte flags + 4 bytes sequence
    // Flags: bit 0 = AI mode, bit 1 = class mode
    uint8_t header[5];
    header[0] = (aiMode ? 0x01 : 0x00) | (classMode ? 0x02 : 0x00);
    memcpy(&header[1], &_sequence, 4);

    udp.write(header, 5);
    udp.write(data, len);

    udp.endPacket();

    _sequence++;
  }
}
