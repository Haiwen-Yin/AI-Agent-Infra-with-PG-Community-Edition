# Deployment Guide — PostgreSQL Memory System v2.0.0

## Prerequisites

- PostgreSQL 18 with `pgvector` 0.8.2+ and `Apache AGE` 1.7.0+
- [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) custom extension (for in-database embedding generation via COPY FROM PROGRAM + Python proxy)
- `pg_cron` extension (for scheduled jobs)
- Python 3.8+ with `psycopg2-binary`

## 4-Phase Deployment

Run the SQL scripts in order against the `memory_graph` database:

```bash
createdb memory_graph           # if not already present

# Phase 1 — Schema (tables, indexes, views, AGE graph, seed data)
psql -d memory_graph -f scripts/deploy/1_schema.sql

# Phase 2 — API functions (memory_fusion, knowledge_api, agent_perm, session_cleanup)
psql -d memory_graph -f scripts/deploy/2_api.sql

# Phase 3 — Scheduled jobs (pg_cron)
psql -d memory_graph -f scripts/deploy/3_jobs.sql

# Phase 4 — Harness templates (harness_meta table + 5 built-in templates)
psql -d memory_graph -f scripts/deploy/4_harness_templates.sql
```

Each script is idempotent (`IF NOT EXISTS` / `ON CONFLICT DO NOTHING`).

## Python Setup

```bash
pip install psycopg2-binary
```

The Python API (`scripts/lib/`) reads configuration from `config.json` at the
project root. Override with environment variables:

| Variable | Overrides | Example |
|----------|-----------|---------|
| `PGHOST` | `database.host` | `10.10.10.131` |
| `PGPORT` | `database.port` | `5432` |
| `PGDATABASE` | `database.database` | `memory_graph` |
| `PGUSER` | `database.user` | `pgsql` |
| `PGPASSWORD` | `database.password` | (empty = .pgpass) |

## Configuration

`config.json` structure:

```json
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "memory_graph",
    "user": "pgsql",
    "password": "",
    "min_conn": 2,
    "max_conn": 5
  },
  "embedding": {
    "api_url": "http://10.10.10.1:12345/v1/embeddings",
    "model": "text-embedding-bge-m3",
    "dimension": 1024
  },
  "security": {
    "masking_enabled": true,
    "pbkdf2_iterations": 100000,
    "max_login_attempts": 5,
    "lockout_minutes": 15
  }
}
```

## Running Tests

```bash
cd /root/memory-pg18-by-yhw

# Run full test suite
python -m pytest scripts/tests/test_all.py -v

# Individual modules
python -m pytest scripts/tests/test_memory.py -v
python -m pytest scripts/tests/test_knowledge.py -v
python -m pytest scripts/tests/test_agent.py -v
python -m pytest scripts/tests/test_security.py -v
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `ERROR: could not open extension control file` | Extension not installed | Install pgvector / AGE / pg_cron packages for PG18 |
| `ERROR: function generate_embedding does not exist` | [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) not installed | Install pg-embedding-gen-by-yhw (see `references/`), then run `embedding_register_model()` |
| `ERROR: graph "memory_graph" already exists` | Re-running Phase 1 | Safe to ignore; the `DO` block checks existence first |
| `connection refused` on Python API | PG not running or wrong host | Verify `pg_isready -h $PGHOST -p $PGPORT`; check `config.json` |
| `FATAL: password authentication failed` | Auth misconfiguration | Use `.pgpass` file or set `PGPASSWORD` env var |
| `HNSW index build out of memory` | Large initial data load | Set `maintenance_work_mem = '1GB'` before deploying Phase 1 |
| pg_cron jobs not executing | `cron.database_name` mismatch | Ensure `cron.database_name = 'memory_graph'` in `postgresql.conf` |
| `permission denied for schema memory` | Role lacks schema grants | Run `GRANT ALL ON SCHEMA memory TO pgsql;` |
