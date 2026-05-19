# Architecture — PostgreSQL Memory System v2.0.0

## Overview

The system stores all memory, knowledge, task outputs, experiences, and harness
templates in a single **ENTITIES** table, discriminated by `entity_type`. Edges,
embeddings, and domain-specific metadata live in companion tables. Apache AGE
provides a property-graph layer (`memory_graph`) for Cypher traversal, while
pg-embedding-gen-by-yhw enables in-database vector generation via COPY FROM PROGRAM + Python proxy, callable from SQL without a Python
client.

## Core Data Model

### Unified Entity Table

| Column           | Purpose                                    |
|------------------|--------------------------------------------|
| `entity_id`      | BIGINT identity PK                         |
| `entity_type`    | MEMORY / KNOWLEDGE / TASK_OUTPUT / EXPERIENCE / HARNESS_TEMPLATE |
| `name`           | Human-readable label                       |
| `content`        | Free-text body                             |
| `visibility`     | PRIVATE / SHARED / COLLABORATIVE           |
| `owned_by_agent` | Owning agent identifier                    |
| `accessible_to`  | JSONB array of agent_ids (COLLABORATIVE)   |
| `metadata`       | JSONB flexible key-value store             |
| `tags`           | JSONB array of tag names                   |

### Companion Tables

| Table              | Role                                           |
|--------------------|------------------------------------------------|
| `entity_edges`     | Directed relationships (source → target) with strength & confidence |
| `entity_embeddings`| vector(1024) per entity, HNSW-indexed          |
| `knowledge_meta`   | Validation status, versioning, lineage for KNOWLEDGE entities |
| `harness_meta`     | Template version, status, variables for HARNESS_TEMPLATE entities |
| `agent_registry`   | Agent identity, capabilities, permission level |
| `agent_session`    | Active sessions with context snapshots         |
| `entity_access_log`| Audit trail of READ/WRITE/DELETE/SHARE events  |

## Visibility Model

- **PRIVATE** — only `owned_by_agent` can access
- **SHARED** — all agents can access (default)
- **COLLABORATIVE** — `owned_by_agent` + agents listed in `accessible_to`

Enforced by `agent_perm.check_entity_access()`.

## Apache AGE Property Graph

The `memory_graph` graph is created during schema deployment. Entities and edges
are mirrored into AGE vertices/edges, enabling Cypher queries such as:

```cypher
SELECT * FROM cypher('memory_graph', $$
  MATCH (n)-[r:RELATED_TO]->(m) RETURN n.name, m.name
$$) AS (a agtype, b agtype);
```

## JSONB for Flexible Metadata

The `metadata` column stores arbitrary key-value data without schema migration.
For HARNESS_TEMPLATE entities it holds `prompt_templates`, `tool_bindings`,
`guardrails`, `memory_access`, and `evaluation` specs.

## pg-embedding-gen-by-yhw

The custom extension [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) (by Haiwen Yin) uses PostgreSQL 18's `COPY FROM PROGRAM` to call a Python proxy that communicates with any OpenAI-compatible `/v1/embeddings` API. The `memory` schema wraps it:

```sql
SELECT memory.generate_embedding('hello world');  -- returns vector(1024)
SELECT memory.add_concept_with_embedding('name', 'desc', 'cat', '{}');
```

No Python round-trip from the application layer is required — embedding generation happens inside a SQL function. However, the extension itself relies on an external embedding API and a Python proxy process. See `references/` for installation and configuration.

## Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Unified ENTITIES table | Single table with `entity_type` discriminator simplifies access control, indexing, and graph traversal across all entity kinds |
| 2 | Entity edges as separate table | Directed, weighted edges with `strength` (0–2) and `confidence` (0–1) support richer semantics than a simple adjacency list |
| 3 | In-database embeddings (pg-embedding-gen-by-yhw) | Eliminates app-layer Python round-trips; embedding generation is a SQL function callable from triggers, jobs, and ad-hoc queries; uses COPY FROM PROGRAM + Python proxy under the hood |
| 4 | Three-tier visibility (PRIVATE/SHARED/COLLABORATIVE) | Balances simplicity with fine-grained access; COLLABORATIVE uses JSONB `accessible_to` list for per-agent grants without a separate ACL table |
| 5 | Apache AGE property graph | Enables Cypher traversal for multi-hop relationship queries that would require recursive SQL; AGE graph coexists with relational tables |
| 6 | pg-embedding-gen-by-yhw for vector generation | Custom PG18 extension using COPY FROM PROGRAM + Python proxy; callable as SQL function, avoids app-layer embedding API calls; configurable model endpoint |
