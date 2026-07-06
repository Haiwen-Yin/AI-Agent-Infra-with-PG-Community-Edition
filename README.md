# AI Agent Infra with PostgreSQL - Community Edition v3.9.0

[![Version](https://img.shields.io/badge/version-v3.9.0-blue.svg)](CHANGELOG.md)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18.3-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

**AI Agent Infrastructure Architecture — Community Edition with Admin/Agent Separation, Context Branching, Multi-Agent Collaboration, Database Access Security (5+1 layers), Portal user system, and Agent pool management — built on PostgreSQL 18.3.**

> **v3.9.0 (2026-07-05): Ecosystem Connectivity — MCP Server (10 tools, stdio+SSE), SSE streaming output, Human-in-the-Loop approval (step/loop/tool), Agent Protocol compatibility, multi-model routing. New: mcp_server.py, approval_api.py, approvals.html. DB: APPROVAL_REQUESTS table + PAUSED state.** See CHANGELOG.md for historical versions. [CHANGELOG.md](CHANGELOG.md)

📄 **[中文完整介绍 / Full Chinese Introduction](docs/introduction_zh_v3.9.0.md)**

📄 **Official Website: [https://db4agent.top](https://db4agent.top)**

---


## Loop Engineering

Loop Engineering is the 4th generation AI engineering paradigm (after Prompt Engineering, Context Engineering, and Harness Engineering), proposed by Peter Steinberger in June 2026. This project implements it with:

- **4 new tables**: loop_meta, loop_runs, loop_iterations, loop_hooks
- **loop_manager** PL/pgSQL schema with ~22 functions for loop lifecycle management
- **loop_api.py** Python module with 33 functions including evaluation engine
- **6 evaluation types**: TEST (run command, check exit code), DIFF (analyze git diff), LLM_JUDGE (LLM scoring, configurable), MANUAL (human review)
- **Stop conditions**: max_iterations, max_tokens, max_duration_seconds
- **Lifecycle hooks**: ON_START, PRE_RUN, POST_ITERATION, ON_STOP, ON_FAIL, ON_TIMEOUT
- **3 pg_cron jobs**: loop_trigger_job, loop_stuck_check_job, loop_cleanup_job

### The 5-Stage Loop Cycle

1. **Intent** - Define goal
2. **Context** - Gather information
3. **Action** - Execute tools
4. **Observe** - Get results
5. **Adjust** - Refine and repeat


## 5-Signal Unified Hybrid Search

The project provides a 10-strategy unified search API (`search_api.py`) for AI agents to retrieve across all data types. The **recommended production strategy** is `unified_sql` — a single-SQL CTE that fuses 5 signals in one database call:

| Signal | Default Weight | Source |
|--------|---------------|--------|
| Vector | 0.40 | `<=>` cosine distance via pgvector |
| Fulltext | 0.25 | PostgreSQL `ts_vector` + `ts_rank` |
| Relational | 0.20 | `KNOWLEDGE_META` / `SPEC_META` / `ENTITIES` metadata |
| Tag | (included in relational) | `ENTITY_TAGS` overlap ratio |
| Graph | 0.15 | `ENTITY_EDGES` BFS proximity (1/depth decay) via Apache AGE |

**Why `unified_sql` is recommended**:
- Eliminates 5 Python-SQL round trips → single database call
- Server-side scoring → no data transfer overhead
- 70-85% lower latency in production
- Returns `engine: "single_sql"` for identification

```python
from lib.search_api import search

# Recommended: single-SQL 5-signal fusion
results = search("database partitioning", strategy="unified_sql", top_k=10)

# Alternative: multi-round fusion (for debugging individual signal scores)
results = search("database partitioning", strategy="unified", top_k=10)

# Auto-detect best strategy
results = search("encryption", strategy="auto")
```

All 10 strategies: `vector`, `fulltext`, `keyword`, `graph`, `hybrid`, `unified`, `unified_sql`, `relational`, `multi_type`, `auto`

---

## Portal User System

Two independent page systems: **Portal** (user-facing: register/login/chat) and **Dashboard** (admin-facing: data management). Root `/` redirects to Portal.

### Portal Login (`/portal/login`)

- Register/login with local system user authentication
- Registration checks SYSTEM_USERS (case-insensitive) for duplicates
- "Enter Admin Portal" button in top-right corner

### Portal Chat (`/portal/chat`)

- **Sidebar**: user info (name + auth type), session list with rename/delete, new chat button
- **Main area**: chat messages, input box, simulated keyword-based replies
- **Session management**: create/switch/rename/delete chat sessions
- **Auto-naming**: new sessions named "New Chat"; auto-renamed to first 60 chars of first message via `WORKSPACE_ALIAS`
- **Agent lifecycle**: POOL → ACTIVE (assigned) → POOL (released)

#### Agent Timeout Auto-Recall

| Config Key | Default | Description |
|------------|---------|-------------|
| `dormant_timeout_min` | 30 min | Agent idle beyond this → auto-recalled to POOL via `DORMANT_AGENT_JOB` |
| `session_timeout_min` | 60 min | Portal session timeout |

Core logic: `LAST_ACTIVE_AT` older than `dormant_timeout_min` → `STATUS='POOL'`, `CURRENT_USER_ID=NULL`.

Change timeout:
```sql
UPDATE system_config SET config_value = '10' WHERE config_key = 'dormant_timeout_min';
```

### Admin Dashboard (`/login`)

- Only LOCAL users can access admin Dashboard
- All existing data management pages unchanged

### Encrypted Credentials

- `config.json`: DB `user`/`password`/`host`/`port`/`dbname` encrypted as `_encrypted` blob
- `AGENT_CREDENTIALS.CREDENTIAL_VALUE`: encrypted with pgcrypto `encrypt_iv`/`decrypt_iv`
- Master key: env `MASTER_DB_KEY` > `~/.pg-infra/master.key` > auto-generate

> **For Enterprise Edition features, see [https://db4agent.top](https://db4agent.top) or the [Enterprise Edition](https://github.com/Haiwen-Yin/AI-Agent-Infra-with-PG-Enterprise-Edition).**

---

## Editions

| Feature | Community Edition | Enterprise Edition |
|---------|------------------|-------------------|
| **Core Infrastructure** | | |
| Memory System & Knowledge Graph | Yes | Yes |
| 5-Signal Unified Hybrid Search | Yes | Yes |
| Spec Driven Development | Yes | Yes |
| Agent Elastic Management | Yes | Yes |
| Collaboration Groups | Yes | Yes |
| Multi-Agent Collaboration (Branch+Spec+Plan+Harness) | Yes | Yes |
| Workspace & Context Continuity | Yes | Yes |
| Context Branching | Yes | Yes |
| Property Graph API (Apache AGE) | Yes | Yes |
| Harness Templates | Yes | Yes |
| Web Visualization Dashboard | Yes | Yes |
| **Portal User System** | | |
| Portal Login / Register | Yes (System User) | Yes (System User) |
| Portal Chat with Sessions | Yes | Yes |
| Session Rename / Delete | Yes | Yes |
| Agent Pool Assignment | Yes | Yes |
| **Identity & Authentication** | | |
| Local System User Auth | Yes | Yes |
| Admin Dashboard Isolation (LOCAL only) | Yes | Yes |
| LDAP Authentication | No | Yes |
| **Skill System** | | |
| Skill CRUD (skill_api.py) | Yes | Yes |
| Skill Distribution via Admin API | Yes | Yes |
| Private Skill Backup (visibility=PRIVATE) | Yes | Yes |
| Skill Management via Admin API | Yes | Yes |
| Secure Token Distribution (skill_token_api.py) | No | Yes |
| **Audit & Compliance** | | |
| Workspace Context Audit | No | Yes |
| Entity Access Audit | No | Yes |
| Compliance Logging | No | Yes |
| **Security & Encryption** | | |
| Encrypted config.json (DB credentials) | Yes | Yes |
| Encrypted AGENT_CREDENTIALS | Yes | Yes |
| Master Key Management | Yes | Yes |
| Data Masking | Yes | Yes |
| **Database** | | |
| Tables | 30 | 35 |
| PL/pgSQL Functions/Packages | 22 base + 78 API in 14 schemas | 22 base + 91 API in 16 schemas |
| pg_cron Jobs | 13 | 17 |
| Row Security Policies | 25+ | 31 |
| Tests | 105 | 135 |
| **License** | Apache 2.0 | BSL 1.1 |

---

## Quick Start

### ⚠️ Pre-Deployment Safety Check (REQUIRED)

**Before running ANY deploy script, check whether the database already has an existing deployment. Re-running deploy scripts on an existing database will DESTROY all data.**

```python
from lib.deploy_api import check_deployment
result = check_deployment()
if result["deployed"]:
    # DO NOT deploy! Only register this Skill.
    pass
else:
    # Safe to deploy from scratch
    pass
```

HTTP endpoint (public, no auth):
```bash
curl http://localhost:18080/api/agent/deployment-check
```

The `1_schema.sql` script now includes built-in protection: it auto-aborts if `system_config.schema_version` exists.

### Prerequisites

- **PostgreSQL 18.3 or later** (required for pgvector, Apache AGE, Row Security Policies)
- **Python 3.8+ with `psycopg2` 2.9+**
- Required PostgreSQL extensions: `pgvector`, `age`, `pg_cron`, `plpython3u`, `pgcrypto`
- `psql` 18+ (for SQL script deployment)

> ⚠️ **Critical**: Ensure `pgvector` extension is installed for vector similarity search. Install with: `CREATE EXTENSION IF NOT EXISTS vector;`

> ⚠️ **Critical**: Ensure `pgcrypto` extension is installed for in-database encryption. Install with: `CREATE EXTENSION IF NOT EXISTS pgcrypto;`

### 1. Install PostgreSQL Extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS plpython3u;
```

### 2. Create Database

```bash
createdb -U postgres ai_agent
```

### 3. Deploy Schema

```bash
psql -U postgres -d ai_agent -f scripts/deploy/1_schema.sql
psql -U postgres -d ai_agent -f scripts/deploy/2_api.sql
psql -U postgres -d ai_agent -f scripts/deploy/3_jobs.sql
```

### 4. Install Python Dependencies

```bash
pip install psycopg2-binary
```

### 5. Configure

Edit `config.json` — database credentials will be auto-encrypted on first run:

```bash
# Option A: Environment variable (recommended)
export MASTER_DB_KEY=$(python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())")
export MEMORY_DB_USER=<db_user>
export MEMORY_DB_PASSWORD=<db_password>
export MEMORY_DB_HOST=<db_host>
export MEMORY_DB_PORT=5432
export MEMORY_DB_NAME=<db_name>

# Option B: Edit config.json (will auto-encrypt on first run)
```

### 6. Run Tests

```bash
cd scripts && python -m tests.test_all
```

### 7. Start Visualization Server

```bash
./start_web_server.sh start    # Start (daemon mode)
./start_web_server.sh status   # Check status
./start_web_server.sh stop     # Stop
# Open http://<web_host>:<web_port> — Login: admin / admin123
```

---

## Project Structure

```
ai-agent-infra-pg-community/
  scripts/
    deploy/
      1_schema.sql              # 35 tables, indexes, property graph (AGE), seed data
      2_api.sql                 # 13 PL/pgSQL function groups
      3_jobs.sql                # 16 pg_cron jobs
    lib/
      config.py                 # Unified Config with encrypted DB credentials
      connection.py             # psycopg2 connection pool (decrypts config)
      connection_crypto.py      # Config encryption/decryption/key rotation
      memory_api.py             # Memory CRUD (8 functions)
      knowledge_api.py          # Knowledge CRUD + graph (7 functions)
      agent_api.py              # Agent, sessions, credentials (17+ functions)
      task_plan_api.py          # Task plans, steps (6 functions)
      security.py               # Data masking, encryption, ConfigEncryption
      harness_api.py            # Harness template CRUD (6 functions)
      graph_api.py              # Property Graph API via Apache AGE (9 functions)
      workspace_api.py          # Workspace lifecycle (14 functions)
      spec_api.py               # Spec CRUD + plan linkage (10 functions)
      collab_api.py             # Collaboration groups (10 functions)
      embedding_api.py          # Vector embedding + search (14 functions)
      search_api.py             # Unified search (3 functions)
      skill_api.py              # Skill CRUD [shared] (Phase 3)
      skill_acquire_api.py      # Agent skill discovery & acquisition [shared] (Phase 3)
      branch_api.py             # Context branching lifecycle (9 functions)
    tests/
      __init__.py               # Package marker
      test_all.py               # Master runner
      ... (14+ suites)
    visualization/
      server.py                 # HTTP server v3.7.5
      templates/                # 14 HTML templates
      static/                   # style.css + vis-network.min.js
  docs/
  config.json                  # Database connection config (auto-encrypted)
  LICENSE           # Apache 2.0
  SKILL.md
  README.md
```

---

## License

Apache License 2.0 — see [LICENSE](LICENSE)

Non-production use is free.

## Author

**Haiwen Yin** — [GitHub](https://github.com/Haiwen-Yin) | [Blog](https://blog.csdn.net/yhw1809)
