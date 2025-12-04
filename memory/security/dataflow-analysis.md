# Dataflow Analysis Patterns

## Overview

This document describes common dataflow analysis patterns used by semantic code analyzers like CodeQL. Understanding these patterns helps interpret scanner results and assess vulnerability validity.

## Dataflow Fundamentals

### What is Dataflow Analysis?

**Dataflow analysis** tracks how data moves through a program from sources (input) to sinks (dangerous operations).

**Key Concepts**:
- **Source**: Where untrusted data originates (user input, files, external APIs)
- **Propagation**: How data flows through functions, assignments, transformations
- **Sink**: Where dangerous operations occur (SQL execution, file writes, code eval)
- **Taint**: Label indicating data is untrusted and potentially malicious
- **Sanitization**: Operations that neutralize taint (validation, escaping, encoding)

### Dataflow vs. Pattern Matching

| Pattern Matching (Semgrep) | Dataflow Analysis (CodeQL) |
|----------------------------|----------------------------|
| Searches for code patterns | Tracks data movement |
| Single-file context | Multi-file, inter-procedural |
| Fast, simple | Slower, comprehensive |
| High false positive rate | Lower false positive rate |
| Misses complex flows | Detects complex flows |

**Example**:

**Pattern matching** detects:
```python
# Direct vulnerability
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Dataflow analysis** also detects:
```python
# Indirect vulnerability through function calls
def get_user(request):
    user_id = extract_id(request)  # Source
    return query_user(user_id)

def extract_id(req):
    return req.GET['id']  # Extract from request

def query_user(uid):
    processed = process_id(uid)  # Flow through processing
    return execute_query(processed)

def process_id(data):
    return data.strip()  # Insufficient sanitization

def execute_query(value):
    cursor.execute(f"SELECT * FROM users WHERE id = {value}")  # Sink
    # Dataflow: request.GET → extract_id → query_user → process_id → execute_query
```

## Common Source Types

### 1. HTTP Requests

**User-Controlled Input**:

```python
# Flask
username = request.form['username']
user_id = request.args.get('id')
auth_token = request.headers.get('Authorization')
file_data = request.files['upload']
json_data = request.get_json()['user_input']

# Django
username = request.POST['username']
user_id = request.GET.get('id')
cookie_val = request.COOKIES.get('session')

# FastAPI
async def endpoint(username: str, user_id: int = Query(...)):
    # username and user_id are tainted sources
```

**Why Tainted**: Attacker fully controls these values.

### 2. File Input

**File System Reads**:

```python
# Reading user-uploaded files
with open(user_provided_path, 'r') as f:
    data = f.read()  # data is tainted

# JSON/YAML parsing
import json
config = json.load(open('user_config.json'))  # config is tainted

# CSV parsing
import csv
rows = csv.reader(open('user_data.csv'))  # rows are tainted
```

**Why Tainted**: Attacker may control file contents.

### 3. External APIs

**Third-Party Data**:

```python
# REST API responses
response = requests.get(external_url)
data = response.json()  # data is tainted

# GraphQL
result = gql_client.execute(query)  # result is tainted

# Webhooks
webhook_data = request.get_json()  # webhook_data is tainted
```

**Why Tainted**: External systems may be compromised or malicious.

### 4. Database Queries

**Data from Database**:

```python
# ORM results
user = User.objects.get(id=user_id)
username = user.username  # username is tainted (if stored user input)

# Raw SQL results
cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
result = cursor.fetchone()
username = result[0]  # username is tainted
```

**Why Tainted**: Database may contain attacker-controlled data from previous requests.

### 5. Environment Variables

**System Environment**:

```python
# Environment variables
api_key = os.environ['API_KEY']  # Potentially tainted
config_path = os.getenv('CONFIG_PATH')  # Tainted if user-controlled

# Command-line arguments
import sys
filename = sys.argv[1]  # Tainted
```

**Why Tainted**: May be influenced by attacker in some contexts (containerized apps, etc.).

## Common Propagation Patterns

### 1. Function Arguments

**Direct Pass**:

```python
def process_user(username):  # username tainted if argument is tainted
    return validate_user(username)  # Taint propagates

def validate_user(name):  # name is tainted
    return query_database(name)  # Taint propagates
```

### 2. Return Values

**Function Returns**:

```python
def get_username(request):
    username = request.POST['username']  # username tainted
    return username  # Return value is tainted

