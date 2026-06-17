"""AI Agent Infra v3.6.2 - PG Community Edition - Database Connection Pool Manager

Unified psycopg2 connection pool with %s bind-variable support.
Includes agent context management via current_setting('app.current_agent_id', TRUE).
Supports Admin/Agent separation modes (standalone, admin, agent).
"""

import json
import logging
import threading
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.pool

from .config import get_config, DatabaseConfig, AgentModeConfig

logger = logging.getLogger(__name__)

_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
_lock = threading.Lock()

_current_agent_id = threading.local()


def _init_pool(cfg: DatabaseConfig) -> psycopg2.pool.ThreadedConnectionPool:
    kwargs = dict(
        database=cfg.dbname,
        user=cfg.user,
        password=cfg.password or None,
        minconn=cfg.min_conn,
        maxconn=cfg.max_conn,
    )
    if cfg.host in ("localhost", "127.0.0.1") or not cfg.host:
        kwargs["host"] = "/tmp"
    else:
        kwargs["host"] = cfg.host
        kwargs["port"] = cfg.port
    return psycopg2.pool.ThreadedConnectionPool(**kwargs)


def get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                cfg = get_config()
                if cfg.agent.mode == "agent":
                    raise RuntimeError("Pool not available in agent mode")
                db_cfg = cfg.database
                logger.info("Initializing connection pool: %s@%s/%s (min=%d, max=%d)",
                            db_cfg.user, db_cfg.host, db_cfg.dbname, db_cfg.min_conn, db_cfg.max_conn)
                _pool = _init_pool(db_cfg)
    return _pool


@contextmanager
def get_connection():
    pool = get_pool()
    conn = pool.getconn()
    try:
        _apply_agent_context(conn)
        yield conn
    finally:
        _clear_agent_context(conn)
        pool.putconn(conn)


def set_agent_context(agent_id: Optional[str]) -> None:
    _current_agent_id.value = agent_id


def get_current_agent_id() -> Optional[str]:
    return getattr(_current_agent_id, "value", None)


def _apply_agent_context(conn, agent_id: Optional[str] = None) -> None:
    aid = agent_id or get_current_agent_id()
    if aid:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT set_config('app.current_agent_id', %s, FALSE)", (aid,))
        except psycopg2.Error as e:
            logger.debug("set_config for agent context failed: %s", e)


def _clear_agent_context(conn) -> None:
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT set_config('app.current_agent_id', '', FALSE)")
    except psycopg2.Error as e:
        logger.debug("clear agent context failed: %s", e)


def close_pool():
    global _pool
    with _lock:
        if _pool is not None:
            _pool.closeall()
            _pool = None
            logger.info("Connection pool closed")


def execute(sql: str, params=None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount


def execute_query(sql: str, params=None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [desc[0].lower() for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
            conn.commit()
            return rows


def execute_query_one(sql: str, params=None) -> Optional[Dict[str, Any]]:
    rows = execute_query(sql, params)
    return rows[0] if rows else None


def execute_insert_returning_id(sql: str, params=None, id_column: str = "entity_id"):
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


def execute_many(sql: str, params_list) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            total = 0
            for params in params_list:
                cur.execute(sql, params)
                total += cur.rowcount
            conn.commit()
            return total


def _sanitize_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_json(i) for i in obj]
    elif isinstance(obj, Decimal):
        return int(obj) if obj == obj.to_integral_value() else float(obj)
    return obj


def sanitize_row(d):
    if not isinstance(d, dict):
        return d
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _sanitize_json(v)
        elif isinstance(v, list):
            result[k] = [_sanitize_json(i) for i in v]
        else:
            result[k] = v
    return result
