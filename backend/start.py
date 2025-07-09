import sql
import flask
from flask import request, jsonify
from flask_cors import CORS
import requests
from sql import create_connection, execute_read_query, close_connection, Creds

app = flask.Flask(__name__)
app.config["DEBUG"] = False
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

    rpo_list = []

    join_clause = """
            JOIN Engines e ON v.engine_id = e.engine_id 
            JOIN Transmissions t ON v.transmission_id = t.transmission_id 
            JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id 
            JOIN Colors c ON v.color_id = c.color_id 
            JOIN Orders o ON v.order_id = o.order_id 
            LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
    """

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
        rpo_list = rpo.split(',') if ',' in rpo else [rpo]
        h40_selected = 'H40' in rpo_list
        zlz_selected = 'ZLZ' in rpo_list
        rpo_n = len(rpo_list)
        join_clause += "\n            JOIN Options opt ON v.vehicle_id = opt.vehicle_id"
        rpo_conditions = {
            "H40": ["(modelYear = '2024' AND model = 'CAMARO' AND trim = '2SS' AND color_name = 'RADIANT RED TINTCOAT' AND opt.option_code = 'SL1') OR v.vin IN ('1G1FK1R65R0117449', '1G1FK3D62R0118478')"],
            "WBL": ["model = 'CAMARO'", "trim NOT IN ('ZL1', '1LS')", "color_name IN ('BLACK', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC')"],
            "B2E": ["model = 'CAMARO'", "trim IN ('2LT', '2SS', '3LT')", "modelYear != '2024'", "color_name IN ('BLACK', 'SUMMIT WHITE', 'RAPID BLUE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC', 'SHOCK')"],
            "Z4B": ["modelYear = '2024'", "model = 'CAMARO'", "color_name IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC')"],
            "X56": ["modelYear = '2024'", "model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'", "transmission_type = 'M6'", "color_name = 'RIPTIDE BLUE METALLIC'", "msrp = '89185'"],
            "A1Z": ["model = 'CAMARO'", "body = 'COUPE'", "trim = 'ZL1'"],
            "A1Y": ["model = 'CAMARO'", "body = 'COUPE'", "trim IN ('1SS', '2SS')"],
            "A1X": ["modelYear IN ('2020', '2021')", "model = 'CAMARO'", "body = 'COUPE'", "trim IN ('1LT', '2LT', '3LT')"],
            "PEH": ["modelYear = '2020'", "model = 'CAMARO'", "body = 'COUPE'", "trim IN ('2SS', 'ZL1')", "transmission_type = 'A10'", "color_name = 'BLACK'"],
            "Z51": ["model = 'CORVETTE STINGRAY'"],
            "ZCR": ["model = 'CORVETTE STINGRAY'", "modelYear = '2022'", "trim = '3LT'", "(color_name = 'HYPERSONIC GRAY METALLIC' OR color_name = 'ACCELERATE YELLOW METALLIC')"],
            "Y70": ["model IN ('CORVETTE STINGRAY', 'CORVETTE Z06')", "modelYear = '2023'", "trim IN ('3LT', '3LZ')", "(color_name = 'WHITE PEARL METALLIC TRICOAT' OR color_name = 'CARBON FLASH METALLIC')"],
            "Z07": ["model = 'CORVETTE Z06'", "modelYear >= '2023'"],
            "ZTK": ["model = 'CORVETTE ZR1'", "modelYear >= '2025'"],
            "ZLE": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'ELECTRIC BLUE'"],
            "ZLD": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'MAVERICK NOIR FROST'"],
            "ZLG": ["modelYear = '2023'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'RIFT METALLIC'"],
            "ZLK": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'MERCURY SILVER METALLIC'"],
            "ZLJ": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'BLACK RAVEN'"],
            "ZLR": ["modelYear = '2024'", "model = 'CT4'", "trim = 'V-SERIES BLACKWING'", "color_name = 'VELOCITY RED'"],
            "ZLZ": ["modelYear = '2025'", "model IN ('CT4', 'CT5')", "trim = 'V-SERIES BLACKWING'", "color_name = 'MAGNUS METAL FROST'"],
            "ABQ": ["modelYear = '2023'", "model = 'CT5'", "trim = 'V-SERIES BLACKWING'", "msrp > '118000'"],
            "ZLT": ["modelYear = '2024'", "model = 'CT5'", "trim = 'V-SERIES BLACKWING'", "opt.option_code IN ('ZLT', 'ZLV')"],
            "Z6X": ["model IN ('HUMMER EV SUV', 'HUMMER EV PICKUP')"],
            "WFP": ["modelYear = '2024'", "model = 'HUMMER EV SUV'", "trim = '3X'", "color_name = 'NEPTUNE BLUE MATTE'"],
        }

        if h40_selected:
            vin_filters = []
            if trim:
                vin_filters.append(f"trim = '{trim}'")
            if color:
                vin_filters.append(f"color_name = '{color}'")
            vin_extra = " AND " + " AND ".join(vin_filters) if vin_filters else ""
            rpo_conditions["H40"] = [
                f"((modelYear = '2024' AND model = 'CAMARO' AND trim = '2SS' "
                f"AND color_name = 'RADIANT RED TINTCOAT' AND opt.option_code = 'SL1') "
                f"OR (v.vin IN ('1G1FK1R65R0117449','1G1FK3D62R0118478'){vin_extra}))"
            ]

        for rpo in rpo_list:
            if rpo in rpo_conditions:
                conditions.extend(rpo_conditions[rpo])

        for code_to_remove in ['H40', 'ZLT']:
            if code_to_remove in rpo_list:
                rpo_list = [code for code in rpo_list if code != code_to_remove]
                rpo_n = len(rpo_list)

        if len(rpo_list) > 1:
            rpo_placeholders = "', '".join(rpo_list)
            conditions.append(f"opt.option_code IN ('{rpo_placeholders}')")
        elif len(rpo_list) == 1:
            conditions.append(f"opt.option_code = '{rpo_list[0]}'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    if not rpo_list or 'H40' in rpo_list:
        rpo_clause = ""
    else:
        rpo_clause = f"HAVING COUNT(DISTINCT opt.option_code) = {rpo_n}"

    def get_all_distinct_values():
        columns = ['modelYear', 'body', 'trim', 'engine_type', 'transmission_type', 'model', 'color_name', 'country']
        sqlStatement = f"""
            SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, c.color_name, o.country 
            FROM Vehicles v 
            {join_clause}
            {where_clause}
            GROUP BY v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, c.color_name, o.country
            {rpo_clause}
        """
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
            c.color_name, v.msrp, o.country, 
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
        FROM Vehicles v {join_clause}
        {where_clause}
        GROUP BY v.vin, v.modelYear, v.model, v.body, v.trim, 
                e.engine_type, t.transmission_type, d.drivetrain_type, 
                c.color_name, v.msrp, o.country 
        {rpo_clause}
        {order_clause}
        LIMIT {limit} OFFSET {offset}
    """
    
    viewTable = execute_read_query(conn, select)
    totalSql = f"SELECT COUNT(*) AS total FROM (\n        SELECT v.vehicle_id FROM Vehicles v {join_clause} \n        {where_clause} \n        GROUP BY v.vehicle_id \n        {rpo_clause}\n) AS filtered_vehicles"
    total_items = execute_read_query(conn, totalSql)[0]['total']
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

@app.route('/stats', methods=['GET'])
def color_stats():
    category = request.args.get('category', '').strip() or None
    year = request.args.get('year', '').strip() or None
    body = request.args.get('body', '').strip() or None
    trim = request.args.get('trim', '').strip() or None
    engine = request.args.get('engine', '').strip() or None
    trans = request.args.get('trans', '').strip() or None
    model = request.args.get('model', '').strip() or None

    if category == 'color':
        conditions = []
        if year:
            conditions.append(f"v.modelYear = '{year}'")
        if model:
            if model == "CORVETTE (ALL)":
                corvette_models = ["CORVETTE STINGRAY", "CORVETTE STINGRAY W/ Z51", "CORVETTE GRAND SPORT", "CORVETTE E-RAY", "CORVETTE Z06", "CORVETTE ZR1"]
                corvette_list = ", ".join(f"'{m}'" for m in corvette_models)
                conditions.append(f"v.model IN ({corvette_list})")
            else:
                conditions.append(f"v.model = '{model}'")
        if body:
            conditions.append(f"v.body = '{body}'")
        if trim:
            conditions.append(f"v.trim = '{trim}'")
        if engine:
            conditions.append(f"e.engine_type = '{engine}'")
        if trans:
            conditions.append(f"t.transmission_type = '{trans}'")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        join_clause = """
            JOIN Colors c ON v.color_id = c.color_id
            JOIN Engines e ON v.engine_id = e.engine_id
            JOIN Transmissions t ON v.transmission_id = t.transmission_id
        """

        distinct_sql = f"""
            SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type
            FROM Vehicles v
            {join_clause}
            {where_clause}
            ORDER BY v.modelYear DESC, v.model, v.body, v.trim, e.engine_type, t.transmission_type
        """

        sqlStatement = f"""
            WITH ColorCounts AS (
                SELECT
                    CASE WHEN c.rpo_code = 'N/A' THEN c.color_name ELSE c.rpo_code END AS rpo_code,
                    COUNT(*) AS total_count,
                    GROUP_CONCAT(DISTINCT c.color_name ORDER BY c.color_name SEPARATOR ', ') AS color_names
                FROM Vehicles v
                {join_clause}
                {where_clause}
                GROUP BY CASE WHEN c.rpo_code = 'N/A' THEN c.color_name ELSE c.rpo_code END
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    rpo_code,
                    total_count,
                    color_names,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM ColorCounts
            )
            SELECT * FROM Ranked;
        """

        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
        distinct_results = execute_read_query(conn, distinct_sql)
        year_list = sorted(set(r['modelYear'] for r in distinct_results if r['modelYear']), reverse=True)
        model_list = sorted(set(r['model'] for r in distinct_results if r['model']))
        body_list = sorted(set(r['body'] for r in distinct_results if r['body']))
        trim_list = sorted(set(r['trim'] for r in distinct_results if r['trim']))
        engine_list = sorted(set(r['engine_type'] for r in distinct_results if r['engine_type']))
        trans_list = sorted(set(r['transmission_type'] for r in distinct_results if r['transmission_type']))

        viewTable = execute_read_query(conn, sqlStatement)
        close_connection(conn)

        return jsonify({
            'stats_data': viewTable,
            'year': year_list,
            'model': model_list,
            'body': body_list,
            'trim': trim_list,
            'engine': engine_list,
            'trans': trans_list,
            'category': category
        })
    elif category == 'msrp':
        conditions = ["o.creation_date IS NOT NULL"]
        if year:
            conditions.append(f"v.modelYear = '{year}'")
        if model:
            if model == "CORVETTE (ALL)":
                corvette_models = ["CORVETTE STINGRAY", "CORVETTE STINGRAY W/ Z51", "CORVETTE GRAND SPORT", "CORVETTE E-RAY", "CORVETTE Z06", "CORVETTE ZR1"]
                corvette_list = ", ".join(f"'{m}'" for m in corvette_models)
                conditions.append(f"v.model IN ({corvette_list})")
            else:
                conditions.append(f"v.model = '{model}'")
        if body:
            conditions.append(f"v.body = '{body}'")
        if trim:
            conditions.append(f"v.trim = '{trim}'")
        if engine:
            conditions.append(f"e.engine_type = '{engine}'")
        if trans:
            conditions.append(f"t.transmission_type = '{trans}'")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        sql = f"""
        WITH FilteredVehicles AS (
            SELECT 
                DATE_FORMAT(o.creation_date, '%Y-%m') AS `year_month`,
                v.model,
                v.msrp
            FROM Vehicles v
            JOIN Engines e ON v.engine_id = e.engine_id
            JOIN Transmissions t ON v.transmission_id = t.transmission_id
            JOIN Orders o ON v.order_id = o.order_id
            {where_clause}
        )
        SELECT
            `year_month`,
            model,
            COUNT(*) AS total_count,
            AVG(msrp) AS avg_msrp,
            MIN(msrp) AS min_msrp,
            MAX(msrp) AS max_msrp
        FROM FilteredVehicles
        GROUP BY `year_month`, model
        ORDER BY `year_month` DESC, model;
        """

        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
        results = execute_read_query(conn, sql)
        close_connection(conn)

        models = sorted(set(r['model'] for r in results if r['model']))

        return jsonify({
            'stats_data': results,
            'model': models,
            'category': category
        })

    else:
        return jsonify([])

#========================= View Pages #=========================

app.run(host="0.0.0.0", port=5000)
