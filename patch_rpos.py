import sys

with open('frontend/views/pages/rpos.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

old_rpo = """            silveradoev: <%- JSON.stringify(silveradoevRpo || {}) %>,
        };"""

new_rpo = """            silveradoev: <%- JSON.stringify(silveradoevRpo || {}) %>,
            sierraev: <%- JSON.stringify(sierraevRpo || {}) %>,
        };"""

if old_rpo in c:
    c = c.replace(old_rpo, new_rpo)
    with open('frontend/views/pages/rpos.ejs', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Patch applied to rpos.ejs")
else:
    print("Block not found")
