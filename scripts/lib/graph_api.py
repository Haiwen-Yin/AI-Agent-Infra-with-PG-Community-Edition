"""PostgreSQL Memory System v2.3.1 - Property Graph API

Core graph operations using Apache AGE Cypher queries via psycopg2.
Provides neighbor traversal, path finding, community detection, and graph analytics.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one

logger = logging.getLogger(__name__)

GRAPH_NAME = "memory_graph"

_AGE_SETUP_SQL = "LOAD 'age'; SET search_path = ag_catalog, \"$user\", public"


def _run_cypher(cypher_query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    sql = f"""
        {_AGE_SETUP_SQL};
        SELECT * FROM cypher(
            '{GRAPH_NAME}',
            $${cypher_query}$$
        ) AS (result agtype)
    """
    try:
        rows = execute_query(sql, params)
        return [_parse_age_row(r) for r in rows]
    except Exception as e:
        logger.error("Cypher query failed: %s", e)
        return []


def _parse_age_row(row: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for k, v in row.items():
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    result[k] = parsed
                else:
                    result[k] = v
            except (json.JSONDecodeError, TypeError):
                result[k] = v
        else:
            result[k] = v
    return result


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for k, v in row.items():
        if hasattr(v, 'read'):
            try:
                v = v.read()
            except Exception:
                v = str(v)
        if isinstance(v, bytes):
            try:
                v = v.decode('utf-8')
            except Exception:
                v = v.hex()
        result[k] = v
    return result


def get_neighbors(
    entity_id: str,
    direction: str = "both",
    edge_type: Optional[str] = None,
    min_strength: float = 0.0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    results = []

    if direction in ("outgoing", "both"):
        cypher = f"MATCH (a)-[r]->(b) WHERE a.entity_id = '{entity_id}'"
        if edge_type:
            cypher += f" AND type(r) = '{edge_type}'"
        if min_strength > 0:
            cypher += f" AND r.strength >= {min_strength}"
        cypher += f" RETURN b.entity_id AS neighbor_id, b.entity_type AS neighbor_type, b.title AS neighbor_title, type(r) AS edge_type, r.strength AS strength, r.confidence AS confidence ORDER BY r.strength DESC LIMIT {limit}"
        for r in _run_cypher(cypher):
            d = _row_to_dict(r)
            d["direction"] = "outgoing"
            results.append(d)

    if direction in ("incoming", "both"):
        cypher = f"MATCH (a)<-[r]-(b) WHERE a.entity_id = '{entity_id}'"
        if edge_type:
            cypher += f" AND type(r) = '{edge_type}'"
        if min_strength > 0:
            cypher += f" AND r.strength >= {min_strength}"
        cypher += f" RETURN b.entity_id AS neighbor_id, b.entity_type AS neighbor_type, b.title AS neighbor_title, type(r) AS edge_type, r.strength AS strength, r.confidence AS confidence ORDER BY r.strength DESC LIMIT {limit}"
        for r in _run_cypher(cypher):
            d = _row_to_dict(r)
            d["direction"] = "incoming"
            results.append(d)

    if not results:
        results = _get_neighbors_sql(entity_id, direction, edge_type, min_strength, limit)

    return results


def _get_neighbors_sql(
    entity_id: str,
    direction: str = "both",
    edge_type: Optional[str] = None,
    min_strength: float = 0.0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    results = []
    if direction in ("outgoing", "both"):
        sql = """SELECT e.entity_id AS neighbor_id, e.entity_type AS neighbor_type,
                        e.title AS neighbor_title, ee.edge_type, ee.strength, ee.confidence
                 FROM entity_edges ee
                 JOIN entities e ON e.entity_id = ee.target_id
                 WHERE ee.source_id = %s"""
        params_list = [entity_id]
        if edge_type:
            sql += " AND ee.edge_type = %s"
            params_list.append(edge_type)
        if min_strength > 0:
            sql += " AND ee.strength >= %s"
            params_list.append(min_strength)
        sql += " ORDER BY ee.strength DESC LIMIT %s"
        params_list.append(limit)
        for row in execute_query(sql, tuple(params_list)):
            results.append({**row, "direction": "outgoing"})

    if direction in ("incoming", "both"):
        sql = """SELECT e.entity_id AS neighbor_id, e.entity_type AS neighbor_type,
                        e.title AS neighbor_title, ee.edge_type, ee.strength, ee.confidence
                 FROM entity_edges ee
                 JOIN entities e ON e.entity_id = ee.source_id
                 WHERE ee.target_id = %s"""
        params_list = [entity_id]
        if edge_type:
            sql += " AND ee.edge_type = %s"
            params_list.append(edge_type)
        if min_strength > 0:
            sql += " AND ee.strength >= %s"
            params_list.append(min_strength)
        sql += " ORDER BY ee.strength DESC LIMIT %s"
        params_list.append(limit)
        for row in execute_query(sql, tuple(params_list)):
            results.append({**row, "direction": "incoming"})

    return results


def get_reachable(
    entity_id: str,
    max_hops: int = 3,
    edge_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conditions = ""
    if edge_type:
        conditions = f" WHERE type(r) = '{edge_type}'"
    cypher = f"MATCH (a)-[r*1..{max_hops}]->(v) WHERE a.entity_id = '{entity_id}'{conditions} RETURN DISTINCT v.entity_id AS entity_id, v.title AS title, v.entity_type AS entity_type LIMIT {limit}"
    return _run_cypher(cypher)


def get_shortest_path(
    source_id: str,
    target_id: str,
    max_hops: int = 5,
) -> Optional[List[Dict[str, Any]]]:
    if max_hops < 1:
        max_hops = 1
    if max_hops > 6:
        max_hops = 6

    cypher = f"MATCH path = shortestPath((a)-[r*1..{max_hops}]-(b)) WHERE a.entity_id = '{source_id}' AND b.entity_id = '{target_id}' RETURN path LIMIT 1"
    rows = _run_cypher(cypher)
    if not rows:
        return None

    path = []
    visited = set()
    sql_outgoing = """
        SELECT e.source_id, e.target_id, e.edge_type, e.strength
        FROM entity_edges e
        WHERE e.source_id = %s
        ORDER BY e.strength DESC
    """
    current_id = source_id
    while current_id != target_id and len(path) < max_hops and current_id not in visited:
        visited.add(current_id)
        edges = execute_query(sql_outgoing, (current_id,))
        found_next = False
        for edge in edges:
            next_id = edge.get("target_id")
            if next_id and next_id not in visited:
                entity_row = execute_query_one(
                    "SELECT entity_id, title, entity_type FROM entities WHERE entity_id = %s",
                    (next_id,)
                )
                path.append({
                    "entity_id": next_id,
                    "title": entity_row.get("title") if entity_row else None,
                    "entity_type": entity_row.get("entity_type") if entity_row else None,
                    "edge_type": edge.get("edge_type"),
                    "strength": edge.get("strength"),
                })
                current_id = next_id
                found_next = True
                break
        if not found_next:
            break

    return path if path else None


def find_similar_entities(
    entity_id: str,
    max_hops: int = 2,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    cypher = f"MATCH (a)-[r*1..{max_hops}]->(v) WHERE a.entity_id = '{entity_id}' AND v.entity_id <> '{entity_id}' RETURN DISTINCT v.entity_id AS entity_id, v.title AS title, v.entity_type AS entity_type, v.category AS category, v.importance AS importance ORDER BY v.importance DESC LIMIT {limit}"
    rows = _run_cypher(cypher)
    return [_row_to_dict(r) for r in rows]


def get_entity_context(
    entity_id: str,
    depth: int = 1,
) -> Dict[str, Any]:
    entity = execute_query_one("""
        SELECT entity_id, entity_type, title, category, status,
               importance, visibility, owned_by_agent, created_at
        FROM entities
        WHERE entity_id = %s
    """, (entity_id,))

    if entity is None:
        return None

    result = _row_to_dict(entity)

    neighbors = get_neighbors(entity_id, direction="both", limit=50)
    result["neighbors"] = neighbors
    result["neighbor_count"] = len(neighbors)

    neighbor_by_type: Dict[str, List] = {}
    neighbor_by_edge: Dict[str, List] = {}
    for n in neighbors:
        ntype = n.get("neighbor_type", "UNKNOWN")
        neighbor_by_type.setdefault(ntype, []).append(n)
        etype = n.get("edge_type", "UNKNOWN")
        neighbor_by_edge.setdefault(etype, []).append(n)

    result["neighbors_by_type"] = neighbor_by_type
    result["neighbors_by_edge"] = neighbor_by_edge

    return result


def get_graph_stats() -> Dict[str, Any]:
    vertex_count = execute_query_one(
        "SELECT COUNT(*) AS cnt FROM entities"
    )["cnt"]

    edge_count_row = execute_query_one(
        "SELECT COUNT(*) AS cnt FROM entity_edges"
    )
    edge_count = edge_count_row["cnt"] if edge_count_row else 0

    type_dist = execute_query("""
        SELECT entity_type, COUNT(*) AS cnt
        FROM entities
        GROUP BY entity_type
        ORDER BY cnt DESC
    """)

    edge_dist = execute_query("""
        SELECT edge_type, COUNT(*) AS cnt
        FROM entity_edges
        GROUP BY edge_type
        ORDER BY cnt DESC
    """)

    avg_degree_row = execute_query_one("""
        SELECT COALESCE(AVG(deg), 0) AS avg_deg FROM (
            SELECT entity_id, COUNT(*) AS deg
            FROM (
                SELECT source_id AS entity_id FROM entity_edges
                UNION ALL
                SELECT target_id AS entity_id FROM entity_edges
            ) sub
            GROUP BY entity_id
        ) deg_q
    """)
    avg_degree = float(avg_degree_row["avg_deg"]) if avg_degree_row else 0.0

    return {
        "vertex_count": vertex_count,
        "edge_count": edge_count,
        "avg_degree": round(avg_degree, 2),
        "entity_type_distribution": {r["entity_type"]: r["cnt"] for r in type_dist},
        "edge_type_distribution": {r["edge_type"]: r["cnt"] for r in edge_dist},
    }


def get_subgraph(
    entity_ids: List[str],
    include_intermediate: bool = False,
) -> Dict[str, Any]:
    if not entity_ids:
        return {"vertices": [], "edges": []}

    placeholders = ", ".join(["%s"] * len(entity_ids))

    vertices = execute_query(f"""
        SELECT entity_id, entity_type, title, category, status,
               importance, visibility, owned_by_agent
        FROM entities
        WHERE entity_id IN ({placeholders})
        ORDER BY entity_type, title
    """, tuple(entity_ids))

    edges = execute_query(f"""
        SELECT e.edge_id, e.source_id, e.source_type, e.target_id,
               e.edge_type, e.strength, e.confidence
        FROM entity_edges e
        WHERE e.source_id IN ({placeholders})
           OR e.target_id IN ({placeholders})
        ORDER BY e.strength DESC
    """, tuple(entity_ids) * 2)

    if include_intermediate:
        extra_ids = set()
        for e in edges:
            if e["source_id"] not in entity_ids:
                extra_ids.add(e["source_id"])
            if e["target_id"] not in entity_ids:
                extra_ids.add(e["target_id"])
        if extra_ids:
            extra_ph = ", ".join(["%s"] * len(extra_ids))
            extra_verts = execute_query(f"""
                SELECT entity_id, entity_type, title, category, status,
                       importance, visibility, owned_by_agent
                FROM entities
                WHERE entity_id IN ({extra_ph})
            """, tuple(extra_ids))
            vertices.extend(extra_verts)

    return {
        "vertices": [_row_to_dict(v) for v in vertices],
        "edges": [_row_to_dict(e) for e in edges],
    }


def find_communities(
    entity_type: Optional[str] = None,
    min_connections: int = 2,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    type_condition = "AND v.entity_type = %s" if entity_type else ""

    sql = f"""
        SELECT v.entity_id, v.title, v.entity_type, v.category,
               COUNT(DISTINCT e2.target_id) + COUNT(DISTINCT e3.source_id) AS connection_count
        FROM entities v
        LEFT JOIN entity_edges e2 ON e2.source_id = v.entity_id
        LEFT JOIN entity_edges e3 ON e3.target_id = v.entity_id
        WHERE 1=1 {type_condition}
        GROUP BY v.entity_id, v.title, v.entity_type, v.category
        HAVING COUNT(DISTINCT e2.target_id) + COUNT(DISTINCT e3.source_id) >= %s
        ORDER BY connection_count DESC
        LIMIT %s
    """
    if entity_type:
        rows = execute_query(sql, (entity_type, min_connections, limit))
    else:
        rows = execute_query(sql, (min_connections, limit))
    return [_row_to_dict(r) for r in rows]


def graph_search(
    keyword: Optional[str] = None,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conditions = ["a.importance >= %s"]
    params: List[Any] = [min_importance]

    if keyword:
        conditions.append("(UPPER(a.title) LIKE UPPER(%s) OR UPPER(a.content) LIKE UPPER(%s) OR EXISTS (SELECT 1 FROM knowledge_meta km WHERE km.entity_id = a.entity_id AND (UPPER(km.domain) LIKE UPPER(%s) OR UPPER(km.topic) LIKE UPPER(%s))))")
        params.extend(['%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'])
    if entity_type:
        conditions.append("a.entity_type = %s")
        params.append(entity_type)
    if category:
        conditions.append("a.category = %s")
        params.append(category)

    params.append(limit)
    where = ' AND '.join(conditions)

    sql = f"""
        SELECT a.entity_id, a.title, a.entity_type, a.category,
               a.importance, a.status, a.visibility
        FROM entities a
        WHERE {where}
        ORDER BY a.importance DESC
        LIMIT %s
    """
    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]