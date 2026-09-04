import re

with open("index_html.h", "r") as f:
    code = f.read()

# Add CSS for action bar and checkboxes
css_insert = """
        .action-bar {
            display: none;
            justify-content: space-between;
            align-items: center;
            background: var(--md-sys-color-secondary-container);
            color: var(--md-sys-color-on-secondary-container);
            padding: 12px 16px;
            border-radius: 12px;
            margin-bottom: 16px;
            animation: slideDown 0.3s cubic-bezier(0.2, 0, 0, 1);
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .action-bar .btn {
            background: transparent;
            color: var(--md-sys-color-on-secondary-container);
            padding: 8px;
        }
        .action-bar .btn:hover {
            background: rgba(0,0,0,0.1);
        }
        .checkbox-container {
            display: flex;
            align-items: center;
            margin-right: 12px;
        }
        .checkbox-container input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: var(--md-sys-color-primary);
            cursor: pointer;
        }
"""
code = code.replace("/* Global Styles */", "/* Global Styles */\n" + css_insert)

# Add Action Bar HTML
html_insert = """
            <div class="action-bar" id="actionBar">
                <div style="display:flex; align-items:center; gap:16px;">
                    <button class="icon-btn" onclick="clearSelection()"><span class="material-symbols-outlined">close</span></button>
                    <strong id="selectedCount">0 selected</strong>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn" onclick="bulkCut()"><span class="material-symbols-outlined">content_cut</span></button>
                    <button class="btn" onclick="bulkCopy()"><span class="material-symbols-outlined">content_copy</span></button>
                    <button class="btn" onclick="bulkDelete()" style="color:var(--md-sys-color-error)"><span class="material-symbols-outlined">delete</span></button>
                </div>
            </div>
"""
code = code.replace('<div class="breadcrumbs" id="breadcrumb" style="margin-bottom:0;"></div>', html_insert + '\n                <div class="breadcrumbs" id="breadcrumb" style="margin-bottom:0;"></div>')


# Modify JS variables
js_vars_insert = """
        let selectedItems = new Set();
"""
code = code.replace('let currentDir = "/";', 'let currentDir = "/";\n' + js_vars_insert)

# Modify render list to include checkboxes
old_render_file = """let li = document.createElement("li");
                    li.innerHTML = `
                        <div class="file-info" onclick="${f.isDir ? `openDir('${path}')` : ''}" style="cursor: ${f.isDir ? 'pointer' : 'default'}">
                            <span class="material-symbols-outlined file-icon">
                                ${f.isDir ? 'folder' : 'draft'}
                            </span>"""

new_render_file = """let li = document.createElement("li");
                    li.innerHTML = `
                        <div class="checkbox-container">
                            <input type="checkbox" onchange="toggleSelection('${path}', this.checked)" ${selectedItems.has(path) ? 'checked' : ''}>
                        </div>
                        <div class="file-info" onclick="${f.isDir ? `openDir('${path}')` : ''}" style="cursor: ${f.isDir ? 'pointer' : 'default'}">
                            <span class="material-symbols-outlined file-icon">
                                ${f.isDir ? 'folder' : 'draft'}
                            </span>"""
code = code.replace(old_render_file, new_render_file)

# Modify image thumbnail render
old_render_img = """let li = document.createElement("li");
                    li.innerHTML = `
                        <div class="file-info" onclick="window.open('/api/download?path=${encodeURIComponent(path)}', '_blank')" style="cursor: pointer">
                            <img data-src="/api/download?path=${encodeURIComponent(path)}" class="lazy-thumbnail file-icon" />"""

new_render_img = """let li = document.createElement("li");
                    li.innerHTML = `
                        <div class="checkbox-container">
                            <input type="checkbox" onchange="toggleSelection('${path}', this.checked)" ${selectedItems.has(path) ? 'checked' : ''}>
                        </div>
                        <div class="file-info" onclick="window.open('/api/download?path=${encodeURIComponent(path)}', '_blank')" style="cursor: pointer">
                            <img data-src="/api/download?path=${encodeURIComponent(path)}" class="lazy-thumbnail file-icon" />"""
code = code.replace(old_render_img, new_render_img)

# Clear selection on folder change
code = code.replace('currentDir = dir;', 'currentDir = dir;\n            clearSelection();')

