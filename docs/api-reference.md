# API Reference — PostgreSQL Memory System v2.0.0

## Python API

All modules live under `scripts/lib/` and use a shared connection pool
(`scripts/lib/connection.py`).

### memory_api — 7 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_memory` | `(name, content, category='general', priority=2, tags=None, metadata=None, owned_by_agent=None, visibility='SHARED', accessible_to=None)` | `entity_id` |
| `get_memory` | `(entity_id)` | `dict or None` |
| `update_memory` | `(entity_id, **kwargs)` | `bool` |
| `delete_memory` | `(entity_id)` | `bool` |
| `search_memories` | `(keyword=None, category=None, visibility=None, owned_by_agent=None, limit=100, offset=0)` | `list[dict]` |
| `get_agent_memories` | `(agent_id, limit=100)` | `list[dict]` |
| `count_memories` | `(category=None)` | `int` |

### knowledge_api — 10 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_concept` | `(name, concept_type, description=None, category=None, content=None, source_type='MANUAL', source_entity_ids=None, confidence=0.8, tags=None, metadata=None, owned_by_agent=None, visibility='SHARED')` | `entity_id` |
| `get_concept` | `(entity_id)` | `dict or None` |
| `update_concept` | `(entity_id, **kwargs)` | `bool` |
| `delete_concept` | `(entity_id)` | `bool` |
| `create_relationship` | `(source_id, target_id, edge_type, strength=1.0, confidence=0.8, properties=None)` | `edge_id` |
| `get_relationships` | `(entity_id, direction='both')` | `list[dict]` |
| `delete_relationship` | `(edge_id)` | `bool` |
| `search_concepts` | `(keyword=None, concept_type=None, category=None, validation_status=None, limit=100)` | `list[dict]` |
| `get_statistics` | `()` | `dict` |
| `get_concept_neighbors` | `(entity_id, max_depth=2)` | `list[dict]` |

### agent_api — 14 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `register_agent` | `(agent_id, agent_name, agent_type='general', capabilities=None, description='', permission_level='READ_WRITE')` | `bool` |
| `get_agent` | `(agent_id)` | `dict or None` |
| `list_agents` | `(agent_type=None, status='ACTIVE')` | `list[dict]` |
| `disable_agent` | `(agent_id, reason='')` | `bool` |
| `enable_agent` | `(agent_id)` | `bool` |
| `create_session` | `(agent_id, working_memory_id=None)` | `session_id or None` |
| `update_session_context` | `(session_id, context)` | `bool` |
| `close_session` | `(session_id)` | `bool` |
| `get_active_sessions` | `(agent_id=None)` | `list[dict]` |
| `log_access` | `(agent_id, entity_id, access_type='READ')` | `None` |
| `get_access_history` | `(agent_id, limit=50)` | `list[dict]` |
| `request_collaboration` | `(sharing_agent, receiving_agent, entity_id, reason='')` | `collab_id or None` |
| `approve_collaboration` | `(collab_id)` | `bool` |
| `reject_collaboration` | `(collab_id)` | `bool` |

### task_plan_api — 9 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_task_plan` | `(plan_name, plan_type='task', description=None, goal=None, priority=2, steps=None, metadata=None, tags=None)` | `plan_id` |
| `get_task_plan` | `(plan_id)` | `dict or None` |
| `get_task_steps` | `(plan_id)` | `list[dict]` |
| `update_step_status` | `(plan_id, step_id, status, result=None, error_msg=None)` | `bool` |
| `save_snapshot` | `(plan_id, context, snapshot_type='MANUAL')` | `snapshot_id` |
| `resume_task` | `(plan_id)` | `dict or None` |
| `log_tool_call` | `(plan_id, tool_name, action, step_id=None, status='SUCCESS', result_size=None, duration_ms=None)` | `call_id` |
| `add_dependency` | `(source_plan_id, target_plan_id, dependency_type='HARD', condition=None)` | `dependency_id` |
| `search_completed_tasks` | `(plan_type=None, status=None, limit=50)` | `list[dict]` |

### security — 4 items

| Item | Type | Description |
|------|------|-------------|
| `DataMaskingService` | class | Context-aware PII masking (7 patterns, 4 context levels) |
| `ReversibleEncryption` | class | PBKDF2 + XOR encryption with key rotation |
| `hash_password(password, salt, iterations)` | function | PBKDF2 password hashing, returns `(hash_hex, salt_hex)` |
| `verify_password(password, stored_hash, salt_hex, iterations)` | function | Constant-time password verification |

