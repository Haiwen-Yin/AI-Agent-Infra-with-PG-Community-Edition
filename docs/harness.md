# Harness Templates — PostgreSQL Memory System v2.2.0

## Architecture

Harness templates are reusable agent execution blueprints stored as ENTITIES
with `entity_type='HARNESS_TEMPLATE'`. The `harness_meta` table stores
template-specific metadata: `input_schema` (JSONB), `output_schema` (JSONB),
and `execution_mode` (VARCHAR).

```
┌─────────────────────────────────────────────────────┐
│                    ENTITIES                          │
│  entity_type = 'HARNESS_TEMPLATE'                   │
│  title, summary, importance, workspace_id           │
├─────────────────────────────────────────────────────┤
│                  HARNESS_META                        │
│  input_schema (JSONB), output_schema (JSONB),       │
│  execution_mode (VARCHAR)                           │
├─────────────────────────────────────────────────────┤
│                ENTITY_EDGES                          │
│  edge_type = 'DERIVES_FROM' → parent template       │
│  (enables template inheritance/lineage)             │
│  source_type, metadata (JSONB)                      │
└─────────────────────────────────────────────────────┘
```

## Template Structure

Templates store their configuration in the `entities` columns and `harness_meta`
companion table. The `harness_meta.input_schema` and `harness_meta.output_schema`
define the expected data contracts, while `harness_meta.execution_mode` specifies
how the template runs (e.g., `SEQUENTIAL`, `PARALLEL`, `INTERACTIVE`).

Template content (prompt_templates, tool_bindings, guardrails, etc.) is stored
in the `entities.content` column as structured JSON:

```json
{
  "prompt_templates": {
    "system": "You are a {{role}}. {{instructions}}",
    "task": "Perform: {{task}}"
  },
  "tool_bindings": [
    {"name": "memory_search", "access": "read"},
    {"name": "memory_create", "access": "write"}
  ],
  "variables": {
    "role": {"type": "string", "required": true},
    "depth": {"type": "string", "enum": ["quick", "deep"], "default": "deep"}
  },
  "guardrails": {
    "max_iterations": 15,
    "max_execution_time": 300,
    "pii_filtering": true
  },
  "memory_access": {
    "read": ["MEMORY", "KNOWLEDGE"],
    "write": ["MEMORY"],
    "share": true
  },
  "evaluation": {
    "criteria": ["accuracy", "completeness"],
    "min_score": 0.7
  }
}
```

### harness_meta Fields

| Field | Type | Description |
|-------|------|-------------|
| `input_schema` | `JSONB` | JSON Schema defining expected input variables and their types |
| `output_schema` | `JSONB` | JSON Schema defining the structure of template output |
| `execution_mode` | `VARCHAR` | Execution strategy: `SEQUENTIAL`, `PARALLEL`, or `INTERACTIVE` |

## Built-in Tool Sets

Tool sets are pre-defined bundles that can be referenced by name in
`create_harness_template(tool_sets=[...])`:

### memory_tools

| Tool | Access |
|------|--------|
| `memory_search` | read |
| `memory_create` | write |
| `memory_update` | write |
| `memory_delete` | write |

### knowledge_tools

| Tool | Access |
|------|--------|
| `knowledge_search` | read |
| `knowledge_create` | write |
| `knowledge_update` | write |
| `knowledge_graph_query` | read |

### agent_tools

| Tool | Access |
|------|--------|
| `agent_register` | write |
| `session_create` | write |
| `collaboration_request` | write |

### security_tools

| Tool | Access |
|------|--------|
| `data_mask` | read |
| `data_unmask` | read |

### task_tools

| Tool | Access |
|------|--------|
| `task_plan_create` | write |
| `task_step_execute` | write |
| `task_status_query` | read |

## Guardrail Presets

