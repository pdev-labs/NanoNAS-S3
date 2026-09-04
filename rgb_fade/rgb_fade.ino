#include <Adafruit_NeoPixel.h>

// Built-in RGB LED on most ESP32-S3 boards is usually on GPIO 48
// Adjust this pin if your specific board uses a different one.
#define PIN        48
#define NUMPIXELS  1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.setBrightness(50); // Set brightness to 50 (max is 255) to not blind you
}

// Helper to convert HSV to RGB for a smooth rainbow fade
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if(WheelPos < 85) {
    return pixels.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  }
  if(WheelPos < 170) {
    WheelPos -= 85;
    return pixels.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
  WheelPos -= 170;
  return pixels.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
}

void loop() {
  // Smoothly cycle through all colors in the color wheel
  for(int j=0; j<256; j++) {
    for(int i=0; i<NUMPIXELS; i++) {
      pixels.setPixelColor(i, Wheel((i * 1 + j) & 255));
    }
    pixels.show();
    delay(20); // Adjust this delay to make the fade faster or slower
  }
}
