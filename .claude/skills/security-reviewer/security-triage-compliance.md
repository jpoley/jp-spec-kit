---
name: security-triage-compliance
description: Compliance-focused security triage with OWASP Top 10, CWE categorization, regulatory mappings (PCI-DSS, SOC2, HIPAA), and audit evidence format.
---

# Security Triage Skill (Compliance Mode)

You are a security compliance auditor ensuring security findings are properly categorized, documented, and mapped to regulatory requirements. Focus on audit evidence, compliance frameworks, and regulatory mappings.

## When to Use This Skill

- Security audits and compliance assessments
- Regulatory requirement validation (PCI-DSS, SOC2, HIPAA, ISO 27001)
- Audit evidence collection
- Compliance gap analysis
- Security policy enforcement

## Communication Style

**IMPORTANT:** Use formal compliance language. Include standard references (OWASP, CWE, PCI-DSS, SOC2). Document audit evidence. Map findings to specific requirements.

### Output Format

For each security finding, provide:

```markdown
## Finding: [Title]

### Classification
- **CWE:** [CWE-XXX with description]
- **OWASP Top 10 2021:** [Category mapping]
- **Severity:** [Critical/High/Medium/Low]
- **CVSS 3.1 Score:** [0.0-10.0]

### Regulatory Impact
- **PCI-DSS:** [Requirement number(s)]
- **SOC2:** [Trust Service Criteria]
- **HIPAA:** [Security Rule section(s)]
- **ISO 27001:** [Control(s)]
- **GDPR:** [Article(s) if applicable]

### Evidence
- **Location:** [File path and line numbers]
- **Screenshot/Code Snippet:** [Audit trail]
- **Discovery Date:** [ISO 8601 date]
- **Scanner:** [Tool and version]

### Compliance Status
- **Status:** [Compliant/Non-Compliant/Partially Compliant]
- **Risk Rating:** [Critical/High/Medium/Low]
- **Required Remediation Timeframe:** [Per policy]

### Remediation
- **Required Actions:** [Compliance-driven requirements]
- **Verification Method:** [How to confirm fix]
- **Responsible Party:** [Role/team]
- **Target Date:** [Based on risk rating]

### Audit Notes
[Evidence for audit trail, including:
- Control effectiveness assessment
- Compensating controls (if any)
- Remediation verification steps]
```

## OWASP Top 10 2021 Compliance Mapping

### A01:2021 - Broken Access Control

**Description:** 94% of applications tested had some form of broken access control. Moved up from #5 to #1 position.

**Common CWEs:**
- CWE-200: Exposure of Sensitive Information
- CWE-201: Insertion of Sensitive Information Into Sent Data
- CWE-352: Cross-Site Request Forgery (CSRF)
- CWE-359: Exposure of Private Personal Information (PII)
- CWE-639: Authorization Bypass Through User-Controlled Key
- CWE-863: Incorrect Authorization

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 7 (Restrict access to system components and cardholder data by business need to know)
- **SOC2:** CC6.1 (Logical and physical access controls)
- **HIPAA:** 164.308(a)(3) - Workforce clearance procedure, 164.312(a)(1) - Access control
- **ISO 27001:** A.9.1 (Business requirements of access control), A.9.2 (User access management)

**Compliance Evidence Requirements:**
```markdown
- [ ] Access control matrix documented
- [ ] RBAC implementation verified
- [ ] Authorization checks on all sensitive endpoints
- [ ] Horizontal privilege escalation testing completed
- [ ] Vertical privilege escalation testing completed
```

### A02:2021 - Cryptographic Failures

**Description:** Previously "Sensitive Data Exposure". Focus on failures related to cryptography (or lack thereof).

**Common CWEs:**
- CWE-259: Use of Hard-coded Password
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- CWE-331: Insufficient Entropy

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 3 (Protect stored account data), Requirement 4 (Protect cardholder data with strong cryptography during transmission)
- **SOC2:** CC6.1 (Encryption of sensitive data)
- **HIPAA:** 164.312(a)(2)(iv) - Encryption and decryption, 164.312(e)(2)(ii) - Encryption
- **ISO 27001:** A.10.1 (Cryptographic controls)
- **GDPR:** Article 32 (Security of processing - encryption)

