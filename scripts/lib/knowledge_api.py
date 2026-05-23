"""PostgreSQL Memory System v2.2.0 - Knowledge API

Knowledge CRUD, graph edges, spaced-review, and tagging.
Operates on entities (entity_type='KNOWLEDGE') + knowledge_meta + entity_edges.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

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
                              importance, status, owned_by_agent, source_agent,
                              visibility, retrieval_count, workspace_id)
        VALUES ('KNOWLEDGE', %s, %s, %s, %s, %s, 'ACTIVE', %s, %s,
                %s, 0, %s)
        RETURNING entity_id
    """
    params = (
        title[:500],
        content,
        summary,
        category,
        importance,
        owned_by_agent,
        owned_by_agent,
        visibility,
        workspace_id,
    )
    entity_id = execute_insert_returning_id(entity_sql, params)

    meta_sql = """
        INSERT INTO knowledge_meta (entity_id, entity_type, domain, topic, difficulty,
                                    review_count, next_review)
        VALUES (%s, 'KNOWLEDGE', %s, %s, %s, 0, NOW() + INTERVAL '7 days')
    """
    execute(meta_sql, (entity_id, domain, topic, difficulty))
    return entity_id


def get_knowledge(entity_id: str) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count, e.expires_at, e.created_at, e.updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               km.last_reviewed, km.next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE e.entity_id = %s AND e.entity_type = 'KNOWLEDGE'
    """
    row = execute_query_one(sql, (entity_id,))
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
        set_parts = ["{} = %s".format(k) for k in entity_updates]
        set_parts.append("updated_at = NOW()")
        values = list(entity_updates.values())
        values.append(entity_id)
        sql = "UPDATE entities SET {} WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'".format(
            ', '.join(set_parts)
        )
        affected += execute(sql, values)

    if meta_updates:
        set_clause = ", ".join("{} = %s".format(k) for k in meta_updates)
        values = list(meta_updates.values())
        values.append(entity_id)
        sql = "UPDATE knowledge_meta SET {} WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'".format(set_clause)
        affected += execute(sql, values)

    return affected > 0


def delete_knowledge(entity_id: str) -> bool:
    execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", (entity_id,))
    execute("DELETE FROM knowledge_meta WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", (entity_id,))
    execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s", (entity_id, entity_id))
    execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'", (entity_id,))
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'"
    return execute(sql, (entity_id,)) > 0


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
    conditions = ["e.entity_type = 'KNOWLEDGE'"]
    params: List[Any] = []

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
        conditions.append("(UPPER(e.title) LIKE UPPER(%s) OR UPPER(e.content) LIKE UPPER(%s))")
        like_val = '%' + keyword + '%'
        params.extend([like_val, like_val])
    if isolation_mode == 'SHARED':
        conditions.append("e.workspace_id IS NULL")
    elif isolation_mode == 'ISOLATED' and workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)
    elif workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)

    where = ' AND '.join(conditions)
    params.extend([limit, offset])

    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count, e.created_at, e.updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               km.last_reviewed, km.next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE {}
        ORDER BY e.created_at DESC
        LIMIT %s OFFSET %s
    """.format(where)

    return [_row_to_dict(r) for r in execute_query(sql, params)]


def get_due_reviews(limit: int = 50) -> List[Dict[str, Any]]:
    sql = """
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
               e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
               e.retrieval_count, e.created_at, e.updated_at,
               km.domain, km.topic, km.difficulty, km.review_count,
               km.last_reviewed, km.next_review
        FROM entities e
        JOIN knowledge_meta km ON km.entity_id = e.entity_id
                               AND km.entity_type = 'KNOWLEDGE'
        WHERE km.next_review <= NOW() AND e.status = 'ACTIVE'
        ORDER BY km.next_review ASC
        LIMIT %s
    """
    return [_row_to_dict(r) for r in execute_query(sql, (limit,))]


def record_review(entity_id: str) -> bool:
    sql = """
        UPDATE knowledge_meta
        SET review_count = review_count + 1,
            last_reviewed = NOW(),
            next_review = NOW() + LEAST(POWER(2, review_count + 1), 30) * INTERVAL '1 day'
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'
    """
    return execute(sql, (entity_id,)) > 0


