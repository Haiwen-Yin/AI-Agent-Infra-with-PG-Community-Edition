"""AI Agent Infra v3.6.2 - PG Community Edition - Workspace API

Workspace lifecycle management, context chains, agent handoff sessions,
workspace recovery, and task linking.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import (execute_query, execute_query_one, execute,
                         execute_insert_returning_id)

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"metadata", "context_data"}

_ALLOWED_UPDATE_FIELDS = frozenset({
    "workspace_name", "status", "isolation_mode",
    "current_agent_id", "current_session_id", "summary", "metadata",
})


def _row_to_dict(row: Any) -> Dict[str, Any]:
    if row is None:
        return {}
    result = dict(row)
    for key in result:
        if key.lower() in _JSON_COLUMNS and isinstance(result[key], str):
            try:
                result[key] = json.loads(result[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_workspace(
    owner_user_id: Optional[str] = None,
    name: Optional[str] = None,
    workspace_type: str = "CONVERSATION",
    isolation_mode: str = "SHARED",
    metadata: Optional[Any] = None,
) -> str:
    meta_val = json.dumps(metadata) if isinstance(metadata, (dict, list)) else metadata
    sql = """
        INSERT INTO workspaces (owner_user_id, workspace_name,
                                workspace_type, isolation_mode, metadata,
                                status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s,
                'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING workspace_id
    """
    return execute_insert_returning_id(sql, [
        owner_user_id, name, workspace_type, isolation_mode, meta_val,
    ], id_column="workspace_id")


def get_workspace(workspace_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
               isolation_mode, current_agent_id, current_session_id,
               summary, metadata, status,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at
        FROM workspaces
        WHERE workspace_id = %s
    """
    row = execute_query_one(sql, [workspace_id])
    return _row_to_dict(row) if row else None


def update_workspace(workspace_id: str, **kwargs: Any) -> bool:
    updates: Dict[str, str] = {}
    params: list = []
    for key, value in kwargs.items():
        col = key.lower()
        if col not in _ALLOWED_UPDATE_FIELDS:
            continue
        if col in ("metadata",) and isinstance(value, (dict, list)):
            updates[col] = "%s"
            params.append(json.dumps(value))
        else:
            updates[col] = "%s"
            params.append(value)
    if not updates:
        return False
    updates["updated_at"] = "CURRENT_TIMESTAMP"
    set_clause = ", ".join(f"{k} = {v}" for k, v in updates.items())
    params.append(workspace_id)
    sql = f"UPDATE workspaces SET {set_clause} WHERE workspace_id = %s"
    return execute(sql, params) > 0


def pause_workspace(workspace_id: str) -> bool:
    sql = """
        UPDATE workspaces SET status = 'PAUSED', updated_at = CURRENT_TIMESTAMP
        WHERE workspace_id = %s
    """
    return execute(sql, [workspace_id]) > 0


def complete_workspace(workspace_id: str) -> bool:
    sql = """
        UPDATE workspaces SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP
        WHERE workspace_id = %s
    """
    return execute(sql, [workspace_id]) > 0


def _sanitize_context_data(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    sensitive_keys = {
        'password', 'passwd', 'secret', 'credential', 'token',
        'api_key', 'apikey', 'private_key', 'access_key',
        'dsn', 'connection_string', 'db_url', 'database_url',
        'master_key', 'encryption_key', 'auth_header',
    }
    sanitized = {}
    for k, v in data.items():
        kl = k.lower()
        if any(sk in kl for sk in sensitive_keys):
            sanitized[k] = '[REDACTED]'
        elif isinstance(v, dict):
            sanitized[k] = _sanitize_context_data(v)
        else:
            sanitized[k] = v
    return sanitized


def save_context(
    workspace_id: str,
    agent_id: str,
    context_type: str,
    context_data: Any,
    session_id: Optional[str] = None,
    parent_context_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    visibility: str = "SHARED",
) -> str:
    context_data = _sanitize_context_data(context_data)
    data_val = json.dumps(context_data) if isinstance(context_data, (dict, list)) else context_data
    sql = """
        INSERT INTO workspace_context (workspace_id, agent_id,
                                       session_id, context_type, context_data,
                                       parent_context_id, branch_id, visibility, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING context_id
    """
    return execute_insert_returning_id(sql, [
        workspace_id, agent_id, session_id, context_type, data_val,
        parent_context_id, branch_id, visibility,
    ], id_column="context_id")


def get_latest_context(workspace_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT context_id, workspace_id, agent_id, session_id,
               context_type, context_data, parent_context_id,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM workspace_context
        WHERE workspace_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    row = execute_query_one(sql, [workspace_id])
    return _row_to_dict(row) if row else None


def get_context_chain(
    workspace_id: str,
    limit: int = 10,
    branch_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if branch_id:
        rows = execute_query("""
            SELECT context_id, workspace_id, agent_id, session_id,
                   context_type, context_data, parent_context_id,
                   TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
            FROM workspace_context
            WHERE workspace_id = %s AND branch_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, [workspace_id, branch_id, limit])
    else:
        rows = execute_query("""
            SELECT context_id, workspace_id, agent_id, session_id,
                   context_type, context_data, parent_context_id,
                   TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
            FROM workspace_context
            WHERE workspace_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, [workspace_id, limit])
    return [_row_to_dict(r) for r in rows]


def create_handoff(
    workspace_id: str,
    new_agent_id: str,
    handoff_data: Optional[Any] = None,
) -> str:
    ws = get_workspace(workspace_id)
    if ws is None:
        raise ValueError("Workspace not found: %s" % workspace_id)

    latest_ctx = get_latest_context(workspace_id)
    current_session_id = ws.get("current_session_id")

    branch_id = None
    try:
        from .branch_api import fork_branch
        branch_id = fork_branch(
            workspace_id=workspace_id,
            fork_context_id=latest_ctx["context_id"] if latest_ctx else None,
            branch_name="handoff-to-%s" % new_agent_id,
            branch_type="HANDOFF",
            agent_id=new_agent_id,
            source_agent_id=ws.get("current_agent_id"),
            purpose="Handoff from %s to %s" % (ws.get('current_agent_id', '?'), new_agent_id),
            fork_session_id=current_session_id,
        )
    except ImportError:
        pass

    ctx_val = json.dumps(handoff_data) if isinstance(handoff_data, (dict, list)) else handoff_data
    sql = """
        INSERT INTO agent_session (agent_id, workspace_id,
                                   predecessor_session_id, owner_user_id,
                                   is_active, context, branch_id)
        VALUES (%s, %s, %s, %s,
                TRUE, %s, %s)
        RETURNING session_id
    """
    new_session_id = execute_insert_returning_id(sql, [
        new_agent_id, workspace_id, current_session_id,
        ws.get("owner_user_id"), ctx_val, branch_id,
    ], id_column="session_id")

    save_context(
        workspace_id=workspace_id,
        agent_id=new_agent_id,
        context_type="HANDOFF",
        context_data=handoff_data or {},
        session_id=new_session_id,
        parent_context_id=latest_ctx.get("context_id") if latest_ctx else None,
        branch_id=branch_id,
    )

    update_workspace(
        workspace_id,
        current_agent_id=new_agent_id,
        current_session_id=new_session_id,
    )

    return new_session_id


def recover_to_checkpoint(workspace_id: str, context_id: Optional[str] = None) -> Dict[str, Any]:
    ws = get_workspace(workspace_id)
    if ws is None:
        raise ValueError("Workspace not found: %s" % workspace_id)

    if context_id:
        checkpoint = execute_query_one("""
            SELECT context_id, context_data, agent_id
            FROM workspace_context
            WHERE context_id = %s AND workspace_id = %s
        """, [context_id, workspace_id])
    else:
        checkpoint = execute_query_one("""
            SELECT context_id, context_data, agent_id
            FROM workspace_context
            WHERE workspace_id = %s AND context_type = 'CHECKPOINT'
            ORDER BY created_at DESC
            LIMIT 1
        """, [workspace_id])

    if not checkpoint:
        return {"recovered": False, "reason": "No checkpoint found"}

    update_workspace(
        workspace_id,
        current_agent_id=checkpoint.get("agent_id"),
        status="ACTIVE",
    )

    return {
        "recovered": True,
        "workspace_id": workspace_id,
        "context_id": checkpoint.get("context_id"),
        "context_data": checkpoint.get("context_data"),
    }


def get_workspace_summary(workspace_id: str) -> Dict[str, Any]:
    ws = get_workspace(workspace_id)
    if ws is None:
        return {}

    ctx_count_row = execute_query_one("""
        SELECT COUNT(*) AS cnt FROM workspace_context WHERE workspace_id = %s
    """, [workspace_id])
    ctx_count = int(ctx_count_row["cnt"]) if ctx_count_row else 0

    entity_count_row = execute_query_one("""
        SELECT COUNT(*) AS cnt FROM entities WHERE workspace_id = %s
    """, [workspace_id])
    entity_count = int(entity_count_row["cnt"]) if entity_count_row else 0

    session_count_row = execute_query_one("""
        SELECT COUNT(*) AS cnt FROM agent_session WHERE workspace_id = %s
    """, [workspace_id])
    session_count = int(session_count_row["cnt"]) if session_count_row else 0

    return {
        "workspace_id": workspace_id,
        "status": ws.get("status"),
        "current_agent_id": ws.get("current_agent_id"),
        "context_count": ctx_count,
        "entity_count": entity_count,
        "session_count": session_count,
    }


def cleanup_abandoned(max_age_hours: int = 168) -> int:
    sql = """
        UPDATE workspaces SET status = 'ABANDONED', updated_at = CURRENT_TIMESTAMP
        WHERE status = 'ACTIVE'
          AND updated_at < CURRENT_TIMESTAMP - (%s || ' hours')::interval
    """
    return execute(sql, [max_age_hours])


def link_task_to_workspace(workspace_id: str, plan_id: str) -> bool:
    sql = """
        INSERT INTO workspace_tasks (workspace_id, plan_id, assigned_at)
        VALUES (%s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING
    """
    return execute(sql, [workspace_id, plan_id]) > 0


def get_user_workspaces(
    user_id: str,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if status:
        rows = execute_query("""
            SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
                   isolation_mode, current_agent_id, current_session_id,
                   summary, metadata, status,
                   TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
                   TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at
            FROM workspaces
            WHERE owner_user_id = %s AND status = %s
            ORDER BY updated_at DESC
        """, [user_id, status])
    else:
        rows = execute_query("""
            SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
                   isolation_mode, current_agent_id, current_session_id,
                   summary, metadata, status,
                   TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
                   TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at
            FROM workspaces
            WHERE owner_user_id = %s
            ORDER BY updated_at DESC
        """, [user_id])
    return [_row_to_dict(r) for r in rows]
