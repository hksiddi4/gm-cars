const express = require('express');
const app = express();
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const basicAuth = require('express-basic-auth');
const rateLimit = require('express-rate-limit');

const authLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    max: 3,
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

const apiLimiter = rateLimit({
    windowMs: 5 * 60 * 1000,
    handler: (req, res) => {
        res.status(429).json({ 
            error: 'Rate limit exceeded', 
            details: 'Too many queries sent. Please wait a moment and try again.' 
        });
    },
    standardHeaders: true,
    legacyHeaders: false,
});

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
app.set('trust proxy', 1);
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

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
        const modelDirs = fs.readdirSync(rpoWheelsDir, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory())
            .map(dirent => dirent.name);

        modelDirs.forEach(modelDir => {
            const modelPath = path.join(rpoWheelsDir, modelDir);
            const imageFiles = fs.readdirSync(modelPath)
                .filter(file => /\.(webp)$/i.test(file));
            
            imageFiles.forEach(file => {
                const rpoCode = path.parse(file).name.toUpperCase();
                const imagePath = `/img/rpos/${modelDir}/${file}`;
                localRpoImages[`${modelDir.toUpperCase()}-${rpoCode}`] = imagePath;
                if (!localRpoImages[rpoCode]) localRpoImages[rpoCode] = imagePath;
            });
        });
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
        res.status(500).render('pages/errors/500', { error: err });
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
            selectedRPO: typeof req.query.rpo === 'string' ? req.query.rpo.split(',') : (req.query.rpo || []),
            selectedModels: Array.isArray(req.query.model) ? req.query.model : (req.query.model ? [req.query.model] : []),
            pagePath: '/vehicles',
            canonicalPath: req.originalUrl
        });
    } catch (error) {
        res.status(500).render('pages/errors/500', { error });
    }
});

app.get('/search', async (req, res) => {
    // 1. Unique variable for the incoming query string
    const vinQuery = req.query.vin?.trim();
    
    if (!vinQuery || vinQuery.length !== 17) {
        return res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
    }

    try {
        // Pass vinQuery to the backend
        const response = await axiosInstance.get(`${baseURL}/search`, { params: { vin: vinQuery } });
        const vin_data = response.data;

        if (!vin_data || vin_data.length === 0) throw new Error('VIN not found');

        // 2. Unique variable for the data object
        const vehicle = vin_data[0]; 
        let verifiedRpoImages = [];

        if (vehicle.rpo_codes && Array.isArray(vehicle.rpo_codes)) {
            const modelUpper = vehicle.model?.toUpperCase() || '';
            const vehicleTrim = vehicle.trim || '';
            
            // Mirror directory resolution logic used on frontend
            let folderName = modelUpper.toLowerCase();
            if (modelUpper.startsWith('CORVETTE')) {
                folderName = 'corvette';
            } else if (modelUpper === 'ESCALADE IQ') {
                folderName = 'escaladeiq';
            } else if (modelUpper === 'CT4' && vehicleTrim.startsWith('V-SERIES')) {
                folderName = 'ct4v';
            } else if (modelUpper === 'CT5' && vehicleTrim.startsWith('V-SERIES')) {
                folderName = 'ct5v';
            } else if (modelUpper === 'HUMMER EV PICKUP') {
                folderName = 'hummer';
            } else if (modelUpper === 'HUMMER EV SUV') {
                folderName = 'hummersuv';
            }

            vehicle.rpo_codes.forEach(rpoCode => {
                const absoluteImagePath = path.join(__dirname, 'public', 'img', 'rpos', folderName, `${rpoCode}.webp`);
                
                // Only pass to view if file physically exists on NVMe drive
                if (fs.existsSync(absoluteImagePath)) {
                    verifiedRpoImages.push(rpoCode);
                }
            });
        }

        vin_data.forEach(v => v.msrp = formatCurrency(v.msrp));

        const stickerPath = `/stickers/${vehicle.model}/${vehicle.modelYear}/${vehicle.vin}.pdf`; 
        const absoluteStickerPath = path.join(__dirname, 'public', 'stickers', vehicle.model, vehicle.modelYear.toString(), `${vehicle.vin}.pdf`);

        const hasSticker = fs.existsSync(absoluteStickerPath);

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
        console.error("Search Route Error:", error);
        res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
    }
});

app.get('/stats', async (req, res) => {
    try {
        const response = await axiosInstance.get(`${baseURL}/stats`, { params: req.query });
        const data = response.data;
        
        const stats_data = Array.isArray(data.stats_data) ? data.stats_data : [];
        stats_data.forEach(item => item.total_count = formatCurrency(item.total_count));

        res.render('pages/stats', {
            stats_data,
            category: data.category,
            year_list: data.year,
            model_list: data.model,
            body_list: data.body,
            trim_list: data.trim,
            engine_list: data.engine,
            trans_list: data.trans,
            drivetrain_list: data.drivetrain,
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
    } catch (error) {
        res.status(500).render('pages/errors/500', { error });
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
        res.status(500).render('pages/errors/500', { error });
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

app.post('/api/rarity', async (req, res) => {
    try {
        const response = await axiosInstance.post(`${baseURL}/api/rarity`, { Options: req.body.Options });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: 'Rarity fetch failed' });
    }
});

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
