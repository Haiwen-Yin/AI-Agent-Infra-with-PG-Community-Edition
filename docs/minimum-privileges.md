# Minimum Database Privileges - AI Agent Infra v3.10.2 (2026-07-16) - PG Community Edition

## Current State (openclaw user)

| Role/Privilege | Status | Needed? |
|----------------|--------|---------|
| SUPERUSER | Granted | **NO - over-privileged** |
| CREATEDB | Granted | **NO - not needed** |
| CREATEROLE | Granted | Partially (needed for RLS roles) |
| MEMORY_ADMIN (custom) | Granted | Optional, app-level |
| MEMORY_READER (custom) | Granted | Optional, app-level |
| MEMORY_WRITER (custom) | Granted | Optional, app-level |

## Required System Privileges

### Phase 1: Schema Deployment (1_schema.sql)
| Privilege | Reason |
|-----------|--------|
| CONNECT | Connect to database |
| CREATE TABLE | Create 30 tables (6 partitioned, 5 reference-partitioned, 19 non-partitioned) |
| CREATE SEQUENCE | Create sequences (BIGSERIAL on TAGS, TASK_CONTEXT_SNAPSHOTS, etc.) |
| CREATE VIEW | Create views with INSTEAD OF triggers (replaces Oracle JRD Duality Views) |
| CREATE FUNCTION | Create safe_ddl, safe_idx helper functions |
| CREATE EXTENSION | Create Apache AGE property graph (pg_memory_graph) |
| USAGE on TABLESPACE | Or: ALTER USER openclaw SET default_tablespace |

**Partitioning-specific requirements**:
- No additional privilege needed for partitioned DDL — `CREATE TABLE` covers it
- LIST partitioning is covered by `CREATE TABLE`
- Reference partitioning is not natively supported in PG; child tables use manual partitioning aligned with parent
- No ROW MOVEMENT equivalent needed in PG

### Phase 2: API Functions (2_api.sql)
| Privilege | Reason |
|-----------|--------|
| CREATE FUNCTION | Create 13 PL/pgSQL function packages |
| CREATE TYPE | Composite types for function returns |

### Phase 3: Scheduled Jobs (3_jobs.sql)
| Privilege | Reason |
|-----------|--------|
| CREATE EXTENSION (pg_cron) | Create 13 pg_cron scheduled jobs |
| pg_cron superuser | pg_cron requires superuser to schedule jobs (or use cron_superuser GUC) |

### Phase 4: Harness Templates (4_harness_templates.sql)
| Privilege | Reason |
|-----------|--------|
| *(none beyond Phase 1)* | INSERT ... ON CONFLICT DO UPDATE on existing tables |

### Phase 5: Row Security Policies (4_rls_policies.sql)
| Privilege | Reason |
|-----------|--------|
| CREATE ROLE | Create admin_data_role, agent_data_role, pool_agent_data_role |
| CREATE POLICY | Create 25+ Row Security Policies for Deep Sec |
| ALTER TABLE ... ENABLE ROW LEVEL SECURITY | Enable RLS on 7 tables |
| GRANT SELECT, INSERT, UPDATE, DELETE | Grant table permissions to data roles |
| CREATE FUNCTION | Create set_agent_context(), agent_auth functions |

**Note**: Portal APIs that access WORKSPACES/SYSTEM_USERS tables temporarily use `connection.set_agent_context(None)` to switch to schema owner connection, because WORKSPACES.CURRENT_AGENT_ID is NULL for most workspaces, causing RLS policies to reject all rows for restricted users.

### Runtime (Python psycopg2 driver)
| Privilege | Reason |
|-----------|--------|
| CONNECT | Connect to database |
| SELECT, INSERT, UPDATE, DELETE on own schema tables | DML operations (auto-granted to schema owner) |

### Partition Maintenance (operational)
| Privilege | Reason |
|-----------|--------|
| ALTER on own schema tables | ADD PARTITION for future quarters (auto-granted to schema owner) |

### Optional: External Embedding API (for GET_EMBEDDING function)
| Privilege | Reason |
|-----------|--------|
| CREATE EXTENSION (pg_net) or http client | Call external embedding API |
| Network access | Allow HTTP connections to embedding server |

## Minimum Privilege Set

### Option A: Custom Role (Recommended for Production)

