# Migration Guide - AI Agent Infra v3.7.0 (2026-06-18) - PG Community Edition

## Oracle to PostgreSQL Migration

This guide covers migrating from AI Agent Infra with OracleDB (Community Edition) to the PostgreSQL Community Edition.

### Key Technology Mapping

| Oracle | PostgreSQL | Notes |
|--------|-----------|-------|
| oracledb 4.0.1+ | psycopg2 2.9+ | Python database driver |
| `:name` named binds | `%s` positional binds | SQL parameter binding |
| PL/SQL | PL/pgSQL + PL/Python3u | Stored procedures |
| DBMS_CRYPTO | pgcrypto (`encrypt_iv`/`decrypt_iv`) | In-database encryption |
| VECTOR_DISTANCE | pgvector `<=>` operator | Vector similarity search |
| CONTAINS + SCORE | ts_vector + ts_rank | Full-text search |
| GRAPH_TABLE (SQL/PGQ) | Apache AGE `cypher()` | Property graph queries |
| Data Grants | Row Security Policies (RLS) | Row-level access control |
| Oracle Scheduler | pg_cron | Scheduled jobs |
| JRD Duality Views | Views with INSTEAD OF triggers | Updatable document views |
| RAWTOHEX(SYS_GUID()) | encode(gen_random_bytes(16), 'hex') | ID generation |
| JSON_OBJECT / JSON_ARRAYAGG | jsonb_build_object / jsonb_agg | JSON construction |
| SYSTIMESTAMP | CURRENT_TIMESTAMP | Current timestamp |
| NUMTODSINTERVAL | INTERVAL | Time intervals |
| VARCHAR2 | VARCHAR | String type |
| CLOB | TEXT | Large text type |
| NUMBER | INTEGER / NUMERIC | Numeric types |
| RAW | BYTEA | Binary data |
| JSON (OSON) | JSONB | JSON storage |
| DSN `host:port/service` | host + port + dbname | Connection parameters |
| `~/.oracle-infra/master.key` | `~/.pg-infra/master.key` | Master key directory |
| AUTHID DEFINER | SECURITY DEFINER | Privilege escalation |
| DBMS_RLS (VPD) | CREATE POLICY (RLS) | Row-level security |

### Schema Migration

#### Data Type Mapping

| Oracle Type | PostgreSQL Type | Example |
|-------------|----------------|---------|
| VARCHAR2(64) | VARCHAR(64) | entity_id columns |
| VARCHAR2(512) | VARCHAR(512) | title |
| VARCHAR2(2000) | VARCHAR(2000) | summary |
| CLOB | TEXT | content |
| NUMBER(3,0) | SMALLINT | importance (1-10) |
| NUMBER(10,0) | INTEGER | retrieval_count |
| TIMESTAMP | TIMESTAMP | created_at, updated_at |
| JSON | JSONB | context_data, metadata |
| RAW | BYTEA | encryption data |
| VECTOR | VECTOR(1024) | embedding (pgvector) |

#### SQL Syntax Changes

```sql
-- Oracle
INSERT INTO entities (entity_id, ...) VALUES (:eid, ...);
SELECT RAWTOHEX(SYS_GUID()) FROM DUAL;
UPDATE agent_registry SET last_seen_at = SYSTIMESTAMP - NUMTODSINTERVAL(1, 'HOUR');
SELECT VECTOR_DISTANCE(embedding, TO_VECTOR(:vec), COSINE) FROM entity_embeddings;
SELECT CONTAINS(title, :ftq, 1), SCORE(1) FROM entities;

-- PostgreSQL
INSERT INTO entities (entity_id, ...) VALUES (%s, ...);
SELECT encode(gen_random_bytes(16), 'hex');
UPDATE agent_registry SET last_seen_at = CURRENT_TIMESTAMP - INTERVAL '1 hour';
SELECT embedding <=> %s::vector FROM entity_embeddings;
SELECT ts_rank(to_tsvector('english', title), to_tsquery(%s)) FROM entities;
```

### Python Code Migration

#### Connection Setup

```python
# Oracle
import oracledb
pool = oracledb.create_pool(user=..., password=..., dsn="host:1521/service")

# PostgreSQL
import psycopg2
from psycopg2 import pool
pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1, maxconn=5,
    host="localhost", port=5432, dbname="ai_agent", user=..., password=...
)
```

