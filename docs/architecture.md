# Architecture - AI Agent Infra v3.7.0 (2026-06-18) - PG Community Edition

## Unified Entity Model

### ENTITIES

Single table with `ENTITY_TYPE` discriminator, composite PK `(ENTITY_ID, ENTITY_TYPE)`:

- **MEMORY**: Short-term agent memories. Fields: title, content, summary, category, importance, status, visibility, source_agent
- **KNOWLEDGE**: Long-term validated knowledge. Extended by KNOWLEDGE_META for domain, topic, difficulty, spaced review
- **TASK_OUTPUT**: Task execution results
- **EXPERIENCE**: Learned patterns and heuristics
- **HARNESS_TEMPLATE**: Reusable agent execution blueprints. Extended by HARNESS_META for input_schema, output_schema, execution_mode
- **OTHER**: Catch-all for future entity types

### ENTITY_EDGES

Unified directed edge table with composite PK `(EDGE_ID, SOURCE_ID)`:

- **SOURCE_TYPE**: Denormalized ENTITY_TYPE of the source entity (required for composite FK)
- FK: `(SOURCE_ID, SOURCE_TYPE)` references `ENTITIES(ENTITY_ID, ENTITY_TYPE)`
- Edge types: DEPENDS_ON, RELATED_TO, DERIVED_FROM, CAUSES, ENABLES, PREVENTS, SIMILAR_TO, EVOLVED_FROM, CONTRADICTS, SUPPORTS
- METADATA (JSONB) column on edges only

## Composite Primary Keys & Denormalized ENTITY_TYPE

| Table | PK | FK to ENTITIES | Denormalized Column |
|-------|----|----------------|-------------------|
| ENTITIES | (ENTITY_ID, ENTITY_TYPE) | — | — |
| ENTITY_EDGES | (EDGE_ID, SOURCE_ID) | (SOURCE_ID, SOURCE_TYPE) | SOURCE_TYPE |
| KNOWLEDGE_META | (ENTITY_ID, ENTITY_TYPE) | (ENTITY_ID, ENTITY_TYPE) | ENTITY_TYPE |
| ENTITY_EMBEDDINGS | (ENTITY_ID, ENTITY_TYPE) | (ENTITY_ID, ENTITY_TYPE) | ENTITY_TYPE |
| HARNESS_META | (ENTITY_ID, ENTITY_TYPE) | (ENTITY_ID, ENTITY_TYPE) | ENTITY_TYPE |
| ENTITY_TAGS | (ENTITY_ID, ENTITY_TYPE, TAG_ID) | (ENTITY_ID, ENTITY_TYPE) | ENTITY_TYPE |

## Partitioning Architecture

### ENTITIES — LIST by ENTITY_TYPE

```sql
PARTITION BY LIST (ENTITY_TYPE)
  P_MEMORY, P_KNOWLEDGE, P_TASK_OUTPUT, P_EXPERIENCE, P_HARNESS, P_OTHERS
```

Benefits: Queries filtering by ENTITY_TYPE prune to a single partition.

### Reference Partitioned Tables (5 tables)

ENTITY_EDGES, KNOWLEDGE_META, ENTITY_EMBEDDINGS, HARNESS_META, and ENTITY_TAGS inherit their partitioning from the parent ENTITIES table via `PARTITION BY REFERENCE (FK_...)`. This ensures child rows co-locate with their parent entity partition.

### AGENT_SESSION — LIST by IS_ACTIVE

```sql
PARTITION BY LIST (IS_ACTIVE): P_ACTIVE('Y'), P_INACTIVE('N')
```

### TASK_PLANS — LIST by STATUS

```sql
PARTITION BY LIST (STATUS): P_ACTIVE(PENDING/RUNNING/BLOCKED), P_TERMINAL(SUCCESS/FAILED/CANCELLED)
```

TASK_STEPS inherits partitioning via reference to TASK_PLANS.

### Non-Partitioned Tables

AGENT_REGISTRY, AGENT_PERMISSION_LOG, AGENT_COLLABORATION, TASK_CONTEXT_SNAPSHOTS, TASK_TOOL_CALLS, TASK_DEPENDENCIES, TAGS, SYSTEM_CONFIG, SYSTEM_USERS.

