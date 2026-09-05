import os
import subprocess
import sys
import shutil
import tempfile

def main():
    print("========================================")
    print("   Universal Arduino Binary Builder")
    print("========================================")

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
    target_path = input("Enter the full path of the sketch folder or .ino file to compile: ").strip()

    if target_path.startswith("'") and target_path.endswith("'"):
        target_path = target_path[1:-1]
    if target_path.startswith('"') and target_path.endswith('"'):
        target_path = target_path[1:-1]

    if not os.path.exists(target_path):
        print(f"[ERROR] Path '{target_path}' does not exist.")
        sys.exit(1)
        
    fqbn_input = input("Enter the FQBN (leave blank for default 'esp32:esp32:esp32s3'): ").strip()
    if not fqbn_input:
        fqbn = "esp32:esp32:esp32s3"
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
