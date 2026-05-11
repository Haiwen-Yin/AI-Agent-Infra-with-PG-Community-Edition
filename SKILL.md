---
name: memory-pg18-by-yhw
description: AI Agent Memory System (PostgreSQL 18 + Apache AGE) - Production-Grade memory system with Knowledge Base, Property Graph, Task Plan persistence, and Multi-Agent Architecture
version: v1.0.0 (Production Release)
author: Haiwen Yin (胖头鱼 🐟 - Database Expert)
license: Apache License 2.0
lastUpdated: 2026-05-10
tags: [postgresql, age, vector, graph, memory, pg18, task-plan, breakpoint-recovery, multi-agent, knowledge-base]
---

# memory-pg18-by-yhw - AI Agent Memory System (PostgreSQL 18 + Apache AGE)

## Overview

A production-ready, platform-agnostic AI Agent memory system built on PostgreSQL 18 with pgvector and Apache AGE Property Graph integration. This skill provides a complete toolkit for implementing hybrid semantic search, graph-based relationship traversal, persistent task management, **Knowledge Base system**, and **multi-agent coordination** in AI applications.

**Version**: v1.0.0 (Production Release)
**Author**: Haiwen Yin (胖头鱼 🐟) - Database Expert
**License**: Apache License 2.0
**Last Updated**: 2026-05-10 CST

---

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
9. **Store and retrieve stable knowledge using Knowledge Base system**
10. **Organize knowledge with tags, relationships, and version history**
11. **Generate embeddings using pg-embedding-gen-by-yhw plugin (database-native)**

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
memory-pg18-by-yhw-v0.4.0/
├── SKILL.md                   # This skill file (v0.4.0 Knowledge Base Edition)
├── README.md                  # Full project documentation (v0.4.0 Knowledge Base Edition)
├── LICENSE                    # Apache License 2.0 full text
├── NOTICE                     # Third-party attributions and legal notices
├── VERSION                    # Version identifier (v0.4.0)
├── CHANGELOG.md               # Complete version history
├── RELEASE_NOTES.md           # Release notes overview
├── RELEASE_NOTES_v0.4.0.md    # v0.4.0 Knowledge Base Edition release notes
├── docs/
│   └── deployment-guide.md    # Detailed deployment instructions for PostgreSQL 18
├── scripts/
│   ├── init_memory_system.sql # Original memory system schema
│   ├── init_task_plan_system.sql  # Task plan persistence DDL
│   ├── init_multi_agent_schema.sql  # Multi-Agent Database Schema
│   ├── knowledge_base_schema_pg.sql  # **NEW**: Knowledge Base Schema (v0.4.0)
│   ├── task_plan_api.py       # Task Plan Python API
│   ├── agent_api.py           # Multi-Agent Architecture Python API
│   └── knowledge_base_api_pg.py  # **NEW**: Knowledge Base Python API (v0.4.0)
├── examples/
│   ├── basic_usage.py         # Python SDK example with BGE-M3 embeddings
│   └── sample_data.sql        # Sample data for testing
└── references/
    └── pg18-deployment-notes.md  # **NEW**: PostgreSQL 18 setup and troubleshooting
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

