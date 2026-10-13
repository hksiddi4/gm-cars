const fs = require('fs');
let c = fs.readFileSync('frontend/views/pages/stats.ejs', 'utf8');
c = c.replace(/imgSrc = localRpoImageMap\[\\`\\$\\{prefixKey\\}-\\$\\{data\.rpo_code\\}\\`\];/g, 'imgSrc = localRpoImageMap[`${prefixKey}-${data.rpo_code}`];');
fs.writeFileSync('frontend/views/pages/stats.ejs', c, 'utf8');
