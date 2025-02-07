const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');
const { colorMap, intColor, seatCode, mmc } = require('./views/partials/modules.js')

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('views'));
app.set('view engine', 'ejs');

const baseURL = 'http://127.0.0.1:5000'

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
    var models = req.query.model;
    var rpo = req.query.rpo;
    var color = req.query.color;
    var country = req.query.country;
    var order = req.query.order;
    var page = parseInt(req.query.page) || 1;
    var limit = Math.min(parseInt(req.query.limit) || 100, 250);

    let url = `${baseURL}/vehicles?page=${page}&limit=${limit}`;
    if (year) url += `&year=${year}`;
    if (body) url += `&body=${body}`;
    if (trim) url += `&trim=${trim}`;
    if (engine) url += `&engine=${engine}`;
    if (trans) url += `&trans=${trans}`;
    if (models) url += `&model=${Array.isArray(models) ? models.join(',') : models}`;
    if (rpo) url += `&rpo=${rpo}`;
    if (color) url += `&color=${color}`;
    if (country) url += `&country=${country}`;
    if (order) url += `&order=${order}`;

    axios.get(url)
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
            var selectedModels = selectedModels ? (Array.isArray(selectedModels) ? selectedModels : [selectedModels]) : [];
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
                selectedRPO: rpo,
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
            res.status(500).send('Error fetching data');
        });
});

app.get('/search', function(req, res) {
    var vin = req.query.vin;
    axios.get(`${baseURL}/search?vin=${vin}`)
    .then((response)=>{
        var vin_data = response.data;

        if (vin_data.length === 0) {
            res.status(404).render('pages/404', { req: req });
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
        res.status(500).json({ error: 'Failed to forward request to Python service' });
    }
});

app.post('/api/genurl', async (req, res) => {
    const data = req.body;

    try {
        const response = await axios.post(`${baseURL}/api/genurl`, {data});
        const generatedUrl = response.data;
        res.json({ url: generatedUrl });
    } catch (error) {
        console.error('Error generating URL:', error);
        res.status(500).json({ error: 'Failed to generate URL' });
    }
});

app.use(function(req, res) {
    res.status(404).render('pages/404', { req: req });
});

const port = 8080;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
