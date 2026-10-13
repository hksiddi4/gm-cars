import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace width="20" height="20" with width="80" height="80" and add align-middle to td
c = c.replace(
    'width="20" height="20" style="margin-right: 8px; border-radius: 50%;"',
    'width="80" height="80" style="margin-right: 15px; border-radius: 50%; object-fit: cover; vertical-align: middle;"'
)

# Find all <tr> and replace with <tr class="align-middle"> in the table blocks
# Or just replace `<td scope="row"` with `<td scope="row" class="align-middle"`
c = c.replace('<td scope="row">', '<td scope="row" class="align-middle">')
c = c.replace('<td scope="row" style="', '<td scope="row" class="align-middle" style="')

with open('frontend/views/pages/stats.ejs', 'w', encoding='utf-8') as f:
    f.write(c)

print("Patch applied for larger images and centered text")
