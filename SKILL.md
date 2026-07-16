---
name: ai-agent-infra-pg-community
version: v3.10.2
author: Haiwen Yin
description: "AI Agent Infra with PostgreSQL - Community Edition v3.10.2 - AI Agent的基础设施架构"
tags: [postgresql, ai-agent, infrastructure, community, knowledge-base, vector-search, hybrid-search, fulltext-search, search-api, psycopg2, property-graph, apache-age, multi-agent, partitioning, composite-pk, workspace, context-continuity, context-branching, spec-driven, elastic-agent, collaboration, admin-agent-separation, pgvector, pg-cron, plpython3u, pgcrypto, row-security-policies]
related_skills: [postgresql-18, psycopg2-execution-methodology]
---

# AI Agent Infra with PostgreSQL - Community Edition v3.10.2

**Author:** Haiwen Yin
**Version:** v3.10.2 - 2026-07-16
**Website:** https://db4agent.top
**License:** Apache License 2.0 (Community Edition)

## ⚠️ CRITICAL: Database & Driver Requirements

### PostgreSQL Version

**Minimum required version: PostgreSQL 18.3**

v3.10.2 extends PostgreSQL features that require version 18.3 or later: pgvector for vector similarity search, Apache AGE for property graph queries, pgcrypto for in-database encryption, Row Security Policies for data isolation, and pg_cron for scheduled jobs.

```sql
SELECT version();
-- Must return: PostgreSQL 18.3 or higher
```

### Python psycopg2 Driver

**Required version: psycopg2 2.9+**

```bash
pip install psycopg2-binary>=2.9
```

**Key differences from Oracle edition:**
- **Bind variables**: PostgreSQL uses `%s` positional binds (not `:name` named binds)
- **Connection**: `psycopg2.pool.ThreadedConnectionPool` (not `oracledb` pool)
- **JSON columns**: PostgreSQL native `JSONB` (not Oracle OSON)
- **Encryption**: `pgcrypto` extension `encrypt_iv`/`decrypt_iv` (not Oracle `DBMS_CRYPTO`)
- **Property Graph**: Apache AGE `cypher()` function (not Oracle SQL/PGQ `GRAPH_TABLE`)
- **Full-text**: PostgreSQL `ts_vector`/`ts_query` (not Oracle Text `CONTAINS`/`SCORE`)
- **Row Security**: PostgreSQL Row Security Policies (not Oracle Data Grants)
- **Scheduling**: `pg_cron` extension (not Oracle Scheduler)
- **Vector**: `pgvector` extension `<=>` operator (not Oracle `VECTOR_DISTANCE`)
- **Stored Procedures**: PL/pgSQL and PL/Python3u (not Oracle PL/SQL)

## Architecture Overview

```
AI Agent Infra with PostgreSQL — Community Edition v3.10.2
│
├── ENTITIES (LIST partitioned by ENTITY_TYPE, 8 partitions)
│   ├── P_MEMORY      — MEMORY
│   ├── P_KNOWLEDGE   — KNOWLEDGE
│   ├── P_TASK_OUTPUT — TASK_OUTPUT
│   ├── P_EXPERIENCE  — EXPERIENCE
│   ├── P_HARNESS     — HARNESS_TEMPLATE
│   ├── P_SPEC        — SPEC
│   ├── P_SKILL       — SKILL
│   └── P_OTHERS      — DEFAULT
│   PK: (ENTITY_ID, ENTITY_TYPE)  |  COL: WORKSPACE_ID -> WORKSPACES
│   8 reference-partitioned children:
│     ENTITY_EDGES, KNOWLEDGE_META, SPEC_META, HARNESS_META,
│     ENTITY_EMBEDDINGS, ENTITY_TAGS, SKILL_META, LOOP_META
│
├── WORKSPACES
│   ├── WORKSPACE_CONTEXT (append-only JSONB)
│   └── WORKSPACE_TASKS (updatable)
│
└── AGENT_SESSION (handoff chain)
    └── PREDECESSOR_SESSION_ID -> self (chain)
```

## Database Access Security

Five-plus-one-layer database access security model with Row Security Policies:

| Layer | Component | Description |
|-------|-----------|-------------|
| L1 | **SKILL.md Policy** | Prohibits direct SQL/DML/DDL except during initial deployment |
| L2 | **4_grants.sql** | Restricted `agent_api` user: EXECUTE on functions + SELECT on tables only |
| L3 | **SECURITY DEFINER** | All PL/pgSQL functions execute with schema owner privileges |
| L4 | **Row Security Policies** | Declarative row-level access control via PostgreSQL RLS; zero-trust (no context = no data) |
| L5 | **Audit logging** | Audit trigger for direct DML bypass detection |
| L6 | **`_sanitize_context_data()`** | Auto-redacts sensitive fields in `save_context()` |

### Row Security Policies — Agent Usage Guide

v3.10.2 uses PostgreSQL Row Security Policies (RLS) for data isolation. RLS provides declarative row-level access control using `current_setting('app.current_agent_id', TRUE)` to enforce per-agent data filtering.

**Zero trust**: If no agent context is set, Row Security Policies return **no data**.

#### Current Enforcement Status (v3.10.2)

| Security Mechanism | Deployed? | Enforcing? | Details |
|---|---|---|---|
| 25+ Row Security Policies | ✅ Yes | ✅ Yes | Queries filtered by `current_setting('app.current_agent_id', TRUE)` predicates |
| 3 Database Roles | ✅ Yes | ✅ Yes | `admin_data_role`, `agent_data_role`, `pool_agent_data_role` |
| Agent Context via current_setting | ✅ Yes | ✅ Yes | `connection.py` sets `app.current_agent_id` per session |
| SECURITY DEFINER functions | ✅ Yes | ✅ Yes | Functions execute with schema owner privileges |
| Restricted user (agent_api) | ✅ Yes | ✅ Yes | No DML/DDL, EXECUTE-only on functions |
| Audit trigger | ✅ Yes | ✅ Yes | Audits direct DML on protected tables |

#### Data Access Summary for Agents

| Table | Agent Can See | Agent Cannot See |
|-------|--------------|-----------------|
| AGENT_REGISTRY | Own row only | Other agents' rows |
| WORKSPACE_CONTEXT | Own workspaces + collab groups; own context always visible; other agents' SHARED/PUBLIC context visible in collab workspaces; other agents' PRIVATE context blocked | Other agents' PRIVATE context in collab workspaces |
| ENTITIES | PUBLIC + own PRIVATE + shared in workspace | Other agents' PRIVATE entities |
| AGENT_CREDENTIALS | Own rows (CREDENTIAL_VALUE masked) | Other agents' credentials |
| SYSTEM_CONFIG | Nothing (admin only) | All rows |
| SKILL_META | All skills (read-only) | Cannot modify |
| CONTEXT_BRANCHES | Own workspaces + collab groups | Other agents' branches |
| TASK_PLANS | Own tasks + collab branches | Other agents' tasks |
| COLLAB_GROUP_MEMBERS | Own membership rows | Other agents' membership rows |
| COLLAB_GROUPS | Groups where member belongs | Groups without membership |

## Admin/Agent Separation Architecture

v3.10.2 introduces a mode system that separates Admin Agent (runs Web Portal, holds schema owner credentials) from Business Agent (independent process, only holds restricted user credentials).

### Modes

| Mode | Process | Schema Owner Credentials | Web Portal | Use Case |
|------|---------|------------------------|------------|----------|
| `standalone` | Single process | Yes | Yes | Development, single-node (default, backward compatible) |
| `admin` | Admin Agent | Yes | Yes | Production Admin node |
| `agent` | Business Agent | No (restricted user only) | No | Production Business Agent |

### Key APIs

