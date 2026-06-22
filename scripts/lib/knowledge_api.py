"""AI Agent Infra v3.7.3 - PG Community Edition - Knowledge API

Knowledge CRUD, graph edges, spaced-review, and tagging.
Operates on entities (entity_type='KNOWLEDGE') + knowledge_meta + entity_edges.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import (execute_query, execute_query_one, execute,
                         execute_insert_returning_id)

logger = logging.getLogger(__name__)


def create_knowledge(
    title: str,
    content: str,
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: str = "INTERMEDIATE",
    category: Optional[str] = None,
    importance: int = 5,
    summary: Optional[str] = None,
    owned_by_agent: Optional[str] = None,
    visibility: str = "PRIVATE",
    workspace_id: Optional[str] = None,
) -> str:
    entity_sql = """
        INSERT INTO entities (entity_type, title, content, summary, category,
                              importance, status, owned_by_agent, source_agent, visibility,
                              workspace_id)
        VALUES ('KNOWLEDGE', %s, %s, %s, %s,
                %s, 'ACTIVE', %s, NULL, %s, %s)
        RETURNING entity_id
    """
    entity_id = execute_insert_returning_id(entity_sql, [
        title[:500], content, summary, category,
        importance, owned_by_agent, visibility, workspace_id,
    ])

    meta_sql = """
        INSERT INTO knowledge_meta (entity_id, entity_type, domain, topic, difficulty,
                                    review_count, next_review)
        VALUES (%s, 'KNOWLEDGE', %s, %s, %s, 0, CURRENT_TIMESTAMP + INTERVAL '7 days')
    """
    execute(meta_sql, [entity_id, domain, topic, difficulty])
    return entity_id


def get_knowledge(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count,
               TO_CHAR(e.expires_at, 'YYYY-MM-DD HH24:MI:SS') AS expires_at,
               TO_CHAR(e.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               TO_CHAR(e.updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               TO_CHAR(km.last_reviewed, 'YYYY-MM-DD HH24:MI:SS') AS last_reviewed,
               TO_CHAR(km.next_review, 'YYYY-MM-DD HH24:MI:SS') AS next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE e.entity_id = %s AND e.entity_type = 'KNOWLEDGE'
    """
    row = execute_query_one(sql, [entity_id])
    if row is None:
        return None
    return _row_to_dict(row)


def update_knowledge(entity_id: str, **kwargs) -> bool:
    entity_fields = {"title", "content", "summary", "category", "importance",
                     "status", "visibility", "expires_at"}
    meta_fields = {"domain", "topic", "difficulty"}

    entity_updates = {}
    meta_updates = {}

    for k, v in kwargs.items():
        lk = k.lower()
        if lk in entity_fields:
            entity_updates[lk] = v
        elif lk in meta_fields:
            meta_updates[lk] = v

    affected = 0

    if entity_updates:
        set_parts = [f"{k} = %s" for k in entity_updates]
        set_parts.append("updated_at = CURRENT_TIMESTAMP")
        values = list(entity_updates.values()) + [entity_id]
        sql = f"UPDATE entities SET {', '.join(set_parts)} WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'"
        affected += execute(sql, values)

    if meta_updates:
        set_clause = ", ".join(f"{k} = %s" for k in meta_updates)
        values = list(meta_updates.values()) + [entity_id]
        sql = f"UPDATE knowledge_meta SET {set_clause} WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'"
        affected += execute(sql, values)

    return affected > 0


def delete_knowledge(entity_id: str) -> bool:
    execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", [entity_id])
    execute("DELETE FROM knowledge_meta WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", [entity_id])
    execute("DELETE FROM entity_edges WHERE (source_id = %s AND source_type = 'KNOWLEDGE') OR target_id = %s", [entity_id, entity_id])
    execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", [entity_id])
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'"
    return execute(sql, [entity_id]) > 0


def list_knowledge(
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    keyword: Optional[str] = None,
    difficulty: Optional[str] = None,
    workspace_id: Optional[str] = None,
    isolation_mode: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    conditions = ["e.entity_type = 'KNOWLEDGE'"]
    params: list = []

    if domain:
        conditions.append("km.domain = %s")
        params.append(domain)
    if topic:
        conditions.append("km.topic = %s")
        params.append(topic)
    if difficulty:
        conditions.append("km.difficulty = %s")
        params.append(difficulty)
    if keyword:
        conditions.append("(e.title ILIKE %s OR e.content ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if isolation_mode == 'SHARED':
        conditions.append("e.workspace_id IS NULL")
    elif isolation_mode == 'ISOLATED' and workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)
    elif workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)

    where = " AND ".join(conditions)
    params.extend([limit, offset])
    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count,
               TO_CHAR(e.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               TO_CHAR(e.updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               TO_CHAR(km.last_reviewed, 'YYYY-MM-DD HH24:MI:SS') AS last_reviewed,
               TO_CHAR(km.next_review, 'YYYY-MM-DD HH24:MI:SS') AS next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE {where}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, params)]


