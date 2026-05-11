# memory-pg18-by-yhw — PostgreSQL 18 AI Agent Memory System

**Version**: v1.0.0 (Production Release)  
**Created**: 2026-05-05  
**Updated**: 2026-05-11  
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**License**: Apache License, Version 2.0

---

## Overview

A universal memory system for AI Agents built on **PostgreSQL 18 with pgvector and Apache AGE extensions**, featuring complete Knowledge Base system, Task Plan persistence, and Multi-Agent architecture support.

### Key Features (v1.0.0)

#### Knowledge Base System
- **Knowledge Concepts** - Stable knowledge entities (FACT/RULE/PATTERN/EXPERIENCE/PRINCIPLE)
- **Knowledge Graph** - Property graph-based relationship management (IS_A/PART_OF/CAUSES/ENABLES/CONTRADICTS/SUPPORTS)
- **Version Control** - Complete version history for knowledge concepts
- **Validation Workflow** - Knowledge validation and approval process
- **Audit Trail** - Complete audit logging for all operations
- **Citation Tracking** - Knowledge concept citation relationships

#### Task Plan System
- **Persistent Task Storage** - Durable task tracking across sessions
- **Breakpoint Recovery** - Resume exactly where interrupted after failures
- **Historical Learning** - Learn from past task patterns and outcomes
- **Status Tracking** - Complete audit trail of all agent actions
- **Auto Snapshot** - Automatic context snapshots on progress updates

#### Multi-Agent Architecture
- **Agent Registry** - Centralized agent registration and discovery
- **Memory Visibility Control** - Three visibility levels (SHARED/PRIVATE/COLLABORATIVE)
- **Session Management** - Active session tracking with context preservation
- **Access Audit Trail** - Complete logging of memory access operations
- **Collaboration Workflow** - Request/approve mechanism for agent-to-agent knowledge sharing

#### Hybrid Search
- **Text Search** - Keyword-based full-text search
- **Semantic Search** - Vector similarity-based semantic search (pgvector HNSW indexing)
- **Graph Traversal** - Knowledge graph relationship queries

---

## Quick Start

### Prerequisites

- **PostgreSQL 18** (Required)
  - Must support pgvector and Apache AGE extensions
  - Download from [PostgreSQL](https://www.postgresql.org/download/)

- **Python 3.8+** (Required for Task Plan API)
  ```bash
  python3 --version
  pip install psycopg2-binary
  ```

---

## Installation

### Step 1: Install PostgreSQL 18 with Extensions

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

Create database if it doesn't exist:
```bash
psql -U postgres -c "CREATE DATABASE memory_graph;"
```

Deploy all schema components:
```bash
# Original memory system (v0.3.1)
psql -U postgres -d memory_graph -f scripts/init_memory_system.sql

# Task plan persistence (NEW v0.4.1)
psql -U postgres -d memory_graph -f scripts/init_task_plan_system.sql

# Multi-Agent Architecture (NEW v0.3.3)
psql -U postgres -d memory_graph -f scripts/init_multi_agent_schema.sql

# Knowledge Base System (NEW v1.0.0)
psql -U postgres -d memory_graph -f scripts/knowledge_base_schema_pg.sql
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

## Architecture

### Task Plan System

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
                    ┌──────▼─────────┐
                    │TASK_STEPS      │ ← Execution steps and results
                    └──────┬─────────┘
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

[Task Completed] ──► [search_completed_tasks()] ──► [Pattern learning and reuse]
```

### Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestrator Layer                   │
│  ┌───────────┐    ┌──────────┐    ┌──────────┐              │
│  │Coordinator│ ←→ │Specialist│ ←→ │Worker    │              │
│  │ (01)      │    │ (DB-01)  │    │ (Task-02)│              │
│  └─────┬─────┘    └─────┬────┘    └─────┬────┘              │
│        │                │               │                   │
│   ┌────▼────────────────▼───────────────▼─────┐             │
│   │         Collaboration & State Layer       │             │
│   │  collaboration_requests | shared_context  │             │
│   │  coordination_log     | agent_cache       │             │
│   └───────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## Testing Status

### v1.0.0 Complete Test Suite (24 Tests)

| Test Category | Tests | Pass | Fail |
|--------------|--------|-------|-------|
| Knowledge Base System | 6 | 6 | 0 |
| Task Plan System | 4 | 4 | 0 |
| Multi-Agent Architecture | 4 | 4 | 0 |
| Python API | 3 | 3 | 0 |
| Documentation | 4 | 4 | 0 |
| **Total** | **24** | **24** | **0** |

**Pass Rate**: 100%

### Test Environment

- **PostgreSQL Version**: 18.x
- **Host**: 10.10.10.131:5432
- **Database**: memory_graph
- **Extensions**: pgvector (0.8.2), Apache AGE (1.7.0)
- **Test Time**: 2026-05-11 20:10 (CST)

---

## Directory Structure

```
memory-pg18-by-yhw/
├── SKILL.md              # Complete skill documentation
├── README.md             # Project overview and quick start guide
├── LICENSE               # Apache License 2.0
├── NOTICE                # Copyright notice for Haiwen Yin/yhw
├── CHANGELOG.md          # Version history
├── VERSION               # Current version string
├── scripts/              # Helper scripts
│   ├── init_memory_system.sql    # Core schema DDL
│   ├── knowledge_base_schema_pg.sql # Knowledge Base Schema (v1.0.0)
│   ├── task_plan_api.py          # Task plan management API
│   ├── vector_similarity.py      # Vector similarity calculations
│   ├── agent_api.py             # Multi-Agent orchestration API
│   └── ...                       # Additional utilities
├── references/           # External documentation references
└── test_pg18_v1.0.0_complete.py  # Complete test suite
```

---

## Related Documentation

- [PostgreSQL 18 Documentation](https://www.postgresql.org/docs/18/) — Official documentation
- [pgvector Extension](https://github.com/pgvector/pgvector) — Vector similarity search
- [Apache AGE](https://age.apache.org/) — Property graph support
- [oracle-memory-by-yhw v1.0.0](../oracle-memory-by-yhw/) — Original version reference

---

## Author & Maintainer

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## License

This project is licensed under [Apache License, Version 2.0](LICENSE).

---

**Last Updated**: 2026-05-11 v1.0.0 (Production Release)
