#include "shapes_3d.h"
#include <math.h>

Shapes3D::Shapes3D(Adafruit_SSD1306 *disp) : display(disp) {}

void Shapes3D::drawLine(int x0, int y0, int x1, int y1) {
  display->drawLine(x0, y0, x1, y1, SSD1306_WHITE);
}

void Shapes3D::rotateY(float *x, float *z, float angle) {
  float rad = angle * PI / 180.0;
  float cosA = cos(rad);
  float sinA = sin(rad);
  float newX = (*x) * cosA - (*z) * sinA;
  float newZ = (*x) * sinA + (*z) * cosA;
  *x = newX;
  *z = newZ;
}

// ============ CUBE (Isometric) ============
void Shapes3D::drawCube(int cx, int cy, int size) {
  int s = size / 2;

  // Isometric projection: angle = 30 degrees
  // Front face vertices
  int x1 = cx - s, y1 = cy + s; // Bottom-left
  int x2 = cx + s, y2 = cy + s; // Bottom-right
  int x3 = cx + s, y3 = cy - s; // Top-right
  int x4 = cx - s, y4 = cy - s; // Top-left

  // Back face (offset for depth)
  int offset_x = s / 2;
  int offset_y = -s / 3;
  int x5 = x1 + offset_x, y5 = y1 + offset_y;
  int x6 = x2 + offset_x, y6 = y2 + offset_y;
  int x7 = x3 + offset_x, y7 = y3 + offset_y;
  int x8 = x4 + offset_x, y8 = y4 + offset_y;

  // Draw front face
  drawLine(x1, y1, x2, y2);
  drawLine(x2, y2, x3, y3);
  drawLine(x3, y3, x4, y4);
  drawLine(x4, y4, x1, y1);

  // Draw back face (dashed for depth)
  drawLine(x5, y5, x6, y6);
  drawLine(x6, y6, x7, y7);
  drawLine(x7, y7, x8, y8);
  drawLine(x8, y8, x5, y5);

  // Connect front to back
  drawLine(x1, y1, x5, y5);
  drawLine(x2, y2, x6, y6);
  drawLine(x3, y3, x7, y7);
  drawLine(x4, y4, x8, y8);
}

// ============ PYRAMID (Triangular) ============
void Shapes3D::drawPyramid(int cx, int cy, int size) {
  int base_size = size;
  int height = size;

  // Base triangle vertices (isometric view)
  int b1_x = cx, b1_y = cy + base_size / 2; // Front
  int b2_x = cx - base_size / 2, b2_y = cy; // Left
  int b3_x = cx + base_size / 2, b3_y = cy; // Right

  // Apex
  int apex_x = cx;
  int apex_y = cy - height;

  // Draw base
  drawLine(b1_x, b1_y, b2_x, b2_y);
  drawLine(b2_x, b2_y, b3_x, b3_y);
  drawLine(b3_x, b3_y, b1_x, b1_y);

  // Draw edges to apex
  drawLine(b1_x, b1_y, apex_x, apex_y);
  drawLine(b2_x, b2_y, apex_x, apex_y);
  drawLine(b3_x, b3_y, apex_x, apex_y);
}

// ============ SPHERE ============
void Shapes3D::drawSphere(int cx, int cy, int radius) {
  // Main circle
  display->drawCircle(cx, cy, radius, SSD1306_WHITE);

  // Latitude lines (horizontal ellipses)
  for (int i = -1; i <= 1; i++) {
    int y_offset = i * radius / 2;
    int r = sqrt(radius * radius - (y_offset * y_offset));
    // Draw ellipse (fake with arcs)
    display->drawCircle(cx, cy + y_offset, r * 0.7, SSD1306_WHITE);
  }

  // Longitude (vertical ellipse)
  // Draw left and right arcs
  for (int i = -radius; i <= radius; i++) {
    int x_offset = i;
    int y = sqrt(radius * radius - x_offset * x_offset) * 0.5;
    display->drawPixel(cx + x_offset, cy + y, SSD1306_WHITE);
    display->drawPixel(cx + x_offset, cy - y, SSD1306_WHITE);
  }
}

