---
name: memory-pg18-by-yhw
version: v2.0.0
author: Haiwen Yin
description: PostgreSQL AI Database Memory System v2.0.0 - Unified architecture with ENTITIES, ENTITY_EDGES, psycopg2 driver, 4-phase SQL deployment, Apache AGE property graph, pg-embedding-gen-by-yhw extension, and multi-agent collaboration
tags: [postgresql, memory-system, knowledge-base, vector-search, psycopg2, property-graph, multi-agent, pg18, age, pg-embedding-gen-by-yhw]
---

# PostgreSQL AI Database Memory System v2.0.0

**Author**: Haiwen Yin
**Version**: v2.0.0 - 2026-05-18
**License**: Apache License 2.0

---

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 18+ | Core database |
| pgvector | 0.8+ | VECTOR type and HNSW index for semantic search |
| Apache AGE | 1.7+ | Property graph and Cypher query support |
| pg-embedding-gen-by-yhw | 1.0+ | Custom extension for in-database embedding generation ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw), see `references/`) |
| Python | 3.6+ | Required by pg-embedding-gen-by-yhw proxy and Python API |
| Python `requests` | Any | HTTP client for pg-embedding-gen-by-yhw proxy |

**pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)) is a custom PostgreSQL 18 extension developed by Haiwen Yin. It is **not** a built-in database feature or a standard PostgreSQL extension. It uses PostgreSQL 18's `COPY FROM PROGRAM` mechanism to call a Python proxy (`embedding_proxy.py`) that communicates with any OpenAI-compatible `/v1/embeddings` API endpoint. Key capabilities:

- Multi-model profile management via SQL (`embedding_register_model`, `embedding_list_models`, etc.)
- Auto-detection of vector dimensions on first use
- Three call modes: default profile, named profile, or inline (model_id + api_url)
- Base64-encoded input for shell-safe special character handling
- Automatic retry with exponential backoff
- Health check, vector validation, batch generation, cosine similarity
- Request logging and statistics

Installation: `sudo bash scripts/install.sh` then `psql -d your_db -f sql/install.sql` (from the pg-embedding-gen-by-yhw project).

## Architecture Overview

```
ENTITIES (unified) --+-- MEMORY (replaces knowledge_concepts + memory concepts)
                     |-- KNOWLEDGE (with KNOWLEDGE_META extension)
                     |-- TASK_OUTPUT
                     |-- EXPERIENCE
                     +-- HARNESS_TEMPLATE (reusable agent execution blueprints)

ENTITY_EDGES (unified) -- replaces knowledge_graph + memory relations

KNOWLEDGE_META -- extended metadata for KNOWLEDGE entities
HARNESS_META -- versioning, status, variables for HARNESS_TEMPLATE entities
ENTITY_EMBEDDINGS -- vector(1024) via pg-embedding-gen-by-yhw for semantic search
```

## Quick Start

### 1. Deploy Schema (4 phases)
```bash
psql -d memory_graph -f scripts/deploy/1_schema.sql
psql -d memory_graph -f scripts/deploy/2_api.sql
psql -d memory_graph -f scripts/deploy/3_jobs.sql
psql -d memory_graph -f scripts/deploy/4_harness_templates.sql
```

### 2. Install Python Dependencies
```bash
pip install psycopg2-binary
```

### 3. Configure
Edit `config.json` or set environment variables:
- `MEMORY_DB_HOST`, `MEMORY_DB_PORT`, `MEMORY_DB_NAME`, `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`
- `MEMORY_EMBEDDING_API`, `MEMORY_SERVER_PORT`

### 4. Run Tests
```bash
cd scripts && python3 -m tests.test_all
```

## Project Structure

