-- ============================================
-- Task Plan System for PostgreSQL 18 (v0.3.2)
-- Task Plan Persistence System for PostgreSQL 18
-- ============================================

BEGIN;

-- ============================================
-- 1. TASK_PLANS - Core task plan table
-- ============================================
CREATE TABLE IF NOT EXISTS task_plans (
    plan_id       SERIAL PRIMARY KEY,
    plan_name     VARCHAR(200),                    -- Task name
    plan_type     VARCHAR(50) NOT NULL DEFAULT 'task',  -- task/deployment/research/analysis
    status        VARCHAR(30) DEFAULT 'PENDING',   -- PENDING/RUNNING/SUCCESS/FAILED/CANCELLED/PAUSED
    description   TEXT,                            -- Task description and intent
    goal          JSONB,                           -- Final goal (structured)
    
    -- Priority and time management
    priority      INTEGER DEFAULT 2 CHECK (priority BETWEEN 1 AND 5),
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    started_at    TIMESTAMPTZ,                     -- Start execution time
    updated_at    TIMESTAMPTZ,                     -- Last update status
    completed_at  TIMESTAMPTZ,                     -- Completion time
    expires_at    TIMESTAMPTZ,                     -- Expiration time
    
    -- Metadata (JSONB)
    metadata      JSONB,                           -- JSON: session_id, agent_context etc.
    tags          JSONB                            -- JSON: tag array
);

-- ============================================
-- 2. TASK_STEPS - Task step execution table
-- ============================================
CREATE TABLE IF NOT EXISTS task_steps (
    step_id       SERIAL PRIMARY KEY,
    plan_id       INTEGER NOT NULL REFERENCES task_plans(plan_id) ON DELETE CASCADE,
    step_order    INTEGER NOT NULL,                  -- Step sequence (1,2,3...)
    step_name     VARCHAR(200),                    -- Step name
    action        TEXT,                             -- Action description to execute
    tools_used    JSONB,                            -- JSON: tools used list
    
    -- Execution status
    status        VARCHAR(30) DEFAULT 'PENDING',   -- PENDING/IN_PROGRESS/SUCCESS/FAILED/BLOCKED
    result        TEXT,                             -- Step execution result
    error_msg     TEXT,                             -- Error message (if any)
    
    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    started_at    TIMESTAMPTZ,
    completed_at  TIMESTAMPTZ,
    
    UNIQUE (plan_id, step_order)
);

-- ============================================
-- 3. TASK_CONTEXT_SNAPSHOTS - Task context snapshot (critical for breakpoint recovery)
-- ============================================
CREATE TABLE IF NOT EXISTS task_context_snapshots (
    snapshot_id   SERIAL PRIMARY KEY,
    plan_id       INTEGER NOT NULL REFERENCES task_plans(plan_id),
    
    -- Snapshot type
    snapshot_type VARCHAR(30) DEFAULT 'AUTO',      -- AUTO/MANUAL/ON_ERROR
    
    -- Context content (complete state)
    context_data  JSONB,                             -- JSON: agent_state, conversation_history etc.
    memory_ids    JSONB,                             -- JSON: associated memory node ID list
    next_action   TEXT,                             -- Next action to execute description
    
    -- Snapshot information
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_latest     BOOLEAN DEFAULT FALSE,
    
    -- Trigger reason (Oracle TRIGGER is a reserved word, use trigger_reason instead)
    trigger_reason JSONB                            -- JSON: trigger_reason
);

-- ============================================
-- 4. TASK_TOOL_CALLS - Tool call records (audit trail)
-- ============================================
CREATE TABLE IF NOT EXISTS task_tool_calls (
    call_id       SERIAL PRIMARY KEY,
    plan_id       INTEGER NOT NULL REFERENCES task_plans(plan_id),
    step_id       INTEGER REFERENCES task_steps(step_id),
    
    -- Tool information
    tool_name     VARCHAR(100) NOT NULL,           -- tool name (terminal/browser/memory etc.)
    action        TEXT NOT NULL,                    -- Executed operation description
    
    -- Call result
    status        VARCHAR(30) DEFAULT 'SUCCESS',   -- SUCCESS/FAILED/TIMEOUT
    result_size   INTEGER,                           -- Return result size (bytes)
    
    -- Time information
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    duration_ms   INTEGER                            -- Execution duration milliseconds
);

-- ============================================
-- 5. TASK_DEPENDENCIES - Task dependency graph
-- ============================================
CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id SERIAL PRIMARY KEY,
    source_plan_id INTEGER NOT NULL REFERENCES task_plans(plan_id),
    target_plan_id INTEGER NOT NULL REFERENCES task_plans(plan_id),
    
    -- Dependency type
    dependency_type VARCHAR(30) DEFAULT 'HARD',    -- HARD/SOFT/EXCLUSIVE/RECOMMENDED
    condition     JSONB,                             -- JSON: trigger condition description
    
    created_at    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Task Plan Indexes (PostgreSQL optimized)
-- ============================================
CREATE INDEX IF NOT EXISTS idx_task_plans_status ON task_plans(status);
CREATE INDEX IF NOT EXISTS idx_task_plans_type ON task_plans(plan_type);
CREATE INDEX IF NOT EXISTS idx_task_plans_created ON task_plans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_task_plans_priority ON task_plans(priority, created_at);

CREATE INDEX IF NOT EXISTS idx_task_steps_plan ON task_steps(plan_id, step_order);
CREATE INDEX IF NOT EXISTS idx_task_steps_status ON task_steps(status);

CREATE INDEX IF NOT EXISTS idx_context_snapshot_plan ON task_context_snapshots(plan_id);

CREATE INDEX IF NOT EXISTS idx_tool_calls_plan ON task_tool_calls(plan_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_time ON task_tool_calls(created_at DESC);

COMMIT;

-- ============================================
-- Verification Queries (Run after execution)
-- ============================================
-- SELECT count(*) FROM information_schema.tables WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots', 'task_tool_calls', 'task_dependencies');
