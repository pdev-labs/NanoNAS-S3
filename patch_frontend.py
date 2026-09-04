import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Add Light Theme CSS
light_theme_css = """
        body.light-theme {
            --text-main: #1e293b;
            --text-muted: #64748b;
            --glass-bg: rgba(255, 255, 255, 0.7);
            --glass-border: rgba(0, 0, 0, 0.1);
            background: linear-gradient(-45deg, #f8fafc, #e2e8f0, #cbd5e1, #f1f5f9);
        }
        body.light-theme h1 { color: #0f172a; text-shadow: none; }
        body.light-theme .stat-card { background: rgba(0, 0, 0, 0.03); }
        body.light-theme .stat-card:hover { background: rgba(0, 0, 0, 0.05); }
        body.light-theme .stat-val { color: #0f172a; }
        body.light-theme .file-item { background: rgba(0,0,0, 0.03); }
        body.light-theme .file-item:hover { background: rgba(0,0,0, 0.06); }
        body.light-theme .btn-delete { color: #ef4444; background: rgba(239, 68, 68, 0.1); }
        body.light-theme .upload-area { background: rgba(59, 130, 246, 0.05); }
        body.light-theme .upload-area p { color: #1d4ed8; }
        body.light-theme textarea { background: rgba(255, 255, 255, 0.5) !important; color: #1e293b !important; }
"""
code = code.replace("</style>", light_theme_css + "</style>")

# 2. Add Theme Toggle Button
old_header = """<button class="btn-primary" onclick="logout()" style="background:var(--danger)">Logout</button>"""
new_header = """<button class="btn-primary" onclick="toggleTheme()" style="background:#8b5cf6">🌗 Theme</button>
            <button class="btn-primary" onclick="logout()" style="background:var(--danger)">Logout</button>"""
code = code.replace(old_header, new_header)

# 3. Add Editor Modal HTML
editor_modal_html = """
    <!-- Text Editor Modal -->
    <div id="editorModal" class="modal" onclick="if(event.target==this) this.style.display='none'">
        <div style="background:var(--glass-bg); padding:20px; border-radius:12px; width:90%; max-width:800px; height:80vh; display:flex; flex-direction:column; gap:10px; border:1px solid var(--glass-border); backdrop-filter:blur(16px); margin:auto; margin-top:5vh;">
            <h3 id="editorTitle" style="margin:0;">Editing...</h3>
            <textarea id="editorContent" style="flex:1; padding:10px; border-radius:8px; border:1px solid var(--glass-border); background:rgba(0,0,0,0.3); color:var(--text-main); font-family:monospace; resize:none;"></textarea>
            <div style="display:flex; justify-content:flex-end; gap:10px;">
                <button onclick="document.getElementById('editorModal').style.display='none'">Cancel</button>
                <button class="btn-primary" onclick="saveEditor()">Save File</button>
            </div>
        </div>
    </div>
"""
code = code.replace('<div id="mediaModal"', editor_modal_html + '\n    <div id="mediaModal"')

# 4. Modify Input File
code = code.replace('<input type="file" id="fileInput" style="display: none;" onchange="handleFiles(this.files)">', '<input type="file" id="fileInput" style="display: none;" multiple onchange="handleFiles(this.files)">')

# 5. Add JS Logic for Theme & Editor
js_additions = """
    // Theme logic
    if(localStorage.getItem('theme') === 'light') document.body.classList.add('light-theme');
    function toggleTheme() {
        document.body.classList.toggle('light-theme');
        localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
    }

    // Text Editor logic
    let editingPath = "";
    async function openEditor(path, name) {
        editingPath = path;
        document.getElementById('editorTitle').innerText = 'Editing: ' + name;
        document.getElementById('editorContent').value = 'Loading...';
        document.getElementById('editorModal').style.display = 'flex';
        
        try {
            let res = await fetch(`/stream?file=${encodeURIComponent(path)}`);
            if(!res.ok) throw new Error("Failed to load");
            let text = await res.text();
            document.getElementById('editorContent').value = text;
        } catch(e) {
            document.getElementById('editorContent').value = "Error loading file.";
        }
    }
    
    async function saveEditor() {
        let content = document.getElementById('editorContent').value;
        let btn = document.querySelector('#editorModal .btn-primary');
        let oldText = btn.innerText;
        btn.innerText = "Saving...";
        
        try {
            let res = await fetch(`/upload_chunk?name=${encodeURIComponent(editingPath)}&append=0`, { 
                method: 'POST', 
                body: new Blob([content]) 
            });
            if(res.ok) {
                alert("File saved successfully!");
                document.getElementById('editorModal').style.display = 'none';
            } else alert("Failed to save.");
        } catch(e) {
            alert("Error saving.");
        }
        btn.innerText = oldText;
        loadFiles();
    }
"""
code = code.replace("let currentDir = \"/\";", "let currentDir = \"/\";" + js_additions)

