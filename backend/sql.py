import pymysql
from pymysql import MySQLError
import pymysql.cursors

# Create new user in mysql wb, don't use root. Will not work otherwise!
class Creds:
    conString = '192.168.1.126'
    userName = 'tester'
    password = 'Hussain92'
    dbName = 'vehicles'

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

def execute_read_query(connection, query):
    result = None
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query)
        result = cursor.fetchall()
    except MySQLError as e:
        print(f"The error {e} occurred.")
    finally:
        if cursor:
            cursor.close()
    return result

def close_connection(connection):
    if connection:
        connection.close()

# def execute_query(connection, query):
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         connection.commit()
#         print("Query executed successfully.")
#     except MySQLError as e:
#         print(f"The error {e} occurred.")
