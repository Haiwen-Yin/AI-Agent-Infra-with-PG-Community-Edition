# memory-pg18-by-yhw - PostgreSQL AI Database Memory System v2.3.1

**Author**: Haiwen Yin (胖头鱼)
**Version**: v2.3.1 - 2026-05-26
**License**: Apache License 2.0
**Database**: PostgreSQL 18.3 + pgvector 0.8.2 + Apache AGE 1.7.0 + pg_cron 1.6 + [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)

**[中文介绍 (Chinese Introduction)](docs/introduction_v2.3.1_zh.md)**

## What's New in v2.3.1

- **Embedding Python API**: embedding_api.py (12 functions) — generate_embedding, store_embedding, store_embedding_vector, get_embedding, delete_embedding, search_similar, search_by_entity_id, search_hybrid, search_multi_type, generate_embeddings_batch, get_embedding_stats, get_model_dimension; uses pgvector cosine distance (<=> operator), %s positional binds, ::vector cast, ILIKE, LIMIT
- **EMBEDDING_GENERATION_JOB**: pg_cron job every 2 hours for MEMORY/KNOWLEDGE entity embedding generation
- **19 New Embedding Tests**: 162/162 API Tests Passing (from 143)
- Leverages existing memory.generate_embedding() PL/pgSQL and pg-embedding-gen-by-yhw extension

## What's New in v2.3.0

- **Spec Driven Development (SDD)**: spec_meta table, spec_plan_links table, spec_api.py (10 functions), SPEC entity type, spec_manager PL/pgSQL schema (6 functions)
- **Agent Elastic Management**: agent_credentials table, DORMANT/POOL agent states, hibernate/wake/pool functions (8 new agent_api functions), dormant_agent_job, credential_cleanup_job
- **Collaboration Groups**: collab_groups table, collab_group_members table, collab_api.py (10 functions), collab_group_manager PL/pgSQL schema (7 functions), auto-created shared/personal workspaces, collab_group_cleanup_job
- **Web Visualization Expanded**: 9 HTML pages (new: Specs, Collab), 16 REST API endpoints
- **162/162 API Tests Passing**: Verified on Python 3.14 (local) + Python 3.6 (remote)

### Previous Releases

- **Language Persistence**: Bilingual (zh/en) toggle now persists across page navigation via `localStorage`
- **UI Text Contrast Fix**: Tasks page step table and Plan Details values now use white text for readability on dark backgrounds

## What's New in v2.2.0

- **Workspace Management**: 3 new tables, 10 PL/pgSQL functions, 11 Python functions for isolated execution environments, context chains, and agent handoff
- **Web Visualization**: 7 HTML pages + server.py + style.css + local vis-network.min.js
- **Visualization REST API**: 14 endpoints including /api/graph/all for full graph rendering
- **graph_api SQL Fallback**: `get_neighbors()` falls back to SQL when AGE Cypher queries fail

## Quick Start

### 1. Deploy Schema
```bash
psql -d memory_graph -f scripts/deploy/1_schema.sql
psql -d memory_graph -f scripts/deploy/2_api.sql
psql -d memory_graph -f scripts/deploy/3_jobs.sql
psql -d memory_graph -f scripts/deploy/4_harness_templates.sql
```

### 2. Install Python Dependencies
```bash
pip install psycopg2-binary   # Python 3.14+ recommended, 3.6+ minimum
```

### 3. Run Tests
```bash
cd /root/memory-pg18-by-yhw
python3.14 -m scripts.tests.test_all
# 162 tests, 100% pass rate
```

### 4. Start Visualization Server (optional)
```bash
./start_web_server.sh start
# http://10.10.10.136:8000 — login: admin / admin123 (dev only)
```

