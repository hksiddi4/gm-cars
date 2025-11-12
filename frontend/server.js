const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { colorMap, intColor, seatCode, mmc, camaroRpo, corvetteRpo, escaladeiqRpo, ct4Rpo, ct4vRpo, ct5Rpo, ct5vRpo } = require('./views/partials/modules.js')
const headerImagesDir = path.join(__dirname, 'public', 'img', 'header');
const rpoWheelsDir = path.join(__dirname, 'public', 'img', 'rpos');

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

const baseURL = 'http://backend:5000'

const axiosInstance = axios.create({
    timeout: 30000
});

let maintenanceMode = false; // Edit this to toggle maintenance mode

function getHeaderImages() {
    try {
        const files = fs.readdirSync(headerImagesDir);
        const imageFiles = files.filter(file => {
            return /\.(png)$/i.test(file);
        });
        const publicImageUrls = imageFiles.map(file => `/img/header/${file}`);
        return publicImageUrls;
    } catch (err) {
        console.error('Error reading header images directory:', err);
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
                localRpoImages[rpoCode] = `/img/rpos/${modelDir}/${file}`; // The final public URL
            });
        });

    } catch (error) {
        console.warn(`Warning: Could not read RPO wheel image directory: ${error.message}`);
    }
    return localRpoImages;
}
const localRpoImageMap = getLocalImageRPOs();


app.use((req, res, next) => {
    if (maintenanceMode && req.path !== '/maintenance') {
        return res.redirect('/maintenance');
    }
    if (!maintenanceMode && req.path === '/maintenance') {
        return res.redirect('/');
    }
    next();
});

app.get('/maintenance', (req, res) => {
    res.render('pages/errors/maintenance');
});

function formatCurrency(number) {
    if (number === null) {
        return 'N/A';
    }
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

app.get('/', function(req, res) {
    const imageUrls = getHeaderImages();
    res.render('pages/index', {
        req: req,
        headerImages: imageUrls,
        canonicalPath: '/',
        pagePath: '/'
    });
});

app.get('/vehicles', function(req, res) {
    const startTime = Date.now();
    var year = req.query.year;
    var body = req.query.body;
    var trim = req.query.trim;
    var engine = req.query.engine;
    var trans = req.query.trans;
    var selectedModels = req.query.model;
    var rpos = req.query.rpo;
    var color = req.query.color;
    var country = req.query.country;
    var order = req.query.order;
    var page = parseInt(req.query.page) || 1;
    var limit = Math.min(parseInt(req.query.limit) || 100, 250);

    if (typeof rpos === 'string') {
        rpos = rpos.split(',');
    }

    let url = `${baseURL}/vehicles?limit=${limit}&page=${page}`;
    if (year) url += `&year=${year}`;
    if (body) url += `&body=${body}`;
    if (trim) url += `&trim=${trim}`;
    if (engine) url += `&engine=${engine}`;
    if (trans) url += `&trans=${trans}`;
    if (selectedModels) url += `&model=${Array.isArray(selectedModels) ? selectedModels.join(',') : selectedModels}`;
    if (rpos && (!Array.isArray(rpos) || rpos.length > 0)) url += `&rpo=${Array.isArray(rpos) ? rpos.join(',') : rpos}`;
    if (color) url += `&color=${color}`;
    if (country) url += `&country=${country}`;
    if (order) url += `&order=${order}`;

    axiosInstance.get(url)
        .then((response) => {
            var vehicle_data = Array.isArray(response.data.data) ? response.data.data : [];
            vehicle_data.forEach(function(data) {
                data.msrp = formatCurrency(data.msrp);
            });
            var totalItems = response.data.total;
            var totalPages = Math.ceil(totalItems / limit);
            var years = response.data.year
            var selectedYear = req.query.year;
            var bodys = response.data.body
            var selectedBody = req.query.body;
            var trim = response.data.trim;
            var selectedTrim = req.query.trim;
            var engine = response.data.engine;
            var selectedEngine = req.query.engine;
            var trans = response.data.trans;
            var selectedTrans = req.query.trans;
            var colors = response.data.color;
            var selectedColor = req.query.color;
            var country = response.data.country;
            var selectedCountry = req.query.country;
            var models = response.data.model;
            selectedModels = selectedModels ? (Array.isArray(selectedModels) ? selectedModels : [selectedModels]) : [];
            const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);

            const queryParams = new URLSearchParams(req.query);
            queryParams.delete('page');
            queryParams.delete('limit');
            const imageUrls = getHeaderImages();
            const canonicalPath = `/vehicles${queryParams.toString() ? '?' + queryParams.toString() : ''}`;

            res.render('pages/vehicles', {
                vehicle_data: vehicle_data,
                years: years,
                bodys: bodys,
                engine: engine,
                trim: trim,
                trans: trans,
                models: models,
                colors: colors,
                country: country,
                colorMap: colorMap,
                currentPage: page,
                totalPages: totalPages,
                limit: limit,
                totalItems: totalItems,
                elapsedTime: elapsedTime,
                selectedRPO: rpos,
                selectedColor: selectedColor,
                selectedYear: selectedYear,
                selectedBody: selectedBody,
                selectedTrim: selectedTrim,
                selectedEngine: selectedEngine,
                selectedTrans: selectedTrans,
                selectedCountry: selectedCountry,
                selectedModels: selectedModels,
                selectedOrder: order,
                canonicalPath: canonicalPath,
                pagePath: '/vehicles',
                headerImages: imageUrls
            });
        })
        .catch((error) => {
            console.error(`Error fetching data: ${error}`);
            res.status(500).render('pages/errors/500', { error: error.toJSON ? error.toJSON() : { message: error.message } });
        });
});

