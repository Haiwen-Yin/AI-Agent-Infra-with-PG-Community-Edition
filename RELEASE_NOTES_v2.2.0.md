# Release Notes - memory-pg18-by-yhw v2.2.0

**Author**: Haiwen Yin (胖头鱼)
**Date**: 2026-05-23
**License**: Apache License 2.0

---

## v2.2.0 — Workspace & Context Continuity

v2.2.0 introduces workspace management, context chain persistence, agent handoff, and web visualization to the PostgreSQL Memory System. This enables agents to operate in isolated execution environments, preserve context across sessions, seamlessly transfer control between agents, and browse/manage all entities through a local web UI.

### Highlights

- **3 new tables**: `workspaces`, `workspace_context`, `workspace_tasks` — workspace lifecycle, append-only context chain, and workspace-task linking
- **Workspace API**: 10 PL/pgSQL functions (`workspace_manager` schema) + 11 Python functions (`workspace_api.py`) for full workspace lifecycle management
- **Context Continuity**: 5 context types (CHECKPOINT, HANDOFF, SUMMARY, ERROR_STATE, AUTO_SAVE) with parent linking for version chains
- **Agent Handoff**: `PREDECESSOR_SESSION_ID` chain in `agent_session` enables seamless context transfer between agents
- **Entity Scoping**: `entities.workspace_id` column enables ISOLATED mode workspaces with strict entity boundaries
- **Web Visualization**: 7 HTML pages + server.py (14 REST endpoints) + local vis-network.min.js for browsing entities via browser; Graph/List dual views, 5-min auto-logout, bilingual UI

### Breaking Changes from v2.1.0

| v2.1 | v2.2 | Impact |
|------|------|--------|
| No workspace concept | WORKSPACES + WORKSPACE_CONTEXT + WORKSPACE_TASKS | New tables, no data migration |
| No agent handoff | PREDECESSOR_SESSION_ID in AGENT_SESSION | New column, backward-compatible |
| No entity-workspace scoping | ENTITIES.WORKSPACE_ID column | New nullable column |
| 7 pg_cron jobs | 9 pg_cron jobs (+2 workspace jobs) | New jobs defined |
| 4 PL/pgSQL schemas | 5 PL/pgSQL schemas (+workspace_manager) | New schema added |

v2.2.0 is **not backward-compatible** with v2.1.0. There is no in-place upgrade path. Deploy into a new database or schema.

### New Features

#### WORKSPACES Table

| Column | Type | Purpose |
|--------|------|---------|
| workspace_id | BIGINT IDENTITY PK | Auto-increment primary key |
| workspace_name | VARCHAR(200) | Human-readable name |
| workspace_type | VARCHAR(32) | CONVERSATION / AUTONOMOUS / PIPELINE |
| isolation_mode | VARCHAR(16) | SHARED / ISOLATED |
| owner_user_id | VARCHAR(64) | Owning user (nullable) |
| current_agent_id | VARCHAR(64) | Currently active agent |
| current_session_id | VARCHAR(128) | Currently active session |
| summary | TEXT | Workspace summary |
| metadata | JSONB | Flexible key-value store |
| status | VARCHAR(32) | ACTIVE / PAUSED / ARCHIVED |

#### WORKSPACE_CONTEXT Table

| Column | Type | Purpose |
|--------|------|---------|
| context_id | BIGINT IDENTITY PK | Auto-increment primary key |
| workspace_id | BIGINT FK | References workspaces |
| agent_id | VARCHAR(64) | Agent that created the context |
| session_id | VARCHAR(128) | Session at time of context |
| context_type | VARCHAR(32) | CHECKPOINT / HANDOFF / SUMMARY / ERROR_STATE / AUTO_SAVE |
| context_data | JSONB | Flexible context payload |
| parent_context_id | BIGINT FK | Parent context for version chain |

#### WORKSPACE_TASKS Table

| Column | Type | Purpose |
|--------|------|---------|
| workspace_id | BIGINT FK | References workspaces |
| plan_id | BIGINT FK | References task_plans |
| assigned_at | TIMESTAMPTZ | Assignment timestamp |

Composite PK: (workspace_id, plan_id)

#### AGENT_SESSION New Columns

| Column | Type | Purpose |
|--------|------|---------|
| owner_user_id | VARCHAR(64) | User who owns the session |
| workspace_id | BIGINT | Workspace the session belongs to |
| predecessor_session_id | VARCHAR(128) | Previous session in handoff chain |

#### workspace_manager PL/pgSQL Schema (10 Functions)

| Function | Returns | Purpose |
|----------|---------|---------|
| create_workspace() | BIGINT | Create a new workspace |
| get_workspace() | JSONB | Get workspace details |
| update_workspace_status() | BOOLEAN | Update workspace lifecycle status |
| delete_workspace() | BOOLEAN | Delete workspace (cascades) |
| add_context_entry() | BIGINT | Add context entry |
| get_context_chain() | TABLE | Get context chain |
| create_handoff() | VARCHAR | Create agent handoff session |
| recover_to_checkpoint() | JSONB | Recover workspace state |
| get_workspace_summary() | JSONB | Get workspace summary |
| cleanup_abandoned() | INT | Archive abandoned workspaces |

#### workspace_api.py (11 Functions)

| Function | Purpose |
|----------|---------|
| create_workspace() | Create workspace with isolation mode |
| get_workspace() | Get workspace details |
| get_user_workspaces() | List workspaces for a user |
| update_workspace() | Update workspace fields |
| save_context() | Save context entry to workspace |
| get_context_chain() | Get workspace context chain |
| get_latest_context() | Get most recent context entry |
| create_handoff_session() | Create agent handoff with context |
| recover_workspace() | Recover full workspace state |
| link_task_to_workspace() | Link task plan to workspace |
| get_workspace_tasks() | List workspace tasks |

