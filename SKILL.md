---
name: memory-pg18-by-yhw
description: AI Agent Memory System (PostgreSQL 18 + Apache AGE) - Hybrid semantic search and graph-based relationship traversal toolkit for AI applications with vector embeddings and graph relationships.
version: v0.3.1
author: Haiwen Yin (Haiwen Yin - Database Expert)
license: Apache License 2.0
lastUpdated: 2026-04-30
tags: [postgresql, age, vector, graph, memory, pg18]
---

# memory-pg18-by-yhw - AI Agent Memory System (PostgreSQL 18 + Apache AGE)

## Overview

A production-ready, platform-agnostic AI Agent memory system built on PostgreSQL 18 with pgvector and Apache AGE Property Graph integration. This skill provides a complete toolkit for implementing hybrid semantic search and graph-based relationship traversal in AI applications.

**Version**: v0.3.1  
**Author**: Haiwen Yin (Haiwen Yin - Database Expert)  
**License**: Apache License 2.0  
**Last Updated**: 2026-04-30 CST

---

## 🎯 **What This Skill Does**

This skill enables you to:
1. Deploy a memory system with PostgreSQL 18 on any platform (bare metal, cloud) using standard Linux installation
2. Store AI knowledge as vectors (semantic embeddings) and concepts (graph nodes)
3. Perform hybrid search combining vector similarity + graph relationship traversal
4. Query relationships using Cypher for multi-hop reasoning
5. Scale to millions of records with HNSW indexing

---

## 📦 **Package Contents**

```
memory-pg18-by-yhw-v0.3.1/
├── SKILL.md                   # This skill file (v0.3.1)
├── README.md                  # Full project documentation (English)
├── LICENSE                    # Apache License 2.0 full text
├── NOTICE                     # Third-party attributions and legal notices
├── VERSION                    # Version identifier (v0.3.1)
├── .gitignore                 # Git ignore rules for this project
├── docs/
│   └── deployment-guide.md    # Detailed deployment instructions for various platforms
├── scripts/
│   └── init_memory_system.sql # Complete database schema and setup SQL
└── examples/
    ├── basic_usage.py         # Python SDK example with BGE-M3 embeddings
    └── sample_data.sql        # Sample INSERT statements for testing
```

---

## 🏗️ **Architecture**

### Hybrid Memory Model (Vector + Graph)

This skill implements a dual-layer memory architecture:

1. **Semantic Layer (pgvector)**: 
   - Stores concept embeddings as `VECTOR(1024)` columns (BGE-M3 compatible)
   - Uses HNSW indexing for fast approximate nearest neighbor search
   - Enables cosine similarity matching for semantic queries

2. **Relationship Layer (Apache AGE)**:
   - Models concepts as graph nodes with properties
   - Defines relationships using Cypher query language
   - Supports multi-hop traversal for reasoning chains

### Why Hybrid?

Pure vector search lacks explicit relationship modeling, while pure graph search struggles with fuzzy matching and semantic understanding. This hybrid approach gives you the best of both worlds:

- **Semantic retrieval**: Find similar concepts even without exact name matches
- **Relationship reasoning**: Traverse connected knowledge for multi-hop queries
- **Flexibility**: Use either layer independently or combine them in complex queries

---

## 🚀 **Usage Guide**

### 1. Quick Deployment (Standard Linux Installation)

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
  -f /path/to/memory-pg18-by-yhw/scripts/init_memory_system.sql
```

### 2. Embedding Generation Options (v0.3.1 NEW)

#### Option A: SQL Function via [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) Extension (Recommended for low latency)

When the **[pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)** extension is installed on your PostgreSQL server, you can generate embeddings directly from SQL without Python SDK overhead:

```sql
-- Generate embedding directly in SQL
SELECT generate_embedding('Hello world');

-- Or use the memory wrapper function that converts to VECTOR type
SELECT memory.generate_embedding_sql('Your text here') AS vector;