### 5. Use the API
```python
from scripts.lib.memory_api import create_memory, search_memories
from scripts.lib.knowledge_api import create_knowledge, add_edge
from scripts.lib.agent_api import register_agent, create_session
from scripts.lib.harness_api import create_harness_template, instantiate_harness_template
from scripts.lib.spec_api import create_spec, link_spec_to_plan
from scripts.lib.collab_api import create_collab_group, add_group_member

# Memory
mid = create_memory("Meeting Notes", "Discussed v2.0 architecture", category="meeting")

# Knowledge
kid = create_knowledge("Architecture Pattern", domain="architecture", importance=9)
add_edge(mid, 'MEMORY', kid, 'DERIVED_FROM', strength=0.9)

# Agent
register_agent("agent-1", "Research Agent", capabilities=["read", "write"])
sid = create_session("agent-1")

# Harness
tpl = create_harness_template("Analyst", execution_mode="PARALLEL")
config = instantiate_harness_template(tpl, {"role": "Data Scientist"}, "agent-1")

# Spec (SDD) — create_spec(entity_data=dict, spec_meta=dict)
spec_id = create_spec(
    entity_data={"title": "API Design Spec", "content": "...", "visibility": "PUBLIC"},
    spec_meta={"spec_scope": "API", "complexity": "HIGH"},
)
# link_type: DRIVES/VALIDATES/CONSTRAINS/EXTENDS
link_spec_to_plan(spec_id, plan_id, 'DRIVES', 0.9)

# Collaboration Group — sharing_policy: OPEN/MODERATED/RESTRICTED
group_id = create_collab_group("Research Team", "TEAM", "Description", "MODERATED", "agent-1")
# role: LEAD/CONTRIBUTOR/OBSERVER
add_group_member(group_id, "agent-2", role="CONTRIBUTOR")
```

## Architecture

```
ENTITIES (unified) --+-- MEMORY
                     |-- KNOWLEDGE (with KNOWLEDGE_META)
                     |-- TASK_OUTPUT
                     |-- EXPERIENCE
                     |-- HARNESS_TEMPLATE (with HARNESS_META)
                     +-- SPEC (with SPEC_META)

ENTITY_EDGES (unified) -- DEPENDS_ON, RELATED_TO, DERIVED_FROM, CAUSES,
                          ENABLES, PREVENTS, SIMILAR_TO, EVOLVED_FROM,
                          CONTRADICTS, SUPPORTS, DERIVES_FROM, USES_HARNESS

ENTITY_EMBEDDINGS -- vector(1024) via pg-embedding-gen-by-yhw
```

### Visibility Model

| Level | Description |
|-------|-------------|
| PRIVATE | Only the owning agent can access |
| SHARED | All agents can access (default for knowledge) |
| PUBLIC | Unrestricted access |

## Database Schema (27 tables)

| Table | Purpose |
|-------|---------|
| entities | Unified entity store (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE, SPEC) |
| entity_edges | Directed relationships with strength (0-1) and confidence (0-1) |
| knowledge_meta | Knowledge domain/topic/difficulty/review scheduling |
| harness_meta | Template input/output schemas and execution mode |
| entity_embeddings | Vector embeddings vector(1024) with HNSW index |
| agent_registry | Agent identity, capabilities, permissions, elastic states (ACTIVE/DORMANT/POOL) |
| agent_session | Session tracking with workspace and predecessor links |
| agent_credentials | Agent credential store for hibernate/wake lifecycle |
| entity_access_log | Access audit trail |
| agent_permission_log | Permission change audit |
| agent_collaboration | Cross-agent sharing |
| task_plans | Task definitions |
| task_steps | Plan steps with status and tool I/O |
| task_context_snapshots | Breakpoint recovery |
| task_tool_calls | Tool call audit |
| task_dependencies | Inter-plan dependency graph |
| tags / entity_tags | Normalized tag system |
| workspaces | Workspace lifecycle and isolation (incl. COLLAB_GROUP, PERSONAL_IN_GROUP types) |
| workspace_context | Context version chain (5 types) |
| workspace_tasks | Workspace-task linking |
| system_config | System configuration |
| system_users | User accounts with PBKDF2-SHA256 |
| spec_meta | Spec metadata (SDD: Spec Driven Development) |
| spec_plan_links | Spec-to-plan linking for SDD |
| collab_groups | Collaboration group definitions |
| collab_group_members | Collaboration group membership |

## PL/pgSQL API (7 schemas)

