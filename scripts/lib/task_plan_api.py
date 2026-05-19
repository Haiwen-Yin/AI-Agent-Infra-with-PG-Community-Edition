"""PostgreSQL Memory System v2.0.0 - Task Plan API

Task plan management with steps, snapshots, tool calls, and dependencies.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)


def create_task_plan(plan_name, plan_type='task', description=None, goal=None,
                     priority=2, steps=None, metadata=None, tags=None):
    plan_sql = """
        INSERT INTO task_plans (plan_name, plan_type, description, goal,
                                priority, status, metadata, tags)
        VALUES (%s, %s, %s, %s, %s, 'PENDING', %s, %s)
        RETURNING plan_id
    """
    plan_id = execute_insert_returning_id(plan_sql, (
        plan_name,
        plan_type,
        description,
        goal,
        priority,
        json.dumps(metadata or {}),
        json.dumps(tags or []),
    ), id_column='plan_id')

    if steps:
        step_sql = """
            INSERT INTO task_steps (plan_id, step_order, step_name, action,
                                    tools_used, status)
            VALUES (%s, %s, %s, %s, %s, 'PENDING')
        """
        for i, step in enumerate(steps):
            step_name = step.get('name', step.get('step_name', 'Step {}'.format(i + 1)))
            action = step.get('action', '')
            tools_used = step.get('tools_used', [])
            execute(step_sql, (
                plan_id, i + 1, step_name, action,
                json.dumps(tools_used if isinstance(tools_used, list) else []),
            ))

    save_snapshot(plan_id, {
        'next_action': steps[0].get('action') if steps else None,
        'step_index': 0,
    }, snapshot_type='AUTO')

    return plan_id


def get_task_plan(plan_id):
    sql = """
        SELECT plan_id, plan_name, plan_type, description, goal,
               priority, status, metadata, tags,
               created_at, started_at, updated_at, completed_at
        FROM task_plans
        WHERE plan_id = %s
    """
    row = execute_query_one(sql, (plan_id,))
    if row is None:
        return None
    for col in ('metadata', 'tags'):
        val = row.get(col)
        if isinstance(val, str):
            try:
                row[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return row


def get_task_steps(plan_id):
    sql = """
        SELECT step_id, plan_id, step_order, step_name, action,
               tools_used, status, result, error_msg,
               created_at, started_at, completed_at
        FROM task_steps
        WHERE plan_id = %s
        ORDER BY step_order ASC
    """
    rows = execute_query(sql, (plan_id,))
    for r in rows:
        for col in ('tools_used',):
            val = r.get(col)
            if isinstance(val, str):
                try:
                    r[col] = json.loads(val)
                except (json.JSONDecodeError, TypeError):
                    pass
    return rows


def update_step_status(plan_id, step_id, status, result=None, error_msg=None):
    if status == 'SUCCESS':
        status = 'COMPLETED'
    elif status == 'IN_PROGRESS':
        status = 'ACTIVE'
    updates = {"status": status}
    if result is not None:
        updates["result"] = result
    if error_msg is not None:
        updates["error_msg"] = error_msg

    if status == 'IN_PROGRESS' or status == 'ACTIVE':
        updates["started_at"] = "now()"
    elif status in ('SUCCESS', 'COMPLETED', 'FAILED', 'BLOCKED', 'SKIPPED'):
        updates["completed_at"] = "now()"

    set_parts = []
    values = []
    for k, v in updates.items():
        if v == "now()":
            set_parts.append("{} = now()".format(k))
        else:
            set_parts.append("{} = %s".format(k))
            values.append(v)

    values.extend([step_id, plan_id])
    sql = "UPDATE task_steps SET {} WHERE step_id = %s AND plan_id = %s".format(', '.join(set_parts))
    affected = execute(sql, values)

    if affected > 0:
        new_status = _derive_plan_status(plan_id)
        execute("UPDATE task_plans SET status = %s, updated_at = now() WHERE plan_id = %s",
                (new_status, plan_id))
        save_snapshot(plan_id, {"trigger": "step_{}".format(status), "step_id": step_id}, snapshot_type='AUTO')

    return affected > 0


def save_snapshot(plan_id, context, snapshot_type='MANUAL'):
    execute(
        "UPDATE task_context_snapshots SET is_latest = FALSE WHERE plan_id = %s AND is_latest = TRUE",
        (plan_id,)
    )

    context_data = context if isinstance(context, dict) else {"context": context}
    next_action = context_data.get('next_action')

    sql = """
        INSERT INTO task_context_snapshots (plan_id, snapshot_type, context_data,
                                            next_action, is_latest, trigger_reason)
        VALUES (%s, %s, %s, %s, TRUE, %s)
        RETURNING snapshot_id
    """
    return execute_insert_returning_id(sql, (
        plan_id,
        snapshot_type,
        json.dumps(context_data),
        next_action,
        json.dumps({"trigger": context_data.get("trigger", snapshot_type)}),
    ), id_column='snapshot_id')


def resume_task(plan_id):
    plan = get_task_plan(plan_id)
    if plan is None:
        return None

    snapshot_row = execute_query_one(
        """SELECT snapshot_id, context_data, next_action, snapshot_type, created_at
           FROM task_context_snapshots
           WHERE plan_id = %s AND is_latest = TRUE
           ORDER BY created_at DESC
           LIMIT 1""",
        (plan_id,)
    )

    context = {}
    if snapshot_row:
        context = snapshot_row.get('context_data', '{}')
        if isinstance(context, str):
            try:
                context = json.loads(context)
            except (json.JSONDecodeError, TypeError):
                context = {}

    incomplete_steps = execute_query(
        """SELECT step_id, step_order, step_name, action, status
           FROM task_steps
           WHERE plan_id = %s AND status IN ('PENDING', 'IN_PROGRESS', 'ACTIVE', 'BLOCKED')
           ORDER BY step_order ASC""",
        (plan_id,)
    )

    execute(
        "UPDATE task_plans SET status = 'ACTIVE', updated_at = now() WHERE plan_id = %s",
        (plan_id,)
    )

    return {
        'plan_id': plan_id,
        'context': context,
        'next_action': snapshot_row.get('next_action') if snapshot_row else None,
        'snapshot_time': snapshot_row.get('created_at') if snapshot_row else None,
        'incomplete_steps': incomplete_steps,
    }


def log_tool_call(plan_id, tool_name, action, step_id=None, status='SUCCESS',
                  result_size=None, duration_ms=None):
    if status == 'SUCCESS':
        status = 'COMPLETED'
    sql = """
        INSERT INTO task_tool_calls (plan_id, step_id, tool_name, action,
                                     status, result_size, duration_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING call_id
    """
    return execute_insert_returning_id(sql, (
        plan_id, step_id, tool_name, action, status, result_size, duration_ms,
    ), id_column='call_id')


def add_dependency(source_plan_id, target_plan_id, dependency_type='HARD',
                   condition=None):
    sql = """
        INSERT INTO task_dependencies (source_plan_id, target_plan_id,
                                       dependency_type, condition)
        VALUES (%s, %s, %s, %s)
        RETURNING dependency_id
    """
    return execute_insert_returning_id(sql, (
        source_plan_id, target_plan_id, dependency_type, condition,
    ), id_column='dependency_id')


def search_completed_tasks(plan_type=None, status=None, limit=50):
    conditions = []
    params = []

    if plan_type:
        conditions.append("plan_type = %s")
        params.append(plan_type)

    if status:
        conditions.append("status = %s")
        params.append(status)
    else:
        conditions.append("status IN ('COMPLETED', 'FAILED', 'CANCELLED')")

    where = ' AND '.join(conditions)
    params.append(limit)

    sql = """
        SELECT plan_id, plan_name, plan_type, description, goal,
               priority, status, created_at, completed_at
        FROM task_plans
        WHERE {}
        ORDER BY completed_at DESC
        LIMIT %s
    """.format(where)

    return execute_query(sql, params)


def _derive_plan_status(plan_id):
    rows = execute_query(
        "SELECT status, COUNT(*) AS cnt FROM task_steps WHERE plan_id = %s GROUP BY status",
        (plan_id,)
    )
    if not rows:
        return 'PENDING'

    counts = {r['status']: r['cnt'] for r in rows}
    total = sum(counts.values())

    if total == 0:
        return 'PENDING'

    done = counts.get('COMPLETED', 0) + counts.get('SKIPPED', 0)
    failed = counts.get('FAILED', 0)
    active = counts.get('IN_PROGRESS', 0) + counts.get('ACTIVE', 0) + counts.get('BLOCKED', 0)

    if done == total:
        return 'COMPLETED'
    if failed > 0:
        return 'FAILED'
    if active > 0:
        return 'ACTIVE'
    if done > 0:
        return 'ACTIVE'

    return 'PENDING'
