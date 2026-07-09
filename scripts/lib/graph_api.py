"""AI Agent Infra v3.10.0 - PG Community Edition - Property Graph API

Core graph operations using SQL queries against entity_edges table.
Provides neighbor traversal, path finding, community detection, and graph analytics.
v3.10.0: Universal Property Graph expansion - 30+ functions across 8 domains.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from .connection import execute, execute_query, execute_query_one

logger = logging.getLogger(__name__)

GRAPH_NAME = "oracle_memory_graph"


def get_neighbors(
    entity_id: str,
    direction: str = "both",
    edge_type: Optional[str] = None,
    min_strength: float = 0.0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    results = []

    if direction in ("outgoing", "both"):
        conditions = ["a.entity_id = :eid"]
        if edge_type:
            conditions.append("e.edge_type = :edge_type")
        if min_strength > 0:
            conditions.append("e.strength >= :min_strength")
        full_where = " AND ".join(conditions)

        sql = f"""
            SELECT gt.neighbor_id, gt.neighbor_type, gt.neighbor_title,
                   gt.edge_id, gt.edge_type, gt.strength, gt.confidence
            FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
              WHERE {full_where}
              COLUMNS(
                b.entity_id AS neighbor_id,
                b.entity_type AS neighbor_type,
                b.title AS neighbor_title,
                e.edge_id AS edge_id,
                e.edge_type AS edge_type,
                e.strength AS strength,
                e.confidence AS confidence
              )
            ) gt
            ORDER BY gt.strength DESC
            FETCH FIRST :lim ROWS ONLY
        """
        params: Dict[str, Any] = {"eid": entity_id, "lim": limit}
        if edge_type:
            params["edge_type"] = edge_type
        if min_strength > 0:
            params["min_strength"] = min_strength

        for r in execute_query(sql, params):
            d = _row_to_dict(r)
            d["direction"] = "outgoing"
            results.append(d)

    if direction in ("incoming", "both"):
        conditions = ["a.entity_id = :eid"]
        if edge_type:
            conditions.append("e.edge_type = :edge_type")
        if min_strength > 0:
            conditions.append("e.strength >= :min_strength")
        full_where = " AND ".join(conditions)

        sql = f"""
            SELECT gt.neighbor_id, gt.neighbor_type, gt.neighbor_title,
                   gt.edge_id, gt.edge_type, gt.strength, gt.confidence
            FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
              WHERE {full_where}
              COLUMNS(
                b.entity_id AS neighbor_id,
                b.entity_type AS neighbor_type,
                b.title AS neighbor_title,
                e.edge_id AS edge_id,
                e.edge_type AS edge_type,
                e.strength AS strength,
                e.confidence AS confidence
              )
            ) gt
            ORDER BY gt.strength DESC
            FETCH FIRST :lim ROWS ONLY
        """
        params = {"eid": entity_id, "lim": limit}
        if edge_type:
            params["edge_type"] = edge_type
        if min_strength > 0:
            params["min_strength"] = min_strength

        for r in execute_query(sql, params):
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
    conditions = [f"a.entity_id = :eid"]
    if edge_type:
        conditions.append(f"e.edge_type = :edge_type")
    full_where = " AND ".join(conditions)

    sql = f"""
        SELECT gt.entity_id, gt.title, gt.entity_type
        FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
          WHERE {full_where}
          COLUMNS(v.entity_id, v.title, v.entity_type)
        ) gt
        FETCH FIRST :lim ROWS ONLY
    """
    params: Dict[str, Any] = {"eid": entity_id, "lim": limit}
    if edge_type:
        params["edge_type"] = edge_type

    return execute_query(sql, params)


def get_shortest_path(
    source_id: str,
    target_id: str,
    max_hops: int = 5,
) -> Optional[List[Dict[str, Any]]]:
    if max_hops < 1:
        max_hops = 1
    if max_hops > 6:
        max_hops = 6

    path_cols = []
    join_clauses = []
    for i in range(1, max_hops + 1):
        path_cols.append(f"v{i}.entity_id AS hop{i}_id")
        path_cols.append(f"v{i}.title AS hop{i}_title")
        path_cols.append(f"v{i}.entity_type AS hop{i}_type")
        if i < max_hops:
            path_cols.append(f"e{i}.edge_type AS hop{i}_edge")
            path_cols.append(f"e{i}.strength AS hop{i}_strength")

    match_parts = ["(a IS entities)"]
    for i in range(1, max_hops + 1):
        match_parts.append(f"-[e{i}]->(v{i} IS entities)")
    match_pattern = "".join(match_parts)

    where_parts = [f"a.entity_id = :src", f"v{max_hops}.entity_id = :tgt"]
    full_where = " AND ".join(where_parts)

    sql = f"""
        SELECT {', '.join(path_cols)}
        FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
          WHERE {full_where}
          COLUMNS({', '.join(path_cols)})
        ) gt
        LIMIT 1
    """
    params = {"src": source_id, "tgt": target_id}
    row = execute_query_one(sql, params)
    if row is None:
        return None

    path = []
    for i in range(1, max_hops + 1):
        hop_id = row.get(f"hop{i}_id")
        if hop_id is None:
            break
        path.append({
            "entity_id": hop_id,
            "title": row.get(f"hop{i}_title"),
            "entity_type": row.get(f"hop{i}_type"),
        })
        if i < max_hops:
            edge = row.get(f"hop{i}_edge")
            if edge is not None:
                path.append({
                    "edge_type": edge,
                    "strength": row.get(f"hop{i}_strength"),
                })

    return path


def find_similar_entities(
    entity_id: str,
    max_hops: int = 2,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    sql = f"""
        SELECT gt.entity_id, gt.title, gt.entity_type,
               gt.category, gt.importance
        FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
          WHERE a.entity_id = :eid AND v.entity_id <> :eid
          COLUMNS(v.entity_id, v.title, v.entity_type,
                  v.category, v.importance)
        ) gt
        ORDER BY gt.importance DESC
        FETCH FIRST :lim ROWS ONLY
    """
    rows = execute_query(sql, {"eid": entity_id, "lim": limit})
    return [_row_to_dict(r) for r in rows]


def get_entity_context(
    entity_id: str,
    depth: int = 1,
) -> Dict[str, Any]:
    entity = execute_query_one("""
        SELECT entity_id, entity_type, title, category, status,
               importance, VISIBILITY, OWNED_BY_AGENT,
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM entities
        WHERE entity_id = :eid
    """, {"eid": entity_id})

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
        "SELECT COUNT(*) AS CNT FROM entities"
    )["cnt"]

    edge_count_row = execute_query_one(
        "SELECT COUNT(*) AS CNT FROM entity_edges"
    )
    edge_count = edge_count_row["cnt"] if edge_count_row else 0

    type_dist = execute_query("""
        SELECT entity_type, COUNT(*) AS CNT
        FROM entities
        GROUP BY entity_type
        ORDER BY CNT DESC
    """)

    edge_dist = execute_query("""
        SELECT edge_type, COUNT(*) AS CNT
        FROM entity_edges
        GROUP BY edge_type
        ORDER BY CNT DESC
    """)

    avg_degree_row = execute_query_one("""
        SELECT NVL(AVG(deg), 0) AS AVG_DEG FROM (
            SELECT entity_id, COUNT(*) AS deg
            FROM (
                SELECT source_id AS entity_id FROM entity_edges
                UNION ALL
                SELECT target_id AS entity_id FROM entity_edges
            )
            GROUP BY entity_id
        )
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

    placeholders = ", ".join([f":id{i}" for i in range(len(entity_ids))])
    src_placeholders = ", ".join([f":sid{i}" for i in range(len(entity_ids))])
    tgt_placeholders = ", ".join([f":tid{i}" for i in range(len(entity_ids))])
    params = {f"id{i}": eid for i, eid in enumerate(entity_ids)}

    vertices = execute_query(f"""
        SELECT entity_id, entity_type, title, category, status,
               importance, VISIBILITY, OWNED_BY_AGENT
        FROM entities
        WHERE entity_id IN ({placeholders})
        ORDER BY entity_type, title
    """, params)

    edge_params = {**{f"sid{i}": eid for i, eid in enumerate(entity_ids)},
                   **{f"tid{i}": eid for i, eid in enumerate(entity_ids)}}
    edges = execute_query(f"""
        SELECT e.edge_id, e.source_id, e.source_type, e.target_id,
               e.edge_type, e.strength, e.confidence
        FROM entity_edges e
        WHERE e.source_id IN ({src_placeholders})
           OR e.target_id IN ({tgt_placeholders})
        ORDER BY e.strength DESC
    """, edge_params)

    if include_intermediate:
        extra_ids = set()
        for e in edges:
            if e["source_id"] not in entity_ids:
                extra_ids.add(e["source_id"])
            if e["target_id"] not in entity_ids:
                extra_ids.add(e["target_id"])
        if extra_ids:
            extra_ph = ", ".join([f":xid{i}" for i, _ in enumerate(extra_ids)])
            extra_params = {f"xid{i}": eid for i, eid in enumerate(extra_ids)}
            extra_verts = execute_query(f"""
                SELECT entity_id, entity_type, title, category, status,
                       importance, VISIBILITY, OWNED_BY_AGENT
                FROM entities
                WHERE entity_id IN ({extra_ph})
            """, extra_params)
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
    type_condition = f"AND e.entity_type = :etype" if entity_type else ""

    sql = f"""
        SELECT v.entity_id, v.title, v.entity_type, v.category,
               COUNT(DISTINCT e2.target_id) + COUNT(DISTINCT e3.source_id) AS connection_count
        FROM entities v
        LEFT JOIN entity_edges e2 ON e2.source_id = v.entity_id
        LEFT JOIN entity_edges e3 ON e3.target_id = v.entity_id
        WHERE 1=1 {type_condition}
        GROUP BY v.entity_id, v.title, v.entity_type, v.category
        HAVING COUNT(DISTINCT e2.target_id) + COUNT(DISTINCT e3.source_id) >= :min_conn
        ORDER BY connection_count DESC
        FETCH FIRST :lim ROWS ONLY
    """
    params: Dict[str, Any] = {"min_conn": min_connections, "lim": limit}
    if entity_type:
        params["etype"] = entity_type

    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]