# Caller receives tainted data
user = get_username(request)  # user is tainted
```

### 3. Object Fields

**Field Assignment**:

```python
class UserData:
    def __init__(self, request):
        self.username = request.POST['username']  # self.username tainted

data = UserData(request)
username = data.username  # username is tainted
```

### 4. Collections

**Arrays and Dictionaries**:

```python
# List
usernames = [request.POST['username']]  # usernames[0] is tainted

# Dictionary
user_data = {'name': request.POST['username']}  # user_data['name'] is tainted

# Iteration
for username in usernames:  # username is tainted in each iteration
    process(username)
```

### 5. String Operations

**Concatenation and Formatting**:

```python
# Concatenation
username = request.POST['username']  # username tainted
greeting = "Hello, " + username  # greeting is tainted

# String formatting
message = f"User: {username}"  # message is tainted

# Template
from string import Template
tmpl = Template("User: $name")
result = tmpl.substitute(name=username)  # result is tainted
```

### 6. Type Conversions

**Casting and Parsing**:

```python
# Type conversion maintains taint
user_id = request.GET['id']  # user_id tainted (string)
user_id_int = int(user_id)  # user_id_int is tainted (int)

# JSON parsing
json_str = request.body  # json_str tainted
data = json.loads(json_str)  # data is tainted
```

## Common Sink Types

### 1. SQL Execution

**Database Queries**:

```python
# Direct SQL (VULNERABLE)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.executemany(f"INSERT INTO logs VALUES ({value})")

# ORM raw SQL (VULNERABLE)
User.objects.raw(f"SELECT * FROM users WHERE name = '{username}'")

# SQLAlchemy text (VULNERABLE if not parameterized)
from sqlalchemy import text
session.execute(text(f"SELECT * FROM users WHERE id = {user_id}"))
```

**Why Dangerous**: SQL injection can read/modify/delete data, bypass authentication.

### 2. OS Command Execution

**System Commands**:

```python
# Shell execution (VULNERABLE)
os.system(f"ping {hostname}")
os.popen(f"curl {url}")

# Subprocess with shell (VULNERABLE)
subprocess.call(f"ls {directory}", shell=True)
subprocess.run(f"rm {filename}", shell=True)

# Eval-like (VULNERABLE)
eval(user_code)
exec(user_script)
compile(user_code, '<string>', 'exec')
```

**Why Dangerous**: Command injection allows arbitrary system commands, full server compromise.

### 3. File System Operations

**File Paths**:

```python
# File read (VULNERABLE to path traversal)
with open(f"/uploads/{filename}", 'r') as f:
    data = f.read()

# File write (VULNERABLE to arbitrary file write)
with open(f"/logs/{logfile}", 'w') as f:
    f.write(log_data)

# File deletion (VULNERABLE)
os.remove(f"/tmp/{temp_file}")
shutil.rmtree(f"/data/{user_dir}")
```

**Why Dangerous**: Path traversal can read sensitive files (`/etc/passwd`), write to system files.

### 4. Code Evaluation

**Dynamic Code Execution**:

```python
# Eval (VULNERABLE to code injection)
result = eval(user_expression)

# Exec (VULNERABLE)
exec(user_code)

# Import (VULNERABLE)
module = __import__(user_module_name)

# Pickle (VULNERABLE to deserialization attacks)
import pickle
obj = pickle.loads(user_data)
```

**Why Dangerous**: Code injection leads to remote code execution.

### 5. Network Operations

**External Requests**:

```python
# HTTP requests (VULNERABLE to SSRF)
requests.get(user_url)
urllib.request.urlopen(user_url)

# Socket operations (VULNERABLE)
sock.connect((user_host, user_port))
sock.send(user_data)
```

**Why Dangerous**: SSRF can access internal services, exfiltrate data.

### 6. Logging

**Sensitive Data Exposure**:

```python
# Logging user input (VULNERABLE to log injection, sensitive data exposure)
logger.info(f"User {username} logged in")
print(f"Processing: {user_data}")

# If user_data contains secrets, PII, or control characters
```

**Why Dangerous**: Logs may contain secrets, PII, or enable log injection attacks.

### 7. Template Rendering

**Server-Side Template Injection (SSTI)**:

```python
# Jinja2 (VULNERABLE if user controls template)
from jinja2 import Template
tmpl = Template(user_template)
result = tmpl.render(data=user_data)

# Django templates (VULNERABLE if user controls template)
from django.template import Template
tmpl = Template(user_template_string)
result = tmpl.render(context)
```

**Why Dangerous**: SSTI can lead to code execution.

## Sanitization Patterns

### Effective Sanitization

**1. Parameterized Queries (SQL)**:

```python
# SAFE: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# SAFE: ORM query methods
User.objects.filter(id=user_id)

