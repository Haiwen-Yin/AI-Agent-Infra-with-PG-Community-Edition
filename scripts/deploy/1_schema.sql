-- ============================================================================
-- PostgreSQL Memory System v2.2.0 - Unified Schema
-- Workspace & Context Continuity
-- ============================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;

-- ============================================================================
-- Core Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS entities (
    entity_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_type     VARCHAR(32) NOT NULL CHECK (entity_type IN ('MEMORY','KNOWLEDGE','TASK_OUTPUT','EXPERIENCE','HARNESS_TEMPLATE')),
    title           VARCHAR(500) NOT NULL,
    content         TEXT,
    summary         VARCHAR(2000),
    category        VARCHAR(100),
    status          VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','ARCHIVED','DELETED','DRAFT')),
    importance      INT DEFAULT 5 CHECK (importance BETWEEN 1 AND 10),
    owned_by_agent  VARCHAR(64),
    source_agent    VARCHAR(64),
    visibility      VARCHAR(16) DEFAULT 'PRIVATE' CHECK (visibility IN ('PRIVATE','SHARED','PUBLIC')),
    retrieval_count INT DEFAULT 0,
    workspace_id    BIGINT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now(),
    expires_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS entity_edges (
    edge_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    source_type VARCHAR(32) NOT NULL,
    target_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    edge_type   VARCHAR(64) NOT NULL,
    strength    NUMERIC DEFAULT 1.0 CHECK (strength >= 0 AND strength <= 1),
    confidence  NUMERIC DEFAULT 0.8 CHECK (confidence >= 0 AND confidence <= 1),
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_meta (
    entity_id     BIGINT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    entity_type   VARCHAR(32) DEFAULT 'KNOWLEDGE',
    domain        VARCHAR(100),
    topic         VARCHAR(200),
    difficulty    VARCHAR(32) DEFAULT 'INTERMEDIATE' CHECK (difficulty IN ('BEGINNER','INTERMEDIATE','ADVANCED','EXPERT')),
    review_count  INT DEFAULT 0,
    last_reviewed TIMESTAMPTZ,
    next_review   TIMESTAMPTZ DEFAULT (now() + INTERVAL '7 days')
);

CREATE TABLE IF NOT EXISTS harness_meta (
    entity_id        BIGINT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    entity_type      VARCHAR(32) DEFAULT 'HARNESS_TEMPLATE',
    template_version INT DEFAULT 1,
    input_schema     JSONB,
    output_schema    JSONB,
    execution_mode   VARCHAR(32) DEFAULT 'SEQUENTIAL' CHECK (execution_mode IN ('SEQUENTIAL','PARALLEL','CONDITIONAL'))
);

CREATE TABLE IF NOT EXISTS entity_embeddings (
    entity_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    entity_type VARCHAR(32),
    embedding   vector(1024),
    embed_model VARCHAR(100) DEFAULT 'text-embedding-bge-m3',
    embedded_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (entity_id, entity_type)
);

-- ============================================================================
-- Tag System (normalized)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tags (
    tag_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tag_name     VARCHAR(100) UNIQUE NOT NULL,
    tag_group    VARCHAR(50),
    usage_count  INT DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_tags (
    entity_id   BIGINT NOT NULL,
    entity_type VARCHAR(32) NOT NULL,
    tag_id      BIGINT NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (entity_id, entity_type, tag_id),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE
);

-- ============================================================================
-- Agent Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_registry (
    agent_id     VARCHAR(64) PRIMARY KEY,
    agent_name   VARCHAR(200) NOT NULL,
    agent_type   VARCHAR(50) DEFAULT 'general',
    description  TEXT,
    capabilities JSONB DEFAULT '[]',
    config       JSONB DEFAULT '{}',
    status       VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','INACTIVE','SUSPENDED','DECOMMISSIONED')),
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_session (
    session_id              VARCHAR(128) PRIMARY KEY,
    agent_id                VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    owner_user_id           VARCHAR(64),
    workspace_id            BIGINT,
    predecessor_session_id  VARCHAR(128),
    is_active               BOOLEAN DEFAULT TRUE,
    context                 JSONB DEFAULT '{}',
    start_time              TIMESTAMPTZ DEFAULT now(),
    end_time                TIMESTAMPTZ,
    last_activity           TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS entity_access_log (
    log_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_id   BIGINT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
    agent_id    VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    access_type VARCHAR(32) DEFAULT 'READ' CHECK (access_type IN ('READ','WRITE','DELETE','SHARE')),
    session_id  VARCHAR(128),
    access_time TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_collaboration (
    collab_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_agent_id VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    target_agent_id VARCHAR(64) NOT NULL REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    col_type        VARCHAR(32) DEFAULT 'SHARE',
    entity_id       BIGINT REFERENCES entities(entity_id) ON DELETE SET NULL,
    context         JSONB,
    strength        NUMERIC DEFAULT 1.0,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- Workspace Tables (v2.2.0)
-- ============================================================================

CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workspace_name     VARCHAR(200),
    workspace_type     VARCHAR(32) DEFAULT 'CONVERSATION' CHECK (workspace_type IN ('CONVERSATION','AUTONOMOUS','PIPELINE')),
    isolation_mode     VARCHAR(16) DEFAULT 'SHARED' CHECK (isolation_mode IN ('SHARED','ISOLATED')),
    owner_user_id      VARCHAR(64),
    current_agent_id   VARCHAR(64),
    current_session_id VARCHAR(128),
    summary            TEXT,
    metadata           JSONB DEFAULT '{}',
    status             VARCHAR(32) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','PAUSED','ARCHIVED')),
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workspace_context (
    context_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workspace_id      BIGINT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    agent_id          VARCHAR(64),
    session_id        VARCHAR(128),
    context_type      VARCHAR(32) NOT NULL CHECK (context_type IN ('SNAPSHOT','CHECKPOINT','HANDOFF','SUMMARY','ERROR_STATE','AUTO_SAVE')),
    context_data      JSONB DEFAULT '{}',
    parent_context_id BIGINT REFERENCES workspace_context(context_id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workspace_tasks (
    workspace_id BIGINT NOT NULL REFERENCES workspaces(workspace_id) ON DELETE CASCADE,
    plan_id      BIGINT NOT NULL,
    assigned_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (workspace_id, plan_id)
);

-- ============================================================================
-- Task Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_plans (
    plan_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent_id       VARCHAR(64),
    goal           TEXT NOT NULL,
    status         VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','RUNNING','BLOCKED','SUCCESS','FAILED','CANCELLED')),
    priority       INT DEFAULT 5,
    strategy       VARCHAR(200),
    result_summary TEXT,
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_at     TIMESTAMPTZ DEFAULT now(),
    completed_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_steps (
    step_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id      BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    plan_status  VARCHAR(32) DEFAULT 'PENDING',
    step_order   INT NOT NULL,
    description  TEXT,
    tool_name    VARCHAR(100),
    tool_input   JSONB,
    tool_output  JSONB,
    status       VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','RUNNING','SUCCESS','FAILED','SKIPPED')),
    started_at   TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS task_context_snapshots (
    snapshot_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id        BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    snapshot_type  VARCHAR(32) DEFAULT 'MANUAL' CHECK (snapshot_type IN ('MANUAL','AUTO','CHECKPOINT','RECOVERY')),
    context_data   JSONB DEFAULT '{}',
    created_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS task_tool_calls (
    call_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id      BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    step_id      BIGINT REFERENCES task_steps(step_id) ON DELETE SET NULL,
    tool_name    VARCHAR(100) NOT NULL,
    tool_input   JSONB,
    tool_output  JSONB,
    status       VARCHAR(32) DEFAULT 'PENDING' CHECK (status IN ('PENDING','RUNNING','SUCCESS','FAILED')),
    duration_ms  INT
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    dep_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_plan_id   BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    target_plan_id   BIGINT NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    dep_type         VARCHAR(32) DEFAULT 'HARD' CHECK (dep_type IN ('HARD','SOFT','CONDITIONAL')),
    created_at       TIMESTAMPTZ DEFAULT now()
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
CREATE INDEX IF NOT EXISTS idx_entities_workspace ON entities(workspace_id);
CREATE INDEX IF NOT EXISTS idx_edges_source ON entity_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON entity_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON entity_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_source_type ON entity_edges(source_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_target_type ON entity_edges(target_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_km_domain ON knowledge_meta(domain);
CREATE INDEX IF NOT EXISTS idx_km_next_review ON knowledge_meta(next_review);
CREATE INDEX IF NOT EXISTS idx_hm_execution_mode ON harness_meta(execution_mode);
CREATE INDEX IF NOT EXISTS idx_et_tag ON entity_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_emb_hnsw ON entity_embeddings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_session_agent ON agent_session(agent_id);
CREATE INDEX IF NOT EXISTS idx_session_active ON agent_session(is_active);
CREATE INDEX IF NOT EXISTS idx_session_workspace ON agent_session(workspace_id);
CREATE INDEX IF NOT EXISTS idx_access_agent ON entity_access_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_access_entity ON entity_access_log(entity_id);
CREATE INDEX IF NOT EXISTS idx_access_time ON entity_access_log(access_time);
CREATE INDEX IF NOT EXISTS idx_ws_status ON workspaces(status);
CREATE INDEX IF NOT EXISTS idx_ws_owner ON workspaces(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_wctx_workspace ON workspace_context(workspace_id);
CREATE INDEX IF NOT EXISTS idx_wctx_type ON workspace_context(context_type);
CREATE INDEX IF NOT EXISTS idx_plan_status ON task_plans(status);
CREATE INDEX IF NOT EXISTS idx_step_plan ON task_steps(plan_id);

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
SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
       e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
       e.retrieval_count, e.workspace_id, e.created_at, e.updated_at, e.expires_at,
       ee.embedding, ee.embed_model, ee.embedded_at
FROM entities e
LEFT JOIN entity_embeddings ee ON e.entity_id = ee.entity_id
WHERE e.entity_type = 'MEMORY';

CREATE OR REPLACE VIEW v_knowledge_entities AS
SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
       e.importance, e.status, e.owned_by_agent, e.source_agent, e.visibility,
       e.retrieval_count, e.workspace_id, e.created_at, e.updated_at, e.expires_at,
       km.domain, km.topic, km.difficulty, km.review_count,
       km.last_reviewed, km.next_review,
       ee.embedding, ee.embed_model, ee.embedded_at
FROM entities e
LEFT JOIN knowledge_meta km ON e.entity_id = km.entity_id
LEFT JOIN entity_embeddings ee ON e.entity_id = ee.entity_id
WHERE e.entity_type = 'KNOWLEDGE';

CREATE OR REPLACE VIEW v_active_sessions AS
SELECT s.session_id, s.agent_id, s.is_active, s.context, s.workspace_id,
       s.owner_user_id, s.predecessor_session_id,
       s.start_time, s.end_time, s.last_activity,
       a.agent_name, a.agent_type
FROM agent_session s
JOIN agent_registry a ON s.agent_id = a.agent_id
WHERE s.is_active = TRUE;

CREATE OR REPLACE VIEW v_entity_graph AS
SELECT ee.edge_id, ee.edge_type, ee.strength, ee.confidence, ee.metadata, ee.created_at,
       ee.source_id, se.title AS source_title, se.entity_type AS source_type,
       ee.target_id, te.title AS target_title, te.entity_type AS target_type
FROM entity_edges ee
JOIN entities se ON ee.source_id = se.entity_id
JOIN entities te ON ee.target_id = te.entity_id;

-- ============================================================================
-- Helper Functions (memory schema)
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
    p_title VARCHAR,
    p_content TEXT,
    p_category VARCHAR,
    p_importance INT DEFAULT 5
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_entity_id BIGINT;
    v_embedding vector(1024);
BEGIN
    INSERT INTO entities (entity_type, title, content, category, importance, status)
    VALUES ('KNOWLEDGE', p_title, p_content, p_category, p_importance, 'ACTIVE')
    RETURNING entity_id INTO v_entity_id;

    INSERT INTO knowledge_meta (entity_id)
    VALUES (v_entity_id);

    v_embedding := memory.generate_embedding(COALESCE(p_title, '') || ' ' || COALESCE(p_content, ''));

    INSERT INTO entity_embeddings (entity_id, entity_type, embedding)
    VALUES (v_entity_id, 'KNOWLEDGE', v_embedding);

    RETURN v_entity_id;
END;
$$;

CREATE OR REPLACE FUNCTION memory.search_similar(
    p_query TEXT,
    p_limit INT DEFAULT 10
)
RETURNS TABLE(entity_id BIGINT, title VARCHAR, category VARCHAR, similarity FLOAT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_embedding vector(1024);
BEGIN
    v_embedding := memory.generate_embedding(p_query);

    RETURN QUERY
    SELECT ee.entity_id, e.title, e.category,
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
VALUES ('system.version', '2.2.0', 'PostgreSQL Memory System version')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = now();

INSERT INTO system_config (config_key, config_value, description)
VALUES ('schema.deployed_at', now()::TEXT, 'Schema deployment timestamp')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = now();

INSERT INTO system_users (user_id, username, password_hash, salt, role, status)
VALUES ('admin', 'admin', 'placeholder_hash', 'placeholder_salt', 'ADMIN', 'ACTIVE')
ON CONFLICT (user_id) DO NOTHING;
