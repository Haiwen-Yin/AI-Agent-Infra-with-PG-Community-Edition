# API Reference — PostgreSQL Memory System v2.3.0

**Python requirement**: 3.14+ recommended, 3.6+ minimum. Verified with `psycopg2-binary` 2.9.12.

## Python API

All modules live under `scripts/lib/` and use a shared connection pool
(`scripts/lib/connection.py`).

### memory_api — 10 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_memory` | `(title, content, category='general', importance=5, tags=None, owned_by_agent=None, visibility='PRIVATE', source_agent=None, workspace_id=None)` | `entity_id` |
| `get_memory` | `(entity_id)` | `dict or None` |
| `update_memory` | `(entity_id, **kwargs)` | `bool` |
| `delete_memory` | `(entity_id)` | `bool` |
| `search_memories` | `(keyword=None, category=None, visibility=None, owned_by_agent=None, workspace_id=None, limit=100, offset=0)` | `list[dict]` |
| `get_agent_memories` | `(agent_id, limit=100)` | `list[dict]` |
| `count_memories` | `(category=None)` | `int` |
| `add_memory_tags` | `(entity_id, tag_names)` | `int` |
| `get_memory_tags` | `(entity_id)` | `list[str]` |
| `remove_memory_tag` | `(entity_id, tag_name)` | `bool` |

### knowledge_api — 13 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_knowledge` | `(title, content=None, summary=None, category=None, domain=None, topic=None, difficulty=None, importance=5, tags=None, owned_by_agent=None, visibility='SHARED', source_type='MANUAL', source_entity_ids=None, confidence=0.8, workspace_id=None)` | `entity_id` |
| `get_knowledge` | `(entity_id)` | `dict or None` |
| `update_knowledge` | `(entity_id, **kwargs)` | `bool` |
| `delete_knowledge` | `(entity_id)` | `bool` |
| `search_knowledge` | `(keyword=None, domain=None, category=None, validation_status=None, limit=100, offset=0)` | `list[dict]` |
| `get_due_reviews` | `(limit=50)` | `list[dict]` |
| `record_review` | `(entity_id)` | `bool` |
| `add_edge` | `(source_id, target_id, edge_type, strength=1.0, confidence=0.8, source_type=None, metadata=None)` | `edge_id` |
| `get_edges` | `(entity_id, direction='both')` | `list[dict]` |
| `add_knowledge_tags` | `(entity_id, tag_names)` | `int` |
| `get_knowledge_tags` | `(entity_id)` | `list[str]` |
| `remove_knowledge_tag` | `(entity_id, tag_name)` | `bool` |
| `count_knowledge` | `(domain=None)` | `int` |

### agent_api — 14 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `register_agent` | `(agent_id, agent_name, agent_type='general', capabilities=None, description='', permission_level='READ_WRITE')` | `bool` |
| `get_agent` | `(agent_id)` | `dict or None` |
| `update_agent` | `(agent_id, **kwargs)` | `bool` |
| `decommission_agent` | `(agent_id, reason='')` | `bool` |
| `heartbeat` | `(agent_id)` | `bool` |
| `create_session` | `(agent_id, owner_user_id=None, workspace_id=None, predecessor_session_id=None)` | `session_id or None` |
| `end_session` | `(session_id)` | `bool` |
| `checkpoint_session` | `(session_id)` | `bool` |
| `get_session_chain` | `(session_id)` | `list[dict]` |
| `get_active_sessions` | `(agent_id=None)` | `list[dict]` |
| `log_access` | `(agent_id, entity_id, access_type='READ')` | `None` |
| `get_access_log` | `(agent_id, limit=50)` | `list[dict]` |
| `create_collaboration` | `(sharing_agent, receiving_agent, entity_id, reason='')` | `collab_id or None` |
| `get_collaborations` | `(agent_id=None, status=None, limit=50)` | `list[dict]` |

