# Changelog

All notable changes to memory-pg18-by-yhw will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.2.1] - 2026-05-24

### Summary

**UI bug fixes: language persistence and text contrast.** Backward-compatible with v2.2.0 — no database or API changes.

### Fixed

- **Language toggle persistence**: Bilingual (zh/en) toggle now saves preference to `localStorage`; language is restored on every page load, persisting across navigation between pages
- **Tasks page text contrast**: Step table cell text and Plan Details values changed to white (`color:#fff`) for readability on dark backgrounds
- **All 7 HTML pages**: Added `localStorage.getItem('lang')` restore on page init and `localStorage.setItem('lang', n)` in `toggleLang()`

### Changed

- **server.py**: Version string updated from 2.2.0 to 2.2.1

---

## [2.2.0] - 2026-05-23

### Summary

**Workspace management, context continuity, agent handoff, web visualization, and comprehensive bug fixes.** Not backward-compatible with v2.1.0 — requires clean deployment.

### Added

- **WORKSPACES table** — Workspace lifecycle (ACTIVE → PAUSED → ARCHIVED), isolation modes (SHARED/ISOLATED), ownership tracking, metadata JSONB
- **WORKSPACE_CONTEXT table** — Version chain of context entries (CHECKPOINT, HANDOFF, SUMMARY, ERROR_STATE, AUTO_SAVE) with PARENT_CONTEXT_ID linking
- **WORKSPACE_TASKS table** — Links task plans to workspaces, composite PK (WORKSPACE_ID, PLAN_ID)
- **AGENT_SESSION: OWNER_USER_ID column** — User who owns/started the session
- **AGENT_SESSION: WORKSPACE_ID column** — Workspace the session belongs to
- **AGENT_SESSION: PREDECESSOR_SESSION_ID column** — Previous session in handoff chain
- **ENTITIES: WORKSPACE_ID column** — Entity scoping for ISOLATED workspaces
- **workspace_api.py** — 11 Python functions: create_workspace, get_workspace, get_user_workspaces, update_workspace, save_context, get_context_chain, get_latest_context, create_handoff_session, recover_workspace, link_task_to_workspace, get_workspace_tasks
- **workspace_manager PL/pgSQL schema** — 10 server-side functions for workspace lifecycle and context management
- **Web Visualization System** — server.py (14 REST endpoints) + 7 HTML pages + style.css + local vis-network.min.js (702KB UMD build)
  - Knowledge page: Graph/List dual view, domain-colored nodes, full field display with tags
  - Memory page: Graph/List dual view, category-colored nodes, full field display with tags
  - Agents page: 3-tab dashboard (registry, sessions, collaborations)
  - Tasks page: expandable step details + plan info panel
  - Workspaces page: context chain timeline + linked tasks
  - Graph Explorer: full graph on page load via `/api/graph/all`, search, neighbor networks
  - Login page: PBKDF2-SHA256 auth, 5-min auto-logout with countdown timer
  - Fixed sidebar: `position:fixed;height:100vh` with centered logout, countdown, language toggle
- **start_web_server.sh** — Daemon control script (start/stop/restart/status/log)
- **graph_api.py: SQL fallback** — `_get_neighbors_sql()` when AGE Cypher queries fail
- **server.py: `/api/graph/all` endpoint** — Full graph rendering without search
- **server.py: `_get_tags_for_entities()`** — JOIN entity_tags with tags table for full tag names
- **knowledge_api: add_knowledge_tags, get_knowledge_tags, remove_knowledge_tag, count_knowledge** — 4 new functions
- **memory_api: add_memory_tags, get_memory_tags, remove_memory_tag** — 3 new functions
- **workspace_cleanup_job** — pg_cron job for workspace maintenance (daily 01:00)
- **stale_workspace_detect_job** — pg_cron job for detecting stale workspaces (hourly)
- **docs/workspace.md** — Workspace & context continuity guide
- **docs/minimum-privileges.md** — PG18 minimum database privileges
- **docs/visualization.md** — Visualization architecture and API docs
- **docs/introduction_v2.2.1_zh.md** — Chinese introduction for v2.2.0 (with visualization section)

### Changed

- **1_schema.sql**: 22 tables (3 new: workspaces, workspace_context, workspace_tasks), 57 indexes, 5 views, AGE graph
- **2_api.sql**: 5 PL/pgSQL schemas (workspace_manager added), 31+ functions; fixed `e.name` → `e.title`
- **3_jobs.sql**: 9 pg_cron jobs (2 new: workspace_cleanup_job, stale_workspace_detect_job)
- **agent_session**: added OWNER_USER_ID, WORKSPACE_ID, PREDECESSOR_SESSION_ID columns
- **entities**: added WORKSPACE_ID column for workspace-scoped entity isolation
- **graph_api.get_neighbors()**: tries AGE Cypher first, falls back to SQL on failure
- **Test suite expanded**: 115 tests (from 63): Connection 6, Memory 16, Knowledge 19, Agent 17, Graph 12, Harness 12, Security 19, Workspace 14

