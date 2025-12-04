# Security Report Guidelines

This document defines standards for generating security audit reports in JP Spec Kit. These guidelines ensure consistency, clarity, and actionability across all security reports.

## Document Purpose

Security audit reports serve multiple audiences:
- **Executives**: Need business impact and risk summary
- **Developers**: Need technical details and remediation steps
- **Security Team**: Need compliance status and vulnerability tracking
- **Auditors**: Need evidence for compliance requirements

## Security Posture Calculation

The security posture is the top-level indicator of codebase security health.

### Posture Levels

| Posture | Definition | Criteria | Action Required |
|---------|------------|----------|-----------------|
| **SECURE** | No known vulnerabilities of concern | Zero critical vulnerabilities AND zero high vulnerabilities | Routine maintenance and monitoring |
| **CONDITIONAL** | Minor issues that require planning | Zero critical AND zero high, but one or more medium/low vulnerabilities | Schedule remediation in normal sprint planning |
| **AT RISK** | Critical vulnerabilities requiring immediate action | One or more critical OR high severity vulnerabilities | Immediate remediation required, consider deployment freeze |

### Calculation Formula

```python
def calculate_security_posture(findings):
    critical_count = count_by_severity(findings, "critical")
    high_count = count_by_severity(findings, "high")
    medium_count = count_by_severity(findings, "medium")
    low_count = count_by_severity(findings, "low")

    if critical_count > 0 or high_count > 0:
        return "AT RISK"
    elif medium_count > 0 or low_count > 0:
        return "CONDITIONAL"
    else:
        return "SECURE"
```

### Posture Overrides

In rare cases, security posture can be overridden if:
- Vulnerability is not exploitable in production environment (e.g., dev-only code)
- Compensating controls fully mitigate the risk
- Risk has been formally accepted by security team and documented

**Override must include:**
- Justification for override
- Approver name and date
- Compensating controls in place
- Re-evaluation date

## Severity Classification

### CVSS Score Mapping

| Severity | CVSS Score Range | Description | Example Vulnerabilities |
|----------|------------------|-------------|------------------------|
| **Critical** | 9.0 - 10.0 | Complete system compromise possible | SQL injection with admin access, Remote Code Execution |
| **High** | 7.0 - 8.9 | Significant data exposure or privilege escalation | XSS in admin panel, Authentication bypass |
| **Medium** | 4.0 - 6.9 | Limited data exposure or DoS | Missing security headers, Information disclosure |
| **Low** | 0.1 - 3.9 | Minor issues, configuration problems | Verbose error messages, Outdated dependencies (no CVE) |
| **Informational** | 0.0 | No security impact | Best practice recommendations |

### Severity Adjustment Factors

Adjust CVSS score based on:

**Increase Severity:**
- Vulnerability in authentication/authorization code
- PII or sensitive data involved
- Publicly exposed endpoint
- High likelihood of exploitation

**Decrease Severity:**
- Requires authenticated access
- Limited to internal network
- Compensating controls in place
- Low likelihood of exploitation

## OWASP Top 10 (2021) Categories

### Category Reference

| ID | Category | Description |
|----|----------|-------------|
| **A01** | Broken Access Control | Users accessing unauthorized functions/data |
| **A02** | Cryptographic Failures | Weak encryption or plaintext sensitive data |
| **A03** | Injection | Untrusted data sent to interpreter |
| **A04** | Insecure Design | Missing security controls in design |
| **A05** | Security Misconfiguration | Incorrect security settings |
| **A06** | Vulnerable and Outdated Components | Using vulnerable dependencies |
| **A07** | Identification and Authentication Failures | Weak authentication mechanisms |
| **A08** | Software and Data Integrity Failures | Missing integrity verification |
| **A09** | Security Logging and Monitoring Failures | Insufficient security event logging |
| **A10** | Server-Side Request Forgery (SSRF) | Fetching remote resource without URL validation |

### Mapping Vulnerabilities to OWASP

When analyzing a finding, determine which OWASP category applies:

**Examples:**
- SQL Injection → A03 (Injection)
- Missing authorization check → A01 (Broken Access Control)
- Hardcoded password → A02 (Cryptographic Failures)
- Outdated library with CVE → A06 (Vulnerable Components)
- No audit logging → A09 (Logging Failures)

**Multiple Categories:**
Some vulnerabilities map to multiple categories. Choose the **primary** category based on root cause.

## CWE (Common Weakness Enumeration) Mapping

Common CWE IDs to include:

| CWE | Name | OWASP |
|-----|------|-------|
| CWE-89 | SQL Injection | A03 |
| CWE-79 | Cross-Site Scripting (XSS) | A03 |
| CWE-78 | OS Command Injection | A03 |
| CWE-287 | Improper Authentication | A07 |
| CWE-285 | Improper Authorization | A01 |
| CWE-798 | Hardcoded Credentials | A02 |
| CWE-327 | Weak Crypto Algorithm | A02 |
| CWE-611 | XXE Injection | A03 |
| CWE-918 | SSRF | A10 |
| CWE-502 | Deserialization of Untrusted Data | A08 |

## Report Structure Standards

### Executive Summary (Required)

**Target Audience:** Non-technical stakeholders

**Length:** 1 page maximum

**Must Include:**
- Security posture (one of: SECURE, CONDITIONAL, AT RISK)
- Key findings count by severity
- Business impact summary (what could happen?)
- Top 3 recommended actions with timeline

**Writing Style:**
- Use business language, avoid jargon
- Focus on impact and risk
- Be specific about timelines
- Avoid technical implementation details

**Example:**
```markdown
## Executive Summary

**Overall Security Posture:** AT RISK

**Key Findings:**
- 2 Critical vulnerabilities requiring immediate attention
- 5 High severity issues to address within 7 days
- 12 Medium/Low issues for backlog

**Business Impact:**
The critical SQL injection vulnerability could allow unauthorized access to customer data,
resulting in potential GDPR violations (fines up to €20M) and significant reputational damage.

**Recommended Actions:**
1. Fix SQL injection in login endpoint - Timeline: 24-48 hours
2. Remediate authentication bypass - Timeline: 1 week
3. Patch XSS vulnerabilities in admin panel - Timeline: 2 weeks
```

### Findings Summary (Required)

**Purpose:** Statistical overview of all findings

**Format:**
```markdown
## Security Assessment Summary

| Metric | Value |
|--------|-------|
| Total Findings | 23 |
| Critical | 2 |
| High | 5 |
| Medium | 10 |
| Low | 6 |
| Informational | 3 |
| False Positives | 5 |

### Overall Security Posture
- [x] **AT RISK** - 2 critical and 5 high severity vulnerabilities require immediate remediation
- [ ] CONDITIONAL
- [ ] SECURE
```

### Detailed Findings (Required)

**Per-Finding Template:**
```markdown
### [VULN-001] SQL Injection in Login Endpoint

**Severity:** Critical
**CVSS Score:** 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
**CWE:** CWE-89 (SQL Injection)
**OWASP:** A03 (Injection)
**Status:** Open

**Description:**
The login endpoint in `src/auth/login.py` constructs SQL queries using string concatenation
with unsanitized user input. An attacker can inject arbitrary SQL code to bypass authentication
or extract sensitive data from the database.

**Location:**
- File: `src/auth/login.py:45`
- Function: `authenticate_user()`
- Component: Authentication Service

**Impact:**
- Complete authentication bypass
- Unauthorized access to all user accounts
- Potential data exfiltration of entire database
- Compliance violation (GDPR, SOC2)

**Proof of Concept:**
```python
# Malicious input
username = "admin' OR '1'='1' --"
password = "anything"

