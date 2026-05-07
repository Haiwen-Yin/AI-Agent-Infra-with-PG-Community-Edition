#!/usr/bin/env python3
"""
Multi-Agent Architecture Python API for memory-pg18-by-yhw v0.3.3

Provides high-level functions for agent registry, access control, 
collaboration, and session management in PostgreSQL 18.

Supports both local connections and remote SSH tunneling to PG18 servers.

Author: Haiwen Yin (胖头鱼 🐟)
License: Apache License 2.0
"""

import json
import subprocess
from datetime import datetime
from typing import Optional, Dict, List, Any

# Default configuration for PG18 remote server
DEFAULT_PG18_CONFIG = {
    'host': '10.10.10.131',  # Remote PG18 server
    'port': 5432,
    'database': 'memory_graph',
    'user': 'pgsql',
    'use_ssh_tunnel': True  # Use SSH tunnel for remote connections
}

class PostgreSQLConnection:
    """Secure PostgreSQL connection handler with SSH tunneling support"""
    
    def __init__(self, conn_params: dict):
        self.conn_params = {**DEFAULT_PG18_CONFIG, **conn_params}
        
    def _get_psql_command(self) -> str:
        """Get psql command string for execution"""
        host = self.conn_params.get('host', 'localhost')
        port = self.conn_params.get('port', 5432)
        database = self.conn_params.get('database', 'memory_graph')
        user = self.conn_params.get('user', 'pgsql')
        
        if self.conn_params.get('use_ssh_tunnel'):
            # Connect via SSH to remote PG18 server
            return f"ssh {user}@{host} '/usr/local/pgsql/bin/psql -h localhost -p 5432 -U {user} -d {database}'"
        else:
            # Direct local connection
            return f"psql -h {host} -p {port} -U {user} -d {database}"
    
    def execute_sql(self, sql_query: str) -> tuple:
        """Execute SQL query via psql command and return (stdout, stderr, return_code)"""
        cmd = self._get_psql_command()
        
        try:
            result = subprocess.run(
                cmd, 
                input=sql_query.encode('utf-8'), 
                shell=True, 
                capture_output=True, 
                text=False,
                timeout=30
            )
            
            output_text = result.stdout.decode('utf-8', errors='replace')
            error_text = result.stderr.decode('utf-8', errors='replace')
            
            if result.returncode == 0:
                return (output_text.strip(), '', 0)
            else:
                # Return SQL error from stderr or output
                return ('', f"PostgreSQL Error (RC={result.returncode}): {error_text[:200]}", result.returncode)
                
        except subprocess.TimeoutExpired:
            return ('', 'Connection timeout - server may be unreachable', 1)
        except ConnectionRefusedError:
            if self.conn_params.get('use_ssh_tunnel'):
                return ('', f'SSH connection to {self.conn_params["host"]} failed. Please verify SSH access.', 1)
            else:
                return ('', 'Connection refused - PostgreSQL not running locally', 1)
        except FileNotFoundError:
            if self.conn_params.get('use_ssh_tunnel'):
                return ('', f'SSH command not found on local machine', 1)
            else:
                return ('', 'psql command not found', 1)
        except Exception as e:
            return ('', f'Connection error: {str(e)}', 1)

