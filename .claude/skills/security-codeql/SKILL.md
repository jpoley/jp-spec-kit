# CodeQL Analysis Skill

## Purpose

This skill enables Claude Code to interpret CodeQL SARIF output, understand complex dataflow paths, assess vulnerability severity, and provide expert remediation guidance based on semantic code analysis.

## When to Use This Skill

- When analyzing CodeQL SARIF output files
- When user runs `/flow:security_scan --scanner codeql`
- When interpreting dataflow analysis results
- When providing deep semantic analysis of vulnerabilities
- When validating complex taint tracking across functions

## CodeQL Fundamentals

### What Makes CodeQL Different

CodeQL performs **semantic analysis** through:

1. **Database-Driven**: Converts code to queryable database
2. **Dataflow Tracking**: Follows data from source to sink across functions
3. **Taint Propagation**: Tracks how untrusted data spreads through code
4. **Control Flow**: Understands program execution paths
5. **Inter-procedural**: Analyzes across function/method boundaries

**Example**: CodeQL can detect SQL injection even when:
- User input flows through 5 helper functions
- Data is transformed along the way
- Validation happens but is insufficient
- Framework APIs are involved

### CodeQL vs. Pattern Matching

**Semgrep** (pattern matching):
```python
# Detects: Direct string concat in SQL
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**CodeQL** (dataflow analysis):
```python
# Detects: SQL injection across function boundaries
def get_user(request):
    user_id = request.GET['id']  # SOURCE
    return fetch_user_data(user_id)

def fetch_user_data(uid):
    processed_id = process_input(uid)  # PROPAGATION
    return query_database(processed_id)

def process_input(data):
    return data.strip()  # INSUFFICIENT SANITIZATION

def query_database(value):
    cursor.execute(f"SELECT * FROM users WHERE id = {value}")  # SINK
    # CodeQL tracks: request.GET -> user_id -> uid -> data -> value -> SQL
```

## Input: SARIF Format

CodeQL outputs SARIF (Static Analysis Results Interchange Format):

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "CodeQL",
          "version": "2.15.0"
        }
      },
      "results": [
        {
          "ruleId": "py/sql-injection",
          "ruleIndex": 0,
          "rule": {
            "id": "py/sql-injection",
            "name": "py/sql-injection"
          },
          "level": "error",
          "message": {
            "text": "This query depends on a user-provided value."
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/database/queries.py",
                  "uriBaseId": "%SRCROOT%"
                },
                "region": {
                  "startLine": 142,
                  "startColumn": 5,
                  "endLine": 142,
                  "endColumn": 50
                }
              }
            }
          ],
          "codeFlows": [
            {
              "threadFlows": [
                {
                  "locations": [
                    {
                      "location": {
                        "physicalLocation": {
                          "artifactLocation": {
                            "uri": "src/api/views.py"
                          },
                          "region": {
                            "startLine": 28,
                            "startColumn": 15
                          }
                        },
                        "message": {
                          "text": "user input (source)"
                        }
                      }
                    },
                    {
                      "location": {
                        "physicalLocation": {
                          "artifactLocation": {
                            "uri": "src/utils/validators.py"
                          },
                          "region": {
                            "startLine": 55,
                            "startColumn": 12
                          }
                        },
                        "message": {
                          "text": "data flows through validation"
                        }
                      }
                    },
                    {
                      "location": {
                        "physicalLocation": {
                          "artifactLocation": {
                            "uri": "src/database/queries.py"
                          },
                          "region": {
                            "startLine": 142,
                            "startColumn": 5
                          }
                        },
                        "message": {
                          "text": "SQL query execution (sink)"
                        }
                      }
                    }
                  ]
                }
              ]
            }
          ],
          "relatedLocations": [
            {
              "id": 1,
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/api/views.py"
                },
                "region": {
                  "startLine": 28,
                  "startColumn": 15
                }
              },
              "message": {
                "text": "User input originates here"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Analysis Process

### Step 1: Read SARIF Output

CodeQL SARIF files are located at:
- Default: `results.sarif` (from CodeQL CLI)
- flowspec: `docs/security/codeql-results.sarif`

```python
# Read SARIF file
sarif_path = "docs/security/codeql-results.sarif"
```

### Step 2: Extract Dataflow Paths

The most valuable CodeQL feature is `codeFlows` - the dataflow path from source to sink.

**Parse dataflow**:
1. Extract `threadFlows[0].locations`
2. For each location:
   - File and line number
   - Code snippet
   - Message describing the flow step
3. Identify:
   - **Source**: Where untrusted data originates
   - **Propagation**: How data flows through functions
   - **Sink**: Where dangerous operation occurs

**Example dataflow extraction**:
```python
dataflow = []
for flow_step in result["codeFlows"][0]["threadFlows"][0]["locations"]:
    location = flow_step["location"]["physicalLocation"]
    dataflow.append({
        "file": location["artifactLocation"]["uri"],
        "line": location["region"]["startLine"],
        "message": flow_step["location"]["message"]["text"],
        "step_type": classify_step_type(flow_step)  # source/propagation/sink
    })
