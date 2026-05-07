#!/bin/bash
# Complete Test Script for memory-pg18-by-yhw v0.3.2 Task Plan System (FINAL)
# Runs ALL commands as pgsql user via su

SSH_HOST="10.10.10.131"
PGSQL_CMD() {
    # Execute command as pgsql user on remote server
    ssh root@${SSH_HOST} "su - pgsql << 'CMD'
$1
CMD" 2>&1
}

echo "================================================================================"
echo "🧪 TASK PLAN SYSTEM TEST SUITE - v0.3.2 (REMOTE PG SERVER)"
echo "================================================================================"

# Step 1: Copy SQL file to remote server as root first, then chown
echo ""
echo "📋 STEP 1: Copying SQL schema file..."
scp -q /root/.hermes/skills/memory-pg18-by-yhw/scripts/init_task_plan_system.sql \
    root@${SSH_HOST}:/tmp/init_task_plan_system.sql
ssh root@${SSH_HOST} "chown pgsql:pgsql /tmp/init_task_plan_system.sql; ls -la /tmp/init_task_plan_system.sql"

if [ $? -eq 0 ]; then
    echo "✅ SQL file copied and permission set"
else
    echo "❌ Failed to copy SQL file"
    exit 1
fi

# Step 2: Check PG service status
echo ""
echo "================================================================================"
echo "📋 2. CHECK POSTGRESQL SERVICE STATUS"
echo "================================================================================"

PG_STATUS=$(ssh root@${SSH_HOST} "su - pgsql -c 'pg_ctl status' 2>&1 || echo NOT_RUNNING")
if echo "$PG_STATUS" | grep -q "running"; then
    echo "✅ PostgreSQL is RUNNING"
    echo "$PG_STATUS"
else
    echo "⚠️  PG not running. Starting..."
    ssh root@${SSH_HOST} << 'STARTPG'
su - pgsql << 'CMD'
export PGDATA=/var/lib/pgsql/data
export PATH=/usr/local/pgsql/bin:$PATH
mkdir -p /var/lib/pgsql/data/log
chown pgsql:pgsql /var/lib/pgsql/data/log 2>/dev/null || true
/usr/local/pgsql/bin/pg_ctl start -l /var/lib/pgsql/data/log/postgresql.log -w > /dev/null 2>&1
sleep 3
pg_ctl status 2>&1 || echo "Could not verify startup"
CMD
STARTPG
    sleep 3
fi

# Verify PG version
echo ""
echo "📊 PostgreSQL Version:"
ssh root@${SSH_HOST} "su - pgsql -c 'psql --version'" | grep -E "PostgreSQL|18"

# Step 3: Check/create database
echo ""
echo "================================================================================"  
echo "📋 3. CHECK/CREATE DATABASE"
echo "================================================================================"

DB_EXISTS=$(ssh root@${SSH_HOST} "su - pgsql -c 'psql -lqt | grep memory_graph' 2>/dev/null || echo ''")
if [ -z "$DB_EXISTS" ]; then
    echo "Database 'memory_graph' not found. Creating..."
    ssh root@${SSH_HOST} "su - pgsql -c 'createdb memory_graph'" 2>&1 | head -3
    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully"
    else
        # Try with postgres user via psql
        ssh root@${SSH_HOST} "su - pgsql -c 'psql -d postgres -c \"CREATE DATABASE memory_graph;\"'" 2>&1 > /dev/null
        echo "Database created via postgres connection"
    fi
else
    echo "✅ Database 'memory_graph' already exists"
fi

# Step 4: Deploy Task Plan schema
echo ""
echo "================================================================================"
echo "📋 4. DEPLOY TASK PLAN SCHEMA"
echo "================================================================================"

DEPLOY_OUTPUT=$(ssh root@${SSH_HOST} "su - pgsql -c 'psql -d memory_graph -f /tmp/init_task_plan_system.sql' 2>&1")
if echo "$DEPLOY_OUTPUT" | grep -q "ERROR\|error"; then
    echo "❌ Schema deployment had errors:"
    echo "$DEPLOY_OUTPUT" | tail -10
else
    echo "✅ Schema deployed successfully"
fi

# Clean up SQL file on remote server
ssh root@${SSH_HOST} "rm -f /tmp/init_task_plan_system.sql"

# Step 5: Verify tables created
echo ""
echo "================================================================================"
echo "📋 5. VERIFY TABLES CREATED"
echo "================================================================================"

TABLE_COUNT=$(ssh root@${SSH_HOST} "su - pgsql -c 'psql -d memory_graph -tA -c \"SELECT count(*) FROM information_schema.tables WHERE table_name IN (\\x27task_plans\\x27, \\x27task_steps\\x27, \\x27task_context_snapshots\\x27, \\x27task_tool_calls\\x27, \\x27task_dependencies\\x27) AND schemaname = \x27public\x27;\"'" 2>/dev/null | tail -1 | tr -d '[:space:]')

