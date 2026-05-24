"""PostgreSQL Memory System v2.2.1 - Harness API

Templates are reusable agent execution blueprints stored as ENTITIES
with ENTITY_TYPE='HARNESS_TEMPLATE' and extended via HARNESS_META.
"""

import json
import re
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

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
                              visibility, retrieval_count)
        VALUES ('HARNESS_TEMPLATE', %s, %s, %s, %s,
                'ACTIVE', %s, %s, %s,
                %s, 0)
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
    meta_updates: Dict[str, Any] = {}

    for k, v in kwargs.items():
        lk = k.lower()
        if lk in entity_fields:
            entity_updates[lk] = v
        elif lk in meta_fields:
            if lk in ("input_schema", "output_schema") and isinstance(v, dict):
                v = json.dumps(v)
            meta_updates[lk] = v

    affected = 0
    if entity_updates:
        set_parts = ["{} = %s".format(k) for k in entity_updates]
        set_parts.append("updated_at = NOW()")
        values = list(entity_updates.values())
        values.append(entity_id)
        sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'".format(
            ', '.join(set_parts)
        )
        affected += execute(sql, values)

    if meta_updates:
        set_clause = ", ".join("{} = %s".format(k) for k in meta_updates)
        values = list(meta_updates.values())
        values.append(entity_id)
        sql = "UPDATE harness_meta SET {} WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'".format(set_clause)
        affected += execute(sql, values)

    return affected > 0


def delete_harness_template(entity_id: str) -> bool:
    execute("DELETE FROM harness_meta WHERE entity_id = %s AND entity_type = 'HARNESS_TEMPLATE'", (entity_id,))
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

    where = ' AND '.join(conditions)
    params.extend([limit, offset])

    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.summary, e.category,
               e.status, e.importance, e.owned_by_agent, e.visibility,
               e.created_at, e.updated_at,
               hm.template_version, hm.execution_mode
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id
                             AND hm.entity_type = e.entity_type
        WHERE {}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
    """.format(where)

    return [_row_to_dict(r) for r in execute_query(sql, params)]


def get_template_with_variables(entity_id: str) -> Optional[Dict[str, Any]]:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        return None

    input_schema = tpl.get("input_schema")
    variables: List[Dict[str, Any]] = []
    if isinstance(input_schema, dict):
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        for var_name, var_def in properties.items():
            entry = {"name": var_name}
            if isinstance(var_def, dict):
                entry["type"] = var_def.get("type", "string")
                entry["description"] = var_def.get("description", "")
                if "default" in var_def:
                    entry["default"] = var_def["default"]
            entry["required"] = var_name in required
            variables.append(entry)

    tpl["variables"] = variables
    return tpl


def instantiate_harness_template(
    entity_id: str,
    variable_values: Dict[str, str],
    agent_id: str,
) -> str:
    tpl = get_harness_template(entity_id)
    if tpl is None:
        raise ValueError(f"Harness template {entity_id} not found")

    content = tpl.get("content") or ""
    instantiated_content = _SLOT_RE.sub(
        lambda m: str(variable_values.get(m.group(1), m.group(0))), content
    )

    title = f"Instance of {tpl.get('title', entity_id)}"

    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              status, importance, owned_by_agent, source_agent,
                              visibility, retrieval_count)
        VALUES ('TASK_OUTPUT', %s, %s, %s, %s,
                'ACTIVE', %s, %s, %s,
                %s, 0)
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


def count_harness_templates(category: Optional[str] = None) -> int:
    conditions = ["e.entity_type = 'HARNESS_TEMPLATE'"]
    params: List[Any] = []

    if category:
        conditions.append("e.category = %s")
        params.append(category)

    where = ' AND '.join(conditions)
    sql = """
        SELECT COUNT(*) AS cnt
        FROM entities e
        JOIN harness_meta hm ON hm.entity_id = e.entity_id
                             AND hm.entity_type = e.entity_type
        WHERE {}
    """.format(where)
    row = execute_query_one(sql, params)
    if row is None:
        return 0
    return int(row.get("cnt", 0))