```

### Step 3: Classify Vulnerability Type

Map `ruleId` to CWE and vulnerability class:

| CodeQL Rule ID | CWE | Vulnerability Type |
|----------------|-----|-------------------|
| `py/sql-injection` | CWE-89 | SQL Injection |
| `py/path-injection` | CWE-22 | Path Traversal |
| `py/command-injection` | CWE-78 | OS Command Injection |
| `py/code-injection` | CWE-94 | Code Injection |
| `py/xxe` | CWE-611 | XML External Entity (XXE) |
| `py/xpath-injection` | CWE-643 | XPath Injection |
| `py/ldap-injection` | CWE-90 | LDAP Injection |
| `py/weak-cryptographic-algorithm` | CWE-327 | Weak Crypto |
| `py/hardcoded-credentials` | CWE-798 | Hardcoded Credentials |
| `py/clear-text-logging-sensitive-data` | CWE-532 | Sensitive Data Logging |

Reference `memory/security/cwe-knowledge.md` for detailed CWE information.

### Step 4: Assess Dataflow Validity

Not all CodeQL findings are true positives. Evaluate the dataflow:

**TRUE POSITIVE indicators**:
- Source is truly untrusted (user input, external API, file)
- No sanitization between source and sink
- Sink is genuinely dangerous (SQL exec, file write, eval)
- Dataflow path is realistic and feasible

**FALSE POSITIVE indicators**:
- Proper validation/sanitization in dataflow
- Framework provides automatic protection
- Whitelisting/allowlisting applied
- Type constraints prevent exploitation

**Example analysis**:
```python
def is_sanitized_in_flow(dataflow):
    """Check if dataflow passes through sanitization"""
    sanitization_keywords = [
        "sanitize", "escape", "validate", "whitelist",
        "parameterized", "prepared", "quote"
    ]

    for step in dataflow:
        message = step["message"].lower()
        if any(keyword in message for keyword in sanitization_keywords):
            # Read the actual code to verify sanitization is effective
            return check_sanitization_effectiveness(step)

    return False
```

### Step 5: Severity Assessment

CodeQL provides `level` field:
- `error` → HIGH or CRITICAL severity
- `warning` → MEDIUM severity
- `note` → LOW severity

**Refine based on context**:
- Upgrade to CRITICAL if:
  - Authentication bypass
  - Remote code execution
  - Data exfiltration at scale
  - Admin functionality compromised

- Downgrade to MEDIUM if:
  - Requires authentication
  - Limited impact scope
  - Difficult to exploit

### Step 6: Generate Remediation

Provide **code-specific** remediation based on:
1. The vulnerable sink (SQL, file, command, etc.)
2. The programming language and framework
3. The dataflow path

**Remediation patterns** (reference `memory/security/fix-patterns.md`):

**SQL Injection**:
```python
# VULNERABLE (CodeQL detected this pattern)
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

