from mysql.connector.pooling import MySQLConnectionPool
from contextlib import contextmanager
import logging

class DatabasePool:
    _instance = None
    _pool = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabasePool, cls).__new__(cls)
        return cls._instance

    def __init__(self, pool_config=None):
        if self._pool is None and pool_config is not None:
            try:
                self._pool = MySQLConnectionPool(**pool_config)
            except Exception as e:
                logging.error(f"Failed to create connection pool: {e}")
                raise

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._pool.get_connection()
            yield conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            raise
        finally:
            if conn is not None:
                conn.close()

    @contextmanager
    def get_cursor(self, dictionary=True):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()

def init_pool(host, user, password, database):
    pool_config = {
        "pool_name": "mypool",
        "pool_size": 5,
        "host": host,
        "user": user,
        "password": password,
        "database": database,
        "connect_timeout": 10,
        "use_pure": True
    }
    return DatabasePool(pool_config)

def execute_read_query(cursor, query, params=None):
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Exception as e:
        logging.error(f"Query execution error: {e}\nQuery: {query}\nParams: {params}")
        raise

def execute_write_query(cursor, query, params=None):
    try:
        cursor.execute(query, params or ())
        cursor.connection.commit()
        return cursor.lastrowid
    except Exception as e:
        cursor.connection.rollback()
        logging.error(f"Query execution error: {e}\nQuery: {query}\nParams: {params}")
        raise