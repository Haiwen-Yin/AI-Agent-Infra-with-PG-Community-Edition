# Migration Guide — v1.x → v2.0 → v2.2.0

## v2.0.0 → v2.2.0 Breaking Changes

### Column Renames & Removals (entities table)

| v2.0 Column | v2.2 Column | Notes |
|-------------|-------------|-------|
| `name` | `title` | Renamed |
| `priority` | `importance` | Renamed; now 1–10 scale (was 1–5) |
| `description` | (removed) | Use `summary` instead |
| `tags` (JSONB) | (removed) | Normalized into `tags` + `entity_tags` tables |
| `metadata` (JSONB) | (removed) | Domain-specific metadata moved to companion tables |
| `accessible_to` (JSONB) | (removed) | COLLABORATIVE visibility removed; use workspaces |

### New Columns (entities table)

| Column | Type | Purpose |
|--------|------|---------|
| `summary` | TEXT | Short description replacing `description` |
| `source_agent` | VARCHAR(64) | Agent that created the entity |
| `retrieval_count` | INT DEFAULT 0 | Access counter |
| `workspace_id` | BIGINT FK | Workspace membership |

### Visibility Change

| v2.0 | v2.2 | Notes |
|------|------|-------|
| `PRIVATE` | `PRIVATE` | Unchanged |
| `SHARED` | `SHARED` | Unchanged |
| `COLLABORATIVE` | `PUBLIC` | Renamed; no per-agent ACL; use workspaces for isolation |

### entity_edges Changes

| Change | Details |
|--------|---------|
| `properties` → `metadata` | Column renamed to JSONB `metadata` |
| New `source_type` column | VARCHAR identifying the source entity type |

### entity_embeddings Change

| Change | Details |
|--------|---------|
| PK: `entity_id` | Now composite PK `(entity_id, entity_type)` |

### knowledge_meta Restructure

v2.2.0 **adds** new columns to knowledge_meta while **retaining** all v2.0 columns. The old columns are not renamed — they coexist:

| New v2.2 Column | Type | Purpose |
|-----------------|------|---------|
| `domain` | VARCHAR | Knowledge domain (e.g., AI, Security, DevOps) |
| `topic` | VARCHAR | Specific topic within domain |
| `difficulty` | VARCHAR | Difficulty level |
| `review_count` | INT | Number of review iterations |
| `last_reviewed` | TIMESTAMPTZ | Timestamp of last review |
| `next_review` | TIMESTAMPTZ | Scheduled next review date |

Retained v2.0 columns: `source_type`, `source_entity_ids`, `validation_status`, `confidence`, `version`, `is_current`, `validated_at`, `deprecated_at`.

### harness_meta Restructure

| v2.0 Column | v2.2 Column | Notes |
|-------------|-------------|-------|
| `template_version` | `input_schema` | JSONB schema for template inputs |
| `template_status` | `output_schema` | JSONB schema for template outputs |
| `variables` | `execution_mode` | VARCHAR execution mode |
| `changelog` | (removed) | |

### New Tables

| Table | Purpose |
|-------|---------|
| `tags` | Normalized tag names (id, name, created_at) |
| `entity_tags` | Many-to-many entity↔tag mapping |
| `workspaces` | Named workspaces for entity isolation |
| `workspace_context` | Context data per workspace |
| `workspace_tasks` | Tasks associated with workspaces |

### agent_session New Columns

| Column | Type | Purpose |
|--------|------|---------|
| `owner_user_id` | VARCHAR(64) | User who owns the session |
| `workspace_id` | BIGINT FK | Workspace context for session |
| `predecessor_session_id` | VARCHAR(128) | Links to previous session |

### New PL/pgSQL Schema

`workspace_manager` — 6 functions for workspace CRUD and task management.

### New Python Modules

- `graph_api.py` — 9 functions for AGE graph operations
- `workspace_api.py` — 11 functions for workspace management

### pg_cron Jobs

7 → 9 jobs (2 new workspace-related scheduled tasks).

### Test Suites

5 → 8 suites (added: test_graph, test_workspace, test_harness).

---

## v1.x → v2.0.0 Migration

## Table Mapping

| v1.x Table | v2.0 Table | Notes |
|------------|------------|-------|
| `knowledge_concepts` | `entities` (entity_type='KNOWLEDGE') + `knowledge_meta` | Core columns in `entities`; domain/topic/difficulty in `knowledge_meta` |
| `knowledge_graph` | `entity_edges` | `source_concept_id` → `source_id`, `target_concept_id` → `target_id` |
| `knowledge_versions` | `knowledge_api.create_concept_version()` | Versions are now separate KNOWLEDGE entities linked by `EVOLVED_FROM` edges |
| `knowledge_tags` | `tags` | Unchanged structure |
| `knowledge_concept_tags` | `entity_tags` | `concept_id` → `entity_id` |
| `knowledge_distillation_log` | (removed) | Use `knowledge_meta.source_type = 'EXTRACTED'` and `memory_fusion.extract_knowledge_from_memories()` |
| `knowledge_search_history` | (removed) | Search analytics no longer persisted |
| `memory.concepts` | `entities` (entity_type='MEMORY') + `entity_embeddings` | Embeddings moved to separate table |
| `memory.relations` | `entity_edges` | Unified edge table |
| `agent_registry` (SERIAL PK) | `agent_registry` (VARCHAR PK) | `agent_id` changed from SERIAL to VARCHAR(64) |
| `agent_memory_access` | `entities.visibility` + workspaces | Visibility columns on entities replace separate ACL table; workspaces provide isolation |
| `agent_session` (SERIAL PK) | `agent_session` (VARCHAR PK) | `session_id` changed from SERIAL to VARCHAR(128) |
| `agent_collaboration` | `agent_collaboration` | Column renames: `source_agent_id` → `sharing_agent`, `target_agent_id` → `receiving_agent`, `memory_id` → `memory_id` (now references `entities`) |

