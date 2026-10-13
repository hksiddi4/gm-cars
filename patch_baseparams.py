import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

snippet = """
                                let baseParams = "";
                                if (typeof selectedYear !== 'undefined' && selectedYear) baseParams += "&year=" + encodeURIComponent(selectedYear);
                                if (typeof selectedModel !== 'undefined' && selectedModel) baseParams += "&model=" + encodeURIComponent(selectedModel);
                                if (typeof selectedBody !== 'undefined' && selectedBody) baseParams += "&body=" + encodeURIComponent(selectedBody);
                                if (typeof selectedTrim !== 'undefined' && selectedTrim) baseParams += "&trim=" + encodeURIComponent(selectedTrim);
                                if (typeof selectedEngine !== 'undefined' && selectedEngine) baseParams += "&engine=" + encodeURIComponent(selectedEngine);
                                if (typeof selectedTrans !== 'undefined' && selectedTrans) baseParams += "&trans=" + encodeURIComponent(selectedTrans);
"""

c = c.replace('let titlePrefix = "Daily Production: ";', snippet + '\n                                let titlePrefix = "Daily Production: ";')

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied for baseParams definition")
