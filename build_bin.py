import os
import subprocess
import sys
import shutil
import tempfile
import json

CACHE_FILE = ".build_cache.json"

def main():
    print("========================================")
    print("   Universal Arduino Binary Builder")
    print("========================================")

    cached_data = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached_data = json.load(f)
        except Exception:
            pass

    # Set up tab completion for file paths
    try:
        import readline
        import glob

        def path_completer(text, state):
            text = os.path.expanduser(text)
            matches = glob.glob(text + '*')
            matches = [m + '/' if os.path.isdir(m) else m for m in matches]
            if state < len(matches):
                return matches[state]
            else:
                return None

        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(path_completer)
    except ImportError:
        pass # Windows

    # Ask for the file path
    default_path = cached_data.get("target_path", "")
    prompt = f"Enter the full path of the sketch folder or .ino file to compile (default: '{default_path}'): " if default_path else "Enter the full path of the sketch folder or .ino file to compile: "
    target_path = input(prompt).strip()
    
    if not target_path and default_path:
        target_path = default_path

    if target_path.startswith("'") and target_path.endswith("'"):
        target_path = target_path[1:-1]
    if target_path.startswith('"') and target_path.endswith('"'):
        target_path = target_path[1:-1]

    if not os.path.exists(target_path):
        print(f"[ERROR] Path '{target_path}' does not exist.")
        sys.exit(1)

    fqbn = None
    detected_board = None
    print("\n[INFO] Scanning for connected Arduino boards...")
    try:
        result = subprocess.run(["arduino-cli", "board", "list", "--format", "json"], capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for port in data.get("detected_ports", []):
                if "matching_boards" in port and len(port["matching_boards"]) > 0:
                    fqbn = port["matching_boards"][0]["fqbn"]
                    board_name = port["matching_boards"][0]["name"]
                    detected_board = f"{board_name} ({fqbn})"
                    break
    except Exception as e:
        pass

    if not detected_board:
        print("[INFO] Arduino CLI couldn't map the USB VID/PID to an FQBN. Probing the hardware chip with esptool...")
        try:
            import re
            result = subprocess.run(["esptool", "flash_id"], capture_output=True, text=True, timeout=10)
            out = result.stdout + result.stderr
            if "ESP32-S3" in out:
                fqbn = "esp32:esp32:esp32s3"
                detected_board = "ESP32-S3 (esp32:esp32:esp32s3)"
            elif "ESP32-S2" in out:
                fqbn = "esp32:esp32:esp32s2"
                detected_board = "ESP32-S2 (esp32:esp32:esp32s2)"
            elif "ESP32-C3" in out:
                fqbn = "esp32:esp32:esp32c3"
                detected_board = "ESP32-C3 (esp32:esp32:esp32c3)"
            elif "ESP32" in out:
                fqbn = "esp32:esp32:esp32"
                detected_board = "ESP32 (esp32:esp32:esp32)"
        except Exception as e:
            pass

    if detected_board:
        ans = input(f"[?] I have detected {detected_board}. Is this correct? [Y/n]: ").strip().lower()
        if ans == 'n':
            fqbn = None

    if not fqbn:
        cached_fqbn = cached_data.get("fqbn", "esp32:esp32:esp32s3")
        print("\n[WARNING] Could not automatically detect a connected board or auto-detection was rejected.")
        fqbn_input = input(f"Enter the FQBN manually (leave blank for default '{cached_fqbn}'): ").strip()
        if not fqbn_input:
            fqbn = cached_fqbn
        else:
            fqbn = fqbn_input

    # Determine if it's a file or dir
    tmp_dir = None
    if os.path.isfile(target_path):
        if not target_path.lower().endswith(".ino"):
            print(f"[ERROR] Only .ino files or directories are supported.")
            sys.exit(1)

        sketch_name = os.path.splitext(os.path.basename(target_path))[0]
        source_dir = os.path.dirname(os.path.abspath(target_path))
        parent_dir_name = os.path.basename(source_dir)

        if parent_dir_name == sketch_name:
            print(f"[INFO] Sketch is correctly structured in '{parent_dir_name}/'. Compiling in-place.")
            build_dir = source_dir
        else:
            print(f"[INFO] Sketch is NOT in a folder named '{sketch_name}'. Staging to temp dir...")
            tmp_dir = tempfile.mkdtemp()
            build_dir = os.path.join(tmp_dir, sketch_name)
            os.makedirs(build_dir)

            for f in os.listdir(source_dir):
                src = os.path.join(source_dir, f)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(build_dir, f))
    else:
        build_dir = os.path.abspath(target_path)

    print(f"\n[INFO] Compiling sketch using FQBN: {fqbn}")

    cmd = [
        "arduino-cli",
        "compile",
        "-e",
        "--fqbn",
        fqbn,
        build_dir
    ]

    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd)

        if tmp_dir:
            shutil.rmtree(tmp_dir)

        if result.returncode == 0:
            print("")
            print("[SUCCESS] Compilation finished successfully!")
            print(f"[INFO] The generated binaries are located in the 'build' folder inside '{build_dir}'")
            
            # Cache the successful config
            with open(CACHE_FILE, "w") as f:
                json.dump({"target_path": target_path, "fqbn": fqbn}, f)
        else:
            print("")
            print("[ERROR] Compilation failed. Please check the logs above.")
            sys.exit(result.returncode)
    except FileNotFoundError:
        print("")
        print("[ERROR] 'arduino-cli' is not installed or not in your system's PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
