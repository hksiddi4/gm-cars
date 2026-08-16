from gevent import monkey
monkey.patch_all()

import sql
import flask
import requests
from flask import request, jsonify
from flask_cors import CORS
from sql import create_connection, execute_read_query, close_connection, Creds

app = flask.Flask(__name__)
app.config["DEBUG"] = False
app.json.sort_keys = False
CORS(app)

myCreds = sql.Creds()

OLLAMA_URL = "http://192.168.1.126:11434/api/generate"
AI_MODEL = "qwen2.5-coder:7b"

# Cleaned, tightly-formatted schema context
DB_SCHEMA_CONTEXT = """You are a MySQL database assistant. Output ONLY a valid raw MySQL SELECT statement. No markdown, no triple backticks, no explanations.

Schema:
Colors (color_id, color_name, rpo_code)
Dealers (dealer_id, dealer_name, location, sitedealer_code)
Drivetrains (drivetrain_id, drivetrain_type)
Engines (engine_id, engine_type, engine_rpo)
MMC_Codes (mmc_code_id, mmc_code)
Orders (order_id, order_number, creation_date, mmc_code_id, sell_source, country)
SpecialEditions (special_id, vehicle_id, special_desc)
Transmissions (transmission_id, transmission_type)
Vehicles (vehicle_id, vin, modelYear, model, body, trim, engine_id, transmission_id, drivetrain_id, color_id, msrp, dealer_id, order_id)

Rules:
1. ONLY SELECT queries. Do NOT append a semicolon at the end of the query.
2. Mandatory column layout when returning vehicles (Note the backticks):
   SELECT v.vin AS `VIN`, v.modelYear AS `Year`, v.model AS `Model`, v.body AS `Body`, v.trim AS `Trim`, e.engine_type AS `Engine`, t.transmission_type AS `Trans`, d.drivetrain_type AS `Drivetrain`, c.color_name AS `Exterior_Color`, v.msrp AS `MSRP`, IFNULL((SELECT GROUP_CONCAT(se.special_desc) FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id), '') AS `Package_Option`, o.country AS `Country`
3. ALWAYS use `LEFT JOIN` for all table relationships to prevent dropping vehicles with missing data. Use these exact links:
   - LEFT JOIN Colors c ON v.color_id = c.color_id
   - LEFT JOIN Engines e ON v.engine_id = e.engine_id
   - LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id
   - LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
   - LEFT JOIN Dealers dealer ON v.dealer_id = dealer.dealer_id
   - LEFT JOIN Orders o ON v.order_id = o.order_id
   - LEFT JOIN MMC_Codes m ON o.mmc_code_id = m.mmc_code_id
4. Do NOT join SpecialEditions in the FROM clause. NEVER use GROUP BY.
5. Append `LIMIT 500` (without a semicolon) unless executing aggregate functions.
6. Transmission: Automatic `t.transmission_type LIKE 'A%'`, Manual `t.transmission_type LIKE 'M%'`. Drivetrains: 'RWD', 'AWD', '4WD'.
7. Use wildcard `LIKE` for generic color matching (e.g., c.color_name LIKE '%ORANGE%').
8. Trims vs Special Editions: Trims are in `v.trim`. Packages like '1LE', 'ZTK' are in SpecialEditions. 
9. Package Filtering: To filter by a package or special edition, you MUST use a correlated EXISTS subquery in the WHERE clause: `EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc LIKE '%Keyword%')`.
10. Package Keywords Reference: Map user requests to these descriptions: 'Collector', 'Garage 56', '1LE', 'Hendrick', 'Indy 500', 'Redline', 'Shock and Steel', 'C8.R', 'ZTK', 'Z07', 'Z51', 'Grand Sport', '70th Anniversary', 'Stars & Steel', 'Quail Silver', 'Watkins Glen', 'Sebring', 'Blackwing', 'Omega Edition', 'Extreme Off-Road'.
11. Corvettes: Models use `v.model LIKE 'CORVETTE%'`.
"""

