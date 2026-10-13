import re

with open('backend/start.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_code = """    elif category == 'interior':
        import re, os
        interior_rpos = []
        try:
            mod_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'views', 'partials', 'modules.js')
            with open(mod_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'const intColor\\s*=\\s*\\{([\\s\\S]*?)\\};', content)
            if match:
                interior_rpos = re.findall(r'"([A-Z0-9]+)"\\s*:', match.group(1))
        except Exception as e:
            print('Error parsing modules.js', e)
            
        rpo_list_str = "'" + "','".join(interior_rpos) + "'" if interior_rpos else "''"
"""

new_code = """    elif category == 'interior':
        interior_rpos_param = request.args.get('interiorRPOs', '')
        interior_rpos = [x.strip() for x in interior_rpos_param.split(',')] if interior_rpos_param else []
        rpo_list_str = "'" + "','".join(interior_rpos) + "'" if interior_rpos else "''"
"""

c = c.replace(old_code, new_code)
with open('backend/start.py', 'w', encoding='utf-8') as f:
    f.write(c)
