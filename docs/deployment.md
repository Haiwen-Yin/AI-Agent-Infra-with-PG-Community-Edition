# Deployment Guide - AI Agent Infra v3.10.0 (2026-06-18) - PG Community Edition

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
Admin Agent (mode=admin)
├── Web Portal
├── AIADMIN Connection Pool
└── Admin Token Generator
        │
        │ admin_token (secure)
        ▼
Encrypted Credential Distribution
        │
        ▼
Business Agent (mode=agent)
├── Agent Bootstrap CLI
├── End User Connection Pool
└── agent_config.json (encrypted)
    ✓ Data Grants enforced    ✗ No AIADMIN access
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
