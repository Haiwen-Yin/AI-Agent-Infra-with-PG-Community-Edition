"""PostgreSQL Memory System v2.3.0 - Spec API

Spec Driven Development: spec CRUD, plan derivation, spec-plan linking,
validation, and spec derivation chains.
Operates on entities (entity_type='SPEC') + spec_meta + spec_plan_links.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

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
    entity_data: Dict[str, Any],
    spec_meta: Dict[str, Any],
    workspace_id: Optional[int] = None,
) -> int:
    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              importance, status, owned_by_agent, source_agent,
                              visibility, retrieval_count, workspace_id)
        VALUES ('SPEC', %s, %s, %s, %s, %s, %s, %s, %s,
                %s, 0, %s)
        RETURNING entity_id
    """
    entity_params = (
        entity_data.get('title', '')[:500],
        entity_data.get('content'),
        entity_data.get('summary'),
        entity_data.get('category'),
        entity_data.get('importance', 5),
        entity_data.get('status', 'ACTIVE'),
        entity_data.get('owned_by_agent'),
        entity_data.get('source_agent'),
        entity_data.get('visibility', 'PRIVATE'),
        workspace_id,
    )
    entity_id = execute_insert_returning_id(entity_sql, entity_params)

    ac_val = spec_meta.get('acceptance_criteria')
    if isinstance(ac_val, (dict, list)):
        ac_val = json.dumps(ac_val)
    sc_val = spec_meta.get('spec_constraints')
    if isinstance(sc_val, (dict, list)):
        sc_val = json.dumps(sc_val)

    meta_sql = """
        INSERT INTO spec_meta (entity_id, spec_version, spec_status,
                               acceptance_criteria, spec_constraints,
                               spec_scope, complexity, parent_spec_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    meta_params = (
        entity_id,
        spec_meta.get('spec_version', 1),
        spec_meta.get('spec_status', 'DRAFT'),
        ac_val,
        sc_val,
        spec_meta.get('spec_scope'),
        spec_meta.get('complexity', 'MEDIUM'),
        spec_meta.get('parent_spec_id'),
    )
    execute(meta_sql, meta_params)
    return entity_id


def get_spec(spec_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count, e.expires_at, e.created_at, e.updated_at,
               sm.spec_version, sm.spec_status, sm.acceptance_criteria,
               sm.spec_constraints, sm.spec_scope, sm.complexity, sm.parent_spec_id
        FROM entities e
        JOIN spec_meta sm ON sm.entity_id = e.entity_id
        WHERE e.entity_id = %s AND e.entity_type = 'SPEC'
    """
    row = execute_query_one(sql, (spec_id,))
    if row is None:
        return None
    return _row_to_dict(row)


def update_spec(spec_id: int, entity_data: Optional[Dict[str, Any]] = None,
                spec_meta: Optional[Dict[str, Any]] = None) -> bool:
    entity_fields = {"title", "content", "summary", "category", "importance",
                     "status", "visibility", "expires_at"}
    meta_fields = {"spec_version", "spec_status", "acceptance_criteria",
                   "spec_constraints", "spec_scope", "complexity"}

    affected = 0

    if entity_data:
        entity_updates = {}
        entity_values: List[Any] = []
        for k, v in entity_data.items():
            lk = k.lower()
            if lk in entity_fields:
                entity_updates[lk] = "%s"
                entity_values.append(v)
        if entity_updates:
            set_parts = ["{} = {}".format(k, v) for k, v in entity_updates.items()]
            set_parts.append("updated_at = NOW()")
            entity_values.append(spec_id)
            sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'SPEC'".format(
                ', '.join(set_parts)
            )
            affected += execute(sql, entity_values)

    if spec_meta:
        meta_updates = {}
        meta_values: List[Any] = []
        for k, v in spec_meta.items():
            lk = k.lower()
            if lk in meta_fields:
                if lk in _JSON_COLUMNS and isinstance(v, (dict, list)):
                    v = json.dumps(v)
                meta_updates[lk] = "%s"
                meta_values.append(v)
        if meta_updates:
            set_parts = ["{} = {}".format(k, v) for k, v in meta_updates.items()]
            meta_values.append(spec_id)
            sql = "UPDATE spec_meta SET {} WHERE entity_id = %s".format(
                ', '.join(set_parts)
            )
            affected += execute(sql, meta_values)

    return affected > 0