# Results in SQL:
# SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = 'anything'
# This bypasses authentication
```

**Remediation:**
1. Replace string concatenation with parameterized queries:
   ```python
   cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
   ```
2. Implement input validation on username field (alphanumeric only, max 50 chars)
3. Add rate limiting to login endpoint (5 attempts per IP per minute)
4. Add security test to verify fix

**Effort Estimate:** 2-4 hours
**Priority:** P0 (Immediate)
**Recommended Owner:** Backend Team

**References:**
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
```

### OWASP Top 10 Compliance (Required)

**Format:**
```markdown
## OWASP Top 10 Compliance Checklist

| Risk | Status | Findings | Notes |
|------|--------|----------|-------|
| A01 Broken Access Control | ❌ Fail | 3 | Missing authorization checks in admin endpoints |
| A02 Cryptographic Failures | ✅ Pass | 0 | All sensitive data encrypted properly |
| A03 Injection | ❌ Fail | 2 | SQL injection in login, XSS in search |
| A04 Insecure Design | ⚠️  Partial | 1 | No rate limiting on public APIs |
| A05 Security Misconfiguration | ✅ Pass | 0 | Security headers configured |
| A06 Vulnerable Components | ❌ Fail | 5 | 5 dependencies with known CVEs |
| A07 Auth Failures | ❌ Fail | 1 | Weak password policy |
| A08 Data Integrity Failures | ✅ Pass | 0 | Code signing implemented |
| A09 Logging Failures | ⚠️  Partial | 1 | Security events not logged |
| A10 SSRF | ✅ Pass | 0 | URL validation in place |

**Overall OWASP Compliance:** 40% (4/10 categories pass)
```

**Status Indicators:**
- ✅ **Pass** - No findings, all controls in place
- ❌ **Fail** - One or more findings in this category
- ⚠️  **Partial** - Controls partially implemented, minor issues

### Remediation Roadmap (Required)

**Purpose:** Prioritized action plan

**Priority Tiers:**
1. **Immediate (P0)**: Critical/High severity - within 7 days
2. **Short-term (P1)**: Medium severity - within 30 days
3. **Long-term (P2)**: Low severity - within 90 days

**Template:**
```markdown
## Remediation Recommendations

### Immediate Actions (P0 - Within 7 Days)

1. **[VULN-001] SQL Injection in Login Endpoint**
   - **Action:** Implement parameterized queries
   - **Owner:** Backend Team
   - **Effort:** 2-4 hours
   - **Due:** 2025-12-06
   - **Acceptance Criteria:**
     - [ ] Parameterized queries implemented
     - [ ] Input validation added
     - [ ] Security test added and passing
     - [ ] Code review completed

2. **[VULN-002] Authentication Bypass**
   - **Action:** Fix authorization logic
   - **Owner:** Backend Team
   - **Effort:** 1 day
   - **Due:** 2025-12-08

### Short-term Actions (P1 - Within 30 Days)

[Medium severity items...]

### Long-term Improvements (P2 - Within 90 Days)

[Low severity items...]

### Process Improvements

1. **Add Security Scanning to CI/CD**
   - Rationale: Catch vulnerabilities before merge
   - Effort: 2 days
   - Impact: Prevent 70% of future vulnerabilities

2. **Security Training for Developers**
   - Rationale: Reduce insecure coding patterns
   - Effort: 1 day workshop
   - Impact: Long-term reduction in vulnerabilities
```

## Output Format Standards

### Markdown (Primary Format)

**File Location:** `docs/security/audit-report.md`

