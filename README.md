# memory-pg18-by-yhw - PostgreSQL AI Database Memory System v2.2.0

**Author**: Haiwen Yin (胖头鱼)
**Version**: v2.2.0 - 2026-05-23
**License**: Apache License 2.0
**Database**: PostgreSQL 18.3 + pgvector 0.8.2 + Apache AGE 1.7.0 + pg_cron 1.6 + [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)

**[中文介绍 (Chinese Introduction)](docs/introduction_v2.2.0_zh.md)**

## What's New in v2.2.0

- **Workspace Management**: 3 new tables, 10 PL/pgSQL functions, 11 Python functions for isolated execution environments, context chains, and agent handoff
- **Web Visualization**: 7 HTML pages + server.py + style.css + local vis-network.min.js for browsing and managing entities via browser
- **115/115 API Tests Passing**: Verified on Python 3.14 (local) + Python 3.6 (remote)
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
# 115 tests, 100% pass rate
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
```

## Architecture

```
ENTITIES (unified) --+-- MEMORY
                     |-- KNOWLEDGE (with KNOWLEDGE_META)
                     |-- TASK_OUTPUT
                     |-- EXPERIENCE
                     +-- HARNESS_TEMPLATE (with HARNESS_META)

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

## Database Schema (22 tables)

| Table | Purpose |
|-------|---------|
| entities | Unified entity store (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE) |
| entity_edges | Directed relationships with strength (0-1) and confidence (0-1) |
| knowledge_meta | Knowledge domain/topic/difficulty/review scheduling |
| harness_meta | Template input/output schemas and execution mode |
| entity_embeddings | Vector embeddings vector(1024) with HNSW index |
| agent_registry | Agent identity and capabilities |
| agent_session | Session tracking with workspace and predecessor links |
| entity_access_log | Access audit trail |
| agent_permission_log | Permission change audit |
| agent_collaboration | Cross-agent sharing |
| task_plans | Task definitions |
| task_steps | Plan steps with status and tool I/O |
| task_context_snapshots | Breakpoint recovery |
| task_tool_calls | Tool call audit |
| task_dependencies | Inter-plan dependency graph |
| tags / entity_tags | Normalized tag system |
| workspaces | Workspace lifecycle and isolation |
| workspace_context | Context version chain (5 types) |
| workspace_tasks | Workspace-task linking |
| system_config | System configuration |
| system_users | User accounts with PBKDF2-SHA256 |

## PL/pgSQL API (5 schemas)

- `memory` (3 functions): generate_embedding, add_concept_with_embedding, search_similar
- `memory_fusion` (4 functions): fuse_similar_memories, extract_knowledge_from_memories, decay_old_memories, get_fusion_stats
- `knowledge_api` (7 functions): validate_concept, deprecate_concept, create_concept_version, get_unvalidated, get_concept_lineage, record_review, get_due_reviews
- `agent_perm` (5 functions): check_entity_access, grant_access, revoke_access, cleanup_expired_sessions, process_collaboration_requests
- `session_cleanup` (4 functions): purge_access_logs, purge_inactive_sessions, archive_old_entities, update_tag_counts
- `workspace_manager` (10 functions): create_workspace, get_workspace, update_workspace_status, delete_workspace, add_context_entry, get_context_chain, create_handoff, recover_to_checkpoint, get_workspace_summary, cleanup_abandoned

## Python API (10 modules)

| Module | Functions | Purpose |
|--------|-----------|---------|
| memory_api | 10 | Memory CRUD, search, tags, count |
| knowledge_api | 13 | Knowledge CRUD, edges, reviews, tags, count |
| agent_api | 14 | Agent registration, sessions, collaboration, access log |
| graph_api | 9 | Graph traversal (AGE Cypher + SQL fallback) |
| workspace_api | 11 | Workspace lifecycle, context chains, handoff |
| task_plan_api | 12 | Plans, steps, dependencies, snapshots, tool calls |
| harness_api | 8 | Template CRUD, instantiation, variable extraction |
| security | 2 | Password hashing and verification |
| config | 1 | Unified configuration with env var overrides |
| connection | 8 | psycopg2 ThreadedConnectionPool management |

## Web Visualization

7 pages served by `scripts/visualization/server.py` on port 8000:

| Page | Route | Features |
|------|-------|----------|
| Knowledge | `/knowledge` | Graph/List dual view, domain-colored nodes, full field display |
| Memory | `/memory` | Graph/List dual view, category-colored nodes, tag display |
| Agents | `/agents` | Registry, active sessions, collaboration requests |
| Tasks | `/tasks` | Status filter, expandable step details, plan info panel |
| Workspaces | `/workspaces` | Context chain timeline, linked tasks |
| Graph Explorer | `/graph` | Full graph on load, search, neighbor networks |
| Login | `/login` | PBKDF2-SHA256 auth, 5-min auto-logout with countdown |

14 REST API endpoints. See [docs/visualization.md](docs/visualization.md) for details.

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

115 tests across 8 test suites, 100% pass rate (Python 3.14 local + Python 3.6 remote):

| Suite | Tests | Coverage |
|-------|-------|----------|
| Connection | 6 | Pool create/get/release/query |
| Memory | 16 | CRUD, search, tags, count |
| Knowledge | 19 | CRUD, edges, reviews, tags, count |
| Agent | 17 | Registration, sessions, collaboration, access |
| Graph | 12 | Neighbors (SQL fallback), paths, context, search |
| Harness | 12 | CRUD, instantiation, variables, count |
| Security | 19 | Masking, encryption, hashing, context levels |
| Workspace | 14 | CRUD, context chains, handoff, recovery, tasks |

## Directory Structure

```
memory-pg18-by-yhw/
  .gitignore
  SKILL.md
  README.md
  CHANGELOG.md
  RELEASE_NOTES_v2.2.0.md
  VERSION
  LICENSE
  NOTICE
  config.json
  start_web_server.sh
  scripts/
    deploy/ (4 SQL files)
    lib/ (10 Python modules)
    tests/ (9 test files)
    visualization/ (server.py, 7 HTML pages, style.css, vis-network.min.js)
  docs/ (9 documentation files)
```

## Author

**Haiwen Yin (胖头鱼)** - PostgreSQL/MySQL ACE Database Expert

## License

Apache License 2.0
