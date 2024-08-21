import sql
import flask
from flask import request, jsonify
from flask_cors import CORS
from sql import create_connection, execute_read_query, Creds
import requests
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

# Create connection to MySQL database
myCreds = sql.Creds()
conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

# ========================= View Pages =========================

@app.route('/search', methods=['GET'])
def search_inv():
    vin = request.args.get('vin')
    sqlStatement = f"SELECT * FROM gm WHERE VIN = '{vin}'"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

@app.route('/api/genurl', methods=['POST'])
def generate_url():
    data = request.json["data"]
    allJson_str = data["allJson"]
    allJson = json.loads(allJson_str)

    model_year = allJson["model_year"].strip()
    mmc_code = allJson["mmc_code"].strip()
    mmcDict = data["mmc"]
    colorMap = data["colorMap"]
    intColor = data["intColor"]
    options = [option for option in allJson["Options"] if option]
    baseURL = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/image.gen?i="
    baseURL_int = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/imageinterior.gen?i="

    trim = mmcDict.get(mmc_code)
    rpos = "_".join(options)
    
    color = None
    colorInt = None
    for option in options:
        if color is None:
            for key, rpo in colorMap.items():
                if rpo == option:
                    color = rpo
                    break
        if colorInt is None:
            for key, rpo in intColor.items():
                if rpo == option:
                    colorInt = rpo
                    break
        if color and colorInt:
            break

    urls_attempted = []
    url_data = [
        (baseURL, color, 1, 9),
        (baseURL_int, colorInt, 1, 4)
    ]
    
    for base_url, color_value, view, view_limit in url_data:
        while view <= view_limit:
            # gmds11 = 2500x1407 | gmds10 = 1920x1080 | gmds5 = 320x178 | gmds4 = 640x360 | gmds3 = 205x115 | gmds2 = 960x540 | gmds1 = 480x270
            end_url = f"gmds10.png&v=deg{view:02d}&std=true&country=US&send404=true&transparentBackgroundPng=true"
            built_url = f"{base_url}{model_year}/{mmc_code}/{mmc_code}__{trim}/{color_value}_{rpos}{end_url}"
            response = requests.head(built_url)
            view += 1
            if response.status_code == 404:
                break
            urls_attempted.append(built_url)
    
    if not urls_attempted:
        ghost_img = "../img/ghost-chevrolet-car-alt.png"
        return jsonify({"generatedImages": ghost_img})
    return jsonify({"generatedImages": urls_attempted})

@app.route('/api/rarity', methods=['POST'])
def unique():
    data = request.json
    options = data.get('Options')

    if options is not None:
        formatted_options = json.dumps(options)
        try:
            sqlStatement = f"SELECT COUNT(*) AS Count FROM gm WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) = '{formatted_options}'"
            response = execute_read_query(conn, sqlStatement)
            return response
        except ValueError:
            return jsonify({'error': 'Invalid value'}), 400
    else:
        return jsonify({'error': 'No value provided'}), 400

