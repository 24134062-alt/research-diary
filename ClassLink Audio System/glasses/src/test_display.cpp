/*************************************************
 * ClassLink - OLED Display Test
 *
 * Test file để kiểm tra hiển thị text trên OLED
 * KHÔNG CẦN: WiFi, MQTT, Box, Raspberry Pi
 * CHỈ CẦN: ESP32 + OLED SSD1306
 *************************************************/

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <Wire.h>

// ====== OLED Config ======
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_I2C_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ====== Text Display Config ======
#define TEXT_SIZE 2
#define CHARS_PER_LINE 10
#define LINES_PER_SCREEN 4
#define SCROLL_DELAY_MS 2000

// ====== Test Text ======
const char *testTexts[] = {
    "Test 1: Chu ngan",
    "Test 2: Day la dong text dai hon de kiem tra tinh nang tu dong cuon trang "
    "pagination",
    "Test 3: Phuong trinh bac nhat ax + b = 0. Nghiem x = -b/a. Vi du: 2x + 4 "
    "= 0 thi x = -2",
    "Test 4: H2O la phan tu nuoc gom 2 nguyen tu Hydro va 1 nguyen tu Oxy"};
int numTests = 4;
int currentTest = 0;

// ====== Button ======
#define BTN_PIN 0 // Boot button on ESP32

void displayText(const char *text);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("=========================================");
  Serial.println("   ClassLink - OLED Display Test        ");
  Serial.println("=========================================");

  pinMode(BTN_PIN, INPUT_PULLUP);

  // OLED Setup
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("[OLED] SSD1306 failed!");
    while (1)
      ;
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Welcome screen
  display.setTextSize(2);
  display.setCursor(10, 20);
  display.println("ClassLink");
  display.setTextSize(1);
  display.setCursor(20, 45);
  display.println("OLED Test Ready");
  display.display();

  Serial.println("[OLED] Display initialized");
  Serial.println();
  Serial.println("Nhan nut BOOT de chuyen test tiep theo");
  Serial.println("-----------------------------------------");

  delay(2000);

  // Show first test
  displayText(testTexts[currentTest]);
}

void loop() {
  // Button press to cycle through tests
  if (digitalRead(BTN_PIN) == LOW) {
    delay(300); // Debounce

    currentTest = (currentTest + 1) % numTests;
    Serial.printf("[TEST] Showing test %d/%d\n", currentTest + 1, numTests);
    displayText(testTexts[currentTest]);
  }

  delay(50);
}

// ====== Display Text with Pagination ======
void displayText(const char *text) {
  String textStr = String(text);
  int textLen = textStr.length();

  int charsPerScreen = CHARS_PER_LINE * LINES_PER_SCREEN;

  Serial.printf("[DISPLAY] Text: %s\n", text);
  Serial.printf("[DISPLAY] Length: %d, CharsPerScreen: %d\n", textLen,
                charsPerScreen);

  // Short text - display directly
  if (textLen <= charsPerScreen) {
    display.clearDisplay();
    display.setTextSize(TEXT_SIZE);
    display.setTextWrap(true);
    display.setCursor(0, 0);
    display.println(text);
    display.display();
    Serial.println("[DISPLAY] Short text - no pagination");
    return;
  }

  // Long text - paginate
  int totalPages = (textLen + charsPerScreen - 1) / charsPerScreen;
  Serial.printf("[DISPLAY] Long text - %d pages\n", totalPages);

  for (int page = 0; page < totalPages; page++) {
    display.clearDisplay();
    display.setTextSize(TEXT_SIZE);
    display.setTextWrap(true);
    display.setCursor(0, 0);

    int startIdx = page * charsPerScreen;
    int endIdx = min(startIdx + charsPerScreen, textLen);
    String pageText = textStr.substring(startIdx, endIdx);

    display.println(pageText);

    // Page indicator
    display.setTextSize(1);
    display.setCursor(100, 56);
    display.print(page + 1);
    display.print("/");
    display.print(totalPages);

    display.display();

    Serial.printf("[DISPLAY] Page %d/%d\n", page + 1, totalPages);
    delay(SCROLL_DELAY_MS);
  }
}
