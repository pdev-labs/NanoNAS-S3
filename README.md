# NanoNAS-S3 🚀

Transform your **ESP32-S3** into a tiny, high-performance Network Attached Storage (NAS) device! 

NanoNAS-S3 connects to your Wi-Fi, mounts a massive USB Pendrive or Hard Drive via USB-OTG, and serves an incredibly snappy web interface to manage your files. Built to bypass standard microcontroller limits, it leverages asynchronous processing and chunked uploading to handle massive multi-gigabyte files effortlessly.

## ✨ Features

- **Asynchronous Web Server**: Powered by `ESPAsyncWebServer`, it handles multiple concurrent connections without blocking, ensuring maximum throughput and zero freezing.
- **Infinite File Sizes (Chunked Uploads)**: Don't let your browser crash! The embedded JavaScript frontend automatically slices massive files (like 10GB movies) into 4MB chunks and streams them to the ESP32. If your Wi-Fi drops, it automatically retries the failed chunk.
- **USB OTG Mass Storage**: Bypasses the tiny internal flash limitation by directly mounting USB drives using `EspUsbHost`.
- **Media Streaming**: Intelligently detects media files (MP4, MP3, JPG, etc.) and provides a "Stream/View" button to play them directly in the browser using HTTP Range requests.
- **Plug-and-Play UI**: The UI is embedded directly into the C++ code as a raw string. No need to mess with uploading files to SPIFFS/LittleFS just to load the frontend!

## 🛠️ Hardware Requirements
- **ESP32-S3** board with exposed USB pins (D+ / D-).
- A USB OTG adapter.
- A USB Pendrive or HDD (If using a mechanical HDD, ensure you use a powered USB hub as the ESP32 cannot provide enough spin-up current).

## 🚀 Setup & Installation (Arduino CLI)

1. **Install Dependencies**:
```bash
arduino-cli lib install ESPAsyncWebServer AsyncTCP ArduinoJson EspUsbHost
```

2. **Configure Board Settings**:
Ensure you have `CDCOnBoot=cdc` enabled if using Hardware CDC, and set PSRAM to `enabled` or `opi` if your board has it for extra buffer space.

3. **Compile and Upload**:
```bash
arduino-cli compile --fqbn esp32:esp32:esp32s3 esp32-s3-server.ino
arduino-cli upload -p /dev/ttyACM0 --fqbn esp32:esp32:esp32s3 esp32-s3-server.ino
```

## ⚠️ Notes
- Update the `ssid` and `password` variables in the `.ino` file to match your Wi-Fi credentials before compiling.
- The `EspUsbHost` library handles the USB Mass Storage mounting. Ensure your USB drive is formatted as FAT32 or exFAT.

---
*Built with cleverly optimized C++ and a whole lot of caffeine.*
