import pymysql
from pymysql import MySQLError
import pymysql.cursors
import os
import time

QUERY_CACHE = {}
CACHE_TTL = 300 # 5 minutes

def get_cache_key(query, params):
    try:
        if isinstance(params, dict):
            return (query, frozenset(params.items()))
        return (query, tuple(params) if isinstance(params, (list, tuple)) else params)
    except TypeError:
        return (query, str(params))

# Create new user in mysql wb, don't use root. Will not work otherwise!
class Creds:
    conString = os.environ.get('DB_HOST')
    userName = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASS')
    dbName = os.environ.get('DB_NAME')

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = pymysql.connect(
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
    except MySQLError as e:
        print(f"Unsuccessful DB Connection, the error: {e} occurred.")
    return connection

def execute_read_query(connection, query, params=None):
    cache_key = get_cache_key(query, params)
    now = time.time()
    
    # Clean up old cache entries periodically to prevent memory leaks
    if len(QUERY_CACHE) > 5000:
        keys_to_delete = [k for k, v in QUERY_CACHE.items() if now - v['time'] > CACHE_TTL]
        for k in keys_to_delete:
            del QUERY_CACHE[k]
        if len(QUERY_CACHE) > 5000: # If still too large, clear it entirely
            QUERY_CACHE.clear()

    if cache_key in QUERY_CACHE:
        if now - QUERY_CACHE[cache_key]['time'] < CACHE_TTL:
            return QUERY_CACHE[cache_key]['result']

    result = None
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        
        # Only cache results if query is successful
        if result is not None:
            QUERY_CACHE[cache_key] = {'time': now, 'result': result}
            
    except MySQLError as e:
        print(f"The error {e} occurred.")
    finally:
        if cursor:
            cursor.close()
    return result

def close_connection(connection):
    if connection:
        connection.close()
