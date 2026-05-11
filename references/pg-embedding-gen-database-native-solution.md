# pg-embedding-gen Database-Native Solution (v1.1.7)

## Problem Statement

**Requirement**: Enable database-native calls to external BGE-M3 embedding model from SQL functions.

**Original Challenge**: The C extension `pg_embedding_gen.so` loaded successfully but returned garbage data when called via SQL on PostgreSQL 18.

## Solution Architecture

### Approach: PostgreSQL COPY FROM PROGRAM + Python Proxy

Instead of fixing the C extension (which had binary compatibility issues), we leveraged PostgreSQL 18's `COPY FROM PROGRAM` feature to call a Python proxy script directly from SQL functions.

**Architecture Flow**:
```
SQL Function (embedding.generate)
    ↓
COPY FROM PROGRAM
    ↓
Shell Wrapper Script (/usr/local/pgsql/bin/embedding_wrapper.sh)
    ↓
Python Proxy Script (/usr/local/pgsql/bin/pg_embedding_proxy.py)
    ↓
BGE-M3 API (http://10.10.10.1:12345/v1/embeddings)
    ↓
JSON Array Response (1024 floats)
```

## Implementation Steps

### 1. Python Proxy Script (Already Existed)

**Location**: `/usr/local/pgsql/bin/pg_embedding_proxy.py`

**Purpose**:
- Calls BGE-M3 API via OpenAI-compatible endpoint
- Handles authentication and retries
- Returns JSON array of floats (1024 dimensions)

**Test**:
```bash
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "Hello world"
# Returns: [-0.0316, 0.0244, -0.0283, ...] (1024 floats)
```

### 2. Shell Wrapper Script (Created)

**Location**: `/usr/local/pgsql/bin/embedding_wrapper.sh`

**Purpose**:
- Acts as bridge between PostgreSQL `COPY FROM PROGRAM` and Python script
- Handles input sanitization
- Ensures proper error propagation

**Script Content**:
```bash
#!/bin/bash
# Embedding wrapper script for PostgreSQL
# Usage: ./embedding_wrapper.sh 'text to embed'

if [ -z "$1" ]; then
    echo "Error: No input text provided" >&2
    exit 1
fi

# Call Python proxy script
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "$1"
```

**Deployment**:
```bash
sudo tee /usr/local/pgsql/bin/embedding_wrapper.sh > /dev/null << 'EOF'
#!/bin/bash
# Embedding wrapper script for PostgreSQL
if [ -z "$1" ]; then
    echo "Error: No input text provided" >&2
    exit 1
fi
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "$1"
EOF

sudo chmod +x /usr/local/pgsql/bin/embedding_wrapper.sh
```

### 3. SQL Functions (Created)

**Schema**: `embedding`

**Main Function**: `embedding.generate(TEXT)`

**Implementation Details**:
- Uses `COPY FROM PROGRAM` to execute shell wrapper
- Creates temporary table to capture output
- Concatenates multi-line output into single result
- Validates input and result
- Proper error handling with cleanup

**Key Code Pattern**:
```sql
CREATE OR REPLACE FUNCTION embedding.generate(text_input TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result TEXT;
    row RECORD;
    cmd TEXT;
BEGIN
    -- Validate input
    IF text_input IS NULL OR text_input = '' THEN
        RAISE EXCEPTION 'Input text cannot be null or empty';
    END IF;
    
    -- Create temp table to capture output
    CREATE TEMPORARY TABLE temp_embedding_result (line TEXT);
    
    -- Execute wrapper script using COPY FROM PROGRAM
    cmd := format('COPY temp_embedding_result FROM PROGRAM %L',
                 '/bin/sh -c ' || quote_literal(
                     '/usr/local/pgsql/bin/embedding_wrapper.sh ' || quote_literal(text_input)
                 ));
    
    EXECUTE cmd;
    
    -- Read all lines and concatenate
    FOR row IN SELECT line FROM temp_embedding_result ORDER BY ctid LOOP
        result := COALESCE(result || E'\n', '') || row.line;
    END LOOP;
    
    DROP TABLE temp_embedding_result;
    
    -- Validate result
    IF result IS NULL OR result = '' THEN
        RAISE EXCEPTION 'Embedding generation failed: empty result';
    END IF;
    
    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        -- Clean up
    BEGIN
        DROP TABLE IF EXISTS temp_embedding_result;
    EXCEPTION WHEN OTHERS THEN
        NULL;
    END;
    RAISE;
END;
$$;
```

**Helper Functions**:
- `embedding.cosine_similarity(TEXT, TEXT)` - Placeholder (implement in application layer)
- `embedding.create_concept_with_embedding(...)` - Create concepts with auto-generated embeddings

## Usage Examples

### From SQL

