import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "<% if (['color', 'engine'].includes(activeCategory)) { %>",
    "<% if (['color', 'engine', 'interior'].includes(activeCategory)) { %>"
)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to show filters for interior")
