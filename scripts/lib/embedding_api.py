"""AI Agent Infra v3.7.3 - PG Community Edition - Embedding API

Generate, store, and search vector embeddings for entities.
Uses external Embedding API (OpenAI-compatible) + pgvector for storage.
5-signal unified hybrid search: vector + fulltext (tsvector) + relational metadata + graph proximity.
Single-SQL CTE fusion search available via search_unified_sql().
"""

import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

from .connection import execute_query, execute_query_one, execute
from .config import get_config

logger = logging.getLogger(__name__)

MODEL_DIMENSIONS = {
    "text-embedding-bge-m3": 1024,
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
    "text-embedding-bge-large-en-v1.5": 1024,
    "text-embedding-bge-small-en-v1.5": 384,
    "all-MiniLM-L6-v2": 384,
    "nomic-embed-text": 768,
    "mxbai-embed-large-v1": 1024,
}


def _get_api_config() -> Dict[str, Any]:
    cfg = get_config()
    return {
        "api_url": cfg.embedding.api_url,
        "model": cfg.embedding.model,
        "dimension": cfg.embedding.dimension,
    }


def _detect_dimension(model: str, api_url: str) -> int:
    if model in MODEL_DIMENSIONS:
        return MODEL_DIMENSIONS[model]
    if not api_url or not model:
        raise ValueError(
            "Embedding model not configured. "
            "Please set embedding.api_url and embedding.model in config.json. "
            "Supported models: " + ", ".join(sorted(MODEL_DIMENSIONS.keys()))
        )
    try:
        result = generate_embedding("dimension probe", api_url=api_url, model=model)
        return len(result)
    except Exception as e:
        logger.warning("Cannot auto-detect dimension for %s: %s", model, e)
        return 1024


def generate_embedding(
    text: str,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 30,
) -> List[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    cfg = _get_api_config()
    api_url = api_url or cfg["api_url"]
    model = model or cfg["model"]

    payload = json.dumps({"model": model, "input": text}).encode("utf-8")

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0]["embedding"]
                logger.debug("Generated embedding: %d dims for '%s...'", len(embedding), text[:50])
                return embedding
            else:
                raise Exception("Unexpected API response format: %s" % list(result.keys()))
    except urllib.error.URLError as e:
        raise Exception("Embedding API connection error (%s): %s" % (api_url, e))
    except Exception as e:
        raise Exception("Error generating embedding: %s" % e)


def store_embedding(
    entity_id: str,
    entity_type: str,
    text: str,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    return store_embedding_vector(entity_id, entity_type, embedding, model=model)


def store_embedding_vector(
    entity_id: str,
    entity_type: str,
    embedding: List[float],
    model: Optional[str] = None,
) -> bool:
    cfg = _get_api_config()
    model = model or cfg["model"]
    dimension = len(embedding)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    try:
        row = execute_query_one("""
            SELECT COUNT(*) AS c FROM entity_embeddings
            WHERE entity_id = %s AND entity_type = %s
        """, [entity_id, entity_type])
        count = int(list(row.values())[0]) if row else 0

        if count > 0:
            execute("""
                UPDATE entity_embeddings
                SET embedding = %s::vector,
                    embedding_model = %s,
                    embedding_dim = %s
                WHERE entity_id = %s AND entity_type = %s
            """, [vec_str, model, dimension, entity_id, entity_type])
        else:
            execute("""
                INSERT INTO entity_embeddings (entity_id, entity_type, embedding, embedding_model, embedding_dim, created_at)
                VALUES (%s, %s, %s::vector, %s, %s, CURRENT_TIMESTAMP)
            """, [entity_id, entity_type, vec_str, model, dimension])
        logger.info("Stored embedding for %s:%s (%dd, %s)", entity_type, entity_id, dimension, model)
        return True
    except Exception as e:
        logger.error("Failed to store embedding for %s: %s", entity_id, e)
        return False


def get_embedding(entity_id: str, entity_type: str = "MEMORY") -> Optional[Dict]:
    try:
        row = execute_query_one("""
            SELECT entity_id, entity_type, embedding_model, embedding_dim, created_at
            FROM entity_embeddings
            WHERE entity_id = %s AND entity_type = %s
        """, [entity_id, entity_type])
        if row and row.get("entity_id"):
            return {
                "entity_id": row["entity_id"],
                "entity_type": row["entity_type"],
                "embedding_model": row["embedding_model"],
                "embedding_dim": int(row["embedding_dim"]) if row["embedding_dim"] else None,
                "created_at": str(row["created_at"]) if row.get("created_at") else None,
            }
        return None
    except Exception as e:
        logger.error("Failed to get embedding for %s: %s", entity_id, e)
        return None


def delete_embedding(entity_id: str, entity_type: str = "MEMORY") -> bool:
    try:
        execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s",
                       [entity_id, entity_type])
        return True
    except Exception as e:
        logger.error("Failed to delete embedding: %s", e)
        return False