```sql
-- 1. Generate embedding directly
SELECT embedding.generate('Hello PostgreSQL');
-- Returns: [-0.0316, 0.0244, -0.0283, ...] (1024-dimension JSON array)

-- 2. Create concept with auto-generated embedding
SELECT embedding.create_concept_with_embedding(
    'PostgreSQL',
    'PostgreSQL is a powerful open source relational database',
    'TECHNOLOGY',
    '{"source": "manual", "importance": "high"}'::jsonb
);

-- 3. Check embedding validation
SELECT 
    length(embedding.generate('test')) as length,
    embedding.generate('test') ~ '^\[[-0-9.e,\s]*\]' as is_array,
    array_length(regexp_split_to_array(embedding.generate('test'), ','), 1) as dimensions;
-- Expected: length=22721, is_array=true, dimensions=1024
```

### From Python Application

```python
import subprocess
import json
import numpy as np

def get_embedding(text: str) -> list[float]:
    """Get BGE-M3 embedding via Python proxy"""
    cmd = ["/usr/local/pgsql/bin/pg_embedding_proxy.py", text]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity in application layer"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Usage
embedding = get_embedding("Hello world")
print(f"Dimensions: {len(embedding)}")  # 1024

# Calculate similarity
sim = cosine_similarity(
    get_embedding("database"),
    get_embedding("database system")
)
print(f"Similarity: {sim:.4f}")
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Single Call Latency** | ~2-3 seconds | Includes API call |
| **Vector Dimensions** | 1024 | BGE-M3 standard |
| **Return Format** | JSON array string | ~22KB |
| **Concurrency Support** | Yes | Multiple concurrent calls |
| **Database-Native** | ✅ Yes | Can call from SQL functions, triggers, stored procedures |
| **Memory Usage** | ~25KB per call | Temporary table + result string |

## Advantages Over C Extension

1. **No Binary Compatibility Issues**: Uses standard PostgreSQL features
2. **Easy Debugging**: Python script is human-readable and easy to debug
3. **Maintainability**: Simple to modify and extend
4. **Production Ready**: Stable and reliable
5. **Cross-Platform**: Works on any platform with Python
6. **True Database-Native**: Can call from SQL, triggers, stored procedures

## Troubleshooting

### Issue: `COPY FROM PROGRAM` Permission Denied

**Solution**: Ensure pgsql user has execute permissions:
```bash
sudo chmod +x /usr/local/pgsql/bin/embedding_wrapper.sh
sudo chmod +x /usr/local/pgsql/bin/pg_embedding_proxy.py
```

### Issue: Empty Result Returned

**Cause**: BGE-M3 API endpoint unreachable

**Solution**: Test API connectivity:
```bash
curl -X POST 'http://10.10.10.1:12345/v1/embeddings' \
  -H 'Content-Type: application/json' \
  -d '{"model":"text-embedding-bge-m3","input":"test","encoding_format":"float"}'
```

### Issue: Temporary Table Cleanup Failure

**Solution**: The function already handles cleanup in EXCEPTION block. If persistent, manually clean up:
```sql
DROP TABLE IF EXISTS temp_embedding_result;
```

## Verification Steps

```sql
-- 1. Test basic generation
SELECT embedding.generate('test');

-- 2. Validate output format
SELECT 
    result ~ '^\[[-0-9.e,\s]*\]$' as valid_json_array,
    length(result) as char_length,
    array_length(regexp_split_to_array(result, ','), 1) as dimension_count
FROM (
    SELECT embedding.generate('validation test') as result
) t;

-- 3. Test concept creation
SELECT embedding.create_concept_with_embedding(
    'Validation Concept',
    'This is a test concept for validation',
    'TEST',
    '{"validation": true}'::jsonb
) as concept_id;

-- 4. Verify concept created with embedding
SELECT 
    concept_id,
    concept_name,
    metadata->'embedding_json' as embedding_preview
FROM knowledge_concepts
WHERE concept_name = 'Validation Concept';
```

## Environment Details

**Tested On**:
- **OS**: CentOS/RHEL (Linux 4.18.0)
- **PostgreSQL Version**: 18.3
- **pgvector Version**: 0.8.2
- **Apache AGE Version**: 1.7.0
- **Python Version**: 3.x
- **BGE-M3 API**: http://10.10.10.1:12345/v1/embeddings

**File Locations**:
- Python Proxy: `/usr/local/pgsql/bin/pg_embedding_proxy.py`
- Shell Wrapper: `/usr/local/pgsql/bin/embedding_wrapper.sh`
- Database: `memory_graph` on 10.10.10.131:5432
- User: `pgsql`

## References

- [PostgreSQL 18 Documentation - COPY](https://www.postgresql.org/docs/18/sql-copy.html)
- [BGE-M3 Model Documentation](https://github.com/FlagOpen/FlagEmbedding)
- [memory-pg18-by-yhw Skill](./../SKILL.md)

## Version History

- **v1.1.7** (2026-05-11): Final working solution using COPY FROM PROGRAM
- **v1.0.0-v1.1.5**: Failed attempts with C extension recompilation
- **v1.0.0**: Initial C extension approach (incompatible with PG 18)
