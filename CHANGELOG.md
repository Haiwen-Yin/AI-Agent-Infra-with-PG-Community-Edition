# Changelog

All notable changes to AI Agent Infra with PostgreSQL are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---
## [3.6.2] - 2026-06-18

### Summary

Bug fix release with 15 bug fixes, updated schema statistics, and improved PG compatibility.

### Schema & Database

- 30 tables with 99+ partition sub-tables
- 70+ indexes (B-tree + HNSW + GIN)
- 5 views
- 25+ RLS policies
- 22 PL/pgSQL base functions + 78 API functions in 13 schemas
- 3 PL/Python3u embedding functions (embedding_generate, embedding_generate_batch, embedding_status)
- 3 pgcrypto wrappers (db_crypto.encrypt/decrypt/rotate_key)
- 13 pg_cron jobs
- Entity LIST partitioning by entity_type (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE, SPEC, SKILL, OTHER)
- agent_session LIST partitioning by is_active
- HNSW vector indexes on entity_embeddings (1024-dim pgvector)
- AGE property graph (ag_catalog)

### Python API

- 23 modules with 305+ functions
- Full psycopg2 adapter with %s binds
- BIGINT auto-generated IDs (not VARCHAR UUIDs)
- PL/Python3u for in-database embedding generation
- Admin/Agent separation with encrypted credential distribution
- Portal chat with session management and workspace switching
- 5-signal unified search (vector + fulltext + relational + tag + graph)
- Recovery codes (8 RC-XXXX-XXXX-XXXX codes)

### Visualization Portal

- 12 pages: login, portal_login, portal_chat, knowledge, memory, agents, tasks, workspaces, graph, specs, collab, skills, branches
- vis.js graph explorer with 50+ nodes and 32+ edges
- Session-based authentication with SHA256+salt password hashing
- Pool Agent auto-assignment on registration
- Chat workspace switching
- Dark theme, EN/ZH bilingual

### Testing

- 105 tests (matching Oracle COM 105)

### Test Data

- 50 entities, 32 edges, 25 embeddings
- 8 agents (including 5 pool agents)
- 5 workspaces, 3 users, 3 collab groups
- 5 task plans with 12 steps, 10 tags

### Bug Fixes

- Fixed conn→connection typo in chat handler
- Fixed uppercase SQL→lowercase for PG compatibility
- Fixed BIGINT .substring errors with String() conversion
- Fixed user authentication using user_manager.authenticate() with salt
- Fixed workspace owner_user_id using username (not numeric user_id)
- Fixed CHAT_MESSAGE context_type constraint
- Fixed agent pool assignment for portal registration
- Fixed Decimal serialization as float in graph API
- Fixed graph stats field names (node_count, edge_count)
- Fixed branch_api.list_branches and graph_api.get_graph_stats missing functions
- Fixed task_plan_api column mismatches (completed_at, started_at, assigned_agent_id)
- Fixed spec_api spec_plan_links column mismatches (created_at)
- Fixed portal chat send (_handle_portal_chat_send missing)
- Fixed session switching error handling

---
## [3.6.1] - 2026-06-16

### Summary

Initial PostgreSQL Community Edition release — feature-matching Oracle Community Edition v3.6.1, adapted for PostgreSQL 18.3 with psycopg2, pgvector, Apache AGE, pg_cron, PL/Python3u, pgcrypto, and Row Security Policies.

### Added

- **PostgreSQL adaptation** — Full port from Oracle 26ai to PostgreSQL 18.3:
  - `oracledb` → `psycopg2` with `ThreadedConnectionPool`
  - `:name` named binds → `%s` positional binds
  - Oracle PL/SQL → PL/pgSQL + PL/Python3u
  - `DBMS_CRYPTO` → `pgcrypto` (`encrypt_iv`/`decrypt_iv`)
  - `VECTOR_DISTANCE` → `pgvector` `<=>` cosine distance operator
  - Oracle Text `CONTAINS`/`SCORE` → PostgreSQL `ts_vector`/`ts_rank`
  - Oracle SQL/PGQ `GRAPH_TABLE` → Apache AGE `cypher()`
  - Oracle Data Grants → PostgreSQL Row Security Policies (RLS)
  - Oracle Scheduler → `pg_cron` extension
  - Oracle JRD Duality Views → PostgreSQL views with triggers
  - `RAWTOHEX(SYS_GUID())` → `gen_random_uuid()` or `encode(gen_random_bytes(16), 'hex')`
  - Oracle `JSON_OBJECT`/`JSON_ARRAYAGG` → PostgreSQL `jsonb_build_object`/`jsonb_agg`
  - Oracle `SYSTIMESTAMP` → `CURRENT_TIMESTAMP`
  - Oracle `NUMTODSINTERVAL` → PostgreSQL `INTERVAL`
  - Oracle `VARCHAR2` → PostgreSQL `VARCHAR`
  - Oracle `CLOB` → PostgreSQL `TEXT`
  - Oracle `NUMBER` → PostgreSQL `INTEGER`/`NUMERIC`
  - Oracle `RAW` → PostgreSQL `BYTEA`
  - DSN `host:port/service` → separate `host`/`port`/`dbname` connection parameters
  - Master key directory `~/.oracle-infra/` → `~/.pg-infra/`
- **Admin/Agent Separation Architecture** — Mode system (standalone/admin/agent), Admin Token authentication, encrypted credential distribution, Recovery Codes, Agent Recovery, Private Skill Backup, Skill Distribution & Management API
- **Portal User System** — Register/login, chat sessions, agent pool assignment, auto-naming
- **Context Branching** — Fork, merge, abandon, resume branches; conflict detection; lesson extraction
- **Multi-Agent Collaboration** — Collaboration groups integrated with Branches, SDD, Task Plans, and Harness
- **5-Signal Unified Hybrid Search** — Vector, fulltext, relational, tag, graph signal fusion via `unified_sql` single-SQL strategy
- **Encrypted Credentials** — config.json auto-encryption, pgcrypto in-database encryption, master key management
- **Row Security Policies** — 23 RLS policies for row-level access control, zero-trust security model
- **Test suite** — 105 tests across 16 modules
