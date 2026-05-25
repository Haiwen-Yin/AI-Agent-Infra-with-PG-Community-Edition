# Security — PostgreSQL Memory System v2.3.0

## Data Masking

`DataMaskingService` provides context-aware PII masking across 7 patterns.

### Sensitive Patterns

| Pattern | Regex Target | Mask Rule |
|---------|-------------|-----------|
| `credit_card` | Visa/MC/Amex numbers | `****-****-****-1234` |
| `ssn` | `XXX-XX-XXXX` | `***-**-1234` |
| `jwt_token` | `eyJ...` format | `eyJ...[last 16]` |
| `api_key` | `secret/key/token` prefix + 16+ chars | `sk-1...abcd` |
| `email` | Standard email format | `*****@domain.com` |
| `ip_address` | IPv4 dotted-quad | `***.***.***.1` |
| `phone` | US phone formats | `123***-5678` |

### Context Levels

| Level | Patterns Masked | Use Case |
|-------|----------------|----------|
| `LOGGING` | email, phone, credit_card, ssn, api_key, jwt_token | Application logs |
| `DEBUGGING` | All LOGGING + ip_address | Developer debugging |
| `ANALYTICS` | credit_card, ssn, api_key, jwt_token | Aggregated analytics |
| `SHARING` | All 7 patterns | Cross-agent sharing |

### Usage

```python
from scripts.lib.security import DataMaskingService

svc = DataMaskingService(context_level="SHARING")
masked = svc.mask_text("Contact john@example.com, SSN 123-45-6789")
# → "Contact *****@example.com, SSN ***-**-6789"

masked_dict = svc.mask_dict({"user_email": "a@b.com", "count": 42})
# → {"user_email": "***MASKED***", "count": 42}
```

## Reversible Encryption

`ReversibleEncryption` uses PBKDF2 key derivation with XOR cipher for
encrypting data that must be read back (e.g., stored API keys).

- **Key derivation**: `PBKDF2-HMAC-SHA256` with random 16-byte IV, 100 000 iterations
- **Cipher**: XOR of plaintext with derived key and IV bytes
- **Encoding**: Base64 of `IV || length_prefix(4B) || encrypted_payload`
- **Key rotation**: `rotate_key(new_key, encrypted_values)` decrypts with old key, re-encrypts with new key

```python
from scripts.lib.security import ReversibleEncryption

enc = ReversibleEncryption(key=b"my-32-byte-secret-key-here-xxxxx")
ct = enc.encrypt("secret data")    # → base64 string
pt = enc.decrypt(ct)                # → "secret data"
```

## Password Hashing

```python
from scripts.lib.security import hash_password, verify_password

h, s = hash_password("MyP@ssw0rd")              # → (hex_hash, hex_salt)
assert verify_password("MyP@ssw0rd", h, s)       # → True
assert not verify_password("wrong", h, s)        # → False
```

- Algorithm: PBKDF2-HMAC-SHA256
- Salt: 16 bytes random, stored as hex
- Iterations: 100 000 (configurable via `config.json` → `security.pbkdf2_iterations`)

## Entity Visibility Controls

Visibility is enforced at the database level by `agent_perm.check_entity_access()`:

| Visibility | Access Rule | SQL Check |
|------------|-------------|-----------|
| `SHARED` | All agents | `visibility = 'SHARED'` |
| `PRIVATE` | Owner only | `owned_by_agent = current_agent` |
| `PUBLIC` | Unrestricted | `visibility = 'PUBLIC'` |

> **Note**: The visibility model is enforced by the `agent_perm.check_entity_access`
> function, which must be called before any entity read/write operation. See the
> `agent_perm` schema in the PL/pgSQL API for grant/revoke operations.

Workspaces provide additional isolation: entities within a workspace are only
accessible to agents operating in that workspace context, regardless of visibility.

### Default Admin Account

The system seeds a default admin user in `system_users` with credentials
`admin` / `admin123`. **This is for development only** — change the password
before any production deployment:

```sql
UPDATE system_users SET password_hash = ... WHERE username = 'admin';
```

Grant/revoke access:

```sql
SELECT agent_perm.grant_access('agent-B', 42, 'agent-A');
SELECT agent_perm.revoke_access('agent-B', 42);
```

## Access Auditing

All entity access is logged to `entity_access_log`:

| Column | Values |
|--------|--------|
| `access_type` | READ, WRITE, DELETE, SHARE |
| `agent_id` | Agent performing the action |
| `entity_id` | Target entity |
| `access_time` | Timestamp |

Purge old logs:

```sql
SELECT session_cleanup.purge_access_logs(90);  -- keep last 90 days
```
