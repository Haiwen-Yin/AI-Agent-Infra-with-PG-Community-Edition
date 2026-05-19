# Release Notes - memory-pg18-by-yhw v2.0.0

**Author**: Haiwen Yin (胖头鱼)  
**Date**: 2026-05-18  
**License**: Apache License 2.0

---

## v2.0.0 — Complete Rewrite: Unified Architecture

v2.0.0 is a **complete rewrite** of the PostgreSQL Memory System, mirroring the unified architecture of oracle-memory-by-yhw v2.0.0. Every component has been redesigned from scratch for consistency, performance, and extensibility.

### Breaking Changes from v1.x

| v1.x | v2.0 | Impact |
|------|------|--------|
| `knowledge_concepts` + separate memory table | `entities` (entity_type discriminator) | All data in one table |
| `knowledge_graph` + separate relations table | `entity_edges` (unified) | All edges in one table |
| psql subprocess calls | psycopg2 ThreadedConnectionPool | 4500x faster (90s → 20ms) |
| 4+ independent SQL scripts | 4-phase ordered deployment | Predictable, idempotent |
| No PL/pgSQL API | 4 schemas, 21 functions | Business logic in database |
| No scheduled jobs | 7 pg_cron jobs | Automated maintenance |
| No security module | DataMaskingService + ReversibleEncryption | Data protection |
| No harness templates | 5 built-in + full CRUD API | Reusable agent blueprints |
| 2 property graphs | 1 unified AGE graph (`memory_graph`) | Simplified graph |
| `agent_memory_access` | `entity_access_log` (all entity types) | Broader audit scope |
| 1046-line SKILL.md | 211 lines + 8 topic docs | Focused, scannable |

### New: Unified Entity Model

All entity types now live in a single `entities` table:

- **MEMORY** — Agent memories (replaces v1.x memory concepts)
- **KNOWLEDGE** — Stable knowledge with `knowledge_meta` extension
- **TASK_OUTPUT** — Task execution results
- **EXPERIENCE** — Distilled experiences
- **HARNESS_TEMPLATE** — Reusable agent execution blueprints with `harness_meta`

### New: 4-Phase SQL Deployment

```bash
# Phase 1 — Schema (18 tables, 53 indexes, 5 views, AGE graph, helper functions)
psql -d memory_graph -f scripts/deploy/1_schema.sql

# Phase 2 — API functions (4 PL/pgSQL schemas, 21 functions)
psql -d memory_graph -f scripts/deploy/2_api.sql

# Phase 3 — Scheduled jobs (7 pg_cron jobs)
psql -d memory_graph -f scripts/deploy/3_jobs.sql

# Phase 4 — Harness templates (5 built-in templates)
psql -d memory_graph -f scripts/deploy/4_harness_templates.sql
```

All scripts are idempotent (`IF NOT EXISTS` / `ON CONFLICT DO NOTHING`).

### New: PL/pgSQL API (4 schemas, 21 functions)

| Schema | Functions | Purpose |
|--------|-----------|---------|
| `memory` | 3 | Embedding generation, auto-embedding concept creation, similarity search |
| `memory_fusion` | 4 | Memory fusion, knowledge extraction, priority decay, stats |
| `knowledge_api` | 5 | Concept validation, deprecation, versioning, lineage |
| `agent_perm` | 5 | Entity access control, session cleanup, collaboration |
| `session_cleanup` | 4 | Log purge, session cleanup, entity archiving, tag counts |

### New: Python API (8 modules, ~2000 lines)

| Module | Functions | Purpose |
|--------|-----------|---------|
| `config.py` | 4 config classes | Unified configuration with env var overrides |
| `connection.py` | 8 | psycopg2 ThreadedConnectionPool, Unix socket support |
| `memory_api.py` | 7 | Memory CRUD on ENTITIES (entity_type='MEMORY') |
| `knowledge_api.py` | 10 | Knowledge CRUD + graph on ENTITIES+KNOWLEDGE_META+ENTITY_EDGES |
| `agent_api.py` | 15 | Agent registration, sessions, collaboration, access log |
| `task_plan_api.py` | 9 | Task plans, steps, snapshots, tool calls, dependencies |
| `security.py` | 4 | DataMaskingService, ReversibleEncryption, password hashing |
| `harness_api.py` | 12 | Template CRUD, instantiate, derive, validate, lineage |

### New: Harness Template System

5 built-in templates with full lifecycle management:

| Template | Category | Purpose |
|----------|----------|---------|
| Research Analyst | research | Research and analysis tasks |
| Code Assistant | development | Code generation and development |
| Data Analyst | analytics | Data analysis and reporting |
| Task Planner | orchestration | Task decomposition and planning |
| Security Auditor | security | Security review and compliance |

