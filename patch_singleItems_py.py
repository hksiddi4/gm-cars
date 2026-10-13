import re

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '''<td scope=\"row\" style=\"white-space: nowrap; text-align: left; width: 200px;\">
                                                            <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                            <%= data.label %>
                                                        </td>''',
    '''<td scope=\"row\" style=\"white-space: nowrap; text-align: left; width: 200px;\">
                                                            <% if (activeCategory === 'color') { %>
                                                                <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
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
                                                                <img src=\"<%= imgSrc %>\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                                <%= data.label %>
                                                            <% } %>
                                                        </td>'''
)

c = c.replace(
    '''<td scope=\"row\" style=\"text-align: left;\">
                                                            <% if (data.color_names) { %>
                                                                <% data.color_names.split(',').forEach((name, i) => { 
                                                                    const trimmedName = name.trim();
                                                                    let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                                    if (data.rpo_code && data.rpo_code !== trimmedName) linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                                %>
                                                                    <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                                <% }) %>
                                                            <% } %>
                                                        </td>''',
    '''<td scope=\"row\" style=\"text-align: left;\">
                                                            <% if (activeCategory === 'color') { %>
                                                                <% if (data.color_names) { %>
                                                                    <% data.color_names.split(',').forEach((name, i) => { 
                                                                        const trimmedName = name.trim();
                                                                        let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                                        if (data.rpo_code && data.rpo_code !== trimmedName) linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                                    %>
                                                                        <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                                    <% }) %>
                                                                <% } %>
                                                            <% } else if (activeCategory === 'interior') { %>
                                                                <% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code] : 'N/A'; %>
                                                                <a class=\"color-link\" href=\"/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %>\"><%= intName %></a>
                                                            <% } %>
                                                        </td>'''
)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)
