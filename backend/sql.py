import mysql.connector
from mysql.connector import Error

class Creds:
    conString = 'vehicles.cbu8q6oeinav.us-east-1.rds.amazonaws.com'
    userName = 'admin'
    password = 'S!dd1qu1'
    dbName = 'vehicles'

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
    except Error as e:
        print(f"Unsuccessful DB Connection, the error: {e} occured.")
    return connection

def execute_read_query(connection, query):
    result = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
    except Error as e:
        print(f"The error {e} occured.")
    finally:
        if cursor:
            cursor.close()
    return result

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()

# def execute_query(connection, query):
#     cursor = connection.cursor()
#     try:
#         cursor.execute(query)
#         connection.commit()
#         print("Query executed successfully.")
#     except Error as e:
#         print(f"The error {e} occured.")
