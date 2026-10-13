const fs = require('fs');
let c = fs.readFileSync('frontend/server.js', 'utf8');
c = c.replace(/localRpoImageMap: res\.locals\.localRpoImageMap,/g, 
`localRpoImageMap: res.locals.localRpoImageMap,
                intColor: modules.intColor,`);
fs.writeFileSync('frontend/server.js', c, 'utf8');
