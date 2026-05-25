# Release Notes - memory-pg18-by-yhw v2.3.0

**Author**: Haiwen Yin (胖头鱼)
**Date**: 2026-05-24
**License**: Apache License 2.0

---

## v2.3.0 — Spec Driven Development, Agent Elastic Management, Collaboration Groups

v2.3.0 introduces three major features to the PostgreSQL Memory System: Spec Driven Development (SDD) for spec-to-implementation traceability, Agent Elastic Management for resource-efficient agent hibernation and pooling, and Collaboration Groups for team-based agent collaboration with shared workspaces.

### Highlights

- **5 new tables**: `spec_meta`, `spec_plan_links`, `agent_credentials`, `collab_groups`, `collab_group_members` — spec lifecycle, agent credential management, collaboration groups
- **Spec Driven Development**: SPEC entity type + spec_meta table + spec_api.py (10 functions) + spec_manager PL/pgSQL schema (6 functions) for spec-to-plan traceability
- **Agent Elastic Management**: agent_credentials table + DORMANT/POOL agent states + 8 new agent_api functions (hibernate/wake/pool) for resource-efficient agent lifecycle
- **Collaboration Groups**: collab_groups + collab_group_members tables + collab_api.py (10 functions) + collab_group_manager PL/pgSQL schema (7 functions) + auto-created shared/personal workspaces
- **agent_registry expanded**: +5 columns (created_by_agent_id, agent_role, current_user_id, pool_config, last_active_at), DORMANT/POOL status states
- **143/143 tests passing** across 11 test suites

### Breaking Changes from v2.2.1

| v2.2.1 | v2.3.0 | Impact |
|--------|--------|--------|
| 2 agent states (ACTIVE/INACTIVE) | 4 agent states (ACTIVE/INACTIVE/DORMANT/POOL) | New statuses, backward-compatible |
| No spec tracking | spec_meta + spec_plan_links + SPEC entity type | New tables, no data migration |
| No agent credentials | agent_credentials table | New table, no data migration |
| No collaboration groups | collab_groups + collab_group_members | New tables, no data migration |
| 5 PL/pgSQL schemas | 7 PL/pgSQL schemas (+spec_manager, +collab_group_manager) | New schemas added |
| 9 pg_cron jobs | 12 pg_cron jobs (+3 new) | New jobs defined |
| 3 workspace types | 5 workspace types (+COLLAB_GROUP, +PERSONAL_IN_GROUP) | New types, backward-compatible |

v2.3.0 is **backward-compatible** with v2.2.1. All existing tables, functions, and APIs are unchanged. The new features are additive.

### New Features

#### Spec Driven Development (SDD)

Spec Driven Development unifies specification management with the entity model, enabling traceability from spec to implementation through plan linking.

**spec_meta Table**

| Column | Type | Purpose |
|--------|------|---------|
| entity_id | BIGINT PK | FK to entities (entity_type='SPEC') |
| entity_type | VARCHAR(32) | Denormalized, fixed 'SPEC' |
| spec_type | VARCHAR(32) | DESIGN / REQUIREMENT / API / ARCHITECTURE |
| status | VARCHAR(32) | DRAFT / REVIEW / APPROVED / IMPLEMENTED / DEPRECATED |
| priority | INT | Priority level 1-10 |
| version | INT | Spec version number |
| parent_spec_id | BIGINT | Parent spec for version chain |

**spec_plan_links Table**

| Column | Type | Purpose |
|--------|------|---------|
| spec_id | BIGINT FK | References entities (spec) |
| plan_id | BIGINT FK | References task_plans |
| link_type | VARCHAR(32) | IMPLEMENTS / VALIDATES / DERIVED_FROM |
| linked_at | TIMESTAMPTZ | Link creation timestamp |

Composite PK: (spec_id, plan_id)

**spec_manager PL/pgSQL Schema (6 Functions)**

| Function | Returns | Purpose |
|----------|---------|---------|
| create_spec() | BIGINT | Create a new spec |
| get_spec() | JSONB | Get spec details |
| update_spec_status() | BOOLEAN | Update spec lifecycle status |
| link_spec_to_plan() | BIGINT | Link spec to a task plan |
| get_spec_plans() | TABLE | Get all plans linked to a spec |
| cleanup_orphaned_specs() | INT | Clean up specs with no linked plans |