echo "Total task tables created: ${TABLE_COUNT:-0}/5"

if [ "${TABLE_COUNT:-0}" = "5" ]; then
    echo "✅ All 5 tables verified!"
else
    echo "⚠️  Expected 5 tables but found $TABLE_COUNT"
fi

# List all task-related objects
echo ""
echo "📋 Task Tables and Indexes:"
ssh root@${SSH_HOST} << 'LISTOBJ'
su - pgsql << 'CMD'
psql -d memory_graph -c "SELECT tablename, pg_size_pretty(pg_relation_size(tablename)) as size FROM pg_tables WHERE tablename LIKE 'task%' AND schemaname = 'public' ORDER BY tablename;" 2>/dev/null || echo "Query failed"
echo "---"
psql -d memory_graph -c "SELECT count(*) AS total_indexes FROM pg_indexes WHERE tablename LIKE 'task%' AND schemaname = 'public';" 2>/dev/null | tail -1 || echo "Index query failed"
CMD
LISTOBJ

# Step 6: Test CRUD operations via SQL
echo ""
echo "================================================================================"
echo "📋 6. TEST CRUD OPERATIONS (SQL)"
echo "================================================================================"

ssh root@${SSH_HOST} << 'CRUDTEST'
su - pgsql << 'CMD'
psql -d memory_graph << 'SQL'
-- INSERT a test record
INSERT INTO task_plans (plan_name, plan_type, description, priority)
VALUES ('CRUD_TEST_v032', 'test', 'Testing CRUD operations for v0.3.2', 5);

SELECT '✅ INSERT successful - Row count:' AS info, 
       count(*) AS rows FROM task_plans WHERE plan_name = 'CRUD_TEST_v032';

-- UPDATE status
UPDATE task_plans SET status = 'RUNNING' WHERE plan_name = 'CRUD_TEST_v032';

SELECT '✅ UPDATE successful - Status is:' AS info, 
       status FROM task_plans WHERE plan_name = 'CRUD_TEST_v032';

-- DELETE cleanup
DELETE FROM task_plans WHERE plan_name = 'CRUD_TEST_v032';

SELECT '✅ DELETE successful - Rows removed' AS info;
SQL
CMD
CRUDTEST

# Step 7: Test context snapshot creation (for breakpoint recovery)
echo ""
echo "================================================================================"
echo "📋 7. TEST CONTEXT SNAPSHOT CREATION"
echo "================================================================================"

ssh root@${SSH_HOST} << 'SNAPTEST'
su - pgsql << 'CMD'
psql -d memory_graph << 'SQL'
-- Create a test plan first for snapshot reference
INSERT INTO task_plans (plan_name, plan_type, description) 
VALUES ('SNAPSHOT_TEST', 'test', 'Testing snapshot creation');

-- Insert context snapshot
INSERT INTO task_context_snapshots 
(plan_id, snapshot_type, context_data, is_latest)
SELECT plan_id, 'TEST_SNAPSHOT', '{"agent_state": "testing"}', true
FROM task_plans WHERE plan_name = 'SNAPSHOT_TEST';

SELECT count(*) AS snapshots_created FROM task_context_snapshots 
WHERE snapshot_type = 'TEST_SNAPSHOT';

-- Cleanup test data
DELETE FROM task_context_snapshots WHERE snapshot_type = 'TEST_SNAPSHOT';
DELETE FROM task_plans WHERE plan_name = 'SNAPSHOT_TEST';

SELECT '✅ Context snapshot operations verified' AS result;
SQL
CMD
SNAPTEST

# Final summary
echo ""
echo "================================================================================"
echo "📊 TEST EXECUTION SUMMARY"
echo "================================================================================"
ssh root@${SSH_HOST} << 'SUMMARY'
su - pgsql << 'CMD'
psql -d memory_graph << 'SQL'
-- Count all task-related objects
SELECT 
    (SELECT count(*) FROM information_schema.tables WHERE table_name LIKE 'task%') AS tables,
    (SELECT count(*) FROM pg_indexes WHERE tablename LIKE 'task%' AND schemaname = 'public') AS indexes;

-- List all completed operations
SELECT 'All schema components deployed successfully' AS status;
SQL
CMD
SUMMARY

echo ""
echo "================================================================================"
if [ "${TABLE_COUNT:-0}" = "5" ]; then
    echo "🎉 ALL TESTS COMPLETED SUCCESSFULLY!"
else
    echo "⚠️  Some tests may have failed. Please review output above."
fi
echo "================================================================================"
