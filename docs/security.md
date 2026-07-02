# Security - AI Agent Infra v3.8.0 (2026-06-18) - PG Community Edition

## Data Masking

`DataMaskingService` automatically detects and masks sensitive data:

| Pattern | Example Input | Masked Output |
|---------|--------------|---------------|
| email | user@example.com | ****@example.com |
| phone | 555-123-4567 | 555***-4567 |
| credit_card | 4111111111111111 | ****-****-****-1111 |
| ssn | 123-45-6789 | ***-**-6789 |
| api_key | secretAbcDefGhi... | secr...Ghi |
| ip_address | 192.168.1.1 | ***.***.***.1 |
| jwt_token | eyJhbG... | eyJ...+last16 |

### Context-Aware Masking

| Context | Patterns Masked |
|---------|----------------|
| LOGGING | email, phone, credit_card, ssn, api_key, jwt_token |
| DEBUGGING | All LOGGING + ip_address |
| ANALYTICS | credit_card, ssn, api_key, jwt_token |
| SHARING | All LOGGING + ip_address |

```python
from scripts.lib.security import DataMaskingService
svc = DataMaskingService("SHARING")
safe_text = svc.mask_text("admin@company.com called from 10.0.0.1")
safe_dict = svc.mask_dict({"password": "secret", "name": "John"})
```

## Password Hashing

PBKDF2-HMAC-SHA256 with configurable iterations (default: 100,000).

```python
from scripts.lib.security import hash_password, verify_password
hash_val, salt = hash_password("MyPassword123!")
is_valid = verify_password("MyPassword123!", hash_val, salt)
```

## Entity Visibility

| Level | Access |
|-------|--------|
| PRIVATE | Only OWNED_BY_AGENT |
| SHARED | All registered agents |
| PUBLIC | Unrestricted |

Cross-agent sharing is managed via the AGENT_COLLABORATION table.

## Access Auditing

All entity access is logged to ENTITY_ACCESS_LOG:
- LOG_ID (VARCHAR(64)), Entity ID, Agent ID, Access Type (READ/WRITE/DELETE/SEARCH/EMBED), Access Time, Session ID, Context

## Row Security Policies (v3.7.0)

v3.7.0 uses PostgreSQL Row Security Policies for data isolation:

- **25+ Row Security Policies** enforce row-level, column-level, and cell-level access control
- **3 Database Roles**: `admin_data_role` (full), `agent_data_role` (filtered by agent), `pool_agent_data_role` (minimum)
- **Agent Context** via `current_setting('app.current_agent_id', TRUE)` for zero-trust agent identification
- **SYSTEM_CONFIG** fully restricted to `admin_data_role` only

**Portal API Context Switching**: Portal APIs that access WORKSPACES or SYSTEM_USERS tables temporarily use `connection.set_agent_context(None)` to switch to the schema owner connection, because WORKSPACES.CURRENT_AGENT_ID is NULL for most workspaces, causing RLS predicates to reject all rows for restricted users. After the operation completes, the agent context is restored.

### WORKSPACE_CONTEXT VISIBILITY

WORKSPACE_CONTEXT has a VISIBILITY column (PRIVATE/SHARED/PUBLIC, default SHARED) that controls cross-agent context visibility in collaboration group workspaces:

| VISIBILITY | Agent sees own context? | Other agents in collab group see it? |
|------------|------------------------|--------------------------------------|
| PRIVATE | Yes (always) | No — blocked by RLS policy |
| SHARED | Yes (always) | Yes — visible to collab group members |
| PUBLIC | Yes (always) | Yes — visible to all |

The `ws_ctx_agent_access` RLS policy enforces these rules:
- Agent always sees its own context (AGENT_ID matches) regardless of VISIBILITY
- Agent sees other agents' SHARED/PUBLIC context only in collab group workspaces
- Agent CANNOT see other agents' PRIVATE context even in the same collab group workspace

## Admin/Agent Separation Security Model

v3.7.0 introduces the Admin/Agent Separation Architecture, which significantly reduces the security blast radius of a compromised Business Agent.

### Threat Model Comparison

| Threat | Before v3.7.0 | After v3.7.0 (Agent mode) |
|--------|--------------|--------------------------|
| Business Agent compromised | Attacker gets schema owner credentials → full database access | Attacker gets restricted user credentials → RLS-filtered access only |
| Credential leakage from config.json | Schema owner user/password exposed | Only restricted user credentials exposed (scoped by RLS) |
| Rogue Agent process | Can bypass all RLS (schema owner bypasses) | Cannot bypass RLS (restricted user connection) |
| Lateral movement | Schema owner access to all tables and rows | Restricted user access limited to agent's own data |

### Admin Token Security

- **Generation**: `generate_admin_token()` creates a 32-byte random token, hex-encoded with AT_ prefix
- **Storage**: Stored in `SYSTEM_CONFIG` as `admin.registration_token` (encrypted with pgcrypto)
- **Rotation**: `POST /api/admin/token/rotate` invalidates old token; Business Agents must re-register
- **Usage**: Single-use for registration; encrypted credential distribution uses it as PBKDF2 key material

### Encrypted Credential Distribution

End User credentials are encrypted in transit using the admin_token as key material:

1. Admin Agent generates admin_token
2. Admin_token shared with Business Agent operator over out-of-band secure channel
3. Business Agent sends registration request with admin_token
4. Admin Agent encrypts credentials with `encrypt_credential_for_distribution(credential, admin_token)`
5. Business Agent decrypts with `decrypt_credential_from_distribution(encrypted, salt, admin_token)`
6. Business Agent saves to encrypted `agent_config.json` with `save_agent_config(config, path)`

**Key properties:**
- admin_token is never stored on the Business Agent node
- PBKDF2-HMAC-SHA512 with 210,000 iterations prevents brute-force
- HMAC-SHA256 authentication tag prevents tampering
- agent_config.json is encrypted at rest using derived key

### Mode-Specific Security Controls

| Control | standalone | admin | agent |
|---------|-----------|-------|-------|
| Schema owner connection pool | Yes | Yes | **No** |
| RLS-restricted connections | Yes | Yes | Yes (only option) |
| Web Portal | Yes | Yes | **No** |
| admin_token stored locally | N/A | No | **No** |
| agent_config.json | No | No | Yes (encrypted) |
| RLS enforcement | Yes (with schema owner bypass) | Yes (with schema owner bypass) | **Always enforced** |
| SYSTEM_CONFIG access | Via schema owner | Via schema owner | **Blocked** (admin_data_role only) |

## Encryption Architecture

### Dual-Track Encryption

| Track | Component | Encrypts | Key Storage |
|-------|-----------|----------|-------------|
| Local file | connection_crypto.py | config.json DB credentials | `~/.pg-infra/master.key` |
| In-database | pgcrypto | AGENT_CREDENTIALS | SYSTEM_CONFIG table |

### pgcrypto In-Database Encryption

```sql
-- Encrypt
SELECT encode(encrypt_iv(%s::bytea, %s::bytea, 'aes-cbc'), 'base64');

-- Decrypt
SELECT convert_from(decrypt_iv(decode(%s, 'base64'), %s::bytea, 'aes-cbc'), 'UTF8');
```

Key properties:
- AES-CBC encryption via pgcrypto extension
- Keys stored in SYSTEM_CONFIG (db_crypto_master_key / db_crypto_key_salt)
- All agents sharing the same database automatically share encryption keys
- Key auto-generation on first use; concurrent-safe via ON CONFLICT
