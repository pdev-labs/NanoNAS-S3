import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

# 1. Add CopyJob definitions
copy_job_def = """
#include <vector>

enum CopyState {
  COPY_IDLE,
  COPY_SCANNING,
  COPY_FILE
};

struct CopyJob {
  CopyState state = COPY_IDLE;
  String srcBase;
  String destBase;
  std::vector<String> scanDirsSrc;
  std::vector<String> scanDirsDest;
  std::vector<String> copyFilesSrc;
  std::vector<String> copyFilesDest;
  
  fs::File currentSrc;
  fs::File currentDest;
  size_t totalBytesToCopy = 0;
  size_t bytesCopied = 0;
  
  bool finished = false;
  bool success = true;
};

CopyJob currentJob;

void processCopyJob() {
  if (currentJob.state == COPY_IDLE) return;

  if (currentJob.state == COPY_SCANNING) {
    if (currentJob.scanDirsSrc.empty()) {
      currentJob.state = COPY_FILE;
      return;
    }
    
    String srcDir = currentJob.scanDirsSrc.back();
    String destDir = currentJob.scanDirsDest.back();
    currentJob.scanDirsSrc.pop_back();
    currentJob.scanDirsDest.pop_back();
    
    getStorage().mkdir(destDir);
    
    fs::File dir = getStorage().open(srcDir);
    if (dir && dir.isDirectory()) {
      fs::File file = dir.openNextFile();
      while (file) {
        String newSrc = srcDir + "/" + file.name();
        String newDest = destDir + "/" + file.name();
        if (file.isDirectory()) {
          currentJob.scanDirsSrc.push_back(newSrc);
          currentJob.scanDirsDest.push_back(newDest);
        } else {
          currentJob.copyFilesSrc.push_back(newSrc);
          currentJob.copyFilesDest.push_back(newDest);
          currentJob.totalBytesToCopy += file.size();
        }
        file = dir.openNextFile();
      }
    }
    return; // Yield to loop
  }

  if (currentJob.state == COPY_FILE) {
    if (!currentJob.currentSrc) {
      if (currentJob.copyFilesSrc.empty()) {
        currentJob.finished = true;
        currentJob.state = COPY_IDLE;
        return;
      }
      
      String src = currentJob.copyFilesSrc.back();
      String dest = currentJob.copyFilesDest.back();
      currentJob.copyFilesSrc.pop_back();
      currentJob.copyFilesDest.pop_back();
      
      currentJob.currentSrc = getStorage().open(src, "r");
      currentJob.currentDest = getStorage().open(dest, "w");
      if (!currentJob.currentSrc || !currentJob.currentDest) {
        currentJob.success = false;
        currentJob.finished = true;
        currentJob.state = COPY_IDLE;
        if (currentJob.currentSrc) currentJob.currentSrc.close();
        if (currentJob.currentDest) currentJob.currentDest.close();
        return;
      }
    }
    
    // Copy a chunk
    uint8_t buf[8192];
    size_t len = currentJob.currentSrc.read(buf, sizeof(buf));
    if (len > 0) {
      currentJob.currentDest.write(buf, len);
      currentJob.bytesCopied += len;
    } else {
      currentJob.currentSrc.close();
      currentJob.currentDest.close();
    }
    return; // Yield to loop
  }
}
"""
# Insert after getContentType
code = re.sub(r'String getContentType\(String filename\) \{', copy_job_def + '\nString getContentType(String filename) {', code)

# 2. Modify loop()
old_loop = """void loop() {
  dnsServer.processNextRequest();
}"""
new_loop = """void loop() {
  dnsServer.processNextRequest();
  processCopyJob();
}"""
code = code.replace(old_loop, new_loop)

# 3. Replace /api/copy endpoint
old_api_copy = """  // API: Copy File/Folder
  server.on("/api/copy", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request)) return request->requestAuthentication();
    if(!request->hasParam("from", true) || !request->hasParam("to", true)) {
      request->send(400, "text/plain", "Missing from or to parameters");
      return;
    }
    String fromPath = sanitizePath(request->getParam("from", true)->value());
    String toPath = sanitizePath(request->getParam("to", true)->value());
    
    if(fromPath == "/" || fromPath == "/System Volume Information") {
       request->send(403, "text/plain", "Cannot copy system folders");
       return;
    }
    
    if(copyRecursive(fromPath, toPath)) {
      request->send(200, "text/plain", "Copied successfully");
    } else {
      request->send(500, "text/plain", "Copy failed");
    }
  });"""