app.get('/search', function(req, res) {
    var vin = req.query.vin.trim();
    const imageUrls = getHeaderImages();
    if (!vin || vin.length !== 17) {
        return res.status(400).render('pages/errors/400', {
            req: req,
            headerImages: imageUrls,
            canonicalPath: '/search', 
            pagePath: '/search' 
        });
    }
    axiosInstance.get(`${baseURL}/search?vin=${encodeURIComponent(vin)}`)
    .then((response)=>{
        var vin_data = response.data;

        if (!vin_data || vin_data.length === 0) {
            res.status(400).render('pages/errors/400', {
                req: req,
                headerImages: imageUrls,
                canonicalPath: '/search', 
                pagePath: '/search' 
            });
        } else {
            vin_data.forEach(function(data) {
                data.msrp = formatCurrency(data.msrp);
            });
    
            res.render('pages/search', {
                req: req,
                headerImages: imageUrls,
                vin_data: vin_data,
                colorMap: colorMap,
                intColor: intColor,
                seatCode: seatCode,
                mmc: mmc,
                camaroRpo: camaroRpo,
                corvetteRpo: corvetteRpo,
                escaladeiqRpo: escaladeiqRpo,
                ct4Rpo: ct4Rpo,
                ct4vRpo: ct4vRpo,
                ct5Rpo: ct5Rpo,
                ct5vRpo: ct5vRpo,
                canonicalPath: `/search?vin=${vin}`,
                pagePath: '/search'
            });
        }
    })
    .catch((error) => {
        console.error(`Error fetching data: ${error}`);
        res.status(500).render('pages/errors/500', { 
            error: error.toJSON ? error.toJSON() : { message: error.message },
            headerImages: imageUrls,
            canonicalPath: '/search', 
            pagePath: '/search'
        });
    });
});

