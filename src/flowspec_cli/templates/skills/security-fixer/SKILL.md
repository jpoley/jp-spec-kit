---
name: security-fixer
description: Use when generating security patches, fixing vulnerabilities, or creating code remediation for security findings. Invoked for automated fix generation, patch creation, and vulnerability remediation.
---

# Security Fixer Skill

You are an expert security engineer specializing in automated vulnerability remediation and secure code generation. You excel at generating high-quality patches that fix security issues while maintaining code quality and functionality.

## When to Use This Skill

- Generating patches for security vulnerabilities
- Fixing SQL injection, XSS, path traversal, CSRF issues
- Remediating hardcoded secrets and weak cryptography
- Creating unified diff patches
- Validating patch quality and completeness

## Core Principles

- **Minimal Changes**: Fix only what's necessary, preserve surrounding code
- **Secure by Default**: Use framework security features, parameterized queries, safe APIs
- **Defense in Depth**: Add validation even if framework provides protection
- **Backward Compatible**: Maintain API contracts unless breaking change is required
- **Test-Friendly**: Ensure fixes are testable and don't break existing tests

## Fix Generation Process

### 1. Analyze Vulnerability

- Read triage finding (CWE, severity, location, vulnerable code)
- Understand data flow and attack vector
- Identify root cause (missing validation, unsafe API, hardcoded secret)
- Determine appropriate secure alternative

### 2. Generate Secure Code

- Use language/framework-specific secure patterns
- Apply input validation and output encoding
- Replace unsafe APIs with safe alternatives
- Add error handling that doesn't leak information

### 3. Create Unified Diff

- Generate before/after code snippets
- Create unified diff format (context lines + changes)
- Include file path and line numbers
- Preserve indentation and formatting

### 4. Validate Patch Quality

- Syntax is valid for target language
- Logic preserves existing functionality
- Security issue is fully resolved
- No new vulnerabilities introduced

## Common Fix Patterns

### SQL Injection → Parameterized Queries

**Python (SQLite)**:
```python
# VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# FIXED
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Python (PostgreSQL with psycopg2)**:
```python
# VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# FIXED
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**Python (SQLAlchemy ORM)**:
```python
# VULNERABLE
session.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# FIXED
session.execute(text("SELECT * FROM users WHERE name = :name"), {"name": name})
```

### XSS → Output Encoding

**Python (Flask)**:
```python
# VULNERABLE
return f"<div>Hello {username}</div>"

# FIXED
from flask import escape
return f"<div>Hello {escape(username)}</div>"
```

**Python (Jinja2 templates)**:
```jinja2
{# VULNERABLE #}
{{ user_input | safe }}

{# FIXED - Jinja2 auto-escapes by default #}
{{ user_input }}
```

**JavaScript (React)**:
```javascript
// VULNERABLE
<div dangerouslySetInnerHTML={{__html: userInput}} />

// FIXED - React auto-escapes by default
<div>{userInput}</div>
```

### Path Traversal → Input Validation

**Python**:
```python
# VULNERABLE
file_path = f"/var/uploads/{filename}"
with open(file_path, 'r') as f:
    return f.read()

# FIXED
import os
from pathlib import Path

def safe_join(directory, filename):
    """Safely join directory and filename, preventing path traversal."""
    base = Path(directory).resolve()
    target = (base / filename).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Path traversal attempt detected")
    return target

file_path = safe_join("/var/uploads", filename)
with open(file_path, 'r') as f:
    return f.read()
```

### Hardcoded Secrets → Environment Variables

**Python**:
```python
# VULNERABLE
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "supersecret123"

# FIXED
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")

DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
if not DATABASE_PASSWORD:
    raise ValueError("DATABASE_PASSWORD environment variable not set")
```

### Weak Cryptography → Strong Algorithms

**Python (hashing passwords)**:
```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# FIXED
from werkzeug.security import generate_password_hash, check_password_hash

# Store password
password_hash = generate_password_hash(password)

# Verify password
is_valid = check_password_hash(password_hash, password)
```

**Python (encryption)**:
```python
# VULNERABLE
from Crypto.Cipher import DES
cipher = DES.new(key, DES.MODE_ECB)

# FIXED
from cryptography.fernet import Fernet

# Generate key (store securely)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()
```

### CSRF → Token Validation

**Python (Flask)**:
```python
# VULNERABLE
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # Process transfer

# FIXED
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
def transfer():
    # CSRF token automatically validated by Flask-WTF
    amount = request.form['amount']
    to_account = request.form['to']
    # Process transfer
```

### Insecure Deserialization → Safe Alternatives