| API | Module | Description |
|-----|--------|-------------|
| `generate_admin_token()` | agent_api | Generate admin registration token (AT_ + 32hex) |
| `verify_admin_token(token)` | agent_api | Constant-time verify admin token |
| `register_agent_via_admin(agent_id, name, token)` | agent_api | Register agent + return recovery codes |
| `recover_agent_via_admin(agent_id, code, token)` | agent_api | Recover agent with recovery code |
| `generate_recovery_codes(agent_id)` | agent_api | Generate 8 one-time RC-XXXX-XXXX-XXXX codes |
| `verify_recovery_code(agent_id, code)` | agent_api | Verify + consume one-time recovery code |
| `encrypt_credential_for_distribution(cred, token)` | connection_crypto | Encrypt credential using admin_token via PBKDF2 |
| `decrypt_credential_from_distribution(enc_cred, token)` | connection_crypto | Decrypt distributed credential using admin_token |
| `save_agent_config(config, path)` | connection_crypto | Encrypt and save agent config to local file |
| `load_agent_config(path)` | connection_crypto | Load and decrypt agent config |

### Admin API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/agent/register` | POST | Register Business Agent with admin token; returns recovery codes |
| `/api/admin/agent/recover` | POST | Recover agent with recovery code; returns recovery confirmation |
| `/api/admin/token/generate` | POST | Generate new admin registration token (admin session required) |
| `/api/admin/token/rotate` | POST | Rotate admin token; Business Agents must re-register |
| `/api/admin/skill/list` | GET | List available skills (admin_token + optional filters) |
| `/api/admin/skill/{id}/acquire` | GET | Acquire skill content (admin_token, optional resource=1 for ZIP) |
| `/api/admin/skill/create` | POST | Create new skill (admin_token + metadata) |
| `/api/admin/skill/update` | POST | Update skill metadata (admin_token + skill_id + fields) |
| `/api/admin/skill/delete` | POST | Delete skill (admin_token + skill_id) |
| `/api/admin/skill/upload` | POST | Upload resource file (admin_token + skill_id + base64 content) |

## Context Branching

Context Branching enables forking, merging, abandoning, and resuming conversation context branches within a workspace.

### Branch Lifecycle

```
fork → work → merge (success) → branch merged into target
fork → work → abandon (failure) → branch preserved as lesson reference
fork → work → pause → resume → continue work
```

### Key APIs

| API | Description |
|-----|-------------|
| `fork_branch(workspace_id, fork_context_id, branch_type, branch_name)` | Create a new branch from an existing context point |
| `merge_branch(source_branch_id, target_branch_id)` | Merge source branch into target; auto-detect conflicts |
| `abandon_branch(branch_id)` | Mark branch as ABANDONED (read-only, preserved as lesson) |
| `pause_branch(branch_id)` | Temporarily suspend work on a branch |
| `resume_branch(branch_id)` | Resume a paused branch |
| `diff_branches(branch_id_1, branch_id_2)` | Compare two branches and return differences |
| `detect_conflicts(source_branch_id, target_branch_id)` | Auto-detect entity conflicts between branches |
| `mark_as_lesson(branch_id)` | Manually mark a branch as a lesson reference |
| `extract_lessons(workspace_id)` | Automatically extract learnings from abandoned branches |

## Multi-Agent Collaboration

Multi-Agent Collaboration integrates Collaboration Groups with Branches, SDD (Spec), Task Plans, and Harness for coordinated multi-agent workflows.

### Key APIs

| API | Module | Description |
|-----|--------|-------------|
| `create_collab_group(branch_id, spec_id)` | collab_api | Create group associated with a branch and spec |
| `add_group_member(branch_id)` | collab_api | Add member with their branch |
| `get_member_branches(group_id)` | collab_api | Get all members' branch info |
| `validate_group_against_spec(group_id)` | collab_api | Validate group progress against spec |
| `sync_group_context(group_id)` | collab_api | Sync member branch summaries to shared workspace |
| `fork_parallel_branches(workspace_id, agent_ids)` | branch_api | Create PARALLEL branches for multiple agents |
| `merge_parallel_branches(source_branch_ids, target_branch_id)` | branch_api | Merge multiple parallel branches with conflict detection |
| `get_parallel_diff(branch_ids)` | branch_api | Pairwise diff of parallel branches |
| `add_step(assigned_agent_id)` | task_plan_api | Assign a plan step to a specific agent |
| `distribute_plan_to_group(plan_id, group_id)` | task_plan_api | Distribute steps to group members round-robin |
| `create_spec_for_group(title, group_id)` | spec_api | Create a spec for a collaboration group |
| `validate_group_progress(spec_id, group_id)` | spec_api | Validate group's overall spec progress |
| `share_harness_to_group(entity_id, group_id)` | harness_api | Share a harness template to a group |
| `instantiate_harness_for_member(entity_id, member_agent_id, group_id)` | harness_api | Instantiate harness for a group member |

