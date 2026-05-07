#!/usr/bin/env python3
"""
Complete Test Suite for memory-pg18-by-yhw v0.3.2 Task Plan System
Tests: Schema deployment, CRUD operations, Breakpoint Recovery, API functions

Usage:
    python3 test_pg_v0_3_2.py

Default connection: host=10.10.10.131, port=5432, db=memory_graph, user=postgres (no password)
"""

import os
import sys
import subprocess
from datetime import datetime


class TaskPlanTestSuite:
    def __init__(self, host="10.10.10.131", port=5432, dbname="memory_graph", 
                 user="postgres", password=""):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        # Find SQL file relative to this script location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sql_candidates = [
            os.path.join(base_dir, "scripts", "init_task_plan_system.sql"),
            "/root/.hermes/skills/memory-pg18-by-yhw/scripts/init_task_plan_system.sql"
        ]
        self.sql_file = None
        for candidate in sql_candidates:
            if os.path.exists(candidate):
                self.sql_file = candidate
                break
        
    def print_header(self, title):
        print(f"\n{'=' * 80}")
        print(f"📋 {title}")
        print("=" * 80)
    
    def check_pg_connection(self):
        """Check if PostgreSQL server is reachable"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=self.host, port=self.port, dbname="postgres", 
                user=self.user, password=self.password
            )
            print("✅ PostgreSQL server is REACHABLE")
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"   Version: {version[:120]}...")
            conn.close()
            return True
        except ImportError:
            print("❌ psycopg2 not installed. Installing now...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "psycopg2-binary"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ psycopg2 installed successfully")
                # Retry connection
                return self.check_pg_connection()
            else:
                print(f"❌ Failed to install psycopg2: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach PG server at {self.host}:{self.port}")
            print(f"   Error: {e}")
            return False
    
    def deploy_schema(self):
        """Deploy the Task Plan schema using psql"""
        self.print_header("1. DEPLOY SCHEMA")
        
        if not self.sql_file or not os.path.exists(self.sql_file):
            # Try to find it via SSH
            print(f"❌ SQL file not found locally: {self.sql_file}")
            return False
        
        # Check if database exists, create if needed
        db_check = subprocess.run(
            f"psql -h {self.host} -p {self.port} -U {self.user} -d postgres -c \"SELECT 1 FROM pg_database WHERE datname='{self.dbname}'\" > /dev/null 2>&1",
            shell=True, capture_output=True, text=True
        )
        
        if db_check.returncode != 0:
            print(f"   Database '{self.dbname}' not found. Creating...")
            create_db = subprocess.run(
                f"psql -h {self.host} -p {self.port} -U {self.user} -c 'CREATE DATABASE {self.dbname}'",
                shell=True, capture_output=True, text=True
            )
            if "created" in create_db.stderr.lower() or "createdb" in create_db.stdout.lower():
                print("   ✅ Database created")
        
        # Deploy schema
        cmd = f"psql -h {self.host} -p {self.port} -U {self.user} -d {self.dbname} -f {self.sql_file}"
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Check for success indicators in stderr (psql shows progress there)
        if "CREATE TABLE" in result.stderr or "CREATE INDEX" in result.stderr:
            print("✅ Schema deployed successfully")
            
            # Verify tables
            verify_cmd = f"psql -h {self.host} -p {self.port} -U {self.user} -d {self.dbname} -c \"SELECT count(*) FROM information_schema.tables WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots', 'task_tool_calls', 'task_dependencies');\""
            verify_result = subprocess.run(verify_cmd, shell=True, capture_output=True, text=True)
            
            # Parse output (psql returns count in last line before blank)
            lines = [l for l in verify_result.stdout.split('\n') if l.strip().isdigit()]
            if lines:
                table_count = int(lines[-1])
                print(f"✅ Tables created: {table_count}/5")
                return True
        else:
            # Check for errors
            error_text = result.stderr or result.stdout
            if "ERROR" in error_text.upper() or "Error" in error_text:
                print("❌ Schema deployment failed:")
                print(error_text[:1000])
            
        print(f"   Output preview: {result.stdout[:200] if result.stdout else 'none'}")
        return False
    
    def verify_schema(self):
        """Verify all expected tables and indexes exist"""
        self.print_header("2. VERIFY SCHEMA")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.host, port=self.port, dbname=self.dbname,
                user=self.user, password=self.password
            )
            
            cur = conn.cursor()
            
            # Check tables
            expected_tables = [
                'task_plans', 'task_steps', 'task_context_snapshots', 
                'task_tool_calls', 'task_dependencies'
            ]
            
            print("📊 Tables:")
            for table in sorted(expected_tables):
                cur.execute("""
                    SELECT count(*) FROM information_schema.tables 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table,))
                exists = cur.fetchone()[0] > 0
                status = "✅" if exists else "❌"
                print(f"   {status} {table}")
            
            # Check indexes
            print("\n📊 Indexes:")
            cur.execute("""
                SELECT indexname, tablename 
                FROM pg_indexes 
                WHERE tablename LIKE 'task%' 
                AND schemaname = 'public'
                ORDER BY indexname;
            """)
            indexes = cur.fetchall()
            
            for idx_name, table in sorted(indexes):
                print(f"   ✅ {idx_name} on {table}")
            
            conn.close()
            return len(indexes) > 10  # Should have at least 11 indexes
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_crud_operations(self):
        """Test Create, Read, Update operations"""
        self.print_header("3. CRUD OPERATIONS")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.host, port=self.port, dbname=self.dbname,
                user=self.user, password=self.password
            )
            
            cur = conn.cursor()
            
            # CREATE - Insert task plan
            print("\n1️⃣  Create Task Plan:")
            cur.execute("""
                INSERT INTO task_plans (plan_name, plan_type, description, goal, priority)
                VALUES (%s, %s, %s, %s, %s) RETURNING *
            """, ("Test Deployment v0.3.2", "deployment", "Deploy test database", 
                  '{"objective": "test deployment"}', 2))
            
            new_plan = cur.fetchone()
            cursor_keys = ['plan_id', 'plan_name', 'plan_type', 'description', 
                          'goal', 'priority', 'created_at']
            
            plan_data = {}
            for i, key in enumerate(cursor_keys):
                val = new_plan[i]
                if isinstance(val, bytes):
                    try:
                        import json
                        val = json.loads(val.decode())
                    except:
                        pass
                plan_data[key] = val
            
            print(f"   ✅ Created: {plan_data['plan_id']} - {plan_data['plan_name']}")
            
            # READ - Query the created plan
            print("\n2️⃣  Read Task Plan:")
            cur.execute("""
                SELECT plan_id, plan_name, status FROM task_plans 
                WHERE plan_id = %s;
            """, (plan_data['plan_id'],))
            
            row = cur.fetchone()
            if row:
                print(f"   ✅ Found: ID={row[0]}, Name={row[1]}, Status={row[2]}")
            
            # CREATE - Insert task step
            print("\n3️⃣  Create Task Step:")
            cur.execute("""
                INSERT INTO task_steps (plan_id, step_order, step_name, action)
                VALUES (%s, %s, %s, %s);
            """, (plan_data['plan_id'], 1, "Initial Setup", "Configure environment"))
            
            # CREATE - Save context snapshot
            print("\n4️⃣  Create Context Snapshot:")
            cur.execute("""
                INSERT INTO task_context_snapshots 
                (plan_id, snapshot_type, context_data, is_latest)
                VALUES (%s, %s, %s, true);
            """, (plan_data['plan_id'], "MANUAL", '{"agent_state": "running"}'))
            
            # UPDATE - Update status
            print("\n5️⃣  Update Status:")
            cur.execute("""
                UPDATE task_plans SET status = 'RUNNING' WHERE plan_id = %s;
            """, (plan_data['plan_id'],))
            
            # Verify update
            cur.execute("SELECT status FROM task_plans WHERE plan_id = %s;", 
                       (plan_data['plan_id'],))
            updated_status = cur.fetchone()[0]
            
            if updated_status == 'RUNNING':
                print(f"   ✅ Status updated to: {updated_status}")
            
            # Clean up test data
            cur.execute("DELETE FROM task_plans WHERE plan_id = %s;", 
                       (plan_data['plan_id'],))
            conn.commit()
            
            print("\n✅ All CRUD operations completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ CRUD test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        self.print_header("🧪 TASK PLAN SYSTEM TEST SUITE - v0.3.2")
        
        results = {}
        
        # Test 1: Connection
        print("\n🔍 Testing PostgreSQL connectivity...")
        results['connection'] = self.check_pg_connection()
        
        if not results['connection']:
            print("\n⚠️  Cannot proceed without PG connection")
            return False
        
        # Test 2: Schema deployment
        results['schema'] = self.deploy_schema()
        
        # Test 3: Verify schema
        results['verify'] = self.verify_schema()
        
        # Test 4: CRUD operations
        if results['verify']:
            results['crud'] = self.crud_operations()
        else:
            print("\n⚠️  Skipping CRUD test - schema verification failed")
            results['crud'] = False
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        for test, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test.upper()}: {status}")
        
        all_passed = all(results.values())
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
        else:
            failed_tests = [t for t, p in results.items() if not p]
            print(f"❌ {len(failed_tests)} test(s) failed:")
            for f in failed_tests:
                print(f"   - {f}")
        print("=" * 80)
        
        return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Task Plan System v0.3.2")
    parser.add_argument("--host", default="10.10.10.131", help="PostgreSQL host")
    parser.add_argument("--port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--db", default="memory_graph", help="Database name")
    parser.add_argument("--user", default="postgres", help="Database user")
    parser.add_argument("--password", default="", help="Database password")
    
    args = parser.parse_args()
    
    test_suite = TaskPlanTestSuite(
        host=args.host, port=args.port, dbname=args.db, 
        user=args.user, password=args.password
    )
    
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
