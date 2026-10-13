import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

old_chartLabels = """                        } else if (currentCategory === 'interior') {
                            const rpo = d.rpo_code || d.label;
                            const name = intColorMap[rpo] ? intColorMap[rpo].toUpperCase() : '';
                            
                            if (!name || rpo === name) return rpo;
                            return [rpo, ...wrapText(name, 22)];
                            
                        } else if (currentCategory === 'engine') {"""

new_chartLabels = """                        } else if (currentCategory === 'interior') {
                            return d.rpo_code || d.label;
                            
                        } else if (currentCategory === 'engine') {"""

if old_chartLabels in c:
    c = c.replace(old_chartLabels, new_chartLabels)
    with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Patch applied")
else:
    print("Block not found")
