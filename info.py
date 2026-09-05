#!/usr/bin/env python3
import sys
import subprocess

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

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else get_esp32_port()

    print("========================================")
    print(" ESP32 Hardware & Software Info Utility")
    print(f" Target Port: {port}")
    print("========================================\n")
    print("[INFO] Querying ESP32 chip using esptool...\n")

    # We use sys.executable to make it completely cross platform (Windows, Mac, Linux, Termux)
    cmd = [sys.executable, "-m", "esptool", "--port", port, "flash_id"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # We filter out the unnecessary stub flasher logs to make it look clean
            output = result.stdout
            lines = output.split('\n')
            
            clean_output = []
            for line in lines:
                # Filter out boring esptool logs
                if "esptool.py" in line or "Connecting" in line or "stub" in line or "Changed." in line:
                    continue
                if line.strip():
                    clean_output.append(line)
            
            print("\n".join(clean_output))
            print("\n✅ Successfully retrieved ESP32 info!")
            
        else:
            print(result.stdout)
            print(result.stderr)
            print("\n❌ Failed to retrieve info. Is the ESP32 plugged in and esptool installed? (pip install esptool)")
            
    except Exception as e:
        print(f"\n❌ Error running esptool: {e}")
        print("Please ensure you have python and esptool installed.")

if __name__ == "__main__":
    main()
