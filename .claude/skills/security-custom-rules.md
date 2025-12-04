# Security Custom Rules Skill

## Purpose

This skill enables Claude Code to help users create, validate, and test custom security rules for `/jpspec:security` scanning. You will guide users through the process of writing Semgrep and Bandit rules tailored to their organization's security requirements.

## When to Use This Skill

- When user asks to create a custom security rule
- When user wants to detect organization-specific vulnerabilities
- When user needs to reduce false positives in security scans
- When user wants to enforce internal coding standards
- When invoked via `/jpspec:security_custom_rules` command

## Rule Formats Supported

### Semgrep Rules (Recommended)

**Location**: `.specify/security/rules/` or `.semgrep/`

Semgrep rules use YAML syntax with pattern matching. Best for:
- Multi-language support
- Complex pattern matching
- Quick prototyping
- Cross-project consistency

### Bandit Rules (Python Only)

**Location**: `.specify/security/bandit/`

Python plugins for extending Bandit scanner. Best for:
- Deep Python AST analysis
- Complex control flow checks
- Custom test IDs

## Creating Semgrep Rules

### Step 1: Identify the Vulnerability Pattern

Ask the user:
1. What vulnerability are you trying to detect?
2. What programming language(s)?
3. Do you have example vulnerable code?
4. What frameworks/libraries are involved?

### Step 2: Write the Basic Pattern

Start with the simplest pattern that matches the vulnerability:

```yaml
rules:
  - id: my-rule-id
    pattern: dangerous_function($ARG)
    message: "Brief description of the issue"
    severity: WARNING  # ERROR, WARNING, or INFO
    languages:
      - python
```

### Step 3: Reduce False Positives

Add `pattern-not` clauses to exclude safe cases:

```yaml
rules:
  - id: sql-injection-check
    patterns:
      - pattern: cursor.execute($QUERY)
      - pattern-not: cursor.execute("...", $PARAMS)
      - pattern-not: cursor.execute($CONST)
      - metavariable-pattern:
          metavariable: $QUERY
          patterns:
            - pattern-either:
                - pattern: $X + $Y
                - pattern: f"..."
                - pattern: "...".format(...)
    message: "SQL query with string interpolation may be vulnerable"
    severity: ERROR
    languages:
      - python
```

### Step 4: Add Context with pattern-inside

Scope rules to specific contexts to reduce noise:

```yaml
rules:
  - id: flask-route-xss
    patterns:
      - pattern-inside: |
          @app.route(...)
          def $FUNC(...):
            ...
      - pattern: return $HTML
      - metavariable-pattern:
          metavariable: $HTML
          pattern-either:
            - pattern: $X + $Y
            - pattern: f"<html>..."
    message: "Flask route returns unsanitized HTML"
    severity: HIGH
    languages:
      - python
```

### Step 5: Add Metadata

Include metadata for better reporting and remediation:

```yaml
rules:
  - id: hardcoded-secrets
    pattern: |
      password = "..."
    message: "Hardcoded password detected"
    severity: ERROR
    languages:
      - python
    metadata:
      cwe: "CWE-798"
      owasp: "A07:2021"
      category: security
      confidence: HIGH
      remediation: |
        Use environment variables or secret management:
        ```python
        import os
        password = os.environ.get('DB_PASSWORD')
        ```
      references:
        - https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
```

## Pattern Operators Reference

| Operator | Description | Example Use Case |
|----------|-------------|------------------|
| `pattern` | Exact match with metavariables | `eval($X)` |
| `pattern-regex` | Regular expression | `password\s*=\s*['\"][^'\"]+['\"]` |
| `pattern-either` | Match any pattern (OR) | Multiple dangerous functions |
| `pattern-not` | Exclude matches | Filter false positives |
| `pattern-inside` | Match within context | Only in route handlers |
| `pattern-not-inside` | Exclude context | Exclude test files |
| `metavariable-pattern` | Match metavariable content | Check if variable is tainted |
| `metavariable-regex` | Regex on metavariable | Match variable names |
| `metavariable-comparison` | Compare metavariables | `$X == $Y` |

## Testing Custom Rules

### Step 1: Validate Syntax

```bash
# Validate rule syntax
semgrep --validate --config .specify/security/rules/my-rule.yml
```

### Step 2: Test Against Code

