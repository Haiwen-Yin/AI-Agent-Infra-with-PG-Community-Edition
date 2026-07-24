# SKILL.md - AI Agent Infra with PostgreSQL

> **Version:** 4.1.0 | **Driver:** psycopg2 2.9+ | **DB:** PostgreSQL 18.3+

This is the operations guide for the AI Agent Infra with PostgreSQL
release package. It covers everything an operator (human or AI Agent)
needs to deploy, configure, start, register against, and operate this
edition.

> **Product brand:** Chuanxu (川序) · **Product:** AI Agent Management Platform
>
> **Technical project:** AI Agent Infra with DB. The database-specific package name
> identifies the PostgreSQL adapter and edition; it is not a separate product
> brand.

This package is **Skill-first and framework-neutral**. Any Agent runtime that
can install or read `SKILL.md` and execute the packaged HTTP, MCP, or CLI
workflows can use the platform; OpenClaw and Hermes Agent are confirmed
integration examples. The runtime does not need to be created by this
platform. Registration and authentication are still required before an Agent
enters the managed inventory, identity, permission, and audit scope.

## 1. Overview

AI Agent Infra with DB is the technical foundation of the **Chuanxu AI Agent
Management Platform**, built on **PostgreSQL 18.3+**. It collapses the
conventional
"Redis + vector DB + graph DB + object store" stack into a single
PostgreSQL kernel - leveraging `pgvector` for embeddings, `pg_trgm` for
fuzzy search, Row-Level Security (RLS) for per-agent isolation,
`pgcrypto` for column encryption, and `pg_cron` for scheduled jobs.

| Edition             | Port  | License          |
|---------------------|-------|------------------|
| Community           | 18080 (default, configurable) | Apache 2.0       |
| Enterprise          | 18090 (default, configurable) | BSL 1.1          |

Enterprise adds: registered-Agent governance, resource policies and bounded
grants, server-attributed N-of-M approvals, emergency control, risk-based audit
and evidence export, per-agent encryption keys, LDAP auth, compliance logs,
skill tokens, and orchestrator approvals.

v4.1.0 requires every external or platform-hosted Agent to register and
authenticate before using non-bootstrap APIs. The Enterprise resource catalog
is authoritative for classification; unknown or sensitive resources without an
explicit policy are denied. Approval, emergency, audit, retention, legal-hold,
and evidence-export controls are enforced by the server and database rather
than by Dashboard visibility.

## 2. Package Contents

After extracting the release zip, you have:

```
AI-Agent-Infra-with-PostgreSQL-{Community,Enterprise}-Edition/
├── SKILL.md                        # this file
├── CHANGELOG.md                    # full version history
├── RELEASE_NOTES_v4.1.0.md   # this release's notes
├── NOTICE                          # third-party attributions
├── LICENSE  /  LICENSE_ENTERPRISE  # edition-specific license
├── requirements.txt                # pinned Python deps
├── config.example.json             # placeholder config template
├── start_web_server.sh             # server control script
├── docs/                           # deep-dive docs
│   ├── introduction_zh.md          # Chinese project introduction
│   ├── architecture.md
│   ├── api-reference.md
│   ├── security.md
│   ├── deployment.md
│   └── ...
├── vendor/                         # 30 pre-downloaded wheels (offline)
└── scripts/
    ├── config_wizard.sh            # first-run interactive config prompt
    ├── install_offline.sh          # install vendor/ wheels (no PyPI)
    ├── verify_deps.py              # pre-flight dependency checker
    ├── agent_bootstrap.py          # Business Agent registration CLI
    ├── deploy/                     # SQL scripts (run in order)
    │   ├── 1_schema.sql            #   tables, indexes, RLS policies
    │   ├── 2_api.sql               #   PL/pgSQL functions (API layer)
    │   ├── 3_jobs.sql              #   pg_cron jobs
    │   ├── 4_harness_templates.sql #   agent harness templates
    │   ├── 4_grants.sql            #   RLS policy grants
    │   ├── 8_v4_1_0_registration.sql # registered-Agent boundary
    │   └── 8_v4_1_0_governance.sql   # Enterprise governance objects
    ├── lib/                        # business modules
    │   ├── connection.py           #   psycopg2 connection pool
    │   ├── config.py               #   config loader (auto-decrypts)
    │   ├── connection_crypto.py    #   PBKDF2 + AES via pgcrypto
    │   ├── agent_api.py            #   dedicated LOGIN role + RLS identity
    │   └── ...                     #   knowledge/graph/memory/loop/...
    ├── tools/
    │   └── encrypt_config.py       # manual encrypt/decrypt CLI
    ├── tests/                      # pytest suite
    └── visualization/
        ├── server.py               # HTTP server (single source of VERSION)
        ├── static/                 # CSS, JS
        └── templates/              # HTML pages
```

