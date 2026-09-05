# NanoNAS 🚀

**NanoNAS** is an ultra-lightweight, premium, dual-mode Network Attached Storage (NAS) system designed exclusively for the **ESP32-S3** microcontroller.

It provides a beautiful, modern, glassmorphism web dashboard for managing, streaming, and uploading files from external USB OTG mass storage devices (FAT16/FAT32).

![NanoNAS Dashboard Screenshot](screenshot.png) *(Add a screenshot here!)*

## 🌟 Features
- **USB OTG Mass Storage:** Plug in any FAT32 USB Pendrive to share Gigabytes of storage! (Requires an OTG Y-Cable or external 5V power to the USB device).
- **Dual-Mode Networking:** Connects to your home WiFi. If the connection drops or is unavailable, it automatically broadcasts its own Hotspot (Access Point)!
- **System Analytics Dashboard:** View live telemetry of your ESP32-S3's Heap, PSRAM usage, Uptime, and WiFi Signal Strength!
- **Zero-Config mDNS:** No need to type IP addresses! Just go to `http://nanonas.local` in your browser.
- **In-Browser Media & Markdown Streaming:** Instantly stream videos, audio, images, and beautifully rendered Markdown (`.md`) files directly in your browser without downloading!
- **Intelligent Drag & Drop Uploads:** Effortlessly upload files by dragging them into the UI. Includes smart collision detection (Skip, Rename, Replace) for duplicate files.
- **Wireless OTA Firmware Updates:** Seamlessly flash new firmware over the air directly from the web dashboard. No USB cables required!
- **Premium UI & Multi-User Auth:** A stunning, mobile-responsive dark glassmorphism dashboard protected by role-based user authentication (Default Admin: `admin` / `admin123`).
- **Dynamic RGB Indicators:** A dedicated FreeRTOS background task featuring an Apple-style exponential sine wave breathing effect. Colors intelligently shift based on system state:
  - 🔵 **Breathing Blue:** Idle (Connected to WiFi)
  - 💧 **Breathing Cyan:** Idle (Hosting AP Hotspot)
  - 🟢 **Pulsing Green:** Reading / Streaming Files
  - 🟠 **Pulsing Orange:** Writing / Uploading Files
  - 🟣 **Strobing Purple:** Receiving OTA Update
  - 🔴 **Blinking Red:** System Error
- **Secure Credentials Management:** WiFi secrets are kept safely in a `.gitignore`d file so you never accidentally push your password to GitHub!

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

---

## 🔒 Configuration & Security Setup

Before flashing, you must set up your WiFi credentials securely!

1. Rename the `secrets.h.example` file in the root directory to `secrets.h`.
2. Open `secrets.h` in any text editor and input your actual WiFi SSID and Password:
   ```c
   #define SECRET_WIFI_SSID "YourWiFiNetwork"
   #define SECRET_WIFI_PASSWORD "YourPassword123"
   ```
3. Because `secrets.h` is in `.gitignore`, Git will automatically ignore this file. Your real password will NEVER be uploaded to GitHub!

---

## 🚀 The Ultimate Python Utilities Guide (Cross-Platform)

We have engineered four incredibly powerful, fully **cross-platform** utility scripts (`build_bin.py`, `flasher.py`, `erase.py`, `info.py`). They are designed to auto-detect your OS and magically run flawlessly on **Windows, macOS, Linux, and Android (Termux)**!

### 1. The Universal Builder (`build_bin.py`)
A smart compiler that auto-detects your attached Arduino board via `arduino-cli`, extracts its FQBN, and generates a `.bin` file perfectly formatted for OTA updates!
```bash
python build_bin.py
```

### 2. The Auto-Flasher (`flasher.py`)
A blazing-fast deployment script that automatically stages your files, utilizes the `arduino-cli` build cache, and auto-detects your COM/TTY ports. No Arduino IDE required!
```bash
python flasher.py
```
- Just type the path to your `.ino` file and hit `Tab` for auto-completion!
- After successfully flashing, it will automatically launch a high-speed Serial Monitor so you can instantly view your boot logs and IP addresses.

### 3. The Diagnostics Tool (`info.py`)
The ultimate hardware and software deep-dive interrogator!
```bash
python info.py
```
Extracts and renders beautiful ASCII tables containing Hardware Specs, Security Posture, and dynamically unpacked Firmware Intel.

### 4. The Nuclear Reset (`erase.py`)
If your ESP32-S3 gets stuck in a boot loop or the partition table gets corrupted, this script rescues it by erasing the flash or pushing a dummy bootloader.
```bash
python erase.py
```

---

## 📦 Releases & Version History

**v1.2.0 - The Pro Update (Latest)**
- Added **Wireless OTA Firmware Updates** via the Web Dashboard.
- Implemented **In-Browser Markdown Viewer** utilizing `marked.js`.
- Implemented **Intelligent Drag & Drop Uploads** with collision detection (Skip/Rename/Replace).
- Re-engineered the RGB NeoPixel to feature **Apple-style exponential sine wave breathing** with dynamic state-based color mapping (Blue/Cyan/Green/Orange/Purple/Red).
- Introduced **Universal Builder Script** (`build_bin.py`) for automatic FQBN detection.
- Allowed admins to change their username/password for higher security.

**v1.1.0 - Media & Auth Update**
- Built **In-Browser Media Player** natively supporting `.mp4`, `.webm`, `.mp3`, and `.wav` streaming directly from the NAS!
- Implemented Multi-User Role-based Authentication (Admin vs Standard Users).
- Polished the Material You Glassmorphism UI.

**v1.0.0 - Initial Release**
- Core USB OTG File Manager features (Upload, Download, Delete, Rename).
- Dual-Mode WiFi Networking (STA / AP Fallback).
- mDNS support and system analytics integration.
- Hardware-accelerated RGB FreeRTOS background task.

---

## 🌍 Platform Specific Notes

Because of our cross-platform architecture, the scripts run identically everywhere, but here are some quick dependency tips for different OSs:

- **Linux (Arch/Ubuntu):** You may need to run `sudo pacman -S python-pyserial` or `sudo apt install python3-serial` for the Auto-Serial Monitor to function.
- **Windows:** Ensure Python is added to your PATH during installation. The script will automatically scan your `COMx` ports.
- **macOS:** You might need to install `esptool` via brew or pip. The script automatically handles macOS `/dev/cu.*` port nomenclature.

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for details.
