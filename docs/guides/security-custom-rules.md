# Custom Security Rules Guide

This guide explains how to create custom security rules for `/flow:security` scanning.

## Overview

Custom rules allow you to:
- Detect organization-specific vulnerability patterns
- Enforce internal coding standards
- Add checks for proprietary frameworks
- Reduce false positives with context-aware rules

## Rule Formats

### Semgrep Rules (Recommended)

Semgrep rules are YAML-based pattern matching rules.

**Location**: `.specify/security/rules/` or `.semgrep/`

**Example**: Detect hardcoded AWS keys

```yaml
# .specify/security/rules/aws-keys.yml
rules:
  - id: hardcoded-aws-access-key
    pattern: AKIA[A-Z0-9]{16}
    message: "Hardcoded AWS access key detected"
    severity: ERROR
    languages:
      - generic
    metadata:
      cwe: "CWE-798"
      owasp: "A07:2021"
      category: security

  - id: hardcoded-aws-secret-key
    pattern-regex: "['\"][A-Za-z0-9/+=]{40}['\"]"
    message: "Possible hardcoded AWS secret key"
    severity: WARNING
    languages:
      - generic
    metadata:
      cwe: "CWE-798"
```

### Bandit Rules (Python)

Bandit plugins are Python modules that extend the scanner.

**Location**: `.specify/security/bandit/`

**Example**: Detect unsafe deserialization

```python
# .specify/security/bandit/unsafe_yaml.py
import bandit
from bandit.core import issue
from bandit.core import test_properties as test

@test.checks('Call')
@test.test_id('B506')
def unsafe_yaml_load(context):
    """Detect yaml.load without SafeLoader."""
    if context.call_function_name_qual == 'yaml.load':
        if not context.check_call_arg_value('Loader', 'SafeLoader'):
            return bandit.Issue(
                severity=bandit.HIGH,
                confidence=bandit.HIGH,
                text="yaml.load() called without SafeLoader",
                cwe=issue.Cwe.DESERIALIZATION_OF_UNTRUSTED_DATA
            )
```

## Creating Semgrep Rules

### Basic Pattern Matching

```yaml
rules:
  - id: my-rule-id
    pattern: dangerous_function($ARG)
    message: "Avoid using dangerous_function"
    severity: WARNING
    languages:
      - python
```

### Pattern Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `pattern` | Exact match | `eval($X)` |
| `pattern-regex` | Regex match | `password\s*=\s*['\"]` |
| `pattern-either` | OR patterns | Multiple patterns |
| `pattern-not` | Exclude pattern | Filter false positives |
| `pattern-inside` | Context match | Match within function |
| `pattern-not-inside` | Exclude context | Exclude safe contexts |

### Example: Complex Rule

```yaml
rules:
  - id: flask-sql-injection
    patterns:
      - pattern-either:
          - pattern: cursor.execute($QUERY)
          - pattern: db.execute($QUERY)
      - pattern-not:
          - pattern: cursor.execute("...", $PARAMS)
      - metavariable-pattern:
          metavariable: $QUERY
          patterns:
            - pattern-either:
                - pattern: $X + $Y
                - pattern: f"..."
                - pattern: "...".format(...)
    message: |
      SQL query constructed with string concatenation or formatting.
      Use parameterized queries instead.
    severity: ERROR
    languages:
      - python
    metadata:
      cwe: "CWE-89"
      owasp: "A03:2021"
      remediation: |
        Use parameterized queries:
        ```python
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        ```
```

### Metavariables

Metavariables capture code elements for analysis:

| Metavariable | Description |
|--------------|-------------|
| `$X` | Any expression |
| `$...X` | Multiple expressions |
| `$_` | Any single item (ignore) |

```yaml
rules:
  - id: insecure-random
    pattern: random.random()
    message: "Use secrets module for security-sensitive randomness"
    severity: WARNING
    languages:
      - python
    fix: secrets.token_hex(16)
```

## Rule Configuration

### Enable Custom Rules

```yaml
# .specify/security.yml
scanners:
  semgrep:
    enabled: true
    config:
      - auto  # OWASP ruleset
      - .specify/security/rules/  # Custom rules
    exclude_rules:
      - generic.secrets.security.detected-generic-api-key
```

### Rule Priority

Rules are applied in order:
1. Built-in rules (auto)
2. Custom rules (.specify/security/rules/)
3. Exclusions applied last

## Testing Custom Rules

### Using Semgrep CLI

```bash
# Test rule against file
semgrep --config .specify/security/rules/my-rule.yml src/

# Test with verbose output
semgrep --config .specify/security/rules/my-rule.yml src/ --verbose

# Validate rule syntax
semgrep --validate --config .specify/security/rules/my-rule.yml
```

### Creating Test Cases

```yaml
# .specify/security/rules/my-rule.yml
rules:
  - id: unsafe-eval
    pattern: eval($X)
    message: "Avoid eval()"
    severity: ERROR
    languages:
      - python

# Test file: .specify/security/rules/my-rule.test.py
# ruleid: unsafe-eval
eval(user_input)

# ok: unsafe-eval
ast.literal_eval(safe_input)
```

