# pg-embedding-gen Installation Procedure

**Version**: 1.0.0  
**Date**: Last updated 2026-05-10  
**Author**: Haiwen Yin (胖头鱼 🐟)

## Overview

The `pg-embedding-gen` extension provides PostgreSQL-native BGE-M3 embedding generation via LM Studio API (http://10.10.10.1:12345/v1/embeddings).

**Key Characteristics:**
- Vector dimensions: 1024 (BGE-M3)
- Model: text-embedding-bge-m3
- Architecture: C extension + Python proxy process
- Auto-registers `generate_embedding(text)` function

## Critical Installation Lessons

### 1. Extension File Locations

Source package: `/tmp/pg-embedding-gen-by-yhw.zip`

Required files and their destinations:
```
Source (in zip)                  | Destination
--------------------------------|--------------------------------------------
pg_embedding_gen.control        | /usr/local/pgsql/share/extension/pg_embedding_gen.control
pg_embedding_gen--1.0.0.sql   | /usr/local/pgsql/share/extension/pg_embedding_gen--1.0.0.sql
pg_embedding_gen.so            | /usr/local/pgsql/lib/extension/pg_embedding_gen.so
pg_embedding_proxy.py          | /usr/local/pgsql/bin/pg_embedding_proxy.py
```

### 2. Control File (.control) Format

**Format:**
```
# pg_embedding_gen extension
comment = 'BGE-M3 Embedding Generation for PostgreSQL 18'
default_version = '1.0.0'
module_pathname = '$libdir/pg_embedding_gen'
relocatable = false
```

**Important:**
- Use `#` for comments (not `--`)
- `module_pathname` must use `$libdir/pg_embedding_gen`
- `relocatable = false` (extension cannot be moved)

### 3. SQL Script (--1.0.0.sql) - Critical Gotcha

**INCORRECT approach (causes errors):**
```sql
-- This fails because extension already auto-registers functions
CREATE OR REPLACE FUNCTION generate_embedding(text)
RETURNS float[]
AS '$libdir/pg_embedding_gen', 'generate_embedding'
LANGUAGE C IMMUTABLE;
```

**CORRECT approach (minimal script):**
```sql
-- pg_embedding_gen Extension v1.0.0
-- Note: This extension automatically registers functions
-- via _PG_init() in pg_embedding_gen.c
-- No manual CREATE OR REPLACE FUNCTION needed
```

**Why minimal?** The C extension's `_PG_init()` function automatically registers the function. Manual CREATE statements cause "could not find function information" errors.

### 4. Root Permission Required

Extension installation requires root permissions:
```bash
# As root user
ssh root@10.10.10.131

# Create control and SQL files
cat > /usr/local/pgsql/share/extension/pg_embedding_gen.control << 'EOF'
...content...
EOF

cat > /usr/local/pgsql/share/extension/pg_embedding_gen--1.0.0.sql << 'EOF'
...content...
EOF
```

### 5. Database Extension Creation

```bash
# Switch to postgres or pgsql user
su - postgres

# Create extension in database
psql -d memory_graph -c "CREATE EXTENSION pg_embedding_gen;"

# Verify
psql -d memory_graph -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_embedding_gen';"
```

**Expected output:**
```
 extname      | extversion
-------------- 
 pg_embedding_gen | 1.0.0
```

### 6. Expected Warnings (Normal)

When installing extension, you may see:
```
WARNING:  Failed to load PostgreSQL binary: /usr/local/pgsql/bin/postgres: cannot dynamically load executable
WARNING:  Failed to load PostgreSQL API functions: (null)
INFO:  pg_embedding_gen extension loaded for PostgreSQL 18
```

**Status: These warnings are NORMAL and expected.** The extension loads as a shared library, not as a PostgreSQL executable process. Ignore these warnings.

### 7. Python Proxy Configuration

The Python proxy at `/usr/local/pgsql/bin/pg_embedding_proxy.py` handles BGE-M3 API calls:

**Default configuration:**
```yaml
model:
  name: text-embedding-bge-m3
  api_url: http://10.10.10.1:12345/v1/embeddings
  dimension: 1024
```

**To configure custom endpoint:**
- Create `/usr/local/pgsql/bin/pg_embedding_config.yaml`
- Override api_url and model name
- Proxy reads this config on startup

## Testing the Installation

### Test Python Proxy Directly
```bash
python3 /usr/local/pgsql/bin/pg_embedding_proxy.py "Hello world"
```

**Expected output:** JSON array of floats (1024 dimensions)
```json
[-0.03918059170246124, 0.03259294480085373, -0.028693009167909622, ...]
```

### Test via PostgreSQL Function
```sql
SELECT generate_embedding('Hello world') as embedding;
```

**Expected output:** Array of floats
```
{ -0.03918059170246124, 0.03259294480085373, ... }
```

## Troubleshooting

| Error | Cause | Solution |
|--------|--------|----------|
| `could not find function information for function "generate_embedding"` | Manual CREATE in SQL script | Remove CREATE statements, use minimal SQL script |
| `function generate_embedding(unknown) does not exist` | Extension not created in database | Run `CREATE EXTENSION pg_embedding_gen;` |
| `Permission denied` writing to /usr/local/pgsql/... | Not running as root | Install as root user |
| `Failed to load PostgreSQL binary` | Extension loading as library | **Ignore** - this is expected/normal |
| Module import errors in Python proxy | Python dependencies missing | Install `requests` library: `pip install requests` |

## Complete Installation Script

```bash
#!/bin/bash
# pg-embedding-gen installation for memory-pg18-by-yhw
# Requires: root access, PostgreSQL 18, Python 3.8+

set -e

echo "=== Installing pg-embedding-gen extension ==="

# 1. Extract files (if from zip)
# unzip /tmp/pg-embedding-gen-by-yhw.zip -d /tmp/pg-embedding-gen

# 2. Create control file
echo "Creating control file..."
cat > /usr/local/pgsql/share/extension/pg_embedding_gen.control << 'EOF'
# pg_embedding_gen extension
comment = 'BGE-M3 Embedding Generation for PostgreSQL 18'
default_version = '1.0.0'
module_pathname = '$libdir/pg_embedding_gen'
relocatable = false
EOF

# 3. Create SQL script (minimal - no manual function creation)
echo "Creating SQL script..."
cat > /usr/local/pgsql/share/extension/pg_embedding_gen--1.0.0.sql << 'EOF'
-- pg_embedding_gen Extension v1.0.0
-- Author: Haiwen Yin (胖头鱼 🐟)
-- Note: This extension automatically registers functions
-- via _PG_init() in pg_embedding_gen.c
-- No manual CREATE OR REPLACE FUNCTION needed
EOF

# 4. Set permissions
echo "Setting permissions..."
chmod 644 /usr/local/pgsql/share/extension/pg_embedding_gen.control
chmod 644 /usr/local/pgsql/share/extension/pg_embedding_gen--1.0.0.sql

# 5. Verify files
echo "Verifying files..."
ls -la /usr/local/pgsql/share/extension/pg_embedding_gen*
ls -la /usr/local/pgsql/lib/extension/pg_embedding_gen.so
ls -la /usr/local/pgsql/bin/pg_embedding_proxy.py

# 6. Create extension in database
echo "Creating extension in database..."
su - postgres -c "psql -d memory_graph -c \"CREATE EXTENSION IF NOT EXISTS pg_embedding_gen;\""

# 7. Verify installation
echo "Verifying installation..."
su - postgres -c "psql -d memory_graph -c \"SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_embedding_gen';\""

echo "=== Installation complete ==="
```

## References

- LM Studio BGE-M3 API: http://10.10.10.1:12345/v1/embeddings
- PostgreSQL 18 Server: 10.10.10.131
- Database: memory_graph
- Skill: memory-pg18-by-yhw v1.0.0
