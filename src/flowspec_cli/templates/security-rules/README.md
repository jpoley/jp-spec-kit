# Custom Security Rules Templates

This directory contains example Semgrep rules for detecting security vulnerabilities in your codebase. These templates demonstrate best practices for writing custom security rules.

## Quick Start

### 1. Copy Templates to Your Project

```bash
# Create custom rules directory
mkdir -p .flowspec/security/rules

# Copy example rules
cp templates/security-rules/python/*.yml .flowspec/security/rules/
cp templates/security-rules/javascript/*.yml .flowspec/security/rules/
```

### 2. Test the Rules

```bash
# Test against your codebase
semgrep --config .flowspec/security/rules/ src/

# Validate rule syntax
semgrep --validate --config .flowspec/security/rules/

# Run rule tests
semgrep --test .flowspec/security/rules/
```

### 3. Integrate with flowspec

Add to your security configuration:

```yaml
# .flowspec/security.yml
scanners:
  semgrep:
    enabled: true
    config:
      - auto  # OWASP Top 10 rules
      - .flowspec/security/rules/  # Your custom rules
```

## Available Templates

### Python Rules

**`python/example-sql-injection.yml`**
- Detects SQL injection via string concatenation
- Detects `.format()` and `%` string formatting in queries
- Demonstrates parameterized query alternatives

**Example vulnerabilities detected:**
```python
# Dangerous - will be flagged
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE name = " + username)

# Safe - will NOT be flagged
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### JavaScript/TypeScript Rules

**`javascript/example-xss.yml`**
- Detects XSS via `innerHTML` and `outerHTML`
- Detects `insertAdjacentHTML` with unsanitized data
- Detects React `dangerouslySetInnerHTML`
- Detects `eval()` and `Function()` constructor misuse

**Example vulnerabilities detected:**
```javascript
// Dangerous - will be flagged
element.innerHTML = userInput;
<div dangerouslySetInnerHTML={{__html: userContent}} />
eval(userCode);

// Safe - will NOT be flagged
element.textContent = userInput;
<div>{userContent}</div>
element.innerHTML = DOMPurify.sanitize(userInput);
```

## Customizing Rules

### Rule Structure

```yaml
rules:
  - id: unique-rule-id           # Unique identifier
    patterns:                     # Pattern matching logic
      - pattern: dangerous($X)
      - pattern-not: safe($X)
    message: "Description"        # User-facing message
    severity: ERROR               # ERROR, WARNING, or INFO
    languages:                    # Supported languages
      - python
    metadata:                     # Additional information
      cwe: "CWE-XXX"
      owasp: "AXX:2021"
      remediation: "How to fix"
```

### Pattern Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `pattern` | Exact match | `eval($X)` |
| `pattern-either` | Match any (OR) | Multiple dangerous functions |
| `pattern-not` | Exclude pattern | Filter false positives |
| `pattern-inside` | Match within context | Only in specific functions |
| `metavariable-pattern` | Pattern on captured variable | Check if variable is tainted |

### Common Customizations

**1. Framework-Specific Rules**

Adapt patterns to your framework:

```yaml
# Django ORM SQL injection
- id: django-sql-injection
  patterns:
    - pattern-either:
        - pattern: Model.objects.raw($QUERY)
        - pattern: Model.objects.extra(where=[$QUERY])
    - metavariable-pattern:
        metavariable: $QUERY
        pattern: $X + $Y
  message: "Django raw SQL with string concatenation"
```

**2. Organization-Specific Patterns**

Add rules for your internal APIs:

```yaml
# Company-specific dangerous function
- id: company-legacy-api-usage
  pattern: CompanyLegacyAPI.unsafe_method($ARG)
  message: "Use CompanySecureAPI instead"
  severity: WARNING
```

**3. Reduce False Positives**

Add `pattern-not` clauses for safe patterns:

```yaml
rules:
  - id: my-rule
    patterns:
      - pattern: dangerous($X)
      # Exclude test files
      - pattern-not-inside: |
          def test_$FUNC(...):
            ...
    paths:
      exclude:
        - "**/test_*.py"
        - "**/tests/**"
```

## Testing Custom Rules

### Create Test Cases

Add test cases directly in your rule file:

```yaml
rules:
  - id: my-rule
    # ... rule definition ...

---
# Test cases (detected by semgrep --test)

# ruleid: my-rule
vulnerable_code_here()

# ok: my-rule
safe_code_here()
```

### Run Tests

```bash
# Run all tests in rules directory
semgrep --test .flowspec/security/rules/

