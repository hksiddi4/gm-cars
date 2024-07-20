const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const axios = require('axios');

app.use(bodyParser.urlencoded({ extended: true }));
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

app.get('/rand', function(req, res) {
    axios.get(`${baseURL}/rand`)
    .then((response)=>{
        var all_data = response.data;

        all_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });

        res.render('pages/rand', {
            req: req,
            all_data: all_data
        });
    })
});

app.get('/msrp', function(req, res) {
    axios.get(`${baseURL}/msrp`)
    .then((response)=>{
        var msrp_data = response.data;

        msrp_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });

        res.render('pages/msrp', {
            msrp_data: msrp_data
        });
    })
});

app.get('/panther350', function(req, res) {
    axios.get(`${baseURL}/panther350`)
    .then((response)=>{
        var ce_data = response.data;

        ce_data.forEach(function(data) {
            if (data.msrp != null) {
                data.msrp = formatCurrency(data.msrp);
            } else {
                data.msrp = 'N/A';
            }
        });
        res.render('pages/panther350', {
            ce_data: ce_data
        });
    })
});

app.get('/garage56', function(req, res) {
    axios.get(`${baseURL}/garage56`)
    .then((response)=>{
        var g56_data = response.data;

        g56_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });
        res.render('pages/garage56', {
            g56_data: g56_data
        });
    })
});

app.get('/blackwing', function(req, res) {
    axios.get(`${baseURL}/blackwing`)
    .then((response)=>{
        var bw_data = response.data;

        bw_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });
        res.render('pages/blackwing', {
            bw_data: bw_data
        });
    })
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
            vin_data: vin_data
        });
    })
});

app.get('/test', function(req, res) {
    axios.get(`${baseURL}/test`)
    .then((response)=>{
        var vin_data = response.data;

        vin_data.forEach(function(data) {
            data.msrp = formatCurrency(data.msrp);
        });

        res.render('pages/test', {
            req: req,
            vin_data: vin_data,
            rpoDescriptions: rpoDescriptions
        });
    })
});

const port = 8080;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
