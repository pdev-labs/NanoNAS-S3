import os
import sys

# Default port
port = "/dev/ttyACM0"

if len(sys.argv) > 1:
    port = sys.argv[1]

print(f"==========================================")
print(f" Erasing ESP32 Flash on port: {port}")
print(f"==========================================")
print("Running esptool...")

# Run esptool to erase flash
# Uses standard ESP32 esptool module included with esptool package
exit_code = os.system(f"esptool --port {port} erase-flash")
if exit_code != 0:
    # Fallback to 'esptool.py' if 'esptool' is not found
    exit_code = os.system(f"esptool.py --port {port} erase-flash")

if exit_code == 0:
    print("\n✅ Successfully erased the ESP32!")
else:
    print("\n❌ Failed to erase the ESP32. Make sure it's plugged in and in bootloader mode if necessary.")