- `memory` (3 functions): generate_embedding, add_concept_with_embedding, search_similar
- `memory_fusion` (4 functions): fuse_similar_memories, extract_knowledge_from_memories, decay_old_memories, get_fusion_stats
- `knowledge_api` (7 functions): validate_concept, deprecate_concept, create_concept_version, get_unvalidated, get_concept_lineage, record_review, get_due_reviews
- `agent_perm` (5 functions): check_entity_access, grant_access, revoke_access, cleanup_expired_sessions, process_collaboration_requests
- `session_cleanup` (4 functions): purge_access_logs, purge_inactive_sessions, archive_old_entities, update_tag_counts
- `workspace_manager` (10 functions): create_workspace, get_workspace, update_workspace_status, delete_workspace, add_context_entry, get_context_chain, create_handoff, recover_to_checkpoint, get_workspace_summary, cleanup_abandoned
- `spec_manager` (6 functions): create_spec, get_spec, update_spec_status, link_spec_to_plan, get_spec_plans, cleanup_orphaned_specs
- `collab_group_manager` (7 functions): create_collab_group, get_collab_group, add_member, remove_member, get_group_members, get_agent_groups, cleanup_empty_groups

## Python API (13 modules)

| Module | Functions | Purpose |
|--------|-----------|---------|
| memory_api | 10 | Memory CRUD, search, tags, count |
| knowledge_api | 13 | Knowledge CRUD, edges, reviews, tags, count |
| agent_api | 22 | Agent registration, sessions, collaboration, access log, hibernate/wake/pool |
| graph_api | 9 | Graph traversal (AGE Cypher + SQL fallback) |
| workspace_api | 11 | Workspace lifecycle, context chains, handoff |
| task_plan_api | 12 | Plans, steps, dependencies, snapshots, tool calls |
| harness_api | 8 | Template CRUD, instantiation, variable extraction |
| spec_api | 10 | Spec CRUD, plan linking, status management (SDD) |
| collab_api | 10 | Collaboration group CRUD, membership, shared workspaces |
| embedding_api | 12 | Embedding generation, storage, search, batch, stats (pgvector + pg-embedding-gen-by-yhw) |
| security | 2 | Password hashing and verification |
| config | 1 | Unified configuration with env var overrides |
| connection | 8 | psycopg2 ThreadedConnectionPool management |

## Web Visualization

9 pages served by `scripts/visualization/server.py` on port 8000:

| Page | Route | Features |
|------|-------|----------|
| Knowledge | `/knowledge` | Graph/List dual view, domain-colored nodes, inline detail expansion |
| Memory | `/memory` | Graph/List dual view, category-colored nodes, inline detail expansion |
| Agents | `/agents` | Registry, active sessions, collaboration requests |
| Tasks | `/tasks` | Status filter, expandable step details, plan info panel |
| Workspaces | `/workspaces` | Context chain timeline, linked tasks, expandable details with close button |
| Graph Explorer | `/graph` | Full graph on load, search, neighbor networks, detail panel with close |
| Specs | `/specs` | Spec list + detail dual tab, acceptance criteria/constraints JSON display |
| Collab | `/collab` | Group list + detail dual tab, member table, sharing policy display |
| Login | `/login` | PBKDF2-SHA256 auth, 5-min auto-logout with countdown |

16 REST API endpoints. See [docs/visualization.md](docs/visualization.md) for details.

## pg-embedding-gen-by-yhw Extension

This system uses **pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)), a custom PostgreSQL 18 extension developed by Haiwen Yin. It is **not** a built-in database feature — it uses PG18's `COPY FROM PROGRAM` mechanism to call a Python proxy that communicates with any OpenAI-compatible `/v1/embeddings` API endpoint.

### Key Features

| Feature | Description |
|---------|-------------|
| Multi-model profiles | Register multiple models via `embedding_register_model()` |
| Auto-dimension detection | Vector dimensions detected on first use and cached |
| Three call modes | Default profile, named profile, or inline (model_id + api_url) |
| Shell-safe | Base64-encoded input prevents injection |
| Auto-retry | Exponential backoff on transient failures |
| Health check | `embedding_health_check()` for API connectivity testing |
| Batch generation | `embedding_generate_batch()` for bulk processing |
| Cosine similarity | `embedding_cosine_similarity()` for in-DB vector comparison |