@app.route('/ai-query', methods=['POST'])
def natural_language_query():
    data = request.json or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    system_combined_prompt = f"{DB_SCHEMA_CONTEXT}\nUser Request: {user_prompt}\nSQL Query:"
    
    payload = {
        "model": AI_MODEL,
        "prompt": system_combined_prompt,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        generated_sql = response.json().get('response', '').strip()
    except Exception as e:
        return jsonify({'error': f'Failed to communicate with AI model: {str(e)}'}), 500

    if generated_sql.startswith("```"):
        generated_sql = generated_sql.replace("```sql", "").replace("```", "").strip()

    destructive_keywords = ["drop", "delete", "truncate", "update", "alter", "insert", "grant"]
    if any(keyword in generated_sql.lower() for keyword in destructive_keywords):
        return jsonify({'error': 'Security restriction: Destructive SQL detected', 'generated_sql': generated_sql}), 403

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    try:
        db_results = execute_read_query(conn, generated_sql)
        if db_results is None:
            close_connection(conn)
            return jsonify({
                'error': 'AI generated invalid SQL syntax or execution failed.', 
                'generated_sql': generated_sql
            }), 400
            
    except Exception as e:
        close_connection(conn)
        return jsonify({
            'error': 'Execution error', 
            'generated_sql': generated_sql, 
            'details': str(e)
        }), 400
    
    close_connection(conn)

    return jsonify({
        'generated_sql': generated_sql,
        'results': db_results
    })

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
        SELECT v.vin, v.modelYear, v.model, v.body, v.trim, e.engine_type,
               t.transmission_type, d.drivetrain_type, c.color_name, v.msrp,
               o.country, o.order_number, mc.mmc_code,
               UPPER(DATE_FORMAT(o.creation_date, '%%W, %%d %%M %%Y')) AS formatted_date,
               dl.dealer_name, dl.location,
               se.special_desc,
               opt.option_code
        FROM Vehicles v
        {join_clause}
        WHERE v.vin = %s
    """
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    rows = execute_read_query(conn, sqlStatement, (vin,))
    close_connection(conn)

    if not rows:
        return jsonify([])

    vehicle = {}
    rpo_codes = []
    special_descs = []

    for row in rows:
        if not vehicle:
            vehicle = {
                'vin': row['vin'],
                'modelYear': row['modelYear'],
                'model': row['model'],
                'body': row['body'],
                'trim': row['trim'],
                'engine_type': row['engine_type'],
                'transmission_type': row['transmission_type'],
                'drivetrain_type': row['drivetrain_type'],
                'color_name': row['color_name'],
                'msrp': row['msrp'],
                'country': row['country'],
                'order_number': row['order_number'],
                'mmc_code': row['mmc_code'],
                'formatted_date': row['formatted_date'],
                'dealer_name': row['dealer_name'],
                'location': row['location']
            }

        if row['option_code']:
            rpo_codes.append(row['option_code'])
        if row['special_desc']:
            special_descs.append(row['special_desc'])

    vehicle['rpo_codes'] = sorted(set(rpo_codes))
    vehicle['special_descs'] = ', '.join(sorted(set(special_descs))) if special_descs else 'NA'

    return jsonify([vehicle])

@app.route('/vehicles', methods=['GET'])
def sort_price():
    year = request.args.get('year')
    body = request.args.get('body')
    trim = request.args.get('trim')
    engine = request.args.get('engine')
    trans = request.args.get('trans')
    drivetrain = request.args.get('drivetrain')
    models_list = request.args.getlist('model') or request.args.getlist('model[]')
    rpo = request.args.get('rpo')
    color = request.args.get('color')
    country = request.args.get('country')
    date = request.args.get('date')
    order = request.args.get('order')
    page = request.args.get('page', 1)
    
    limit = 100
    try:
        page = int(page)
        offset = (page - 1) * limit
    except (ValueError, TypeError):
        page = 1
        offset = 0

    rpo_list = []
    rpo_list_for_filtering = []
    conditions = []
    params = []

    filter_join_clause = """
        JOIN Engines e ON v.engine_id = e.engine_id
        JOIN Transmissions t ON v.transmission_id = t.transmission_id
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        JOIN Colors c ON v.color_id = c.color_id
        JOIN Orders o ON v.order_id = o.order_id
    """

    country_map = {
        "CAN": "CANADA",
        "MEX": "MEXICO"
    }

    if year:
        conditions.append("v.modelYear = %s")
        params.append(year)
    if models_list:
        if "CORVETTE (C8)" in models_list:
            models_list.remove("CORVETTE (C8)")
            c8_cond = "(v.model LIKE 'CORVETTE%%' AND v.modelYear >= '2020')"
            if models_list:
                placeholders = ', '.join(['%s'] * len(models_list))
                conditions.append(f"({c8_cond} OR v.model IN ({placeholders}))")
                params.extend(models_list)
            else:
                conditions.append(c8_cond)
        else:
            placeholders = ', '.join(['%s'] * len(models_list))
            conditions.append(f"v.model IN ({placeholders})")
            params.extend(models_list)
    if body:
        conditions.append("v.body = %s")
        params.append(body)
    if trim:
        conditions.append("v.trim = %s")
        params.append(trim)
    if engine:
        conditions.append("e.engine_type = %s")
        params.append(engine)
    if trans:
        conditions.append("t.transmission_type = %s")
        params.append(trans)
    if drivetrain:
        conditions.append("d.drivetrain_type = %s")
        params.append(drivetrain)
    if color:
        conditions.append("c.color_name = %s")
        params.append(color)
    if country:
        conditions.append("o.country = %s")
        params.append(country_map.get(country, 'USA'))
    if date:
        if len(date) == 4:
            conditions.append("YEAR(o.creation_date) = %s")
        elif len(date) == 7:
            conditions.append("DATE_FORMAT(o.creation_date, '%%Y-%%m') = %s")
        else:
            conditions.append("DATE(o.creation_date) = %s")
        params.append(date)

    if rpo:
        rpo_list = rpo.split(',') if ',' in rpo else [rpo]
        filter_join_clause += " JOIN Options opt ON v.vehicle_id = opt.vehicle_id"
        
        rpo_conditions = {
            "Z4B": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "c.color_name IN ('PANTHER BLACK MATTE', 'PANTHER BLACK METALLIC TINTCOAT')"],
            "ZL4B": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "v.trim = 'ZL1'", "c.color_name = 'PANTHER BLACK MATTE'"],
            "X56": ["v.modelYear = '2024'", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim = 'ZL1'", "t.transmission_type = 'M6'", "c.color_name = 'RIPTIDE BLUE METALLIC'", "v.msrp = '89185'"],
            "A1Z": ["v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim = 'ZL1'"],
            "A1Y": ["v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('1SS', '2SS')"],
            "A1X": ["v.modelYear IN ('2019', '2020', '2021')", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('1LT', '2LT', '3LT')"],
            "H40": ["((v.modelYear = '2024' AND v.model = 'CAMARO' AND v.trim = '2SS' AND c.color_name = 'RADIANT RED TINTCOAT' AND opt.option_code = 'SL1') OR v.vin IN ('1G1FK1R65R0117449', '1G1FK3D62R0118478'))"],
            "PEH": ["v.modelYear = '2020'", "v.model = 'CAMARO'", "v.body = 'COUPE'", "v.trim IN ('2SS', 'ZL1')", "t.transmission_type = 'A10'", "c.color_name = 'BLACK'"],
            "Z4Z": ["v.model = 'CAMARO'", "v.body = 'CONVERTIBLE'", "v.trim = '2SS'", "c.color_name IN ('WILD CHERRY TINTCOAT', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC')"],
            "WBL": ["v.modelYear IN ('2020', '2021', '2022', '2023', '2024')", "v.model = 'CAMARO'", "v.trim NOT IN ('ZL1', '1LS')", "c.color_name IN ('BLACK', 'SUMMIT WHITE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC')"],
            "B2E": ["v.model = 'CAMARO'", "v.trim IN ('2LT', '2SS', '3LT')", "v.modelYear IN ('2020', '2021', '2022', '2023')", "c.color_name IN ('BLACK', 'SUMMIT WHITE', 'RAPID BLUE', 'SHARKSKIN METALLIC', 'SATIN STEEL GRAY METALLIC', 'SHOCK')"],
            "ZCR": ["v.model = 'CORVETTE STINGRAY'", "v.modelYear = '2022'", "v.trim = '3LT'", "(c.color_name = 'HYPERSONIC GRAY METALLIC' OR c.color_name = 'ACCELERATE YELLOW METALLIC')"],
            "ZTK": ["v.model IN ('CORVETTE ZR1', 'CORVETTE ZR1X')", "v.modelYear IN ('2019', '2025', '2026', '2027')"],
            "Z07": ["v.model = 'CORVETTE Z06'"],
            "Z51": ["v.model = 'CORVETTE STINGRAY'"],
            "Z25": ["v.model = 'CORVETTE GRAND SPORT'"],
            "FEB": ["v.model = 'CORVETTE GRAND SPORT'"],
            "FEY": ["v.model = 'CORVETTE GRAND SPORT'"],
            "Y70": ["v.model IN ('CORVETTE STINGRAY', 'CORVETTE Z06')", "v.modelYear = '2023'", "v.trim IN ('3LT', '3LZ')", "(c.color_name = 'WHITE PEARL METALLIC TRICOAT' OR c.color_name = 'CARBON FLASH METALLIC')"],
            "I26": ["v.model = 'CORVETTE E-RAY'", "v.modelYear = '2026'", "v.trim = '3LZ'", "c.color_name = 'ARCTIC WHITE'", "o.country = 'USA'", "v.body = 'CONVERTIBLE'", "v.msrp = '160835'"],
            "USA": ["v.model IN ('CORVETTE STINGRAY', 'CORVETTE Z06', 'CORVETTE E-RAY', 'CORVETTE ZR1', 'CORVETTE ZR1X')", "v.modelYear = '2026'", "v.trim IN ('3LT', '3LZ')", "(c.color_name = 'ARCTIC WHITE' OR c.color_name = 'BLACK')"],
            "ZRA": ["v.model = 'CORVETTE ZR1X'", "v.modelYear = '2026'", "v.trim = '3LZ'", "c.color_name = 'BLADE SILVER MATTE'"],
            "ZLE": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'ELECTRIC BLUE'"],
            "ZLD": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'MAVERICK NOIR FROST'"],
            "ZLG": ["v.modelYear = '2023'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'RIFT METALLIC'"],
            "ZLK": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'MERCURY SILVER METALLIC'"],
            "ZLJ": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'BLACK RAVEN'"],
            "ZLR": ["v.modelYear = '2024'", "v.model = 'CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'VELOCITY RED'"],
            "ZLZ4": ["v.modelYear = '2025'", "v.model ='CT4'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'MAGNUS METAL FROST'"],
            "ZLZ5": ["v.modelYear = '2025'", "v.model ='CT5'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'MAGNUS METAL FROST'"],
            "ABQ": ["v.modelYear = '2023'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "v.msrp > '118000'"],
            "ZLT": ["v.modelYear = '2024'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "opt.option_code IN ('ZLT', 'ZLV')"],
            "V8V": ["v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'"],
            "PCK1": ["v.modelYear = '2026'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'DEEP OCEAN TINTCOAT'"],
            "Z6X": ["v.model IN ('HUMMER EV SUV', 'HUMMER EV PICKUP')"],
            "WFP": ["v.modelYear = '2024'", "v.model = 'HUMMER EV SUV'", "v.trim = '3X'", "c.color_name = 'NEPTUNE BLUE MATTE'"],
        }

        for rpo_code in rpo_list:
            if rpo_code in rpo_conditions:
                conditions.extend(rpo_conditions[rpo_code])

        substitution_map = {
            'ZL4B': 'Z4B',
            'ZLZ4': 'ZLZ',
            'ZLZ5': 'ZLZ',
            'PCK1': 'PCK',
            "I26": "R7V",
        }

        for code in rpo_list:
            if code in substitution_map:
                rpo_list_for_filtering.append(substitution_map[code])
            elif code not in ['H40', 'ZLT']:
                rpo_list_for_filtering.append(code)

        rpo_list_for_filtering = list(set(rpo_list_for_filtering))
        rpo_n = len(rpo_list_for_filtering)

        if len(rpo_list_for_filtering) > 1:
            placeholders = ', '.join(['%s'] * len(rpo_list_for_filtering))
            conditions.append(f"opt.option_code IN ({placeholders})")
            params.extend(rpo_list_for_filtering)
        elif len(rpo_list_for_filtering) == 1:
            conditions.append("opt.option_code = %s")
            params.append(rpo_list_for_filtering[0])

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    if not rpo_list_for_filtering or 'H40' in rpo_list:
        rpo_clause = ""
    else:
        rpo_clause = f"HAVING COUNT(DISTINCT opt.option_code) = {rpo_n}"

    if any(code in ["ZL4B", "X56", "PEH"] for code in rpo_list) and order not in ["ASC", "DESC"]:
        order_clause = "ORDER BY SUBSTRING(v.vin, -6)"
    elif order in ["ASC", "DESC"]:
        order_clause = f"ORDER BY v.msrp {'ASC' if order == 'ASC' else 'DESC'}"
    elif order in ["vinASC", "vinDESC"]:
        order_clause = f"ORDER BY SUBSTRING(v.vin, -6) {'DESC' if order == 'vinDESC' else 'ASC'}, v.modelYear ASC"
    else:
        order_clause = "ORDER BY v.vehicle_id DESC"

    def get_all_distinct_values(current_where, current_params, current_filter_joins, current_rpo_clause):
        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

        if not current_where:
            years = execute_read_query(conn, "SELECT DISTINCT modelYear FROM Vehicles ORDER BY modelYear DESC")
            models = execute_read_query(conn, "SELECT DISTINCT model FROM Vehicles ORDER BY model ASC")
            bodies = execute_read_query(conn, "SELECT DISTINCT body FROM Vehicles ORDER BY body ASC")
            trims = execute_read_query(conn, "SELECT DISTINCT trim FROM Vehicles ORDER BY trim ASC")
            engines = execute_read_query(conn, "SELECT engine_rpo AS rpo, engine_type AS name FROM Engines ORDER BY engine_rpo ASC")
            trans = execute_read_query(conn, "SELECT DISTINCT transmission_type FROM Transmissions ORDER BY transmission_type ASC")
            drivetrains = execute_read_query(conn, "SELECT DISTINCT drivetrain_type FROM Drivetrains ORDER BY drivetrain_type ASC")
            colors = execute_read_query(conn, "SELECT DISTINCT color_name FROM Colors ORDER BY color_name ASC")
            countries = execute_read_query(conn, "SELECT DISTINCT country FROM Orders ORDER BY country ASC")
            close_connection(conn)

            return {
                'modelYear': [r['modelYear'] for r in years],
                'model': [r['model'] for r in models],
                'body': [r['body'] for r in bodies],
                'trim': [r['trim'] for r in trims],
                'transmission_type': [r['transmission_type'] for r in trans],
                'drivetrain_type': [r['drivetrain_type'] for r in drivetrains],
                'color_name': [r['color_name'] for r in colors],
                'country': [r['country'] for r in countries]
            }, engines

        else:
            columns = ['modelYear', 'body', 'trim', 'transmission_type', 'drivetrain_type', 'model', 'color_name', 'country']
            
            sqlStatement = f"""
                SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, e.engine_rpo,
                                t.transmission_type, d.drivetrain_type, c.color_name, o.country
                FROM (
                    SELECT v.vehicle_id
                    FROM Vehicles v
                    {current_filter_joins}
                    {current_where}
                    GROUP BY v.vehicle_id
                    {current_rpo_clause}
                ) AS filtered_ids
                JOIN Vehicles v ON v.vehicle_id = filtered_ids.vehicle_id
                JOIN Engines e ON v.engine_id = e.engine_id
                JOIN Transmissions t ON v.transmission_id = t.transmission_id
                JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
                JOIN Colors c ON v.color_id = c.color_id
                JOIN Orders o ON v.order_id = o.order_id
            """
            results = execute_read_query(conn, sqlStatement, current_params)
            close_connection(conn)

            distinct_values = {col: set() for col in columns}
            distinct_engines = set()
            for result in results:
                for col in columns:
                    if result[col] is not None:
                        distinct_values[col].add(result[col])
                if result['engine_type'] is not None:
                    distinct_engines.add((result['engine_rpo'], result['engine_type']))

            sorted_values = {
                'modelYear': sorted(list(distinct_values['modelYear']), reverse=True),
                **{col: sorted(list(distinct_values[col])) for col in columns if col != 'modelYear'}
            }
            sorted_engines = [
                {'rpo': rpo, 'name': name}
                for rpo, name in sorted(list(distinct_engines), key=lambda x: x[0] or "")
            ]
            return sorted_values, sorted_engines

    distinct_values, engine_list = get_all_distinct_values(where_clause, params, filter_join_clause, rpo_clause)

    year_list = distinct_values['modelYear']
    body_list = distinct_values['body']
    trim_list = distinct_values['trim']
    trans_list = distinct_values['transmission_type']
    drivetrain_list = distinct_values['drivetrain_type']
    model_list = distinct_values['model']
    color_list = distinct_values['color_name']
    country_list = distinct_values['country']

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    
    inner_sql = f"""
        SELECT v.vehicle_id
        FROM Vehicles v {filter_join_clause}
        {where_clause}
        GROUP BY v.vehicle_id
        {rpo_clause}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    select = f"""
        SELECT v.vehicle_id, v.vin, v.modelYear, v.model, v.body, v.trim,
            e.engine_type, t.transmission_type, d.drivetrain_type,
            c.color_name, v.msrp, o.country,
            GROUP_CONCAT(DISTINCT se.special_desc ORDER BY se.special_desc ASC SEPARATOR ', ') AS special_desc
        FROM (
            {inner_sql}
        ) AS page_keys
        JOIN Vehicles v ON v.vehicle_id = page_keys.vehicle_id
        JOIN Engines e ON v.engine_id = e.engine_id
        JOIN Transmissions t ON v.transmission_id = t.transmission_id
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        JOIN Colors c ON v.color_id = c.color_id
        JOIN Orders o ON v.order_id = o.order_id
        LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        GROUP BY v.vehicle_id, v.vin, v.modelYear, v.model, v.body, v.trim,
                 e.engine_type, t.transmission_type, d.drivetrain_type,
                 c.color_name, v.msrp, o.country
        {order_clause}
    """
    
    query_params = params + [limit, offset]
    viewTable = execute_read_query(conn, select, query_params)

    if where_clause:
        totalSql = f"""
            SELECT COUNT(*) AS total FROM (
                SELECT v.vehicle_id 
                FROM Vehicles v {filter_join_clause}
                {where_clause}
                GROUP BY v.vehicle_id {rpo_clause}
            ) AS filtered_vehicles
        """
        total_items = execute_read_query(conn, totalSql, params)[0]['total']
    else:
        total_items = execute_read_query(conn, "SELECT COUNT(vehicle_id) AS total FROM Vehicles")[0]['total']

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
        'drivetrain': drivetrain_list,
        'color': color_list,
        'country': country_list,
        'limit': limit
    })

