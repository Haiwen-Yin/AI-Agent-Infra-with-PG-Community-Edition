"""AI Agent Infra v3.6.2 - PG Community Edition - Memory API

Unified memory management using psycopg2 with %s positional binds.
Operates on the entities table (entity_type='MEMORY').
"""

import logging
from typing import Any, Dict, List, Optional

from .connection import (execute_query, execute_query_one, execute,
                         execute_insert_returning_id)

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
                              importance, status, owned_by_agent, source_agent, visibility,
                              workspace_id)
        VALUES ('MEMORY', %s, %s, %s, %s,
                %s, 'ACTIVE', %s, %s, %s, %s)
        RETURNING entity_id
    """
    return execute_insert_returning_id(sql, [
        title[:500], content, summary, category,
        importance, owned_by_agent, source_agent, visibility, workspace_id,
    ])


def get_memory(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT entity_id, entity_type, title, content, summary, category,
               importance, status, owned_by_agent, source_agent, visibility,
               retrieval_count,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               TO_CHAR(updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at,
               TO_CHAR(expires_at, 'YYYY-MM-DD HH24:MI:SS') AS expires_at
        FROM entities
        WHERE entity_id = %s AND entity_type = 'MEMORY'
    """
    row = execute_query_one(sql, [entity_id])
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

    set_parts = [f"{k} = %s" for k in updates]
    set_parts.append("updated_at = CURRENT_TIMESTAMP")
    values = list(updates.values()) + [entity_id]

    sql = f"UPDATE entities SET {', '.join(set_parts)} WHERE entity_id = %s AND entity_type = 'MEMORY'"
    return execute(sql, values) > 0


def delete_memory(entity_id: str) -> bool:
    execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'MEMORY'", [entity_id])
    execute("DELETE FROM entity_edges WHERE source_id = %s AND source_type = 'MEMORY'", [entity_id])
    execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'MEMORY'", [entity_id])
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'MEMORY'"
    return execute(sql, [entity_id]) > 0


def list_memories(
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
    params: list = []

    if keyword:
        conditions.append("(title ILIKE %s OR content ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
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

    where = " AND ".join(conditions)
    params.extend([limit, offset])
    sql = f"""
        SELECT entity_id, entity_type, title, content, summary, category,
               importance, status, owned_by_agent, source_agent, visibility,
               retrieval_count,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM entities
        WHERE {where}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, params)]


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
    return list_memories(keyword=keyword, category=category, visibility=visibility,
                         owned_by_agent=owned_by_agent, workspace_id=workspace_id,
                         isolation_mode=isolation_mode, limit=limit, offset=offset)


def archive_memory(entity_id: str) -> bool:
    sql = """
        UPDATE entities SET status = 'ARCHIVED', updated_at = CURRENT_TIMESTAMP
        WHERE entity_id = %s AND entity_type = 'MEMORY'
    """
    return execute(sql, [entity_id]) > 0


def restore_memory(entity_id: str) -> bool:
    sql = """
        UPDATE entities SET status = 'ACTIVE', updated_at = CURRENT_TIMESTAMP
        WHERE entity_id = %s AND entity_type = 'MEMORY'
    """
    return execute(sql, [entity_id]) > 0


def get_memory_stats() -> Dict[str, Any]:
    row = execute_query_one("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE status = 'ACTIVE') AS active,
               COUNT(*) FILTER (WHERE status = 'ARCHIVED') AS archived,
               COUNT(DISTINCT category) AS category_count,
               AVG(importance) AS avg_importance
        FROM entities
        WHERE entity_type = 'MEMORY'
    """)
    if row:
        return {
            "total": int(row.get("total", 0)),
            "active": int(row.get("active", 0)),
            "archived": int(row.get("archived", 0)),
            "category_count": int(row.get("category_count", 0)),
            "avg_importance": float(row.get("avg_importance", 0) or 0),
        }
    return {"total": 0, "active": 0, "archived": 0, "category_count": 0, "avg_importance": 0}


def fuse_similar_memories(
    entity_ids: Optional[list] = None,
    similarity_threshold: float = 0.9,
    strategy: str = "merge",
) -> Dict[str, Any]:
    try:
        row = execute_query_one(
            "SELECT memory_fusion.fuse_similar(%s, %s, %s) AS result",
            [entity_ids, similarity_threshold, strategy]
        )
        if row and row.get("result"):
            import json
            return json.loads(row["result"]) if isinstance(row["result"], str) else row["result"]
    except Exception as e:
        logger.error("memory_fusion.fuse_similar call failed: %s", e)
    return {"fused": 0, "details": []}


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
