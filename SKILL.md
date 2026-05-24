---
name: memory-pg18-by-yhw
version: v2.2.1
author: Haiwen Yin
description: "PostgreSQL AI Database Memory System v2.2.1 - Workspace & context continuity, agent handoff, Apache AGE property graph, pgvector HNSW, pg-embedding-gen-by-yhw, psycopg2 driver, 4-phase SQL deployment, normalized tags, 22 tables, 5 PL/pgSQL schemas"
tags: [postgresql, memory-system, knowledge-base, vector-search, psycopg2, property-graph, multi-agent, pg18, age, pg-embedding-gen-by-yhw, workspace, context-continuity, handoff, normalized-tags, jsonb]
---

# PostgreSQL AI Database Memory System v2.2.1

**Author**: Haiwen Yin
**Version**: v2.2.1 - 2026-05-24
**License**: Apache License 2.0

---

## Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| PostgreSQL | 18+ | Core database |
| pgvector | 0.8+ | VECTOR type and HNSW index for semantic search |
| Apache AGE | 1.7+ | Property graph and Cypher query support |
| pg-embedding-gen-by-yhw | 1.0+ | Custom extension for in-database embedding generation ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)) |
| Python | 3.14+ | Python API, web visualization (3.6+ for API only) |
| Python `psycopg2-binary` | 2.9+ | PostgreSQL database driver |
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
+------------------------------------------------------------------+
|                     PostgreSQL AI Memory System                  |
+------------------------------------------------------------------+
|                                                                  |
|  +-----------------------------------------------------------+   |
|  |           ENTITIES (unified, BIGINT IDENTITY PK)          |   |
|  |  +----------+----------+----------+--------+--------------+   |
|  |  | MEMORY   | KNOWLEDGE|TASK_OUT  |EXPERI- | HARNESS_     |   |
|  |  |          |          |PUT       |ENCE    | TEMPLATE     |   |
|  |  +----------+----------+----------+--------+--------------+   |
|  |  COL: WORKSPACE_ID -> WORKSPACES                          |   |
|  +-----------------------------------------------------------+   |
|                         |                                        |
|  +-----------------------------------------------+               |
|  |  ENTITY_EDGES (unified directed edges)        |               |
|  |  SOURCE_TYPE denormalized for AGE + queries   |               |
|  +-----------------------------------------------+               |
|                                                                  |
|  +-----------------------------------------------+               |
|  |  WORKSPACES (v2.2.0)                          |               |
|  |  |-- WORKSPACE_CONTEXT (append-only JSONB)    |               |
|  |  +-- WORKSPACE_TASKS (workspace <-> plan link)|               |
|  +-----------------------------------------------+               |
|                                                                  |
|  +-----------------------------------------------+               |
|  |  AGENT_SESSION (handoff chain)                |               |
|  |  PREDECESSOR_SESSION_ID -> self (chain)       |               |
|  |  WORKSPACE_ID -> WORKSPACES                   |               |
|  +-----------------------------------------------+               |
|                                                                  |
+------------------------------------------------------------------+
```

## v2.2.0 Key Addition: Workspace & Context Continuity

| Feature | Description |
|---------|-------------|
| WORKSPACES | Isolated execution environments for agents with SHARED/ISOLATED modes |
| ISOLATION_MODE | SHARED (cross-workspace visibility) or ISOLATED (strict boundary) |
| WORKSPACE_CONTEXT | Append-only context chain (CHECKPOINT, HANDOFF, SUMMARY, ERROR_STATE, AUTO_SAVE) |
| Agent Handoff | Session chain via PREDECESSOR_SESSION_ID; context auto-loaded on create_session |
| ENTITIES.WORKSPACE_ID | FK to WORKSPACES; all entity queries scoped by workspace when ISOLATED |
| workspace_manager Schema | 10 PL/pgSQL functions for workspace lifecycle, context chain, handoff, recovery |

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
    2_api.sql       # PL/pgSQL functions (5 schemas, 31+ functions)
    3_jobs.sql      # pg_cron jobs (9 automated jobs)
    4_harness_templates.sql  # HARNESS_META + 5 built-in harness templates
  lib/
    config.py       # Unified Config with env var overrides
    connection.py   # psycopg2 ThreadedConnectionPool
    memory_api.py   # Memory CRUD on ENTITIES (entity_type='MEMORY')
    knowledge_api.py # Knowledge CRUD + graph on ENTITIES+KNOWLEDGE_META+ENTITY_EDGES
    agent_api.py    # Agent registration, sessions, collaboration, access log
    task_plan_api.py # Task plans, steps, snapshots, tool calls, dependencies
    security.py     # DataMaskingService, ReversibleEncryption, password hashing
    harness_api.py  # Harness template CRUD, instantiate, variable extraction
    graph_api.py    # Property graph traversal via Apache AGE Cypher + SQL fallback (9 functions)
    workspace_api.py # Workspace lifecycle, context chain, handoff, recovery (11 functions)
  tests/
    test_connection.py
    test_memory.py
    test_knowledge.py
    test_agent.py
    test_graph.py
    test_harness.py
    test_security.py
    test_workspace.py
    test_all.py
docs/
  architecture.md
  api-reference.md
  deployment.md
  migration.md
  security.md
  harness.md
  workspace.md
  minimum-privileges.md
  visualization.md
  introduction_v2.2.1_zh.md
config.json         # Database, server, embedding, security config
```

