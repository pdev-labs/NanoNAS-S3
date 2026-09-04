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
        
        import shutil
        import tempfile
        
        # arduino-cli requires the .ino to be inside a folder with the SAME name.
        # e.g. rgb_fade.ino MUST be in a folder called rgb_fade/
        sketch_name = os.path.splitext(os.path.basename(file_path))[0]
        source_dir = os.path.dirname(os.path.abspath(file_path))
        parent_dir_name = os.path.basename(source_dir)
        
        tmp_dir = None
        
        # If the sketch is already in a correctly named folder, compile it in-place.
        # This preserves the arduino-cli build cache (which makes it 10x faster)
        # and avoids the appearance of "getting stuck" on a full recompile.
        if parent_dir_name == sketch_name:
            print(f"[INFO] Sketch is correctly structured in '{parent_dir_name}/'. Compiling in-place.")
            sketch_dir = source_dir
        else:
            import shutil
            import tempfile
            
            print(f"[INFO] Sketch is NOT in a folder named '{sketch_name}'. Staging to temp dir...")
            # Create a temp directory and stage the sketch inside it
            tmp_dir = tempfile.mkdtemp()
            sketch_dir = os.path.join(tmp_dir, sketch_name)
            os.makedirs(sketch_dir)
            
            # Copy ALL files from the source directory
            copied = []
            for f in os.listdir(source_dir):
                src = os.path.join(source_dir, f)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(sketch_dir, f))
                    copied.append(f)
            print(f"[INFO] Staged {len(copied)} file(s) to: {sketch_dir}")
        
        # Compile using the folder (not the file)
        compile_cmd = ["arduino-cli", "compile", "--fqbn", "esp32:esp32:esp32s3", sketch_dir]
        print(f"Running: {' '.join(compile_cmd)}")
        result = subprocess.run(compile_cmd)
        if result.returncode != 0:
            print("\n[ERROR] Compilation failed!")
            if tmp_dir:
                shutil.rmtree(tmp_dir)
            sys.exit(1)
            
        # Upload using the folder
        upload_cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", "esp32:esp32:esp32s3", sketch_dir]
        print(f"\nRunning: {' '.join(upload_cmd)}")
        result = subprocess.run(upload_cmd)
        
        # Clean up the temp folder if we created one
        if tmp_dir:
            shutil.rmtree(tmp_dir)
        
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
