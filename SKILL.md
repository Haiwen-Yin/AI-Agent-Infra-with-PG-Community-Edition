---
name: memory-pg18-by-yhw
description: AI Agent Memory System (PostgreSQL 18 + Apache AGE) - Hybrid semantic search, graph traversal, and Task Plan persistence toolkit for multi-agent applications with vector embeddings and relationship management.
version: v0.3.3
author: Haiwen Yin (胖头鱼 🐟 - Database Expert)
license: Apache License 2.0
lastUpdated: 2026-05-07
tags: [postgresql, age, vector, graph, memory, pg18, task-plan, breakpoint-recovery, multi-agent]
---

# memory-pg18-by-yhw - AI Agent Memory System (PostgreSQL 18 + Apache AGE)

## Overview

A production-ready, platform-agnostic AI Agent memory system built on PostgreSQL 18 with pgvector and Apache AGE Property Graph integration. This skill provides a complete toolkit for implementing hybrid semantic search, graph-based relationship traversal, persistent task management, **and multi-agent coordination** in AI applications.

**Version**: v0.3.3  
**Author**: Haiwen Yin (胖头鱼 🐟) - Database Expert  
**License**: Apache License 2.0  
**Last Updated**: 2026-05-07 CST

---

## 🎯 **What This Skill Does**

This skill enables you to:
1. Deploy a memory system with PostgreSQL 18 on any platform (bare metal, cloud) using standard Linux installation
2. Store AI knowledge as vectors (semantic embeddings) and concepts (graph nodes)
3. Perform hybrid search combining vector similarity + graph relationship traversal
4. Query relationships using Cypher for multi-hop reasoning
5. Scale to millions of records with HNSW indexing
6. **Manage persistent task plans across agent sessions**
7. **Recover task execution from breakpoints after failures**
8. **Learn from historical task patterns and completed executions**

---

## 🆕 v0.3.2 New: Task Plan Persistence System

### Overview

The Task Plan system provides AI Agents with durable task execution tracking, enabling:
- **Breakpoint recovery after failures** - Resume exactly where interrupted with full context
- **Historical pattern learning from completed tasks** - Learn from past success/failure modes
- **Detailed status auditing** - Complete audit trail of all agent actions

### Quick Start

```bash
# 1. Deploy Task Plan schema
psql -U postgres -d memory_graph -f scripts/init_task_plan_system.sql

# 2. Import Python API
from scripts.task_plan_api import create_task_plan, resume_task, search_completed_tasks

# 3. Create task plan with auto-snapshot
plan = create_task_plan(
    plan_name="Deploy Database Migration",
    plan_type="deployment",
    goal={"objective": "Migrate schema changes safely"}
)

# 4. Resume from breakpoint (if agent was interrupted)
context = resume_task(plan_id=plan['plan_id'])
```

### Task Plan Architecture

```
┌──────────────────────────────────────────────────────┐
│                   AI Agent Task Execution            │
└──────────────────────────────────────────────────────┘

[Agent] ──Start Task──► [create_task_plan()]
                         │
                  ┌──────▼───────┐
                  │ TASK_PLANS   │ ← Task plan (status, goals)
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │ TASK_STEPS   │ ← Execution steps and results
                  └──────┬───────┘
                         │
              [Executing...] ──► [update_task_progress()]
                              │
                       ┌──────▼──────────┐
                       │CONTEXT_SNAPSHOTS│ ← **Critical for breakpoint recovery**
                       └──────┬──────────┘
                              │
                    ┌─────────▼─────────┐
                    │  AGENT_STATE      │ ← Agent current state
                    │  CONVERSATION     │ ← Conversation history
                    │  NEXT_ACTION      │ ← Next action
                    │  MEMORY_IDS       │ ← Associated memory nodes
                    └───────────────────┘

[Exception/Interruption] ◄──► [resume_task()] ──► [Load latest snapshot to continue execution]
```

### Database Schema (Task Plan System)

Five new tables for task persistence:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `task_plans` | Core plan management | plan_id, status, goal(JSONB), priority |
| `task_steps` | Step execution tracking | step_order, action, tools_used(JSONB) |
| `task_context_snapshots` | Breakpoint recovery state | context_data(JSONB), is_latest(BOOLEAN), next_action |
| `task_tool_calls` | Tool call audit trail | tool_name, action, duration_ms |
| `task_dependencies` | Task dependency graph | source_plan_id, target_plan_id, condition(JSONB) |