## Community vs Enterprise Feature Matrix

| Feature | Community | Enterprise |
|---------|-----------|------------|
| Memory & Knowledge System | Yes | Yes |
| 5-Signal Unified Search | Yes | Yes |
| Spec Driven Development | Yes | Yes |
| Agent Elastic Management | Yes | Yes |
| Collaboration Groups | Yes | Yes |
| Multi-Agent Collaboration (Branch+Spec+Plan+Harness) | Yes | Yes |
| Workspace & Context | Yes | Yes |
| Admin/Agent Separation | Yes | Yes |
| Recovery Codes + Agent Recovery | Yes | Yes |
| Private Skill Backup | Yes | Yes |
| Skill Storage & Distribution | Yes (basic) | Yes (secure token) |
| Encrypted DB Credentials | Yes | Yes |
| Workspace Context Audit | No | Yes |
| License | Apache 2.0 | BSL 1.1 |

## Agent Retrieval Guide

When an AI Agent needs to search for information, **always prefer `unified_sql` strategy** — it fuses all 5 signals in a single database call:

```python
from lib.search_api import search

# RECOMMENDED: Single-SQL 5-signal fusion (production)
results = search("database partitioning", strategy="unified_sql", top_k=10)

# With filters
results = search("encryption", strategy="unified_sql", domain="security", category="database")

# DEBUGGING ONLY: Multi-round fusion
results = search("database partitioning", strategy="unified", top_k=10)

# CONVENIENCE: Auto-detect best strategy
results = search("partition*", strategy="auto")
```

## ⚠️ CRITICAL: Database Access Policy

### 1. NEVER Bypass the API Layer

**All data operations MUST go through the Python API layer (`scripts/lib/*.py`) or PL/pgSQL functions. Direct SQL/DML/DDL operations on database tables are STRICTLY PROHIBITED except during initial schema deployment (`scripts/deploy/*.sql`).**

### 2. Database Connection Credentials Must Not Be Injected into Agent Context

When saving context via `save_context()`, any context_data containing keys like `password`, `host`, `connection`, `credential`, `secret`, `key`, or `token` will be automatically masked by `DataMaskingService`. Agents MUST NOT store database connection strings or credentials in WORKSPACE_CONTEXT.

### 3. Use the Restricted Database User for Agent Connections

A restricted `agent_api` database user should be used for runtime connections. This user:
- Has **EXECUTE only** on PL/pgSQL functions (no direct table DML)
- Has **SELECT only** on tables needed for read operations
- **Cannot** CREATE TABLE, CREATE VIEW, ALTER, DROP, INSERT, UPDATE, DELETE directly on tables
- All writes go through `SECURITY DEFINER` PL/pgSQL functions which execute with schema owner privileges while enforcing business rules

### 4. Deployment Scripts Are the Only Exception

The `scripts/deploy/*.sql` scripts are the ONLY authorized direct SQL operations.

## ⚠️ CRITICAL: Pre-Deployment Safety Check

**Before running ANY deploy script, an Agent MUST check whether the database already has an existing deployment.**

```python
from lib.deploy_api import check_deployment
result = check_deployment()
if result["deployed"]:
    # DO NOT run deploy scripts!
    pass
else:
    # Safe to deploy from scratch
    pass
```

### Agent Decision Flow

```
Agent receives Skill → check_deployment() → deployed?
  Yes → Register Skill only (DO NOT deploy)
  No  → Deploy from scratch
```

## PostgreSQL Extension Requirements

| Extension | Version | Purpose |
|-----------|---------|---------|
| pgvector | 0.7+ | Vector similarity search (`<=>` cosine distance) |
| pgcrypto | 1.3+ | In-database encryption (`encrypt_iv`/`decrypt_iv`) |
| age | 1.5+ | Property graph queries (Apache AGE `cypher()`) |
| pg_cron | 1.6+ | Scheduled job execution |
| plpython3u | — | Python stored procedures for embedding generation |
| tsvector | built-in | Full-text search (`to_tsvector`/`to_tsquery`) |


