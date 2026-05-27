"""PG Memory System v2.3.1 - Embedding API

Generate, store, and search vector embeddings for entities.
Uses external Embedding API (OpenAI-compatible) + pgvector for storage and similarity search.
Auto-detects vector dimension from model response.
Supports vector similarity search, hybrid search (vector + keyword), and multi-type search.
"""

import json
import logging
import urllib.request
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query, execute_query_one, execute_insert_returning_id
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
    try:
        result = generate_embedding("dimension probe", api_url=api_url, model=model)
        return len(result)
    except Exception as e:
        logger.warning(f"Cannot auto-detect dimension for {model}: {e}")
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
                logger.debug(f"Generated embedding: {len(embedding)} dims for '{text[:50]}...'")
                return embedding
            else:
                raise Exception(f"Unexpected API response format: {list(result.keys())}")
    except urllib.error.URLError as e:
        raise Exception(f"Embedding API connection error ({api_url}): {e}")
    except Exception as e:
        raise Exception(f"Error generating embedding: {e}")


def store_embedding(
    entity_id: int,
    entity_type: str,
    text: str,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    return store_embedding_vector(entity_id, entity_type, embedding, model=model)


def store_embedding_vector(
    entity_id: int,
    entity_type: str,
    embedding: List[float],
    model: Optional[str] = None,
) -> bool:
    cfg = _get_api_config()
    model = model or cfg["model"]
    vec_str = json.dumps(embedding)

    try:
        row = execute_query_one(
            "SELECT COUNT(*) AS cnt FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s",
            (entity_id, entity_type),
        )
        count = row["cnt"] if row else 0

        if count > 0:
            execute(
                """UPDATE entity_embeddings
                   SET embedding = %s::vector, embed_model = %s, embedded_at = NOW()
                   WHERE entity_id = %s AND entity_type = %s""",
                (vec_str, model, entity_id, entity_type),
            )
        else:
            execute_insert_returning_id(
                """INSERT INTO entity_embeddings (entity_id, entity_type, embedding, embed_model, embedded_at)
                   VALUES (%s, %s, %s::vector, %s, NOW())
                   RETURNING entity_id""",
                (entity_id, entity_type, vec_str, model),
            )
        logger.info(f"Stored embedding for {entity_type}:{entity_id} ({len(embedding)}d, {model})")
        return True
    except Exception as e:
        logger.error(f"Failed to store embedding for {entity_id}: {e}")
        return False


def get_embedding(entity_id: int, entity_type: str = "MEMORY") -> Optional[Dict]:
    try:
        row = execute_query_one(
            """SELECT entity_id, entity_type, embed_model, embedded_at
               FROM entity_embeddings
               WHERE entity_id = %s AND entity_type = %s""",
            (entity_id, entity_type),
        )
        if row and row.get("entity_id"):
            return {
                "entity_id": row["entity_id"],
                "entity_type": row["entity_type"],
                "embedding_model": row["embed_model"],
                "embedded_at": str(row["embedded_at"]) if row.get("embedded_at") else None,
            }
        return None
    except Exception as e:
        logger.error(f"Failed to get embedding for {entity_id}: {e}")
        return None


def delete_embedding(entity_id: int, entity_type: str = "MEMORY") -> bool:
    try:
        execute(
            "DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s",
            (entity_id, entity_type),
        )
        return True
    except Exception as e:
        logger.error(f"Failed to delete embedding: {e}")
        return False


def search_similar(
    text: str,
    top_k: int = 10,
    entity_type: Optional[str] = None,
    workspace_id: Optional[int] = None,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = json.dumps(embedding)

    conditions = []
    params = [vec_str]
    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        conditions.append("AND e.workspace_id = %s")
        params.append(workspace_id)

    where = " ".join(conditions)
    params.append(top_k)

    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.category,
               (ee.embedding <=> %s::vector) AS distance
        FROM entity_embeddings ee
        JOIN entities e ON e.entity_id = ee.entity_id AND e.entity_type = ee.entity_type
        WHERE e.status = 'ACTIVE' {where}
        ORDER BY distance ASC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, tuple(params))
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
        logger.error(f"Vector search failed: {e}")
        return []


def search_by_entity_id(
    entity_id: int,
    entity_type: str = "MEMORY",
    top_k: int = 10,
    workspace_id: Optional[int] = None,
) -> List[Dict]:
    try:
        row = execute_query_one(
            "SELECT COUNT(*) AS cnt FROM entity_embeddings WHERE entity_id = %s AND entity_type = %s",
            (entity_id, entity_type),
        )
        count = row["cnt"] if row else 0
        if count == 0:
            return []

        ws_filter = "AND e.workspace_id = %s" if workspace_id else ""
        sql = f"""
            SELECT e.entity_id, e.entity_type, e.title, e.category,
                   (ee.embedding <=> (
                       SELECT embedding FROM entity_embeddings
                       WHERE entity_id = %s AND entity_type = %s
                   )) AS distance
            FROM entity_embeddings ee
            JOIN entities e ON e.entity_id = ee.entity_id AND e.entity_type = ee.entity_type
            WHERE ee.entity_id != %s {ws_filter}
            ORDER BY distance ASC
            LIMIT %s
        """

        params = [entity_id, entity_type, entity_id]
        if workspace_id:
            params.append(workspace_id)
        params.append(top_k)

        rows = execute_query(sql, tuple(params))
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
        logger.error(f"Entity-based vector search failed: {e}")
        return []


def search_hybrid(
    text: str,
    keyword: Optional[str] = None,
    top_k: int = 10,
    entity_type: Optional[str] = None,
    workspace_id: Optional[int] = None,
    vector_weight: float = 0.7,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict]:
    embedding = generate_embedding(text, api_url=api_url, model=model)
    vec_str = json.dumps(embedding)

    conditions = []
    params = [vec_str]
    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if workspace_id:
        conditions.append("AND e.workspace_id = %s")
        params.append(workspace_id)
    if keyword:
        conditions.append("AND (e.title ILIKE %s OR e.category ILIKE %s)")
        kw_pattern = f"%{keyword}%"
        params.extend([kw_pattern, kw_pattern])

    where = " ".join(conditions)
    params.append(top_k)

    sql = f"""
        SELECT e.entity_id, e.entity_type, e.title, e.category,
               (ee.embedding <=> %s::vector) AS distance
        FROM entity_embeddings ee
        JOIN entities e ON e.entity_id = ee.entity_id AND e.entity_type = ee.entity_type
        WHERE e.status = 'ACTIVE' {where}
        ORDER BY distance ASC
        LIMIT %s
    """

    try:
        rows = execute_query(sql, tuple(params))
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
        logger.error(f"Hybrid search failed: {e}")
        return []


def search_multi_type(
    text: str,
    entity_types: Optional[List[str]] = None,
    top_k: int = 10,
    workspace_id: Optional[int] = None,
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


def generate_embeddings_batch(
    entity_type: str = "MEMORY",
    limit: int = 100,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict:
    sql = """
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
    """

    try:
        rows = execute_query(sql, (entity_type, limit))
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
                logger.error(f"Batch embedding failed for {eid}: {e}")
                failed += 1

        return {"generated": generated, "failed": failed, "total_candidates": len(rows)}
    except Exception as e:
        logger.error(f"Batch embedding generation failed: {e}")
        return {"generated": 0, "failed": 0, "error": str(e)}


def get_embedding_stats() -> Dict:
    try:
        row = execute_query_one("""
            SELECT COUNT(*) AS total,
                   COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) AS with_vector,
                   COUNT(DISTINCT embed_model) AS model_count
            FROM entity_embeddings
        """)
        if row:
            return {
                "total": row["total"],
                "with_vector": row["with_vector"],
                "model_count": row["model_count"],
            }
        return {"total": 0, "with_vector": 0, "model_count": 0}
    except Exception as e:
        logger.error(f"Failed to get embedding stats: {e}")
        return {"error": str(e)}


def get_model_dimension(model: Optional[str] = None) -> int:
    cfg = _get_api_config()
    model = model or cfg["model"]

    if model in MODEL_DIMENSIONS:
        return MODEL_DIMENSIONS[model]

    return _detect_dimension(model, cfg["api_url"])
