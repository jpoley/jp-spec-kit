---
name: "flow-security_triage"
description: "Triage security scan findings using AI-powered analysis with persona-specific output."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
---
# /flow:security_triage

Triage security scan findings using AI-powered analysis with persona-specific output.

## Purpose

This command analyzes security findings from scanners (Semgrep, CodeQL, Bandit) and provides:
- Classification (True Positive, False Positive, Needs Investigation)
- Risk scoring using Raptor formula: (Impact × Exploitability) / Detection_Time
- Plain-English explanations tailored to expertise level
- Remediation guidance
- Root cause clustering

## Prerequisites

- Security scan results available (from `/flow:security scan`)
- Configuration file at `.flowspec/security-config.yml`
- Findings to triage (JSON or SARIF format)

## Workflow

### 1. Load Configuration

Read the security configuration to determine persona and settings:

```bash
# Check if config exists
if [ -f .flowspec/security-config.yml ]; then
    echo "Using configuration from .flowspec/security-config.yml"
else
    echo "No configuration found. Using defaults (expert persona)."
fi
```

**Configuration Parameters:**
- `triage.persona` - Output style: `beginner`, `expert`, `compliance`
- `triage.confidence_threshold` - Minimum confidence for classification (0.0-1.0)
- `triage.auto_dismiss_fp` - Auto-dismiss false positives below threshold
- `triage.cluster_similar` - Group findings by root cause

### 2. Select Persona Skill

Based on the `persona` configuration, invoke the appropriate triage skill:

```markdown
**Persona Selection Logic:**

- If `persona: beginner` -> Use **security-triage-beginner** skill
  - Simple, non-technical explanations
  - Step-by-step fixes with code examples
  - Learning resources and tutorials
  - Explanations under 100 words

- If `persona: expert` -> Use **security-triage-expert** skill
  - Technical depth with CWE/CVE references
  - Advanced exploitation scenarios
  - Performance and edge case considerations
  - Defense in depth strategies

- If `persona: compliance` -> Use **security-triage-compliance** skill
  - Regulatory mapping (PCI-DSS, SOC2, HIPAA, ISO 27001)
  - Audit evidence format
  - Compliance status assessment
  - Remediation timeframes per policy

- If no persona specified -> Default to **expert**
```

### 3. Load Findings

Load security findings from the most recent scan:

```bash
# Find most recent scan results
SCAN_RESULTS=$(ls -t .flowspec/security-reports/*.json 2>/dev/null | head -1)

if [ -z "$SCAN_RESULTS" ]; then
    echo "ERROR: No scan results found. Run /flow:security scan first."
    exit 1
fi

echo "Triaging findings from: $SCAN_RESULTS"
```

### 4. Invoke Triage Skill

Using the selected persona skill, analyze each finding:

**For each finding:**

1. **Extract finding details:**
   - ID, title, description
   - CWE, severity, CVSS score
   - File path, line numbers
   - Code snippet with context

2. **Classify:**
   - Analyze code context and data flow
   - Determine if user input reaches dangerous sink
   - Check for validation/sanitization
   - Return classification (TP/FP/NI) with confidence

3. **Score risk:**
   - Impact: CVSS score or AI-estimated (0-10)
   - Exploitability: AI-estimated likelihood (0-10)
   - Detection time: Days since code written (git blame)
   - Risk = (Impact × Exploitability) / Detection_Time

4. **Generate explanation:**
   - Use persona-specific format and language
   - Provide What, Why, How to Exploit (if TP), How to Fix
   - Include references appropriate to persona

5. **Cluster findings:**
   - Group by CWE category (≥3 findings)
   - Group by file (≥2 findings)
   - Identify systemic issues

### 5. Generate Report

Create triage report with persona-specific formatting:

**Report Structure:**

```markdown
# Security Triage Report

**Generated:** [ISO 8601 timestamp]
**Persona:** [beginner/expert/compliance]
**Total Findings:** [count]
**Classification Breakdown:**
- True Positive: [count] ([percentage]%)
- False Positive: [count] ([percentage]%)
- Needs Investigation: [count] ([percentage]%)

## Executive Summary
[High-level overview of findings and risk]

## Critical Findings (Risk Score > 8.0)
[Findings sorted by risk score, highest first]

## High Priority Findings (Risk Score 5.0-8.0)
[Findings sorted by risk score]

## Medium Priority Findings (Risk Score 2.0-5.0)
[Findings sorted by risk score]

## Low Priority Findings (Risk Score < 2.0)
[Findings sorted by risk score]

## Clustered Findings (Systemic Issues)
[Findings grouped by root cause with fix recommendations]

## Remediation Summary
[Top remediations that would fix multiple findings]

## False Positives
[Findings classified as false positives with reasoning]
[Only included if reporting.include_false_positives: true]
```