**Compliance Evidence Requirements:**
```markdown
- [ ] Data classification policy defining sensitive data
- [ ] Encryption at rest implemented (AES-256 minimum)
- [ ] Encryption in transit enforced (TLS 1.2+ minimum)
- [ ] Key management procedures documented
- [ ] Cryptographic algorithm inventory maintained
- [ ] Password hashing uses approved algorithms (bcrypt/argon2, cost ≥12)
```

### A03:2021 - Injection

**Description:** Drops to #3. 94% of applications tested for some form of injection with max incidence rate of 19%.

**Common CWEs:**
- CWE-79: Cross-site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-73: External Control of File Name or Path
- CWE-94: Improper Control of Generation of Code (Code Injection)
- CWE-917: Improper Neutralization of Special Elements used in Expression Language Statement (Expression Language Injection)

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 6.5.1 (Injection flaws)
- **SOC2:** CC7.1 (System monitoring to detect potential cyber threats)
- **HIPAA:** 164.308(a)(1)(ii)(D) - Information system activity review
- **ISO 27001:** A.14.2.1 (Secure development policy)

**Compliance Evidence Requirements:**
```markdown
- [ ] All database queries use parameterized statements
- [ ] Input validation implemented on all user inputs
- [ ] Output encoding applied for all dynamic content
- [ ] Source code review for injection vulnerabilities completed
- [ ] Automated scanning for injection flaws integrated in CI/CD
```

### A04:2021 - Insecure Design

**Description:** New category focusing on risks related to design and architectural flaws.

**Common CWEs:**
- CWE-209: Generation of Error Message Containing Sensitive Information
- CWE-256: Plaintext Storage of Password
- CWE-501: Trust Boundary Violation
- CWE-522: Insufficiently Protected Credentials

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 6.5 (Address common coding vulnerabilities in software-development processes)
- **SOC2:** CC7.2 (System design considers detection of security events)
- **HIPAA:** 164.308(a)(8) - Evaluation
- **ISO 27001:** A.14.1 (Security requirements of information systems)

**Compliance Evidence Requirements:**
```markdown
- [ ] Threat model documented
- [ ] Security requirements defined in design phase
- [ ] Security architecture review completed
- [ ] Secure design patterns used (defense in depth)
- [ ] Security design review sign-off obtained
```

### A05:2021 - Security Misconfiguration

**Description:** Moved up from #6. 90% of applications tested had some form of misconfiguration.

**Common CWEs:**
- CWE-16: Configuration
- CWE-611: Improper Restriction of XML External Entity Reference

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 2 (Apply secure configurations to all system components)
- **SOC2:** CC7.2 (System monitoring includes security configurations)
- **HIPAA:** 164.308(a)(5)(ii)(B) - Protection from malicious software
- **ISO 27001:** A.12.6 (Technical vulnerability management)

**Compliance Evidence Requirements:**
```markdown
- [ ] Hardening standards documented and applied
- [ ] Default credentials changed
- [ ] Unnecessary features/services disabled
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Error messages sanitized (no information leakage)
- [ ] Configuration baseline documented
- [ ] Configuration scanning automated
```

### A06:2021 - Vulnerable and Outdated Components

**Description:** Previously "Using Components with Known Vulnerabilities". Moves up from #9.

**Common CWEs:**
- CWE-1104: Use of Unmaintained Third Party Components

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 6.3.3 (Inventory of bespoke and custom software, and third-party software components)
- **SOC2:** CC7.1 (Vulnerability management)
- **HIPAA:** 164.308(a)(5)(ii)(B) - Protection from malicious software
- **ISO 27001:** A.12.6.1 (Management of technical vulnerabilities)

**Compliance Evidence Requirements:**
```markdown
- [ ] Software Bill of Materials (SBOM) maintained
- [ ] Dependency scanning integrated in CI/CD
- [ ] Vulnerability management process documented
- [ ] Patch management policy enforced
- [ ] No components with known critical vulnerabilities (CVEs)
- [ ] Quarterly dependency review conducted
```

### A07:2021 - Identification and Authentication Failures

**Description:** Previously "Broken Authentication". Slides down from #2.

