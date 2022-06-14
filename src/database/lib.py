from os import getenv
from threading import Lock
from typing import Optional, Dict, List

from flask import g
from psycopg2 import pool
from psycopg2.extensions import cursor
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

pool: Optional[ThreadedConnectionPool] = None  # noqa F811
connection_lock = Lock()


def init_database():
    global pool
    try:
        pool = ThreadedConnectionPool(
            1,
            2000,
            host=getenv('PGHOST'),
            dbname=getenv('PGDATABASE'),
            user=getenv('PGUSER'),
            password=getenv('PGPASSWORD'),
            port=getenv('PGPORT', '5432'),
            cursor_factory=RealDictCursor
        )
    except Exception as error:
        print("Failed to connect to the database: ", error)
    return pool


def get_pool():
    return pool


def get_cursor() -> cursor:
    if 'cursor' not in g:
        g.connection = pool.getconn()
        g.cursor = g.connection.cursor()
    return g.cursor


def query_one(query: str, query_args: Dict) -> Optional[Dict]:
    cursor = get_cursor()
    cursor.execute(query, query_args)
    result = cursor.fetchone()

    return result


def query_all(query: str, query_args: Dict) -> List[Dict]:
    cursor = get_cursor()
    cursor.execute(query, query_args)
    result = cursor.fetchall()

    return result
