# Architecture — PostgreSQL Memory System v2.2.1

## Overview

The system stores all memory, knowledge, task outputs, experiences, and harness
templates in a single **ENTITIES** table, discriminated by `entity_type`. Edges,
embeddings, and domain-specific metadata live in companion tables. Apache AGE
provides a property-graph layer (`memory_graph`) for Cypher traversal, while
pg-embedding-gen-by-yhw enables in-database vector generation via COPY FROM PROGRAM + Python proxy, callable from SQL without a Python
client.

**Python requirement**: 3.14+ recommended, 3.6+ minimum (verified with psycopg2-binary 2.9.12).

**Database**: PostgreSQL 18.3 with pgvector 0.8.2, Apache AGE 1.7.0, pg_cron 1.6.

## Core Data Model

### Unified Entity Table

| Column             | Purpose                                    |
|--------------------|--------------------------------------------|
| `entity_id`        | BIGINT identity PK                         |
| `entity_type`      | MEMORY / KNOWLEDGE / TASK_OUTPUT / EXPERIENCE / HARNESS_TEMPLATE |
| `title`            | Human-readable label (was `name`)          |
| `content`          | Free-text body                             |
| `summary`          | Short description of entity content        |
| `visibility`       | PRIVATE / SHARED / PUBLIC                  |
| `owned_by_agent`   | Owning agent identifier                    |
| `importance`       | Priority rank 1–10 (was `priority`)        |
| `source_agent`     | Agent that created the entity              |
| `retrieval_count`  | Number of times entity has been accessed   |
| `workspace_id`     | Workspace the entity belongs to (FK)       |

### Companion Tables

| Table              | Role                                           |
|--------------------|------------------------------------------------|
| `entity_edges`     | Directed relationships (source → target) with strength, confidence, `source_type`, and `metadata` (JSONB, was `properties`) |
| `entity_embeddings`| vector(1024) per entity, composite PK `(entity_id, entity_type)`, HNSW-indexed |
| `knowledge_meta`   | Domain/topic/difficulty/review_count/last_reviewed/next_review for KNOWLEDGE entities |
| `harness_meta`     | input_schema/output_schema/execution_mode for HARNESS_TEMPLATE entities |
| `tags`             | Normalized tag names (id, name, created_at)   |
| `entity_tags`      | Many-to-many entity↔tag mapping (replaces JSONB tags column) |
| `workspaces`       | Named workspaces for entity isolation          |
| `workspace_context`| Context data per workspace                     |
| `workspace_tasks`  | Tasks associated with workspaces               |
| `agent_registry`   | Agent identity, capabilities, permission level |
| `agent_session`    | Active sessions with context snapshots, `owner_user_id`, `workspace_id`, `predecessor_session_id` |
| `entity_access_log`| Audit trail of READ/WRITE/DELETE/SHARE events  |

## Visibility Model

- **PRIVATE** — only `owned_by_agent` can access
- **SHARED** — all agents can access (default)
- **PUBLIC** — unrestricted access

Enforced by `agent_perm.check_entity_access()`.

## Apache AGE Property Graph

The `memory_graph` graph is created during schema deployment. Entities and edges
are mirrored into AGE vertices/edges, enabling Cypher queries such as:

```cypher
SELECT * FROM cypher('memory_graph', $$
  MATCH (n)-[r:RELATED_TO]->(m) RETURN n.title, m.title
$$) AS (a agtype, b agtype);
```

## JSONB for Flexible Metadata

The `entity_edges.metadata` column (renamed from `properties`) stores arbitrary
key-value data on edges. For HARNESS_TEMPLATE entities, the `harness_meta` table
holds structured `input_schema`, `output_schema`, and `execution_mode` fields.
Tags are now normalized via the `tags` and `entity_tags` tables rather than a
JSONB column on entities.

## pg-embedding-gen-by-yhw

The custom extension [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) (by Haiwen Yin) uses PostgreSQL 18's `COPY FROM PROGRAM` to call a Python proxy that communicates with any OpenAI-compatible `/v1/embeddings` API. The `memory` schema wraps it:

```sql
SELECT memory.generate_embedding('hello world');  -- returns vector(1024)
SELECT memory.add_concept_with_embedding('name', 'desc', 'cat', '{}');
```

No Python round-trip from the application layer is required — embedding generation happens inside a SQL function. However, the extension itself relies on an external embedding API and a Python proxy process. See the [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) repository for installation and configuration.

## Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Unified ENTITIES table | Single table with `entity_type` discriminator simplifies access control, indexing, and graph traversal across all entity kinds |
| 2 | Entity edges as separate table | Directed, weighted edges with `strength` (0–1), `confidence` (0–1), `source_type`, and `metadata` (JSONB) support richer semantics than a simple adjacency list |
| 3 | In-database embeddings (pg-embedding-gen-by-yhw) | Eliminates app-layer Python round-trips; embedding generation is a SQL function callable from triggers, jobs, and ad-hoc queries; uses COPY FROM PROGRAM + Python proxy under the hood |
| 4 | Three-tier visibility (PRIVATE/SHARED/PUBLIC) | Simplified from COLLABORATIVE; PUBLIC replaces COLLABORATIVE for unrestricted access; workspaces provide isolation instead of per-agent ACL |
| 5 | Normalized tags (tags + entity_tags) | Replaces JSONB tags array for referential integrity, deduplication, and efficient tag-based queries |
| 6 | Workspace isolation | New `workspaces`, `workspace_context`, and `workspace_tasks` tables enable multi-tenant entity grouping and context management |
| 7 | Apache AGE property graph | Enables Cypher traversal for multi-hop relationship queries that would require recursive SQL; AGE graph coexists with relational tables |
| 8 | pg-embedding-gen-by-yhw for vector generation | Custom PG18 extension using COPY FROM PROGRAM + Python proxy; callable as SQL function, avoids app-layer embedding API calls; configurable model endpoint |
| 9 | Local visualization server → remote DB | Skill runs on the agent side; web UI (7 HTML pages + server.py + style.css) connects to remote PostgreSQL via TCP for browsing and managing entities |
| 10 | pg_cron 1.6 for scheduled maintenance | 9 automated jobs (embedding generation, fusion, decay, cleanup, etc.) running inside the database |