#### Query Execution

```python
# Oracle (named binds)
cursor.execute("SELECT * FROM entities WHERE entity_id = :eid", {"eid": "ABC123"})
cursor.execute("INSERT INTO entities VALUES (:eid, :etype, :title)",
               {"eid": "X", "etype": "MEMORY", "title": "test"})

# PostgreSQL (%s positional binds)
cursor.execute("SELECT * FROM entities WHERE entity_id = %s", ["ABC123"])
cursor.execute("INSERT INTO entities VALUES (%s, %s, %s)",
               ["X", "MEMORY", "test"])
```

#### JSON Handling

```python
# Oracle: oracledb returns dict for JSON columns; str for JSON expressions
row = cursor.fetchone()
data = row["CONTEXT_DATA"]  # Already a dict

# PostgreSQL: psycopg2 returns dict for JSONB columns
row = cursor.fetchone()
data = row["context_data"]  # Already a dict (lowercase column names)
```

### Encryption Migration

```sql
-- Oracle (DBMS_CRYPTO)
v_cipher := DB_CRYPTO.encrypt(v_plain);
v_plain := DB_CRYPTO.decrypt(v_cipher);

-- PostgreSQL (pgcrypto)
SELECT encode(encrypt_iv(%s::bytea, %s::bytea, 'aes-cbc'), 'base64');
SELECT convert_from(decrypt_iv(decode(%s, 'base64'), %s::bytea, 'aes-cbc'), 'UTF8');
```

### Row-Level Security Migration

```sql
-- Oracle (Data Grants)
CREATE DATA GRANT entities_agent_own
  ON ENTITIES TO agent_data_role
  WITH PREDICATE (...);

-- PostgreSQL (Row Security Policies)
CREATE POLICY entities_agent_own ON entities
  FOR SELECT TO agent_data_role
  USING (...);

ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
```

### Scheduler Job Migration

```sql
-- Oracle (DBMS_SCHEDULER)
DBMS_SCHEDULER.CREATE_JOB(job_name => 'MEMORY_FUSION_JOB', ...);

-- PostgreSQL (pg_cron)
SELECT cron.schedule('memory_fusion_job', '0 2 * * *', $$SELECT memory_fusion_engine_fuse()$$);
```

### Property Graph Migration

```sql
-- Oracle (SQL/PGQ GRAPH_TABLE)
SELECT * FROM GRAPH_TABLE(ORACLE_MEMORY_GRAPH
  MATCH (a)-[e]->(b)
  COLUMNS(a.entity_id, b.entity_id, e.edge_type));

-- PostgreSQL (Apache AGE cypher)
SELECT * FROM cypher('pg_memory_graph', $$
  MATCH (a)-[e]->(b)
  RETURN a.entity_id, b.entity_id, e.edge_type
$$) AS (a_id VARCHAR, b_id VARCHAR, edge_type VARCHAR);
```

### Configuration Migration

```json
// Oracle config.json
{
  "database": {"user": "openclaw", "password": "hermes", "dsn": "10.10.10.130:1521/openclaw"}
}

// PostgreSQL config.json
{
  "database": {"user": "postgres", "password": "secret", "host": "10.10.10.130", "port": 5432, "dbname": "ai_agent"}
}
```

### Master Key Directory

```bash
# Oracle
~/.oracle-infra/master.key

# PostgreSQL
~/.pg-infra/master.key
```

## Full Migration Steps

1. **Install PostgreSQL 18.3** with required extensions (pgvector, age, pg_cron, pgcrypto, plpython3u)
2. **Create the database**: `createdb -U postgres ai_agent`
3. **Deploy schema**: `psql -U postgres -d ai_agent -f scripts/deploy/1_schema.sql`
4. **Deploy API functions**: `psql -U postgres -d ai_agent -f scripts/deploy/2_api.sql`
5. **Deploy scheduled jobs**: `psql -U postgres -d ai_agent -f scripts/deploy/3_jobs.sql`
6. **Export Oracle data** using custom ETL scripts (data pump not compatible)
7. **Transform and load** data with type mappings applied
8. **Update config.json** for PostgreSQL connection parameters
9. **Update master key directory** from `~/.oracle-infra/` to `~/.pg-infra/`
10. **Run tests**: `cd scripts && python -m tests.test_all`
