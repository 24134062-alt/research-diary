/*************************************************
 * ClassLink - 3D Shapes Test
 *
 * Test file để kiểm tra hiển thị hình học 3D trên OLED
 * CHỈ CẦN: ESP32 + OLED SSD1306
 *
 * Wiring:
 *   OLED VCC -> 3.3V
 *   OLED GND -> GND
 *   OLED SDA -> GPIO 21
 *   OLED SCL -> GPIO 22
 *
 * Nhấn nút BOOT để chuyển qua các hình
 *************************************************/

#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Arduino.h>
#include <Wire.h>
#include <math.h>

// ====== OLED Config ======
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_I2C_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ====== Button ======
#define BTN_PIN 0

// ====== Shapes3D Class (embedded) ======
class Shapes3D {
private:
  Adafruit_SSD1306 *disp;

  void drawLine(int x0, int y0, int x1, int y1) {
    disp->drawLine(x0, y0, x1, y1, SSD1306_WHITE);
  }

  void rotateY(float *x, float *z, float angle) {
    float rad = angle * PI / 180.0;
    float cosA = cos(rad);
    float sinA = sin(rad);
    float newX = (*x) * cosA - (*z) * sinA;
    float newZ = (*x) * sinA + (*z) * cosA;
    *x = newX;
    *z = newZ;
  }

public:
  Shapes3D(Adafruit_SSD1306 *d) : disp(d) {}

  // ====== CUBE ======
  void drawCube(int cx, int cy, int size) {
    int s = size / 2;
    int x1 = cx - s, y1 = cy + s;
    int x2 = cx + s, y2 = cy + s;
    int x3 = cx + s, y3 = cy - s;
    int x4 = cx - s, y4 = cy - s;

    int offset_x = s / 2;
    int offset_y = -s / 3;
    int x5 = x1 + offset_x, y5 = y1 + offset_y;
    int x6 = x2 + offset_x, y6 = y2 + offset_y;
    int x7 = x3 + offset_x, y7 = y3 + offset_y;
    int x8 = x4 + offset_x, y8 = y4 + offset_y;

    // Front
    drawLine(x1, y1, x2, y2);
    drawLine(x2, y2, x3, y3);
    drawLine(x3, y3, x4, y4);
    drawLine(x4, y4, x1, y1);
    // Back
    drawLine(x5, y5, x6, y6);
    drawLine(x6, y6, x7, y7);
    drawLine(x7, y7, x8, y8);
    drawLine(x8, y8, x5, y5);
    // Connect
    drawLine(x1, y1, x5, y5);
    drawLine(x2, y2, x6, y6);
    drawLine(x3, y3, x7, y7);
    drawLine(x4, y4, x8, y8);
  }

  // ====== PYRAMID ======
  void drawPyramid(int cx, int cy, int size) {
    int b1_x = cx, b1_y = cy + size / 2;
    int b2_x = cx - size / 2, b2_y = cy;
    int b3_x = cx + size / 2, b3_y = cy;
    int apex_x = cx, apex_y = cy - size;

    drawLine(b1_x, b1_y, b2_x, b2_y);
    drawLine(b2_x, b2_y, b3_x, b3_y);
    drawLine(b3_x, b3_y, b1_x, b1_y);
    drawLine(b1_x, b1_y, apex_x, apex_y);
    drawLine(b2_x, b2_y, apex_x, apex_y);
    drawLine(b3_x, b3_y, apex_x, apex_y);
  }

  // ====== SPHERE ======
  void drawSphere(int cx, int cy, int radius) {
    disp->drawCircle(cx, cy, radius, SSD1306_WHITE);
    for (int i = -1; i <= 1; i++) {
      int y_offset = i * radius / 2;
      int r = sqrt(radius * radius - (y_offset * y_offset));
      disp->drawCircle(cx, cy + y_offset, r * 0.7, SSD1306_WHITE);
    }
  }

  // ====== CYLINDER ======
  void drawCylinder(int cx, int cy, int radius, int height) {
    disp->drawCircle(cx, cy - height / 2, radius, SSD1306_WHITE);
    disp->drawCircle(cx, cy + height / 2, radius, SSD1306_WHITE);
    drawLine(cx - radius, cy - height / 2, cx - radius, cy + height / 2);
    drawLine(cx + radius, cy - height / 2, cx + radius, cy + height / 2);
  }

