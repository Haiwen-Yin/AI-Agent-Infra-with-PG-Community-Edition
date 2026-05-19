# Migration Guide — v1.x to v2.0.0

## Table Mapping

| v1.x Table | v2.0 Table | Notes |
|------------|------------|-------|
| `knowledge_concepts` | `entities` (entity_type='KNOWLEDGE') + `knowledge_meta` | Core columns in `entities`; validation/versioning in `knowledge_meta` |
| `knowledge_graph` | `entity_edges` | `source_concept_id` → `source_id`, `target_concept_id` → `target_id` |
| `knowledge_versions` | `knowledge_api.create_concept_version()` | Versions are now separate KNOWLEDGE entities linked by `EVOLVED_FROM` edges |
| `knowledge_tags` | `tags` | Unchanged structure |
| `knowledge_concept_tags` | `entity_tags` | `concept_id` → `entity_id` |
| `knowledge_distillation_log` | (removed) | Use `knowledge_meta.source_type = 'EXTRACTED'` and `memory_fusion.extract_knowledge_from_memories()` |
| `knowledge_search_history` | (removed) | Search analytics no longer persisted |
| `memory.concepts` | `entities` (entity_type='MEMORY') + `entity_embeddings` | Embeddings moved to separate table |
| `memory.relations` | `entity_edges` | Unified edge table |
| `agent_registry` (SERIAL PK) | `agent_registry` (VARCHAR PK) | `agent_id` changed from SERIAL to VARCHAR(64) |
| `agent_memory_access` | `entities.visibility` + `entities.accessible_to` | Visibility columns on entities replace separate ACL table |
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
| `agent_memory_access` | table | `entities.visibility` / `entities.accessible_to` |
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
INSERT INTO entities (entity_id, entity_type, name, description, content,
                      category, status, tags, metadata,
                      created_at, updated_at)
SELECT concept_id, 'KNOWLEDGE', concept_name, description, content,
       category,
       CASE WHEN deprecated_at IS NOT NULL THEN 'DEPRECATED'
            WHEN is_current THEN 'ACTIVE' ELSE 'ARCHIVED' END,
       '[]', metadata,
       created_at, updated_at
FROM knowledge_concepts;

INSERT INTO knowledge_meta (entity_id, source_type, source_entity_ids,
                            validation_status, confidence, version, is_current,
                            validated_at, deprecated_at)
SELECT concept_id, source_type,
       CASE WHEN source_memory_ids IS NOT NULL
            THEN to_jsonb(string_to_array(source_memory_ids, ','))
            ELSE '[]' END,
       validation_status, confidence, version, is_current,
       validated_at, deprecated_at
FROM knowledge_concepts;

-- 2. Migrate knowledge_graph → entity_edges
INSERT INTO entity_edges (source_id, target_id, edge_type, strength,
                          confidence, properties, created_at)
SELECT source_concept_id, target_concept_id, relationship_type,
       relationship_strength, confidence, properties, created_at
FROM knowledge_graph;

-- 3. Migrate memory.concepts → entities (entity_type='MEMORY')
INSERT INTO entities (entity_type, name, description, category, created_at, updated_at)
SELECT 'MEMORY', name, description, category, created_at, updated_at
FROM memory.concepts;

-- 4. Migrate embeddings
INSERT INTO entity_embeddings (entity_id, embedding)
SELECT c.concept_id, c.embedding
FROM memory.concepts c
WHERE c.embedding IS NOT NULL;

-- 5. Drop old schema
DROP SCHEMA memory CASCADE;
DROP TABLE IF EXISTS knowledge_concepts, knowledge_graph,
                    knowledge_versions, knowledge_distillation_log,
                    knowledge_search_history, agent_memory_access;
```

After migration, re-run Phase 2–4 to install the v2.0 API functions and
scheduled jobs.
