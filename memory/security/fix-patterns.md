# Security Fix Patterns

Secure coding alternatives and fix patterns for common vulnerability categories. Used by security-fixer skill to generate patches.

## CWE-89: SQL Injection

### Root Cause
String concatenation or interpolation used to build SQL queries with user input.

### Secure Alternative
Parameterized queries or prepared statements.

### Python Examples

**SQLite**:
```python
# Vulnerable
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# Fixed
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**PostgreSQL (psycopg2)**:
```python
# Vulnerable
cursor.execute(f"UPDATE users SET email = '{email}' WHERE id = {user_id}")

# Fixed
cursor.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
```

**SQLAlchemy ORM**:
```python
# Vulnerable
from sqlalchemy import text
result = session.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# Fixed
result = session.execute(text("SELECT * FROM users WHERE name = :name"), {"name": name})
```

**Django ORM**:
```python
# Vulnerable
User.objects.raw(f"SELECT * FROM users WHERE status = '{status}'")

# Fixed (use ORM)
User.objects.filter(status=status)

# Or if raw SQL needed
User.objects.raw("SELECT * FROM users WHERE status = %s", [status])
```

### JavaScript/TypeScript Examples

**Node.js (pg)**:
```javascript
// Vulnerable
const query = `SELECT * FROM users WHERE email = '${email}'`;
await client.query(query);

// Fixed
await client.query('SELECT * FROM users WHERE email = $1', [email]);
```

**Prisma ORM**:
```typescript
// Vulnerable (raw SQL)
await prisma.$queryRaw`SELECT * FROM users WHERE name = '${name}'`;

// Fixed
await prisma.user.findMany({ where: { name } });

// Or if raw SQL needed
await prisma.$queryRaw`SELECT * FROM users WHERE name = ${name}`;
```

## CWE-79: Cross-Site Scripting (XSS)

### Root Cause
User input rendered in HTML without encoding, allowing script injection.

### Secure Alternative
Output encoding, Content Security Policy, framework auto-escaping.

### Python Examples

**Flask**:
```python
# Vulnerable
from flask import Flask
@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"<h1>Hello {name}!</h1>"

# Fixed
from flask import Flask, escape
@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"<h1>Hello {escape(name)}!</h1>"

