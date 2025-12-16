#pragma once
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <Wire.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

// Vietnamese character normalization (remove diacritics for OLED display)
String normalizeVietnamese(const char *text);

class OLEDDisplay {
private:
  Adafruit_SSD1306 display;
  String scrollText;
  int scrollPos;
  unsigned long lastScrollTime;

public:
  OLEDDisplay();

  void begin();
  void clear();

  // Display modes
  void showStatus(const char *mode, int battery);
  void showAIListening();
  void showAIThinking();
  void showAIResponse(const char *text);

  // Text utilities
  void displayText(const char *text, int x, int y, int size);
  void displayCentered(const char *text, int y, int size);

  // Auto-scroll for long text
  void startScroll(const char *text);
  void updateScroll();
};
