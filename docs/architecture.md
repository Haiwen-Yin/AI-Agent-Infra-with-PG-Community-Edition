# Architecture - AI Agent Infra v3.7.3 (2026-06-18) - PG Community Edition

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
Admin Agent (mode=admin)
├── Web Portal
├── AIADMIN Connection Pool
└── Admin Token Generator
        │  admin_token (secure)
        ▼
Encrypted Credential Distribution
        │
        ▼
Business Agent (mode=agent)
├── Agent Bootstrap CLI
├── End User Connection Pool
└── agent_config.json (encrypted)
    ✓ Data Grants enforced    ✗ No AIADMIN access
```
Business Agent (mode=agent)
├── Agent Bootstrap CLI
├── End User Connection Pool (RLS-filtered)
└── agent_config.json (encrypted)
    ✓ RLS enforced    ✗ No schema owner access
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
