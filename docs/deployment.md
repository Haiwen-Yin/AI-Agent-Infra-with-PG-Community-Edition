# Deployment Guide - AI Agent Infra v3.7.0 (2026-06-18) - PG Community Edition

## Prerequisites

- PostgreSQL 18.3 or later
- Python 3.8+ with psycopg2 2.9+
- psql 18+ (for SQL script deployment)
- Required PostgreSQL extensions: pgvector, age, pg_cron, plpython3u, pgcrypto

## 3-Phase Deployment

### Phase 0: Install PostgreSQL Extensions

```sql
-- Connect as superuser
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS plpython3u;

-- Load Apache AGE graph
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
```

### Phase 1: Schema (1_schema.sql)

Creates all tables, partitions, indexes, property graph (Apache AGE), and views.

```bash
psql -U postgres -d ai_agent -f scripts/deploy/1_schema.sql
```

- **Destructive**: Drops all existing tables before creating new ones (`CASCADE`)
- Creates 30 tables (partitioned and non-partitioned)
- Composite primary keys on ENTITIES, ENTITY_EDGES, KNOWLEDGE_META, ENTITY_EMBEDDINGS, HARNESS_META, ENTITY_TAGS, TASK_PLANS, TASK_STEPS, AGENT_SESSION, WORKSPACES, WORKSPACE_CONTEXT, WORKSPACE_TASKS
- WORKSPACE_CONTEXT includes VISIBILITY column (PRIVATE/SHARED/PUBLIC, default SHARED)
- Partitioning: LIST on ENTITIES (by ENTITY_TYPE), AGENT_SESSION (by IS_ACTIVE), TASK_PLANS (by STATUS); REFERENCE on 5 child tables
- Seeds system_config with version 3.7.0
- Seeds system_config with `admin.registration_token` for Admin/Agent separation
- Creates Apache AGE property graph `pg_memory_graph`

### Phase 2: API Functions (2_api.sql)

Creates 13 PL/pgSQL function groups.

```bash
psql -U postgres -d ai_agent -f scripts/deploy/2_api.sql
```

- memory_fusion_engine (uses gen_random_uuid(), jsonb_build_object, composite FKs)
- knowledge_base_api (spaced review, concept lineage with composite key joins)
- agent_permission_manager (access control, session cleanup)
- session_cleanup (purge logs, archive entities)
- workspace_manager (workspace lifecycle, context chain management, cleanup)
- All functions use SECURITY DEFINER

### Phase 3: Scheduler Jobs (3_jobs.sql)

Creates 13 pg_cron scheduled jobs.

```bash
psql -U postgres -d ai_agent -f scripts/deploy/3_jobs.sql
```

| Job | Schedule | Action |
|-----|----------|--------|
| memory_fusion_job | Daily 02:00 | Fuse similar memories + decay importance |
| knowledge_extraction_job | Daily 03:00 | Extract knowledge from memory patterns |
| knowledge_review_job | Daily 06:00 | Schedule spaced reviews for knowledge entities |
| session_cleanup_job | Every 30 min | Clean expired sessions + purge inactive |
| access_log_purge_job | Weekly Sun 04:00 | Purge access logs older than 90 days |
| entity_archive_job | Weekly Sun 05:00 | Archive low-importance memories older than 180 days |
| collab_expiry_job | Daily 00:30 | Process collaboration requests |
| workspace_cleanup_job | Daily 01:00 | Clean stale workspaces and paused sessions |
| context_archive_job | Weekly Sun 03:00 | Archive old context entries |
| stale_workspace_detect_job | Daily 04:00 | Detect stale workspaces |
| dormant_agent_job | Daily 05:00 | Hibernate dormant agents |
| credential_cleanup_job | Daily 06:30 | Clean expired credentials |
| branch_cleanup_job | Weekly Sat 02:00 | Archive abandoned branches |

## Python Setup

```bash
pip install psycopg2-binary
```

## Configuration

Edit `config.json`:
```json
{
  "database": {"user": "postgres", "password": "secret", "host": "localhost", "port": 5432, "dbname": "ai_agent"},
  "server": {"host": "0.0.0.0", "port": 18080, "session_timeout": 300},
  "embedding": {"api_url": "http://10.10.10.1:12345/v1/embeddings", "model": "text-embedding-bge-m3", "dimension": 1024},
  "security": {"masking_enabled": true, "pbkdf2_iterations": 100000, "max_login_attempts": 5, "lockout_minutes": 15}
}
```

Environment variable overrides: `MEMORY_DB_USER`, `MEMORY_DB_PASSWORD`, `MEMORY_DB_HOST`, `MEMORY_DB_PORT`, `MEMORY_DB_NAME`, `MEMORY_SERVER_PORT`, `MEMORY_SERVER_HOST`, `MEMORY_SESSION_TIMEOUT`, `MEMORY_EMBEDDING_API`

## Running Tests

```bash
cd scripts && python -m tests.test_all
```

v3.7.0 test suite: 121 tests across 17 modules.

## Starting the Web Server

```bash
./start_web_server.sh start    # Start (daemon mode)
./start_web_server.sh status   # Status + config
./start_web_server.sh stop     # Stop
```

## Partitioning Maintenance

### Adding Future Partitions

```sql
ALTER TABLE entities ADD PARTITION P_SPEC VALUES ('SPEC');
```

## Row Security Policy Deployment

### Deploy RLS Policies

```bash
psql -U postgres -d ai_agent -f scripts/deploy/4_rls_policies.sql
```

- Creates 3 database roles: `admin_data_role`, `agent_data_role`, `pool_agent_data_role`
- Creates 25+ Row Security Policies for row-level and column-level access control
- Creates restricted `agent_api` user with EXECUTE-only on functions + SELECT on tables
- Creates audit trigger for direct DML bypass detection

## Admin Mode and Agent Mode Deployment

### Admin Agent Deployment (mode=admin)

**1. Configure config.json:**

```json
{
  "mode": "admin",
  "database": {"user": "postgres", "password": "...", "host": "db", "port": 5432, "dbname": "ai_agent"},
  "server": {"host": "0.0.0.0", "port": 18080}
}
```

**2. Start Admin Agent:**

```bash
./start_web_server.sh start
```

**3. Generate admin token for Business Agent registration:**

```bash
curl -X POST http://localhost:18080/api/admin/token/generate \
  -H "Cookie: session=<admin-session>"
```

### Business Agent Deployment (mode=agent)

**1. Bootstrap the Business Agent:**

```bash
python agent_bootstrap.py --admin-url http://admin-host:18080 \
                          --admin-token <token> \
                          --agent-name "business-agent-1" \
                          --output-dir /opt/agent
```

**2. Start Business Agent:**

```bash
python -m scripts.lib.agent_runner --config /opt/agent/agent_config.json
```

The Business Agent:
- Does NOT have schema owner credentials
- Connects only as RLS-restricted user (Row Security Policies enforced)
- Does NOT run Web Portal
- Reads connection info from encrypted `agent_config.json`

### Standalone Mode (default)

No configuration changes needed. `mode` defaults to `standalone`, preserving existing single-process behavior.

## Troubleshooting

- **Connection refused**: Check host/port, ensure PostgreSQL is running on port 5432
- **Pool exhausted**: Increase max_conn in config.json (default: 5)
- **Extension not found**: Install required extensions (pgvector, age, pg_cron, pgcrypto, plpython3u)
- **Permission denied for table**: Check Row Security Policies; ensure agent context is set
- **Port not listening**: Server may take 10-20s to initialize pool; `start_web_server.sh` waits up to 45s