@app.route('/calendar-activity', methods=['GET'])
def calendar_activity():
    year = request.args.get('year')
    model_filter = request.args.get('model')
    category = request.args.get('category', 'daily')
    
    if category != 'yearly' and not year:
        return jsonify({'error': 'Year required'}), 400

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    
    params = []
    model_join = ""
    model_cond = ""
    
    if model_filter:
        model_join = "JOIN Vehicles v ON o.order_id = v.order_id"
        if model_filter == 'CORVETTE (C8)':
            model_cond = "AND v.model LIKE %s AND v.modelYear >= '2020'"
            params.append('CORVETTE%')
        else:
            model_cond = "AND v.model = %s"
            params.append(model_filter)
            
    if category == 'yearly':
        sqlStatement = f"""
            SELECT CAST(YEAR(o.creation_date) AS CHAR) as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE o.creation_date IS NOT NULL {model_cond}
            GROUP BY prod_date
        """
    elif category == 'monthly':
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m') as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE YEAR(o.creation_date) = %s {model_cond} AND o.creation_date IS NOT NULL
            GROUP BY prod_date
        """
        params.insert(0, year)
    else:
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m-%%d') as prod_date, COUNT(o.order_id) as count
            FROM Orders o
            {model_join}
            WHERE YEAR(o.creation_date) = %s {model_cond} AND o.creation_date IS NOT NULL
            GROUP BY prod_date
        """
        params.insert(0, year)
    
    rows = execute_read_query(conn, sqlStatement, params)
    close_connection(conn)
    
    activity_map = {r['prod_date']: r['count'] for r in rows} if rows else {}
    return jsonify(activity_map)

