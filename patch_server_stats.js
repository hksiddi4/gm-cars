const fs = require('fs');
let c = fs.readFileSync('frontend/server.js', 'utf8');
c = c.replace(
    'const response = await axiosInstance.get(`${baseURL}/stats`, { params: req.query });',
    `const queryParams = { ...req.query };
            if (category === 'interior') queryParams.interiorRPOs = Object.keys(modules.intColor).join(',');
            const response = await axiosInstance.get(\`\${baseURL}/stats\`, { params: queryParams });`
);
fs.writeFileSync('frontend/server.js', c, 'utf8');
