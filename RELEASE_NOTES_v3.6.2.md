# Release Notes - AI Agent Infra with PostgreSQL v3.6.2 (2026-06-18) - Community Edition

## v3.6.2 — Bug Fix Release

### Overview

This is a bug fix release addressing 15 issues discovered since v3.6.1, including critical fixes for portal chat, user authentication, graph API, and PG compatibility.

### Schema & Database

| Object | Count |
|--------|-------|
| Tables | 30 |
| Partition sub-tables | 99+ |
| Indexes (B-tree + HNSW + GIN) | 70+ |
| Views | 5 |
| PL/pgSQL base functions | 22 |
| API functions in 13 schemas | 78 |
| PL/Python3u embedding functions | 3 (embedding_generate, embedding_generate_batch, embedding_status) |
| pgcrypto wrappers | 3 (db_crypto.encrypt/decrypt/rotate_key) |
| pg_cron jobs | 13 |
| Row Security Policies | 25+ |

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

### Bug Fixes from v3.6.1

| # | Fix | Impact |
|---|-----|--------|
| 1 | Fixed conn→connection typo in chat handler | Portal chat could not send messages |
| 2 | Fixed uppercase SQL→lowercase for PG compatibility | PG returns lowercase column names by default |
| 3 | Fixed BIGINT .substring errors with String() conversion | BIGINT IDs caused substring TypeError |
| 4 | Fixed user authentication using user_manager.authenticate() with salt | Users could not log in with salted passwords |
| 5 | Fixed workspace owner_user_id using username (not numeric user_id) | Workspaces created with wrong owner reference |
| 6 | Fixed CHAT_MESSAGE context_type constraint | Chat messages rejected by constraint violation |
| 7 | Fixed agent pool assignment for portal registration | Portal users did not get pool agents assigned |
| 8 | Fixed Decimal serialization as float in graph API | Graph API returned Decimal objects that couldn't serialize |
| 9 | Fixed graph stats field names (node_count, edge_count) | Graph stats returned wrong field names |
| 10 | Fixed branch_api.list_branches and graph_api.get_graph_stats missing functions | API endpoints returned 404 |
| 11 | Fixed task_plan_api column mismatches (completed_at, started_at, assigned_agent_id) | Task plan operations failed with column errors |
| 12 | Fixed spec_api spec_plan_links column mismatches (created_at) | Spec plan links operations failed |
| 13 | Fixed portal chat send (_handle_portal_chat_send missing) | Portal chat send endpoint returned 404 |
| 14 | Fixed session switching error handling | Session switching could cause unhandled exceptions |

### Partitioning

- Entity LIST partitioning by entity_type: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE, SPEC, SKILL, OTHER
- agent_session LIST partitioning by is_active
- HNSW vector indexes on entity_embeddings (1024-dim pgvector)
- AGE property graph (ag_catalog)

### Known Limitations

- Apache AGE property graph requires `LOAD 'age'` and `SET search_path = ag_catalog, "$user", public` before use
- pg_cron jobs run in the database server process; no Oracle Scheduler-like external agent execution
- Row Security Policies use `current_setting()` which can be overridden by superusers; ensure proper role assignment
- PL/Python3u is an untrusted language; only superusers can create functions
- pgcrypto encrypt_iv requires bytea key input; key management is handled in Python (connection_crypto.py)

### Website

- https://db4agent.top
