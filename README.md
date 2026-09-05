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

---

## 🛠️ The Ultimate Deployment Guide

Deploying NanoNAS is incredibly easy. You can choose the **Automated Setup** (recommended) which handles everything for you, or the **Manual Setup** if you prefer complete control over your environment.

### 🌟 Automated Setup (Recommended)
Our cross-platform Python script (`setup.py`) acts as a smart installation wizard. It will interactively ask you for your WiFi credentials, generate your security files, and automatically download and install `arduino-cli`, `esptool`, and all necessary C++ libraries!

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```
2. **Run the interactive setup wizard:**
   ```bash
   python setup.py
   ```
3. Follow the on-screen prompts. That's it! You are ready to flash!

### 🔧 Manual Setup (Step-by-Step)
If you prefer to configure the NAS manually, follow the platform-specific instructions below.

#### Step 1: Clone the Repository
```bash
git clone https://github.com/pdev-labs/NanoNAS-S3.git
cd NanoNAS-S3
```

#### Step 2: Install `arduino-cli` and `esptool`
<details>
<summary><b>🐧 Linux (Ubuntu/Debian/Arch)</b></summary>

1. **Install Python dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3-pip python3-serial curl
   # Arch Linux
   sudo pacman -S python-pip python-pyserial curl
   ```
2. **Install esptool:**
   ```bash
   pip install esptool
   ```
3. **Install arduino-cli:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
   sudo mv bin/arduino-cli /usr/local/bin/
   ```
</details>

<details>
<summary><b>🪟 Windows</b></summary>

1. Ensure **Python** is installed and added to your system PATH.
2. **Install esptool:**
   Open Command Prompt or PowerShell as Administrator and run:
   ```cmd
   pip install esptool
   ```
3. **Install arduino-cli:**
   Download the latest Windows MSI installer from the [official Arduino CLI page](https://arduino.github.io/arduino-cli/latest/installation/). Run the installer and ensure you check the box to **Add to PATH**.
</details>

<details>
<summary><b>🍏 macOS</b></summary>

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install dependencies:**
   ```bash
   brew install python arduino-cli
   pip3 install esptool
   ```
</details>

<details>
<summary><b>📱 Android (Termux)</b></summary>

1. **Install dependencies:**
   ```bash
   pkg update && pkg upgrade
   pkg install python clang make git
   ```
2. **For Non-Rooted Devices:**
   Standard `esptool.py` cannot access USB devices on non-rooted Androids due to OS security policies. However, you have two options:
   
   **Option A: The OTA Method (Recommended)**
   - Run `python setup.py` to configure your credentials.
   - Run `python build_bin.py` to compile your `.bin` file inside Termux.
   - Open your Android browser, log in to your NanoNAS dashboard, and upload the generated `.bin` file via the **Firmware Update (OTA)** panel! No USB cables required!

   **Option B: The TCP Bridge Method (USB Flashing)**
   You can bypass the USB restriction by routing the USB serial connection through a local TCP socket using a companion app:
   - Download a TCP-to-UART bridge app from the Play Store (e.g., "TCPUART" or "Serial to TCP bridge").
   - Connect your ESP32 via USB OTG and grant the app USB permissions.
   - Start the TCP server in the app (e.g., on port 8080).
   - In Termux, you can now flash the board by passing the TCP port to `esptool` using RFC2217:
     ```bash
     esptool.py -p socket://127.0.0.1:8080 write_flash 0x0 build/your_sketch.bin
     ```

3. **For Rooted Devices (Direct USB Flashing):**
   If you are rooted and want to flash via a USB OTG cable directly from Termux:
   ```bash
   pkg install tsu
   pip install esptool pyserial
   ```
   *Note: You must have Termux USB API permissions enabled, and you will need to run the flash scripts as root (`tsu`) to allow `esptool` access to `/dev/bus/usb`.*
</details>

#### Step 3: Install Required C++ Libraries
Once `arduino-cli` is installed on your system, install the ESP32 core and required libraries:
```bash
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli lib install "ArduinoJson" "Adafruit NeoPixel" "EspUsbHost"
```
*(Note: You will also need to manually clone or install `ESPAsyncWebServer` and `AsyncTCP` into your Arduino libraries folder).*

#### Step 4: Configure Credentials securely
1. Rename the `secrets.h.example` file to `secrets.h`.
2. Open `secrets.h` and input your actual WiFi SSID and Password, along with your desired Admin credentials:
   ```c
   #define SECRET_WIFI_SSID "YourWiFiNetwork"
   #define SECRET_WIFI_PASSWORD "YourPassword123"
   #define SECRET_ADMIN_USERNAME "admin"
   #define SECRET_ADMIN_PASSWORD "admin123"
   ```
*(Git will automatically ignore `secrets.h` so your real password will NEVER be uploaded to GitHub!)*

---

## 🚀 The Python Utilities (Cross-Platform)

We have engineered five incredibly powerful, fully **cross-platform** utility scripts. They auto-detect your OS and magically run flawlessly on all platforms!

### 1. The Interactive Setup Wizard (`setup.py`)
Automatically downloads toolchains, configures your WiFi, and sets up your environment in 60 seconds.
```bash
python setup.py
```

### 2. The Universal Builder (`build_bin.py`)
A smart compiler that auto-detects your attached Arduino board via `arduino-cli`, extracts its FQBN, and generates a `.bin` file perfectly formatted for OTA updates!
```bash
python build_bin.py
```

### 3. The Auto-Flasher (`flasher.py`)
A blazing-fast deployment script that automatically stages your files, utilizes the `arduino-cli` build cache, and auto-detects your COM/TTY ports.
```bash
python flasher.py
```
After successfully flashing, it will automatically launch a high-speed Serial Monitor so you can instantly view your boot logs and IP addresses.

### 4. The Diagnostics Tool (`info.py`)
The ultimate hardware and software deep-dive interrogator!
```bash
python info.py
```
Extracts and renders beautiful ASCII tables containing Hardware Specs, Security Posture, and dynamically unpacked Firmware Intel.

### 5. The Nuclear Reset (`erase.py`)
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
- Added **Interactive Setup Script** (`setup.py`) for automated cross-platform deployments.
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

## 📜 License
This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE` file for details.
