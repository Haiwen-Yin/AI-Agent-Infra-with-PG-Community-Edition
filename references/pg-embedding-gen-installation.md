# pg-embedding-gen-by-yhw Installation Guide

**Extension**: [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) v0.2.0
**Author**: Haiwen Yin (yhw)  
**Type**: Custom PostgreSQL 18 extension (COPY FROM PROGRAM + Python proxy, NOT a C extension)

## Overview

pg-embedding-gen-by-yhw enables in-database embedding generation via SQL functions. It uses PostgreSQL 18's `COPY FROM PROGRAM` mechanism to call a Python proxy process that communicates with any OpenAI-compatible `/v1/embeddings` API endpoint.

**Key Facts:**
- **NOT a C extension** — no `.so` file, no C compilation required
- Uses `COPY FROM PROGRAM` to invoke shell wrapper + Python proxy
- Supports any OpenAI-compatible embedding API (BGE-M3, OpenAI, Ollama, vLLM, Xinference)
- Vector dimensions auto-detected on first use
- Multi-model profiles managed via SQL

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| PostgreSQL | 18+ | Required for `COPY FROM PROGRAM` |
| Python | 3.6+ | Required by embedding proxy |
| Python `requests` | Any | HTTP client for API calls |

## Installation Steps

### 1. Install Extension Files

From the pg-embedding-gen-by-yhw project directory:

```bash
sudo bash scripts/install.sh
```

This copies:
- `embedding_wrapper.sh` → `/usr/local/pgsql/lib/embedding_wrapper.sh`
- `embedding_proxy.py` → `/usr/local/pgsql/lib/embedding_proxy.py`

### 2. Install SQL Functions

```bash
psql -d memory_graph -f sql/install.sql
```

This creates:
- Tables: `pg_embedding_gen_config`, `embedding_model_profiles`, `embedding_dimension_cache`, `embedding_logs`
- Functions: `embedding_generate()`, `embedding_generate_model()`, `embedding_register_model()`, `embedding_health_check()`, and 15+ more
- Seeds a default `bge-m3` profile pointing to `http://10.10.10.1:12345/v1/embeddings`

### 3. Install Python Dependencies

```bash
pip3 install requests
```

### 4. Verify Installation

```bash
# Test proxy directly
/usr/local/pgsql/lib/embedding_wrapper.sh --text 'Hello world'

# Test via SQL
psql -d memory_graph -c "SELECT embedding_generate('Hello world');"

# Health check
psql -d memory_graph -c "SELECT * FROM embedding_health_check();"

# List registered models
psql -d memory_graph -c "SELECT * FROM embedding_list_models();"
```

## Registering Additional Models

```sql
-- Register an OpenAI model
SELECT embedding_register_model(
    'openai-small',
    'https://api.openai.com/v1/embeddings',
    'text-embedding-3-small',
    false,
    'OpenAI small embedding model'
);

-- Register an Ollama model
SELECT embedding_register_model(
    'nomic',
    'http://localhost:11434/v1/embeddings',
    'nomic-embed-text',
    false,
    'Nomic embed text via Ollama'
);

-- Test and auto-detect dimensions
SELECT * FROM embedding_test_model('openai-small');

-- Set as default
SELECT embedding_set_default_model('openai-small');
```

## File Configuration (Fallback)

If no model profiles are registered, the proxy reads `/etc/pg_embedding-gen/config.json`:

```json
{
    "api_url": "http://10.10.10.1:12345/v1/embeddings",
    "model": "text-embedding-bge-m3",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "WARNING",
    "log_file": ""
}
```

## Permissions

The PostgreSQL server process (typically `pgsql` or `postgres` user) must have:
- Execute permission on `/usr/local/pgsql/lib/embedding_wrapper.sh`
- Execute permission on `/usr/local/pgsql/lib/embedding_proxy.py`
- Network access to the embedding API endpoint
- `COPY FROM PROGRAM` is available to superusers by default; non-superusers need explicit grant

```bash
sudo chmod +x /usr/local/pgsql/lib/embedding_wrapper.sh
sudo chmod +x /usr/local/pgsql/lib/embedding_proxy.py
```

## Integration with memory-pg18-by-yhw

The `memory` schema in `scripts/deploy/1_schema.sql` wraps pg-embedding-gen-by-yhw:

```sql
-- memory.generate_embedding() calls embedding_generate()
SELECT memory.generate_embedding('text');  -- returns vector(1024)

-- memory.add_concept_with_embedding() creates entity + auto-embedding
SELECT memory.add_concept_with_embedding('Name', 'Desc', 'category', '{}'::jsonb);

-- memory.search_similar() generates query embedding + vector search
SELECT * FROM memory.search_similar('query', 10);
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ERROR: function embedding_generate does not exist` | SQL functions not installed | Run `psql -d memory_graph -f sql/install.sql` |
| `ERROR: COPY FROM PROGRAM permission denied` | PG user lacks execute permission | `chmod +x` the wrapper and proxy scripts |
| Empty/null result from `embedding_generate()` | API endpoint unreachable | Test: `curl -X POST 'http://10.10.10.1:12345/v1/embeddings' -H 'Content-Type: application/json' -d '{"model":"text-embedding-bge-m3","input":"test"}'` |
| `ModuleNotFoundError: No module named 'requests'` | Python dependency missing | `pip3 install requests` |
| `WARNING: embedding_generate: no default model profile` | No models registered | Run `embedding_register_model()` or re-run `install.sql` |

## Reference

- Source: `/root/pg-embedding-gen-by-yhw-v0.2.0/pg_embedding-gen/`
- Install script: `scripts/install.sh`
- SQL install: `sql/install.sql`
- Proxy: `lib/embedding_proxy.py`
- Wrapper: `lib/embedding_wrapper.sh`