**spec_api.py (10 Functions)**

| Function | Purpose |
|----------|---------|
| create_spec() | Create spec with type, status, priority |
| get_spec() | Get spec with full metadata |
| update_spec() | Update spec fields and metadata |
| delete_spec() | Delete spec + spec_meta |
| list_specs() | List specs with type/status filters |
| link_spec_to_plan() | Link spec to a task plan |
| unlink_spec_from_plan() | Remove spec-plan link |
| get_spec_plans() | Get all plans for a spec |
| get_plan_specs() | Get all specs for a plan |
| update_spec_status() | Update spec lifecycle status |

#### Agent Elastic Management

Agent Elastic Management introduces DORMANT and POOL agent states with hibernate/wake/pool lifecycle, enabling resource-efficient agent management.

**agent_credentials Table**

| Column | Type | Purpose |
|--------|------|---------|
| credential_id | BIGINT IDENTITY PK | Auto-increment primary key |
| agent_id | VARCHAR(64) FK | References agent_registry |
| credential_type | VARCHAR(32) | API_KEY / TOKEN / CERTIFICATE / CUSTOM |
| encrypted_value | TEXT | Encrypted credential value |
| expires_at | TIMESTAMPTZ | Credential expiration |
| created_at | TIMESTAMPTZ | Creation timestamp |

**agent_registry New Columns**

| Column | Type | Purpose |
|--------|------|---------|
| created_by_agent_id | VARCHAR(64) | Agent that created this agent |
| agent_role | VARCHAR(32) | LEAD / MEMBER / OBSERVER |
| current_user_id | VARCHAR(64) | Current user controlling the agent |
| pool_config | JSONB | Pool configuration (max_pool_size, idle_timeout, etc.) |
| last_active_at | TIMESTAMPTZ | Last activity timestamp |

**agent_registry Expanded Status**: ACTIVE, INACTIVE, **DORMANT** (hibernated, credentials preserved), **POOL** (available for reuse)

**agent_session New Column**

| Column | Type | Purpose |
|--------|------|---------|
| last_active_at | TIMESTAMPTZ | Last session activity timestamp |

**New agent_api.py Functions (8)**

| Function | Purpose |
|----------|---------|
| hibernate_agent() | Transition agent to DORMANT state, preserve credentials |
| wake_agent() | Transition agent from DORMANT to ACTIVE, restore credentials |
| pool_agent() | Transition agent to POOL state for reuse |
| get_dormant_agents() | List all dormant agents |
| get_pool_agents() | List all pooled agents |
| update_agent_role() | Update agent role (LEAD/MEMBER/OBSERVER) |
| get_agent_credentials() | Retrieve agent credentials |
| cleanup_credentials() | Remove expired credentials |

#### Collaboration Groups

Collaboration Groups enable team-based agent collaboration with auto-created shared and personal workspaces.

**collab_groups Table**

| Column | Type | Purpose |
|--------|------|---------|
| group_id | BIGINT IDENTITY PK | Auto-increment primary key |
| group_name | VARCHAR(200) | Human-readable group name |
| owner_agent_id | VARCHAR(64) FK | Group owner (references agent_registry) |
| shared_workspace_id | BIGINT FK | Auto-created shared workspace |
| description | TEXT | Group description |
| settings | JSONB | Group settings (permissions, defaults) |
| status | VARCHAR(32) | ACTIVE / ARCHIVED |
| created_at | TIMESTAMPTZ | Creation timestamp |

**collab_group_members Table**

| Column | Type | Purpose |
|--------|------|---------|
| group_id | BIGINT FK | References collab_groups |
| agent_id | VARCHAR(64) FK | References agent_registry |
| role | VARCHAR(32) | LEAD / MEMBER / OBSERVER |
| personal_workspace_id | BIGINT FK | Auto-created personal workspace |
| joined_at | TIMESTAMPTZ | Join timestamp |

Composite PK: (group_id, agent_id)

**collab_group_manager PL/pgSQL Schema (7 Functions)**

