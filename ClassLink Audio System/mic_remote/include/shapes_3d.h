#ifndef SHAPES_3D_H
#define SHAPES_3D_H

#include <Adafruit_SSD1306.h>

/**
 * 3D Shapes Visualization Library
 * Draws geometric shapes using isometric projection on OLED
 * Perfect for educational AR glasses!
 */

class Shapes3D {
private:
  Adafruit_SSD1306 *display;

  // Helper: Draw line with clipping
  void drawLine(int x0, int y0, int x1, int y1);

  // Helper: Rotate point around axis
  void rotateY(float *x, float *z, float angle);

public:
  Shapes3D(Adafruit_SSD1306 *disp);

  // Basic 3D shapes (static - no animation)
  void drawCube(int centerX, int centerY, int size);
  void drawPyramid(int centerX, int centerY, int size);
  void drawSphere(int centerX, int centerY, int radius);
  void drawCylinder(int centerX, int centerY, int radius, int height);
  void drawCone(int centerX, int centerY, int radius, int height);
  void drawRectangularPrism(int centerX, int centerY, int w, int h, int d);

  // Basic 2D shapes
  void drawSquare(int centerX, int centerY, int size);
  void drawCircle2D(int centerX, int centerY, int radius);

  // Animated rotating shapes
  void drawRotatingCube(int centerX, int centerY, int size, float angle);
  void drawRotatingPyramid(int centerX, int centerY, int size, float angle);

  // Chemistry molecules (simple)
  void drawWaterMolecule();   // H2O
  void drawCO2Molecule();     // CO2
  void drawMethaneMolecule(); // CH4

  // Math diagrams
  void drawCoordinateSystem(); // 3D coordinate axes
  void drawAngle(int degrees); // Show angle measurement

  // Helper: Show shape with label
  void showShape(const char *shapeName, const char *shapeType);
};

#endif