## Loop Engineering [NEW v3.7.3]

Loop Engineering is the 4th generation AI engineering methodology (after Prompt Engineering, Context Engineering, and Harness Engineering), proposed by Peter Steinberger in June 2026.

### Overview
- **4 new tables**: loop_meta, loop_runs, loop_iterations, loop_hooks
- **loop_manager** PL/pgSQL schema with ~33 functions
- **loop_api.py** Python module with 33 functions including evaluation engine
- **6 evaluation types**: TEST (command), DIFF (git diff), LLM_JUDGE (LLM scoring), MANUAL (human review)
- **Stop conditions**: max_iterations, max_tokens, max_duration_seconds
- **Lifecycle hooks**: PRE_RUN, POST_ITERATION, ON_STOP, ON_FAIL, ON_TIMEOUT, ON_START
- **3 pg_cron jobs**: loop_trigger_job (every minute), loop_stuck_check_job (every 5 min), loop_cleanup_job (weekly Sunday)


### Database Schema (35 Tables)
- **14** PL/pgSQL schemas (including loop_manager)
- **23** Python modules (including loop_api)
- **16** pg_cron jobs (including 3 loop jobs)
- **121** tests across 17 test suites

### Collaborative Integration (v3.7.3)
- **Spec-Driven Loop** | Create loops from Spec acceptance_criteria; SPEC_VALIDATION eval type |
- **Task-Loop Binding** | Bind loops to task steps; auto-complete on loop success; TASK_LOOP_BINDING table |
- **Collaborative Loop** | Parent/child loops for collab groups; AGGREGATE eval type; 2-level nesting |
- **Branch-Isolated Loop** | Loops bound to branch_id run in branch context |
- **Skill-Triggered Loop** | Skills with validation_loop metadata auto-start verification |
- **ON_START lifecycle hook** | Added to hook event types |
- **7 new API endpoints** | /api/loops/from-spec, /api/loops/collab, /api/loops/{id}/children, /api/loops/{id}/aggregation, /api/tasks/steps/{id}/bind-loop, /api/tasks/steps/{id}/loop, /api/collab/{id}/loop |

### Bug Fixes (v3.7.3)
- **COM navigation** — Added loops link to Community Edition sidebar (loops is a core feature)
- **Loop detail close button** — Added ❌ close button to loop detail panel header
- **PG authentication** — Fixed `user_manager.authenticate()` hash comparison with `upper()`
- **Server startup** — Fixed startup script using `nohup` instead of `setsid` to prevent timeout deadlocks

## Database Schema (35 Tables)

### Core Tables (7)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| ENTITIES | Unified entity store (13 types) | entity_id BIGINT IDENTITY, entity_type, title, content, visibility, status, workspace_id |
| ENTITY_EDGES | Directed relationships | edge_id BIGINT, source_id BIGINT, target_id BIGINT, edge_type VARCHAR, strength FLOAT |
| KNOWLEDGE_META | Knowledge metadata | entity_id, domain, topic, difficulty_level |
| ENTITY_EMBEDDINGS | Vector embeddings (pgvector) | entity_id, entity_type, embedding VECTOR(1024), model |
| SPEC_META | Specification metadata | entity_id, spec_version, spec_status, spec_scope, complexity |
| HARNESS_META | Harness template metadata | entity_id, execution_mode, timeout_seconds |
| ENTITY_TAGS | Tags for categorization | entity_id, entity_type, tag |

### System Tables (2)

| Table | Purpose |
|-------|---------|
| SYSTEM_USERS | User accounts (SHA256 password hashes, salt, role, status, auth_source) |
| SYSTEM_CONFIG | Key-value store (config_key, config_value, description) |

### Agent Tables (5)

| Table | Purpose |
|-------|---------|
| AGENT_REGISTRY | Agent definitions + elastic management |
| AGENT_CREDENTIALS | Encrypted credential storage |
| AGENT_SESSION | Session with handoff chain (context JSONB) |
| ENTITY_ACCESS_LOG | Audit trail of entity access |
| AGENT_PERMISSION_LOG | Agent action audit trail |

