import re

with open("esp32-s3-server.ino", "r") as f:
    code = f.read()

tar_class = """
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
        addHeader("Content-Disposition", "attachment; filename=\\"" + tarName + ".tar\\"");
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
"""

code = code.replace("void setup() {", tar_class + "\\nvoid setup() {")

with open("esp32-s3-server.ino", "w") as f:
    f.write(code)

print("Done injecting TarResponse!")
