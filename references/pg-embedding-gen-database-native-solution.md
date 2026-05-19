# pg-embedding-gen-by-yhw: In-Database Embedding Generation (v0.2.0)

## Overview

**pg-embedding-gen-by-yhw** ([GitHub](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw)) is a custom PostgreSQL 18 extension developed by **Haiwen Yin (yhw)**. It generates text vector embeddings via SQL functions by calling any OpenAI-compatible `/v1/embeddings` API endpoint.

**It is NOT a C extension.** It uses PostgreSQL 18's `COPY FROM PROGRAM` mechanism to invoke a Python proxy process, which communicates with the embedding API. No C compilation is required.

## Architecture

```
SQL Function Call (e.g., embedding_generate('text'))
       |
       v
embedding_generate_model() — resolves profile, builds command string
       |
       v
COPY _pg_emb_temp FROM PROGRAM '/usr/local/pgsql/lib/embedding_wrapper.sh --text <input> --model <id> --api-url <url>'
       |
       v
embedding_wrapper.sh (shell script)
       |
       v
embedding_proxy.py (Python process)
       |
       v
HTTP POST to OpenAI-compatible /v1/embeddings API
       |
       v
Returns: comma-separated float8[] (e.g., 1024 dimensions)
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `embedding_wrapper.sh` | `/usr/local/pgsql/lib/embedding_wrapper.sh` | Shell script called by `COPY FROM PROGRAM` |
| `embedding_proxy.py` | `/usr/local/pgsql/lib/embedding_proxy.py` | Python proxy that calls the embedding API |
| `install.sql` | SQL functions + tables | Creates all functions, config tables, model profiles |
| `install.sh` | Shell script | Copies proxy files to `/usr/local/pgsql/lib/` |

## Features

| Feature | Description |
|---------|-------------|
| **Multi-model profiles** | Register and switch between embedding models via SQL |
| **Auto-detect dimensions** | Vector dimensions detected automatically on first use |
| **Three call modes** | Default profile, named profile, or inline (model_id + api_url) |
| **Any OpenAI-compatible API** | BGE-M3, OpenAI, Ollama, vLLM, Xinference, etc. |
| **Shell-safe** | Base64-encoded input prevents injection |
| **Auto-retry** | Exponential backoff on transient failures (via proxy) |
| **Health check** | `embedding_health_check()` for API connectivity testing |
| **Similarity functions** | `embedding_cosine_similarity()`, `embedding_euclidean_distance()` |
| **Batch generation** | `embedding_generate_batch()` for bulk processing |
| **Logging & statistics** | `embedding_logs` table, `embedding_stats()`, `embedding_errors()` |
| **Vector validation** | `embedding_validate_vector()` checks dimension, NaN, Inf, norm |

## Database Tables Created

| Table | Purpose |
|-------|---------|
| `pg_embedding_gen_config` | Global configuration (default_profile, timeout, max_retries, log_level) |
| `embedding_model_profiles` | Registered models (name, api_url, model_id, dimensions, is_default) |
| `embedding_dimension_cache` | Auto-detected dimensions per unique model+url combination |
| `embedding_logs` | Request log with status, timing, and error messages |

## SQL Function Reference

### Core Generation

| Function | Returns | Description |
|----------|---------|-------------|
| `embedding_generate(text)` | `float8[]` | Generate using default model profile |
| `embedding_generate(text, profile)` | `float8[]` | Generate using named model profile |
| `embedding_generate_model(text, model, api_url)` | `float8[]` | Generate with inline model_id + api_url |
| `embedding_generate_batch(text[], profile)` | `SETOF float8[]` | Generate for multiple texts |

### Model Management

| Function | Returns | Description |
|----------|---------|-------------|
| `embedding_register_model(name, api_url, model_id, is_default, desc)` | `TEXT` | Register a new model profile |
| `embedding_list_models()` | `TABLE` | List all registered profiles |
| `embedding_set_default_model(name)` | `TEXT` | Set default profile |
| `embedding_drop_model(name)` | `boolean` | Remove a profile |
| `embedding_test_model(name)` | `TABLE` | Test API call, auto-detect dimensions |
| `embedding_detect_dimensions(name)` | `TABLE` | Auto-detect dimensions for profiles |

### Similarity & Validation

| Function | Returns | Description |
|----------|---------|-------------|
| `embedding_cosine_similarity(vec1, vec2)` | `float8` | Cosine similarity (IMMUTABLE) |
| `embedding_euclidean_distance(vec1, vec2)` | `float8` | Euclidean distance (IMMUTABLE) |
| `embedding_validate_vector(vec, dim)` | `TABLE` | Validate: dimension, NaN, Inf, norm |
| `embedding_health_check()` | `TABLE` | Test API connectivity |
| `embedding_health_check(profile)` | `TABLE` | Test specific profile connectivity |

### Configuration & Logging

| Function | Returns | Description |
|----------|---------|-------------|
| `embedding_set_config(key, value)` | `TEXT` | Set configuration parameter |
| `embedding_get_config(key)` | `TABLE` | Get configuration |
| `embedding_stats()` | `TABLE` | Request statistics |
| `embedding_errors(limit)` | `TABLE` | Recent error messages |
| `embedding_cleanup_logs(days)` | `bigint` | Delete old logs |

## Usage in This Memory System

The `memory` schema in `1_schema.sql` wraps pg-embedding-gen-by-yhw:

```sql
-- Generate embedding (calls embedding_generate() under the hood)
SELECT memory.generate_embedding('hello world');  -- returns vector(1024)

-- Create knowledge concept with auto-embedding
SELECT memory.add_concept_with_embedding('Name', 'Description', 'category', '{}'::jsonb);

-- Semantic search
SELECT * FROM memory.search_similar('query text', 10);
```

## Installation

```bash
# From the pg-embedding-gen-by-yhw project directory
sudo bash scripts/install.sh
psql -d memory_graph -f sql/install.sql

# Verify
psql -d memory_graph -c "SELECT * FROM embedding_health_check();"
```

## Environment Details

| Component | Value |
|-----------|-------|
| PostgreSQL | 18.3 |
| Default model | text-embedding-bge-m3 (BGE-M3, 1024 dims) |
| Default API | http://10.10.10.1:12345/v1/embeddings |
| Python | 3.6+ |
| Required Python lib | `requests` |

## Version History

- **v0.2.0** (current): Multi-model support, auto-dimension detection, health check, batch, validation
- **v1.1.7** (legacy): Single model, COPY FROM PROGRAM + shell wrapper + Python proxy
- **v1.0.0** (legacy): Initial C extension approach (incompatible with PG 18)
