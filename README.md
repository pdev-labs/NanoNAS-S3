# NanoNAS 🚀

**NanoNAS** is an ultra-lightweight, premium, dual-mode Network Attached Storage (NAS) system designed exclusively for the **ESP32-S3** microcontroller. 

It provides a beautiful, modern, glassmorphism web dashboard for managing, streaming, and uploading files from external USB OTG mass storage devices (FAT16/FAT32).

![NanoNAS Dashboard Screenshot](screenshot.png) *(Add a screenshot here!)*

## 🌟 Features
- **USB OTG Mass Storage:** Plug in any FAT32 USB Pendrive to share Gigabytes of storage! (Requires an OTG Y-Cable or external 5V power to the USB device).
- **Dual-Mode Networking:** Connects to your home WiFi. If the connection drops or is unavailable, it automatically broadcasts its own Hotspot (Access Point)!
- **Zero-Config mDNS:** No need to type IP addresses! Just go to `http://nanonas.local` in your browser.
- **In-Browser Media Streaming:** Instantly stream videos and music directly from your NAS to your browser without downloading!
- **Heavenly RGB Fade:** A dedicated FreeRTOS background task on Core 0 that flawlessly breathes a glacier-paced 65K color rainbow on your board's NeoPixel, all without interrupting the web server! (Can be disabled via `#define ENABLE_RGB_FADE`).
- **Premium UI:** A stunning, mobile-responsive dashboard with dark glassmorphism styling.
- **Admin Authentication:** Secure your files! Requires a login (Default: `admin` / `admin`).
- **OTA Updates:** Flash new firmware wirelessly directly from the settings page!

## ⚙️ Hardware Requirements
- **ESP32-S3** (Tested on 8MB Flash variant).
- A **USB OTG Y-Cable** to inject 5V power into the USB port.
- A **FAT32** formatted USB Pendrive.

## 🛠️ Software Dependencies
Install the following libraries via `arduino-cli` or the Arduino IDE:
- `ESPAsyncWebServer` (by me-no-dev)
- `AsyncTCP`
- `ArduinoJson`
- `EspUsbHost` (v2.7.9+)
- `Adafruit NeoPixel`

## 🚀 Quick Start

**IMPORTANT:** Before flashing, open `esp32-s3-server.ino` and replace the placeholder WiFi credentials on lines 58-59 with your actual network details!

We have included a custom blazing-fast Python flasher script that automatically stages your files and utilizes the `arduino-cli` build cache. You do not need to use the Arduino IDE!

1. Connect your ESP32-S3 via USB.
2. Run the auto-flasher:
   ```bash
   python flasher.py
   ```
3. Enter the path to `esp32-s3-server.ino` when prompted.
4. Once flashed, connect to the same WiFi network (or the `NanoNAS` fallback hotspot).
5. Open your browser and navigate to `http://nanonas.local`!

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for details.
