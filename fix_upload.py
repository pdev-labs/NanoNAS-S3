import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Remove the old handleFiles function (the one that only uploads files[0])
# 2. Add a new `uploadFile(file, index, total)` and `handleFiles(files)`

old_handle_files = re.search(r'async function handleFiles\(files\) \{.*?\}\n        \} catch \(e\) \{\}\n    \}', code, re.DOTALL)
if old_handle_files:
    code = code.replace(old_handle_files.group(0), "")
    
# Actually, let's just write the proper batch upload logic
batch_upload_logic = """
    async function handleFiles(files) {
        if (!files || files.length === 0) return;
        for (let i = 0; i < files.length; i++) {
            await uploadFile(files[i], i + 1, files.length);
        }
        loadFiles();
        document.getElementById('progress-bar-container').style.display = 'none';
    }

    async function uploadFile(file, currentIdx, totalFiles) {
        const pContainer = document.getElementById('progress-bar-container');
        const pBar = document.getElementById('progress-bar');
        const pText = document.getElementById('progress-text');
        
        pContainer.style.display = 'block';
        pBar.style.width = '0%';
        pText.innerText = `[${currentIdx}/${totalFiles}] Uploading ${file.name} (0%)`;
        
        const chunkSize = 1024 * 256; 
        const totalChunks = Math.ceil(file.size / chunkSize) || 1; // handle 0 byte files
        let uploadedBytes = 0;
        
        let fullPath = (currentDir === "/" ? "" : currentDir) + "/" + file.name;

        for (let i = 0; i < totalChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);
            const append = (i === 0) ? '0' : '1';
            
            let success = false;
            let retries = 3;
            
            while (!success && retries > 0) {
                try {
                    let res = await fetch(`/upload_chunk?name=${encodeURIComponent(fullPath)}&append=${append}`, {
                        method: 'POST',
                        body: chunk
                    });
                    if (res.ok) {
                        success = true;
                        uploadedBytes += chunk.size;
                        let pct = Math.round((uploadedBytes / file.size) * 100);
                        pBar.style.width = pct + '%';
                        pText.innerText = `[${currentIdx}/${totalFiles}] Uploading ${file.name} (${pct}%)`;
                    } else {
                        retries--;
                        if (retries === 0) throw new Error("Upload failed");
                        await new Promise(r => setTimeout(r, 1000));
                    }
                } catch (e) {
                    retries--;
                    if (retries === 0) { alert(`Failed to upload ${file.name}`); return; }
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
        }
    }
"""

# Find the end of `createFolder()`
create_folder_match = re.search(r'async function createFolder\(\) \{.*?\}\n    \}', code, re.DOTALL)
if create_folder_match:
    # Remove any existing handleFiles/uploadFile up to the start of "function isTextFile" or similar
    # Actually it's easier to just do a precise replace.
    pass

with open("index_html.h", "r") as f:
    lines = f.readlines()
    
out_lines = []
skip = False
for line in lines:
    if "async function handleFiles(files)" in line:
        skip = True
    if skip and line.strip() == "}":
        # Check if the next line is also part of it... it's hard to parse JS in python like this
        pass

