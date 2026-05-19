# memory-pg18-by-yhw - PostgreSQL AI Database Memory System v2.0.0

**Author**: Haiwen Yin (胖头鱼)
**Version**: v2.0.0 - 2026-05-17
**License**: Apache License 2.0
**Database**: PostgreSQL 18 + pgvector + Apache AGE + [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)

## What's New in v2.0.0

v2.0.0 is a complete rewrite of the memory system, mirroring the architecture of the Oracle version (oracle-memory-by-yhw v2.0.0):

- **Unified Entity Model**: All entity types (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE) in a single `entities` table
- **Unified Edge Model**: All relationships in a single `entity_edges` table
- **psycopg2 Connection Pool**: Replaces psql subprocess calls (20ms/query vs 90s, 4500x faster)
- **4-Phase SQL Deployment**: Ordered schema, API, jobs, and harness template scripts
- **PL/pgSQL API**: 4 schemas with 21 database functions
- **7 Scheduled Jobs**: pg_cron automated maintenance
- **Security Module**: Data masking, reversible encryption, password hashing
- **Harness Template System**: 5 built-in templates with full CRUD, instantiate, derive, validate
- **pg-embedding-gen-by-yhw Integration**: In-database embedding generation via custom PG18 extension
- **Apache AGE Property Graph**: Cypher queries on unified entity graph

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
pip install psycopg2-binary
```

### 3. Run Tests
```bash
cd scripts && python3 -m tests.test_all
# 37 tests, 100% pass rate
```

### 4. Use the API
```python
from scripts.lib.memory_api import create_memory, search_memories
from scripts.lib.knowledge_api import create_concept, create_relationship
from scripts.lib.agent_api import register_agent, create_session
from scripts.lib.harness_api import create_template, instantiate_template

# Memory
mid = create_memory("Meeting Notes", "Discussed v2.0 architecture", category="meeting")

# Knowledge
kid = create_concept("Architecture Pattern", "principle", description="Unified entity model")
create_relationship(mid, kid, "DERIVED_FROM", strength=0.9)

# Agent
register_agent("agent-1", "Research Agent", capabilities=["read", "write"])
sid = create_session("agent-1")

# Harness
tpl = create_template("Analyst", prompt_templates={"system": "You are a {role}..."},
                       tool_sets=["knowledge_tools"], variables={"role": "Analyst"})
config = instantiate_template(tpl, variables={"role": "Data Scientist"})
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
| SHARED | All agents can access (default) |
| COLLABORATIVE | Only agents in `accessible_to` JSONB array |

## Database Schema (18 tables)

| Table | Purpose |
|-------|---------|
| entities | Unified entity store |
| entity_edges | Directed relationships |
| knowledge_meta | Knowledge validation/versioning |
| harness_meta | Template lifecycle |
| entity_embeddings | Vector embeddings |
| agent_registry | Agent identity |
| agent_session | Session tracking |
| entity_access_log | Access audit |
| agent_permission_log | Permission audit |
| agent_collaboration | Cross-agent sharing |
| task_plans | Task definitions |
| task_steps | Plan steps |
| task_context_snapshots | Breakpoint recovery |
| task_tool_calls | Tool audit |
| task_dependencies | Inter-plan deps |
| tags / entity_tags | Tag system |
| system_config | Configuration |
| system_users | User accounts |

## PL/pgSQL API (4 schemas)

- `memory` (3 functions): generate_embedding, add_concept_with_embedding, search_similar
- `memory_fusion` (4 functions): fuse_similar_memories, extract_knowledge_from_memories, decay_old_memories, get_fusion_stats
- `knowledge_api` (5 functions): validate_concept, deprecate_concept, create_concept_version, get_unvalidated, get_concept_lineage
- `agent_perm` (5 functions): check_entity_access, grant_access, revoke_access, cleanup_expired_sessions, process_collaboration_requests
- `session_cleanup` (4 functions): purge_access_logs, purge_inactive_sessions, archive_old_entities, update_tag_counts

## Python API (8 modules, ~2000 lines)

