# CHANGELOG

All notable changes to memory-pg18-by-yhw will be documented in this file.

## [v0.3.2] - 2026-05-04

### Added
- **Task Plan Persistence System**: Complete task tracking with 5 new database tables
  - `task_plans` - Core plan management (status, goals, priority)
  - `task_steps` - Step-by-step execution tracking
  - `task_context_snapshots` - Critical state snapshots for breakpoint recovery
  - `task_tool_calls` - Complete tool call audit trail
  - `task_dependencies` - Task dependency graph
- **Breakpoint Recovery API**: Resume exactly where interrupted after failures
- **Task Pattern Learning**: Search completed tasks for historical pattern reuse
- **Python Task Plan API**: Three core functions (create_task_plan, resume_task, search_completed_tasks)
- **PostgreSQL JSONB Optimizations**: Native JSON indexing capabilities over TEXT storage
- **TIMESTAMPTZ Support**: Timezone-aware timestamps across all tables

### Changed
- Updated VERSION to 0.3.2
- Enhanced SKILL.md with Task Plan System documentation
- Updated README.md feature comparison table (v0.3.1 → v0.3.2)

### Files Added
- `scripts/init_task_plan_system.sql` - Task Plan DDL schema
- `scripts/task_plan_api.py` - Python API functions
- `RELEASE_NOTES_v0.3.2.md` - Detailed release notes

---

## [v0.3.1] - 2026-04-30

### Added
- Dual-mode embedding generation via pg-embedding-gen-by-ywh extension
- BGE-M3 vector dimension standardization (1024 dimensions)
- Chinese language embedding optimization notes
- Comprehensive deployment guide for multiple platforms
- Apache AGE 1.7.0 compatibility documentation for PostgreSQL 18

### Fixed
- Cypher query type casting requirement (`create_graph('graph_name'::name)`)
- Dollar quoting emphasis for Cypher strings
- SQL keyword avoidance in Cypher queries

---

## [v0.3.0] - 2026-04-15

### Added
- Apache AGE Property Graph integration with PostgreSQL 18
- Cypher query language support for multi-hop relationship traversal
- HNSW indexing on embedding properties for fast semantic retrieval
- Platform-agnostic deployment instructions (Ubuntu/Debian, CentOS/RHEL)
- Initial memory system schema design
- Basic usage examples with Python SDK

---

## [v0.2.0] - 2026-03-01

### Added
- PostgreSQL 18 memory system foundation
- Basic vector storage capabilities
- Graph node relationship tracking
- Initial SKILL.md documentation

[unreleased]: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/compare/v0.3.2...HEAD
[v0.3.2]: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/releases/tag/v0.3.2
[v0.3.1]: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/releases/tag/v0.3.1
[v0.3.0]: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/releases/tag/v0.3.0
[v0.2.0]: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/releases/tag/v0.2.0
