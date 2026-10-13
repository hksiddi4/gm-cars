import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# I will inject a reusable query string builder in EJS at the top of the table blocks, or just append it locally.
# Actually, I can just create a variable `const filterParams = ...` at the top of the stats.ejs body, but I can't easily execute JS EJS in all places safely without breaking scope.
# Let's just create a snippet:
snippet = """
<% 
    let baseParams = "";
    if (typeof selectedYear !== 'undefined' && selectedYear) baseParams += "&year=" + encodeURIComponent(selectedYear);
    if (typeof selectedModel !== 'undefined' && selectedModel) baseParams += "&model=" + encodeURIComponent(selectedModel);
    if (typeof selectedBody !== 'undefined' && selectedBody) baseParams += "&body=" + encodeURIComponent(selectedBody);
    if (typeof selectedTrim !== 'undefined' && selectedTrim) baseParams += "&trim=" + encodeURIComponent(selectedTrim);
    if (typeof selectedEngine !== 'undefined' && selectedEngine) baseParams += "&engine=" + encodeURIComponent(selectedEngine);
    if (typeof selectedTrans !== 'undefined' && selectedTrans) baseParams += "&trans=" + encodeURIComponent(selectedTrans);
%>
"""

# Let's insert this snippet before the first `<tbody>` in the main block.
c = c.replace('<tbody>\n                                        <% multiItems.forEach', snippet + '<tbody>\n                                        <% multiItems.forEach')

# Update the linkHref constructions in multiItems
c = c.replace(
    'let linkHref = "/vehicles?color=" + encodeURIComponent(trimmedName);',
    'let linkHref = "/vehicles?color=" + encodeURIComponent(trimmedName) + baseParams;'
)

c = c.replace(
    '<a class="color-link" href="/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %>">',
    '<a class="color-link" href="/vehicles?rpo=<%= encodeURIComponent(data.rpo_code) %><%= baseParams %>">'
)

c = c.replace(
    '<a class="color-link" href="/vehicles?engine=<%= encodeURIComponent(data.engine_type) %>"',
    '<a class="color-link" href="/vehicles?engine=<%= encodeURIComponent(data.engine_type) %><%= baseParams %>"'
)

# And for singleItems
c = c.replace('<tbody>\n                                                <% singleItems.forEach', snippet + '<tbody>\n                                                <% singleItems.forEach')

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied to append baseParams to links")
