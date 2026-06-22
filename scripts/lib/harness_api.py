"""AI Agent Infra v3.7.3 - PG Community Edition - Harness API

Templates are reusable agent execution blueprints stored as entities
with entity_type='HARNESS_TEMPLATE' and extended via harness_meta.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)

_SLOT_RE = re.compile(r"\{(\w+)\}")


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(row)
    for json_col in ("input_schema", "output_schema"):
        val = result.get(json_col)
        if isinstance(val, str):
            try:
                result[json_col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_harness_template(
    title: str,
    summary: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    input_schema: Optional[Dict[str, Any]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    execution_mode: str = "SEQUENTIAL",
    importance: int = 5,
    owned_by_agent: Optional[str] = None,
    visibility: str = "SHARED",
) -> str:
    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              status, importance, owned_by_agent, source_agent,
                              visibility, retrieval_count, created_at, updated_at)
        VALUES ('HARNESS_TEMPLATE', %s, %s, %s, %s,
                'ACTIVE', %s, %s, %s,
                %s, 0, NOW(), NOW())
        RETURNING entity_id
    """
    entity_id = execute_insert_returning_id(entity_sql, (
        title, content, summary, category,
        importance, owned_by_agent, owned_by_agent,
        visibility,
    ))

    meta_sql = """
        INSERT INTO harness_meta (entity_id, entity_type, template_version,
                                  input_schema, output_schema, execution_mode)
        VALUES (%s, 'HARNESS_TEMPLATE', 1, %s, %s, %s)
    """
    execute(meta_sql, (
        entity_id,
        json.dumps(input_schema) if input_schema else None,
        json.dumps(output_schema) if output_schema else None,
        execution_mode,
    ))

    return entity_id


def get_harness_template(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary,
               e.category, e.status, e.importance, e.owned_by_agent,
               e.source_agent, e.visibility, e.retrieval_count,
               e.expires_at, e.created_at, e.updated_at,
               hm.template_version, hm.input_schema, hm.output_schema,
               hm.execution_mode
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id
                             AND hm.entity_type = e.entity_type
        WHERE e.entity_id = %s AND e.entity_type = 'HARNESS_TEMPLATE'
    """
    row = execute_query_one(sql, (entity_id,))
    if row is None:
        return None
    return _row_to_dict(row)


def update_harness_template(entity_id: str, **kwargs) -> bool:
    entity_fields = {"title", "content", "summary", "category", "status",
                     "importance", "owned_by_agent", "source_agent",
                     "visibility", "retrieval_count", "expires_at"}
    meta_fields = {"template_version", "input_schema", "output_schema", "execution_mode"}

    entity_updates: Dict[str, Any] = {}
    entity_values: List[Any] = []
    meta_updates: Dict[str, Any] = {}
    meta_values: List[Any] = []

    for k, v in kwargs.items():
        lk = k.lower()
        if lk in entity_fields:
            entity_updates[lk] = "%s"
            entity_values.append(v)
        elif lk in meta_fields:
            if lk in ("input_schema", "output_schema") and isinstance(v, dict):
                v = json.dumps(v)
            meta_updates[lk] = "%s"
            meta_values.append(v)

    affected = 0
    if entity_updates:
        set_parts = ["{} = {}".format(k, v) for k, v in entity_updates.items()]
        set_parts.append("updated_at = NOW()")
        entity_values.append(entity_id)
        sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'".format(
            ", ".join(set_parts)
        )
        affected += execute(sql, entity_values)

    if meta_updates:
        set_clause = ", ".join("{} = %s".format(k) for k in meta_updates)
        meta_values.append(entity_id)
        sql = "UPDATE harness_meta SET {} WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'".format(set_clause)
        affected += execute(sql, meta_values)

    return affected > 0


def delete_harness_template(entity_id: str) -> bool:
    execute("DELETE FROM harness_meta WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'", (entity_id,))
    execute("DELETE FROM entity_edges WHERE source_id = %s AND edge_type = 'USES_HARNESS'", (entity_id,))
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'"
    return execute(sql, (entity_id,)) > 0


def list_harness_templates(
    category: Optional[str] = None,
    execution_mode: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = ["e.entity_type = 'HARNESS_TEMPLATE'"]
    params: List[Any] = []

    if category:
        conditions.append("e.category = %s")
        params.append(category)
    if execution_mode:
        conditions.append("hm.execution_mode = %s")
        params.append(execution_mode)

    where = " AND ".join(conditions)
    params.extend([limit, offset])

    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.summary, e.category,
               e.status, e.importance, e.owned_by_agent, e.visibility,
               e.created_at, e.updated_at,
               hm.template_version, hm.execution_mode
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id
                             AND hm.entity_type = e.entity_type
        WHERE {where}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
    """.format(where=where)

    return [_row_to_dict(r) for r in execute_query(sql, params)]


def instantiate_harness(
    entity_id: str,
    variable_values: Dict[str, str],
    agent_id: str,
) -> str:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        raise ValueError("Harness template {} not found".format(entity_id))

    content = tpl.get("content") or ""
    instantiated_content = _SLOT_RE.sub(
        lambda m: str(variable_values.get(m.group(1), m.group(0))), content
    )

    title = "Instance of {}".format(tpl.get("title", entity_id))

    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              status, importance, owned_by_agent, source_agent,
                              visibility, retrieval_count, created_at, updated_at)
        VALUES ('TASK_OUTPUT', %s, %s, %s, %s,
                'ACTIVE', %s, %s, %s,
                %s, 0, NOW(), NOW())
        RETURNING entity_id
    """
    instance_id = execute_insert_returning_id(entity_sql, (
        title,
        instantiated_content,
        tpl.get("summary"),
        tpl.get("category"),
        tpl.get("importance", 5),
        agent_id,
        agent_id,
        tpl.get("visibility", "SHARED"),
    ))

    edge_sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type, strength, confidence)
        VALUES (%s, 'TASK_OUTPUT', %s, 'USES_HARNESS', 1.0, 1.0)
    """
    execute(edge_sql, (instance_id, entity_id))

    return instance_id