```bash
# Test rule against codebase
semgrep --config .specify/security/rules/my-rule.yml src/

# Test with verbose output for debugging
semgrep --config .specify/security/rules/my-rule.yml src/ --verbose
```

### Step 3: Create Test Cases

Add test cases directly in the rule file:

```yaml
rules:
  - id: unsafe-eval
    pattern: eval($X)
    message: "Avoid eval() with untrusted input"
    severity: ERROR
    languages:
      - python

# Test cases below (Semgrep will auto-detect)
---
# ruleid: unsafe-eval
eval(user_input)

# ruleid: unsafe-eval
result = eval(request.GET['expr'])

# ok: unsafe-eval
ast.literal_eval(safe_input)

# ok: unsafe-eval
ALLOWED_FUNCTIONS = ['sum', 'max']
```

Run tests:

```bash
semgrep --test .specify/security/rules/
```

## Common Rule Patterns

### Dangerous Functions

```yaml
rules:
  - id: dangerous-exec
    pattern-either:
      - pattern: exec($X)
      - pattern: eval($X)
      - pattern: __import__($X)
    message: "Dangerous code execution function"
    severity: ERROR
    languages:
      - python
```

### Insecure Configuration

```yaml
rules:
  - id: flask-debug-production
    patterns:
      - pattern: app.run(..., debug=True, ...)
      - pattern-not-inside: |
          if __name__ == "__main__":
            ...
    message: "Flask debug mode should not be enabled in production"
    severity: ERROR
    languages:
      - python
```

### Hardcoded Credentials

```yaml
rules:
  - id: hardcoded-api-key
    patterns:
      - pattern-either:
          - pattern: api_key = "..."
          - pattern: API_KEY = "..."
          - pattern: secret = "..."
      - pattern-not: $VAR = ""
      - pattern-not: $VAR = os.environ[...]
      - pattern-not: $VAR = os.getenv(...)
    message: "Hardcoded API key detected"
    severity: ERROR
    languages:
      - python
```

### SQL Injection

```yaml
rules:
  - id: sql-injection
    patterns:
      - pattern-either:
          - pattern: cursor.execute($QUERY)
          - pattern: db.execute($QUERY)
          - pattern: connection.execute($QUERY)
      - metavariable-pattern:
          metavariable: $QUERY
          pattern-either:
            - pattern: $X + $Y
            - pattern: f"..."
            - pattern: "...".format(...)
            - pattern: "..." % (...)
      - pattern-not: cursor.execute("...", $PARAMS)
    message: "SQL query with string interpolation - use parameterized queries"
    severity: ERROR
    languages:
      - python
    metadata:
      cwe: "CWE-89"
```

### XSS (Cross-Site Scripting)

```yaml
rules:
  - id: flask-xss
    patterns:
      - pattern-inside: |
          @app.route(...)
          def $FUNC(...):
            ...
      - pattern-either:
          - pattern: return $HTML
          - pattern: render_template_string($HTML)
      - metavariable-pattern:
          metavariable: $HTML
          pattern-either:
            - pattern: $X + $Y
            - pattern: f"..."
            - pattern: "...".format(...)
    message: "Potential XSS - sanitize user input before rendering"
    severity: HIGH
    languages:
      - python
```

## Interactive Rule Creation Workflow

When user requests custom rule creation:

### 1. Gather Requirements

Ask:
- What vulnerability pattern are you detecting?
- What language(s)?
- Do you have example vulnerable code?
- Do you have example safe code (should NOT match)?

### 2. Draft Initial Rule

Create simple pattern based on user input:

```yaml
rules:
  - id: [descriptive-id]
    pattern: [basic-pattern]
    message: "[clear description]"
    severity: [ERROR/WARNING/INFO]
    languages:
      - [language]
```

### 3. Test and Refine

```bash
# Save to temp file
echo "$RULE_YAML" > /tmp/test-rule.yml

# Test against user's code
semgrep --config /tmp/test-rule.yml [target-files]
```

Review results with user:
- Are there false positives?
- Are there false negatives (missed cases)?

### 4. Add False Positive Filters

Add `pattern-not` clauses based on safe patterns:

```yaml
rules:
  - id: my-rule
    patterns:
      - pattern: [main-pattern]
      - pattern-not: [safe-case-1]
      - pattern-not: [safe-case-2]
```