# Test specific rule
semgrep --test .flowspec/security/rules/my-rule.yml

# Verbose output
semgrep --test .flowspec/security/rules/ --verbose
```

### Validate Rules

```bash
# Check syntax
semgrep --validate --config .flowspec/security/rules/

# Test against real code
semgrep --config .flowspec/security/rules/ src/ --verbose
```

## Best Practices

### 1. Start Specific, Then Generalize

```yaml
# Too broad - many false positives
pattern: $X + $Y

# Better - scoped to dangerous context
patterns:
  - pattern: cursor.execute($X + $Y)
```

### 2. Include Clear Messages

```yaml
message: |
  SQL injection via string concatenation.
  Use parameterized queries: cursor.execute("... WHERE id = ?", (id,))
```

### 3. Add Metadata for Reporting

```yaml
metadata:
  cwe: "CWE-89"
  owasp: "A03:2021"
  category: security
  confidence: HIGH
  remediation: |
    Code example showing the fix
  references:
    - https://owasp.org/...
```

### 4. Use Semantic Versioning

```yaml
# version: 1.0.0
# changelog:
#   - 1.0.0: Initial rule
#   - 1.1.0: Added support for Framework X
```

### 5. Test Thoroughly

- Create positive test cases (should match)
- Create negative test cases (should NOT match)
- Test on real codebase before deploying
- Review with security team

## Rule Organization

### By Language

```
.flowspec/security/rules/
├── python/
│   ├── sql-injection.yml
│   ├── command-injection.yml
│   └── hardcoded-secrets.yml
├── javascript/
│   ├── xss.yml
│   ├── prototype-pollution.yml
│   └── insecure-deserialization.yml
└── go/
    ├── sql-injection.yml
    └── race-conditions.yml
```

### By Vulnerability Type

```
.flowspec/security/rules/
├── injection/
│   ├── sql-injection.yml
│   ├── command-injection.yml
│   └── ldap-injection.yml
├── authentication/
│   ├── weak-passwords.yml
│   └── session-fixation.yml
└── cryptography/
    ├── weak-hashing.yml
    └── insecure-random.yml
```

## Common Rule Patterns

### Dangerous Functions

```yaml
rules:
  - id: dangerous-functions
    pattern-either:
      - pattern: eval($X)
      - pattern: exec($X)
      - pattern: compile($X, ...)
    message: "Dangerous code execution function"
    severity: ERROR
```

### Hardcoded Credentials

```yaml
rules:
  - id: hardcoded-secrets
    patterns:
      - pattern-either:
          - pattern: password = "..."
          - pattern: api_key = "..."
      - pattern-not: $VAR = ""
      - pattern-not: $VAR = os.environ[...]
    message: "Hardcoded secret detected"
    severity: ERROR
```

### Insecure Configuration

```yaml
rules:
  - id: insecure-config
    pattern: app.run(..., debug=True, ...)
    message: "Debug mode enabled in production"
    severity: ERROR
    paths:
      exclude:
        - "**/test_*.py"
```

## Troubleshooting

### Rule Not Matching

```bash
# Debug with verbose output
semgrep --config rule.yml file.py --verbose

# Check pattern syntax
semgrep --validate --config rule.yml

# Test incrementally - start simple, add complexity
```

### Too Many False Positives

1. Add `pattern-not` clauses
2. Use `paths.exclude` for test files
3. Add `pattern-inside` for context
4. Use `metavariable-pattern` for constraints

### Performance Issues

1. Use specific file types in `languages`
2. Use `paths.include` to limit scope
3. Avoid overly broad regex patterns

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    semgrep --config auto \
            --config .flowspec/security/rules/ \
            --sarif -o semgrep.sarif

- name: Upload Results
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: semgrep.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/returntocorp/semgrep
    rev: 'v1.45.0'
    hooks:
      - id: semgrep
        args:
          - --config=auto
          - --config=.flowspec/security/rules/
          - --error
```

## Additional Resources

- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax/)
- [Semgrep Rule Examples](https://semgrep.dev/r)
- [Custom Security Rules Guide](../../docs/guides/security-custom-rules.md)
- [OWASP Top 10](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## Contributing

To add new template rules:

1. Create rule file in appropriate language directory
2. Include comprehensive test cases
3. Add metadata (CWE, OWASP, remediation)
4. Test thoroughly against real code
5. Document in this README

## License

These templates are provided as-is for educational and security testing purposes. Customize them for your organization's specific needs.
