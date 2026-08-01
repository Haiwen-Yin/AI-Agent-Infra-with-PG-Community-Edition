# SKILL.md - AI Agent Infra with PostgreSQL

> **Version:** 4.3.2 | **Driver:** psycopg2 2.9+ | **DB:** PostgreSQL 18.3+

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

v4.3.1 requires every human and external or platform-hosted Agent to resolve to
an active database Principal before using non-bootstrap APIs. Agent enrollment
uses a one-time user-sponsored token; Business Agents receive neither database
credentials nor a Schema Owner fallback. The Enterprise resource catalog
is authoritative for classification; unknown or sensitive resources without an
explicit policy are denied. Approval, emergency, audit, retention, legal-hold,
and evidence-export controls are enforced by the server and database rather
than by Dashboard visibility.

v4.3.2 adds versioned Memory lifecycle controls. Existing Memory is adopted
without changing its external entity ID; ordinary delete becomes reasoned
logical unavailability, while authorized history remains available. Agents may
read current authorized Memory, request bounded chains, submit attributed
feedback or governed candidates, and start only permitted dry-run or managed
jobs. Approved semantic candidates require a separate reasoned activation that
creates a successor Version; snapshot refresh and job completion are fenced.
Memory content and model output are untrusted data and never authority.
MCP exposes `memory_lifecycle_create`, `memory_lifecycle_chain`,
`memory_lifecycle_feedback`, and `memory_lifecycle_candidate` only for the
authenticated Agent's own Memory Versions; candidates still require governed
review and separate activation.

The Organization workspace is a governed query and change interface. Agents
may discover only organization facts allowed by their authenticated Principal
and `organizations.*` scope. Reading this Skill does not grant graphical edit,
Human administration, directory synchronization, or publication authority.
Relational facts remain authoritative; Apache AGE is a projection only.

## 2. Package Contents

After extracting the release zip, you have:

```
AI-Agent-Infra-with-PostgreSQL-{Community,Enterprise}-Edition/
├── SKILL.md                        # this file
├── CHANGELOG.md                    # full version history
├── RELEASE_NOTES_v4.3.2.md   # this release's notes
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
├── vendor/                         # bundled Python wheels; verify before offline install
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
    │   ├── 8_v4_1_0_registration.sql # registered-Agent boundary (Community)
    │   ├── 8_v4_1_0_governance.sql   # registration + governance (Enterprise)
    │   ├── 9_v4_2_0_graph_engineering.sql
    │   ├── 10_v4_2_0_graph_runtime.sql
    │   ├── 11_v4_2_0_graph_control.sql
    │   ├── 12_v4_2_0_graph_edge_scope.sql
    │   ├── 13_v4_2_0_scheduler_ha.sql # Enterprise overlay only
    │   ├── 14_v4_2_0_graph_triggers.sql
    │   ├── 15_v4_2_1_executor_registry.sql # internal closure
    │   ├── 16_v4_3_0_identity_channels.sql
    │   ├── 17_v4_3_0_governance_lifecycle.sql
    │   ├── 18_v4_3_0_security_lifecycle.sql
    │   └── 19_v4_3_1_organization_governance.sql
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
| Python | 3.14+ | selected through `scripts/python_runtime.sh` |
| psycopg2 driver | 2.9+ | bundled in `vendor/` |
| Extensions | `pgvector`, `pg_trgm`, `pgcrypto`, `pg_cron`, Apache AGE 1.7+ | install AGE and the other extensions as a privileged PostgreSQL operator |
| Memory | 2 GB free | for connection pool + vector search |

Install required PostgreSQL extensions (as superuser):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS age;
```

Apache AGE is installed by the PostgreSQL operator, not by the restricted
application role. Grant the runtime database role the minimum projection
access after installation:

```sql
GRANT USAGE ON SCHEMA ag_catalog TO <APP_ROLE>;
GRANT SELECT ON ALL TABLES IN SCHEMA ag_catalog TO <APP_ROLE>;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ag_catalog TO <APP_ROLE>;
GRANT USAGE ON TYPE ag_catalog.agtype TO <APP_ROLE>;
```

The v4.3.0 migration does not issue `LOAD 'age'`: hardened PostgreSQL
installations commonly reserve `LOAD` for superusers, and an already
installed AGE extension exposes the required SQL objects without that
session-level command. The `ag_catalog` grants above are required for the
runtime role to create and use `ai_execution_graph`.

### PostgreSQL Agent role provisioning prerequisite

The Admin Agent connects as the Schema Owner when it provisions a Business
Agent. The Schema Owner therefore needs two narrowly scoped PostgreSQL role
management prerequisites:

1. `CREATEROLE`, so it can create the per-Agent `LOGIN` role.
2. `ADMIN OPTION` on the pre-created `ai_agent_runtime` role, so it can grant
   that shared `NOLOGIN` runtime role to the new Agent login.

