#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include "EspUsbHost.h"

// Define the Wi-Fi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "gxtcgc599h5rb8d";

AsyncWebServer server(80);

EspUsbHost usb;
EspUsbHostMscFS usbMassStorage;

static uint32_t lastMountAttemptMs = 0;

// Helper to get mime type
String getContentType(String filename) {
  if (filename.endsWith(".html")) return "text/html";
  else if (filename.endsWith(".css")) return "text/css";
  else if (filename.endsWith(".js")) return "application/javascript";
  else if (filename.endsWith(".png")) return "image/png";
  else if (filename.endsWith(".gif")) return "image/gif";
  else if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) return "image/jpeg";
  else if (filename.endsWith(".mp4")) return "video/mp4";
  else if (filename.endsWith(".mp3")) return "audio/mpeg";
  else if (filename.endsWith(".wav")) return "audio/wav";
  else if (filename.endsWith(".webm")) return "video/webm";
  else if (filename.endsWith(".ogg")) return "audio/ogg";
  else if (filename.endsWith(".mkv")) return "video/x-matroska";
  return "application/octet-stream";
}

// HTML page embedded directly
const char* index_html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 File Share (Pro)</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --primary-color: #3b82f6;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --danger-color: #ef4444;
            --success-color: #10b981;
            --border-radius: 12px;
        }
        body { font-family: 'Segoe UI', sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 800px; width: 100%; background-color: var(--surface-color); border-radius: var(--border-radius); padding: 2rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        h1 { text-align: center; margin-top: 0; color: var(--primary-color); }
        .upload-area { border: 2px dashed var(--primary-color); border-radius: var(--border-radius); padding: 3rem; text-align: center; cursor: pointer; transition: background-color 0.3s; margin-bottom: 2rem; }
        .upload-area:hover, .upload-area.dragover { background-color: rgba(59, 130, 246, 0.1); }
        .file-list { list-style: none; padding: 0; margin: 0; }
        .file-item { display: flex; justify-content: space-between; align-items: center; padding: 1rem; background-color: rgba(255, 255, 255, 0.05); margin-bottom: 0.5rem; border-radius: 8px; }
        .file-info { display: flex; flex-direction: column; }
        .file-name { font-weight: bold; }
        .file-size { font-size: 0.85rem; color: var(--text-muted); }
        .actions button, .actions a { padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; color: white; font-weight: 500; margin-left: 0.5rem; transition: opacity 0.2s; display: inline-block; }
        .actions button:hover, .actions a:hover { opacity: 0.8; }
        .btn-download { background-color: var(--primary-color); }
        .btn-stream { background-color: var(--success-color); }
        .btn-delete { background-color: var(--danger-color); }
        #progress-bar-container { display: none; width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 8px; margin-top: 1rem; overflow: hidden; position: relative;}
        #progress-bar { height: 24px; width: 0%; background-color: var(--primary-color); transition: width 0.1s; }
        #progress-text { position: absolute; width: 100%; text-align: center; top: 2px; font-size: 0.85rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
    </style>
</head>
<body>
<div class="container">
    <h1>ESP32 File Share (Pro USB)</h1>
    <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
        <p>Drag & Drop massive files here (Chunked Uploads Enabled)</p>
        <input type="file" id="fileInput" style="display: none" onchange="handleFiles(this.files)">
    </div>
    <div id="progress-bar-container">
        <div id="progress-bar"></div>
        <div id="progress-text">0%</div>
    </div>
    <h2>Files (USB Drive)</h2>
    <ul class="file-list" id="fileList"></ul>
</div>
<script>
    const uploadArea = document.getElementById('uploadArea');
    const fileListEl = document.getElementById('fileList');
    const progressBarContainer = document.getElementById('progress-bar-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    loadFiles();
    
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
    uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
    
    function formatBytes(bytes, decimals = 2) { if (bytes === 0) return '0 Bytes'; const k = 1024; const dm = decimals < 0 ? 0 : decimals; const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']; const i = Math.floor(Math.log(bytes) / Math.log(k)); return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]; }
    
    function isMedia(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        return ['mp4', 'webm', 'ogg', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'gif'].includes(ext);
    }

    async function loadFiles() {
        try {
            const response = await fetch('/list');
            const files = await response.json();
            fileListEl.innerHTML = '';
            if(files.length === 0) { fileListEl.innerHTML = '<li class="file-item"><div class="file-info"><span class="file-name">No files found.</span></div></li>'; }
            files.forEach(file => {
                const li = document.createElement('li');
                li.className = 'file-item';
                
                let streamBtn = '';
                if(isMedia(file.name)) {
                    streamBtn = `<a href="/stream?file=${encodeURIComponent(file.name)}" class="btn-stream" target="_blank">Stream/View</a>`;
                }

                li.innerHTML = `
                    <div class="file-info">
                        <span class="file-name">${file.name}</span>
                        <span class="file-size">${formatBytes(file.size)}</span>
                    </div>
                    <div class="actions">
                        ${streamBtn}
                        <a href="/download?file=${encodeURIComponent(file.name)}" class="btn-download" download>Download</a>
                        <button class="btn-delete" onclick="deleteFile('${file.name}')">Delete</button>
                    </div>
                `;
                fileListEl.appendChild(li);
            });
        } catch (error) { console.error('Error loading files:', error); }
    }

    async function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];
        
        progressBarContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressText.innerText = '0%';
        
        // 4MB chunks for stable, fast uploading
        const chunkSize = 1024 * 1024 * 4; 
        const totalChunks = Math.ceil(file.size / chunkSize);
        let uploadedBytes = 0;

        for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);
            
            const append = (i === 0) ? '0' : '1';
            
            let success = false;
            let retries = 3;
            
            while (!success && retries > 0) {
                try {
                    const response = await fetch(`/upload_chunk?name=${encodeURIComponent(file.name)}&append=${append}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/octet-stream'
                        },
                        body: chunk
                    });
                    
                    if (response.ok) {
                        success = true;
                        uploadedBytes += (end - start);
                        const percent = ((uploadedBytes / file.size) * 100).toFixed(1);
                        progressBar.style.width = percent + '%';
                        progressText.innerText = percent + '% (Chunk ' + (i+1) + '/' + totalChunks + ')';
                    } else {
                        console.warn("Chunk failed, retrying...", retries);
                        retries--;
                        await new Promise(r => setTimeout(r, 1000));
                    }
                } catch (e) {
                    console.warn("Network error, retrying...", retries);
                    retries--;
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
            
            if (!success) {
                alert('Upload failed definitively at chunk ' + (i+1));
                progressBarContainer.style.display = 'none';
                return;
            }
        }
        
        progressText.innerText = 'Upload Complete!';
        setTimeout(() => {
            progressBarContainer.style.display = 'none';
            loadFiles();
        }, 1500);
    }

    async function deleteFile(filename) {
        if (!confirm('Are you sure you want to delete ' + filename + '?')) return;
        try { const response = await fetch('/delete?file=' + encodeURIComponent(filename), { method: 'DELETE' }); if (response.ok) { loadFiles(); } else { alert('Delete failed.'); } } catch (error) { console.error('Error deleting file:', error); }
    }
</script>
</body>
</html>
)rawliteral";


void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize USB Host
  usb.onDeviceConnected([](const EspUsbHostDeviceInfo &device) {
      Serial.print("USB connected: ");
      espUsbHostPrint(device); 
  });
  usb.onDeviceDisconnected([](const EspUsbHostDeviceInfo &device) {
      Serial.print("USB disconnected: ");
      espUsbHostPrint(device); 
  });
  
  if (!usb.begin()) {
      Serial.printf("usb.begin() failed: %s\n", usb.lastErrorName());
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  
  // OPTIMIZATION: Disable WiFi power saving mode and set max TX power
  WiFi.setSleep(false); 
  WiFi.setTxPower(WIFI_POWER_19_5dBm);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Root Page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/html", index_html);
  });

  // List Files
  server.on("/list", HTTP_GET, [](AsyncWebServerRequest *request){
    if (!usbMassStorage.mounted()) {
      request->send(500, "application/json", "[]");
      return;
    }

    String json = "[";
    File root = usbMassStorage.open("/");
    if (!root) {
      request->send(500, "application/json", "[]");
      return;
    }

    bool first = true;
    while (true) {
      File entry = root.openNextFile();
      if (!entry) break;

      if (!entry.isDirectory()) {
        if (!first) json += ",";
        json += "{\"name\":\"";
        json += entry.name();
        json += "\",\"size\":";
        json += entry.size();
        json += "}";
        first = false;
      }
      entry.close();
    }
    root.close();
    
    json += "]";
    request->send(200, "application/json", json);
  });

  // Download
  server.on("/download", HTTP_GET, [](AsyncWebServerRequest *request){
    if (!usbMassStorage.mounted()) return request->send(500, "text/plain", "USB Not Mounted");
    if (request->hasParam("file")) {
      String filename = request->getParam("file")->value();
      String path = "/" + filename;
      AsyncWebServerResponse *response = request->beginResponse(usbMassStorage, path, "application/octet-stream", true);
      response->addHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
      request->send(response);
    } else {
      request->send(400, "text/plain", "Missing file parameter");
    }
  });

  // Stream
  server.on("/stream", HTTP_GET, [](AsyncWebServerRequest *request){
    if (!usbMassStorage.mounted()) return request->send(500, "text/plain", "USB Not Mounted");
    if (request->hasParam("file")) {
      String filename = request->getParam("file")->value();
      String path = "/" + filename;
      String contentType = getContentType(filename);
      request->send(usbMassStorage, path, contentType);
    } else {
      request->send(400, "text/plain", "Missing file parameter");
    }
  });

  // Delete
  server.on("/delete", HTTP_DELETE, [](AsyncWebServerRequest *request){
    if (!usbMassStorage.mounted()) return request->send(500, "text/plain", "USB Not Mounted");
    if (request->hasParam("file")) {
      String path = "/" + request->getParam("file")->value();
      if (usbMassStorage.remove(path)) {
        request->send(200, "text/plain", "File Deleted");
      } else {
        request->send(500, "text/plain", "Delete Failed");
      }
    } else {
      request->send(400, "text/plain", "Missing file parameter");
    }
  });
  
  // Chunked Upload Endpoint (Requires raw struct definition for storing File)
  struct FileContext { File f; };

  server.on("/upload_chunk", HTTP_POST, 
    [](AsyncWebServerRequest *request){
      FileContext* ctx = (FileContext*)request->_tempObject;
      if (ctx) {
        if (ctx->f) ctx->f.close();
        delete ctx;
        request->_tempObject = NULL;
      }
      request->send(200, "text/plain", "Chunk OK");
    }, 
    NULL, 
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total){
      if (!usbMassStorage.mounted()) return;
      if (!request->hasParam("name")) return;
      
      FileContext* ctx = (FileContext*)request->_tempObject;
      
      if (!ctx && index == 0) {
        String filename = request->getParam("name")->value();
        String path = "/" + filename;
        bool append = request->hasParam("append") && request->getParam("append")->value() == "1";
        
        ctx = new FileContext();
        ctx->f = usbMassStorage.open(path, append ? FILE_APPEND : FILE_WRITE);
        request->_tempObject = ctx;
      }
      
      if(ctx && ctx->f) {
        ctx->f.write(data, len);
      }
    }
  );

  server.begin();
  Serial.println("Async HTTP server started");
}

void loop() {
  if (!usbMassStorage.mounted()) {
      const uint32_t now = millis();
      if (now - lastMountAttemptMs >= 1000) {
          lastMountAttemptMs = now;
          if (usbMassStorage.begin(usb, "/usb")) {
              Serial.println("USB Mounted Successfully");
          }
      }
  }
  delay(10);
}
