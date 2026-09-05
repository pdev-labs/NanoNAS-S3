import os
import sys
import subprocess
import requests
import json
import time
import socket
import concurrent.futures

CACHE_FILE = ".build_cache.json"

def check_ip(ip):
    try:
        r = requests.get(f"http://{ip}/", timeout=1.0)
        if r.status_code == 401:
            auth_header = r.headers.get('WWW-Authenticate', '')
            if 'NanoNAS' in auth_header or 'Login Required' in auth_header:
                return ip
    except Exception:
        pass
    return None

def auto_detect_nanonas():
    print("\n[INFO] Scanning local network (Hotspot/WiFi) for NanoNAS devices...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '192.168.43.1'
    finally:
        s.close()
    
    subnet = ".".join(local_ip.split('.')[:-1])
    ips_to_check = [f"{subnet}.{i}" for i in range(1, 255)]
    if subnet != "192.168.4":
        ips_to_check.append("192.168.4.1")
        
    found_ip = None
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_ip, ip): ip for ip in ips_to_check}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                found_ip = res
                break # We found it, other threads will quickly timeout
                
    return found_ip

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
    cached_ip = cache.get("ota_ip", "nanonas.local")
    cached_user = cache.get("ota_user", "admin")
    cached_pass = cache.get("ota_pass", "admin")
    
    scanned_ip = auto_detect_nanonas()
    if scanned_ip:
        print(f"[SUCCESS] Found NanoNAS automatically at {scanned_ip}")
        cached_ip = scanned_ip
    else:
        print("[WARNING] Could not automatically find NanoNAS on the local network.")

    print("\n--- OTA Configuration ---")
    ip_addr = input(f"Enter the NanoNAS IP or mDNS (leave blank for '{cached_ip}'): ").strip()
    if not ip_addr:
        ip_addr = cached_ip
        
    # Standardize URL
    clean_ip = ip_addr
    if not ip_addr.startswith("http://"):
        ip_addr = "http://" + ip_addr
    else:
        clean_ip = ip_addr.replace("http://", "")

    username = input(f"Admin Username (leave blank for '{cached_user}'): ").strip()
    if not username:
        username = cached_user
        
    password = input(f"Admin Password (leave blank for '{cached_pass}'): ").strip()
    if not password:
        password = cached_pass

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
                
                # Save the successful credentials back to cache
                cache["ota_ip"] = clean_ip
                cache["ota_user"] = username
                cache["ota_pass"] = password
                with open(CACHE_FILE, "w") as out:
                    json.dump(cache, out)
                    
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
