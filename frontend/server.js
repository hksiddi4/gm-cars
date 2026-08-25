const express = require('express');
const compression = require('compression');
const app = express();
const axios = require('axios');
const TurndownService = require('turndown');
const turndownService = new TurndownService();
const fs = require('fs');
const path = require('path');

const basicAuth = require('express-basic-auth');
const { rateLimit, ipKeyGenerator } = require('express-rate-limit');

const authLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    max: 3,
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req, res) => {
        const ip = req.headers['cf-connecting-ip'] || req.headers['x-forwarded-for'] || req.ip;
        return ipKeyGenerator(ip);
    },
    handler: (req, res) => {
        res.status(429).send(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="refresh" content="4;url=/" />
                <title>Too Many Requests</title>
                <style>
                    body { background-color: #1e1e1e; color: #d4d4d4; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
                    .box { background: #2b2b2b; padding: 40px; border-radius: 8px; border: 1px solid #444; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
                    a { color: #0d6efd; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h2 style="color: #ff4c4c;">Too Many Attempts</h2>
                    <p>Too many login attempts from this IP.<br>Please try again after 5 minutes.</p>
                    <p style="font-size: 0.9em; color: #888;">Redirecting home in a few seconds...</p>
                    <a href="/">Click here to return home now</a>
                </div>
            </body>
            </html>
        `);
    },
    standardHeaders: true,
    legacyHeaders: false,
});

const searchLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    max: 30,
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req, res) => {
        const ip = req.headers['cf-connecting-ip'] || req.headers['x-forwarded-for'] || req.ip;
        return ipKeyGenerator(ip);
    },
});

const apiLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    max: 3,
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req, res) => {
        const ip = req.headers['cf-connecting-ip'] || req.headers['x-forwarded-for'] || req.ip;
        return ipKeyGenerator(ip);
    },
    handler: (req, res) => {
        res.status(429).json({ 
            error: 'Rate limit exceeded', 
            details: 'Too many queries sent. Please wait a moment and try again.' 
        });
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// --- Security Middleware to block direct API access ---
const blockDirectApiAccess = (req, res, next) => {
    // Check if the request is an AJAX call or comes from the same site
    const isAjax = req.headers['x-requested-with'] === 'XMLHttpRequest';
    const isSameOrigin = req.headers['sec-fetch-site'] === 'same-origin';
    
    if (isAjax || isSameOrigin) {
        next(); // Allow access
    } else {
        res.status(403).json({ error: 'Forbidden: Direct API access is restricted.' });
    }
};

const requireAdmin = basicAuth({
    users: {
        [process.env.ADMIN_USER]: process.env.ADMIN_PASS
    },
    challenge: true,
    unauthorizedResponse: (req) => {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="refresh" content="3;url=/" />
                <title>Unauthorized</title>
                <style>
                    body { background-color: #1e1e1e; color: #d4d4d4; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
                    .box { background: #2b2b2b; padding: 40px; border-radius: 8px; border: 1px solid #444; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
                    a { color: #0d6efd; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h2 style="color: #ff4c4c;">Unauthorized Access</h2>
                    <p>You do not have permission to view this page.</p>
                    <p style="font-size: 0.9em; color: #888;">Redirecting home in 3 seconds...</p>
                    <a href="/">Click here to return home now</a>
                </div>
            </body>
            </html>
        `;
    }
});

const modules = require('./views/partials/modules.js');

const headerImagesDir = path.join(__dirname, 'public', 'img', 'header');
const rpoWheelsDir = path.join(__dirname, 'public', 'img', 'rpos');

const baseURL = 'http://backend:5000';

// Axios instance with default timeout
const axiosInstance = axios.create({ timeout: 240000 });

// App Configuration
app.use(compression());
app.set('trust proxy', 1);
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public', {
    maxAge: '30d',
    etag: true
}));
app.set('view engine', 'ejs');
// Agent Content Negotiation Middleware
app.use((req, res, next) => {
    const originalRender = res.render;
    
    res.render = function (view, options, callback) {
        originalRender.call(this, view, options, (err, html) => {
            if (err) {
                if (callback) return callback(err);
                return next(err);
            }
            
            // If the agent specifically requests markdown over html
            if (req.accepts(['html', 'text/markdown']) === 'text/markdown') {
                res.set('Content-Type', 'text/markdown');
                // Convert the rendered HTML template to Markdown
                const markdown = turndownService.turndown(html);
                if (callback) return callback(null, markdown);
                return res.send(markdown);
            }
            
            // Default to standard HTML for standard web browsers
            if (callback) return callback(null, html);
            res.send(html);
        });
    };
    next();
});

