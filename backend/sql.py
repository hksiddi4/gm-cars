import mysql.connector
from mysql.connector import Error

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            password = user_password,
            database = db_name
        )
        print("Connection to MySQL db successful!")
    except Error as e:
        print(f"Unsuccessful DB Connection, the error: {e} occured.")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully.")
    except Error as e:
        print(f"The error {e} occured.")

def execute_read_query(connection, query):
    # dictionary=True (returns info from sql query and puts into dictionary)
    cursor = connection.cursor(dictionary=True)
    result = None
    try:
        # Deliver query to database
        cursor.execute(query)
        # Return result from query
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error {e} occured.")
