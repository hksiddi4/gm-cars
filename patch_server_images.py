import sys

with open('frontend/server.js', 'r', encoding='utf-8') as f:
    c = f.read()

old_block = """                    if (prefix) {
                        const formattedPrefix = prefix.replace(/\\//g, '-').toUpperCase();
                        if (!localRpoImages[`${formattedPrefix}-${rpoCode}`]) {
                            localRpoImages[`${formattedPrefix}-${rpoCode}`] = imagePath;
                        }
                    } else {
                        if (!localRpoImages[rpoCode]) {
                            localRpoImages[rpoCode] = imagePath;
                        }
                    }"""

new_block = """                    if (prefix) {
                        const formattedPrefix = prefix.replace(/\\//g, '-').toUpperCase();
                        if (!localRpoImages[`${formattedPrefix}-${rpoCode}`]) {
                            localRpoImages[`${formattedPrefix}-${rpoCode}`] = imagePath;
                        }
                        if (!localRpoImages[rpoCode]) {
                            localRpoImages[rpoCode] = imagePath;
                        }
                    } else {
                        if (!localRpoImages[rpoCode]) {
                            localRpoImages[rpoCode] = imagePath;
                        }
                    }"""

if old_block in c:
    c = c.replace(old_block, new_block)
    with open('frontend/server.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Patch applied")
else:
    print("Block not found")
