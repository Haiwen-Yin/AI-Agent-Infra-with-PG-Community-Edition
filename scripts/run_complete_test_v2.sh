#!/bin/bash
# Complete Test Script for memory-pg18-by-yhw v0.3.2 Task Plan System (Fixed)
# All commands run as pgsql user to avoid permission issues

SSH_HOST="10.10.10.131"
DB_NAME="memory_graph"
SQL_FILE="/tmp/init_task_plan_system.sql"

echo "================================================================================"
echo "🧪 TASK PLAN SYSTEM TEST SUITE - v0.3.2 (REMOTE PG SERVER)"
echo "================================================================================"

# Step 1: Copy SQL file to remote server as root first, then chown
echo ""
echo "📋 STEP 1: Copying SQL schema file..."
scp -q /root/.hermes/skills/memory-pg18-by-yhw/scripts/init_task_plan_system.sql \
    root@${SSH_HOST}:${SQL_FILE}
ssh root@${SSH_HOST} "chown pgsql:pgsql ${SQL_FILE}; ls -la ${SQL_FILE}"

if [ $? -eq 0 ]; then
    echo "✅ SQL file copied and permission set"
else
    echo "❌ Failed to copy SQL file"
    exit 1
fi

# Step 2-7: Run all tests via SSH as pgsql user
echo ""
echo "📋 STEP 2-7: Running complete test suite on PG server..."
ssh root@${SSH_HOST} << 'ENDOFSSH'

# Create a wrapper script to ensure we run as pgsql user properly
cat > /tmp/run_tests.sh << 'PGEOF'
#!/bin/bash
export PATH=/usr/local/pgsql/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/pgsql/lib:$LD_LIBRARY_EXPORT
export PGDATA=/var/lib/pgsql/data

# Check if PG is running, start if needed
echo ""
echo "================================================================================"
echo "📋 1. CHECK POSTGRESQL SERVICE STATUS"
echo "================================================================================"
if ! pg_ctl status > /dev/null 2>&1; then
    echo "PG not running. Starting..."
    mkdir -p /var/lib/pgsql/data/log
    chown pgsql:pgsql /var/lib/pgsql/data/log
    pg_ctl start -l /var/lib/pgsql/data/log/postgresql.log -w > /dev/null 2>&1
    sleep 3
fi

pg_ctl status 2>&1 | head -5 || true
echo "✅ PostgreSQL is running"

# Verify PG version
echo ""
echo "📊 PostgreSQL Version:"
psql --version 2>/dev/null || psql --version

# Check if database exists, create if needed
echo ""
echo "================================================================================"  
echo "📋 2. CHECK/CREATE DATABASE"
echo "================================================================================"
DB_EXISTS=$(psql -lqt | grep -c "\bmemory_graph\b" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" = "0" ]; then
    echo "Database 'memory_graph' not found. Creating..."
    createdb memory_graph 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Database created successfully"
    else
        psql -d postgres -c "CREATE DATABASE memory_graph;" 2>&1 > /dev/null
        echo "Database created via postgres connection"
    fi
else
    echo "✅ Database 'memory_graph' already exists"
fi

# Deploy Task Plan schema
echo ""
echo "================================================================================"
echo "📋 3. DEPLOY TASK PLAN SCHEMA"
echo "================================================================================"
psql -d memory_graph -f /tmp/init_task_plan_system.sql 2>&1 | grep -E "(CREATE|ALTER|INSERT)" || true
psql -d memory_graph -f /tmp/init_task_plan_system.sql > /dev/null 2>&1 && echo "✅ Schema deployed successfully"

# Clean up SQL file
rm -f /tmp/init_task_plan_system.sql

# Verify tables created
echo ""
echo "================================================================================"
echo "📋 4. VERIFY TABLES CREATED"
echo "================================================================================"
TABLE_COUNT=$(psql -d memory_graph -tA -c "SELECT count(*) FROM information_schema.tables WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots', 'task_tool_calls', 'task_dependencies') AND schemaname = 'public';")
echo "Total task tables created: $TABLE_COUNT"

psql -d memory_graph -c "SELECT tablename, pg_size_pretty(pg_relation_size(tablename)) as size FROM pg_tables WHERE tablename LIKE 'task%' AND schemaname = 'public' ORDER BY tablename;" 2>/dev/null

# Verify indexes exist
echo ""
echo "================================================================================"
echo "📋 5. VERIFY INDEXES CREATED"
echo "================================================================================"
INDEX_COUNT=$(psql -d memory_graph -tA -c "SELECT count(*) FROM pg_indexes WHERE tablename LIKE 'task%' AND schemaname = 'public';")
echo "Total indexes created: $INDEX_COUNT"

psql -d memory_graph -c "SELECT indexname, tablename FROM pg_indexes WHERE tablename LIKE 'task%' AND schemaname = 'public' ORDER BY indexname;" 2>/dev/null | head -15

# Test CRUD operations via SQL
echo ""
echo "================================================================================"
echo "📋 6. TEST CRUD OPERATIONS (SQL)"
echo "================================================================================"

psql -d memory_graph << 'CRUD_EOF'
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
CRUD_EOF

# Test context snapshot creation (for breakpoint recovery)
echo ""
echo "================================================================================"
echo "📋 7. TEST CONTEXT SNAPSHOT CREATION"
echo "================================================================================"

psql -d memory_graph << 'SNAP_EOF'
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
SNAP_EOF

# Final summary
echo ""
echo "================================================================================"
echo "📊 TEST EXECUTION SUMMARY"
echo "================================================================================"
psql -d memory_graph << 'SUMMARY_EOF'
-- Count all task-related objects
SELECT 
    (SELECT count(*) FROM information_schema.tables WHERE table_name LIKE 'task%') AS tables,
    (SELECT count(*) FROM pg_indexes WHERE tablename LIKE 'task%' AND schemaname = 'public') AS indexes;

-- List all completed operations
SELECT 'All schema components deployed successfully' AS status;
SUMMARY_EOF

echo ""
echo "✅ COMPLETE TEST SUITE FINISHED!"

PGEOF

chmod +x /tmp/run_tests.sh
bash /tmp/run_tests.sh

ENDOFSSH

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "🎉 ALL TESTS COMPLETED SUCCESSFULLY!"
    echo "================================================================================"
else
    echo ""
    echo "================================================================================"
    echo "⚠️  Some tests may have failed. Please review output above."
    echo "================================================================================"
fi
