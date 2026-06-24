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
AI_MODEL = "qwen2.5-coder:14b"

DB_SCHEMA_CONTEXT = """
You are a MySQL expert database assistant. Generate ONLY a valid MySQL statement. No Markdown wrapper, no markdown blocks, no triple backticks, and no explanations.

Here is the exact database schema based on the actual table structures:

CREATE TABLE Colors (color_id BIGINT, color_name VARCHAR(64), rpo_code VARCHAR(3));
CREATE TABLE Dealers (dealer_id BIGINT, dealer_name VARCHAR(128), dealer_address VARCHAR(256), dealer_code VARCHAR(16));
CREATE TABLE Drivetrains (drivetrain_id BIGINT, drivetrain_type VARCHAR(8));
CREATE TABLE Engines (engine_id BIGINT, engine_type VARCHAR(64), engine_rpo VARCHAR(3));
CREATE TABLE MMC_Codes (mmc_id BIGINT, mmc_code VARCHAR(16));
CREATE TABLE Options (option_id BIGINT, vehicle_id BIGINT, option_code CHAR(3));
CREATE TABLE Orders (order_id BIGINT, order_number VARCHAR(6), creation_date DATE, dealer_id BIGINT, allocation_id BIGINT, country VARCHAR(32));
CREATE TABLE SpecialEditions (special_id BIGINT, vehicle_id BIGINT, special_desc VARCHAR(64));
CREATE TABLE Transmissions (transmission_id BIGINT, transmission_type VARCHAR(16));
CREATE TABLE Vehicles (vehicle_id BIGINT, vin VARCHAR(17), modelYear INT, model VARCHAR(32), body VARCHAR(32), trim VARCHAR(32), engine_id BIGINT, transmission_id BIGINT, drivetrain_id BIGINT, color_id BIGINT, msrp INT, mmc_id BIGINT, order_id BIGINT);

Join Relationships:
- v.color_id = c.color_id
- v.engine_id = e.engine_id
- v.transmission_id = t.transmission_id
- v.drivetrain_id = d.drivetrain_id
- v.mmc_id = m.mmc_id
- v.order_id = o.order_id
- o.dealer_id = dealer.dealer_id
- opt.vehicle_id = v.vehicle_id
- se.vehicle_id = v.vehicle_id

Rules:
1. Only output SELECT queries.
2. Use standard table aliases (e.g., Vehicles v, Colors c, Transmissions t, Engines e, Drivetrains d, Orders o, Options opt, Dealers dealer, MMC_Codes m, SpecialEditions se).
3. MANDATORY COLUMN SELECTION AND ORDER: If returning vehicle records, you MUST select EXACTLY the following 12 columns in this exact sequence. Do NOT add, omit, or rearrange any columns:
   SELECT v.vin AS VIN, v.modelYear AS Year, v.model AS Model, v.body AS Body, v.trim AS Trim, e.engine_type AS Engine, t.transmission_type AS Trans, d.drivetrain_type AS Drivetrain, c.color_name AS Exterior_Color, v.msrp AS MSRP, IFNULL(GROUP_CONCAT(DISTINCT se.special_desc), '') AS Package_Option, o.country AS Country
4. MANDATORY JOINS: Because the mandatory SELECT statement requires data from Orders and SpecialEditions, you MUST ALWAYS include both `JOIN Orders o ON v.order_id = o.order_id` and `LEFT JOIN SpecialEditions se ON v.vehicle_id = se.vehicle_id` in your query when returning vehicle records.
5. Because of the GROUP_CONCAT, if you are returning vehicle records, you MUST include "GROUP BY v.vehicle_id" before the limit.
6. ALWAYS append LIMIT 100 to the end of the query unless the user is asking for an aggregate function (COUNT, SUM, AVG).
7. CRITICAL DATA MAPPING FOR WHERE CLAUSES:
   - Transmission types are stored as codes. "Automatic" means t.transmission_type LIKE 'A%' (e.g., A10, A8, DCT8). "Manual" means t.transmission_type LIKE 'M%' (e.g., M6, M7).
   - Drivetrains are stored as short codes: 'RWD', 'AWD', '4WD'.
8. STRICT ANTI-HALLUCINATION: Do NOT add WHERE conditions for transmission, drivetrain, year, or any other attribute UNLESS the user explicitly requests them in the prompt.
9. COLOR MATCHING: Database color names are highly specific (e.g., 'SEBRING ORANGE TINTCOAT'). When a user asks for a generic color like 'Orange', 'Red', or 'Black', you MUST use a wildcard search (e.g., c.color_name LIKE '%ORANGE%') instead of an exact match.
10. DECONSTRUCTING COMPOUND NAMES: Users combine attributes into one phrase (e.g., "Camaro 2SS 1LE"). You MUST explicitly separate them AND you MUST include all requested parts in the WHERE clause. NEVER combine a trim and a special edition into the same string, and NEVER silently drop the special edition from the query.
    - INCORRECT: `WHERE v.trim = '1LE 2SS'` (Combines them)
    - INCORRECT: `WHERE v.trim = '2SS'` (Drops the 1LE condition entirely)
    - CORRECT: `WHERE v.model = 'CAMARO' AND v.trim = '2SS' AND se.special_desc LIKE '%1LE%'`
    'Camaro' is the model. '1LT', '2SS', '3LZ', 'ZL1' are trims. Identifiers like '1LE', 'Launch Edition', 'Collector Edition' belong EXCLUSIVELY in the SpecialEditions table (`se.special_desc LIKE '%1LE%'`).
11. FUZZY PACKAGE MATCHING: Database special edition descriptions contain full marketing names (e.g., 'ZTK Track Performance Package'). If a user asks for a multi-word package like 'Track Package', you MUST place wildcards between the keywords (e.g., `se.special_desc LIKE '%Track%Package%'`) to allow for words in the middle, or search for the single most unique keyword (e.g., `se.special_desc LIKE '%Track%'`). NEVER use exact adjacent wildcards like `'%Track Package%'`.
12. CORVETTE MODEL NAME: All Corvette models are 'CORVETTE XXX'. If a user asks for corvette without specifing model ('STINGRAY', 'E-RAY', 'GRAND SPORT', 'GRAND SPORT X', 'Z06', 'ZR1', 'ZR1X'), use wildcards after Corvette (`'CORVETTE%'`).
    - INCORRECT: `WHERE v.model LIKE 'CORVETTE%' AND v.trim = 'ZR1'` (Treats model as trim)
    - CORRECT: `WHERE v.model LIKE 'CORVETTE ZR1`
"""