# 6. Replace `handleFiles(files)` with Batch Upload logic
# We use regex to match the old handleFiles block
old_handle_files = re.search(r'    async function handleFiles\(files\) \{.*?\n        pText\.innerText = \'Upload Complete!\';\n        setTimeout\(\(\) => \{ pContainer\.style\.display = \'none\'; loadFiles\(\); \}, 1000\);\n    \}', code, re.DOTALL)

batch_logic = """
    async function handleFiles(files) {
        if (!files || files.length === 0) return;
        const pContainer = document.getElementById('progress-bar-container');
        const pBar = document.getElementById('progress-bar');
        const pText = document.getElementById('progress-text');
        
        pContainer.style.display = 'block';

        for (let idx = 0; idx < files.length; idx++) {
            const file = files[idx];
            if (file.size > 1.5 * 1024 * 1024 && currentDir === "/" && !document.querySelector('.storage-bar-fill')) { 
                // Only warn if they're likely on LittleFS (storage bar fill doesn't exist for LittleFS in stats right now wait no... just let it fail or upload)
                // Actually let's just omit this specific check and let the upload fail if they are out of space.
            }
            
            pBar.style.width = '0%';
            pText.innerText = `[${idx+1}/${files.length}] Uploading ${file.name} (0%)`;
            
            const chunkSize = 1024 * 256; 
            const totalChunks = Math.ceil(file.size / chunkSize) || 1;
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
                        const response = await fetch(`/upload_chunk?name=${encodeURIComponent(fullPath)}&append=${append}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/octet-stream' },
                            body: chunk
                        });
                        if (response.ok) {
                            success = true;
                            uploadedBytes += (end - start);
                            const percent = ((uploadedBytes / file.size) * 100).toFixed(1);
                            pBar.style.width = percent + '%';
                            pText.innerText = `[${idx+1}/${files.length}] Uploading ${file.name} (${percent}%)`;
                        } else {
                            retries--;
                            await new Promise(r => setTimeout(r, 1000));
                        }
                    } catch (e) {
                        retries--;
                        await new Promise(r => setTimeout(r, 1000));
                    }
                }
                if (!success) {
                    alert(`Upload failed for ${file.name}`);
                    break;
                }
            }
        }
        pText.innerText = 'All Uploads Complete!';
        setTimeout(() => { pContainer.style.display = 'none'; loadFiles(); }, 1000);
    }
"""

if old_handle_files:
    code = code.replace(old_handle_files.group(0), batch_logic)
else:
    print("Warning: old_handle_files regex failed")


# 7. Add ZIP Button and Text Editor to render block
code = code.replace("🗑️ Delete</button>", "🗑️ Delete</button>\n                            <a href=\"/download_dir?dir=${encodeURIComponent(fullPath)}\" class=\"btn-download\">📦 Zip</a>")

text_exts = "['txt', 'csv', 'json', 'md', 'ino', 'js', 'css', 'html', 'py']"
code = code.replace("function isPlayable(name) {", f"""function isTextFile(name) {{ return {text_exts}.includes(name.split('.').pop().toLowerCase()); }}\n    function isPlayable(name) {{""")
code = code.replace("['mp4', 'webm', 'mp3', 'wav', 'ogg', 'jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);", "['mp4', 'webm', 'mp3', 'wav', 'ogg', 'jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext) || isTextFile(name);")

play_media_render = """        } else {
            container.innerHTML = `<audio controls autoplay style="width:300px;"><source src="${url}" type="audio/${ext}"></audio>`;
        }"""
new_play_media_render = """        } else if (isTextFile(name)) {
            closeModal();
            return openEditor(path, name);
        } else {
            container.innerHTML = `<audio controls autoplay style="width:300px;"><source src="${url}" type="audio/${ext}"></audio>`;
        }"""
code = code.replace(play_media_render, new_play_media_render)


with open("index_html.h", "w") as f:
    f.write(code)

print("Done patching frontend!")
