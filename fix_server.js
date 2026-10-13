const fs = require('fs');

let content = fs.readFileSync('frontend/server.js', 'utf8');

const regex = /function getRpoImageCandidates\([^\{]*\{[\s\S]*?return candidates;\r?\n\}/;

const replacement = `function getRpoImageCandidates(modelUpper, vehicleTrim, rpoCode, options = []) {
    const candidates = [];
    const prefixKey = modelUpper.replace(/ /g, '').toUpperCase();
    
    if (modelUpper.startsWith('CORVETTE')) {
        let subPrefix = 'CORVETTE-STINGRAY';
        
        if (modelUpper.includes('ZR1X') || (options.includes('LS9') && (vehicleTrim.includes('ZR1X') || modelUpper.includes('X')))) {
            subPrefix = 'CORVETTE-ZR1X';
        } else if (modelUpper.includes('ZR1') || options.includes('LS9')) {
            subPrefix = 'CORVETTE-ZR1';
        } else if (modelUpper.includes('Z06') || options.includes('LT6')) {
            subPrefix = 'CORVETTE-Z06';
        } else if (modelUpper.includes('GRAND SPORT X') || (options.includes('LS6') && (vehicleTrim.includes('GSX') || modelUpper.includes('X')))) {
            subPrefix = 'CORVETTE-GRAND_SPORT_X';
        } else if (modelUpper.includes('GRAND SPORT') || options.includes('LS6')) {
            subPrefix = 'CORVETTE-GRAND_SPORT';
        } else if (modelUpper.includes('E-RAY') || options.includes('HP1')) {
            subPrefix = 'CORVETTE-E-RAY';
        }

        candidates.push(\`\${subPrefix}-\${rpoCode}\`);

        // Submodel fallbacks
          if (subPrefix === 'CORVETTE-GRAND_SPORT_X') {
              candidates.push(\`CORVETTE-GRAND_SPORT-\${rpoCode}\`);
          } else if (subPrefix === 'CORVETTE-ZR1X') {
              candidates.push(\`CORVETTE-ZR1-\${rpoCode}\`);
              candidates.push(\`CORVETTE-Z06-\${rpoCode}\`);
          }

          if (subPrefix !== 'CORVETTE-STINGRAY') {
              candidates.push(\`CORVETTE-STINGRAY-\${rpoCode}\`);
          }

        // Base Corvette shared folder (/img/rpos/corvette/RPO.webp)
        candidates.push(\`CORVETTE-\${rpoCode}\`);

    } else if (modelUpper === 'CAMARO') {
        candidates.push(\`CAMARO-\${rpoCode}\`);

    } else if (modelUpper.startsWith('CT4')) {
        if (vehicleTrim.startsWith('V-SERIES') || modelUpper.includes('V')) {
            candidates.push(\`CT4V-\${rpoCode}\`);
        }
        candidates.push(\`CT4-\${rpoCode}\`);

    } else if (modelUpper.startsWith('CT5')) {
        if (vehicleTrim.startsWith('V-SERIES') || modelUpper.includes('V')) {
            candidates.push(\`CT5V-\${rpoCode}\`);
        }
        candidates.push(\`CT5-\${rpoCode}\`);

    } else if (modelUpper.startsWith('CT6')) {
        if (vehicleTrim.startsWith('V-SERIES') || modelUpper.includes('V')) {
            candidates.push(\`CT6V-\${rpoCode}\`);
        }
        candidates.push(\`CT6-\${rpoCode}\`);

    } else if (modelUpper.includes('ESCALADE IQ')) {
        candidates.push(\`ESCALADEIQ-\${rpoCode}\`);
        candidates.push(\`ESCALADE-IQ-\${rpoCode}\`);
        candidates.push(\`ESCALADE-\${rpoCode}\`);

    } else if (modelUpper.startsWith('ESCALADE')) {
        candidates.push(\`ESCALADE-\${rpoCode}\`);

    } else if (modelUpper === 'HUMMER EV SUV') {
        candidates.push(\`HUMMERSUV-\${rpoCode}\`);
        candidates.push(\`HUMMER-\${rpoCode}\`);

    } else if (modelUpper === 'HUMMER EV PICKUP') {
        candidates.push(\`HUMMER-\${rpoCode}\`);

    } else if (modelUpper === 'SIERRA EV') {
        candidates.push(\`SIERRAEV-\${rpoCode}\`);
        candidates.push(\`SIERRA-EV-\${rpoCode}\`);

    } else if (modelUpper === 'SILVERADO EV') {
        candidates.push(\`SILVERADOEV-\${rpoCode}\`);
        candidates.push(\`SILVERADO-EV-\${rpoCode}\`);

    } else {
        candidates.push(\`\${modelUpper.replace(/ /g, '-')}-\${rpoCode}\`);
        candidates.push(\`\${modelUpper.replace(/ /g, '')}-\${rpoCode}\`);
    }

    return candidates;
}`;

content = content.replace(regex, replacement);

fs.writeFileSync('frontend/server.js', content, 'utf8');
console.log("Patched server.js with correct string literal format");
