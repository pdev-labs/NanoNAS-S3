# NanoNAS 🚀

**NanoNAS** is an ultra-lightweight, premium, dual-mode Network Attached Storage (NAS) system designed exclusively for the **ESP32-S3** microcontroller. 

It provides a beautiful, modern, glassmorphism web dashboard for managing, streaming, and uploading files from external USB OTG mass storage devices (FAT16/FAT32).

![NanoNAS Dashboard Screenshot](screenshot.png) *(Add a screenshot here!)*

## 🌟 Features
- **USB OTG Mass Storage:** Plug in any FAT32 USB Pendrive to share Gigabytes of storage! (Requires an OTG Y-Cable or external 5V power to the USB device).
- **Dual-Mode Networking:** Connects to your home WiFi. If the connection drops or is unavailable, it automatically broadcasts its own Hotspot (Access Point)!
- **System Analytics Dashboard:** View live telemetry of your ESP32-S3's Heap, PSRAM usage, Uptime, and WiFi Signal Strength!
- **Zero-Config mDNS:** No need to type IP addresses! Just go to `http://nanonas.local` in your browser.
- **In-Browser Media Streaming:** Instantly stream videos and music directly from your NAS to your browser without downloading!
- **Heavenly RGB Fade:** A dedicated FreeRTOS background task on Core 0 that flawlessly breathes a glacier-paced 65K color rainbow on your board's NeoPixel, all without interrupting the web server! 
- **Premium UI:** A stunning, mobile-responsive dashboard with dark glassmorphism styling.
- **Admin Authentication:** Secure your files! Requires a login (Default: `admin` / `admin`).
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

We have engineered three incredibly powerful, fully **cross-platform** utility scripts (`flasher.py`, `erase.py`, `info.py`). They are designed to auto-detect your OS and magically run flawlessly on **Windows, macOS, Linux, and Android (Termux)**!

Make sure you have `esptool` installed globally (`pip install esptool`).

### 1. The Auto-Flasher (`flasher.py`)
A blazing-fast deployment script that automatically stages your files, utilizes the `arduino-cli` build cache, and auto-detects your COM/TTY ports. No Arduino IDE required!

**To use:**
```bash
python flasher.py
```
- Just type the path to your `.ino` file and hit `Tab` for auto-completion!
- After successfully flashing, it will automatically launch a high-speed Serial Monitor so you can instantly view your boot logs and IP addresses.

### 2. The Diagnostics Tool (`info.py`)
The ultimate hardware and software deep-dive interrogator! 

**To use:**
```bash
python info.py
```
It extracts and renders beautiful ASCII tables containing:
- **Hardware & Flash Specs:** ESP32 chip type, features, crystal freq, and PSRAM/Flash dimensions.
- **Security Posture:** Secure Boot and Flash Encryption status.
- **Firmware Intel:** Dynamically unpacks the raw `.bin` partition on your chip to extract the Project Name, Compile Time, Date, and ESP-IDF version of your currently running code!

### 3. The Nuclear Reset (`erase.py`)
If your ESP32-S3 gets stuck in a boot loop or the partition table gets corrupted, this script rescues it.

**To use:**
```bash
python erase.py
```
It gives you an interactive menu:
- **Option 1 (Normal Erase):** Formats the flash memory using `esptool`.
- **Option 2 (Factory Reset):** Not only erases the memory, but compiles and flashes a dummy bootloader directly to the chip to restore completely ruined partition tables.

---

## 🌍 Platform Specific Notes

Because of our cross-platform architecture, the scripts run identically everywhere, but here are some quick dependency tips for different OSs:

- **Linux (Arch/Ubuntu):** You may need to run `sudo pacman -S python-pyserial` or `sudo apt install python3-serial` for the Auto-Serial Monitor to function.
- **Windows:** Ensure Python is added to your PATH during installation. The script will automatically scan your `COMx` ports.
- **macOS:** You might need to install `esptool` via brew or pip. The script automatically handles macOS `/dev/cu.*` port nomenclature.
- **Android (Termux):** You must have `termux-usb` permissions enabled, and you may need to run the scripts as root (`tsu`) depending on your device's USB OTG permission layers to allow `esptool` access to `/dev/bus/usb`.

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for details.