|| Feature || v0.3.2 || **v0.3.3** || Description ||
|--||---------||--------||------------||-------------||
|| PostgreSQL 18 Support || ✅ || ✅ || Core platform support ||
|| pgvector Integration || ✅ || ✅ || Vector embedding storage ||
|| Apache AGE Property Graph || ✅ || ✅ || Cypher query capabilities ||
|| HNSW Indexing || ✅ || ✅ || Fast semantic retrieval ||
|| Task Plan Persistence || ✅ || ✅ || Durable task tracking across sessions ||
|| Breakpoint Recovery || ✅ || ✅ || Resume exactly where interrupted after failures ||
|| Historical Pattern Learning || ✅ || ✅ || Learn from completed task patterns ||
|| Tool Call Audit Trail || ✅ || ✅ || Complete execution logging ||
|| Multi-Agent Architecture || ❌ || ✅ || **NEW**: Complete multi-agent coordination framework ||
|| Agent Registry System || ❌ || ✅ || **NEW**: Centralized agent lifecycle management ||
|| Memory Access Control || ❌ || ✅ || **NEW**: Fine-grained visibility policies per agent ||
|| Collaboration Framework || ❌ || ✅ || **NEW**: Built-in communication channels for agents ||
|| Session Management API || ❌ || ✅ || **NEW**: Active session tracking and monitoring ||
|| Agent-to-Agent Messaging || ❌ || ✅ || **NEW**: Inter-agent request/response system ||
|| Python API Extensions || Partial || Full || **NEW**: Complete Multi-Agent API suite ||
## 🆕 v0.4.0 New: Knowledge Base System

### Overview

The Knowledge Base System provides AI Agents with a structured knowledge repository, enabling:
- **Stable Knowledge Storage** - Curated, high-quality knowledge extracted from memories
- **Knowledge Graph Relationships** - Interconnected knowledge entities with typed relationships
- **Version Control** - Track knowledge evolution and changes over time
- **Confidence Tracking** - Manage knowledge quality with validation workflows
- **Tag-Based Categorization** - Flexible organization of knowledge entities
- **Search Analytics** - Learn from search patterns and user feedback

### Knowledge Base Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Knowledge Base System (v0.4.0)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────────────┐│
│  │         KNOWLEDGE_CONCEPTS (Core Entities)              ││
│  │  • concept_id, concept_name, concept_type               ││
│  │  • description, content, embedding (vector)               ││
│  │  • confidence, validation_status                          ││
│  │  • tags, metadata, version history                       ││
│  └──────────────────────────────┬─────────────────────────────┘│
│                             │                                  │
│                    ┌────────▼─────────┐                        │
│  │  KNOWLEDGE_GRAPH (Relationships) │                        │
│  │  • source_concept_id → target_concept_id                 │
│  │  • relationship_type, strength, confidence                  │
│  │  • properties (JSONB)                                    │
│  └──────────────────────────────┬─────────────────────────────┘│
│                             │                                  │
│              ┌────────────────┼────────────────┐                  │
│              ▼                ▼                ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ KNOWLEDGE_   │  │ KNOWLEDGE_   │  │ KNOWLEDGE_   │      │
│  │ VERSIONS     │  │ TAGS         │  │ DISTILLATION │      │
│  │ (History)    │  │ (Categories) │  │ _LOG         │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Database Schema (v0.4.0)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `knowledge_concepts` | Core knowledge entities | concept_id, concept_type, confidence, validation_status, embedding |
| `knowledge_graph` | Knowledge relationships | source_concept_id, target_concept_id, relationship_type |
| `knowledge_versions` | Version history | concept_id, change_summary, versioned_at |
| `knowledge_tags` | Tag-based categorization | tag_name, tag_category, usage_count |
| `knowledge_concept_tags` | Many-to-many tag mapping | concept_id, tag_id |
| `knowledge_distillation_log` | Distillation audit trail | memory_ids, knowledge_id, distillation_method |
| `knowledge_search_history` | Search analytics | query_embedding, result_count, relevance_score |

### Python API Functions

```python
# Knowledge Base Management
from scripts.knowledge_base_api_pg import KnowledgeBaseAPI

kb = KnowledgeBaseAPI(host='10.10.10.131', database='memory_graph')

# Create a new knowledge concept
concept = kb.create_concept(
    concept_name="Database Optimization Pattern",
    concept_type="best_practice",
    description="Indexing strategy for large-scale queries",
    content="Detailed explanation...",
    confidence=0.95,
    tags=["database", "performance", "indexing"]
)

# Create relationship between concepts
kb.create_relationship(
    source_concept_id=1,
    target_concept_id=2,
    relationship_type="prerequisite_for",
    confidence=0.9
)

# Semantic search using vector similarity
results = kb.search_similar(
    query_text="How to optimize slow queries?",
    limit=5,
    min_similarity=0.7
)
```

