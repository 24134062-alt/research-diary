#include "oled_display.h"

// Vietnamese to ASCII normalization for OLED display
// Removes diacritics since Adafruit GFX doesn't support Vietnamese fonts
String normalizeVietnamese(const char *text) {
  String result = "";
  String input = String(text);

  // Mapping Vietnamese characters to ASCII equivalents
  const char *viet[] = {
      "á", "à", "ả", "ã", "ạ", "ă", "ắ", "ằ", "ẳ", "ẵ", "ặ", "â", "ấ", "ầ", "ẩ",
      "ẫ", "ậ", "é", "è", "ẻ", "ẽ", "ẹ", "ê", "ế", "ề", "ể", "ễ", "ệ", "í", "ì",
      "ỉ", "ĩ", "ị", "ó", "ò", "ỏ", "õ", "ọ", "ô", "ố", "ồ", "ổ", "ỗ", "ộ", "ơ",
      "ớ", "ờ", "ở", "ỡ", "ợ", "ú", "ù", "ủ", "ũ", "ụ", "ư", "ứ", "ừ", "ử", "ữ",
      "ự", "ý", "ỳ", "ỷ", "ỹ", "ỵ", "đ", "Á", "À", "Ả", "Ã", "Ạ", "Ă", "Ắ", "Ằ",
      "Ẳ", "Ẵ", "Ặ", "Â", "Ấ", "Ầ", "Ẩ", "Ẫ", "Ậ", "É", "È", "Ẻ", "Ẽ", "Ẹ", "Ê",
      "Ế", "Ề", "Ể", "Ễ", "Ệ", "Í", "Ì", "Ỉ", "Ĩ", "Ị", "Ó", "Ò", "Ỏ", "Õ", "Ọ",
      "Ô", "Ố", "Ồ", "Ổ", "Ỗ", "Ộ", "Ơ", "Ớ", "Ờ", "Ở", "Ỡ", "Ợ", "Ú", "Ù", "Ủ",
      "Ũ", "Ụ", "Ư", "Ứ", "Ừ", "Ử", "Ữ", "Ự", "Ý", "Ỳ", "Ỷ", "Ỹ", "Ỵ", "Đ"};

  const char *ascii[] = {
      "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a",
      "a", "a", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "e", "i", "i",
      "i", "i", "i", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o", "o",
      "o", "o", "o", "o", "o", "u", "u", "u", "u", "u", "u", "u", "u", "u", "u",
      "u", "y", "y", "y", "y", "y", "d", "A", "A", "A", "A", "A", "A", "A", "A",
      "A", "A", "A", "A", "A", "A", "A", "A", "A", "E", "E", "E", "E", "E", "E",
      "E", "E", "E", "E", "E", "I", "I", "I", "I", "I", "O", "O", "O", "O", "O",
      "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "U", "U", "U",
      "U", "U", "U", "U", "U", "U", "U", "U", "Y", "Y", "Y", "Y", "Y", "D"};

  int numChars = sizeof(viet) / sizeof(viet[0]);

  for (int i = 0; i < input.length();) {
    bool replaced = false;

    // Check for multi-byte UTF-8 characters
    for (int j = 0; j < numChars; j++) {
      String vietChar = String(viet[j]);
      if (input.substring(i).startsWith(vietChar)) {
        result += ascii[j];
        i += vietChar.length();
        replaced = true;
        break;
      }
    }

    if (!replaced) {
      result += input.charAt(i);
      i++;
    }
  }

  return result;
}

OLEDDisplay::OLEDDisplay()
    : display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET), scrollPos(0),
      lastScrollTime(0) {}

void OLEDDisplay::begin() {
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;
  }

  // AR OPTIMIZATION: Max brightness for combiner glass
  display.dim(false);       // No dimming - full brightness
  display.setContrast(255); // Maximum contrast

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.display();

  Serial.println(F("OLED initialized for AR combiner (max brightness)"));
}

