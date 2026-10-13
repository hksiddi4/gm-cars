import sys

with open('frontend/views/pages/vehicles.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update the module imports in vehicles.ejs
old_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;

        // Initialize state variables"""

new_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
        const sierraevRpo = <%- JSON.stringify(sierraevRpo) %>;

        // Initialize state variables"""

c = c.replace(old_script, new_script)

old_dataset = """                { data: celestiqRpo, label: 'Celestiq' },
                { data: silveradoevRpo, label: 'Silverado EV' }
            ];"""

new_dataset = """                { data: celestiqRpo, label: 'Celestiq' },
                { data: silveradoevRpo, label: 'Silverado EV' },
                { data: sierraevRpo, label: 'Sierra EV' }
            ];"""

c = c.replace(old_dataset, new_dataset)

with open('frontend/views/pages/vehicles.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to vehicles.ejs")