let maintenanceMode = false; // Toggle this to true to lock the site

// --- Helper Functions ---

function getHeaderImages() {
    try {
        const files = fs.readdirSync(headerImagesDir);
        return files.filter(file => /\.(webp)$/i.test(file)).map(file => `/img/header/${file}`);
    } catch (err) {
        console.error('Error reading header images:', err);
        return [];
    }
}

function getLocalImageRPOs() {
    const localRpoImages = {};
    try {
        // Recursive function to dig into nested folders like corvette/z06
        function scanDirectory(currentPath, prefix = '') {
            const entries = fs.readdirSync(currentPath, { withFileTypes: true });
            entries.forEach(entry => {
                if (entry.isDirectory()) {
                    scanDirectory(path.join(currentPath, entry.name), prefix ? `${prefix}/${entry.name}` : entry.name);
                } else if (/\.(webp)$/i.test(entry.name)) {
                    const rpoCode = path.parse(entry.name).name.toUpperCase();
                    const imagePath = `/img/rpos/${prefix}/${entry.name}`;
                    
                    // Add to map (e.g., CORVETTE-Z06-RPO or just RPO)
                    localRpoImages[`${prefix.replace(/\//g, '-').toUpperCase()}-${rpoCode}`] = imagePath;
                    if (!localRpoImages[rpoCode]) localRpoImages[rpoCode] = imagePath;
                }
            });
        }
        scanDirectory(rpoWheelsDir);
    } catch (error) {
        console.warn(`Warning: Could not read RPO wheel image directory: ${error.message}`);
    }
    return localRpoImages;
}

