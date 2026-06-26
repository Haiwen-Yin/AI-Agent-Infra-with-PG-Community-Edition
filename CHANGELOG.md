## [3.7.4] - 2026-06-26

### Summary

6 expansion directions: Agent Communication Protocol, Multi-Agent Orchestration, Event-Driven Architecture, Advanced Memory Management, Observability, and Tool Ecosystem.

### Added - All Editions

- **Agent Communication Protocol** — COLLAB_MESSAGES table + message_api.py (15 functions): send/reply/broadcast/thread messages with priority levels, attachment references, and unread tracking.
- **Multi-Agent Orchestration** — orchestrator.py: DAG resolution (topological sort), sequential/parallel execution groups, fan-out/fan-in with multiple strategies. STEP_RETRY_POLICY table.
- **Event-Driven Architecture** — EVENT_LOG + EVENT_SUBSCRIPTIONS tables. event_bus.py: publish/subscribe, agent capability discovery, LOOP_HOOKS execution engine.
- **Advanced Memory Management** — consolidate_branch_memories(), promote_to_semantic(), merge_knowledge(), detect_knowledge_conflicts(), reindex_entity().
- **Observability** — Distributed tracing (TRACE_ID on 6 tables). trace_api.py, monitor_api.py. monitor.html dashboard page. 3 PL/pgSQL schemas.
- **Tool Ecosystem** — OpenAPI spec auto-import into harness templates. TOOL_REGISTRY table. TOOL_CHAINS + TOOL_CHAIN_STEPS for tool DAG composition.
- 25 new API endpoints. 3 new pg_cron jobs.

---

## [3.7.3] - 2026-06-23

### Summary

Deployment fix release — resolves schema creation order issues, hardcoded schema owner names, configuration priority, and embedding model auto-detection discovered during fresh deployment testing.

### Fixed - Oracle COM/ENT

- **CONTEXT_BRANCHES FK ordering** — Removed inline FK constraints referencing not-yet-created tables (WORKSPACES, WORKSPACE_CONTEXT, AGENT_REGISTRY); added via ALTER TABLE after parent tables exist
- **LOOP_RUNS self-reference** — Moved UK_LOOP_RUNS_ID UNIQUE(RUN_ID) inline to CREATE TABLE (was added via ALTER TABLE after, causing ORA-02270 on FK_LR_PARENT_RUN self-reference)
- **LOOP_ITERATIONS partitioning** — Changed from PARTITION BY REFERENCE to PARTITION BY RANGE(STARTED_AT) to resolve incompatibility with parent table's composite subpartitioning (ORA-14661)

### Fixed - All Editions

- **Hardcoded schema owner** — 4_grants.sql and 6_deep_sec_policy.sql: replaced literal AIADMIN with `DEFINE SCHEMA_OWNER` substitution variable; connection.py: `ALTER SESSION SET CURRENT_SCHEMA` and `SET_AGENT_CONTEXT` calls now read schema name from config
- **PG RLS policy** — Replaced hardcoded `'aiadmin'` in RLS policies with psql variable `:'schema_owner'`
- **PG agent_bootstrap.py** — Changed `SET search_path TO aiadmin` to `SET search_path TO public`
- **Config priority** — Changed from Environment Variables > config.json > Defaults to config.json (encrypted) > Environment Variables > Defaults; removed hardcoded default credentials (openclaw/hermes/10.10.10.130)
- **EmbeddingConfig defaults** — Changed from hardcoded model/dimension to empty strings, forcing explicit configuration
- **SecurityConfig** — pbkdf2_iterations default 100000 → 210000
- **Embedding model auto-detection** — embedding_api.py now raises ValueError with supported model list when embedding model is not configured, instead of silently using default
- **server.py startup** — Added embedding configuration check with WARNING message on startup

---
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
## [3.7.1] - 2026-06-19

### Summary

**Loop Engineering Collaborative Integration** — Connects Loop Engineering with Spec, Task, Branch, Collab, and Skill modules, enabling Spec-driven loops, Task-Loop bindings, and Collaborative Loops. Also fixes session persistence, PG loop API compatibility, and adds SPEC_VALIDATION and AGGREGATE evaluation types.

### Added - Both Editions

