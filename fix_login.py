import re

with open("index_html.h", "r") as f:
    code = f.read()

# 1. Remove login-screen div
code = re.sub(r'<div id="login-screen">.*?</div>\n\n    <div id="app-screen"', '<div id="app-screen"', code, flags=re.DOTALL)

# 2. Make app-screen visible by default
code = code.replace('<div id="app-screen" style="display:none; flex:1;">', '<div id="app-screen" style="display:flex; flex:1; flex-direction:column;">')

# 3. Remove auth JS logic
auth_logic = r"""        // --- Auth & State ---
        let currentDir = "/";
        let sessionToken = localStorage.getItem\('token'\) \|\| "";
        
        // Setup fetch interceptor for auth
        const originalFetch = window\.fetch;
        window\.fetch = async function\(\) \{.*?return response;
        \};

        if \(sessionToken\) \{
            document\.getElementById\('login-screen'\)\.style\.display = 'none';
            document\.getElementById\('app-screen'\)\.style\.display = 'flex';
            loadFiles\(\);
            loadStats\(\);
        \}

        async function login\(\) \{.*?\}

        function logout\(\) \{.*?\}"""

code = re.sub(auth_logic, "let currentDir = \"/\";\n        loadFiles();\n        loadStats();", code, flags=re.DOTALL)

# 4. Remove logout button from header
code = code.replace('<button class="icon-btn" onclick="logout()" title="Logout"><span class="material-symbols-outlined">logout</span></button>', '')

# 5. Remove `&token=${sessionToken}` from all URLs
code = code.replace('&token=${sessionToken}', '')

with open("index_html.h", "w") as f:
    f.write(code)

print("Fixed index_html.h!")