function formatCurrency(number) {
    if (number === null || number === undefined) return 'N/A';
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Initial Data Caching
const cachedHeaderImages = getHeaderImages();
const localRpoImageMap = getLocalImageRPOs();

// --- GLOBAL MIDDLEWARE ---
// This handles maintenance and makes common variables available to ALL templates
app.use((req, res, next) => {
    // 1. Maintenance Logic
    if (maintenanceMode && req.path !== '/maintenance' && !req.path.startsWith('/css') && !req.path.startsWith('/img')) {
        return res.redirect('/maintenance');
    }
    if (!maintenanceMode && req.path === '/maintenance') {
        return res.redirect('/');
    }

    // 2. Global View Variables (res.locals)
    res.locals.req = req;
    res.locals.headerImages = cachedHeaderImages;
    res.locals.currentHeaderImage = cachedHeaderImages[Math.floor(Math.random() * cachedHeaderImages.length)];
    res.locals.localRpoImageMap = localRpoImageMap;
    res.locals.formatCurrency = formatCurrency;
    
    // 3. Inject all RPO modules (camaroRpo, corvetteRpo, etc.)
    Object.assign(res.locals, modules);
    
    next();
});

// --- ROUTES ---

app.get('/maintenance', (req, res) => {
    res.render('pages/errors/maintenance', {
        pagePath: '/maintenance',
        canonicalPath: '/maintenance'
    });
});

app.get('/', (req, res) => {
    res.render('pages/index', {
        canonicalPath: '/',
        pagePath: '/'
    });
});

app.get('/about', async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/about`);
        res.render('pages/about', {
            stats: response.data || {},
            canonicalPath: '/about',
            pagePath: '/about'
        });
    } catch (err) {
        console.error("About Route Error:", err);
        res.status(500).render('pages/errors/500', { pagePath: '/about', canonicalPath: '/about' });
    }
});

app.get('/vehicles', async (req, res) => {
    const startTime = Date.now();
    try {
        // Axios 'params' automatically converts req.query into a URL string
        const response = await axiosInstance.get(`${baseURL}/vehicles`, { params: req.query });
        const data = response.data;
        
        const limit = Math.min(parseInt(req.query.limit) || 100, 250);
        const page = parseInt(req.query.page) || 1;

        // Clean up MSRP formatting
        const vehicle_data = Array.isArray(data.data) ? data.data : [];
        vehicle_data.forEach(v => v.msrp = formatCurrency(v.msrp));

        res.render('pages/vehicles', {
            vehicle_data,
            years: data.year,
            bodys: data.body,
            trim: data.trim,
            engine: data.engine,
            trans: data.trans,
            drivetrains: data.drivetrain,
            colors: data.color,
            country: data.country,
            models: data.model,
            currentPage: page,
            totalPages: Math.ceil(data.total / limit),
            totalItems: data.total,
            limit: limit,
            elapsedTime: ((Date.now() - startTime) / 1000).toFixed(2),
            selectedYear: req.query.year,
            selectedBody: req.query.body,
            selectedTrim: req.query.trim,
            selectedEngine: req.query.engine,
            selectedTrans: req.query.trans,
            selectedDrivetrain: req.query.drivetrain,
            selectedColor: req.query.color,
            selectedCountry: req.query.country,
            selectedOrder: req.query.order,
            selectedDate: req.query.date,
            selectedRPO: typeof req.query.rpo === 'string' ? req.query.rpo.split(',') : (req.query.rpo || []),
            selectedModels: Array.isArray(req.query.model) ? req.query.model : (req.query.model ? [req.query.model] : []),
            pagePath: '/vehicles',
            canonicalPath: req.originalUrl
        });
    } catch (error) {
        console.error("Vehicles Route Error:", error);
        res.status(500).render('pages/errors/500', { pagePath: '/vehicles', canonicalPath: req.originalUrl });
    }
});

app.get('/search', searchLimiter, async (req, res) => {
    // 1. Unique variable for the incoming query string
    const vinQuery = req.query.vin?.trim();
    
    if (!vinQuery || vinQuery.length !== 17) {
        return res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
    }

    try {
        // Pass vinQuery to the backend
        const response = await axiosInstance.get(`${baseURL}/search`, { params: { vin: vinQuery } });
        const vin_data = response.data;

        if (!vin_data || vin_data.length === 0) {
            return res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
        }

        // 2. Unique variable for the data object
        const vehicle = vin_data[0]; 
        let verifiedRpoImages = [];

        if (vehicle.rpo_codes && Array.isArray(vehicle.rpo_codes)) {
            const modelUpper = vehicle.model?.toUpperCase() || '';
            const vehicleTrim = vehicle.trim || '';
            
            // Generate the exact prefix matching localRpoImageMap for instant memory lookups
            let prefixKey = modelUpper.replace(/ /g, '-');
            
            if (modelUpper.startsWith('CORVETTE')) {
                if (vehicle.rpo_codes.includes('LT6')) {
                    prefixKey = 'CORVETTE-Z06';
                } else if (vehicle.rpo_codes.includes('LT7')) {
                    prefixKey = (vehicleTrim.includes('ZR1X') || vehicle.rpo_codes.includes('ZTK')) ? 'CORVETTE-ZR1X' : 'CORVETTE-ZR1';
                } else if (vehicle.rpo_codes.includes('HP1')) {
                    prefixKey = 'CORVETTE-E-RAY';
                } else if (vehicle.rpo_codes.includes('LS6')) {
                    prefixKey = (vehicleTrim === 'GRAND SPORT X') ? 'CORVETTE-GRAND_SPORT_X' : 'CORVETTE-GRAND_SPORT';
                } else {
                    prefixKey = 'CORVETTE-STINGRAY';
                }
            } else if (modelUpper === 'ESCALADE IQ') {
                prefixKey = 'ESCALADEIQ';
            } else if (modelUpper === 'CT4' && vehicleTrim.startsWith('V-SERIES')) {
                prefixKey = 'CT4V';
            } else if (modelUpper === 'CT5' && vehicleTrim.startsWith('V-SERIES')) {
                prefixKey = 'CT5V';
            } else if (modelUpper === 'HUMMER EV PICKUP') {
                prefixKey = 'HUMMER';
            } else if (modelUpper === 'HUMMER EV SUV') {
                prefixKey = 'HUMMERSUV';
            }

            vehicle.rpo_codes.forEach(rpoCode => {
                // Instantly checks the in-memory map instead of slow file system operations
                if (localRpoImageMap[`${prefixKey}-${rpoCode}`] || localRpoImageMap[rpoCode]) {
                    verifiedRpoImages.push(rpoCode);
                }
            });
        }

        vin_data.forEach(v => v.msrp = formatCurrency(v.msrp));

        let formattedModel = vehicle.model;
        if (formattedModel === 'CT4' || formattedModel === 'CT5') {
            formattedModel = 'CT4-CT5';
        } else if (formattedModel.startsWith('CORVETTE')) {
            formattedModel = 'CORVETTE';
        }

        const baseStickerDir = path.resolve(__dirname, 'public', 'window-stickers', `${formattedModel}_${vehicle.modelYear}`);
        const absoluteStickerPath = path.resolve(baseStickerDir, `${vehicle.vin}.pdf`);
        const relativeStickerPath = path.relative(baseStickerDir, absoluteStickerPath);

        const hasSticker = !relativeStickerPath.startsWith('..') && !path.isAbsolute(relativeStickerPath) && fs.existsSync(absoluteStickerPath);
        const stickerPath = `/window-stickers/${formattedModel}_${vehicle.modelYear}/${vehicle.vin}.pdf`; 

        res.render('pages/search', {
            vin_data,
            hasSticker,
            stickerPath,
            verifiedRpoImages,
            colorMap: modules.colorMap,
            intColor: modules.intColor,
            pagePath: '/search',
            canonicalPath: `/search?vin=${vinQuery}`
        });
    } catch (error) {
        // Output the VIN and only the error message to keep the logs clean
        console.error(`Search Route Error for VIN [${vinQuery}]:`, error.message);
        res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
    }
});

app.get('/calendar-activity', blockDirectApiAccess, async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/calendar-activity`, { params: req.query });
        res.json(response.data);
    } catch (error) {
        console.error("Calendar Activity Error:", error);
        res.status(500).json({ error: 'Failed to fetch calendar activity' });
    }
});