class AgentRegistryAPI:
    """Centralized agent lifecycle management API"""
    
    def __init__(self, conn_params: dict = None):
        if not conn_params:
            conn_params = DEFAULT_PG18_CONFIG.copy()
        self.conn = PostgreSQLConnection(conn_params)
        
    def register_agent(self, agent_name: str, agent_type: str = 'general', 
                       capabilities: dict = None, description: str = None,
                       status: str = 'ACTIVE') -> Dict[str, Any]:
        """Register a new AI agent"""
        caps_json = json.dumps(capabilities) if capabilities else '{}'
        
        # Escape single quotes in strings to prevent SQL injection
        safe_name = agent_name.replace("'", "''") if agent_name else ''
        safe_desc = (description or '').replace("'", "''")
        
        # Use tuples_only to get simple one-value-per-line output
        sql = f"\pset tuples_only true\n" + f"""
            INSERT INTO agent_registry (agent_name, agent_type, capabilities, 
                                       description, status)
            VALUES ('{safe_name}', '{agent_type}', '{caps_json}', '{safe_desc}', '{status}')
            RETURNING agent_id;
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            raise Exception(f"Failed to register agent: {stderr}")
        
        # Parse result - with tuples_only, first non-empty line is the ID
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if line and line.isdigit():
                return {
                    'agent_id': int(line),
                    'agent_name': agent_name,
                    'created_at': str(datetime.now()),
                    'status': status
                }
        
        raise Exception("Failed to parse agent registration result")
    
    def get_agent(self, agent_id: Optional[int] = None, agent_name: Optional[str] = None):
        """Get agent details"""
        if agent_id:
            sql = f"SELECT * FROM agent_registry WHERE agent_id = {agent_id};"
        else:
            safe_name = (agent_name or '').replace("'", "''")
            sql = f"SELECT * FROM agent_registry WHERE agent_name = '{safe_name}';"
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            return None
        
        lines = [line.strip() for line in stdout.split('\n') if line.strip()]
        if not lines:
            return None
        
        # Parse first data row (skip headers)
        data_row = next((l for l in lines if '|' in l and '---' not in l), None)
        if not data_row:
            return None
        
        parts = [p.strip() for p in data_row.split('|')]
        
        try:
            capabilities_str = parts[4] if len(parts) > 4 else '{}'
            capabilities = json.loads(capabilities_str) if isinstance(capabilities_str, str) and capabilities_str != '{}' else {}
            
            return {
                'agent_id': int(parts[0]),
                'agent_name': parts[1],
                'agent_type': parts[2],
                'status': parts[3],
                'capabilities': capabilities,
                'description': parts[5] if len(parts) > 5 else ''
            }
        except (ValueError, IndexError):
            return None
    
    def list_active_agents(self) -> List[Dict]:
        """List all active agents"""
        sql = "SELECT * FROM agent_registry WHERE status = 'ACTIVE';"
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            return []
        
        rows = [line.strip() for line in stdout.split('\n') if line.strip()]
        result = []
        
        for row in rows:
            # Skip header separators (---) and non-data lines (no |)
            if '---' in row or not ('|' in row):
                continue
            
            parts = [p.strip() for p in row.split('|')]
            try:
                capabilities_str = parts[4] if len(parts) > 4 else '{}'
                capabilities = json.loads(capabilities_str) if isinstance(capabilities_str, str) and capabilities_str != '{}' else {}
                
                result.append({
                    'agent_id': int(parts[0]),
                    'agent_name': parts[1],
                    'agent_type': parts[2],
                    'status': parts[3],
                    'capabilities': capabilities,
                    'description': parts[5] if len(parts) > 5 else ''
                })
            except (ValueError, IndexError):
                continue
        
        return result

class MemoryVisibilityAPI:
    """Fine-grained memory access control API"""
    
    def __init__(self, conn_params: dict = None):
        if not conn_params:
            conn_params = DEFAULT_PG18_CONFIG.copy()
        self.conn = PostgreSQLConnection(conn_params)
        
    def set_access_policy(self, agent_id: int, memory_scope: str = 'SHARED',
                         accessible_to: List[int] = None, can_read: bool = True,
                         can_write: bool = False) -> bool:
        """Set or update memory access policy for an agent"""
        scope_json = json.dumps(accessible_to) if accessible_to else '[]'
        
        sql = f"""
            INSERT INTO agent_memory_access (agent_id, memory_scope, accessible_to, 
                                            can_read, can_write)
            VALUES ({agent_id}, '{memory_scope}', '{scope_json}', {can_read}, {can_write})
            ON CONFLICT (agent_id, memory_scope) DO UPDATE SET
                accessible_to = EXCLUDED.accessible_to,
                can_read = EXCLUDED.can_read,
                can_write = EXCLUDED.can_write;
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        return rc == 0 and 'ERROR' not in stderr
    
    def get_access_policy(self, agent_id: int) -> Optional[Dict]:
        """Get current access policy"""
        sql = f"SELECT * FROM agent_memory_access WHERE agent_id = {agent_id};"
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            return None
        
        lines = [line.strip() for line in stdout.split('\n') if line.strip()]
        if not lines:
            return None
        
        data_row = next((l for l in lines if '|' in l and '---' not in l), None)
        if not data_row:
            return None
        
        parts = [p.strip() for p in data_row.split('|')]
        
        try:
            accessible_str = parts[3] if len(parts) > 3 else '[]'
            accessible_to = json.loads(accessible_str) if isinstance(accessible_str, str) and accessible_str != '[]' else []
            
            return {
                'access_id': int(parts[0]),
                'agent_id': int(parts[1]),
                'memory_scope': parts[2],
                'accessible_to': accessible_to,
                'can_read': bool(int(parts[4])) if len(parts) > 4 else True,
                'can_write': bool(int(parts[5])) if len(parts) > 5 else False
            }
        except (ValueError, IndexError):
            return None

