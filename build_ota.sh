#!/bin/bash
echo -e "\e[1;36m========================================\e[0m"
echo -e "\e[1;36m   ESP32-S3 OTA Binary Builder\e[0m"
echo -e "\e[1;36m========================================\e[0m"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "\e[1;33m[INFO]\e[0m Compiling sketch in '$DIR'..."

arduino-cli compile -e --fqbn esp32:esp32:esp32s3 "$DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "\e[1;32m[SUCCESS]\e[0m Compilation finished successfully!"
    echo -e "\e[1;33m[INFO]\e[0m You can now upload this binary via the NanoNAS Web UI:"
    echo -e "  -> \e[1;37m$DIR/build/esp32.esp32.esp32s3/esp32-s3-server.ino.bin\e[0m"
else
    echo ""
    echo -e "\e[1;31m[ERROR]\e[0m Compilation failed. Please check the logs above."
fi
