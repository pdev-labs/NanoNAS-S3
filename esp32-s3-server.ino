#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include <DNSServer.h>
#include "index_html.h"
#include "EspUsbHost.h"
#include <ESPmDNS.h>
#include <Update.h>


EspUsbHost usb;
EspUsbHostMscFS usbMassStorage;
static uint32_t lastMountAttemptMs = 0;

fs::FS& getStorage() {
  if (usbMassStorage.mounted()) {
    return usbMassStorage;
  }
  return LittleFS;
}



// Configuration
const char* ap_ssid = "NanoNAS";
const char* ap_pass = "nanopass";
const char* sta_ssid = "vivo T4x 5G";
const char* sta_pass = "gxtcgc599h5rb8d";


AsyncWebServer server(80);
DNSServer dnsServer;

// User Management
struct AppUser {
  String username;
  String password;
  String role;
};
std::vector<AppUser> users;

void loadUsers() {
  users.clear();
  if (LittleFS.exists("/users.json")) {
    File f = LittleFS.open("/users.json", "r");
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, f);
    f.close();
    JsonArray arr = doc.as<JsonArray>();
    for (JsonObject u : arr) {
      AppUser user;
      user.username = u["username"].as<String>();
      user.password = u["password"].as<String>();
      user.role = u["role"].as<String>();
      users.push_back(user);
    }
  }
  // Ensure default admin exists
  if (users.empty()) {
    users.push_back({"admin", "admin", "admin"});
  }
}

void saveUsers() {
  DynamicJsonDocument doc(1024);
  JsonArray arr = doc.to<JsonArray>();
  for (auto& u : users) {
    JsonObject obj = arr.createNestedObject();
    obj["username"] = u.username;
    obj["password"] = u.password;
    obj["role"] = u.role;
  }
  File f = LittleFS.open("/users.json", "w");
  serializeJson(doc, f);
  f.close();
}

AppUser* getAuthenticatedUser(AsyncWebServerRequest *request) {
  for (auto& u : users) {
    if (request->authenticate(u.username.c_str(), u.password.c_str())) {
      return &u;
    }
  }
  return nullptr;
}

bool checkAuth(AsyncWebServerRequest *request, bool requireAdmin = false) {
  AppUser* u = getAuthenticatedUser(request);
  if (!u) {
    request->requestAuthentication();
    return false;
  }
  if (requireAdmin && u->role != "admin") {
    request->send(403, "text/plain", "Forbidden: Admin access required");
    return false;
  }
  return true;
}