### Fixed

- `2_api.sql`: `memory_fusion` and `knowledge_api` functions referencing `e.name` (should be `e.title` in v2.2 schema)
- `server.py`: Auth redirect — `_get_session()` instead of `_require_auth()` for endpoint handlers
- `server.py`: `_knowledge_to_vis()` / `_memory_to_vis()` returning full fields + tags via `_get_tags_for_entities()`
- All 6 HTML pages: Sidebar `position:fixed;height:100vh` with centered logout, countdown timer, language toggle
- `graph.html`: vis.js container height and `setTimeout(100ms)` recreate pattern for hidden→visible switch
- `knowledge.html` / `memory.html`: Graph/List dual view toggle with list as default
- `tasks.html`: JS syntax error (duplicate code block) removed, expandable step details + Plan Details panel added
- `test_memory.py`, `test_knowledge.py`, `test_harness.py`: `test_get_nonexistent` — entity_id is BIGINT, not string
- `test_security.py`: `test_mask_dict` — "safe_key" contains "key" (sensitive); renamed to "description"
- `test_security.py`: `test_context_level_analytics` — ANALYTICS masks CC/SSN, not email
- `test_workspace.py`: `test_create_workspace_with_options` — "PROJECT" not valid workspace_type (use "PIPELINE")

---

## [2.1.0] - 2026-05-20

### Summary

**Schema evolution with normalized tags, property graph API, column renames, ID strategy, and simplified visibility.** Not backward-compatible with v2.0.0 — requires fresh deployment.

### Added

- **Normalized tag system** — TAGS + ENTITY_TAGS tables replace JSON tag arrays; indexable, queryable, countable
- **graph_api.py: Property Graph API** with Apache AGE Cypher — 9 functions: get_neighbors, get_reachable, get_shortest_path, find_similar_entities, get_entity_context, get_subgraph, graph_search, find_communities, get_graph_stats
- **memory_graph AGE graph** — Unified property graph for Cypher traversal on PG18
- **HARNESS_META: INPUT_SCHEMA/OUTPUT_SCHEMA** — JSON Schema definitions for template inputs and outputs
- **HARNESS_META: EXECUTION_MODE** — SEQUENTIAL/PARALLEL/CONDITIONAL execution modes
- **knowledge_api.record_review()** — Spaced repetition review scheduling
- **knowledge_api.get_due_reviews()** — Get concepts due for review
- **KNOWLEDGE_REVIEW_JOB** — pg_cron job for daily knowledge review scheduling
- **8 graph tests** in test suite (test_graph.py)

### Changed

