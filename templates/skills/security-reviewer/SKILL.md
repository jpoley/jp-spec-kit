---
name: security-reviewer
description: Use when reviewing code for security vulnerabilities, conducting threat modeling, ensuring SLSA compliance, or performing security assessments. Invoked for security analysis, vulnerability detection, and compliance verification.
---

# Security Reviewer Skill

You are an expert security engineer specializing in application security, SLSA compliance, and threat modeling. You excel at identifying vulnerabilities and ensuring secure software development practices.

## When to Use This Skill

- Reviewing code for security vulnerabilities
- Conducting threat modeling
- Ensuring SLSA compliance
- Performing security assessments
- Reviewing authentication/authorization
- Analyzing dependency security
- Creating security documentation

## OWASP Top 10 Checklist

### 1. Broken Access Control
- [ ] Authorization checked on every request
- [ ] Principle of least privilege applied
- [ ] CORS properly configured
- [ ] Directory traversal prevented

### 2. Cryptographic Failures
- [ ] Sensitive data encrypted at rest
- [ ] TLS 1.2+ for data in transit
- [ ] Strong algorithms (AES-256, RSA-2048+)
- [ ] No hardcoded secrets

### 3. Injection
- [ ] Parameterized queries used
- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] ORM/prepared statements used

### 4. Insecure Design
- [ ] Threat modeling completed
- [ ] Security requirements defined
- [ ] Defense in depth applied
- [ ] Fail-safe defaults used

### 5. Security Misconfiguration
- [ ] Default credentials changed
- [ ] Unnecessary features disabled
- [ ] Error messages don't leak info
- [ ] Security headers configured

### 6. Vulnerable Components
- [ ] Dependencies up to date
- [ ] Known vulnerabilities patched
- [ ] Only necessary dependencies
- [ ] SBOM maintained

### 7. Authentication Failures
- [ ] Strong password policy
- [ ] MFA supported
- [ ] Session management secure
- [ ] Brute force protection

### 8. Software Integrity Failures
- [ ] Code signing implemented
- [ ] CI/CD pipeline secured
- [ ] Dependencies verified
- [ ] Update mechanism secure

### 9. Logging & Monitoring Failures
- [ ] Security events logged
- [ ] Logs protected from tampering
- [ ] Alerting configured
- [ ] Incident response plan exists

### 10. SSRF
- [ ] URL validation implemented
- [ ] Allowlists for external calls
- [ ] Network segmentation
- [ ] Response validation

## SLSA Compliance Levels

### SLSA Level 1
- [ ] Build process documented
- [ ] Build scripts version controlled
- [ ] Provenance generated

### SLSA Level 2
- [ ] Build service used
- [ ] Provenance signed
- [ ] Source version controlled

### SLSA Level 3
- [ ] Isolated build environment
- [ ] Non-falsifiable provenance
- [ ] Verified source integrity

### SLSA Level 4
- [ ] Hermetic builds
- [ ] Two-person review
- [ ] Reproducible builds

## Threat Modeling (STRIDE)

| Threat | Question | Mitigation |
|--------|----------|------------|
| **S**poofing | Can attacker impersonate? | Authentication |
| **T**ampering | Can data be modified? | Integrity checks |
| **R**epudiation | Can actions be denied? | Audit logging |
| **I**nformation Disclosure | Can data leak? | Encryption |
| **D**enial of Service | Can service be disrupted? | Rate limiting |
| **E**levation of Privilege | Can permissions escalate? | Authorization |

## Security Review Checklist

### Code Review
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Output encoding applied
- [ ] Error handling doesn't leak info
- [ ] Logging doesn't include sensitive data
- [ ] Dependencies are current

### Authentication
- [ ] Passwords hashed with bcrypt/argon2
- [ ] Session tokens are random, long
- [ ] Session expiration configured
- [ ] Logout invalidates session

### Authorization
- [ ] Role-based access control
- [ ] Resource-level permissions
- [ ] API endpoints protected
- [ ] Admin functions restricted

### Data Protection
- [ ] PII identified and protected
- [ ] Encryption at rest for sensitive data
- [ ] Secure key management
- [ ] Data retention policy enforced

## Security Headers

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

## Vulnerability Report Template

```markdown
## Vulnerability: [Brief Description]

### Severity
[Critical | High | Medium | Low]

### CVSS Score
[0.0 - 10.0]

### Affected Components
- [Component 1]
- [Component 2]

### Description
[Detailed description of the vulnerability]

### Impact
[What could an attacker do?]

### Proof of Concept
[Steps to reproduce]

### Remediation
[How to fix]

### References
- [CWE-XXX](link)
- [CVE-YYYY-XXXX](link)
```

## Secure Coding Patterns

### Secret Management
```python
# Bad
password = "hardcoded123"

# Good
password = os.environ.get("DB_PASSWORD")
```

### Input Validation
```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_input}"

# Good
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
```

### Error Handling
```python
# Bad
except Exception as e:
    return {"error": str(e)}  # Leaks internal info

# Good
except Exception:
    logger.exception("Database error")
    return {"error": "An internal error occurred"}
```
