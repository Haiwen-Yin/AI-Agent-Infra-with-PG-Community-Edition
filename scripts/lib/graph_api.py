"""AI Agent Infra v3.8.0 - PG Community Edition - Property Graph API

Core graph operations using Apache AGE cypher queries with SQL fallback.
Provides neighbor traversal, path finding, community detection, and graph analytics.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from .connection import execute_query, execute_query_one, execute, execute_insert_returning_id

logger = logging.getLogger(__name__)

GRAPH_NAME = "memory_graph"

_AGE_AVAILABLE = None


def _check_age() -> bool:
    global _AGE_AVAILABLE
    if _AGE_AVAILABLE is not None:
        return _AGE_AVAILABLE
    try:
        execute_query_one("SELECT * FROM cypher(%s, $$RETURN 1$$) AS (result agtype) LIMIT 1", [GRAPH_NAME])
        _AGE_AVAILABLE = True
    except Exception:
        _AGE_AVAILABLE = False
        logger.info("Apache AGE not available, using SQL fallback for graph operations")
    return _AGE_AVAILABLE


def get_neighbors(
    entity_id: str,
    direction: str = "both",
    edge_type: Optional[str] = None,
    min_strength: float = 0.0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    results = []

    if direction in ("outgoing", "both"):
        conditions = ["e.source_id = %s"]
        params: list = [entity_id]
        if edge_type:
            conditions.append("e.edge_type = %s")
            params.append(edge_type)
        if min_strength > 0:
            conditions.append("e.strength >= %s")
            params.append(min_strength)
        params.append(limit)
        where = " AND ".join(conditions)

        rows = execute_query(f"""
            SELECT e.target_id AS neighbor_id, ent.entity_type AS neighbor_type, ent.title AS neighbor_title,
                   e.edge_id, e.edge_type, e.strength, e.confidence
            FROM entity_edges e
            JOIN entities ent ON ent.entity_id = e.target_id
            WHERE {where}
            ORDER BY e.strength DESC
            LIMIT %s
        """, params)
        for r in rows:
            d = _row_to_dict(r)
            d["direction"] = "outgoing"
            results.append(d)

    if direction in ("incoming", "both"):
        conditions = ["e.target_id = %s"]
        params = [entity_id]
        if edge_type:
            conditions.append("e.edge_type = %s")
            params.append(edge_type)
        if min_strength > 0:
            conditions.append("e.strength >= %s")
            params.append(min_strength)
        params.append(limit)
        where = " AND ".join(conditions)

        rows = execute_query(f"""
            SELECT e.source_id AS neighbor_id, ent.entity_type AS neighbor_type, ent.title AS neighbor_title,
                   e.edge_id, e.edge_type, e.strength, e.confidence
            FROM entity_edges e
            JOIN entities ent ON ent.entity_id = e.source_id
            WHERE {where}
            ORDER BY e.strength DESC
            LIMIT %s
        """, params)
        for r in rows:
            d = _row_to_dict(r)
            d["direction"] = "incoming"
            results.append(d)

    return results


def get_reachable(
    entity_id: str,
    max_hops: int = 3,
    edge_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if _check_age():
        edge_filter = f"WHERE e.edge_type = '{edge_type}'" if edge_type else ""
        try:
            rows = execute_query(f"""
                SELECT * FROM cypher(%s, $$
                    MATCH (a)-[e*1..{max_hops}]->(v)
                    WHERE a.entity_id = '{entity_id}'
                    {edge_filter}
                    RETURN v.entity_id, v.title, v.entity_type
                    LIMIT {limit}
                $$) AS (entity_id agtype, title agtype, entity_type agtype)
            """, [GRAPH_NAME])
            return [_row_to_dict(r) for r in rows]
        except Exception as e:
            logger.debug("AGE get_reachable failed, using BFS fallback: %s", e)

    visited = {entity_id}
    frontier = {entity_id}
    result = []

    for hop in range(max_hops):
        if not frontier:
            break
        next_frontier = set()
        placeholders = ", ".join(["%s"] * len(frontier))
        params = list(frontier)
        edge_filter = " AND edge_type = %s" if edge_type else ""
        if edge_type:
            params.append(edge_type)

        rows = execute_query(f"""
            SELECT DISTINCT target_id AS entity_id FROM entity_edges
            WHERE source_id IN ({placeholders}){edge_filter}
        """, params)

        for r in rows:
            eid = r["entity_id"]
            if eid not in visited:
                visited.add(eid)
                next_frontier.add(eid)
                result.append(r)
        frontier = next_frontier

    return result[:limit]


def get_shortest_path(
    source_id: str,
    target_id: str,
    max_hops: int = 5,
) -> Optional[List[Dict[str, Any]]]:
    if _check_age():
        try:
            rows = execute_query(f"""
                SELECT * FROM cypher(%s, $$
                    MATCH path = shortestPath((a)-[e*1..{max_hops}]-(b))
                    WHERE a.entity_id = '{source_id}' AND b.entity_id = '{target_id}'
                    RETURN path
                    LIMIT 1
                $$) AS (path agtype)
            """, [GRAPH_NAME])
            if rows:
                return _parse_age_path(rows[0].get("path"))
        except Exception as e:
            logger.debug("AGE shortest_path failed, using BFS fallback: %s", e)

    path = _bfs_shortest_path(source_id, target_id, max_hops)
    return path


def _bfs_shortest_path(source_id: str, target_id: str, max_hops: int) -> Optional[List[Dict]]:
    from collections import deque
    queue = deque([(source_id, [{"entity_id": source_id}])])
    visited = {source_id}

    while queue:
        current_id, path = queue.popleft()
        if len(path) > max_hops * 2:
            break

        rows = execute_query("""
            SELECT e.target_id, e.edge_type, e.strength, ent.title, ent.entity_type
            FROM entity_edges e
            JOIN entities ent ON ent.entity_id = e.target_id
            WHERE e.source_id = %s
        """, [current_id])

        for r in rows:
            nid = r["target_id"]
            if nid == target_id:
                path.append({"edge_type": r["edge_type"], "strength": r["strength"]})
                path.append({"entity_id": nid, "title": r["title"], "entity_type": r["entity_type"]})
                return path
            if nid not in visited:
                visited.add(nid)
                new_path = path + [
                    {"edge_type": r["edge_type"], "strength": r["strength"]},
                    {"entity_id": nid, "title": r["title"], "entity_type": r["entity_type"]},
                ]
                queue.append((nid, new_path))

    return None


def _parse_age_path(path_data) -> Optional[List[Dict]]:
    if not path_data:
        return None
    try:
        if isinstance(path_data, str):
            path_data = json.loads(path_data)
        return path_data if isinstance(path_data, list) else None
    except Exception:
        return None


def find_similar_entities(
    entity_id: str,
    max_hops: int = 2,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    reachable = get_reachable(entity_id, max_hops=max_hops, limit=limit)
    return [r for r in reachable if r.get("entity_id") != entity_id]


def get_entity_context(
    entity_id: str,
    depth: int = 1,
) -> Dict[str, Any]:
    entity = execute_query_one("""
        SELECT entity_id, entity_type, title, category, status,
               importance, visibility, owned_by_agent,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM entities
        WHERE entity_id = %s
    """, [entity_id])

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
    """, entity_ids)

    edges = execute_query(f"""
        SELECT e.edge_id, e.source_id, e.source_type, e.target_id,
               e.edge_type, e.strength, e.confidence
        FROM entity_edges e
        WHERE e.source_id IN ({placeholders})
           OR e.target_id IN ({placeholders})
        ORDER BY e.strength DESC
    """, entity_ids + entity_ids)

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
            """, list(extra_ids))
            vertices = list(vertices) + extra_verts

    return {
        "vertices": [_row_to_dict(v) for v in vertices],
        "edges": [_row_to_dict(e) for e in edges],
    }


def find_communities(
    entity_type: Optional[str] = None,
    min_connections: int = 2,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    type_condition = "AND e.entity_type = %s" if entity_type else ""
    params: list = [min_connections, limit]
    if entity_type:
        params.insert(0, entity_type)

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
    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]


def graph_search(
    keyword: Optional[str] = None,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conditions = ["importance >= %s"]
    params: list = [min_importance]

    if keyword:
        conditions.append("title ILIKE %s")
        params.append(f"%{keyword}%")
    if entity_type:
        conditions.append("entity_type = %s")
        params.append(entity_type)
    if category:
        conditions.append("category = %s")
        params.append(category)

    params.append(limit)
    where = " AND ".join(conditions)

    rows = execute_query(f"""
        SELECT entity_id, title, entity_type, category,
               importance, status, visibility
        FROM entities
        WHERE {where}
        ORDER BY importance DESC
        LIMIT %s
    """, params)
    return [_row_to_dict(r) for r in rows]


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
    meta_val = json.dumps(metadata) if metadata else None
    edge_id = execute_insert_returning_id(sql, [source_id, source_type, target_id, edge_type,
                               strength, confidence, meta_val], id_column="edge_id")
    return edge_id


def remove_edge(edge_id: str) -> bool:
    return execute("DELETE FROM entity_edges WHERE edge_id = %s", [edge_id]) > 0


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for k, v in row.items():
        if isinstance(v, bytes):
            try:
                v = v.decode('utf-8')
            except Exception:
                v = v.hex()
        result[k] = v
    return result


def get_graph_stats() -> Dict[str, Any]:
    from .connection import execute_query_one
    node_count = execute_query_one("SELECT COUNT(*) AS cnt FROM entities")
    edge_count = execute_query_one("SELECT COUNT(*) AS cnt FROM entity_edges")
    type_count = execute_query_one("SELECT COUNT(DISTINCT entity_type) AS cnt FROM entities")
    return {
        "node_count": node_count["cnt"] if node_count else 0,
        "edge_count": edge_count["cnt"] if edge_count else 0,
        "type_count": type_count["cnt"] if type_count else 0,
    }
