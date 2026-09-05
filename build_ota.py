import os
import subprocess
import sys

def main():
    print("========================================")
    print("   ESP32-S3 OTA Binary Builder")
    print("========================================")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    if not current_dir:
        current_dir = os.getcwd()
        
    print(f"[INFO] Compiling sketch in '{current_dir}'...")
    
    cmd = [
        "arduino-cli", 
        "compile", 
        "-e", 
        "--fqbn", 
        "esp32:esp32:esp32s3", 
        current_dir
    ]
    
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            bin_path = os.path.join(current_dir, "build", "esp32.esp32.esp32s3", "esp32-s3-server.ino.bin")
            print("")
            print("[SUCCESS] Compilation finished successfully!")
            print("[INFO] You can now upload this binary via the NanoNAS Web UI:")
            print(f"  -> {bin_path}")
        else:
            print("")
            print("[ERROR] Compilation failed. Please check the logs above.")
            sys.exit(result.returncode)
    except FileNotFoundError:
        print("")
        print("[ERROR] 'arduino-cli' is not installed or not in your system's PATH.")
        print("Please install arduino-cli to build the project.")
        sys.exit(1)

if __name__ == "__main__":
    main()
