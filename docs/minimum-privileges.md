# Minimum Database Privileges - PostgreSQL Memory System v2.2.1

## Required Permissions by Deploy Phase

### Phase 1: Schema Deployment (1_schema.sql)

| Permission | Reason |
|-----------|--------|
| CREATE TABLE | Create 22 tables |
| CREATE SEQUENCE | IDENTITY columns use sequences internally |
| CREATE VIEW | 4 views (v_memory_entities, etc.) |
| CREATE FUNCTION | 3 helper functions in `memory` schema |
| CREATE SCHEMA | 5 PL/pgSQL schemas |
| CREATE EXTENSION | pgvector, age, pg_cron |
| USAGE ON TABLESPACE | Or: specific tablespace quota |

### Phase 2: API Functions (2_api.sql)

| Permission | Reason |
|-----------|--------|
| CREATE FUNCTION | PL/pgSQL functions in 5 schemas |

### Phase 3: Scheduled Jobs (3_jobs.sql)

| Permission | Reason |
|-----------|--------|
| USAGE ON SCHEMA pg_cron | Schedule cron jobs |
| EXECUTE ON FUNCTION cron.schedule | Register scheduled jobs |

### Phase 4: Harness Templates (4_harness_templates.sql)

| Permission | Reason |
|-----------|--------|
| *(none beyond Phase 1)* | INSERT on existing tables |

### Runtime (Python psycopg2 driver)

| Permission | Reason |
|-----------|--------|
| CONNECT | Connect to database |
| SELECT, INSERT, UPDATE, DELETE on own schema tables | DML operations |
| USAGE ON SCHEMA ag_catalog | Apache AGE Cypher queries |

## Minimum Role Setup

```sql
-- 1. Create a dedicated role
CREATE ROLE memory_system_role;

-- 2. Grant schema creation and object creation
GRANT CREATE ON SCHEMA public TO memory_system_role;
GRANT CREATE TABLE TO memory_system_role;
GRANT CREATE FUNCTION TO memory_system_role;
GRANT CREATE SCHEMA TO memory_system_role;
GRANT CREATE VIEW TO memory_system_role;

-- 3. Grant extension installation (superuser only)
-- Run as superuser:
CREATE EXTENSION IF NOT EXISTS vector SCHEMA public;
CREATE EXTENSION IF NOT EXISTS age SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pg_cron SCHEMA public;
GRANT USAGE ON SCHEMA public TO memory_system_role;
GRANT USAGE ON SCHEMA ag_catalog TO memory_system_role;

-- 4. Grant to user
GRANT memory_system_role TO pgsql;
```

## Verification Script

```sql
-- Test: can we create a table?
CREATE TABLE _priv_test (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, data TEXT);
DROP TABLE _priv_test;

-- Test: can we create a function?
CREATE OR REPLACE FUNCTION _priv_test_fn() RETURNS TEXT LANGUAGE plpgsql AS $$ BEGIN RETURN 'ok'; END; $$;
DROP FUNCTION _priv_test_fn();

-- Test: can we query AGE graph?
SELECT count(*) FROM ag_catalog.ag_graph;

-- Test: can we use pg_cron?
SELECT cron.schedule('test_job', '0 0 31 2 *', $$SELECT 1$$);
SELECT cron.unschedule('test_job');
```

## Risk Summary

| Current Risk | Severity | Fix |
|-------------|----------|-----|
| Superuser access for deployment | HIGH | Use dedicated role with minimal permissions |
| pg_cron available to all users | MEDIUM | Restrict pg_cron extensions to specific roles |
| AGE schema accessible to all | LOW | GRANT USAGE selectively |
