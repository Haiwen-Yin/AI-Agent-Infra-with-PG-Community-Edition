"""PostgreSQL Memory System v2.2.1 - Memory API

CRUD operations on entities with entity_type='MEMORY'.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)


def create_memory(
    title: str,
    content: str,
    category: str = "general",
    importance: int = 5,
    summary: Optional[str] = None,
    source_agent: Optional[str] = None,
    owned_by_agent: Optional[str] = None,
    visibility: str = "PRIVATE",
    workspace_id: Optional[str] = None,
) -> str:
    sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              importance, status, owned_by_agent, source_agent,
                              visibility, workspace_id)
        VALUES ('MEMORY', %s, %s, %s, %s, %s, 'ACTIVE', %s, %s, %s, %s)
        RETURNING entity_id
    """
    params = (
        title[:500],
        content,
        summary,
        category,
        importance,
        owned_by_agent,
        source_agent,
        visibility,
        workspace_id,
    )
    return execute_insert_returning_id(sql, params)


def get_memory(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT entity_id, entity_type, title, content, summary, category,
               importance, status, owned_by_agent, source_agent, visibility,
               retrieval_count, created_at, updated_at, expires_at
        FROM entities
        WHERE entity_id = %s AND entity_type = 'MEMORY'
    """
    row = execute_query_one(sql, (entity_id,))
    if row is None:
        return None
    return _row_to_dict(row)


def update_memory(entity_id: str, **kwargs) -> bool:
    allowed = {"title", "content", "summary", "category", "importance",
               "status", "visibility", "expires_at"}
    updates = {}
    for k, v in kwargs.items():
        lk = k.lower()
        if lk not in allowed:
            continue
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


def delete_memory(entity_id: str) -> bool:
    execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'MEMORY'", (entity_id,))
    execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s",
            (entity_id, entity_id))
    execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'MEMORY'", (entity_id,))
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'MEMORY'"
    return execute(sql, (entity_id,)) > 0


def search_memories(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    visibility: Optional[str] = None,
    owned_by_agent: Optional[str] = None,
    workspace_id: Optional[str] = None,
    isolation_mode: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = ["entity_type = 'MEMORY'"]
    params: List[Any] = []

    if keyword:
        conditions.append("(UPPER(title) LIKE UPPER(%s) OR UPPER(content) LIKE UPPER(%s))")
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
    if isolation_mode == 'SHARED':
        conditions.append("workspace_id IS NULL")
    elif isolation_mode == 'ISOLATED' and workspace_id:
        conditions.append("workspace_id = %s")
        params.append(workspace_id)
    elif workspace_id:
        conditions.append("workspace_id = %s")
        params.append(workspace_id)

    where = ' AND '.join(conditions)
    params.extend([limit, offset])

    sql = """
        SELECT entity_id, entity_type, title, content, summary, category,
               importance, status, owned_by_agent, source_agent, visibility,
               retrieval_count, created_at, updated_at
        FROM entities
        WHERE {}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """.format(where)

    return [_row_to_dict(r) for r in execute_query(sql, params)]


def get_agent_memories(agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    sql = """
        SELECT entity_id, entity_type, title, content, summary, category,
               importance, status, owned_by_agent, source_agent, visibility,
               retrieval_count, created_at
        FROM entities
        WHERE entity_type = 'MEMORY'
          AND (visibility = 'SHARED' OR visibility = 'PUBLIC' OR owned_by_agent = %s)
        ORDER BY created_at DESC
        LIMIT %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, (agent_id, limit))]


def count_memories(category: Optional[str] = None) -> int:
    if category:
        sql = "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'MEMORY' AND category = %s"
        row = execute_query_one(sql, (category,))
    else:
        sql = "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'MEMORY'"
        row = execute_query_one(sql)
    return row['cnt'] if row else 0


def add_memory_tags(entity_id: str, tag_names: List[str]) -> int:
    added = 0
    for tag_name in tag_names:
        execute(
            "INSERT INTO tags (tag_name, usage_count) VALUES (%s, 0) ON CONFLICT (tag_name) DO NOTHING",
            (tag_name,)
        )
        tag_row = execute_query_one(
            "SELECT tag_id FROM tags WHERE tag_name = %s",
            (tag_name,),
        )
        if tag_row is None:
            continue
        tag_id = tag_row["tag_id"]
        affected = execute(
            "INSERT INTO entity_tags (entity_id, entity_type, tag_id) VALUES (%s, 'MEMORY', %s) ON CONFLICT DO NOTHING",
            (entity_id, tag_id)
        )
        if affected > 0:
            added += 1
    return added


def get_memory_tags(entity_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT t.tag_id, t.tag_name, t.tag_group
        FROM entity_tags et
        JOIN tags t ON et.tag_id = t.tag_id
        WHERE et.entity_id = %s AND et.entity_type = 'MEMORY'
    """
    rows = execute_query(sql, (entity_id,))
    return [
        {"tag_id": r["tag_id"], "tag_name": r["tag_name"], "tag_group": r.get("tag_group")}
        for r in rows
    ]


def remove_memory_tag(entity_id: str, tag_id: int) -> bool:
    sql = """
        DELETE FROM entity_tags
        WHERE entity_id = %s AND entity_type = 'MEMORY' AND tag_id = %s
    """
    return execute(sql, (entity_id, tag_id)) > 0


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "entity_id": row.get("entity_id"),
        "entity_type": row.get("entity_type"),
        "title": row.get("title"),
        "content": row.get("content"),
        "summary": row.get("summary"),
        "category": row.get("category"),
        "importance": row.get("importance"),
        "status": row.get("status"),
        "owned_by_agent": row.get("owned_by_agent"),
        "source_agent": row.get("source_agent"),
        "visibility": row.get("visibility"),
        "retrieval_count": row.get("retrieval_count"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "expires_at": row.get("expires_at"),
    }