| Preset | max_iterations | max_execution_time | context_window | content_moderation | pii_filtering | max_retry |
|--------|---------------|--------------------|-----------------|-------------------|--------------|-----------|
| `conservative` | 5 | 60s | sliding | true | true | 1 |
| `balanced` | 15 | 300s | summarize | true | true | 3 |
| `aggressive` | 50 | 900s | truncate | false | false | 5 |

Usage: `create_harness_template(name="...", guardrail_preset="conservative")`

## Python API — 12 Functions

### create_harness_template

```python
entity_id = create_harness_template(
    title="My Agent",
    summary="Custom agent template",
    prompt_templates={"system": "You are {{role}}.", "task": "Do: {{task}}"},
    tool_bindings=[{"name": "custom_tool", "access": "read"}],
    tool_sets=["memory_tools", "knowledge_tools"],
    guardrail_preset="balanced",
    variables={"role": {"type": "string", "required": True}},
    category="custom",
    visibility="SHARED",
    parent_template_id=None,
    input_schema={"type": "object", "properties": {"role": {"type": "string"}}},
    output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
    execution_mode="SEQUENTIAL",
)
```

### get_harness_template

```python
tpl = get_harness_template(entity_id)
# Returns dict with title, summary, content fields, input_schema, output_schema, execution_mode
```

### list_harness_templates

```python
templates = list_harness_templates(category="research", status="PUBLISHED", limit=50)
```

### update_harness_template

```python
update_harness_template(entity_id, title="Updated Title", execution_mode="PARALLEL")
```

### delete_harness_template

```python
delete_harness_template(entity_id)  # cascades to harness_meta and edges
```

### get_template_with_variables

Merges the template with its parent chain (via `DERIVES_FROM` edges) using
deep-merge semantics. Child values override parent values.

```python
resolved = get_template_with_variables(entity_id)
```

### instantiate_harness_template

Resolves the template, substitutes `{{variables}}` in prompt_templates, and
applies runtime overrides:

```python
instance = instantiate_harness_template(
    template_id,
    variables={"role": "analyst", "task": "review data"},
    overrides={"guardrails": {"max_iterations": 20}},
    agent_id="agent-001",
)
```

### Derive from Parent Template

> **Note**: `derive_template` is not a separate function. Use `create_harness_template` with `parent_template_id` parameter to create a child template that inherits from a parent.


Creates a child template that inherits from a parent via a `DERIVES_FROM` edge:

```python
child_id = create_harness_template(
    parent_id,
    title="Specialized Analyst",
    overrides={"prompt_templates": {"system": "You are a {{role}} specialist."}},
    category="research",
)
```

### Validate Template (via get_harness_template)

> **Note**: There is no standalone `validate_template` function. Use `get_harness_template` to retrieve and inspect the template structure.


Checks for: missing `system` prompt, undefined variables in prompts, duplicate
tool bindings, invalid guardrails, and no memory access configured.

```python
result = get_harness_template(entity_id)
# {"valid": True/False, "errors": [...], "warnings": [...]}
```

### Publish / Deprecate (via update_harness_template)

> **Note**: There are no standalone `publish_template` or `deprecate_template` functions. Use `update_harness_template(entity_id, status="PUBLISHED")` or `update_harness_template(entity_id, status="DEPRECATED")` instead.


```python
update_harness_template(entity_id)           # DRAFT → PUBLISHED
update_harness_template(entity_id, reason="Superseded by v2")
```

### Template Lineage (via get_harness_template + edges)

Returns the chain of parent templates via `DERIVES_FROM` edges:

```python
lineage = get_harness_template_lineage(entity_id)
```

## Workflow Examples

### Create and Publish a New Template

```python
from scripts.lib import harness_api

tid = harness_api.create_harness_template(
    title="Document Summarizer",
    summary="Summarizes documents with configurable length",
    prompt_templates={
        "system": "You summarize documents. Target length: {{length}}.",
        "summarize": "Summarize: {{document}}",
    },
    tool_sets=["memory_tools"],
    guardrail_preset="balanced",
    variables={
        "length": {"type": "string", "enum": ["brief", "standard", "detailed"], "default": "standard"},
        "document": {"type": "string", "required": True},
    },
    category="productivity",
)

report = harness_api.get_harness_template(tid)
if report["valid"]:
    harness_api.update_harness_template(tid)
```