app.get('/daily-stats', blockDirectApiAccess, async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/daily-stats`, { params: req.query });
        res.json(response.data);
    } catch (error) {
        console.error("Daily Stats API Error:", error);
        res.status(500).json({ error: 'Failed to fetch daily stats' });
    }
});

app.get('/model-bounds', blockDirectApiAccess, async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/model-bounds`, { params: req.query });
        res.json(response.data);
    } catch (error) {
        console.error("Model Bounds API Error:", error);
        res.status(500).json({ error: 'Failed to fetch bounds' });
    }
});

app.get('/stats', async (req, res) => {
    try {
        const category = req.query.category || 'daily';
        const isDashboard = ['daily', 'monthly', 'yearly'].includes(category);

        if (isDashboard) {
            // Fetch Dashboard Data (Daily/Monthly/Yearly)
            const [statsResponse, wheelsResponse] = await Promise.all([
                axiosInstance.get(`${baseURL}/daily-stats`, { params: req.query }),
                axiosInstance.get(`${baseURL}/wheels`)
            ]);
            
            res.render('pages/stats', {
                category: category,
                stats: statsResponse.data,
                all_models: wheelsResponse.data.model,
                selectedModel: req.query.model || '',
                pagePath: '/stats',
                canonicalPath: '/stats'
            });
        } else {
            // Fetch Rankings/Trends Data (Color/Engine/Production)
            const response = await axiosInstance.get(`${baseURL}/stats`, { params: req.query });
            const data = response.data;
            
            const stats_data = Array.isArray(data.stats_data) ? data.stats_data : [];
            stats_data.forEach(item => item.total_count = formatCurrency(item.total_count));

            res.render('pages/stats', {
                category: data.category || category,
                stats_data,
                year_list: data.year || [],
                model_list: data.model || [],
                body_list: data.body || [],
                trim_list: data.trim || [],
                engine_list: data.engine || [],
                trans_list: data.trans || [],
                drivetrain_list: data.drivetrain || [],
                selectedYear: req.query.year || '',
                selectedModel: req.query.model || '',
                selectedBody: req.query.body || '',
                selectedTrim: req.query.trim || '',
                selectedEngine: req.query.engine || '',
                selectedTrans: req.query.trans || '',
                selectedDrivetrain: req.query.drivetrain || '',
                pagePath: '/stats',
                canonicalPath: req.originalUrl
            });
        }
    } catch (error) {
        console.error('Error in /stats:', error);
        res.status(500).render('pages/errors/500', { error: 'Internal Server Error', pagePath: '/stats', canonicalPath: req.originalUrl });
    }
});

