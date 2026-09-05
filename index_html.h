
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-width=1.0">
    <title>NanoNAS S3</title>
    <!-- Material Design Fonts and Icons -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
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
        :root {
            /* Light Theme (Material 3 Baseline) */
            --md-sys-color-primary: #6750A4;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #EADDFF;
            --md-sys-color-on-primary-container: #21005D;
            --md-sys-color-secondary: #625B71;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-error: #B3261E;
            --md-sys-color-on-error: #FFFFFF;
            --md-sys-color-background: #FFFBFE;
            --md-sys-color-on-background: #1C1B1F;
            --md-sys-color-surface: #FFFBFE;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-surface-variant: #E7E0EC;
            --md-sys-color-on-surface-variant: #49454F;
            --md-sys-color-outline: #79747E;
            
            --elevation-1: 0px 1px 2px 0px rgba(0,0,0,0.3), 0px 1px 3px 1px rgba(0,0,0,0.15);
            --elevation-2: 0px 1px 2px 0px rgba(0,0,0,0.3), 0px 2px 6px 2px rgba(0,0,0,0.15);
            --elevation-3: 0px 1px 3px 0px rgba(0,0,0,0.3), 0px 4px 8px 3px rgba(0,0,0,0.15);
            --elevation-4: 0px 2px 3px 0px rgba(0,0,0,0.3), 0px 6px 10px 4px rgba(0,0,0,0.15);
        }

        body.dark-theme {
            /* Dark Theme */
            --md-sys-color-primary: #D0BCFF;
            --md-sys-color-on-primary: #381E72;
            --md-sys-color-primary-container: #4F378B;
            --md-sys-color-on-primary-container: #EADDFF;
            --md-sys-color-secondary: #CCC2DC;
            --md-sys-color-on-secondary: #332D41;
            --md-sys-color-error: #F2B8B5;
            --md-sys-color-on-error: #601410;
            --md-sys-color-background: #1C1B1F;
            --md-sys-color-on-background: #E6E1E5;
            --md-sys-color-surface: #1C1B1F;
            --md-sys-color-on-surface: #E6E1E5;
            --md-sys-color-surface-variant: #49454F;
            --md-sys-color-on-surface-variant: #CAC4D0;
            --md-sys-color-outline: #938F99;
            
            --elevation-1: 0px 1px 2px 0px rgba(0,0,0,0.5), 0px 1px 3px 1px rgba(0,0,0,0.3);
            --elevation-2: 0px 1px 2px 0px rgba(0,0,0,0.5), 0px 2px 6px 2px rgba(0,0,0,0.3);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Roboto', sans-serif;
        }

        body {
            background-color: var(--md-sys-color-background);
            color: var(--md-sys-color-on-background);
            transition: background-color 0.3s, color 0.3s;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* Material Icons Setup */
        .material-symbols-outlined {
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
            vertical-align: middle;
        }

        /* App Bar */
        .app-bar {
            background-color: var(--md-sys-color-surface);
            color: var(--md-sys-color-on-surface);
            height: 64px;
            display: flex;
            align-items: center;
            padding: 0 16px;
            box-shadow: var(--elevation-2);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .app-bar-title {
            font-size: 22px;
            font-weight: 500;
            flex-grow: 1;
            margin-left: 16px;
        }
        
        .icon-btn {
            background: none;
            border: none;
            color: var(--md-sys-color-on-surface);
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s;
        }
        .icon-btn:hover { background-color: var(--md-sys-color-surface-variant); }

        /* Container */
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 24px;
            flex: 1;
            width: 100%;
        }

        /* Storage Stats Card */
        .card {
            background-color: var(--md-sys-color-surface);
            border-radius: 12px;
            padding: 24px;
            box-shadow: var(--elevation-1);
            margin-bottom: 24px;
            border: 1px solid var(--md-sys-color-outline);
            border-opacity: 0.1;
        }

        .storage-title {
            font-size: 14px;
            color: var(--md-sys-color-on-surface-variant);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 12px;
        }

        .storage-val {
            font-size: 32px;
            font-weight: 400;
            color: var(--md-sys-color-primary);
        }

        .storage-bar-bg {
            height: 8px;
            background-color: var(--md-sys-color-surface-variant);
            border-radius: 4px;
            margin-top: 16px;
            overflow: hidden;
        }

        .storage-bar-fill {
            height: 100%;
            background-color: var(--md-sys-color-primary);
            transition: width 0.5s ease-out;
        }

        /* Breadcrumbs */
        .breadcrumbs {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            font-size: 18px;
            font-weight: 500;
            gap: 8px;
            overflow-x: auto;
            white-space: nowrap;
            padding-bottom: 8px;
        }
        .breadcrumb-item {
            color: var(--md-sys-color-on-surface);
            cursor: pointer;
            text-decoration: none;
        }
        .breadcrumb-item:hover { text-decoration: underline; }
        .breadcrumb-separator { color: var(--md-sys-color-outline); }

        /* File List */
        .file-list {
            list-style: none;
            background-color: var(--md-sys-color-surface);
            border-radius: 12px;
            box-shadow: var(--elevation-1);
            overflow: hidden;
        }

        .file-item {
            display: flex;
            align-items: center;
            padding: 12px 16px;
            border-bottom: 1px solid var(--md-sys-color-surface-variant);
            transition: background-color 0.2s;
        }
        .file-item:last-child { border-bottom: none; }
        .file-item:hover { background-color: var(--md-sys-color-surface-variant); }

        /* Thumbnails! */
        .file-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background-color: var(--md-sys-color-surface-variant);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 16px;
            color: var(--md-sys-color-primary);
            overflow: hidden;
            flex-shrink: 0;
        }
        .file-icon img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .file-icon .material-symbols-outlined { font-size: 24px; }

        .file-info { flex-grow: 1; min-width: 0; display: flex; flex-direction: column; }
        .file-name {
            font-size: 16px;
            font-weight: 400;
            color: var(--md-sys-color-on-surface);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
        }
        .file-name:hover { text-decoration: underline; color: var(--md-sys-color-primary); }
        .file-size {
            font-size: 12px;
            color: var(--md-sys-color-on-surface-variant);
            margin-top: 4px;
        }

        /* Actions */
        .actions {
            display: flex;
            gap: 8px;
            flex-shrink: 0;
            margin-left: 16px;
        }
        
        /* Material Buttons */
        .btn {
            background: none;
            border: none;
            padding: 0 16px;
            height: 36px;
            border-radius: 18px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: all 0.2s;
            text-decoration: none;
        }
        .btn .material-symbols-outlined { font-size: 18px; }
        
        .btn-filled {
            background-color: var(--md-sys-color-primary);
            color: var(--md-sys-color-on-primary);
            box-shadow: var(--elevation-1);
        }
        .btn-filled:hover { box-shadow: var(--elevation-2); opacity: 0.9; }
        
        .btn-text {
            color: var(--md-sys-color-primary);
        }
        .btn-text:hover { background-color: var(--md-sys-color-primary-container); }

        .btn-error { color: var(--md-sys-color-error); }
        .btn-error:hover { background-color: rgba(179, 38, 30, 0.1); }

        /* Floating Action Button (FAB) */
        .fab {
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background-color: var(--md-sys-color-primary-container);
            color: var(--md-sys-color-on-primary-container);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--elevation-3);
            cursor: pointer;
            transition: all 0.2s;
            z-index: 100;
            border: none;
        }
        .fab:hover { box-shadow: var(--elevation-4); transform: translateY(-2px); }
        .fab .material-symbols-outlined { font-size: 24px; }

        .fab-menu {
            position: fixed;
            bottom: 100px;
            right: 32px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s, transform 0.2s;
            transform: translateY(20px);
            z-index: 99;
        }
        .fab-menu.active { opacity: 1; pointer-events: auto; transform: translateY(0); }
        
        .mini-fab {
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: flex-end;
            cursor: pointer;
        }
        .mini-fab-label {
            background: var(--md-sys-color-surface);
            color: var(--md-sys-color-on-surface);
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 14px;
            box-shadow: var(--elevation-1);
        }
        .mini-fab-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--md-sys-color-surface);
            color: var(--md-sys-color-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--elevation-2);
            border: none;
            cursor: pointer;
        }

        /* Upload Area Drag & Drop */
        .upload-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(4px);
            z-index: 2000;
            display: none;
            align-items: center;
            justify-content: center;
        }
        .upload-overlay.dragover { display: flex; }
        .upload-box {
            background: var(--md-sys-color-surface);
            padding: 48px;
            border-radius: 24px;
            text-align: center;
            border: 2px dashed var(--md-sys-color-primary);
        }

        /* Progress Bar */
        .progress-card {
            display: none;
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            max-width: 400px;
            background: var(--md-sys-color-surface);
            padding: 16px;
            border-radius: 12px;
            box-shadow: var(--elevation-3);
            z-index: 2000;
        }
        .progress-text { font-size: 14px; margin-bottom: 8px; color: var(--md-sys-color-on-surface); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .progress-bar-bg { height: 4px; background: var(--md-sys-color-surface-variant); border-radius: 2px; overflow: hidden; }
        .progress-bar-fill { height: 100%; background: var(--md-sys-color-primary); width: 0%; transition: width 0.2s; }

        /* Modals */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(2px);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            background: var(--md-sys-color-surface);
            border-radius: 24px;
            padding: 24px;
            width: 90%;
            max-width: 800px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            box-shadow: var(--elevation-4);
        }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .modal-title { font-size: 22px; font-weight: 500; }
        .modal-body { flex: 1; overflow-y: auto; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }

        /* Editor specific */
        #editorContent {
            width: 100%;
            min-height: 400px;
            padding: 16px;
            border: 1px solid var(--md-sys-color-outline);
            border-radius: 8px;
            background: var(--md-sys-color-surface);
            color: var(--md-sys-color-on-surface);
            font-family: monospace;
            font-size: 14px;
            resize: vertical;
        }

        /* Login Screen */
        #login-screen {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .login-card {
            background: var(--md-sys-color-surface);
            padding: 32px;
            border-radius: 24px;
            box-shadow: var(--elevation-2);
            width: 100%;
            max-width: 360px;
            text-align: center;
        }
        .login-card .material-symbols-outlined { font-size: 48px; color: var(--md-sys-color-primary); margin-bottom: 16px; }
        .input-field {
            width: 100%;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid var(--md-sys-color-outline);
            border-radius: 8px;
            background: var(--md-sys-color-surface);
            color: var(--md-sys-color-on-surface);
            font-size: 16px;
        }
        .input-field:focus { outline: 2px solid var(--md-sys-color-primary); border-color: transparent; }
    
        .file-item.drag-hover { background-color: var(--md-sys-color-primary-container); border: 2px dashed var(--md-sys-color-primary); }
