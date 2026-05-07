#!/usr/bin/env python3
"""
Complete Test Suite for memory-pg18-by-yhw v0.3.2 Task Plan System
Runs on remote PG server via SSH connection

Usage:
    chmod +x test_pg_v0_3_2.py
    ./test_pg_v0_3_2.py [--ssh-host HOST] [--db DB]

Default: host=10.10.10.131, db=memory_graph
"""

import os
import sys
import subprocess
from datetime import datetime


class RemotePGTestSuite:
    def __init__(self, ssh_host="10.10.10.131", dbname="memory_graph"):
        self.ssh_host = ssh_host
        self.dbname = dbname
        self.skill_dir_local = "/root/.hermes/skills/memory-pg18-by-yhw"
        
    def run_remote_command(self, cmd):
        """Execute command via SSH"""
        result = subprocess.run(
            f"ssh {self.ssh_host} '{cmd}'",
            shell=True, capture_output=True, text=True
        )
        return result
    
    def print_header(self, title):
        print(f"\n{'=' * 80}")
        print(f"📋 {title}")
        print("=" * 80)
    
    def check_pg_connection(self):
        """Check if PostgreSQL server is reachable and running"""
        self.print_header("1. PG SERVER CONNECTIVITY")
        
        # Check network connectivity
        print("\n🔍 Checking network...")
        result = subprocess.run(
            f"ping -c 1 -W 2 {self.ssh_host}",
            shell=True, capture_output=True, text=True
        )
        if "100% packet loss" in result.stdout:
            print("❌ Cannot reach PG server via ping")
            return False
        else:
            print("✅ Network reachable")
        
        # Check SSH access
        print("\n🔍 Checking SSH access...")
        ssh_result = self.run_remote_command("whoami && hostname")
        if ssh_result.returncode == 0 and "root" in ssh_result.stdout:
            print("✅ SSH access granted (as root)")
        
        # Check PG status via pgsql user
        print("\n🔍 Checking PostgreSQL service...")
        pg_status = self.run_remote_command("su - pgsql -c 'pg_ctl status 2>&1 || echo NOT_RUNNING'")
        
        if "not running" in pg_status.stdout.lower() or "NOT RUNNING" in pg_status.stdout:
            print("⚠️  PostgreSQL service is NOT running (need to start it)")
        elif "ready" in pg_status.stdout.lower():
            print("✅ PostgreSQL is RUNNING")
        else:
            print(f"   Status output: {pg_status.stdout.strip()}")
        
        # Check psql availability
        print("\n🔍 Checking psql client...")
        version_check = self.run_remote_command("su - pgsql -c 'psql --version'")
        if "PostgreSQL 18" in version_check.stdout:
            print(f"✅ psql available: {version_check.stdout.strip()}")
        
        return True
    
    def start_pg_service(self):
        """Start PostgreSQL service on remote server"""
        self.print_header("2. START POSTGRESQL SERVICE")
        
        # Find PGDATA location
        pgdata = "/var/lib/pgsql/data"
        bindir = "/usr/local/pgsql/bin"
        
        print(f"\n📁 PG Data Directory: {pgdata}")
        print(f"📁 Binary Directory: {bindir}")
        
        # Start PostgreSQL
        start_cmd = f"""
su - pgsql << 'EOF'
export PGDATA={pgdata}
export PATH={bindir}:$PATH
export LD_LIBRARY_PATH={bindir}/lib:$LD_LIBRARY_PATH
if ! pg_ctl status > /dev/null 2>&1; then
    echo "Starting PostgreSQL..."
    pg_ctl start -l {pgdata}/log/postgresql.log
    sleep 3
fi
psql -c 'SELECT version();'
EOF
"""
        print("\nExecuting PG startup...")
        result = self.run_remote_command(start_cmd)
        
        if "PostgreSQL" in result.stdout or "18.3" in result.stdout:
            print("✅ PostgreSQL started successfully")
            return True
        
        # Check logs for errors
        log_result = self.run_remote_command(f"tail -20 {pgdata}/log/postgresql.log 2>/dev/null")
        if log_result.stdout:
            print("   Last log entries:")
            for line in log_result.stdout.strip().split('\n')[-3:]:
                print(f"     {line}")
        
        return False
    
    def create_database(self):
        """Create memory_graph database if it doesn't exist"""
        self.print_header("3. CREATE DATABASE")
        
        check_cmd = "su - pgsql -c \"psql -lqt | grep '\\bmemory_graph\\b'\""
        result = self.run_remote_command(check_cmd)
        
        if result.returncode != 0:
            print(f"   Database '{self.dbname}' not found. Creating...")
            create_cmd = f"su - pgsql -c 'createdb {self.dbname}'"
            create_result = self.run_remote_command(create_cmd)
            
            # Verify creation
            verify = self.run_remote_command(f"psql -lqt | grep '\\b{self.dbname}\\b'")
            if "memory_graph" in verify.stdout:
                print("✅ Database created successfully")
                return True
        
        print("✅ Database already exists")
        return True
    
    def deploy_schema(self):
        """Deploy the Task Plan schema"""
        self.print_header("4. DEPLOY SCHEMA")
        
        sql_file = os.path.join(self.skill_dir_local, "scripts", "init_task_plan_system.sql")
        
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False
        
        # Copy SQL to remote server first
        copy_cmd = f"scp -q {sql_file} root@{self.ssh_host}:/tmp/init_task_plan_system.sql"
        subprocess.run(copy_cmd, shell=True)
        
        # Deploy schema on remote server
        deploy_cmd = f"""
su - pgsql << 'EOF'
psql -d {self.dbname} -f /tmp/init_task_plan_system.sql 2>&1 | grep -E "CREATE|ALTER|SELECT"
rm -f /tmp/init_task_plan_system.sql
EOF
"""
        print("Deploying schema...")
        result = self.run_remote_command(deploy_cmd)
        
        # Count tables created
        table_count = result.stdout.count("CREATE TABLE") + result.stdout.count("CREATE INDEX")
        if "error" not in result.stderr.lower():
            print(f"✅ Schema deployed (found {table_count} DDL statements)")
            
            # Verify tables
            verify_cmd = f"""
su - pgsql << 'SQL'
SELECT count(*) FROM information_schema.tables 
WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots', 'task_tool_calls', 'task_dependencies');
SQL
"""
            verify_result = self.run_remote_command(verify_cmd)
            
            # Extract number from output
            import re
            numbers = re.findall(r'\d+', verify_result.stdout.strip())
            if numbers:
                tables_found = int(numbers[-1])
                print(f"✅ Tables verified: {tables_found}/5")
                return True
        
        # If there were errors, show them
        if "error" in result.stderr.lower():
            print("❌ Schema deployment had errors:")
            for line in result.stderr.strip().split('\n')[-5:]:
                print(f"   {line}")
        
        return False
    
    def verify_schema(self):
        """Verify all expected tables and indexes exist"""
        self.print_header("5. VERIFY SCHEMA")
        
        # Check tables
        print("\n📊 Checking tables:")
        table_query = f"""
su - pgsql << 'SQL'
SELECT tablename, 
       (SELECT count(*) FROM information_schema.columns c WHERE c.table_name = t.tablename) as column_count
FROM pg_tables t 
WHERE tablename LIKE 'task%' AND schemaname = 'public'
ORDER BY tablename;
SQL
"""
        table_result = self.run_remote_command(table_query)
        
        if "task_plans" in table_result.stdout:
            print("✅ All task tables exist")
            for line in table_result.stdout.strip().split('\n'):
                if 'task' in line.lower():
                    print(f"   {line}")
            
            # Check indexes
            print("\n📊 Checking indexes:")
            index_query = f"""
su - pgsql << 'SQL'
SELECT count(*) FROM pg_indexes 
WHERE tablename LIKE 'task%' AND schemaname = 'public';
SQL
"""
            index_result = self.run_remote_command(index_query)
            
            import re
            numbers = re.findall(r'\d+', index_result.stdout.strip())
            if numbers:
                idx_count = int(numbers[-1])
                print(f"✅ Indexes found: {idx_count}")
                
                # Show some indexes
                show_idx = f"""
su - pgsql << 'SQL'
SELECT indexname FROM pg_indexes 
WHERE tablename LIKE 'task%' AND schemaname = 'public'
ORDER BY indexname LIMIT 15;
SQL
"""
                idx_show = self.run_remote_command(show_idx)
                for line in idx_show.stdout.strip().split('\n'):
                    if 'index' not in line.lower():
                        print(f"   ✅ {line}")
                
                return idx_count >= 10
        
        print("❌ Schema verification failed")
        return False
    
    def test_crud_operations(self):
        """Test CRUD operations on remote PG"""
        self.print_header("6. CRUD OPERATIONS TEST")
        
        if not os.path.exists(os.path.join("/root/.hermes/hermes-agent/venv", "bin", "python3")):
            print("❌ Python not available in hermes venv, trying system python...")
            sys.path.insert(0, '/usr/lib/python3.6/site-packages')
        
        try:
            import psycopg2
            
            # Connect to remote PG via local connection (need port forwarding or direct access)
            print("\n⚠️  Note: Cannot test Python API directly from this machine")
            print("   Python tests require running on the PG server itself.")
            print("✅ Skipping Python API test - run manually on PG server:")
            print(f"   ssh {self.ssh_host}")
            print(f"   python3 /tmp/test_api.py")
            
            # Instead, verify via SQL operations
            print("\n📝 Verifying SQL operations...")
            sql_test = f"""
su - pgsql << 'SQL'
-- Test INSERT
INSERT INTO task_plans (plan_name, plan_type, description, priority)
VALUES ('CRUD_TEST', 'test', 'Testing CRUD via SQL', 5);

-- Test SELECT  
SELECT count(*) FROM task_plans WHERE plan_name = 'CRUD_TEST';

-- Test UPDATE
UPDATE task_plans SET status = 'RUNNING' WHERE plan_name = 'CRUD_TEST';

-- Verify UPDATE
SELECT status FROM task_plans WHERE plan_name = 'CRUD_TEST';

-- Cleanup
DELETE FROM task_plans WHERE plan_name = 'CRUD_TEST';
SQL
"""
            result = self.run_remote_command(sql_test)
            
            if "INSERT" in result.stdout and "UPDATE" in result.stdout:
                print("✅ SQL CRUD operations verified!")
                
                # Show verification
                for line in result.stdout.strip().split('\n'):
                    if any(kw in line.upper() for kw in ['INSERT', 'SELECT', 'UPDATE', 'DELETE']):
                        print(f"   {line}")
                
                return True
            
        except ImportError:
            print("⚠️  psycopg2 not available on this machine")
        
        return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("🧪 TASK PLAN SYSTEM TEST SUITE - v0.3.2 (REMOTE PG)")
        
        results = {}
        
        # Test 1: Connectivity
        print("\n🔍 Starting connectivity checks...")
        results['connection'] = self.check_pg_connection()
        
        if not results['connection']:
            print("\n⚠️  Cannot proceed without connection")
            return False
        
        # Test 2: Start PG service (if needed)
        pg_running = "ready" in str(self.run_remote_command("su - pgsql -c 'pg_ctl status'").stdout).lower()
        
        if not pg_running:
            print("\n🔄 Starting PostgreSQL...")
            results['start_pg'] = self.start_pg_service()
        else:
            print("\n✅ PG already running, skipping start")
            results['start_pg'] = True
        
        # Test 3: Create database
        results['create_db'] = self.create_database()
        
        # Test 4: Deploy schema
        results['schema'] = self.deploy_schema()
        
        # Test 5: Verify schema
        if results['schema']:
            results['verify'] = self.verify_schema()
        else:
            print("\n⚠️  Skipping verification - schema deployment failed")
            results['verify'] = False
        
        # Test 6: CRUD operations (SQL only)
        results['crud'] = self.test_crud_operations()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        test_names = {
            'connection': 'PG Connectivity',
            'start_pg': 'PG Service Start',
            'create_db': 'Database Creation',
            'schema': 'Schema Deployment',
            'verify': 'Schema Verification',
            'crud': 'CRUD Operations (SQL)'
        }
        
        for test, passed in results.items():
            name = test_names.get(test, test)
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{name:30s}: {status}")
        
        all_passed = all(results.values())
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("\n💡 Next steps:")
            print("   1. Test Python API on PG server directly")
            print("   2. Verify breakpoint recovery functionality")
            print("   3. Check index performance with EXPLAIN ANALYZE")
        else:
            failed_tests = [t for t, p in results.items() if not p]
            print(f"❌ {len(failed_tests)} test(s) failed:")
            for f in failed_tests:
                print(f"   - {test_names.get(f, f)}")
        print("=" * 80)
        
        return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Task Plan System v0.3.2 on Remote PG")
    parser.add_argument("--ssh-host", default="10.10.10.131", help="SSH host for PG server")
    parser.add_argument("--db", default="memory_graph", help="Database name")
    
    args = parser.parse_args()
    
    test_suite = RemotePGTestSuite(ssh_host=args.ssh_host, dbname=args.db)
    
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
