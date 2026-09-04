# NanoNAS 🚀

**NanoNAS** is an ultra-lightweight, premium, dual-mode Network Attached Storage (NAS) system designed exclusively for the **ESP32-S3** microcontroller. 

It provides a beautiful, modern, glassmorphism web dashboard for managing, streaming, and uploading files from external USB OTG mass storage devices (FAT16/FAT32).

![NanoNAS Dashboard Screenshot](screenshot.png) *(Add a screenshot here!)*

## 🌟 Features
- **USB OTG Mass Storage:** Plug in any FAT32 USB Pendrive to share Gigabytes of storage! (Requires an OTG Y-Cable or external 5V power to the USB device).
- **Dual-Mode Networking:** Connects to your home WiFi. If the connection drops or is unavailable, it automatically broadcasts its own Hotspot (Access Point)!
- **Premium UI:** A stunning, mobile-responsive dashboard with dark glassmorphism styling.
- **Admin Authentication:** Secure your files! Requires a login (Default: `admin` / `admin`).
- **File Management:** Upload, stream, delete, and create folders directly from the browser.
- **OTA Updates:** Flash new firmware wirelessly directly from the settings page!

## ⚙️ Hardware Requirements
- **ESP32-S3** (Tested on 8MB Flash variant).
- A **USB OTG Y-Cable** to inject 5V power into the USB port.
- A **FAT32** formatted USB Pendrive.

## 🛠️ Software Dependencies
Install the following libraries via the Arduino Library Manager:
- `ESPAsyncWebServer` (by me-no-dev)
- `AsyncTCP`
- `ArduinoJson`
- `EspUsbHost` (v2.7.9+)

## 🚀 Quick Start
1. Flash `esp32-s3-server.ino` to your ESP32-S3.
2. Plug in your FAT32 pendrive via a powered OTG cable to the native USB port.
3. Power the ESP32-S3.
4. Connect to the `NanoNAS` WiFi hotspot or check your router for its IP.
5. Visit the IP address in your browser and log in with `admin` / `admin`.

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for details.
