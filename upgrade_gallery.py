import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Update the mediaModal HTML to include Next/Prev buttons
modal_html_old = """    <div id="mediaModal" class="modal" onclick="if(event.target==this) closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <div id="mediaContainer" style="display:flex; justify-content:center; align-items:center; width:100%; height:100%;"></div>
    </div>"""

modal_html_new = """    <div id="mediaModal" class="modal" onclick="if(event.target==this) closeModal()">
        <span class="close" onclick="closeModal()">&times;</span>
        <div id="mediaNavPrev" class="media-nav" onclick="prevMedia()">&#10094;</div>
        <div id="mediaContainer" style="display:flex; justify-content:center; align-items:center; width:100%; height:100%;"></div>
        <div id="mediaNavNext" class="media-nav" onclick="nextMedia()">&#10095;</div>
    </div>"""

code = code.replace(modal_html_old, modal_html_new)

# 2. Add CSS for media-nav buttons
css_injection = """
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
"""
code = code.replace("</style>", css_injection + "</style>")

# 3. Update JS to track current media list and index
js_globals = """
    let currentFiles = [];
    let currentMediaIndex = -1;
    let mediaList = [];
"""
code = code.replace("let currentDir = \"/\";", "let currentDir = \"/\";" + js_globals)

# Save files list in loadFiles
code = code.replace("const files = await response.json();", "const files = await response.json();\n            currentFiles = files;")

# 4. Update playMedia to populate mediaList and handle Next/Prev
play_media_old = """    function playMedia(path, name) {
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
    }"""

play_media_new = """    function playMedia(path, name) {
        // Build media list for gallery
        mediaList = currentFiles.filter(f => !f.isDir && isPlayable(f.name));
        currentMediaIndex = mediaList.findIndex(f => f.name === name);
        updateMediaNav();
        renderMedia(path, name);
    }
    
    function renderMedia(path, name) {
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
    
    function updateMediaNav() {
        document.getElementById('mediaNavPrev').style.display = currentMediaIndex > 0 ? 'block' : 'none';
        document.getElementById('mediaNavNext').style.display = currentMediaIndex < mediaList.length - 1 ? 'block' : 'none';
    }
    
    function nextMedia() {
        if (currentMediaIndex < mediaList.length - 1) {
            currentMediaIndex++;
            let f = mediaList[currentMediaIndex];
            let p = (currentDir === "/" ? "" : currentDir) + "/" + f.name;
            renderMedia(p, f.name);
            updateMediaNav();
        }
    }
    
    function prevMedia() {
        if (currentMediaIndex > 0) {
            currentMediaIndex--;
            let f = mediaList[currentMediaIndex];
            let p = (currentDir === "/" ? "" : currentDir) + "/" + f.name;
            renderMedia(p, f.name);
            updateMediaNav();
        }
    }
"""
code = code.replace(play_media_old, play_media_new)


with open("index_html.h", "w") as f:
    f.write(code)

print("Done upgrading gallery.")