### graph_api — 9 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `get_neighbors` | `(entity_id, max_hops=2, entity_type=None, direction='both')` | `list[dict]` |
| `get_reachable` | `(entity_id, max_hops=3, entity_type=None)` | `list[dict]` |
| `get_shortest_path` | `(from_entity_id, to_entity_id)` | `list[dict]` |
| `find_similar_entities` | `(entity_id, limit=10)` | `list[dict]` |
| `get_entity_context` | `(entity_id, max_hops=2)` | `dict` |
| `get_graph_stats` | `()` | `dict` |
| `get_subgraph` | `(entity_ids)` | `dict` |
| `find_communities` | `(entity_type=None, min_size=3)` | `list[list[int]]` |
| `graph_search` | `(keyword=None, entity_type=None, category=None, min_importance=1, limit=50)` | `list[dict]` |

### workspace_api — 11 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_workspace` | `(name, workspace_type='CONVERSATION', isolation_mode='SHARED', owner_user_id=None)` | `workspace_id` |
| `get_workspace` | `(workspace_id)` | `dict or None` |
| `get_user_workspaces` | `(owner_user_id=None, limit=100)` | `list[dict]` |
| `update_workspace` | `(workspace_id, **kwargs)` | `bool` |
| `save_context` | `(workspace_id, agent_id, context_type, context_data, session_id=None)` | `context_id` |
| `get_context_chain` | `(workspace_id, limit=10)` | `list[dict]` |
| `get_latest_context` | `(workspace_id)` | `dict or None` |
| `create_handoff_session` | `(workspace_id, new_agent_id, handoff_data=None)` | `session_id` |
| `recover_workspace` | `(workspace_id, checkpoint_context_id=None)` | `bool` |
| `link_task_to_workspace` | `(workspace_id, plan_id)` | `bool` |
| `get_workspace_tasks` | `(workspace_id, status=None)` | `list[dict]` |

### task_plan_api — 12 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_plan` | `(goal, agent_id=None, priority=5, workspace_id=None)` | `plan_id` |
| `get_plan` | `(plan_id)` | `dict or None` |
| `update_plan` | `(plan_id, **kwargs)` | `bool` |
| `add_step` | `(plan_id, description, tool_name=None, tool_input=None)` | `step_id` |
| `update_step` | `(step_id, **kwargs)` | `bool` |
| `get_plan_steps` | `(plan_id)` | `list[dict]` |
| `add_dependency` | `(source_plan_id, target_plan_id, dependency_type='HARD', condition=None)` | `dependency_id` |
| `get_plan_dependencies` | `(plan_id)` | `list[dict]` |
| `log_tool_call` | `(plan_id, tool_name, action, step_id=None, status='SUCCESS', result_size=None, duration_ms=None)` | `call_id` |
| `save_snapshot` | `(plan_id, context, snapshot_type='MANUAL')` | `snapshot_id` |
| `list_plans` | `(status=None, agent_id=None, limit=50)` | `list[dict]` |
| `delete_plan` | `(plan_id)` | `bool` |

### security — 2 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `hash_password` | `(password, salt=None, iterations=100000)` | `(hash_hex, salt_hex)` |
| `verify_password` | `(password, stored_hash, salt_hex, iterations=100000)` | `bool` |

### harness_api — 8 functions

| Function | Signature | Returns |
|----------|-----------|---------|
| `create_harness_template` | `(title, summary=None, prompt_templates=None, tool_bindings=None, tool_sets=None, memory_access=None, guardrails=None, guardrail_preset=None, evaluation=None, variables=None, category=None, tags=None, owned_by_agent=None, visibility='SHARED', parent_template_id=None, workspace_id=None, input_schema=None, output_schema=None, execution_mode=None)` | `entity_id` |
| `get_harness_template` | `(entity_id)` | `dict or None` |
| `update_harness_template` | `(entity_id, **kwargs)` | `bool` |
| `delete_harness_template` | `(entity_id)` | `bool` |
| `list_harness_templates` | `(category=None, status=None, limit=100)` | `list[dict]` |
| `get_template_with_variables` | `(entity_id)` | `dict or None` |
| `instantiate_harness_template` | `(template_id, variables=None, overrides=None, agent_id=None)` | `dict or None` |
| `count_harness_templates` | `(category=None)` | `int` |

---

## PL/pgSQL API

### Schema: `memory`