@app.route('/daily-stats', methods=['GET'])
def daily_stats():
    model_filter = request.args.get('model')
    date_filter = request.args.get('date')
    category = request.args.get('category', 'daily')
    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    
    from datetime import date
    
    bounds_params = []
    if model_filter:
        if model_filter == 'CORVETTE (C8)':
            bounds_sql = "SELECT DATE_FORMAT(MIN(o.creation_date), '%%Y-%%m-%%d') as min_date, DATE_FORMAT(MAX(o.creation_date), '%%Y-%%m-%%d') as max_date FROM Orders o JOIN Vehicles v ON o.order_id = v.order_id WHERE v.model LIKE %s AND v.modelYear >= '2020' AND o.creation_date IS NOT NULL"
            bounds_params.append('CORVETTE%')
        else:
            bounds_sql = "SELECT DATE_FORMAT(MIN(o.creation_date), '%%Y-%%m-%%d') as min_date, DATE_FORMAT(MAX(o.creation_date), '%%Y-%%m-%%d') as max_date FROM Orders o JOIN Vehicles v ON o.order_id = v.order_id WHERE v.model = %s AND o.creation_date IS NOT NULL"
            bounds_params.append(model_filter)
    else:
        bounds_sql = "SELECT DATE_FORMAT(MIN(creation_date), '%Y-%m-%d') as min_date, DATE_FORMAT(MAX(creation_date), '%Y-%m-%d') as max_date FROM Orders WHERE creation_date IS NOT NULL"
        bounds_params = None
    
    bounds_rows = execute_read_query(conn, bounds_sql, bounds_params)
    min_date = bounds_rows[0]['min_date'] if bounds_rows else None
    max_date = bounds_rows[0]['max_date'] if bounds_rows else None

    curr_date_str = date_filter or max_date or date.today().strftime('%Y-%m-%d')
    
    if category == 'monthly':
        date_condition = "DATE_FORMAT(o.creation_date, '%%Y-%%m') = %s"
        base_params = [curr_date_str[:7]] 
    elif category == 'yearly':
        date_condition = "YEAR(o.creation_date) = %s"
        base_params = [curr_date_str[:4]] 
    else:
        date_condition = "DATE(o.creation_date) = %s"
        base_params = [curr_date_str]

    models_sql = f"""
        SELECT DISTINCT v.model 
        FROM Vehicles v 
        JOIN Orders o ON v.order_id = o.order_id 
        WHERE {date_condition} AND v.model IS NOT NULL 
        ORDER BY v.model ASC
    """
    model_rows = execute_read_query(conn, models_sql, base_params)
    available_models = [r['model'] for r in model_rows] if model_rows else []

    sqlStatement = f"""
        SELECT v.modelYear, v.model, v.body, v.trim, e.engine_type, e.engine_rpo,
               t.transmission_type, d.drivetrain_type, c.color_name, c.rpo_code,
               GROUP_CONCAT(DISTINCT se.special_desc SEPARATOR ', ') AS special_desc
        FROM Vehicles v
        JOIN Orders o ON v.order_id = o.order_id
        LEFT JOIN Engines e ON v.engine_id = e.engine_id
        LEFT JOIN Transmissions t ON v.transmission_id = t.transmission_id
        LEFT JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
        LEFT JOIN Colors c ON v.color_id = c.color_id
        LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id
        WHERE {date_condition}
    """
    
    params = list(base_params)

    if model_filter:
        if model_filter == 'CORVETTE (C8)':
            sqlStatement += " AND v.model LIKE %s AND v.modelYear >= '2020'"
            params.append('CORVETTE%')
        else:
            sqlStatement += " AND v.model = %s"
            params.append(model_filter)
        
    sqlStatement += """
        GROUP BY v.vehicle_id, v.modelYear, v.model, v.body, v.trim, 
                 e.engine_type, e.engine_rpo, t.transmission_type, d.drivetrain_type, c.color_name, c.rpo_code
    """
    
    if params:
        rows = execute_read_query(conn, sqlStatement, params)
    else:
        rows = execute_read_query(conn, sqlStatement)
        
    close_connection(conn)

    stats = {
        'total': len(rows) if rows else 0,
        'current_date': curr_date_str,
        'min_date': min_date,
        'max_date': max_date,
        'available_models': available_models,
        'modelYear': {}, 'model': {}, 'body': {}, 'trim': {},
        'engine': {}, 'trans': {}, 'drivetrain': {}, 'color': {}, 'specialedition': {}
    }

    if rows:
        for r in rows:
            my = str(r['modelYear']) if r['modelYear'] else 'Unknown'
            mod = r['model'] or 'Unknown'
            bdy = r['body'] or 'Unknown'
            trm = r['trim'] or 'Unknown'
            
            eng_type = r['engine_type'] or 'Unknown'
            eng_rpo = r['engine_rpo']
            eng = f"{eng_rpo} - {eng_type}" if eng_rpo and eng_rpo != 'N/A' else eng_type
            
            clr_name = r['color_name'] or 'Unknown'
            clr_rpo = r['rpo_code']
            clr = f"{clr_rpo} - {clr_name}" if clr_rpo and clr_rpo != 'N/A' else clr_name

            trn = r['transmission_type'] or 'Unknown'
            drv = r['drivetrain_type'] or 'Unknown'

            stats['modelYear'][my] = stats['modelYear'].get(my, 0) + 1
            stats['model'][mod] = stats['model'].get(mod, 0) + 1
            stats['body'][bdy] = stats['body'].get(bdy, 0) + 1
            stats['trim'][trm] = stats['trim'].get(trm, 0) + 1
            stats['engine'][eng] = stats['engine'].get(eng, 0) + 1
            stats['trans'][trn] = stats['trans'].get(trn, 0) + 1
            stats['drivetrain'][drv] = stats['drivetrain'].get(drv, 0) + 1
            stats['color'][clr] = stats['color'].get(clr, 0) + 1
            
            if r['special_desc']:
                for sp in r['special_desc'].split(', '):
                    stats['specialedition'][sp] = stats['specialedition'].get(sp, 0) + 1

    for key in stats:
        if key not in ['total', 'current_date', 'min_date', 'max_date', 'available_models']:
            stats[key] = dict(sorted(stats[key].items(), key=lambda item: item[1], reverse=True))

    return jsonify(stats)