def search_knowledge(
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    keyword: Optional[str] = None,
    difficulty: Optional[str] = None,
    workspace_id: Optional[str] = None,
    isolation_mode: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    return list_knowledge(domain=domain, topic=topic, keyword=keyword,
                          difficulty=difficulty, workspace_id=workspace_id,
                          isolation_mode=isolation_mode, limit=limit, offset=offset)


def schedule_review(entity_id: str, interval_days: int = 7) -> bool:
    sql = """
        UPDATE knowledge_meta
        SET next_review = CURRENT_TIMESTAMP + (%s || ' days')::interval
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'
    """
    return execute(sql, [interval_days, entity_id]) > 0


def record_review(entity_id: str) -> bool:
    sql = """
        UPDATE knowledge_meta
        SET review_count = review_count + 1,
            last_reviewed = CURRENT_TIMESTAMP,
            next_review = CURRENT_TIMESTAMP + LEAST(POWER(2, review_count + 1), 30) * INTERVAL '1 day'
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'
    """
    return execute(sql, [entity_id]) > 0


def get_due_reviews(limit: int = 50) -> List[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count,
               TO_CHAR(e.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
               TO_CHAR(e.updated_at, 'YYYY-MM-DD HH24:MI:SS') AS updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               TO_CHAR(km.last_reviewed, 'YYYY-MM-DD HH24:MI:SS') AS last_reviewed,
               TO_CHAR(km.next_review, 'YYYY-MM-DD HH24:MI:SS') AS next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE km.next_review <= CURRENT_TIMESTAMP AND e.status = 'ACTIVE'
        ORDER BY km.next_review ASC
        LIMIT %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, [limit])]


def get_concept_lineage(entity_id: str, max_depth: int = 5) -> List[Dict[str, Any]]:
    lineage = []
    visited = set()
    current_id = entity_id
    while current_id and current_id not in visited and len(lineage) < max_depth:
        visited.add(current_id)
        sql = """
            SELECT e.entity_id, e.entity_type, e.title, e.content,
                   ee.edge_type, ee.strength
            FROM entity_edges ee
            JOIN entities e ON e.entity_id = ee.source_id
            WHERE ee.target_id = %s AND ee.edge_type = 'DERIVED_FROM'
            LIMIT 1
        """
        row = execute_query_one(sql, [current_id])
        if not row:
            break
        lineage.append({
            "entity_id": row["entity_id"],
            "title": row["title"],
            "edge_type": row.get("edge_type"),
            "strength": row.get("strength"),
        })
        current_id = row["entity_id"]
    return lineage


def validate_concept(entity_id: str, validation_status: str = "VALIDATED") -> bool:
    sql = """
        UPDATE entities
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'
    """
    return execute(sql, [validation_status, entity_id]) > 0


def deprecate_concept(entity_id: str, reason: Optional[str] = None) -> bool:
    sql = """
        UPDATE entities
        SET status = 'DEPRECATED', updated_at = CURRENT_TIMESTAMP
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'
    """
    affected = execute(sql, [entity_id])
    if affected > 0 and reason:
        sql2 = """
            INSERT INTO entity_edges (source_id, source_type, target_id, edge_type, metadata)
            VALUES (%s, 'KNOWLEDGE', %s, 'DEPRECATED_BY',
                    jsonb_build_object('reason', %s))
        """
        execute(sql2, [entity_id, entity_id, reason])
    return affected > 0


def create_concept_version(
    entity_id: str,
    new_title: str,
    new_content: str,
    **kwargs,
) -> str:
    original = get_knowledge(entity_id)
    if not original:
        raise ValueError(f"Knowledge entity not found: {entity_id}")

    new_id = create_knowledge(
        title=new_title,
        content=new_content,
        domain=kwargs.get("domain", original.get("domain")),
        topic=kwargs.get("topic", original.get("topic")),
        difficulty=kwargs.get("difficulty", original.get("difficulty")),
        category=kwargs.get("category", original.get("category")),
        importance=kwargs.get("importance", original.get("importance")),
        summary=kwargs.get("summary", original.get("summary")),
        owned_by_agent=kwargs.get("owned_by_agent", original.get("owned_by_agent")),
        visibility=kwargs.get("visibility", original.get("visibility")),
        workspace_id=kwargs.get("workspace_id", original.get("workspace_id")),
    )

    sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type, strength)
        VALUES (%s, 'KNOWLEDGE', %s, 'VERSION_OF', 1.0)
    """
    execute(sql, [new_id, entity_id])
    return new_id


def extract_knowledge_from_memory(
    memory_entity_id: str,
    domain: Optional[str] = None,
    topic: Optional[str] = None,
) -> Optional[str]:
    from .memory_api import get_memory
    memory = get_memory(memory_entity_id)
    if not memory:
        return None

    knowledge_id = create_knowledge(
        title=memory.get("title", ""),
        content=memory.get("content", ""),
        domain=domain or memory.get("category"),
        topic=topic,
        category=memory.get("category"),
        importance=memory.get("importance", 5),
        summary=memory.get("summary"),
        owned_by_agent=memory.get("owned_by_agent"),
        visibility=memory.get("visibility", "PRIVATE"),
        workspace_id=memory.get("workspace_id"),
    )

    sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type, strength)
        VALUES (%s, 'KNOWLEDGE', %s, 'EXTRACTED_FROM', 1.0)
    """
    execute(sql, [knowledge_id, memory_entity_id])
    return knowledge_id


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
        "expires_at": row.get("expires_at"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "domain": row.get("domain"),
        "topic": row.get("topic"),
        "difficulty": row.get("difficulty"),
        "review_count": row.get("review_count"),
        "last_reviewed": row.get("last_reviewed"),
        "next_review": row.get("next_review"),
    }
