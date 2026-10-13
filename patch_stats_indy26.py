import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

old_code = '"Z52 Track Performance Package": "FEY"'
new_code = old_code + ',\n                                                "2026 Indianapolis 500 Festival Vehicle": "INDY26"'

if old_code in c:
    c = c.replace(old_code, new_code)
    with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Success")
else:
    print("Not found")