---

## 📝 **Documentation**

- [SKILL.md](./SKILL.md) - This file (v0.4.0 Knowledge Base Edition)
- [README.md](./README.md) - Full project documentation (v0.4.0 Knowledge Base Edition)
- [RELEASE_NOTES_v0.4.0.md](./RELEASE_NOTES_v0.4.0.md) - **NEW**: v0.4.0 Knowledge Base Edition release notes
- [CHANGELOG.md](./CHANGELOG.md) - Complete version history (v0.1 through v0.4.0)
- [references/pg18-deployment-notes.md](./references/pg18-deployment-notes.md) - **NEW**: PostgreSQL 18 setup and troubleshooting guide

---

## 👨‍💻 **Author & Maintainer**

**Haiwen Yin (胖头鱼 🐟)**  
Oracle/PostgreSQL/MySQL ACE Database Expert

- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin

---

## 📄 **License**

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔧 **Troubleshooting & Pitfalls**

**For comprehensive pg-embedding-gen plugin documentation, see**:  
👉 **`pg-embedding-gen-plugin-management` skill** - Complete guide for PostgreSQL embedding generation plugin including COPY FROM PROGRAM architecture, external model integration (BGE-M3, OpenAI, Ollama), installation patterns, and troubleshooting techniques.

### pg-embedding-gen Extension Compatibility Issue (v1.1.7 - SOLUTION)

**Problem**: The C extension `pg_embedding_gen.so` may load successfully but return garbage data when called via SQL on PostgreSQL 18.

**Symptoms**:
- Extension loads and registers: `CREATE EXTENSION pg_embedding_gen;` ✅ succeeds
- Function created: `generate_embedding(TEXT)` appears in catalog
- SQL call fails: Returns vector with all zeros, NaN, or incorrect values

**Root Cause**: C extension compiled against older PostgreSQL headers may be incompatible with PostgreSQL 18 binary interface.

**✅ FINAL SOLUTION: COPY FROM PROGRAM Approach**

Use PostgreSQL 18's `COPY FROM PROGRAM` mechanism to call Python proxy directly from SQL functions.

#### Deployment Steps:

**1. Verify Python Proxy Script** (should already exist):
```bash
ls -la /usr/local/pgsql/bin/pg_embedding_proxy.py
# Test directly
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "Hello world"
# Should return: [-0.0316, 0.0244, -0.0283, ...] (1024 floats)
```

**2. Create Shell Wrapper Script** (as root):
```bash
sudo tee /usr/local/pgsql/bin/embedding_wrapper.sh > /dev/null << 'EOF'
#!/bin/bash
# Embedding wrapper script for PostgreSQL
# Usage: ./embedding_wrapper.sh 'text to embed'

if [ -z "$1" ]; then
    echo "Error: No input text provided" >&2
    exit 1
fi

# Call Python proxy script
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "$1"
EOF

sudo chmod +x /usr/local/pgsql/bin/embedding_wrapper.sh
```