# SAFE: SQLAlchemy bound parameters
from sqlalchemy import text
session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

**Why Safe**: Database driver escapes parameters, preventing SQL injection.

### 2. Allowlist Validation (Path Traversal)

```python
# SAFE: Allowlist validation
def safe_filename(filename):
    # Remove path traversal sequences
    safe_name = os.path.basename(filename)

    # Validate against allowlist
    allowed = ['report.pdf', 'data.csv', 'config.json']
    if safe_name not in allowed:
        raise ValueError("Invalid filename")

    return safe_name
```

**Why Safe**: Only explicitly allowed values are accepted.

### 3. Input Validation (Command Injection)

```python
# SAFE: Strict validation + safe API
def safe_hostname(hostname):
    import re
    # Allowlist: only alphanumeric, dots, hyphens
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        raise ValueError("Invalid hostname")
    return hostname

def ping_host(hostname):
    safe_host = safe_hostname(hostname)
    # Use list arguments (no shell)
    subprocess.run(["ping", "-c", "1", safe_host], check=True)
```

**Why Safe**: Validation prevents injection + list args prevent shell interpretation.

### 4. Escaping (HTML/JS)

```python
# SAFE: HTML escaping
import html
safe_output = html.escape(user_input)

# SAFE: Framework auto-escaping
# Django templates auto-escape by default
{{ user_input }}  # Auto-escaped

# Jinja2 with autoescape
from jinja2 import Environment
env = Environment(autoescape=True)
```

**Why Safe**: Special characters are escaped, preventing XSS.

### Ineffective Sanitization

**1. Insufficient Validation**:

```python
# INSUFFICIENT: Only strips whitespace
username = user_input.strip()
cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
# Still vulnerable to: admin' OR 1=1 --
```

**2. Blacklist Filtering**:

```python
# INSUFFICIENT: Blacklist can be bypassed
def sanitize(user_input):
    return user_input.replace("'", "").replace("--", "")
# Bypasses: " (double quote), /**/ (comment), etc.
```

**3. Partial Escaping**:

```python
# INSUFFICIENT: Only escapes single quotes
username = user_input.replace("'", "\\'")
cursor.execute(f'SELECT * FROM users WHERE name = "{username}"')
# Still vulnerable if query uses double quotes
```

**4. Type Casting Alone**:

```python
# INSUFFICIENT: Type casting doesn't prevent injection
user_id = int(user_input)  # Validates it's an integer
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# Safe from SQL injection but still bad practice (use parameterized queries)
```

## Analyzing Dataflow Validity

### Step-by-Step Analysis

1. **Identify Source**: Is it truly untrusted?
2. **Trace Propagation**: Follow data through each step
3. **Check Sanitization**: Is sanitization effective for the sink type?
4. **Evaluate Sink**: Is the sink genuinely dangerous?
5. **Consider Context**: Are there framework protections?

### Example Analysis

**Scenario**:
```python
# Step 1: Source
username = request.POST['username']  # ✓ Untrusted source

# Step 2: Propagation
clean_username = sanitize_input(username)

# Step 3: Sanitization (CHECK THIS)
def sanitize_input(data):
    return data.replace("'", "''")  # SQL quote escaping

# Step 4: Sink
cursor.execute(f"SELECT * FROM users WHERE name = '{clean_username}'")  # Dangerous sink
```

**Assessment**:
- **Source**: User-controlled (tainted) ✓
- **Sanitization**: Single quote escaping
- **Sink**: String interpolation in SQL
- **Verdict**: VULNERABLE

**Why**: Sanitization escapes single quotes, but:
1. Using f-string instead of parameterized query is inherently unsafe
2. Escaping can be bypassed in some SQL dialects
3. Best practice is parameterized queries, not manual escaping

### Context-Dependent Validity

**Framework Protection Example**:

```python
# Django ORM (SAFE - framework handles escaping)
User.objects.filter(username=user_input)
# Even though user_input is tainted, Django ORM uses parameterized queries

# Django raw SQL (UNSAFE - bypasses ORM protection)
User.objects.raw(f"SELECT * FROM users WHERE username = '{user_input}'")
# Tainted data + raw SQL = vulnerable
```

**Analysis**: Same source, different sinks. Framework protection matters.

## Dataflow Patterns by Vulnerability Type

