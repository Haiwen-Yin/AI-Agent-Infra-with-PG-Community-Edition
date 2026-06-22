"""AI Agent Infra v3.7.3 - PG Community Edition - Collaboration Group API

Collaboration group lifecycle, membership management,
shared/personal workspaces, entity sharing, and group statistics.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import (
    execute,
    execute_query,
    execute_query_one,
    execute_insert_returning_id,
    sanitize_row,
)
from .workspace_api import create_workspace

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"metadata", "sharing_policy"}

_ALLOWED_UPDATE_FIELDS = frozenset({
    "group_name", "group_type", "description",
    "coordinator_agent_id", "sharing_policy", "status", "metadata",
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
    return sanitize_row(result)


def create_collab_group(
    name: str,
    group_type: str,
    coordinator_agent_id: Optional[str] = None,
    description: Optional[str] = None,
    sharing_policy: str = "OPEN",
    metadata: Optional[Any] = None,
    branch_id: Optional[str] = None,
    spec_id: Optional[str] = None,
) -> str:
    ws_id = create_workspace(
        name="CollabGroup: " + name,
        workspace_type="COLLAB_GROUP",
        isolation_mode="SHARED",
        metadata=json.dumps({"collab_group_name": name, "group_type": group_type}),
    )

    meta_val = json.dumps(metadata) if isinstance(metadata, (dict, list)) else metadata
    sql = """
        INSERT INTO collab_groups (group_name, group_type, description,
                                    workspace_id, coordinator_agent_id, sharing_policy,
                                    status, metadata, branch_id, spec_id, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s,
                'ACTIVE', %s, %s, %s, NOW(), NOW())
        RETURNING group_id
    """
    return execute_insert_returning_id(sql, (
        name, group_type, description,
        ws_id, coordinator_agent_id, sharing_policy,
        meta_val, branch_id, spec_id,
    ), id_column="group_id")


def get_collab_group(group_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT group_id, group_name, group_type, description,
               workspace_id, coordinator_agent_id, sharing_policy,
               status, metadata, branch_id, spec_id,
               created_at, updated_at
        FROM collab_groups
        WHERE group_id = %s
    """
    row = execute_query_one(sql, (group_id,))
    if row is None:
        return None
    group = _row_to_dict(row)
    group["members"] = get_collab_members(group_id)
    return group


def update_collab_group(group_id: str, **kwargs: Any) -> bool:
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
    values.append(group_id)
    sql = "UPDATE collab_groups SET {} WHERE group_id = %s".format(", ".join(set_parts))
    return execute(sql, values) > 0


def add_collab_member(
    group_id: str,
    agent_id: str,
    role: str = "MEMBER",
    branch_id: Optional[str] = None,
) -> str:
    personal_workspace_id = None
    if role in ("LEAD", "CONTRIBUTOR"):
        personal_workspace_id = create_workspace(
            name="Personal: {} in {}".format(agent_id, group_id),
            workspace_type="PERSONAL_IN_GROUP",
            isolation_mode="ISOLATED",
            metadata=json.dumps({"group_id": group_id, "agent_id": agent_id, "role": role}),
        )

    sql = """
        INSERT INTO collab_group_members (group_id, agent_id, role,
                                           personal_workspace_id, branch_id, joined_at, status)
        VALUES (%s, %s, %s, %s, %s, NOW(), 'ACTIVE')
        ON CONFLICT (group_id, agent_id) DO UPDATE
            SET role = EXCLUDED.role,
                status = 'ACTIVE',
                personal_workspace_id = COALESCE(collab_group_members.personal_workspace_id, EXCLUDED.personal_workspace_id),
                branch_id = COALESCE(collab_group_members.branch_id, EXCLUDED.branch_id)
        RETURNING member_id
    """
    return execute_insert_returning_id(sql, (
        group_id, agent_id, role,
        personal_workspace_id, branch_id,
    ), id_column="member_id")


def remove_collab_member(group_id: str, agent_id: str) -> bool:
    sql = """
        UPDATE collab_group_members
        SET status = 'LEFT'
        WHERE group_id = %s AND agent_id = %s AND status = 'ACTIVE'
    """
    return execute(sql, (group_id, agent_id)) > 0