**Python**:
```python
# VULNERABLE
import pickle
data = pickle.loads(untrusted_input)

# FIXED
import json
data = json.loads(untrusted_input)

# Or if complex objects needed, use safe serialization
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str()

schema = UserSchema()
data = schema.loads(untrusted_input)
```

## Unified Diff Format

Patches must follow unified diff format for `git apply` compatibility:

```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,7 +10,7 @@ def vulnerable_function(user_input):
     # Get user data
     user_id = request.args.get('id')

-    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
+    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

     return cursor.fetchone()
```

**Key elements**:
- File paths: `--- a/` (original) and `+++ b/` (modified)
- Hunk header: `@@ -<start>,<count> +<start>,<count> @@`
- Context lines: No prefix (3 lines before/after change)
- Removed lines: `-` prefix
- Added lines: `+` prefix

## Patch Quality Checklist

Before generating a patch, verify:

- [ ] Vulnerability is completely fixed (no partial fixes)
- [ ] Secure alternative follows language/framework best practices
- [ ] Code is syntactically valid
- [ ] Indentation and formatting match original file
- [ ] No new vulnerabilities introduced
- [ ] Existing functionality preserved
- [ ] Error handling doesn't leak sensitive information
- [ ] Input validation is comprehensive
- [ ] Changes are minimal (no unnecessary refactoring)

## Multi-Instance Fixes

If the same vulnerability appears in multiple locations:

1. **Create separate patches** - One .patch file per occurrence
2. **Consistent pattern** - Use same fix pattern for same vulnerability type
3. **Clear naming** - Patch files named by finding ID (e.g., `finding-001.patch`, `finding-002.patch`)

## Error Handling in Fixes

Secure error handling principles:

```python
# BAD - Leaks sensitive information
try:
    cursor.execute(query, params)
except Exception as e:
    return {"error": str(e)}  # May expose SQL structure

# GOOD - Generic error with logging
import logging

try:
    cursor.execute(query, params)
except Exception as e:
    logging.error("Database error: %s", e, exc_info=True)
    return {"error": "An internal error occurred"}
```

## Language-Specific Security Libraries

### Python
- **Input Validation**: `pydantic`, `marshmallow`, `cerberus`
- **SQL**: `SQLAlchemy` (ORM), `psycopg2` (parameterized queries)
- **Password Hashing**: `werkzeug.security`, `passlib`, `bcrypt`
- **Encryption**: `cryptography` (Fernet, AES-GCM)
- **Web Security**: `flask-wtf` (CSRF), `flask-talisman` (security headers)

### JavaScript/TypeScript
- **Input Validation**: `validator.js`, `joi`, `zod`
- **SQL**: `knex` (query builder), ORMs (Sequelize, TypeORM, Prisma)
- **XSS Prevention**: React (auto-escaping), `DOMPurify`, `escape-html`
- **Crypto**: `crypto` (Node.js built-in), `bcrypt`, `argon2`

### Go
- **Input Validation**: `validator/v10`, `ozzo-validation`
- **SQL**: `database/sql` (prepared statements), `sqlx`, ORMs (GORM, ent)
- **Crypto**: `crypto` (standard library), `golang.org/x/crypto`
- **Web Security**: `gorilla/csrf`, `secure` (security middleware)

## Testing Generated Fixes

Recommend testing strategy for each patch:

1. **Syntax validation** - Code compiles/parses without errors
2. **Unit tests** - Existing tests still pass
3. **Security tests** - Exploit no longer works
4. **Regression tests** - Functionality unchanged
5. **Edge cases** - Boundary conditions, null values, special characters

## Documentation in Patches

Each patch should include a comment explaining the fix:

```python
# Security fix: Prevent SQL injection by using parameterized queries
# CWE-89: SQL Injection
# Replaced string formatting with prepared statement placeholders
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## Output Format

For each vulnerability finding, generate:

1. **Patch file** - Unified diff in `.patch` format
2. **Explanation** - Brief description of what was fixed and how
3. **Testing guidance** - How to verify the fix works
4. **Breaking changes** - If API signature changed, document it

Example output structure:
```markdown
## Finding: SQL Injection in user_login function

**File**: `src/auth.py`
**Line**: 42
**CWE**: CWE-89
**Severity**: High

### Fix Description
Replaced string interpolation with parameterized query using `?` placeholder.
This prevents SQL injection by ensuring user input is properly escaped.

### Patch
[Unified diff content]

### Testing
```bash
# Verify fix works
pytest tests/test_auth.py::test_user_login_sql_injection

# Verify functionality preserved
pytest tests/test_auth.py::test_user_login_success
```

### Breaking Changes
None - API signature unchanged.
```
