#pragma once
#include <Arduino.h>

class I2SMic {
public:
    void setup();
    size_t read(uint8_t* buffer, size_t size);
};
