import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# The snippet I injected earlier
snippet_to_remove = """                                
                                let baseParams = "";
                                if (typeof selectedYear !== 'undefined' && selectedYear) baseParams += "&year=" + encodeURIComponent(selectedYear);
                                if (typeof selectedModel !== 'undefined' && selectedModel) baseParams += "&model=" + encodeURIComponent(selectedModel);
                                if (typeof selectedBody !== 'undefined' && selectedBody) baseParams += "&body=" + encodeURIComponent(selectedBody);
                                if (typeof selectedTrim !== 'undefined' && selectedTrim) baseParams += "&trim=" + encodeURIComponent(selectedTrim);
                                if (typeof selectedEngine !== 'undefined' && selectedEngine) baseParams += "&engine=" + encodeURIComponent(selectedEngine);
                                if (typeof selectedTrans !== 'undefined' && selectedTrans) baseParams += "&trans=" + encodeURIComponent(selectedTrans);
"""

c = c.replace(snippet_to_remove, "")

# Now inject it right after `<body>`
snippet_to_inject = """<body>
<% 
    let baseParams = "";
    if (typeof selectedYear !== 'undefined' && selectedYear) baseParams += "&year=" + encodeURIComponent(selectedYear);
    if (typeof selectedModel !== 'undefined' && selectedModel) baseParams += "&model=" + encodeURIComponent(selectedModel);
    if (typeof selectedBody !== 'undefined' && selectedBody) baseParams += "&body=" + encodeURIComponent(selectedBody);
    if (typeof selectedTrim !== 'undefined' && selectedTrim) baseParams += "&trim=" + encodeURIComponent(selectedTrim);
    if (typeof selectedEngine !== 'undefined' && selectedEngine) baseParams += "&engine=" + encodeURIComponent(selectedEngine);
    if (typeof selectedTrans !== 'undefined' && selectedTrans) baseParams += "&trans=" + encodeURIComponent(selectedTrans);
%>"""

c = c.replace('<body>', snippet_to_inject)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied for global baseParams definition")