</style>
</head>
<body class="dark-theme">

    <div id="app-screen" style="display:flex; flex:1; flex-direction:column;">
        
        <header class="app-bar">
            <span class="material-symbols-outlined" style="color:var(--md-sys-color-primary);">dns</span>
            <div class="app-bar-title">NanoNAS S3</div>
            <button class="icon-btn" onclick="openSysInfo()" title="System Info"><span class="material-symbols-outlined">analytics</span></button>
            <button class="icon-btn" onclick="toggleTheme()" title="Toggle Theme"><span class="material-symbols-outlined">dark_mode</span></button>
            <button class="icon-btn" onclick="openSettings()" title="Settings"><span class="material-symbols-outlined">settings</span></button>
            
        </header>

        <div class="container">
            <div class="card" id="storageCard" style="display:none;">
                <div class="storage-title">Storage Space</div>
                <div class="storage-val" id="storageText">Loading...</div>
                <div class="storage-bar-bg">
                    <div class="storage-bar-fill" id="storageBar" style="width: 0%;"></div>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:16px;">
                
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

                <div class="breadcrumbs" id="breadcrumb" style="margin-bottom:0;"></div>
                <button id="paste-btn" class="btn" style="display:none; gap:4px; border-radius:100px; padding:0 16px; background:var(--md-sys-color-primary-container); color:var(--md-sys-color-on-primary-container);" onclick="pasteFile()">
                    <span class="material-symbols-outlined">content_paste</span> Paste Here
                </button>
            </div>

            <ul class="file-list" id="fileList"></ul>
        </div>

        <!-- FAB for actions -->
        <button class="fab" onclick="toggleFabMenu()">
            <span class="material-symbols-outlined" id="fabIcon">add</span>
        </button>
        <div class="fab-menu" id="fabMenu">
            <div class="mini-fab" onclick="document.getElementById('fileInput').click(); toggleFabMenu();">
                <div class="mini-fab-label">Upload File</div>
                <button class="mini-fab-btn"><span class="material-symbols-outlined">upload_file</span></button>
            </div>
            <div class="mini-fab" onclick="createFolder(); toggleFabMenu();">
                <div class="mini-fab-label">New Folder</div>
                <button class="mini-fab-btn"><span class="material-symbols-outlined">create_new_folder</span></button>
            </div>
        </div>

        <input type="file" id="fileInput" style="display: none;" multiple onchange="handleFiles(this.files)">

    </div>

    <!-- Drag Overlay -->
    <div class="upload-overlay" id="uploadArea">
        <div class="upload-box">
            <span class="material-symbols-outlined" style="font-size: 64px; color:var(--md-sys-color-primary);">cloud_upload</span>
            <h2 style="margin-top:16px;">Drop files to upload</h2>
        </div>
    </div>

    <!-- Progress -->
    <div class="progress-card" id="progressContainer">
        <div class="progress-text" id="progressText">Uploading...</div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="progressBar"></div>
        </div>
    </div>

    <!-- Text Editor Modal -->
    <div id="editorModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="editorTitle">Editing File</div>
                <button class="icon-btn" onclick="closeEditor()"><span class="material-symbols-outlined">close</span></button>
            </div>
            <div class="modal-body">
                <textarea id="editorContent"></textarea>
            </div>
            <div class="modal-actions">
                <button class="btn btn-text" onclick="closeEditor()">CANCEL</button>
                <button class="btn btn-filled" onclick="saveEditor()">SAVE</button>
            </div>
        </div>
    </div>

    <!-- Markdown Viewer Modal -->
    <div id="markdownModal" class="modal">
        <div class="modal-content" style="max-width: 800px; height: 80vh; display: flex; flex-direction: column;">
            <div class="modal-header">
                <div class="modal-title" id="markdownTitle">Viewing File</div>
                <div>
                    <button class="icon-btn" id="markdownEditBtn" style="margin-right:8px;"><span class="material-symbols-outlined">edit</span></button>
                    <button class="icon-btn" onclick="document.getElementById('markdownModal').style.display='none'"><span class="material-symbols-outlined">close</span></button>
                </div>
            </div>
            <div class="modal-body" id="markdownContent" style="background: var(--md-sys-color-surface-container); padding: 24px; border-radius: 8px; overflow-y: auto; line-height: 1.6;">
            </div>
        </div>
    </div>
    
    <!-- Media Player Modal -->
    <div id="mediaModal" class="modal" onclick="if(event.target==this) this.style.display='none'">
        <div style="background:var(--md-sys-color-surface); padding:20px; border-radius:12px; max-width:90%; position:relative;">
            <button class="icon-btn" onclick="document.getElementById('mediaModal').style.display='none'" style="position:absolute; top:8px; right:8px; z-index:10;"><span class="material-symbols-outlined">close</span></button>
            <div id="mediaContainer" style="display:flex; justify-content:center; align-items:center; min-height:200px;"></div>
            <div style="display:flex; justify-content:space-between; margin-top:16px;">
                <button class="btn btn-text" onclick="prevMedia()"><span class="material-symbols-outlined">skip_previous</span> PREV</button>
                <button class="btn btn-text" onclick="nextMedia()">NEXT <span class="material-symbols-outlined">skip_next</span></button>
            </div>
        </div>
    </div>

    <!-- System Info Modal -->
    <div id="sysInfoModal" class="modal" onclick="if(event.target==this) { this.style.display='none'; clearInterval(sysInfoInterval); }">
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <div class="modal-title">System Health & Analytics</div>
                <button class="icon-btn" onclick="document.getElementById('sysInfoModal').style.display='none'; clearInterval(sysInfoInterval);"><span class="material-symbols-outlined">close</span></button>
            </div>
            <div class="modal-body" style="display:grid; grid-template-columns:1fr 1fr; gap:16px;" id="sysInfoBody">
                Loading...
            </div>
        </div>
    </div>

    <!-- Settings Modal -->
    <div id="settingsModal" class="modal">
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <div class="modal-title">Settings</div>
                <button class="icon-btn" onclick="document.getElementById('settingsModal').style.display='none'"><span class="material-symbols-outlined">close</span></button>
            </div>
            <div class="modal-body">
                <h3 style="margin-bottom:16px;">Users</h3>
                <ul class="file-list" id="usersList" style="margin-bottom:16px;"></ul>
                <input type="text" id="newUsername" class="input-field" placeholder="New Username" style="margin-bottom:8px;">
                <input type="password" id="newPassword" class="input-field" placeholder="New Password" style="margin-bottom:8px;">
                <select id="newRole" class="input-field" style="margin-bottom:16px; width:100%;">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>
                <button class="btn btn-filled" onclick="addUser()" style="width:100%; margin-bottom:24px;">ADD USER</button>
                
                <h3 style="margin-bottom:16px;">Firmware Update (OTA)</h3>
                <input type="file" id="otaFile" accept=".bin" style="margin-bottom:8px;">
                <button class="btn btn-filled" onclick="uploadOTA()" style="width:100%; margin-bottom:8px;">UPDATE FIRMWARE</button>
                <div class="storage-bar-bg" id="otaProgressBg" style="display:none; height:8px; margin-bottom:8px;">
                    <div class="storage-bar-fill" id="otaProgressFill" style="width:0%; background:var(--md-sys-color-primary);"></div>
                </div>
                <div id="otaStatus" style="font-size:14px; text-align:center;"></div>
            </div>
        </div>
    </div>

    <!-- Collision Modal -->
    <div id="collisionModal" class="modal">
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <div class="modal-title">File Conflict</div>
                <button class="icon-btn" onclick="handleCollision('skip')"><span class="material-symbols-outlined">close</span></button>
            </div>
            <div class="modal-body">
                <p style="margin-bottom:16px;">The item <b id="collisionFilename"></b> already exists in this folder. What would you like to do?</p>
                <div style="display:flex; gap:8px; margin-bottom:16px;">
                    <button class="btn btn-error" style="flex:1;" onclick="handleCollision('replace')">Replace</button>
                    <button class="btn" style="flex:1; background:var(--md-sys-color-surface-container-high); color:var(--md-sys-color-on-surface);" onclick="handleCollision('skip')">Skip</button>
                </div>
                <p style="margin-bottom:8px; font-size:14px; font-weight:500;">Or keep both and rename:</p>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="collisionRenameInput" class="input-field" style="flex:1;">
                    <button class="btn btn-filled" onclick="handleCollision('rename')">Rename</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- Theme ---
        if(localStorage.getItem('theme') === 'light') document.body.classList.replace('dark-theme', 'light-theme');
        function toggleTheme() {
            if (document.body.classList.contains('dark-theme')) {
                document.body.classList.replace('dark-theme', 'light-theme');
                localStorage.setItem('theme', 'light');
            } else {
                document.body.classList.replace('light-theme', 'dark-theme');
                localStorage.setItem('theme', 'dark');
            }
        }

        // --- FAB Menu ---
        function toggleFabMenu() {
            const menu = document.getElementById('fabMenu');
            const icon = document.getElementById('fabIcon');
            if(menu.classList.contains('active')) {
                menu.classList.remove('active');
                icon.innerText = 'add';
                icon.style.transform = 'rotate(0deg)';
            } else {
                menu.classList.add('active');
                icon.innerText = 'close';
                icon.style.transform = 'rotate(45deg)';
            }
        }

