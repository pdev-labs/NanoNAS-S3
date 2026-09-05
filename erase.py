import os
import sys
import subprocess
import tempfile
import shutil

def get_esp32_port():
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for p in ports:
            desc = p.description.lower()
            if "esp32" in desc or "ch340" in desc or "cp210" in desc or "usb jtag" in desc:
                return p.device
        for p in ports:
            if "ttyUSB" in p.device or "ttyACM" in p.device:
                return p.device
    except ImportError:
        pass
    return "/dev/ttyACM0"

# Auto-detect port if not provided
port = sys.argv[1] if len(sys.argv) > 1 else get_esp32_port()

print(f"==========================================")
print(f" Erasing & Factory Resetting ESP32-S3")
print(f" Port: {port}")
print(f"==========================================")
print("\n[1/3] Erasing Entire Flash Memory...")

exit_code = os.system(f"esptool --port {port} erase-flash")
if exit_code != 0:
    exit_code = os.system(f"esptool.py --port {port} erase-flash")

if exit_code != 0:
    print("\n❌ Failed to erase flash. Is it in bootloader mode?")
    sys.exit(1)

print("\n[2/3] Generating Factory Bootloader & Partition Table...")
tmp_dir = tempfile.mkdtemp()
sketch_dir = os.path.join(tmp_dir, "factory_reset")
os.makedirs(sketch_dir)
with open(os.path.join(sketch_dir, "factory_reset.ino"), "w") as f:
    f.write("void setup() {}\nvoid loop() {}")

compile_cmd = ["arduino-cli", "compile", "--fqbn", "esp32:esp32:esp32s3", sketch_dir]
compile_res = subprocess.run(compile_cmd, capture_output=True)

if compile_res.returncode == 0:
    print("\n[3/3] Flashing Clean Factory Bootloader...")
    upload_cmd = ["arduino-cli", "upload", "-p", port, "--fqbn", "esp32:esp32:esp32s3", sketch_dir]
    upload_res = subprocess.run(upload_cmd)
    shutil.rmtree(tmp_dir)
    if upload_res.returncode == 0:
        print("\n✅ Factory Reset Complete! The ESP32 is now in a pristine state.")
    else:
        print("\n❌ Failed to flash factory bootloader.")
else:
    shutil.rmtree(tmp_dir)
    print("\n⚠️ Flash erased successfully, but failed to compile factory bootloader.")
    print("You may need to flash your project manually using flasher.py to restore it.")