### Derive a Specialized Template

```python
child_id = harness_api.create_harness_template(
    parent_id=tid,
    title="Legal Document Summarizer",
    overrides={
        "prompt_templates": {
            "system": "You summarize legal documents. Target length: {{length}}. Flag risks.",
        },
        "guardrails": {"max_iterations": 20},
    },
    category="legal",
)
```

### Instantiate at Runtime

```python
instance = harness_api.instantiate_harness_template(
    template_id=child_id,
    variables={"length": "detailed", "document": "Contract text..."},
    agent_id="legal-agent-01",
)
# instance["prompt_templates"]["system"] has {{length}} → "detailed"
```

## Built-in Templates

5 templates are seeded by `scripts/deploy/4_harness_templates.sql` (deployed in
Phase 4 of the 4-phase deployment process):

### 1. Research Analyst

- **Category**: `research`
- **Tools**: web_search, document_reader, data_extractor, note_taker
- **Guardrails**: max 10 iterations, 30 min timeout, citations required, fact-check enabled
- **Memory**: read MEMORY+KNOWLEDGE, write MEMORY, share enabled
- **Evaluation**: completeness, accuracy, citation_quality, clarity (min 0.7)
- **Variables**: `topic` (required), `depth` (quick/standard/deep), `output_format` (summary/report/brief)

### 2. Code Assistant

- **Category**: `development`
- **Tools**: code_editor, file_system, terminal, linter, test_runner
- **Guardrails**: max 15 iterations, 20 min timeout, tests required, security scan, no direct exec
- **Memory**: read MEMORY+KNOWLEDGE+EXPERIENCE, write MEMORY+EXPERIENCE, share enabled
- **Evaluation**: correctness, readability, test_coverage, security (min 0.8)
- **Variables**: `task` (required), `language` (required), `framework`, `style` (minimal/documented/enterprise)

### 3. Data Analyst

- **Category**: `analytics`
- **Tools**: sql_runner, data_processor, chart_generator, statistics_engine
- **Guardrails**: max 8 iterations, 25 min timeout, validate results, max 10K rows, PII detection
- **Memory**: read MEMORY+KNOWLEDGE, write MEMORY, share disabled
- **Evaluation**: accuracy, insight_depth, visualization_quality, actionability (min 0.75)
- **Variables**: `dataset_description` (required), `analysis_type` (exploratory/confirmatory/predictive), `output_format` (table/chart/narrative)

### 4. Task Planner

- **Category**: `orchestration`
- **Tools**: task_manager, scheduler, dependency_resolver, progress_tracker
- **Guardrails**: max 20 iterations, 60 min timeout, max 50 subtasks, auto-retry
- **Memory**: read MEMORY+KNOWLEDGE+TASK_OUTPUT, write MEMORY+TASK_OUTPUT, share enabled
- **Evaluation**: goal_alignment, completeness, feasibility, efficiency (min 0.7)
- **Variables**: `goal` (required), `complexity` (simple/moderate/complex), `parallelism` (int)

### 5. Security Auditor

- **Category**: `security`
- **Tools**: vulnerability_scanner, compliance_checker, log_analyzer, report_generator
- **Guardrails**: max 12 iterations, 45 min timeout, readonly mode, no exploit, log all actions
- **Memory**: read MEMORY+KNOWLEDGE, write MEMORY, share disabled
- **Evaluation**: coverage, severity_accuracy, remediation_quality, false_positive_rate (min 0.85)
- **Variables**: `target` (required), `scan_type` (quick/standard/comprehensive), `standard` (OWASP/CIS/SOC2/PCI-DSS)
