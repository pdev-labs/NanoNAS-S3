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
  // Use a 16-bit hue value (0 to 65535) for ultra-smooth 65K color resolution!
  // This provides incredibly smooth gradients and millions of more intermediate colors.
  // We increment by a small step of 10 to move through the wheel smoothly.
  for(long firstPixelHue = 0; firstPixelHue < 65536; firstPixelHue += 10) {
    for(int i = 0; i < NUMPIXELS; i++) {
      // ColorHSV takes a 16-bit hue (0-65535), 8-bit saturation (0-255), and 8-bit value (0-255)
      // gamma32 makes the colors appear linearly smooth to the human eye
      uint32_t color = pixels.gamma32(pixels.ColorHSV(firstPixelHue, 255, 255));
      pixels.setPixelColor(i, color);
    }
    pixels.show();
    
    // Very short delay for silky smooth 500+ FPS fading
    delay(2); 
  }
}
