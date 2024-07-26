const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');
const { colorMap, mmc } = require('./views/partials/modules.js')

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static('views'));
app.set('view engine', 'ejs');

const baseURL = 'http://127.0.0.1:5000'

function formatCurrency(number) {
    if (number === null) {
        return 'N/A';
    }
    return '$' + number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

app.get('/', function(req, res) {
    res.render('pages/index', { req: req });
});

app.get('/msrp', function(req, res) {
    var models = req.query.model;
    var rpo = req.query.rpo;
    var color = req.query.color;
    var country = req.query.country;
    var order = req.query.order;
    var page = parseInt(req.query.page) || 1;
    var limit = parseInt(req.query.limit) || 100;

    limit = Math.min(limit, 250);

    let url = `${baseURL}/msrp?page=${page}&limit=${limit}`;

    if (models) {
        models = Array.isArray(models) ? models.join(',') : models;
        url += `&model=${models}`;
    }

    if (rpo) {
        url += `&rpo=${rpo}`;
    }

    if (color) {
        url += `&color=${color}`;
    }

    if (country) {
        url += `&country=${country}`;
    }

    if (order) {
        url += `&order=${order}`;
    }

    axios.get(url)
        .then((response) => {
            var msrp_data = Array.isArray(response.data.data) ? response.data.data : [];
            var totalItems = response.data.total;
            var totalPages = Math.ceil(totalItems / limit);

            msrp_data.forEach(function(data) {
                data.msrp = formatCurrency(data.msrp);
            });

            axios.get(`${baseURL}/api/models`)
                .then((modelResponse) => {
                    var models = modelResponse.data;
                    var selectedModels = req.query.model;
                    selectedModels = selectedModels ? (Array.isArray(selectedModels) ? selectedModels : [selectedModels]) : [];

                    axios.get(`${baseURL}/api/colors`)
                        .then((colorResponse) => {
                            var colors = colorResponse.data;
                            var selectedColor = req.query.color;

                            res.render('pages/msrp', {
                                msrp_data: msrp_data,
                                models: models,
                                colors: colors,
                                colorMap: colorMap,
                                selectedCountry: country,
                                selectedModels: selectedModels,
                                currentPage: page,
                                totalPages: totalPages,
                                limit: limit,
                                totalItems: totalItems,
                                selectedRPO: rpo,
                                selectedColor: selectedColor,
                                selectedOrder: order
                            });
                        })
                        .catch((colorError) => {
                            console.error('Error fetching color data:', colorError);
                            res.status(500).send('Error fetching color data');
                        });
                })
                .catch((modelError) => {
                    console.error('Error fetching model data:', modelError);
                    res.status(500).send('Error fetching model data');
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

        vin_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });

        res.render('pages/search', {
            req: req,
            vin_data: vin_data,
            colorMap: colorMap,
            mmc: mmc
        });
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

const port = 8080;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
