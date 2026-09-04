import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Update file rendering to include drag/drop handlers
old_dir_html = r"""                    if (file.isDir) {
                        li.innerHTML = `
                            ${iconHtml}
                            <div class="file-info">
                                <span class="file-name" onclick="changeDir('${fullPath}')">${file.name}</span>
                                <span class="file-size">-</span>
                            </div>
                            <div class="actions">
                                <a href="/download_dir?dir=${encodeURIComponent(fullPath)}" class="btn btn-text" title="Download ZIP"><span class="material-symbols-outlined">archive</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', true)" title="Delete Folder"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    } else {"""
                    
new_dir_html = r"""                    if (file.isDir) {
                        li.setAttribute('draggable', 'true');
                        li.setAttribute('ondragstart', `dragStart(event, '${fullPath}')`);
                        li.setAttribute('ondragover', `dragOver(event)`);
                        li.setAttribute('ondragleave', `dragLeave(event)`);
                        li.setAttribute('ondrop', `dropOnFolder(event, '${fullPath}')`);
                        li.innerHTML = `
                            ${iconHtml}
                            <div class="file-info">
                                <span class="file-name" onclick="changeDir('${fullPath}')">${file.name}</span>
                                <span class="file-size">-</span>
                            </div>
                            <div class="actions">
                                <a href="/download_dir?dir=${encodeURIComponent(fullPath)}" class="btn btn-text" title="Download ZIP"><span class="material-symbols-outlined">archive</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', true)" title="Delete Folder"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    } else {"""
                    
code = code.replace(old_dir_html, new_dir_html)

old_file_html = r"""                    } else {
                        let playBtn = isPlayable ? `<button class="btn btn-text" onclick="playMedia('${fullPath}', '${file.name}')" title="View/Play"><span class="material-symbols-outlined">${isImg||isTxt?'visibility':'play_arrow'}</span></button>` : '';
                        li.innerHTML = `
                            ${iconHtml}
                            <div class="file-info">
                                <span class="file-name" onclick="${isPlayable ? `playMedia('${fullPath}', '${file.name}')` : ''}">${file.name}</span>
                                <span class="file-size">${formatBytes(file.size)}</span>
                            </div>
                            <div class="actions">
                                ${playBtn}
                                <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn btn-text" download title="Download"><span class="material-symbols-outlined">download</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', false)" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    }"""
                    
new_file_html = r"""                    } else {
                        li.setAttribute('draggable', 'true');
                        li.setAttribute('ondragstart', `dragStart(event, '${fullPath}')`);
                        let playBtn = isPlayable ? `<button class="btn btn-text" onclick="playMedia('${fullPath}', '${file.name}')" title="View/Play"><span class="material-symbols-outlined">${isImg||isTxt?'visibility':'play_arrow'}</span></button>` : '';
                        li.innerHTML = `
                            ${iconHtml}
                            <div class="file-info">
                                <span class="file-name" onclick="${isPlayable ? `playMedia('${fullPath}', '${file.name}')` : ''}">${file.name}</span>
                                <span class="file-size">${formatBytes(file.size)}</span>
                            </div>
                            <div class="actions">
                                ${playBtn}
                                <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn btn-text" download title="Download"><span class="material-symbols-outlined">download</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', false)" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    }"""

code = code.replace(old_file_html, new_file_html)

# Add CSS for drag hover state
css_injection = r"""
        .file-item.drag-hover { background-color: var(--md-sys-color-primary-container); border: 2px dashed var(--md-sys-color-primary); }
"""
code = code.replace("</style>", css_injection + "</style>")

# Add Drag and Drop moving logic
dnd_js = r"""
        // --- Drag and Drop File Moving ---
        function dragStart(e, path) {
            e.dataTransfer.setData('text/plain', path);
            e.dataTransfer.effectAllowed = 'move';
        }
        function dragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('drag-hover');
        }
        function dragLeave(e) {
            e.currentTarget.classList.remove('drag-hover');
        }
        async function dropOnFolder(e, targetFolderPath) {
            e.preventDefault();
            e.currentTarget.classList.remove('drag-hover');
            
            // Check if OS files were dropped (Smart Upload)
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                let originalDir = currentDir;
                currentDir = targetFolderPath;
                await handleFiles(e.dataTransfer.files);
                currentDir = originalDir;
                loadFiles();
                return;
            }
            
            // Otherwise it's a move operation within the UI
            let sourcePath = e.dataTransfer.getData('text/plain');
            if (!sourcePath || sourcePath === targetFolderPath) return;
            
            let sourceName = sourcePath.substring(sourcePath.lastIndexOf('/') + 1);
            let destPath = targetFolderPath + "/" + sourceName;
            if (sourcePath === destPath) return; // Same location
            
            try {
                let res = await fetch('/api/move', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                });
                if(res.ok) {
                    loadFiles();
                } else {
                    alert("Failed to move file.");
                }
            } catch(e) {
                alert("Error moving file.");
            }
        }
"""
code = code.replace("// --- Upload Logic ---", dnd_js + "\n        // --- Upload Logic ---")

with open("index_html.h", "w") as f:
    f.write(code)

print("index_html.h patched with DnD!")