// ============ CYLINDER ============
void Shapes3D::drawCylinder(int cx, int cy, int radius, int height) {
  // Top ellipse
  display->drawCircle(cx, cy - height / 2, radius, SSD1306_WHITE);

  // Bottom ellipse
  display->drawCircle(cx, cy + height / 2, radius, SSD1306_WHITE);

  // Side lines
  drawLine(cx - radius, cy - height / 2, cx - radius, cy + height / 2);
  drawLine(cx + radius, cy - height / 2, cx + radius, cy + height / 2);

  // Add depth with ellipse
  for (int i = -radius; i <= radius; i++) {
    int y_top = sqrt(radius * radius - i * i) * 0.3;
    display->drawPixel(cx + i, cy - height / 2 + y_top, SSD1306_WHITE);

    int y_bot = sqrt(radius * radius - i * i) * 0.3;
    display->drawPixel(cx + i, cy + height / 2 + y_bot, SSD1306_WHITE);
  }
}

// ============ CONE ============
void Shapes3D::drawCone(int cx, int cy, int radius, int height) {
  // Base circle
  display->drawCircle(cx, cy + height / 2, radius, SSD1306_WHITE);

  // Apex point
  int apex_x = cx;
  int apex_y = cy - height / 2;

  // Side lines (tangent to circle)
  drawLine(cx - radius, cy + height / 2, apex_x, apex_y);
  drawLine(cx + radius, cy + height / 2, apex_x, apex_y);

  // Add depth with ellipse on base
  for (int i = -radius; i <= radius; i++) {
    int y = sqrt(radius * radius - i * i) * 0.3;
    display->drawPixel(cx + i, cy + height / 2 + y, SSD1306_WHITE);
  }
}

// ============ RECTANGULAR PRISM ============
void Shapes3D::drawRectangularPrism(int cx, int cy, int w, int h, int d) {
  int hw = w / 2;
  int hh = h / 2;

  // Front face
  display->drawRect(cx - hw, cy - hh, w, h, SSD1306_WHITE);

  // Top face (isometric)
  int offset_x = d / 3;
  int offset_y = -d / 4;

  drawLine(cx - hw, cy - hh, cx - hw + offset_x, cy - hh + offset_y);
  drawLine(cx + hw, cy - hh, cx + hw + offset_x, cy - hh + offset_y);
  drawLine(cx + hw + offset_x, cy - hh + offset_y, cx - hw + offset_x,
           cy - hh + offset_y);

  // Right face
  drawLine(cx + hw, cy - hh, cx + hw + offset_x, cy - hh + offset_y);
  drawLine(cx + hw, cy + hh, cx + hw + offset_x, cy + hh + offset_y);
  drawLine(cx + hw + offset_x, cy - hh + offset_y, cx + hw + offset_x,
           cy + hh + offset_y);
}

// ============ 2D SHAPES ============
void Shapes3D::drawSquare(int cx, int cy, int size) {
  display->drawRect(cx - size / 2, cy - size / 2, size, size, SSD1306_WHITE);
}

void Shapes3D::drawCircle2D(int cx, int cy, int radius) {
  display->drawCircle(cx, cy, radius, SSD1306_WHITE);
}

// ============ ROTATING CUBE ============
void Shapes3D::drawRotatingCube(int cx, int cy, int size, float angle) {
  // 8 vertices of cube
  float vertices[8][3] = {
      {-1, -1, -1}, {1, -1, -1}, {1, 1, -1}, {-1, 1, -1}, // Front
      {-1, -1, 1},  {1, -1, 1},  {1, 1, 1},  {-1, 1, 1}   // Back
  };

  // Scale
  float s = size / 2.0;

  // Rotate and project
  int projected[8][2];
  for (int i = 0; i < 8; i++) {
    float x = vertices[i][0] * s;
    float y = vertices[i][1] * s;
    float z = vertices[i][2] * s;

    // Rotate around Y axis
    rotateY(&x, &z, angle);

    // Simple perspective projection
    float scale = 200.0 / (200.0 + z);
    projected[i][0] = cx + (int)(x * scale);
    projected[i][1] = cy + (int)(y * scale);
  }

  // Draw edges
  int edges[12][2] = {
      {0, 1}, {1, 2}, {2, 3}, {3, 0}, // Front face
      {4, 5}, {5, 6}, {6, 7}, {7, 4}, // Back face
      {0, 4}, {1, 5}, {2, 6}, {3, 7}  // Connecting edges
  };

  for (int i = 0; i < 12; i++) {
    int v1 = edges[i][0];
    int v2 = edges[i][1];
    drawLine(projected[v1][0], projected[v1][1], projected[v2][0],
             projected[v2][1]);
  }
}