# ========================= AI NL-to-SQL Route =========================

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
        "options": {
            "temperature": 0.1
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
            return jsonify({'error': 'AI generated invalid SQL syntax or execution failed.', 'generated_sql': generated_sql}), 400
            
    except Exception as e:
        close_connection(conn)
        return jsonify({'error': 'Execution error', 'generated_sql': generated_sql, 'details': str(e)}), 400
    
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

    # Aggregate results
    vehicle = {}
    rpo_codes = []
    special_descs = []

    for row in rows:
        if not vehicle:  # fill in once
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
    order = request.args.get('order')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    
    try:
        page = int(page)
        limit = int(limit)
        offset = (page - 1) * limit
    except (ValueError, TypeError):
        page = 1
        limit = 100
        offset = 0

    rpo_list = []
    rpo_list_for_filtering = []
    conditions = []
    params = []

    # 1. BASE FILTER JOINS (SpecialEditions intentionally excluded for performance)
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

    # 2. RPO HANDLING
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
            # F1 Collector "": ["v.modelYear = '2026'", "v.model = 'CT5'", "v.trim = 'V-SERIES BLACKWING'", "c.color_name = 'MIDNIGHT STONE FROST'", "opt.option_code = 'V8V'"],
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
            'PCK1': 'PCK'
        }

        for code in rpo_list:
            if code in substitution_map:
                rpo_list_for_filtering.append(substitution_map[code])
            elif code not in ['H40', 'ZLT']:
                rpo_list_for_filtering.append(code)

        rpo_list_for_filtering = list(set(rpo_list_for_filtering))
        rpo_n = len(rpo_list_for_filtering)

        if len(rpo_list_for_filtering) > 1:
            rpo_placeholders = "', '".join(rpo_list_for_filtering)
            conditions.append(f"opt.option_code IN ('{rpo_placeholders}')")
        elif len(rpo_list_for_filtering) == 1:
            conditions.append(f"opt.option_code = '{rpo_list_for_filtering[0]}'")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    if not rpo_list_for_filtering or 'H40' in rpo_list:
        rpo_clause = ""
    else:
        rpo_clause = f"HAVING COUNT(DISTINCT opt.option_code) = {rpo_n}"

    # 3. ORDERING
    if any(code in ["ZL4B", "X56", "PEH"] for code in rpo_list) and order not in ["ASC", "DESC"]:
        order_clause = "ORDER BY SUBSTRING(v.vin, -6)"
    elif order in ["ASC", "DESC"]:
        order_clause = f"ORDER BY v.msrp {'ASC' if order == 'ASC' else 'DESC'}"
    elif order in ["vinASC", "vinDESC"]:
        order_clause = f"ORDER BY SUBSTRING(v.vin, -6) {'DESC' if order == 'vinDESC' else 'ASC'}, v.modelYear ASC"
    else:
        order_clause = "ORDER BY v.vehicle_id DESC"

    # 4. DROPDOWN GENERATOR (Optimized)
    def get_all_distinct_values(current_where, current_params, current_filter_joins, current_rpo_clause):
        conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

        if not current_where:
            # Fastest path for default page load
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
            # Optimized deferred join approach for fetching valid dropdowns on filtered views
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

    # 5. FETCH DATA
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
    
    # Inner subquery specifically to grab the paginated IDs rapidly
    inner_sql = f"""
        SELECT v.vehicle_id
        FROM Vehicles v {filter_join_clause}
        {where_clause}
        GROUP BY v.vehicle_id
        {rpo_clause}
        {order_clause}
        LIMIT %s OFFSET %s
    """

    # Outer query to fetch the wide dataset and attach Special Editions purely for those 100 rows
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

    # 6. TOTAL COUNT CALCULATION
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
        'country': country_list
    })

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

    # 4. EXECUTE AND FILTER RESULTS
    distinct_sql = f"SELECT DISTINCT v.modelYear, v.model, v.body, v.trim, e.engine_type, t.transmission_type, d.drivetrain_type FROM Vehicles v {join_clause} {where_clause}"
    distinct_results = execute_read_query(conn, distinct_sql, params)

    # Get all available years for the dropdown
    all_years_raw = execute_read_query(conn, "SELECT DISTINCT modelYear FROM Vehicles ORDER BY modelYear DESC")
    all_years = [r['modelYear'] for r in all_years_raw if r.get('modelYear')]

    # --- FILTER THE DROPDOWN LIST ---
    if model == "CORVETTE (C8)":
    # Ensure y is treated as an int for the comparison
        all_years = [y for y in all_years if y is not None and int(y) >= 2020]

    if category == 'production':
        viewTable = execute_read_query(conn, sqlStatement, prod_params)
    elif category:
        viewTable = execute_read_query(conn, sqlStatement, params)
    else:
        viewTable = []

    # 3. DYNAMIC DROPDOWN LOGIC (Like the /vehicles page)
    # Fetch years agnostic of the current year selection
    year_agnostic_conds = [c for c in conditions if c != year_cond]
    
    # Reconstruct params without the year param
    year_agnostic_params = []
    if model and model != "CORVETTE (C8)": year_agnostic_params.append(model)
    if body: year_agnostic_params.append(body)
    if trim: year_agnostic_params.append(trim)
    if engine: year_agnostic_params.append(engine)
    if trans: year_agnostic_params.append(trans)
    if drivetrain: year_agnostic_params.append(drivetrain)

    year_where = f"WHERE {' AND '.join(year_agnostic_conds)}" if year_agnostic_conds else ""

    # Query for the Year dropdown
    year_sql = f"SELECT DISTINCT v.modelYear FROM Vehicles v {join_clause} {year_where} ORDER BY v.modelYear DESC"
    all_years_raw = execute_read_query(conn, year_sql, year_agnostic_params)
    all_years = [r['modelYear'] for r in all_years_raw if r.get('modelYear')]

    # Query for all other dropdowns based on FULL filters
    distinct_sql = f"""
        SELECT DISTINCT v.model, v.body, v.trim, e.engine_type, t.transmission_type, d.drivetrain_type
        FROM Vehicles v
        {join_clause}
        {where_clause}
    """
    distinct_results = execute_read_query(conn, distinct_sql, params)

    close_connection(conn)

    # Final logic for the CORVETTE (C8) year restriction
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

# Replace with better implementation
# @app.route('/api/rarity', methods=['POST'])
# def unique():
#     data = request.json
#     options = data.get('Options')

#     if options is not None:
#         formatted_options = json.dumps(options)
#         try:
#             sqlStatement = f"SELECT COUNT(*) AS Count FROM gm WHERE JSON_UNQUOTE(JSON_EXTRACT(allJson, '$.Options')) = '{formatted_options}'"
#             conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)
#             response = execute_read_query(conn, sqlStatement)
#             close_connection(conn)
#             return response
#         except ValueError:
#             return jsonify({'error': 'Invalid value'}), 400
#     else:
#         return jsonify({'error': 'No value provided'}), 400

#========================= View Pages #=========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
