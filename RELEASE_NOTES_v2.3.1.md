# PG Memory System v2.3.1 Release Notes

**Release Date**: 2026-05-26
**Version**: v2.3.1
**Compatibility**: Backward-compatible with v2.3.0 database

---

## Summary

**Embedding Generation & Vector Search Enhancement + UI Fixes** — Adds Python embedding_api.py module with 12 functions for vector embedding generation, storage, similarity search, hybrid search, and cross-type search. Fixes list scrolling, sticky table headers, and pagination across all 7 list pages. Aligns with Oracle v2.3.1 embedding capabilities.

## What's New

### embedding_api.py (NEW)

| Function | Description |
|----------|-------------|
| `generate_embedding(text)` | Generate vector via OpenAI-compatible embedding API |
| `store_embedding(entity_id, entity_type, text)` | Generate + store in entity_embeddings |
| `store_embedding_vector(entity_id, entity_type, embedding)` | Store pre-computed vector |
| `get_embedding(entity_id, entity_type)` | Get embedding metadata |
| `delete_embedding(entity_id, entity_type)` | Delete embedding |
| `search_similar(text, top_k, entity_type, workspace_id)` | pgvector cosine similarity search |
| `search_by_entity_id(entity_id, entity_type, top_k)` | Search similar to existing entity (auto-excludes self) |
| `search_hybrid(text, keyword, top_k, vector_weight)` | Vector + keyword hybrid search with 3D scoring |
| `search_multi_type(text, entity_types, top_k)` | Cross-type vector search (MEMORY/KNOWLEDGE/SPEC) |
| `generate_embeddings_batch(entity_type, limit)` | Batch embed entities missing vectors |
| `get_embedding_stats()` | Embedding statistics |
| `get_model_dimension(model)` | Get/auto-detect model dimension |

### EMBEDDING_GENERATION_JOB (NEW)

pg_cron job that runs every 2 hours to automatically generate embeddings for new MEMORY and KNOWLEDGE entities that don't have vectors yet.

### Test Coverage

19 embedding tests covering: generation, storage, retrieval, vector similarity search, entity-based search, hybrid search, cross-type search, batch processing, dimension detection, statistics, and cleanup.

## PG18-Specific Implementation

- Uses pgvector `<=>` operator for cosine distance (not Oracle VECTOR_DISTANCE)
- Uses `%s` positional bind variables (not Oracle `:named` binds)
- Uses `::vector` cast (not Oracle TO_VECTOR)
- Uses `ILIKE` for keyword matching (not Oracle UPPER/LIKE)
- Uses `LIMIT` (not Oracle FETCH FIRST)
- BIGINT entity_id (not Oracle VARCHAR)
- Leverages existing `memory.generate_embedding()` PL/pgSQL and `pg-embedding-gen-by-yhw` extension

## Database Changes

No schema changes. New objects:
- `EMBEDDING_GENERATION_JOB` pg_cron job in 3_jobs.sql

## Upgrade from v2.3.0

```bash
# Deploy EMBEDDING_GENERATION_JOB
psql -h 10.10.10.131 -U pgsql -d memory_graph -f scripts/deploy/3_jobs.sql

# No data migration required. Existing entity_embeddings data is preserved.
```

## Test Results

```
PG Memory System v2.3.1 - Full Test Suite
============================================================
  Connection:   6/6 PASS
  Memory:      16/16 PASS
  Knowledge:   19/19 PASS
  Agent:       22/22 PASS
  Graph:       12/12 PASS
  Harness:     12/12 PASS
  Security:    19/19 PASS
  Workspace:   14/14 PASS
  Spec:        10/10 PASS
  Collab:      10/10 PASS
  Credential:   9/9 PASS
  Embedding:   19/19 PASS
Overall: 168/168 ALL PASSED
```

## Comparison

| Metric | v2.3.0 | v2.3.1 | Delta |
|--------|--------|--------|-------|
| PL/pgSQL Schemas | 7 | 7 | No change |
| pg_cron Jobs | 12 | 13 | +1 (EMBEDDING_GENERATION_JOB) |
| Python Modules | 12 | 13 | +1 (embedding_api.py) |
| Tests | 143 | 162 | +19 (embedding tests) |
| Tables | 27 | 27 | No change |

## UI Fixes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| List pages cannot scroll with mouse wheel | `body` used `min-height:100vh` (no definite height for flex children) | Changed to `height:100vh` |
| List pages cannot scroll (Pattern B) | `.content-area` lacked `min-height:0` (required for flex overflow) | Added `min-height:0` |
| Table headers not sticky on scroll | `border-collapse:collapse` breaks `position:sticky` on `<th>` | Changed to `border-collapse:separate;border-spacing:0` |
| Scrolled content visible behind sticky header | Scroll container had `padding:16px 20px` (top padding gap) | Changed to `padding:0 20px` (remove top/bottom padding) |
| No pagination for lists >30 items | Missing pagination code | Added `PAGE_SIZE=30`, `renderPagination()`, `goPage()` to all 7 pages |
| Missing knowledge_meta for entity 1009 | `search_knowledge` JOIN requires knowledge_meta row | Inserted missing row |
