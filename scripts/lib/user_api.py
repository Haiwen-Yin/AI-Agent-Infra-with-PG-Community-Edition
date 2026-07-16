"""AI Agent Infra v3.10.2 - PG Community Edition - User Management API

User registration, profile, and user-scoped content retrieval.
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one

logger = logging.getLogger(__name__)


def create_user(username: str, password: str, role: str = "USER", auth_source: str = "LOCAL") -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        "SELECT user_manager.create(%s, %s, %s, %s) AS user_id",
        [username, password, role, auth_source],
    )
    if row is None or row.get("user_id") is None or row["user_id"] == -1:
        return None
    return {
        "user_id": row["user_id"],
        "username": username,
        "role": role,
        "status": "ACTIVE",
        "auth_source": auth_source,
    }


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        "SELECT user_manager.authenticate(%s, %s) AS result",
        [username, password],
    )
    if row and row.get("result"):
        val = row["result"]
        if isinstance(val, str):
            val = json.loads(val)
        if isinstance(val, dict) and val.get("authenticated"):
            return val
    return None


def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        "SELECT user_manager.get_profile(%s) AS profile",
        [user_id],
    )
    if row and row.get("profile"):
        val = row["profile"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return None


def update_last_login(user_id: int) -> None:
    execute("SELECT user_manager.update_last_login(%s)", [user_id])


def get_user_memories(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT entity_id, title, entity_type, status, created_at
           FROM entities
           WHERE entity_type = 'MEMORY'
           ORDER BY created_at DESC
           LIMIT %s""",
        [limit],
    )
    return rows[:limit]


def get_user_workspaces(user_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT w.workspace_id, w.workspace_name, w.workspace_type, w.status, w.created_at
           FROM workspaces w
           WHERE w.owner_user_id = %s
           ORDER BY w.created_at DESC""",
        [str(user_id)],
    )
    return rows
