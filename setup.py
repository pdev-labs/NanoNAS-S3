import os
import sys
import subprocess
import shutil

def is_tool_installed(name):
    """Check whether `name` is on PATH and marked as executable."""
    return shutil.which(name) is not None

def prompt_yes_no(prompt, default="y"):
    choices = " [Y/n]: " if default.lower() == "y" else " [y/N]: "
    while True:
        ans = input(prompt + choices).strip().lower()
        if not ans:
            return default.lower() == "y"
        if ans in ["y", "yes"]:
            return True
        if ans in ["n", "no"]:
            return False
        print("Please answer 'yes' or 'no'.")

def install_esptool():
    print("\n[INFO] Attempting to install python dependencies (esptool, requests) via pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "esptool", "requests"])
        print("[SUCCESS] Python dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install dependencies automatically.")
        print("Please run manually: python -m pip install esptool requests")

def install_arduino_cli():
    print("\n[INFO] Arduino CLI installation requires platform-specific steps.")
    if sys.platform.startswith('win'):
        print("-> Windows detected. Please download the MSI installer from:")
        print("   https://arduino.github.io/arduino-cli/latest/installation/")
        print("   Make sure to check 'Add to PATH' during installation!")
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        print("-> Linux/macOS detected. Running the official install script...")
        try:
            # Installs into ~/bin
            home_bin = os.path.expanduser("~/bin")
            os.makedirs(home_bin, exist_ok=True)
            cmd = f"curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh -s -- -b {home_bin}"
            os.system(cmd)
            print(f"\n[SUCCESS] arduino-cli installed to {home_bin}/arduino-cli")
            print(f"*** IMPORTANT: Please ensure {home_bin} is added to your system PATH! ***")
            print("For example, add: export PATH=$PATH:~/bin to your ~/.bashrc or ~/.zshrc")
        except Exception as e:
            print(f"[ERROR] Failed to install arduino-cli: {e}")

def install_libraries():
    if not is_tool_installed("arduino-cli"):
        # Check if they just installed it to ~/bin but it's not in PATH yet
        home_cli = os.path.expanduser("~/bin/arduino-cli")
        if os.path.exists(home_cli):
            cli_path = home_cli
        else:
            print("\n[WARNING] arduino-cli not found in PATH. Skipping library installation.")
            return
    else:
        cli_path = "arduino-cli"
        
    print("\n[INFO] Updating Arduino Core Index...")
    subprocess.run([cli_path, "core", "update-index"])
    
    print("[INFO] Installing ESP32 Core...")
    subprocess.run([cli_path, "core", "install", "esp32:esp32"])

    libs = [
        "ArduinoJson",
        "Adafruit NeoPixel",
        "EspUsbHost"
    ]
    
    print("\n[INFO] Installing required Arduino libraries...")
    for lib in libs:
        print(f" -> Installing {lib}...")
        subprocess.run([cli_path, "lib", "install", lib])
        
    print("[INFO] ESPAsyncWebServer requires manual installation via git.")
    print("If you haven't already, please install it in your Arduino/libraries folder.")

def main():
    print("========================================")
    print("    NanoNAS Interactive Setup Wizard")
    print("========================================")
    
    # --- Step 1: Toolchain Validation ---
    print("\n--- Step 1: Checking System Dependencies ---")
    
    # Check esptool
    if is_tool_installed("esptool.py") or is_tool_installed("esptool"):
        print("[OK] esptool is installed.")
    else:
        print("[WARNING] esptool is missing.")
        if prompt_yes_no("Would you like to install esptool now (requires pip)?"):
            install_esptool()
            
    # Check arduino-cli
    if is_tool_installed("arduino-cli"):
        print("[OK] arduino-cli is installed.")
        if prompt_yes_no("Would you like to automatically download/update required Arduino libraries?"):
            install_libraries()
    else:
        print("[WARNING] arduino-cli is missing.")
        if prompt_yes_no("Would you like instructions to install arduino-cli?"):
            install_arduino_cli()
            # If they just installed it on linux/mac, ask to install libs
            home_cli = os.path.expanduser("~/bin/arduino-cli")
            if os.path.exists(home_cli):
                if prompt_yes_no("\nWould you like to automatically download/update required Arduino libraries now?"):
                    install_libraries()

    # --- Step 2: Credentials Configuration ---
    print("\n--- Step 2: Configuring NanoNAS Secrets ---")
    secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets.h")
    
    proceed_with_secrets = True
    if os.path.exists(secrets_path):
        if not prompt_yes_no("secrets.h already exists. Do you want to overwrite it?"):
            print("Skipping secrets.h generation.")
            proceed_with_secrets = False

    if proceed_with_secrets:
        print("Please enter the WiFi credentials for the network the NAS should connect to.")
        ssid = input("  WiFi Network Name (SSID): ").strip()
        pwd = input("  WiFi Password: ").strip()
        
        print("\nNow let's configure the secure Admin Panel credentials.")
        admin_user = input("  Admin Username [default: admin]: ").strip()
        if not admin_user: admin_user = "admin"
        
        admin_pass = input("  Admin Password [default: admin123]: ").strip()
        if not admin_pass: admin_pass = "admin123"
        
        with open(secrets_path, "w") as f:
            f.write("// Auto-generated by setup.py\n")
            f.write("#ifndef SECRETS_H\n")
            f.write("#define SECRETS_H\n\n")
            f.write(f'#define SECRET_WIFI_SSID "{ssid}"\n')
            f.write(f'#define SECRET_WIFI_PASSWORD "{pwd}"\n\n')
            f.write(f'#define SECRET_ADMIN_USERNAME "{admin_user}"\n')
            f.write(f'#define SECRET_ADMIN_PASSWORD "{admin_pass}"\n\n')
            f.write("#endif\n")
            
        print(f"\n[SUCCESS] Successfully generated {secrets_path}!")
        print("[INFO] Your credentials are safe! Git is configured to ignore secrets.h.")

    print("\n========================================")
    print(" Setup Complete! You are ready to deploy.")
    print(" Run 'python flasher.py' to compile and flash the NAS!")
    print("========================================")

if __name__ == "__main__":
    main()