## Database Schema (22 Tables)

### Core Tables (8)

| Table | Purpose |
|-------|---------|
| entities | Unified store: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE |
| entity_edges | Unified directed edges with strength/confidence |
| knowledge_meta | Domain, topic, difficulty, review scheduling, validation, versioning |
| harness_meta | Template versioning, input/output schema, execution mode |
| entity_embeddings | vector(1024) embeddings (pg-embedding-gen-by-yhw) |
| tags | Normalized tag definitions (tag_id, tag_name, tag_group) |
| entity_tags | Entity-tag associations (composite PK: entity_id + entity_type + tag_id) |
| agent_permission_log | Permission change audit |

### Agent Tables (4)

| Table | Purpose |
|-------|---------|
| agent_registry | Agent identity, capabilities, permissions |
| agent_session | Session tracking with context snapshots, handoff chain (PREDECESSOR_SESSION_ID) |
| entity_access_log | Audit trail for all entity access |
| agent_collaboration | Cross-agent sharing requests |

### Task Tables (5)

| Table | Purpose |
|-------|---------|
| task_plans | Multi-step task definitions |
| task_steps | Plan steps with status tracking |
| task_context_snapshots | Breakpoint/recovery snapshots |
| task_tool_calls | Tool invocation audit |
| task_dependencies | Inter-plan dependency graph |

### Workspace Tables (3 NEW)

| Table | Purpose |
|-------|---------|
| workspaces | Workspace lifecycle (ACTIVE/PAUSED/ARCHIVED), isolation mode, ownership |
| workspace_context | Append-only context chain (CHECKPOINT, HANDOFF, SUMMARY, ERROR_STATE, AUTO_SAVE) |
| workspace_tasks | Junction: workspace <-> task plans |

### System Tables (2)

| Table | Purpose |
|-------|---------|
| system_config | System configuration key-value store |
| system_users | System user accounts with roles |

## PL/pgSQL API (5 Schemas, 31+ Functions)

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
| knowledge_api | record_review() | Record knowledge review with spaced repetition |
| knowledge_api | get_due_reviews() | Get concepts due for review |
| agent_perm | check_entity_access() | Check agent access to entity |
| agent_perm | grant_access() | Grant entity access to agent |
| agent_perm | revoke_access() | Revoke entity access |
| agent_perm | cleanup_expired_sessions() | Clean expired sessions |
| agent_perm | process_collaboration_requests() | Expire stale requests |
| session_cleanup | purge_access_logs() | Delete old access logs |
| session_cleanup | purge_inactive_sessions() | Delete closed sessions |
| session_cleanup | archive_old_entities() | Archive low-priority memories |
| session_cleanup | update_tag_counts() | Recalculate tag usage counts |
| workspace_manager | create_workspace() | Create a new workspace |
| workspace_manager | get_workspace() | Get workspace details as JSONB |
| workspace_manager | update_workspace_status() | Update workspace lifecycle status |
| workspace_manager | delete_workspace() | Delete workspace (cascades) |
| workspace_manager | add_context_entry() | Add context entry to workspace |
| workspace_manager | get_context_chain() | Get workspace context chain |
| workspace_manager | create_handoff() | Create agent handoff session |
| workspace_manager | recover_to_checkpoint() | Recover workspace to checkpoint |
| workspace_manager | get_workspace_summary() | Get workspace summary as JSONB |
| workspace_manager | cleanup_abandoned() | Archive abandoned workspaces |