-- Add concept with auto-generated embedding (NEW in v0.3.1)
SELECT memory.add_concept_with_embedding('My Concept', 'category', 'Description text');

-- Check extension version
SELECT extension_version();
```

**Requirements:**
- [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) C extension installed on PG server
- Python proxy running at configured endpoint (e.g., `http://localhost:12345/v1/embeddings`)
- Extension registered in init_memory_system.sql Step 0

#### Option B: Python SDK with flagembedding (Original method)

```python
from flagembedding import EmbeddingModel
import psycopg2
import numpy as np

# Initialize embedding model (BGE-M3, 1024 dimensions)
model = EmbeddingModel("BAAI/bge-m3")

# Generate embedding for your text
text = "Your knowledge content here"
embedding = model.encode([text])[0].tolist()

# Store in database with concept metadata
cursor.execute("""
    INSERT INTO memory.concepts (name, category, description, embedding)
    VALUES (%s, %s, %s, %s::vector)
""", ("Concept Name", "category_type", "Description text", embedding))
```

**Pros of Option A:** Lower network latency, simpler SQL-based workflows  
**Pros of Option B:** More control over model parameters, no C extension dependency

### 3. Semantic Search Query

```python
# Find top-5 most similar concepts to a query vector
cursor.execute("""
    SELECT name, category, 
           1 - (embedding <=> %s::vector) as similarity_score
    FROM memory.concepts
    ORDER BY similarity_score DESC
    LIMIT 5;
""", (query_embedding,))
```

### 4. Graph Relationship Query (Cypher)

**IMPORTANT: AGE PG18 Usage Notes:**

1. **must set search path to ag_catalog**
   ```sql
   SET search_path TO ag_catalog;
   ```

2. **create graph requires explicit type cast**
   ```sql
   -- ✅ correct way (with ::name type cast)
   SELECT create_graph('memory_knowledge'::name);
   
   -- ❌ incorrect way (will fail with error)
   SELECT create_graph('memory_knowledge');
   ```

3. **Avoid SQL reserved words**
   - don't use END, START and other keywords as variable names in Cypher
   - use node_a, node_b instead of start, end

4. **agtype attribute access requires CAST**
   ```sql
   MATCH (n) RETURN n.name::varchar, n.id::int
   ```

```python
# Find all relationships connected to a concept
cursor.execute("""
    SET search_path TO ag_catalog;
    SELECT * FROM cypher('memory_graph', $$
        MATCH (c:concepts {name: 'Concept Name'})-[:RELATION_TYPE]->(related:concepts)
        RETURN c.name::varchar, type(rel), related.name::varchar, rel.strength::float
    $$) AS (start_node agtype, relation_type agtype, end_node agtype, strength float);
""")
```

---

## 🔧 **Configuration Options**

### Vector Embedding Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Dimension Size | 1024 | BGE-M3 embedding size (adjustable) |
| Similarity Metric | Cosine | `vector_cosine_ops` for cosine distance |
| HNSW m | 16 | Links per node in graph structure |
| HNSW ef_construction | 200 | Index building quality vs speed tradeoff |

### Graph Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Label Type | `concepts` | Node label for concept entities |
| Relation Types | Dynamic | Define custom relationship types per domain |
| Strength Range | 0.0 - 1.0 | Float weight for edges (default: 1.0) |

---

## 📈 **Performance Optimization**

### Indexing Strategies

1. **HNSW Index**: Always create on `embedding` column for semantic search
   ```sql
   CREATE INDEX idx_concepts_embedding 
   ON memory.concepts USING hnsw (embedding vector_cosine_ops) 
   WITH (m = 16, ef_construction = 200);
   ```

2. **B-tree Index**: For category filtering
   ```sql
   CREATE INDEX idx_concepts_category ON memory.concepts(category);
   ```

