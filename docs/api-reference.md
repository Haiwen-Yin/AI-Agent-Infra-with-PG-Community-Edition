# API Reference - AI Agent Infra v3.10.2 (2026-07-16) - PG Community Edition

## Python API (scripts/lib/)

### memory_api.py

```python
create_memory(title, content, category, importance, summary, source_agent, owned_by_agent, visibility) -> str
get_memory(entity_id) -> dict | None
update_memory(entity_id, **kwargs) -> bool
delete_memory(entity_id) -> bool
search_memories(keyword, category, visibility, owned_by_agent, limit, offset) -> list
get_agent_memories(agent_id, limit) -> list
count_memories(category) -> int
add_memory_tags(entity_id, tag_names) -> int
get_memory_tags(entity_id) -> list
remove_memory_tag(entity_id, tag_id) -> bool
```

### knowledge_api.py

```python
create_knowledge(title, content, domain, topic, difficulty, category, importance, summary, owned_by_agent, visibility) -> str
get_knowledge(entity_id) -> dict | None
update_knowledge(entity_id, **kwargs) -> bool
delete_knowledge(entity_id) -> bool
search_knowledge(domain, topic, keyword, difficulty, limit, offset) -> list
get_due_reviews(limit) -> list
record_review(entity_id) -> bool
add_edge(source_id, source_type, target_id, edge_type, strength, confidence, metadata) -> str
get_edges(entity_id, direction) -> list
count_knowledge(domain) -> int
add_knowledge_tags(entity_id, tag_names) -> int
get_knowledge_tags(entity_id) -> list
remove_knowledge_tag(entity_id, tag_id) -> bool
```

### graph_api.py

```python
get_neighbors(entity_id, direction, edge_type, min_strength, limit) -> list
get_reachable(entity_id, max_hops, edge_type, limit) -> list
get_shortest_path(source_id, target_id, max_hops) -> list | None
find_similar_entities(entity_id, max_hops, limit) -> list
get_entity_context(entity_id, depth) -> dict
get_graph_stats() -> dict
get_subgraph(entity_ids, include_intermediate) -> dict
find_communities(entity_type, min_connections, limit) -> list
graph_search(keyword, entity_type, category, min_importance, limit) -> list
```

All functions use Apache AGE `cypher()` function against `pg_memory_graph`.

### agent_api.py

```python
register_agent(agent_id, agent_name, agent_type, description, capabilities, config) -> str
get_agent(agent_id) -> dict | None
update_agent(agent_id, **kwargs) -> bool
decommission_agent(agent_id) -> bool
heartbeat(agent_id) -> bool
create_session(agent_id, wm_entity_id, context, owner_user_id, workspace_id, predecessor_session_id) -> str
end_session(session_id) -> bool
checkpoint_session(session_id, context_data) -> bool
get_session_chain(session_id, limit) -> list
get_active_sessions(agent_id) -> list
log_access(agent_id, entity_id, access_type, session_id) -> str
get_access_log(entity_id, agent_id, limit) -> list
create_collaboration(source_agent_id, target_agent_id, col_type, entity_id, context, strength) -> str
get_collaborations(agent_id, limit) -> list
```

### task_plan_api.py

```python
create_plan(agent_id, goal, priority, strategy) -> str
get_plan(plan_id) -> dict | None
update_plan(plan_id, **kwargs) -> bool
add_step(plan_id, plan_status, description, step_order, tool_name, tool_input) -> str
update_step(step_id, **kwargs) -> bool
get_plan_steps(plan_id) -> list
add_dependency(source_plan_id, target_plan_id, dep_type) -> str
get_plan_dependencies(plan_id) -> list
log_tool_call(plan_id, step_id, tool_name, tool_input, tool_output, status, duration_ms) -> str
save_snapshot(plan_id, snapshot_type, context_data) -> str
list_plans(agent_id, status, limit) -> list
delete_plan(plan_id) -> bool
```

### harness_api.py

```python
create_harness_template(title, summary, content, category, input_schema, output_schema, execution_mode, importance, owned_by_agent, visibility) -> str
get_harness_template(entity_id) -> dict | None
update_harness_template(entity_id, **kwargs) -> bool
delete_harness_template(entity_id) -> bool
list_harness_templates(category, execution_mode, limit, offset) -> list
get_template_with_variables(entity_id) -> dict | None
instantiate_harness_template(entity_id, variable_values, agent_id) -> str
count_harness_templates(category) -> int
```

### security.py

```python
DataMaskingService(context_level).mask_text(text) -> str
DataMaskingService(context_level).mask_dict(data) -> dict
DataMaskingService(context_level).mask_json(json_string) -> str
hash_password(password, salt, iterations) -> (hash, salt_hex)
verify_password(password, stored_hash, salt_hex, iterations) -> bool
```

### workspace_api.py

```python
create_workspace(owner_user_id, name, workspace_type, isolation_mode, metadata) -> str
get_workspace(workspace_id) -> dict | None
get_user_workspaces(user_id, status) -> list
update_workspace(workspace_id, **kwargs) -> bool
save_context(workspace_id, agent_id, context_type, context_data, session_id, parent_context_id, visibility) -> str
get_context_chain(workspace_id, limit) -> list
get_latest_context(workspace_id) -> dict | None
create_handoff_session(workspace_id, new_agent_id, handoff_data) -> str
recover_workspace(workspace_id) -> dict
link_task_to_workspace(workspace_id, plan_id) -> bool
get_workspace_tasks(workspace_id) -> list
```

