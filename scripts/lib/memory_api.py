"""PostgreSQL Memory System v2.0.0 - Memory API

CRUD operations on entities with entity_type='MEMORY'.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)


def create_memory(name, content, category='general', priority=2, tags=None,
                  metadata=None, owned_by_agent=None, visibility='SHARED',
                  accessible_to=None):
    sql = """
        INSERT INTO entities (entity_type, name, content, category, priority,
                              status, tags, metadata, owned_by_agent, visibility,
                              accessible_to)
        VALUES ('MEMORY', %s, %s, %s, %s, 'ACTIVE', %s, %s, %s, %s, %s)
        RETURNING entity_id
    """
    params = (
        name[:500],
        content,
        category,
        priority,
        json.dumps(tags or []),
        json.dumps(metadata or {}),
        owned_by_agent,
        visibility,
        json.dumps(accessible_to or []),
    )
    return execute_insert_returning_id(sql, params, id_column='entity_id')


def get_memory(entity_id):
    sql = """
        SELECT entity_id, entity_type, name, content, category, priority, status,
               tags, metadata, owned_by_agent, visibility, accessible_to,
               created_at, updated_at, expires_at
        FROM entities
        WHERE entity_id = %s AND entity_type = 'MEMORY'
    """
    row = execute_query_one(sql, (entity_id,))
    if row is None:
        return None
    return _decorate_memory(row)


def update_memory(entity_id, **kwargs):
    allowed = {'name', 'content', 'category', 'priority', 'status', 'tags',
               'metadata', 'visibility', 'accessible_to', 'expires_at'}
    jsonb_fields = {'tags', 'metadata', 'accessible_to'}

    updates = {}
    for k, v in kwargs.items():
        lk = k.lower()
        if lk in allowed:
            if lk in jsonb_fields and isinstance(v, (list, dict)):
                v = json.dumps(v)
            updates[lk] = v

    if not updates:
        return False

    set_parts = ["{} = %s".format(k) for k in updates]
    set_parts.append("updated_at = NOW()")
    values = list(updates.values())
    values.append(entity_id)

    sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'MEMORY'".format(
        ', '.join(set_parts)
    )
    return execute(sql, values) > 0


def delete_memory(entity_id):
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'MEMORY'"
    return execute(sql, (entity_id,)) > 0


def search_memories(keyword=None, category=None, visibility=None,
                    owned_by_agent=None, limit=100, offset=0):
    conditions = ["entity_type = 'MEMORY'"]
    params = []

    if keyword:
        conditions.append("(UPPER(name) LIKE UPPER(%s) OR UPPER(content) LIKE UPPER(%s))")
        like_val = '%' + keyword + '%'
        params.extend([like_val, like_val])

    if category:
        conditions.append("category = %s")
        params.append(category)

    if visibility:
        conditions.append("visibility = %s")
        params.append(visibility)

    if owned_by_agent:
        conditions.append("owned_by_agent = %s")
        params.append(owned_by_agent)

    where = ' AND '.join(conditions)
    params.extend([limit, offset])

    sql = """
        SELECT entity_id, name, content, category, priority, status,
               tags, metadata, owned_by_agent, visibility, accessible_to,
               created_at, updated_at
        FROM entities
        WHERE {}
        ORDER BY priority DESC, created_at DESC
        LIMIT %s OFFSET %s
    """.format(where)

    rows = execute_query(sql, params)
    return [_decorate_memory(r) for r in rows]


def get_agent_memories(agent_id, limit=100):
    sql = """
        SELECT entity_id, name, content, category, priority, status,
               tags, metadata, owned_by_agent, visibility, accessible_to,
               created_at, updated_at
        FROM entities
        WHERE entity_type = 'MEMORY'
          AND (visibility = 'SHARED'
               OR owned_by_agent = %s
               OR (visibility = 'COLLABORATIVE'
                   AND %s IN (SELECT jsonb_array_elements_text(accessible_to))))
        ORDER BY priority DESC, created_at DESC
        LIMIT %s
    """
    rows = execute_query(sql, (agent_id, agent_id, limit))
    return [_decorate_memory(r) for r in rows]


def count_memories(category=None):
    if category:
        sql = "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'MEMORY' AND category = %s"
        row = execute_query_one(sql, (category,))
    else:
        sql = "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'MEMORY'"
        row = execute_query_one(sql)
    return row['cnt'] if row else 0


def _decorate_memory(row):
    for col in ('tags', 'metadata', 'accessible_to'):
        val = row.get(col)
        if isinstance(val, str):
            try:
                row[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
        elif val is None:
            if col == 'tags':
                row[col] = []
            elif col == 'metadata':
                row[col] = {}
            elif col == 'accessible_to':
                row[col] = []
    return row
