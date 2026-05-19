-- ============================================
-- Memory System v0.3.1 - Initialization Script
-- Platform-agnostic AI Agent Memory with PostgreSQL 18 + Apache AGE
-- ============================================
-- 
-- NEW in v0.3.1: Added pg-embedding-gen-by-yhw extension support
-- This allows generating embeddings directly from SQL functions
-- without requiring a Python client SDK in the application layer.
--
-- Prerequisites for embedding generation:
-- 1. Install pg-embedding-gen-by-yhw extension (uses COPY FROM PROGRAM + Python proxy)
--    See references/ for installation instructions
-- 2. Configure default model profile or use inline mode
-- ============================================

BEGIN;

-- =====================================================
-- Step 0: pg-embedding-gen-by-yhw Extension
-- Optional - enables SQL-based embedding generation
-- Install first: sudo bash scripts/install.sh && psql -d memory_graph -f sql/install.sql
-- =====================================================
-- 
-- The extension provides embedding_generate() and embedding_generate_model() functions
-- via COPY FROM PROGRAM + Python proxy. No C compilation required.
--
-- If the extension is installed, the following functions are available:
--   embedding_generate(text)              -- default model profile
--   embedding_generate(text, profile)     -- named model profile
--   embedding_generate_model(text, model, api_url)  -- inline mode
--   embedding_health_check()              -- test API connectivity
--   embedding_list_models()               -- list registered models

-- =====================================================
-- Step 1: Create Schema and Tables
-- =====================================================

CREATE SCHEMA IF NOT EXISTS memory;

