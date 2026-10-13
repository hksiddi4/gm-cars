import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add intColorMap
old_decl = """            const stats_data = <%- JSON.stringify(stats_data) %>;
            const currentCategory = '<%= activeCategory %>';"""
new_decl = """            const stats_data = <%- JSON.stringify(stats_data) %>;
            const currentCategory = '<%= activeCategory %>';
            const intColorMap = <%- typeof intColor !== 'undefined' ? JSON.stringify(intColor) : '{}' %>;"""
c = c.replace(old_decl, new_decl)

# 2. Update chartLabels map for axis labels
old_chartLabels = """                    const chartLabels = displayData.map(d => {
                        if (currentCategory === 'color') {
                            const rpo = d.rpo_code || d.label;
                            const name = d.color_names ? d.color_names.split(',')[0].trim() : '';
                            
                            if (!name || rpo === name) return rpo;
                            return [rpo, ...wrapText(name, 22)];
                            
                        } else if (currentCategory === 'engine') {"""

new_chartLabels = """                    const chartLabels = displayData.map(d => {
                        if (currentCategory === 'color') {
                            const rpo = d.rpo_code || d.label;
                            const name = d.color_names ? d.color_names.split(',')[0].trim() : '';
                            
                            if (!name || rpo === name) return rpo;
                            return [rpo, ...wrapText(name, 22)];
                            
                        } else if (currentCategory === 'interior') {
                            const rpo = d.rpo_code || d.label;
                            const name = intColorMap[rpo] ? intColorMap[rpo].toUpperCase() : '';
                            
                            if (!name || rpo === name) return rpo;
                            return [rpo, ...wrapText(name, 22)];
                            
                        } else if (currentCategory === 'engine') {"""
c = c.replace(old_chartLabels, new_chartLabels)

# 3. Update tooltip callbacks
old_tooltip = """                                            if (item) {
                                                if (currentCategory === 'color') {
                                                    const rpo = item.rpo_code || item.label;
                                                    const name = item.color_names ? item.color_names.split(',')[0].trim() : '';
                                                    if (name && rpo !== name) {
                                                        return `${rpo} | ${name}`;
                                                    }
                                                    return rpo;
                                                } else if (currentCategory === 'engine') {"""

new_tooltip = """                                            if (item) {
                                                if (currentCategory === 'color') {
                                                    const rpo = item.rpo_code || item.label;
                                                    const name = item.color_names ? item.color_names.split(',')[0].trim() : '';
                                                    if (name && rpo !== name) {
                                                        return `${rpo} | ${name}`;
                                                    }
                                                    return rpo;
                                                } else if (currentCategory === 'interior') {
                                                    const rpo = item.rpo_code || item.label;
                                                    const name = intColorMap[rpo] ? intColorMap[rpo].toUpperCase() : '';
                                                    if (name && rpo !== name) {
                                                        return `${rpo} | ${name}`;
                                                    }
                                                    return rpo;
                                                } else if (currentCategory === 'engine') {"""
c = c.replace(old_tooltip, new_tooltip)

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied")
