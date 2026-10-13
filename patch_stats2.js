const fs = require('fs');

let c = fs.readFileSync('frontend/views/pages/stats.ejs', 'utf8');

c = c.replace(/<% if \(activeCategory === 'color'\) \{ %><th scope="col">Names<\/th><% \} %>/g, 
`<% if (activeCategory === 'color' || activeCategory === 'interior') { %><th scope="col">Names</th><% } %>`);

c = c.replace(/<% if \(activeCategory === 'color'\) \{ %>\s*<img src="\/img\/extColors\/<%= data.rpo_code %>.webp" alt="<%= data.label %> color swatch" data-fallback="\/img\/extColors\/default.webp" width="20" height="20" style="margin-right: 8px; border-radius: 50%;">\s*<%= data.label %>\s*<% \} else if \(activeCategory === 'engine'\) \{ %>/g,
`<% if (activeCategory === 'color') { %>
                                                        <img src="/img/extColors/<%= data.rpo_code %>.webp" alt="<%= data.label %> color swatch" data-fallback="/img/extColors/default.webp" width="20" height="20" style="margin-right: 8px; border-radius: 50%;">
                                                        <%= data.label %>
                                                    <% } else if (activeCategory === 'interior') { %>
                                                        <%
                                                            let imgSrc = '';
                                                            if (typeof localRpoImageMap !== 'undefined') {
                                                                if (typeof active_model !== 'undefined' && active_model) {
                                                                    const prefixKey = active_model.replace(/ /g, '').toUpperCase();
                                                                    imgSrc = localRpoImageMap[\`\${prefixKey}-\${data.rpo_code}\`];
                                                                }
                                                                if (!imgSrc) imgSrc = localRpoImageMap[data.rpo_code];
                                                            }
                                                            if (!imgSrc) imgSrc = '/img/extColors/default.webp';
                                                        %>
                                                        <img src="<%= imgSrc %>" alt="<%= data.label %> color swatch" data-fallback="/img/extColors/default.webp" width="20" height="20" style="margin-right: 8px; border-radius: 50%;">
                                                        <%= data.label %>
                                                    <% } else if (activeCategory === 'engine') { %>`);

c = c.replace(/<% if \(activeCategory === 'color'\) \{ %>\s*<td scope="row" style="text-align: left;">\s*<% if \(data.color_names\) \{ %>\s*<% data.color_names.split\(\',\'.forEach\(\(name, i\) => \{/g, 
`<% if (activeCategory === 'color') { %>
                                                    <td scope="row" style="text-align: left;">
                                                    <% if (data.color_names) { %>
                                                        <% data.color_names.split(',').forEach((name, i) => {`);

c = c.replace(/<% } %>\s*<% } %>\s*<\/td>\s*<% } %>/g,
`<% }) %>
                                                    <% } %>
                                                    </td>
                                                <% } else if (activeCategory === 'interior') { %>
                                                    <td scope="row" style="text-align: left;">
                                                        <% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code] : 'N/A'; %>
                                                        <a class="color-link" href="/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %>"><%= intName %></a>
                                                    </td>
                                                <% } %>`);

c = c.replace(/<% if \(activeCategory === 'color' && singleItems\.length > 0\) \{ %>/g, 
`<% if ((activeCategory === 'color' || activeCategory === 'interior') && singleItems.length > 0) { %>`);

c = c.replace(/<% if \(activeCategory === 'color'\) \{ %>\s*multiItems = stats_data.filter\(d => Number\(String\(d.total_count\).replace\(\/\,\/g, ''\)\) > 1\);\s*singleItems = stats_data.filter\(d => Number\(String\(d.total_count\).replace\(\/\,\/g, ''\)\) === 1\);\s*<% \} %>/g,
`<% if (activeCategory === 'color' || activeCategory === 'interior') {
                                    multiItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) > 1);
                                    singleItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) === 1);
                                }
                            %>`);

fs.writeFileSync('frontend/views/pages/stats.ejs', c, 'utf8');