-- Concepts table (nodes in Property Graph)
CREATE TABLE IF NOT EXISTS memory.concepts (
    concept_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(256) NOT NULL,
    category VARCHAR(128),
    description TEXT,
    content JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1024),  -- Configurable dimension (default: BGE-M3 = 1024)
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Relations table (edges in Property Graph)
CREATE TABLE IF NOT EXISTS memory.relations (
    relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_concept_id UUID REFERENCES memory.concepts(concept_id),
    to_concept_id UUID REFERENCES memory.concepts(concept_id),
    relation_type VARCHAR(128) NOT NULL,
    strength FLOAT DEFAULT 1.0 CHECK (strength BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Step 2: Create Indexes for Performance
-- =====================================================

-- HNSW index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_concepts_embedding 
ON memory.concepts USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 200);

-- B-tree indexes for filtering and traversal
CREATE INDEX IF NOT EXISTS idx_concepts_category ON memory.concepts(category);
CREATE INDEX IF NOT EXISTS idx_relations_from ON memory.relations(from_concept_id);
CREATE INDEX IF NOT EXISTS idx_relations_to ON memory.relations(to_concept_id);

-- =====================================================
-- Step 3: Create Helper Functions
-- =====================================================

-- Function to add a concept with optional embedding
CREATE OR REPLACE FUNCTION memory.add_concept(
    p_name VARCHAR,
    p_category VARCHAR DEFAULT 'custom',
    p_description TEXT DEFAULT '',
    p_content JSONB DEFAULT '{}'::jsonb,
    p_embedding VECTOR DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_concept_id UUID;
BEGIN
    INSERT INTO memory.concepts (name, category, description, content, embedding)
    VALUES (p_name, p_category, p_description, p_content, p_embedding)
    RETURNING concept_id INTO v_concept_id;
    
    RETURN v_concept_id;
END;
$$ LANGUAGE plpgsql;

-- Function to add a relation between concepts
CREATE OR REPLACE FUNCTION memory.add_relation(
    p_from_uuid UUID,
    p_to_uuid UUID,
    p_relation_type VARCHAR DEFAULT 'related_to',
    p_strength FLOAT DEFAULT 1.0
) RETURNS VOID AS $$
BEGIN
    INSERT INTO memory.relations (from_concept_id, to_concept_id, relation_type, strength)
    VALUES (p_from_uuid, p_to_uuid, p_relation_type, p_strength);
END;
$$ LANGUAGE plpgsql;

-- Function for semantic search with optional category filter
CREATE OR REPLACE FUNCTION memory.search_similar(
    p_query_embedding VECTOR,
    p_limit INT DEFAULT 5,
    p_min_score FLOAT DEFAULT 0.7,
    p_category_filter VARCHAR DEFAULT NULL
) RETURNS TABLE (
    concept_id UUID,
    name VARCHAR,
    category VARCHAR,
    description TEXT,
    similarity_score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.concept_id,
        c.name,
        c.category,
        c.description,
        1 - (c.embedding <=> p_query_embedding)::FLOAT as similarity_score
    FROM memory.concepts c
    WHERE c.embedding IS NOT NULL
      AND 1 - (c.embedding <=> p_query_embedding)::FLOAT >= p_min_score
      AND (p_category_filter IS NULL OR c.category = p_category_filter)
    ORDER BY similarity_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- NEW in v0.3.1: Generate embedding directly from SQL using pg-embedding-gen-by-yhw
-- Requires pg-embedding-gen-by-yhw installed (see references/)
CREATE OR REPLACE FUNCTION memory.generate_embedding_sql(text_input TEXT)
RETURNS VECTOR AS $$
DECLARE
    result_vector FLOAT[];
BEGIN
    SELECT embedding_generate(text_input) INTO result_vector;
    
    RETURN result_vector::vector;
END;
$$ LANGUAGE plpgsql VOLATILE STRICT;

-- NEW in v0.3.1: Add concept with auto-generated embedding via SQL
CREATE OR REPLACE FUNCTION memory.add_concept_with_embedding(
    p_name VARCHAR,
    p_category VARCHAR DEFAULT 'custom',
    p_description TEXT DEFAULT ''
) RETURNS UUID AS $$
DECLARE
    v_concept_id UUID;
    v_embedding VECTOR;
BEGIN
    -- Generate embedding using pg-embedding-gen-by-yhw (requires extension installed; see references/)
    SELECT generate_embedding_sql(p_description)::vector INTO v_embedding;
    
    -- Insert concept with generated embedding
    INSERT INTO memory.concepts (name, category, description, embedding)
    VALUES (p_name, p_category, p_description, v_embedding)
    RETURNING concept_id INTO v_concept_id;
    
    RETURN v_concept_id;
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;

-- =====================================================
-- Step 4: Create Views for Common Queries
-- =====================================================

CREATE OR REPLACE VIEW memory.v_concepts_with_relations AS
SELECT 
    c.concept_id,
    c.name,
    c.category,
    CASE WHEN c.embedding IS NOT NULL THEN 'OK' ELSE '-' END as has_embedding,
    COUNT(DISTINCT r.relation_id) as relation_count,
    c.created_at
FROM memory.concepts c
LEFT JOIN memory.relations r ON c.concept_id = r.from_concept_id OR c.concept_id = r.to_concept_id
GROUP BY c.concept_id, c.name, c.category, c.embedding, c.created_at;

CREATE OR REPLACE VIEW memory.v_relations_with_names AS
SELECT 
    from_c.name as from_name,
    to_c.name as to_name,
    r.relation_type,
    r.strength as confidence,
    r.created_at
FROM memory.relations r
JOIN memory.concepts from_c ON r.from_concept_id = from_c.concept_id
JOIN memory.concepts to_c ON r.to_concept_id = to_c.concept_id;

-- =====================================================
-- Step 5: Initialize with Sample Data
-- =====================================================

DELETE FROM memory.relations;
DELETE FROM memory.concepts;

INSERT INTO memory.concepts (concept_id, name, category, description) VALUES
    ('001', 'Haiwen Yin (胖头鱼 🐟)', 'user_profile', 
     'Oracle/PostgreSQL/MySQL ACE Database Expert specializing in AI Agent Memory System'),
    
    ('002', 'Hermes Agent', 'ai_agent', 
     'AI Assistant with persistent memory, skills system, and multi-agent orchestration');

INSERT INTO memory.relations (from_concept_id, to_concept_id, relation_type, strength) VALUES
    ((SELECT concept_id FROM memory.concepts WHERE name = 'Haiwen Yin (胖头鱼 🐟)'),
     (SELECT concept_id FROM memory.concepts WHERE name = 'Hermes Agent'),
     'RELATED_TO', 0.9);

-- =====================================================
-- Step 6: Grant Permissions and Cleanup
-- =====================================================

GRANT ALL PRIVILEGES ON SCHEMA memory TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA memory TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA memory TO postgres;

COMMIT;

-- =====================================================
-- Verification Queries (Run after COMMIT)
-- =====================================================

SELECT 
    name,
    category,
    has_embedding::text as vector_enabled,
    relation_count
FROM memory.v_concepts_with_relations
ORDER BY created_at DESC;

-- NEW in v0.3.1: Test embedding generation via SQL (requires pg-embedding-gen-by-yhw; see references/)
SELECT 'Test embedding generation via SQL:' AS test,
       extension_version() AS result;
