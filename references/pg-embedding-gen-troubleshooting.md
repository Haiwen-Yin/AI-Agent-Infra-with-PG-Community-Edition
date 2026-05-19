# pg-embedding-gen-by-yhw Troubleshooting Guide

**Extension**: [pg-embedding-gen-by-yhw](https://github.com/Haiwen-Yin/pg-embedding-gen-by-yhw) v0.2.0
**Author**: Haiwen Yin (yhw)  
**Architecture**: COPY FROM PROGRAM + Python proxy (NOT a C extension)

## Architecture Overview

```
SQL → embedding_generate_model() → COPY FROM PROGRAM → embedding_wrapper.sh → embedding_proxy.py → HTTP API
```

If any step fails, the function returns NULL and raises a WARNING.

## Common Issues

### 1. Function Does Not Exist

**Symptom**: `ERROR: function embedding_generate(unknown) does not exist`

**Cause**: SQL functions not installed in the database

**Solution**:
```bash
psql -d memory_graph -f /path/to/pg-embedding-gen-by-yhw/sql/install.sql
```

Verify:
```sql
SELECT proname FROM pg_proc WHERE proname LIKE 'embedding_%' ORDER BY proname;
```

### 2. COPY FROM PROGRAM Permission Denied

**Symptom**: `ERROR: cannot execute COPY FROM PROGRAM` or `permission denied`

**Cause**: PostgreSQL user lacks permission to execute external programs

**Solution**:
```bash
# Ensure scripts are executable
sudo chmod +x /usr/local/pgsql/lib/embedding_wrapper.sh
sudo chmod +x /usr/local/pgsql/lib/embedding_proxy.py

# Non-superusers need explicit grant (PG 18)
# As superuser:
GRANT pg_execute_server_program TO pgsql;
```

### 3. NULL Result / Empty Embedding

**Symptom**: `embedding_generate('text')` returns NULL

**Diagnosis**:
```sql
-- Check for warnings in PostgreSQL log
SELECT * FROM embedding_health_check();

-- Check registered models
SELECT * FROM embedding_list_models();
```

**Common causes**:
- No default model profile configured
- API endpoint unreachable
- Python proxy script not found

**Solution**:
```bash
# Test proxy directly
/usr/local/pgsql/lib/embedding_wrapper.sh --text 'Hello world'

# If proxy fails, check Python
python3 /usr/local/pgsql/lib/embedding_proxy.py --text 'Hello world'

# Test API endpoint
curl -X POST 'http://10.10.10.1:12345/v1/embeddings' \
  -H 'Content-Type: application/json' \
  -d '{"model":"text-embedding-bge-m3","input":"test","encoding_format":"float"}'
```

### 4. Python Module Not Found

**Symptom**: Proxy script fails with `ModuleNotFoundError: No module named 'requests'`

**Cause**: Python `requests` library not installed

**Solution**:
```bash
pip3 install requests

# Verify
python3 -c "import requests; print(requests.__version__)"
```

### 5. No Default Model Profile

**Symptom**: `WARNING: embedding_generate: no default model profile configured`

**Cause**: `embedding_model_profiles` table is empty or no model marked as default

**Solution**:
```sql
-- Register a model
SELECT embedding_register_model(
    'bge-m3',
    'http://10.10.10.1:12345/v1/embeddings',
    'text-embedding-bge-m3',
    true,
    'BGE-M3 default model'
);

-- Or re-run the install SQL to seed defaults
```

### 6. Dimension Mismatch

**Symptom**: `WARNING: embedding_generate: unexpected vector dimension`

**Cause**: API returned a vector with dimensions outside the expected range (16–8192)

**Solution**:
```sql
-- Check what dimensions the model returns
SELECT * FROM embedding_detect_dimensions();

-- View cached dimensions
SELECT * FROM embedding_dimension_cache;
```

### 7. API Timeout

**Symptom**: Embedding generation takes too long or times out

**Cause**: Network latency to API endpoint, or API server overloaded

**Solution**:
```sql
-- Increase timeout (default: 30 seconds)
SELECT embedding_set_config('timeout', '60');

-- Check response time
SELECT * FROM embedding_health_check();
```

### 8. Log Analysis

```sql
-- View recent errors
SELECT * FROM embedding_errors(20);

-- View statistics
SELECT * FROM embedding_stats();

-- Check recent logs
SELECT * FROM embedding_logs ORDER BY created_at DESC LIMIT 20;

-- Clean up old logs
SELECT embedding_cleanup_logs(30);
```

## File Locations

| File | Path |
|------|------|
| Shell wrapper | `/usr/local/pgsql/lib/embedding_wrapper.sh` |
| Python proxy | `/usr/local/pgsql/lib/embedding_proxy.py` |
| Config (fallback) | `/etc/pg_embedding-gen/config.json` |
| PostgreSQL log | `~/pgsql_data/logfile` |

## Direct Proxy Testing

```bash
# Test shell wrapper
/usr/local/pgsql/lib/embedding_wrapper.sh --text 'Hello world'

# Test Python proxy directly
python3 /usr/local/pgsql/lib/embedding_proxy.py --text 'Hello world'

# Test with specific model
/usr/local/pgsql/lib/embedding_wrapper.sh --text 'Hello world' \
  --model 'text-embedding-bge-m3' \
  --api-url 'http://10.10.10.1:12345/v1/embeddings'

# Test API endpoint
curl -v -X POST 'http://10.10.10.1:12345/v1/embeddings' \
  -H 'Content-Type: application/json' \
  -d '{"model":"text-embedding-bge-m3","input":"test","encoding_format":"float"}'
```

## Version History

- **v0.2.0**: Multi-model, auto-dimension, health check, batch, validation, logging
- **v1.1.7**: Single model, COPY FROM PROGRAM approach (legacy)
- **v1.0.0**: C extension approach (abandoned — binary incompatibility with PG 18)

---

**Last Updated**: 2026-05-18  
**Tested On**: PostgreSQL 18.3, CentOS/RHEL, Python 3.6+