def search_similar(
    text: str,
    top_k: int = 10,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    conditions = []
    params: list = [vec_str, top_k]
    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        conditions.append("AND e.workspace_id = %s")
        params.append(workspace_id)

    where = " ".join(conditions)
    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.category,
               em.embedding <=> %s::vector AS distance
        FROM entity_embeddings em
        JOIN entities e ON e.entity_id = em.entity_id AND e.entity_type = em.entity_type
        WHERE 1=1 {where}
        ORDER BY distance ASC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, params)
        results = []
        for row in rows:
            dist = float(row["distance"]) if row.get("distance") is not None else None
            results.append({
                "entity_id": row["entity_id"],
                "entity_type": row["entity_type"],
                "title": row.get("title", ""),
                "category": row.get("category", ""),
                "distance": dist,
                "similarity": round(1.0 - dist, 4) if dist is not None else None,
            })
        return results
    except Exception as e:
        logger.error("Vector search failed: %s", e)
        return []


def search_by_entity_id(
    entity_id: str,
    entity_type: str = "MEMORY",
    top_k: int = 10,
    workspace_id: Optional[str] = None,
) -> List[Dict]:
    try:
        row = execute_query_one("""
            SELECT COUNT(*) AS c FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s
        """, [entity_id, entity_type])
        count = int(list(row.values())[0]) if row else 0
        if count == 0:
            return []

        ws_filter = "AND e.workspace_id = %s" if workspace_id else ""
        sql = f"""
            SELECT e.entity_id, e.entity_type, e.title, e.category,
                   em.embedding <=> (SELECT embedding FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s)::vector AS distance
            FROM entity_embeddings em
            JOIN entities e ON e.entity_id = em.entity_id AND e.entity_type = em.entity_type
            WHERE em.entity_id != %s {ws_filter}
            ORDER BY distance ASC
            LIMIT %s
        """
        params = [entity_id, entity_type, entity_id, top_k]
        if workspace_id:
            params.insert(3, workspace_id)

        rows = execute_query(sql, params)
        results = []
        for r in rows:
            dist = float(r["distance"]) if r.get("distance") is not None else None
            results.append({
                "entity_id": r["entity_id"],
                "entity_type": r["entity_type"],
                "title": r.get("title", ""),
                "category": r.get("category", ""),
                "distance": dist,
                "similarity": round(1.0 - dist, 4) if dist is not None else None,
            })
        return results
    except Exception as e:
        logger.error("Entity-based vector search failed: %s", e)
        return []


