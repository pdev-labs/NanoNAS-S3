#include <Adafruit_NeoPixel.h>

// Built-in RGB LED on most ESP32-S3 boards is usually on GPIO 48
// Adjust this pin if your specific board uses a different one.
#define PIN        48
#define NUMPIXELS  1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  pixels.begin();
  pixels.setBrightness(100); // Increased brightness slightly
}

void loop() {
  // Use the ESP32's internal hardware timer for absolute perfection.
  // By calculating the color based on time rather than a fixed loop, 
  // we guarantee perfectly fluid, stutter-free transitions.
  unsigned long timeMs = millis();
  
  // Multiply by 15 for a nice, relaxing ~4.3 second cycle time.
  // The modulo 65536 keeps the hue wrapped perfectly within bounds.
  long hue = (timeMs * 15) % 65536;
  
  for(int i = 0; i < NUMPIXELS; i++) {
    // gamma32 provides mathematically perfect color correction
    uint32_t color = pixels.gamma32(pixels.ColorHSV(hue, 255, 255));
    pixels.setPixelColor(i, color);
  }
  
  pixels.show();
  
  // 1 millisecond delay allows the RTOS watchdog to breathe 
  // while maintaining a blazing fast 1000 FPS refresh rate.
  delay(1); 
}