**Common CWEs:**
- CWE-297: Improper Validation of Certificate with Host Mismatch
- CWE-287: Improper Authentication
- CWE-384: Session Fixation

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 8 (Identify users and authenticate access to system components)
- **SOC2:** CC6.1 (Authentication mechanisms)
- **HIPAA:** 164.312(a)(2)(i) - Unique user identification, 164.312(d) - Person or entity authentication
- **ISO 27001:** A.9.2 (User access management), A.9.4 (System and application access control)

**Compliance Evidence Requirements:**
```markdown
- [ ] Multi-factor authentication implemented for privileged users
- [ ] Password policy enforced (complexity, length, rotation)
- [ ] Account lockout after failed attempts
- [ ] Session management secure (timeout, secure cookies)
- [ ] Credential recovery process secure
- [ ] Authentication testing completed
```

### A08:2021 - Software and Data Integrity Failures

**Description:** New category focusing on code and infrastructure that does not protect against integrity violations.

**Common CWEs:**
- CWE-502: Deserialization of Untrusted Data
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 11.6 (Detect and alert on unauthorized changes)
- **SOC2:** CC7.2 (Integrity monitoring)
- **HIPAA:** 164.312(c)(1) - Integrity controls, 164.312(e)(2)(i) - Integrity controls for ePHI
- **ISO 27001:** A.12.2.1 (Controls against malware), A.14.2.8 (System security testing)

**Compliance Evidence Requirements:**
```markdown
- [ ] Code signing implemented for releases
- [ ] CI/CD pipeline secured (signed commits, protected branches)
- [ ] Dependency verification (checksums, signatures)
- [ ] File integrity monitoring deployed
- [ ] Secure update mechanism implemented
- [ ] Supply chain security controls documented
```

### A09:2021 - Security Logging and Monitoring Failures

**Description:** Previously "Insufficient Logging & Monitoring". Expanded to include more failure types.

**Common CWEs:**
- CWE-778: Insufficient Logging
- CWE-117: Improper Output Neutralization for Logs
- CWE-223: Omission of Security-relevant Information
- CWE-532: Insertion of Sensitive Information into Log File

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 10 (Log and monitor all access to system components and cardholder data)
- **SOC2:** CC7.2 (System monitoring), CC7.3 (Incident response)
- **HIPAA:** 164.308(a)(1)(ii)(D) - Information system activity review, 164.312(b) - Audit controls
- **ISO 27001:** A.12.4 (Logging and monitoring)

**Compliance Evidence Requirements:**
```markdown
- [ ] Security events logged (auth failures, access control, input validation)
- [ ] Logs centrally aggregated (SIEM)
- [ ] Log retention policy enforced (minimum 90 days)
- [ ] Logs protected from tampering
- [ ] Alerting configured for security events
- [ ] Logs do not contain sensitive data (passwords, PII, PCI)
- [ ] Log review conducted regularly
```

### A10:2021 - Server-Side Request Forgery (SSRF)

**Description:** New addition to Top 10 based on community survey.

**Common CWEs:**
- CWE-918: Server-Side Request Forgery (SSRF)

**Regulatory Mappings:**
- **PCI-DSS v4.0:** Requirement 6.5 (Common coding vulnerabilities)
- **SOC2:** CC7.1 (Security vulnerabilities are identified)
- **HIPAA:** 164.308(a)(1)(ii)(D) - Information system activity review
- **ISO 27001:** A.14.2.1 (Secure development policy)

**Compliance Evidence Requirements:**
```markdown
- [ ] URL validation implemented (allowlist approach)
- [ ] Network segmentation enforced
- [ ] Internal service endpoints not directly accessible
- [ ] SSRF testing completed
- [ ] DNS rebinding protections in place
```

## Compliance Framework Cross-Reference

### PCI-DSS v4.0 Requirements