```
scripts/
  deploy/
    1_schema.sql    # Tables, indexes, AGE graph, views, helper functions
    2_api.sql       # PL/pgSQL functions (memory_fusion, knowledge_api, agent_perm, session_cleanup)
    3_jobs.sql      # pg_cron jobs (7 automated jobs)
    4_harness_templates.sql  # HARNESS_META + 5 built-in harness templates
  lib/
    config.py       # Unified Config with env var overrides
    connection.py   # psycopg2 ThreadedConnectionPool
    memory_api.py   # Memory CRUD on ENTITIES (entity_type='MEMORY')
    knowledge_api.py # Knowledge CRUD + graph on ENTITIES+KNOWLEDGE_META+ENTITY_EDGES
    agent_api.py    # Agent registration, sessions, collaboration, access log
    task_plan_api.py # Task plans, steps, snapshots, tool calls, dependencies
    security.py     # DataMaskingService, ReversibleEncryption, password hashing
    harness_api.py  # Harness template CRUD, instantiate, derive, validate
  tests/
    test_connection.py
    test_memory.py
    test_knowledge.py
    test_agent.py
    test_security.py
    test_all.py
docs/
  architecture.md
  api-reference.md
  deployment.md
  migration.md
  security.md
  harness.md
config.json         # Database, server, embedding, security config
```

## Key Tables (18 total)

| Table | Purpose |
|-------|---------|
| entities | Unified store: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE |
| entity_edges | Unified directed edges with strength/confidence |
| knowledge_meta | Source type, validation, versioning, confidence |
| harness_meta | Harness template versioning, status, variables, changelog |
| entity_embeddings | vector(1024) embeddings (pg-embedding-gen-by-yhw) |
| agent_registry | Agent identity, capabilities, permissions |
| agent_session | Session tracking with context snapshots |
| entity_access_log | Audit trail for all entity access |
| agent_permission_log | Permission change audit |
| agent_collaboration | Cross-agent sharing requests |
| task_plans | Multi-step task definitions |
| task_steps | Plan steps with status tracking |
| task_context_snapshots | Breakpoint/recovery snapshots |
| task_tool_calls | Tool invocation audit |
| task_dependencies | Inter-plan dependency graph |
| tags / entity_tags | Normalized tag system |
| system_config / system_users | System configuration and user accounts |

## PL/pgSQL API (4 schemas, 21 functions)

| Schema | Function | Purpose |
|--------|----------|---------|
| memory | generate_embedding() | Generate embedding via pg-embedding-gen-by-yhw |
| memory | add_concept_with_embedding() | Create knowledge with auto-embedding |
| memory | search_similar() | Vector similarity search |
| memory_fusion | fuse_similar_memories() | Merge similar memories |
| memory_fusion | extract_knowledge_from_memories() | Extract knowledge from patterns |
| memory_fusion | decay_old_memories() | Decay old memory priorities |
| memory_fusion | get_fusion_stats() | Fusion statistics as JSONB |
| knowledge_api | validate_concept() | Mark knowledge as validated |
| knowledge_api | deprecate_concept() | Deprecate knowledge concept |
| knowledge_api | create_concept_version() | Create new version of concept |
| knowledge_api | get_unvalidated() | List unvalidated concepts |
| knowledge_api | get_concept_lineage() | Get concept ancestry/descendants |
| agent_perm | check_entity_access() | Check agent access to entity |
| agent_perm | grant_access() | Grant entity access to agent |
| agent_perm | revoke_access() | Revoke entity access |
| agent_perm | cleanup_expired_sessions() | Clean expired sessions |
| agent_perm | process_collaboration_requests() | Expire stale requests |
| session_cleanup | purge_access_logs() | Delete old access logs |
| session_cleanup | purge_inactive_sessions() | Delete closed sessions |
| session_cleanup | archive_old_entities() | Archive low-priority memories |
| session_cleanup | update_tag_counts() | Recalculate tag usage counts |

## Scheduled Jobs (7)

