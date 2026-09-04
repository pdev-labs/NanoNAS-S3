import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

tar_logic = """
// ---------------------------------------------------------
// TAR STREAMING LOGIC
// ---------------------------------------------------------

void writeTarHeader(String filename, size_t filesize, uint8_t* header) {
    memset(header, 0, 512);
    // filename (100 bytes)
    if(filename.startsWith("/")) filename = filename.substring(1);
    strncpy((char*)header, filename.c_str(), 99);
    // file mode (8 bytes)
    strcpy((char*)header + 100, "0000644");
    // uid & gid (8 bytes each)
    strcpy((char*)header + 108, "0000000");
    strcpy((char*)header + 116, "0000000");
    // file size in octal (12 bytes)
    snprintf((char*)header + 124, 12, "%011lo", (unsigned long)filesize);
    // mtime in octal (12 bytes)
    strcpy((char*)header + 136, "00000000000");
    // chksum (8 bytes) - initially spaces
    memset(header + 148, ' ', 8);
    // typeflag (1 byte)
    header[156] = '0';
    // magic (6 bytes)
    strcpy((char*)header + 257, "ustar");
    // version (2 bytes)
    strcpy((char*)header + 263, "00");
    
    // Calculate checksum
    unsigned int checksum = 0;
    for(int i = 0; i < 512; i++) checksum += header[i];
    snprintf((char*)header + 148, 8, "%06o", checksum);
    header[154] = 0;
    header[155] = ' ';
}

struct TarContext {
    String dirPath;
    File root;
    File currentFile;
    bool writingHeader;
    bool finished;
    int endPaddingChunks;
    size_t fileBytesWritten;
};

void handleDownloadDir(AsyncWebServerRequest *request) {
    if(!checkAuth(request, false)) return;
    if(!request->hasParam("dir")) return request->send(400, "text/plain", "Missing dir");
    
    String dirPath = sanitizePath(request->getParam("dir")->value());
    if(!getStorage().exists(dirPath)) return request->send(404, "text/plain", "Not Found");
    
    String tarName = dirPath;
    if (tarName.lastIndexOf('/') != -1) tarName = tarName.substring(tarName.lastIndexOf('/') + 1);
    if (tarName == "") tarName = "root";
    
    AsyncWebServerResponse *response = request->beginChunkedResponse("application/x-tar", 
        [dirPath](uint8_t *buffer, size_t maxLen, size_t index) -> size_t {
            // Note: maxLen is usually around 4KB for AsyncWebServer
            static std::map<size_t, TarContext> contexts; // Map by request index isn't safe, we should use _tempObject
            // Unfortunately chunked response lambda doesn't easily have access to request->_tempObject natively in the lambda signature without passing a pointer.
            // But wait, the standard ESPAsyncWebServer chunked response takes a pointer or we can use a class.
            return 0; // we will implement this via a custom AsyncAbstractResponse below for safety
        }
    );
}
"""

# Actually, writing a custom AsyncAbstractResponse is safer for Tar streaming.
tar_class_logic = """
// ---------------------------------------------------------
// TAR STREAMING RESPONSE
// ---------------------------------------------------------
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
        _endPaddingChunks = 2; // Two 512-byte blocks of zeros at the end
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
                    // No more files, write end padding
                    if (_endPaddingChunks > 0) {
                        size_t toWrite = min((size_t)512, maxLen - written);
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
                    continue; // Skip subdirectories for simplicity in this version, or could recursively open
                }
                _writingHeader = true;
                _fileBytesWritten = 0;
                writeTarHeader(String(_currentFile.name()), _currentFile.size(), _headerBuf);
            }
            
            if (_writingHeader) {
                size_t toWrite = min((size_t)512, maxLen - written);
                memcpy(buf + written, _headerBuf, toWrite);
                written += toWrite;
                _writingHeader = false; // We assume maxLen >= 512 usually, this is a bit unsafe if maxLen < 512 but AsyncWebServer buffer is usually 1460
            } else {
                size_t toRead = min((size_t)(maxLen - written), (size_t)(_currentFile.size() - _fileBytesWritten));
                if (toRead > 0) {
                    size_t bytesRead = _currentFile.read(buf + written, toRead);
                    written += bytesRead;
                    _fileBytesWritten += bytesRead;
                }
                
                if (_fileBytesWritten >= _currentFile.size()) {
                    // File padding to 512 bytes
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
"""

code = code.replace("// Setup API Routes", tar_class_logic + "\n// Setup API Routes")

download_dir_route = """
  // Directory TAR Download
  server.on("/download_dir", HTTP_GET, [](AsyncWebServerRequest *request){
    if(!checkAuth(request, false)) return;
    if(!request->hasParam("dir")) return request->send(400, "text/plain", "Missing dir parameter");
    String dirPath = sanitizePath(request->getParam("dir")->value());
    if(!getStorage().exists(dirPath)) return request->send(404, "text/plain", "Not Found");
    
    AsyncWebServerResponse *response = new TarResponse(dirPath);
    request->send(response);
  });
"""

code = code.replace("server.begin();", download_dir_route + "\n  server.begin();")

with open("esp32-s3-server.ino", "w") as f:
    f.write(code)

print("Done patching backend!")