### Collaboration Tables (3)

| Table | Purpose |
|-------|---------|
| AGENT_COLLABORATION | Inter-agent collaboration records |
| COLLAB_GROUPS | Group definitions |
| COLLAB_GROUP_MEMBERS | Group membership |

### Workspace Tables (3)

| Table | Purpose |
|-------|---------|
| WORKSPACES | Isolated environments (isolation_mode) |
| WORKSPACE_CONTEXT | Append-only context chain (context_data JSONB) |
| WORKSPACE_TASKS | Junction: workspaces ↔ task plans |

### Task Tables (5)

| Table | Purpose |
|-------|---------|
| TASK_PLANS | Plan definitions |
| TASK_STEPS | Plan steps (step_data JSONB) |
| TASK_CONTEXT_SNAPSHOTS | Step execution context |
| TASK_TOOL_CALLS | Tool invocation records |
| TASK_DEPENDENCIES | Step dependency graph |

### Loop Tables (4)

| Table | Purpose |
|-------|---------|
| LOOP_META | Loop definitions (stop_conditions JSONB) |
| LOOP_RUNS | Loop execution instances |
| LOOP_ITERATIONS | Per-iteration records (evaluation_result JSONB) |
| LOOP_HOOKS | Lifecycle hook definitions |

## PL/pgSQL Functions (170+ Functions)

| Schema | Count | Key Functions |
|--------|-------|---------------|
| memory_api | 8 | create_memory, get_memory, search_memories, update_memory, delete_memory, reinforce_memory, decay_memories, get_agent_memories |
| knowledge_api | 7 | create_knowledge, get_knowledge, search_knowledge, validate_knowledge, link_knowledge, add_edge, get_edges |
| agent_api | 15 | register_agent, get_agent, create_session, end_session, issue_credential, verify_credential, hibernate_agent, wake_agent, register_pool_agent, assign_pool_agent |
| task_plan_api | 6 | create_plan, get_plan, update_plan_status, add_step, update_step_status, list_steps |
| harness_api | 6 | create_template, get_template, list_templates, instantiate_template, derive_template, validate_template |
| graph_api | 30+ | graph_search, get_neighbors, get_subgraph, add_edge, remove_edge, graph_causal, graph_lineage, graph_collaboration, graph_stats |
| workspace_api | 14 | create_workspace, get_workspace, save_context, get_context_chain, get_latest_context, create_handoff_session, recover_workspace |
| spec_api | 10 | create_spec, get_spec, update_spec, list_specs, delete_spec, create_plan_from_spec, link_spec_to_plan, derive_spec |
| collab_api | 10 | create_collab_group, add_group_member, remove_group_member, share_memory_to_group, get_group_shared_memories |
| security | 4 | hash_password, verify_password, encrypt_value, decrypt_value (pgcrypto) |
| loop_api | 33 | create_loop, start_run, stop_run, add_iteration, evaluate_iteration, register_hook, trigger_hook, get_loop_stats |

## Python API (29 Modules)

PG uses `psycopg2` with `RealDictCursor` for dict returns, and `_convert_params()` for Oracle `:param` → PG `%s` conversion. All 29 modules share identical function signatures with Oracle editions.

Key PG differences:
- `execute_insert_returning_id()` returns `int` for BIGINT identity (vs `str` for Oracle VARCHAR GUID)
- `_convert_params()` transparently handles `:param` → `%s` conversion
- PG `jsonb` columns accept Python dict/list directly via psycopg2 auto-adaptation
- PG `VECTOR(1024)` requires pgvector extension

## pg_cron Jobs (16 Jobs)

| Job | Schedule | Description |
|-----|----------|-------------|
| MEMORY_FUSION_JOB | Weekly Sunday 06:00 | Fuses similar memories, decays importance |
| MEMORY_FUSION_CYCLE | Daily 04:00 | Full fusion cycle |
| SESSION_CLEANUP_JOB | Hourly | Ends stale active sessions |
| KNOWLEDGE_EXTRACTION_JOB | Daily 06:00 | Extracts knowledge from high-importance memories |
| WORKSPACE_CLEANUP_JOB | Daily 04:00 | Archives completed workspaces |
| DORMANT_AGENT_JOB | Every 30 min | Auto-hibernates inactive agents |
| CREDENTIAL_CLEANUP_JOB | Daily 02:00 | Purges expired credentials |
| EMBEDDING_GENERATION_JOB | Every 2 hours | Auto-generates embeddings for new entities |
| LOOP_TRIGGER_JOB | Every 1 min | Triggers pending loop runs |
| LOOP_STUCK_CHECK_JOB | Every 5 min | Detects stuck loop runs |
| LOOP_CLEANUP_JOB | Weekly Sunday | Cleans up finished/failed loop runs |

