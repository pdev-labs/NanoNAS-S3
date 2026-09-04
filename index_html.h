#pragma once
const char* index_html = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NanoNAS | Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --danger: #ef4444;
            --success: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --glass-bg: rgba(30, 41, 59, 0.6);
            --glass-border: rgba(255, 255, 255, 0.08);
            --radius: 16px;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        body { 
            font-family: 'Inter', sans-serif; 
            margin: 0; padding: 20px; 
            min-height: 100vh;
            color: var(--text-main);
            background: linear-gradient(-45deg, #0f172a, #1e3a8a, #0c4a6e, #020617);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            display: flex; flex-direction: column; align-items: center; 
        }

        .container { 
            width: 100%; max-width: 900px;
            background: var(--glass-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius);
            padding: 2rem; 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            margin-bottom: 2rem;
        }

        h1 { text-align: center; margin-top: 0; color: #fff; font-weight: 700; font-size: 2.2rem; letter-spacing: -0.5px; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        h1 span { color: var(--primary); }

        /* Dashboard Stats */
        .dashboard {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; margin-bottom: 2rem;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 12px; padding: 15px;
            display: flex; flex-direction: column; align-items: center;
            transition: transform 0.2s;
        }
        .stat-card:hover { transform: translateY(-2px); background: rgba(255, 255, 255, 0.05); }
        .stat-val { font-size: 1.5rem; font-weight: 600; color: #fff; }
        .stat-lbl { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 5px; }

        /* Storage Progress */
        .storage-bar-bg { width: 100%; height: 8px; background: rgba(0,0,0,0.3); border-radius: 4px; overflow: hidden; margin-top: 10px; }
        .storage-bar-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); width: 0%; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }

        /* Breadcrumb & Toolbar */
        .toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 10px; }
        .breadcrumb { display: flex; gap: 8px; font-size: 1.1rem; font-weight: 600; background: rgba(0,0,0,0.2); padding: 10px 15px; border-radius: 10px; }
        .breadcrumb a { color: var(--primary); text-decoration: none; cursor: pointer; transition: color 0.2s; }
        .breadcrumb a:hover { color: #60a5fa; }
        
        button { 
            padding: 10px 18px; border: none; border-radius: 8px; cursor: pointer; 
            font-weight: 600; font-family: 'Inter', sans-serif;
            color: white; transition: all 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .btn-primary { background: var(--primary); }
        .btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }

        /* Upload Area */
        .upload-area { 
            border: 2px dashed rgba(59, 130, 246, 0.5); border-radius: 12px; 
            padding: 2.5rem; text-align: center; cursor: pointer; 
            background: rgba(59, 130, 246, 0.05); margin-bottom: 2rem;
            transition: all 0.3s;
        }
        .upload-area:hover, .upload-area.dragover { background: rgba(59, 130, 246, 0.15); border-color: var(--primary); transform: scale(1.01); }
        .upload-area p { margin: 0; font-size: 1.1rem; color: #bfdbfe; }
        
        /* File List */
        .file-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
        .file-item { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 15px 20px; background: rgba(0, 0, 0, 0.2); 
            border: 1px solid transparent; border-radius: 12px; 
            transition: all 0.2s;
        }
        .file-item:hover { background: rgba(0, 0, 0, 0.3); border-color: var(--glass-border); transform: translateX(4px); }
        .file-info { display: flex; flex-direction: column; flex-grow: 1; cursor: pointer; }
        .file-name { font-weight: 600; font-size: 1.05rem; display: flex; align-items: center; gap: 10px;}
        .file-size { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; margin-left: 30px; }
        
        /* Actions */
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .actions button, .actions a { 
            padding: 8px 14px; font-size: 0.9rem; border-radius: 6px; 
            text-decoration: none; display: inline-flex; align-items: center; gap: 5px;
            box-shadow: none;
        }
        .btn-stream { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .btn-stream:hover { background: rgba(16, 185, 129, 0.4); }
        .btn-download { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
        .btn-download:hover { background: rgba(59, 130, 246, 0.4); }
        .btn-delete { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .btn-delete:hover { background: rgba(239, 68, 68, 0.4); }

        /* Progress Bar */
        #progress-bar-container { display: none; width: 100%; background: rgba(0,0,0,0.4); border-radius: 8px; margin: 1rem 0 2rem; position: relative; height: 28px; overflow: hidden; }
        #progress-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #3b82f6, #2dd4bf); transition: width 0.2s; }
        #progress-text { position: absolute; width: 100%; text-align: center; top: 5px; font-size: 0.85rem; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
        
        /* Media Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(5px); z-index: 1000; align-items: center; justify-content: center; }
        .modal-content { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 20px; max-width: 90%; max-height: 90%; position: relative; }
        .close-modal { position: absolute; top: -15px; right: -15px; background: var(--danger); width: 35px; height: 35px; border-radius: 50%; font-size: 20px; display: flex; align-items: center; justify-content: center; cursor: pointer; border: 2px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        media-player { max-width: 100%; border-radius: 8px; }

        @media (max-width: 600px) {
            .file-item { flex-direction: column; align-items: flex-start; gap: 15px; }
            .actions { width: 100%; justify-content: stretch; }
            .actions a, .actions button { flex: 1; justify-content: center; }
            .stat-card { padding: 10px; }
            .stat-val { font-size: 1.2rem; }
        }
    
        .media-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            font-size: 40px;
            color: rgba(255, 255, 255, 0.7);
            cursor: pointer;
            user-select: none;
            padding: 20px;
            transition: 0.2s;
            z-index: 2001;
        }
        .media-nav:hover { color: white; background: rgba(0,0,0,0.3); border-radius: 10px; }
        #mediaNavPrev { left: 20px; }
        #mediaNavNext { right: 20px; }
</style>
</head>
<body>

<div class="container">
    <h1>Nano<span>NAS</span></h1>
    
    <!-- Dashboard -->
    <div class="dashboard">
        <div class="stat-card">
            <div class="stat-val" id="stat-storage">-- / --</div>
            <div class="stat-lbl">Storage</div>
            <div class="storage-bar-bg"><div class="storage-bar-fill" id="storage-fill"></div></div>
        </div>
        <div class="stat-card">
            <div class="stat-val" id="stat-wifi">-- dBm</div>
            <div class="stat-lbl">Signal Strength</div>
        </div>
        <div class="stat-card">
            <div class="stat-val" id="stat-ram">-- KB</div>
            <div class="stat-lbl">Free RAM</div>
        </div>
        <div class="stat-card">
            <div class="stat-val" id="stat-uptime">--</div>
            <div class="stat-lbl">Uptime</div>
        </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
        <div class="breadcrumb" id="breadcrumb"></div>
        <button class="btn-primary" onclick="createFolder()">✨ New Folder</button>
        <button class="btn-primary" style="margin-left:10px; background:#e67e22;" onclick="openSettings()">⚙️ Settings</button>
    </div>

    <!-- File Upload -->
    <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
        <p>📁 Drag & Drop files here or click to browse</p>
        <input type="file" id="fileInput" style="display: none" onchange="handleFiles(this.files)">
    </div>
    
    <div id="progress-bar-container">
        <div id="progress-bar"></div>
        <div id="progress-text">0%</div>
    </div>
    
    <ul class="file-list" id="fileList"></ul>
</div>

<!-- Modal for Media -->
    <!-- Settings Modal -->
    <div id="settingsModal" class="modal">
        <div class="modal-content settings-modal">
            <span class="close-modal" onclick="closeSettings()">✕</span>
            <h2 style="margin-bottom:15px">System Settings</h2>
            
            <div class="settings-tabs">
                <button class="tab-btn active" onclick="switchTab('users')">👥 Users</button>
                <button class="tab-btn" onclick="switchTab('firmware')">🔄 Firmware Update</button>
            </div>
            
            <div id="tab-users" class="settings-section active">
                <h3>Access Control</h3>
                <div class="user-list" id="userList">
                    <!-- Users injected here -->
                </div>
                
                <h4 style="margin-top:15px">Add New User</h4>
                <div class="add-user-form">
                    <input type="text" id="newUsername" placeholder="Username" required>
                    <input type="password" id="newPassword" placeholder="Password" required>
                    <select id="newRole">
                        <option value="guest">Guest (Read-only)</option>
                        <option value="admin">Admin (Full Access)</option>
                    </select>
                    <button class="btn-stream" onclick="addUser()">➕ Add</button>
                </div>
            </div>
            
            <div id="tab-firmware" class="settings-section">
                <h3>Over-The-Air Update</h3>
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 15px;">
                    Select a compiled .bin file to update the ESP32 firmware wirelessly. The device will automatically reboot after completion.
                </p>
                <input type="file" id="otaInput" accept=".bin" style="margin-bottom:15px; color:white;">
                <button class="btn-upload" onclick="startOTA()">🚀 Flash Firmware</button>
                
                <div class="progress-bar-container" id="otaProgressContainer" style="display:none; margin-top:20px; background:rgba(0,0,0,0.5); height:20px; border-radius:10px;">
                    <div class="progress-bar-fill" id="otaProgressFill" style="width: 0%; background:#2ecc71; height:100%; border-radius:10px;"></div>
                </div>
                <div id="otaStatus" style="margin-top:10px; font-size:0.9rem; color:#aaa;"></div>
            </div>
        </div>
    </div>

<div class="modal" id="mediaModal">
    <div class="modal-content">
        <div class="close-modal" onclick="closeModal()">✕</div>
        <div id="mediaContainer"></div>
    </div>
</div>

<script>
    let currentDir = "/";
    let currentFiles = [];
    let currentMediaIndex = -1;
    let mediaList = [];

    const uploadArea = document.getElementById('uploadArea');
    const fileListEl = document.getElementById('fileList');
    const breadcrumbEl = document.getElementById('breadcrumb');
    
    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
    uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
    uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
    
    function formatBytes(bytes, decimals = 2) { 
        if (bytes === 0) return '0 B'; 
        const k = 1024; const dm = decimals < 0 ? 0 : decimals; 
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB']; 
        const i = Math.floor(Math.log(bytes) / Math.log(k)); 
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]; 
    }

    function formatTime(sec) {
        const h = Math.floor(sec / 3600);
        const m = Math.floor((sec % 3600) / 60);
        return h > 0 ? `${h}h ${m}m` : `${m}m ${sec % 60}s`;
    }
    
    function getIcon(name, isDir) {
        if (isDir) return '📁';
        const ext = name.split('.').pop().toLowerCase();
        if (['mp4','mkv','avi','webm'].includes(ext)) return '🎬';
        if (['mp3','wav','ogg'].includes(ext)) return '🎵';
        if (['jpg','jpeg','png','gif','webp'].includes(ext)) return '🖼️';
        if (['pdf','txt','md','doc'].includes(ext)) return '📄';
        if (['zip','rar','tar','gz'].includes(ext)) return '📦';
        return '📦';
    }

    function isPlayable(name) {
        const ext = name.split('.').pop().toLowerCase();
        return ['mp4', 'webm', 'mp3', 'wav', 'ogg', 'jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext);
    }
    
    function updateBreadcrumb() {
        let parts = currentDir.split('/').filter(p => p !== "");
        let html = `<a onclick="navigate('/')">🏠 Home</a>`;
        let path = "";
        for (let p of parts) {
            path += "/" + p;
            html += ` <span style="color:var(--text-muted)">/</span> <a onclick="navigate('${path}')">${p}</a>`;
        }
        breadcrumbEl.innerHTML = html;
    }

    function navigate(path) { currentDir = path; loadFiles(); }

    async function loadStats() {
        try {
            const res = await fetch('/sysinfo');
            const data = await res.json();
            
            document.getElementById('stat-ram').innerText = formatBytes(data.freeHeap);
            document.getElementById('stat-wifi').innerText = data.rssi + " dBm";
            document.getElementById('stat-uptime').innerText = formatTime(data.uptime);
            
            document.getElementById('stat-storage').innerText = `${formatBytes(data.usedBytes)} / ${formatBytes(data.totalBytes)}`;
            const pct = (data.usedBytes / data.totalBytes) * 100;
            document.getElementById('storage-fill').style.width = Math.min(pct, 100) + "%";
            
            if (pct > 90) document.getElementById('storage-fill').style.background = 'linear-gradient(90deg, #ef4444, #f97316)';
            else document.getElementById('storage-fill').style.background = 'linear-gradient(90deg, #3b82f6, #8b5cf6)';
        } catch(e) {}
    }

    async function loadFiles() {
        updateBreadcrumb();
        loadStats();
        try {
            const response = await fetch(`/list?dir=${encodeURIComponent(currentDir)}`);
            const files = await response.json();
            currentFiles = files;
            fileListEl.innerHTML = '';
            
            if (currentDir !== "/") {
                let parentDir = currentDir.substring(0, currentDir.lastIndexOf('/'));
                if (parentDir === "") parentDir = "/";
                const li = document.createElement('li');
                li.className = 'file-item';
                li.innerHTML = `<div class="file-info" onclick="navigate('${parentDir}')"><span class="file-name">🔙 .. (Go Back)</span></div>`;
                fileListEl.appendChild(li);
            }

            if(files.length === 0 && currentDir === "/") { 
                fileListEl.innerHTML += '<li class="file-item"><div class="file-info" style="align-items:center"><span class="file-name" style="color:var(--text-muted)">Empty directory</span></div></li>'; 
            }
            
            files.sort((a, b) => {
                if (a.isDir === b.isDir) return a.name.localeCompare(b.name);
                return a.isDir ? -1 : 1;
            });

            files.forEach(file => {
                const li = document.createElement('li');
                li.className = 'file-item';
                let fullPath = (currentDir === "/" ? "" : currentDir) + "/" + file.name;
                const icon = getIcon(file.name, file.isDir);
                
                if (file.isDir) {
                    li.innerHTML = `
                        <div class="file-info" onclick="navigate('${fullPath}')">
                            <span class="file-name">${icon} ${file.name}</span>
                        </div>
                        <div class="actions">
                            <button class="btn-delete" onclick="deleteFile('${fullPath}', true)">🗑️ Delete</button>
                        </div>
                    `;
                } else {
                    let isImg = ['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(file.name.split('.').pop().toLowerCase());
                    let btnText = isImg ? '👁️ View' : '▶️ Play';
                    let streamBtn = isPlayable(file.name) ? `<button class="btn-stream" onclick="playMedia('${fullPath}', '${file.name}')">${btnText}</button>` : '';
                    li.innerHTML = `
                        <div class="file-info">
                            <span class="file-name">${icon} ${file.name}</span>
                            <span class="file-size">${formatBytes(file.size)}</span>
                        </div>
                        <div class="actions">
                            ${streamBtn}
                            <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn-download" download>⬇️ Download</a>
                            <button class="btn-delete" onclick="deleteFile('${fullPath}', false)">🗑️ Delete</button>
                        </div>
                    `;
                }
                fileListEl.appendChild(li);
            });
        } catch (error) { console.error(error); }
    }
    
    async function createFolder() {
        let name = prompt("Enter new folder name:");
        if (!name) return;
        let path = (currentDir === "/" ? "" : currentDir) + "/" + name;
        try {
            const res = await fetch(`/mkdir?dir=${encodeURIComponent(path)}`, {method: 'POST'});
            if(res.ok) loadFiles();
            else alert("Failed to create folder");
        } catch (e) {}
    }

    async function handleFiles(files) {
        if (files.length === 0) return;
        const file = files[0];
        
        if (file.size > 1.5 * 1024 * 1024) {
            alert("File is too large for LittleFS! Limit is ~1.5MB.");
            return;
        }

        const pContainer = document.getElementById('progress-bar-container');
        const pBar = document.getElementById('progress-bar');
        const pText = document.getElementById('progress-text');
        
        pContainer.style.display = 'block';
        pBar.style.width = '0%';
        pText.innerText = '0%';
        
        const chunkSize = 1024 * 256; 
        const totalChunks = Math.ceil(file.size / chunkSize);
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
                        pText.innerText = percent + '% (Chunk ' + (i+1) + '/' + totalChunks + ')';
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
                alert('Upload failed definitively at chunk ' + (i+1));
                pContainer.style.display = 'none';
                return;
            }
        }
        pText.innerText = 'Upload Complete!';
        setTimeout(() => { pContainer.style.display = 'none'; loadFiles(); }, 1000);
    }

    async function deleteFile(path, isDir) {
        if (!confirm(`Are you sure you want to delete ${path}?`)) return;
        try { 
            const response = await fetch('/delete?file=' + encodeURIComponent(path), { method: 'DELETE' }); 
            if (response.ok) loadFiles(); 
            else alert('Delete failed. Make sure folder is empty.'); 
        } catch (error) { console.error('Error:', error); }
    }

    
    /* Settings Modal & Tabs */
    function openSettings() {
        document.getElementById('settingsModal').style.display = 'flex';
        loadUsers();
    }
    function closeSettings() {
        document.getElementById('settingsModal').style.display = 'none';
    }
    function switchTab(tabId) {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.settings-section').forEach(sec => sec.classList.remove('active'));
        event.target.classList.add('active');
        document.getElementById('tab-' + tabId).classList.add('active');
    }
    
    /* User Management */
    async function loadUsers() {
        try {
            let res = await fetch('/api/users');
            if (!res.ok) throw new Error('Unauthorized');
            let users = await res.json();
            let html = '';
            users.forEach(u => {
                let badge = u.role === 'admin' ? '<span style="color:#e74c3c">[Admin]</span>' : '<span style="color:#2ecc71">[Guest]</span>';
                html += `
                    <div class="user-item">
                        <span>${badge} ${u.username}</span>
                        <button class="btn-delete" onclick="deleteUser('${u.username}')">🗑️</button>
                    </div>
                `;
            });
            document.getElementById('userList').innerHTML = html;
        } catch (e) {
            document.getElementById('userList').innerHTML = '<p style="color:red">Error loading users (Admin access required)</p>';
        }
    }
    
    async function addUser() {
        let u = document.getElementById('newUsername').value;
        let p = document.getElementById('newPassword').value;
        let r = document.getElementById('newRole').value;
        if(!u || !p) return alert('Username and password required');
        
        let formData = new URLSearchParams();
        formData.append('username', u);
        formData.append('password', p);
        formData.append('role', r);
        
        let res = await fetch('/api/users', { method: 'POST', body: formData });
        if(res.ok) {
            document.getElementById('newUsername').value = '';
            document.getElementById('newPassword').value = '';
            loadUsers();
        } else {
            alert(await res.text());
        }
    }
    
    async function deleteUser(username) {
        if(!confirm(`Delete user ${username}?`)) return;
        let formData = new URLSearchParams();
        formData.append('username', username);
        let res = await fetch('/api/users', { method: 'DELETE', body: formData });
        if(res.ok) {
            loadUsers();
        } else {
            alert(await res.text());
        }
    }
    
    /* OTA Firmware Update */
    function startOTA() {
        let fileInput = document.getElementById('otaInput');
        if(fileInput.files.length === 0) return alert('Please select a .bin file');
        let file = fileInput.files[0];
        
        let formData = new FormData();
        formData.append("update", file, file.name);
        
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/update", true);
        
        document.getElementById('otaProgressContainer').style.display = 'block';
        document.getElementById('otaStatus').innerText = 'Uploading firmware...';
        
        xhr.upload.addEventListener("progress", function(evt) {
            if (evt.lengthComputable) {
                let percentComplete = (evt.loaded / evt.total) * 100;
                document.getElementById('otaProgressFill').style.width = percentComplete + '%';
            }
        });
        
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    document.getElementById('otaStatus').innerHTML = '<span style="color:#2ecc71">Update Complete! Rebooting...</span>';
                    setTimeout(() => location.reload(), 10000); // Reload after 10s
                } else {
                    document.getElementById('otaStatus').innerHTML = '<span style="color:#e74c3c">Update Failed!</span>';
                }
            }
        };
        xhr.send(formData);
    }

    /* Modal Player */
    function playMedia(path, name) {
        const modal = document.getElementById('mediaModal');
        const container = document.getElementById('mediaContainer');
        const url = `/stream?file=${encodeURIComponent(path)}`;
        const ext = name.split('.').pop().toLowerCase();
        
        container.innerHTML = '';
        if (['mp4', 'webm'].includes(ext)) {
            container.innerHTML = `<video controls autoplay style="max-width:100%; max-height:80vh; border-radius:12px;"><source src="${url}" type="video/${ext}"></video>`;
        } else if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
            container.innerHTML = `<img src="${url}" style="max-width:100%; max-height:80vh; border-radius:12px;">`;
        } else {
            container.innerHTML = `<audio controls autoplay style="width:300px;"><source src="${url}" type="audio/${ext}"></audio>`;
        }
        modal.style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('mediaModal').style.display = 'none';
        document.getElementById('mediaContainer').innerHTML = '';
    }

    // Interval to refresh stats
    setInterval(loadStats, 5000);
    loadFiles();
</script>
</body>
</html>
)rawliteral";
