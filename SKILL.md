---
name: memory-pg18-by-yhw
description: AI Agent Memory System (PostgreSQL 18 + Apache AGE) - Hybrid semantic search, graph traversal, and Task Plan persistence toolkit for AI applications with vector embeddings and relationship management.
version: v0.3.2
author: Haiwen Yin (胖头鱼 🐟 - Database Expert)
license: Apache License 2.0
lastUpdated: 2026-05-04
tags: [postgresql, age, vector, graph, memory, pg18, task-plan, breakpoint-recovery]
---

# memory-pg18-by-yhw - AI Agent Memory System (PostgreSQL 18 + Apache AGE)

## Overview

A production-ready, platform-agnostic AI Agent memory system built on PostgreSQL 18 with pgvector and Apache AGE Property Graph integration. This skill provides a complete toolkit for implementing hybrid semantic search, graph-based relationship traversal, **and persistent task management** in AI applications.

**Version**: v0.3.2  
**Author**: Haiwen Yin (胖头鱼 🐟) - Database Expert  
**License**: Apache License 2.0  
**Last Updated**: 2026-05-04 CST

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
                       │ CONTEXT_SNAPSHOTS│ ← **Critical for breakpoint recovery**
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
memory-pg18-by-yhw-v0.3.2/
├── SKILL.md                   # This skill file (v0.3.2)
├── README.md                  # Full project documentation (English)
├── LICENSE                    # Apache License 2.0 full text
├── NOTICE                     # Third-party attributions and legal notices
├── VERSION                    # Version identifier (v0.3.2)
├── CHANGELOG.md               # Complete version history
├── docs/
│   └── deployment-guide.md    # Detailed deployment instructions for various platforms
├── scripts/
│   ├── init_memory_system.sql # Original memory system schema
│   ├── init_task_plan_system.sql  # **NEW**: Task plan persistence DDL
│   └── task_plan_api.py       # **NEW**: Python API functions (create/resume/search)
└── examples/
    ├── basic_usage.py         # Python SDK example with BGE-M3 embeddings
    └── sample_data.sql        # Sample data for testing
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

## 📝 **Documentation**

- [SKILL.md](./SKILL.md) - This file (skill definition and usage guide)
- [README.md](./README.md) - Full project documentation (v0.3.2 with Task Plan System)
- [RELEASE_NOTES_v0.3.2.md](./RELEASE_NOTES_v0.3.2.md) - Detailed v0.3.2 release notes
- [CHANGELOG.md](./CHANGELOG.md) - Complete version history

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