### SQL Injection

**Pattern**:
```
Source: HTTP request parameter
Propagation: Passed to query building function
Sanitization: None or insufficient escaping
Sink: String concatenation in SQL query
```

**Fix**: Use parameterized queries (see `memory/security/fix-patterns.md`).

### Path Traversal

**Pattern**:
```
Source: User-provided filename
Propagation: Passed to file handling function
Sanitization: None or insufficient (only checks extension)
Sink: Direct use in file path
```

**Fix**: Use `os.path.basename()` + allowlist validation.

### Command Injection

**Pattern**:
```
Source: User-provided hostname/argument
Propagation: Passed to command building function
Sanitization: None or blacklist filtering
Sink: Shell command execution with string interpolation
```

**Fix**: Use subprocess with list arguments (no shell).

### XSS (Cross-Site Scripting)

**Pattern**:
```
Source: User input from form/query param
Propagation: Stored in database or passed to template
Sanitization: None or insufficient escaping
Sink: Direct rendering in HTML without escaping
```

**Fix**: Use framework auto-escaping or `html.escape()`.

### Code Injection

**Pattern**:
```
Source: User-provided expression/code
Propagation: Passed to evaluation function
Sanitization: None or blacklist (ineffective)
Sink: eval(), exec(), compile()
```

**Fix**: Never use eval/exec with user input. Use safe alternatives.

## Multi-Step Dataflow Examples

### Example 1: 5-Step SQL Injection

```python
# Step 1: Source
def login(request):
    username = request.POST['username']  # SOURCE: User input
    return authenticate_user(username)

# Step 2: Propagation
def authenticate_user(name):
    clean_name = validate_username(name)  # Flow to validation
    return find_user(clean_name)

# Step 3: Sanitization (INSUFFICIENT)
def validate_username(username):
    # Only checks length, doesn't sanitize
    if len(username) > 100:
        raise ValueError("Too long")
    return username.strip()  # INSUFFICIENT

# Step 4: Propagation
def find_user(username):
    query = build_query(username)  # Flow to query builder
    return execute_query(query)

# Step 5: Sink
def build_query(username):
    return f"SELECT * FROM users WHERE username = '{username}'"  # SINK

def execute_query(sql):
    cursor.execute(sql)  # Execution
    return cursor.fetchone()
```

**Dataflow**: `request.POST → authenticate_user → validate_username → find_user → build_query → execute_query`

**Vulnerability**: Despite 5 steps, taint propagates because validation is insufficient.

### Example 2: Inter-Module Dataflow

```python
# api/views.py
from utils.validators import validate_input
from database.queries import find_user

def user_endpoint(request):
    user_id = request.GET['id']  # SOURCE
    validated_id = validate_input(user_id)  # Propagation across modules
    return find_user(validated_id)

# utils/validators.py
def validate_input(data):
    return data.strip()  # INSUFFICIENT sanitization

# database/queries.py
def find_user(user_id):
    return User.objects.raw(f"SELECT * FROM users WHERE id = '{user_id}'")  # SINK
```

**Dataflow**: Crosses 3 files/modules. CodeQL detects this; pattern matching might not.

## Best Practices for Dataflow Assessment

1. **Trust the Source Classification**: If CodeQL marks it as a source, it's untrusted.
2. **Read Sanitization Code**: Don't assume functions named "sanitize" are effective.
3. **Validate Against Sink Type**: SQL sanitization doesn't help for command injection.
4. **Consider Framework Protection**: ORMs, template engines may auto-protect.
5. **Assume Propagation**: Taint flows through functions unless explicitly sanitized.
6. **Prefer Safe APIs**: Parameterized queries > escaping, list args > shell.
7. **Document Assumptions**: If marking false positive, explain why.

## References

### Internal Documentation
- `memory/security/cwe-knowledge.md` - CWE descriptions and remediation
- `memory/security/fix-patterns.md` - Language-specific fix patterns
- `memory/security/triage-guidelines.md` - Triage classification rules
- `.claude/skills/security-codeql.md` - CodeQL analysis skill

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Semgrep Rules](https://semgrep.dev/r)

### Academic Papers
- "Precise Interprocedural Dataflow Analysis via Graph Reachability" (Reps et al.)
- "Taint Tracking for Security" (Livshits & Lam)
- "Sound and Precise Analysis of Web Applications for Injection Vulnerabilities" (Tripp et al.)

---

**Last Updated**: 2025-12-04
**Maintained By**: JP Spec Kit Security Team
