# Workspace & Context Continuity - PostgreSQL Memory System v2.3.0

## Design Philosophy

v2.2 adopts a layered JSON strategy that balances relational integrity with document convenience:

1. **Native JSONB columns** for storage - `WORKSPACES.METADATA`, `WORKSPACE_CONTEXT.CONTEXT_DATA` use PostgreSQL's native JSONB type. This provides schemaless flexibility while remaining queryable via `->`, `->>`, `jsonb_path_query`, etc.

2. **Structured relational tables** for core operations - WORKSPACES has explicit columns for workspace_name, status, isolation_mode, etc. This enables efficient indexing and constraint enforcement.

3. **JSONB for flexible extensions** - METADATA and CONTEXT_DATA are JSONB to accommodate evolving schema needs without ALTER TABLE.

**Why not everything in JSONB?** Core fields that are queried, filtered, or constrained should be explicit columns. JSONB is reserved for truly schemaless, append-only, or rapidly evolving data (context chains, metadata blobs).

---

## WORKSPACE Lifecycle

```
ACTIVE --pause--> PAUSED --resume--> ACTIVE
   |                  |
   +--archive--> ARCHIVED <--archive--+
```

| Status | Description | Allowed Transitions |
|--------|-------------|-------------------|
| ACTIVE | Workspace is in use, agents can operate | -> PAUSED, -> ARCHIVED |
| PAUSED | Temporarily suspended, no new sessions | -> ACTIVE, -> ARCHIVED |
| ARCHIVED | Read-only, preserved for history | (terminal) |

WORKSPACES tracks the `CURRENT_AGENT_ID` and `CURRENT_SESSION_ID` to identify the active agent and session at any point. When a handoff occurs, these are updated atomically with the new session creation.

---

## CONTEXT_DATA Structure by CONTEXT_TYPE

Each `WORKSPACE_CONTEXT.CONTEXT_DATA` JSONB document follows a structure determined by `CONTEXT_TYPE`:

### SNAPSHOT

Full workspace state at a point in time:

```json
{
  "entity_count": 42,
  "active_tasks": ["plan_123", "plan_456"],
  "recent_entities": ["entity_xxx", "entity_yyy"],
  "session_summary": "Completed data analysis phase",
  "workspace_status": "ACTIVE"
}
```

### CHECKPOINT

Intermediate save during a session:

```json
{
  "progress": "Step 3 of 7 complete",
  "intermediate_results": {},
  "pending_actions": ["Run validation", "Generate report"],
  "timestamp_offset_ms": 145000
}
```

### HANDOFF

Context transferred between agents:

```json
{
  "from_agent": "agent-1",
  "to_agent": "agent-2",
  "reason": "Specialist handoff for code review",
  "current_state": "Analysis complete, review pending",
  "instructions": "Review the generated SQL queries for optimization",
  "artifacts": ["entity_sql_draft", "entity_analysis_report"]
}
```

### SUMMARY

Condensed summary of session activity:

```json
{
  "session_id": "session-agent-1-1234567890",
  "duration_minutes": 45,
  "entities_created": 5,
  "entities_modified": 3,
  "tasks_completed": 1,
  "key_findings": "Identified 3 optimization opportunities"
}
```

### ERROR_STATE

Context when an error occurs:

```json
{
  "error_type": "ValueError",
  "error_message": "Invalid configuration",
  "stack_trace": "Traceback...",
  "recovery_hints": ["Check config.json", "Verify database connection"]
}
```

### AUTO_SAVE

Automatically saved context:

```json
{
  "incremental_state": "partial state delta",
  "last_operation": "INSERT INTO entities",
  "timestamp": "2026-05-20T14:30:00Z"
}
```

---

## Handoff Flow

Agent handoff transfers workspace control from one agent to another while preserving context continuity:

```
Agent-1 (current)                   Agent-2 (new)
     |                                   |
     | 1. create_handoff_session(ws_id)  |
     | --------------------------------> |
     |                                    |
     | 2. New AGENT_SESSION created:      |
     |    PREDECESSOR_SESSION_ID = old     |
     |    WORKSPACE_ID = ws_id            |
     |                                    |
     | 3. HANDOFF context saved:          |
     |    PARENT_CONTEXT_ID = latest ctx  |
     |                                    |
     | 4. WORKSPACES updated:             |
     |    CURRENT_AGENT_ID = agent-2      |
     |    CURRENT_SESSION_ID = new_ses    |
     |                                    |
     |           <-- Agent-2 active -->   |
```

**Steps performed by `create_handoff_session()`:**

1. Retrieve the workspace's current state (latest context, current session)
2. Create a new `AGENT_SESSION` with `PREDECESSOR_SESSION_ID` pointing to the current session
3. Save a `HANDOFF` context entry
4. Update `WORKSPACES` to set `CURRENT_AGENT_ID` and `CURRENT_SESSION_ID` to the new values

**Session chain traversal:** `get_session_chain(session_id)` walks `PREDECESSOR_SESSION_ID` backwards, returning the full history of sessions in the workspace.

---

## Recovery Flow

When a workspace needs to be restored (after crash, pause, or agent loss):

```
recover_workspace(workspace_id)
     |
     +-- Returns workspace metadata
     +-- Returns context chain (latest 5 entries)
     +-- Returns active tasks (PENDING/RUNNING/BLOCKED)
     +-- Returns recent sessions (latest 5)
     +-- Returns recent entities (ISOLATED mode only, latest 10)
```

**Recovery procedure:**

1. Call `recover_workspace()` to get the full recoverable state
2. Inspect the context chain for the latest CHECKPOINT or HANDOFF entry
3. Create a new session with `PREDECESSOR_SESSION_ID` pointing to the last known good session
4. Save a RECOVERY context entry with resume instructions
5. Resume operations from the recovery point

---

## Isolation Modes

| Mode | Behavior | Entity Scoping |
|------|----------|---------------|
| SHARED | Entities are visible across workspaces | `ENTITIES.WORKSPACE_ID` is nullable; queries are not filtered |
| ISOLATED | Entities are scoped to the workspace | `ENTITIES.WORKSPACE_ID` is set; Python API filters by `WORKSPACE_ID` when the workspace has `ISOLATION_MODE = 'ISOLATED'` |

In ISOLATED mode, agents operating in a workspace can only see entities tagged with that `WORKSPACE_ID`. This is enforced at the application layer -- the Python API filters by `WORKSPACE_ID` when the workspace has `ISOLATION_MODE = 'ISOLATED'`.

---

## CONTEXT_DATA JSONB Recommendations

While CONTEXT_DATA is stored as schemaless JSONB, the following patterns are recommended:

### General Guidelines

- Always include a human-readable `description` or `summary` field for debugging
- Use consistent field names across CONTEXT_TYPEs (e.g., `session_id` not `ses_id`)
- Include timestamps as ISO 8601 strings for cross-language compatibility
- Keep CONTEXT_DATA under 32KB to avoid performance issues with large JSONB columns
- Use arrays for ordered collections, objects for keyed lookups

### Versioning

If CONTEXT_DATA schema evolves, include a `_version` field:

```json
{
  "_version": 2,
  "new_field": "value",
  "legacy_field": "deprecated"
}
```

### Nested vs Flat

Prefer flat structures for query performance. Nest only when the sub-document is always read/written atomically:

```json
{
  "progress": "50%",
  "metadata": {
    "tool": "sql_analyzer",
    "version": "1.2"
  }
}
```

The `metadata` sub-object is appropriate because it is always read together. Individual progress fields should be at the top level for `->>` access.