### 6. Output Report

Save report and display summary:

```bash
# Save report
REPORT_FILE=".flowspec/security-reports/triage-$(date +%Y%m%d-%H%M%S).md"
echo "Triage report saved to: $REPORT_FILE"

# Display summary
echo "
Triage Complete
===============
Total Findings: [count]
True Positive: [count]
False Positive: [count]
Needs Investigation: [count]

Critical Risk: [count]
High Risk: [count]
Medium Risk: [count]
Low Risk: [count]

Report: $REPORT_FILE
"
```

## Persona Examples

### Beginner Mode Example

```markdown
## Finding: SQL Injection in Authentication

### What Is This?
Your login form has a security hole. Someone could type special characters
in the username field to trick the database into giving them access without
a password.

### Why Does It Matter?
An attacker could:
- Log in as any user (including administrators)
- Steal all user data from the database
- Delete or modify data

### How Do I Fix It?
1. Open the file `src/auth/login.py`
2. Find line 42 where it says:
   ```python
   query = f"SELECT * FROM users WHERE username = '{username}'"
   ```
3. Change it to:
   ```python
   query = "SELECT * FROM users WHERE username = %s"
   cursor.execute(query, (username,))
   ```
4. The `%s` is a placeholder. It keeps the username safe.

### Learn More
- [What is SQL Injection?](https://owasp.org/www-community/attacks/SQL_Injection)
- [How to prevent it](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
```

### Expert Mode Example

```markdown
## Finding: SQL Injection (CWE-89)

### Vulnerability Analysis
- **CWE:** CWE-89 - SQL Injection
- **CVSS 3.1:** 9.8 (Critical) - CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
- **Attack Vector:** Network (unauthenticated public endpoint)
- **Complexity:** Low (trivial exploitation, public PoCs)

### Technical Description
String concatenation in SQL query construction allows second-order SQL injection.
User input flows through `request.form['username']` -> `build_query()` -> `cursor.execute()`
without sanitization or parameterization. No WAF or input validation present.

### Exploitation Analysis
- **Exploitability:** Critical (9.0/10)
- **Attack Scenario:**
  ```bash
  # Boolean-based blind injection
  POST /api/login
  username=admin' AND (SELECT 1 FROM users WHERE username='admin' AND password LIKE 'a%')--

  # UNION-based data exfiltration
  username=' UNION SELECT password,email,1 FROM users WHERE '1'='1

  # Time-based blind injection
  username=admin' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE 0 END)='0
  ```
- **Prerequisites:** None (public endpoint, no rate limiting, no WAF)
- **Impact:** Full database compromise, lateral movement via stored credentials

### Remediation
- **Immediate Fix:**
  ```python
  # Use parameterized queries
  cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                 (username, password_hash))
  ```
- **Defense in Depth:**
  - Input validation: `^[a-zA-Z0-9_-]{3,20}$`
  - WAF rule: ModSecurity CRS SQL injection rules
  - Least privilege: Read-only DB user for authentication
  - Query logging: Alert on `UNION`, `--`, `/**/`
- **Performance:** Parameterization adds <0.5ms per query

### References
- [CWE-89](https://cwe.mitre.org/data/definitions/89.html)
- [SQLMap](https://sqlmap.org/) - Automated exploitation tool
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection)
```

### Compliance Mode Example