  // ====== ROTATING CUBE ======
  void drawRotatingCube(int cx, int cy, int size, float angle) {
    float vertices[8][3] = {{-1, -1, -1}, {1, -1, -1}, {1, 1, -1}, {-1, 1, -1},
                            {-1, -1, 1},  {1, -1, 1},  {1, 1, 1},  {-1, 1, 1}};

    float s = size / 2.0;
    int projected[8][2];

    for (int i = 0; i < 8; i++) {
      float x = vertices[i][0] * s;
      float y = vertices[i][1] * s;
      float z = vertices[i][2] * s;
      rotateY(&x, &z, angle);
      float scale = 200.0 / (200.0 + z);
      projected[i][0] = cx + (int)(x * scale);
      projected[i][1] = cy + (int)(y * scale);
    }

    int edges[12][2] = {{0, 1}, {1, 2}, {2, 3}, {3, 0}, {4, 5}, {5, 6},
                        {6, 7}, {7, 4}, {0, 4}, {1, 5}, {2, 6}, {3, 7}};

    for (int i = 0; i < 12; i++) {
      drawLine(projected[edges[i][0]][0], projected[edges[i][0]][1],
               projected[edges[i][1]][0], projected[edges[i][1]][1]);
    }
  }

  // ====== H2O MOLECULE ======
  void drawH2O(int cx, int cy) {
    disp->fillCircle(cx, cy, 8, SSD1306_WHITE);
    disp->fillCircle(cx - 20, cy - 10, 5, SSD1306_WHITE);
    disp->fillCircle(cx + 20, cy - 10, 5, SSD1306_WHITE);
    drawLine(cx - 6, cy - 4, cx - 15, cy - 8);
    drawLine(cx + 6, cy - 4, cx + 15, cy - 8);
  }

  // ====== COORDINATE SYSTEM ======
  void drawCoordinate(int cx, int cy, int size) {
    drawLine(cx, cy, cx + size, cy);
    drawLine(cx, cy, cx, cy - size);
    drawLine(cx, cy, cx - size / 2, cy + size / 2);
    disp->fillCircle(cx, cy, 2, SSD1306_WHITE);
  }
};

// ====== Test Data ======
const char *shapeNames[] = {"CUBE - Hinh lap phuong", "PYRAMID - Hinh chop",
                            "SPHERE - Hinh cau",      "CYLINDER - Hinh tru",
                            "H2O - Phan tu nuoc",     "XYZ - He truc toa do",
                            "ROTATING CUBE"};
int numShapes = 7;
int currentShape = 0;
float rotationAngle = 0;

Shapes3D *shapes;

// Function prototype
void drawCurrentShape();

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("=========================================");
  Serial.println("   ClassLink - 3D Shapes Test           ");
  Serial.println("=========================================");

  pinMode(BTN_PIN, INPUT_PULLUP);

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("[OLED] Failed!");
    while (1)
      delay(1000);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  shapes = new Shapes3D(&display);

  // Welcome
  display.setCursor(20, 20);
  display.println("ClassLink 3D");
  display.setCursor(20, 35);
  display.println("Shapes Test");
  display.display();

  Serial.println("Nhan nut BOOT de chuyen hinh");
  delay(2000);

  drawCurrentShape();
}

void drawCurrentShape() {
  display.clearDisplay();

  // Title
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(shapeNames[currentShape]);
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  int cx = 64, cy = 40;

  switch (currentShape) {
  case 0:
    shapes->drawCube(cx, cy, 30);
    break;
  case 1:
    shapes->drawPyramid(cx, cy, 28);
    break;
  case 2:
    shapes->drawSphere(cx, cy, 18);
    break;
  case 3:
    shapes->drawCylinder(cx, cy, 15, 30);
    break;
  case 4:
    shapes->drawH2O(cx, cy);
    break;
  case 5:
    shapes->drawCoordinate(cx, cy, 25);
    break;
  case 6:
    break; // Rotating handled in loop
  }

  display.display();
  Serial.printf("[SHAPE] %s\n", shapeNames[currentShape]);
}

void loop() {
  // Button press
  if (digitalRead(BTN_PIN) == LOW) {
    delay(300);
    currentShape = (currentShape + 1) % numShapes;
    rotationAngle = 0;
    drawCurrentShape();
  }

  // Rotating cube animation
  if (currentShape == 6) {
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("ROTATING CUBE");
    display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

    shapes->drawRotatingCube(64, 40, 35, rotationAngle);
    display.display();

    rotationAngle += 5;
    if (rotationAngle >= 360)
      rotationAngle = 0;
    delay(50);
  }

  delay(50);
}
