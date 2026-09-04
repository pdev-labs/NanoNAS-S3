import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Add copy/cut buttons to directory actions
old_dir_actions = r"""                            <div class="actions">
                                <a href="/download_dir?dir=${encodeURIComponent(fullPath)}" class="btn btn-text" title="Download ZIP"><span class="material-symbols-outlined">archive</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', true)" title="Delete Folder"><span class="material-symbols-outlined">delete</span></button>
                            </div>"""
new_dir_actions = r"""                            <div class="actions">
                                <button class="btn btn-text" onclick="cutFile('${fullPath}')" title="Cut"><span class="material-symbols-outlined">content_cut</span></button>
                                <button class="btn btn-text" onclick="copyFile('${fullPath}')" title="Copy"><span class="material-symbols-outlined">content_copy</span></button>
                                <a href="/download_dir?dir=${encodeURIComponent(fullPath)}" class="btn btn-text" title="Download ZIP"><span class="material-symbols-outlined">archive</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', true)" title="Delete Folder"><span class="material-symbols-outlined">delete</span></button>
                            </div>"""
code = code.replace(old_dir_actions, new_dir_actions)

# 2. Add copy/cut buttons to file actions
old_file_actions = r"""                            <div class="actions">
                                ${playBtn}
                                <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn btn-text" download title="Download"><span class="material-symbols-outlined">download</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', false)" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                            </div>"""
new_file_actions = r"""                            <div class="actions">
                                ${playBtn}
                                <button class="btn btn-text" onclick="cutFile('${fullPath}')" title="Cut"><span class="material-symbols-outlined">content_cut</span></button>
                                <button class="btn btn-text" onclick="copyFile('${fullPath}')" title="Copy"><span class="material-symbols-outlined">content_copy</span></button>
                                <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn btn-text" download title="Download"><span class="material-symbols-outlined">download</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', false)" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                            </div>"""
code = code.replace(old_file_actions, new_file_actions)

# 3. Add Paste button to header path-bar area
old_path_bar = r"""            <div class="path-bar">
                <span class="material-symbols-outlined">folder</span>
                <span id="current-path" style="font-weight: 500;">/</span>
            </div>"""
new_path_bar = r"""            <div class="path-bar" style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span class="material-symbols-outlined">folder</span>
                    <span id="current-path" style="font-weight: 500;">/</span>
                </div>
                <button id="paste-btn" class="btn btn-text" style="display:none; gap:4px;" onclick="pasteFile()">
                    <span class="material-symbols-outlined">content_paste</span> Paste
                </button>
            </div>"""
code = code.replace(old_path_bar, new_path_bar)

# 4. Add JS logic for clipboard
clipboard_js = r"""
        // --- Clipboard Logic ---
        function updatePasteButton() {
            let cb = localStorage.getItem('clipboard');
            let btn = document.getElementById('paste-btn');
            if (cb) {
                btn.style.display = 'flex';
                let data = JSON.parse(cb);
                btn.title = `Paste ${data.path}`;
            } else {
                btn.style.display = 'none';
            }
        }
        function copyFile(path) {
            localStorage.setItem('clipboard', JSON.stringify({action: 'copy', path: path}));
            updatePasteButton();
        }
        function cutFile(path) {
            localStorage.setItem('clipboard', JSON.stringify({action: 'cut', path: path}));
            updatePasteButton();
        }
        async function pasteFile() {
            let cb = localStorage.getItem('clipboard');
            if (!cb) return;
            let data = JSON.parse(cb);
            
            let sourcePath = data.path;
            let sourceName = sourcePath.substring(sourcePath.lastIndexOf('/') + 1);
            let destPath = currentDir + "/" + sourceName;
            if (currentDir === "/") destPath = "/" + sourceName;
            if (sourcePath === destPath) return; // Same location
            
            let endpoint = data.action === 'cut' ? '/api/move' : '/api/copy';
            
            try {
                // Show loading spinner for copy since it takes a while
                if (data.action === 'copy') {
                    document.getElementById('file-list').innerHTML = `<li class="file-item" style="justify-content:center;">Copying... this may take a while.</li>`;
                }
                
                let res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                });
                if(res.ok) {
                    if (data.action === 'cut') {
                        localStorage.removeItem('clipboard'); // clear clipboard on move
                    }
                    loadFiles();
                    updatePasteButton();
                } else {
                    alert(`Failed to ${data.action} file.`);
                    loadFiles();
                }
            } catch(e) {
                alert(`Error during ${data.action}.`);
                loadFiles();
            }
        }
        
        // Ensure paste button state is updated on load
        window.addEventListener('DOMContentLoaded', () => {
            updatePasteButton();
        });
"""
code = code.replace("// --- Drag and Drop File Moving ---", clipboard_js + "\n        // --- Drag and Drop File Moving ---")

# Add call to updatePasteButton() in loadFiles to ensure UI stays synced
code = code.replace("updateBreadcrumbs();", "updateBreadcrumbs();\n                updatePasteButton();")

with open("index_html.h", "w") as f:
    f.write(code)

print("index_html.h patched with clipboard logic!")
