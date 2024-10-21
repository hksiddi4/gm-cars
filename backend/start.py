import sql
import flask
from flask import request, jsonify
from flask_cors import CORS
from sql import create_connection, execute_read_query, close_connection, Creds
import requests
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

myCreds = sql.Creds()

#========================= View Pages #=========================

@app.route('/search', methods=['GET'])
def search_inv():
    vin = request.args.get('vin')
    join_clause = """
        JOIN Engines e ON v.engine_id = e.engine_id 
        JOIN Transmissions t ON v.transmission_id = t.transmission_id 
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
        JOIN Colors c ON v.color_id = c.color_id 
        JOIN Orders o ON v.order_id = o.order_id 
        JOIN Dealers dl ON v.dealer_id = dl.dealer_id
        LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        LEFT JOIN Options opt ON v.vehicle_id = opt.vehicle_id
        LEFT JOIN MMC_Codes mc ON o.mmc_code_id = mc.mmc_code_id
    """
    sqlStatement = f"""
        SELECT v.vin, v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, 
            d.drivetrain_type, c.color_name, v.msrp, o.country, o.order_number, mc.mmc_code, 
            UPPER(DATE_FORMAT(o.creation_date, '%W, %d %M %Y')) AS formatted_date, 
            dl.dealer_name, dl.location, 
            COALESCE(GROUP_CONCAT(DISTINCT se.special_desc SEPARATOR ', '), 'NA') AS special_descs,
            GROUP_CONCAT(DISTINCT opt.option_code SEPARATOR ', ') AS rpo_codes
        FROM Vehicles v
        {join_clause}
        WHERE v.vin = '{vin}' 
        GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, 
                d.drivetrain_type, c.color_name, v.msrp, o.country, o.order_number, mc.mmc_code, 
                formatted_date, dl.dealer_name, dl.location
        LIMIT 1
    """
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    viewTable = execute_read_query(conn, sqlStatement)
    close_connection(conn)
    
    for row in viewTable:
        if 'rpo_codes' in row:
            row['rpo_codes'] = row['rpo_codes'].split(', ')
    return jsonify(viewTable)

@app.route('/api/genurl', methods=['POST'])
def generate_url():
    data = request.json["data"]
    vin_data = data["vin_data"]

    model_year = vin_data[0]["modelYear"]
    mmc_code = vin_data[0]["mmc_code"]
    mmcDict = data["mmc"]
    colorMap = data["colorMap"]
    intColor = data["intColor"]
    options = vin_data[0]["rpo_codes"]
    rpos = "_".join(options)
    baseURL = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/image.gen?i="
    baseURL_int = "https://cgi.chevrolet.com/mmgprod-us/dynres/prove/imageinterior.gen?i="

    if mmc_code in ["1YC07", "1YC67"]:
        trim = next((opt for opt in options if opt in ["1LT", "2LT", "3LT"]), mmcDict.get(mmc_code))
    elif mmc_code in ["1YH07", "1YH67", "1YG07", "1YG67"]:
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
            #print(built_url)
            response = requests.head(built_url)
            view += 1
            if response.status_code == 404:
                break
            urls_attempted.append(built_url)
    
    if not urls_attempted:
        ghost_img = "../img/ghost-chevrolet-car-alt.png"
        return jsonify({"generatedImages": ghost_img})
    return jsonify({"generatedImages": urls_attempted})

