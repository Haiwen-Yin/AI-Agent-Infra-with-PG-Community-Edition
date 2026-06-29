# Release Notes — v3.7.5

**Version**: v3.7.5 | **Date**: 2026-06-28

## Overview

v3.7.5 is a critical bug fix release for PostgreSQL editions. Fixes connection layer and SQL compatibility issues that prevented PG editions from functioning.

## Bug Fixes

### 1. connection.py complete rewrite (Critical)
- Replaced `oracledb` with `psycopg2` connection pool
- Adapted to PG `DatabaseConfig` fields (host/port/dbname/min_conn/max_conn instead of dsn/pool_min/pool_max)
- Implemented `_convert_params()` to translate Oracle `:param` bind variables to psycopg2 `%s` positional parameters
- Implemented `execute_insert_returning_id()` to handle PG `RETURNING` clause (removed Oracle `INTO :ret_id`)
- `sanitize_row()` converts `Decimal` to `float` for JSON serialization

### 2. Oracle SQL to PostgreSQL migration (10 modules)
- `RAWTOHEX(SYS_GUID())` -> `gen_random_uuid()::text`
- `SYSTIMESTAMP` -> `NOW()`
- `FETCH FIRST N ROWS ONLY` -> `LIMIT N`
- `FROM DUAL` -> removed
- `RETURNING ... INTO :ret_id` -> `RETURNING ...`
- `TO_VECTOR(:vec)` -> `:vec::vector`
- `NUMTODSINTERVAL` -> `INTERVAL`
- `CAST(... AS DATE) * 86400` -> `EXTRACT(EPOCH FROM ...)`
- `LOCAL` index keyword removed

### 3. monitor_api.py column name fixes
- `START_TIME` -> `created_at` (PG uses lowercase column names)
- `END_TIME` -> `last_active_at`
- Performance metrics SQL adapted to PG column names

### 4. orchestrator.py execute_step_with_retry stub
- Now queries actual TASK_STEPS before marking SUCCESS
- Checks for active LOOP_RUNS bound to the step before completing

### 5. event_bus.py webhook/script execution
- Webhook: added retry with exponential backoff, configurable timeout
- Script: replaced `shell=True` with safe `shlex.split()` + argument list

### 6. message_api.py delete_message status
- Changed soft-delete from `STATUS='FAILED'` to `STATUS='DELETED'`
- Updated CK_CM_STATUS constraint

### 7. loop_api.py missing logger
- Added `import logging` and `logger` definition for `_fire_hooks`

## Upgrade Notes

- **Critical**: Replace `connection.py` with new psycopg2-based version
- Replace all 10 updated Python modules
- Deploy v3.7.5 schema additions (9 new tables + TRACE_ID columns) if not already deployed
- No data migration required for existing data