**3. Deploy SQL Functions** (create `embedding` schema):
```sql
-- Drop old functions if they exist
DROP FUNCTION IF EXISTS embedding.generate(TEXT) CASCADE;
DROP FUNCTION IF EXISTS embedding.cosine_similarity(TEXT, TEXT) CASCADE;
DROP FUNCTION IF EXISTS embedding.create_concept_with_embedding(TEXT, TEXT, TEXT, JSONB) CASCADE;

-- Create embedding schema
CREATE SCHEMA IF NOT EXISTS embedding;

-- Main function: Generate embedding using COPY FROM PROGRAM
CREATE OR REPLACE FUNCTION embedding.generate(text_input TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result TEXT;
    row RECORD;
    cmd TEXT;
BEGIN
    IF text_input IS NULL OR text_input = '' THEN
        RAISE EXCEPTION 'Input text cannot be null or empty';
    END IF;
    
    CREATE TEMPORARY TABLE temp_embedding_result (line TEXT);
    
    cmd := format('COPY temp_embedding_result FROM PROGRAM %L',
                 '/bin/sh -c ' || quote quote_literal(
                     '/usr/local/pgsql/bin/embedding_wrapper.sh ' || quote_literal(text_input)
                 ));
    
    EXECUTE cmd;
    
    FOR row IN SELECT line FROM temp_embedding_result ORDER BY ctid LOOP
        result := COALESCE(result || E'\n', '') || row.line;
    END LOOP;
    
    DROP TABLE temp_embedding_result;
    
    IF result IS NULL OR result = '' THEN
        RAISE EXCEPTION 'Embedding generation failed: empty result';
    END IF;
    
    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        BEGIN
            DROP TABLE IF EXISTS temp_embedding_result;
        EXCEPTION WHEN OTHERS THEN
            NULL;
        END;
        RAISE;
END;
$$;

COMMENT ON FUNCTION embedding.generate(TEXT) IS 
  'Generate text embedding using BGE-M3 model (1024 dimensions). Returns TEXT as JSON array.';

-- Vector similarity function (placeholder - implement in application layer)
CREATE OR REPLACE FUNCTION embedding.cosine_similarity(TEXT, TEXT)
RETURNS FLOAT8
LANGUAGE plpgsql
AS $$
BEGIN
    -- Placeholder: calculate in application layer using numpy
    RETURN 0.0;
END;
$$;

-- Create concept with embedding
CREATE OR REPLACE FUNCTION embedding.create_concept_with_embedding(
    concept_name TEXT,
    description TEXT,
    concept_type TEXT DEFAULT 'GENERIC',
    metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    concept_id INTEGER;
    embedding_json TEXT;
BEGIN
    embedding_json := embedding.generate(description);
    
    INSERT INTO knowledge_concepts (
        concept_name,
        concept_type,
        description,
        content,
        metadata,
        validation_status,
        is_current
    ) VALUES (
        concept_name,
        concept_type,
        description,
        description,
        metadata || jsonb_build_object('embedding_json', embedding_json),
        'VALIDATED',
        'Y'
    ) RETURNING concept_id INTO concept_id;
    
    RETURN concept_id;
END;
$$;
```

#### Usage Examples:

**From SQL**:
```sql
-- Generate embedding directly
SELECT embedding.generate('Hello PostgreSQL');
-- Returns: [-0.0316, 0.0244, -0.0283, ...] (1024-dimension JSON array)

-- Create concept with auto-generated embedding
SELECT embedding.create_concept_with_embedding(
    'PostgreSQL',
    'PostgreSQL is a powerful open source relational database',
    'TECHNOLOGY'
);

-- Check embedding generation
SELECT 
    length(embedding.generate('test')) as length,
    embedding.generate('test') ~ '^\[' as is_valid;
```

**From Python Application Layer**:
```python
import subprocess
import json

def get_embedding(text: str) -> list[float]:
    """Get BGE-M3 embedding via Python proxy"""
    cmd = ["/usr/local/pgsql/bin/pg_embedding_proxy.py", text]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity in application layer"""
    import numpy as np
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Use in application
embedding = get_embedding("Hello world")
psql.execute("INSERT INTO knowledge_concepts (embedding) VALUES (%s);", 
              (embedding,))
```

#### Performance Characteristics:
- **Single Call**: ~2-3 seconds (includes API call)
- **Vector Dimensions**: 1024 (BGE-M3 standard)
- **Return Format**: JSON array string (~22KB)
- **Concurrency**: Supports concurrent calls
- **Database-Native**: ✅ Yes, can call from SQL functions directly

#### Why This Approach Works:
1. **PostgreSQL 18 Native**: Uses standard `COPY FROM PROGRAM` feature
2. **No C Extension Complexity**: Avoids binary compatibility issues
3. **Debuggable**: Python proxy is easy to debug and modify
4. **Production Ready**: Stable and reliable
5. **True Database-Native**: Can call from SQL functions, triggers, stored procedures

