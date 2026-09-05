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

def get_command(module_name):
    import shutil
    # Try Python module execution first
    cmd = [sys.executable, "-m", module_name, "-h"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode == 0:
        return [sys.executable, "-m", module_name]
    
    # Fallback to globally installed binary (common on Arch Linux/pipx)
    if shutil.which(module_name):
        return [module_name]
    if shutil.which(f"{module_name}.py"):
        return [f"{module_name}.py"]
        
    return [module_name] # Let it fail natively

def print_table(title, data_dict):
    if not data_dict: return
    max_k = max([len(str(k)) for k in data_dict.keys()] + [10])
    max_v = max([len(str(v)) for v in data_dict.values()] + [10])
    max_v = min(max_v, 80)
    
    print("\n" + f" {title} ".center(max_k + max_v + 7, "="))
    print(f"┌─{'─'*max_k}─┬─{'─'*max_v}─┐")
    print(f"│ {'Property'.ljust(max_k)} │ {'Value'.ljust(max_v)} │")
    print(f"├─{'─'*max_k}─┼─{'─'*max_v}─┤")
    for k, v in data_dict.items():
        v_str = str(v).replace('\n', ' ')
        if len(v_str) > max_v:
            v_str = v_str[:max_v - 3] + "..."
        print(f"│ {str(k).ljust(max_k)} │ {v_str.ljust(max_v)} │")
    print(f"└─{'─'*max_k}─┴─{'─'*max_v}─┘")

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else get_esp32_port()

    print("========================================")
    print(" ESP32 Hardware & Software Info Utility")
    print(f" Target Port: {port}")
    print("========================================\n")
    print("[INFO] Querying ESP32 chip for all available details...\n")

    # Commands to extract maximum information
    commands = {
        "Hardware Specs & Flash Info": (get_command("esptool"), ["flash_id"]),
        "Security Info (Software/Encryption)": (get_command("esptool"), ["get_security_info"]),
        "Raw MAC Addresses": (get_command("esptool"), ["read_mac"]),
        "Ultimate eFuse Configuration Dump": (get_command("espefuse"), ["summary", "--format", "json"])
    }

    try:
        for title, (base_cmd, args) in commands.items():
            cmd = base_cmd + ["--port", port] + args
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if "json" in args:
                    try:
                        import json
                        json_str = result.stdout[result.stdout.find("{"):]
                        efuses = json.loads(json_str)
                        
                        categories = {}
                        for k, v in efuses.items():
                            cat = v.get("category", "general").title()
                            val = str(v.get("value", "")) if v.get("value") is not None else str(v.get("raw_value", ""))
                            if cat not in categories:
                                categories[cat] = {}
                            categories[cat][k] = val
                            
                        for cat, data_dict in categories.items():
                            print_table(f"eFuse: {cat}", data_dict)
                            
                    except Exception as e:
                        print(f"❌ Failed to parse eFuse JSON: {e}")
                        
                else:
                    lines = result.stdout.split('\n')
                    data_dict = {}
                    last_key = None
                    for line in lines:
                        if any(x in line for x in ["esptool.py", "Connecting", "stub", "Changed.", "Hard resetting", "esptool v", "espefuse v", "espefuse.py", "DEPRECATED", "Serial port", "Detecting chip type", "Connected to", "===", "---"]):
                            continue
                        line = line.strip()
                        if not line:
                            continue
                            
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k, v = k.strip(), v.strip()
                            if k and v:
                                data_dict[k] = v
                                last_key = k
                            elif k:
                                data_dict[k] = ""
                                last_key = k
                        elif "-" in line and last_key:
                            # Append nested lines like "BLOCK_KEY0 - USER" to the last key
                            data_dict[last_key] += f" | {line}"
                        
                    print_table(title, data_dict)
            else:
                print(f"\n❌ Failed to retrieve {title}. (Error code {result.returncode})")
                if "No module named" in result.stderr:
                    print("Make sure esptool is installed! (pip install esptool or sudo pacman -S esptool)\n")
                else:
                    print(result.stderr.strip() + "\n")
                
        print("\n✅ Successfully retrieved all available ESP32 info!")
            
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
        print("Please ensure you have python and esptool installed (pip install esptool).")

if __name__ == "__main__":
    main()
