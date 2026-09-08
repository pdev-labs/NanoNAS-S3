# NanoNAS-S3

A lightweight, high-performance Network Attached Storage (NAS) solution designed specifically for the ESP32-S3 microcontroller. It transforms your ESP32-S3 into a fully functional local wireless file server with a beautiful, modern, material-design web interface.

## Features

- **Modern Web Interface**: Responsive, Material Design UI with Dark Mode support.
- **Gallery & Grid View**: Beautiful image thumbnails and grid layout toggles.
- **Folder Uploads**: Drag and drop or upload entire nested directory structures directly from the browser.
- **Guest Access**: Role-based permission system restricts write actions for non-admin users.
- **Storage Analytics**: Colorful breakdown of used storage by file type in the System Info modal.
- **Multi-WiFi Support**: Configure multiple WiFi networks; the ESP32 will auto-connect to the strongest available network.
- **Advanced Flasher**: Built-in Python script for automatic port detection, custom 16MB partition table generation, and PSRAM (OPI/QSPI) configuration on the fly.
- **Over-The-Air (OTA) Updates**: Update the ESP32 firmware directly from the web interface.
- **Robust File Management**: Create, rename, delete, copy, cut, and paste files and folders.

## Hardware Requirements

- **ESP32-S3 Board**: Recommended 8MB PSRAM and 16MB Flash for maximum storage and performance.
- Any standard ESP32-S3 dev board will work.

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/pdev-labs/NanoNAS-S3.git
   cd NanoNAS-S3
   ```

2. **Configure Credentials:**
   Copy the example secrets file and add your WiFi credentials:
   ```bash
   cp secrets.h.example secrets.h
   ```
   Edit `secrets.h` to define your WiFi networks (`SECRET_WIFI_SSID_1`, `SECRET_WIFI_PASSWORD_1`, etc.) and the admin login for the web interface.

3. **Flash the Firmware:**
   Run the included auto-flasher script:
   ```bash
   python flasher.py
   ```
   *Follow the interactive prompts to enable PSRAM and select your Flash size (select 16MB to automatically generate the massive storage partition).*

## Usage

Once flashed, the ESP32-S3 will connect to your WiFi network and display its IP address in the Serial Monitor.
Open a web browser on any device on the same network and navigate to that IP address (e.g., `http://192.168.1.100`).

Log in using the admin credentials defined in your `secrets.h` file. 

To give access to friends or family without giving them delete/modify privileges, you can create a "guest" user from the Settings menu.

## License

This project is open-source and available under the standard MIT License.