// ============ ROTATING PYRAMID ============
void Shapes3D::drawRotatingPyramid(int cx, int cy, int size, float angle) {
  // 5 vertices (4 base + 1 apex)
  float vertices[5][3] = {
      {-1, 1, -1},
      {1, 1, -1},
      {1, 1, 1},
      {-1, 1, 1}, // Base
      {0, -1, 0}  // Apex
  };

  float s = size / 2.0;
  int projected[5][2];

  for (int i = 0; i < 5; i++) {
    float x = vertices[i][0] * s;
    float y = vertices[i][1] * s;
    float z = vertices[i][2] * s;

    rotateY(&x, &z, angle);

    float scale = 200.0 / (200.0 + z);
    projected[i][0] = cx + (int)(x * scale);
    projected[i][1] = cy + (int)(y * scale);
  }

  // Draw edges
  int edges[8][2] = {
      {0, 1}, {1, 2}, {2, 3}, {3, 0}, // Base
      {0, 4}, {1, 4}, {2, 4}, {3, 4}  // To apex
  };

  for (int i = 0; i < 8; i++) {
    int v1 = edges[i][0];
    int v2 = edges[i][1];
    drawLine(projected[v1][0], projected[v1][1], projected[v2][0],
             projected[v2][1]);
  }
}

// ============ MOLECULES ============
void Shapes3D::drawWaterMolecule() {
  display->clearDisplay();

  // H2O
  int centerX = 64, centerY = 32;

  // Oxygen (large circle)
  display->fillCircle(centerX, centerY, 8, SSD1306_WHITE);
  display->setCursor(centerX - 3, centerY - 3);
  display->print("O");

  // Hydrogen 1 (left)
  display->fillCircle(centerX - 20, centerY - 10, 5, SSD1306_WHITE);
  display->setCursor(centerX - 22, centerY - 12);
  display->setTextColor(SSD1306_BLACK);
  display->print("H");
  display->setTextColor(SSD1306_WHITE);

  // Hydrogen 2 (right)
  display->fillCircle(centerX + 20, centerY - 10, 5, SSD1306_WHITE);
  display->setCursor(centerX + 18, centerY - 12);
  display->setTextColor(SSD1306_BLACK);
  display->print("H");
  display->setTextColor(SSD1306_WHITE);

  // Bonds
  drawLine(centerX - 6, centerY - 4, centerX - 15, centerY - 8);
  drawLine(centerX + 6, centerY - 4, centerX + 15, centerY - 8);

  // Label
  display->setCursor(40, 0);
  display->print("H2O - Nuoc");

  display->display();
}

void Shapes3D::drawCO2Molecule() {
  display->clearDisplay();

  // CO2: O=C=O
  int centerX = 64, centerY = 32;

  // Carbon (center)
  display->fillCircle(centerX, centerY, 6, SSD1306_WHITE);
  display->setCursor(centerX - 3, centerY - 3);
  display->setTextColor(SSD1306_BLACK);
  display->print("C");
  display->setTextColor(SSD1306_WHITE);

  // Oxygen 1 (left)
  display->fillCircle(centerX - 25, centerY, 7, SSD1306_WHITE);
  display->setCursor(centerX - 27, centerY - 3);
  display->setTextColor(SSD1306_BLACK);
  display->print("O");
  display->setTextColor(SSD1306_WHITE);

  // Oxygen 2 (right)
  display->fillCircle(centerX + 25, centerY, 7, SSD1306_WHITE);
  display->setCursor(centerX + 23, centerY - 3);
  display->setTextColor(SSD1306_BLACK);
  display->print("O");
  display->setTextColor(SSD1306_WHITE);

  // Double bonds
  drawLine(centerX - 6, centerY - 2, centerX - 18, centerY - 2);
  drawLine(centerX - 6, centerY + 2, centerX - 18, centerY + 2);
  drawLine(centerX + 6, centerY - 2, centerX + 18, centerY - 2);
  drawLine(centerX + 6, centerY + 2, centerX + 18, centerY + 2);

  // Label
  display->setCursor(30, 0);
  display->print("CO2 - Cacbon");

  display->display();
}

