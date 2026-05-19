# memory-pg18-by-yhw v0.3.3 Release Notes

**Release Date**: 2026-05-07  
**Version**: v0.3.3 (Multi-Agent Architecture Edition)  
**Author**: Haiwen Yin (胖头鱼 🐟)  

---

## 🆕 Major New Features in v0.3.3

### Multi-Agent Architecture Support

This is the most significant update, introducing a complete multi-agent coordination framework on top of PostgreSQL 18.

#### What's New:
1. **Agent Registry System** - Centralized agent lifecycle management with registration, capability discovery, and health monitoring
2. **Memory Access Control** - Fine-grained visibility policies (SHARED/PRIVATE/COLLABORATIVE) per agent
3. **Collaboration Framework** - Built-in communication channels for agent-to-agent coordination
4. **Session Management** - Active session tracking with state persistence

#### Database Schema Added:
- `agent_registry` - Agent lifecycle management table
- `agent_memory_access` - Memory access control policies  
- `agent_collaboration` - Inter-agent communication records
- `agent_session` - Session tracking and monitoring
- Views: `v_active_sessions`, `v_collaboration_status`

#### Python API Added:
- `AgentRegistryAPI` - Agent registration and discovery
- `MemoryVisibilityAPI` - Access policy management
- `CollaborationAPI` - Inter-agent messaging
- `AgentSessionAPI` - Session lifecycle management

---

## 📋 What's Included in This Release

### New Files Added:
| File | Size | Description |
|------|------|-------------|
| `scripts/init_multi_agent_schema.sql` | 6.5 KB | Multi-Agent DDL schema with views and seed data |
| `scripts/agent_api.py` | 10.7 KB | Python API for multi-agent coordination |

### Updated Files:
- `SKILL.md` - Added v0.3.3 Multi-Agent documentation (version bumped to v0.3.3)
- `README.md` - Updated feature comparison and documentation references
- `CHANGELOG.md` - Version history updated

---

## 🚀 Quick Migration Guide for Existing Users

### For v0.3.2 Users:

1. **Backup your database first** (always recommended before schema changes):
   ```bash
   pg_dump memory_graph > memory_graph_backup_v032.sql
   ```

2. **Deploy new Multi-Agent schema**:
   ```bash
   psql -U postgres -d memory_graph -f scripts/init_multi_agent_schema.sql
   ```

3. **Verify the deployment**:
   ```bash
   psql -U postgres -d memory_graph -c "SELECT * FROM v_active_sessions;"
   psql -U postgres -d memory_graph -c "SELECT agent_name, status FROM agent_registry;"
   ```

4. **Test the Python API**:
   ```python
   from scripts.agent_api import create_agent
   
   # Register a test agent
   agent = create_agent(
       agent_name="test-agent", 
       agent_type="general"
   )
   print(f"Created: {agent['agent_id']}")
   ```

---

## 📊 Version Comparison Matrix

| Feature | v0.3.2 | **v0.3.3** | Description |
|---------|--------|------------|-------------|
| PostgreSQL 18 Support | ✅ | ✅ | Core platform support |
| pgvector Integration | ✅ | ✅ | Vector embedding storage |
| Apache AGE Property Graph | ✅ | ✅ | Cypher query capabilities |
| HNSW Indexing | ✅ | ✅ | Fast semantic retrieval |
| Task Plan Persistence | ✅ | ✅ | Durable task tracking across sessions |
| Breakpoint Recovery | ✅ | ✅ | Resume exactly where interrupted after failures |
| Historical Pattern Learning | ✅ | ✅ | Learn from completed task patterns |
| **Agent Registry** | ❌ | ✅ | **NEW**: Centralized agent lifecycle management |
| **Memory Access Control** | ❌ | ✅ | **NEW**: Fine-grained visibility policies |
| **Collaboration Framework** | ❌ | ✅ | **NEW**: Agent-to-agent communication channels |
| **Session Management** | ❌ | ✅ | **NEW**: Active session tracking and monitoring |

---

## 🔧 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent Memory System                 │
│                      v0.3.3 Edition                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐            │
│  │ Agent A   │    │ Agent B   │    │ Agent C   │            │
│  │ (Analyzer)│    │(Writer)   │    │(Deployer)│             │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                    │
│        ▼                ▼                ▼                    │
│  ┌───────────────────────────────────────────────────────────┐│
│  │              AGENT_REGISTRY (Central)                     ││
│  │  • Registration & Lifecycle                               ││
│  │  • Capability Discovery                                   ││
│  │  • Health Monitoring                                      ││
│  └───────────────────────┬───────────────────────────────────┘│
│                          │                                     │
│                    ┌──────▼───────┐                           │
│  │    AGENT_MEMORY_ACCESS        │                                    │
│  │  • Visibility Policies        │                                    │
│  │  • Data Access Control        │                                    │
│  └───────────────────────────────┘                                    │
│                          │                                             │
│                    ┌──────▼───────┐                                    │
│  │    AGENT_COLLABORATION        │                                    │
│  │  • Communication Channels     │                                    │
│  │  • Cross-Agent Sharing       │                                    │
│  └───────────────────────────────┘                                    │
│                          │                                             │
│                    ┌──────▼───────┐                                    │
│  │    AGENT_SESSION             │                                    │
│  │  • Session Tracking         │                                    │
│  │  • State Management        │                                    │
│  └───────────────────────────────┘                                    │
│                          │                                             │
│                    ┌──────▼───────┐                                    │
│  │       MEMORIES TABLE          │                                    │
│  │    (Memory Storage Layer)     │                                    │
│  └───────────────────────────────┘                                    │
│                                                                      │
│    Benefits:                                                         │
│    ✅ Centralized Agent Management                                  │
│    ✅ Fine-Grained Memory Access Control                            │
│    ✅ Built-in Collaboration Framework                              │
│    ✅ Session State Persistence                                     │
│    ✅ Multi-Agent Scalability                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

---

## 📝 Summary of Changes

### What Changed (Breaking vs Non-Breaking):
- **Non-breaking**: All new features are additive; existing v0.3.2 functionality remains fully compatible
- **Schema additions**: New tables do NOT affect existing Task Plan or Memory tables
- **API additions**: Python API is purely additive, no changes to existing functions

### Upgrade Path:
1. v0.3.1 → v0.3.2 → v0.3.3 (sequential recommended)
2. OR v0.3.1 → v0.3.3 (skip directly, then deploy both schemas)

---

## 🔗 Related Documentation

- [SKILL.md](../SKILL.md) - Complete skill definition with Multi-Agent usage examples
- [README.md](../README.md) - Installation guide and architecture overview (v0.3.3 Edition)
- [CHANGELOG.md](../CHANGELOG.md) - Full version history

---

## 📧 Support & Feedback

For questions, bug reports, or feature requests:
- **GitHub Issues**: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/issues
- **Author Email**: haiwen.yin@csdn.net (via blog)
- **Blog**: https://blog.csdn.net/yhw1809

---

*Release Notes generated on 2026-05-07 by Haiwen Yin (胖头鱼 🐟)*