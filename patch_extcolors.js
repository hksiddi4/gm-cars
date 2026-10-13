const fs = require('fs');
let c = fs.readFileSync('frontend/server.js', 'utf-8');

const replacement = `function getLocalImageRPOs() {
    const localRpoImages = {};
    try {
        function scanDirectory(currentPath, prefix = '', urlBase = '/img/rpos/') {
            if (!fs.existsSync(currentPath)) return;
            const entries = fs.readdirSync(currentPath, { withFileTypes: true });
            entries.forEach(entry => {
                if (entry.isDirectory()) {
                    scanDirectory(require('path').join(currentPath, entry.name), prefix ? \`\${prefix}/\${entry.name}\` : entry.name, urlBase);
                } else if (/\\.(webp)$/i.test(entry.name)) {
                    const rpoCode = require('path').parse(entry.name).name.toUpperCase();
                    const imagePath = \`\${urlBase}\${prefix ? prefix + '/' : ''}\${entry.name}\`;
                    
                    if (prefix) {
                        const formattedPrefix = prefix.replace(/\\//g, '-').toUpperCase();
                        if (!localRpoImages[\`\${formattedPrefix}-\${rpoCode}\`]) {
                            localRpoImages[\`\${formattedPrefix}-\${rpoCode}\`] = imagePath;
                        }
                    } else {
                        if (!localRpoImages[rpoCode]) {
                            localRpoImages[rpoCode] = imagePath;
                        }
                    }
                }
            });
        }
        scanDirectory(rpoWheelsDir, '', '/img/rpos/');
        
        const extColorsDir = require('path').join(__dirname, 'public', 'img', 'extColors');
        scanDirectory(extColorsDir, '', '/img/extColors/');
        
    } catch (error) {
        console.warn(\`Warning: Could not read RPO image directories: \${error.message}\`);
    }
    return localRpoImages;
}`;

c = c.replace(/function getLocalImageRPOs\(\) \{[\s\S]*?return localRpoImages;\r?\n\}/, replacement);
fs.writeFileSync('frontend/server.js', c);
