"""PostgreSQL Memory System v2.3.1 - Agent API

Agent registration, session management, access audit logging,
and collaboration tracking.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"capabilities", "config", "context"}

_ALLOWED_UPDATE_FIELDS = {
    "agent_name", "agent_type", "description",
    "capabilities", "config", "status",
}


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


def register_agent(
    agent_id: str,
    agent_name: str,
    agent_type: Optional[str] = None,
    description: Optional[str] = None,
    capabilities: Optional[Any] = None,
    config: Optional[Any] = None,
) -> str:
    caps_val = json.dumps(capabilities) if isinstance(capabilities, (dict, list)) else capabilities
    cfg_val = json.dumps(config) if isinstance(config, (dict, list)) else config
    sql = """
        INSERT INTO agent_registry (agent_id, agent_name, agent_type, description,
                                    capabilities, config, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', NOW(), NOW())
        ON CONFLICT (agent_id) DO NOTHING
    """
    execute(sql, (agent_id, agent_name, agent_type, description, caps_val, cfg_val))
    return agent_id


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT agent_id, agent_name, agent_type, description,
               capabilities, config, status,
               last_seen_at, created_at, updated_at
        FROM agent_registry
        WHERE agent_id = %s
    """
    row = execute_query_one(sql, (agent_id,))
    return _row_to_dict(row) if row else None


def update_agent(agent_id: str, **kwargs: Any) -> bool:
    updates = {}
    values: List[Any] = []
    for key, value in kwargs.items():
        col = key.lower()
        if col not in _ALLOWED_UPDATE_FIELDS:
            continue
        if col in ("capabilities", "config") and isinstance(value, (dict, list)):
            updates[col] = "%s"
            values.append(json.dumps(value))
        else:
            updates[col] = "%s"
            values.append(value)
    if not updates:
        return False
    set_parts = ["{} = {}".format(k, v) for k, v in updates.items()]
    set_parts.append("updated_at = NOW()")
    values.append(agent_id)
    sql = "UPDATE agent_registry SET {} WHERE agent_id = %s".format(', '.join(set_parts))
    return execute(sql, values) > 0


def decommission_agent(agent_id: str) -> bool:
    sql = """
        UPDATE agent_registry
        SET status = 'DECOMMISSIONED', updated_at = NOW()
        WHERE agent_id = %s
    """
    return execute(sql, (agent_id,)) > 0


def heartbeat(agent_id: str) -> bool:
    sql = """
        UPDATE agent_registry
        SET last_seen_at = NOW()
        WHERE agent_id = %s
    """
    return execute(sql, (agent_id,)) > 0


def create_session(
    agent_id: str,
    owner_user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    predecessor_session_id: Optional[str] = None,
    context: Optional[Any] = None,
) -> str:
    import time
    session_id = "session-{}-{}".format(agent_id, int(time.time() * 1000))
    ctx_val = json.dumps(context) if isinstance(context, (dict, list)) else context
    sql = """
        INSERT INTO agent_session (session_id, agent_id, owner_user_id, workspace_id,
                                    predecessor_session_id, is_active,
                                    start_time, context)
        VALUES (%s, %s, %s, %s, %s, TRUE, NOW(), %s)
        RETURNING session_id
    """
    return execute_insert_returning_id(sql, (
        session_id, agent_id, owner_user_id, workspace_id,
        predecessor_session_id, ctx_val,
    ), id_column="session_id")


def end_session(session_id: str) -> bool:
    sql = """
        UPDATE agent_session
        SET is_active = FALSE, end_time = NOW()
        WHERE session_id = %s AND is_active = TRUE
    """
    return execute(sql, (session_id,)) > 0


def checkpoint_session(session_id: str, context_data: Any) -> bool:
    sql = """
        SELECT workspace_id, agent_id
        FROM agent_session
        WHERE session_id = %s
    """
    row = execute_query_one(sql, (session_id,))
    if not row or not row.get("workspace_id"):
        return False
    from .workspace_api import save_context
    save_context(
        workspace_id=row["workspace_id"],
        agent_id=row["agent_id"],
        context_type="CHECKPOINT",
        context_data=context_data,
        session_id=session_id,
    )
    return True


def get_session_chain(session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    chain = []
    current_id = session_id
    visited = set()
    while current_id and current_id not in visited and len(chain) < limit:
        visited.add(current_id)
        sql = """
            SELECT session_id, agent_id, workspace_id, predecessor_session_id,
                   is_active, start_time, end_time, context
            FROM agent_session
            WHERE session_id = %s
        """
        row = execute_query_one(sql, (current_id,))
        if not row:
            break
        chain.append(_row_to_dict(row))
        current_id = row.get("predecessor_session_id")
    return chain


def get_active_sessions(agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if agent_id:
        sql = """
            SELECT session_id, agent_id, workspace_id, owner_user_id,
                   is_active, start_time, context
            FROM agent_session
            WHERE is_active = TRUE AND agent_id = %s
            ORDER BY start_time DESC
        """
        rows = execute_query(sql, (agent_id,))
    else:
        sql = """
            SELECT session_id, agent_id, workspace_id, owner_user_id,
                   is_active, start_time, context
            FROM agent_session
            WHERE is_active = TRUE
            ORDER BY start_time DESC
        """
        rows = execute_query(sql)
    return [_row_to_dict(r) for r in rows]


def log_access(
    agent_id: str,
    entity_id: str,
    access_type: str,
    session_id: Optional[str] = None,
) -> str:
    sql = """
        INSERT INTO entity_access_log (entity_id, agent_id, access_type, access_time, session_id)
        VALUES (%s, %s, %s, NOW(), %s)
        RETURNING log_id
    """
    return execute_insert_returning_id(sql, (
        entity_id, agent_id, access_type, session_id,
    ), id_column="log_id")


def get_access_log(
    entity_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []
    if entity_id:
        conditions.append("entity_id = %s")
        params.append(entity_id)
    if agent_id:
        conditions.append("agent_id = %s")
        params.append(agent_id)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(limit)
    sql = """
        SELECT log_id, entity_id, agent_id, access_type, session_id,
               access_time
        FROM entity_access_log
        {}
        ORDER BY access_time DESC
        LIMIT %s
    """.format(where)
    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]


def create_collaboration(
    source_agent_id: str,
    target_agent_id: str,
    col_type: str,
    entity_id: Optional[str] = None,
    context: Optional[Any] = None,
    strength: float = 1.0,
) -> str:
    ctx_val = json.dumps(context) if isinstance(context, (dict, list)) else context
    sql = """
        INSERT INTO agent_collaboration (source_agent_id, target_agent_id,
                                          col_type, entity_id, context, strength,
                                          created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING collab_id
    """
    return execute_insert_returning_id(sql, (
        source_agent_id, target_agent_id, col_type,
        entity_id, ctx_val, strength,
    ), id_column="collab_id")


def get_collaborations(
    agent_id: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    if agent_id:
        sql = """
            SELECT collab_id, source_agent_id, target_agent_id, col_type,
                   entity_id, context, strength, created_at, updated_at
            FROM agent_collaboration
            WHERE source_agent_id = %s OR target_agent_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (agent_id, agent_id, limit))
    else:
        sql = """
            SELECT collab_id, source_agent_id, target_agent_id, col_type,
                   entity_id, context, strength, created_at, updated_at
            FROM agent_collaboration
            ORDER BY created_at DESC
            LIMIT %s
        """
        rows = execute_query(sql, (limit,))
    return [_row_to_dict(r) for r in rows]


def issue_credential(agent_id: str, user_id: str, cred_type: str, scope: Any, expires_hours: int = 24) -> int:
    import uuid
    credential_value = uuid.uuid4().hex
    scope_val = json.dumps(scope) if isinstance(scope, (dict, list)) else scope
    sql = """
        INSERT INTO agent_credentials (agent_id, user_id, credential_type,
                                        credential_value, scope, is_active,
                                        expires_at, created_at)
        VALUES (%s, %s, %s, %s, %s, TRUE,
                NOW() + %s * INTERVAL '1 hour', NOW())
        RETURNING credential_id
    """
    cid = execute_insert_returning_id(sql, (
        agent_id, user_id, cred_type,
        credential_value, scope_val, expires_hours,
    ), id_column='credential_id')
    return cid


def verify_credential(credential_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT credential_id, agent_id, user_id, credential_type,
               credential_value, scope, is_active, expires_at, created_at
        FROM agent_credentials
        WHERE credential_id = %s AND is_active = TRUE
              AND (expires_at IS NULL OR expires_at > NOW())
    """
    row = execute_query_one(sql, (credential_id,))
    if row:
        return _row_to_dict(row)
    expire_sql = """
        UPDATE agent_credentials SET is_active = FALSE
        WHERE credential_id = %s AND is_active = TRUE AND expires_at IS NOT NULL AND expires_at <= NOW()
    """
    execute(expire_sql, (credential_id,))
    return None


def get_credentials_for_user(user_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT credential_id, agent_id, user_id, credential_type,
               credential_value, scope, is_active, expires_at, created_at
        FROM agent_credentials
        WHERE user_id = %s AND is_active = TRUE
              AND (expires_at IS NULL OR expires_at > NOW())
        ORDER BY created_at DESC
    """
    rows = execute_query(sql, (user_id,))
    return [_row_to_dict(r) for r in rows]


def revoke_credential(credential_id: int) -> bool:
    sql = """
        UPDATE agent_credentials SET is_active = FALSE
        WHERE credential_id = %s
    """
    return execute(sql, (credential_id,)) > 0


def hibernate_agent(agent_id: str) -> bool:
    sql = """
        UPDATE agent_registry SET status = 'DORMANT', updated_at = NOW()
        WHERE agent_id = %s AND status IN ('ACTIVE', 'INACTIVE')
    """
    result = execute(sql, (agent_id,)) > 0
    cred_sql = """
        UPDATE agent_credentials SET is_active = FALSE
        WHERE agent_id = %s AND is_active = TRUE
    """
    execute(cred_sql, (agent_id,))
    return result


def wake_agent(agent_id: str) -> bool:
    sql = """
        UPDATE agent_registry SET status = 'ACTIVE', last_active_at = NOW(), updated_at = NOW()
        WHERE agent_id = %s AND status = 'DORMANT'
    """
    return execute(sql, (agent_id,)) > 0


def register_pool_agent(agent_name: str, capabilities: Optional[Any] = None, skills_tags: Optional[List[str]] = None) -> str:
    import uuid
    agent_id = "pool-{}".format(uuid.uuid4().hex[:8])
    caps_val = json.dumps(capabilities) if isinstance(capabilities, (dict, list)) else capabilities
    pool_config = json.dumps({"skills_tags": skills_tags or []})
    sql = """
        INSERT INTO agent_registry (agent_id, agent_name, agent_type, capabilities,
                                     status, pool_config, created_at, updated_at)
        VALUES (%s, %s, 'pool', %s, 'POOL', %s, NOW(), NOW())
        RETURNING agent_id
    """
    return execute_insert_returning_id(sql, (
        agent_id, agent_name, caps_val, pool_config,
    ), id_column="agent_id")


def assign_pool_agent(user_id: str, required_skills: Optional[List[str]] = None) -> Optional[str]:
    if not required_skills:
        sql = """
            SELECT agent_id FROM agent_registry
            WHERE status = 'POOL'
            ORDER BY created_at ASC
            LIMIT 1
        """
        row = execute_query_one(sql)
    else:
        sql = """
            SELECT agent_id FROM agent_registry
            WHERE status = 'POOL'
            ORDER BY (
                SELECT COUNT(*)
                FROM jsonb_array_elements_text(
                    COALESCE(pool_config->'skills_tags', '[]'::jsonb)
                ) AS tag
                WHERE tag = ANY(%s)
            ) DESC, created_at ASC
            LIMIT 1
        """
        row = execute_query_one(sql, (required_skills,))
    if not row:
        return None
    agent_id = row["agent_id"]
    update_sql = """
        UPDATE agent_registry
        SET status = 'ACTIVE', current_user_id = %s, last_active_at = NOW(), updated_at = NOW()
        WHERE agent_id = %s AND status = 'POOL'
    """
    updated = execute(update_sql, (user_id, agent_id)) > 0
    if not updated:
        return None
    issue_credential(
        agent_id, user_id, 'assignment',
        {"access_level": "FULL", "restricted_domains": [], "max_clearance": "CONFIDENTIAL"},
    )
    return agent_id