-- ====================================================================
-- PostgreSQL 18 Memory System v1.0.0 - Knowledge Base Schema (Fixed)
-- ====================================================================
-- Description: Complete Knowledge Base System for AI Agents
-- Version: 1.0.0-KB-PG18
-- Author: Haiwen Yin (胖头鱼 🐟)
-- Date: 2026-05-10
-- 
-- Components:
--   1. Knowledge Concepts (core knowledge storage)
--   2. Knowledge Graph (relationships and structure)
--   3. Knowledge Versions (version history)
--   4. Knowledge Tags (taxonomy and classification)
--   5. Knowledge Distillation (experience accumulation)
--   6. Knowledge Search History (query analytics)
--   7. Views and Indexes (query optimization)
-- ====================================================================

-- Ensure extensions are loaded
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;

-- ====================================================================
-- SECTION 1: Knowledge Concepts Table
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_concepts (
    concept_id       SERIAL PRIMARY KEY,
    concept_name     VARCHAR(200) NOT NULL,
    concept_type     VARCHAR(50) NOT NULL,
    title            VARCHAR(500),
    description      TEXT,
    content          TEXT,
    category         VARCHAR(100),
    confidence       DECIMAL(3,2) DEFAULT 0.8,
    source_type      VARCHAR(50) DEFAULT 'MANUAL',
    source_memory_ids TEXT,
    validation_status VARCHAR(50) DEFAULT 'PENDING',
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW(),
    validated_at     TIMESTAMP,
    deprecated_at     TIMESTAMP,
    version          INTEGER DEFAULT 1,
    is_current       BOOLEAN DEFAULT TRUE,
    embedding        VECTOR(1024),
    metadata         JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_name ON knowledge_concepts(concept_name);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_type ON knowledge_concepts(concept_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_category ON knowledge_concepts(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_embedding ON knowledge_concepts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_status ON knowledge_concepts(validation_status, is_current);
CREATE INDEX IF NOT EXISTS idx_knowledge_concepts_created ON knowledge_concepts(created_at DESC);

-- Comments
COMMENT ON TABLE knowledge_concepts IS 'Core knowledge concepts for AI agents with embeddings';
COMMENT ON COLUMN knowledge_concepts.embedding IS 'BGE-M3 vector embedding (1024 dimensions)';

-- ====================================================================
-- SECTION 2: Knowledge Graph Table
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_graph (
    relationship_id      SERIAL PRIMARY KEY,
    source_concept_id    INTEGER NOT NULL REFERENCES knowledge_concepts(concept_id) ON DELETE CASCADE,
    target_concept_id    INTEGER NOT NULL REFERENCES knowledge_concepts(concept_id) ON DELETE CASCADE,
    relationship_type    VARCHAR(100) NOT NULL,
    relationship_strength DECIMAL(3,2) DEFAULT 1.0,
    properties          JSONB,
    confidence          DECIMAL(3,2) DEFAULT 0.8,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),
    is_active           BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_source ON knowledge_graph(source_concept_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_target ON knowledge_graph(target_concept_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_type ON knowledge_graph(relationship_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_strength ON knowledge_graph(relationship_strength DESC);
CREATE INDEX IF NOT EXISTS idx_knowledge_graph_composite ON knowledge_graph(source_concept_id, target_concept_id, relationship_type);

-- Comments
COMMENT ON TABLE knowledge_graph IS 'Knowledge graph relationships between concepts';

-- ====================================================================
-- SECTION 3: Knowledge Versions Table
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_versions (
    version_id        SERIAL PRIMARY KEY,
    concept_id        INTEGER NOT NULL REFERENCES knowledge_concepts(concept_id) ON DELETE CASCADE,
    title             VARCHAR(500),
    description       TEXT,
    content           TEXT,
    version_number     INTEGER NOT NULL,
    versioned_by      VARCHAR(100),
    versioned_at      TIMESTAMP DEFAULT NOW(),
    change_reason     TEXT,
    metadata          JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_versions_concept ON knowledge_versions(concept_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_versions_number ON knowledge_versions(concept_id, version_number);
CREATE INDEX IF NOT EXISTS idx_knowledge_versions_date ON knowledge_versions(versioned_at DESC);

-- Comments
COMMENT ON TABLE knowledge_versions IS 'Version history for knowledge concepts';

-- ====================================================================
-- SECTION 4: Knowledge Tags Table
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_tags (
    tag_id           SERIAL PRIMARY KEY,
    tag_name         VARCHAR(100) NOT NULL UNIQUE,
    tag_category     VARCHAR(100),
    usage_count      INTEGER DEFAULT 1,
    created_at       TIMESTAMP DEFAULT NOW(),
    metadata         JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_tags_name ON knowledge_tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags_category ON knowledge_tags(tag_category);

-- Comments
COMMENT ON TABLE knowledge_tags IS 'Tag taxonomy for knowledge concepts';

-- ====================================================================
-- SECTION 5: Knowledge Concept Tags (Many-to-Many)
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_concept_tags (
    concept_id       INTEGER NOT NULL REFERENCES knowledge_concepts(concept_id) ON DELETE CASCADE,
    tag_id           INTEGER NOT NULL REFERENCES knowledge_tags(tag_id) ON DELETE CASCADE,
    added_at         TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (concept_id, tag_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_concept_tags_concept ON knowledge_concept_tags(concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_tags_tag ON knowledge_concept_tags(tag_id);

-- Comments
COMMENT ON TABLE knowledge_concept_tags IS 'Many-to-many relationship between concepts and tags';

-- ====================================================================
-- SECTION 6: Knowledge Distillation Log
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_distillation_log (
    log_id             SERIAL PRIMARY KEY,
    source_type        VARCHAR(50) NOT NULL,
    source_memory_ids   TEXT,
    target_concept_id  INTEGER REFERENCES knowledge_concepts(concept_id) ON DELETE SET NULL,
    extraction_method  VARCHAR(100),
    confidence         DECIMAL(3,2),
    distillation_date  TIMESTAMP DEFAULT NOW(),
    metadata           JSONB
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_distillation_source ON knowledge_distillation_log(source_type);
CREATE INDEX IF NOT EXISTS idx_distillation_target ON knowledge_distillation_log(target_concept_id);
CREATE INDEX IF NOT EXISTS idx_distillation_date ON knowledge_distillation_log(distillation_date DESC);

-- Comments
COMMENT ON TABLE knowledge_distillation_log IS 'Experience distillation from memories to knowledge';

-- ====================================================================
-- SECTION 7: Knowledge Search History
-- ====================================================================

CREATE TABLE IF NOT EXISTS knowledge_search_history (
    history_id        SERIAL PRIMARY KEY,
    query_text        TEXT NOT NULL,
    query_embedding   VECTOR(1024),
    result_count      INTEGER,
    search_time_ms    INTEGER,
    user_context      VARCHAR(100),
    search_date       TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_search_history_date ON knowledge_search_history(search_date DESC);
CREATE INDEX IF NOT EXISTS idx_search_history_query ON knowledge_search_history(query_text);
CREATE INDEX IF NOT EXISTS idx_search_history_embedding ON knowledge_search_history USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 100);

-- Comments
COMMENT ON TABLE knowledge_search_history IS 'Query analytics for knowledge base optimization';

-- ====================================================================
-- SECTION 8: Utility Functions
-- ====================================================================

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_knowledge_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to knowledge_concepts
DROP TRIGGER IF EXISTS update_knowledge_concepts_timestamp ON knowledge_concepts;
CREATE TRIGGER update_knowledge_concepts_timestamp
    BEFORE UPDATE ON knowledge_concepts
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_timestamp();

-- Apply trigger to knowledge_graph
DROP TRIGGER IF EXISTS update_knowledge_graph_timestamp ON knowledge_graph;
CREATE TRIGGER update_knowledge_graph_timestamp
    BEFORE UPDATE ON knowledge_graph
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_timestamp();

-- ====================================================================
-- SECTION 9: Views
-- ====================================================================

-- Active concepts view (non-deprecated, current versions)
CREATE OR REPLACE VIEW v_knowledge_concepts_active AS
SELECT * FROM knowledge_concepts
WHERE is_current = TRUE
  AND deprecated_at IS NULL;

COMMENT ON VIEW v_knowledge_concepts_active IS 'Active, non-deprecated knowledge concepts';

-- Knowledge graph summary view
CREATE OR REPLACE VIEW v_knowledge_graph_summary AS
SELECT 
    COUNT(*) as total_concepts,
    COUNT(*) FILTER (WHERE validation_status = 'VALIDATED') as validated_concepts,
    COUNT(DISTINCT concept_type) as distinct_types,
    AVG(confidence) as avg_confidence
FROM knowledge_concepts
WHERE is_current = TRUE
  AND deprecated_at IS NULL;

COMMENT ON VIEW v_knowledge_graph_summary IS 'Knowledge base statistics and summary';

-- ====================================================================
-- SUCCESS MESSAGE
-- ====================================================================

DO $$
BEGIN
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Knowledge Base Schema v1.0.0 deployed successfully!';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - knowledge_concepts (7 indexes)';
    RAISE NOTICE '  - knowledge_graph (6 indexes)';
    RAISE NOTICE '  - knowledge_versions (3 indexes)';
    RAISE NOTICE '  - knowledge_tags (2 indexes)';
    RAISE NOTICE '  - knowledge_concept_tags (2 indexes)';
    RAISE NOTICE '  - knowledge_distillation_log (3 indexes)';
    RAISE NOTICE '  - knowledge_search_history (3 indexes)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - v_knowledge_concepts_active';
    RAISE NOTICE '  - v_knowledge_graph_summary';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - update_knowledge_timestamp()';
    RAISE NOTICE '';
    RAISE NOTICE 'Triggers created:';
    RAISE NOTICE '  - update_knowledge_concepts_timestamp';
    RAISE NOTICE '  - update_knowledge_graph_timestamp';
    RAISE NOTICE '====================================================================';
END $$;
