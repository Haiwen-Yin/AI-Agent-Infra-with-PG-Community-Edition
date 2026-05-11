# pg-embedding-gen Troubleshooting Guide

## Problem Summary

The `pg_embedding_gen` C extension may load successfully on `CREATE EXTENSION` but return corrupted data when called via SQL function `generate_embedding(TEXT)`.

## Observed Behavior (PostgreSQL 18 Environment)

### Environment
- PostgreSQL 18.3 on CentOS/RHEL
- Extension location: `/usr/local/pgsql/lib/extension/pg_embedding_gen.so`
- Python proxy: `/usr/local/pgsql/bin/pg_embedding_proxy.py`
- BGE-M3 API: `http://10.10.10.1:12345/v1/embeddings`

### Working: Direct Python Proxy Call
```bash
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "Hello world"
# Returns: [-0.013345..., 0.004086..., -0.065920...] (1024 correct floats)
```

### Failing: PostgreSQL SQL Function Call
```sql
SELECT generate_embedding('Hello world');
# Returns: {9.548e-15, 4.578e-16, ..., NaN, 0, 0, ...} (corrupted)
```

## Root Cause Analysis

### Extension Loads Successfully
```
CREATE EXTENSION pg_embedding_gen;
-- Output: CREATE EXTENSION
-- Extension appears in pg_extension table
```

### Symbol Exports Present
```
objdump -T /usr/local/pgsql/lib/extension/pg_embedding_gen.so
-- Shows: generate_embedding, pg_finfo_generate_embedding
```

### Function Creation Issues
```
CREATE FUNCTION generate_embedding(TEXT) RETURNS float[] 
AS '$libdir/pg_embedding_gen', 'generate_embedding' 
LANGUAGE C IMMUTABLE;
-- Issue: May not correctly initialize PostgreSQL API
```

### Suspected Root Cause
C extension compiled against older PostgreSQL headers. When PostgreSQL 18 loads the extension:
- Extension registers successfully
- Function signature matches
- Runtime initialization fails silently
- Returns garbage when called

## Workaround 1: Python Proxy (Recommended)

### Implementation
```python
import subprocess
import json

def get_embedding_bge_m3(text: str) -> list[float]:
    """Reliable BGE-M3 embedding via Python proxy."""
    cmd = ["python3", "/usr/local/pgsql/bin/pg_embedding_proxy.py", text]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Embedding generation failed: {result.stderr}")
    
    return json.loads(result.stdout)

# Example usage
embedding = get_embedding_bge_m3("PostgreSQL database performance")
# embedding: [-0.013..., 0.045..., ...] (1024 floats)
```

### Advantages
- ✅ Reliable (tested and working)
- ✅ No C extension compatibility issues
- ✅ Easy to debug (Python stack traces)
- ✅ Can add retry logic and error handling

### Disadvantages
- ⚠️ Out-of-process call (slower than C extension)
- ⚠️ Cannot use in pure SQL queries

## Workaround 2: Database Function Wrapper

### Create SQL Function Using Python Proxy
```sql
CREATE OR REPLACE FUNCTION generate_embedding_python(TEXT)
RETURNS float[]
AS $$
import subprocess
import json
result = subprocess.run(
    ["python3", "/usr/local/pgsql/bin/pg_embedding_proxy.py", $1],
    capture_output=True,
    text=True
)
return result.stdout
$$ LANGUAGE plpython3u IMMUTABLE;
```

### Usage
```sql
SELECT generate_embedding_python('Hello world');
-- Returns correct embedding via Python proxy
```

## Solution: Recompile C Extension

### Prerequisites
```bash
# Install PostgreSQL 18 development headers
apt install postgresql-18-server-dev-18  # Debian/Ubuntu
yum install postgresql18-devel              # CentOS/RHEL
```

### Compilation
```bash
cd /path/to/pg-embedding-gen-source
make clean
make PG_VERSION=18
make install
```

### Verification
```sql
DROP EXTENSION pg_embedding_gen CASCADE;
CREATE EXTENSION pg_embedding_gen;
SELECT generate_embedding('Test');
-- Should return correct values
```

## Reference: pg-embedding-gen File Locations

### Source Archive
```
/tmp/pg-embedding-gen-extract/pg_embedding_gen/
├── sql/
│   ├── pg_embedding_gen.control
│   ├── pg_embedding_gen--1.0.0.sql
│   └── register.sql
└── lib/
    ├── embedding_proxy.py
    └── pg_embedding_gen.so
```

### Installation Locations (PostgreSQL 18)
```
/usr/local/pgsql/lib/extension/pg_embedding_gen.so
/usr/local/pgsql/share/extension/pg_embedding_gen.control
/usr/local/pgsql/share/extension/pg_embedding_gen--1.0.0.sql
/usr/local/pgsql/bin/pg_embedding_proxy.py
```

## Key Takeaways

1. **C extension compatibility** is fragile across PostgreSQL versions
2. **Python proxy is reliable** and production-ready workaround
3. **Recompile only if needed** - adds complexity
4. **Document your workaround** in application code for future maintainers

## Related Issues

- Knowledge Base Schema views may fail with type casting issues
- IVFFlat indexes on empty tables produce warnings (expected, not errors)

---

**Last Updated**: 2026-05-11
**Tested On**: PostgreSQL 18.3, CentOS/RHEL, pg_embedding_gen v1.0.0