@app.route('/stats', methods=['GET'])
def stats():
    category = request.args.get('category', '').strip() or None
    year = request.args.get('year', '').strip() or None
    model = request.args.get('model', '').strip() or None
    body = request.args.get('body', '').strip() or None
    trim = request.args.get('trim', '').strip() or None
    engine = request.args.get('engine', '').strip() or None
    trans = request.args.get('trans', '').strip() or None
    drivetrain = request.args.get('drivetrain', '').strip() or None
    conditions = []
    year_cond = None
    params = []

    if model == "CORVETTE (C8)" and year and int(year) < 2020:
        year = None
        target_year = "2026"
    else:
        target_year = year if year else "2026"

    if year:
        year_cond = "v.modelYear = %s"
        conditions.append(year_cond)
        params.append(year)

    if model:
        if model == "CORVETTE (C8)":
            conditions.append("v.model LIKE 'CORVETTE%'")
            conditions.append("v.modelYear >= '2020'")
        else:
            conditions.append("v.model = %s")
            params.append(model)

    if body: conditions.append("v.body = %s"); params.append(body)
    if trim: conditions.append("v.trim = %s"); params.append(trim)
    if engine: conditions.append("e.engine_type = %s"); params.append(engine)
    if trans: conditions.append("t.transmission_type = %s"); params.append(trans)
    if drivetrain: conditions.append("d.drivetrain_type = %s"); params.append(drivetrain)
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    join_clause = """
        JOIN Colors c ON v.color_id = c.color_id
        JOIN Engines e ON v.engine_id = e.engine_id
        JOIN Transmissions t ON v.transmission_id = t.transmission_id
        JOIN Drivetrains d ON v.drivetrain_id = d.drivetrain_id
    """

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

    if category == 'color':
        sqlStatement = f"""
            WITH ColorCounts AS (
                SELECT
                    CASE
                        WHEN c.color_name = 'BLADE SILVER METALLIC' AND v.modelYear >= '2026' THEN 'GKA'
                        WHEN c.rpo_code = 'N/A' THEN c.color_name
                        ELSE c.rpo_code
                    END AS rpo_code,
                    COUNT(*) AS total_count,
                    GROUP_CONCAT(DISTINCT c.color_name ORDER BY c.color_name SEPARATOR ', ') AS color_names
                FROM Vehicles v
                {join_clause}
                {where_clause}
                GROUP BY 1
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    rpo_code AS label,
                    rpo_code,
                    total_count,
                    color_names,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM ColorCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'engine':
        sqlStatement = f"""
            WITH EngineCounts AS (
                SELECT
                    e.engine_rpo,
                    e.engine_type,
                    COUNT(*) AS total_count
                FROM Vehicles v
                {join_clause}
                {where_clause}
                GROUP BY e.engine_rpo, e.engine_type
            ),
            Ranked AS (
                SELECT
                    DENSE_RANK() OVER (ORDER BY total_count DESC) AS `rank`,
                    CONCAT(IFNULL(engine_rpo, ''), IF(engine_rpo IS NOT NULL, ' - ', ''), engine_type) AS label,
                    IFNULL(engine_rpo, '') AS engine_rpo,
                    engine_type,
                    total_count,
                    ROUND(100.0 * total_count / SUM(total_count) OVER (), 5) AS percent
                FROM EngineCounts
            )
            SELECT * FROM Ranked;
        """
    elif category == 'production':
        prod_conditions = conditions.copy()
        prod_params = params.copy()
        if not any("v.modelYear" in c for c in prod_conditions):
            prod_conditions.append("v.modelYear = %s")
            prod_params.append(target_year)

        full_where = f"WHERE {' AND '.join(prod_conditions)}"
        sqlStatement = f"""
            SELECT DATE_FORMAT(o.creation_date, '%%Y-%%m-%%d') AS label, COUNT(*) AS total_count
            FROM Vehicles v
            JOIN Orders o ON v.order_id = o.order_id
            {full_where}
            GROUP BY label ORDER BY label ASC;
        """
    else:
        close_connection(conn)
        return jsonify([])

    distinct_sql = f"SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, d.drivetrain_type FROM Vehicles v {join_clause} {where_clause}"
    distinct_results = execute_read_query(conn, distinct_sql, params)

    if category == 'production':
        viewTable = execute_read_query(conn, sqlStatement, prod_params)
    elif category:
        viewTable = execute_read_query(conn, sqlStatement, params)
    else:
        viewTable = []

    year_agnostic_conds = [c for c in conditions if c != year_cond]
    
    year_agnostic_params = []
    if model and model != "CORVETTE (C8)": year_agnostic_params.append(model)
    if body: year_agnostic_params.append(body)
    if trim: year_agnostic_params.append(trim)
    if engine: year_agnostic_params.append(engine)
    if trans: year_agnostic_params.append(trans)
    if drivetrain: year_agnostic_params.append(drivetrain)

    year_where = f"WHERE {' AND '.join(year_agnostic_conds)}" if year_agnostic_conds else ""

    year_sql = f"SELECT DISTINCT v.modelYear FROM Vehicles v {join_clause} {year_where} ORDER BY v.modelYear DESC"
    all_years_raw = execute_read_query(conn, year_sql, year_agnostic_params)
    all_years = [r['modelYear'] for r in all_years_raw if r.get('modelYear')]

    distinct_sql = f"""
        SELECT DISTINCT v.model, v.body, v.trim, e.engine_type, t.transmission_type, d.drivetrain_type
        FROM Vehicles v
        {join_clause}
        {where_clause}
    """
    distinct_results = execute_read_query(conn, distinct_sql, params)

    close_connection(conn)

    if model == "CORVETTE (C8)":
        all_years = [y for y in all_years if y and int(y) >= 2020]

    return jsonify({
        'stats_data': viewTable,
        'year': all_years,
        'selectedYear': target_year,
        'model': sorted(set(r['model'] for r in distinct_results if r.get('model'))),
        'body': sorted(set(r['body'] for r in distinct_results if r.get('body'))),
        'trim': sorted(set(r['trim'] for r in distinct_results if r.get('trim'))),
        'engine': sorted(set(r['engine_type'] for r in distinct_results if r.get('engine_type'))),
        'trans': sorted(set(r['transmission_type'] for r in distinct_results if r.get('transmission_type'))),
        'drivetrain': sorted(set(r['drivetrain_type'] for r in distinct_results if r.get('drivetrain_type'))),
        'category': category
    })

@app.route('/wheels', methods=['GET'])
def wheel_stats():
    model = request.args.get('model', '').strip() or None

    conditions = []
    params = []
    if model:
        if model == "CORVETTE (ALL)":
            corvette_models = ["CORVETTE STINGRAY", "CORVETTE STINGRAY W/ Z51", "CORVETTE GRAND SPORT", "CORVETTE E-RAY", "CORVETTE Z06", "CORVETTE ZR1", "CORVETTE ZR1X"]
            corvette_list = ", ".join(['%s'] * len(corvette_models))
            conditions.append(f"model IN ({corvette_list})")
            params.extend(corvette_models)
        else:
            conditions.append("model = %s")
            params.append(model)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    distinct_sql = f"""
        SELECT DISTINCT model
        FROM Vehicles
        {where_clause}
    """

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    distinct_results = execute_read_query(conn, distinct_sql, params)
    model_list = sorted(set(r['model'] for r in distinct_results if r['model']))

    close_connection(conn)

    return jsonify({
        'model': model_list,
    })

@app.route('/about', methods=['GET'])
def about_stats():
    distinct_sql = """
        SELECT
            CASE
                WHEN v.model LIKE 'CORVETTE%' THEN 'CORVETTE'
                WHEN v.model LIKE 'HUMMER EV%' THEN 'HUMMER EV'
                ELSE v.model
            END AS model_group,
            DATE_FORMAT(MAX(o.creation_date), '%M %e, %Y') AS latest_date
        FROM Vehicles v
        JOIN Orders o ON v.order_id = o.order_id
        GROUP BY model_group
    """

    conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
    results = execute_read_query(conn, distinct_sql)
    close_connection(conn)

    stats_map = {r['model_group'].replace(' ', '_'): r['latest_date'] for r in results}
    return jsonify(stats_map)

#========================= View Pages #=========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
