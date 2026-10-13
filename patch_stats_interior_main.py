import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

old_image_logic = """                                                        <%
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

new_image_logic = """                                                        <%
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

print("Patch applied for main table images")
