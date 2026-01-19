@echo off
echo Uploading firmware to ESP32 on COM3...
python -m esptool --chip esp32 --port COM3 --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 80m --flash_size detect 0x1000 .pio\build\esp32dev\bootloader.bin 0x8000 .pio\build\esp32dev\partitions.bin 0xe000 .pio\build\esp32dev\boot_app0.bin 0x10000 .pio\build\esp32dev\firmware.bin
pause
