import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

# Add recursive copy function
copy_func = """
// Helper to copy files and directories recursively
bool copyRecursive(String srcPath, String destPath) {
  fs::File src = getStorage().open(srcPath, "r");
  if (!src) return false;

  if (!src.isDirectory()) {
    fs::File dest = getStorage().open(destPath, "w");
    if (!dest) { src.close(); return false; }
    
    uint8_t buf[4096];
    size_t len = 0;
    while ((len = src.read(buf, sizeof(buf))) > 0) {
      dest.write(buf, len);
      delay(1); // prevent WDT
    }
    dest.close();
    src.close();
    return true;
  } else {
    getStorage().mkdir(destPath);
    fs::File dir = src;
    fs::File file = dir.openNextFile();
    while (file) {
      String newSrc = srcPath + "/" + file.name();
      String newDest = destPath + "/" + file.name();
      if (!copyRecursive(newSrc, newDest)) {
        return false;
      }
      file = dir.openNextFile();
      delay(1);
    }
    return true;
  }
}

  // Delete File/Folder
"""

code = code.replace("  // Delete File/Folder", copy_func)

# Add /api/copy endpoint
copy_endpoint = """  // API: Copy File/Folder
  server.on("/api/copy", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if(request->hasParam("from", true) && request->hasParam("to", true)) {
      String fromPath = sanitizePath(request->getParam("from", true)->value());
      String toPath = sanitizePath(request->getParam("to", true)->value());
      if(copyRecursive(fromPath, toPath)) {
        request->send(200, "text/plain", "OK");
      } else {
        request->send(500, "text/plain", "Copy failed");
      }
    } else {
      request->send(400, "text/plain", "Missing from or to parameter");
    }
  });

  // API: Move / Rename"""

code = code.replace("  // API: Move / Rename", copy_endpoint)

with open("esp32-s3-server.ino", "w") as f:
    f.write(code)

print("Backend patched with copy API!")
