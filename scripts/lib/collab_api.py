"""PostgreSQL Memory System v2.3.0 - Collaboration Group API

Collaboration group lifecycle management, membership, and group memory sharing.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id
from .workspace_api import create_workspace

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"metadata", "context"}

_ALLOWED_UPDATE_FIELDS = frozenset({
    "group_name", "group_type", "description", "sharing_policy",
    "coordinator_agent_id", "status", "metadata",
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


def create_collab_group(
    group_name: str,
    group_type: str,
    description: Optional[str] = None,
    sharing_policy: str = 'OPEN',
    coordinator_agent_id: Optional[str] = None,
) -> int:
    ws_sql = """
        INSERT INTO workspaces (workspace_name, workspace_type, isolation_mode, status)
        VALUES (%s, 'COLLAB_GROUP', 'SHARED', 'ACTIVE')
        RETURNING workspace_id
    """
    ws_id = execute_insert_returning_id(ws_sql, (group_name + ' (Shared)',), id_column='workspace_id')
    meta_val = None
    sql = """
        INSERT INTO collab_groups (group_name, group_type, description,
                                    workspace_id, sharing_policy, coordinator_agent_id,
                                    status, metadata, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s,
                'ACTIVE', %s, NOW(), NOW())
        RETURNING group_id
    """
    return execute_insert_returning_id(sql, (
        group_name, group_type, description,
        ws_id, sharing_policy, coordinator_agent_id, meta_val,
    ), id_column="group_id")


def get_collab_group(group_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT group_id, group_name, group_type, description,
               workspace_id, coordinator_agent_id, sharing_policy,
               status, metadata, created_at, updated_at
        FROM collab_groups
        WHERE group_id = %s
    """
    row = execute_query_one(sql, (group_id,))
    return _row_to_dict(row) if row else None


def update_collab_group(group_id: int, **kwargs: Any) -> bool:
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
    sql = "UPDATE collab_groups SET {} WHERE group_id = %s".format(', '.join(set_parts))
    return execute(sql, values) > 0


def add_group_member(
    group_id: int,
    agent_id: str,
    role: str = 'CONTRIBUTOR',
) -> int:
    personal_workspace_id = None
    if role in ('LEAD', 'CONTRIBUTOR', 'MEMBER'):
        personal_workspace_id = create_workspace(
            name="personal-in-group-{}".format(group_id),
            workspace_type="PERSONAL_IN_GROUP",
        )
    sql = """
        INSERT INTO collab_group_members (group_id, agent_id, role,
                                           personal_workspace_id, status, joined_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', NOW())
        ON CONFLICT (group_id, agent_id) DO UPDATE
            SET role = EXCLUDED.role,
                status = 'ACTIVE',
                personal_workspace_id = COALESCE(collab_group_members.personal_workspace_id, EXCLUDED.personal_workspace_id)
        RETURNING member_id
    """
    return execute_insert_returning_id(sql, (
        group_id, agent_id, role, personal_workspace_id,
    ), id_column="member_id")


def remove_group_member(group_id: int, agent_id: str) -> bool:
    sql = """
        UPDATE collab_group_members
        SET status = 'REMOVED'
        WHERE group_id = %s AND agent_id = %s AND status = 'ACTIVE'
    """
    return execute(sql, (group_id, agent_id)) > 0


def list_group_members(group_id: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT member_id, group_id, agent_id, role,
               personal_workspace_id, joined_at, status
        FROM collab_group_members
        WHERE group_id = %s
        ORDER BY joined_at ASC
    """
    rows = execute_query(sql, (group_id,))
    return [_row_to_dict(r) for r in rows]


def get_agent_groups(agent_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT cg.group_id, cg.group_name, cg.group_type, cg.description,
               cg.workspace_id, cg.coordinator_agent_id, cg.sharing_policy,
               cg.status, cg.metadata, cg.created_at, cg.updated_at,
               cgm.role, cgm.joined_at AS member_joined_at
        FROM collab_groups cg
        JOIN collab_group_members cgm ON cg.group_id = cgm.group_id
        WHERE cgm.agent_id = %s AND cgm.status = 'ACTIVE'
        ORDER BY cg.updated_at DESC
    """
    rows = execute_query(sql, (agent_id,))
    return [_row_to_dict(r) for r in rows]


def share_memory_to_group(
    group_id: int,
    memory_id: int,
    shared_by: str,
) -> int:
    context_val = json.dumps({"group_id": group_id})
    sql = """
        INSERT INTO agent_collaboration (source_agent_id, target_agent_id,
                                          col_type, entity_id, context,
                                          strength, created_at, updated_at)
        VALUES (%s, %s, 'GROUP_SHARE', %s, %s,
                1.0, NOW(), NOW())
        ON CONFLICT DO NOTHING
        RETURNING collab_id
    """
    return execute_insert_returning_id(sql, (
        shared_by, None, memory_id, context_val,
    ), id_column="collab_id")


def get_group_shared_memories(group_id: int) -> List[Dict[str, Any]]:
    context_val = '%"group_id": {}%'.format(group_id)
    sql = """
        SELECT collab_id, source_agent_id, target_agent_id,
               col_type, entity_id, context, strength,
               created_at, updated_at
        FROM agent_collaboration
        WHERE col_type = 'GROUP_SHARE'
          AND context::text LIKE %s
        ORDER BY created_at DESC
    """
    rows = execute_query(sql, (context_val,))
    return [_row_to_dict(r) for r in rows]


def delete_collab_group(group_id: int) -> bool:
    sql = """
        UPDATE collab_groups
        SET status = 'ARCHIVED', updated_at = NOW()
        WHERE group_id = %s AND status != 'ARCHIVED'
    """
    return execute(sql, (group_id,)) > 0
