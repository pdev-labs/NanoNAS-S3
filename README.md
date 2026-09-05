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

## 🛠️ The Ultimate Beginner's Deployment Guide

Don't know how to code? Never used a terminal before? **No problem!** 
We have designed NanoNAS to be so incredibly easy to install that a 5-year-old could do it. Just follow these exact baby steps!

### 🌟 Automated Setup (The "One-Click" Magic)
Our smart robot script (`setup.py`) handles 99% of the hard work for you. It will download the tools, configure your WiFi, and get everything ready.

#### Step 1: Open your Terminal (Command Prompt)
- **Windows:** Click the Start menu, type `cmd`, and press Enter.
- **Mac:** Press `Command + Space`, type `Terminal`, and press Enter.
- **Linux:** Press `Ctrl + Alt + T`.
- **Android:** Download the app `Termux` from F-Droid, open it, and type `pkg install git python` then press Enter.

#### Step 2: Download (Clone) the Code
In your terminal window, carefully type (or copy-paste) this exact command and press Enter:
```bash
git clone https://github.com/pdev-labs/NanoNAS-S3.git
```
*This downloads the NanoNAS code from the internet directly to your computer!*

#### Step 3: Go inside the NanoNAS folder
Now, tell your terminal to go inside the folder it just downloaded by typing this and pressing Enter:
```bash
cd NanoNAS-S3
```

#### Step 4: Run the Magic Setup Wizard!
Now for the fun part! Type this command and press Enter:
```bash
python setup.py
```
The wizard will wake up and start talking to you! Just answer its questions:
1. It will ask if you want to install `esptool` and `arduino-cli`. **Type `y` for yes!**
2. It will ask for your **WiFi Name (SSID)** and **WiFi Password**. Type them carefully! This is how the NAS connects to your home router.
3. It will ask you to create an **Admin Username and Password**. This is your secret login to access your files later.

#### Step 5: Flash the board!
Plug your ESP32-S3 into your computer with a USB cable.
Type this final command and press Enter:
```bash
python flasher.py
```
*Boom!* You just built and installed an entire Network Attached Storage operating system!

---

### 🔧 Manual Setup (For Advanced Hackers)
If you want to install everything manually piece by piece, click on your Operating System below for the exact commands.

<details>
<summary><b>🐧 Linux (Ubuntu / Debian / Arch)</b></summary>

1. **Install Python and Git:**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3-pip python3-serial curl git
   # Arch Linux
   sudo pacman -S python-pip python-pyserial curl git
   ```
2. **Download the code:**
   ```bash
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```
3. **Install esptool (The flashing tool):**
   ```bash
   pip install esptool
   ```
4. **Install arduino-cli (The compiler):**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
   sudo mv bin/arduino-cli /usr/local/bin/
   ```
</details>

<details>
<summary><b>🪟 Windows</b></summary>

1. **Install Python & Git:**
   - Download and install [Python](https://www.python.org/downloads/). *(CRITICAL: Check the box that says "Add Python to PATH" during install!)*
   - Download and install [Git for Windows](https://git-scm.com/download/win).
2. **Download the code:**
   Open Command Prompt and type:
   ```cmd
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```
3. **Install esptool:**
   ```cmd
   pip install esptool
   ```
4. **Install arduino-cli:**
   Download the latest Windows MSI installer from the [official Arduino CLI page](https://arduino.github.io/arduino-cli/latest/installation/). Run the installer and check the box to **Add to PATH**.
</details>

<details>
<summary><b>🍏 macOS</b></summary>

1. **Install Homebrew** (The Mac App Store for nerds):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install everything else:**
   ```bash
   brew install python arduino-cli git
   pip3 install esptool
   ```
3. **Download the code:**
   ```bash
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```
</details>

<details>
<summary><b>📱 Android (Termux)</b></summary>

1. **Download Termux:** (Get it from F-Droid, NOT the Google Play Store).
2. **Install tools:**
   ```bash
   pkg update && pkg upgrade
   pkg install python clang make git
   ```
3. **Download the code:**
   ```bash
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```

4. **Flashing on Android:**
   Standard Android blocks USB access for terminals, but you have several clever options depending on what you want to achieve:

   **Option A: The Wireless OTA Method (No Root Needed - Easiest)**
   - Run `python setup.py` to configure your passwords.
   - Run `python build_bin.py` to magically compile your firmware into a `.bin` file inside Termux.
   - Open Chrome on your phone, log in to your NanoNAS dashboard, and upload the `.bin` file using the **Firmware Update (OTA)** button! No USB cables required!

   **Option B: Web Tools (No Termux Required - Easiest for pre-compiled bins)**
   If you just want to flash a pre-compiled `.bin` without automation scripts, you can completely bypass Termux by using Chrome on Android:
   - Connect your ESP chip via USB OTG.
   - Open Chrome on Android and navigate to [ESP Web Tools](https://espressif.github.io/esptool-js/).
   - Tap **Connect**, grant Chrome permission to access the USB device, and flash your firmware directly from the browser using WebUSB!
   - *Note: If Chrome fails to connect due to your phone manufacturer blocking raw serial drivers, use the [Adafruit Web Serial ESPTool](https://adafruit.github.io/Adafruit_WebSerial_ESPTool/) instead, as it includes built-in poly-fills to bypass these blocks.*

   **Option C: The TCP Bridge Method (No Root Needed - Clever)**
   - Download a "TCP-to-UART bridge" app from the Play Store (e.g., "TCPUART").
   - Plug in your ESP32 via USB OTG. The app will ask for USB permissions. Say yes!
   - Start the TCP server in the app (e.g., on port 8080).
   - In Termux, type this to flash the board through the bridge using RFC2217:
     ```bash
     esptool.py -p socket://127.0.0.1:8080 write_flash 0x0 build/your_sketch.bin
     ```

   **Option D: Specialized Terminal Apps (No Root / No TCP)**
   If you just need a command-line interface to interact with or monitor the serial output (and don't want to deal with network bridges), use apps like **Serial USB Terminal** (by Kai Morich). It handles the USB connection natively in user-space without root.

   **Option E: Direct USB Flashing (Root Required)**
   - If your phone is rooted:
     ```bash
     pkg install tsu
     pip install esptool pyserial
     ```
   - *Note: Run `tsu` first to become the root user, then you can use `flasher.py` normally!*
</details>

#### Advanced Step: Install C++ Libraries Manually
If you didn't use `setup.py`, you must install these libraries yourself:
```bash
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli lib install "ArduinoJson" "Adafruit NeoPixel" "EspUsbHost"
```

#### Advanced Step: Configure Passwords Manually
1. Rename the `secrets.h.example` file to `secrets.h`.
2. Open `secrets.h` in Notepad/TextEdit and type your WiFi Name and Password:
   ```c
   #define SECRET_WIFI_SSID "MyHomeWiFi"
   #define SECRET_WIFI_PASSWORD "MySecretPassword123"
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
