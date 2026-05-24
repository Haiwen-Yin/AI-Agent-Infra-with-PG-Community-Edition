-- ============================================================================
-- PostgreSQL Memory System v2.2.1 - Built-in Harness Templates
-- ============================================================================

-- Research Analyst
INSERT INTO entities (entity_type, title, summary, category, importance, status, visibility)
VALUES ('HARNESS_TEMPLATE', 'Research Analyst', 'Multi-step research workflow', 'research', 5, 'ACTIVE', 'SHARED')
ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, input_schema, output_schema, execution_mode)
SELECT entity_id, 1,
    '{"type":"object","properties":{"role":{"type":"string","description":"Agent role"},"domain":{"type":"string","description":"Research domain"},"objective":{"type":"string","description":"Research objective"},"query":{"type":"string","description":"Search query"}},"required":["role","objective"]}'::jsonb,
    '{"type":"object","properties":{"report":{"type":"string"},"sources":{"type":"array"}}}'::jsonb,
    'SEQUENTIAL'
FROM entities
WHERE entity_type = 'HARNESS_TEMPLATE' AND title = 'Research Analyst'
ON CONFLICT DO NOTHING;

-- Code Assistant
INSERT INTO entities (entity_type, title, summary, category, importance, status, visibility)
VALUES ('HARNESS_TEMPLATE', 'Code Assistant', 'Code analysis and generation workflow', 'development', 5, 'ACTIVE', 'SHARED')
ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, input_schema, output_schema, execution_mode)
SELECT entity_id, 1,
    '{"type":"object","properties":{"role":{"type":"string","description":"Agent role"},"language":{"type":"string","description":"Programming language"},"guidelines":{"type":"string","description":"Coding guidelines"},"task":{"type":"string","description":"Code task"}},"required":["role","task"]}'::jsonb,
    '{"type":"object","properties":{"code":{"type":"string"},"explanation":{"type":"string"}}}'::jsonb,
    'SEQUENTIAL'
FROM entities
WHERE entity_type = 'HARNESS_TEMPLATE' AND title = 'Code Assistant'
ON CONFLICT DO NOTHING;

-- Data Analyst
INSERT INTO entities (entity_type, title, summary, category, importance, status, visibility)
VALUES ('HARNESS_TEMPLATE', 'Data Analyst', 'Data pipeline and analysis workflow', 'analytics', 5, 'ACTIVE', 'SHARED')
ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, input_schema, output_schema, execution_mode)
SELECT entity_id, 1,
    '{"type":"object","properties":{"role":{"type":"string","description":"Agent role"},"focus_area":{"type":"string","description":"Analysis focus"},"data_query":{"type":"string","description":"Data query"}},"required":["role","focus_area"]}'::jsonb,
    '{"type":"object","properties":{"analysis":{"type":"string"},"visualizations":{"type":"array"}}}'::jsonb,
    'PARALLEL'
FROM entities
WHERE entity_type = 'HARNESS_TEMPLATE' AND title = 'Data Analyst'
ON CONFLICT DO NOTHING;

-- Task Planner
INSERT INTO entities (entity_type, title, summary, category, importance, status, visibility)
VALUES ('HARNESS_TEMPLATE', 'Task Planner', 'General task planning and execution', 'orchestration', 5, 'ACTIVE', 'SHARED')
ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, input_schema, output_schema, execution_mode)
SELECT entity_id, 1,
    '{"type":"object","properties":{"role":{"type":"string","description":"Agent role"},"constraints":{"type":"string","description":"Task constraints"},"objective":{"type":"string","description":"Task objective"}},"required":["role","objective"]}'::jsonb,
    '{"type":"object","properties":{"plan":{"type":"array"},"status":{"type":"string"}}}'::jsonb,
    'CONDITIONAL'
FROM entities
WHERE entity_type = 'HARNESS_TEMPLATE' AND title = 'Task Planner'
ON CONFLICT DO NOTHING;

-- Security Auditor
INSERT INTO entities (entity_type, title, summary, category, importance, status, visibility)
VALUES ('HARNESS_TEMPLATE', 'Security Auditor', 'Security analysis and audit workflow', 'security', 5, 'ACTIVE', 'SHARED')
ON CONFLICT DO NOTHING;

INSERT INTO harness_meta (entity_id, template_version, input_schema, output_schema, execution_mode)
SELECT entity_id, 1,
    '{"type":"object","properties":{"role":{"type":"string","description":"Agent role"},"policies":{"type":"string","description":"Security policies"},"action":{"type":"string","description":"Audit action"}},"required":["role","policies"]}'::jsonb,
    '{"type":"object","properties":{"findings":{"type":"array"},"risk_level":{"type":"string"}}}'::jsonb,
    'SEQUENTIAL'
FROM entities
WHERE entity_type = 'HARNESS_TEMPLATE' AND title = 'Security Auditor'
ON CONFLICT DO NOTHING;