### Python API Functions

```python
# Create new task plan with auto-snapshot
create_task_plan(
    plan_name="Deploy Database",
    plan_type="deployment",
    description="Execute production migration",
    goal={"objective": "Migrate safely"},
    steps=[
        {"order": 1, "name": "Backup current state"},
        {"order": 2, "name": "Execute migration script"}
    ]
)

# Resume from breakpoint
resume_task(plan_id=123)
# Returns: {"restored_context": {...}, "incomplete_steps": [...]}

# Search completed tasks for pattern learning
search_completed_tasks({"status": "SUCCESS", "type": "deployment"})
```

---

## 📦 **Package Contents**

```
memory-pg18-by-yhw-v0.3.3/
├── SKILL.md                   # This skill file (v0.3.3 Multi-Agent Edition)
├── README.md                  # Full project documentation (v0.3.3 Multi-Agent Edition)
├── LICENSE                    # Apache License 2.0 full text
├── NOTICE                     # Third-party attributions and legal notices
├── VERSION                    # Version identifier (v0.3.3)
├── CHANGELOG.md               # Complete version history
├── RELEASE_NOTES.md           # Release notes overview
├── RELEASE_NOTES_v0.3.2.md    # v0.3.2 release notes
├── RELEASE_NOTES_v0.3.3.md    # **NEW**: v0.3.3 Multi-Agent Edition release notes
├── docs/
│   └── deployment-guide.md    # Detailed deployment instructions for various platforms
├── scripts/
│   ├── init_memory_system.sql # Original memory system schema (v0.3.1)
│   ├── init_task_plan_system.sql  # Task plan persistence DDL (v0.3.2)
│   ├── task_plan_api.py       # Task Plan Python API (v0.3.2)
│   ├── agent_api.py           # **NEW**: Multi-Agent Architecture Python API (v0.3.3)
│   └── init_multi_agent_schema.sql  # **NEW**: Multi-Agent Database Schema (v0.3.3)
├── examples/
│   ├── basic_usage.py         # Python SDK example with BGE-M3 embeddings
│   └── sample_data.sql        # Sample data for testing
```

---

## 🚀 **Quick Start**

### Step 1: Install PostgreSQL 18 with Extensions (Standard Linux Installation)

For Ubuntu/Debian systems:
```bash
# Install PostgreSQL 18 and extensions
sudo apt update && sudo apt install postgresql-18 -y
sudo apt install postgresql-18-vector postgresql-18-age -y

# Start PostgreSQL service
sudo systemctl start postgresql@18-main
sudo systemctl enable postgresql@18-main
```

For CentOS/RHEL systems:
```bash
# Add PostgreSQL repository (example for RHEL 9)
curl https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/postgresql-pgdg-redhat-repo-latest.noarch.rpm | sudo rpm -Uvh

# Install PostgreSQL 18 with extensions
sudo yum install postgresql18-server postgresql18-vector postgresql18-age -y

# Initialize and start PostgreSQL
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb
sudo systemctl enable --now postgresql-18.service
```

### Step 2: Create Database and Schema

Create the database if it doesn't exist:
```bash
psql -U postgres -c "CREATE DATABASE memory_graph;"
```

Deploy all schema components:
```bash
# Original memory system (v0.3.1)
psql -U postgres -d memory_graph -f scripts/init_memory_system.sql

# Task plan persistence (NEW v0.3.2)
psql -U postgres -d memory_graph -f scripts/init_task_plan_system.sql
```

### Step 3: Use Python API for Task Management

```python
from scripts.task_plan_api import create_task_plan, resume_task

# Create task with auto-snapshot on creation
plan = create_task_plan(
    plan_name="Deploy Production Database",
    plan_type="deployment",
    description="Execute zero-downtime migration with rollback capability",
    goal={
        "objective": "Migrate schema changes safely without downtime",
        "risk_level": "high",
        "rollback_required": True,
        "estimated_duration_minutes": 45
    },
    steps=[
        {"order": 1, "name": "Backup current state"},
        {"order": 2, "name": "Execute migration script"},
        {"order": 3, "name": "Run validation queries"},
        {"order": 4, "name": "Update documentation"}
    ]
)

print(f"Created task: {plan['plan_id']} - {plan['plan_name']}")

# If agent was interrupted and needs to resume
context = resume_task(plan_id=plan['plan_id'])
if context.get('incomplete_steps'):
    print(f"Resuming from step: {context['next_action']}")
```

