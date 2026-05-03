# memory-pg18-by-yhw v0.3.1

[GitHub Repository](https://github.com/Haiwen-Yin/memory-pg18-by-ywh) · [SKILL.md](SKILL.md) · [RELEASE_NOTES.md](RELEASE_NOTES.md)

AI Agent Memory System with PostgreSQL 18 + Apache AGE + pg-embedding-gen-by-yhw

**Version**: v0.3.1  
**Author**: Haiwen Yin - Database Expert  
**Date**: 2026-04-30 CST  
**License**: Apache License 2.0

---

## 🎯 **Project Overview**

An AI Agent memory system built on PostgreSQL 18 + pgvector + Apache AGE Property Graph. Features:

- ✅ **Hybrid Search**: Vector similarity search + Graph relationship traversal
- ✅ **Property Graph**: Cypher query language, supports multi-hop relationship traversal
- ✅ **Auto Indexing**: HNSW indexing on embedding properties for fast semantic retrieval
- ✅ **Platform Agnostic**: Suitable for any AI Agent, chatbot, or knowledge graph application
- ✅ **Dual-mode Embedding Generation**: SQL-based generation via [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) extension (v0.3.1+)

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

Then run the initialization script:
```bash
psql -U postgres -d memory_graph \
  -f scripts/init_memory_system.sql
```

> **⚠️ AGE PG18 Critical Setup Requirements**: Before running any Cypher queries, execute these commands in every session:
> ```sql
> SET search_path TO ag_catalog;
> SELECT create_graph('memory_graph'::name);  -- Note: ::name type cast is REQUIRED!
> ```

This ensures Cypher functions are accessible and the graph object exists. Without this setup, you will encounter errors like "function cypher(unknown) does not exist" when attempting graph queries.
    name VARCHAR(256) NOT NULL,
    category VARCHAR(128),
    description TEXT,
    content JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory.relations (
    relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_concept_id UUID REFERENCES memory.concepts(concept_id),
    to_concept_id UUID REFERENCES memory.concepts(concept_id),
    relation_type VARCHAR(128) NOT NULL,
    strength FLOAT DEFAULT 1.0
);

-- Create HNSW index for vector similarity search
CREATE INDEX idx_concepts_embedding 
ON memory.concepts USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 200);

GRANT ALL PRIVILEGES ON SCHEMA memory TO postgres;
EOSQL
```

### Step 3: Insert Sample Data

```bash
psql -U postgres -d memory_graph << 'EOSQL'
INSERT INTO memory.concepts (name, category, description) VALUES
    ('Haiwen Yin - DB Expert', 'user_profile', 'Oracle/PostgreSQL/MySQL ACE Database Expert'),
    ('Oracle AI Database', 'knowledge_base', 'Oracle AI Database Enterprise Edition v23.26.1'),
    ('Apache AGE', 'technology', 'PostgreSQL Property Graph extension');

-- Create relationships using Cypher
SELECT * FROM cypher('memory_graph', $$
    MATCH (a:concepts {name: 'Haiwen Yin - DB Expert'}), 
          (b:concepts {name: 'Oracle AI Database'})
    CREATE (a)-[:RELATED_TO]->(b)
$$) AS (result agtype);
EOSQL
```

### Step 4: Query Memory System

#### Semantic Search (Vector Similarity)

```bash
psql -U postgres -d memory_graph << 'EOSQL'
SELECT 
    name,
    category,
    1 - (embedding <=> '[0.1,0.2,...,1.0]'::vector) as similarity_score
FROM memory.concepts
WHERE embedding IS NOT NULL
ORDER BY similarity_score DESC
LIMIT 5;
EOSQL
```

#### Property Graph Query (Cypher)

```bash
psql -U postgres -d memory_graph << 'EOSQL'
SELECT 
    start_node.name,
    end_node.name,
    type(rel) as relation_type
FROM cypher('memory_graph', $$
    MATCH path = (node_a:concepts)-[rel]->(node_b:concepts)
    RETURN node_a, node_b, rel
$$) AS (start_node agtype, end_node agtype, rel agtype);
EOSQL
```

---

### 🧠 Embedding Generation (v0.3.1+)

#### Option A: SQL-Based (Recommended for Production)

Requires [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw):

```sql
-- Generate embedding directly in SQL
SELECT generate_embedding('Hello world');

-- Use memory wrapper function
SELECT memory.generate_embedding_sql('Your text here') AS vector;

-- Add concept with auto-generated embedding (NEW)
SELECT memory.add_concept_with_embedding('My Concept', 'category', 'Description');
```

**Requirements:**
- pg-embedding-gen-by-yhw C extension installed on PG server
- Python proxy running at configured endpoint

#### Option B: Python SDK (Development/Testing)

```python
from flagembedding import EmbeddingModel
model = EmbeddingModel('BAAI/bge-m3')
embedding = model.encode("Your text here")
```

---



| Metric | Value | Conditions |
|--------|-------|------------|
| Vector Dimensions | 1024 (BGE-M3) | Cosine similarity |
| HNSW Index Build Time | ~5s | 1K records, m=16 |
| Semantic Search (<1K) | <30ms | Average latency |
| Multi-hop Traversal | <100ms | Up to 3 hops |

---

## 📚 **Reference Resources**

- Apache AGE Documentation: https://age.apache.org/docs.html
- Cypher Reference Manual: https://neo4j.com/docs/cypher-manual/
- pgvector Documentation: https://github.com/pgvector/pgvector
- HNSW Algorithm Paper: https://arxiv.org/abs/1603.09320

---

## 📄 **License**

Apache License 2.0 - Free to use, modify, and distribute with proper attribution.

See LICENSE file for full license terms.

---

**Last Updated**: 2026-04-30  
See [RELEASE_NOTES.md](RELEASE_NOTES.md) for detailed version changelog