# FIXED: Use parameterized queries
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
```

**Path Traversal**:
```python
# VULNERABLE
def read_file(filename):
    path = f"/uploads/{filename}"
    with open(path, 'r') as f:
        return f.read()

# FIXED: Validate against allowlist + sanitize
def read_file(filename):
    # Remove path traversal sequences
    safe_name = os.path.basename(filename)

    # Validate against allowlist
    allowed_extensions = ['.jpg', '.png', '.pdf']
    if not any(safe_name.endswith(ext) for ext in allowed_extensions):
        raise ValueError("Invalid file type")

    # Use safe path join
    path = os.path.join("/uploads", safe_name)

    # Verify path stays within upload directory
    if not os.path.abspath(path).startswith("/uploads"):
        raise ValueError("Path traversal detected")

    with open(path, 'r') as f:
        return f.read()
```

**Command Injection**:
```python
# VULNERABLE
def ping_host(hostname):
    os.system(f"ping -c 1 {hostname}")

# FIXED: Use subprocess with list arguments
def ping_host(hostname):
    # Validate hostname format
    import re
    if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
        raise ValueError("Invalid hostname")

    # Use list arguments (no shell)
    subprocess.run(["ping", "-c", "1", hostname], check=True)
```

### Step 7: Explain Dataflow Path

Generate clear explanation of how data flows from source to sink:

**Template**:
```
Dataflow Path:
1. User input originates at {source_file}:{source_line}
   → {source_code_snippet}

2. Data flows through {intermediate_function} at {file}:{line}
   → {transformation_description}

3. [Repeat for each propagation step]

4. Dangerous operation at {sink_file}:{sink_line}
   → {sink_code_snippet}
   → {why_dangerous}

Why This Is Exploitable:
{exploitation_explanation}

Attack Scenario:
{concrete_attack_example}
```

**Example**:
```
Dataflow Path:
1. User input originates at src/api/views.py:28
   → username = request.POST['username']
   → Untrusted user input from HTTP request

2. Data flows through src/utils/validators.py:55
   → clean_username = username.strip()
   → Only whitespace trimming - INSUFFICIENT sanitization

3. Data flows through src/database/queries.py:142
   → cursor.execute(f"SELECT * FROM users WHERE username = '{clean_username}'")
   → Direct string interpolation into SQL query

Why This Is Exploitable:
The validation only removes whitespace, but does not prevent SQL metacharacters.
An attacker can inject SQL commands through the username parameter.

