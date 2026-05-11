# PostgreSQL 18 Deployment & Knowledge Base Setup

**Author**: Haiwen Yin (胖头鱼 🐟)  
**Updated**: 2026-05-10  
**Purpose**: PostgreSQL 18 deployment notes and troubleshooting for memory-pg18-by-yhw v0.4.0

---

## 🚀 Quick Deployment Checklist

### Prerequisites
- **Operating System**: RHEL 8 / CentOS 8
- **PostgreSQL Version**: 18.3
- **Required Extensions**: pgvector, age
- **Python**: 3.8+ with `psycopg2` and `requests`

### PostgreSQL 18 Installation

```bash
# 1. Install PostgreSQL 18
sudo yum install postgresql18-server postgresql18-contrib -y

# 2. Initialize database cluster (if needed)
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb

# 3. Start service
sudo systemctl start postgresql-18
sudo systemctl enable postgresql-18
```

### Custom PostgreSQL Setup (pgsql user)

```bash
# 1. Initialize data directory as pgsql user
/usr/local/pgsql/bin/initdb -D ~/pgsql_data

# 2. Start PostgreSQL server
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data -l ~/pgsql_data/logfile start

# 3. Verify (运行中状态检查)
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data status
# Expected output: "server is running (PID: XXXX)"
```

### Database & Extensions Setup

```bash
# 1. Create memory database
/usr/local/pgsql/bin/psql -d postgres -c 'CREATE DATABASE memory_graph;'

# 2. Enable required extensions
/usr/local/pgsql/bin/psql -d memory_graph -c 'CREATE EXTENSION IF NOT EXISTS vector;'
/usr/local/pgsql/bin/psql -d memory_graph -c 'CREATE EXTENSION IF NOT EXISTS age;'

# 3. Verify extensions
/usr/local/pgsql/bin/psql -d memory_graph -c '\dx'
# Expected: list, vector, age
```

---

## 🐛 Common Issues & Solutions

### Issue 1: SSH Permission Denied

**Symptom**: `Permission denied, please try again` when connecting to pgsql user

**Cause**: Public key not in target server's `~/.ssh/authorized_keys`

**Solution**:
```bash
# On target server (10.10.10.131) as root:
mkdir -p /home/pgsql/.ssh
chmod 700 /home/pgsql/.ssh

# Add public key (from source server)
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDR7bqDlFTKonC+m3OYr0vDUSwPPA3AxTb2ne/3Vu+3KKIl+oNSPaxp0WDl9H29z0xB7E43QW8msNUHrU1w62glbjrugdhUz3M0BKBxBYQAnYGalzIVeQpC8dJW+Xqxf0bV3PstuajAa06S5Qhj28LxcA+g4PVy2cHD5Lv6pPjA7aBfkwBGBGqwhOp7K7JE60/drTA8FKvF9sBCF4xIHqLLQbnGCjFUMp9SE6oV3X9GvYW9NY1p8kGvjfGQE76Ie4acjkpwM00WK841/ITpHpEVqC9GRGIVpZKSaCiaIrhGC22EeG9is8cWWFsVhy40UH0MBA+4fVKiFK5WZcHtzB7Gtke7u6oh5s4ygsyjIbuqGUQ6ug86gj9F8dfKaSmoQauY7mWSEaRnBET/ijRve/j7Tnwb2pdrzVKplKvY2+bmKUjAd7Rx2eBnuw507yeyoxckOUw9TKfekk3li1icb+HBL+fMjGCqtSLXPyPTsrbRCGmuxgibmjeFrWPCABjpRp0= root@hermes" >> /home/pgsql/.ssh/authorized_keys

chown pgsql:pgsql /home/pgsql/.ssh/authorized_keys
chmod 600 /home/pgsql/.ssh/authorized_keys
```

### Issue 2: PostgreSQL "socket connection failed"

**Symptom**: `psql: error: connection to server on socket "/tmp/.s.PGSQL.5432" failed`

**Cause**: PostgreSQL server not running or data directory not initialized

**Solution**:
```bash
# Check if server is running
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data status

# If not running, start it
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data -l ~/pgsql_data/logfile start
```

### Issue 3: Permission Denied Creating Data Directory

**Symptom**: `initdb: error: could not create directory "/usr/local/pgsql/data": Permission denied`

**Cause**: Trying to create directory in system-owned location

**Solution**: Use user's home directory
```bash
# Use ~/pgsql_data instead of /usr/local/pgsql/data
mkdir -p ~/pgsql_data
/usr/local/pgsql/bin/initdb -D ~/pgsql_data
```

### Issue 4: pg-embedding-gen Extension Not Found

**Symptom**: `ERROR: extension "pg_embedding_gen" does not exist`

**Cause**: Missing .control file or SQL script