## Column Renames

| v1.x Column | v2.0 Column | Table |
|-------------|-------------|-------|
| `concept_id` | `entity_id` | concepts → entities |
| `concept_name` | `name` | knowledge_concepts → entities |
| `concept_type` | `category` | knowledge_concepts → entities |
| `from_concept_id` | `source_id` | relations → entity_edges |
| `to_concept_id` | `target_id` | relations → entity_edges |
| `relation_type` | `edge_type` | relations → entity_edges |
| `relationship_id` | `edge_id` | knowledge_graph → entity_edges |
| `source_concept_id` | `source_id` | knowledge_graph → entity_edges |
| `target_concept_id` | `target_id` | knowledge_graph → entity_edges |
| `relationship_type` | `edge_type` | knowledge_graph → entity_edges |
| `relationship_strength` | `strength` | knowledge_graph → entity_edges |
| `source_agent_id` | `sharing_agent` | agent_collaboration |
| `target_agent_id` | `receiving_agent` | agent_collaboration |

## Dropped Objects

| Object | Type | Replacement |
|--------|------|-------------|
| `knowledge_concepts` | table | `entities` + `knowledge_meta` |
| `knowledge_graph` | table | `entity_edges` |
| `knowledge_versions` | table | `knowledge_api.create_concept_version()` |
| `knowledge_distillation_log` | table | `memory_fusion.extract_knowledge_from_memories()` |
| `knowledge_search_history` | table | (none) |
| `agent_memory_access` | table | `entities.visibility` + workspaces |
| `memory.concepts` | table | `entities` |
| `memory.relations` | table | `entity_edges` |
| `memory.v_concepts_with_relations` | view | `v_entity_graph` |
| `memory.v_relations_with_names` | view | `v_entity_graph` |
| `v_knowledge_concepts_active` | view | `v_knowledge_entities` |
| `v_knowledge_graph_summary` | view | `knowledge_api.get_unvalidated()` |

## Migration Strategies

### Clean Install (Recommended for new deployments)

```bash
createdb memory_graph
psql -d memory_graph -f scripts/deploy/1_schema.sql
psql -d memory_graph -f scripts/deploy/2_api.sql
psql -d memory_graph -f scripts/deploy/3_jobs.sql
psql -d memory_graph -f scripts/deploy/4_harness_templates.sql
```

### Data Migration (Existing v1.x data)

```sql
-- 1. Migrate knowledge_concepts → entities + knowledge_meta
INSERT INTO entities (entity_id, entity_type, title, summary, content,
                      category, status, importance, source_agent,
                      created_at, updated_at)
SELECT concept_id, 'KNOWLEDGE', concept_name, description, content,
       category,
       CASE WHEN deprecated_at IS NOT NULL THEN 'DEPRECATED'
            WHEN is_current THEN 'ACTIVE' ELSE 'ARCHIVED' END,
       5, source_type,
       created_at, updated_at
FROM knowledge_concepts;

INSERT INTO knowledge_meta (entity_id, domain, topic, difficulty,
                            review_count, last_reviewed, next_review)
SELECT concept_id, source_type,
       CASE WHEN source_memory_ids IS NOT NULL
            THEN source_memory_ids
            ELSE NULL END,
       CASE WHEN confidence >= 0.8 THEN 'advanced'
            WHEN confidence >= 0.5 THEN 'intermediate'
            ELSE 'beginner' END,
       0, validated_at, NULL
FROM knowledge_concepts;

-- 2. Migrate knowledge_graph → entity_edges
INSERT INTO entity_edges (source_id, target_id, edge_type, strength,
                          confidence, source_type, metadata, created_at)
SELECT source_concept_id, target_concept_id, relationship_type,
       relationship_strength, confidence, 'KNOWLEDGE', properties, created_at
FROM knowledge_graph;

-- 3. Migrate memory.concepts → entities (entity_type='MEMORY')
INSERT INTO entities (entity_type, title, summary, category, importance, created_at, updated_at)
SELECT 'MEMORY', name, description, category, 5, created_at, updated_at
FROM memory.concepts;

-- 4. Migrate embeddings (composite PK: entity_id, entity_type)
INSERT INTO entity_embeddings (entity_id, entity_type, embedding)
SELECT c.concept_id, 'MEMORY', c.embedding
FROM memory.concepts c
WHERE c.embedding IS NOT NULL;

-- 5. Migrate JSONB tags → normalized tags + entity_tags
INSERT INTO tags (name)
SELECT DISTINCT jsonb_array_elements_text(tags)
FROM entities
WHERE tags IS NOT NULL
ON CONFLICT (name) DO NOTHING;

INSERT INTO entity_tags (entity_id, tag_id)
SELECT e.entity_id, t.id
FROM entities e, jsonb_array_elements_text(e.tags) AS tag_name
JOIN tags t ON t.name = tag_name
WHERE e.tags IS NOT NULL;

-- 6. Drop old schema
DROP SCHEMA memory CASCADE;
DROP TABLE IF EXISTS knowledge_concepts, knowledge_graph,
                    knowledge_versions, knowledge_distillation_log,
                    knowledge_search_history, agent_memory_access;
```

After migration, re-run Phase 2–4 to install the v2.2 API functions and
scheduled jobs.