// Helper to copy files and directories recursively
bool copyRecursive(String srcPath, String destPath) {
  fs::File src = getStorage().open(srcPath, "r");
  if (!src) return false;

  if (!src.isDirectory()) {
    fs::File dest = getStorage().open(destPath, "w");
    if (!dest) { src.close(); return false; }
    
    uint8_t *buf = (uint8_t *)malloc(4096);
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

// Helper to get mime type
String getContentType(String filename) {
  if (filename.endsWith(".html")) return "text/html";
  else if (filename.endsWith(".css")) return "text/css";
  else if (filename.endsWith(".js")) return "application/javascript";
  else if (filename.endsWith(".png")) return "image/png";
  else if (filename.endsWith(".gif")) return "image/gif";
  else if (filename.endsWith(".jpg") || filename.endsWith(".jpeg")) return "image/jpeg";
  else if (filename.endsWith(".ico")) return "image/x-icon";
  else if (filename.endsWith(".xml")) return "text/xml";
  else if (filename.endsWith(".pdf")) return "application/pdf";
  else if (filename.endsWith(".zip")) return "application/zip";
  else if (filename.endsWith(".mp4")) return "video/mp4";
  else if (filename.endsWith(".mp3")) return "audio/mpeg";
  else if (filename.endsWith(".wav")) return "audio/wav";
  return "application/octet-stream";
}

String sanitizePath(String path) {
  if (!path.startsWith("/")) path = "/" + path;
  return path;
}


class TarResponse : public AsyncAbstractResponse {
private:
    String _dirPath;
    File _root;
    File _currentFile;
    uint8_t _headerBuf[512];
    bool _writingHeader;
    bool _finished;
    int _endPaddingChunks;
    size_t _fileBytesWritten;

    void writeTarHeader(String filename, size_t filesize, uint8_t* header) {
        memset(header, 0, 512);
        if(filename.startsWith("/")) filename = filename.substring(1);
        strncpy((char*)header, filename.c_str(), 99);
        strcpy((char*)header + 100, "0000644");
        strcpy((char*)header + 108, "0000000");
        strcpy((char*)header + 116, "0000000");
        snprintf((char*)header + 124, 12, "%011lo", (unsigned long)filesize);
        strcpy((char*)header + 136, "00000000000");
        memset(header + 148, ' ', 8);
        header[156] = '0';
        strcpy((char*)header + 257, "ustar");
        strcpy((char*)header + 263, "00");
        unsigned int checksum = 0;
        for(int i = 0; i < 512; i++) checksum += header[i];
        snprintf((char*)header + 148, 8, "%06o", checksum);
        header[154] = 0;
        header[155] = ' ';
    }

public:
    TarResponse(String dirPath) {
        _dirPath = dirPath;
        _code = 200;
        _contentType = "application/x-tar";
        _root = getStorage().open(dirPath);
        _writingHeader = false;
        _finished = false;
        _endPaddingChunks = 2; 
        _fileBytesWritten = 0;
        
        String tarName = dirPath;
        if (tarName.lastIndexOf('/') != -1) tarName = tarName.substring(tarName.lastIndexOf('/') + 1);
        if (tarName == "" || tarName == "/") tarName = "archive";
        addHeader("Content-Disposition", "attachment; filename=\"" + tarName + ".tar\"");
    }
    
    ~TarResponse() {
        if(_root) _root.close();
        if(_currentFile) _currentFile.close();
    }
    
    bool _sourceValid() const { return true; }
    
    virtual size_t _fillBuffer(uint8_t *buf, size_t maxLen) override {
        if(_finished) return 0;
        size_t written = 0;
        
        while (written < maxLen && !_finished) {
            if (!_currentFile) {
                _currentFile = _root.openNextFile();
                if (!_currentFile) {
                    if (_endPaddingChunks > 0) {
                        size_t toWrite = std::min((size_t)512, maxLen - written);
                        memset(buf + written, 0, toWrite);
                        written += toWrite;
                        _endPaddingChunks--;
                        if (_endPaddingChunks == 0) _finished = true;
                    } else {
                        _finished = true;
                    }
                    break;
                }
                if (_currentFile.isDirectory()) {
                    _currentFile.close();
                    continue; 
                }
                _writingHeader = true;
                _fileBytesWritten = 0;
                writeTarHeader(String(_currentFile.name()), _currentFile.size(), _headerBuf);
            }
            
            if (_writingHeader) {
                size_t toWrite = std::min((size_t)512, maxLen - written);
                memcpy(buf + written, _headerBuf, toWrite);
                written += toWrite;
                _writingHeader = false; 
            } else {
                size_t toRead = std::min((size_t)(maxLen - written), (size_t)(_currentFile.size() - _fileBytesWritten));
                if (toRead > 0) {
                    size_t bytesRead = _currentFile.read(buf + written, toRead);
                    written += bytesRead;
                    _fileBytesWritten += bytesRead;
                }
                
                if (_fileBytesWritten >= _currentFile.size()) {
                    size_t padding = 512 - (_currentFile.size() % 512);
                    if (padding == 512) padding = 0;
                    if (padding > 0 && maxLen - written >= padding) {
                        memset(buf + written, 0, padding);
                        written += padding;
                    }
                    _currentFile.close();
                }
            }
        }
        return written;
    }
};
void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize LittleFS
  if (!LittleFS.begin(true)) {
    Serial.println("An Error has occurred while mounting LittleFS");
  } else {
    Serial.println("LittleFS Mounted");
    loadUsers();
  }

  // Try connecting to Hotspot first (Station Mode)
  Serial.println("Attempting to connect to Hotspot...");
  WiFi.mode(WIFI_STA);
  WiFi.setHostname("nanonas");
  WiFi.begin(sta_ssid, sta_pass);
  
  // OPTIMIZATION: Disable WiFi power saving mode and set max TX power
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to Hotspot successfully!");
    Serial.print("NAS IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    // Fallback to AP_STA Mode so it hosts the network BUT keeps trying to connect to the hotspot
    Serial.println("Hotspot not found. Falling back to AP Mode...");
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP(ap_ssid, ap_pass);
    Serial.print("AP IP Address: ");
    Serial.println(WiFi.softAPIP());
    
    // Captive Portal DNS only needed in AP Mode
    dnsServer.start(53, "*", WiFi.softAPIP());
  }
  
  // mDNS
  if (!MDNS.begin("nanonas")) {
    Serial.println("Error setting up MDNS responder!");
  } else {
    Serial.println("mDNS responder started (nanonas.local)");
    MDNS.addService("http", "tcp", 80);
  }

  // HTTP Routes
  // -----------------------------------------------------
  // Root Page (Captive Portal fallback included)
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    request->send(200, "text/html", index_html);
  });

  // Captive Portal Redirect for Android/iOS
  server.onNotFound([](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    request->redirect("/");
  });
  
  // System Telemetry Endpoint
  server.on("/sysinfo", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    
    String json;
    DynamicJsonDocument doc(256);
    doc["freeHeap"] = ESP.getFreeHeap();
    doc["uptime"] = millis() / 1000;
    doc["rssi"] = WiFi.status() == WL_CONNECTED ? WiFi.RSSI() : 0;
    doc["usedBytes"] = usbMassStorage.mounted() ? 0 : LittleFS.usedBytes();
    doc["totalBytes"] = usbMassStorage.mounted() ? 0 : LittleFS.totalBytes();
    serializeJson(doc, json);
    request->send(200, "application/json", json);
  });


  // API: Get Users
  server.on("/api/users", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    String json;
    DynamicJsonDocument doc(1024);
    JsonArray arr = doc.to<JsonArray>();
    for (auto& u : users) {
      JsonObject obj = arr.createNestedObject();
      obj["username"] = u.username;
      obj["role"] = u.role;
    }
    serializeJson(doc, json);
    request->send(200, "application/json", json);
  });

  // API: Add User
  server.on("/api/users", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if (request->hasParam("username", true) && request->hasParam("password", true) && request->hasParam("role", true)) {
      AppUser u;
      u.username = request->getParam("username", true)->value();
      u.password = request->getParam("password", true)->value();
      u.role = request->getParam("role", true)->value();
      users.push_back(u);
      saveUsers();
      request->send(200, "text/plain", "OK");
    } else {
      request->send(400, "text/plain", "Missing params");
    }
  });

  // API: Delete User
  server.on("/api/users", HTTP_DELETE, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if (request->hasParam("username")) {
      String uname = request->getParam("username")->value();
      // Don't delete last admin
      int adminCount = 0;
      for (auto& u : users) if (u.role == "admin") adminCount++;
      
      for (auto it = users.begin(); it != users.end(); ++it) {
        if (it->username == uname) {
          if (it->role == "admin" && adminCount <= 1) {
             request->send(400, "text/plain", "Cannot delete last admin");
             return;
          }
          users.erase(it);
          saveUsers();
          request->send(200, "text/plain", "OK");
          return;
        }
      }
      request->send(404, "text/plain", "User not found");
    } else {
      request->send(400, "text/plain", "Missing username");
    }
  });

  // List Files and Folders
  server.on("/list", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    
    String dirPath = "/";
    if (request->hasParam("dir")) dirPath = sanitizePath(request->getParam("dir")->value());
    
    File root = getStorage().open(dirPath);
    if (!root || !root.isDirectory()) return request->send(500, "application/json", "[]");

    String json = "[";
    bool first = true;
    while (true) {
      File entry = root.openNextFile();
      if (!entry) break;

      if (!first) json += ",";
      json += "{\"name\":\"";
      String name = String(entry.name());
      // LittleFS openNextFile returns full path sometimes, we just want the basename
      int lastSlash = name.lastIndexOf('/');
      if (lastSlash >= 0) name = name.substring(lastSlash + 1);
      
      json += name;
      json += "\",\"isDir\":";
      json += entry.isDirectory() ? "true" : "false";
      json += ",\"size\":";
      json += entry.size();
      json += "}";
      
      first = false;
      entry.close();
    }
    root.close();
    json += "]";
    request->send(200, "application/json", json);
  });

  // Make Directory
  server.on("/mkdir", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if (request->hasParam("dir")) {
      String path = sanitizePath(request->getParam("dir")->value());
      if (getStorage().mkdir(path)) request->send(200, "text/plain", "OK");
      else request->send(500, "text/plain", "Failed to create folder");
    } else {
      request->send(400, "text/plain", "Missing dir param");
    }
  });

  // Download
  server.on("/download", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    if (request->hasParam("file")) {
      String path = sanitizePath(request->getParam("file")->value());
      if (!getStorage().exists(path)) return request->send(404, "text/plain", "Not Found");

      String filename = path.substring(path.lastIndexOf('/') + 1);
      AsyncWebServerResponse *response = request->beginResponse(LittleFS, path, "application/octet-stream", true);
      response->addHeader("Content-Disposition", "attachment; filename=\"" + filename + "\"");
      request->send(response);
    }
  });

  // Stream
  server.on("/stream", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    if (request->hasParam("file")) {
      String path = sanitizePath(request->getParam("file")->value());
      if (!getStorage().exists(path)) return request->send(404, "text/plain", "Not Found");
      request->send(getStorage(), path, getContentType(path));
    }
  });


  // Delete File/Folder

  // API: Copy File/Folder
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

  // API: Move / Rename
  server.on("/api/move", HTTP_POST, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if(request->hasParam("from", true) && request->hasParam("to", true)) {
      String fromPath = sanitizePath(request->getParam("from", true)->value());
      String toPath = sanitizePath(request->getParam("to", true)->value());
      if(getStorage().rename(fromPath, toPath)) {
        request->send(200, "text/plain", "OK");
      } else {
        request->send(500, "text/plain", "Move failed");
      }
    } else {
      request->send(400, "text/plain", "Missing from or to parameter");
    }
  });

  server.on("/delete", HTTP_DELETE, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, true)) return;
    if (request->hasParam("file")) {
      String path = sanitizePath(request->getParam("file")->value());
      File f = getStorage().open(path);
      bool isDir = f && f.isDirectory();
      if(f) f.close();
      
      bool success = isDir ? getStorage().rmdir(path) : getStorage().remove(path);
      if (success) request->send(200, "text/plain", "Deleted");
      else request->send(500, "text/plain", "Failed");
    }
  });
  
  // Chunked Upload Endpoint
  struct FileContext { File f; };
  server.on("/upload_chunk", HTTP_POST, 
    [](AsyncWebServerRequest *request){
      if(!checkAuth(request, true)) return;
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
      if(!getAuthenticatedUser(request)) return;
      if (!request->hasParam("name")) return;
      
      FileContext* ctx = (FileContext*)request->_tempObject;
      if (!ctx && index == 0) {
        String path = sanitizePath(request->getParam("name")->value());
        bool append = request->hasParam("append") && request->getParam("append")->value() == "1";
        ctx = new FileContext();
        ctx->f = getStorage().open(path, append ? FILE_APPEND : FILE_WRITE);
        request->_tempObject = ctx;
      }
      if(ctx && ctx->f) ctx->f.write(data, len);
    }
  );

  // OTA Firmware Update
  server.on("/update", HTTP_POST, [](AsyncWebServerRequest *request) {
    if(!checkAuth(request, true)) return;
    bool shouldReboot = !Update.hasError();
    AsyncWebServerResponse *response = request->beginResponse(200, "text/plain", shouldReboot ? "OK" : "FAIL");
    response->addHeader("Connection", "close");
    request->send(response);
    if(shouldReboot) {
      delay(500);
      ESP.restart();
    }
  }, [](AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
    AppUser* u = getAuthenticatedUser(request);
    if (!u || u->role != "admin") return;
    if(!index){
      Serial.printf("Update Start: %s\n", filename.c_str());
      if(!Update.begin(UPDATE_SIZE_UNKNOWN)){
        Update.printError(Serial);
      }
    }
    if(!Update.hasError()){
      if(Update.write(data, len) != len){
        Update.printError(Serial);
      }
    }
    if(final){
      if(Update.end(true)){
        Serial.printf("Update Success: %uB\n", index+len);
      } else {
        Update.printError(Serial);
      }
    }
  });

  
  // Directory TAR Download
  server.on("/download_dir", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    if(!request->hasParam("dir")) return request->send(400, "text/plain", "Missing dir parameter");
    String dirPath = sanitizePath(request->getParam("dir")->value());
    if(!getStorage().exists(dirPath)) return request->send(404, "text/plain", "Not Found");
    
    AsyncWebServerResponse *response = new TarResponse(dirPath);
    request->send(response);
  });

  server.begin();
  Serial.println("Setup complete");
}

void loop() {
  dnsServer.processNextRequest();
  
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck > 5000) {
    lastCheck = millis();
    
    // If in STA mode and lost connection, switch to AP_STA to host WiFi while reconnecting
    if (WiFi.getMode() == WIFI_STA && WiFi.status() != WL_CONNECTED) {
      Serial.println("Lost Hotspot connection! Switching to AP Mode...");
      WiFi.mode(WIFI_AP_STA);
      WiFi.softAP(ap_ssid, ap_pass);
      dnsServer.start(53, "*", WiFi.softAPIP());
    }
    
    // If in AP_STA mode and hotspot comes back, switch back to STA to clean up
    if (WiFi.getMode() == WIFI_AP_STA && WiFi.status() == WL_CONNECTED) {
      Serial.println("Reconnected to Hotspot! Disabling AP Mode...");
      dnsServer.stop();
      WiFi.mode(WIFI_STA);
    }
  }

  delay(10);
}