| Function | Returns | Purpose |
|----------|---------|---------|
| create_collab_group() | BIGINT | Create group + shared workspace |
| get_collab_group() | JSONB | Get group details |
| add_member() | BIGINT | Add agent to group + create personal workspace |
| remove_member() | BOOLEAN | Remove agent from group |
| get_group_members() | TABLE | Get all members of a group |
| get_agent_groups() | TABLE | Get all groups for an agent |
| cleanup_empty_groups() | INT | Remove groups with no members |

**collab_api.py (10 Functions)**

| Function | Purpose |
|----------|---------|
| create_collab_group() | Create group with auto-created shared workspace |
| get_collab_group() | Get group with member list |
| update_collab_group() | Update group fields |
| delete_collab_group() | Delete group + workspaces |
| add_group_member() | Add member with auto-created personal workspace |
| remove_group_member() | Remove member from group |
| get_group_members() | List group members |
| get_agent_groups() | List groups for an agent |
| get_group_workspace() | Get group's shared workspace |
| list_collab_groups() | List groups with status filter |

#### New Scheduled Jobs

| Job | Schedule | Action |
|-----|----------|--------|
| dormant_agent_job | Daily 04:00 | Hibernate agents inactive >30 days |
| credential_cleanup_job | Weekly Sun 06:00 | Purge expired agent credentials |
| collab_group_cleanup_job | Daily 05:00 | Remove empty collaboration groups |

### Test Results

```
PostgreSQL Memory System v2.3.0 - Full Test Suite
============================================================
  Connection:  6/6 PASS
  Memory:     16/16 PASS
  Knowledge:  19/19 PASS
  Agent:      22/22 PASS
  Security:   19/19 PASS
  Graph:      12/12 PASS
  Harness:    12/12 PASS
  Workspace:  14/14 PASS
  Spec:       10/10 PASS
  Collab:     10/10 PASS
  Task Plan:   4/4 PASS
Overall: 143/143 ALL PASSED
```

### File Inventory

| File | Status | Description |
|------|--------|-------------|
| scripts/deploy/1_schema.sql | Updated | 27 tables, 69 indexes, 5 views, AGE graph, seed data |
| scripts/deploy/2_api.sql | Updated | 7 PL/pgSQL schemas, 44+ functions |
| scripts/deploy/3_jobs.sql | Updated | 12 pg_cron jobs |
| scripts/deploy/4_harness_templates.sql | Unchanged | 5 built-in templates |
| scripts/lib/spec_api.py | New | 10 Python functions for spec management (SDD) |
| scripts/lib/collab_api.py | New | 10 Python functions for collaboration groups |
| scripts/lib/agent_api.py | Updated | 22 Python functions (was 14; +8 elastic management) |
| scripts/tests/test_spec.py | New | 10 spec tests |
| scripts/tests/test_collab.py | New | 10 collaboration group tests |
| SKILL.md | Updated | v2.3.0 with SDD, Elastic Agents, Collab Groups |
| CHANGELOG.md | Updated | v2.3.0 entry |
| README.md | Updated | v2.3.0 version, counts, features |
| docs/introduction_v2.3.0_zh.md | New/Updated | Chinese introduction for v2.3.0 |
| RELEASE_NOTES_v2.3.0.md | New | This file |
| VERSION | Updated | v2.3.0 |
| config.json | Unchanged | Database, server, embedding, security config |

### Database Schema Summary

| Metric | Count |
|--------|-------|
| Tables | 27 |
| Indexes | 69 |
| Views | 5 |
| PL/pgSQL schemas | 7 |
| PL/pgSQL functions | 44+ |
| AGE graphs | 1 (memory_graph) |
| Harness templates | 5 built-in |
| System config rows | 3 seeded |
| pg_cron jobs | 12 defined |

### Compatibility

- **PostgreSQL**: 18+
- **pgvector**: 0.8.2+
- **Apache AGE**: 1.7.0+
- **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)**: v1.0+
- **Python**: 3.6+
- **psycopg2-binary**: 2.8.6+

---

**Release Date**: 2026-05-24
**Author**: Haiwen Yin (胖头鱼)
**License**: Apache License 2.0
