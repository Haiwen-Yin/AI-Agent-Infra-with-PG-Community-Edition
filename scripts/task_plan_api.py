#!/usr/bin/env python3
"""
Task Plan API for PostgreSQL 18 + pgvector
PostgreSQL 18 + pgvector integration for AI Agent task management

Features:
- Task plan persistence across sessions
- Breakpoint recovery after failures  
- Historical pattern learning from completed tasks
- Detailed status auditing

Usage:
    from scripts.task_plan_api import create_task_plan, resume_task, search_completed_tasks
    
Author: Haiwen Yin (胖头鱼 🐟)
Version: v0.3.2
License: Apache License 2.0
"""

import json
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class TaskPlanAPI:
    """Task Plan Management API for AI Agents"""
    
    def __init__(self, host="localhost", port=5432, database="memory_graph", 
                 user="postgres", password=""):
        self.host = host
        self.port = port  
        self.database = database
        self.user = user
        self.password = password
        
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password
        )
    
    def create_task_plan(self, plan_name: str, plan_type: str = "task", 
                        description: str = "", goal: Dict = None, 
                        steps: List[Dict] = None) -> Dict[str, Any]:
        """
        Create a new task plan and automatically save initial context snapshot
        
        Args:
            plan_name (str): Task name
            plan_type (str): task/deployment/research/analysis
            description (str): Task description
            goal (dict): Final goal (structured)
            steps (list[dict]): Step list [{order, name, action}, ...]
            
        Returns:
            dict: Created plan information
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Insert task plan
                cur.execute("""
                    INSERT INTO task_plans (plan_name, plan_type, description, goal)
                    VALUES (%s, %s, %s, %s) RETURNING *
                """, (plan_name, plan_type, description, json.dumps(goal)))
                
                new_plan = cur.fetchone()
                cursor_keys = ['plan_id', 'plan_name', 'plan_type', 'description', 
                             'goal', 'priority', 'created_at']
                
                result = {}
                for i, key in enumerate(cursor_keys):
                    val = new_plan[i]
                    if isinstance(val, bytes):
                        try:
                            val = json.loads(val.decode())
                        except:
                            pass
                    result[key] = val
                
                # Save initial context snapshot
                self._save_snapshot(conn, result['plan_id'], "INIT", {
                    "agent_state": "idle",
                    "conversation_history": [],
                    "next_action": f"Start task: {plan_name}"
                })
                
                # Add steps if provided
                if steps:
                    for step_info in steps:
                        cur.execute("""
                            INSERT INTO task_steps (plan_id, step_order, step_name, action)
                            VALUES (%s, %s, %s, %s)
                        """, (result['plan_id'], step_info.get('order', 1), 
                             step_info.get('name', ''), step_info.get('action', '')))
                
                conn.commit()
                return result
                
        finally:
            conn.close()
    
    def resume_task(self, plan_id: int) -> Dict[str, Any]:
        """
        Resume task execution from breakpoint
        
        Args:
            plan_id (int): Plan ID
            
        Returns:
            dict: Restored context information including next_action, incomplete_steps
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Get latest snapshot
                cur.execute("""
                    SELECT context_data FROM task_context_snapshots 
                    WHERE plan_id = %s AND is_latest = true ORDER BY created_at DESC LIMIT 1
                """, (plan_id,))
                
                row = cur.fetchone()
                if not row:
                    return {"error": "No snapshot found for this plan"}
                
                context_data = json.loads(row[0].decode()) if isinstance(row[0], bytes) else row[0]
                
                # Get incomplete steps
                cur.execute("""
                    SELECT step_order, step_name, action FROM task_steps 
                    WHERE plan_id = %s AND status IN ('PENDING', 'BLOCKED') 
                    ORDER BY step_order
                """, (plan_id,))
                
                incomplete_steps = []
                for srow in cur.fetchall():
                    incomplete_steps.append({
                        "order": srow[0],
                        "name": srow[1],
                        "action": srow[2]
                    })
                
                context_data["incomplete_steps"] = incomplete_steps
                return {"restored_context": context_data, "plan_id": plan_id}
                
        finally:
            conn.close()
    
    def search_completed_tasks(self, query_params: Dict[str, Any]) -> List[Dict]:
        """
        Search completed tasks for learning and pattern reuse
        
        Args:
            query_params (dict): {type, status, tags, keywords, date_range}
            
        Returns:
            list[dict]: Matching task list with success metrics and statistics
        """
        conn = self.get_connection()
        try:
            conditions = ["status = %s"] if query_params.get("status") else []
            params = [query_params.get("status", "SUCCESS")] if query_params.get("status") else []
            
            if query_params.get("type"):
                conditions.append("plan_type = %s")
                params.append(query_params["type"])
                
            # Build WHERE clause and execute
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT plan_id, plan_name, plan_type, status, created_at, priority
                    FROM task_plans 
                    WHERE {where_clause}
                    ORDER BY created_at DESC LIMIT 20
                """, params)
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        "plan_id": row[0],
                        "plan_name": row[1],
                        "plan_type": row[2], 
                        "status": row[3],
                        "created_at": str(row[4]) if row[4] else None,
                        "priority": row[5]
                    })
                
                return results
                
        finally:
            conn.close()
    
    def _save_snapshot(self, conn, plan_id, snapshot_type, context_data):
        """Save task context snapshot (internal)"""
        # Mark existing latest as not latest
        with conn.cursor() as cur:
            cur.execute("UPDATE task_context_snapshots SET is_latest = false WHERE plan_id = %s AND is_latest = true", (plan_id,))
            
            cur.execute("""
                INSERT INTO task_context_snapshots (plan_id, snapshot_type, context_data, is_latest)
                VALUES (%s, %s, %s, true)
            """, (plan_id, snapshot_type, json.dumps(context_data)))


# Convenience functions for direct use
def create_task_plan(plan_name, plan_type="task", description="", goal=None, steps=None):
    """Create a new task plan"""
    api = TaskPlanAPI()
    return api.create_task_plan(plan_name, plan_type, description, goal, steps)

def resume_task(plan_id):
    """Resume task execution from breakpoint"""
    api = TaskPlanAPI()
    return api.resume_task(plan_id)

def search_completed_tasks(query_params=None):
    """Search completed tasks for learning"""
    api = TaskPlanAPI()
    if query_params is None:
        query_params = {"status": "SUCCESS"}
    return api.search_completed_tasks(query_params)


if __name__ == "__main__":
    # Demo usage
    print("Task Plan API v0.3.2")
    print("=" * 50)
    
    # Create sample task plan
    result = create_task_plan(
        plan_name="Deploy Database Migration",
        plan_type="deployment",
        description="Execute production database migration with rollback capability",
        goal={
            "objective": "Migrate schema changes safely",
            "risk_level": "high",
            "rollback_required": True
        },
        steps=[
            {"order": 1, "name": "Backup current state"},
            {"order": 2, "name": "Execute migration script"},
            {"order": 3, "name": "Run validation queries"},
            {"order": 4, "name": "Update documentation"}
        ]
    )
    
    print(f"\n✅ Created task plan: {result['plan_id']} - {result['plan_name']}")
    print(f"   Status: {result.get('status', 'PENDING')}")