## 3. Prerequisites

| Component | Minimum | Notes |
|-----------|---------|-------|
| PostgreSQL | 18.3+ | requires `pgvector`, `pg_trgm`, `pgcrypto`, `pg_cron` extensions |
| Python | 3.8+ (3.14 recommended) | |
| psycopg2 driver | 2.9+ | bundled in `vendor/` |
| Extensions | `pgvector`, `pg_trgm`, `pgcrypto`, `pg_cron` | install via `CREATE EXTENSION` |
| Memory | 2 GB free | for connection pool + vector search |

Install required PostgreSQL extensions (as superuser):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_cron;
```

## 4. Installation (offline-friendly)

The release zip is self-contained - no PyPI access needed.

```bash
# 1. Extract the zip
unzip AI-Agent-Infra-with-PG-Enterprise-Edition-v4.1.0.zip
cd AI-Agent-Infra-with-PG-Enterprise-Edition

# 2. Install Python dependencies from the bundled wheels
bash scripts/install_offline.sh

# 3. Verify all dependencies are present
python3 scripts/verify_deps.py
```

## 5. Configuration

The zip ships **`config.example.json`** with `<PLACEHOLDER>` values only -
real credentials are NEVER bundled. Two ways to produce a runnable
`config.json`:

### Path A: Interactive wizard (recommended for first run)
```bash
./start_web_server.sh start
# -> wizard auto-detects <PLACEHOLDER> tokens and prompts for:
#     database: user / password / host / port / database
#     llm:      api_url / model / api_key
#     embedding: api_url / model / dimension
# -> writes config.json
# -> server then auto-encrypts sensitive sections on first boot
```
Standalone invocation:
```bash
bash scripts/config_wizard.sh
```

### Path B: Manual edit
```bash
cp config.example.json config.json
vim config.json   # replace every <PLACEHOLDER> with a real value
./start_web_server.sh start
```

### Auto-encryption
On first startup, `auto_encrypt_config()` encrypts sensitive fields in the
`database`, `security`, `llm`, and `model_routing` sections of `config.json`
as AES-256-GCM `_encrypted` blobs. This includes database credentials, API
keys, and `security.secret_key`; non-sensitive policy remains readable. The
server enforces owner-only (`0600`) permissions and decrypts transparently.

Manual encrypt / decrypt:
```bash
python3 scripts/tools/encrypt_config.py encrypt config.json
python3 scripts/tools/encrypt_config.py decrypt config.json
```

## 6. Database Schema Deployment

PostgreSQL deployment uses `psql` to run the SQL scripts in
`scripts/deploy/` in order:

```bash
# Deploy schema + API functions + jobs + grants
psql -h <host> -p <port> -U <user> -d <dbname> -f scripts/deploy/1_schema.sql
psql -h <host> -p <port> -U <user> -d <dbname> -f scripts/deploy/2_api.sql
psql -h <host> -p <port> -U <user> -d <dbname> -f scripts/deploy/3_jobs.sql
psql -h <host> -p <port> -U <user> -d <dbname> -f scripts/deploy/4_harness_templates.sql
psql -h <host> -p <port> -U <user> -d <dbname> -f scripts/deploy/4_grants.sql
```

Verify deployment:
```bash
curl http://localhost:<port>/api/agent/deployment-check
```

The schema script `1_schema.sql` is idempotent - it auto-aborts if
`system_config.schema_version` already exists.

## 7. Start the Server

```bash
./start_web_server.sh start     # start (calls wizard if config.json missing)
./start_web_server.sh status    # check status
./start_web_server.sh stop      # stop
./start_web_server.sh restart   # restart
```

Access the dashboard at `http://<host>:<port>` - login: `admin / <password>`
(the password is set in `config.json` under `security.admin_password`).

## 8. Business Agent Registration

Business Agents register against the Admin Agent to obtain encrypted
database credentials:

```bash
# Register a new Business Agent
python3 scripts/agent_bootstrap.py register \
    --agent-id MY_AGENT \
    --agent-name "My Business Agent" \
    --admin-token AT_xxx \
    --admin-url http://<admin-host>:<port>

# Test the resulting connection
python3 scripts/agent_bootstrap.py test

# Recover if the agent crashed and lost credentials
python3 scripts/agent_bootstrap.py recover \
    --agent-id MY_AGENT \
    --recovery-code RC-XXXX-XXXX-XXXX \
    --admin-token AT_xxx \
    --admin-url http://<admin-host>:<port>
```

The bootstrap CLI auto-detects the driver from `agent_config.json`'s
`db_type` field (set to `"pg"` by this adapter) and imports `psycopg2`.

