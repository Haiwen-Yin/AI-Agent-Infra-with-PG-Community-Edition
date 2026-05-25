"""PostgreSQL Memory System v2.3.0 - Workspace API

Workspace lifecycle management, context chains, agent handoff sessions,
workspace recovery, and task linking.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

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
                'ACTIVE', NOW(), NOW())
        RETURNING workspace_id
    """
    return execute_insert_returning_id(sql, (
        owner_user_id, name, workspace_type, isolation_mode, meta_val,
    ), id_column="workspace_id")


def get_workspace(workspace_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
               isolation_mode, current_agent_id, current_session_id,
               summary, metadata, status, created_at, updated_at
        FROM workspaces
        WHERE workspace_id = %s
    """
    row = execute_query_one(sql, (workspace_id,))
    return _row_to_dict(row) if row else None


def get_user_workspaces(
    user_id: str,
    status: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if status:
        sql = """
            SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
                   isolation_mode, current_agent_id, current_session_id,
                   summary, metadata, status, created_at, updated_at
            FROM workspaces
            WHERE owner_user_id = %s AND status = %s
            ORDER BY updated_at DESC
        """
        rows = execute_query(sql, (user_id, status))
    else:
        sql = """
            SELECT workspace_id, owner_user_id, workspace_name, workspace_type,
                   isolation_mode, current_agent_id, current_session_id,
                   summary, metadata, status, created_at, updated_at
            FROM workspaces
            WHERE owner_user_id = %s
            ORDER BY updated_at DESC
        """
        rows = execute_query(sql, (user_id,))
    return [_row_to_dict(r) for r in rows]


def update_workspace(workspace_id: str, **kwargs: Any) -> bool:
    updates: Dict[str, str] = {}
    values: List[Any] = []
    for key, value in kwargs.items():
        col = key.lower()
        if col not in _ALLOWED_UPDATE_FIELDS:
            continue
        if col in ("metadata",) and isinstance(value, (dict, list)):
            updates[col] = "%s"
            values.append(json.dumps(value))
        else:
            updates[col] = "%s"
            values.append(value)
    if not updates:
        return False
    set_parts = ["{} = {}".format(k, v) for k, v in updates.items()]
    set_parts.append("updated_at = NOW()")
    values.append(workspace_id)
    sql = "UPDATE workspaces SET {} WHERE workspace_id = %s".format(', '.join(set_parts))
    return execute(sql, values) > 0


def save_context(
    workspace_id: str,
    agent_id: str,
    context_type: str,
    context_data: Any,
    session_id: Optional[str] = None,
    parent_context_id: Optional[str] = None,
) -> str:
    data_val = json.dumps(context_data) if isinstance(context_data, (dict, list)) else context_data
    sql = """
        INSERT INTO workspace_context (workspace_id, agent_id,
                                       session_id, context_type, context_data,
                                       parent_context_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        RETURNING context_id
    """
    return execute_insert_returning_id(sql, (
        workspace_id, agent_id, session_id,
        context_type, data_val, parent_context_id,
    ), id_column="context_id")


def get_context_chain(
    workspace_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT context_id, workspace_id, agent_id, session_id,
               context_type, context_data, parent_context_id, created_at
        FROM workspace_context
        WHERE workspace_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    rows = execute_query(sql, (workspace_id, limit))
    return [_row_to_dict(r) for r in rows]


def get_latest_context(workspace_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT context_id, workspace_id, agent_id, session_id,
               context_type, context_data, parent_context_id, created_at
        FROM workspace_context
        WHERE workspace_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    row = execute_query_one(sql, (workspace_id,))
    return _row_to_dict(row) if row else None


def create_handoff_session(
    workspace_id: str,
    new_agent_id: str,
    handoff_data: Optional[Any] = None,
) -> str:
    import time
    ws = get_workspace(workspace_id)
    if ws is None:
        raise ValueError(f"Workspace not found: {workspace_id}")

    latest_ctx = get_latest_context(workspace_id)
    current_session_id = ws.get("current_session_id")

    new_session_id = "session-{}-{}".format(new_agent_id, int(time.time() * 1000))
    sql = """
        INSERT INTO agent_session (session_id, agent_id, workspace_id,
                                    predecessor_session_id, owner_user_id,
                                    is_active, start_time, context)
        VALUES (%s, %s, %s, %s, %s, TRUE, NOW(), %s)
        RETURNING session_id
    """
    returned_id = execute_insert_returning_id(sql, (
        new_session_id, new_agent_id, workspace_id, current_session_id,
        ws.get("owner_user_id"),
        json.dumps(handoff_data) if isinstance(handoff_data, (dict, list)) else handoff_data,
    ), id_column="session_id")

    save_context(
        workspace_id=workspace_id,
        agent_id=new_agent_id,
        context_type="HANDOFF",
        context_data=handoff_data or {},
        session_id=new_session_id,
        parent_context_id=latest_ctx.get("context_id") if latest_ctx else None,
    )

    update_workspace(
        workspace_id,
        current_agent_id=new_agent_id,
        current_session_id=new_session_id,
    )

    return new_session_id


def recover_workspace(workspace_id: str) -> Dict[str, Any]:
    ws = get_workspace(workspace_id)
    if ws is None:
        raise ValueError(f"Workspace not found: {workspace_id}")

    context_chain = get_context_chain(workspace_id, limit=5)

    active_tasks_sql = """
        SELECT tp.plan_id, tp.goal, tp.status,
               tp.priority, tp.strategy, tp.created_at, tp.updated_at
        FROM task_plans tp
        JOIN workspace_tasks wt ON tp.plan_id = wt.plan_id
        WHERE wt.workspace_id = %s
          AND tp.status IN ('PENDING', 'RUNNING', 'BLOCKED')
        ORDER BY tp.updated_at DESC
    """
    active_tasks = execute_query(active_tasks_sql, (workspace_id,))

    recent_sessions_sql = """
        SELECT session_id, agent_id, workspace_id, predecessor_session_id,
               owner_user_id, is_active, start_time, end_time, context
        FROM agent_session
        WHERE workspace_id = %s
        ORDER BY start_time DESC
        LIMIT 5
    """
    recent_sessions = [_row_to_dict(r) for r in execute_query(recent_sessions_sql, (workspace_id,))]

    recent_entities: List[Dict[str, Any]] = []
    if ws.get("isolation_mode") == "ISOLATED":
        recent_entities_sql = """
            SELECT entity_id, entity_type, title, category, status,
                   created_at, updated_at
            FROM entities
            WHERE workspace_id = %s
            ORDER BY updated_at DESC
            LIMIT 10
        """
        recent_entities = [_row_to_dict(r) for r in execute_query(recent_entities_sql, (workspace_id,))]

    return {
        "workspace": ws,
        "context_chain": context_chain,
        "active_tasks": active_tasks,
        "recent_sessions": recent_sessions,
        "recent_entities": recent_entities,
    }


def link_task_to_workspace(workspace_id: str, plan_id: str) -> bool:
    sql = """
        INSERT INTO workspace_tasks (workspace_id, plan_id, assigned_at)
        VALUES (%s, %s, NOW())
    """
    return execute(sql, (workspace_id, plan_id)) > 0


def get_workspace_tasks(workspace_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT tp.plan_id, tp.goal, tp.status,
               tp.priority, tp.strategy, tp.agent_id,
               tp.created_at, tp.updated_at,
               wt.workspace_id, wt.assigned_at
        FROM task_plans tp
        JOIN workspace_tasks wt ON tp.plan_id = wt.plan_id
        WHERE wt.workspace_id = %s
        ORDER BY tp.updated_at DESC
    """
    return execute_query(sql, (workspace_id,))