| Module | Functions |
|--------|-----------|
| memory_api | create_memory, get_memory, update_memory, delete_memory, search_memories, get_agent_memories, count_memories |
| knowledge_api | create_concept, get_concept, update_concept, delete_concept, create_relationship, get_relationships, delete_relationship, search_concepts, get_statistics, get_concept_neighbors |
| agent_api | register_agent, get_agent, list_agents, disable_agent, enable_agent, create_session, update_session_context, close_session, get_active_sessions, log_access, get_access_history, request_collaboration, approve_collaboration, reject_collaboration, get_pending_requests |
| task_plan_api | create_task_plan, get_task_plan, get_task_steps, update_step_status, save_snapshot, resume_task, log_tool_call, add_dependency, search_completed_tasks |
| security | DataMaskingService, ReversibleEncryption, hash_password, verify_password |
| harness_api | create_template, get_template, list_templates, update_template, delete_template, resolve_template, instantiate_template, derive_template, validate_template, publish_template, deprecate_template, get_template_lineage |
| config | DatabaseConfig, ServerConfig, EmbeddingConfig, SecurityConfig, Config |
| connection | get_pool, get_connection, close_pool, execute, execute_query, execute_query_one, execute_insert_returning_id, execute_many |

## pg-embedding-gen-by-yhw Extension

This system uses **pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)), a custom PostgreSQL 18 extension developed by Haiwen Yin. It is **not** a built-in database feature — it uses PG18's `COPY FROM PROGRAM` mechanism to call a Python proxy that communicates with any OpenAI-compatible `/v1/embeddings` API endpoint.

### How It Works

```
SQL Function Call
       |
       v
COPY FROM PROGRAM '/usr/local/pgsql/lib/embedding_wrapper.sh --text <base64> --model <id> --api-url <url>'
       |
       v
embedding_wrapper.sh  -->  embedding_proxy.py  -->  HTTP POST /v1/embeddings
       |                                                    |
       v                                                    v
  Parse comma-separated float8[]              Return JSON array (1024 dims)
```

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

### Usage in This System

The `memory` schema wraps pg-embedding-gen-by-yhw functions:

```sql
-- Generate embedding and store with entity
SELECT memory.add_concept_with_embedding('Concept', 'Description', 'category', '{}'::jsonb);

-- Semantic search
SELECT * FROM memory.search_similar('query text', 10);
```

See `references/` for detailed pg-embedding-gen-by-yhw documentation.

## Harness Templates (5 built-in)

| Template | Category | Purpose |
|----------|----------|---------|
| Research Analyst | research | Research and analysis tasks |
| Code Assistant | development | Code generation and development |
| Data Analyst | analytics | Data analysis and reporting |
| Task Planner | orchestration | Task decomposition and planning |
| Security Auditor | security | Security review and compliance |

## Configuration

Edit `config.json`:
```json
{
  "database": {"host": "localhost", "port": 5432, "database": "memory_graph", "user": "pgsql"},
  "server": {"host": "0.0.0.0", "port": 8000},
  "embedding": {"api_url": "http://10.10.10.1:12345/v1/embeddings", "model": "text-embedding-bge-m3", "dimension": 1024},
  "security": {"masking_enabled": true, "pbkdf2_iterations": 100000}
}
```

Environment variables: `MEMORY_DB_HOST`, `MEMORY_DB_PORT`, `MEMORY_DB_NAME`, `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`, `MEMORY_EMBEDDING_API`

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

37 tests across 5 test suites, 100% pass rate:
- Connection: 6 tests
- Memory: 7 tests
- Knowledge: 7 tests
- Agent: 7 tests
- Security: 10 tests

## Directory Structure

```
memory-pg18-by-yhw/
  SKILL.md
  README.md
  CHANGELOG.md
  VERSION
  LICENSE
  NOTICE
  config.json
  scripts/
    deploy/ (4 SQL files)
    lib/ (8 Python modules)
    tests/ (6 test files)
  docs/ (6 documentation files)
  examples/
  references/
```

## Author

**Haiwen Yin (胖头鱼)** - Oracle/PostgreSQL/MySQL ACE Database Expert

## License

Apache License 2.0