**Requirements:**
- Use semantic markdown (proper headings, tables, code blocks)
- Include table of contents for reports >5 pages
- Use consistent heading levels (# for title, ## for sections, ### for subsections)
- Code blocks must specify language for syntax highlighting
- Tables must be well-formatted with alignment

### HTML (Optional Format)

**File Location:** `docs/security/audit-report.html`

**Generation:** Use Pandoc to convert markdown to HTML
```bash
pandoc docs/security/audit-report.md \
  -o docs/security/audit-report.html \
  --standalone \
  --css=security-report.css \
  --metadata title="Security Audit Report"
```

**Requirements:**
- Standalone HTML (includes CSS inline or linked)
- Responsive design for mobile viewing
- Print-friendly stylesheet
- Navigation links for sections

### PDF (Optional Format)

**File Location:** `docs/security/audit-report.pdf`

**Generation:** Convert HTML to PDF using wkhtmltopdf
```bash
wkhtmltopdf \
  --enable-local-file-access \
  --print-media-type \
  docs/security/audit-report.html \
  docs/security/audit-report.pdf
```

**Requirements:**
- Professional formatting suitable for compliance audits
- Page numbers and table of contents
- Consistent fonts and styling
- Printable on letter/A4 paper

## Quality Checklist

Before finalizing any security audit report, verify:

### Completeness
- [ ] Executive summary present and non-technical
- [ ] Security posture clearly stated and justified
- [ ] All findings documented with severity, description, location, remediation
- [ ] OWASP Top 10 compliance section complete (all 10 categories)
- [ ] Remediation roadmap with priorities and timelines
- [ ] Sign-off section for stakeholder approval

### Technical Accuracy
- [ ] CVSS scores calculated correctly (use CVSS calculator)
- [ ] CWE mappings accurate (verify on cwe.mitre.org)
- [ ] OWASP categories correct (reference OWASP Top 10 2021)
- [ ] Remediation steps technically sound and specific
- [ ] No false positives included (verified through triage)

### Clarity and Actionability
- [ ] Executive summary understandable by non-technical readers
- [ ] Technical details sufficient for developers to implement fixes
- [ ] Recommendations specific and actionable (not vague)
- [ ] Timelines realistic based on severity and effort
- [ ] Ownership clearly assigned

### Formatting and Style
- [ ] Consistent markdown formatting
- [ ] Tables well-formatted and aligned
- [ ] Code blocks use syntax highlighting
- [ ] No spelling or grammar errors
- [ ] Professional tone throughout

## Compliance and Audit Requirements

### Audit Trail

Every security audit report must include:
- **Report Version:** Semantic versioning (1.0, 1.1, 2.0)
- **Generated Date:** ISO 8601 timestamp
- **Assessor:** Name or system that generated report
- **Input Data Sources:** Links to scan-results.json, triage-results.json

### Version Control

- Store all reports in Git for version history
- Use conventional commit messages: `docs(security): add audit report for feature-x`
- Tag significant reports: `security-audit-v1.0`

### Retention Policy

- Keep audit reports for minimum 3 years for compliance
- Archive reports in `docs/security/archive/YYYY-MM/` after 1 year
- Update reports as vulnerabilities are remediated (track status changes)

## Common Mistakes to Avoid

1. **Severity Inflation:** Don't label everything as Critical to get attention
2. **Vague Remediation:** "Fix the vulnerability" is not helpful
3. **Missing Context:** Always include file location and line number
4. **Ignoring False Positives:** Verify findings before reporting
5. **Technical Jargon in Executive Summary:** Use business language
6. **Unrealistic Timelines:** Consider team capacity and priorities
7. **Incomplete OWASP Mapping:** All 10 categories must be addressed
8. **No Follow-up Plan:** Include re-scan recommendations

## Report Maintenance

### Updating Reports

When vulnerabilities are remediated:
1. Update finding status from "Open" to "Remediated"
2. Add remediation date and verification method
3. Recalculate security posture
4. Update OWASP compliance checklist
5. Increment report version (1.0 → 1.1)

### Re-scanning

After remediation:
1. Re-run security scans
2. Verify vulnerabilities are fixed
3. Generate updated audit report
4. Compare before/after metrics

## Tools and Resources

### CVSS Calculator
- [NIST CVSS v3.1 Calculator](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator)

### CWE Database
- [CWE List](https://cwe.mitre.org/data/index.html)

### OWASP Resources
- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

### Report Generation Tools
- Pandoc (markdown to HTML/PDF)
- wkhtmltopdf (HTML to PDF)
- markdown-pdf (alternative PDF generator)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-04
**Owner:** Security Team
