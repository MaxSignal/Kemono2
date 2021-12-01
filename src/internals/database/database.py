from threading import Lock
from typing import Optional

from flask import g
from psycopg2 import pool
from psycopg2.extensions import cursor
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from configs.env_vars import ENV_VARS

pool: Optional[ThreadedConnectionPool] = None  # noqa F811
connection_lock = Lock()


def init():
    global pool
    try:
        pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=2000,
            host=ENV_VARS.PGHOST,
            dbname=ENV_VARS.PGDATABASE,
            user=ENV_VARS.PGUSER,
            password=ENV_VARS.PGPASSWORD,
            port=ENV_VARS.PGPORT,
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
