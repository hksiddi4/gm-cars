import re

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    '<% if (activeCategory === \'color\') { %><th scope=\"col\">Names</th><% } %>',
    '<% if (activeCategory === \'color\' or activeCategory === \'interior\') { %><th scope=\"col\">Names</th><% } %>'
)

c = c.replace(
    '<% if (activeCategory === \'color\' && singleItems.length > 0) { %>',
    '<% if ((activeCategory === \'color\' || activeCategory === \'interior\') && singleItems.length > 0) { %>'
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                    multiItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) > 1);
                                    singleItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) === 1);
                                }''',
    '''<% if (activeCategory === 'color' || activeCategory === 'interior') {
                                    multiItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) > 1);
                                    singleItems = stats_data.filter(d => Number(String(d.total_count).replace(/,/g, '')) === 1);
                                }'''
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                                        <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                        <%= data.label %>
                                                    <% } else if (activeCategory === 'engine') { %>''',
    '''<% if (activeCategory === 'color') { %>
                                                        <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                        <%= data.label %>
                                                    <% } else if (activeCategory === 'interior') { %>
                                                        <%
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
                                                        <img src=\"<%= imgSrc %>\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                        <%= data.label %>
                                                    <% } else if (activeCategory === 'engine') { %>'''
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                                    <td scope=\"row\" style=\"text-align: left;\">
                                                    <% if (data.color_names) { %>
                                                        <% data.color_names.split(',').forEach((name, i) => { 
                                                            const trimmedName = name.trim();
                                                            let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                            if (data.rpo_code && data.rpo_code !== trimmedName) {
                                                                linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                            }
                                                        %>
                                                            <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                        <% }) %>
                                                    <% } %>
                                                    </td>
                                                <% } %>''',
    '''<% if (activeCategory === 'color') { %>
                                                    <td scope=\"row\" style=\"text-align: left;\">
                                                    <% if (data.color_names) { %>
                                                        <% data.color_names.split(',').forEach((name, i) => { 
                                                            const trimmedName = name.trim();
                                                            let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                            if (data.rpo_code && data.rpo_code !== trimmedName) {
                                                                linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                            }
                                                        %>
                                                            <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                        <% }) %>
                                                    <% } %>
                                                    </td>
                                                <% } else if (activeCategory === 'interior') { %>
                                                    <td scope=\"row\" style=\"text-align: left;\">
                                                        <% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code] : 'N/A'; %>
                                                        <a class=\"color-link\" href=\"/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %>\"><%= intName %></a>
                                                    </td>
                                                <% } %>'''
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                                            <th scope=\"col\">Names</th>
                                                        <% } %>''',
    '''<% if (activeCategory === 'color' || activeCategory === 'interior') { %>
                                                            <th scope=\"col\">Names</th>
                                                        <% } %>'''
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                                            <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                            <%= data.label %>
                                                        <% } %>''',
    '''<% if (activeCategory === 'color') { %>
                                                            <img src=\"/img/extColors/<%= data.rpo_code %>.webp\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                            <%= data.label %>
                                                        <% } else if (activeCategory === 'interior') { %>
                                                            <%
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
                                                            <img src=\"<%= imgSrc %>\" alt=\"<%= data.label %> color swatch\" data-fallback=\"/img/extColors/default.webp\" width=\"20\" height=\"20\" style=\"margin-right: 8px; border-radius: 50%;\">
                                                            <%= data.label %>
                                                        <% } %>'''
)

c = c.replace(
    '''<% if (activeCategory === 'color') { %>
                                                            <td scope=\"row\" style=\"text-align: left;\">
                                                                <% if (data.color_names) { %>
                                                                    <% data.color_names.split(',').forEach((name, i) => { 
                                                                        const trimmedName = name.trim();
                                                                        let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                                        if (data.rpo_code && data.rpo_code !== trimmedName) linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                                    %>
                                                                        <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                                    <% }) %>
                                                                <% } %>
                                                            </td>
                                                        <% } %>''',
    '''<% if (activeCategory === 'color') { %>
                                                            <td scope=\"row\" style=\"text-align: left;\">
                                                                <% if (data.color_names) { %>
                                                                    <% data.color_names.split(',').forEach((name, i) => { 
                                                                        const trimmedName = name.trim();
                                                                        let linkHref = \"/vehicles?color=\" + encodeURIComponent(trimmedName);
                                                                        if (data.rpo_code && data.rpo_code !== trimmedName) linkHref += \"&rpo=\" + encodeURIComponent(data.rpo_code);
                                                                    %>
                                                                        <a class=\"color-link\" href=\"<%= linkHref %>\"><%= trimmedName %></a><%= i < data.color_names.split(',').length - 1 ? ', ' : '' %>
                                                                    <% }) %>
                                                                <% } %>
                                                            </td>
                                                        <% } else if (activeCategory === 'interior') { %>
                                                            <td scope=\"row\" style=\"text-align: left;\">
                                                                <% const intName = (typeof intColor !== 'undefined' && intColor[data.rpo_code]) ? intColor[data.rpo_code] : 'N/A'; %>
                                                                <a class=\"color-link\" href=\"/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %>\"><%= intName %></a>
                                                            </td>
                                                        <% } %>'''
)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)
