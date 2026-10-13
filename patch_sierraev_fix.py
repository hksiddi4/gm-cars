import sys

with open('frontend/views/pages/vehicles.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# Add the missing const declaration
old_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;

        function buildQueryString"""

new_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
        const sierraevRpo = <%- JSON.stringify(sierraevRpo) %>;

        function buildQueryString"""

if old_script in c:
    c = c.replace(old_script, new_script)
    with open('frontend/views/pages/vehicles.ejs', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Fixed sierraevRpo definition in vehicles.ejs")
else:
    print("Could not find the target string to replace.")