@app.route('/vehicles', methods=['GET'])
def sort_price():
    year = request.args.get('year')
    trim = request.args.get('trim')
    engine = request.args.get('engine')
    trans = request.args.get('trans')
    models = request.args.get('model')
    rpo = request.args.get('rpo')
    color = request.args.get('color')
    country = request.args.get('country')
    order = request.args.get('order')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    offset = (page - 1) * limit

    conditions = []

    if year:
        conditions.append(f"modelYear = '{year}'")
    
    if trim:
        conditions.append(f"trim = '{trim}'")
    
    if engine:
        conditions.append(f"vehicleEngine = '{engine}'")
    
    if trans:
        conditions.append(f"transmission = '{trans}'")

    if models:
        models = [model.strip() for model in models.split(',')]
        models = "', '".join(models)
        conditions.append(f"model IN ('{models}')")

    if rpo == "Z4B":
        conditions.append("exterior_color IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC')")
    elif rpo == "X56":
        conditions.append("trim = 'ZL1'")
        conditions.append("exterior_color = 'RIPTIDE BLUE METALLIC'")
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")
    elif rpo == "A1Z":
        conditions.append("trim = 'ZL1'")
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")
    elif rpo == "A1Y":
        conditions.append("trim in ('1SS', '2SS')")
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")
    elif rpo == "A1X":
        conditions.append("trim in ('1LT', '2LT', '3LT')")
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")
    elif rpo == "LF4":
        conditions.append("model = 'CT4'")
        conditions.append("trim = 'V-SERIES BLACKWING'")
    elif rpo == "1SV":
        conditions.append("model = 'CT5'")
        conditions.append("trim = 'V-SERIES BLACKWING'")
    elif rpo:
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")

    if color:
        conditions.append(f"exterior_color = '{color}'")

    if country == "USA":
        conditions.append("NOT JSON_CONTAINS(allJson->'$.maker', '\"GMCANADA\"')")
        conditions.append("NOT JSON_CONTAINS(allJson->'$.maker', '\"N/A\"')")
    elif country == "CAN":
        conditions.append("JSON_CONTAINS(allJson->'$.maker', '\"GMCANADA\"')")
    elif country:
        conditions.append("JSON_CONTAINS(allJson->'$.maker', '\"N/A\"')")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    count_query = f"SELECT COUNT(*) AS total FROM gm{where_clause}"
    total_items_result = execute_read_query(conn, count_query)
    total_items = total_items_result[0]['total']

    if order == "ASC":
        select_query = f"SELECT * FROM gm{where_clause} ORDER BY msrp LIMIT {limit} OFFSET {offset}"
    else:
        select_query = f"SELECT * FROM gm{where_clause} ORDER BY msrp DESC LIMIT {limit} OFFSET {offset}"
    viewTable = execute_read_query(conn, select_query)

    return jsonify({'data': viewTable, 'total': total_items})

# ========================= View Pages =========================

# =========================    APIs    =========================

@app.route('/api/years', methods=['GET'])
def get_trim():
    sqlStatement = "SELECT DISTINCT modelYear FROM gm ORDER BY modelYear"
    years = execute_read_query(conn, sqlStatement)
    year_list = [year['modelYear'] for year in years]
    return jsonify(year_list)

@app.route('/api/years', methods=['GET'])
def get_years():
    sqlStatement = "SELECT DISTINCT modelYear FROM gm ORDER BY modelYear"
    years = execute_read_query(conn, sqlStatement)
    year_list = [year['modelYear'] for year in years]
    return jsonify(year_list)

@app.route('/api/trims', methods=['GET'])
def get_trims():
    sqlStatement = "SELECT DISTINCT trim FROM gm ORDER BY trim"
    trims = execute_read_query(conn, sqlStatement)
    trim_list = [trim['trim'] for trim in trims]
    return jsonify(trim_list)

@app.route('/api/engine', methods=['GET'])
def get_engine():
    sqlStatement = "SELECT DISTINCT vehicleEngine FROM gm ORDER BY vehicleEngine"
    engines = execute_read_query(conn, sqlStatement)
    engine_list = [engine['vehicleEngine'] for engine in engines]
    return jsonify(engine_list)

@app.route('/api/trans', methods=['GET'])
def get_trans():
    sqlStatement = "SELECT DISTINCT transmission FROM gm ORDER BY transmission"
    trans = execute_read_query(conn, sqlStatement)
    trans_list = [transmission['transmission'] for transmission in trans]
    return jsonify(trans_list)

@app.route('/api/colors', methods=['GET'])
def get_colors():
    sqlStatement = "SELECT DISTINCT exterior_color FROM gm ORDER BY exterior_color"
    colors = execute_read_query(conn, sqlStatement)
    color_list = [color['exterior_color'] for color in colors]
    return jsonify(color_list)

@app.route('/api/models', methods=['GET'])
def get_models():
    sqlStatement = "SELECT DISTINCT model FROM gm ORDER BY model"
    models = execute_read_query(conn, sqlStatement)
    model_list = [model['model'] for model in models]
    return jsonify(model_list)

# =========================    APIs    =========================

app.run()
