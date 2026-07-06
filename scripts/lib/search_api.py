"""AI Agent Infra v3.9.0 - PG Community Edition - Unified Search API

Single entry point for AI agents to search across all data types and modalities.

- "vector"       - Semantic similarity via pgvector <=> cosine distance
- "fulltext"     - tsvector/tsquery with GIN index
- "keyword"      - ILIKE pattern matching
- "graph"        - AGE cypher traversal
- "hybrid"       - Vector + fulltext combined
- "unified"      - 5-signal fusion in Python (vector + fulltext + relational + tag + graph)
- "unified_sql"  - Single SQL CTE fusing all 5 signals (70-85% lower latency)
- "relational"   - Structured metadata filtering
- "multi_type"   - Cross entity_type search
- "auto"         - Intelligent strategy selection
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import execute_query, execute_query_one

logger = logging.getLogger(__name__)

STRATEGIES = {
    "vector": {
        "name": "Vector Similarity Search",
        "description": "Semantic similarity via pgvector <=> cosine distance. Best for meaning/concept search.",
        "signals": ["vector"],
        "best_for": ["semantic search", "concept matching", "finding similar content"],
        "requires_embedding": True,
        "supports_filters": ["entity_type", "workspace_id"],
        "speed": "medium",
        "precision": "high",
    },
    "fulltext": {
        "name": "Full-Text Search",
        "description": "tsvector/tsquery with GIN index. Best for exact keyword/phrase search.",
        "signals": ["fulltext"],
        "best_for": ["exact keyword", "phrase search", "boolean queries"],
        "requires_embedding": False,
        "supports_filters": ["entity_type", "category", "workspace_id"],
        "speed": "fast",
        "precision": "high",
    },
    "keyword": {
        "name": "ILIKE Pattern Matching",
        "description": "Simple ILIKE pattern matching on title/content.",
        "signals": ["keyword"],
        "best_for": ["partial match", "wildcard patterns", "simple filtering"],
        "requires_embedding": False,
        "supports_filters": ["entity_type", "category", "workspace_id"],
        "speed": "slow",
        "precision": "low",
    },
    "graph": {
        "name": "Graph Traversal Search",
        "description": "Graph traversal via entity edges. Best for connected entities.",
        "signals": ["graph"],
        "best_for": ["relationship queries", "neighborhood exploration"],
        "requires_embedding": False,
        "supports_filters": ["entity_type", "edge_type"],
        "speed": "medium",
        "precision": "medium",
    },
    "hybrid": {
        "name": "Vector + Fulltext Hybrid",
        "description": "Combines vector similarity with full-text scoring.",
        "signals": ["vector", "fulltext"],
        "best_for": ["general search", "semantic + keyword"],
        "requires_embedding": True,
        "supports_filters": ["entity_type", "workspace_id"],
        "speed": "medium",
        "precision": "high",
    },
    "unified": {
        "name": "5-Signal Unified Search",
        "description": "Full fusion: vector + fulltext + relational + tag + graph.",
        "signals": ["vector", "fulltext", "relational", "tag", "graph"],
        "best_for": ["comprehensive search", "multi-dimensional ranking"],
        "requires_embedding": True,
        "supports_filters": ["entity_type", "workspace_id", "domain", "category", "tags"],
        "speed": "slow",
        "precision": "very high",
    },
    "unified_sql": {
        "name": "Single-SQL 5-Signal Unified Search",
        "description": "Same 5-signal fusion as unified but as single CTE-based SQL. 70-85% lower latency.",
        "signals": ["vector", "fulltext", "relational", "tag", "graph"],
        "best_for": ["production search", "low-latency retrieval"],
        "requires_embedding": True,
        "supports_filters": ["entity_type", "workspace_id", "domain", "category", "tags"],
        "speed": "fast",
        "precision": "very high",
    },
    "relational": {
        "name": "Relational Metadata Search",
        "description": "Structured query on KNOWLEDGE_META, SPEC_META, ENTITIES metadata.",
        "signals": ["relational"],
        "best_for": ["domain filtering", "category browsing", "structured metadata"],
        "requires_embedding": False,
        "supports_filters": ["domain", "category", "entity_type", "importance"],
        "speed": "fast",
        "precision": "high",
    },
    "multi_type": {
        "name": "Cross-Type Vector Search",
        "description": "Vector similarity across multiple entity types simultaneously.",
        "signals": ["vector", "multi_type"],
        "best_for": ["cross-type discovery", "holistic knowledge retrieval"],
        "requires_embedding": True,
        "supports_filters": ["entity_types", "workspace_id"],
        "speed": "medium",
        "precision": "high",
    },
    "auto": {
        "name": "Auto Strategy Selection",
        "description": "Automatically selects the best search strategy.",
        "signals": ["auto"],
        "best_for": ["unknown query type", "mixed intent"],
        "requires_embedding": False,
        "supports_filters": ["all"],
        "speed": "varies",
        "precision": "varies",
    },
}


def _detect_strategy(text: str, **kwargs) -> str:
    if kwargs.get("entity_id") and not text:
        return "graph"
    if any(op in text.upper() for op in [" AND ", " OR ", " NOT "]):
        return "fulltext"
    if "%" in text or "_" in text:
        return "keyword"
    if kwargs.get("domain") or kwargs.get("tags"):
        return "unified"
    if kwargs.get("graph_seed_entity_id"):
        return "unified"
    if len(text.split()) <= 2:
        return "fulltext"
    if len(text.split()) >= 5:
        return "unified"
    return "hybrid"


def _search_vector(text, top_k=10, entity_type=None, workspace_id=None):
    from . import embedding_api
    return embedding_api.search_similar(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id)


def _search_fulltext(text, top_k=20, entity_type=None, category=None, workspace_id=None):
    conditions = ["e.search_vector @@ plainto_tsquery('english', %s)", "e.status = 'ACTIVE'"]
    params = [text]
    if entity_type:
        conditions.append("e.entity_type = %s")
        params.append(entity_type)
    if category:
        conditions.append("e.category = %s")
        params.append(category)
    if workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)
    params.append(top_k)
    where = " AND ".join(conditions)
    sql = f"""SELECT e.entity_id, e.entity_type, e.title, e.category, e.importance,
               e.workspace_id, e.owned_by_agent,
               ts_rank(e.search_vector, plainto_tsquery('english', %s)) AS rank
        FROM entities e WHERE {where} ORDER BY rank DESC LIMIT %s"""
    return execute_query(sql, params)


def _search_keyword(keyword, entity_type=None, category=None, workspace_id=None, limit=100):
    conditions = ["e.status = 'ACTIVE'"]
    params = []
    like_pattern = f"%{keyword}%"
    conditions.append("(e.title ILIKE %s OR e.content ILIKE %s)")
    params.extend([like_pattern, like_pattern])
    if entity_type:
        conditions.append("e.entity_type = %s")
        params.append(entity_type)
    if category:
        conditions.append("e.category = %s")
        params.append(category)
    if workspace_id:
        conditions.append("e.workspace_id = %s")
        params.append(workspace_id)
    params.append(limit)
    where = " AND ".join(conditions)
    sql = f"""SELECT e.entity_id, e.entity_type, e.title, e.category, e.importance,
               e.workspace_id, e.owned_by_agent
        FROM entities e WHERE {where} ORDER BY e.importance DESC LIMIT %s"""
    return execute_query(sql, params)


def _search_graph(entity_id, entity_type=None, direction="both", edge_type=None, limit=100):
    from . import graph_api
    return graph_api.get_neighbors(entity_id, direction=direction, edge_type=edge_type, limit=limit)


def _search_hybrid(text, top_k=10, entity_type=None, workspace_id=None, vector_weight=0.7, fulltext_weight=0.3):
    from . import embedding_api
    return embedding_api.search_hybrid(text, top_k=top_k, entity_type=entity_type,
                                       workspace_id=workspace_id, vector_weight=vector_weight,
                                       fulltext_weight=fulltext_weight)


def _search_unified(text, top_k=20, entity_type=None, workspace_id=None, domain=None,
                    category=None, tags=None, graph_seed_entity_id=None,
                    graph_seed_entity_type=None, vector_weight=0.4, fulltext_weight=0.25,
                    relational_weight=0.2, graph_weight=0.15):
    from . import embedding_api
    return embedding_api.search_unified(text, top_k=top_k, entity_type=entity_type,
                                        workspace_id=workspace_id, domain=domain, category=category,
                                        tags=tags, graph_seed_entity_id=graph_seed_entity_id,
                                        graph_seed_entity_type=graph_seed_entity_type,
                                        vector_weight=vector_weight, fulltext_weight=fulltext_weight,
                                        relational_weight=relational_weight, graph_weight=graph_weight)


def _search_unified_sql(text, top_k=20, entity_type=None, workspace_id=None, domain=None,
                        category=None, tags=None, graph_seed_entity_id=None,
                        graph_seed_entity_type=None, vector_weight=0.4, fulltext_weight=0.25,
                        relational_weight=0.2, graph_weight=0.15):
    from . import embedding_api
    return embedding_api.search_unified_sql(text, top_k=top_k, entity_type=entity_type,
                                            workspace_id=workspace_id, domain=domain, category=category,
                                            tags=tags, graph_seed_entity_id=graph_seed_entity_id,
                                            graph_seed_entity_type=graph_seed_entity_type,
                                            vector_weight=vector_weight, fulltext_weight=fulltext_weight,
                                            relational_weight=relational_weight, graph_weight=graph_weight)


def _search_relational(entity_type=None, domain=None, category=None, min_importance=None, limit=50):
    params = [limit]
    conditions = []
    if entity_type:
        conditions.append("AND e.entity_type = %s")
        params.append(entity_type)
    if domain:
        conditions.append("AND km.domain = %s")
        params.append(domain)
    if category:
        conditions.append("AND e.category = %s")
        params.append(category)
    if min_importance:
        conditions.append("AND e.importance >= %s")
        params.append(min_importance)
    where = " ".join(conditions)
    sql = f"""SELECT e.entity_id, e.entity_type, e.title, e.category, e.importance,
               km.domain, km.topic, km.difficulty,
               sm.spec_scope, sm.complexity, sm.spec_status
        FROM entities e
        LEFT JOIN knowledge_meta km ON km.entity_id = e.entity_id
        LEFT JOIN spec_meta sm ON sm.entity_id = e.entity_id
        WHERE 1=1 {where}
        ORDER BY e.importance DESC LIMIT %s"""
    try:
        rows = execute_query(sql, params)
        results = []
        for r in rows:
            results.append({
                "entity_id": r["entity_id"], "entity_type": r["entity_type"],
                "title": r.get("title", ""), "category": r.get("category", ""),
                "importance": float(r["importance"]) if r.get("importance") else None,
                "km_domain": r.get("domain"), "km_topic": r.get("topic"),
                "km_difficulty": r.get("difficulty"),
                "sm_scope": r.get("spec_scope"), "sm_complexity": r.get("complexity"),
                "sm_spec_status": r.get("spec_status"),
            })
        return results
    except Exception as e:
        logger.error("Relational search failed: %s", e)
        return []


def _search_multi_type(text, top_k=10, entity_types=None, workspace_id=None):
    from . import embedding_api
    mt = embedding_api.search_multi_type(text, top_k=top_k, entity_types=entity_types, workspace_id=workspace_id)
    if isinstance(mt, dict):
        flat = []
        for etype, items in mt.items():
            for item in items:
                item["_source_type"] = etype
                flat.append(item)
        return flat
    return mt


def search(
    text, strategy="auto", top_k=10, entity_type=None, workspace_id=None,
    domain=None, category=None, tags=None, graph_seed_entity_id=None,
    graph_seed_entity_type=None, entity_id=None, entity_types=None,
    min_importance=None, vector_weight=None, fulltext_weight=None,
    relational_weight=None, graph_weight=None, **kwargs,
):
    if strategy == "auto":
        strategy = _detect_strategy(text, **kwargs)

    result = {"strategy": strategy, "query": text, "results": [], "count": 0}

    try:
        if strategy == "vector":
            result["results"] = _search_vector(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id)
        elif strategy == "fulltext":
            result["results"] = _search_fulltext(text, top_k=top_k, entity_type=entity_type, category=category, workspace_id=workspace_id)
        elif strategy == "keyword":
            result["results"] = _search_keyword(keyword=text, entity_type=entity_type, category=category, workspace_id=workspace_id, limit=top_k)
        elif strategy == "graph":
            seed_id = entity_id or graph_seed_entity_id
            if seed_id:
                result["results"] = _search_graph(seed_id, entity_type=entity_type, direction=kwargs.get("direction", "both"), edge_type=kwargs.get("edge_type"), limit=top_k)
        elif strategy == "hybrid":
            result["results"] = _search_hybrid(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id, vector_weight=vector_weight or 0.7, fulltext_weight=fulltext_weight or 0.3)
        elif strategy == "unified":
            result["results"] = _search_unified(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id, domain=domain, category=category, tags=tags, graph_seed_entity_id=graph_seed_entity_id, graph_seed_entity_type=graph_seed_entity_type, vector_weight=vector_weight or 0.4, fulltext_weight=fulltext_weight or 0.25, relational_weight=relational_weight or 0.2, graph_weight=graph_weight or 0.15)
        elif strategy == "unified_sql":
            result["results"] = _search_unified_sql(text, top_k=top_k, entity_type=entity_type, workspace_id=workspace_id, domain=domain, category=category, tags=tags, graph_seed_entity_id=graph_seed_entity_id, graph_seed_entity_type=graph_seed_entity_type, vector_weight=vector_weight or 0.4, fulltext_weight=fulltext_weight or 0.25, relational_weight=relational_weight or 0.2, graph_weight=graph_weight or 0.15)
        elif strategy == "relational":
            result["results"] = _search_relational(entity_type=entity_type, domain=domain, category=category, min_importance=min_importance, limit=top_k)
        elif strategy == "multi_type":
            result["results"] = _search_multi_type(text, top_k=top_k, entity_types=entity_types, workspace_id=workspace_id)
        else:
            logger.warning("Unknown strategy: %s, falling back to unified", strategy)
            result["strategy"] = "unified"
            result["results"] = _search_unified(text, top_k=top_k)
    except Exception as e:
        logger.error("Search failed (strategy=%s): %s", strategy, e)
        result["error"] = str(e)

    result["count"] = len(result["results"])
    return result


def search_vector(text, top_k=10, entity_type=None, workspace_id=None):
    return search(text, strategy="vector", top_k=top_k, entity_type=entity_type, workspace_id=workspace_id)


def search_fulltext(text, top_k=20, entity_type=None, category=None, workspace_id=None):
    return search(text, strategy="fulltext", top_k=top_k, entity_type=entity_type, category=category, workspace_id=workspace_id)


def search_keyword(keyword, entity_type=None, category=None, workspace_id=None, limit=100):
    return search(keyword, strategy="keyword", top_k=limit, entity_type=entity_type, category=category, workspace_id=workspace_id)


def search_unified(text, top_k=20, **kwargs):
    return search(text, strategy="unified", top_k=top_k, **kwargs)


def search_auto(text, top_k=10, **kwargs):
    return search(text, strategy="auto", top_k=top_k, **kwargs)