## Harness Templates (5 Built-in)

| Template | Description |
|----------|-------------|
| RESEARCH_AGENT | Multi-step research: gather, synthesize, produce report |
| CODE_REVIEW_AGENT | Code analysis: parse, identify issues, suggest improvements |
| DATA_ANALYSIS_AGENT | Data pipeline: load, compute stats, generate visualizations |
| CONVERSATION_AGENT | Multi-turn dialogue: maintain context, track intent |
| TASK_EXECUTION_AGENT | General task execution: plan steps, execute, handle errors |

## Critical PostgreSQL / psycopg2 Quirks

- **RealDictCursor**: Returns `RealDictRow`; use `dict(row)` for plain dict
- **BIGINT identity**: Returns Python `int` from `RETURNING`, not `str`
- **Empty tuple params**: `cur.execute(sql, ())` fails with `%` in LIKE patterns. Pass `None` instead
- **VECTOR type**: Pass list `[1.0, 2.0,...]` to pgvector columns
- **JSONB**: psycopg2 auto-adapts Python dict/list; no manual `json.dumps()`
- **PL/pgSQL**: Functions use `SECURITY DEFINER` for privilege escalation
- **pg_cron**: Requires `shared_preload_libraries = 'pg_cron'` in postgresql.conf
- **Apache AGE**: Graph queries use `cypher()` function
- **Port**: 5432 for COM, 5433 for ENT. Separate data directories

## Database Connection

| Parameter | Value |
|-----------|-------|
| Host | `<pg_host>` |
| Port | 5432 (COM) / 5433 (ENT) |
| Database | `ai_agent` (COM) / `ai_agent_ee` (ENT) |
| User | `pgsql` |
| Driver | psycopg2 2.9+ |
| Python | 3.14+ |
| Server URL | `http://<host>:18080` (COM) / `http://<host>:18090` (ENT) |

## Quick Start

### Prerequisites

**PostgreSQL 18.3** with these extensions:
```sql
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS plpython3u;
```

### Install Dependencies

**Option A — Offline (recommended for air-gapped environments):**
```bash
bash scripts/install_offline.sh
python3.14 scripts/verify_deps.py
```
The `vendor/` directory contains 30 pre-downloaded cp314 wheels. No internet required.

**Option B — Online:**
```bash
pip install -r requirements.txt
```

### Deploy Schema

```bash
psql -U pgsql -d ai_agent -f scripts/deploy/1_schema.sql
psql -U pgsql -d ai_agent -f scripts/deploy/2_api.sql
psql -U pgsql -d ai_agent -f scripts/deploy/3_jobs.sql
psql -U pgsql -d ai_agent -f scripts/deploy/4_harness_templates.sql
```

### Configure

Edit `scripts/lib/config.py` or set environment variables:
```bash
export MEMORY_DB_HOST="<db_host>"
export MEMORY_DB_PORT="5432"
export MEMORY_DB_NAME="ai_agent"
export MEMORY_DB_USER="pgsql"
export MEMORY_DB_PASSWORD=""
```

Then optionally encrypt the config:
```bash
python3.14 -m tools.encrypt_config auto
```

### Start Web Server

```bash
python3.14 scripts/visualization/server.py &
```
Access at `http://<host>:18080`. Admin login: admin/admin.

### Database Connection

| Parameter | Value |
|-----------|-------|
| Host | `<pg_host>` |
| Port | 5432 (COM) / 5433 (ENT) |
| Database | `ai_agent` (COM) / `ai_agent_ee` (ENT) |
| User | `pgsql` |
| Driver | psycopg2 2.9+ |

