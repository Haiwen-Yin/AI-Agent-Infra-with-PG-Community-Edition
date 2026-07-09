"""AI Agent Infra v3.10.0 - PG Community Edition - Context Branching API

Context branch lifecycle management: fork, merge, abandon, pause, resume,
branch comparison, conflict detection, and lesson extraction from abandoned branches.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, get_connection

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"context_data", "metadata", "conflicts", "lesson_tags"}


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


def fork_branch(
    workspace_id: int,
    fork_context_id: Optional[int],
    branch_name: str,
    branch_type: str,
    agent_id: str,
    source_agent_id: Optional[str] = None,
    purpose: Optional[str] = None,
    fork_session_id: Optional[int] = None,
) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT branch_manager.fork(%s, %s, %s, %s, %s, %s, %s, %s)",
                [workspace_id, fork_context_id, branch_name, branch_type,
                 agent_id, source_agent_id, purpose, fork_session_id],
            )
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else -1


def get_branch(branch_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        "SELECT branch_manager.get(%s) AS bj", [branch_id]
    )
    if row and row.get("bj"):
        val = row["bj"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return None


def get_branch_tree(workspace_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM branch_manager.get_tree(%s)", [workspace_id]
    )
    flat = [_row_to_dict(r) for r in rows]
    children_map: Dict[str, List] = {}
    roots = []
    for b in flat:
        children_map.setdefault(b.get("parent_branch_id"), []).append(b)
    for b in flat:
        b["children"] = children_map.get(b["branch_id"], [])
    for b in flat:
        if b.get("parent_branch_id") is None:
            roots.append(b)
    return roots


def get_branch_chain(branch_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM branch_manager.get_chain(%s, %s)",
        [branch_id, limit],
    )
    return [_row_to_dict(r) for r in rows]


def diff_branches(branch_a_id: int, branch_b_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM branch_manager.diff(%s, %s)",
        [branch_a_id, branch_b_id],
    )
    return [_row_to_dict(r) for r in rows]


def detect_conflicts(source_branch_id: int, target_branch_id: int) -> Dict[str, Any]:
    row = execute_query_one(
        "SELECT branch_manager.detect_conflicts(%s, %s) AS cj",
        [source_branch_id, target_branch_id],
    )
    if row and row.get("cj"):
        val = row["cj"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return {"total_conflicts": 0}


def merge_branch(
    source_branch_id: int,
    target_branch_id: int,
    merge_type: str = "MERGE",
    merged_by_agent: Optional[str] = None,
    conflict_resolutions: Optional[Dict] = None,
) -> Dict[str, Any]:
    conflicts = detect_conflicts(source_branch_id, target_branch_id)
    total = conflicts.get("total_conflicts", 0)
    if total > 0 and conflict_resolutions is None:
        return {
            "status": "CONFLICTS_DETECTED",
            "conflicts": conflicts,
            "merge_id": None,
            "message": "Conflicts detected. Provide conflict_resolutions to proceed.",
        }
    cr_json = json.dumps(conflict_resolutions) if conflict_resolutions else None
    row = execute_query_one(
        "SELECT branch_manager.merge(%s, %s, %s, %s, %s) AS merge_id",
        [source_branch_id, target_branch_id, merge_type, merged_by_agent, cr_json],
    )
    result = "PARTIAL" if total > 0 else "SUCCESS"
    return {"status": result, "conflicts": conflicts, "merge_id": row["merge_id"] if row else None}


def abandon_branch(branch_id: int, reason: Optional[str] = None) -> bool:
    execute("SELECT branch_manager.abandon(%s, %s)", [branch_id, reason])
    return True


def pause_branch(branch_id: int) -> bool:
    execute("SELECT branch_manager.pause(%s)", [branch_id])
    return True


def resume_branch(branch_id: int) -> bool:
    row = execute_query_one(
        "SELECT branch_manager.resume(%s) AS session_id", [branch_id]
    )
    return row is not None


def get_agent_branches(agent_id: str, status: str = "ACTIVE") -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM branch_manager.get_agent_branches(%s, %s)",
        [agent_id, status],
    )
    return [_row_to_dict(r) for r in rows]


def get_branch_stats(branch_id: int) -> Dict[str, Any]:
    row = execute_query_one(
        "SELECT branch_manager.get_stats(%s) AS sj", [branch_id]
    )
    if row and row.get("sj"):
        val = row["sj"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return {"branch_id": branch_id, "error": "not found"}


def mark_as_lesson(
    branch_id: int,
    context_id: int,
    lesson_type: str,
    lesson_summary: str,
    lesson_detail: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> int:
    row = execute_query_one(
        "SELECT branch_manager.mark_as_lesson(%s, %s, %s, %s, %s, %s) AS entity_id",
        [branch_id, context_id, lesson_type, lesson_summary, lesson_detail, agent_id],
    )
    return row["entity_id"] if row else -1


def extract_lessons(
    branch_id: int,
    auto_confirm: bool = False,
) -> Dict[str, Any]:
    row = execute_query_one(
        "SELECT branch_manager.extract_lessons(%s, %s) AS result",
        [branch_id, auto_confirm],
    )
    if row and row.get("result"):
        val = row["result"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return {"branch_id": branch_id, "error": "extraction failed"}


def cleanup_branches(days_threshold: int = 90) -> int:
    row = execute_query_one(
        "SELECT branch_manager.cleanup(%s) AS deleted_count",
        [days_threshold],
    )
    return row["deleted_count"] if row else 0


def fork_for_spec(workspace_id: int, spec_id: int, branch_name: str,
                  agent_id: str, source_agent_id: Optional[str] = None) -> int:
    from . import spec_api
    spec = spec_api.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Spec {spec_id} not found")
    purpose = f"Implement spec: {spec.get('title', spec_id)}"
    branch_id = fork_branch(
        workspace_id=workspace_id,
        fork_context_id=None,
        branch_name=branch_name,
        branch_type="EXPLORATION",
        agent_id=agent_id,
        source_agent_id=source_agent_id,
        purpose=purpose,
    )
    return branch_id


def validate_for_spec(source_branch_id: int, target_branch_id: int,
                      spec_id: Optional[int] = None,
                      merged_by_agent: Optional[str] = None,
                      conflict_resolutions: Optional[Any] = None) -> Dict[str, Any]:
    result = {"merge_status": None, "validation": None}
    merge_branch(
        source_branch_id=source_branch_id,
        target_branch_id=target_branch_id,
        merged_by_agent=merged_by_agent,
        conflict_resolutions=conflict_resolutions,
    )
    result["merge_status"] = "completed"
    if spec_id:
        from . import spec_api
        validation = spec_api.validate_branch_against_spec(source_branch_id, spec_id)
        result["validation"] = validation
    return result


def fork_parallel(workspace_id: int, agent_ids: List[str],
                  branch_name_prefix: str = "parallel",
                  spec_id: Optional[int] = None,
                  purpose: Optional[str] = None) -> Dict[str, Any]:
    results = []
    for i, agent_id in enumerate(agent_ids):
        branch_name = f"{branch_name_prefix}-{agent_id}-{i+1}"
        branch_purpose = purpose or f"Parallel exploration by {agent_id}"
        if spec_id:
            branch_purpose = f"Implement spec {spec_id}: {branch_purpose}"
        bid = fork_branch(
            workspace_id=workspace_id,
            fork_context_id=None,
            branch_name=branch_name,
            branch_type="PARALLEL",
            agent_id=agent_id,
            purpose=branch_purpose,
        )
        results.append({"branch_id": bid, "agent_id": agent_id, "branch_name": branch_name})
    return {"workspace_id": workspace_id, "branches": results, "count": len(results)}


def compare_branches(branch_a_id: int, branch_b_id: int) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT branch_a, branch_b, common_ancestor, workspace_id,
                  ctx_count_a, ctx_count_b, agent_a, agent_b,
                  type_a, type_b, status_a, status_b
           FROM v_branch_comparison
           WHERE branch_a = %s AND branch_b = %s""",
        [branch_a_id, branch_b_id],
    )
    return [_row_to_dict(r) for r in rows]


