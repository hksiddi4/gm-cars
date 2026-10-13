import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix singleItems logic
c = c.replace(
    "if (activeCategory === 'color') {\n                                    multiItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) > 1);\n                                    singleItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) === 1);\n                                }",
    "if (activeCategory === 'color' || activeCategory === 'interior') {\n                                    multiItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) > 1);\n                                    singleItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) === 1);\n                                }"
)

# 2. Main table - Exterior color uppercase
c = c.replace(
    '<a class="color-link" href="<%= linkHref %>"><%= trimmedName %></a>',
    '<a class="color-link" href="<%= linkHref %>"><%= trimmedName.toUpperCase() %></a>'
)

# 3. Main table - Interior color uppercase
c = c.replace(
    "<% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code] : 'N/A'; %>",
    "<% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code].toUpperCase() : 'N/A'; %>"
)

# 4. Fix image resolution for interior in main table AND 1-of-1 table.
old_image_logic = """                                                                <%
                                                                    let imgSrc = '';
                                                                    if (typeof localRpoImageMap !== 'undefined') {
                                                                        if (typeof active_model !== 'undefined' && active_model) {
                                                                            const prefixKey = active_model.replace(/ /g, '').toUpperCase();
                                                                            imgSrc = localRpoImageMap[`${prefixKey}-${data.rpo_code}`];
                                                                        }
                                                                        if (!imgSrc) imgSrc = localRpoImageMap[data.rpo_code];
                                                                    }
                                                                    if (!imgSrc) imgSrc = '/img/extColors/default.webp';
                                                                %>
                                                                <img src="<%= imgSrc %>" alt="<%= data.label %> color swatch" data-fallback="/img/extColors/default.webp" width="20" height="20" style="margin-right: 8px; border-radius: 50%;">"""

new_image_logic = """                                                                <%
                                                                    let imgSrc = '';
                                                                    if (typeof localRpoImageMap !== 'undefined' && typeof getRpoImageCandidates === 'function') {
                                                                        const candidates = getRpoImageCandidates(selectedModel || '', selectedTrim || '', data.rpo_code, []);
                                                                        for (const cand of candidates) {
                                                                            if (localRpoImageMap[cand]) {
                                                                                imgSrc = localRpoImageMap[cand];
                                                                                break;
                                                                            }
                                                                        }
                                                                        if (!imgSrc) imgSrc = localRpoImageMap[data.rpo_code];
                                                                    }
                                                                    if (!imgSrc) imgSrc = '/img/rpos/default.webp';
                                                                %>
                                                                <img src="<%= imgSrc %>" alt="<%= data.label %> color swatch" data-fallback="/img/rpos/default.webp" width="20" height="20" style="margin-right: 8px; border-radius: 50%;">"""

c = c.replace(old_image_logic, new_image_logic)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied")
