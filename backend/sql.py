import os
import time
from collections import deque
import pymysql
from pymysql import MySQLError
import pymysql.cursors

QUERY_CACHE = {}
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 5000

_CONN_POOLS = {}
_POOL_MAX_SIZE = 16


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
    pool_key = (host_name, user_name, db_name)
    pool = _CONN_POOLS.get(pool_key)
    while pool:
        conn = pool.pop()
        try:
            if conn.open:
                conn.ping(reconnect=False)
                return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass

    try:
        conn = pymysql.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name,
            connect_timeout=10,
            read_timeout=30,
            write_timeout=30,
            autocommit=True,
        )
        conn._pool_key = pool_key
        return conn
    except MySQLError as e:
        print(f"Unsuccessful DB Connection, the error: {e} occurred.", flush=True)
        return None


def execute_read_query(connection, query, params=None):
    cache_key = get_cache_key(query, params)
    now = time.time()

    cached = QUERY_CACHE.get(cache_key)
    if cached and (now - cached['time'] < CACHE_TTL):
        return cached['result']

    if connection is None:
        return None

    result = None
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()

        if result is not None:
            if len(QUERY_CACHE) >= CACHE_MAX_SIZE:
                # Evict expired entries first, then oldest entry (O(1) dict order)
                expired = [k for k, v in QUERY_CACHE.items() if now - v['time'] >= CACHE_TTL]
                for k in expired:
                    del QUERY_CACHE[k]
                if len(QUERY_CACHE) >= CACHE_MAX_SIZE:
                    QUERY_CACHE.pop(next(iter(QUERY_CACHE)), None)
            QUERY_CACHE[cache_key] = {'time': now, 'result': result}
    except Exception as e:
        print(f"The error {e} occurred.", flush=True)
        # Mark broken connection so close_connection discards instead of pooling it
        try:
            connection.close()
        except Exception:
            pass
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
    return result


def close_connection(connection):
    if not connection:
        return
    pool_key = getattr(connection, '_pool_key', None)
    if pool_key and getattr(connection, 'open', False):
        pool = _CONN_POOLS.setdefault(pool_key, deque())
        if len(pool) < _POOL_MAX_SIZE:
            pool.append(connection)
            return
    try:
        connection.close()
    except Exception:
        pass
