# Audio Protocol

## Format
- **Sample Rate**: 16000 Hz
- **Bit Depth**: 16-bit
- **Channels**: Mono (1 channel)
- **Encoding**: PCM (Signed 16-bit Little Endian)

## Transport
- **Protocol**: UDP
- **Port**: 12345 (Default)

## Packet Structure
Each UDP packet consists of a header and a payload.

| Field | Type | Size | Description |
|---|---|---|---|
| Sequence Number | uint32_t | 4 bytes | Incremental counter to detect packet loss |
| Audio Data | byte[] | N bytes | Raw PCM audio samples (e.g., 512 or 1024 bytes) |

**Total Packet Size**: 4 + N bytes.
