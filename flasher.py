#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("========================================")
    print(" ESP32-S3 Auto-Flasher Script")
    print("========================================")
    
    # Ask for the file path
    file_path = input("Enter the full path of the file to flash (.ino or .bin): ").strip()
    
    # Strip quotes if the user dragged and dropped the file into the terminal
    if file_path.startswith("'") and file_path.endswith("'"):
        file_path = file_path[1:-1]
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]
        
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
        
    ext = os.path.splitext(file_path)[1].lower()
    port = "/dev/ttyACM0" # Default port for ESP32-S3 native USB
    
    if ext == ".ino":
        print(f"\n[INFO] Detected an Arduino sketch (.ino).")
        print(f"[INFO] This will compile and flash using arduino-cli to {port}...\n")
        
        # Compile
        compile_cmd = ["arduino-cli", "compile", "--fqbn", "esp32:esp32:esp32s3", file_path]
        print(f"Running: {' '.join(compile_cmd)}")
        result = subprocess.run(compile_cmd)
        if result.returncode != 0:
            print("\n[ERROR] Compilation failed!")
            sys.exit(1)
            
        # Upload
        upload_cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", "esp32:esp32:esp32s3", file_path]
        print(f"\nRunning: {' '.join(upload_cmd)}")
        result = subprocess.run(upload_cmd)
        if result.returncode == 0:
            print("\n[SUCCESS] Sketch successfully flashed to the ESP32-S3!")
        else:
            print("\n[ERROR] Flashing failed!")
            
    elif ext == ".bin":
        print(f"\n[INFO] Detected a compiled binary (.bin).")
        print(f"[INFO] This will flash the app partition using esptool to {port}...\n")
        
        # Flash using esptool at 0x10000 (standard app partition offset)
        esptool_cmd = [
            "esptool.py",
            "--chip", "esp32s3",
            "--port", port,
            "--baud", "921600",
            "--before", "default_reset",
            "--after", "hard_reset",
            "write_flash",
            "-z",
            "--flash_mode", "dio",
            "--flash_freq", "80m",
            "--flash_size", "detect",
            "0x10000", file_path
        ]
        
        print(f"Running: {' '.join(esptool_cmd)}")
        result = subprocess.run(esptool_cmd)
        
        if result.returncode == 0:
            print("\n[SUCCESS] Binary successfully flashed to the ESP32-S3!")
        else:
            print("\n[ERROR] Flashing failed. Please check if the port is correct and the board is plugged in.")
    else:
        print(f"\n[ERROR] Unsupported file extension: {ext}. Please provide a .ino or .bin file.")

if __name__ == "__main__":
    main()
