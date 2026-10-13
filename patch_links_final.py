import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

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

# Insert snippet after `<div class="container-fluid stats-container py-4">`
c = c.replace('<div class="container-fluid stats-container py-4">', '<div class="container-fluid stats-container py-4">' + snippet)

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

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied")