Each Business Agent uses a dedicated PostgreSQL LOGIN role mapped to its
registered Agent identity. The role receives the least-privilege runtime grant
set and RLS still scopes rows to `app.current_agent_id`; a connection failure
or identity mismatch fails closed and never falls back to the Schema Owner.

## 9. API Reference

Once the server is running, these endpoints are available:

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **System** | `/api/health` | GET | Health check |
| **Auth** | `/api/login` | POST | Admin login |
| **Agents** | `/api/agents` | GET/POST | List / register agents |
| **Memory** | `/api/memory` | GET/POST | Memory search / store |
| **Knowledge** | `/api/knowledge` | GET/POST | Knowledge base CRUD |
| **Graph** | `/api/graph/all` | GET | Full graph |
| **Graph** | `/api/graph/search` | POST | Graph search |
| **Graph** | `/api/graph/neighbors` | POST | Neighbor traversal |
| **Tasks** | `/api/tasks` | GET/POST | Task management |
| **Branches** | `/api/branches` | GET/POST | Context branches |
| **Monitor** | `/api/monitor/overview` | GET | System overview |
| **Monitor** | `/api/monitor/agents` | GET | Agent status |
| **Portal** | `/portal/api/login` | POST | Portal user login |
| **Portal** | `/portal/api/chat/send` | POST | Portal chat (SSE) |
| **Enterprise** | `/api/admin/crypto/rotate` | POST | Rotate encryption keys |
| **Enterprise** | `/api/approvals` | GET/POST | Approval requests |
| **Enterprise** | `/api/audit` | GET | Audit trail |
| **Enterprise** | `/api/governance/resources` | GET/POST | Governed resource catalog |
| **Enterprise** | `/api/governance/decide` | POST | Server-side policy decision |
| **Enterprise** | `/api/governance/approvals/{id}/decision` | POST | N-of-M approval decision |
| **Enterprise** | `/api/governance/emergency` | GET/POST | Emergency disable and retry |
| **Enterprise** | `/api/governance/evidence/export` | GET | Scoped evidence export |
| **Agent Protocol** | `/ap/v1/agent/tasks` | POST | Agent Protocol compat |

Full API details: `docs/api-reference.md`.

## 10. Security Model

| Layer | Mechanism |
|-------|-----------|
| Row-level isolation | **Row-Level Security (RLS)** via `app.current_agent_id` session setting |
| Column encryption | `pgcrypto` extension (AES) |
| Auth | Local users + LDAP (Enterprise) |
| Audit | `entity_access_log` + `audit_api` (Enterprise) |
| Governance | Resource policy, bounded grants, approvals, emergency control (Enterprise) |

Business Agents connect with the shared DB role, then issue
`SET app.current_agent_id = '<agent_id>'` to activate RLS scoping. The
credentials are distributed encrypted via the registration API; the Schema
Owner is Admin-only and is never a Business Agent fallback.

## 11. Testing

```bash
# Run the full test suite
python3 -m pytest scripts/tests/ -v

# Or the legacy runner
cd scripts && python -m tests.test_all
```

Tests use the configured `config.json` connection. Set
`AIAGENT_SKIP_DB=oracle,yashandb` to skip unreachable backends.

## 12. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `import psycopg2` fails | driver not installed | `bash scripts/install_offline.sh` |
| `password authentication failed` | wrong DB user/password | re-run `bash scripts/config_wizard.sh` |
| `extension "vector" does not exist` | pgvector not installed | `CREATE EXTENSION vector;` as superuser |
| `extension "pgcrypto" does not exist` | pgcrypto not installed | `CREATE EXTENSION pgcrypto;` |
| `extension "pg_cron" does not exist` | pg_cron not in shared_preload_libraries | edit `postgresql.conf` then restart PG |
| Server starts but RLS not filtering | `app.current_agent_id` not set | ensure connection.py `apply_agent_context` is called |
| Portal chat returns 500 | LLM `api_url` not configured | edit `config.json` -> `llm.api_url` |
| Deployment fails with "schema_version exists" | DB already has schema | drop schema or use `--force` |
| `config.json` has `_encrypted` but server can't decrypt | configured master key does not match | restore the matching `MASTER_DB_KEY` or `~/.ai-agent-infra/master.key` backup |

Server log: `viz_server.log` in the project directory.

## 13. Offline Deployment

The release zip is fully self-contained:
- `vendor/` - 30 wheels (no PyPI access needed)
- `scripts/install_offline.sh` - installs all wheels
- `scripts/verify_deps.py` - integrity check
- Schema deployment via `psql -f scripts/deploy/*.sql`
- `docs/deployment.md` - detailed deployment guide
