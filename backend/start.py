# Before first run do:
# pip install mysql.connector
# pip install npm
# npm install flask
# Run by:
# python start.py

import parameters
import flask
from flask import request, jsonify
from sql import create_connection, execute_query, execute_read_query

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create connection to MySQL database
myCreds = parameters.Creds()
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

@app.route('/msrp', methods=['GET'])
def sort_price():
    models = request.args.get('model')
    
    # Build the SQL query
    sqlStatement = "SELECT * FROM gm"
    
    if models:
        models_str = "', '".join(models)
        sqlStatement += f" WHERE model IN ('{models_str}')"
    
    sqlStatement += " ORDER BY msrp DESC LIMIT 100"
    
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)
# ========================= View Pages =========================

# ============================ Reports ===========================
# Total $ value from both tables
@app.route('/report/total', methods=['GET'])
def totalPrice():
    # Select calculated total from both locations
    sqlStatement = f"SELECT 'galleria' as tableName, SUM(quantity * price) AS totalValue FROM {galleria} UNION ALL SELECT 'allland' as tableName, SUM(quantity * price) AS total_value FROM {allland}"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

# List values from both tables based on filter
@app.route('/report/category', methods=['GET'])
def categoryReport():
    category = request.args.get("category")
    # Select calculated total from both locations
    sqlStatement = f"SELECT 'Galleria' as tableName, item, category, quantity, price FROM {galleria} WHERE category = '{category}' UNION ALL SELECT 'allland' as tableName, item, category, quantity, price FROM {allland} WHERE category = '{category}'"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

# Low stock report
@app.route('/report/low', methods=['GET'])
def lowStock():
    # Select all stock from both inventory tables under 20
    sqlStatement = f"SELECT 'galleria' as tableName, item, category, quantity, price FROM {galleria} WHERE quantity < 20 UNION ALL SELECT 'allland' as tableName, item, category, quantity, price FROM {allland} WHERE quantity < 20 ORDER BY quantity ASC"
    viewTable = execute_read_query(conn, sqlStatement)
    return jsonify(viewTable)

# ============================ Reports ===========================

app.run()