void Shapes3D::drawMethaneMolecule() {
  display->clearDisplay();

  // CH4 - tetrahedral
  int centerX = 64, centerY = 32;

  // Carbon (center)
  display->fillCircle(centerX, centerY, 6, SSD1306_WHITE);
  display->setCursor(centerX - 3, centerY - 3);
  display->setTextColor(SSD1306_BLACK);
  display->print("C");
  display->setTextColor(SSD1306_WHITE);

  // 4 Hydrogens (tetrahedral layout)
  int h_positions[4][2] = {{centerX - 18, centerY - 15},
                           {centerX + 18, centerY - 15},
                           {centerX - 18, centerY + 15},
                           {centerX + 18, centerY + 15}};

  for (int i = 0; i < 4; i++) {
    display->fillCircle(h_positions[i][0], h_positions[i][1], 4, SSD1306_WHITE);
    display->setCursor(h_positions[i][0] - 2, h_positions[i][1] - 2);
    display->setTextColor(SSD1306_BLACK);
    display->print("H");
    display->setTextColor(SSD1306_WHITE);

    // Bond
    drawLine(centerX, centerY, h_positions[i][0], h_positions[i][1]);
  }

  // Label
  display->setCursor(30, 0);
  display->print("CH4 - Metan");

  display->display();
}

// ============ COORDINATE SYSTEM ============
void Shapes3D::drawCoordinateSystem() {
  display->clearDisplay();

  int cx = 64, cy = 32;
  int size = 25;

  // X axis (red in concept, white here)
  drawLine(cx, cy, cx + size, cy);
  display->setCursor(cx + size + 2, cy - 3);
  display->print("X");

  // Y axis
  drawLine(cx, cy, cx, cy - size);
  display->setCursor(cx - 3, cy - size - 8);
  display->print("Y");

  // Z axis (isometric)
  drawLine(cx, cy, cx - size / 2, cy + size / 2);
  display->setCursor(cx - size / 2 - 8, cy + size / 2 + 2);
  display->print("Z");

  // Origin
  display->fillCircle(cx, cy, 2, SSD1306_WHITE);
  display->setCursor(cx + 3, cy + 3);
  display->print("O");

  display->display();
}

// ============ SHOW SHAPE WITH LABEL ============
void Shapes3D::showShape(const char *shapeName, const char *shapeType) {
  display->clearDisplay();

  // Title
  display->setTextSize(1);
  display->setCursor(0, 0);
  display->print(shapeName);
  display->drawLine(0, 10, 128, 10, SSD1306_WHITE);

  // Draw shape based on type
  if (strcmp(shapeType, "cube") == 0) {
    drawCube(64, 40, 30);
  } else if (strcmp(shapeType, "pyramid") == 0) {
    drawPyramid(64, 42, 28);
  } else if (strcmp(shapeType, "sphere") == 0) {
    drawSphere(64, 40, 18);
  } else if (strcmp(shapeType, "cylinder") == 0) {
    drawCylinder(64, 40, 15, 30);
  } else if (strcmp(shapeType, "cone") == 0) {
    drawCone(64, 40, 18, 30);
  } else if (strcmp(shapeType, "square") == 0) {
    drawSquare(64, 32, 40);
  } else if (strcmp(shapeType, "circle") == 0) {
    drawCircle2D(64, 32, 25);
  }

  display->display();
}