Attack Scenario:
POST /login with username=' OR 1=1 --
Results in query: SELECT * FROM users WHERE username='' OR 1=1 --'
The OR 1=1 bypasses authentication, -- comments out the rest of the query.
```

## Output: UFFormat with Dataflow

Convert CodeQL SARIF to UFFormat, preserving dataflow information:

```json
{
  "id": "CODEQL-CWE-89-001",
  "scanner": "codeql",
  "rule_id": "py/sql-injection",
  "severity": "high",
  "confidence": 0.95,
  "title": "SQL Injection via user input in authentication query",
  "description": "User input from HTTP request flows through insufficient validation to SQL query execution",
  "location": {
    "file": "src/database/queries.py",
    "line_start": 142,
    "line_end": 142,
    "code_snippet": "cursor.execute(f\"SELECT * FROM users WHERE username = '{clean_username}'\")"
  },
  "cwe_id": "CWE-89",
  "cwe_name": "SQL Injection",
  "cvss_score": 9.8,
  "dataflow": [
    {
      "step": 1,
      "type": "source",
      "location": {
        "file": "src/api/views.py",
        "line": 28,
        "snippet": "username = request.POST['username']"
      },
      "description": "Untrusted user input from HTTP POST request",
      "taint_label": "user_controlled"
    },
    {
      "step": 2,
      "type": "propagation",
      "location": {
        "file": "src/utils/validators.py",
        "line": 55,
        "snippet": "clean_username = username.strip()"
      },
      "description": "Data flows through whitespace removal - insufficient sanitization",
      "taint_label": "user_controlled"
    },
    {
      "step": 3,
      "type": "sink",
      "location": {
        "file": "src/database/queries.py",
        "line": 142,
        "snippet": "cursor.execute(f\"SELECT * FROM users WHERE username = '{clean_username}'\")"
      },
      "description": "Tainted data reaches SQL execution sink",
      "taint_label": "sql_injection_sink"
    }
  ],
  "dataflow_summary": "User input → strip() → SQL query (3 steps)",
  "exploitation": {
    "attack_vector": "HTTP POST parameter",
    "payload_example": "' OR 1=1 --",
    "impact": "Authentication bypass, full database access",
    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
  },
  "remediation": {
    "fix_type": "parameterized_query",
    "description": "Use parameterized queries to prevent SQL injection",
    "code_example": "cursor.execute('SELECT * FROM users WHERE username = ?', (clean_username,))",
    "references": [
      "https://cwe.mitre.org/data/definitions/89.html",
      "https://owasp.org/www-community/attacks/SQL_Injection",
      "https://codeql.github.com/codeql-query-help/python/py-sql-injection/"
    ]
  },
  "metadata": {
    "codeql_version": "2.15.0",
    "query_id": "py/sql-injection",
    "query_name": "SQL query built from user-controlled sources",
    "query_severity": "error",
    "scan_timestamp": "2025-12-04T10:30:00Z"
  }
}
```

## Dataflow Analysis Patterns

Reference `memory/security/dataflow-analysis.md` for common patterns:

### Source Types

- **User Input**: `request.POST`, `request.GET`, `request.body`
- **File Input**: `open()`, `read()`, `json.load()`
- **External API**: `requests.get()`, `urllib.request()`
- **Database**: `cursor.fetchone()`, `query.all()`
- **Environment**: `os.environ`, `sys.argv`

### Propagation Types

- **Function Call**: Data passed as argument
- **Return Value**: Data returned from function
- **Field Assignment**: Data stored in object field
- **Array/Dict**: Data stored in collection
- **String Operation**: Concatenation, formatting

### Sink Types

- **SQL**: `execute()`, `executemany()`, `raw()`
- **OS Command**: `os.system()`, `subprocess.call()`
- **File System**: `open()`, `os.remove()`, `shutil.rmtree()`
- **Code Execution**: `eval()`, `exec()`, `compile()`
- **Network**: `socket.send()`, `requests.post()`
- **Logging**: `logger.info()`, `print()` (if sensitive)

## Interpreting CodeQL Confidence

CodeQL findings generally have HIGH confidence because:
1. Dataflow is proven (not pattern-based)
2. Inter-procedural analysis confirms the path
3. Type system validates data types

**Assign confidence**:
- **0.95-1.0**: Full dataflow path with no sanitization
- **0.85-0.94**: Dataflow path but ambiguous sanitization
- **0.70-0.84**: Partial dataflow or framework may mitigate
- **<0.70**: Mark as NEEDS_INVESTIGATION

## Handling Complex Dataflows

### Multi-Step Flows (5+ steps)

For complex flows, summarize key points:

```
Dataflow Summary:
Source: HTTP request → user_id parameter
Path: request → validate_uuid() → fetch_user() → build_query() → execute_raw_sql()
Steps: 5 function calls
Sanitization: UUID validation only (insufficient for SQL)
Sink: Raw SQL execution with string formatting
Result: SQL Injection despite UUID validation
```

### Conditional Flows

CodeQL may show multiple paths. Evaluate each:

```python
def process_data(user_input):
    if is_admin():
        # Path 1: Admin flow (no validation)
        return execute_query(user_input)  # VULNERABLE
    else:
        # Path 2: User flow (validated)
        validated = sanitize(user_input)
        return execute_query(validated)   # SAFE
```

**Analysis**: Mark as TP if ANY path is vulnerable.

### Framework Magic

CodeQL understands framework protections:

```python
# Django ORM (SAFE - CodeQL knows this is parameterized)
User.objects.filter(username=user_input)