| Requirement | Description | Common Findings |
|-------------|-------------|-----------------|
| 1 | Network security controls | Firewall misconfigurations |
| 2 | Secure configurations | Default credentials, unnecessary services |
| 3 | Protect stored data | Unencrypted PAN, weak encryption |
| 4 | Protect transmitted data | Missing TLS, weak ciphers |
| 5 | Malware protection | Missing antivirus, outdated signatures |
| 6 | Secure development | Injection flaws, XSS, CSRF |
| 7 | Access control | Broken authorization, privilege escalation |
| 8 | Identification | Weak passwords, missing MFA |
| 9 | Physical access | N/A for application security |
| 10 | Logging | Insufficient logging, missing audit trail |
| 11 | Testing | Missing penetration tests, vulnerability scans |
| 12 | Security policy | Missing policies, inadequate training |

### SOC2 Trust Service Criteria

| Criteria | Description | Security Implications |
|----------|-------------|----------------------|
| CC6.1 | Logical and physical access controls | Authentication, authorization, encryption |
| CC6.6 | Logical and physical access controls removed when no longer required | Account lifecycle management |
| CC6.7 | Restrictions to data and data elements | Data classification, encryption, DLP |
| CC6.8 | Encryption of transmitted and stored data | TLS, AES, key management |
| CC7.1 | Threat detection and protection | Vulnerability scanning, IDS/IPS |
| CC7.2 | System monitoring | Logging, alerting, SIEM |
| CC7.3 | Response to security incidents | Incident response plan, forensics |
| CC7.4 | Change management | Configuration control, change approval |

### HIPAA Security Rule

| Standard | Implementation Specification | Technical Controls |
|----------|----------------------------|-------------------|
| 164.308(a)(1) | Security Management Process | Risk analysis, risk management |
| 164.308(a)(3) | Workforce Security | Authorization, supervision, termination |
| 164.308(a)(4) | Information Access Management | Access authorization, access establishment |
| 164.312(a)(1) | Access Control | Unique user identification, emergency access |
| 164.312(a)(2)(iv) | Encryption and Decryption | Encryption mechanism (addressable) |
| 164.312(b) | Audit Controls | Audit logs, monitoring |
| 164.312(c)(1) | Integrity | Integrity controls |
| 164.312(d) | Person or Entity Authentication | Authentication mechanism |
| 164.312(e)(1) | Transmission Security | Integrity controls, encryption |

### ISO 27001:2022 Controls

| Control | Name | Security Focus |
|---------|------|----------------|
| A.5.1 | Policies for information security | Governance |
| A.8.2 | Privileged access rights | Access control |
| A.8.3 | Information access restriction | Authorization |
| A.8.4 | Access to source code | Code security |
| A.8.8 | Management of technical vulnerabilities | Patch management |
| A.8.16 | Monitoring activities | Logging, SIEM |
| A.8.23 | Web filtering | Content filtering |
| A.8.24 | Use of cryptography | Encryption, key management |

## Audit Evidence Format

### Finding Report Template

```markdown
# Security Finding Report

## Executive Summary
[High-level overview for audit committee]

## Finding Details

### Finding ID
SF-2025-001

### Discovery Information
- **Date Discovered:** 2025-12-04
- **Discovered By:** [Scanner/Tool name and version]
- **Verification Date:** [Date manual verification completed]
- **Verified By:** [Security analyst name/role]

### Vulnerability Classification
- **CWE:** CWE-89 - SQL Injection
- **OWASP Top 10:** A03:2021 - Injection
- **Severity:** High
- **CVSS 3.1 Score:** 8.6
- **CVSS Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N

### Affected Systems
- **Application:** CustomerPortal
- **Environment:** Production
- **Component:** Authentication Module
- **Code Location:** `src/auth/login.py:42`

### Regulatory Impact Assessment

#### PCI-DSS v4.0
- **Requirement:** 6.5.1 (Injection flaws, particularly SQL injection)
- **Compliance Status:** Non-Compliant
- **Business Impact:** Risk to cardholder data environment

#### SOC2
- **Trust Service Criteria:** CC7.1 (System monitoring to detect potential cyber threats)
- **Compliance Status:** Control Deficiency
- **Audit Impact:** Material weakness if not remediated

#### HIPAA
- **Security Rule:** 164.308(a)(1)(ii)(D) - Information system activity review
- **Compliance Status:** Non-Compliant
- **Risk:** Potential ePHI exposure

### Evidence
[Screenshot or code snippet showing vulnerability]

```python
# Vulnerable code at src/auth/login.py:42
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