## Python API (10 Modules)

| Module | Functions | Purpose |
|--------|-----------|---------|
| config.py | 4 config classes | Unified configuration with env var overrides |
| connection.py | 8 | psycopg2 ThreadedConnectionPool, Unix socket support |
| memory_api.py | 10 | Memory CRUD + tags + count on ENTITIES (entity_type='MEMORY') |
| knowledge_api.py | 13 | Knowledge CRUD + edges + reviews + tags + count |
| agent_api.py | 14 | Agent registration, sessions, collaboration, access log |
| task_plan_api.py | 12 | Task plans, steps, snapshots, tool calls, dependencies |
| security.py | 2 | Password hashing and verification (hash_password, verify_password) |
| harness_api.py | 8 | Template CRUD, instantiate, variable extraction, count |
| graph_api.py | 9 | Property graph traversal via Apache AGE Cypher + SQL fallback |
| workspace_api.py | 11 | Workspace lifecycle, context chain, handoff, recovery |

## Scheduled Jobs (9)

| Job | Schedule | Action |
|-----|----------|--------|
| memory_fusion_job | Daily 02:00 | Fuse similar memories + decay priorities |
| knowledge_extraction_job | Daily 03:00 | Extract knowledge from memory patterns |
| knowledge_review_job | Daily 06:00 | Schedule knowledge spaced-repetition reviews |
| session_cleanup_job | Every 30 min | Cleanup expired sessions |
| access_log_purge_job | Weekly Sun 04:00 | Purge logs >90 days |
| entity_archive_job | Weekly Sun 05:00 | Archive low-priority memories >180 days |
| collab_expiry_job | Daily 00:30 | Expire stale collaboration requests |
| workspace_cleanup_job | Daily 01:00 | Archive abandoned workspaces |
| stale_workspace_detect_job | Hourly | Pause workspaces inactive >7 days |

**Note**: pg_cron is not installed on the target server; jobs are defined but will not run automatically until pg_cron is installed.

## Harness Templates (5 Built-in)

| Template | Category | Execution Mode |
|----------|----------|---------------|
| Research Analyst | research | SEQUENTIAL |
| Code Assistant | development | SEQUENTIAL |
| Data Analyst | analytics | PARALLEL |
| Task Planner | orchestration | CONDITIONAL |
| Security Auditor | security | SEQUENTIAL |

## CONTEXT_DATA Structures (v2.2.0)

### CHECKPOINT
```json
{
  "progress": "Step 3 of 7 complete",
  "intermediate_results": {},
  "pending_actions": ["Run validation", "Generate report"]
}
```

### HANDOFF
```json
{
  "from_agent": "agent-1",
  "to_agent": "agent-2",
  "reason": "Specialist handoff for code review",
  "current_state": "Analysis complete, review pending",
  "instructions": "Review the generated SQL queries"
}
```

### SUMMARY
```json
{
  "session_id": "session-abc123",
  "duration_minutes": 45,
  "entities_created": 5,
  "tasks_completed": 1,
  "key_findings": "Identified 3 optimization opportunities"
}
```

### ERROR_STATE
```json
{
  "error_type": "ConnectionError",
  "error_message": "Failed to connect to embedding API",
  "stack_trace": "...",
  "recovery_hints": ["Check API endpoint", "Retry with backoff"]
}
```

### AUTO_SAVE
```json
{
  "incremental_state": "partial state delta",
  "last_operation": "embedding generation for entity 42",
  "timestamp": "2026-05-22T14:30:00Z"
}
```

## Critical Constraints

