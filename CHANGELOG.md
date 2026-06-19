## [3.7.2] - 2026-06-19

### Fixed — Documentation Consistency

- LOOP_MANAGER function count corrected: ~33 → ~22 (actual package spec count)
- loop_api.py description corrected: "33 functions" → "32 public API functions + private evaluation helpers"
- LOOP_CLEANUP_JOB schedule corrected: "Weekly Sunday 06:00" → "Weekly Sunday 06:00" (matches actual SQL)
- ENTITIES partition count corrected: 7 → 8 (includes SKILL partition)
- Reference-partitioned children count corrected: 6 → 8 (includes SKILL_META, LOOP_META)
- ON_START lifecycle hook added to v3.7.0 entry (was previously omitted)
- loop-engineering.md body text corrected: "four evaluation types" → "six evaluation types"
- RELEASE_NOTES v3.7.0/v3.7.1 bug fixes boundary clarified
- README project structure updated: all Python modules listed, template count corrected
- PG terminology corrected: "PL/SQL" → "PL/pgSQL", "loop_manager schema" → "loop_manager schema" in docs
- PG Community Edition loop table count corrected: "New Tables (4)" → "(5)" including task_loop_binding

## v3.7.1 (2026-06-19)

### New Feature: Loop Engineering Collaborative Integration
- Spec-Driven Loop: create loops from Spec acceptance criteria with SPEC_VALIDATION evaluation
- Task-Loop Binding: bind loops to task steps with auto-completion; task_loop_binding table
- Collaborative Loop: parent/child loops for collaboration groups with AGGREGATE evaluation; 2-level nesting
- Branch-Isolated Loop: loops bound to branch_id run in branch context
- Skill-Triggered Loop: skills with validation_loop metadata auto-start verification loops
- loop_meta new columns: spec_id, parent_loop_id, collab_group_id
- loop_runs new column: parent_run_id
- task_steps new columns: loop_id, step_completion_type (MANUAL/LOOP/SPEC + WAITING_LOOP status)
- task_loop_binding table
- SPEC_VALIDATION and AGGREGATE evaluation types
- 7 new API endpoints: /api/loops/from-spec, /api/loops/collab, /api/loops/{id}/children, /api/loops/{id}/aggregation, /api/tasks/steps/{id}/bind-loop, /api/tasks/steps/{id}/loop, /api/collab/{id}/loop
- 8 new loop_api.py functions + derive_loop_from_spec() + bind_loop_to_step() + create_group_loop()
- loops.html: From Spec creation, Collab Group selector, Child Loops panel
- loop_audit collab_group_id column (ENT only)

### Bug Fixes
- Session persistence: Added Max-Age=3600 to session cookie; sliding 5-min timeout using last_access
- PG loop API: Fixed method name mismatches and _api_loops_runs() signature
- PG ENT audit: Created audit_api.py, audit.html, routes
- PG ENT edition label: Fixed "Community Edition" → "Enterprise Edition"
- PG authentication: Fixed hash comparison with upper()
- Route order: children/aggregation before catch-all
- Server startup: nohup instead of setsid
- Loop detail: ❌ close button on detail panel
- COM navigation: loops link in sidebar


## v3.7.0 (2026-06-18)

### New Feature: Loop Engineering
- Added Loop Engineering as the 4th generation AI engineering methodology
- 4 new tables: LOOP_META, LOOP_RUNS, LOOP_ITERATIONS, LOOP_HOOKS
- loop_manager schema/schema with ~22 functions for loop lifecycle management
- loop_api.py Python module with 25 functions including evaluation engine
- 4 evaluation types: TEST (command), DIFF (git diff), LLM_JUDGE (LLM scoring), MANUAL (human review)
- Stop conditions: max_iterations, max_tokens, max_duration_seconds
- Lifecycle hooks: PRE_RUN, POST_ITERATION, ON_STOP, ON_FAIL, ON_TIMEOUT
- 3 new scheduler jobs: LOOP_TRIGGER_JOB, LOOP_STUCK_CHECK_JOB, LOOP_CLEANUP_JOB
- loops.html template with loop management dashboard
- docs/loop-engineering.md documentation
- config.json llm_judge section (disabled by default)
- [ENT only] LOOP_AUDIT table for audit trail
### Bug Fixes (v3.7.0)

- **COM navigation** — Added loops link to Community Edition sidebar (loops is a core feature)
- **Loop detail close button** — Added ❌ close button to loop detail panel header
- **PG authentication** — Fixed `user_manager.authenticate()` hash comparison by adding `upper()` for case-insensitive matching
- **PG ENT audit** — Created missing audit_api.py, audit.html template, /audit route and /api/audit endpoint
- **Server startup** — Fixed server startup script using `nohup` instead of `setsid` to prevent shell timeout deadlocks
- **Loop seed data** — Added realistic loop definitions with runs, iterations, and hooks to all editions


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