def add_edge(
    source_id: str,
    source_type: str,
    target_id: str,
    edge_type: str,
    strength: float = 1.0,
    confidence: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    sql = """
        INSERT INTO entity_edges (source_id, source_type, target_id, edge_type,
                                  strength, confidence, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING edge_id
    """
    return execute_insert_returning_id(sql, (
        source_id, source_type, target_id, edge_type,
        strength, confidence,
        json.dumps(metadata) if metadata else None,
    ), id_column="edge_id")


def get_edges(entity_id: str, direction: str = "both") -> List[Dict[str, Any]]:
    if direction == "outgoing":
        sql = """
            SELECT edge_id, source_id, source_type, target_id, edge_type,
                   strength, confidence, metadata, created_at
            FROM entity_edges
            WHERE source_id = %s
            ORDER BY created_at DESC
        """
    elif direction == "incoming":
        sql = """
            SELECT edge_id, source_id, source_type, target_id, edge_type,
                   strength, confidence, metadata, created_at
            FROM entity_edges
            WHERE target_id = %s
            ORDER BY created_at DESC
        """
    else:
        sql = """
            SELECT edge_id, source_id, source_type, target_id, edge_type,
                   strength, confidence, metadata, created_at,
                   'outgoing' AS direction
            FROM entity_edges
            WHERE source_id = %s
            UNION ALL
            SELECT edge_id, source_id, source_type, target_id, edge_type,
                   strength, confidence, metadata, created_at,
                   'incoming' AS direction
            FROM entity_edges
            WHERE target_id = %s
            ORDER BY created_at DESC
        """
    if direction == "both":
        rows = execute_query(sql, (entity_id, entity_id))
    else:
        rows = execute_query(sql, (entity_id,))
    result = []
    for r in rows:
        edge = {
            "edge_id": r.get("edge_id"),
            "source_id": r.get("source_id"),
            "source_type": r.get("source_type"),
            "target_id": r.get("target_id"),
            "edge_type": r.get("edge_type"),
            "strength": r.get("strength"),
            "confidence": r.get("confidence"),
            "metadata": r.get("metadata"),
            "created_at": r.get("created_at"),
        }
        if direction == "both":
            edge["direction"] = r.get("direction")
        if isinstance(edge["metadata"], str):
            try:
                edge["metadata"] = json.loads(edge["metadata"])
            except (json.JSONDecodeError, TypeError):
                pass
        result.append(edge)
    return result


def add_knowledge_tags(entity_id: str, tag_names: List[str]) -> int:
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
            "INSERT INTO entity_tags (entity_id, entity_type, tag_id) VALUES (%s, 'KNOWLEDGE', %s) ON CONFLICT DO NOTHING",
            (entity_id, tag_id)
        )
        if affected > 0:
            added += 1
    return added


def get_knowledge_tags(entity_id: str) -> List[Dict[str, Any]]:
    sql = """
        SELECT t.tag_id, t.tag_name, t.tag_group
        FROM entity_tags et
        JOIN tags t ON et.tag_id = t.tag_id
        WHERE et.entity_id = %s AND et.entity_type = 'KNOWLEDGE'
    """
    rows = execute_query(sql, (entity_id,))
    return [
        {"tag_id": r["tag_id"], "tag_name": r["tag_name"], "tag_group": r.get("tag_group")}
        for r in rows
    ]


def remove_knowledge_tag(entity_id: str, tag_id: int) -> bool:
    sql = """
        DELETE FROM entity_tags
        WHERE entity_id = %s AND entity_type = 'KNOWLEDGE' AND tag_id = %s
    """
    return execute(sql, (entity_id, tag_id)) > 0


def count_knowledge(domain: Optional[str] = None) -> int:
    if domain:
        sql = """
            SELECT COUNT(*) AS cnt
            FROM entities e
            JOIN knowledge_meta km ON km.entity_id = e.entity_id AND km.entity_type = 'KNOWLEDGE'
            WHERE e.entity_type = 'KNOWLEDGE' AND km.domain = %s
        """
        row = execute_query_one(sql, (domain,))
    else:
        sql = "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'KNOWLEDGE'"
        row = execute_query_one(sql)
    return row['cnt'] if row else 0


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