3. **Foreign Key Constraints**: Ensure referential integrity for relations table
   ```sql
   ALTER TABLE memory.relations 
   ADD CONSTRAINT fk_from_concept FOREIGN KEY (from_concept_id) REFERENCES memory.concepts(concept_id);
   ALTER TABLE memory.relations 
   ADD CONSTRAINT fk_to_concept FOREIGN KEY (to_concept_id) REFERENCES memory.concepts(concept_id);
   ```

### Query Optimization Tips

- **Filter by category first**, then apply vector search:
  ```sql
  SELECT * FROM memory.concepts 
  WHERE category = 'user_profile' 
    AND embedding IS NOT NULL
  ORDER BY embedding <=> %s::vector LIMIT 5;
  ```

- **Use EXPLAIN ANALYZE** to identify bottlenecks:
  ```bash
  psql -d memory_graph << 'EOSQL'
  EXPLAIN ANALYZE 
  SELECT * FROM memory.concepts 
  ORDER BY embedding <=> '[0.1,0.2,...]'::vector LIMIT 5;
  EOSQL
  ```

---

## 🧪 **Testing & Validation**

### Basic Sanity Check

```bash
# Verify schema creation
psql -U postgres -d memory_graph << 'EOSQL'
SELECT table_name FROM information_schema.tables WHERE table_schema = 'memory';
-- Expected output: concepts, relations
EOSQL

# Test vector insertion and retrieval
psql -U postgres -d memory_graph << 'EOSQL'
INSERT INTO memory.concepts (name, category, description, embedding) 
VALUES ('test', 'testing', 'Sanity check', ARRAY[0.1, 0.2, ...]);  -- 1024 dims

SELECT name FROM memory.concepts WHERE name = 'test';
-- Expected output: test
EOSQL
```

### Performance Benchmark Script

See `scripts/benchmark.py` (not included in v0.3.0 but available on request):

- Insert 1K sample records
- Measure HNSW index build time
- Time semantic search queries (<30ms target)
- Test multi-hop traversal latency (<100ms for 3 hops)

---

## 🐛 **Troubleshooting**

### Common Issues & Solutions

#### Issue 1: AGE create_graph() function not found

**Symptoms**: `ERROR: function create_graph(unknown) does not exist`  
**Cause**: Missing type cast or search path not set  

**Solution**:
```sql
-- Set search path first
SET search_path TO ag_catalog;

-- Use explicit type cast for graph name
SELECT create_graph('graph_name'::name);
```

---

#### Issue 2: AGE Cypher "unhandled cypher(cstring) function call"

**Symptoms**: `ERROR: unhandled cypher(cstring) function call`  
**Cause**: Using single quotes instead of dollar quoting for Cypher strings  

**Solution**:
```sql
-- ✅ Correct: Use dollar quoting ($$...$$)
SELECT * FROM cypher('graph_name', $$ RETURN 1 AS result $$) AS (result int);

-- ❌ Incorrect: Single quotes cause issues
SELECT * FROM cypher('graph_name', 'RETURN 1') AS (result int);
```

---

#### Issue 3: AGE Cypher syntax error with SQL keywords (END, START)

**Symptoms**: `ERROR: syntax error at or near "end"`  
**Cause**: Using SQL reserved words as variable names in Cypher  

**Solution**:
```sql
-- ❌ Incorrect - END is a SQL keyword
MATCH p = (start)-[*1..3]->(end) RETURN length(p);

-- ✅ Correct - Use alternative names
MATCH p = (node_a)-[*1..3]->(node_b) RETURN length(p);
```

---

#### Issue 4: PostgreSQL fails to start after extension installation

**Symptoms**: `FATAL: could not load library ".../vector.so": file too short`  
**Cause**: Extension binary incompatible with PG version or corrupted copy  

**Solution**:
```bash
# Recompile pgvector from source on target host
git clone https://github.com/pgvector/pgvector.git
cd pgvector && make && sudo make install

# Verify control file compatibility (PG 18 specific)
cat /usr/local/pgsql/share/extension/vector.control
# Remove "microversion_format" parameter if present
```

