const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');
const { colorMap, intColor, seatCode, mmc } = require('./views/partials/modules.js')

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');

const baseURL = 'http://192.168.1.111:5000'

let maintenanceMode = true; // Edit this to toggle maintenance mode

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
    res.render('pages/index', { req: req });
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
    if (rpos) url += `&rpo=${Array.isArray(rpos) ? rpos.join(',') : rpos}`;
    if (color) url += `&color=${color}`;
    if (country) url += `&country=${country}`;
    if (order) url += `&order=${order}`;

    axios.get(url, { timeout: 10000 })
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
                selectedOrder: order
            });
        })
        .catch((error) => {
            console.error(`Error fetching data: ${error}`);
            res.status(500).render('pages/errors/500', { error: error.toJSON ? error.toJSON() : { message: error.message } });
        });
});

app.get('/search', function(req, res) {
    var vin = req.query.vin;
    axios.get(`${baseURL}/search?vin=${vin}`, { timeout: 10000 })
    .then((response)=>{
        var vin_data = response.data;

        if (vin_data.length === 0) {
            res.status(404).render('pages/errors/404', { req: req });
        } else {
            vin_data.forEach(function(data) {
                data.msrp = formatCurrency(data.msrp);
            });
    
            res.render('pages/search', {
                req: req,
                vin_data: vin_data,
                colorMap: colorMap,
                intColor: intColor,
                seatCode: seatCode,
                mmc: mmc
            });
        }
    })
});

app.get('/stats', function(req, res) {
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

    axios.get(url.toString(), { timeout: 10000 })
        .then((response) => {
            const data = response.data;
            var stats_data = Array.isArray(response.data.stats_data) ? response.data.stats_data : [];
            stats_data.forEach((item) => {
                item.total_count = formatCurrency(item.total_count);
            });

            res.render('pages/stats', {
                stats_data: data.stats_data,
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
                selectedTrans: req.query.trans || ''
            });
        })
        .catch((error) => {
            console.error(`Error fetching data: ${error}`);
            res.status(500).render('pages/errors/500', {
                error: error.toJSON ? error.toJSON() : { message: error.message }
            });
        });
});

app.post('/api/rarity', async (req, res) => {
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
        res.status(500).render('pages/errors/500', { error: error.toJSON ? error.toJSON() : { message: error.message } });
    }
});

app.use((req, res) => {
    res.status(404).render('pages/errors/404', { req });
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).render('pages/errors/500', {
        error: err.toJSON ? err.toJSON() : { message: err.message }
    });
});

const port = 80;
app.listen(port, "0.0.0.0",() => {
    console.log(`Frontend is running on port ${port}`);
});
