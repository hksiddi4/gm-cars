import sys

with open('frontend/views/pages/wheels.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update the module imports in wheels.ejs
old_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
        const localRpoImageMap = <%- JSON.stringify(localRpoImageMap) %>;"""

new_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
        const sierraevRpo = <%- JSON.stringify(sierraevRpo) %>;
        const localRpoImageMap = <%- JSON.stringify(localRpoImageMap) %>;"""

c = c.replace(old_script, new_script)

old_rpoDescriptions = """            ...celestiqRpo,
            ...silveradoevRpo
        };"""

new_rpoDescriptions = """            ...celestiqRpo,
            ...silveradoevRpo,
            ...sierraevRpo
        };"""

c = c.replace(old_rpoDescriptions, new_rpoDescriptions)

old_case = """                case 'CELESTIQ': return celestiqRpo[rpoCode];
                case 'SILVERADO EV': return silveradoevRpo[rpoCode];
                case 'CORVETTE (ALL)': return corvetteRpo[rpoCode];"""

new_case = """                case 'CELESTIQ': return celestiqRpo[rpoCode];
                case 'SILVERADO EV': return silveradoevRpo[rpoCode];
                case 'SIERRA EV': return sierraevRpo[rpoCode];
                case 'CORVETTE (ALL)': return corvetteRpo[rpoCode];"""

c = c.replace(old_case, new_case)

with open('frontend/views/pages/wheels.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to wheels.ejs")
