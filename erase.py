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
            if "ttyusb" in p.device.lower() or "ttyacm" in p.device.lower() or "com" in p.device.lower():
                return p.device
    except ImportError:
        pass
        
    if sys.platform.startswith('win'):
        return "COM3"
    elif sys.platform.startswith('darwin'):
        return "/dev/cu.usbserial-0001"
    else:
        return "/dev/ttyACM0"

# Auto-detect port if not provided
port = sys.argv[1] if len(sys.argv) > 1 else get_esp32_port()

print(f"==========================================")
print(f" ESP32-S3 Erase Utility")
print(f" Port: {port}")
print(f"==========================================")
print("1. Normal Erase (Wipes all files, configs, and firmware)")
print("2. Factory Reset (Erases everything AND flashes a clean bootloader)")
choice = input("\nEnter your choice (1 or 2): ").strip()

def get_command(module_name):
    import shutil
    cmd = [sys.executable, "-m", module_name, "-h"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0:
        return [sys.executable, "-m", module_name]
    if shutil.which(module_name):
        return [module_name]
    if shutil.which(f"{module_name}.py"):
        return [f"{module_name}.py"]
    return [module_name]

if choice == "2":
    print("\n[1/3] Erasing Entire Flash Memory...")
else:
    print("\nErasing Entire Flash Memory...")

# Use robust command resolution (works on Windows/Mac/Linux/Termux)
erase_cmd = get_command("esptool") + ["--port", port, "erase_flash"]
result = subprocess.run(erase_cmd)

if result.returncode != 0:
    print("\n❌ Failed to erase flash. Is it in bootloader mode? Do you have esptool installed? (pip install esptool)")
    sys.exit(1)

if choice != "2":
    print("\n✅ Successfully erased the ESP32!")
    sys.exit(0)

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
