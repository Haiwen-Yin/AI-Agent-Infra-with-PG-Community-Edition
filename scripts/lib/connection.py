"""AI Agent Infra v3.10.1 - PG Enterprise Edition - Database Connection Pool Manager

psycopg2-based connection pool with parameterized query support.
Supports Admin/Agent separation modes (standalone, admin, agent).
"""

import json
import threading
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extras import RealDictCursor

from .config import get_config, DatabaseConfig, AgentModeConfig

logger = logging.getLogger(__name__)

_pool: Optional[pg_pool.ThreadedConnectionPool] = None
_lock = threading.Lock()


def _init_pool(cfg: DatabaseConfig) -> pg_pool.ThreadedConnectionPool:
    return pg_pool.ThreadedConnectionPool(
        minconn=cfg.min_conn,
        maxconn=cfg.max_conn,
        host=cfg.host,
        port=cfg.port,
        dbname=cfg.dbname,
        user=cfg.user,
        password=cfg.password,
    )


def get_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                cfg = get_config()
                if cfg.agent.mode == "agent":
                    raise RuntimeError("Schema owner pool not available in agent mode")
                db_cfg = cfg.database
                logger.info("Initializing connection pool: %s@%s:%d/%s (min=%d, max=%d)",
                            db_cfg.user, db_cfg.host, db_cfg.port, db_cfg.dbname,
                            db_cfg.min_conn, db_cfg.max_conn)
                _pool = _init_pool(db_cfg)
    return _pool


@contextmanager
def get_connection():
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def get_current_agent_id() -> Optional[str]:
    return getattr(_thread_local, "agent_id", None)


_thread_local = threading.local()


def set_agent_context(agent_id: Optional[str]) -> None:
    _thread_local.agent_id = agent_id


def close_end_user_connections():
    pass


@contextmanager
def get_connection_for_agent(agent_id: Optional[str] = None):
    with get_connection() as conn:
        yield conn


def apply_agent_context(conn, agent_id: Optional[str] = None) -> None:
    pass


def clear_agent_context(conn) -> None:
    pass


def close_pool():
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


def _convert_params(sql: str, params: Optional[Any]) -> tuple:
    """Convert Oracle-style :param to psycopg2 %s style.
    Supports both dict params (:param style) and tuple/list params (%s style).
    
    For dict params:
    - Each :param is replaced with %s and value collected in order of appearance
    - Existing %s placeholders get values from dict keys 'limit', 'offset', etc.
      (for backwards compat with PG-native SQL that uses LIMIT %s)
    
    For tuple/list params:
    - %s placeholders are used as-is with values in order
    """
    if params is None:
        return sql, ()
    if isinstance(params, dict):
        import re
        ordered_values = []
        
        # First, replace all :param with %s and collect values
        def replace_param(match):
            key = match.group(1)
            if key in params:
                ordered_values.append(params[key])
                return '%s'
            return match.group(0)
        converted = re.sub(r':(\w+)', replace_param, sql)
        
        # Now handle any remaining %s placeholders that weren't from :param
        # These come from PG-native SQL (e.g., LIMIT %s)
        # We need to provide values for them from the dict
        # Count remaining %s and try to match with dict values not yet used
        remaining_s = converted.count('%s') - len(ordered_values)
        if remaining_s > 0:
            # Find dict keys that weren't used by :param replacement
            used_keys = set()
            for m in re.finditer(r':(\w+)', sql):
                if m.group(1) in params:
                    used_keys.add(m.group(1))
            # Common positional keys in order of typical SQL appearance
            positional_keys = ['limit', 'offset', 'status', 'agent_id', 'workspace_id']
            for key in positional_keys:
                if key in params and key not in used_keys and remaining_s > 0:
                    ordered_values.append(params[key])
                    used_keys.add(key)
                    remaining_s -= 1
            # If still remaining, add any unused values
            for key in params:
                if remaining_s <= 0:
                    break
                if key not in used_keys:
                    ordered_values.append(params[key])
                    used_keys.add(key)
                    remaining_s -= 1
        
        return converted, tuple(ordered_values)
    elif isinstance(params, (list, tuple)):
        return sql, tuple(params)
    return sql, ()


def execute(sql: str, params: Optional[Dict[str, Any]] = None) -> int:
    sql, pg_params = _convert_params(sql, params)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, pg_params)
            conn.commit()
            return cur.rowcount


def execute_query(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    sql, pg_params = _convert_params(sql, params)
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, pg_params)
            return [dict(row) for row in cur.fetchall()]


def execute_query_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    sql, pg_params = _convert_params(sql, params)
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, pg_params)
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else None


def execute_insert(sql: str, params: Optional[Dict[str, Any]] = None) -> str:
    sql, pg_params = _convert_params(sql, params)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, pg_params)
            conn.commit()
            return "ok"


def execute_insert_returning_id(
    sql: str,
    params: Optional[Dict[str, Any]] = None,
    returning_col: str = None,
    id_column: str = None
) -> str:
    """Execute INSERT with RETURNING clause and return the ID.
    
    For PostgreSQL, the RETURNING clause is already in the SQL.
    The :ret_id bind variable should be removed from the SQL before calling.
    `id_column` is an alias for `returning_col` for Oracle API compatibility.
    """
    if id_column and not returning_col:
        returning_col = id_column
    sql, pg_params = _convert_params(sql, params)
    # Remove any RETURNING ... INTO :ret_id clause (Oracle-specific)
    if "INTO :ret_id" in sql:
        sql = sql.replace("INTO :ret_id", "")
    if "RETURNING" in sql.upper() and "INTO" in sql:
        # Clean up Oracle-style RETURNING ... INTO ...
        import re
        sql = re.sub(r'\s+INTO\s+:\w+', '', sql, flags=re.IGNORECASE)
    
    # If RETURNING clause is not in SQL, add it
    if returning_col and "RETURNING" not in sql.upper():
        # Find the column name to return
        col = returning_col.lower() if not returning_col.startswith(':') else returning_col
        sql = sql.rstrip().rstrip(';') + f' RETURNING {col}'
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, pg_params)
            row = cur.fetchone()
            conn.commit()
            if row:
                val = row[0]
                if isinstance(val, int):
                    return val
                return str(val)
            return None


def execute_many(sql: str, params_list) -> int:
    """Execute a batch INSERT/UPDATE/DELETE."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
            conn.commit()
            return cur.rowcount


def sanitize_row(row) -> Dict[str, Any]:
    """Convert a RealDictRow to a plain dict, handling Decimal and datetime."""
    if row is None:
        return {}
    d = dict(row) if not isinstance(row, dict) else row
    # Convert Decimal to float for JSON serialization
    for k, v in d.items():
        if isinstance(v, Decimal):
            d[k] = float(v)
    return d


def _row_to_dict(row) -> Dict[str, Any]:
    return sanitize_row(row)


# Import Decimal for sanitize_row
from decimal import Decimal
