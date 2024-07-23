# Before first run do:
# pip install mysql.connector
# pip install npm
# npm install flask
# Run by:
# python start.py

import sql
import flask
from flask import request, jsonify
from flask_cors import CORS
from sql import create_connection, execute_read_query, Creds
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True
CORS(app)

# Create connection to MySQL database
myCreds = sql.Creds()
conn = create_connection(myCreds.conString, myCreds.userName, myCreds.password, myCreds.dbName)

# ========================= View Pages =========================
# Random 25 view
@app.route('/rand', methods=['GET'])
def all_inv():
    sqlStatement = f"SELECT * FROM gm ORDER BY RAND() LIMIT 25"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

@app.route('/search', methods=['GET'])
def search_inv():
    vin = request.args.get('vin')
    sqlStatement = f"SELECT * FROM gm WHERE VIN = '{vin}'"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)
    
@app.route('/api/test', methods=['POST'])
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

@app.route('/msrp', methods=['GET'])
def sort_price():
    models = request.args.get('model')
    rpo = request.args.get('rpo')
    color = request.args.get('color')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    offset = (page - 1) * limit

    conditions = []

    if models:
        models = [model.strip() for model in models.split(',')]
        models = "', '".join(models)
        conditions.append(f"model IN ('{models}')")

    if rpo:
        conditions.append(f"JSON_CONTAINS(allJson->'$.Options', '\"{rpo}\"')")

    if color:
        conditions.append(f"exterior_color = '{color}'")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    count_query = f"SELECT COUNT(*) AS total FROM gm{where_clause}"
    total_items_result = execute_read_query(conn, count_query)
    total_items = total_items_result[0]['total']

    select_query = f"SELECT * FROM gm{where_clause} ORDER BY msrp DESC LIMIT {limit} OFFSET {offset}"
    viewTable = execute_read_query(conn, select_query)

    return jsonify({'data': viewTable, 'total': total_items})

@app.route('/api/colors', methods=['GET'])
def get_colorss():
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

@app.route('/api/trims', methods=['GET'])
def get_trims():
    sqlStatement = "SELECT DISTINCT trim FROM gm WHERE model = 'CAMARO' ORDER BY trim"
    trims = execute_read_query(conn, sqlStatement)
    trim_list = [trim['trim'] for trim in trims]
    return jsonify(trim_list)

@app.route('/panther350', methods=['GET'])
def panther():
    sqlStatement = "SELECT * FROM gm WHERE trim = 'ZL1' AND exterior_color = 'PANTHER BLACK MATTE' ORDER BY SUBSTRING(vin, -6)"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

@app.route('/garage56', methods=['GET'])
def garage():
    sqlStatement = "SELECT * FROM gm WHERE trim = 'ZL1' AND exterior_color = 'RIPTIDE BLUE METALLIC' AND JSON_CONTAINS(allJson->'$.Options', '[\"X56\"]') ORDER BY SUBSTRING(vin, -6)"    
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

@app.route('/blackwing', methods=['GET'])
def allblackwing():
    sqlStatement = "SELECT * FROM gm WHERE trim = 'V-SERIES BLACKWING' ORDER BY SUBSTRING(vin, -6) LIMIT 100"    
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

# ========================= View Pages =========================

app.run()