---

#### Issue 5: Vector dimension mismatch errors

**Symptoms**: `error: vector dimensions do not match`  

**Solution**: Ensure all vectors are exactly 1024 dimensions for BGE-M3:
```python
embedding = model.encode([text])[0]  # Should be shape (1024,)
assert len(embedding) == 1024, f"Expected 1024 dims, got {len(embedding)}"
```

---


---

## 📄 **License & Attribution**

This project is licensed under **Apache License 2.0**. See LICENSE file for full terms.

For third-party component attributions and legal notices, see NOTICE file.

---

## 👤 **Author & Contributors**

- **Original Author**: Haiwen Yin (Haiwen Yin - Database Expert) - Oracle/PostgreSQL/MySQL ACE Database Expert
- **Blog**: https://blog.csdn.net/yhw1809
- **GitHub**: https://github.com/Haiwen-Yin
- **Location**: Xipu Town, Pidu District, Chengdu, Sichuan, China

---


## 📞 **Support & Contact**

For issues, feature requests, or collaboration:
- Open an issue on GitHub: https://github.com/Haiwen-Yin/memory-pg18-by-yhw/issues
- Email: Available via blog contact form
- WeChat: Contact author via blog for WeChat communication

---

## 🎓 **Educational Resources**

To understand the underlying technologies better:

1. **Apache AGE Tutorial**: https://age.apache.org/age-site/v1.7/docs/tutorial.html
2. **pgvector Quick Start**: https://github.com/pgvector/pgvector#quick-start
3. **Cypher Query Language Manual**: https://neo4j.com/docs/cypher-manual/current/
4. **HNSW Algorithm Explained**: https://arxiv.org/abs/1603.09320 (original paper)

---

**Ready to deploy!** 🚀  
For complete deployment instructions, see `docs/deployment-guide.md`.

---

## RELEASE NOTES (v0.3.0)

### Release Date: 2026-04-30
### Author: Haiwen Yin (Haiwen Yin - Database Expert)

#### Summary
v0.3.0 focuses on **AGE PG18 compatibility documentation** and **Cypher query usage guidelines**. This release provides critical information for using Apache AGE 1.7.0 with PostgreSQL 18, including proper type casting requirements and workarounds for known limitations.

#### ✨ New Features & Documentation
- **AGE PG18 Compatibility Guide**: Added comprehensive documentation on AGE 1.7.0 support for PostgreSQL 18; clarified that AGE has official PG18 build: `PG18/v1.7.0-rc0`
- **Cypher Usage Guidelines**: Type casting requirement (`create_graph('graph_name'::name)`), dollar quoting emphasis, SQL keyword avoidance

#### 🔧 Changes & Updates
- **Vector Dimension Update**: 1024 dimensions (BGE-M3 standard) (BGE-M3 optimized for Chinese language embeddings)
- **Documentation Improvements**: Updated all SQL examples to reflect PG18 + AGE 1.7.0 best practices, added Chinese language notes

#### ⚠️ Important Notes for Upgrading from v0.2.0
1. **AGE setup is critical**: Always run these commands before Cypher queries:
   ```sql
   SET search_path TO ag_catalog;
   SELECT create_graph('your_graph_name'::name);
   ```
2. **Vector dimension change**: If using BGE-M3, vectors remain at 1024 dimensions by default
3. **Cypher syntax matters**: Use dollar quoting `$$...$$`, never single quotes for Cypher strings

#### 🧪 Testing Recommendations
Before deploying v0.3.0 to production:
1. Verify AGE extension is loaded: `SELECT extname FROM pg_extension WHERE extname = 'age';`
2. Test graph creation with type cast: `SELECT create_graph('test'::name);`
3. Run a simple Cypher query with dollar quoting
4. Confirm vector operations work with your chosen dimension

---

**Enjoy using memory-pg18-by-yhw v0.3.1!** 🚀