new_api_copy = """  // API: Copy File/Folder (Background)
  server.on("/api/copy", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request)) return request->requestAuthentication();
    if(!request->hasParam("from", true) || !request->hasParam("to", true)) {
      request->send(400, "text/plain", "Missing from or to parameters");
      return;
    }
    if (currentJob.state != COPY_IDLE) {
      request->send(429, "text/plain", "Another copy job is already in progress");
      return;
    }
    
    String fromPath = sanitizePath(request->getParam("from", true)->value());
    String toPath = sanitizePath(request->getParam("to", true)->value());
    
    if(fromPath == "/" || fromPath == "/System Volume Information") {
       request->send(403, "text/plain", "Cannot copy system folders");
       return;
    }
    
    // Initialize background copy
    currentJob.srcBase = fromPath;
    currentJob.destBase = toPath;
    currentJob.scanDirsSrc.clear();
    currentJob.scanDirsDest.clear();
    currentJob.copyFilesSrc.clear();
    currentJob.copyFilesDest.clear();
    currentJob.totalBytesToCopy = 0;
    currentJob.bytesCopied = 0;
    currentJob.finished = false;
    currentJob.success = true;
    
    fs::File src = getStorage().open(fromPath);
    if (!src) {
       request->send(404, "text/plain", "Source not found");
       return;
    }
    
    if (src.isDirectory()) {
       currentJob.scanDirsSrc.push_back(fromPath);
       currentJob.scanDirsDest.push_back(toPath);
       currentJob.state = COPY_SCANNING;
    } else {
       currentJob.copyFilesSrc.push_back(fromPath);
       currentJob.copyFilesDest.push_back(toPath);
       currentJob.totalBytesToCopy = src.size();
       currentJob.state = COPY_FILE;
    }
    src.close();
    
    request->send(202, "text/plain", "Copy job started");
  });

  // API: Copy Status
  server.on("/api/copy_status", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request)) return request->requestAuthentication();
    String json = "{";
    json += "\"finished\":" + String(currentJob.finished ? "true" : "false") + ",";
    json += "\"success\":" + String(currentJob.success ? "true" : "false") + ",";
    json += "\"total\":" + String(currentJob.totalBytesToCopy) + ",";
    json += "\"copied\":" + String(currentJob.bytesCopied) + ",";
    json += "\"scanning\":" + String(currentJob.state == COPY_SCANNING ? "true" : "false");
    json += "}";
    
    if (currentJob.finished) {
       currentJob.state = COPY_IDLE; // Reset for next job
    }
    
    request->send(200, "application/json", json);
  });"""
code = code.replace(old_api_copy, new_api_copy)

# 4. Remove old copyRecursive
code = re.sub(r'// Helper to copy files and directories recursively.*?return true;\n}', '', code, flags=re.DOTALL)


with open("esp32-s3-server.ino", "w") as f:
    f.write(code)


# 5. Patch index_html.h
with open("index_html.h", "r") as f:
    html = f.read()

old_paste = """                try {
                    let res = await fetch(`/api/${data.action}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                    });
                    if (!res.ok) {
                        console.error(`Failed to ${data.action} ${sourcePath}`);
                    }
                } catch(e) {
                    console.error(`Error during ${data.action} ${sourcePath}`, e);
                }"""

new_paste = """                try {
                    let res = await fetch(`/api/${data.action}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                    });
                    if (res.ok && data.action === 'copy') {
                        // Poll for status
                        let finished = false;
                        while (!finished) {
                            await new Promise(r => setTimeout(r, 1000));
                            let statRes = await fetch('/api/copy_status');
                            if (statRes.ok) {
                                let status = await statRes.json();
                                if (status.scanning) {
                                    btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Scanning ${i+1}/${arr.length}...`;
                                } else {
                                    let pct = status.total > 0 ? Math.round((status.copied / status.total) * 100) : 100;
                                    btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Pasting ${i+1}/${arr.length} (${pct}%)...`;
                                }
                                finished = status.finished;
                                if (finished && !status.success) {
                                    console.error("Backend reported copy failure");
                                }
                            }
                        }
                    } else if (!res.ok) {
                        console.error(`Failed to ${data.action} ${sourcePath}`);
                    }
                } catch(e) {
                    console.error(`Error during ${data.action} ${sourcePath}`, e);
                }"""
html = html.replace(old_paste, new_paste)

with open("index_html.h", "w") as f:
    f.write(html)

print("Chunked background copy implemented!")