# Better: Use templates (auto-escaping)
return render_template('hello.html', name=name)
```

**Jinja2 Templates**:
```jinja2
{# Vulnerable - disables auto-escaping #}
<div>{{ user_comment | safe }}</div>

{# Fixed - auto-escaping enabled #}
<div>{{ user_comment }}</div>

{# If HTML needed, sanitize first #}
<div>{{ user_comment | bleach }}</div>
```

### JavaScript/TypeScript Examples

**React**:
```jsx
// Vulnerable
function UserGreeting({ name }) {
  return <div dangerouslySetInnerHTML={{__html: `Hello ${name}`}} />;
}

// Fixed - React auto-escapes
function UserGreeting({ name }) {
  return <div>Hello {name}</div>;
}
```

**DOM Manipulation**:
```javascript
// Vulnerable
element.innerHTML = userInput;

// Fixed
element.textContent = userInput;

// Or sanitize HTML
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

## CWE-22: Path Traversal

### Root Cause
User input used directly in file paths without validation.

### Secure Alternative
Path validation, allowlists, safe path joining.

### Python Examples

**Unsafe Path Joining**:
```python
# Vulnerable
import os
file_path = os.path.join('/var/uploads', user_filename)
with open(file_path, 'r') as f:
    return f.read()

# Fixed
from pathlib import Path

def safe_join(directory, filename):
    """Safely join paths and prevent traversal."""
    base = Path(directory).resolve()
    target = (base / filename).resolve()

    # Ensure resolved path is within base directory
    if not str(target).startswith(str(base) + os.sep):
        raise ValueError("Path traversal attempt detected")

    return target

file_path = safe_join('/var/uploads', user_filename)
with open(file_path, 'r') as f:
    return f.read()
```

**Filename Validation**:
```python
# Vulnerable
file_path = f"/data/{user_provided_path}"

# Fixed
import re
from pathlib import Path

def validate_filename(filename):
    """Validate filename against allowlist pattern."""
    # Only allow alphanumeric, dash, underscore, dot
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        raise ValueError("Invalid filename")

    # Prevent double extensions (.php.jpg)
    if filename.count('.') > 1:
        raise ValueError("Multiple extensions not allowed")

    # Check extension allowlist
    allowed = {'.jpg', '.png', '.pdf', '.txt'}
    if Path(filename).suffix.lower() not in allowed:
        raise ValueError("File type not allowed")

    return filename

filename = validate_filename(user_input)
file_path = Path('/data') / filename
```

### Node.js Examples

```javascript
// Vulnerable
const fs = require('fs');
const path = require('path');
const filePath = path.join('/uploads', userInput);
const content = fs.readFileSync(filePath, 'utf8');

// Fixed
const fs = require('fs');
const path = require('path');

function safeJoin(base, target) {
  const resolvedBase = path.resolve(base);
  const resolvedTarget = path.resolve(base, target);

  if (!resolvedTarget.startsWith(resolvedBase + path.sep)) {
    throw new Error('Path traversal detected');
  }

  return resolvedTarget;
}

const filePath = safeJoin('/uploads', userInput);
const content = fs.readFileSync(filePath, 'utf8');
```

## CWE-798: Hardcoded Credentials

### Root Cause
Secrets embedded in source code.

### Secure Alternative
Environment variables, secret management systems, config files (.gitignored).

### Python Examples

**Hardcoded API Keys**:
```python
# Vulnerable
API_KEY = "sk_live_1234567890abcdef"
DB_PASSWORD = "supersecret123"

# Fixed
import os

API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable required")

DB_PASSWORD = os.environ.get('DB_PASSWORD')
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable required")
```

**Configuration Management**:
```python
# Vulnerable
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# Fixed
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str

    class Config:
        env_file = '.env'  # Load from .env file (gitignored)

settings = Settings()
```

### JavaScript/TypeScript Examples

```typescript
// Vulnerable
const config = {
  apiKey: 'sk_live_abcd1234',
  dbPassword: 'admin123',
};

// Fixed
import dotenv from 'dotenv';
dotenv.config();

const config = {
  apiKey: process.env.API_KEY,
  dbPassword: process.env.DB_PASSWORD,
};

if (!config.apiKey || !config.dbPassword) {
  throw new Error('Required environment variables not set');
}
```

## CWE-327: Weak Cryptography

### Root Cause
Use of broken/weak crypto algorithms (MD5, SHA1, DES, ECB mode).

### Secure Alternative
Modern algorithms (AES-256-GCM, SHA-256+, bcrypt, Argon2).

### Python Examples

**Password Hashing**:
```python
# Vulnerable - MD5/SHA1
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# Fixed - bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# Verification
is_valid = check_password_hash(password_hash, password)

# Better - Argon2
from argon2 import PasswordHasher
ph = PasswordHasher()

password_hash = ph.hash(password)
is_valid = ph.verify(password_hash, password)
```

**Symmetric Encryption**:
```python
# Vulnerable - DES, ECB mode
from Crypto.Cipher import DES
cipher = DES.new(key, DES.MODE_ECB)
encrypted = cipher.encrypt(data)

# Fixed - AES-256-GCM
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # 96-bit nonce
encrypted = aesgcm.encrypt(nonce, data.encode(), None)

# Decrypt
decrypted = aesgcm.decrypt(nonce, encrypted, None).decode()
```

### JavaScript/TypeScript Examples

**Password Hashing**:
```javascript
// Vulnerable - SHA256
import crypto from 'crypto';
const hash = crypto.createHash('sha256').update(password).digest('hex');

// Fixed - bcrypt
import bcrypt from 'bcrypt';

// Hash
const saltRounds = 10;
const hash = await bcrypt.hash(password, saltRounds);

// Verify
const isValid = await bcrypt.compare(password, hash);
```

## CWE-352: CSRF

### Root Cause
State-changing operations lack CSRF token validation.

### Secure Alternative
Synchronizer token pattern, SameSite cookies, double-submit cookies.

### Python Examples

**Flask**:
```python
# Vulnerable
from flask import Flask, request

@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    process_transfer(amount, to_account)
    return "Transfer complete"

# Fixed - Flask-WTF
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
def transfer():
    # CSRF token automatically validated
    amount = request.form['amount']
    to_account = request.form['to']
    process_transfer(amount, to_account)
    return "Transfer complete"

# Template includes token
# <form method="post">
#   {{ csrf_token() }}
#   ...
# </form>
```

**Django**:
```python
# Vulnerable - CSRF exempt
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def transfer(request):
    amount = request.POST['amount']
    process_transfer(amount)
    return HttpResponse("Done")

# Fixed - Use CSRF middleware (default)
def transfer(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        process_transfer(amount)
        return HttpResponse("Done")

# Template includes token
# {% csrf_token %}
```

### JavaScript/TypeScript Examples

**Express**:
```javascript
// Vulnerable - No CSRF protection
app.post('/transfer', (req, res) => {
  processTransfer(req.body.amount, req.body.to);
  res.send('Done');
});

// Fixed - csurf middleware
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: true });

app.post('/transfer', csrfProtection, (req, res) => {
  processTransfer(req.body.amount, req.body.to);
  res.send('Done');
});

// Generate token for forms
app.get('/form', csrfProtection, (req, res) => {
  res.render('form', { csrfToken: req.csrfToken() });
});
```

## CWE-502: Insecure Deserialization

### Root Cause
Deserializing untrusted data with pickle, YAML, or other unsafe formats.

### Secure Alternative
Safe formats (JSON), schema validation, allowlists.

### Python Examples

**Pickle Deserialization**:
```python
# Vulnerable
import pickle

def load_data(serialized_data):
    return pickle.loads(serialized_data)  # Arbitrary code execution!

# Fixed - Use JSON
import json
from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    name: str
    email: str

def load_data(json_data):
    data = json.loads(json_data)
    return UserData(**data)  # Validates against schema
```

**YAML Deserialization**:
```python
# Vulnerable
import yaml

config = yaml.load(untrusted_input)  # yaml.load is unsafe

# Fixed
import yaml

config = yaml.safe_load(untrusted_input)  # Only loads safe types
```

### JavaScript Examples

```javascript
// Vulnerable - eval
const data = eval('(' + userInput + ')');

// Fixed - JSON.parse
const data = JSON.parse(userInput);

// With validation
import Ajv from 'ajv';

const schema = {
  type: 'object',
  properties: {
    id: { type: 'number' },
    name: { type: 'string' },
  },
  required: ['id', 'name'],
};

const ajv = new Ajv();
const validate = ajv.compile(schema);
const data = JSON.parse(userInput);

if (!validate(data)) {
  throw new Error('Invalid data: ' + JSON.stringify(validate.errors));
}
```

## Framework-Specific Patterns

### Django Security

**Settings**:
```python
# Vulnerable settings.py
DEBUG = True
SECRET_KEY = 'hardcoded-key'
ALLOWED_HOSTS = ['*']
SECURE_SSL_REDIRECT = False

# Fixed settings.py
import os

DEBUG = False  # Never True in production
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Flask Security

**Configuration**:
```python
# Vulnerable
app.config['SECRET_KEY'] = 'dev'
app.config['SESSION_COOKIE_SECURE'] = False

# Fixed
import os
from flask_talisman import Talisman

app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Security headers
Talisman(app, content_security_policy={
    'default-src': "'self'",
})
```

### Express.js Security

**Middleware**:
```javascript
// Vulnerable
const express = require('express');
const app = express();

// Fixed
const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();

// Security headers
app.use(helmet());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// CSRF protection
const csrf = require('csurf');
app.use(csrf({ cookie: true }));
```

## Validation Patterns

### Input Validation

**Python (Pydantic)**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class UserInput(BaseModel):
    email: str = Field(..., regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    age: int = Field(..., ge=0, le=150)
    username: str = Field(..., min_length=3, max_length=50)

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

# Usage
try:
    user = UserInput(**request_data)
except ValidationError as e:
    return {"error": e.errors()}, 400
```

**JavaScript (Zod)**:
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
});

// Usage
try {
  const user = userSchema.parse(requestData);
} catch (error) {
  if (error instanceof z.ZodError) {
    return res.status(400).json({ errors: error.errors });
  }
}
```

## Testing Fixes

### Verify SQL Injection Fix

```python
import pytest

def test_sql_injection_prevented():
    """Verify SQL injection no longer possible."""
    malicious_input = "1' OR '1'='1"

    # Should not return all users
    result = get_user_by_id(malicious_input)
    assert result is None or result.id == malicious_input

    # Should raise error or return None, not execute injection
    malicious_input = "1; DROP TABLE users; --"
    result = get_user_by_id(malicious_input)
    assert result is None
```

### Verify XSS Fix

```python
def test_xss_prevented():
    """Verify XSS script tags are escaped."""
    malicious_input = "<script>alert('XSS')</script>"

    response = render_greeting(malicious_input)

    # Should be escaped
    assert '<script>' not in response
    assert '&lt;script&gt;' in response
```

### Verify Path Traversal Fix

```python
def test_path_traversal_prevented():
    """Verify directory traversal is blocked."""
    with pytest.raises(ValueError, match="Path traversal"):
        safe_join('/uploads', '../../../etc/passwd')

    with pytest.raises(ValueError, match="Path traversal"):
        safe_join('/uploads', 'subdir/../../etc/passwd')
```