Run tests:

```bash
semgrep --test .specify/security/rules/
```

## Common Rule Patterns

### 1. Detect Dangerous Functions

```yaml
rules:
  - id: dangerous-exec
    pattern-either:
      - pattern: exec($X)
      - pattern: eval($X)
      - pattern: compile($X, ...)
    message: "Dangerous code execution function"
    severity: ERROR
    languages:
      - python
```

### 2. Detect Insecure Configuration

```yaml
rules:
  - id: flask-debug-true
    pattern: app.run(..., debug=True, ...)
    message: "Flask debug mode enabled in production"
    severity: ERROR
    languages:
      - python
    paths:
      exclude:
        - "**/test_*.py"
        - "**/tests/**"
```

### 3. Detect Missing Security Headers

```yaml
rules:
  - id: missing-csrf-protection
    patterns:
      - pattern: |
          @app.route(...)
          def $FUNC(...):
            ...
      - pattern-not-inside: |
          @csrf.exempt
          ...
      - pattern-not-inside: |
          csrf_token()
          ...
    message: "Route handler may be missing CSRF protection"
    severity: WARNING
    languages:
      - python
```

### 4. Detect Hardcoded Credentials

```yaml
rules:
  - id: hardcoded-password
    patterns:
      - pattern-either:
          - pattern: password = "..."
          - pattern: PASSWORD = "..."
          - pattern: secret = "..."
      - pattern-not: password = ""
      - pattern-not: password = os.environ[...]
    message: "Hardcoded password detected"
    severity: ERROR
    languages:
      - python
```

### 5. Detect SQL Injection (Framework-Specific)

```yaml
rules:
  - id: django-raw-sql-injection
    patterns:
      - pattern-either:
          - pattern: Model.objects.raw($QUERY)
          - pattern: connection.cursor().execute($QUERY)
      - metavariable-pattern:
          metavariable: $QUERY
          pattern-either:
            - pattern: $X + $Y
            - pattern: f"..."
            - pattern: "...".format(...)
    message: "Django raw SQL with string interpolation"
    severity: ERROR
    languages:
      - python
```

## Integrating with flowspec

### Custom Rule Workflow

1. **Create rule file**:
   ```bash
   mkdir -p .specify/security/rules
   vim .specify/security/rules/company-rules.yml
   ```

2. **Test locally**:
   ```bash
   specify security scan --config .specify/security/rules/
   ```

3. **Add to configuration**:
   ```yaml
   # .specify/security.yml
   scanners:
     semgrep:
       config:
         - auto
         - .specify/security/rules/
   ```

4. **Commit and use**:
   ```bash
   git add .specify/security/rules/
   git commit -m "Add custom security rules"
   specify security scan
   ```

## Rule Metadata

Include metadata for better reporting:

```yaml
rules:
  - id: my-rule
    metadata:
      # OWASP mapping
      owasp: "A03:2021"

      # CWE identifier
      cwe: "CWE-89"

      # Category for grouping
      category: security

      # Confidence level
      confidence: HIGH

      # Technology tags
      technology:
        - flask
        - python

      # Remediation guidance
      remediation: |
        Use parameterized queries instead of string concatenation.

      # References
      references:
        - https://owasp.org/Top10/A03_2021-Injection/
```

## Best Practices

### 1. Start Specific

Begin with specific patterns, then generalize:

```yaml
# Too broad - many false positives
pattern: $X + $Y

# Better - scoped to SQL context
patterns:
  - pattern: cursor.execute($X + $Y)
```

### 2. Use Pattern-Not for False Positives

```yaml
patterns:
  - pattern: yaml.load($X)
  - pattern-not: yaml.load($X, Loader=yaml.SafeLoader)
```

### 3. Include Fix Suggestions

```yaml
rules:
  - id: md5-usage
    pattern: hashlib.md5($X)
    message: "MD5 is cryptographically weak"
    fix: hashlib.sha256($X)
```

### 4. Test Thoroughly

- Create positive test cases (should match)
- Create negative test cases (should not match)
- Test on real codebase before deploying

### 5. Document Rules

```yaml
rules:
  - id: company-specific-rule
    message: |
      ## Issue
      Description of the security issue.

      ## Impact
      What could happen if exploited.

      ## Remediation
      How to fix it.
```

## Troubleshooting

### Rule Not Matching

```bash
# Debug with verbose output
semgrep --verbose --config rule.yml file.py

# Check pattern syntax
semgrep --validate --config rule.yml
```

### Too Many False Positives

1. Add `pattern-not` clauses
2. Use `paths.exclude` for test files
3. Add `pattern-inside` for context

### Performance Issues

1. Use specific file types in `languages`
2. Avoid overly broad regex patterns
3. Use `paths.include` to limit scope

## Related Documentation

- [Security Quickstart](./security-quickstart.md)
- [Command Reference](../reference/flowspec-security-commands.md)
- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax/)
