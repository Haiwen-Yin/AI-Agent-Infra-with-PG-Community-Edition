# Change Log

All notable changes to memory-pg18-by-yhw will be documented in this file.

## [2.0.0] - 2026-05-18

### Major Release — Complete Rewrite: Unified Architecture

v2.0.0 is a **complete rewrite** mirroring oracle-memory-by-yhw v2.0.0. Every component redesigned from scratch.

### Added

- **Unified Entity Model** — All entity types (MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, HARNESS_TEMPLATE) in single `entities` table with `entity_type` discriminator
- **Unified Edge Model** — All relationships in single `entity_edges` table with strength (0–2) and confidence (0–1)
- **4-Phase SQL Deployment** — Ordered schema, API, jobs, harness template scripts (idempotent)
- **18 Tables** — entities, entity_edges, knowledge_meta, harness_meta, entity_embeddings, agent_registry, agent_session, entity_access_log, agent_permission_log, agent_collaboration, task_plans, task_steps, task_context_snapshots, task_tool_calls, task_dependencies, tags, entity_tags, system_config, system_users
- **53 Indexes** — B-tree, GIN, HNSW (vector), composite
- **5 Views** — v_memory_entities, v_knowledge_entities, v_active_sessions, v_collaboration_status, v_entity_graph
- **PL/pgSQL API** — 4 schemas (memory, memory_fusion, knowledge_api, agent_perm, session_cleanup) with 21 functions
- **7 pg_cron Jobs** — Memory fusion, knowledge extraction, session cleanup, log purge, tag counts, collaboration expiry, entity archiving
- **Python API** — 8 modules (~2000 lines): config, connection, memory_api, knowledge_api, agent_api, task_plan_api, security, harness_api
- **psycopg2 ThreadedConnectionPool** — Replaces psql subprocess (20ms/query vs 90s, 4500x faster)
- **Unix Socket Support** — Automatic when config host is localhost/empty
- **Security Module** — DataMaskingService (email, phone, SSN, credit card, custom patterns), ReversibleEncryption (AES-256-CBC), PBKDF2 password hashing
- **Harness Template System** — 5 built-in templates (Research Analyst, Code Assistant, Data Analyst, Task Planner, Security Auditor) with full CRUD, instantiate, derive, validate, publish, deprecate, lineage
- **Apache AGE Property Graph** — 1 unified `memory_graph` graph (replaces 2 separate v1.x graphs)
- **pg-embedding-gen-by-yhw Integration** — Custom PG18 extension (COPY FROM PROGRAM + Python proxy) for in-database embedding generation; multi-model profiles, auto-dimension detection, health check, batch, validation, cosine similarity, logging
- **Test Suite** — 37 tests across 5 modules (connection, memory, knowledge, agent, security), all passing
- **Documentation** — SKILL.md (211 lines), README.md, 6 topic docs, 4 reference docs

### Changed

- knowledge_concepts + memory concepts → `entities` (entity_type discriminator)
- knowledge_graph + memory relations → `entity_edges`
- psql subprocess → psycopg2 ThreadedConnectionPool
- 4+ independent SQL scripts → 4-phase ordered deployment
- No PL/pgSQL API → 4 schemas with 21 functions
- No scheduled jobs → 7 pg_cron jobs
- No security module → DataMaskingService + ReversibleEncryption
- No harness templates → 5 built-in templates + full CRUD API
- 2 property graphs → 1 unified AGE graph (memory_graph)
- agent_memory_access → entity_access_log (all entity types)
- `generate_embedding()` marked VOLATILE (not STABLE) since it calls external API

### Fixed

- knowledge_api.py: `concept_type` column → `category` in entities table
- agent_api.py: wrong table name references
- task_plan_api.py: column names and status values (SUCCESS→COMPLETED, IN_PROGRESS→ACTIVE)
- test_agent.py: wrong assertions and table names
- 1_schema.sql: `generate_embedding()` STABLE → VOLATILE (calls external API)
- All pg-embedding-gen-by-yhw documentation: corrected from "C extension" / "database-native" to accurate description (COPY FROM PROGRAM + Python proxy)

### Removed

- `knowledge_concepts` table (replaced by entities with entity_type='KNOWLEDGE')
- `knowledge_graph` table (replaced by entity_edges)
- `knowledge_versions` table (replaced by knowledge_meta.version)
- `knowledge_tags` / `knowledge_concept_tags` tables (replaced by tags / entity_tags)
- `knowledge_distillation_log` table (replaced by knowledge_meta.source_type)
- `knowledge_search_history` table (removed)
- `agent_memory_access` table (replaced by entity_access_log)
- All v1.x SQL scripts (replaced by 4-phase deployment)
- psql subprocess approach (replaced by psycopg2)

---

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

- **Enhanced pg-embedding-gen-by-yhw Integration**
  - In-database embedding generation via COPY FROM PROGRAM + Python proxy
  - Multi-model profile management
  - Auto-dimension detection, health check, batch generation

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
| v2.0.0 | 2026-05-18 | Complete rewrite: unified entities, psycopg2, PL/pgSQL API, harness, security | ✅ Current |
| v1.0.0 | 2026-05-10 | Knowledge Base, Enhanced API, Production-Ready | ✅ Stable |
| v0.3.3 | 2026-05-07 | Multi-Agent Architecture | ✅ Stable |
| v0.3.2 | 2026-05-06 | Task Plan Persistence | ✅ Stable |
| v0.3.1 | 2026-05-05 | Property Graph, Vector Search | ✅ Stable |
| v0.3.0 | 2026-05-04 | PostgreSQL 18 Support | ✅ Stable |