def get_collab_members(group_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT member_id, group_id, agent_id, role,
               personal_workspace_id, branch_id, status, joined_at
        FROM collab_group_members
        WHERE group_id = %s
        ORDER BY joined_at ASC
    """
    rows = execute_query(sql, (group_id,))
    return [sanitize_row(dict(r)) for r in rows]


def archive_collab_group(group_id: str) -> bool:
    sql = """
        UPDATE collab_groups
        SET status = 'ARCHIVED', updated_at = NOW()
        WHERE group_id = %s AND status != 'ARCHIVED'
    """
    return execute(sql, (group_id,)) > 0


def list_collab_groups(
    status: Optional[str] = None,
    group_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []
    if status:
        conditions.append("status = %s")
        params.append(status)
    if group_type:
        conditions.append("group_type = %s")
        params.append(group_type)
    where = "WHERE {}".format(" AND ".join(conditions)) if conditions else ""
    params.extend([limit, offset])
    sql = """
        SELECT group_id, group_name, group_type, description,
               workspace_id, coordinator_agent_id, sharing_policy,
               status, metadata, branch_id, spec_id,
               created_at, updated_at
        FROM collab_groups
        {where}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """.format(where=where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def share_entity_to_group(
    group_id: int,
    entity_id: int,
    shared_by: str,
    share_type: str = "READ",
) -> bool:
    return execute(
        "UPDATE entities SET visibility = 'SHARED' WHERE entity_id = %s",
        [entity_id],
    ) > 0


def unshare_entity_from_group(group_id: int, entity_id: int) -> bool:
    return execute(
        "UPDATE entities SET visibility = 'PRIVATE' WHERE entity_id = %s",
        [entity_id],
    ) > 0


def get_group_shared_entities(
    group_id: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    sql = """
        SELECT s.share_id, s.group_id, s.entity_id, s.shared_by,
               s.share_type, s.created_at,
               e.entity_type, e.title, e.category
        FROM collab_group_shares s
        LEFT JOIN entities e ON e.entity_id = s.entity_id
        WHERE s.group_id = %s
        ORDER BY s.created_at DESC
        LIMIT %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, (group_id, limit))]


def get_agent_groups(agent_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT g.group_id, g.group_name, g.group_type, g.description,
               g.workspace_id, g.coordinator_agent_id, g.sharing_policy,
               g.status, g.metadata,
               g.created_at, g.updated_at,
               m.role AS member_role,
               m.status AS member_status
        FROM collab_groups g
        JOIN collab_group_members m ON g.group_id = m.group_id
        WHERE m.agent_id = %s
        ORDER BY g.created_at DESC
    """
    rows = execute_query(sql, (agent_id,))
    return [_row_to_dict(r) for r in rows]


def cleanup_expired_groups(max_age_hours: int = 72) -> int:
    sql = """
        UPDATE collab_groups
        SET status = 'ARCHIVED', updated_at = NOW()
        WHERE status = 'ACTIVE'
          AND created_at < NOW() - INTERVAL '%s hours'
    """
    return execute(sql, (max_age_hours,))


def get_collab_stats() -> Dict[str, Any]:
    group_stats = execute_query_one("""
        SELECT COUNT(*) AS total_groups,
               COUNT(*) FILTER (WHERE status = 'ACTIVE') AS active_groups,
               COUNT(*) FILTER (WHERE status = 'ARCHIVED') AS archived_groups
        FROM collab_groups
    """)
    member_stats = execute_query_one("""
        SELECT COUNT(*) AS total_members,
               COUNT(*) FILTER (WHERE status = 'ACTIVE') AS active_members
        FROM collab_group_members
    """)
    share_stats = execute_query_one("""
        SELECT COUNT(*) AS total_shares
        FROM collab_group_shares
    """)
    return {
        "groups": sanitize_row(group_stats) if group_stats else {},
        "members": sanitize_row(member_stats) if member_stats else {},
        "shares": sanitize_row(share_stats) if share_stats else {},
    }


def create_group_loop(group_id: int, title: str, goal_definition: dict, agent_id: str, **kwargs) -> int:
    from .loop_api import create_loop
    loop_id = create_loop(
        title=title,
        goal_definition=goal_definition,
        stop_conditions=kwargs.get("stop_conditions", {"max_iterations": 10, "timeout_minutes": 60, "consecutive_passes": 2}),
        evaluation_config=kwargs.get("evaluation_config", {"type": "AGGREGATE"}),
        owned_by_agent=agent_id,
        collab_group_id=group_id,
        **{k: v for k, v in kwargs.items() if k not in ("stop_conditions", "evaluation_config")}
    )
    return loop_id

def get_group_loop_status(group_id: int) -> Dict[str, Any]:
    rows = execute_query("""
        SELECT e.entity_id, e.title, e.status, m.collab_group_id
        FROM entities e JOIN loop_meta m ON e.entity_id = m.entity_id
        WHERE m.collab_group_id = %s AND e.entity_type = 'LOOP_DEFINITION'
    """, (group_id,))
    return {"group_id": group_id, "loops": [_row_to_dict(r) for r in rows]}