| Function | Signature |
|----------|-----------|
| `memory.generate_embedding` | `(p_text TEXT) → vector(1024)` |
| `memory.add_concept_with_embedding` | `(p_title VARCHAR, p_content TEXT, p_category VARCHAR, p_importance INT DEFAULT 5) → BIGINT` |
| `memory.search_similar` | `(p_query TEXT, p_limit INT DEFAULT 10) → TABLE(entity_id BIGINT, title VARCHAR, category VARCHAR, similarity FLOAT)` |

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
| `knowledge_api.get_unvalidated` | `() → TABLE(entity_id BIGINT, title VARCHAR, category VARCHAR, validation_status VARCHAR, confidence NUMERIC, version INT)` |
| `knowledge_api.get_concept_lineage` | `(p_entity_id BIGINT) → JSONB` |
| `knowledge_api.record_review` | `(p_entity_id BIGINT) → VOID` |
| `knowledge_api.get_due_reviews` | `(p_limit INT DEFAULT 50) → TABLE(entity_id BIGINT, title VARCHAR, domain VARCHAR, review_count INT, next_review TIMESTAMPTZ)` |

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

### Schema: `workspace_manager`

| Function | Signature |
|----------|-----------|
| `workspace_manager.create_workspace` | `(p_name VARCHAR DEFAULT NULL, p_workspace_type VARCHAR DEFAULT 'CONVERSATION', p_isolation_mode VARCHAR DEFAULT 'SHARED', p_owner_user_id VARCHAR DEFAULT NULL) → BIGINT` |
| `workspace_manager.get_workspace` | `(p_workspace_id BIGINT) → JSONB` |
| `workspace_manager.update_workspace_status` | `(p_workspace_id BIGINT, p_new_status VARCHAR) → BOOLEAN` |
| `workspace_manager.delete_workspace` | `(p_workspace_id BIGINT) → BOOLEAN` |
| `workspace_manager.add_context_entry` | `(p_workspace_id BIGINT, p_agent_id VARCHAR, p_context_type VARCHAR, p_session_id VARCHAR DEFAULT NULL, p_context_data JSONB DEFAULT '{}') → BIGINT` |
| `workspace_manager.get_context_chain` | `(p_workspace_id BIGINT, p_limit INT DEFAULT 10) → JSONB` |
| `workspace_manager.create_handoff` | `(p_workspace_id BIGINT, p_new_agent_id VARCHAR, p_handoff_data JSONB DEFAULT '{}') → VARCHAR` |
| `workspace_manager.recover_to_checkpoint` | `(p_workspace_id BIGINT) → BOOLEAN` |
| `workspace_manager.get_workspace_summary` | `(p_workspace_id BIGINT) → JSONB` |
| `workspace_manager.cleanup_abandoned` | `() → INT` |

---

## Visualization API

The web visualization server (`scripts/visualization/server.py`) exposes REST
endpoints that proxy to the remote PostgreSQL database. It runs locally on the
agent side and connects via TCP.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | No | Server health check and DB connectivity status |
| `/api/login` | POST | No | Authenticate with username/password; returns session token |
| `/api/logout` | GET | Yes | Clear session cookie and redirect to login |
| `/api/knowledge` | GET | Yes | Knowledge entities with edges for vis.js rendering |
| `/api/memory` | GET | Yes | Memory entities with edges for vis.js rendering |
| `/api/agents` | GET | Yes | Agent registry, active sessions, collaborations |
| `/api/tasks` | GET | Yes | Task plans with steps |
| `/api/workspaces` | GET | Yes | Workspaces with context chains |
| `/api/stats` | GET | Yes | System statistics (entity counts, edge count, workspace count, agent count) |
| `/api/graph/neighbors` | GET | Yes | `?entity_id=X` — neighbor data for graph exploration |
| `/api/graph/context` | GET | Yes | `?entity_id=X` — entity context with grouped neighbors |
| `/api/graph/stats` | GET | Yes | Graph statistics (vertex/edge counts, avg degree, type distribution) |
| `/api/graph/search` | GET | Yes | `?q=X&type=Y` — search entities by keyword and type |
| `/api/graph/all` | GET | Yes | All entities and edges for full graph rendering |

All endpoints require a valid session cookie (except `/api/health` and `/api/login`).
Default admin credentials: `admin` / `admin123` (**development only**).
Session timeout: 5 minutes of inactivity (auto-logout with countdown timer).