```sql
-- 1. Create a dedicated role
CREATE ROLE MEMORY_SYSTEM_ROLE;

-- 2. Grant system privileges
GRANT CONNECT ON DATABASE pg_memory TO MEMORY_SYSTEM_ROLE;
GRANT CREATE TABLE ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT CREATE SEQUENCE ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT CREATE FUNCTION ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT CREATE VIEW ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT CREATE TYPE ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT CREATE POLICY ON SCHEMA public TO MEMORY_SYSTEM_ROLE;
GRANT USAGE ON SCHEMA public TO MEMORY_SYSTEM_ROLE;

-- 3. Grant the role to user
GRANT MEMORY_SYSTEM_ROLE TO openclaw;

-- 4. (Optional) pg_cron requires superuser or cron_superuser setting
-- ALTER SYSTEM SET cron.superuser = 'openclaw';
```

### Option B: CREATEROLE + Supplement (Simpler)

```sql
-- CREATEROLE already provides ability to create roles

-- Supplement with missing privileges:
GRANT CREATE TABLE ON SCHEMA public TO openclaw;
GRANT CREATE SEQUENCE ON SCHEMA public TO openclaw;
GRANT CREATE FUNCTION ON SCHEMA public TO openclaw;
GRANT CREATE VIEW ON SCHEMA public TO openclaw;
GRANT CREATE TYPE ON SCHEMA public TO openclaw;
GRANT CREATE POLICY ON SCHEMA public TO openclaw;
```

## Partitioned Tables Requiring Maintenance Access

| Table | Partition Strategy | Maintenance Operations |
|-------|-------------------|----------------------|
| ENTITIES | LIST (6 partitions by ENTITY_TYPE) | ADD PARTITION for new entity types |
| AGENT_SESSION | LIST (2 partitions by IS_ACTIVE) | Minimal maintenance |
| TASK_PLANS | LIST (2 partitions by STATUS) | Minimal maintenance |
| ENTITY_ACCESS_LOG | RANGE by month | ADD PARTITION for new months |
| ENTITY_EDGES | Aligned with parent ENTITIES | Manual alignment with parent partitions |
| KNOWLEDGE_META | Aligned with parent ENTITIES | Manual alignment with parent partitions |
| ENTITY_EMBEDDINGS | Aligned with parent ENTITIES | Manual alignment with parent partitions |
| HARNESS_META | Aligned with parent ENTITIES | Manual alignment with parent partitions |
| ENTITY_TAGS | Aligned with parent ENTITIES | Manual alignment with parent partitions |
| TASK_STEPS | Aligned with parent TASK_PLANS | Manual alignment with parent partitions |

## Privileges to REVOKE (Security Hardening)

```sql
-- Remove excessive privileges
REVOKE SUPERUSER FROM openclaw;
REVOKE CREATEDB FROM openclaw;
-- Ensure CREATEROLE is scoped to only needed roles
ALTER USER openclaw NOCREATEDB;
```

## Verification Script

```sql
-- After hardening, verify minimum set is intact
SELECT rolname, rolcreaterole, rolcreatedb, rolsuper
FROM pg_roles WHERE rolname = 'openclaw';

-- Check schema permissions
SELECT has_schema_privilege('openclaw', 'public', 'CREATE');
SELECT has_schema_privilege('openclaw', 'public', 'USAGE');

-- Test: can we still create a partitioned table?
CREATE TABLE _priv_test (id VARCHAR(64), type VARCHAR(32), PRIMARY KEY (id, type))
  PARTITION BY LIST (type);
CREATE TABLE _priv_test_p1 PARTITION OF _priv_test FOR VALUES IN ('A');
CREATE TABLE _priv_test_p2 PARTITION OF _priv_test DEFAULT;
DROP TABLE _priv_test;

-- Test: can we still create a function?
CREATE OR REPLACE FUNCTION _priv_test_func() RETURNS VOID AS $$
BEGIN NULL; END;
$$ LANGUAGE plpgsql;
DROP FUNCTION _priv_test_func();

-- Test: can we create a Row Security Policy?
CREATE TABLE _rls_test (id VARCHAR(64), agent_id VARCHAR(64));
ALTER TABLE _rls_test ENABLE ROW LEVEL SECURITY;
CREATE POLICY _rls_test_policy ON _rls_test USING (agent_id = current_setting('app.current_agent_id', TRUE));
DROP TABLE _rls_test;
```

## Risk Summary

| Current Risk | Severity | Fix |
|-------------|----------|-----|
| SUPERUSER granted | **CRITICAL** | Revoke SUPERUSER, use custom role |
| CREATEDB granted | HIGH | Revoke, not needed |
| pg_cron requires superuser | MEDIUM | Use cron_superuser GUC or dedicated cron runner |
| No network access control | MEDIUM | Configure pg_hba.conf for embedding API |
| Custom roles empty (MEMORY_ADMIN/READER/WRITER) | LOW | Populate or drop |
