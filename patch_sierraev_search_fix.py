import sys

with open('frontend/views/pages/search.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

old_script = """      const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
      const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;

      const invertedColorMap"""

new_script = """      const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
      const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
      const sierraevRpo = <%- JSON.stringify(sierraevRpo) %>;

      const invertedColorMap"""

if old_script in c:
    c = c.replace(old_script, new_script)
    with open('frontend/views/pages/search.ejs', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Fixed sierraevRpo definition in search.ejs")
else:
    print("Could not find the target string to replace in search.ejs.")
