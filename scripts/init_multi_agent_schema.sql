-- ============================================
-- Multi-Agent Architecture Schema for PG18
-- Part of memory-pg18-by-yhw v0.3.3
-- Created: 2026-05-07 by Haiwen Yin (胖头鱼 🐟)
-- ============================================

-- ============================================
-- 1. AGENT_REGISTRY - Agent lifecycle management
-- ============================================
CREATE TABLE IF NOT EXISTS agent_registry (
    agent_id          SERIAL PRIMARY KEY,
    agent_name        VARCHAR(200) NOT NULL UNIQUE,
    agent_type        VARCHAR(50) NOT NULL DEFAULT 'general',
    status            VARCHAR(30) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    capabilities      JSONB DEFAULT '{}'::jsonb,
    description       TEXT,
    
    -- Metadata
    version           VARCHAR(20),
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen         TIMESTAMP WITH TIME ZONE,
    
    -- Configuration
    max_concurrency   INTEGER DEFAULT 1 CHECK (max_concurrency > 0),
    priority          INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5)
);

COMMENT ON TABLE agent_registry IS 'Centralized registry for AI agents lifecycle management';
COMMENT ON COLUMN agent_registry.capabilities IS 'JSONB: List of capabilities the agent can perform';

-- ============================================
-- 2. AGENT_MEMORY_ACCESS - Memory access control
-- ============================================
CREATE TABLE IF NOT EXISTS agent_memory_access (
    access_id         SERIAL PRIMARY KEY,
    agent_id          INTEGER REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    
    -- Access policy
    memory_scope      VARCHAR(30) DEFAULT 'SHARED' CHECK (memory_scope IN ('SHARED', 'PRIVATE', 'COLLABORATIVE')),
    accessible_to     JSONB DEFAULT '[]'::jsonb,  -- Array of agent_ids for COLLABORATIVE
    
    -- Permissions
    can_read          BOOLEAN DEFAULT TRUE,
    can_write         BOOLEAN DEFAULT FALSE,
    can_delete        BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at        TIMESTAMP WITH TIME ZONE,
    
    UNIQUE (agent_id, memory_scope)
);

COMMENT ON TABLE agent_memory_access IS 'Fine-grained memory access control per agent';
COMMENT ON COLUMN agent_memory_access.memory_scope IS 'SHARED=public, PRIVATE=owner-only, COLLABORATIVE=list-of-agents';

-- ============================================
-- 3. AGENT_COLLABORATION - Agent-to-agent communication
-- ============================================
CREATE TABLE IF NOT EXISTS agent_collaboration (
    collab_id         SERIAL PRIMARY KEY,
    source_agent_id   INTEGER REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    target_agent_id   INTEGER REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    
    -- Collaboration type
    collab_type       VARCHAR(50) DEFAULT 'REQUEST',  -- REQUEST/RESPONSE/SYNC/ASYNC
    priority          INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5),
    
    -- Message content
    message           TEXT,
    response          TEXT,
    
    -- Status tracking
    status            VARCHAR(30) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED')),
    
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at      TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE agent_collaboration IS 'Agent-to-agent communication channels';

-- ============================================
-- 4. AGENT_SESSION - Session management
-- ============================================
CREATE TABLE IF NOT EXISTS agent_session (
    session_id        SERIAL PRIMARY KEY,
    agent_id          INTEGER REFERENCES agent_registry(agent_id) ON DELETE CASCADE,
    
    -- Session state
    is_active         BOOLEAN DEFAULT TRUE,
    started_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at          TIMESTAMP WITH TIME ZONE,
    
    -- Context tracking
    task_plan_id      INTEGER REFERENCES task_plans(plan_id),
    memory_accessed   JSONB DEFAULT '[]'::jsonb,  -- List of memory node IDs accessed
    actions_performed INTEGER DEFAULT 0,
    
    -- Resource usage
    tokens_used       BIGINT DEFAULT 0,
    duration_seconds  INTEGER
    
);

COMMENT ON TABLE agent_session IS 'Active session tracking and monitoring';

-- ============================================
-- Indexes for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_agent_registry_name ON agent_registry(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_registry_status ON agent_registry(status);
CREATE INDEX IF NOT EXISTS idx_agent_memory_access_agent ON agent_memory_access(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_collab_source ON agent_collaboration(source_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_collab_target ON agent_collaboration(target_agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_session_active ON agent_session(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_agent_session_agent ON agent_session(agent_id);

-- ============================================
-- Seed Data - Example Agents (Optional)
-- Seed Data - Example Agents (Optional)
INSERT INTO agent_registry (agent_name, agent_type, capabilities, status) VALUES
    ('analysis-agent', 'analytical', '{"sql_query": true, "data_analysis": true}', 'ACTIVE'),
    ('writing-agent', 'content', '{"text_generation": true, "editing": true}', 'ACTIVE'),
    ('deployment-agent', 'operations', '{"database_migration": true, "schema_management": true}')
ON CONFLICT (agent_name) DO NOTHING;

-- ============================================
-- Views for Easy Access
-- ============================================
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT 
    s.session_id,
    ar.agent_name,
    ar.agent_type,
    s.is_active,
    s.started_at,
    s.actions_performed,
    s.tokens_used
FROM agent_session s
JOIN agent_registry ar ON s.agent_id = ar.agent_id
WHERE s.is_active = true;

CREATE OR REPLACE VIEW v_collaboration_status AS
SELECT 
    ac.collab_id,
    sa.agent_name AS source_agent,
    ta.agent_name AS target_agent,
    ac.collab_type,
    ac.status,
    ac.created_at
FROM agent_collaboration ac
JOIN agent_registry sa ON ac.source_agent_id = sa.agent_id
JOIN agent_registry ta ON ac.target_agent_id = ta.agent_id;
