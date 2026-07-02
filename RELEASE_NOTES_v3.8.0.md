# Release Notes — v3.8.0 (2026-07-02) — PostgreSQL Editions

## Overview

**v3.8.0** is a multi-Agent integration testing release for PostgreSQL editions. Completed full 5-phase deployment and 15-module functional test suite on a fresh PG 18.3 database with zero failures. Multiple runtime bugs discovered and fixed during testing.

## Bugs Fixed

### connection.py — `_convert_params` Parameter Order (Critical)

The `_convert_params` function iterated over `params.keys()` (a dict) to replace `:param` placeholders with `%s`. Dict iteration order is not guaranteed to match the order of `:param` appearances in SQL, causing parameters to be bound to wrong placeholders. Additionally, when the same `:param` appeared multiple times in one SQL statement (e.g., `WHERE title LIKE :kw OR content LIKE :kw`), only the first occurrence was replaced.

**Fix**: Rewrote to use `re.sub` with a callback that replaces each `:param` occurrence in SQL order of appearance, collecting values into a tuple that matches the `%s` placeholder order.

### connection.py — `execute_insert_returning_id` Missing `id_column` Parameter

Oracle editions call `execute_insert_returning_id(sql, params, id_column="group_id")`, but PG's `connection.py` used `returning_col` as the parameter name. This caused `TypeError: got an unexpected keyword argument 'id_column'` in collab_api, workspace_api, task_plan_api, and other modules.

**Fix**: Added `id_column` as an alias parameter; when `returning_col` is not set but `id_column` is, use `id_column`. Also auto-adds `RETURNING <col>` clause when the SQL doesn't already contain one.

### connection.py — `execute_query_one` Missing Commit

`execute_query_one` did not call `conn.commit()`. When a PL/pgSQL function performs DML internally (e.g., `skill_manager.register()` inserts into `skill_meta`), the INSERT was silently rolled back when the connection was returned to the pool.

**Fix**: Added `conn.commit()` after `cur.fetchone()`.

### 1_schema.sql — Double `ON` Clause in CREATE POLICY

Multiple `CREATE POLICY` statements had a duplicated `ON public.<table>` clause (e.g., `CREATE POLICY lm_agent_isolation ON public.loop_meta ON public.loop_meta`), causing syntax errors.

**Fix**: Removed the duplicate `ON` clause.

### 1_schema.sql — loop_audit FK to Partitioned Table

`loop_audit.fk_la_loop` referenced `entities(entity_id)`, but `entities` is partitioned with composite PK `(entity_id, entity_type)`. PostgreSQL does not allow FK references to a subset of a composite PK.

**Fix**: Removed the FK constraint; `loop_id` is now a soft reference without enforced integrity.

### 2_api.sql — `user_manager.authenticate` Missing Variable

The function body used `v_salt` but did not declare it in the `DECLARE` section, causing a compilation error. The `authenticate` function never worked on PG.

**Fix**: Added `v_salt TEXT;` to the DECLARE section.

### loop_api.py — Oracle `TO_CHAR` on Integer

`stop_run` used `TO_CHAR(ITERATION_COUNT)` which is Oracle syntax. PG's `to_char(integer)` does not exist (only `to_char(numeric)`).

**Fix**: Changed to `ITERATION_COUNT::text`.

### monitor_api.py — Wrong Table Name and Column

Referenced `CONTEXT_AUDIT_LOG` table (does not exist) instead of `WORKSPACE_CONTEXT_AUDIT`. Also filtered on `RESOLUTION_STATUS` column which does not exist in that table.

**Fix**: Changed table name to `WORKSPACE_CONTEXT_AUDIT`; removed the `RESOLUTION_STATUS` filter; changed `ORDER BY CREATED_AT` to `ORDER BY CHANGED_AT`.

### event_bus.py — Wrong Column Names

Referenced `SUB_ID` (should be `SUBSCRIPTION_ID`), `CAP_ID` (should be `CAPABILITY_ID`), and `ENABLED='Y'` (should be `STATUS='ACTIVE'`). Also had mixed `:param` and `%s` styles in `get_pending_events` SQL.

**Fix**: Corrected all column names; changed `LIMIT %s` to `LIMIT :limit` for consistent dict-param handling.

### server.py — Missing Audit API Routes (ENT only)

The `_api_audit_list` and `_api_audit_stats` methods were defined but never registered in the API router, causing the audit page to return "API endpoint not found".

**Fix**: Added `elif path == '/api/audit'` and `elif path == '/api/audit/stats'` to the GET routing section.

### audit.html — `audit_id.substring()` on Number (ENT only)

PG uses `BIGINT IDENTITY` for `audit_id`, so the value is a JavaScript number. `number.substring()` throws a TypeError, crashing the entire table render.

**Fix**: Wrapped with `String()` conversion: `String(e.audit_id||'').substring(0,12)`.

## Test Results

### 15-Module Functional Test Suite — All Passed

| # | Module | Operations Tested |
|---|--------|-------------------|
| 1 | Memory API | create → get → search → update → delete |
| 2 | Knowledge API | create → get → search → delete |
| 3 | Message API | send → get_messages → mark_read → delete |
| 4 | Collaboration API | create_group → add_member → list_members → delete |
| 5 | Loop API | create_loop → start_run → record_iteration → list_runs → stop_run |
| 6 | Graph API | knowledge nodes + edges → get_neighbors → get_graph_stats |
| 7 | Workspace API | create → save_context → get_latest_context → list_branches |
| 8 | Spec API | create → get → list → delete |
| 9 | Tool Registry | import_openapi → list → get → delete |
| 10 | Monitor API | get_agent_health → get_system_overview → get_active_alerts |
| 11 | Event Bus | subscribe_agent → publish_event → get_pending → unsubscribe |
| 12 | Task Plan API | create_plan → create_step → list_steps → list_plans → delete |
| 13 | Skill API | register_skill → list_skills → delete_skill |
| 14 | Agent API | get_agent → update_agent → heartbeat → get_active_sessions |
| 15 | LLM Integration | server health endpoint + config verification |

### Database

- 69 tables deployed on fresh PG 18.3
- 176 functions compiled
- 4 Business Agents registered with recovery codes

## Upgrade Notes

This is a bug-fix release. To upgrade:

1. Redeploy `2_api.sql` to pick up the `user_manager.authenticate` fix
2. Replace `connection.py` with the updated version
3. Replace `event_bus.py`, `monitor_api.py`, `loop_api.py` with updated versions
4. (ENT only) Replace `server.py` and `audit.html` with updated versions
5. No data migration required
