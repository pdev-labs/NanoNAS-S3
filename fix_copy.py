import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

old_code = """    uint8_t buf[4096];
    size_t len = 0;
    while ((len = src.read(buf, sizeof(buf))) > 0) {
      dest.write(buf, len);
      delay(1); // prevent WDT
    }
    dest.close();
    src.close();
    return true;"""

new_code = """    uint8_t *buf = (uint8_t *)malloc(4096);
    if (!buf) {
      dest.close();
      src.close();
      return false;
    }
    size_t len = 0;
    while ((len = src.read(buf, 4096)) > 0) {
      dest.write(buf, len);
      delay(1); // prevent WDT
    }
    free(buf);
    dest.close();
    src.close();
    return true;"""

code = code.replace(old_code, new_code)

with open("esp32-s3-server.ino", "w") as f:
    f.write(code)

print("Fixed stack overflow in copyRecursive!")