# Django raw SQL (VULNERABLE - CodeQL detects this)
User.objects.raw(f"SELECT * FROM users WHERE username = '{user_input}'")
```

## Integration with Security Triage

After converting CodeQL SARIF to UFFormat:

1. **Invoke security-triage skill** to classify findings
2. Triage will:
   - Read dataflow paths
   - Assess sanitization effectiveness
   - Calculate risk scores
   - Generate explanations
3. Dataflow information enhances triage accuracy

**Example**:
```markdown
# In security triage skill

if finding["scanner"] == "codeql":
    # CodeQL provides high-quality dataflow
    dataflow = finding["dataflow"]

    # Check for sanitization in dataflow
    is_sanitized = any(
        "sanitize" in step["description"].lower() or
        "validate" in step["description"].lower()
        for step in dataflow
    )

    if is_sanitized:
        # Read actual sanitization code to verify
        confidence = verify_sanitization_effectiveness(dataflow)
    else:
        # No sanitization in flow → high confidence TP
        confidence = 0.95
```

## Success Criteria

- Parse all CodeQL SARIF findings correctly
- Extract and preserve complete dataflow paths
- Map CodeQL rule IDs to CWEs accurately
- Assess dataflow validity (sanitization checks)
- Provide code-specific remediation with examples
- Convert to UFFormat with dataflow preservation
- Generate clear, educational explanations of dataflow
- Integrate with security triage for risk scoring

## Example Workflow

```bash
# User runs CodeQL scan
specify security scan --scanner codeql --language python

# You execute:
1. Read docs/security/codeql-results.sarif
2. For each SARIF result:
   a. Extract dataflow path from codeFlows
   b. Classify source, propagation, sink
   c. Map ruleId to CWE
   d. Assess dataflow validity
   e. Generate remediation with code examples
   f. Create UFFormat finding with dataflow
3. Write to docs/security/findings.json
4. Invoke security-triage skill for classification
5. Report summary with dataflow insights
```

## Knowledge Base

Reference these files for deep analysis:

- `memory/security/dataflow-analysis.md` - Dataflow patterns and analysis techniques
- `memory/security/cwe-knowledge.md` - CWE descriptions and remediation
- `memory/security/fix-patterns.md` - Language-specific fix patterns
- `docs/guides/codeql-setup.md` - CodeQL setup and configuration
- `docs/legal/codeql-licensing-review.md` - Licensing compliance

## Notes

- This is a SKILL, not Python code. You (Claude Code) execute the logic.
- CodeQL provides the highest-quality dataflow information of any scanner.
- Preserve dataflow paths in UFFormat - they're the most valuable information.
- Use Read tool to examine actual code for sanitization validation.
- Apply semantic understanding to assess whether sanitization is sufficient.
- Reference CWE knowledge base for vulnerability-specific remediation.
- Explain dataflow in clear, educational language for developers.

## Advanced: Custom CodeQL Queries

If user requests custom query analysis:

1. Read the `.ql` query file
2. Understand the query logic:
   - Source definitions
   - Sink definitions
   - Dataflow configuration
3. Interpret results in context of custom query
4. Document custom query in finding metadata

**Example**:
```ql
// Custom query: API key exposure
import python
import semmle.python.dataflow.TaintTracking

class ApiKeyExposure extends TaintTracking::Configuration {
  ApiKeyExposure() { this = "ApiKeyExposure" }

  override predicate isSource(DataFlow::Node source) {
    // Source: Environment variable access
    exists(Call c | c.getFunc().(Attribute).getName() = "get" and
                    c.getArg(0).(StringLiteral).getText() = "API_KEY" and
                    source.asExpr() = c)
  }

  override predicate isSink(DataFlow::Node sink) {
    // Sink: HTTP request headers
    exists(Call c | c.getFunc().(Attribute).getName() = "post" and
                    sink.asExpr() = c.getArgByName("headers"))
  }
}
```

**Interpret**: This query tracks API keys from environment variables to HTTP headers, detecting potential credential exposure in logs or error messages.