Ask a PostgreSQL DBA to apply the following once. Replace the placeholder with
the configured Schema Owner; never grant these privileges to a Business Agent
or to `ai_agent_runtime` itself:

```sql
ALTER ROLE <SCHEMA_OWNER> CREATEROLE;
GRANT ai_agent_runtime TO <SCHEMA_OWNER> WITH ADMIN OPTION;
```

If `ai_agent_runtime` does not exist, the first Admin provisioning request can
create it, provided the Schema Owner has `CREATEROLE`; a DBA-created runtime
role still requires the explicit `ADMIN OPTION` grant above. The resulting
per-Agent login remains `NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS`.
If either prerequisite is missing, registration fails closed with an
actionable provisioning error and never falls back to the Schema Owner.

## 4. Installation (offline-capable runtime)

The compiled Web assets run without Node.js, npm, or network access. Python
installation is offline only when every requirement in `requirements.txt` has
an exact compatible wheel in `vendor/`; `verify_deps.py` is the release gate
and must pass before using `install_offline.sh`.

```bash
# 1. Extract the zip
unzip AI-Agent-Infra-with-PG-Enterprise-Edition-v4.3.2.zip
cd AI-Agent-Infra-with-PG-Enterprise-Edition

# Select any accessible Python 3.14+ runtime; no vendor-specific path is required.
source scripts/python_runtime.sh
export PYTHON_BIN="$(cx_resolve_python)"
cx_prepare_python_environment "$PYTHON_BIN"

# 2. Install Python dependencies from the bundled wheels
bash scripts/install_offline.sh

# 3. Verify all dependencies are present
"$PYTHON_BIN" scripts/verify_deps.py
```

The installer fails closed when a required wheel is missing or incompatible;
obtain the missing release dependencies from the approved internal mirror
before retrying.

`vendor/` may contain both the upstream `cryptography==49.0.0` wheel for
glibc 2.34+ and the RHEL 8/glibc 2.28 source-built wheel. The installer and
`verify_deps.py` select the compatible one automatically. Customers on newer
systems do not need to rebuild cryptography; the reproducible source-build
procedure is documented in `docs/cryptography-build.md`.
The current v4.3.2 archive includes the verified glibc 2.28 wheel; do not
rename the `manylinux_2_34` wheel or substitute an older cryptography release.

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
"$PYTHON_BIN" scripts/tools/encrypt_config.py encrypt config.json
"$PYTHON_BIN" scripts/tools/encrypt_config.py decrypt config.json
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

For the integrated v4.3.0 profile, use `scripts/migration_runner.py` for the
additive migration tail. Community applies these nine scripts in order:
`9_v4_2_0_graph_engineering.sql`, `10_v4_2_0_graph_runtime.sql`,
`11_v4_2_0_graph_control.sql`, `12_v4_2_0_graph_edge_scope.sql`,
`14_v4_2_0_graph_triggers.sql`, `15_v4_2_1_executor_registry.sql`,
`16_v4_3_0_identity_channels.sql`, and
`17_v4_3_0_governance_lifecycle.sql`, and
`18_v4_3_0_security_lifecycle.sql`. Enterprise inserts
`13_v4_2_0_scheduler_ha.sql` between `12` and `14`, for ten scripts total.
The internal `15` step is part of v4.3.0 and is not a public v4.2.1 release.

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
"$PYTHON_BIN" scripts/agent_bootstrap.py register \
    --agent-id MY_AGENT \
    --agent-name "My Business Agent" \
    --admin-token AT_xxx \
    --admin-url http://<admin-host>:<port>

# Test the resulting connection
"$PYTHON_BIN" scripts/agent_bootstrap.py test

# Recover if the agent crashed and lost credentials
"$PYTHON_BIN" scripts/agent_bootstrap.py recover \
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

### Canonical And Legacy Entry Points

New integrations use the authenticated FastAPI service (`web_app:app`) and
its Principal-aware `/api/auth/*`, resource, Graph, Channel, Barrier, Gateway,
and governance routes, or the equivalent HTTP/MCP/Skill workflow. The
established Dashboard, Portal, and Agent paths are retained through the
request-local compatibility bridge to `visualization/server.py`; the bridge
does not open a second listener or grant direct database access. Legacy callers
remain subject to session, CSRF, Agent identity, and permission checks. The
`production` runtime profile exposes the integrated v4.3.2 stable core and is
the current production recommendation; the v4.3.2 release and closure evidence
are PASS. `graph-preview` and `development` remain explicitly controlled
profiles for experimental capabilities.

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
"$PYTHON_BIN" -m pytest scripts/tests/ -v

# Or the legacy runner
cd scripts && "$PYTHON_BIN" -m tests.test_all
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