## Visibility Model

| Level | Behavior |
|-------|----------|
| PRIVATE | Only owner agent can access |
| SHARED | All registered agents can access |
| PUBLIC | Unrestricted access |

## Property Graph (Apache AGE)

### PG_MEMORY_GRAPH

Single property graph using Apache AGE `cypher()` function:

```sql
SELECT * FROM cypher('pg_memory_graph', $$
  MATCH (a)-[e]->(b)
  WHERE a.entity_id = 'E_001'
  RETURN b.entity_id, b.title, e.edge_type
$$) AS (entity_id VARCHAR, title VARCHAR, edge_type VARCHAR);
```

### Property Graph API (graph_api.py)

9 Python functions using the Apache AGE `cypher()` SQL function:

| Function | Description |
|----------|-------------|
| `get_neighbors(entity_id, direction, edge_type, min_strength, limit)` | Get adjacent entities with direction filtering |
| `get_reachable(entity_id, max_hops, edge_type, limit)` | Multi-hop reachability |
| `get_shortest_path(source_id, target_id, max_hops)` | Shortest path between two entities (up to 6 hops) |
| `find_similar_entities(entity_id, max_hops, limit)` | Find structurally similar entities via graph proximity |
| `get_entity_context(entity_id, depth)` | Full entity context with neighbors grouped by type/edge |
| `get_graph_stats()` | Graph statistics: vertex/edge counts, degree distribution |
| `get_subgraph(entity_ids, include_intermediate)` | Extract subgraph by entity ID list |
| `find_communities(entity_type, min_connections, limit)` | Find highly-connected entity clusters |
| `graph_search(keyword, entity_type, category, min_importance, limit)` | Graph-aware search via AGE cypher |

## ID Generation

All IDs are `VARCHAR(64)`, generated via `encode(gen_random_bytes(16), 'hex')` producing 32-character hex strings. Prefix conventions: `E_` for edges, `SES_` for sessions, `LOG_` for access logs, `COL_` for collaborations, `PLAN_` for plans, `STEP_` for steps, `SNAP_` for snapshots, `CALL_` for tool calls, `DEP_` for dependencies, `HARNESS_` for templates.

## Design Decisions

1. **Composite PKs** enable partition-by-reference and co-location of parent/child rows
2. **Denormalized ENTITY_TYPE** on child tables required for composite FKs and reference partitioning
3. **LIST partitioning** on ENTITIES enables type-based pruning
4. **Normalized tags** (TAGS + ENTITY_TAGS) replace JSONB TAG column for indexable tag queries
5. **TEXT** for CONTENT fields (large text storage)
6. **VECTOR** (pgvector) for embeddings (compatible with BGE-M3 model)
7. **JSONB** for JSON columns (queryable, indexed via GIN)
8. **pgcrypto** for in-database encryption (encrypt_iv/decrypt_iv AES-CBC)
9. **Row Security Policies** for declarative row-level access control
10. **Apache AGE** for property graph queries (cypher function)
11. **pg_cron** for scheduled job execution

## Workspace & Context Continuity

### WORKSPACES Table

Top-level container for grouping entities, sessions, and tasks:

| Column | Type | Description |
|--------|------|-------------|
| WORKSPACE_ID | VARCHAR(64) | PK |
| OWNER_USER_ID | VARCHAR(64) | User who owns the workspace |
| WORKSPACE_NAME | VARCHAR(200) | Human-readable name |
| WORKSPACE_TYPE | VARCHAR(30) | CONVERSATION, PROJECT, ANALYSIS |
| ISOLATION_MODE | VARCHAR(20) | SHARED (default) or ISOLATED |
| CURRENT_AGENT_ID | VARCHAR(64) | Agent currently controlling the workspace |
| CURRENT_SESSION_ID | VARCHAR(64) | Active session in the workspace |
| SUMMARY | VARCHAR(4000) | Current workspace summary |
| METADATA | JSONB | Arbitrary workspace metadata |
| STATUS | VARCHAR(20) | ACTIVE, PAUSED, ARCHIVED |
| CREATED_AT / UPDATED_AT | TIMESTAMP | Lifecycle timestamps |

### WORKSPACE_CONTEXT Table

Version chain of context entries enabling continuity across sessions and agent handoffs:

| Column | Type | Description |
|--------|------|-------------|
| CONTEXT_ID | VARCHAR(64) | PK |
| WORKSPACE_ID | VARCHAR(64) | FK to WORKSPACES |
| AGENT_ID | VARCHAR(64) | Agent that created this context |
| SESSION_ID | VARCHAR(64) | Session during which context was created |
| CONTEXT_TYPE | VARCHAR(30) | SNAPSHOT, CHECKPOINT, HANDOFF, SUMMARY, RECOVERY |
| CONTEXT_DATA | JSONB | Structured context payload |
| PARENT_CONTEXT_ID | VARCHAR(64) | FK to parent context (version chain) |
| VISIBILITY | VARCHAR(16) | PRIVATE/SHARED/PUBLIC (default SHARED) |
| CREATED_AT | TIMESTAMP | Creation timestamp |

### JSON Strategy

- **Native JSONB columns** for storage — queryable, GIN-indexed
- **Views with INSTEAD OF triggers** for document API (replaces Oracle JRD Duality Views)
- **jsonb_set** for partial updates (replaces Oracle JSON_TRANSFORM)

## Row Security Policy Architecture

v3.7.0 uses PostgreSQL Row Security Policies (RLS) for data isolation:

- **25+ Row Security Policies** enforce row-level, column-level, and cell-level access control
- **3 Database Roles**: `admin_data_role` (full access), `agent_data_role` (filtered), `pool_agent_data_role` (minimum)
- **Agent Context**: `current_setting('app.current_agent_id', TRUE)` for per-session agent identification
- **Zero Trust**: No context = no data

| Connection Type | User | Access Method | Data Scope |
|----------------|------|--------------|------------|
| Portal | Restricted user | Direct logon with RLS | Filtered by Row Security Policies |
| Admin | Schema owner | Pool connection | Unrestricted (RLS bypassed) |

## Admin/Agent Separation Architecture

v3.7.0 introduces a mode system that separates Admin Agent from Business Agent:

```
┌──────────────────────────────────────────────────────────┐
│                    Admin Agent (mode=admin)               │
│                                                          │
│  ┌────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │ Web Portal │   │ Schema Owner │   │ Admin Token   │  │
│  │ server.py  │   │ Pool         │   │ Generator     │  │
│  └────────────┘   └──────────────┘   └───────────────┘  │
│        │                  │                  │           │
│        │           RLS User Pool           │           │
│        │           (filtered)              │           │
│        │                  │                  │           │
│        │    ┌─────────────────────────┐     │           │
│        │    │  Admin API Endpoints    │     │           │
│        │    │  /api/admin/agent/*     │     │           │
│        │    └─────────────────────────┘     │           │
│        │                  │                  │           │
└────────│──────────────────│──────────────────│───────────┘
         │                  │   admin_token    │
         │                  │   (out-of-band)  │
         ▼                  ▼                  ▼
┌──────────────────────────────────────────────────────────┐
│                  Business Agent (mode=agent)              │
│                                                          │
│  ┌────────────┐   ┌──────────────┐   ┌───────────────┐  │
│  │ Agent      │   │ RLS User     │   │ agent_config  │  │
│  │ Bootstrap  │──▶│ Pool Only    │   │ .json (enc)   │  │
│  │ CLI        │   │ (filtered)   │   │               │  │
│  └────────────┘   └──────────────┘   └───────────────┘  │
│                                                          │
│  ✗ No schema owner pool    ✗ No Web Portal             │
│  ✓ Row Security Policies always enforced                 │
│  ✓ agent_config.json encrypted at rest                  │
└──────────────────────────────────────────────────────────┘
```

### Mode Comparison

| Component | standalone | admin | agent |
|-----------|-----------|-------|-------|
| Schema owner pool | ✓ | ✓ | ✗ |
| RLS user pool | ✓ | ✓ | ✓ |
| Web Portal | ✓ | ✓ | ✗ |
| agent_config.json | ✗ | ✗ | ✓ (encrypted) |
| Admin API | ✗ | ✓ | ✗ |
| `get_connection()` | Schema owner or RLS user | Schema owner or RLS user | RLS user only |
| `set_agent_context()` | Switches pool | Switches pool | No-op (always RLS user) |