- **Database**: PostgreSQL 18 on 10.10.10.131, user=`pgsql`, trust auth, Unix socket at `/tmp`
- **Connection**: When config `host` is `localhost` or empty, connect via Unix socket (`host='/tmp'`), not TCP
- **AGE graph name**: Cannot start with `pg_` (reserved); use `memory_graph`
- **pg_cron**: Installed and configured on 10.10.10.131 (`cron.database_name = 'memory_graph'`). 9 scheduled jobs defined in `3_jobs.sql`.
- **Embedding API**: http://10.10.10.1:12345/v1, model `text-embedding-bge-m3`, 1024 dimensions
- **Python**: 3.14 on local machine (primary); 3.6 on remote server. psycopg2-binary 2.9+ on local, 2.8.6 on remote.
- **Web Visualization**: `./start_web_server.sh start` — runs locally, connects to remote DB. Port 8000. Session auth via system_users table. 7 pages: Knowledge, Memory, Agents, Tasks, Workspaces, Graph Explorer, Login. 14 REST API endpoints.
- **Entity types**: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE — stored in `entities.entity_type`
- **Knowledge category**: Stored in `entities.category`, NOT in `knowledge_meta` (no concept_type column there)
- **Task status mapping**: Python API maps SUCCESS→COMPLETED, IN_PROGRESS→ACTIVE to match schema CHECK constraints
- **Visibility**: PRIVATE (owner only), SHARED (all agents), PUBLIC (unrestricted) — COLLABORATIVE removed in v2.1
- **Edge strength**: 0.0–1.0 (v2.1 normalized from v2.0's 0–2 range); confidence: 0.0–1.0

## PostgreSQL-Specific Features

- **pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)): Custom PostgreSQL 18 extension (by Haiwen Yin) for in-database embedding generation. Uses PG18's `COPY FROM PROGRAM` mechanism + Python proxy to call any OpenAI-compatible `/v1/embeddings` API — no C compilation required. Supports multi-model profiles, auto-dimension detection, batch generation, health checks, cosine similarity, and request logging. Not a built-in database feature; requires separate installation from [GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw).
- **pgvector HNSW**: Hardware-accelerated vector similarity search with `vector_cosine_ops`
- **Apache AGE Cypher**: Graph traversal queries on unified entity graph (`memory_graph`)
- **JSONB**: Native JSON operations with GIN indexing for flexible metadata
- **IDENTITY columns**: Clean auto-increment (`BIGINT GENERATED ALWAYS AS IDENTITY`) without explicit sequences

## Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | BIGINT IDENTITY PKs | Clean auto-increment without sequence management; sufficient for all use cases |
| 2 | No partitioning | PG18 partitioning adds complexity without proportional benefit at expected scale; B-tree indexes sufficient |
| 3 | JSONB for flexible schema | Native JSONB columns + PL/pgSQL provide document-style operations without rigid schema constraints |
| 4 | Apache AGE for graph | AGE provides Cypher query capability on PG18; use `_run_cypher()` wrapper for graph traversal |
| 5 | psycopg2 driver | ThreadedConnectionPool (min=2, max=5) provides 4500x speedup over psql subprocess; well-supported on Python 3.6+; use psycopg2-binary 2.9+ for Python 3.14 |
| 6 | JSONB for context | WORKSPACE_CONTEXT.CONTEXT_DATA uses JSONB for append-only context chain; flexible schemaless storage |
| 7 | Normalized tags | TAGS + ENTITY_TAGS replace JSON tag arrays; indexable, queryable, countable |
| 8 | Simplified visibility | PRIVATE/SHARED/PUBLIC replaces v2.0's PRIVATE/SHARED/COLLABORATIVE; collaboration via AGENT_COLLABORATION table |
| 9 | Edge strength 0-1 | Normalized from v2.0's 0-2 range for consistency with confidence scale |
| 10 | ON DELETE CASCADE | All child FKs use CASCADE for clean workspace/entity deletion; PostgreSQL supports this natively |
| 11 | Local-first Skill | Skill runs locally (Agent side), connects to remote DB via TCP; visualization server runs locally too |
| 12 | Web Visualization | Standard library HTTP server + local vis-network.min.js; no Flask/Django; bilingual (zh/en); session auth via system_users; 5-min auto-logout |