| Job | Schedule | Action |
|-----|----------|--------|
| memory_fusion_job | Daily 02:00 | Fuse similar memories + decay priorities |
| knowledge_extraction_job | Daily 03:00 | Extract knowledge from memory patterns |
| session_cleanup_job | Every 30 min | Cleanup expired sessions |
| access_log_purge_job | Weekly Sun 04:00 | Purge logs >90 days |
| tag_count_update_job | Daily 01:00 | Update tag usage counts |
| collab_expiry_job | Daily 00:30 | Expire stale collaboration requests |
| entity_archive_job | Weekly Sun 05:00 | Archive low-priority memories >180 days |

## Python API Quick Reference

```python
from scripts.lib.memory_api import create_memory, get_memory, search_memories
from scripts.lib.knowledge_api import create_concept, create_relationship
from scripts.lib.agent_api import register_agent, create_session
from scripts.lib.harness_api import create_template, instantiate_template

entity_id = create_memory("Meeting Notes", "Discussed v2.0 architecture", category="meeting")
concept_id = create_concept("Architecture Pattern", "principle", description="Unified entity model")
edge_id = create_relationship(entity_id, concept_id, "DERIVED_FROM", strength=0.9)
register_agent("agent-1", "Research Agent", capabilities=["read", "write"])
config = instantiate_template(tpl_id, variables={"role": "Data Scientist"})
```

## v1.x to v2.0 Key Changes

- knowledge_concepts + memory concepts -> ENTITIES (entity_type discriminator)
- knowledge_graph + memory relations -> ENTITY_EDGES
- psql subprocess -> psycopg2 ThreadedConnectionPool (20ms/query, 4500x faster)
- 4+ independent SQL scripts -> 4-phase ordered deployment
- No PL/pgSQL API -> 4 schemas with 21 functions
- No scheduled jobs -> 7 pg_cron jobs
- No security module -> DataMaskingService + ReversibleEncryption
- No harness templates -> 5 built-in templates + full CRUD API
- 1046-line SKILL.md -> 200 lines + 8 topic docs
- 2 property graphs -> 1 unified AGE graph (memory_graph)
- agent_memory_access -> entity_access_log (all entity types)

## PostgreSQL-Specific Features

- **pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)): Custom PostgreSQL 18 extension (by Haiwen Yin) for in-database embedding generation. Uses PG18's `COPY FROM PROGRAM` mechanism + Python proxy to call any OpenAI-compatible `/v1/embeddings` API — no C compilation required. Supports multi-model profiles, auto-dimension detection, batch generation, health checks, cosine similarity, and request logging. Not a built-in database feature; requires separate installation (see `references/`).
- **pgvector HNSW**: Hardware-accelerated vector similarity search
- **Apache AGE Cypher**: Graph traversal queries on unified entity graph
- **JSONB**: Native JSON operations with GIN indexing
- **IDENTITY columns**: Clean auto-increment without sequences

## Critical Constraints

- **Database**: PostgreSQL 18 on 10.10.10.131, user=`pgsql`, trust auth, Unix socket at `/tmp`
- **Connection**: When config `host` is `localhost` or empty, connect via Unix socket (`host='/tmp'`), not TCP
- **AGE graph name**: Cannot start with `pg_` (reserved); use `memory_graph`
- **pg_cron**: NOT installed on server — jobs are defined in `3_jobs.sql` but won't run automatically
- **Embedding API**: http://10.10.10.1:12345/v1, model `text-embedding-bge-m3`, 1024 dimensions
- **Python**: 3.6 on remote server; psycopg2-binary 2.8.6 installed via `pip3 --user`
- **Entity types**: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE — stored in `entities.entity_type`
- **Knowledge category**: Stored in `entities.category`, NOT in `knowledge_meta` (no concept_type column there)
- **Task status mapping**: Python API maps SUCCESS→COMPLETED, IN_PROGRESS→ACTIVE to match schema CHECK constraints
- **Visibility**: PRIVATE (owner only), SHARED (all agents), COLLABORATIVE (owner + `accessible_to` list)
- **Edge strength**: 0.0–2.0 (not 0–1); confidence: 0.0–1.0
