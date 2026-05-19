"""PostgreSQL Memory System v2.0.0 - Agent API

Agent management, sessions, access logging, and collaboration.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)


def register_agent(agent_id, agent_name, agent_type='general',
                   capabilities=None, description='', permission_level='READ_WRITE'):
    sql = """
        INSERT INTO agent_registry (agent_id, agent_name, agent_type, capabilities,
                                    description, permission_level, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
        ON CONFLICT (agent_id) DO NOTHING
    """
    affected = execute(sql, (
        agent_id,
        agent_name,
        agent_type,
        json.dumps(capabilities or []),
        description,
        permission_level,
    ))
    return affected > 0


def get_agent(agent_id):
    sql = """
        SELECT agent_id, agent_name, agent_type, capabilities, description,
               permission_level, status, pending_recovery, recovered_count,
               created_at, updated_at
        FROM agent_registry
        WHERE agent_id = %s
    """
    row = execute_query_one(sql, (agent_id,))
    if row is None:
        return None
    if isinstance(row.get('capabilities'), str):
        try:
            row['capabilities'] = json.loads(row['capabilities'])
        except (json.JSONDecodeError, TypeError):
            pass
    return row


def list_agents(agent_type=None, status='ACTIVE'):
    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status)

    if agent_type:
        conditions.append("agent_type = %s")
        params.append(agent_type)

    where = ' AND '.join(conditions) if conditions else '1=1'

    sql = """
        SELECT agent_id, agent_name, agent_type, capabilities,
               permission_level, status, created_at
        FROM agent_registry
        WHERE {}
        ORDER BY created_at
    """.format(where)

    rows = execute_query(sql, params)
    for r in rows:
        if isinstance(r.get('capabilities'), str):
            try:
                r['capabilities'] = json.loads(r['capabilities'])
            except (json.JSONDecodeError, TypeError):
                pass
    return rows


def disable_agent(agent_id, reason=''):
    affected = execute(
        "UPDATE agent_registry SET status = 'DISABLED', updated_at = now(), pending_recovery = TRUE WHERE agent_id = %s AND status != 'DISABLED'",
        (agent_id,)
    )
    if affected > 0:
        execute(
            """INSERT INTO agent_permission_log (agent_id, old_status, new_status, change_reason, status)
               VALUES (%s, 'ACTIVE', 'DISABLED', %s, 'COMPLETED')""",
            (agent_id, reason)
        )
    return affected > 0


def enable_agent(agent_id):
    affected = execute(
        """UPDATE agent_registry
           SET status = 'ACTIVE', updated_at = now(), pending_recovery = FALSE,
               recovered_count = recovered_count + 1
           WHERE agent_id = %s AND status = 'DISABLED'""",
        (agent_id,)
    )
    if affected > 0:
        execute(
            """INSERT INTO agent_permission_log (agent_id, old_status, new_status, change_reason, status)
               VALUES (%s, 'DISABLED', 'ACTIVE', 'Agent re-enabled', 'COMPLETED')""",
            (agent_id,)
        )
    return affected > 0


def create_session(agent_id, working_memory_id=None):
    session_id = "session-{}-{}".format(agent_id, int(time.time()))
    sql = """
        INSERT INTO agent_session (session_id, agent_id, is_active, context_snapshot, working_memory_id)
        VALUES (%s, %s, TRUE, %s, %s)
    """
    try:
        execute(sql, (session_id, agent_id, json.dumps({}), working_memory_id))
        return session_id
    except Exception as e:
        logger.error("Failed to create session: %s", e)
        return None


def update_session_context(session_id, context):
    if isinstance(context, dict):
        context = json.dumps(context)
    sql = "UPDATE agent_session SET context_snapshot = %s, last_activity = now() WHERE session_id = %s AND is_active = TRUE"
    return execute(sql, (context, session_id)) > 0


def close_session(session_id):
    sql = "UPDATE agent_session SET is_active = FALSE, end_time = now() WHERE session_id = %s"
    return execute(sql, (session_id,)) > 0


def get_active_sessions(agent_id=None):
    if agent_id:
        sql = """
            SELECT s.session_id, s.agent_id, a.agent_name,
                   s.working_memory_id, s.start_time, s.last_activity
            FROM agent_session s
            LEFT JOIN agent_registry a ON a.agent_id = s.agent_id
            WHERE s.is_active = TRUE AND s.agent_id = %s
            ORDER BY s.start_time DESC
        """
        return execute_query(sql, (agent_id,))
    else:
        sql = """
            SELECT s.session_id, s.agent_id, a.agent_name,
                   s.working_memory_id, s.start_time, s.last_activity
            FROM agent_session s
            LEFT JOIN agent_registry a ON a.agent_id = s.agent_id
            WHERE s.is_active = TRUE
            ORDER BY s.start_time DESC
        """
        return execute_query(sql)


def log_access(agent_id, entity_id, access_type='READ'):
    sql = """
        INSERT INTO entity_access_log (agent_id, entity_id, access_type)
        VALUES (%s, %s, %s)
    """
    execute(sql, (agent_id, entity_id, access_type))


def get_access_history(agent_id, limit=50):
    sql = """
        SELECT log_id, agent_id, entity_id, access_type, access_time
        FROM entity_access_log
        WHERE agent_id = %s
        ORDER BY access_time DESC
        LIMIT %s
    """
    return execute_query(sql, (agent_id, limit))


def request_collaboration(sharing_agent, receiving_agent, entity_id, reason=''):
    sql = """
        INSERT INTO agent_collaboration (sharing_agent, receiving_agent,
                                         memory_id, share_reason, status)
        VALUES (%s, %s, %s, %s, 'PENDING')
        RETURNING collab_id
    """
    try:
        return execute_insert_returning_id(sql, (
            sharing_agent, receiving_agent, entity_id, reason,
        ), id_column='collab_id')
    except Exception as e:
        logger.error("Failed to request collaboration: %s", e)
        return None


def approve_collaboration(collab_id):
    sql = """
        UPDATE agent_collaboration
        SET status = 'APPROVED', approved_at = now()
        WHERE collab_id = %s AND status = 'PENDING'
    """
    return execute(sql, (collab_id,)) > 0


def reject_collaboration(collab_id):
    sql = """
        UPDATE agent_collaboration
        SET status = 'REJECTED'
        WHERE collab_id = %s AND status = 'PENDING'
    """
    return execute(sql, (collab_id,)) > 0


def get_pending_requests(agent_id, role='receiving'):
    if role == 'receiving':
        sql = """
            SELECT collab_id, sharing_agent, receiving_agent, memory_id,
                   share_reason, status, created_at
            FROM agent_collaboration
            WHERE receiving_agent = %s AND status = 'PENDING'
            ORDER BY created_at DESC
        """
    else:
        sql = """
            SELECT collab_id, sharing_agent, receiving_agent, memory_id,
                   share_reason, status, created_at
            FROM agent_collaboration
            WHERE sharing_agent = %s AND status = 'PENDING'
            ORDER BY created_at DESC
        """
    return execute_query(sql, (agent_id,))
