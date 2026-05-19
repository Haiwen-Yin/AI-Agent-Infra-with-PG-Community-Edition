-- ============================================================================
-- PostgreSQL Memory System v2.0.0 - Harness Templates
-- ============================================================================

-- ============================================================================
-- Extend entity_type constraint to include HARNESS_TEMPLATE
-- ============================================================================

ALTER TABLE entities DROP CONSTRAINT IF EXISTS entities_entity_type_check;
ALTER TABLE entities ADD CONSTRAINT entities_entity_type_check
    CHECK (entity_type IN ('MEMORY','KNOWLEDGE','TASK_OUTPUT','EXPERIENCE','HARNESS_TEMPLATE'));

-- ============================================================================
-- Harness Metadata Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS harness_meta (
    entity_id        BIGINT PRIMARY KEY REFERENCES entities(entity_id) ON DELETE CASCADE,
    template_version INT DEFAULT 1,
    template_status  VARCHAR(32) DEFAULT 'DRAFT' CHECK (template_status IN ('DRAFT','PUBLISHED','DEPRECATED','ARCHIVED')),
    variables        JSONB DEFAULT '{}',
    changelog        JSONB DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_harness_meta_status ON harness_meta(template_status);

-- ============================================================================
-- Seed Built-in Harness Templates
-- ============================================================================

-- 1. Research Analyst
INSERT INTO entities (entity_type, name, description, category, priority, status, metadata)
VALUES (
    'HARNESS_TEMPLATE',
    'Research Analyst',
    'Comprehensive research and analysis harness for information gathering, synthesis, and reporting',
    'research',
    1,
    'ACTIVE',
    '{
        "prompt_templates": {
            "system": "You are a research analyst. Gather information, analyze findings, and produce structured reports.",
            "research_plan": "Create a research plan for: {{topic}}",
            "synthesis": "Synthesize the following findings into a coherent analysis: {{findings}}",
            "report": "Generate a final report based on analysis: {{analysis}}"
        },
        "tool_bindings": ["web_search", "document_reader", "data_extractor", "note_taker"],
        "variables": {
            "topic": {"type": "string", "required": true, "description": "Research topic or question"},
            "depth": {"type": "string", "enum": ["quick", "standard", "deep"], "default": "standard"},
            "output_format": {"type": "string", "enum": ["summary", "report", "brief"], "default": "report"}
        },
        "guardrails": {
            "max_iterations": 10,
            "timeout_minutes": 30,
            "require_citations": true,
            "fact_check_enabled": true
        },
        "memory_access": {
            "read": ["MEMORY", "KNOWLEDGE"],
            "write": ["MEMORY"],
            "share": true
        },
        "evaluation": {
            "criteria": ["completeness", "accuracy", "citation_quality", "clarity"],
            "min_score": 0.7
        }
    }'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, template_status, variables, changelog)
SELECT entity_id, 1, 'PUBLISHED',
    '{"topic": {"type": "string", "required": true}, "depth": {"type": "string", "default": "standard"}, "output_format": {"type": "string", "default": "report"}}'::jsonb,
    '[{"version": 1, "date": "2025-01-01", "change": "Initial template"}]'::jsonb
FROM entities WHERE entity_type = 'HARNESS_TEMPLATE' AND name = 'Research Analyst'
ON CONFLICT DO NOTHING;

-- 2. Code Assistant
INSERT INTO entities (entity_type, name, description, category, priority, status, metadata)
VALUES (
    'HARNESS_TEMPLATE',
    'Code Assistant',
    'Software development harness for code generation, review, debugging, and refactoring',
    'development',
    1,
    'ACTIVE',
    '{
        "prompt_templates": {
            "system": "You are a code assistant. Help with coding tasks including writing, reviewing, and debugging code.",
            "generate": "Generate code for: {{task}} in {{language}}",
            "review": "Review the following code for issues and improvements: {{code}}",
            "debug": "Debug the following code with error: {{error}}\nCode: {{code}}"
        },
        "tool_bindings": ["code_editor", "file_system", "terminal", "linter", "test_runner"],
        "variables": {
            "task": {"type": "string", "required": true, "description": "Coding task description"},
            "language": {"type": "string", "required": true, "description": "Programming language"},
            "framework": {"type": "string", "required": false, "description": "Framework to use"},
            "style": {"type": "string", "enum": ["minimal", "documented", "enterprise"], "default": "documented"}
        },
        "guardrails": {
            "max_iterations": 15,
            "timeout_minutes": 20,
            "require_tests": true,
            "security_scan": true,
            "no_direct_exec": false
        },
        "memory_access": {
            "read": ["MEMORY", "KNOWLEDGE", "EXPERIENCE"],
            "write": ["MEMORY", "EXPERIENCE"],
            "share": true
        },
        "evaluation": {
            "criteria": ["correctness", "readability", "test_coverage", "security"],
            "min_score": 0.8
        }
    }'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, template_status, variables, changelog)
SELECT entity_id, 1, 'PUBLISHED',
    '{"task": {"type": "string", "required": true}, "language": {"type": "string", "required": true}, "framework": {"type": "string"}, "style": {"type": "string", "default": "documented"}}'::jsonb,
    '[{"version": 1, "date": "2025-01-01", "change": "Initial template"}]'::jsonb
FROM entities WHERE entity_type = 'HARNESS_TEMPLATE' AND name = 'Code Assistant'
ON CONFLICT DO NOTHING;

-- 3. Data Analyst
INSERT INTO entities (entity_type, name, description, category, priority, status, metadata)
VALUES (
    'HARNESS_TEMPLATE',
    'Data Analyst',
    'Data analysis harness for querying, transforming, visualizing, and interpreting datasets',
    'analytics',
    1,
    'ACTIVE',
    '{
        "prompt_templates": {
            "system": "You are a data analyst. Analyze data, create visualizations, and derive insights.",
            "analyze": "Analyze the following dataset: {{dataset_description}}",
            "query": "Write a query to: {{query_goal}}",
            "visualize": "Suggest a visualization for: {{data_pattern}}"
        },
        "tool_bindings": ["sql_runner", "data_processor", "chart_generator", "statistics_engine"],
        "variables": {
            "dataset_description": {"type": "string", "required": true, "description": "Description of the dataset"},
            "analysis_type": {"type": "string", "enum": ["exploratory", "confirmatory", "predictive"], "default": "exploratory"},
            "output_format": {"type": "string", "enum": ["table", "chart", "narrative"], "default": "narrative"}
        },
        "guardrails": {
            "max_iterations": 8,
            "timeout_minutes": 25,
            "validate_results": true,
            "max_rows_return": 10000,
            "pii_detection": true
        },
        "memory_access": {
            "read": ["MEMORY", "KNOWLEDGE"],
            "write": ["MEMORY"],
            "share": false
        },
        "evaluation": {
            "criteria": ["accuracy", "insight_depth", "visualization_quality", "actionability"],
            "min_score": 0.75
        }
    }'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, template_status, variables, changelog)
SELECT entity_id, 1, 'PUBLISHED',
    '{"dataset_description": {"type": "string", "required": true}, "analysis_type": {"type": "string", "default": "exploratory"}, "output_format": {"type": "string", "default": "narrative"}}'::jsonb,
    '[{"version": 1, "date": "2025-01-01", "change": "Initial template"}]'::jsonb
FROM entities WHERE entity_type = 'HARNESS_TEMPLATE' AND name = 'Data Analyst'
ON CONFLICT DO NOTHING;

-- 4. Task Planner
INSERT INTO entities (entity_type, name, description, category, priority, status, metadata)
VALUES (
    'HARNESS_TEMPLATE',
    'Task Planner',
    'Orchestration harness for breaking down complex tasks, planning execution, and managing workflows',
    'orchestration',
    1,
    'ACTIVE',
    '{
        "prompt_templates": {
            "system": "You are a task planner. Break down complex goals into actionable steps and coordinate execution.",
            "decompose": "Break down the following goal into subtasks: {{goal}}",
            "prioritize": "Prioritize these tasks: {{tasks}}",
            "adjust": "Adjust the plan based on: {{feedback}}"
        },
        "tool_bindings": ["task_manager", "scheduler", "dependency_resolver", "progress_tracker"],
        "variables": {
            "goal": {"type": "string", "required": true, "description": "High-level goal or objective"},
            "complexity": {"type": "string", "enum": ["simple", "moderate", "complex"], "default": "moderate"},
            "parallelism": {"type": "integer", "default": 1, "description": "Max parallel subtasks"}
        },
        "guardrails": {
            "max_iterations": 20,
            "timeout_minutes": 60,
            "max_subtasks": 50,
            "require_approval": false,
            "auto_retry": true
        },
        "memory_access": {
            "read": ["MEMORY", "KNOWLEDGE", "TASK_OUTPUT"],
            "write": ["MEMORY", "TASK_OUTPUT"],
            "share": true
        },
        "evaluation": {
            "criteria": ["goal_alignment", "completeness", "feasibility", "efficiency"],
            "min_score": 0.7
        }
    }'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, template_status, variables, changelog)
SELECT entity_id, 1, 'PUBLISHED',
    '{"goal": {"type": "string", "required": true}, "complexity": {"type": "string", "default": "moderate"}, "parallelism": {"type": "integer", "default": 1}}'::jsonb,
    '[{"version": 1, "date": "2025-01-01", "change": "Initial template"}]'::jsonb
FROM entities WHERE entity_type = 'HARNESS_TEMPLATE' AND name = 'Task Planner'
ON CONFLICT DO NOTHING;

-- 5. Security Auditor
INSERT INTO entities (entity_type, name, description, category, priority, status, metadata)
VALUES (
    'HARNESS_TEMPLATE',
    'Security Auditor',
    'Security analysis harness for vulnerability scanning, compliance checking, and threat assessment',
    'security',
    1,
    'ACTIVE',
    '{
        "prompt_templates": {
            "system": "You are a security auditor. Identify vulnerabilities, check compliance, and assess threats.",
            "scan": "Perform a security scan on: {{target}}",
            "compliance": "Check compliance against: {{standard}} for: {{scope}}",
            "threat_model": "Create a threat model for: {{system_description}}"
        },
        "tool_bindings": ["vulnerability_scanner", "compliance_checker", "log_analyzer", "report_generator"],
        "variables": {
            "target": {"type": "string", "required": true, "description": "Target system or code to audit"},
            "scan_type": {"type": "string", "enum": ["quick", "standard", "comprehensive"], "default": "standard"},
            "standard": {"type": "string", "enum": ["OWASP", "CIS", "SOC2", "PCI-DSS"], "default": "OWASP"}
        },
        "guardrails": {
            "max_iterations": 12,
            "timeout_minutes": 45,
            "readonly_mode": true,
            "no_exploit": true,
            "log_all_actions": true
        },
        "memory_access": {
            "read": ["MEMORY", "KNOWLEDGE"],
            "write": ["MEMORY"],
            "share": false
        },
        "evaluation": {
            "criteria": ["coverage", "severity_accuracy", "remediation_quality", "false_positive_rate"],
            "min_score": 0.85
        }
    }'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, template_status, variables, changelog)
SELECT entity_id, 1, 'PUBLISHED',
    '{"target": {"type": "string", "required": true}, "scan_type": {"type": "string", "default": "standard"}, "standard": {"type": "string", "default": "OWASP"}}'::jsonb,
    '[{"version": 1, "date": "2025-01-01", "change": "Initial template"}]'::jsonb
FROM entities WHERE entity_type = 'HARNESS_TEMPLATE' AND name = 'Security Auditor'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- System Config
-- ============================================================================

INSERT INTO system_config (config_key, config_value, description)
VALUES ('harness.builtin_templates', '5', 'Number of built-in harness templates')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, updated_at = now();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE harness_meta IS 'Metadata for HARNESS_TEMPLATE entities tracking versioning, status, and variables';
COMMENT ON COLUMN harness_meta.template_status IS 'Template lifecycle: DRAFT, PUBLISHED, DEPRECATED, or ARCHIVED';
COMMENT ON COLUMN harness_meta.variables IS 'JSONB schema of configurable template variables';
COMMENT ON COLUMN harness_meta.changelog IS 'JSONB array of version change records';