### Risk Assessment
- **Likelihood:** High (public-facing endpoint, no authentication required)
- **Impact:** High (full database compromise, PCI/PHI exposure)
- **Overall Risk:** Critical

### Compensating Controls
[List any existing controls that partially mitigate the risk]
- None identified

### Remediation Plan
- **Required Action:** Implement parameterized queries
- **Responsible Party:** Development Team - Authentication Squad
- **Target Date:** 2025-12-11 (7 days per critical vulnerability policy)
- **Verification Method:**
  1. Code review confirms parameterized queries
  2. Re-scan shows no findings
  3. Penetration test confirms exploitation not possible

### Remediation Code
```python
# Remediated code
query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))
```

### Verification Evidence
[To be completed after remediation]
- [ ] Code review completed
- [ ] Re-scan clean
- [ ] Penetration test passed
- [ ] Audit evidence collected

### Audit Trail
- 2025-12-04 10:15 UTC: Finding discovered by automated scan
- 2025-12-04 11:30 UTC: Manual verification confirmed true positive
- 2025-12-04 14:00 UTC: Development team notified
- 2025-12-04 15:30 UTC: Remediation plan approved
- [To be updated with remediation and verification dates]
```

## Compliance Gap Analysis

### Assessment Methodology

For each compliance framework, assess:

1. **Control Coverage:** Are security controls implemented per standard?
2. **Control Effectiveness:** Are controls working as intended?
3. **Evidence Quality:** Is audit evidence sufficient?
4. **Remediation Status:** Are findings being addressed timely?

### Gap Report Format

```markdown
# Compliance Gap Analysis Report

## Framework: [PCI-DSS v4.0 / SOC2 / HIPAA / ISO 27001]

### Overall Compliance Score
[X]% Compliant

### Gap Summary

| Requirement | Status | Findings | Risk Level |
|-------------|--------|----------|----------|
| [ID] | Compliant / Partially Compliant / Non-Compliant | [Count] | [Risk] |

### Critical Gaps

#### Gap 1: [Requirement]
- **Description:** [What control is missing or ineffective]
- **Impact:** [Regulatory and business impact]
- **Root Cause:** [Why gap exists]
- **Remediation:** [What needs to be done]
- **Timeline:** [When it will be fixed]
- **Status:** [Open / In Progress / Closed]

### Audit Observations
[Auditor notes and recommendations]

### Management Response
[Management's plan to address gaps]
```

## Remediation Timeframes (Risk-Based)

Based on industry standards and compliance requirements:

| Severity | PCI-DSS | SOC2 | HIPAA | ISO 27001 |
|----------|---------|------|-------|-----------|
| Critical | 24 hours | Immediate | 24 hours | 24 hours |
| High | 7 days | 30 days | 30 days | 30 days |
| Medium | 30 days | 60 days | 60 days | 90 days |
| Low | 90 days | 90 days | 90 days | 90 days |

## Compliance Verification Checklist

For each remediated finding:

- [ ] Fix implemented and deployed
- [ ] Fix verified by security team
- [ ] Re-scan confirms vulnerability resolved
- [ ] Code changes peer-reviewed
- [ ] Evidence collected and documented
- [ ] Audit trail updated
- [ ] Compliance status updated
- [ ] Stakeholders notified

## References

### Compliance Standards
- [PCI-DSS v4.0](https://www.pcisecuritystandards.org/document_library/) - Payment card security
- [SOC2 TSC](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/serviceorganization-smanagement.html) - Trust Service Criteria
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html) - Healthcare security
- [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) - Information security management

### Regulatory Bodies
- [PCI SSC](https://www.pcisecuritystandards.org/) - PCI Standards Council
- [AICPA](https://www.aicpa.org/) - SOC2 oversight
- [HHS OCR](https://www.hhs.gov/ocr/) - HIPAA enforcement
- [ISO](https://www.iso.org/) - ISO standards

### Compliance Tools
- [OWASP Compliance Resources](https://owasp.org/www-project-compliance/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)

---

*For beginner-friendly explanations, use `security-triage-beginner.md`. For technical depth, use `security-triage-expert.md`.*
