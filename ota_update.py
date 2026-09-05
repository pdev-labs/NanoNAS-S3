import os
import sys
import subprocess
import requests
import json
import time

CACHE_FILE = ".build_cache.json"

def main():
    print("========================================")
    print("   NanoNAS OTA Firmware Updater")
    print("========================================")

    # 1. Run the builder to compile the latest binary
    print("[INFO] Starting compilation process...")
    try:
        # Run build_bin.py interactively so the user can see it
        subprocess.run([sys.executable, "build_bin.py"], check=True)
    except subprocess.CalledProcessError:
        print("\n[ERROR] Compilation failed. OTA update aborted.")
        sys.exit(1)

    # 2. Extract cache data to find the binary path
    if not os.path.exists(CACHE_FILE):
        print("\n[ERROR] Build cache not found. Please run build_bin.py successfully first.")
        sys.exit(1)

    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            target_path = cache["target_path"]
            fqbn = cache["fqbn"]
    except Exception as e:
        print("\n[ERROR] Failed to read build cache:", e)
        sys.exit(1)

    # Reconstruct the path to the .bin file based on arduino-cli standards
    if os.path.isfile(target_path):
        build_dir = os.path.dirname(os.path.abspath(target_path))
        sketch_name = os.path.splitext(os.path.basename(target_path))[0]
    else:
        build_dir = os.path.abspath(target_path)
        sketch_name = os.path.basename(build_dir)

    fqbn_sanitized = fqbn.replace(":", ".")
    bin_file = os.path.join(build_dir, "build", fqbn_sanitized, f"{sketch_name}.ino.bin")

    if not os.path.exists(bin_file):
        print(f"\n[ERROR] Could not find the compiled binary at: {bin_file}")
        sys.exit(1)

    print(f"\n[SUCCESS] Found compiled binary at exact path:\n  -> {bin_file}")

    ans = input("\n[?] Do you want to flash this firmware to the NanoNAS now? [Y/n]: ").strip().lower()
    if ans == 'n':
        print("[INFO] OTA Flash aborted by user.")
        sys.exit(0)

    # 3. Prompt for OTA credentials
    print("\n--- OTA Configuration ---")
    ip_addr = input("Enter the NanoNAS IP or mDNS (leave blank for auto-detect 'nanonas.local'): ").strip()
    if not ip_addr:
        ip_addr = "nanonas.local"
        
    if not ip_addr.startswith("http://"):
        ip_addr = "http://" + ip_addr

    username = input("Admin Username (leave blank for 'admin'): ").strip()
    if not username:
        username = "admin"
        
    password = input("Admin Password (leave blank for 'admin'): ").strip()
    if not password:
        password = "admin"

    print("\n[INFO] Connecting to NanoNAS and uploading firmware...")
    
    url = f"{ip_addr}/update"
    
    try:
        with open(bin_file, "rb") as f:
            # Using basic auth and multipart file upload
            files = {'update': (os.path.basename(bin_file), f, 'application/octet-stream')}
            response = requests.post(url, auth=(username, password), files=files)
            
            if response.status_code == 200 and "OK" in response.text:
                print("\n[SUCCESS] OTA Update Successful!")
                print("[INFO] NanoNAS is now rebooting. Please wait about 15 seconds for it to come back online.")
            elif response.status_code == 401:
                print("\n[ERROR] Authentication failed. Invalid username or password.")
            else:
                print(f"\n[ERROR] OTA Update Failed. Server responded: HTTP {response.status_code}")
                print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Failed to connect to NanoNAS at {ip_addr}")
        print("Details:", e)
        print("Please ensure the NAS is powered on and connected to the same network.")

if __name__ == "__main__":
    main()