#### New Scheduled Jobs

| Job | Schedule | Action |
|-----|----------|--------|
| workspace_cleanup_job | Daily 01:00 | Archive abandoned workspaces (>30 days, no active sessions) |
| stale_workspace_detect_job | Hourly | Pause workspaces inactive >7 days |

### Bug Fixes

- `1_schema.sql`: Fixed `agent_session` missing `workspace_id`, `owner_user_id`, `predecessor_session_id` columns
- `1_schema.sql`: Fixed `entities` missing `workspace_id` column
- `2_api.sql`: Fixed `memory_fusion` functions referencing `name` column (should be `title` in v2.2 schema)
- `2_api.sql`: Fixed `knowledge_api` functions referencing v2.0 columns (`name`, `description`, `priority`)
- `graph_api.py`: Added SQL fallback for `get_neighbors()` when AGE Cypher queries fail
- `server.py`: Fixed auth redirect — use `_get_session()` instead of `_require_auth()` for endpoint handlers
- `server.py`: Fixed `_knowledge_to_vis()` and `_memory_to_vis()` to return full fields + tags via `_get_tags_for_entities()`
- `server.py`: Added `/api/graph/all` endpoint for full graph rendering
- All HTML pages: Fixed sidebar to `position:fixed;height:100vh` with centered logout button, countdown timer, and language toggle
- `graph.html`: Fixed vis.js container height and `setTimeout` recreate pattern for hidden→visible container switch
- `knowledge.html`/`memory.html`: Added Graph/List dual view toggle with list view as default
- `tasks.html`: Fixed JS syntax error (duplicate code block) and added expandable step details + Plan Details panel
- `test_*.py`: Fixed `test_get_nonexistent` — entity_id is BIGINT, not string
- `test_security.py`: Fixed `test_mask_dict` — "safe_key" contains "key" which is sensitive; renamed to "description"
- `test_security.py`: Fixed `test_context_level_analytics` — ANALYTICS doesn't mask email, test CC/SSN instead
- `test_workspace.py`: Fixed `test_create_workspace_with_options` — "PROJECT" is not a valid workspace_type (use "PIPELINE")

### Test Results

```
PostgreSQL Memory System v2.2.0 - Full Test Suite
============================================================
  Connection:  6/6 PASS
  Memory:     16/16 PASS
  Knowledge:  19/19 PASS
  Agent:      17/17 PASS
  Security:   19/19 PASS
  Graph:      12/12 PASS
  Harness:    12/12 PASS
  Workspace:  14/14 PASS
Overall: 115/115 ALL PASSED
```

### File Inventory

| File | Status | Description |
|------|--------|-------------|
| scripts/deploy/1_schema.sql | Updated | 22 tables, 57 indexes, 5 views, AGE graph, seed data |
| scripts/deploy/2_api.sql | Updated | 5 PL/pgSQL schemas, 31+ functions |
| scripts/deploy/3_jobs.sql | Updated | 9 pg_cron jobs |
| scripts/deploy/4_harness_templates.sql | Unchanged | 5 built-in templates |
| scripts/lib/workspace_api.py | New | 11 Python functions for workspace management |
| scripts/lib/graph_api.py | Updated | 9 Python functions for graph traversal + SQL fallback |
| scripts/tests/test_graph.py | Updated | 12 graph tests |
| scripts/tests/test_workspace.py | New | 14 workspace tests |
| scripts/visualization/server.py | New | Web server with 14 REST API endpoints |
| scripts/visualization/templates/*.html | New | 7 HTML pages (knowledge, memory, agents, tasks, workspaces, graph, login) |
| scripts/visualization/static/vis-network.min.js | New | Local vis.js standalone UMD build (702KB) |
| scripts/visualization/static/style.css | New | Dark theme CSS with fixed sidebar |
| start_web_server.sh | New | Daemon control script (start/stop/restart/status/log) |
| SKILL.md | Updated | v2.2.0 with workspace section |
| CHANGELOG.md | Updated | v2.2.0 + v2.1.0 entries |
| docs/workspace.md | New | Workspace & context continuity guide |
| docs/visualization.md | New | Visualization architecture and API docs |
| docs/api-reference.md | Updated | Full Python + PL/pgSQL + REST API reference |
| docs/minimum-privileges.md | New | PG18 minimum database privileges |
| docs/introduction_v2.2.0_zh.md | New | Chinese introduction for v2.2.0 |
| VERSION | Updated | v2.2.0 |
| config.json | Unchanged | Database, server, embedding, security config |

### Database Schema Summary

| Metric | Count |
|--------|-------|
| Tables | 22 |
| Indexes | 57 |
| Views | 5 |
| PL/pgSQL schemas | 5 |
| PL/pgSQL functions | 31+ |
| AGE graphs | 1 (memory_graph) |
| Harness templates | 5 built-in |
| System config rows | 3 seeded |
| pg_cron jobs | 9 defined |

### Upgrade from v2.1.0

v2.2.0 requires a **clean deployment**. There is no in-place upgrade path from v2.1.0.

1. Deploy v2.2.0 schema into a new database (or new schema)
2. Export data from v2.1.0 tables
3. Transform and load into v2.2.0 tables (add `workspace_id`, `owner_user_id`, `predecessor_session_id`)
4. See `docs/migration.md` for detailed mapping

### Compatibility

- **PostgreSQL**: 18+
- **pgvector**: 0.8.2+
- **Apache AGE**: 1.7.0+
- **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)**: v1.0+
- **Python**: 3.6+
- **psycopg2-binary**: 2.8.6+

---

**Release Date**: 2026-05-23
**Author**: Haiwen Yin (胖头鱼)
**License**: Apache License 2.0