const fs = require('fs');
let c = fs.readFileSync('frontend/views/partials/modules.js', 'utf-8');
c = c.split('"WOX": "Cadillac Curated Customization"').join('"WOX": "Curated by Cadillac"');
fs.writeFileSync('frontend/views/partials/modules.js', c);