# Add JS functions for multi-select
js_funcs_insert = """
        function toggleSelection(path, isChecked) {
            if (isChecked) {
                selectedItems.add(path);
            } else {
                selectedItems.delete(path);
            }
            updateActionBar();
        }

        function clearSelection() {
            selectedItems.clear();
            updateActionBar();
            // Uncheck all boxes visually
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        }

        function updateActionBar() {
            let bar = document.getElementById('actionBar');
            let count = document.getElementById('selectedCount');
            if (selectedItems.size > 0) {
                bar.style.display = 'flex';
                count.innerText = selectedItems.size + " selected";
            } else {
                bar.style.display = 'none';
            }
        }

        async function bulkDelete() {
            if (!confirm(`Delete ${selectedItems.size} items?`)) return;
            let items = Array.from(selectedItems);
            for (let i = 0; i < items.length; i++) {
                try {
                    await fetch('/api/delete?path=' + encodeURIComponent(items[i]), { method: 'DELETE' });
                } catch(e) { console.error("Error deleting", items[i], e); }
            }
            clearSelection();
            loadFiles();
        }

        function bulkCut() {
            let arr = Array.from(selectedItems).map(p => ({ action: 'move', path: p }));
            sessionStorage.setItem('clipboard', JSON.stringify(arr));
            clearSelection();
            updatePasteButton();
        }

        function bulkCopy() {
            let arr = Array.from(selectedItems).map(p => ({ action: 'copy', path: p }));
            sessionStorage.setItem('clipboard', JSON.stringify(arr));
            clearSelection();
            updatePasteButton();
        }
"""
code = code.replace('function openDir(dir) {', js_funcs_insert + '\n        function openDir(dir) {')

# Rewrite copyFile, cutFile, updatePasteButton, pasteFile to support arrays instead of single items
old_clipboard_funcs = """
        function copyFile(path) {
            sessionStorage.setItem('clipboard', JSON.stringify({action: 'copy', path: path}));
            updatePasteButton();
        }

        function cutFile(path) {
            sessionStorage.setItem('clipboard', JSON.stringify({action: 'move', path: path}));
            updatePasteButton();
        }

        function updatePasteButton() {
            let cb = sessionStorage.getItem('clipboard');
            let btn = document.getElementById('paste-btn');
            if (cb) {
                btn.style.display = 'flex';
            } else {
                btn.style.display = 'none';
            }
        }

        async function pasteFile() {
            let cb = sessionStorage.getItem('clipboard');
            if (!cb) return;
            let data = JSON.parse(cb);
            let sourcePath = data.path;
            let sourceName = sourcePath.substring(sourcePath.lastIndexOf('/') + 1);
            let destPath = currentDir + "/" + sourceName;
            if (currentDir === "/") destPath = "/" + sourceName;
            if (sourcePath === destPath) return; // Same location
            
            try {
                let res = await fetch(`/api/${data.action}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                });
                if (res.ok) {
                    sessionStorage.removeItem('clipboard');
                    updatePasteButton();
                    loadFiles();
                } else {
                    alert(`Failed to ${data.action} file.`);
                }
            } catch(e) {
                alert(`Error during ${data.action}.`);
            }
        }
"""

new_clipboard_funcs = """
        function copyFile(path) {
            sessionStorage.setItem('clipboard', JSON.stringify([{action: 'copy', path: path}]));
            updatePasteButton();
        }

        function cutFile(path) {
            sessionStorage.setItem('clipboard', JSON.stringify([{action: 'move', path: path}]));
            updatePasteButton();
        }

        function updatePasteButton() {
            let cb = sessionStorage.getItem('clipboard');
            let btn = document.getElementById('paste-btn');
            if (cb) {
                let arr = JSON.parse(cb);
                if (arr.length > 0) {
                    btn.style.display = 'flex';
                    btn.innerHTML = `<span class="material-symbols-outlined">content_paste</span> Paste ${arr.length} items`;
                    return;
                }
            }
            btn.style.display = 'none';
        }

        async function pasteFile() {
            let cb = sessionStorage.getItem('clipboard');
            if (!cb) return;
            let arr = JSON.parse(cb);
            let btn = document.getElementById('paste-btn');
            
            for (let i = 0; i < arr.length; i++) {
                let data = arr[i];
                let sourcePath = data.path;
                let sourceName = sourcePath.substring(sourcePath.lastIndexOf('/') + 1);
                let destPath = currentDir + "/" + sourceName;
                if (currentDir === "/") destPath = "/" + sourceName;
                if (sourcePath === destPath) continue; // Same location
                
                btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Pasting ${i+1}/${arr.length}...`;
                
                try {
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
                }
            }
            
            sessionStorage.removeItem('clipboard');
            updatePasteButton();
            loadFiles();
        }
"""
code = code.replace(old_clipboard_funcs.strip(), new_clipboard_funcs.strip())


with open("index_html.h", "w") as f:
    f.write(code)

print("index_html.h patched successfully for Multi-Select!")
