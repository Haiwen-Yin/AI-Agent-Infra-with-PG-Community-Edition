# Release Notes - memory-pg18-by-yhw

## Version 0.3.1 (May 3, 2026)

### New Features

#### SQL-Based Embedding Generation (via [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) extension)

**What's new:** Added support for generating text embeddings directly from PostgreSQL using the **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)** C extension. This eliminates the need for Python SDK overhead and reduces network latency when calling external embedding APIs.

**New SQL Functions:**
```sql
-- Generate embedding directly in SQL
SELECT generate_embedding('Hello world');

-- Use memory wrapper function (converts to VECTOR type)
SELECT memory.generate_embedding_sql('Your text here') AS vector;

-- Add concept with auto-generated embedding (NEW convenience function)
SELECT memory.add_concept_with_embedding('My Concept', 'category', 'Description text');

-- Check extension version
SELECT extension_version();
```

**Benefits:**
- Lower network latency - PG server communicates directly with local/embedding API
- Simpler SQL-based workflows - no Python SDK required for basic operations
- Reduced dependency management - single source of truth on PG server

#### Dual-Mode Embedding Generation Architecture

The memory system now supports two complementary approaches:

| Mode | Method | Best For | Latency |
|------|--------|----------|---------|
| **Option A** | SQL `generate_embedding()` via [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) extension | Production deployments, low-latency needs | Lower (PG→API) |
| **Option B** | Python SDK `flagencoding` client library | Development, complex model configurations | Higher (Client→API) |

### Updated Files

- `init_memory_system.sql` - Added Step 0 for [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) registration + new wrapper functions
- `SKILL.md` - Documentation updated with dual-mode embedding options
- `VERSION` - Bumped to 0.3.1

### Migration Notes for v0.3.0 Users

**No breaking changes.** All existing Python SDK workflows continue to work unchanged. The SQL-based approach is purely additive and optional.

**If you want to use SQL embedding generation:**
1. Install [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) extension on your PG server
2. Run the updated `init_memory_system.sql` (Step 0 registers the functions)
3. Start using `SELECT generate_embedding('text')` in your queries

### Technical Details

**New Functions Added to `memory` Schema:**
```sql
-- Generate embedding and return as VECTOR type
CREATE FUNCTION memory.generate_embedding_sql(text_input TEXT) RETURNS VECTOR;

-- Add concept with auto-generated embedding
CREATE FUNCTION memory.add_concept_with_embedding(
    name VARCHAR, 
    category VARCHAR DEFAULT 'custom', 
    description TEXT
) RETURNS UUID;
```

**Requires:** [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) C extension installed at `/usr/local/pgsql/lib/[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)` with Python proxy configured.

---

## Version 0.3.0 (April 30, 2026)

### Release Summary

v0.3.0 focuses on **AGE PG18 compatibility documentation** and **Cypher query usage guidelines**. This release provides critical information for using Apache AGE 1.7.0 with PostgreSQL 18, including proper type casting requirements and workarounds for known limitations.

### Key Changes

- **AGE PG18 Compatibility Guide**: Added comprehensive documentation on AGE 1.7.0 support for PostgreSQL 18
- **Cypher Usage Guidelines**: Type casting requirement (`create_graph('graph_name'::name)`), dollar quoting emphasis, SQL keyword avoidance
- **Vector Dimension Update**: 1024 dimensions (BGE-M3 standard) (BGE-M3 optimized for Chinese language embeddings)
- **Documentation Improvements**: Updated all SQL examples to reflect PG18 + AGE 1.7.0 best practices

### Important Notes for Upgrading from v0.2.0

1. **AGE setup is critical**: Always run these commands before Cypher queries:
   ```sql
   SET search_path TO ag_catalog;
   SELECT create_graph('your_graph_name'::name);
   ```

2. **Vector dimension change**: If using BGE-M3, vectors remain at 1024 dimensions by default

3. **Cypher syntax matters**: Use dollar quoting `$$...$$`, never single quotes for Cypher strings

---

## License

This project is licensed under the Apache License, Version 2.0. See LICENSE file for full terms and conditions.
