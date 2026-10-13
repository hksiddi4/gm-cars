import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "if (currentCategory === 'color') {\n                        rawData = rawData.filter(d => d.count > 1);\n                    }",
    "if (currentCategory === 'color' || currentCategory === 'interior') {\n                        rawData = rawData.filter(d => d.count > 1);\n                    }"
)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied for chart data")
