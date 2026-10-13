import sys

with open('frontend/views/pages/search.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update the module imports in search.ejs
old_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;

        // Create a unified mapping object combining all specific rpo sets"""

new_script = """        const celestiqRpo = <%- JSON.stringify(celestiqRpo) %>;
        const silveradoevRpo = <%- JSON.stringify(silveradoevRpo) %>;
        const sierraevRpo = <%- JSON.stringify(sierraevRpo) %>;

        // Create a unified mapping object combining all specific rpo sets"""

c = c.replace(old_script, new_script)

# 2. Update allModelRpos
old_allModelRpos = """        ...hummersuvRpo, ...celestiqRpo, ...silveradoevRpo,
      };"""

new_allModelRpos = """        ...hummersuvRpo, ...celestiqRpo, ...silveradoevRpo, ...sierraevRpo,
      };"""

c = c.replace(old_allModelRpos, new_allModelRpos)

# 3. Add to display rpo descriptions conditionally
old_display = """            (derivedModel === 'SILVERADO EV' && silveradoevRpo[rpoCode])
          ) {
            hasModelSpecificDesc = true;
          }"""

new_display = """            (derivedModel === 'SILVERADO EV' && silveradoevRpo[rpoCode]) ||
            (derivedModel === 'SIERRA EV' && sierraevRpo[rpoCode])
          ) {
            hasModelSpecificDesc = true;
          }"""

c = c.replace(old_display, new_display)

old_html = """        if (derivedModel === 'CELESTIQ' && celestiqRpo[rpoCode]) { element.innerHTML = `<div>${celestiqRpo[rpoCode]}</div>`; return; }
        if (derivedModel === 'SILVERADO EV' && silveradoevRpo[rpoCode]) { element.innerHTML = `<div>${silveradoevRpo[rpoCode]}</div>`; return; }"""

new_html = """        if (derivedModel === 'CELESTIQ' && celestiqRpo[rpoCode]) { element.innerHTML = `<div>${celestiqRpo[rpoCode]}</div>`; return; }
        if (derivedModel === 'SILVERADO EV' && silveradoevRpo[rpoCode]) { element.innerHTML = `<div>${silveradoevRpo[rpoCode]}</div>`; return; }
        if (derivedModel === 'SIERRA EV' && sierraevRpo[rpoCode]) { element.innerHTML = `<div>${sierraevRpo[rpoCode]}</div>`; return; }"""

c = c.replace(old_html, new_html)

with open('frontend/views/pages/search.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to search.ejs")
