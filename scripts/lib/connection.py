"""PostgreSQL Memory System v2.2.1 - Connection Pool Manager"""

import logging
import threading
from contextlib import contextmanager

import psycopg2
import psycopg2.pool

from .config import get_config

logger = logging.getLogger(__name__)

_pool = None
_lock = threading.Lock()


def get_pool():
    global _pool
    if _pool is not None:
        return _pool
    with _lock:
        if _pool is not None:
            return _pool
        cfg = get_config().database
        kwargs = dict(
            database=cfg.database, user=cfg.user,
            password=cfg.password or None,
            minconn=cfg.min_conn, maxconn=cfg.max_conn,
        )
        if cfg.host in ('localhost', '127.0.0.1') or not cfg.host:
            kwargs['host'] = '/tmp'
        else:
            kwargs['host'] = cfg.host
            kwargs['port'] = cfg.port
        _pool = psycopg2.pool.ThreadedConnectionPool(**kwargs)
        logger.info("Connection pool created (%d-%d connections)", cfg.min_conn, cfg.max_conn)
        return _pool


@contextmanager
def get_connection():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def close_pool():
    global _pool
    with _lock:
        if _pool is not None:
            _pool.closeall()
            _pool = None
            logger.info("Connection pool closed")


def execute(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def execute_query(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [desc[0].lower() for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


def execute_query_one(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            if row is None:
                return None
            columns = [desc[0].lower() for desc in cur.description]
            return dict(zip(columns, row))


def execute_insert_returning_id(sql, params=None, id_column='entity_id'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            conn.commit()
            if row is None:
                return None
            columns = [desc[0].lower() for desc in cur.description]
            result = dict(zip(columns, row))
            return result.get(id_column, result.get(list(result.keys())[0]))


def execute_many(sql, params_list):
    with get_connection() as conn:
        with conn.cursor() as cur:
            total = 0
            for params in params_list:
                cur.execute(sql, params)
                total += cur.rowcount
            conn.commit()
            return total