---

## 🆕 v0.3.3 New: Multi-Agent Architecture

### Overview

The Multi-Agent Architecture provides a structured framework for managing multiple AI agents with centralized memory access control, session management, and collaboration capabilities.

This edition introduces four new components:
- **Agent Registry (agent_registry)** - Centralized agent lifecycle management
- **Memory Access Control (agent_memory_access)** - Fine-grained visibility policies  
- **Collaboration Framework (agent_collaboration)** - Agent-to-agent communication channels
- **Session Management (agent_session)** - Active session tracking and monitoring

### Architecture Diagram (Multi-Agent System)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Multi-Agent Memory System                        │
│                      v0.3.3 Edition                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐                    │
│  │ Agent A   │    │ Agent B   │    │ Agent C   │                    │
│  │ (Analyzer)│    │(Writer)   │    │(Deployer) │                    │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘                    │
│        │                │                │                          │
│        ▼                ▼                ▼                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              AGENT_REGISTRY (Central)                         │  │
│  │  • Registration & Lifecycle                                   │  │
│  │  • Capability Discovery                                       │  │
│  │  • Health Monitoring                                          │  │
│  └───────────────────────┬───────────────────────────────────────┘  │
│                          │                                          │
│  ┌───────────────────────▼───────┐                                  │
│  │    AGENT_MEMORY_ACCESS        │                                  │
│  │  • Visibility Policies        │                                  │
│  │  • Data Access Control        │                                  │
│  └───────────────────────────────┘                                  │
│                          │                                          │
│  ┌───────────────────────▼───────┐                                  │
│  │    AGENT_COLLABORATION        │                                  │
│  │  • Communication Channels     │                                  │
│  │  • Cross-Agent Sharing        │                                  │
│  └───────────────────────────────┘                                  │
│                          │                                          │
│  ┌───────────────────────▼───────┐                                  │
│  │    AGENT_SESSION              │                                  │
│  │  • Session Tracking           │                                  │
│  │  • State Management           │                                  │
│  └───────────────────────────────┘                                  │
│                          │                                          │
│  ┌───────────────────────▼───────┐                                  │
│  │       MEMORIES TABLE          │                                  │
│  │    (Memory Storage Layer)     │                                  │
│  └───────────────────────────────┘                                  │
│                                                                     │
│    Benefits:                                                        │
│    ✅ Centralized Agent Management	                              │
│    ✅ Fine-Grained Memory Access Control	                          │
│    ✅ Built-in Collaboration Framework	                          │
│    ✅ Session State Persistence	                                  │
│    ✅ Multi-Agent Scalability	                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Quick Start (Multi-Agent)

```bash
# 1. Deploy Multi-Agent schema
psql -U postgres -d memory_graph -f scripts/init_multi_agent_schema.sql

# 2. Import Python API
from scripts.agent_api import create_agent, get_active_agents, create_session

# 3. Register an agent
agent = create_agent(
    agent_name="analysis-agent",
    agent_type="analytical",
    capabilities={"sql_query": True, "data_analysis": True}
)
print(f"Registered agent: {agent['agent_id']}")

# 4. Create a session
session = create_session(agent_id=agent['agent_id'])
print(f"Created session: {session['session_id']}")

# 5. List active agents
agents = get_active_agents()
for agent in agents:
    print(f"- {agent['agent_name']} ({agent['status']})")
```

### Python API Functions (Multi-Agent)

#### AgentRegistryAPI - Agent Lifecycle Management

```python
from scripts.agent_api import AgentRegistryAPI

registry = AgentRegistryAPI(conn_params={'host': 'localhost', 'database': 'memory_graph'})

# Register new agent
agent = registry.register_agent(
    agent_name="writing-agent",
    agent_type="content",
    capabilities={"text_generation": True, "editing": True},
    status="ACTIVE"
)

# Get agent details
agent_info = registry.get_agent(agent_id=1)

# List active agents
active_agents = registry.list_active_agents()
```

#### MemoryVisibilityAPI - Access Control

```python
from scripts.agent_api import MemoryVisibilityAPI

access_api = MemoryVisibilityAPI(conn_params={'host': 'localhost', 'database': 'memory_graph'})

# Set collaborative access (shared among specific agents)
access_api.set_access_policy(
    agent_id=1,
    memory_scope="COLLABORATIVE",
    accessible_to=[2, 3],  # Agents 2 and 3 can access
    can_read=True,
    can_write=False
)

# Get current policy
policy = access_api.get_access_policy(agent_id=1)
```