### New: Security Module

- **DataMaskingService** — Mask sensitive data (email, phone, SSN, credit card, custom patterns)
- **ReversibleEncryption** — AES-256-CBC encryption/decryption for sensitive storage
- **Password hashing** — PBKDF2-HMAC-SHA256 with configurable iterations

### New: Scheduled Jobs (7)

| Job | Schedule | Action |
|-----|----------|--------|
| memory_fusion_job | Daily 02:00 | Fuse similar memories + decay priorities |
| knowledge_extraction_job | Daily 03:00 | Extract knowledge from memory patterns |
| session_cleanup_job | Every 30 min | Cleanup expired sessions |
| access_log_purge_job | Weekly Sun 04:00 | Purge logs >90 days |
| tag_count_update_job | Daily 01:00 | Update tag usage counts |
| collab_expiry_job | Daily 00:30 | Expire stale collaboration requests |
| entity_archive_job | Weekly Sun 05:00 | Archive low-priority memories >180 days |

**Note**: pg_cron is not installed on the target server; jobs are defined but will not run automatically until pg_cron is installed.

### pg-embedding-gen-by-yhw Integration

The system integrates with **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)**, a custom PostgreSQL 18 extension by Haiwen Yin. This extension is **not** a C extension or a built-in database feature. It uses PG18's `COPY FROM PROGRAM` mechanism to call a Python proxy (`embedding_proxy.py`) that communicates with any OpenAI-compatible `/v1/embeddings` API endpoint.

Key capabilities:
- Multi-model profile management via SQL
- Auto-detection of vector dimensions on first use
- Three call modes: default profile, named profile, or inline
- Base64-encoded input for shell-safe special character handling
- Automatic retry with exponential backoff
- Health check, vector validation, batch generation, cosine similarity
- Request logging and statistics

### Test Suite (37 tests, all passing)

| Module | Tests |
|--------|-------|
| connection | 5 (connect, create_pool, execute, query, query_one) |
| memory | 7 (create, get, update, delete, search, agent_memories, count) |
| knowledge | 8 (create, get, update, delete, relationship, search, stats, neighbors) |
| agent | 9 (register, get, list, session, access_log, collaboration) |
| security | 8 (masking, encryption, password_hash, password_verify) |

### Key Bug Fixes During Development

- `knowledge_api.py`: Fixed `concept_type` column (should be `category` in entities table)
- `agent_api.py`: Fixed wrong table name references
- `task_plan_api.py`: Fixed column names and status values (SUCCESS→COMPLETED, IN_PROGRESS→ACTIVE)
- `test_agent.py`: Fixed assertions and table names
- `1_schema.sql`: Fixed `generate_embedding()` from STABLE to VOLATILE (calls external API)

### Documentation

| File | Lines | Content |
|------|-------|---------|
| SKILL.md | 211 | Agent-learnable skill definition |
| README.md | 250+ | Project overview, quick start, reference |
| docs/architecture.md | 86 | Data model, design decisions |
| docs/api-reference.md | — | Full API documentation |
| docs/deployment.md | 104 | 4-phase deployment, troubleshooting |
| docs/migration.md | — | v1.x → v2.0 migration guide |
| docs/security.md | — | Security module documentation |
| docs/harness.md | — | Harness template system |
| references/ | 4 files | pg-embedding-gen-by-yhw docs |

### Database Schema Summary

| Metric | Count |
|--------|-------|
| Tables | 18 |
| Indexes | 53 |
| Views | 5 |
| PL/pgSQL schemas | 4 |
| PL/pgSQL functions | 21 |
| AGE graphs | 1 (memory_graph) |
| Harness templates | 5 built-in |
| System config rows | 3 seeded |

---

## Compatibility

- **PostgreSQL**: 18+
- **pgvector**: 0.8.2+
- **Apache AGE**: 1.7.0+
- **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)**: v0.2.0+ (install separately; see `references/`)
- **Python**: 3.6+
- **psycopg2-binary**: 2.8.6+

---

## Upgrade from v1.x

v2.0.0 is a **complete rewrite** with a new schema. There is no in-place upgrade path. To migrate:

1. Deploy v2.0.0 schema into a new database (or new schema)
2. Export data from v1.x tables
3. Transform and load into v2.0.0 unified `entities` / `entity_edges` tables
4. See `docs/migration.md` for detailed mapping

---

**Release Date**: 2026-05-18  
**Author**: Haiwen Yin (胖头鱼)  
**License**: Apache License 2.0