## 14. v4.3.0 Integrated Graph Engineering and Governed Collaboration

This package uses the v4.3.0 shared code line. It includes the internal v4.2.1
Graph closure: versioned Graph Definitions, deterministic compilation, durable
Graph Runs, State Events, Checkpoints, Workers, Event Inbox/Outbox, Artifacts,
evaluators, reason-required interventions, a versioned Node Executor registry,
bounded delivery attempts, dead-letter replay, and operator governance events.
The internal v4.2.1 milestone is not a separately published package.

The migration tail above is part of the same profile and must be applied
through the checksum ledger before using the new Graph, Channel, Barrier, or
governance lifecycle objects.

PostgreSQL 18 uses **Apache AGE** for the database graph projection. The
relational `GRAPH_*` runtime tables remain the portable transaction and
recovery authority. PostgreSQL 19 native Property Graph is a future adapter
target and is not required for this package.

Human and Agent activity is governed by the same Principal and database-backed
Session boundary. A permitted user creates a one-time Enrollment Token that
fixes sponsorship, owner, runtime, environment, risk tier, quota, and Security
Domain. A Channel is a collaboration view, not an authorization grant: it
cannot enlarge database, API, Skill, Tool, model, memory, Artifact, or export
access. Barrier arrivals and decisions are durable and attributable. The Agent
Gateway delivers channel events through short-lived instance tokens, fencing,
acknowledgement, retry, and dead-letter rules; web restart recovery is scoped to
the local node.

### Agent Skill Workflow

After registration and authentication, an external Agent can use the common
HTTP or MCP contract:

```bash
# Discover AGE-backed graph capability and registered types
curl -b cookies.txt http://localhost:<port>/api/graph/capabilities
curl -b cookies.txt http://localhost:<port>/api/graph-types

# Create a definition, import or create a Draft, compile, and publish
curl -b cookies.txt -H 'Content-Type: application/json' -d '{"name":"support-flow"}' \
  http://localhost:<port>/api/graphs
curl -b cookies.txt -H 'Content-Type: application/json' -d @graph-version.json \
  http://localhost:<port>/api/graphs/<graph_id>/versions
curl -b cookies.txt -H 'Content-Type: application/json' -d '{"reason":"validated POC topology"}' \
  http://localhost:<port>/api/graph-versions/<version_id>/compile
curl -b cookies.txt -H 'Content-Type: application/json' -d '{"reason":"approved for test execution"}' \
  http://localhost:<port>/api/graph-versions/<version_id>/publish
```

Workers receive bounded input and a short Lease Token, never database
credentials. They must heartbeat, checkpoint, and complete/fail with the
fencing token. Stale or expired tokens cannot overwrite a newer Attempt. Use
`/api/graph-runs/<run_id>/state` and `/snapshot` after a restart to recover
managed state. Existing Task Plan and Loop behavior remains available through
the v4.1 compatibility bridge.

### Executor and delivery operations

Executors are declarative manifests, not arbitrary Python, SQL, shell, or
network callbacks. Built-in `CONTROL`, `WORKER`, and `WAIT` Executors are
resolved for every node before claim and completion. Custom manifests require
an authenticated registration actor; disabling or deprecating one requires a
reason and affects new claims only.

```bash
curl -b cookies.txt 'http://localhost:<port>/api/graph-executors?include_inactive=true'
curl -b cookies.txt http://localhost:<port>/api/graph/events/inbox
curl -b cookies.txt http://localhost:<port>/api/graph/events/dead-letter
curl -b cookies.txt http://localhost:<port>/api/graph/events/outbox
curl -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"reason":"verified downstream availability"}' \
  http://localhost:<port>/api/graph/events/inbox/<inbox_id>/replay
```

The database stores attempt counters, next-available time, maximum attempts,
and terminal `DEAD_LETTER` state. Non-idempotent external work is not blindly
replayed after an uncertain outcome.

The Graph contract may evolve within the v4.3.x maturity cycle. Breaking
changes require a new definition/schema version, migration or review state,
and new release evidence. The v4.3.2 production profile is the current
production baseline; v4.1.x remains available as the prior baseline.
Graduation is controlled by configuration and evidence, not a second code line.

## 13. Offline Deployment

The release zip contains the compiled Web runtime and the bundled dependency
set. The Web assets require no Node.js, npm, or network access. Python is
offline-installable only after `scripts/verify_deps.py` reports PASS; the
installer fails closed when a required wheel is absent or incompatible.
- `vendor/` - bundled Python wheels
- `scripts/install_offline.sh` - installs verified wheels
- `scripts/verify_deps.py` - integrity check
- Schema deployment via `psql -f scripts/deploy/*.sql`
- `docs/deployment.md` - detailed deployment guide