def graph_search(
    keyword: Optional[str] = None,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    conditions = [f"a.importance >= :min_imp"]
    params: Dict[str, Any] = {"min_imp": min_importance, "lim": limit}

    if keyword:
        conditions.append("UPPER(a.title) LIKE UPPER(:kw)")
        params["kw"] = f"%{keyword}%"
    if entity_type:
        conditions.append("a.entity_type = :etype")
        params["etype"] = entity_type
    if category:
        conditions.append("a.category = :cat")
        params["cat"] = category

    full_where = " AND ".join(conditions)

    sql = f"""
        SELECT gt.entity_id, gt.title, gt.entity_type, gt.category,
               gt.importance, gt.status, gt.VISIBILITY
        FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.target_id
          WHERE {full_where}
          COLUMNS(a.entity_id, a.title, a.entity_type, a.category,
                  a.importance, a.status, a.VISIBILITY)
        ) gt
        ORDER BY gt.importance DESC
        FETCH FIRST :lim ROWS ONLY
    """
    rows = execute_query(sql, params)
    return [_row_to_dict(r) for r in rows]


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


# ============================================================
# v3.10.0: Universal Property Graph Expansion
# ============================================================

# --- Generic edge operations ---

def add_edge(source_id, source_type, target_id, edge_type, strength=1.0, confidence=1.0, metadata=None):
    from .connection import execute_insert_returning_id
    import json as _json
    meta_str = _json.dumps(metadata) if metadata else None
    return execute_insert_returning_id(
        "INSERT INTO entity_edges (edge_id, source_id, source_type, target_id, edge_type, strength, confidence, metadata) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s) RETURNING edge_id",
        [source_id, source_type, target_id, edge_type, strength, confidence, meta_str],
    )

def remove_edge(edge_id):
    from .connection import execute
    return execute("DELETE FROM entity_edges WHERE edge_id = :eid", {"eid": edge_id}) > 0

def _get_entity_type(entity_id):
    row = execute_query_one("SELECT entity_type FROM entities WHERE entity_id::text = :eid", {"eid": entity_id})
    return row.get("entity_type") if row else None

def _get_trust_config():
    configs = {}
    for key in ['trust_success_delta', 'trust_failure_delta', 'trust_min_threshold', 'trust_max_value', 'trust_initial_coordinator', 'trust_initial_member']:
        row = execute_query_one("SELECT config_value FROM system_config WHERE config_key = :k", {"k": key})
        if row:
            try: configs[key] = float(row.get('config_value', 0))
            except: configs[key] = 0.0
    return configs


# --- 1. Knowledge Causal Graph ---

def add_causal_edge(source_id, target_id, edge_type="CAUSES", metadata=None):
    st = _get_entity_type(source_id) or "KNOWLEDGE"
    return add_edge(source_id, st, target_id, edge_type, strength=0.9, metadata=metadata)

def find_causes(entity_id, depth=3):
    rows = execute_query(
        "SELECT e.target_id, e.edge_type, e.strength, e.metadata, e.created_at, ent.title, ent.entity_type FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.source_id WHERE e.target_id = :eid AND e.edge_type = 'CAUSES' LIMIT :limit",
        {"eid": entity_id, "limit": depth * 20},
    )
    results = [_row_to_dict(r) for r in rows] if rows else []
    if depth > 1 and results:
        for r in results:
            r['root_causes'] = find_causes(r.get('target_id', ''), depth - 1)
    return results

def find_contradictions(entity_id):
    rows = execute_query(
        "SELECT e.source_id, e.target_id, e.metadata, e.created_at, ent.title, ent.entity_type FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.source_id WHERE (e.source_id = :eid OR e.target_id = :eid) AND e.edge_type = 'CONTRADICTS'",
        {"eid": entity_id},
    )
    return [_row_to_dict(r) for r in rows] if rows else []

def trace_provenance(entity_id, depth=5):
    chain = []
    current_id = entity_id
    for _ in range(depth):
        rows = execute_query(
            "SELECT e.source_id, e.edge_type, ent.title, ent.entity_type, ent.category FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.source_id WHERE e.target_id = :eid AND e.edge_type IN ('DERIVED_FROM', 'DERIVED_FROM_DATA', 'SUPERSEDES', 'SUPERSEDED_BY') LIMIT 1",
            {"eid": current_id},
        )
        if not rows:
            break
        r = _row_to_dict(rows[0])
        chain.append(r)
        current_id = str(r.get('source_id', ''))
    return chain

def supersede_knowledge(old_id, new_id, reason=""):
    return add_edge(old_id, "KNOWLEDGE", new_id, "SUPERSEDES", strength=1.0, metadata={"reason": reason} if reason else None)


# --- 2. Agent Collaboration Graph ---

def init_group_trust(agent_id, group_id, coordinator_id, members):
    cfg = _get_trust_config()
    count = 0
    if agent_id != coordinator_id:
        add_edge(agent_id, "AGENT", coordinator_id, "TRUSTS", strength=cfg.get('trust_initial_coordinator', 0.5), metadata={"group_id": group_id})
        count += 1
    for mid in members:
        if mid != agent_id and mid != coordinator_id:
            add_edge(agent_id, "AGENT", mid, "TRUSTS", strength=cfg.get('trust_initial_member', 0.3), metadata={"group_id": group_id})
            count += 1
    return count

def get_trusted_agents(agent_id, group_id, min_strength=None):
    cfg = _get_trust_config()
    if min_strength is None:
        min_strength = cfg.get('trust_min_threshold', 0.3)
    rows = execute_query(
        "SELECT e.target_id AS agent_id, e.strength, e.metadata, e.created_at FROM entity_edges e WHERE e.source_id = :aid AND e.edge_type = 'TRUSTS' AND e.strength >= :min_str ORDER BY e.strength DESC",
        {"aid": agent_id, "min_str": min_strength},
    )
    if not rows:
        return []
    import json as _json
    results = []
    for r in rows:
        d = _row_to_dict(r)
        meta = d.get('metadata', {})
        if isinstance(meta, str):
            try: meta = _json.loads(meta)
            except: meta = {}
        if isinstance(meta, dict) and meta.get('group_id') == group_id:
            if meta.get('status') == 'inactive':
                continue
            results.append(d)
    return results

def update_trust(agent_id, target_id, group_id, success):
    cfg = _get_trust_config()
    delta = cfg.get('trust_success_delta', 0.1) if success else -cfg.get('trust_failure_delta', 0.15)
    max_val = cfg.get('trust_max_value', 1.0)
    row = execute_query_one("SELECT edge_id, strength FROM entity_edges WHERE source_id = :aid AND target_id = :tid AND edge_type = 'TRUSTS' ", {"aid": agent_id, "tid": target_id})
    if not row:
        return False
    new_strength = max(0.0, min(max_val, (row.get('strength') or 0.5) + delta))
    from .connection import execute
    return execute("UPDATE entity_edges SET strength = :str WHERE edge_id = :eid", {"str": new_strength, "eid": row.get('edge_id')}) > 0

def recommend_collaborators(agent_id, group_id, skills=None):
    trusted = get_trusted_agents(agent_id, group_id)
    if not trusted:
        return []
    results = []
    for t in trusted:
        score = t.get('strength', 0.3)
        results.append({"agent_id": t.get('agent_id'), "score": score, "trust": t.get('strength')})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def record_delegation(from_agent, to_agent, task_id, group_id=None):
    meta = {"task_id": task_id}
    if group_id: meta["group_id"] = group_id
    return add_edge(from_agent, "AGENT", to_agent, "DELEGATED_TO", metadata=meta)

def find_complementary_agents(agent_id, group_id, skills):
    rows = execute_query("SELECT DISTINCT e.target_id AS agent_id, e.metadata FROM entity_edges e WHERE e.source_id = :aid AND e.edge_type = 'COMPLEMENTS_SKILL'", {"aid": agent_id})
    return [_row_to_dict(r) for r in rows] if rows else []


# --- 3. Task Orchestration Graph ---

def record_task_dependency(step_a_id, step_b_id, dependency_type="FEEDS_INTO"):
    return add_edge(step_a_id, "TASK_STEP", step_b_id, dependency_type)

def get_task_lineage(entity_id):
    chain = []
    current_id = entity_id
    for _ in range(10):
        rows = execute_query(
            "SELECT e.source_id, e.edge_type, ent.title, ent.entity_type FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.source_id WHERE e.target_id = :eid AND e.edge_type IN ('PRODUCED_ARTIFACT', 'CONSUMED_ARTIFACT', 'FEEDS_INTO') LIMIT 1",
            {"eid": current_id},
        )
        if not rows: break
        r = _row_to_dict(rows[0])
        chain.append(r)
        current_id = str(r.get('source_id', ''))
    return chain

def find_affected_steps(failed_step_id):
    affected = set()
    queue = [failed_step_id]
    while queue:
        current = queue.pop(0)
        rows = execute_query("SELECT target_id FROM entity_edges WHERE source_id = :sid AND edge_type = 'FEEDS_INTO'", {"sid": current})
        if rows:
            for r in rows:
                tid = str(r.get('target_id', ''))
                if tid and tid not in affected:
                    affected.add(tid)
                    queue.append(tid)
    return list(affected)

def get_artifact_chain(step_id):
    produced = execute_query("SELECT target_id, metadata FROM entity_edges WHERE source_id = :sid AND edge_type = 'PRODUCED_ARTIFACT'", {"sid": step_id})
    consumed = execute_query("SELECT target_id, metadata FROM entity_edges WHERE source_id = :sid AND edge_type = 'CONSUMED_ARTIFACT'", {"sid": step_id})
    return {"step_id": step_id, "produced": [_row_to_dict(r) for r in produced] if produced else [], "consumed": [_row_to_dict(r) for r in consumed] if consumed else []}


# --- 4. Skill Dependency Graph ---

def add_skill_dependency(skill_id, required_skill_id):
    source_type = _get_entity_type(skill_id) or "SKILL"
    return add_edge(skill_id, source_type, required_skill_id, "REQUIRES", strength=1.0)

def get_required_skills(skill_id, depth=5):
    required = set()
    queue = [skill_id]
    for _ in range(depth):
        if not queue: break
        current = queue.pop(0)
        rows = execute_query("SELECT target_id FROM entity_edges WHERE source_id = :sid AND edge_type = 'REQUIRES'", {"sid": current})
        if rows:
            for r in rows:
                tid = str(r.get('target_id', ''))
                if tid and tid not in required:
                    required.add(tid)
                    queue.append(tid)
    return list(required)

def find_skill_gaps(agent_id):
    agent_skills = execute_query("SELECT DISTINCT e.target_id AS skill_id FROM entity_edges e WHERE e.source_id = :aid AND e.edge_type = 'HAS_SKILL'", {"aid": agent_id})
    if not agent_skills: return []
    gaps = []
    for s in agent_skills:
        sid = str(s.get('skill_id', ''))
        for req_id in get_required_skills(sid):
            has_row = execute_query("SELECT 1 FROM entity_edges WHERE source_id = :aid AND target_id = :rid AND edge_type = 'HAS_SKILL'", {"aid": agent_id, "rid": req_id})
            if not has_row:
                gaps.append({"missing_skill_id": req_id, "required_by": sid})
    return gaps


# --- 5. Approval Propagation Graph ---

def add_approval_block(approval_id, step_ids):
    count = 0
    for step_id in step_ids:
        add_edge(approval_id, "APPROVAL", step_id, "BLOCKS")
        count += 1
    return count

def cascade_reject(approval_id):
    rows = execute_query("SELECT target_id FROM entity_edges WHERE source_id = :aid AND edge_type = 'BLOCKS'", {"aid": approval_id})
    if not rows: return []
    from .connection import execute
    blocked = []
    for r in rows:
        step_id = str(r.get('target_id', ''))
        if step_id:
            execute("UPDATE step_execution_plan SET status = 'SKIPPED' WHERE step_id = :sid", {"sid": step_id})
            blocked.append(step_id)
    return blocked

def find_approval_bottlenecks(group_id=None):
    rows = execute_query("SELECT e.source_id AS approval_id, COUNT(*) AS blocked_count FROM entity_edges e WHERE e.edge_type = 'BLOCKS' GROUP BY e.source_id ORDER BY blocked_count DESC LIMIT 10", {})
    return [_row_to_dict(r) for r in rows] if rows else []


# --- 6. Data Flow (DERIVED_FROM_DATA + existing audit tables) ---

def trace_data_lineage(entity_id):
    graph_chain = trace_provenance(entity_id, depth=5)
    try:
        audit_rows = execute_query("SELECT accessor_id, access_type, accessed_at FROM entity_access_audit WHERE entity_id = :eid ORDER BY accessed_at DESC LIMIT 20", {"eid": entity_id})
    except Exception:
        audit_rows = None
    return {"entity_id": entity_id, "derivation_chain": graph_chain, "access_history": [_row_to_dict(r) for r in audit_rows] if audit_rows else []}

def find_data_paths(source_agent, target_entity):
    try:
        access_rows = execute_query("SELECT entity_id, access_type, accessed_at FROM entity_access_audit WHERE accessor_id = :aid ORDER BY accessed_at DESC LIMIT 50", {"aid": source_agent})
    except Exception:
        access_rows = None
    return [_row_to_dict(r) for r in access_rows] if access_rows else []


# --- 7. Memory Evolution Graph ---

def record_promotion(memory_id, knowledge_id):
    return add_edge(memory_id, "MEMORY", knowledge_id, "PROMOTED_TO", strength=1.0)

def record_merge(source_ids, target_id):
    count = 0
    for sid in source_ids:
        add_edge(sid, "MEMORY", target_id, "MERGED_INTO", strength=1.0)
        count += 1
    return count

def trace_memory_origin(entity_id):
    chain = []
    current_id = entity_id
    for _ in range(10):
        rows = execute_query(
            "SELECT e.source_id, e.edge_type, ent.title, ent.entity_type FROM entity_edges e JOIN entities ent ON ent.entity_id::text = e.source_id WHERE e.target_id = :eid AND e.edge_type IN ('PROMOTED_TO', 'MERGED_INTO', 'SUPERSEDED_BY') LIMIT 1",
            {"eid": current_id},
        )
        if not rows: break
        r = _row_to_dict(rows[0])
        chain.append(r)
        current_id = str(r.get('source_id', ''))
    return chain


# --- 8. Loop Iteration Graph ---

def record_iteration_link(iter_from, iter_to, link_type="BUILDS_ON", metadata=None):
    return add_edge(str(iter_from), "LOOP_ITERATION", str(iter_to), link_type, metadata=metadata)

def get_iteration_graph(run_id):
    rows = execute_query(
        "SELECT e.source_id AS from_iter, e.target_id AS to_iter, e.edge_type, e.metadata FROM entity_edges e WHERE e.edge_type IN ('BUILDS_ON', 'INFORMS', 'CORRECTS') AND (e.source_id IN (SELECT iteration_id FROM loop_iterations WHERE run_id = :rid) OR e.target_id IN (SELECT iteration_id FROM loop_iterations WHERE run_id = :rid))",
        {"rid": run_id},
    )
    return [_row_to_dict(r) for r in rows] if rows else []

def find_key_iterations(run_id):
    rows = execute_query(
        "SELECT e.source_id AS iteration_id, COUNT(*) AS influence_count FROM entity_edges e WHERE e.edge_type IN ('INFORMS', 'CORRECTS') AND e.source_id IN (SELECT iteration_id FROM loop_iterations WHERE run_id = :rid) GROUP BY e.source_id ORDER BY influence_count DESC LIMIT 5",
        {"rid": run_id},
    )
    return [_row_to_dict(r) for r in rows] if rows else []