### Installation

```bash
# From the pg-embedding-gen-by-yhw project directory
sudo bash scripts/install.sh
psql -d memory_graph -f sql/install.sql

# Register your model (if not using defaults)
psql -d memory_graph -c "SELECT embedding_register_model('bge-m3', 'http://10.10.10.1:12345/v1/embeddings', 'text-embedding-bge-m3', true);"

# Verify
psql -d memory_graph -c "SELECT * FROM embedding_health_check();"
```

See the [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) repository for installation and configuration.

## Harness Templates (5 built-in)

| Template | Category | Execution Mode |
|----------|----------|---------------|
| Research Analyst | research | SEQUENTIAL |
| Code Assistant | development | SEQUENTIAL |
| Data Analyst | analytics | PARALLEL |
| Task Planner | orchestration | CONDITIONAL |
| Security Auditor | security | SEQUENTIAL |

## Configuration

Edit `config.json`:
```json
{
  "database": {"host": "10.10.10.131", "port": 5432, "database": "memory_graph", "user": "pgsql"},
  "server": {"host": "0.0.0.0", "port": 8000, "session_timeout": 300},
  "embedding": {"api_url": "http://10.10.10.1:12345/v1/embeddings", "model": "text-embedding-bge-m3", "dimension": 1024},
  "security": {"masking_enabled": true, "pbkdf2_iterations": 100000}
}
```

Environment variables: `MEMORY_DB_HOST`, `MEMORY_DB_PORT`, `MEMORY_DB_NAME`, `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`, `MEMORY_SERVER_HOST`, `MEMORY_SERVER_PORT`, `MEMORY_SESSION_TIMEOUT`

## v1.x to v2.0 Migration

| v1.x | v2.0 |
|------|------|
| knowledge_concepts | entities (entity_type='KNOWLEDGE') |
| knowledge_graph | entity_edges |
| knowledge_versions | knowledge_meta.version |
| knowledge_tags + knowledge_concept_tags | tags + entity_tags |
| knowledge_distillation_log | (dropped, use memory_fusion) |
| knowledge_search_history | (dropped) |
| agent_memory_access | entity_access_log |
| concepts (memory schema) | entities (entity_type='MEMORY') |
| relations (memory schema) | entity_edges |
| 4 independent SQL scripts | 4-phase ordered deployment |
| psql subprocess | psycopg2 connection pool |

## Testing

115 tests across 8 test suites → 162 tests across 12 test suites, 100% pass rate (Python 3.14 local + Python 3.6 remote):

| Suite | Tests | Coverage |
|-------|-------|----------|
| Connection | 6 | Pool create/get/release/query |
| Memory | 16 | CRUD, search, tags, count |
| Knowledge | 19 | CRUD, edges, reviews, tags, count |
| Agent | 22 | Registration, sessions, collaboration, access, hibernate/wake/pool |
| Graph | 12 | Neighbors (SQL fallback), paths, context, search |
| Harness | 12 | CRUD, instantiation, variables, count |
| Security | 19 | Masking, encryption, hashing, context levels |
| Workspace | 14 | CRUD, context chains, handoff, recovery, tasks |
| Spec | 10 | CRUD, plan linking, status management |
| Collab | 10 | Group CRUD, membership, shared workspaces |
| Embedding | 19 | Generate, store, search, batch, stats, hybrid, multi-type |
| Task Plan | 4 | Plans, steps, dependencies |

## Directory Structure

```
memory-pg18-by-yhw/
  .gitignore
  SKILL.md
  README.md
  CHANGELOG.md
  RELEASE_NOTES_v2.2.0.md
  RELEASE_NOTES_v2.2.1.md
  RELEASE_NOTES_v2.3.0.md
  VERSION
  LICENSE
  NOTICE
  config.json
  start_web_server.sh
  scripts/
    deploy/ (4 SQL files)
    lib/ (13 Python modules)
    tests/ (13 test files)
    visualization/ (server.py, 9 HTML pages, style.css, vis-network.min.js)
  docs/ (10 documentation files)
```

## Author

**Haiwen Yin (胖头鱼)** - PostgreSQL/MySQL ACE Database Expert

## License

Apache License 2.0
