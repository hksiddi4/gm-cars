const fs = require('fs');
let c = fs.readFileSync('frontend/views/pages/search.ejs', 'utf-8');

c = c.replace(/`CADILLAC-\${rpoCode}`/g, 'null');
c = c.replace(/`GMC-\${rpoCode}`/g, 'null');
c = c.replace(/`CHEVROLET-\${rpoCode}`/g, 'null');

const ct5Block = `          } else if (modelUpper.startsWith('CT5')) {
              const cCandidates = [
                  vehicleTrim.startsWith('V-SERIES') ? \`CT5V-\${rpoCode}\` : null,
                  \`CT5-\${rpoCode}\`,
                  null
              ].filter(Boolean);
              for (const key of cCandidates) {
                  if (localRpoImageMap[key]) { imgSrc = localRpoImageMap[key]; break; }
              }`;

const ct6Block = `          } else if (modelUpper.startsWith('CT6')) {
              const cCandidates = [
                  vehicleTrim.startsWith('V-SERIES') ? \`CT6V-\${rpoCode}\` : null,
                  \`CT6-\${rpoCode}\`
              ].filter(Boolean);
              for (const key of cCandidates) {
                  if (localRpoImageMap[key]) { imgSrc = localRpoImageMap[key]; break; }
              }`;

if (!c.includes("modelUpper.startsWith('CT6')")) {
    c = c.replace(ct5Block, ct5Block + '\n' + ct6Block);
}

fs.writeFileSync('frontend/views/pages/search.ejs', c);