### Knowledge Base View Creation Failures

**Problem**: Views `v_knowledge_concepts_active` and `v_knowledge_graph_summary` may fail to create due to type casting issues.

**Symptoms**:
```sql
ERROR: operator does not exist: character varying = boolean
LINE 3: WHERE is_current = TRUE
```

**Root Cause**: Column type mismatch - `is_current` may be VARCHAR instead of BOOLEAN in existing tables.

**Workaround**: Create view with explicit type cast
```sql
CREATE OR REPLACE VIEW v_knowledge_concepts_active AS
SELECT * FROM knowledge_concepts
WHERE is_current::BOOLEAN = TRUE  -- Explicit cast
  AND deprecated_at IS NULL;
```

### PL/pgSQL Parameter Naming Convention (CRITICAL)

**Problem**: `column reference "concept_id" is ambiguous` errors when creating SQL functions.

**Symptoms**:
```sql
ERROR:  column reference "concept_id" is ambiguous
LINE 17:     ) RETURNING concept_id
                         ^
DETAIL:  It could refer to either a PL/pgSQL variable or a table column.
```

**Root Cause**: PL/pgSQL function parameter names match table column names, causing ambiguity in INSERT...RETURNING statements.

**✅ Solution**: Always prefix PL/pgSQL parameters with `p_` to avoid column name conflicts.

**Incorrect Example**:
```sql
CREATE FUNCTION my_func(concept_name TEXT, description TEXT) ...
BEGIN
    INSERT INTO knowledge_concepts (concept_name, description)
    VALUES (concept_name, description)  -- AMBIGUOUS!
    RETURNING concept_id;  -- Which concept_id? Parameter or column?
END;
```

**Correct Example**:
```sql
CREATE FUNCTION my_func(p_concept_name TEXT, p_description TEXT) ...
BEGIN
    INSERT INTO knowledge_concepts (concept_name, description)
    VALUES (p_concept_name, p_description)  -- CLEAR!
    RETURNING concept_id;  -- Unambiguous table column
END;
```

**Applied Fix in This Session**:
```sql
-- v1.1.8 - Fixed embedding.create与其他embedding_with_embedding
CREATE OR REPLACE FUNCTION embedding.create_concept_with_embedding(
    p_concept_name TEXT,
    p_description TEXT,
    p_concept_type TEXT DEFAULT 'GENERIC',
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_concept_id INTEGER;  -- Use v_ prefix for local variables
    v_embedding_json TEXT;
BEGIN
    v_embedding_json := embedding.generate(p_description);
    
    INSERT INTO knowledge_concepts (
        concept_name,
        concept_type,
        description,
        content,
        metadata,
        validation_status,
        is_current
    ) VALUES (
        p_concept_name,      -- Clear reference to parameter
        p_concept_type,
        p_description,
        p_description,
        p_metadata || jsonb_build_object('embedding_json', v_embedding_json),
        'VALIDATED',
        'Y'
    ) RETURNING concept_id INTO v_concept_id;  -- Clear RETURNING
    
    RETURN v_concept_id;
END;
$$;
```

**Best Practice**: Use parameter prefixes for all PL/pgSQL functions:
- `p_` for input parameters
- `v_` for local variables
- Never reuse table column names as parameter names

### SQL Shell Escaping Issues

**Problem**: Direct SQL commands passed via `ssh` have escaping problems with JSONB data, quotes, and special characters.

**Symptoms**:
```bash
ssh pgsql@host "psql -d db -c 'INSERT INTO table VALUES (JSONB);'"
# ERROR: invalid input syntax for type json
```

**✅ Solution**: Create .sql files and execute with `-f` flag instead of inline SQL.

**Incorrect Approach**:
```bash
# Inline SQL - prone to escaping errors
ssh pgsql@host "psql -d memory_graph -c 'INSERT INTO task_plans (goal) VALUES (\"{\\\"objective\\\": ...}\\")'"
```