def get_branch_detail(branch_id: int) -> Optional[Dict[str, Any]]:
    branch = get_branch(branch_id)
    if branch is None:
        return None
    stats = get_branch_stats(branch_id)
    chain = get_branch_chain(branch_id, limit=10)
    return {
        "branch": branch,
        "stats": stats,
        "recent_contexts": chain,
    }


def list_active_branches(
    workspace_id: Optional[int] = None,
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    branch_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conditions = []
    params: List[Any] = []
    if workspace_id:
        conditions.append("workspace_id = %s")
        params.append(workspace_id)
    if agent_id:
        conditions.append("agent_id = %s")
        params.append(agent_id)
    if status:
        conditions.append("status = %s")
        params.append(status)
    else:
        conditions.append("status IN ('ACTIVE', 'PAUSED')")
    if branch_type:
        conditions.append("branch_type = %s")
        params.append(branch_type)
    params.append(limit)
    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"""
        SELECT branch_id, workspace_id, parent_branch_id, branch_name,
               branch_type, status, agent_id, source_context_id,
               description, is_lesson,
               to_char(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               to_char(merged_at, 'YYYY-MM-DD HH24:MI:SS') AS merged_at,
               to_char(abandoned_at, 'YYYY-MM-DD HH24:MI:SS') AS abandoned_at
        FROM context_branches
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT %s
    """
    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]


def list_branches(workspace_id: Optional[int] = None, agent_id: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    from .connection import execute_query
    conditions = []
    params: List[Any] = []
    if workspace_id is not None:
        conditions.append("workspace_id = %s")
        params.append(workspace_id)
    if agent_id is not None:
        conditions.append("agent_id = %s")
        params.append(agent_id)
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    where = "WHERE {}".format(" AND ".join(conditions)) if conditions else ""
    params.append(limit)
    return execute_query(f"SELECT * FROM context_branches {where} ORDER BY created_at DESC LIMIT %s", params)


def extract_lessons_from_branch(branch_id, agent_id=None):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"extract_lessons_from_branch is not yet implemented in PostgreSQL edition")


def fork_branch_for_spec(spec_id, parent_branch_id, agent_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"fork_branch_for_spec is not yet implemented in PostgreSQL edition")


def fork_parallel_branches(parent_branch_id, agent_ids):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"fork_parallel_branches is not yet implemented in PostgreSQL edition")


def get_branch_context_chain(branch_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"get_branch_context_chain is not yet implemented in PostgreSQL edition")


def merge_branch_with_validation(source_branch_id, target_branch_id, agent_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"merge_branch_with_validation is not yet implemented in PostgreSQL edition")


def merge_parallel_branches(branch_ids, target_branch_id, agent_id):
    """Stub — not yet implemented in PG edition."""
    raise NotImplementedError(f"merge_parallel_branches is not yet implemented in PostgreSQL edition")
