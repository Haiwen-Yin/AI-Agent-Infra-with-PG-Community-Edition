"""AI Agent Infra v3.8.0 - PG Community Edition - Spec API

Spec Driven Development: spec CRUD, plan linkage, validation,
derivation, and spec status management.
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

logger = logging.getLogger(__name__)

_JSON_COLUMNS = {"acceptance_criteria", "spec_constraints"}


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


def create_spec(
    title: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
    category: Optional[str] = None,
    importance: int = 5,
    owned_by_agent: Optional[str] = None,
    visibility: str = "SHARED",
    workspace_id: Optional[str] = None,
    spec_scope: Optional[str] = None,
    complexity: str = "MEDIUM",
    acceptance_criteria: Optional[Any] = None,
    constraints: Optional[Any] = None,
    parent_spec_id: Optional[str] = None,
    branch_id: Optional[str] = None,
) -> str:
    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              status, owned_by_agent, visibility,
                              importance, workspace_id, created_at, updated_at)
        VALUES ('SPEC', %s, %s, %s, %s,
                'ACTIVE', %s, %s,
                %s, %s, NOW(), NOW())
        RETURNING entity_id
    """
    entity_id = execute_insert_returning_id(entity_sql, (
        title, content, summary, category,
        owned_by_agent, visibility,
        importance, workspace_id,
    ))

    ac_val = json.dumps(acceptance_criteria) if acceptance_criteria and not isinstance(acceptance_criteria, str) else acceptance_criteria
    cs_val = json.dumps(constraints) if constraints and not isinstance(constraints, str) else constraints

    meta_sql = """
        INSERT INTO spec_meta (entity_id, entity_type, spec_version, spec_status,
                               acceptance_criteria, spec_constraints, spec_scope,
                               complexity, parent_spec_id, branch_id)
        VALUES (%s, 'SPEC', 1, 'DRAFT', %s, %s, %s, %s, %s, %s)
    """
    execute(meta_sql, (
        entity_id, ac_val, cs_val,
        spec_scope, complexity, parent_spec_id, branch_id,
    ))

    return entity_id