def generate_embeddings_batch(
    entity_type: str = "MEMORY",
    limit: int = 100,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict:
    try:
        rows = execute_query("""
            SELECT e.entity_id, e.entity_type, e.title, e.content
            FROM entities e
            WHERE e.entity_type = %s
              AND NOT EXISTS (
                SELECT 1 FROM entity_embeddings em
                WHERE em.entity_id = e.entity_id AND em.entity_type = e.entity_type
              )
              AND e.title IS NOT NULL
            ORDER BY e.created_at DESC
            LIMIT %s
        """, [entity_type, limit])

        generated = 0
        failed = 0

        for row in rows:
            eid = row["entity_id"]
            etype = row["entity_type"]
            text = (row.get("title", "") or "") + " " + (row.get("content", "") or "")
            text = text.strip()[:8000]

            if not text:
                continue

            try:
                ok = store_embedding(eid, etype, text, api_url=api_url, model=model)
                if ok:
                    generated += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error("Batch embedding failed for %s: %s", eid, e)
                failed += 1

        return {"generated": generated, "failed": failed, "total_candidates": len(rows)}
    except Exception as e:
        logger.error("Batch embedding generation failed: %s", e)
        return {"generated": 0, "failed": 0, "error": str(e)}


def search_hybrid(
    text: str,
    keyword: Optional[str] = None,
    top_k: int = 10,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    vector_weight: float = 0.7,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    conditions = []
    params: list = [vec_str, top_k]
    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        conditions.append("AND e.workspace_id = %s")
        params.append(workspace_id)
    if keyword:
        conditions.append("AND (e.title ILIKE %s OR e.category ILIKE %s)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    where = " ".join(conditions)
    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.category,
               em.embedding <=> %s::vector AS distance
        FROM entity_embeddings em
        JOIN entities e ON e.entity_id = em.entity_id AND e.entity_type = em.entity_type
        WHERE 1=1 {where}
        ORDER BY distance ASC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, params)
        results = []
        for r in rows:
            dist = float(r["distance"]) if r.get("distance") is not None else None
            vec_score = max(0, 1.0 - dist) * vector_weight if dist is not None else 0
            kw_score = (1.0 - vector_weight) if keyword and (
                keyword.lower() in (r.get("title", "") or "").lower() or
                keyword.lower() in (r.get("category", "") or "").lower()
            ) else 0
            results.append({
                "entity_id": r["entity_id"],
                "entity_type": r["entity_type"],
                "title": r.get("title", ""),
                "category": r.get("category", ""),
                "distance": dist,
                "vector_score": round(vec_score, 4),
                "keyword_score": round(kw_score, 4),
                "hybrid_score": round(vec_score + kw_score, 4),
            })
        results.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return results
    except Exception as e:
        logger.error("Hybrid search failed: %s", e)
        return []


def search_fulltext(
    query: str,
    top_k: int = 20,
    entity_type: Optional[str] = None,
    category: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> List[Dict]:
    if not query or not query.strip():
        return []

    params: list = [query, query, top_k]
    conditions = []

    if entity_type:
        conditions.append("AND entity_type = %s")
        params.append(entity_type)
    if category:
        conditions.append("AND category = %s")
        params.append(category)
    if workspace_id:
        conditions.append("AND workspace_id = %s")
        params.append(workspace_id)

    where = " ".join(conditions)
    sql = f"""
        SELECT entity_id, entity_type, title, content, category,
               ts_rank_cd(to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'')),
                          plainto_tsquery('english', %s)) AS ft_score
        FROM entities
        WHERE to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'')) @@ plainto_tsquery('english', %s)
        {where}
        ORDER BY ft_score DESC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, params)
        results = []
        for r in rows:
            score = float(r["ft_score"]) if r.get("ft_score") else 0
            results.append({
                "entity_id": r["entity_id"],
                "entity_type": r["entity_type"],
                "title": r.get("title", ""),
                "content": (r.get("content", "") or "")[:200],
                "category": r.get("category", ""),
                "ft_score": round(min(score, 1.0), 4),
            })
        return results
    except Exception as e:
        logger.error("Full-text search failed: %s", e)
        return []


def search_unified(
    text: str,
    top_k: int = 20,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    domain: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    graph_seed_entity_id: Optional[str] = None,
    graph_seed_entity_type: Optional[str] = None,
    graph_depth: int = 2,
    vector_weight: float = 0.4,
    fulltext_weight: float = 0.25,
    relational_weight: float = 0.2,
    graph_weight: float = 0.15,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    params: list = [vec_str, text, text, top_k * 3]
    conditions = []

    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        conditions.append("AND e.workspace_id = %s")
        params.append(workspace_id)

    where = " ".join(conditions)

    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.content, e.category, e.importance,
               e.workspace_id,
               em.embedding <=> %s::vector AS vec_distance,
               ts_rank_cd(to_tsvector('english', coalesce(e.title,'') || ' ' || coalesce(e.content,'')),
                          plainto_tsquery('english', %s)) AS ft_raw,
               km.domain AS km_domain, km.topic AS km_topic, km.difficulty AS km_difficulty
        FROM entity_embeddings em
        JOIN entities e ON e.entity_id = em.entity_id AND e.entity_type = em.entity_type
        LEFT JOIN knowledge_meta km ON km.entity_id = e.entity_id AND km.entity_type = e.entity_type
        WHERE 1=1 {where}
        ORDER BY vec_distance ASC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, params)
    except Exception as e:
        logger.error("Unified search vector+fulltext phase failed: %s", e)
        return []

    eid_set = {r["entity_id"] for r in rows}
    eid_list = list(eid_set)

    tag_map: Dict[str, List[str]] = {}
    if eid_list and tags:
        tag_pairs = _batch_get_tags(eid_list)
        for eid, tag_name in tag_pairs:
            tag_map.setdefault(eid, []).append(tag_name)

    graph_neighbors: Dict[str, float] = {}
    if graph_seed_entity_id and eid_list:
        graph_neighbors = _batch_graph_proximity(graph_seed_entity_id, graph_seed_entity_type or "MEMORY", eid_list, graph_depth)

    edge_counts: Dict[str, int] = {}
    if eid_list:
        edge_counts = _batch_edge_counts(eid_list)

    results = []
    text_lower = text.lower()

    for r in rows:
        eid = r["entity_id"]

        vec_dist = float(r["vec_distance"]) if r.get("vec_distance") is not None else 1.0
        vec_score = max(0.0, 1.0 - vec_dist)

        ft_raw = float(r["ft_raw"]) if r.get("ft_raw") else 0
        ft_score = min(ft_raw, 1.0)

        rel_score = _relational_score(
            r.get("km_domain"), r.get("km_topic"), r.get("km_difficulty"),
            r.get("category"), r.get("importance"),
            domain, category, text_lower,
        )

        tag_score = _tag_score(tag_map.get(eid, []), tags or [], text_lower)

        graph_score = graph_neighbors.get(eid, 0.0)

        connectivity_boost = min(edge_counts.get(eid, 0) / 10.0, 0.1)

        final_score = (
            vector_weight * vec_score
            + fulltext_weight * ft_score
            + relational_weight * (rel_score + tag_score) / 2.0
            + graph_weight * (graph_score + connectivity_boost) / 2.0
        )
        final_score = min(final_score, 1.0)

        results.append({
            "entity_id": eid,
            "entity_type": r.get("entity_type", ""),
            "title": r.get("title", ""),
            "category": r.get("category", ""),
            "importance": int(r["importance"]) if r.get("importance") else None,
            "workspace_id": r.get("workspace_id"),
            "km_domain": r.get("km_domain"),
            "km_topic": r.get("km_topic"),
            "km_difficulty": r.get("km_difficulty"),
            "tags": tag_map.get(eid, []),
            "edge_count": edge_counts.get(eid, 0),
            "graph_proximity": round(graph_score, 4),
            "scores": {
                "vector": round(vec_score, 4),
                "fulltext": round(ft_score, 4),
                "relational": round(rel_score, 4),
                "tag": round(tag_score, 4),
                "graph": round(graph_score, 4),
            },
            "final_score": round(final_score, 4),
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:top_k]


def search_unified_sql(
    text: str,
    top_k: int = 20,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    domain: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    graph_seed_entity_id: Optional[str] = None,
    graph_seed_entity_type: Optional[str] = None,
    graph_depth: int = 2,
    vector_weight: float = 0.4,
    fulltext_weight: float = 0.25,
    relational_weight: float = 0.2,
    graph_weight: float = 0.15,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = "[" + ",".join(str(x) for x in embedding) + "]"

    params: list = [vec_str, text, text, top_k * 3, top_k,
                    vector_weight, fulltext_weight, relational_weight, graph_weight]

    filter_conds = []
    if entity_type:
        filter_conds.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        filter_conds.append("AND e.workspace_id = %s")
        params.append(workspace_id)

    filter_where = " ".join(filter_conds)

    tag_cte = ""
    tag_join = ""
    tag_select = "0 AS tag_score"

    if tags:
        tag_placeholders = ", ".join(["%s"] * len(tags))
        params.extend(tags)
        tag_cte = f""",
tag_scores AS (
    SELECT et.entity_id,
           COUNT(CASE WHEN t.tag_name IN ({tag_placeholders}) THEN 1 END) AS matched_tags,
           COUNT(*) AS total_tags
    FROM entity_tags et
    JOIN tags t ON t.tag_id = et.tag_id
    WHERE et.entity_id IN (SELECT entity_id FROM candidates)
    GROUP BY et.entity_id
)"""
        tag_join = "LEFT JOIN tag_scores ts ON ts.entity_id = c.entity_id"
        tag_select = "CASE WHEN ts.total_tags > 0 THEN COALESCE(ts.matched_tags, 0)::float / ts.total_tags ELSE 0 END AS tag_score"

    graph_cte = ""
    graph_join = ""
    graph_select = "0 AS graph_proximity"

    if graph_seed_entity_id:
        params.append(graph_seed_entity_id)
        depth2_join = ""
        if graph_depth >= 2:
            depth2_join = """
            UNION ALL
            SELECT e2.target_id AS entity_id, 0.5 AS proximity
            FROM entity_edges e1
            JOIN entity_edges e2 ON e2.source_id = e1.target_id
            WHERE e1.source_id = %s
              AND e2.target_id IN (SELECT entity_id FROM candidates)
              AND e2.target_id != %s"""
            params.extend([graph_seed_entity_id, graph_seed_entity_id])

        graph_cte = f""",
graph_prox AS (
    SELECT target_id AS entity_id, 1.0 AS proximity
    FROM entity_edges
    WHERE source_id = %s
      AND target_id IN (SELECT entity_id FROM candidates){depth2_join}
)"""
        params.append(graph_seed_entity_id)
        graph_join = "LEFT JOIN (SELECT entity_id, MAX(proximity) AS proximity FROM graph_prox GROUP BY entity_id) gp ON gp.entity_id = c.entity_id"
        graph_select = "COALESCE(gp.proximity, 0) AS graph_proximity"

    tag_join_left = tag_join if tags else ""
    graph_join_left = graph_join if graph_seed_entity_id else ""

    rel_score_expr = "0"
    if domain:
        params.append(domain.lower())
        rel_score_expr = "CASE WHEN LOWER(c.km_domain) = %s THEN 0.5 ELSE 0 END"
    if category:
        params.append(category.lower())
        existing = rel_score_expr
        rel_score_expr = f"{existing} + CASE WHEN LOWER(c.category) = %s THEN 0.3 ELSE 0 END"

    importance_part = "COALESCE(c.importance, 0)::float / 100.0"
    rel_score_expr = f"LEAST({rel_score_expr} + {importance_part}, 1.0)"

    tag_final_expr = tag_select if tags else "0 AS tag_score"
    graph_final_expr = graph_select if graph_seed_entity_id else "0 AS graph_proximity"

    final_score_expr = (
        f"%s * (1 - c.vec_distance)"
        f" + %s * CASE WHEN c.ft_raw > 0 THEN LEAST(c.ft_raw, 1.0) ELSE 0 END"
        f" + %s * ({rel_score_expr} + {tag_final_expr.replace(' AS tag_score', '')}) / 2.0"
        f" + %s * ({graph_final_expr.replace(' AS graph_proximity', '')} + LEAST(COALESCE(ec.edge_count, 0)::float / 10.0, 0.1)) / 2.0"
    )

    sql = f"""
WITH candidates AS (
    SELECT e.entity_id, e.entity_type, e.title, e.content, e.category, e.importance,
           e.workspace_id,
           em.embedding <=> %s::vector AS vec_distance,
           ts_rank_cd(to_tsvector('english', coalesce(e.title,'') || ' ' || coalesce(e.content,'')),
                      plainto_tsquery('english', %s)) AS ft_raw,
           km.domain AS km_domain, km.topic AS km_topic, km.difficulty AS km_difficulty
    FROM entity_embeddings em
    JOIN entities e ON e.entity_id = em.entity_id AND e.entity_type = em.entity_type
    LEFT JOIN knowledge_meta km ON km.entity_id = e.entity_id AND km.entity_type = e.entity_type
    WHERE 1=1 {filter_where}
    ORDER BY vec_distance ASC
    LIMIT %s
),
edge_counts AS (
    SELECT source_id AS entity_id, COUNT(*) AS edge_count
    FROM entity_edges
    WHERE source_id IN (SELECT entity_id FROM candidates)
    GROUP BY source_id
){tag_cte}{graph_cte}
SELECT c.entity_id, c.entity_type, c.title, c.category, c.importance,
       c.workspace_id, c.km_domain, c.km_topic, c.km_difficulty,
       (1 - c.vec_distance) AS vec_score,
       CASE WHEN c.ft_raw > 0 THEN LEAST(c.ft_raw, 1.0) ELSE 0 END AS ft_score,
       LEAST({rel_score_expr}, 1.0) AS rel_score,
       {tag_final_expr},
       COALESCE(ec.edge_count, 0) AS edge_count,
       {graph_final_expr},
       LEAST({final_score_expr}, 1.0) AS final_score
FROM candidates c
LEFT JOIN edge_counts ec ON ec.entity_id = c.entity_id
{tag_join_left}
{graph_join_left}
ORDER BY final_score DESC
LIMIT %s
"""

    try:
        rows = execute_query(sql, params)
    except Exception as e:
        logger.error("search_unified_sql failed: %s", e)
        return []

    tag_map: Dict[str, List[str]] = {}
    if rows and tags:
        eid_list = [r["entity_id"] for r in rows]
        tag_pairs = _batch_get_tags(eid_list)
        for eid, tag_name in tag_pairs:
            tag_map.setdefault(eid, []).append(tag_name)

    results = []
    for r in rows:
        eid = r["entity_id"]
        results.append({
            "entity_id": eid,
            "entity_type": r.get("entity_type", ""),
            "title": r.get("title", ""),
            "category": r.get("category", ""),
            "importance": int(r["importance"]) if r.get("importance") else None,
            "workspace_id": r.get("workspace_id"),
            "km_domain": r.get("km_domain"),
            "km_topic": r.get("km_topic"),
            "km_difficulty": r.get("km_difficulty"),
            "tags": tag_map.get(eid, []),
            "edge_count": int(r.get("edge_count", 0) or 0),
            "graph_proximity": round(float(r.get("graph_proximity", 0) or 0), 4),
            "scores": {
                "vector": round(float(r.get("vec_score", 0) or 0), 4),
                "fulltext": round(float(r.get("ft_score", 0) or 0), 4),
                "relational": round(float(r.get("rel_score", 0) or 0), 4),
                "tag": round(float(r.get("tag_score", 0) or 0), 4),
                "graph": round(float(r.get("graph_proximity", 0) or 0), 4),
            },
            "final_score": round(float(r.get("final_score", 0) or 0), 4),
            "engine": "single_sql",
        })

    return results


def search_multi_type(
    text: str,
    entity_types: Optional[List[str]] = None,
    top_k: int = 10,
    workspace_id: Optional[str] = None,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, List[Dict]]:
    if entity_types is None:
        entity_types = ["MEMORY", "KNOWLEDGE", "SPEC"]

    results = {}
    for etype in entity_types:
        results[etype] = search_similar(
            text, top_k=top_k, entity_type=etype, workspace_id=workspace_id,
            api_url=api_url, model=model,
        )
    return results


def search_auto(
    text: str,
    top_k: int = 10,
    entity_type: Optional[str] = None,
    workspace_id: Optional[str] = None,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    try:
        results = search_similar(text, top_k=top_k, entity_type=entity_type,
                                 workspace_id=workspace_id, api_url=api_url, model=model)
        if results:
            return results
    except Exception:
        pass
    return search_fulltext(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id)


def get_embedding_stats() -> Dict:
    try:
        row = execute_query_one("""
            SELECT COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE embedding IS NOT NULL) AS with_vector,
                   COUNT(DISTINCT embedding_model) AS model_count
            FROM entity_embeddings
        """)
        if row:
            return {
                "total": int(row.get("total", 0)),
                "with_vector": int(row.get("with_vector", 0)),
                "model_count": int(row.get("model_count", 0)),
            }
        return {"total": 0, "with_vector": 0, "model_count": 0}
    except Exception as e:
        logger.error("Failed to get embedding stats: %s", e)
        return {"error": str(e)}


def get_model_dimension(model: Optional[str] = None) -> int:
    cfg = _get_api_config()
    model = model or cfg["model"]
    if model in MODEL_DIMENSIONS:
        return MODEL_DIMENSIONS[model]
    return _detect_dimension(model, cfg["api_url"])


def _relational_score(
    km_domain: Optional[str], km_topic: Optional[str], km_difficulty: Optional[str],
    category: Optional[str], importance: Optional[Any],
    filter_domain: Optional[str], filter_category: Optional[str],
    query_lower: str,
) -> float:
    score = 0.0
    if filter_domain:
        if km_domain and km_domain.lower() == filter_domain.lower():
            score += 0.4
    if filter_category:
        if category and category.lower() == filter_category.lower():
            score += 0.3
    if km_domain and km_domain.lower() in query_lower:
        score += 0.2
    if km_topic and km_topic.lower() in query_lower:
        score += 0.2
    if importance:
        try:
            score += min(int(importance) / 10.0, 1.0) * 0.1
        except (ValueError, TypeError):
            pass
    return min(score, 1.0)


def _tag_score(entity_tags: List[str], filter_tags: List[str], query_lower: str) -> float:
    if not entity_tags and not filter_tags:
        return 0.0
    score = 0.0
    if filter_tags:
        filter_lower = {t.lower() for t in filter_tags}
        entity_lower = {t.lower() for t in entity_tags}
        overlap = len(filter_lower & entity_lower)
        if overlap > 0:
            score += min(overlap / len(filter_lower), 1.0) * 0.5
    for tag in entity_tags:
        if tag.lower() in query_lower:
            score += 0.3
            break
    return min(score, 1.0)


def _batch_get_tags(entity_ids: List[str]) -> List[tuple]:
    if not entity_ids:
        return []
    try:
        placeholders = ", ".join(["%s"] * len(entity_ids))
        sql = f"""
            SELECT et.entity_id, t.tag_name
            FROM entity_tags et
            JOIN tags t ON t.tag_id = et.tag_id
            WHERE et.entity_id IN ({placeholders})
        """
        rows = execute_query(sql, entity_ids)
        return [(r["entity_id"], r["tag_name"]) for r in rows]
    except Exception as e:
        logger.debug("Batch tag query failed: %s", e)
        return []


def _batch_graph_proximity(
    seed_id: str, seed_type: str, candidate_ids: List[str], max_depth: int = 2
) -> Dict[str, float]:
    if not candidate_ids:
        return {}
    try:
        proximity: Dict[str, float] = {}
        candidate_set = set(candidate_ids)
        visited = set()
        current_frontier = {seed_id}

        for depth in range(1, max_depth + 1):
            next_frontier = set()
            if not current_frontier:
                break

            placeholders = ", ".join(["%s"] * len(current_frontier))
            params = list(current_frontier)

            sql = f"""
                SELECT source_id, target_id FROM entity_edges
                WHERE source_id IN ({placeholders})
            """
            try:
                rows = execute_query(sql, params)
            except Exception:
                break

            for r in rows:
                src = r.get("source_id")
                tgt = r.get("target_id")
                if src and src not in visited:
                    next_frontier.add(src)
                if tgt and tgt in candidate_set and tgt not in visited:
                    old = proximity.get(tgt, 0)
                    score = 1.0 / depth
                    proximity[tgt] = max(old, score)
                if tgt and tgt not in visited:
                    next_frontier.add(tgt)

            visited.update(current_frontier)
            current_frontier = next_frontier - visited

        return proximity
    except Exception as e:
        logger.debug("Graph proximity computation failed: %s", e)
        return {}


def _batch_edge_counts(entity_ids: List[str]) -> Dict[str, int]:
    if not entity_ids:
        return {}
    try:
        placeholders = ", ".join(["%s"] * len(entity_ids))
        sql = f"""
            SELECT source_id AS entity_id, COUNT(*) AS cnt
            FROM entity_edges WHERE source_id IN ({placeholders})
            GROUP BY source_id
        """
        rows = execute_query(sql, entity_ids)
        return {r["entity_id"]: int(list(r.values())[1]) for r in rows}
    except Exception as e:
        logger.debug("Batch edge count query failed: %s", e)
        return {}