### 5. Add Metadata and Documentation

```yaml
rules:
  - id: my-rule
    # ... patterns ...
    metadata:
      cwe: "CWE-XXX"
      owasp: "AXX:2021"
      category: security
      confidence: HIGH
      remediation: |
        Explain how to fix with code example
      references:
        - https://...
```

### 6. Create Test Cases

Add test cases to rule file or separate `.test.py` file.

### 7. Integrate with Project

```bash
# Move to project security rules
mkdir -p .specify/security/rules
cp /tmp/test-rule.yml .specify/security/rules/

# Update security config if needed
# .specify/security.yml
```

## Troubleshooting

### Rule Not Matching Expected Code

1. **Check pattern syntax**:
   ```bash
   semgrep --validate --config rule.yml
   ```

2. **Use verbose mode**:
   ```bash
   semgrep --config rule.yml file.py --verbose
   ```

3. **Test pattern incrementally**:
   - Start with simplest pattern
   - Add one constraint at a time
   - Verify each step matches

### Too Many False Positives

1. **Add context with `pattern-inside`**:
   ```yaml
   patterns:
     - pattern-inside: |
         def $FUNC(...):
           ...
     - pattern: dangerous($X)
   ```

2. **Exclude safe patterns**:
   ```yaml
   patterns:
     - pattern: eval($X)
     - pattern-not: eval($SAFE_CONSTANT)
   ```

3. **Use metavariable constraints**:
   ```yaml
   patterns:
     - pattern: func($ARG)
     - metavariable-regex:
         metavariable: $ARG
         regex: "^(user_|request\\.)"
   ```

### Performance Issues

1. **Limit to specific languages**
2. **Use `paths.include` to scope**:
   ```yaml
   rules:
     - id: my-rule
       # ... patterns ...
       paths:
         include:
           - "src/**/*.py"
         exclude:
           - "tests/**"
   ```

3. **Avoid overly broad regex patterns**

## Integration with jpspec Workflow

### Creating Rules for Project

1. **Bootstrap custom rules directory**:
   ```bash
   specify security init-custom-rules
   ```
   Creates `.specify/security/rules/` with example rules.

2. **Add rule to project**:
   ```bash
   # Create rule file
   vim .specify/security/rules/company-standards.yml
   ```

3. **Test locally**:
   ```bash
   specify security scan --config .specify/security/rules/
   ```

4. **Update security config**:
   ```yaml
   # .specify/security.yml
   scanners:
     semgrep:
       enabled: true
       config:
         - auto  # OWASP Top 10 rules
         - .specify/security/rules/  # Custom rules
   ```

5. **Commit and use**:
   ```bash
   git add .specify/security/rules/
   git commit -m "Add custom security rules for [purpose]"
   ```

## Success Criteria

A good custom rule should:
- [ ] Have a clear, descriptive ID
- [ ] Match true vulnerabilities (no false negatives)
- [ ] Minimize false positives (<10%)
- [ ] Include actionable message
- [ ] Specify correct severity
- [ ] Include metadata (CWE, OWASP, remediation)
- [ ] Have test cases (positive and negative)
- [ ] Be documented with examples

## Example Workflow

```bash
# User asks: "Create a rule to detect hardcoded JWT secrets"

# You respond:
1. Create rule file: .specify/security/rules/jwt-secrets.yml
2. Draft pattern:
   ```yaml
   rules:
     - id: hardcoded-jwt-secret
       pattern-either:
         - pattern: jwt.encode(..., secret="...", ...)
         - pattern: PyJWT.encode(..., key="...", ...)
       pattern-not: jwt.encode(..., secret=os.environ[...], ...)
       message: "Hardcoded JWT secret - use environment variable"
       severity: ERROR
   ```
3. Test: semgrep --config .specify/security/rules/jwt-secrets.yml src/
4. Refine based on results
5. Add to project security config
```

## Related Documentation

- [Custom Security Rules Guide](../../docs/guides/security-custom-rules.md)
- [Security Quickstart](../../docs/guides/security-quickstart.md)
- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax/)
- [OWASP Top 10](https://owasp.org/Top10/)

## Notes

- This is a SKILL file - you (Claude Code) execute the logic
- No LLM API calls from Python code
- Use Read/Write/Bash tools to create and test rules
- Reference existing security documentation
- Focus on practical, actionable guidance