def get_spec(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary,
               e.category, e.status, e.owned_by_agent, e.visibility, e.importance,
               e.workspace_id, e.created_at, e.updated_at,
               sm.spec_version, sm.spec_status, sm.acceptance_criteria,
               sm.spec_constraints, sm.spec_scope, sm.complexity, sm.parent_spec_id,
               sm.branch_id
        FROM entities e
        LEFT JOIN spec_meta sm ON sm.entity_id = e.entity_id
                               AND sm.entity_type = e.entity_type
        WHERE e.entity_id = %s AND e.entity_type = 'SPEC'
    """
    row = execute_query_one(sql, (entity_id,))
    if row is None:
        return None

    result = _row_to_dict(row)

    links_sql = """
        SELECT link_id, spec_id, plan_id, link_type, link_strength
        FROM spec_plan_links
        WHERE spec_id = %s
    """
    links = execute_query(links_sql, (entity_id,))
    result["plan_links"] = [sanitize_row(l) for l in links]
    return result


def update_spec(entity_id: str, **kwargs: Any) -> bool:
    entity_fields = {"title", "content", "summary", "category", "importance",
                     "visibility", "status"}
    meta_fields = {"spec_status", "spec_scope", "complexity",
                   "acceptance_criteria", "constraints", "branch_id"}

    entity_updates: Dict[str, Any] = {}
    entity_values: List[Any] = []
    meta_updates: Dict[str, Any] = {}
    meta_values: List[Any] = []

    for k, v in kwargs.items():
        lk = k.lower()
        if lk in entity_fields and v is not None:
            entity_updates[lk] = "%s"
            entity_values.append(v)
        elif lk in meta_fields and v is not None:
            if lk in ("acceptance_criteria", "constraints") and not isinstance(v, str):
                meta_updates[lk] = "%s"
                meta_values.append(json.dumps(v))
            else:
                meta_updates[lk] = "%s"
                meta_values.append(v)

    affected = 0

    if entity_updates:
        set_parts = ["{} = {}".format(k, v) for k, v in entity_updates.items()]
        set_parts.append("updated_at = NOW()")
        entity_values.append(entity_id)
        sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'SPEC'".format(
            ", ".join(set_parts)
        )
        affected += execute(sql, entity_values)

    if meta_updates:
        col_map = {"constraints": "spec_constraints"}
        actual_updates = {}
        for k, v in meta_updates.items():
            actual_key = col_map.get(k, k)
            actual_updates[actual_key] = v
        set_parts = ["{} = {}".format(k, v) for k, v in actual_updates.items()]
        meta_values.append(entity_id)
        sql = "UPDATE spec_meta SET {} WHERE entity_id = %s AND entity_type = 'SPEC'".format(
            ", ".join(set_parts)
        )
        affected += execute(sql, meta_values)

    return affected > 0


def delete_spec(entity_id: str) -> bool:
    try:
        execute("DELETE FROM spec_plan_links WHERE spec_id = %s", (entity_id,))
        execute("DELETE FROM spec_meta WHERE entity_id = %s AND entity_type = 'SPEC'", (entity_id,))
        execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'SPEC'", (entity_id,))
        execute("DELETE FROM entity_edges WHERE source_id = %s AND source_type = 'SPEC'", (entity_id,))
        execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'SPEC'", (entity_id,))
        affected = execute("DELETE FROM entities WHERE entity_id = %s AND entity_type = 'SPEC'", (entity_id,))
        return affected > 0
    except Exception:
        return False


def list_specs(
    spec_scope: Optional[str] = None,
    spec_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = ["e.entity_type = 'SPEC'"]
    params: List[Any] = []

    if spec_scope:
        conditions.append("sm.spec_scope = %s")
        params.append(spec_scope)
    if spec_status:
        conditions.append("sm.spec_status = %s")
        params.append(spec_status)

    where = " AND ".join(conditions)
    params.extend([limit, offset])
    sql = """
        SELECT e.entity_id, e.title, e.category, e.status, e.importance,
               sm.spec_version, sm.spec_status, sm.spec_scope, sm.complexity,
               sm.branch_id
        FROM entities e
        JOIN spec_meta sm ON sm.entity_id = e.entity_id
                          AND sm.entity_type = e.entity_type
        WHERE {where}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
    """.format(where=where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def link_spec_to_plan(
    spec_id: str,
    plan_id: str,
    link_type: str,
    strength: float = 1.0,
) -> str:
    sql = """
        INSERT INTO spec_plan_links (spec_id, plan_id, link_type, link_strength)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING link_id
    """
    result = execute_insert_returning_id(sql, (spec_id, plan_id, link_type, strength), id_column="link_id")
    if result is None:
        existing = execute_query_one(
            "SELECT link_id FROM spec_plan_links WHERE spec_id = %s AND plan_id = %s AND link_type = %s",
            (spec_id, plan_id, link_type),
        )
        return existing["link_id"] if existing else None
    return result


def get_spec_plan_links(spec_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT spl.link_id, spl.spec_id, spl.plan_id, spl.link_type,
               spl.link_strength,
               tp.goal, tp.status AS plan_status
        FROM spec_plan_links spl
        JOIN task_plans tp ON tp.plan_id = spl.plan_id
        WHERE spl.spec_id = %s
        ORDER BY spl.link_id
    """
    return [sanitize_row(r) for r in execute_query(sql, (spec_id,))]


def unlink_spec_from_plan(spec_id: str, plan_id: str, link_type: Optional[str] = None) -> bool:
    if link_type:
        sql = "DELETE FROM spec_plan_links WHERE spec_id = %s AND plan_id = %s AND link_type = %s"
        return execute(sql, (spec_id, plan_id, link_type)) > 0
    sql = "DELETE FROM spec_plan_links WHERE spec_id = %s AND plan_id = %s"
    return execute(sql, (spec_id, plan_id)) > 0


def validate_spec(spec_id: str) -> Dict[str, Any]:
    spec = get_spec(spec_id)
    if spec is None:
        return {"valid": False, "errors": ["Spec not found: {}".format(spec_id)], "warnings": []}

    errors: List[str] = []
    warnings: List[str] = []

    if not spec.get("title"):
        errors.append("Spec has no title")

    spec_status = spec.get("spec_status")
    if spec_status not in ("DRAFT", "APPROVED", "IMPLEMENTED", "DEPRECATED"):
        errors.append("Spec has invalid status: {}".format(spec_status))

    acceptance_criteria = spec.get("acceptance_criteria")
    if acceptance_criteria:
        if isinstance(acceptance_criteria, str):
            try:
                acceptance_criteria = json.loads(acceptance_criteria)
            except (json.JSONDecodeError, TypeError):
                acceptance_criteria = None
        if isinstance(acceptance_criteria, list) and len(acceptance_criteria) == 0:
            warnings.append("Spec has empty acceptance criteria")
    else:
        warnings.append("Spec has no acceptance criteria defined")

    complexity = spec.get("complexity")
    if complexity == "CRITICAL" and spec.get("importance", 0) < 8:
        warnings.append("Spec complexity is CRITICAL but importance is below 8")

    plan_links = spec.get("plan_links", [])
    if not plan_links:
        warnings.append("Spec has no linked plans")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def derive_spec(
    parent_spec_id: str,
    title: str,
    content: Optional[str] = None,
    summary: Optional[str] = None,
) -> str:
    parent = get_spec(parent_spec_id)
    if parent is None:
        raise ValueError("Parent spec {} not found".format(parent_spec_id))

    entity_id = create_spec(
        title=title,
        content=content or parent.get("content"),
        summary=summary or parent.get("summary"),
        category=parent.get("category"),
        importance=parent.get("importance"),
        owned_by_agent=parent.get("owned_by_agent"),
        visibility=parent.get("visibility"),
        workspace_id=parent.get("workspace_id"),
        spec_scope=parent.get("spec_scope"),
        complexity=parent.get("complexity"),
        acceptance_criteria=parent.get("acceptance_criteria"),
        constraints=parent.get("spec_constraints"),
        parent_spec_id=parent_spec_id,
    )

    edge_sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type,
                                  strength, confidence)
        VALUES (%s, 'SPEC', %s, 'DERIVES_FROM', 1.0, 1.0)
    """
    execute(edge_sql, (entity_id, parent_spec_id))

    return entity_id


def update_spec_status(spec_id: str, new_status: str) -> bool:
    valid_statuses = {"DRAFT", "APPROVED", "IMPLEMENTED", "DEPRECATED"}
    if new_status not in valid_statuses:
        return False
    sql = """
        UPDATE spec_meta SET spec_status = %s
        WHERE entity_id = %s AND entity_type = 'SPEC'
    """
    return execute(sql, (new_status, spec_id)) > 0


def get_spec_by_branch(branch_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.title, e.category, e.status, e.importance,
               sm.spec_version, sm.spec_status, sm.spec_scope, sm.complexity,
               sm.branch_id
        FROM entities e
        JOIN spec_meta sm ON sm.entity_id = e.entity_id
                          AND sm.entity_type = e.entity_type
        WHERE sm.branch_id = %s AND e.entity_type = 'SPEC'
        ORDER BY e.created_at DESC
    """
    return [_row_to_dict(r) for r in execute_query(sql, (branch_id,))]