#### AgentSessionAPI - Session Management

```python
from scripts.agent_api import AgentSessionAPI

session_api = AgentSessionAPI(conn_params={'host': 'localhost', 'database': 'memory_graph'})

# Create session for agent execution
session = session_api.create_session(
    agent_id=1,
    task_plan_id=42  # Optional: link to a task plan
)

# Get all active sessions
active_sessions = session_api.get_active_sessions()

# End session when done
session_api.end_session(session['session_id'])
```

#### CollaborationAPI - Agent Communication

```python
from scripts.agent_api import CollaborationAPI

collab_api = CollaborationAPI(conn_params={'host': 'localhost', 'database': 'memory_graph'})

# Send collaboration request to another agent
request = collab_api.send_collaboration_message(
    source_agent_id=1,  # analysis-agent
    target_agent_id=2,  # writing-agent
    collab_type="REQUEST",
    message="Please generate documentation for this query result"
)

# Update request status when complete
collab_api.update_collaboration_status(request['collab_id'], "COMPLETED")

# Get all pending requests
pending = collab_api.get_pending_requests()
```

---

## 📊 **Feature Comparison**

### v0.3.1 vs v0.3.2 Feature Matrix

| Feature | v0.3.1 | **v0.3.2** | Description |
|---------|--------|------------|-------------|
| PostgreSQL 18 Support | ✅ | ✅ | Core platform support |
| pgvector Integration | ✅ | ✅ | Vector embedding storage |
| Apache AGE Property Graph | ✅ | ✅ | Cypher query capabilities |
| HNSW Indexing | ✅ | ✅ | Fast semantic retrieval |
| Task Plan Persistence | ❌ | ✅ | **NEW**: Durable task tracking across sessions |
| Breakpoint Recovery | ❌ | ✅ | **NEW**: Resume exactly where interrupted after failures |
| Historical Pattern Learning | ❌ | ✅ | **NEW**: Learn from completed task patterns |
| Tool Call Audit Trail | ❌ | ✅ | **NEW**: Complete execution logging |

---


### v0.3.2 vs v0.3.3 Feature Matrix

| Feature | v0.3.2 | **v0.3.3** | Description |
|---------|--------|------------|-------------|
| PostgreSQL 18 Support | ✅ | ✅ | Core platform support |
| pgvector Integration | ✅ | ✅ | Vector embedding storage |
| Apache AGE Property Graph | ✅ | ✅ | Cypher query capabilities |
| HNSW Indexing | ✅ | ✅ | Fast semantic retrieval |
| Task Plan Persistence | ✅ | ✅ | Durable task tracking across sessions |
| Breakpoint Recovery | ✅ | ✅ | Resume exactly where interrupted after failures |
| Historical Pattern Learning | ✅ | ✅ | Learn from completed task patterns |
| Tool Call Audit Trail | ✅ | ✅ | Complete execution logging |
| Multi-Agent Architecture | ❌ | ✅ | **NEW**: Complete multi-agent coordination framework |
| Agent Registry System | ❌ | ✅ | **NEW**: Centralized agent lifecycle management |
| Memory Access Control | ❌ | ✅ | **NEW**: Fine-grained visibility policies per agent |
| Collaboration Framework | ❌ | ✅ | **NEW**: Built-in communication channels for agents |
| Session Management API | ❌ | ✅ | **NEW**: Active session tracking and monitoring |
| Agent-to-Agent Messaging | ❌ | ✅ | **NEW**: Inter-agent request/response system |
| Python API Extensions | Partial | Full | **NEW**: Complete Multi-Agent API suite |
## 📝 **Documentation**

- [SKILL.md](./SKILL.md) - This file (v0.3.3 Multi-Agent Edition)
- [README.md](./README.md) - Full project documentation (v0.3.3 Multi-Agent Edition)
- [RELEASE_NOTES_v0.3.2.md](./RELEASE_NOTES_v0.3.2.md) - Detailed v0.3.2 release notes
- [CHANGELOG.md](./CHANGELOG.md) - Complete version history (v0.1 through v0.3.3)

---

## 👨‍💻 **Author & Maintainer**

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## 📄 **License**

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

**Last Updated**: 2026-05-04 v0.3.2