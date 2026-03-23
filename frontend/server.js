const express = require('express');
const app = express();
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Import all RPO constants as a single object
const modules = require('./views/partials/modules.js');

const headerImagesDir = path.join(__dirname, 'public', 'img', 'header');
const rpoWheelsDir = path.join(__dirname, 'public', 'img', 'rpos');

const baseURL = 'http://backend:5000';

// Axios instance with default timeout
const axiosInstance = axios.create({ timeout: 30000 });

// App Configuration
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

let maintenanceMode = false; // Toggle this to true to lock the site

// --- Helper Functions ---

function getHeaderImages() {
    try {
        const files = fs.readdirSync(headerImagesDir);
        return files.filter(file => /\.(png)$/i.test(file)).map(file => `/img/header/${file}`);
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
                .filter(file => /\.(jpg|jpeg|png|webp)$/i.test(file));
            
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
    const vin = req.query.vin?.trim();
    if (!vin || vin.length !== 17) {
        return res.status(400).render('pages/errors/400', { pagePath: '/search', canonicalPath: '/search' });
    }

    try {
        const response = await axiosInstance.get(`${baseURL}/search`, { params: { vin } });
        const vin_data = response.data;

        if (!vin_data || vin_data.length === 0) throw new Error('VIN not found');

        vin_data.forEach(v => v.msrp = formatCurrency(v.msrp));

        res.render('pages/search', {
            vin_data,
            pagePath: '/search',
            canonicalPath: `/search?vin=${vin}`
        });
    } catch (error) {
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
            selectedYear: req.query.year || '',
            selectedModel: req.query.model || '',
            selectedBody: req.query.body || '',
            selectedTrim: req.query.trim || '',
            selectedEngine: req.query.engine || '',
            selectedTrans: req.query.trans || '',
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
    const isDev = process.env.NODE_ENV === 'development';
    res.status(500).render('pages/errors/500', {
        error: isDev ? err.stack : "Internal Server Error",
        showDetails: isDev,
        pagePath: '/500',
        canonicalPath: req.originalUrl
    });
});

const port = 80;
app.listen(port, "0.0.0.0", () => {
    console.log(`Server running on port ${port}`);
});
