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
    allJson = json.loads(data["allJson"])

    model_year = allJson["model_year"]
    mmc_code = allJson["mmc_code"]
    mmcDict = data["mmc"]
    colorMap = data["colorMap"]
    intColor = data["intColor"]
    options = [option for option in allJson["Options"] if option]
    rpos = "_".join(options)
    baseURL = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/image.gen?i="
    baseURL_int = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/imageinterior.gen?i="

    if mmc_code in ["1YC07", "1YC67"]:
        trim = next((opt for opt in options if opt in ["1LT", "2LT", "3LT"]), mmcDict.get(mmc_code))
    elif mmc_code in ["1YH07", "1YH67"]:
        trim = next((opt for opt in options if opt in ["1LZ", "2LZ", "3LZ"]), mmcDict.get(mmc_code))
    else:
        trim = mmcDict.get(mmc_code)
    
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
                if key == option:
                    colorInt = key
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
            print(built_url)
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
    body = request.args.get('body')
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
    if body:
        conditions.append(f"body = '{body}'")
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
    if color:
        conditions.append(f"exterior_color = '{color}'")
    if country == "USA":
        conditions.append("NOT JSON_CONTAINS(allJson->'$.maker', '\"GMCANADA\"')")
        conditions.append("NOT JSON_CONTAINS(allJson->'$.maker', '\"N/A\"')")
    elif country == "CAN":
        conditions.append("JSON_CONTAINS(allJson->'$.maker', '\"GMCANADA\"')")
    elif country:
        conditions.append("JSON_CONTAINS(allJson->'$.maker', '\"N/A\"')")

    rpo_conditions = {
        "Z4B": ["modelYear = '2024'", "model = 'CAMARO'", "exterior_color IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC')"],
        "X56": ["modelYear = '2024'", "model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'", "transmission = 'M6'", "exterior_color = 'RIPTIDE BLUE METALLIC'", "msrp = '89185'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "A1Z": ["model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "A1Y": ["model = 'CAMARO'", "body = 'COUPE'", "trim in ('1SS', '2SS')", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "A1X": ["modelYear in ('2020', '2021')", "model = 'CAMARO'", "body = 'COUPE'", "trim in ('1LT', '2LT', '3LT')", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "Z51": ["model = 'CORVETTE STINGRAY'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZCR": ["model = 'CORVETTE STINGRAY'", "modelYear = '2022'", "trim = '3LT'", "(exterior_color = 'HYPERSONIC GRAY' OR exterior_color = 'ACCELERATE YELLOW')", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "Y70": ["model in ('CORVETTE STINGRAY', 'CORVETTE Z06')", "modelYear = '2023'", "trim in ('3LT', '3LZ')", "(exterior_color = 'WHITE PEARL' OR exterior_color = 'CARBON FLASH')", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "Z07": ["model = 'CORVETTE Z06'", "modelYear = '2023'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "LF4": ["model = 'CT4'", "trim = 'V-SERIES BLACKWING'"],
        "ZLE": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'ELECTRIC BLUE'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZLD": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'MAVERICK NOIR FROST'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZLG": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'RIFT METALLIC'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZLK": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'MERCURY SILVER METALLIC'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZLJ": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'BLACK RAVEN'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "ZLR": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "exterior_color = 'VELOCITY RED'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"],
        "1SV": ["model = 'CT5'", "trim = 'V-SERIES BLACKWING'"],
        "ABQ": ["modelYear = '2023'", "model = 'CT5'", "trim = 'V-SERIES BLACKWING'", "msrp > '118000'", f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')"]
    }

    if rpo in rpo_conditions:
        conditions.extend(rpo_conditions[rpo])
    elif rpo:
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    def get_distinct_values(column):
        sqlStatement = f"SELECT DISTINCT {column} FROM gm{where_clause} ORDER BY {column}"
        results = execute_read_query(conn, sqlStatement)
        return [result[column] for result in results]

    year_list = get_distinct_values('modelYear')
    body_list = get_distinct_values('body')
    trim_list = get_distinct_values('trim')
    engine_list = get_distinct_values('vehicleEngine')
    trans_list = get_distinct_values('transmission')
    model_list = get_distinct_values('model')
    color_list = get_distinct_values('exterior_color')

    if rpo in ["Z4B", "X56"] and order not in ["ASC", "DESC"]:
        order_clause = "ORDER BY SUBSTRING(vin, -6)"
    else:
        order_clause = f"ORDER BY msrp {'ASC' if order == 'ASC' else 'DESC'}"

    viewTable = execute_read_query(conn, f"SELECT * FROM gm{where_clause} {order_clause} LIMIT {limit} OFFSET {offset}")
    total_items = execute_read_query(conn, f"SELECT COUNT(*) AS total FROM gm{where_clause}")[0]['total']

    return jsonify({
        'data': viewTable,
        'total': total_items,
        'year': year_list,
        'body': body_list,
        'trim': trim_list,
        'engine': engine_list,
        'trans': trans_list,
        'color': color_list,
        'model': model_list
    })

# ========================= View Pages =========================

app.run()
