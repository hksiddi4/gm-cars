import sys
import json

with open('sierra_rpos.json', 'r', encoding='utf-8') as f:
    sierra_data = f.read()

with open('frontend/views/partials/modules.js', 'r', encoding='utf-8') as f:
    c = f.read()

sierra_decl = "\nconst sierraevRpo = " + sierra_data + ";\n\nmodule.exports ="
c = c.replace("module.exports =", sierra_decl)
c = c.replace("  silveradoevRpo,\n}", "  silveradoevRpo,\n  sierraevRpo,\n}")

with open('frontend/views/partials/modules.js', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to modules.js")