def list_specs(status: Optional[str] = None,
               workspace_id: Optional[int] = None) -> List[Dict[str, Any]]:
    conditions = ["e.entity_type = 'SPEC'"]
    params: List[Any] = []

    if status:
        conditions.append("sm.spec_status = %s")
        params.append(status)
    if workspace_id is not None:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)

    where = ' AND '.join(conditions)

    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count, e.created_at, e.updated_at,
               sm.spec_version, sm.spec_status, sm.acceptance_criteria,
               sm.spec_constraints, sm.spec_scope, sm.complexity, sm.parent_spec_id
        FROM entities e
        JOIN spec_meta sm ON sm.entity_id = e.entity_id
        WHERE {}
        ORDER BY e.created_at DESC
    """.format(where)

    return [_row_to_dict(r) for r in execute_query(sql, params)]


def create_plan_from_spec(spec_id: int, plan_title: str,
                          plan_description: str) -> int:
    spec = get_spec(spec_id)
    if spec is None:
        raise ValueError("Spec not found: {}".format(spec_id))

    plan_sql = """
        INSERT INTO task_plans (goal, agent_id, priority, status, workspace_id)
        VALUES (%s, %s, %s, 'PENDING', %s)
        RETURNING plan_id
    """
    plan_id = execute_insert_returning_id(plan_sql, (
        plan_title,
        spec.get('owned_by_agent'),
        5,
        spec.get('workspace_id'),
    ), id_column="plan_id")

    link_sql = """
        INSERT INTO spec_plan_links (spec_id, plan_id, link_type, link_strength)
        VALUES (%s, %s, 'DRIVES', 1.0)
    """
    execute(link_sql, (spec_id, plan_id))

    return plan_id


def link_spec_to_plan(spec_id: int, plan_id: int,
                      link_type: str = 'DRIVES',
                      strength: float = 1.0) -> int:
    sql = """
        INSERT INTO spec_plan_links (spec_id, plan_id, link_type, link_strength)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (spec_id, plan_id, link_type) DO NOTHING
        RETURNING link_id
    """
    result = execute_insert_returning_id(sql, (spec_id, plan_id, link_type, strength),
                                         id_column="link_id")
    if result is None:
        existing = execute_query_one(
            "SELECT link_id FROM spec_plan_links WHERE spec_id = %s AND plan_id = %s AND link_type = %s",
            (spec_id, plan_id, link_type),
        )
        return existing['link_id'] if existing else None
    return result


def get_spec_plan_links(spec_id: int) -> List[Dict[str, Any]]:
    sql = """
        SELECT spl.link_id, spl.spec_id, spl.plan_id, spl.link_type,
               spl.link_strength, spl.created_at,
               tp.goal, tp.status AS plan_status, tp.priority, tp.agent_id
        FROM spec_plan_links spl
        JOIN task_plans tp ON tp.plan_id = spl.plan_id
        WHERE spl.spec_id = %s
        ORDER BY spl.created_at DESC
    """
    return [_row_to_dict(r) for r in execute_query(sql, (spec_id,))]


def validate_plan_against_spec(spec_id: int, plan_id: int) -> Dict[str, Any]:
    spec = get_spec(spec_id)
    if spec is None:
        return {"valid": False, "errors": ["Spec not found: {}".format(spec_id)], "warnings": []}

    plan_sql = "SELECT plan_id, goal, status, priority, agent_id FROM task_plans WHERE plan_id = %s"
    plan = execute_query_one(plan_sql, (plan_id,))
    if plan is None:
        return {"valid": False, "errors": ["Plan not found: {}".format(plan_id)], "warnings": []}

    errors: List[str] = []
    warnings: List[str] = []

    spec_status = spec.get('spec_status')
    if spec_status not in ('APPROVED', 'IMPLEMENTED'):
        errors.append("Spec status is {} but must be APPROVED or IMPLEMENTED to validate plans against".format(spec_status))

    acceptance_criteria = spec.get('acceptance_criteria')
    if acceptance_criteria:
        if isinstance(acceptance_criteria, str):
            try:
                acceptance_criteria = json.loads(acceptance_criteria)
            except (json.JSONDecodeError, TypeError):
                acceptance_criteria = None
        if isinstance(acceptance_criteria, list) and len(acceptance_criteria) > 0:
            if not plan.get('goal'):
                errors.append("Plan has no goal defined; cannot map to acceptance criteria")
        elif not acceptance_criteria:
            warnings.append("Spec has no acceptance criteria defined")

    spec_constraints = spec.get('spec_constraints')
    if spec_constraints:
        if isinstance(spec_constraints, str):
            try:
                spec_constraints = json.loads(spec_constraints)
            except (json.JSONDecodeError, TypeError):
                spec_constraints = None
        if isinstance(spec_constraints, dict):
            if spec_constraints.get('blocked') and plan.get('status') == 'RUNNING':
                errors.append("Plan is RUNNING but spec constraints indicate blocked")

    link_sql = """
        SELECT link_id FROM spec_plan_links
        WHERE spec_id = %s AND plan_id = %s
    """
    link = execute_query_one(link_sql, (spec_id, plan_id))
    if link is None:
        warnings.append("Spec and plan are not explicitly linked")

    complexity = spec.get('complexity')
    if complexity == 'CRITICAL' and plan.get('priority', 0) < 8:
        warnings.append("Spec complexity is CRITICAL but plan priority is below 8")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def derive_spec(parent_spec_id: int, entity_data: Dict[str, Any],
                spec_meta: Dict[str, Any]) -> int:
    parent = get_spec(parent_spec_id)
    if parent is None:
        raise ValueError("Parent spec not found: {}".format(parent_spec_id))

    merged_meta = dict(spec_meta)
    merged_meta['parent_spec_id'] = parent_spec_id
    if 'spec_version' not in merged_meta:
        merged_meta['spec_version'] = (parent.get('spec_version') or 0) + 1
    if 'spec_status' not in merged_meta:
        merged_meta['spec_status'] = 'DRAFT'
    if 'complexity' not in merged_meta:
        merged_meta['complexity'] = parent.get('complexity', 'MEDIUM')

    entity_id = create_spec(entity_data, merged_meta,
                            workspace_id=parent.get('workspace_id'))

    edge_sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type,
                                  strength, confidence)
        VALUES (%s, 'SPEC', %s, 'DERIVES_FROM', 1.0, 1.0)
    """
    execute(edge_sql, (entity_id, parent_spec_id))

    return entity_id


def delete_spec(spec_id: int) -> bool:
    execute("DELETE FROM spec_plan_links WHERE spec_id = %s", (spec_id,))
    execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'SPEC'", (spec_id,))
    execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s", (spec_id, spec_id))
    execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'SPEC'", (spec_id,))
    execute("DELETE FROM spec_meta WHERE entity_id = %s", (spec_id,))
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'SPEC'"
    return execute(sql, (spec_id,)) > 0