let currentDir = "/";

        let selectedItems = new Set();

        loadFiles();
        loadStats();

        // --- File System ---
        function formatBytes(bytes) { 
            if (bytes === 0) return '0 B'; 
            const k = 1024, dm = 2, sizes = ['B', 'KB', 'MB', 'GB', 'TB']; 
            const i = Math.floor(Math.log(bytes) / Math.log(k)); 
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]; 
        }

        async function loadStats() {
            try {
                let res = await fetch('/stats');
                if(!res.ok) return;
                let data = await res.json();
                document.getElementById('storageCard').style.display = 'block';
                document.getElementById('storageText').innerText = `${formatBytes(data.used)} / ${formatBytes(data.total)}`;
                if(data.total > 0) {
                    document.getElementById('storageBar').style.width = (data.used / data.total * 100) + '%';
                }
            } catch(e) {}
        }

        let mediaList = [];
        let currentMediaIndex = -1;

        const textExts = ['txt', 'csv', 'json', 'ino', 'js', 'css', 'html', 'py'];
        const imgExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
        const audioExts = ['mp3', 'wav', 'ogg'];
        const vidExts = ['mp4', 'webm'];
        const mdExts = ['md'];
        
        function getIcon(name, isDir) {
            if(isDir) return 'folder';
            let ext = name.split('.').pop().toLowerCase();
            if(imgExts.includes(ext)) return 'image';
            if(audioExts.includes(ext)) return 'audio_file';
            if(vidExts.includes(ext)) return 'video_file';
            if(mdExts.includes(ext)) return 'markdown';
            if(textExts.includes(ext)) return 'description';
            return 'insert_drive_file';
        }

        async function loadFiles() {
            try {
                const response = await fetch('/list?dir=' + encodeURIComponent(currentDir));
                const files = await response.json();
                const fileListEl = document.getElementById('fileList');
                fileListEl.innerHTML = '';
                mediaList = [];

                // Sort: directories first
                files.sort((a,b) => b.isDir - a.isDir || a.name.localeCompare(b.name));

                // Update Breadcrumb
                const parts = currentDir.split('/').filter(p => p);
                let breadcrumbHTML = `<a class="breadcrumb-item" onclick="changeDir('/')"><span class="material-symbols-outlined">home</span></a>`;
                let buildPath = "";
                parts.forEach((p, i) => {
                    buildPath += "/" + p;
                    breadcrumbHTML += ` <span class="breadcrumb-separator material-symbols-outlined">chevron_right</span> <a class="breadcrumb-item" onclick="changeDir('${buildPath}')">${p}</a>`;
                });
                document.getElementById('breadcrumb').innerHTML = breadcrumbHTML;

                files.forEach(file => {
                    let fullPath = (currentDir === "/" ? "" : currentDir) + "/" + file.name;
                    let ext = file.name.split('.').pop().toLowerCase();
                    let isImg = imgExts.includes(ext);
                    let isAud = audioExts.includes(ext);
                    let isVid = vidExts.includes(ext);
                    let isTxt = textExts.includes(ext) || mdExts.includes(ext);
                    let isPlayable = isImg || isTxt || isAud || isVid;

                    if(isPlayable && !file.isDir) mediaList.push({name: file.name, path: fullPath, type: ext});

                    let li = document.createElement('li');
                    li.className = 'file-item';
                    
                    // Thumbnail Logic
                    let iconHtml = '';
                    if (isImg && !file.isDir) {
                        iconHtml = `<div class="file-icon"><img src="/stream?file=${encodeURIComponent(fullPath)}" loading="lazy" alt="thumb"></div>`;
                    } else {
                        iconHtml = `<div class="file-icon"><span class="material-symbols-outlined">${getIcon(file.name, file.isDir)}</span></div>`;
                    }

                    if (file.isDir) {
                        li.setAttribute('draggable', 'true');
                        li.setAttribute('ondragstart', `dragStart(event, '${fullPath}')`);
                        li.setAttribute('ondragover', `dragOver(event)`);
                        li.setAttribute('ondragleave', `dragLeave(event)`);
                        li.setAttribute('ondrop', `dropOnFolder(event, '${fullPath}')`);
                        li.innerHTML = `
                            <div class="checkbox-container" style="display:flex; align-items:center; margin-right:12px;">
                                <input type="checkbox" onchange="toggleSelection('${fullPath}', this.checked)" ${selectedItems.has(fullPath) ? 'checked' : ''}>
                            </div>
                            ${iconHtml}
                            <div class="file-info" onclick="changeDir('${fullPath}')" style="cursor: pointer;">
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">-</span>
                            </div>
                            <div class="actions">
                                <button class="btn btn-text" onclick="cutFile('${fullPath}')" title="Cut"><span class="material-symbols-outlined">content_cut</span></button>
                                <button class="btn btn-text" onclick="copyFile('${fullPath}')" title="Copy"><span class="material-symbols-outlined">content_copy</span></button>
                                <a href="/download_dir?dir=${encodeURIComponent(fullPath)}" class="btn btn-text" title="Download ZIP"><span class="material-symbols-outlined">archive</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', true)" title="Delete Folder"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    } else {
                        li.setAttribute('draggable', 'true');
                        li.setAttribute('ondragstart', `dragStart(event, '${fullPath}')`);
                        let playBtn = isPlayable ? `<button class="btn btn-text" onclick="playMedia('${fullPath}', '${file.name}')" title="View/Play"><span class="material-symbols-outlined">${isImg||isTxt?'visibility':'play_arrow'}</span></button>` : '';
                        li.innerHTML = `
                            <div class="checkbox-container" style="display:flex; align-items:center; margin-right:12px;">
                                <input type="checkbox" onchange="toggleSelection('${fullPath}', this.checked)" ${selectedItems.has(fullPath) ? 'checked' : ''}>
                            </div>
                            ${iconHtml}
                            <div class="file-info" ${isPlayable ? `onclick="playMedia('${fullPath}', '${file.name}')" style="cursor: pointer;"` : ''}>
                                <span class="file-name">${file.name}</span>
                                <span class="file-size">${formatBytes(file.size)}</span>
                            </div>
                            <div class="actions">
                                ${playBtn}
                                <button class="btn btn-text" onclick="cutFile('${fullPath}')" title="Cut"><span class="material-symbols-outlined">content_cut</span></button>
                                <button class="btn btn-text" onclick="copyFile('${fullPath}')" title="Copy"><span class="material-symbols-outlined">content_copy</span></button>
                                <a href="/download?file=${encodeURIComponent(fullPath)}" class="btn btn-text" download title="Download"><span class="material-symbols-outlined">download</span></a>
                                <button class="btn btn-error" onclick="deleteFile('${fullPath}', false)" title="Delete"><span class="material-symbols-outlined">delete</span></button>
                            </div>
                        `;
                    }
                    fileListEl.appendChild(li);
                });
            } catch (error) { console.error(error); }
        }

        function changeDir(dir) { currentDir = dir;
            clearSelection(); loadFiles(); }

        async function createFolder() {
            let name = prompt("Enter new folder name:");
            if (!name) return;
            let path = (currentDir === "/" ? "" : currentDir) + "/" + name;
            try {
                let res = await fetch(`/mkdir?dir=${encodeURIComponent(path)}`, {method: 'POST'});
                if(res.ok) loadFiles();
                else alert("Failed to create folder");
            } catch (e) {}
        }

        async function deleteFile(path, isDir) {
            if (!confirm(`Delete ${path}?`)) return;
            try { 
                const response = await fetch('/delete?file=' + encodeURIComponent(path), { method: 'DELETE' }); 
                if (response.ok) { loadFiles(); loadStats(); }
                else alert('Delete failed. Ensure folder is empty.'); 
            } catch (e) {}
        }

        // --- Editor ---
        let editingPath = "";
        async function openEditor(path, name) {
            editingPath = path;
            document.getElementById('editorTitle').innerText = name;
            document.getElementById('editorContent').value = 'Loading...';
            document.getElementById('editorModal').style.display = 'flex';
            try {
                let res = await fetch(`/stream?file=${encodeURIComponent(path)}`);
                if(!res.ok) throw new Error("Failed");
                document.getElementById('editorContent').value = await res.text();
            } catch(e) { document.getElementById('editorContent').value = "Error loading file."; }
        }
        function closeEditor() { document.getElementById('editorModal').style.display = 'none'; }
        
        async function saveEditor() {
            let content = document.getElementById('editorContent').value;
            try {
                let res = await fetch(`/upload_chunk?name=${encodeURIComponent(editingPath)}&append=0`, { 
                    method: 'POST', body: new Blob([content]) 
                });
                if(res.ok) { closeEditor(); loadFiles(); }
                else alert("Failed to save.");
            } catch(e) { alert("Error saving."); }
        }

        // --- Media Player ---
        async function playMedia(path, name) {
            let ext = name.split('.').pop().toLowerCase();
            
            if (mdExts.includes(ext)) {
                document.getElementById('markdownTitle').innerText = name;
                document.getElementById('markdownContent').innerHTML = '<div style="text-align:center; padding: 40px;">Loading...</div>';
                document.getElementById('markdownModal').style.display = 'flex';
                
                // Set up the edit button to open the plain text editor
                document.getElementById('markdownEditBtn').onclick = () => {
                    document.getElementById('markdownModal').style.display = 'none';
                    openEditor(path, name);
                };
                
                try {
                    let res = await fetch('/stream?file=' + encodeURIComponent(path));
                    if (res.ok) {
                        let text = await res.text();
                        document.getElementById('markdownContent').innerHTML = marked.parse(text);
                    } else {
                        document.getElementById('markdownContent').innerHTML = '<div style="color:red;">Error loading markdown file.</div>';
                    }
                } catch(e) {
                    document.getElementById('markdownContent').innerHTML = '<div style="color:red;">Network error.</div>';
                }
                return;
            }
            
            if(textExts.includes(ext)) return openEditor(path, name);
            
            currentMediaIndex = mediaList.findIndex(m => m.path === path);
            const container = document.getElementById('mediaContainer');
            document.getElementById('mediaModal').style.display = 'flex';
            
            let url = `/stream?file=${encodeURIComponent(path)}`;
            if (imgExts.includes(ext)) {
                container.innerHTML = `<img src="${url}" style="max-width:100%; max-height:70vh; border-radius:8px;">`;
            } else if (vidExts.includes(ext)) {
                container.innerHTML = `<video controls autoplay style="max-width:100%; max-height:70vh; border-radius:8px;"><source src="${url}" type="video/${ext}"></video>`;
            } else if (audioExts.includes(ext)) {
                container.innerHTML = `<audio controls autoplay style="width:100%;"><source src="${url}" type="audio/${ext}"></audio>`;
            }
        }
        function nextMedia() {
            if(mediaList.length === 0) return;
            currentMediaIndex = (currentMediaIndex + 1) % mediaList.length;
            playMedia(mediaList[currentMediaIndex].path, mediaList[currentMediaIndex].name);
        }
        function prevMedia() {
            if(mediaList.length === 0) return;
            currentMediaIndex = (currentMediaIndex - 1 + mediaList.length) % mediaList.length;
            playMedia(mediaList[currentMediaIndex].path, mediaList[currentMediaIndex].name);
        }

        
        
        // --- Clipboard Logic ---
        function updatePasteButton() {
            let cb = sessionStorage.getItem('clipboardData');
            let btn = document.getElementById('paste-btn');
            if (cb) {
                let arr = JSON.parse(cb);
                btn.style.display = 'flex';
                btn.innerHTML = `<span class="material-symbols-outlined">content_paste</span> Paste ${arr.length} item${arr.length !== 1 ? 's' : ''}`;
            } else {
                btn.style.display = 'none';
            }
        }
        function copyFile(path) {
            sessionStorage.setItem('clipboardAction', 'copy');
            sessionStorage.setItem('clipboardData', JSON.stringify([path]));
            updatePasteButton();
        }
        function cutFile(path) {
            sessionStorage.setItem('clipboardAction', 'move');
            sessionStorage.setItem('clipboardData', JSON.stringify([path]));
            updatePasteButton();
        }
        let resolveCollision;

        function promptCollision(filename) {
            return new Promise(resolve => {
                document.getElementById('collisionFilename').innerText = filename;
                document.getElementById('collisionRenameInput').value = filename;
                document.getElementById('collisionModal').style.display = 'flex';
                resolveCollision = resolve;
            });
        }

        function handleCollision(action) {
            document.getElementById('collisionModal').style.display = 'none';
            if (action === 'rename') {
                resolveCollision(document.getElementById('collisionRenameInput').value);
            } else {
                resolveCollision(action);
            }
        }

        async function pasteFile() {
            let cbData = sessionStorage.getItem('clipboardData');
            let action = sessionStorage.getItem('clipboardAction');
            if (!cbData || !action) return;
            let arr = JSON.parse(cbData);
            let btn = document.getElementById('paste-btn');

            let response = await fetch('/list?dir=' + encodeURIComponent(currentDir));
            let existingFiles = await response.json();
            let existingNames = existingFiles.map(f => f.name);

            for (let i = 0; i < arr.length; i++) {
                let sourcePath = arr[i];
                let sourceName = sourcePath.substring(sourcePath.lastIndexOf('/') + 1);

                if (existingNames.includes(sourceName)) {
                    let choice = await promptCollision(sourceName);
                    if (choice === 'skip') {
                        continue;
                    } else if (choice !== 'replace') {
                        sourceName = choice;
                    }
                }
                
                let destPath = currentDir + "/" + sourceName;
                if (currentDir === "/") destPath = "/" + sourceName;
                if (sourcePath === destPath) continue; // Same location
                
                let endpoint = action === 'move' ? '/api/move' : '/api/copy';
                
                try {
                    btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Pasting ${i+1}/${arr.length}...`;
                    
                    let res = await fetch(endpoint, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        body: `from=${encodeURIComponent(sourcePath)}&to=${encodeURIComponent(destPath)}`
                    });
                    
                    if (res.ok && action === 'copy') {
                        let finished = false;
                        while (!finished) {
                            await new Promise(r => setTimeout(r, 1000));
                            let statRes = await fetch('/api/copy_status');
                            if (statRes.ok) {
                                let status = await statRes.json();
                                if (status.scanning) {
                                    btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Scanning ${i+1}/${arr.length}...`;
                                } else {
                                    let pct = status.total > 0 ? Math.round((status.copied / status.total) * 100) : 100;
                                    btn.innerHTML = `<span class="material-symbols-outlined">pending</span> Pasting ${i+1}/${arr.length} (${pct}%)...`;
                                }
                                finished = status.finished;
                            }
                        }
                    } else if (!res.ok) {
                        console.error(`Failed to ${action} ${sourcePath}`);
                    }
                } catch(e) {
                    console.error(`Error during ${action} ${sourcePath}`, e);
                }
            }
            
            if (action === 'move') {
                sessionStorage.removeItem('clipboardData');
                sessionStorage.removeItem('clipboardAction');
            }
            updatePasteButton();
            loadFiles();
        }
        
        // Ensure paste button state is updated on load
        window.addEventListener('DOMContentLoaded', () => {
            updatePasteButton();
        });

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

        // --- Upload Logic ---
        const uploadArea = document.getElementById('uploadArea');
        document.body.addEventListener('dragover', (e) => { e.preventDefault(); uploadArea.classList.add('dragover'); });
        uploadArea.addEventListener('dragleave', () => { uploadArea.classList.remove('dragover'); });
        uploadArea.addEventListener('drop', (e) => { e.preventDefault(); uploadArea.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });

        async function handleFiles(files) {
            if (!files || files.length === 0) return;
            
            let response = await fetch('/list?dir=' + encodeURIComponent(currentDir));
            let existingFiles = await response.json();
            let existingNames = existingFiles.map(f => f.name);
            
            const pContainer = document.getElementById('progressContainer');
            const pBar = document.getElementById('progressBar');
            const pText = document.getElementById('progressText');

            pContainer.style.display = 'block';

            for (let idx = 0; idx < files.length; idx++) {
                const file = files[idx];
                let finalName = file.name;

                if (existingNames.includes(finalName)) {
                    let choice = await promptCollision(finalName);
                    if (choice === 'skip') {
                        continue;
                    } else if (choice !== 'replace') {
                        finalName = choice;
                    }
                }

                pBar.style.width = '0%';
                pText.innerText = `[${idx+1}/${files.length}] Uploading ${finalName} (0%)`;

                const chunkSize = 1024 * 256; 
                const totalChunks = Math.ceil(file.size / chunkSize) || 1;
                let uploadedBytes = 0;
                let fullPath = (currentDir === "/" ? "" : currentDir) + "/" + finalName;

                for (let i = 0; i < totalChunks; i++) {
                    const start = i * chunkSize;
                    const end = Math.min(start + chunkSize, file.size);
                    const chunk = file.slice(start, end);
                    const append = (i === 0) ? '0' : '1';
                    
                    let success = false; let retries = 3;
                    while (!success && retries > 0) {
                        try {
                            const res = await fetch(`/upload_chunk?name=${encodeURIComponent(fullPath)}&append=${append}`, {
                                method: 'POST', body: chunk
                            });
                            if (res.ok) {
                                success = true; uploadedBytes += (end - start);
                                const pct = ((uploadedBytes / file.size) * 100).toFixed(1);
                                pBar.style.width = pct + '%';
                                pText.innerText = `[${idx+1}/${files.length}] Uploading ${file.name} (${pct}%)`;
                            } else { retries--; await new Promise(r => setTimeout(r, 1000)); }
                        } catch (e) { retries--; await new Promise(r => setTimeout(r, 1000)); }
                    }
                    if (!success) { alert(`Upload failed: ${file.name}`); break; }
                }
            }
            pText.innerText = 'Upload Complete!';
            setTimeout(() => { pContainer.style.display = 'none'; loadFiles(); loadStats(); }, 1500);
        }

        // --- Settings / Users ---
        let sysInfoInterval = null;
        async function fetchSysInfo() {
            try {
                let res = await fetch('/api/sysinfo');
                if(!res.ok) return;
                let data = await res.json();
                
                let formatBytes = (bytes) => {
                    if (bytes === 0) return '0 B';
                    const k = 1024;
                    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                };

                let html = `
                    <div class="card" style="margin-bottom:0; padding:16px;">
                        <div class="storage-title">Heap RAM</div>
                        <div class="storage-val" style="font-size:24px;">${formatBytes(data.heap_free)} <span style="font-size:14px;color:var(--md-sys-color-on-surface-variant);">/ ${formatBytes(data.heap_total)}</span></div>
                        <div class="storage-bar-bg" style="height:4px;"><div class="storage-bar-fill" style="width:${100 - (data.heap_free/data.heap_total*100)}%;"></div></div>
                    </div>
                    <div class="card" style="margin-bottom:0; padding:16px;">
                        <div class="storage-title">PSRAM</div>
                        <div class="storage-val" style="font-size:24px;">${formatBytes(data.psram_free)} <span style="font-size:14px;color:var(--md-sys-color-on-surface-variant);">/ ${formatBytes(data.psram_total)}</span></div>
                        <div class="storage-bar-bg" style="height:4px;"><div class="storage-bar-fill" style="width:${data.psram_total ? 100 - (data.psram_free/data.psram_total*100) : 0}%;"></div></div>
                    </div>
                    <div class="card" style="margin-bottom:0; padding:16px;">
                        <div class="storage-title">WiFi Signal (RSSI)</div>
                        <div class="storage-val" style="font-size:24px;">${data.wifi_rssi} dBm</div>
                    </div>
                    <div class="card" style="margin-bottom:0; padding:16px;">
                        <div class="storage-title">System Uptime</div>
                        <div class="storage-val" style="font-size:24px;">${Math.floor(data.uptime / 60)}m ${data.uptime % 60}s</div>
                    </div>
                `;
                document.getElementById('sysInfoBody').innerHTML = html;
            } catch(e) {}
        }

        function openSysInfo() {
            document.getElementById('sysInfoModal').style.display = 'flex';
            fetchSysInfo();
            sysInfoInterval = setInterval(fetchSysInfo, 2000);
        }

        function openSettings() {
            document.getElementById('settingsModal').style.display = 'flex';
            loadUsers();
        }
        async function loadUsers() {
            try {
                let res = await fetch('/api/users');
                if(!res.ok) return;
                let users = await res.json();
                let html = '';
                users.forEach(u => {
                    html += `<li class="file-item"><div class="file-info"><span class="file-name">${u.username}</span></div>`;
                    if(u.username !== 'admin') html += `<div class="actions"><button class="btn btn-error" onclick="deleteUser('${u.username}')"><span class="material-symbols-outlined">delete</span></button></div>`;
                    html += `</li>`;
                });
                document.getElementById('usersList').innerHTML = html;
            } catch(e){}
        }
        async function addUser() {
            let u = document.getElementById('newUsername').value;
            let p = document.getElementById('newPassword').value;
            let r = document.getElementById('newRole').value;
            if(!u || !p) return;
            try {
                let res = await fetch('/api/users', {
                    method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `username=${encodeURIComponent(u)}&password=${encodeURIComponent(p)}&role=${encodeURIComponent(r)}`
                });
                if(res.ok) { document.getElementById('newUsername').value=''; document.getElementById('newPassword').value=''; loadUsers(); }
                else alert("Failed to add user");
            } catch(e){}
        }
        async function deleteUser(u) {
            if(!confirm(`Delete user ${u}?`)) return;
            try {
                let res = await fetch('/api/users?username=' + encodeURIComponent(u), {method: 'DELETE'});
                if(res.ok) loadUsers();
            } catch(e){}
        }

        async function uploadOTA() {
            const fileInput = document.getElementById('otaFile');
            if (!fileInput.files.length) return alert('Please select a firmware .bin file first.');
            const file = fileInput.files[0];
            const bg = document.getElementById('otaProgressBg');
            const fill = document.getElementById('otaProgressFill');
            const status = document.getElementById('otaStatus');
            
            bg.style.display = 'block';
            fill.style.width = '0%';
            status.innerText = 'Authenticating...';
            status.style.color = 'var(--md-sys-color-on-surface)';

            try {
                // Force browser to authenticate the path before sending the giant binary payload
                let preflight = await fetch('/update');
                if(!preflight.ok) throw new Error("Auth failed");
            } catch(e) {
                // Ignore preflight errors, the XHR might still work
            }

            status.innerText = 'Uploading...';
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/update', true);
            
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable) {
                    const pct = Math.round((e.loaded / e.total) * 100);
                    fill.style.width = pct + '%';
                    status.innerText = `Uploading... ${pct}%`;
                }
            };
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    fill.style.background = 'var(--md-sys-color-primary)';
                    status.innerText = 'Success! Rebooting NAS...';
                    setTimeout(() => window.location.reload(), 3000);
                } else {
                    fill.style.background = 'var(--md-sys-color-error)';
                    status.innerText = 'Update failed!';
                    status.style.color = 'var(--md-sys-color-error)';
                }
            };
            
            xhr.onerror = function() {
                fill.style.background = 'var(--md-sys-color-error)';
                status.innerText = 'Network error during update!';
                status.style.color = 'var(--md-sys-color-error)';
            };
            
            const formData = new FormData();
            formData.append("update", file, file.name);
            xhr.send(formData);
        }

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
            document.querySelectorAll('.checkbox-container input').forEach(el => el.checked = false);
            updateActionBar();
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

        function bulkCopy() {
            if(selectedItems.size === 0) return;
            sessionStorage.setItem('clipboardAction', 'copy');
            sessionStorage.setItem('clipboardData', JSON.stringify(Array.from(selectedItems)));
            alert(`Copied ${selectedItems.size} items. Go to destination and Paste.`);
            clearSelection();
            loadFiles();
        }

        function bulkCut() {
            if(selectedItems.size === 0) return;
            sessionStorage.setItem('clipboardAction', 'move');
            sessionStorage.setItem('clipboardData', JSON.stringify(Array.from(selectedItems)));
            alert(`Cut ${selectedItems.size} items. Go to destination and Paste.`);
            clearSelection();
            loadFiles();
        }

        async function bulkDelete() {
            if(selectedItems.size === 0) return;
            if(!confirm(`Delete ${selectedItems.size} selected items?`)) return;
            let arr = Array.from(selectedItems);
            let successCount = 0;
            
            for (let i = 0; i < arr.length; i++) {
                try {
                    let res = await fetch('/delete?file=' + encodeURIComponent(arr[i]), { method: 'DELETE' });
                    if (res.ok) successCount++;
                } catch(e) {}
            }
            alert(`Deleted ${successCount}/${arr.length} items.`);
            clearSelection();
            loadFiles();
            loadStats();
        }

    </script>
</body>
</html>
)rawliteral";
