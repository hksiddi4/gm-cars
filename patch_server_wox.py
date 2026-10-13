import sys

with open('frontend/server.js', 'r', encoding='utf-8') as f:
    c = f.read()

old_block = """function getRpoImageCandidates(modelUpper, vehicleTrim, rpoCode, options = []) {
    const candidates = [];
    const prefixKey = modelUpper.replace(/ /g, '').toUpperCase();"""

new_block = """function getRpoImageCandidates(modelUpper, vehicleTrim, rpoCode, options = []) {
    if (rpoCode === 'WOX') rpoCode = 'HMR';
    const candidates = [];
    const prefixKey = modelUpper.replace(/ /g, '').toUpperCase();"""

if old_block in c:
    c = c.replace(old_block, new_block)
    with open('frontend/server.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Patch applied for WOX -> HMR alias")
else:
    print("Block not found")