### harness_api — 12 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_template` | `(name, description=None, prompt_templates=None, tool_bindings=None, tool_sets=None, memory_access=None, guardrails=None, guardrail_preset=None, evaluation=None, variables=None, category=None, tags=None, metadata=None, owned_by_agent=None, visibility='SHARED', parent_template_id=None)` | `entity_id` |
| `get_template` | `(entity_id)` | `dict or None` |
| `list_templates` | `(category=None, status=None, limit=100)` | `list[dict]` |
| `update_template` | `(entity_id, **kwargs)` | `bool` |
| `delete_template` | `(entity_id)` | `bool` |
| `resolve_template` | `(entity_id)` | `dict or None` — merges parent chain |
| `instantiate_template` | `(template_id, variables=None, overrides=None, agent_id=None)` | `dict or None` — variable substitution applied |
| `derive_template` | `(parent_id, name, description=None, overrides=None, category=None, owned_by_agent=None, visibility='SHARED')` | `entity_id` |
| `validate_template` | `(entity_id)` | `dict` with `valid`, `errors`, `warnings` |
| `publish_template` | `(entity_id)` | `bool` |
| `deprecate_template` | `(entity_id, reason=None)` | `bool` |
| `get_template_lineage` | `(entity_id)` | `list[dict]` |

---

## PL/pgSQL API

### Schema: `memory`

| Function | Signature |
|----------|-----------|
| `memory.generate_embedding` | `(p_text TEXT) → vector(1024)` |
| `memory.add_concept_with_embedding` | `(p_name VARCHAR, p_description TEXT, p_category VARCHAR, p_metadata JSONB) → BIGINT` |
| `memory.search_similar` | `(p_query TEXT, p_limit INT DEFAULT 10) → TABLE(entity_id BIGINT, name VARCHAR, category VARCHAR, similarity FLOAT)` |

### Schema: `memory_fusion`

| Function | Signature |
|----------|-----------|
| `memory_fusion.fuse_similar_memories` | `(p_category TEXT DEFAULT NULL, p_min_similarity NUMERIC DEFAULT 0.85, p_dry_run BOOLEAN DEFAULT TRUE) → TABLE(source_id BIGINT, target_id BIGINT, similarity NUMERIC, action TEXT)` |
| `memory_fusion.extract_knowledge_from_memories` | `(p_category TEXT DEFAULT NULL, p_min_count INT DEFAULT 3) → TABLE(category TEXT, memory_count INT, knowledge_entity_id BIGINT)` |
| `memory_fusion.decay_old_memories` | `(p_days_threshold INT DEFAULT 90, p_decay_factor NUMERIC DEFAULT 0.5) → INT` |
| `memory_fusion.get_fusion_stats` | `() → JSONB` |

### Schema: `knowledge_api`

| Function | Signature |
|----------|-----------|
| `knowledge_api.validate_concept` | `(p_entity_id BIGINT, p_validator TEXT DEFAULT 'SYSTEM') → BOOLEAN` |
| `knowledge_api.deprecate_concept` | `(p_entity_id BIGINT, p_reason TEXT DEFAULT NULL) → BOOLEAN` |
| `knowledge_api.create_concept_version` | `(p_entity_id BIGINT, p_new_content TEXT) → BIGINT` |
| `knowledge_api.get_unvalidated` | `() → TABLE(entity_id BIGINT, name VARCHAR, category VARCHAR, validation_status VARCHAR, confidence NUMERIC, version INT)` |
| `knowledge_api.get_concept_lineage` | `(p_entity_id BIGINT) → JSONB` |

### Schema: `agent_perm`

| Function | Signature |
|----------|-----------|
| `agent_perm.check_entity_access` | `(p_agent_id VARCHAR, p_entity_id BIGINT, p_access_type VARCHAR) → TEXT` |
| `agent_perm.grant_access` | `(p_agent_id VARCHAR, p_entity_id BIGINT, p_granted_by VARCHAR) → BOOLEAN` |
| `agent_perm.revoke_access` | `(p_agent_id VARCHAR, p_entity_id BIGINT) → BOOLEAN` |
| `agent_perm.cleanup_expired_sessions` | `() → INT` |
| `agent_perm.process_collaboration_requests` | `() → INT` |

### Schema: `session_cleanup`

| Function | Signature |
|----------|-----------|
| `session_cleanup.purge_access_logs` | `(p_days_to_keep INT DEFAULT 90) → INT` |
| `session_cleanup.purge_inactive_sessions` | `(p_days_to_keep INT DEFAULT 30) → INT` |
| `session_cleanup.archive_old_entities` | `(p_days_threshold INT DEFAULT 180) → INT` |
| `session_cleanup.update_tag_counts` | `() → INT` |