- **ENTITIES: NAME → TITLE** — Column renamed for clarity
- **ENTITIES: PRIORITY → IMPORTANCE** — Column renamed, range 1-10
- **ENTITIES: TAGS (JSON) removed** — Replaced by TAGS + ENTITY_TAGS normalized tables
- **ENTITIES: METADATA (JSON) removed** — Only retained in ENTITY_EDGES.METADATA
- **ENTITIES: ACCESSIBLE_TO (JSON) removed** — Simplified visibility model
- **ENTITIES: DESCRIPTION removed** — Replaced by SUMMARY (VARCHAR 2000)
- **ENTITIES: New columns** — SUMMARY, SOURCE_AGENT, RETRIEVAL_COUNT, IMPORTANCE
- **ENTITY_EDGES: Added SOURCE_TYPE** — Denormalized for AGE graph and query optimization
- **ENTITY_EDGES: STRENGTH range** — Normalized to 0.0–1.0 (from v2.0's 0–2)
- **Visibility model simplified** — PRIVATE/SHARED/PUBLIC replaces v2.0's PRIVATE/SHARED/COLLABORATIVE; collaboration via AGENT_COLLABORATION table
- **COMPOSITE PK on entity_embeddings** — (ENTITY_ID, ENTITY_TYPE) replaces single ENTITY_ID
- **COMPOSITE PK on entity_tags** — (ENTITY_ID, ENTITY_TYPE, TAG_ID) replaces single ID
- **All PL/pgSQL functions** — Updated for v2.1 schema (column renames, new tables)

### Removed

- **ENTITIES.TAGS column** — Replaced by normalized TAGS + ENTITY_TAGS
- **ENTITIES.METADATA column** — Only in ENTITY_EDGES now
- **ENTITIES.ACCESSIBLE_TO column** — Simplified visibility model
- **ENTITIES.DESCRIPTION column** — Replaced by SUMMARY
- **COLLABORATIVE visibility** — Replaced by PUBLIC; cross-agent sharing via AGENT_COLLABORATION

---

## [2.0.0] - 2026-05-18

### Major Release — Complete Rewrite: Unified Architecture

v2.0.0 is a **complete rewrite** of the system. Every component redesigned from scratch.

### Added

- **Unified Entity Model** — All entity types (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE) in single `entities` table with `entity_type` discriminator
- **Unified Edge Model** — All relationships in single `entity_edges` table with strength and confidence
- **4-Phase SQL Deployment** — Ordered schema, API, jobs, harness template scripts (idempotent)
- **18 Tables** — entities, entity_edges, knowledge_meta, harness_meta, entity_embeddings, agent_registry, agent_session, entity_access_log, agent_permission_log, agent_collaboration, task_plans, task_steps, task_context_snapshots, task_tool_calls, task_dependencies, tags, entity_tags, system_config, system_users
- **53 Indexes** — B-tree, GIN, HNSW (vector), composite
- **5 Views** — v_memory_entities, v_knowledge_entities, v_active_sessions, v_collaboration_status, v_entity_graph
- **PL/pgSQL API** — 4 schemas (memory, memory_fusion, knowledge_api, agent_perm, session_cleanup) with 21 functions
- **7 pg_cron Jobs** — Memory fusion, knowledge extraction, session cleanup, log purge, tag counts, collaboration expiry, entity archiving
- **Python API** — 8 modules (~2000 lines): config, connection, memory_api, knowledge_api, agent_api, task_plan_api, security, harness_api
- **psycopg2 ThreadedConnectionPool** — Replaces psql subprocess (20ms/query vs 90s, 4500x faster)
- **Unix Socket Support** — Automatic when config host is localhost/empty
- **Security Module** — DataMaskingService (email, phone, SSN, credit card, custom patterns), ReversibleEncryption (AES-256-CBC), PBKDF2 password hashing
- **Harness Template System** — 5 built-in templates (Research Analyst, Code Assistant, Data Analyst, Task Planner, Security Auditor) with full CRUD, instantiate, derive, validate, publish, deprecate, lineage
- **Apache AGE Property Graph** — 1 unified `memory_graph` graph (replaces 2 separate v1.x graphs)
- **pg-embedding-gen-by-yhw Integration** — Custom PG18 extension (COPY FROM PROGRAM + Python proxy) for in-database embedding generation; multi-model profiles, auto-dimension detection, health check, batch, validation, cosine similarity, logging
- **Test Suite** — 37 tests across 5 modules (connection, memory, knowledge, agent, security), all passing
- **Documentation** — SKILL.md (211 lines), README.md, 6 topic docs, 4 reference docs

### Changed

- knowledge_concepts + memory concepts → `entities` (entity_type discriminator)
- knowledge_graph + memory relations → `entity_edges`
- psql subprocess → psycopg2 ThreadedConnectionPool
- 4+ independent SQL scripts → 4-phase ordered deployment
- No PL/pgSQL API → 4 schemas with 21 functions
- No scheduled jobs → 7 pg_cron jobs
- No security module → DataMaskingService + ReversibleEncryption
- No harness templates → 5 built-in templates + full CRUD API
- 2 property graphs → 1 unified AGE graph (memory_graph)
- agent_memory_access → entity_access_log (all entity types)
- `generate_embedding()` marked VOLATILE (not STABLE) since it calls external API

### Fixed

- knowledge_api.py: `concept_type` column → `category` in entities table
- agent_api.py: wrong table name references
- task_plan_api.py: column names and status values (SUCCESS→COMPLETED, IN_PROGRESS→ACTIVE)
- test_agent.py: wrong assertions and table names
- 1_schema.sql: `generate_embedding()` STABLE → VOLATILE (calls external API)
- All pg-embedding-gen-by-yhw documentation: corrected from "C extension" / "database-native" to accurate description (COPY FROM PROGRAM + Python proxy)

### Removed

- `knowledge_concepts` table (replaced by entities with entity_type='KNOWLEDGE')
- `knowledge_graph` table (replaced by entity_edges)
- `knowledge_versions` table (replaced by knowledge_meta.version)
- `knowledge_tags` / `knowledge_concept_tags` tables (replaced by tags / entity_tags)
- `knowledge_distillation_log` table (replaced by knowledge_meta.source_type)
- `knowledge_search_history` table (removed)
- `agent_memory_access` table (replaced by entity_access_log)
- All v1.x SQL scripts (replaced by 4-phase deployment)
- psql subprocess approach (replaced by psycopg2)

---

## [1.0.0] - 2026-05-10

### Major Release - Production-Grade Memory System

This is a **major breakthrough for Production AI Agents** - v1.0.0 brings PostgreSQL 18 Memory System to full production, including a complete Knowledge Base system for managing stable knowledge and distilled experiences.

### Added

- **Knowledge Base System** - Complete knowledge management framework
  - `knowledge_concepts` table - Knowledge concepts with embeddings and metadata
  - `knowledge_graph` table - Concept relationships and graph structure
  - `knowledge_versions` table - Version history for all concepts
  - `knowledge_tags` table - Tag taxonomy and classification
  - `knowledge_concept_tags` table - Many-to-many tag relationships
  - `knowledge_distillation_log` table - Experience distillation tracking
  - `knowledge_search_history` table - Query analytics and optimization
  - Views: `v_knowledge_concepts_active`, `v_knowledge_graph_summary`

- **Python Knowledge Base API** - `scripts/knowledge_base_api_pg.py`
  - `create_concept()` - Create knowledge concepts with auto-embedding
  - `search_concepts_by_text()` - Semantic search with vector similarity
  - `get_concept()` / `update_concept()` - Concept CRUD operations
  - `create_relationship()` / `get_related_concepts()` - Graph operations
  - `add_tag_to_concept()` - Tag management
  - `get_statistics()` - System analytics

- **Enhanced pg-embedding-gen-by-yhw Integration**
  - In-database embedding generation via COPY FROM PROGRAM + Python proxy
  - Multi-model profile management
  - Auto-dimension detection, health check, batch generation

### Updated

- SKILL.md - Updated to v1.0.0 with production emphasis
- README.md - Complete rewrite for v1.0.0 release
- CHANGELOG.md - Full version history maintained

### Fixed

- AGE graph creation compatibility issues with PostgreSQL 18
- pgvector index configuration for optimal performance
- Python API connection pooling and error handling
- Embedding generation failure recovery

### Notes

- This release is **battle-tested** and production-ready
- Fully compatible with existing v0.3.3 deployments (additive schema)
- All Multi-Agent Architecture features retained and enhanced

---

## [0.3.3] - 2026-05-07

### Added

- **Multi-Agent Architecture** - Complete framework for managing multiple AI agents
  - Agent Registry (agent_registry) - Centralized agent lifecycle management
  - Memory Access Control (agent_memory_access) - Fine-grained visibility policies
  - Collaboration Framework (agent_collaboration) - Agent-to-agent communication channels
  - Session Management (agent_session) - Active session tracking and monitoring
  - Python API for all multi-agent operations

### Updated

- Enhanced task plan system with session context tracking
- Improved memory access control policies
- Added agent capability discovery system

---

## [0.3.2] - 2026-05-06

### Added

- **Task Plan Persistence System** - Complete task execution tracking
  - `task_plans` table - Core plan management with goals and priorities
  - `task_steps` table - Step execution tracking and results
  - `task_context_snapshots` table - Breakpoint recovery state
  - `task_tool_calls` table - Tool call audit trail
  - `task_dependencies` table - Task dependency graph
  - Python API for task plan creation, update, and resume
  - Auto-snapshot functionality for breakpoint recovery

### Fixed

- Context snapshot JSON handling
- Task step status transitions

---

## [0.3.1] - 2026-05-05

### Added

- **Property Graph Integration** - Apache AGE with Cypher query support
  - Full Cypher query compatibility
  - Graph visualization support
  - Relationship traversal optimization
  - Node/edge property indexing

- **Enhanced Vector Search** - pgvector HNSW indexing
  - Optimized HNSW index configuration
  - Batch embedding generation
  - Similarity search performance tuning

### Fixed

- Vector index rebuild issues
- Cypher query syntax compatibility

---

## [0.3.0] - 2026-05-04

### Added

- **PostgreSQL 18 Support** - Full PostgreSQL 18 compatibility
  - pgvector extension for vector similarity search
  - Apache AGE extension for property graph queries
  - Native JSONB support for flexible metadata
  - HNSW indexing for high-performance vector search

### Updated

- Complete schema redesign for PostgreSQL 18
- Python API updated for psycopg2
- Vector embedding generation integration

---

## Version Summary

| Version | Release Date | Major Features | Status |
|---------|--------------|----------------|--------|
| v2.2.1 | 2026-05-24 | UI fixes: language persistence, text contrast | Current |
| v2.2.0 | 2026-05-23 | Workspace management, web visualization, context continuity, bug fixes | Stable |
| v2.1.0 | 2026-05-20 | Normalized tags, property graph API, column renames, simplified visibility | Stable |
| v2.0.0 | 2026-05-18 | Complete rewrite: unified entities, psycopg2, PL/pgSQL API, harness, security | Stable |
| v1.0.0 | 2026-05-10 | Knowledge Base, Enhanced API, Production-Ready | Stable |
| v0.3.3 | 2026-05-07 | Multi-Agent Architecture | Stable |
| v0.3.2 | 2026-05-06 | Task Plan Persistence | Stable |
| v0.3.1 | 2026-05-05 | Property Graph, Vector Search | Stable |
| v0.3.0 | 2026-05-04 | PostgreSQL 18 Support | Stable |