# Working on replacing
@app.route('/api/rarity', methods=['POST'])
def unique():
    data = request.json
    options = data.get('Options')

    if options is not None:
        formatted_options = json.dumps(options)
        try:
            sqlStatement = f"SELECT COUNT(*) AS Count FROM gm WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) = '{formatted_options}'"
            conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
            response = execute_read_query(conn, sqlStatement)
            close_connection(conn)
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

    join_clause = """
            JOIN Engines e ON v.engine_id = e.engine_id 
            JOIN Transmissions t ON v.transmission_id = t.transmission_id 
            JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
            JOIN Colors c ON v.color_id = c.color_id 
            JOIN Orders o ON v.order_id = o.order_id 
            JOIN Dealers dl ON v.dealer_id = dl.dealer_id 
            LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id """

    country_map = {
        "CAN": "CANADA",
        "MEX": "MEXICO"
        }

    conditions = []
    if year:
        conditions.append(f"modelYear = '{year}'")
    if models:
        models = [model.strip() for model in models.split(',')]
        models = "', '".join(models)
        conditions.append(f"model IN ('{models}')")
    if body:
        conditions.append(f"body = '{body}'")
    if trim:
        conditions.append(f"trim = '{trim}'")
    if engine:
        conditions.append(f"engine_type = '{engine}'")
    if trans:
        conditions.append(f"transmission_type = '{trans}'")
    if color:
        conditions.append(f"color_name = '{color}'")
    if country:
        conditions.append(f"country = '{country_map.get(country, 'USA')}'")
    if rpo:
        join_clause += "\n            JOIN Options opt ON v.vehicle_id = opt.vehicle_id"
        rpo_conditions = {
            "WBL": ["model = 'CAMARO'", "trim NOT IN ('ZL1', '1LS')", "color_name IN ('BLACK', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC')", f"opt.option_code = '{rpo}'"],
            "B2E": ["model = 'CAMARO'", "trim IN ('2LT', '2SS', '3LT')", "modelYear != '2024'", "color_name IN ('BLACK', 'SUMMIT WHITE', 'RAPID BLUE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC', 'SHOCK')", f"opt.option_code = '{rpo}'"],
            "Z4B": ["modelYear = '2024'", "model = 'CAMARO'", "color_name IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC')", f"opt.option_code = '{rpo}'"],
            "X56": ["modelYear = '2024'", "model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'", "transmission_type = 'M6'", "color_name = 'RIPTIDE BLUE METALLIC'", "msrp = '89185'", f"opt.option_code = '{rpo}'"],
            "A1Z": ["model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'", f"opt.option_code = '{rpo}'"],
            "A1Y": ["model = 'CAMARO'", "body = 'COUPE'", "trim in ('1SS', '2SS')", f"opt.option_code = '{rpo}'"],
            "A1X": ["modelYear in ('2020', '2021')", "model = 'CAMARO'", "body = 'COUPE'", "trim in ('1LT', '2LT', '3LT')", f"opt.option_code = '{rpo}'"],
            "PEH": ["modelYear = '2020'", "model = 'CAMARO'", "body = 'COUPE'", "trim in ('2SS', 'ZL1')", "transmission_type = 'A10'", "color_name = 'BLACK'", f"opt.option_code = '{rpo}'"],
            "Z51": ["model = 'CORVETTE STINGRAY'", f"opt.option_code = '{rpo}'"],
            "ZCR": ["model = 'CORVETTE STINGRAY'", "modelYear = '2022'", "trim = '3LT'", "(color_name = 'HYPERSONIC GRAY METALLIC' OR color_name = 'ACCELERATE YELLOW METALLIC')", f"opt.option_code = '{rpo}'"],
            "Y70": ["model in ('CORVETTE STINGRAY', 'CORVETTE Z06')", "modelYear = '2023'", "trim in ('3LT', '3LZ')", "(color_name = 'WHITE PEARL METALLIC TRICOAT' OR color_name = 'CARBON FLASH METALLIC')", f"opt.option_code = '{rpo}'"],
            "Z07": ["model = 'CORVETTE Z06'", "modelYear = '2023'", f"opt.option_code = '{rpo}'"],
            "ZLE": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'ELECTRIC BLUE'", f"opt.option_code = '{rpo}'"],
            "ZLD": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'MAVERICK NOIR FROST'", f"opt.option_code = '{rpo}'"],
            "ZLG": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'RIFT METALLIC'", f"opt.option_code = '{rpo}'"],
            "ZLK": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'MERCURY SILVER METALLIC'", f"opt.option_code = '{rpo}'"],
            "ZLJ": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'BLACK RAVEN'", f"opt.option_code = '{rpo}'"],
            "ZLR": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'VELOCITY RED'", f"opt.option_code = '{rpo}'"],
            "ABQ": ["modelYear = '2023'", "model = 'CT5'", "trim = 'V-SERIES BLACKWING'", "msrp > '118000'", f"opt.option_code = '{rpo}'"]
        }

        if rpo in rpo_conditions:
            conditions.extend(rpo_conditions[rpo])
        elif rpo:
            conditions.append(f"opt.option_code = '{rpo}'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    def get_all_distinct_values():
        columns = ['modelYear', 'body', 'trim', 'engine_type', 'transmission_type', 'model', 'color_name', 'country']
        sqlStatement = f"SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, c.color_name, o.country FROM vehicles v {join_clause} \n            {where_clause}"
        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
        results = execute_read_query(conn, sqlStatement)
        close_connection(conn)
        distinct_values = {col: set() for col in columns}
        for result in results:
            for col in columns:
                if result[col] is not None:
                    distinct_values[col].add(result[col])
        sorted_values = {
            'modelYear': sorted(list(distinct_values['modelYear']), reverse=True),
            **{col: sorted(list(distinct_values[col])) for col in columns if col != 'modelYear'}
        }
        return sorted_values
    distinct_values = get_all_distinct_values()

    year_list = distinct_values['modelYear']
    body_list = distinct_values['body']
    trim_list = distinct_values['trim']
    engine_list = distinct_values['engine_type']
    trans_list = distinct_values['transmission_type']
    model_list = distinct_values['model']
    color_list = distinct_values['color_name']
    country_list = distinct_values['country']

    if rpo in ["Z4B", "X56", "PEH"] and order not in ["ASC", "DESC"]:
        order_clause = "ORDER BY SUBSTRING(vin, -6)"
    elif order in ["ASC", "DESC"]:
        order_clause = f"ORDER BY msrp {'ASC' if order == 'ASC' else 'DESC'}"
    elif order in ["vinASC", "vinDESC"]:
        order_clause = f"ORDER BY SUBSTRING(vin, -6) {'DESC' if order == 'vinDESC' else 'ASC'}, modelYear ASC"
    else: order_clause = ""

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    select = f"""
        SELECT v.vin, v.modelYear, v.model, v.body, v.trim, 
            e.engine_type, t.transmission_type, d.drivetrain_type, 
            c.color_name, v.msrp, o.country, dl.dealer_name, 
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
        FROM Vehicles v {join_clause}
        {where_clause}
        GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, 
                e.engine_type, t.transmission_type, d.drivetrain_type, 
                c.color_name, v.msrp, o.country, dl.dealer_name
        {order_clause}
        LIMIT {limit} OFFSET {offset}
    """
    viewTable = execute_read_query(conn, select)
    total_items = execute_read_query(conn, f"SELECT COUNT(DISTINCT v.vehicle_id) AS total FROM Vehicles v {join_clause} {where_clause}")[0]['total']
    close_connection(conn)

    return jsonify({
        'data': viewTable,
        'total': total_items,
        'year': year_list,
        'model': model_list,
        'body': body_list,
        'trim': trim_list,
        'engine': engine_list,
        'trans': trans_list,
        'color': color_list,
        'country': country_list
    })

#========================= View Pages #=========================

app.run()
