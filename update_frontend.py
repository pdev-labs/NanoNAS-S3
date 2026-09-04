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

# 2. Add Theme Toggle Button and Editor Modal HTML
old_header = """<button class="btn-primary" onclick="logout()" style="background:var(--danger)">Logout</button>"""
new_header = """<button class="btn-primary" onclick="toggleTheme()" style="background:#8b5cf6">🌗 Theme</button>
            <button class="btn-primary" onclick="logout()" style="background:var(--danger)">Logout</button>"""
code = code.replace(old_header, new_header)

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

# 3. Update Input File to multiple
code = code.replace('<input type="file" id="fileInput" style="display: none;" onchange="uploadFile()">', '<input type="file" id="fileInput" style="display: none;" multiple onchange="handleFiles(this.files)">')
code = code.replace('ondrop="event.preventDefault(); uploadFile(event.dataTransfer.files[0])"', 'ondrop="event.preventDefault(); handleFiles(event.dataTransfer.files)"')

# 4. JavaScript Logic for Theme, Editor, Batch Upload
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
            let formData = new FormData();
            formData.append("file", new Blob([content]), editingPath.split('/').pop());
            let res = await fetch(`/save?path=${encodeURIComponent(editingPath)}`, { method: 'POST', body: formData });
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

    // Batch Upload logic
    async function handleFiles(files) {
        if (!files || files.length === 0) return;
        for (let i = 0; i < files.length; i++) {
            await uploadFile(files[i], i + 1, files.length);
        }
    }
"""
code = code.replace("let currentDir = \"/\";", "let currentDir = \"/\";" + js_additions)

# Update uploadFile signature and UI update
code = re.sub(r'async function uploadFile\(file = null\) \{.*?(?=const formData)', 
"""async function uploadFile(fileObj, currentIdx, totalFiles) {
        const file = fileObj;
        if (!file) return;
        const progressBar = document.getElementById('uploadProgress');
        const progressBg = document.getElementById('uploadProgressBg');
        const uploadText = document.getElementById('uploadText');
        
        progressBg.style.display = 'block';
        if(totalFiles > 1) {
            uploadText.innerText = `Uploading file ${currentIdx} of ${totalFiles}...`;
        } else {
            uploadText.innerText = `Uploading ${file.name}...`;
        }
""", code, flags=re.DOTALL)

# Add "Download Folder" button for directories
code = code.replace("🗑️ Delete</button>", "🗑️ Delete</button>\n                            <a href=\"/download_dir?dir=${encodeURIComponent(fullPath)}\" class=\"btn-download\">📦 Zip</a>")

# Update isPlayable and file rendering to support text files
text_exts = "['txt', 'csv', 'json', 'md', 'ino', 'js', 'css', 'html']"
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

print("Done updating index_html.h")
