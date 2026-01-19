#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Với size 2: 6 ký tự rộng * 2 = 12px, 8 ký tự cao * 2 = 16px
// 128 / 12 = 10 ký tự/dòng (nhưng để an toàn dùng 9)
// 64 / 16 = 4 dòng
#define CHARS_PER_LINE 9
#define NUM_LINES 4

// 4 dòng text
String lines[NUM_LINES] = {"", "", "", ""};

// Danh sách các từ
String words[] = {"Me",    "em",    "la",   "nguoi", "phu",  "nu",     "diu",
                  "dang",  "va",    "giau", "long",  "yeu",  "thuong", "nhat",
                  "ma",    "em",    "biet", "Moi",   "ngay", "me",     "luon",
                  "day",   "som",   "de",   "lo",    "lang", "cho",    "moi",
                  "nguoi", "trong", "gia",  "dinh"};
int numWords = 32;
int currentWord = 0;
int currentLine = 0;

unsigned long lastUpdateTime = 0;
int typingSpeed = 500; // 500ms mỗi từ - CHẬM

void setup() {
  Wire.begin();
  Wire.setClock(100000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    while (1)
      ;
  }

  display.clearDisplay();
  display.display();
  delay(500);
}

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);

  for (int i = 0; i < NUM_LINES; i++) {
    display.setCursor(0, i * 16);
    display.print(lines[i]);
  }

  display.display();
}

void scrollUp() {
  // Dịch các dòng lên 1
  for (int i = 0; i < NUM_LINES - 1; i++) {
    lines[i] = lines[i + 1];
  }
  lines[NUM_LINES - 1] = ""; // Xóa dòng cuối
}

void addWord(String word) {
  // Kiểm tra xem có vừa dòng hiện tại không
  String testLine = lines[currentLine];
  if (testLine.length() > 0) {
    testLine += " ";
  }
  testLine += word;

  if (testLine.length() <= CHARS_PER_LINE) {
    // Vừa -> thêm vào dòng hiện tại
    if (lines[currentLine].length() > 0) {
      lines[currentLine] += " ";
    }
    lines[currentLine] += word;
  } else {
    // Không vừa -> xuống dòng mới
    currentLine++;
    if (currentLine >= NUM_LINES) {
      // Hết chỗ -> scroll lên
      scrollUp();
      currentLine = NUM_LINES - 1;
    }
    lines[currentLine] = word;
  }
}

void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastUpdateTime >= typingSpeed) {
    lastUpdateTime = currentTime;

    if (currentWord < numWords) {
      addWord(words[currentWord]);
      currentWord++;
    } else {
      // Hết từ -> reset
      delay(3000);
      for (int i = 0; i < NUM_LINES; i++) {
        lines[i] = "";
      }
      currentWord = 0;
      currentLine = 0;
    }
  }

  updateDisplay();
  delay(10);
}