**Current Status** (v0.4.0):
- Plugin files exist: `/usr/local/pgsql/lib/extension/pg_embedding_gen.so`, `/usr/local/pgsql/bin/pg_embedding_proxy.py`
- Missing: `.control` file and SQL installation script

**Recommended Approach** (v0.4.0):
Use external BGE-M3 API instead of native PostgreSQL extension:

```python
# BGE-M3 API configuration
BGE_M3_API = "http://10.10.10.1:12345/v1/embeddings"
MODEL_NAME = "text-embedding-bge-m3"
VECTOR_DIM = 1024

# Python client for embedding generation
import requests

def generate_embedding(text):
    payload = {
        "model": MODEL_NAME,
        "input": text,
        "encoding_format": "float"
    }
    response = requests.post(BGE_M3_API, json=payload, timeout=30)
    return response.json()["data"][0]["embedding"]
```

### Issue 5: AGE Graph Creation Fails

**Symptom**: `ERROR: function create_graph(unknown) does not exist`

**Cause**: Wrong function path or extension not properly loaded

**Solution**:
```bash
# Check if AGE extension is loaded
/usr/local/pgsql/bin/psql -d memory_graph -c '\dx+ age'

# Correct AGE graph creation
/usr/local/pgsql/bin/psql -d memory_graph -c 'SELECT * FROM ag_catalog.create_graph('\''knowledge_graph_age'\'');'
```

**Note**: In PostgreSQL 18 + AGE 1.7.0, use `ag_catalog.create_graph()` not `create_graph()`.

---

## 📊 Knowledge Base Deployment (v0.4.0)

### Step-by-Step Deployment

```bash
# 1. Deploy Knowledge Base schema
/usr/local/pgsql/bin/psql -d memory_graph -f scripts/knowledge_base_schema_pg.sql

# 2. Verify tables created
/usr/local/pgsql/bin/psql -d memory_graph -c '\dt knowledge_*'

# Expected output:
# knowledge_concepts
# knowledge_graph
# knowledge_versions
# knowledge_tags
# knowledge_concept_tags
# knowledge_distillation_log
# knowledge_search_history
```

### Vector Index Setup

```bash
# Verify pgvector index created
/usr/local/pgsql/bin/psql -d memory_graph -c '\di'

# Expected: idx_kc_embedding (ivfflat) on knowledge_concepts
```

### AGE Graph Verification

```bash
# Check AGE graph exists
/usr/local/pgsql/bin/psql -d memory_graph -c 'SELECT * FROM ag_catalog.ag_graph;'

# Expected: graph with name 'knowledge_graph_age'
```

---

## 🔍 Verification Commands

```bash
# PostgreSQL version
/usr/local/pgsql/bin/psql --version

# Server status
/usr/local/pgsql/bin/pg_ctl -D ~/pgsql_data status

# Extension list
/usr/local/pgsql/bin/psql -d memory_graph -c '\dx'

# Table list
/usr/local/pgsql/bin/psql -d memory_graph -c '\dt'

# Index list
/usr/local/pgsql/bin/psql -d memory_graph -c '\di'

# Vector index details
/usr/local/pgsql/bin/psql -d memory_graph -c '\di idx_kc_embedding'

# AGE graph list
/usr/local/pgsql/bin/psql -d memory_graph -c 'SELECT * FROM ag_catalog.ag_graph;'
```

---

## 📚 Reference: Server Configuration

| Component | Path | Notes |
|-----------|-------|-------|
| PostgreSQL Binary | `/usr/local/pgsql/bin/` | psql, pg_ctl, postgres |
| Data Directory | `~/pgsql_data` | User-owned location |
| Log File | `~/pgsql_data/logfile` | Server logs |
| Socket | `/tmp/.s.PGSQL.5432` | Local connection socket |
| BGE-M3 API | `http://10.10.10.1:12345/v1/embeddings` | External embedding service |

---

## 🎯 Best Practices

1. **Always use user home directory** for custom PostgreSQL installations
2. **Verify extensions before schema deployment** - pgvector, age must be loaded
3. **Use external embedding APIs** for reliability (BGE-M3 via LM Studio)
4. **Test connectivity first** - SSH, PostgreSQL, API endpoints
5. **Monitor log files** - `~/pgsql_data/logfile` for startup errors
6. **Create data backups** - Regular dumps of `memory_graph` database

---

## 🆘 Version Notes

- **PostgreSQL**: 18.3
- **pgvector**: 0.8.2
- **Apache AGE**: 1.7.0
- **memory-pg18-by-yhw**: v0.4.0 (Knowledge Base Edition)
- **BGE-M3**: text-embedding-bge-m3 (1024 dimensions)

---

## 🔗 Related Skills

- `oracle-memory-by-yhw` v1.0.0 - Source for Knowledge Base system design
- `memory-ob4-ce-by-yhw` v0.1.2 - OceanBase CE alternative implementation
- `memory-tidb8-ce-by-yhw` v0.1.2 - TiDB CE alternative implementation
