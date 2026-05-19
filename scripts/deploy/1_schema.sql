-- ============================================================================
-- PostgreSQL Memory System v2.0.0 - Unified Schema
-- ============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;

-- ============================================================================
-- Core Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS entities (
    entity_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type   VARCHAR(32) NOT NULL CHECK (entity_type IN ('MEMORY','KNOWLEDGE','TASK_OUTPUT','EXPERIENCE','HARNESS_TEMPLATE')),
    name          VARCHAR(500) NOT NULL,
    description   TEXT,
    content       TEXT,
    category      VARCHAR(100),
    priority      INT DEFAULT 2,
    status        VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','ARCHIVED','DEPRECATED','DELETED')),
    tags          JSONB DEFAULT '[]',
    metadata      JSONB DEFAULT '{}',
    owned_by_agent VARCHAR(64),
    visibility    VARCHAR(32) DEFAULT 'SHARED' CHECK (visibility IN ('PRIVATE','SHARED','COLLABORATIVE')),
    accessible_to JSONB DEFAULT '[]',
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now(),
    expires_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS entity_edges (
    edge_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    target_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    edge_type   VARCHAR(64) NOT NULL,
    strength    NUMERIC DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 2),
    confidence  NUMERIC DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    properties  JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_meta (
    entity_id         BIGINT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    source_type       VARCHAR(32) DEFAULT 'MANUAL',
    source_entity_ids JSONB DEFAULT '[]',
    validation_status VARCHAR(32) DEFAULT 'PENDING' CHECK (validation_status IN ('PENDING','VALIDATED','REJECTED','DEPRECATED')),
    confidence        NUMERIC DEFAULT 0.8,
    version           INT DEFAULT 1,
    is_current        BOOLEAN DEFAULT TRUE,
    validated_at      TIMESTAMPTZ,
    deprecated_at     TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS entity_embeddings (
    entity_id   BIGINT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    embedding   vector(1024),
    embed_model VARCHAR(100) DEFAULT 'text-embedding-bge-m3',
    embedded_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- Agent Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_registry (
    agent_id         VARCHAR(64) PRIMARY KEY,
    agent_name       VARCHAR(200) NOT NULL,
    agent_type       VARCHAR(50) DEFAULT 'general',
    description      TEXT,
    capabilities     JSONB DEFAULT '[]',
    status           VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISABLED','SUSPENDED')),
    permission_level VARCHAR(32) DEFAULT 'READ_WRITE' CHECK (permission_level IN ('READ_ONLY','READ_WRITE','ADMIN')),
    pending_recovery BOOLEAN DEFAULT FALSE,
    recovered_count  INT DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_session (
    session_id       VARCHAR(128) PRIMARY KEY,
    agent_id         VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    is_active        BOOLEAN DEFAULT TRUE,
    context_snapshot JSONB DEFAULT '{}',
    working_memory_id BIGINT REFERENCES entities(entity_id),
    start_time       TIMESTAMPTZ DEFAULT now(),
    end_time         TIMESTAMPTZ,
    last_activity    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_access_log (
    log_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent_id    VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    entity_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    access_type VARCHAR(32) DEFAULT 'READ' CHECK (access_type IN ('READ','WRITE','DELETE','SHARE')),
    access_time TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_permission_log (
    log_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent_id      VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    old_status    VARCHAR(32),
    new_status    VARCHAR(32),
    change_reason TEXT,
    status        VARCHAR(32) DEFAULT 'APPLIED',
    created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_collaboration (
    collab_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sharing_agent   VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    receiving_agent VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    memory_id       BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    share_reason    TEXT,
    status          VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','APPROVED','REJECTED','EXPIRED')),
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- Task Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_plans (
    plan_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_name    VARCHAR(500) NOT NULL,
    plan_type    VARCHAR(50) DEFAULT 'task',
    status       VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','ACTIVE','PAUSED','COMPLETED','FAILED','CANCELLED')),
    description  TEXT,
    goal         TEXT,
    priority     INT DEFAULT 2,
    metadata     JSONB DEFAULT '{}',
    tags         JSONB DEFAULT '[]',
    created_at   TIMESTAMPTZ DEFAULT now(),
    started_at   TIMESTAMPTZ,
    updated_at   TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_steps (
    step_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id      BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    step_order   INT NOT NULL,
    step_name    VARCHAR(500) NOT NULL,
    action       TEXT,
    tools_used   JSONB DEFAULT '[]',
    status       VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','ACTIVE','COMPLETED','FAILED','SKIPPED')),
    result       TEXT,
    error_msg    TEXT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_context_snapshots (
    snapshot_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id        BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    snapshot_type  VARCHAR(32) DEFAULT 'MANUAL' CHECK (snapshot_type IN ('MANUAL','AUTO','CHECKPOINT','RECOVERY')),
    context_data   JSONB DEFAULT '{}',
    next_action    TEXT,
    is_latest      BOOLEAN DEFAULT TRUE,
    trigger_reason JSONB DEFAULT '{}',
    created_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS task_tool_calls (
    call_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id      BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    step_id      BIGINT REFERENCES task_steps(step_id) ON DELETE SET NULL,
    tool_name    VARCHAR(100) NOT NULL,
    action       TEXT,
    status       VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','ACTIVE','COMPLETED','FAILED')),
    result_size  INT,
    duration_ms  INT
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_plan_id  BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    target_plan_id  BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    dependency_type VARCHAR(32) DEFAULT 'HARD' CHECK (dependency_type IN ('HARD','SOFT','CONDITIONAL')),
    condition       TEXT
);

-- ============================================================================
-- Tag System
-- ============================================================================

CREATE TABLE IF NOT EXISTS tags (
    tag_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag_name     VARCHAR(100) UNIQUE NOT NULL,
    tag_category VARCHAR(50),
    usage_count  INT DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_tags (
    entity_id BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    tag_id    BIGINT NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (entity_id, tag_id)
);

-- ============================================================================
-- System Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS system_config (
    config_key   VARCHAR(200) PRIMARY KEY,
    config_value TEXT,
    description  TEXT,
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS system_users (
    user_id       VARCHAR(64) PRIMARY KEY,
    username      VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    salt          VARCHAR(64) NOT NULL,
    role          VARCHAR(32) DEFAULT 'USER' CHECK (role IN ('ADMIN','USER','VIEWER')),
    status        VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISABLED','LOCKED')),
    last_login    TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_category ON entities(category);
CREATE INDEX IF NOT EXISTS idx_entities_status ON entities(status);
CREATE INDEX IF NOT EXISTS idx_entities_owner ON entities(owned_by_agent);
CREATE INDEX IF NOT EXISTS idx_entities_visibility ON entities(visibility);
CREATE INDEX IF NOT EXISTS idx_entities_created ON entities(created_at);
CREATE INDEX IF NOT EXISTS idx_entities_type_owner ON entities(entity_type, owned_by_agent);
CREATE INDEX IF NOT EXISTS idx_entities_type_cat ON entities(entity_type, category);
CREATE INDEX IF NOT EXISTS idx_edges_source ON entity_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON entity_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON entity_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_source_type ON entity_edges(source_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_target_type ON entity_edges(target_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_km_validation ON knowledge_meta(validation_status);
CREATE INDEX IF NOT EXISTS idx_km_current ON knowledge_meta(is_current);
CREATE INDEX IF NOT EXISTS idx_access_agent ON entity_access_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_access_entity ON entity_access_log(entity_id);
CREATE INDEX IF NOT EXISTS idx_access_time ON entity_access_log(access_time);
CREATE INDEX IF NOT EXISTS idx_session_agent ON agent_session(agent_id);
CREATE INDEX IF NOT EXISTS idx_session_active ON agent_session(is_active);
CREATE INDEX IF NOT EXISTS idx_plan_status ON task_plans(status);
CREATE INDEX IF NOT EXISTS idx_step_plan ON task_steps(plan_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(tag_name);
CREATE INDEX IF NOT EXISTS idx_et_tag ON entity_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_emb_hnsw ON entity_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- ============================================================================
-- Apache AGE Graph
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'memory_graph') THEN
        PERFORM ag_catalog.create_graph('memory_graph');
    END IF;
END
$$;

-- ============================================================================
-- Views
-- ============================================================================

CREATE OR REPLACE VIEW v_memory_entities AS
SELECT e.entity_id, e.entity_type, e.name, e.description, e.content, e.category,
       e.priority, e.status, e.tags, e.metadata, e.owned_by_agent, e.visibility,
       e.accessible_to, e.created_at, e.updated_at, e.expires_at,
       ee.embedding, ee.embed_model, ee.embedded_at
FROM entities e
LEFT JOIN entity_embeddings ee ON e.entity_id = ee.entity_id
WHERE e.entity_type = 'MEMORY';

CREATE OR REPLACE VIEW v_knowledge_entities AS
SELECT e.entity_id, e.entity_type, e.name, e.description, e.content, e.category,
       e.priority, e.status, e.tags, e.metadata, e.owned_by_agent, e.visibility,
       e.accessible_to, e.created_at, e.updated_at, e.expires_at,
       km.source_type, km.source_entity_ids, km.validation_status, km.confidence AS km_confidence,
       km.version, km.is_current, km.validated_at, km.deprecated_at,
       ee.embedding, ee.embed_model, ee.embedded_at
FROM entities e
LEFT JOIN knowledge_meta km ON e.entity_id = km.entity_id
LEFT JOIN entity_embeddings ee ON e.entity_id = ee.entity_id
WHERE e.entity_type = 'KNOWLEDGE';

CREATE OR REPLACE VIEW v_active_sessions AS
SELECT s.session_id, s.agent_id, s.is_active, s.context_snapshot, s.working_memory_id,
       s.start_time, s.end_time, s.last_activity,
       a.agent_name, a.agent_type, a.permission_level
FROM agent_session s
JOIN agent_registry a ON s.agent_id = a.agent_id
WHERE s.is_active = TRUE;

CREATE OR REPLACE VIEW v_collaboration_status AS
SELECT c.collab_id, c.sharing_agent, c.receiving_agent, c.memory_id, c.share_reason,
       c.status, c.approved_at, c.created_at,
       sa.agent_name AS sharing_agent_name,
       ra.agent_name AS receiving_agent_name
FROM agent_collaboration c
JOIN agent_registry sa ON c.sharing_agent = sa.agent_id
JOIN agent_registry ra ON c.receiving_agent = ra.agent_id;

CREATE OR REPLACE VIEW v_entity_graph AS
SELECT ee.edge_id, ee.edge_type, ee.strength, ee.confidence, ee.properties, ee.created_at,
       ee.source_id, se.name AS source_name, se.entity_type AS source_type,
       ee.target_id, te.name AS target_name, te.entity_type AS target_type
FROM entity_edges ee
JOIN entities se ON ee.source_id = se.entity_id
JOIN entities te ON ee.target_id = te.entity_id;

-- ============================================================================
-- Helper Functions (memory schema)
-- These functions wrap pg-embedding-gen-by-yhw (custom extension by Haiwen Yin)
-- which uses COPY FROM PROGRAM + Python proxy to call embedding APIs.
-- Install pg-embedding-gen-by-yhw first: see references/ for instructions.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS memory;

CREATE OR REPLACE FUNCTION memory.generate_embedding(p_text TEXT)
RETURNS vector(1024)
LANGUAGE plpgsql VOLATILE
AS $$
DECLARE
    v_result vector(1024);
BEGIN
    SELECT embedding_generate(p_text)::vector INTO v_result;
    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION memory.add_concept_with_embedding(
    p_name VARCHAR,
    p_description TEXT,
    p_category VARCHAR,
    p_metadata JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_entity_id BIGINT;
    v_embedding vector(1024);
BEGIN
    INSERT INTO entities (entity_type, name, description, category, metadata, status)
    VALUES ('KNOWLEDGE', p_name, p_description, p_category, COALESCE(p_metadata, '{}'), 'ACTIVE')
    RETURNING entity_id INTO v_entity_id;

    INSERT INTO knowledge_meta (entity_id, source_type, validation_status, confidence, version, is_current)
    VALUES (v_entity_id, 'MANUAL', 'PENDING', 0.8, 1, TRUE);

    v_embedding := memory.generate_embedding(COALESCE(p_name, '') || ' ' || COALESCE(p_description, ''));

    INSERT INTO entity_embeddings (entity_id, embedding)
    VALUES (v_entity_id, v_embedding);

    RETURN v_entity_id;
END;
$$;

CREATE OR REPLACE FUNCTION memory.search_similar(
    p_query TEXT,
    p_limit INT DEFAULT 10
)
RETURNS TABLE(entity_id BIGINT, name VARCHAR, category VARCHAR, similarity FLOAT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_embedding vector(1024);
BEGIN
    v_embedding := memory.generate_embedding(p_query);

    RETURN QUERY
    SELECT ee.entity_id, e.name, e.category,
           1 - (ee.embedding <=> v_embedding) AS similarity
    FROM entity_embeddings ee
    JOIN entities e ON ee.entity_id = e.entity_id
    WHERE e.status = 'ACTIVE'
    ORDER BY ee.embedding <=> v_embedding
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- Seed Data
-- ============================================================================

INSERT INTO system_config (config_key, config_value, description)
VALUES ('system.version', '2.0.0', 'PostgreSQL Memory System version')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = now();

INSERT INTO system_config (config_key, config_value, description)
VALUES ('schema.deployed_at', now()::TEXT, 'Schema deployment timestamp')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = now();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE entities IS 'Core entity table storing all memory, knowledge, task outputs, experiences, and harness templates';
COMMENT ON TABLE entity_edges IS 'Directed relationships between entities with strength and confidence weights';
COMMENT ON TABLE knowledge_meta IS 'Metadata for KNOWLEDGE entities tracking validation, versioning, and lineage';
COMMENT ON TABLE entity_embeddings IS 'Vector embeddings for semantic search on entities';
COMMENT ON TABLE agent_registry IS 'Registered agents with their capabilities and permission levels';
COMMENT ON TABLE agent_session IS 'Active and historical agent sessions';
COMMENT ON TABLE entity_access_log IS 'Audit log of entity access by agents';
COMMENT ON TABLE agent_permission_log IS 'Audit log of agent permission changes';
COMMENT ON TABLE agent_collaboration IS 'Memory sharing and collaboration requests between agents';
COMMENT ON TABLE task_plans IS 'Task execution plans with status tracking';
COMMENT ON TABLE task_steps IS 'Individual steps within a task plan';
COMMENT ON TABLE task_context_snapshots IS 'Context snapshots for task recovery and resumption';
COMMENT ON TABLE task_tool_calls IS 'Tool invocation records within task steps';
COMMENT ON TABLE task_dependencies IS 'Dependencies between task plans';
COMMENT ON TABLE tags IS 'Tag dictionary with usage counts';
COMMENT ON TABLE entity_tags IS 'Many-to-many association between entities and tags';
COMMENT ON TABLE system_config IS 'System configuration key-value store';
COMMENT ON TABLE system_users IS 'System user accounts with authentication';

COMMENT ON COLUMN entities.entity_type IS 'Entity type: MEMORY, KNOWLEDGE, TASK_OUTPUT, EXPERIENCE, or HARNESS_TEMPLATE';
COMMENT ON COLUMN entities.visibility IS 'Access scope: PRIVATE (owner only), SHARED (all agents), COLLABORATIVE (specific agents)';
COMMENT ON COLUMN entities.accessible_to IS 'JSONB array of agent_ids with explicit access when visibility is COLLABORATIVE';
COMMENT ON COLUMN entities.priority IS 'Priority level: 1=high, 2=medium, 3=low';
COMMENT ON COLUMN entities.status IS 'Entity lifecycle status';
COMMENT ON COLUMN entity_edges.strength IS 'Relationship strength from 0.0 to 2.0';
COMMENT ON COLUMN entity_edges.confidence IS 'Confidence score from 0.0 to 1.0';
COMMENT ON COLUMN knowledge_meta.validation_status IS 'Validation state: PENDING, VALIDATED, REJECTED, or DEPRECATED';
COMMENT ON COLUMN knowledge_meta.is_current IS 'Whether this is the current version of the knowledge concept';
COMMENT ON COLUMN agent_registry.permission_level IS 'Agent permission: READ_ONLY, READ_WRITE, or ADMIN';
COMMENT ON COLUMN agent_collaboration.status IS 'Collaboration state: PENDING, APPROVED, REJECTED, or EXPIRED';
COMMENT ON COLUMN task_plans.status IS 'Plan lifecycle: PENDING, ACTIVE, PAUSED, COMPLETED, FAILED, or CANCELLED';
COMMENT ON COLUMN task_steps.status IS 'Step lifecycle: PENDING, ACTIVE, COMPLETED, FAILED, or SKIPPED';
