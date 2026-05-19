-- ============================================
-- Sample Data for Memory System v0.3.1
-- Platform-agnostic AI Agent Knowledge Base
-- ============================================
-- 
-- Requires pg-embedding-gen-by-yhw extension (uses COPY FROM PROGRAM + Python proxy; see references/)

BEGIN;

-- Clear existing data (for demo purposes)
DELETE FROM memory.relations;
DELETE FROM memory.concepts;

|-- Insert sample concepts with optional embedding support
INSERT INTO memory.concepts (concept_id, name, category, description, content) VALUES
    ('user-001', 'Haiwen Yin (胖头鱼 🐟)', 'user_profile', 
     'Oracle/PostgreSQL/MySQL ACE Database Expert specializing in AI Agent Memory System development',
     '{"name": "Haiwen Yin", "nickname": "胖头鱼", "role": "ACE DB Expert"}'),
    
    ('db-001', 'PostgreSQL 18', 'knowledge_base/database', 
     'PostgreSQL Memory System',
     '{"version": "26ai", "features": ["DBMS_VECTOR_DATABASE"]}'),
     
    ('tech-001', 'Apache AGE', 'knowledge_base/technology', 
     'PostgreSQL Property Graph extension with Cypher support',
     '{"project": "apache.org", "license": "MIT", "version": "1.7.0"}');

|-- Create relationships
INSERT INTO memory.relations (from_concept_id, to_concept_id, relation_type, strength) VALUES
    ((SELECT concept_id FROM memory.concepts WHERE name = 'Haiwen Yin (胖头鱼 🐟)'),
     (SELECT concept_id FROM memory.concepts WHERE name = 'PostgreSQL 18'),
     'RELATED_TO', 0.9),
    
    ((SELECT concept_id FROM memory.concepts WHERE name = 'PostgreSQL 18'),
     (SELECT concept_id FROM memory.concepts WHERE name = 'Apache AGE'),
     'EXTENDS', 0.8);

COMMIT;

-- Verification query
-- Verify graph relationships using Cypher (requires AGE extension)
-- IMPORTANT: Use dollar quoting $$...$$ for Cypher strings, not single quotes!
SET search_path TO ag_catalog;
SELECT 
    start_node->>'name' || ' --[' || relation_type || ']--> ' || end_node->>'name' as graph_path,
    strength::float as confidence
FROM cypher('memory_graph', $$
    MATCH (node_a:concepts)-[r]->(node_b:concepts)
    RETURN node_a.name, type(r), node_b.name, r.strength
$$) AS (start_node agtype, relation_type agtype, end_node agtype, strength float);

-- v0.3.1 Note: For vector similarity search with pg-embedding-gen-by-yhw extension, use:
-- SELECT memory.generate_embedding_sql('your text here');