app.get('/rpos', (req, res) => {
    res.render('pages/rpos', { pagePath: '/rpos', canonicalPath: '/rpos' });
});

app.get('/wheels', async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/wheels`);
        res.render('pages/wheels', {
            model_list: response.data.model,
            pagePath: '/wheels',
            canonicalPath: '/wheels'
        });
    } catch (error) {
        console.error('Error in /wheels:', error);
        res.status(500).render('pages/errors/500', { error: 'Internal Server Error' });
    }
});

app.get('/query', authLimiter, requireAdmin, (req, res) => {
    res.render('pages/query', {
        canonicalPath: '/query',
        pagePath: '/query',
        colorMap: modules.colorMap || {} 
    });
});

app.post('/ai-query', apiLimiter, requireAdmin, async (req, res) => {
    try {
        const userPrompt = req.body.prompt;

        // --- NEW LOGGING LOGIC ---
        const timestamp = new Date().toLocaleString('en-US', { timeZone: 'America/Chicago' }); 
        const logEntry = `[${timestamp}] ${userPrompt}\n`;
        const logFilePath = path.join(__dirname, 'query_logs.txt');

        fs.appendFile(logFilePath, logEntry, (err) => {
            if (err) console.error("Failed to write to query log:", err);
        });
        // -------------------------

        const response = await axiosInstance.post(`${baseURL}/ai-query`, { 
            prompt: userPrompt 
        });

        res.json(response.data);
    } catch (error) {
        console.error("AI Query Error:", error.response?.data || error.message);
        res.status(500).json({ 
            error: 'AI query failed', 
            details: error.response?.data?.error || 'Unknown error' 
        });
    }
});

// app.post('/api/rarity', async (req, res) => {
//     try {
//         const response = await axiosInstance.post(`${baseURL}/api/rarity`, { Options: req.body.Options });
//         res.json(response.data);
//     } catch (error) {
//         res.status(500).json({ error: 'Rarity fetch failed' });
//     }
// });

// --- ERROR HANDLING ---

app.use((req, res) => {
    res.status(404).render('pages/errors/404', {
        pagePath: '/404',
        canonicalPath: req.originalUrl
    });
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).render('pages/errors/500', {
        error: err.message || err,
        pagePath: '/500',
        canonicalPath: req.originalUrl
    });
});

const port = 80;
app.listen(port, "0.0.0.0", () => {
    console.log(`Server running on port ${port}`);
});