class AgentSessionAPI:
    """Active session tracking and monitoring API"""
    
    def __init__(self, conn_params: dict = None):
        if not conn_params:
            conn_params = DEFAULT_PG18_CONFIG.copy()
        self.conn = PostgreSQLConnection(conn_params)
        
    def create_session(self, agent_id: int, task_plan_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new session for an agent"""
        # Use tuples_only to get simple one-value-per-line output
        sql = f"\pset tuples_only true\n" + f"""
            INSERT INTO agent_session (agent_id, task_plan_id, is_active)
            VALUES ({agent_id}, {task_plan_id if task_plan_id else 'NULL'}, true)
            RETURNING session_id;
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            raise Exception(f"Failed to create session: {stderr}")
        
        # Parse result - with tuples_only, first non-empty line is the session_id
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if line and line.isdigit():
                session_id = int(line)
                break
        started_at = str(datetime.now())
        
        # Get started_at from psql output if available, otherwise use current time
        try:
            lines = stdout.strip().split('\n')
            started_at = str(datetime.now())
            for line in lines:
                stripped = line.strip()
                # Look for timestamp pattern like '2026-05-07 19:03:49.540154'
                if '-' in stripped and ':' in stripped and len(stripped) > 10:
                    started_at = stripped.split()[-1] if ' ' in stripped else stripped
                    break
            
            return {
                'session_id': session_id,
                'started_at': started_at
            }
        except (ValueError, IndexError):
            raise Exception("Failed to parse session creation response")
    
    def end_session(self, session_id: int) -> bool:
        """End a session"""
        sql = f"""
            UPDATE agent_session 
            SET is_active = false, ended_at = CURRENT_TIMESTAMP
            WHERE session_id = {session_id};
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        return rc == 0 and 'ERROR' not in stderr
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        sql = "SELECT * FROM v_active_sessions ORDER BY started_at DESC;"
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            return []
        
        rows = [line.strip() for line in stdout.split('\n') if line.strip()]
        result = []
        
        for row in rows:
            # Skip header separators (---) and non-data lines (no |)
            if '---' in row or not ('|' in row):
                continue
            
            parts = [p.strip() for p in row.split('|')]
            try:
                result.append({
                    'session_id': int(parts[0]),
                    'agent_name': parts[1],
                    'agent_type': parts[2],
                    'is_active': bool(int(parts[3])) if len(parts) > 3 else True,
                    'started_at': parts[4] if len(parts) > 4 else '',
                    'actions_performed': int(parts[5]) if len(parts) > 5 else 0,
                    'tokens_used': int(parts[6]) if len(parts) > 6 else 0
                })
            except (ValueError, IndexError):
                continue
        
        return result

class CollaborationAPI:
    """Agent-to-agent communication channels"""
    
    def __init__(self, conn_params: dict = None):
        if not conn_params:
            conn_params = DEFAULT_PG18_CONFIG.copy()
        self.conn = PostgreSQLConnection(conn_params)
        
    def send_collaboration_message(self, source_agent_id: int, target_agent_id: int,
                                   collab_type: str = 'REQUEST', message: str = '',
                                   priority: int = 2) -> Dict[str, Any]:
        """Send a collaboration request to another agent"""
        
        # Escape single quotes in message
        safe_message = message.replace("'", "''") if message else ''
        
        # Use tuples_only to get simple one-value-per-line output
        sql = f"\pset tuples_only true\n" + f"""
            INSERT INTO agent_collaboration (source_agent_id, target_agent_id,
                                            collab_type, priority, message)
            VALUES ({source_agent_id}, {target_agent_id}, '{collab_type}', {priority}, '{safe_message}')
            RETURNING collab_id;
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            raise Exception(f"Failed to send collaboration request: {stderr}")
        
        # Parse result - with tuples_only, first non-empty line is the collab_id
        collab_id = None
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if line and line.isdigit():
                collab_id = int(line)
                break
        
        created_at = str(datetime.now())
        
        return {
            'collab_id': collab_id,
            'created_at': created_at
        }


    def update_collaboration_status(self, collab_id: int, status: str) -> bool:
        """Update collaboration status"""
        sql = f"""
            UPDATE agent_collaboration 
            SET status = '{status}', completed_at = CURRENT_TIMESTAMP
            WHERE collab_id = {collab_id};
        """
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        return rc == 0 and 'ERROR' not in stderr
    
    def get_pending_requests(self) -> List[Dict]:
        """Get all pending collaboration requests"""
        sql = "SELECT * FROM v_collaboration_status WHERE status = 'PENDING';"
        
        stdout, stderr, rc = self.conn.execute_sql(sql)
        
        if rc != 0 or 'ERROR' in stderr:
            return []
        
        rows = [line.strip() for line in stdout.split('\n') if line.strip()]
        result = []
        
        for row in rows:
            # Skip header separators (---) and non-data lines (no |)
            if '---' in row or not ('|' in row):
                continue
            
            parts = [p.strip() for p in row.split('|')]
            try:
                result.append({
                    'collab_id': int(parts[0]),
                    'source_agent': parts[1],
                    'target_agent': parts[2],
                    'collab_type': parts[3],
                    'status': parts[4],
                    'created_at': parts[5] if len(parts) > 5 else ''
                })
            except (ValueError, IndexError):
                continue
        
        return result

# Convenience functions

def create_agent(agent_name: str, agent_type: str = 'general', conn_params: dict = None):
    """Quick function to register an agent"""
    if not conn_params:
        conn_params = DEFAULT_PG18_CONFIG.copy()
    
    registry = AgentRegistryAPI(conn_params)
    return registry.register_agent(agent_name, agent_type)

def get_active_agents(conn_params: dict = None):
    """Quick function to list active agents"""
    if not conn_params:
        conn_params = DEFAULT_PG18_CONFIG.copy()
    
    registry = AgentRegistryAPI(conn_params)
    return registry.list_active_agents()

def create_session(agent_id: int, conn_params: dict = None):
    """Quick function to create a session"""
    if not conn_params:
        conn_params = DEFAULT_PG18_CONFIG.copy()
    
    session_api = AgentSessionAPI(conn_params)
    return session_api.create_session(agent_id)
