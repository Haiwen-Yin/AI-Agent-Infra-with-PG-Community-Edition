# memory-pg18-by-yhw v0.3.2 - Database Testing Guide

## Current Environment Status

**PG Server (10.10.10.131:5432):**
- ✅ Network reachable (ping successful)
- ❌ Cannot connect to port 5432 (Connection refused)
- ⚠️ Possible reasons: PG service not running, firewall blocking, or listening only on localhost

**Local Environment:**
- No local PostgreSQL installation
- No psql client available
- Podman available but pull timed out for postgres:18 image

---

## Testing Options

### Option 1: Run Tests via SSH (Recommended)

If you have access to the PG server, run tests there:

```bash
# Step 1: Install psycopg2 on remote server
ssh root@10.10.10.131 "pip3 install psycopg2-binary -q"

# Step 2: Copy test script to remote server
scp /root/.hermes/skills/memory-pg18-by-yhw/scripts/test_pg_v0_3_2.py \
    root@10.10.10.131:/tmp/

# Step 3: Run tests on PG server (use localhost)
ssh root@10.10.10.131 "python3 /tmp/test_pg_v0_3_2.py --host localhost"
```

### Option 2: Manual Testing Steps

Execute these commands on any machine with psql client and access to PG18:

#### Step 1: Check PG Service Status
```bash
# On remote server
systemctl status postgresql-18
# or
pg_lsclusters
```

#### Step 2: Verify Port Listening
```bash
ss -tlnp | grep :5432
# Should show something like: LISTEN 0 128 *:5432 *:* users:(("postgres",pid=123,fd=6))
```

If not listening on `*:5432`, check postgresql.conf:
```bash
grep listen_addresses /var/lib/pgsql/18/data/postgresql.conf
# Should be: listen_addresses = '*'  or include the IP
```

#### Step 3: Deploy Schema
```bash
psql -U postgres -d memory_graph -f scripts/init_task_plan_system.sql
```

Expected output should show CREATE TABLE and CREATE INDEX statements.

#### Step 4: Verify Tables Created
```bash
psql -U postgres -d memory_graph << 'SQL'
SELECT count(*) FROM information_schema.tables 
WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots', 
                      'task_tool_calls', 'task_dependencies');
-- Expected result: 5
SQL
```

#### Step 5: Check Indexes Exist
```bash
psql -U postgres -d memory_graph << 'SQL'
SELECT indexname, tablename 
FROM pg_indexes 
WHERE tablename LIKE 'task%' 
AND schemaname = 'public'
ORDER BY indexname;
-- Expected: ~11+ indexes (idx_task_plans_*, idx_task_steps_*, etc.)
SQL
```

#### Step 6: Test CRUD Operations
```bash
psql -U postgres -d memory_graph << 'SQL'
-- Create task plan
INSERT INTO task_plans (plan_name, plan_type, description, priority)
VALUES ('Test CRUD', 'test', 'Testing CRUD operations', 3);

-- Read the created plan
SELECT plan_id, plan_name, status FROM task_plans 
WHERE plan_name = 'Test CRUD';

-- Update status
UPDATE task_plans SET status = 'RUNNING' 
WHERE plan_name = 'Test CRUD';

-- Verify update
SELECT plan_id, status FROM task_plans WHERE plan_name = 'Test CRUD';

-- Cleanup
DELETE FROM task_plans WHERE plan_name = 'Test CRUD';
SQL
```

#### Step 7: Test Python API (requires psycopg2)
```bash
pip3 install psycopg2-binary -q

# Create test file
cat > /tmp/test_api.py << 'PYEOF'
from scripts.task_plan_api import create_task_plan, resume_task

# Create task plan
plan = create_task_plan(
    plan_name="API Test",
    plan_type="test",
    description="Test via Python API"
)

print(f"✅ Created: {plan['plan_id']}")

# Resume (should work even without interruption)
context = resume_task(plan_id=plan['plan_id'])
if context.get('restored_context'):
    print("✅ Breakpoint recovery works!")
else:
    print("⚠️  No snapshot found - may need to run create first")

PYEOF

# Run with correct paths
cd /root/.hermes/skills/memory-pg18-by-yhw && python3 /tmp/test_api.py
```

---

## Test Results Expected

### Schema Deployment (Step 4 & 5)
| Component | Count | Status |
|-----------|-------|--------|
| Tables | 5 | ✅ task_plans, task_steps, task_context_snapshots, task_tool_calls, task_dependencies |
| Indexes | ≥11 | ✅ idx_task_plans_*, idx_task_steps_*, etc. |

### CRUD Operations (Step 6)
| Operation | Expected Result |
|-----------|-----------------|
| INSERT INTO task_plans | Returns plan_id |
| SELECT from task_plans | Found row with correct data |
| UPDATE status → 'RUNNING' | Status changed successfully |
| DELETE cleanup | Row removed |

### Python API (Step 7)
| Function | Expected Behavior |
|----------|-------------------|
| create_task_plan() | Creates plan + auto-saves snapshot |
| resume_task() | Returns restored context or "No snapshot found" |
| search_completed_tasks() | Returns list of completed plans |

---

## Troubleshooting

### Issue: Connection Refused
**Solution:** Start PostgreSQL service on remote server
```bash
ssh root@10.10.10.131 "systemctl start postgresql-18"
```

### Issue: Authentication Failed
**Solution:** Check pg_hba.conf for passwordless access
```bash
# On PG server - add line if missing:
echo "host all postgres 127.0.0.1/32 trust" >> /var/lib/pgsql/18/data/pg_hba.conf
sudo systemctl reload postgresql-18
```

### Issue: Table Already Exists
**Solution:** The DDL uses CREATE TABLE IF NOT EXISTS - safe to re-run

---

## Verification Checklist

After running tests, verify:

- [ ] All 5 tables created successfully
- [ ] ≥11 indexes present on task_* tables
- [ ] INSERT/SELECT/UPDATE/DELETE all work
- [ ] Python API functions callable without errors
- [ ] Context snapshots being saved correctly

---

**Last Updated:** 2026-05-04  
**Version:** v0.3.2  
**Author:** Haiwen Yin (胖头鱼 🐟)