void OLEDDisplay::clear() {
  display.clearDisplay();
  display.display();
}

void OLEDDisplay::showStatus(const char *mode, int battery) {
  display.clearDisplay();

  // Mode indicator
  display.setTextSize(1);
  display.setCursor(0, 0);
  if (strcmp(mode, "class") == 0) {
    display.println("MODE: CLASS");
  } else if (strcmp(mode, "private") == 0) {
    display.println("MODE: PRIVATE");
  }

  // Battery
  display.setCursor(0, 16);
  display.print("BAT: ");
  display.print(battery);
  display.println("%");

  // Battery icon
  int barWidth = map(battery, 0, 100, 0, 40);
  display.drawRect(85, 16, 42, 12, SSD1306_WHITE);
  display.fillRect(87, 18, barWidth, 8, SSD1306_WHITE);
  display.fillRect(127, 20, 1, 8, SSD1306_WHITE); // Battery nub

  display.display();
}

void OLEDDisplay::showAIListening() {
  display.clearDisplay();
  display.setTextSize(2);

  // Icon: Microphone
  display.setCursor(48, 10);
  display.println("AI");

  display.setTextSize(1);
  display.setCursor(20, 40);
  display.println("Dang nghe...");

  display.display();
}

void OLEDDisplay::showAIThinking() {
  display.clearDisplay();
  display.setTextSize(1);

  display.setCursor(30, 20);
  display.println("AI dang suy nghi");

  // Animated dots
  for (int i = 0; i < 3; i++) {
    display.fillCircle(40 + i * 15, 40, 2, SSD1306_WHITE);
  }

  display.display();
}

void OLEDDisplay::showAIResponse(const char *text) {
  display.clearDisplay();
  display.setTextSize(1);

  // Header
  display.setCursor(0, 0);
  display.println("AI TRO GIANG:");
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  // Text - auto wrap at ~16 chars per line
  int y = 16;
  int lineHeight = 10;
  int maxCharsPerLine = 21;

  // Normalize Vietnamese text to ASCII for OLED compatibility
  String str = normalizeVietnamese(text);
  int len = str.length();
  int start = 0;

  while (start < len && y < 60) {
    int end = start + maxCharsPerLine;
    if (end > len)
      end = len;

    // Find last space before maxCharsPerLine
    if (end < len) {
      int lastSpace = str.lastIndexOf(' ', end);
      if (lastSpace > start) {
        end = lastSpace;
      }
    }

    String line = str.substring(start, end);
    display.setCursor(0, y);
    display.println(line);

    start = end;
    if (start < len && str.charAt(start) == ' ')
      start++; // Skip space
    y += lineHeight;
  }

  // If text is too long, show scroll indicator
  if (start < len) {
    display.setCursor(115, 56);
    display.println("...");
    startScroll(text);
  }

  display.display();
}

void OLEDDisplay::displayText(const char *text, int x, int y, int size) {
  display.setTextSize(size);
  display.setCursor(x, y);
  display.println(text);
  display.display();
}

void OLEDDisplay::displayCentered(const char *text, int y, int size) {
  display.setTextSize(size);
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds(text, 0, y, &x1, &y1, &w, &h);
  int x = (SCREEN_WIDTH - w) / 2;
  display.setCursor(x, y);
  display.println(text);
  display.display();
}

void OLEDDisplay::startScroll(const char *text) {
  scrollText = String(text);
  scrollPos = 0;
  lastScrollTime = millis();
}

void OLEDDisplay::updateScroll() {
  if (scrollText.length() == 0)
    return;

  unsigned long now = millis();
  if (now - lastScrollTime > 3000) { // Scroll every 3 seconds
    scrollPos += 21;                 // One line
    if (scrollPos >= scrollText.length()) {
      scrollPos = 0; // Loop
    }

    // Re-display with new scroll position
    String visible = scrollText.substring(scrollPos);
    showAIResponse(visible.c_str());

    lastScrollTime = now;
  }
}