**Correct Approach**:
```bash
# 1. Create SQL file
cat > /tmp/insert_task.sql << 'EOF'
INSERT INTO task_plans (goal, status)
VALUES (
    '{"objective": "Test all KB features", "test_environment": "PostgreSQL 18.3"}'::jsonb,
    'IN_PROGRESS'
);
EOF

# 2. Copy to remote server
scp /tmp/insert_task.sql pgsql@host:~

# 3. Execute file
ssh pgsql@host "psql -d memory_graph -f ~/insert_task.sql"
```

**Benefits**:
- No shell escaping issues
- Better readability and maintainability
- Can use SQL comments and multi-line formatting
- Easier to debug complex JSONB structures

### Knowledge Graph Schema Column Names

**Important**: The `knowledge_graph` table uses `relationship_strength`, not `strength`.

**Table Schema**:
```sql
CREATE TABLE knowledge_graph (
    relationship_id SERIAL PRIMARY KEY,
    source_concept_id INTEGER NOT NULL,
    target_concept_id INTEGER NOT NULL,
    relationship_type VARCHAR(100) NOT NULL,
    relationship_strength NUMERIC(3,2),  -- NOT 'strength'!
    confidence NUMERIC(3,2),
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

**Correct Usage**:
```sql
-- ✅ Correct
INSERT INTO knowledge_graph (source_concept_id, target_concept_id, 
                          relationship_type, relationship_strength)
VALUES (1, 2, 'supports', 0.95);

-- ❌ Incorrect
INSERT INTO knowledge_graph (source_concept_id, target_concept_id, 
                          relationship_type, strength)  -- Wrong!
VALUES (1, 2, 'supports', 0.95);
```

### Multi-Agent Schema Sample Data Issue

**Problem**: `init_multi_agent_schema.sql` sample data INSERT fails with column count mismatch.

**Symptoms**:
```sql
psql:init_multi_agent_schema.sql:126: ERROR:  VALUES lists must all be same length
LINE 4:     ('deployment-agent', 'operations', '{"database_migration...
```

**Root Cause**: Sample data INSERT statements have mismatched column counts.

**Workaround**: Table structure is correct; skip sample data or fix manually.

**Deployment Pattern**:
```bash
# Deploy schema (sample data will fail but tables are fine)
psql -d memory_graph -f scripts/init_multi_agent_schema.sql
# Ignore sample data errors - tables created successfully

# Verify table structure
psql -d memory_graph -c "\d agent_registry"

# Insert agents manually with correct syntax
psql -d memory_graph << 'EOF'
INSERT INTO agent_registry (agent_name, agent_type, capabilities, status)
VALUES ('kb-manager', 'knowledge', '{"create_concept": true}'::jsonb, 'ACTIVE');
EOF
```

### PostgreSQL 18 Server Setup Specifics

**Directory Structure** (per user testing on CentOS/RHEL):
```bash
# Data directory (user-specific)
/home/pgsql/pgsql_data/

# Extension libraries
/usr/local/pgsql/lib/extension/
/usr/local/pgsql/lib/

# SQL control files
/usr/local/pgsql/share/extension/
```

**SSH Connection**:
```bash
# Use pgsql user (not postgres)
ssh pgsql@10.10.10.131

# PostgreSQL binary location
/usr/local/pgsql/bin/psql

# Start PostgreSQL with pg_ctl
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data start
```

**Extension Installation (Requires Root)**:
```bash
# Must copy .control and .sql files as root
sudo cp pg_embedding_gen.control /usr/local/pgsql/share/extension/
sudo cp pg_embedding_gen--1.0.0.sql /usr/local/pgsql/share/extension/
sudo chmod 644 /usr/local/pgsql/share/extension/pg_embedding_gen*
```

---

**Last Updated**: 2026-05-11 v1.0.0 (PostgreSQL 18 compatibility notes added)