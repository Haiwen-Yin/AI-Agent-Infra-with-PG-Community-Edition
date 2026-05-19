"""PostgreSQL Memory System v2.0.0 - Knowledge API

CRUD + graph operations on entities (entity_type='KNOWLEDGE'),
knowledge_meta, and entity_edges.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id

logger = logging.getLogger(__name__)


def create_concept(name, concept_type, description=None, category=None,
                   content=None, source_type='MANUAL', source_entity_ids=None,
                   confidence=0.8, tags=None, metadata=None,
                   owned_by_agent=None, visibility='SHARED'):
    entity_sql = """
        INSERT INTO entities (entity_type, name, description, content, category,
                              priority, status, tags, metadata,
                              owned_by_agent, visibility)
        VALUES ('KNOWLEDGE', %s, %s, %s, %s, 1, 'ACTIVE', %s, %s, %s, %s)
        RETURNING entity_id
    """
    entity_params = (
        name[:500],
        description,
        content,
        category,
        json.dumps(tags or []),
        json.dumps(metadata or {}),
        owned_by_agent,
        visibility,
    )
    entity_id = execute_insert_returning_id(entity_sql, entity_params, id_column='entity_id')

    meta_sql = """
        INSERT INTO knowledge_meta (entity_id, source_type,
                                    source_entity_ids, confidence, validation_status)
        VALUES (%s, %s, %s, %s, 'PENDING')
    """
    execute(meta_sql, (
        entity_id,
        source_type,
        json.dumps(source_entity_ids or []),
        confidence,
    ))

    return entity_id


def get_concept(entity_id):
    sql = """
        SELECT e.entity_id, e.entity_type, e.name, e.description, e.content,
               e.category, e.status, e.tags, e.metadata,
               e.owned_by_agent, e.visibility,
               e.created_at, e.updated_at,
                km.source_type, km.source_entity_ids,
                km.confidence, km.validation_status, km.validated_at
        FROM entities e
        LEFT JOIN knowledge_meta km ON km.entity_id = e.entity_id
        WHERE e.entity_id = %s AND e.entity_type = 'KNOWLEDGE'
    """
    row = execute_query_one(sql, (entity_id,))
    if row is None:
        return None
    return _decorate_concept(row)


def update_concept(entity_id, **kwargs):
    entity_fields = {'name', 'description', 'content', 'category', 'status',
                     'tags', 'metadata', 'visibility'}
    jsonb_entity = {'tags', 'metadata'}
    meta_fields = {'source_type', 'source_entity_ids',
                   'confidence', 'validation_status'}
    jsonb_meta = {'source_entity_ids'}

    entity_updates = {}
    meta_updates = {}

    for k, v in kwargs.items():
        lk = k.lower()
        if lk in entity_fields:
            if lk in jsonb_entity and isinstance(v, (list, dict)):
                v = json.dumps(v)
            entity_updates[lk] = v
        elif lk in meta_fields:
            if lk in jsonb_meta and isinstance(v, (list, dict)):
                v = json.dumps(v)
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
        sql = "UPDATE knowledge_meta SET {} WHERE entity_id = %s".format(set_clause)
        affected += execute(sql, values)

    return affected > 0


def delete_concept(entity_id):
    execute("DELETE FROM knowledge_meta WHERE entity_id = %s", (entity_id,))
    execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s",
            (entity_id, entity_id))
    sql = "DELETE FROM entities WHERE entity_id = %s AND entity_type = 'KNOWLEDGE'"
    return execute(sql, (entity_id,)) > 0


def create_relationship(source_id, target_id, edge_type, strength=1.0,
                        confidence=0.8, properties=None):
    sql = """
        INSERT INTO entity_edges (source_id, target_id, edge_type, strength,
                                  confidence, properties)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING edge_id
    """
    return execute_insert_returning_id(sql, (
        source_id, target_id, edge_type, strength, confidence,
        json.dumps(properties or {}),
    ), id_column='edge_id')


def get_relationships(entity_id, direction='both'):
    if direction == 'outgoing':
        sql = """
            SELECT e.edge_id, e.source_id, e.target_id, e.edge_type,
                   e.strength, e.confidence, e.properties, e.created_at,
                   'outgoing' AS direction
            FROM entity_edges e
            WHERE e.source_id = %s
            ORDER BY e.created_at DESC
        """
        return execute_query(sql, (entity_id,))
    elif direction == 'incoming':
        sql = """
            SELECT e.edge_id, e.source_id, e.target_id, e.edge_type,
                   e.strength, e.confidence, e.properties, e.created_at,
                   'incoming' AS direction
            FROM entity_edges e
            WHERE e.target_id = %s
            ORDER BY e.created_at DESC
        """
        return execute_query(sql, (entity_id,))
    else:
        sql = """
            SELECT e.edge_id, e.source_id, e.target_id, e.edge_type,
                   e.strength, e.confidence, e.properties, e.created_at,
                   CASE
                       WHEN e.source_id = %s THEN 'outgoing'
                       ELSE 'incoming'
                   END AS direction
            FROM entity_edges e
            WHERE e.source_id = %s OR e.target_id = %s
            ORDER BY e.created_at DESC
        """
        return execute_query(sql, (entity_id, entity_id, entity_id))


def delete_relationship(edge_id):
    sql = "DELETE FROM entity_edges WHERE edge_id = %s"
    return execute(sql, (edge_id,)) > 0


def search_concepts(keyword=None, concept_type=None, category=None,
                    validation_status=None, limit=100):
    conditions = ["e.entity_type = 'KNOWLEDGE'"]
    params = []

    if keyword:
        conditions.append("(UPPER(e.name) LIKE UPPER(%s) OR UPPER(e.description) LIKE UPPER(%s))")
        like_val = '%' + keyword + '%'
        params.extend([like_val, like_val])

    if concept_type:
        conditions.append("e.category = %s")
        params.append(concept_type)

    if category:
        conditions.append("e.category = %s")
        params.append(category)

    if validation_status:
        conditions.append("km.validation_status = %s")
        params.append(validation_status)

    where = ' AND '.join(conditions)
    params.append(limit)

    sql = """
        SELECT e.entity_id, e.name, e.description, e.content, e.category,
               e.status, e.tags, e.metadata, e.owned_by_agent, e.visibility,
               e.created_at, e.updated_at,
               km.source_type, km.confidence,
               km.validation_status
        FROM entities e
        LEFT JOIN knowledge_meta km ON km.entity_id = e.entity_id
        WHERE {}
        ORDER BY e.created_at DESC
        LIMIT %s
    """.format(where)

    rows = execute_query(sql, params)
    return [_decorate_concept(r) for r in rows]


def get_statistics():
    entity_count_row = execute_query_one(
        "SELECT COUNT(*) AS cnt FROM entities WHERE entity_type = 'KNOWLEDGE'"
    )
    edge_count_row = execute_query_one(
        "SELECT COUNT(*) AS cnt FROM entity_edges"
    )
    type_rows = execute_query(
        """SELECT e.category, COUNT(*) AS cnt
           FROM entities e
           WHERE e.entity_type = 'KNOWLEDGE'
           GROUP BY e.category
           ORDER BY cnt DESC"""
    )
    status_rows = execute_query(
        """SELECT validation_status, COUNT(*) AS cnt
           FROM knowledge_meta
           GROUP BY validation_status
           ORDER BY cnt DESC"""
    )

    return {
        'total_concepts': entity_count_row['cnt'] if entity_count_row else 0,
        'total_edges': edge_count_row['cnt'] if edge_count_row else 0,
        'by_concept_type': {r['category']: r['cnt'] for r in type_rows},
        'by_validation_status': {r['validation_status']: r['cnt'] for r in status_rows},
    }


def get_concept_neighbors(entity_id, max_depth=2):
    sql = """
        WITH RECURSIVE neighbors AS (
            SELECT e.entity_id, e.name, e.category,
                   eg.edge_type, eg.strength,
                   1 AS depth
            FROM entity_edges eg
            JOIN entities e ON (e.entity_id = CASE
                WHEN eg.source_id = %s THEN eg.target_id
                ELSE eg.source_id END)
            WHERE (eg.source_id = %s OR eg.target_id = %s)
              AND e.entity_type = 'KNOWLEDGE'

            UNION ALL

            SELECT e2.entity_id, e2.name, e2.category,
                   eg2.edge_type, eg2.strength,
                   n.depth + 1
            FROM neighbors n
            JOIN entity_edges eg2 ON (eg2.source_id = n.entity_id OR eg2.target_id = n.entity_id)
            JOIN entities e2 ON (e2.entity_id = CASE
                WHEN eg2.source_id = n.entity_id THEN eg2.target_id
                ELSE eg2.source_id END)
            WHERE n.depth < %s
              AND e2.entity_type = 'KNOWLEDGE'
              AND e2.entity_id != %s
        )
        SELECT DISTINCT ON (entity_id) entity_id, name, category,
               edge_type, strength, depth
        FROM neighbors
        ORDER BY entity_id, depth ASC
    """
    return execute_query(sql, (entity_id, entity_id, entity_id, max_depth, entity_id))


def _decorate_concept(row):
    for col in ('tags', 'metadata', 'source_entity_ids'):
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
            elif col == 'source_entity_ids':
                row[col] = []
    return row