app.get('/stats', function(req, res) {
    const imageUrls = getHeaderImages();
    const category = req.query.category;
    const url = new URL(`${baseURL}/stats`);
    const params = new URLSearchParams();

    if (category) params.append("category", category);
    if (req.query.year) params.append("year", req.query.year);
    if (req.query.body) params.append("body", req.query.body);
    if (req.query.trim) params.append("trim", req.query.trim);
    if (req.query.engine) params.append("engine", req.query.engine);
    if (req.query.trans) params.append("trans", req.query.trans);
    if (req.query.model) params.append("model", req.query.model);

    url.search = params.toString();

    const canonicalPath = `/stats${params.toString() ? '?' + params.toString() : ''}`;

    axiosInstance.get(url.toString())
        .then((response) => {
            const data = response.data;
            var stats_data = Array.isArray(response.data.stats_data) ? response.data.stats_data : [];
            stats_data.forEach((item) => {
                item.total_count = formatCurrency(item.total_count);
            });

            res.render('pages/stats', {
                stats_data: data.stats_data,
                headerImages: imageUrls,
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
                canonicalPath: canonicalPath,
                pagePath: '/stats'
            });
        })
        .catch((error) => {
            console.error(`Error fetching data: ${error}`);
            res.status(500).render('pages/errors/500', {
                error: error.toJSON ? error.toJSON() : { message: error.message },
                headerImages: imageUrls,
                canonicalPath: '/stats', 
                pagePath: '/stats'
            });
        });
});

app.get('/rpos', function(req, res) {
    const imageUrls = getHeaderImages();
    res.render('pages/rpos', {
        headerImages: imageUrls,
        camaroRpo: camaroRpo,
        corvetteRpo: corvetteRpo,
        escaladeiqRpo: escaladeiqRpo,
        ct4Rpo: ct4Rpo,
        ct4vRpo: ct4vRpo,
        ct5Rpo: ct5Rpo,
        ct5vRpo: ct5vRpo,
        canonicalPath: '/rpos',
        pagePath: '/rpos'
    });
});

app.get('/wheels', function(req, res) {
    const imageUrls = getHeaderImages();
    const url = new URL(`${baseURL}/wheels`);

    axiosInstance.get(url.toString())
        .then((response) => {
            const data = response.data;

            res.render('pages/wheels', {
                model_list: data.model,
                headerImages: imageUrls,
                // Passing the individual RPO objects, now used for priority check logic in EJS
                camaroRpo: camaroRpo, 
                corvetteRpo: corvetteRpo,
                escaladeiqRpo: escaladeiqRpo,
                ct4Rpo: ct4Rpo,
                ct4vRpo: ct4vRpo,
                ct5Rpo: ct5Rpo,
                ct5vRpo: ct5vRpo,
                localRpoImageMap: localRpoImageMap, 
                
                canonicalPath: '/wheels',
                pagePath: '/wheels'
            });
        })
        .catch((error) => {
            console.error(`Error fetching data: ${error}`);
            res.status(500).render('pages/errors/500', {
                error: error.toJSON ? error.toJSON() : { message: error.message },
                headerImages: imageUrls,
                canonicalPath: '/wheels',
                pagePath: '/wheels'
            });
        });
});

app.post('/api/rarity', async (req, res) => {
    const imageUrls = getHeaderImages();
    const options = req.body.Options;

    try {
        const response = await fetch(`${baseURL}/api/rarity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ Options: options })
        });

        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).render('pages/errors/500', { error: error.toJSON ? error.toJSON() : { message: error.message }, headerImages: imageUrls });
    }
});

app.use((req, res) => {
    const imageUrls = getHeaderImages();
    res.status(404).render('pages/errors/404', {
        req,
        headerImages: imageUrls,
        canonicalPath: req.originalUrl,
        pagePath: '/404'
    });
});

app.use((err, req, res, next) => {
    const imageUrls = getHeaderImages();
    console.error(err.stack);
    res.status(500).render('pages/errors/500', {
        error: err.toJSON ? err.toJSON() : { message: err.message },
        headerImages: imageUrls,
        canonicalPath: req.originalUrl,
        pagePath: '/500'
    });
});

const port = 80;
app.listen(port, "0.0.0.0",() => {
    // console.log(`Frontend is running on port ${port}`);
});
