import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

tar_class_logic = re.search(r'// ---------------------------------------------------------\n// TAR STREAMING RESPONSE.*?// Setup API Routes', code, re.DOTALL)
if tar_class_logic:
    extracted = tar_class_logic.group(0).replace('// Setup API Routes', '')
    # Remove from inside setup()
    code = code.replace(tar_class_logic.group(0), '// Setup API Routes')
    
    # Inject before setup()
    code = code.replace('void setup() {', extracted + '\nvoid setup() {')

with open("esp32-s3-server.ino", "w") as f:
    f.write(code)

print("Done fixing tar scope!")