## PL/pgSQL API (13 function groups)

### memory_fusion_engine

- `fuse_similar_memories(category, min_similarity, dry_run)` — Merge similar memories
- `extract_knowledge_from_memories(category, min_count)` — Auto-extract knowledge
- `decay_old_memories(days_threshold, decay_factor)` — Reduce IMPORTANCE of old memories
- `get_fusion_stats()` — Fusion statistics as JSONB

### knowledge_base_api

- `schedule_review(entity_id, entity_type)` — Schedule next spaced review
- `record_review(entity_id, entity_type)` — Record review with doubling interval
- `get_due_reviews()` — List pending reviews
- `get_concept_lineage(entity_id, entity_type)` — Ancestor/descendant graph as JSONB

### agent_permission_manager

- `check_entity_access(agent_id, entity_id)` — 'GRANTED'/'DENIED' based on visibility
- `log_access(agent_id, entity_id, access_type, session_id)` — Insert into entity_access_log
- `cleanup_expired_sessions()` — Close sessions inactive >300min

### session_cleanup

- `purge_access_logs(days_to_keep)` — Delete old access logs
- `purge_inactive_sessions(days_to_keep)` — Delete old closed sessions
- `archive_old_entities(days_threshold)` — Archive low-importance memories

## Admin API (v3.7.0)

Admin API endpoints for Admin/Agent Separation Architecture. Only available in `admin` or `standalone` mode.

### POST /api/admin/agent/register

Register a Business Agent with admin token. Returns recovery codes.

**Request:**
```json
{
  "admin_token": "<registration-token>",
  "agent_name": "business-agent-1",
  "capabilities": {"type": "research", "skills": ["search", "memory"]}
}
```

**Response:**
```json
{
  "agent_id": "AGENT_XXX",
  "recovery_codes": ["RC-XXXX-XXXX-XXXX", ...]
}
```

### POST /api/admin/token/generate

Generate a new admin registration token. Requires admin session.

**Response:**
```json
{
  "admin_token": "<new-token>",
  "expires_at": "2026-06-16T13:00:00Z"
}
```

### POST /api/admin/token/rotate

Rotate the admin token. Existing Business Agents must re-register with the new token.

**Response:**
```json
{
  "admin_token": "<rotated-token>",
  "previous_token_invalidated": true
}
```

### POST /api/admin/agent/recover

Recover an agent using a one-time recovery code.

| Field | Required | Description |
|-------|----------|-------------|
| admin_token | Yes | Admin registration token |
| agent_id | Yes | Agent identifier to recover |
| recovery_code | Yes | One-time recovery code (RC-XXXX-XXXX-XXXX) |

Response: `{"agent_id": "...", "recovered": true}`

**Recovery Process:**
1. Verify admin_token + recovery_code
2. Check LAST_SEEN_AT — reject if agent may still be active (< 5 min)
3. Reset agent status to ACTIVE
4. Return recovery confirmation

### GET /api/admin/skill/list

List available skills. Requires admin_token as query parameter.

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| admin_token | query | Yes | Admin registration token |
| type | query | No | Filter by skill type |
| runtime | query | No | Filter by runtime |
| keyword | query | No | Search keyword |

Response: `{"skills": [...]}`

### GET /api/admin/skill/{skill_id}/acquire

Acquire skill content. Requires admin_token as query parameter.

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| skill_id | path | Yes | Skill entity ID |
| admin_token | query | Yes | Admin registration token |
| resource | query | No | Set to 1 to include resource ZIP (base64 encoded) |

### POST /api/admin/skill/create

Create a new skill. Requires admin_token in request body.

| Field | Required | Description |
|-------|----------|-------------|
| admin_token | Yes | Admin registration token |
| title | Yes | Skill title |
| skill_name | Yes | Skill name |
| skill_version | No | Version (default 1.0.0) |
| skill_type | No | Type (default CUSTOM) |
| skill_format | No | Format (default TEXT) |
| text_content | No | SKILL.md content |
| visibility | No | PRIVATE/SHARED/PUBLIC |

### POST /api/admin/skill/update

Update an existing skill. Requires admin_token and skill_id.

### POST /api/admin/skill/delete

Delete a skill. Requires admin_token and skill_id.

### POST /api/admin/skill/upload

Upload resource file for a skill. Requires admin_token, skill_id, filename, and content_base64.

### Admin Token Functions (Python API)

```python
from scripts.lib.agent_api import generate_admin_token, verify_admin_token
from scripts.lib.connection_crypto import (
    encrypt_credential_for_distribution,
    decrypt_credential_from_distribution,
    save_agent_config,
    load_agent_config,
)

token = generate_admin_token()
is_valid = verify_admin_token(token)
encrypted = encrypt_credential_for_distribution(credential_data, admin_token)
decrypted = decrypt_credential_from_distribution(encrypted_credential, salt, admin_token)
save_agent_config(agent_id, credential_data, "/path/to/agent_config.json")
config = load_agent_config("/path/to/agent_config.json")
```
