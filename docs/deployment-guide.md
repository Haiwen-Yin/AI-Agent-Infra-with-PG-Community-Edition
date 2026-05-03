# PostgreSQL 18 + pgvector + Apache AGE Deployment Guide (Standard Linux Installation)

**Version**: v0.3.1  
**Applicable Systems**: RHEL 9.x / CentOS Stream 9 / Ubuntu 24.04 LTS

---

## 📋 **System Requirements**

| Component | Minimum | Recommended |
|--|--|--:|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk | 50 GB SSD | 100+ GB NVMe |
| OS | RHEL 9 / Ubuntu 22.04 | Ubuntu 24.04 LTS |

---

## 💻 **Standard Linux Installation Guide**

### Step 1: Install PostgreSQL 18 with Extensions

#### Ubuntu/Debian Systems
```bash
# Update package lists and install PostgreSQL 18
sudo apt update && sudo apt install postgresql-18 -y

# Install pgvector extension (if available in repository)
sudo apt install postgresql-18-vector -y || echo "pgvector not found in repos, will compile manually"

# Start PostgreSQL service
sudo systemctl start postgresql@18-main
sudo systemctl enable postgresql@18-main
```

#### CentOS/RHEL 9 Systems
```bash
# Add PostgreSQL repository for RHEL 9
curl https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/postgresql-pgdg-redhat-repo-latest.noarch.rpm | sudo rpm -Uvh

# Install PostgreSQL 18 server and vector extension
sudo yum install postgresql18-server postgresql18-vector -y

# Initialize database cluster
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb

# Start PostgreSQL service
sudo systemctl enable --now postgresql-18.service
```

### Step 2: Install Apache AGE Extension (If Not Available in Repos)

For systems where AGE extension is not pre-packaged, compile from source:
sudo dnf install -y postgresql18-server postgresql18-contrib

# Initialize cluster
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb
sudo systemctl enable --now postgresql-18
```

#### Ubuntu 24.04+
```bash
# Add PGDG repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL 18
sudo apt-get update
sudo apt-get install -y postgresql-18 postgresql-contrib-18
```

### Step 2: Install pgvector

```bash
cd /tmp
git clone https://github.com/pgvector/pgvector.git
cd pgvector

# Build and install
make PG_CONFIG=/usr/bin/pg_config
sudo make install PG_CONFIG=/usr/bin/pg_config

# Verify installation
psql -U postgres -c "CREATE EXTENSION vector;"
```

### Step 3: Install Apache AGE

#### Option A: From Source (Recommended)
```bash
cd /tmp
git clone https://github.com/apache/age.git
cd age
git checkout tags/v1.7.0

# Build and install
make PG_CONFIG=/usr/bin/pg_config
sudo make install PG_CONFIG=/usr/bin/pg_config
```

#### Option B: From RPM (RHEL/CentOS 9+)
```bash
wget https://apache.jfrog.io/artifactory/age/rpm/latest/el9/x86_64/apache-age-1.7.0.rpm
sudo rpm -ivh --force apache-age-1.7.0.rpm
```

### Step 4: Configure PostgreSQL Extensions

Edit the PostgreSQL configuration file to load extensions on startup:

**For Ubuntu/Debian:**
```bash
sudo nano /etc/postgresql/18/main/postgresql.conf
```

**For RHEL/CentOS:**
```bash
sudo nano /var/lib/pgsql/data/postgresql.conf
```

Add or uncomment these lines in the configuration file:
```ini
shared_preload_libraries = 'age, vector'
listen_addresses = '*'
max_connections = 200
```

Restart PostgreSQL service to apply changes:
**Ubuntu/Debian:**
```bash
sudo systemctl restart postgresql@18-main
```

**RHEL/CentOS:**
```bash
sudo systemctl restart postgresql-18.service
```

---

## ⚠️ **AGE PG18 Critical Setup Requirements**

> **🔥 IMPORTANT**: These requirements are specific to AGE 1.7.0 on PostgreSQL 18 and must be followed for Cypher queries to work correctly.

### Requirement 1: Always Set Search Path Before Cypher Queries
```sql
SET search_path TO ag_catalog;
```

Without this, Cypher functions will not be found.

---

### Requirement 2: create_graph() Requires Type Cast (::name)

**❌ INCORRECT - Will fail with:** `ERROR: function create_graph(unknown) does not exist`
```sql
SELECT create_graph('memory_graph');
```

**✅ CORRECT - Always use ::name cast:**
```sql
SELECT create_graph('memory_graph'::name);
```

---

### Requirement 3: Use Dollar Quoting for Cypher Strings

**❌ INCORRECT - Will fail with:** `ERROR: unhandled cypher(cstring) function call`
```sql
SELECT * FROM cypher('graph', 'RETURN 1');
```

**✅ CORRECT - Always use $$...$$:**
```sql
SELECT * FROM cypher('graph', $$ RETURN 1 $$);
```

---

### Requirement 4: Avoid SQL Reserved Words in Cypher Variables

**❌ INCORRECT**: `start` and `end` are SQL reserved words
```sql
MATCH (start)-[r]->(end) RETURN start, end;
```

**✅ CORRECT - Use alternative names:**
```sql
MATCH (node_a)-[r]->(node_b) RETURN node_a, node_b;
```

---

### Quick Setup Checklist for Cypher Queries

Before running any Cypher query, execute these commands first:
```sql
SET search_path TO ag_catalog;
SELECT create_graph('your_graph_name'::name);
```

---

## 🔐 **Security Hardening**

### Step 1: Configure pg_hba.conf
Allow local connections only:
```
host    all             all             127.0.0.1/32            scram-sha-256
local   all             all                                     scram-sha-256
```

### Step 2: Set Strong Password
```bash
psql -U postgres << 'EOSQL'
ALTER USER postgres WITH PASSWORD 'your_strong_password_here';
EOSQL
```

---

## 📊 **Monitoring & Maintenance**

### Check Extension Versions
```bash
psql -U postgres << 'EOSQL'
SELECT extname, extversion, n.nspname as schema_name
FROM pg_extension e
JOIN pg_namespace n ON e.extnamespace = n.oid
WHERE e.extname IN ('vector', 'age')
ORDER BY e.extname;
EOSQL
```

### Backup Strategy
```bash
# Daily backup
pg_dump -d memory_graph -f /backup/memory_graph_$(date +%Y%m%d).sql
```

---

## 🚨 **Troubleshooting**

### Issue: "extension 'vector' is not available"
**Solution**: Verify pgvector installation with `psql -U postgres -c "\\dx vector"`

### Issue: "could not load library 'age.so'"
**Solution**: Check that age.so exists in extension directory

---

**Version**: v0.3.1  
**Last Updated**: 2026-04-30 CST (Standard Linux Installation Guide)
