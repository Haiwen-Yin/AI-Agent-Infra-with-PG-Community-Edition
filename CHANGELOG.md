# Change Log

All notable changes to memory-pg18-by-yhw will be documented in this file.

## [1.0.0] - 2026-05-10

### Major Release - Production-Grade Memory System

This is a **major breakthrough for Production AI Agents** - v1.0.0 brings PostgreSQL 18 Memory System to full production parity with oracle-memory-by-yhw v1.0.0, including a complete Knowledge Base system for managing stable knowledge and distilled experiences.

### Added

- **Knowledge Base System** - Complete knowledge management framework
  - `knowledge_concepts` table - Knowledge concepts with embeddings and metadata
  - `knowledge_graph` table - Concept relationships and graph structure
  - `knowledge_versions` table - Version history for all concepts
  - `knowledge_tags` table - Tag taxonomy and classification
  - `knowledge_concept_tags` table - Many-to-many tag relationships
  - `knowledge_distillation_log` table - Experience distillation tracking
  - `knowledge_search_history` table - Query analytics and optimization
  - Views: `v_knowledge_concepts_active`, `v_knowledge_graph_summary`

- **Python Knowledge Base API** - `scripts/knowledge_base_api_pg.py`
  - `create_concept()` - Create knowledge concepts with auto-embedding
  - `search_concepts_by_text()` - Semantic search with vector similarity
  - `get_concept()` / `update_concept()` - Concept CRUD operations
  - `create_relationship()` / `get_related_concepts()` - Graph operations
  - `add_tag_to_concept()` - Tag management
  - `get_statistics()` - System analytics

- **Enhanced pg-embedding-gen Integration**
  - Database-native BGE-M3 embedding generation
  - Configurable model endpoints
  - Retry logic and error handling

### Updated

- SKILL.md - Updated to v1.0.0 with production emphasis
- README.md - Complete rewrite for v1.0.0 release
- CHANGELOG.md - Full version history maintained

### Fixed

- AGE graph creation compatibility issues with PostgreSQL 18
- pgvector index configuration for optimal performance
- Python API connection pooling and error handling
- Embedding generation failure recovery

### Notes

- This release is **battle-tested** and production-ready
- Fully compatible with existing v0.3.3 deployments (additive schema)
- All Multi-Agent Architecture features retained and enhanced

---

## [0.3.3] - 2026-05-07

### Added

- **Multi-Agent Architecture** - Complete framework for managing multiple AI agents
  - Agent Registry (agent_registry) - Centralized agent lifecycle management
  - Memory Access Control (agent_memory_access) - Fine-grained visibility policies
  - Collaboration Framework (agent_collaboration) - Agent-to-agent communication channels
  - Session Management (agent_session) - Active session tracking and monitoring
  - Python API for all multi-agent operations

### Updated

- Enhanced task plan system with session context tracking
- Improved memory access control policies
- Added agent capability discovery system

### Notes

- This edition targets multi-agent teams
- Fine-grained memory access control per agent
- Built-in collaboration channels for agent coordination

---

## [0.3.2] - 2026-05-06

### Added

- **Task Plan Persistence System** - Complete task execution tracking
  - `task_plans` table - Core plan management with goals and priorities
  - `task_steps` table - Step execution tracking and results
  - `task_context_snapshots` table - Breakpoint recovery state
  - `task_tool_calls` table - Tool call audit trail
  - `task_dependencies` table - Task dependency graph
  - Python API for task plan creation, update, and resume
  - Auto-snapshot functionality for breakpoint recovery

### Updated

- Enhanced Python API with task plan operations
- Added historical learning from completed tasks

### Fixed

- Context snapshot JSON handling
- Task step status transitions

### Notes

- Breakpoint recovery after failures - Resume exactly where interrupted
- Historical pattern learning from completed tasks
- Complete audit status for all agent actions

---

## [0.3.1] - 2026-05-05

### Added

- **Property Graph Integration** - Apache AGE with Cypher query support
  - Full Cypher query compatibility
  - Graph visualization support
  - Relationship traversal optimization
  - Node/edge property indexing

- **Enhanced Vector Search** - pgvector HNSW indexing
  - Optimized HNSW index configuration
  - Batch embedding generation
  - Similarity search performance tuning

### Updated

- Memory node/edge schema for better property graph integration
- Vector embedding dimension configuration (1024)
- Query performance optimizations

### Fixed

- Vector index rebuild issues
- Cypher query syntax compatibility

### Notes

- Multi-model embedding support (BGE-M3, OpenAI, etc.)
- Hybrid semantic and graph traversal queries
- Improved memory node/edge property management

---

## [0.3.0] - 2026-05-04

### Added

- **PostgreSQL 18 Support** - Full PostgreSQL 18 compatibility
  - pgvector extension for vector similarity search
  - Apache AGE extension for property graph queries
  - Native JSONB support for flexible metadata
  - HNSW indexing for high-performance vector search

### Updated

- Complete schema redesign for PostgreSQL 18
- Python API updated for psycopg2
- Vector embedding generation integration

### Notes

- Designed for PostgreSQL 18.3+
- Requires pgvector 0.8.2+ and Apache AGE 1.7.0+
- First release with vector and graph capabilities

---

## Version Summary

| Version | Release Date | Major Features | Status |
|---------|--------------|----------------|--------|
| v1.0.0 | 2026-05-10 | Knowledge Base, Enhanced API, Production-Ready | ✅ Stable |
| v0.3.3 | 2026-05-07 | Multi-Agent Architecture | ✅ Stable |
| v0.3.2 | 2026-05-06 | Task Plan Persistence | ✅ Stable |
| v0.3.1 | 2026-05-05 | Property Graph, Vector Search | ✅ Stable |
| v0.3.0 | 2026-05-04 | PostgreSQL 18 Support | ✅ Stable |
