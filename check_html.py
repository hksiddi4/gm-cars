import sys

with open('frontend/views/pages/stats.ejs', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'id="filterYear"' in line:
        start = max(0, i - 15)
        end = min(len(lines), i + 20)
        print("".join(lines[start:end]))
        break