def validate_harness_input(
    entity_id: str,
    input_values: Dict[str, Any],
) -> Dict[str, Any]:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        return {"valid": False, "errors": ["Harness template {} not found".format(entity_id)]}

    input_schema = tpl.get("input_schema")
    if not input_schema or not isinstance(input_schema, dict):
        return {"valid": True, "errors": [], "warnings": ["No input schema defined; skipping validation"]}

    errors: List[str] = []
    warnings: List[str] = []
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])

    for req_field in required:
        if req_field not in input_values:
            errors.append("Missing required field: {}".format(req_field))

    for key, value in input_values.items():
        if key not in properties:
            warnings.append("Extra field not in schema: {}".format(key))
            continue
        expected_type = properties[key].get("type", "string")
        type_map = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "array": list, "object": dict}
        expected_py = type_map.get(expected_type)
        if expected_py and not isinstance(value, expected_py):
            errors.append("Field '{}' expected type {} but got {}".format(key, expected_type, type(value).__name__))

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def validate_harness_output(
    entity_id: str,
    output_values: Any,
) -> Dict[str, Any]:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        return {"valid": False, "errors": ["Harness template {} not found".format(entity_id)]}

    output_schema = tpl.get("output_schema")
    if not output_schema or not isinstance(output_schema, dict):
        return {"valid": True, "errors": [], "warnings": ["No output schema defined; skipping validation"]}

    errors: List[str] = []
    warnings: List[str] = []

    if isinstance(output_values, dict):
        properties = output_schema.get("properties", {})
        required = output_schema.get("required", [])
        for req_field in required:
            if req_field not in output_values:
                errors.append("Missing required output field: {}".format(req_field))

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def search_harness_templates(
    query: str,
    category: Optional[str] = None,
    execution_mode: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    conditions = [
        "e.entity_type = 'HARNESS_TEMPLATE'",
        "(e.title ILIKE %s OR e.content ILIKE %s OR e.summary ILIKE %s)",
    ]
    like_val = "%{}%".format(query)
    params: List[Any] = [like_val, like_val, like_val]

    if category:
        conditions.append("e.category = %s")
        params.append(category)
    if execution_mode:
        conditions.append("hm.execution_mode = %s")
        params.append(execution_mode)

    where = " AND ".join(conditions)
    params.append(limit)
    sql = """
        SELECT e.entity_id, e.title, e.summary, e.category, e.status,
               hm.template_version, hm.execution_mode
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id
                             AND hm.entity_type = e.entity_type
        WHERE {where}
        ORDER BY e.importance DESC, e.created_at DESC
        LIMIT %s
    """.format(where=where)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def duplicate_harness(entity_id: str, new_title: Optional[str] = None) -> str:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        raise ValueError("Harness template {} not found".format(entity_id))

    title = new_title or "{} (Copy)".format(tpl.get("title", "Untitled"))
    input_schema = tpl.get("input_schema")
    output_schema = tpl.get("output_schema")

    return create_harness_template(
        title=title,
        summary=tpl.get("summary"),
        content=tpl.get("content"),
        category=tpl.get("category"),
        input_schema=input_schema if isinstance(input_schema, dict) else None,
        output_schema=output_schema if isinstance(output_schema, dict) else None,
        execution_mode=tpl.get("execution_mode", "SEQUENTIAL"),
        importance=tpl.get("importance", 5),
        owned_by_agent=tpl.get("owned_by_agent"),
        visibility=tpl.get("visibility", "SHARED"),
    )


def get_harness_stats() -> Dict[str, Any]:
    by_mode = execute_query("""
        SELECT hm.execution_mode, COUNT(*) AS cnt
        FROM harness_meta hm
        JOIN entities e ON e.entity_id = hm.entity_id AND e.entity_type = 'HARNESS_TEMPLATE'
        WHERE e.status = 'ACTIVE'
        GROUP BY hm.execution_mode
    """)
    by_category = execute_query("""
        SELECT e.category, COUNT(*) AS cnt
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id AND hm.entity_type = 'HARNESS_TEMPLATE'
        WHERE e.entity_type = 'HARNESS_TEMPLATE' AND e.status = 'ACTIVE'
        GROUP BY e.category
    """)
    total = execute_query_one("""
        SELECT COUNT(*) AS total,
               AVG(e.importance) AS avg_importance
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id AND hm.entity_type = 'HARNESS_TEMPLATE'
        WHERE e.entity_type = 'HARNESS_TEMPLATE' AND e.status = 'ACTIVE'
    """)
    instances = execute_query_one("""
        SELECT COUNT(*) AS instance_count
        FROM entity_edges
        WHERE edge_type = 'USES_HARNESS'
    """)
    return {
        "total": total["total"] if total else 0,
        "avg_importance": float(total["avg_importance"]) if total and total.get("avg_importance") else 0,
        "by_execution_mode": {r["execution_mode"]: r["cnt"] for r in by_mode},
        "by_category": {r["category"] or "uncategorized": r["cnt"] for r in by_category},
        "total_instances": instances["instance_count"] if instances else 0,
    }


def export_harness(entity_id: str) -> Optional[Dict[str, Any]]:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        return None
    export_data = {
        "version": "3.7.3",
        "type": "HARNESS_TEMPLATE",
        "entity_id": tpl.get("entity_id"),
        "title": tpl.get("title"),
        "summary": tpl.get("summary"),
        "content": tpl.get("content"),
        "category": tpl.get("category"),
        "importance": tpl.get("importance"),
        "visibility": tpl.get("visibility"),
        "execution_mode": tpl.get("execution_mode"),
        "template_version": tpl.get("template_version"),
        "input_schema": tpl.get("input_schema"),
        "output_schema": tpl.get("output_schema"),
    }
    return export_data


def import_harness(export_data: Dict[str, Any], owned_by_agent: Optional[str] = None) -> str:
    return create_harness_template(
        title=export_data.get("title", "Imported Template"),
        summary=export_data.get("summary"),
        content=export_data.get("content"),
        category=export_data.get("category"),
        input_schema=export_data.get("input_schema"),
        output_schema=export_data.get("output_schema"),
        execution_mode=export_data.get("execution_mode", "SEQUENTIAL"),
        importance=export_data.get("importance", 5),
        owned_by_agent=owned_by_agent,
        visibility=export_data.get("visibility", "SHARED"),
    )
