import re

with open("index_html.h", "r") as f:
    code = f.read()

# Fix HTML input to include role dropdown
old_html = """                <input type="text" id="newUsername" class="input-field" placeholder="New Username" style="margin-bottom:8px;">
                <input type="password" id="newPassword" class="input-field" placeholder="New Password" style="margin-bottom:16px;">"""
new_html = """                <input type="text" id="newUsername" class="input-field" placeholder="New Username" style="margin-bottom:8px;">
                <input type="password" id="newPassword" class="input-field" placeholder="New Password" style="margin-bottom:8px;">
                <select id="newRole" class="input-field" style="margin-bottom:16px; width:100%;">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                </select>"""
code = code.replace(old_html, new_html)

# Fix Javascript
code = code.replace("fetch('/users'", "fetch('/api/users'")
code = code.replace("fetch('/users?", "fetch('/api/users?")
code = code.replace("fetch('/users',", "fetch('/api/users',")

old_addUser = """        async function addUser() {
            let u = document.getElementById('newUsername').value;
            let p = document.getElementById('newPassword').value;
            if(!u || !p) return;
            try {
                let res = await fetch('/api/users', {
                    method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: `username=${encodeURIComponent(u)}&password=${encodeURIComponent(p)}`
                });
                if(res.ok) { document.getElementById('newUsername').value=''; document.getElementById('newPassword').value=''; loadUsers(); }
                else alert("Failed to add user");
            } catch(e){}
        }"""
        
new_addUser = """        async function addUser() {
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
        }"""
        
code = code.replace(old_addUser, new_addUser)

with open("index_html.h", "w") as f:
    f.write(code)

print("Fixed index_html.h users logic!")