def search_specs(
    query: str,
    spec_scope: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    conditions = [
        "e.entity_type = 'SPEC'",
        "(e.title ILIKE %s OR e.content ILIKE %s OR e.summary ILIKE %s)",
    ]
    like_val = "%{}%".format(query)
    params: List[Any] = [like_val, like_val, like_val]

    if spec_scope:
        conditions.append("sm.spec_scope = %s")
        params.append(spec_scope)

    where = " AND ".join(conditions)
    params.append(limit)
    sql = """
        SELECT e.entity_id, e.title, e.summary, e.category, e.status,
               sm.spec_status, sm.spec_scope, sm.complexity
        FROM entities e
        JOIN spec_meta sm ON sm.entity_id = e.entity_id
                          AND sm.entity_type = e.entity_type
        WHERE {where}
        ORDER BY e.importance DESC, e.created_at DESC
        LIMIT %s
    """.format(where=where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def validate_plan_against_spec(
    spec_id: str,
    plan_id: Optional[str] = None,
) -> Dict[str, Any]:
    spec = get_spec(spec_id)
    if spec is None:
        raise ValueError("Spec {} not found".format(spec_id))

    ac = spec.get("acceptance_criteria")
    if isinstance(ac, str):
        try:
            ac = json.loads(ac)
        except (json.JSONDecodeError, TypeError):
            ac = None

    results: Dict[str, Any] = {
        "spec_id": spec_id,
        "criteria_count": len(ac) if isinstance(ac, list) else 0,
        "validations": [],
    }

    if plan_id:
        plan_ids = [plan_id]
    else:
        links = get_spec_plan_links(spec_id)
        plan_ids = [l["plan_id"] for l in links if l.get("link_type") == "DRIVES"]

    from . import task_plan_api

    for pid in plan_ids:
        plan = task_plan_api.get_plan(pid)
        steps = task_plan_api.list_steps(pid)
        step_descs = [s.get("description", "") for s in steps]

        validated = 0
        passed = 0
        if isinstance(ac, list):
            for criterion in ac:
                validated += 1
                crit_str = criterion if isinstance(criterion, str) else json.dumps(criterion)
                for desc in step_descs:
                    if crit_str.lower() in desc.lower():
                        passed += 1
                        break

        results["validations"].append({
            "plan_id": pid,
            "goal": plan.get("goal", "") if plan else "",
            "plan_status": plan.get("status", "") if plan else "",
            "criteria_validated": validated,
            "criteria_passed": passed,
            "pass_rate": round(passed / validated, 2) if validated > 0 else 0,
        })

    return results


def get_spec_stats() -> Dict[str, Any]:
    by_status = execute_query("""
        SELECT sm.spec_status, COUNT(*) AS cnt
        FROM spec_meta sm
        JOIN entities e ON e.entity_id = sm.entity_id AND e.entity_type = 'SPEC'
        WHERE e.status = 'ACTIVE'
        GROUP BY sm.spec_status
    """)
    by_complexity = execute_query("""
        SELECT sm.complexity, COUNT(*) AS cnt
        FROM spec_meta sm
        JOIN entities e ON e.entity_id = sm.entity_id AND e.entity_type = 'SPEC'
        WHERE e.status = 'ACTIVE'
        GROUP BY sm.complexity
    """)
    total = execute_query_one("""
        SELECT COUNT(*) AS total
        FROM entities
        WHERE entity_type = 'SPEC' AND status = 'ACTIVE'
    """)
    linked = execute_query_one("""
        SELECT COUNT(DISTINCT spl.spec_id) AS linked_count
        FROM spec_plan_links spl
        JOIN entities e ON e.entity_id = spl.spec_id AND e.entity_type = 'SPEC'
    """)
    return {
        "total": total["total"] if total else 0,
        "by_status": {r["spec_status"]: r["cnt"] for r in by_status},
        "by_complexity": {r["complexity"]: r["cnt"] for r in by_complexity},
        "linked_to_plans": linked["linked_count"] if linked else 0,
    }


def derive_loop_from_spec(spec_id: str, agent_id: str) -> Dict[str, Any]:
    """Derive a loop definition from a spec. Returns the derived loop parameters."""
    spec = get_spec(spec_id)
    if not spec:
        raise ValueError("Spec {} not found".format(spec_id))

    properties = spec.get("properties", {})
    acceptance_criteria = properties.get("acceptance_criteria", [])

    goal_definition = {
        "type": "SPEC_VALIDATION",
        "spec_id": spec_id,
        "success_criteria": [str(c) for c in acceptance_criteria] if acceptance_criteria else ["Spec {} validated".format(spec_id)],
        "constraints": ["Must validate against all acceptance criteria"]
    }

    stop_conditions = {
        "max_iterations": 10,
        "timeout_minutes": 60,
        "consecutive_passes": 2
    }

    evaluation_config = {
        "type": "SPEC_VALIDATION",
        "spec_id": spec_id,
        "criteria": [str(c) for c in acceptance_criteria] if acceptance_criteria else []
    }

    return {
        "title": "Loop for spec: {}".format(spec.get("title", spec_id)),
        "summary": "Auto-derived loop for spec validation",
        "goal_definition": goal_definition,
        "stop_conditions": stop_conditions,
        "evaluation_config": evaluation_config,
        "spec_id": spec_id,
        "owned_by_agent": agent_id
    }
