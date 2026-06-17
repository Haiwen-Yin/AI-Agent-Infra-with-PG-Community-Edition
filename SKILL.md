---
name: ai-agent-infra-pg-community
version: v3.6.2
author: Haiwen Yin
description: "AI Agent Infra with PostgreSQL - Community Edition v3.6.2 - AI Agent的基础设施架构"
tags: [postgresql, ai-agent, infrastructure, community, knowledge-base, vector-search, hybrid-search, fulltext-search, search-api, psycopg2, property-graph, apache-age, multi-agent, partitioning, composite-pk, workspace, context-continuity, context-branching, spec-driven, elastic-agent, collaboration, admin-agent-separation, pgvector, pg-cron, plpython3u, pgcrypto, row-security-policies]
related_skills: [postgresql-18, psycopg2-execution-methodology]
---

# AI Agent Infra with PostgreSQL - Community Edition v3.6.2

**Author:** Haiwen Yin
**Version:** v3.6.2 - 2026-06-18
**License:** Apache License 2.0 (Community Edition)

## ⚠️ CRITICAL: Database & Driver Requirements

### PostgreSQL Version

**Minimum required version: PostgreSQL 18.3**

v3.6.2 uses PostgreSQL features that require version 18.3 or later: pgvector for vector similarity search, Apache AGE for property graph queries, pgcrypto for in-database encryption, Row Security Policies for data isolation, and pg_cron for scheduled jobs.

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
+-----------------------------------------------------------------+
|                AI Agent Infra with PostgreSQL                   |
|                   Community Edition v3.6.2                      |
+-----------------------------------------------------------------+
|                                                                 |
|  +-----------------------------------------------------------+  |
|  |  ENTITIES (unified, LIST partitioned)                     |  |
|  |  +----------+----------+----------+--------+-----------+  |  |
|  |  | MEMORY   | KNOWLEDGE|TASK_OUT  |EXPERI- | HARNESS_  |  |  |
|  |  |          |          |PUT       |ENCE    | TEMPLATE  |  |  |
|  |  +----------+----------+----------+--------+-----------+  |  |
|  |  PK: (ENTITY_ID, ENTITY_TYPE)                             |  |
|  |  COL: WORKSPACE_ID -> WORKSPACES                          |  |
|  +-----------------------------------------------------------+  |
|                         |                                       |
|  +----------------------------------------------+               |
|  |  ENTITY_EDGES (REFERENCE partitioned)        |               |
|  |  PK: (EDGE_ID, SOURCE_ID)                    |               |
|  |  FK: -> ENTITIES(ENTITY_ID, ENTITY_TYPE)     |               |
|  |  + 4 other reference-partitioned children    |               |
|  +----------------------------------------------+               |
|                                                                 |
|  +----------------------------------------------+               |
|  |  WORKSPACES                                  |               |
|  |  |-- WORKSPACE_CONTEXT (append-only JSONB)   |               |
|  |  +-- WORKSPACE_TASKS (updatable)             |               |
|  +----------------------------------------------+               |
|                                                                 |
|  +----------------------------------------------+               |
|  |  AGENT_SESSION (handoff chain)               |               |
|  |  PREDECESSOR_SESSION_ID -> self (chain)      |               |
|  +----------------------------------------------+               |
|                                                                 |
+-----------------------------------------------------------------+
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

v3.6.2 uses PostgreSQL Row Security Policies (RLS) for data isolation. RLS provides declarative row-level access control using `current_setting('app.current_agent_id', TRUE)` to enforce per-agent data filtering.

**Zero trust**: If no agent context is set, Row Security Policies return **no data**.

#### Current Enforcement Status (v3.6.2)

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

v3.6.2 introduces a mode system that separates Admin Agent (runs Web Portal, holds schema owner credentials) from Business Agent (independent process, only holds restricted user credentials).

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
