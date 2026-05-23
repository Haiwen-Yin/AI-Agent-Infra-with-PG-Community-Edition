"""PostgreSQL Memory System v2.2.0 - Task Plan API

Task plan creation, step management, breakpoint recovery,
tool call auditing, and dependency tracking.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "CANCELLED"})
_STEP_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "SKIPPED"})
_ALLOWED_PLAN_UPDATES = frozenset({"goal", "priority", "strategy", "result_summary", "status"})
_ALLOWED_STEP_UPDATES = frozenset({"description", "tool_name", "tool_input", "tool_output", "status"})


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in row.items():
        lk = key.lower()
        if isinstance(value, str) and lk in (
            "tool_input", "tool_output", "context_data",
        ):
            try:
                result[lk] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[lk] = value
        else:
            result[lk] = value
    return result


def create_plan(agent_id: str, goal: str, priority: int = 5,
                strategy: Optional[str] = None) -> str:
    sql = """
        INSERT INTO task_plans (agent_id, goal, status, priority, strategy)
        VALUES (%s, %s, 'PENDING', %s, %s)
        RETURNING plan_id
    """
    return execute_insert_returning_id(sql, (
        agent_id, goal, priority, strategy,
    ))


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT plan_id, agent_id, goal, status, priority, strategy, result_summary,
               created_at, updated_at, completed_at
        FROM task_plans
        WHERE plan_id = %s
    """
    row = execute_query_one(sql, (plan_id,))
    if row is None:
        return None
    return _row_to_dict(row)


def update_plan(plan_id: str, **kwargs: Any) -> bool:
    valid = {k: v for k, v in kwargs.items() if k in _ALLOWED_PLAN_UPDATES}
    if not valid:
        return False

    set_parts = []
    values: List[Any] = []
    for key, value in valid.items():
        if key == "status" and value in _TERMINAL_STATUSES:
            set_parts.append("completed_at = NOW()")
        set_parts.append("{} = %s".format(key))
        values.append(value)

    if not set_parts:
        return False

    set_parts.append("updated_at = NOW()")
    values.append(plan_id)
    sql = "UPDATE task_plans SET {} WHERE plan_id = %s".format(', '.join(set_parts))
    return execute(sql, values) > 0


def add_step(plan_id: str, plan_status: str, description: str, step_order: int,
             tool_name: Optional[str] = None, tool_input: Optional[Any] = None) -> str:
    sql = """
        INSERT INTO task_steps (plan_id, plan_status, step_order, description,
                                tool_name, tool_input, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')
        RETURNING step_id
    """
    return execute_insert_returning_id(sql, (
        plan_id, plan_status, step_order, description,
        tool_name,
        json.dumps(tool_input) if tool_input is not None else None,
    ))


def update_step(step_id: str, **kwargs: Any) -> bool:
    valid = {k: v for k, v in kwargs.items() if k in _ALLOWED_STEP_UPDATES}
    if not valid:
        return False

    set_parts = []
    values: List[Any] = []
    for key, value in valid.items():
        if key in ("tool_input", "tool_output"):
            values.append(json.dumps(value) if value is not None else None)
        else:
            values.append(value)
        set_parts.append("{} = %s".format(key))

    if "status" in valid:
        if valid["status"] == "RUNNING":
            set_parts.append("started_at = NOW()")
        elif valid["status"] in _STEP_TERMINAL_STATUSES:
            set_parts.append("completed_at = NOW()")

    values.append(step_id)
    sql = "UPDATE task_steps SET {} WHERE step_id = %s".format(', '.join(set_parts))
    return execute(sql, values) > 0


def get_plan_steps(plan_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT step_id, plan_id, plan_status, step_order, description,
               tool_name, tool_input, tool_output, status,
               started_at, completed_at
        FROM task_steps
        WHERE plan_id = %s
        ORDER BY step_order
    """
    rows = execute_query(sql, (plan_id,))
    return [_row_to_dict(r) for r in rows]


def add_dependency(source_plan_id: str, target_plan_id: str, dep_type: str) -> str:
    sql = """
        INSERT INTO task_dependencies (source_plan_id, target_plan_id, dep_type)
        VALUES (%s, %s, %s)
        RETURNING dep_id
    """
    return execute_insert_returning_id(sql, (
        source_plan_id, target_plan_id, dep_type,
    ))


def get_plan_dependencies(plan_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT dep_id, source_plan_id, target_plan_id, dep_type, created_at
        FROM task_dependencies
        WHERE source_plan_id = %s OR target_plan_id = %s
        ORDER BY created_at
    """
    return [_row_to_dict(r) for r in execute_query(sql, (plan_id, plan_id))]


def log_tool_call(plan_id: str, step_id: Optional[str] = None,
                  tool_name: Optional[str] = None,
                  tool_input: Optional[Any] = None,
                  tool_output: Optional[Any] = None,
                  status: str = "PENDING",
                  duration_ms: Optional[int] = None) -> str:
    sql = """
        INSERT INTO task_tool_calls (plan_id, step_id, tool_name,
                                     tool_input, tool_output, status, duration_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING call_id
    """
    return execute_insert_returning_id(sql, (
        plan_id, step_id, tool_name,
        json.dumps(tool_input) if tool_input is not None else None,
        json.dumps(tool_output) if tool_output is not None else None,
        status, duration_ms,
    ))


def save_snapshot(plan_id: str, snapshot_type: str, context_data: Any) -> str:
    sql = """
        INSERT INTO task_context_snapshots (plan_id, snapshot_type, context_data)
        VALUES (%s, %s, %s)
        RETURNING snapshot_id
    """
    return execute_insert_returning_id(sql, (
        plan_id,
        snapshot_type,
        json.dumps(context_data) if context_data is not None else None,
    ))


def list_plans(agent_id: Optional[str] = None, status: Optional[str] = None,
               limit: int = 50) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []
    if agent_id is not None:
        conditions.append("agent_id = %s")
        params.append(agent_id)
    if status is not None:
        conditions.append("status = %s")
        params.append(status)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    params.append(limit)
    sql = """
        SELECT plan_id, agent_id, goal, status, priority, strategy, result_summary,
               created_at, updated_at, completed_at
        FROM task_plans
        {}
        ORDER BY created_at DESC
        LIMIT %s
    """.format(where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def delete_plan(plan_id: str) -> bool:
    execute("DELETE FROM task_tool_calls WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_context_snapshots WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_steps WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_dependencies WHERE source_plan_id = %s OR target_plan_id = %s",
            (plan_id, plan_id))
    return execute("DELETE FROM task_plans WHERE plan_id = %s", (plan_id,)) > 0