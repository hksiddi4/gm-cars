const fs = require('fs');
let c = fs.readFileSync('frontend/server.js', 'utf-8');

c = c.replace(/    \} else \{\r?\n        candidates\.push[^;]+;\r?\n        candidates\.push[^;]+;\r?\n    \}\r?\n\r?\n    return candidates;/m, 
`    } else {
        candidates.push(\`\${modelUpper.replace(/ /g, '-')}-\${rpoCode}\`);
        candidates.push(\`\${modelUpper.replace(/ /g, '')}-\${rpoCode}\`);
    }

    candidates.push(rpoCode);

    return candidates;`);

fs.writeFileSync('frontend/server.js', c);
