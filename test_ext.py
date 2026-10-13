import re, os
interior_rpos = []
try:
    mod_path = os.path.join('.', 'frontend', 'views', 'partials', 'modules.js')
    with open(mod_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'const intColor\s*=\s*\{([\s\S]*?)\};', content)
    if match:
        interior_rpos = re.findall(r'"([A-Z0-9]+)"\s*:', match.group(1))
except Exception as e:
    print('Error parsing modules.js', e)

print('Extracted:', len(interior_rpos), interior_rpos)
