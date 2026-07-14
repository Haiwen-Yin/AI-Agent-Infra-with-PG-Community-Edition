"""AI Agent Infra v3.10.1 - PG Community Edition - Task Plan API

Task plan creation, step management, dependency tracking,
snapshot/restore, and plan statistics.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)

_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "CANCELLED"})
_STEP_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "SKIPPED"})
_ALLOWED_PLAN_UPDATES = frozenset({"goal", "priority", "strategy", "result_summary", "status", "branch_id"})
_ALLOWED_STEP_UPDATES = frozenset({"description", "tool_name", "tool_input", "tool_output", "status", })


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


def create_plan(
    agent_id: str,
    goal: str,
    priority: int = 5,
    strategy: Optional[str] = None,
    branch_id: Optional[str] = None,
) -> str:
    sql = """
        INSERT INTO task_plans (agent_id, goal, status, priority, strategy, branch_id, created_at, updated_at)
        VALUES (%s, %s, 'PENDING', %s, %s, %s, NOW(), NOW())
        RETURNING plan_id
    """
    return execute_insert_returning_id(sql, (
        agent_id, goal, priority, strategy, branch_id,
    ), id_column="plan_id")


def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id,
               created_at, updated_at
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
            set_parts.append("updated_at = NOW()")
        set_parts.append("{} = %s".format(key))
        values.append(value)

    if not set_parts:
        return False

    set_parts.append("updated_at = NOW()")
    values.append(plan_id)
    sql = "UPDATE task_plans SET {} WHERE plan_id = %s".format(", ".join(set_parts))
    return execute(sql, values) > 0


def delete_plan(plan_id: str) -> bool:
    execute("DELETE FROM task_tool_calls WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_context_snapshots WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_steps WHERE plan_id = %s", (plan_id,))
    execute("DELETE FROM task_dependencies WHERE source_plan_id = %s OR target_plan_id = %s",
            (plan_id, plan_id))
    return execute("DELETE FROM task_plans WHERE plan_id = %s", (plan_id,)) > 0


def list_plans(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []
    if agent_id is not None:
        conditions.append("agent_id = %s")
        params.append(agent_id)
    if status is not None:
        conditions.append("status = %s")
        params.append(status)

    where = "WHERE {}".format(" AND ".join(conditions)) if conditions else ""
    params.extend([limit, offset])
    sql = """
        SELECT plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id,
               created_at, updated_at
        FROM task_plans
        {where}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """.format(where=where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def cancel_plan(plan_id: str) -> bool:
    sql = """
        UPDATE task_plans
        SET status = 'CANCELLED' = NOW(), updated_at = NOW()
        WHERE plan_id = %s AND status NOT IN ('SUCCESS', 'FAILED', 'CANCELLED')
    """
    if execute(sql, (plan_id,)) > 0:
        step_sql = """
            UPDATE task_steps
            SET status = 'SKIPPED' = NOW()
            WHERE plan_id = %s AND status IN ('PENDING', 'RUNNING')
        """
        execute(step_sql, (plan_id,))
        return True
    return False


def create_step(
    plan_id: str,
    description: str,
    step_order: int,
    tool_name: Optional[str] = None,
    tool_input: Optional[Any] = None,
    
) -> str:
    plan = get_plan(plan_id)
    plan_status = plan["status"] if plan else "PENDING"
    sql = """
        INSERT INTO task_steps (plan_id, plan_status, step_order, description,
                                tool_name, tool_input, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', NOW())
        RETURNING step_id
    """
    return execute_insert_returning_id(sql, (
        plan_id, plan_status, step_order, description,
        tool_name,
        json.dumps(tool_input) if tool_input is not None else None,
    ), id_column="step_id")


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
            set_parts.append("updated_at = NOW()")
        elif valid["status"] in _STEP_TERMINAL_STATUSES:
            set_parts.append("updated_at = NOW()")

    values.append(step_id)
    sql = "UPDATE task_steps SET {} WHERE step_id = %s".format(", ".join(set_parts))
    return execute(sql, values) > 0


def delete_step(step_id: str) -> bool:
    sql = "DELETE FROM task_steps WHERE step_id = %s"
    return execute(sql, (step_id,)) > 0


def list_steps(plan_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT step_id, plan_id, plan_status, step_order, description,
               tool_name, tool_input, tool_output, status,
               created_at
        FROM task_steps
        WHERE plan_id = %s
        ORDER BY step_order
    """
    rows = execute_query(sql, (plan_id,))
    return [_row_to_dict(r) for r in rows]


def create_dependency(
    source_plan_id: str,
    target_plan_id: str,
    dep_type: str,
) -> str:
    sql = """
        INSERT INTO task_dependencies (source_plan_id, target_plan_id, dep_type, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING dep_id
    """
    return execute_insert_returning_id(sql, (
        source_plan_id, target_plan_id, dep_type,
    ), id_column="dep_id")


def delete_dependency(dep_id: str) -> bool:
    sql = "DELETE FROM task_dependencies WHERE dep_id = %s"
    return execute(sql, (dep_id,)) > 0


def list_dependencies(plan_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT dep_id, source_plan_id, target_plan_id, dep_type, created_at
        FROM task_dependencies
        WHERE source_plan_id = %s OR target_plan_id = %s
        ORDER BY created_at
    """
    return [_row_to_dict(r) for r in execute_query(sql, (plan_id, plan_id))]


def create_snapshot(plan_id: str, snapshot_type: str, context_data: Any) -> str:
    sql = """
        INSERT INTO task_context_snapshots (plan_id, snapshot_type, context_data, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING snapshot_id
    """
    return execute_insert_returning_id(sql, (
        plan_id,
        snapshot_type,
        json.dumps(context_data) if context_data is not None else None,
    ), id_column="snapshot_id")


def restore_snapshot(snapshot_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT snapshot_id, plan_id, snapshot_type, context_data, created_at
        FROM task_context_snapshots
        WHERE snapshot_id = %s
    """
    row = execute_query_one(sql, (snapshot_id,))
    if row is None:
        return None
    result = _row_to_dict(row)
    context_data = result.get("context_data")
    if isinstance(context_data, str):
        try:
            context_data = json.loads(context_data)
            result["context_data"] = context_data
        except (json.JSONDecodeError, TypeError):
            pass
    plan_id = result.get("plan_id")
    if plan_id and isinstance(context_data, dict):
        if "goal" in context_data:
            update_plan(plan_id, goal=context_data["goal"])
        if "strategy" in context_data:
            update_plan(plan_id, strategy=context_data["strategy"])
    return result


def get_plan_stats() -> Dict[str, Any]:
    by_status = execute_query("""
        SELECT status, COUNT(*) AS cnt
        FROM task_plans
        GROUP BY status
    """)
    total = execute_query_one("""
        SELECT COUNT(*) AS total,
               AVG(priority) AS avg_priority
        FROM task_plans
    """)
    steps_total = execute_query_one("""
        SELECT COUNT(*) AS total_steps,
               COUNT(*) FILTER (WHERE status = 'PENDING') AS pending_steps,
               COUNT(*) FILTER (WHERE status = 'RUNNING') AS running_steps,
               COUNT(*) FILTER (WHERE status = 'SUCCESS') AS success_steps,
               COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_steps
        FROM task_steps
    """)
    return {
        "plans": {
            "total": total["total"] if total else 0,
            "avg_priority": float(total["avg_priority"]) if total and total.get("avg_priority") else 0,
            "by_status": {r["status"]: r["cnt"] for r in by_status},
        },
        "steps": _row_to_dict(steps_total) if steps_total else {},
    }


def bind_loop_to_step(step_id: int, loop_id: int, binding_type: str = 'COMPLETION', auto_start: str = 'N') -> int:
    from .loop_api import start_run
    binding_id = execute_insert_returning_id("""
        INSERT INTO task_loop_binding (step_id, loop_id, binding_type, auto_start, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING binding_id
    """, (step_id, loop_id, binding_type, auto_start), id_column="binding_id")
    execute("UPDATE task_steps SET loop_id = %s, step_completion_type = 'LOOP' WHERE step_id = %s", (loop_id, step_id))
    if auto_start == 'Y':
        start_run(loop_id, ...)
    return binding_id

def get_step_loop(step_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one("""
        SELECT b.binding_id, b.step_id, b.loop_id, b.binding_type, b.auto_start, b.created_at
        FROM task_loop_binding b WHERE b.step_id = %s
    """, (step_id,))
    return _row_to_dict(row) if row else None


def distribute_plan_to_group(plan_id, group_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"distribute_plan_to_group is not yet implemented in PostgreSQL edition")


def get_branch_plans(branch_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"get_branch_plans is not yet implemented in PostgreSQL edition")