```markdown
## Finding: SQL Injection Vulnerability

### Classification
- **CWE:** CWE-89 - Improper Neutralization of Special Elements in SQL Command
- **OWASP Top 10 2021:** A03:2021 - Injection
- **Severity:** Critical
- **CVSS 3.1 Score:** 9.8

### Regulatory Impact
- **PCI-DSS v4.0:**
  - Requirement 6.5.1: Injection flaws, particularly SQL injection
  - Status: **Non-Compliant** (Failed control test)
- **SOC2:**
  - CC7.1: System monitoring to detect potential cyber threats
  - Status: **Control Deficiency** (Material weakness)
- **HIPAA:**
  - 164.308(a)(1)(ii)(D): Information system activity review
  - 164.312(c)(1): Integrity controls
  - Status: **Non-Compliant** (ePHI at risk)
- **ISO 27001:2022:**
  - A.14.2.1: Secure development policy
  - Status: **Non-Compliant**

### Evidence
- **Location:** `src/auth/login.py:42`
- **Discovery Date:** 2025-12-04T18:30:00Z
- **Scanner:** Semgrep v1.50.0
- **Rule:** python.lang.security.audit.sqli.string-concat
- **Verification:** Manual code review confirmed true positive (2025-12-04T19:00:00Z)

### Compliance Status
- **Status:** Non-Compliant
- **Risk Rating:** Critical
- **Required Remediation Timeframe:** 24 hours (per critical vulnerability policy)
- **Business Impact:** Potential PCI-DSS non-compliance, SOC2 Type II material weakness

### Remediation
- **Required Actions:**
  1. Implement parameterized SQL queries per OWASP SQL Injection Prevention Cheat Sheet
  2. Code review to identify similar patterns across codebase
  3. Deploy fix to all environments (dev, staging, production)
  4. Update secure coding standards documentation
  5. Developer training on SQL injection prevention
- **Verification Method:**
  - [ ] Code review confirms parameterized queries used
  - [ ] Static analysis re-scan shows no SQL injection findings
  - [ ] Dynamic testing (penetration test) confirms not exploitable
  - [ ] Audit evidence collected and filed
- **Responsible Party:** Development Team - Authentication Squad (Lead: John Doe)
- **Target Date:** 2025-12-05T18:30:00Z (24 hours)

### Audit Notes
**Control Effectiveness Assessment:**
Input validation control (PCI-DSS 6.5.1) ineffective. String concatenation
in SQL query construction bypasses parameterization controls. No secondary
controls (WAF, input validation) in place.

**Compensating Controls:** None identified.

**Root Cause:** Lack of secure coding training, missing code review checklist
for SQL injection vulnerabilities, inadequate SAST integration in CI/CD.

**Evidence Collection:**
- Source code snapshot: `evidence/security/SF-2025-001-code.txt`
- Scan report: `evidence/security/SF-2025-001-scan.json`
- Manual verification notes: `evidence/security/SF-2025-001-verification.md`

**Remediation Verification:**
- Post-remediation code review required (security team sign-off)
- Re-scan must show clean (no SQL injection findings)
- Penetration test must confirm not exploitable
- Evidence documented in `evidence/security/SF-2025-001-remediation.md`

**Audit Trail:**
- 2025-12-04 18:30 UTC: Finding discovered (automated scan)
- 2025-12-04 19:00 UTC: Manual verification (security analyst)
- 2025-12-04 19:30 UTC: Development team notified (ticket SEC-2025-001)
- 2025-12-04 20:00 UTC: Remediation plan approved (security manager)
- [Pending] 2025-12-05 18:30 UTC: Target remediation date
- [Pending] Verification and closure
```

## Command Options

```bash
/flow:security_triage [OPTIONS]

Options:
  --persona [beginner|expert|compliance]  Override config persona
  --input FILE                            Scan results file (JSON/SARIF)
  --output FILE                           Output report file
  --confidence FLOAT                      Override confidence threshold
  --format [markdown|html|json]           Report format
  --interactive                           Interactive mode (confirm each classification)
  --cluster                               Enable finding clustering
  --no-cluster                            Disable finding clustering
```

## Integration with Backlog

After triage, findings can be converted to backlog tasks:

```bash
# For each True Positive finding:
backlog task create "Fix [finding title]" \
  -d "[finding description]" \
  --ac "Implement remediation per triage report" \
  --ac "Verify fix with re-scan" \
  --ac "Update documentation if needed" \
  -l security,bug \
  --priority high

# Add triage report reference to task notes
backlog task edit [task-id] --notes "See triage report: [report-file]"
```

## Error Handling

- **No scan results found:** Prompt to run `/flow:security scan` first
- **Invalid configuration:** Use default settings, warn user
- **Persona not recognized:** Default to `expert` persona
- **LLM API errors:** Fall back to rule-based classification, warn user
- **Git blame errors:** Use default detection time (30 days)

## Performance Considerations

- **Parallel processing:** Triage findings concurrently (up to 10 at a time)
- **Caching:** Cache classification results for identical findings
- **Batch requests:** Group LLM requests to reduce API overhead
- **Progress indicators:** Show progress for large finding sets (>20)

## Success Criteria

- All findings classified (TP/FP/NI)
- Risk scores calculated
- Report generated in persona-specific format
- Clusters identified (if enabled)
- Exit code 0 if successful, 1 if errors

## Related Commands

- `/flow:security scan` - Run security scanners
- `/flow:security fix` - Apply automated fixes
- `/flow:security report` - Generate comprehensive security report

## References

- [Security Triage Guidelines](../../../memory/security/triage-guidelines.md)
- [ADR-006: AI Triage Engine Design](../../../docs/adr/ADR-006-ai-triage-engine-design.md)
- [Security Configuration Schema](../../../docs/security/config-schema.yaml)