- **Spec-Driven Loop** — Create loops from Spec acceptance criteria; SPEC_VALIDATION evaluation type validates against spec criteria
- **Task-Loop Binding** — Bind loops to task steps; step auto-completes when loop succeeds; new TASK_LOOP_BINDING table
- **Collaborative Loop** — Create parent/child loops for collaboration groups; AGGREGATE evaluation type collects child results; 2-level nesting limit
- **Branch-Isolated Loop** — Loops bound to a branch_id automatically run in branch context
- **Skill-Triggered Loop** — Skills with validation_loop metadata auto-start verification loops on acquire
- LOOP_META new columns: SPEC_ID, PARENT_LOOP_ID, COLLAB_GROUP_ID
- LOOP_RUNS new column: PARENT_RUN_ID
- TASK_STEPS new columns: LOOP_ID, STEP_COMPLETION_TYPE (MANUAL/LOOP/SPEC + WAITING_LOOP status)
- TASK_LOOP_BINDING table (BINDING_ID, STEP_ID, LOOP_ID, BINDING_TYPE, AUTO_START)
- SPEC_VALIDATION evaluation type — validates iteration against spec acceptance_criteria
- AGGREGATE evaluation type — aggregates child loop run results
- 7 new API endpoints: /api/loops/from-spec, /api/loops/collab, /api/loops/{id}/children, /api/loops/{id}/aggregation, /api/tasks/steps/{id}/bind-loop, /api/tasks/steps/{id}/loop, /api/collab/{id}/loop
- 8 new loop_api.py functions: create_loop_from_spec, create_collab_loop, create_sub_loops_for_group, aggregate_child_runs, bind_loop_to_step, get_step_loop, on_loop_run_completed, create_validation_loop_for_skill
- derive_loop_from_spec() in spec_api.py
- bind_loop_to_step(), get_step_loop() in task_plan_api.py
- create_group_loop(), get_group_loop_status() in collab_api.py
- loops.html: From Spec creation, Collab Group selector, Child Loops panel, SPEC_VALIDATION/AGGREGATE badges
- [ENT only] LOOP_AUDIT COLLAB_GROUP_ID column for collaborative audit trail
- [ENT only] log_loop_audit() enhanced with collaborative action types: SUB_LOOP_CREATED, SUB_LOOP_COMPLETED, AGGREGATION_DONE

### Fixed - Both Editions

- **Session persistence** — Added Max-Age=3600 to session cookie; session survives tab switches
- **Session timeout** — Changed from 5-hour (300*60) to 5-minute sliding window using last_access
- **PG loop API compatibility** — Fixed method name mismatches (_api_loop_get → _api_loops_get etc.)
- **PG runs API** — Fixed _api_loops_runs() signature to accept qs parameter
- **Oracle COM loop API imports** — Fixed from scripts.lib.loop_api to from lib.loop_api
- **Oracle COM missing handlers** — Added _api_loops_stats, _api_loops_hooks, _api_loops_run_get methods
- **COM navigation** — Added loops link to Community Edition sidebar
- **Loop detail close button** — Added close button to detail panel header
- **Oracle ENT audit** — Added missing /audit route and /api/audit endpoint
- **PG ENT audit** — Created audit_api.py, audit.html, routes, and endpoints
- **PG authentication** — Fixed user_manager.authenticate() hash comparison with upper()
- **Route order** — /api/loops/{id}/children and /aggregation now match before catch-all /api/loops/{id}
- **Server startup** — Fixed startup script using nohup instead of setsid
- **PG ENT edition label** — Fixed templates showing "Community Edition" instead of "Enterprise Edition"

---
## [3.7.0] - 2026-06-18

### Summary

**Loop Engineering** — Introduces Loop Engineering as the 4th generation AI engineering methodology (after Prompt Engineering, Context Engineering, and Harness Engineering), proposed by Peter Steinberger in June 2026. Adds 4 new tables, LOOP_MANAGER PL/SQL package, loop_api.py Python module, evaluation engine with 4 evaluation types, lifecycle hooks, and 3 scheduler jobs.

### Added - Both Editions

- **Loop Engineering methodology** — The 4th generation AI engineering methodology (after Prompt/Context/Harness Engineering), proposed by Peter Steinberger in June 2026
- 4 new tables: LOOP_META, LOOP_RUNS, LOOP_ITERATIONS, LOOP_HOOKS
- LOOP_MANAGER package/schema with ~22 functions for loop lifecycle management
- loop_api.py Python module with 25 functions including evaluation engine
- 4 evaluation types: TEST (command), DIFF (git diff), LLM_JUDGE (LLM scoring), MANUAL (human review)
- Stop conditions: max_iterations, max_tokens, max_duration_seconds
- Lifecycle hooks: PRE_RUN, POST_ITERATION, ON_STOP, ON_FAIL, ON_TIMEOUT
- 3 new scheduler jobs: LOOP_TRIGGER_JOB, LOOP_STUCK_CHECK_JOB, LOOP_CLEANUP_JOB
- loops.html template with loop management dashboard
- docs/loop-engineering.md documentation
- config.json llm_judge section (disabled by default)
- [ENT only] LOOP_AUDIT table for audit trail

### Changed - Both Editions

- **Test suite** — Community Edition: 121 tests; Enterprise Edition: 151 tests
- **Schema** — COM: 30 → 34 tables, 13 → 14 PL/SQL packages, 13 → 16 scheduler jobs; ENT: 35 → 40 tables, 16 → 17 PL/SQL packages, 17 → 20 scheduler jobs
- **Python modules** — COM: 23 → 24 modules; ENT: 24 → 25 modules

### Fixed - Both Editions

- **Oracle COM loop API imports** — Fixed `from scripts.lib.loop_api` to `from lib.loop_api` causing HTTP 500 on /api/loops endpoints
- **Oracle COM missing handler methods** — Added missing `_api_loops_stats`, `_api_loops_hooks`, `_api_loops_run_get` methods; fixed route-method name mismatches
- **COM navigation** — Added loops link back to Community Edition sidebar (loops is a core feature available in all editions)
- **Loop detail close button** — Added close button to loop detail panel header
- **Oracle ENT audit** — Added missing /audit route and /api/audit endpoint with handler methods
- **Server startup** — Fixed server startup script using `nohup` instead of `setsid` to prevent shell timeout deadlocks
- **Loop seed data** — Added realistic loop definitions with runs, iterations, and hooks to all editions


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
