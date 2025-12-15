---
description: Generate comprehensive security audit report from scan and triage results using security-reporter skill.
---

# /flow:security report - Security Audit Report Generator

Generate a comprehensive security audit report by aggregating scan results, triage findings, and patch recommendations into a stakeholder-ready document.

## User Input

```text
$ARGUMENTS
```

**Expected Input**: Optional feature slug or report options (e.g., `--format html`, `--format pdf`)

## Execution Instructions

This command generates a comprehensive security audit report using the Security Reporter skill. It reads security scan and triage results, analyzes findings, calculates security posture, maps vulnerabilities to OWASP Top 10, and produces actionable remediation recommendations.

### Phase 1: Data Collection and Validation

**Report progress**: Print "Phase 1: Collecting security scan and triage results..."

#### Step 1: Locate Security Data Files

```bash
# Check for required input files
SCAN_RESULTS="docs/security/scan-results.json"
TRIAGE_RESULTS="docs/security/triage-results.json"
PATCHES_DIR="docs/security/patches/"

if [ ! -f "$SCAN_RESULTS" ]; then
    echo "[X] Error: scan-results.json not found. Run /flow:security scan first to generate scan results."
    exit 1
fi

if [ ! -f "$TRIAGE_RESULTS" ]; then
    echo "[X] Error: triage-results.json not found. Run /flow:security triage first."
    exit 1
fi
```

#### Step 2: Load and Parse Data

Read the following files:

1. **Scan Results** (`docs/security/scan-results.json`)
   - Contains raw vulnerability findings from security scanners
   - Includes CVSS scores, CWE mappings, file locations

2. **Triage Results** (`docs/security/triage-results.json`)
   - Contains AI-triaged findings with severity classifications
   - Includes false positive analysis and prioritization

3. **Patch Files** (if exist in `docs/security/patches/`)
   - Contains generated fix patches for vulnerabilities
   - Link patches to corresponding findings

**Data Structure Example:**
```json
{
  "findings": [
    {
      "id": "VULN-001",
      "severity": "critical",
      "title": "SQL Injection in login endpoint",
      "cvss_score": 9.8,
      "cwe": "CWE-89",
      "owasp": "A03",
      "location": "src/auth/login.py:45",
      "description": "...",
      "impact": "...",
      "remediation": "...",
      "status": "open"
    }
  ]
}
```

**Phase 1 Success**: Print summary:
```
✅ Phase 1 Complete: Security data loaded
   Scan results: 23 findings
   Triage results: 18 findings (5 false positives)
   Patches: 3 available
```

---

### Phase 2: Security Analysis

**Report progress**: Print "Phase 2: Analyzing security posture and OWASP compliance..."

Invoke the **security-reporter skill** with the loaded data:

```
# SKILL INVOCATION: security-reporter

You are analyzing security scan and triage results to generate a comprehensive audit report.

## Input Data

### Scan Results
[Include full scan-results.json contents]

### Triage Results
[Include full triage-results.json contents]

### Available Patches
[List patch files from docs/security/patches/]

## Analysis Tasks

### Task 1: Calculate Security Posture

Apply the security posture formula:
- Count findings by severity (Critical, High, Medium, Low, Info)
- Determine posture: SECURE, CONDITIONAL, or AT RISK
- Justify posture determination

### Task 2: OWASP Top 10 Compliance Assessment

For each OWASP Top 10 category (A01-A10):
- Identify relevant findings
- Assess compliance status (Pass/Fail)
- Provide evidence and notes

### Task 3: Risk Analysis

- Identify most critical attack vectors
- Assess exploitability and business impact
- Prioritize findings by risk score

### Task 4: Remediation Planning

Group findings into three priority tiers:
1. **Immediate** (Critical/High - within 7 days)
2. **Short-term** (Medium - within 30 days)
3. **Long-term** (Low - within 90 days)

For each finding, provide:
- Specific remediation steps
- Estimated effort
- Recommended owner
- Suggested due date

## Output Format

Generate a complete audit report following this structure:

# Security Audit Report: [Feature Name]

**Feature**: [feature-slug]
**Date**: [YYYY-MM-DD]
**Security Assessor**: AI Security Reporter
**Version**: 1.0

## Executive Summary

[Non-technical summary for stakeholders]

**Overall Security Posture:** [SECURE | CONDITIONAL | AT RISK]

**Key Findings:**
- [N] Critical vulnerabilities requiring immediate attention
- [N] High severity issues to address within 7 days
- [N] Medium/Low issues for backlog

**Business Impact:**
[Brief description of business risk]

**Recommended Actions:**
1. [Priority 1 action] - Timeline: [timeframe]
2. [Priority 2 action] - Timeline: [timeframe]

## Security Assessment Summary

| Metric | Value |
|--------|-------|
| Total Findings | [N] |
| Critical | [N] |
| High | [N] |
| Medium | [N] |
| Low | [N] |
| Informational | [N] |
| False Positives | [N] |

### Overall Security Posture
- [x] **[SELECTED POSTURE]** - [Justification]
- [ ] [Other options]

## Detailed Findings

[For each vulnerability, use the detailed findings template from the skill]

### Critical Severity
[List critical findings with full details]

### High Severity
[List high findings with full details]

### Medium Severity
[List medium findings with full details]

### Low Severity
[List low findings with full details]

## Security Testing Performed

### Static Analysis (SAST)
- **Tools Used**: [List scanners]
- **Findings**: [Count]
- **False Positives**: [Count]

### Dependency Scanning (SCA)
- **Tools Used**: [List scanners]
- **Vulnerable Dependencies**: [Count]
- **Outdated Dependencies**: [Count]

### Secret Scanning
- **Tools Used**: [List scanners]
- **Secrets Found**: [Count]
- **Status**: [All remediated/Pending]

## OWASP Top 10 Compliance Checklist

[Include complete OWASP Top 10 compliance assessment from skill]

| Risk | Status | Notes |
|------|--------|-------|
| A01 Broken Access Control | [Pass/Fail] | [Evidence] |
| A02 Cryptographic Failures | [Pass/Fail] | [Evidence] |
| A03 Injection | [Pass/Fail] | [Evidence] |
| A04 Insecure Design | [Pass/Fail] | [Evidence] |
| A05 Security Misconfiguration | [Pass/Fail] | [Evidence] |
| A06 Vulnerable Components | [Pass/Fail] | [Evidence] |
| A07 Auth Failures | [Pass/Fail] | [Evidence] |
| A08 Data Integrity Failures | [Pass/Fail] | [Evidence] |
| A09 Logging Failures | [Pass/Fail] | [Evidence] |
| A10 SSRF | [Pass/Fail] | [Evidence] |

## Remediation Recommendations

### Immediate Actions (Critical/High - Within 7 Days)
[List prioritized actions with details]

### Short-term Actions (Medium - Within 30 Days)
[List prioritized actions with details]

### Long-term Improvements (Low - Within 90 Days)
[List prioritized actions with details]

### Process Improvements
[Recommendations to prevent similar issues]

## Sign-off

| Role | Name | Date | Approval |
|------|------|------|----------|
| Security Lead | [TBD] | [Date] | [ ] Approved |
| Dev Lead | [TBD] | [Date] | [ ] Acknowledged |
| Product Owner | [TBD] | [Date] | [ ] Accepted Risk |

### Conditions for Approval
- [ ] All critical vulnerabilities remediated or risk accepted
- [ ] All high vulnerabilities remediated or risk accepted with mitigation plan
- [ ] Security testing completed and documented

---

**Generated by**: `/flow:security report`
**Report Version**: 1.0
**Generated At**: [ISO 8601 timestamp]
```

**Phase 2 Success**: Print summary:
```
✅ Phase 2 Complete: Security analysis finished
   Security Posture: AT RISK
   OWASP Compliance: 6/10 categories pass
   Findings analyzed: 18
   Remediation priorities: 3 immediate, 8 short-term, 7 long-term
```

---

### Phase 3: Report Generation

**Report progress**: Print "Phase 3: Writing audit report to docs/security/..."

#### Step 1: Write Markdown Report

Write the generated report to `docs/security/audit-report.md`:

```bash
# Ensure security directory exists
mkdir -p docs/security

# Write the report (skill output from Phase 2)
# [AI-generated markdown content goes here]
```

**Validation:**
- [ ] All required sections present
- [ ] Executive summary is non-technical
- [ ] All findings have severity, description, remediation
- [ ] OWASP checklist complete
- [ ] Remediation priorities clear

#### Step 2: Generate Additional Formats (Optional)

If user requested HTML or PDF format:

**HTML Generation:**
```bash
if [ "$FORMAT" = "html" ] || [ "$FORMAT" = "all" ]; then
    # Convert markdown to HTML using Pandoc
    pandoc docs/security/audit-report.md \
        -o docs/security/audit-report.html \
        --standalone \
        --css=security-report.css \
        --metadata title="Security Audit Report"

    echo "✅ HTML report: docs/security/audit-report.html"
fi
```

**PDF Generation:**
```bash
if [ "$FORMAT" = "pdf" ] || [ "$FORMAT" = "all" ]; then
    # Convert HTML to PDF using wkhtmltopdf
    wkhtmltopdf docs/security/audit-report.html docs/security/audit-report.pdf

    echo "✅ PDF report: docs/security/audit-report.pdf"
fi
```

**Note:** HTML/PDF generation requires Pandoc and wkhtmltopdf to be installed. If not available, skip gracefully with a warning.

**Phase 3 Success**: Print summary:
```
✅ Phase 3 Complete: Audit report generated
   Markdown: docs/security/audit-report.md
   HTML: docs/security/audit-report.html (if requested)
   PDF: docs/security/audit-report.pdf (if requested)
```

---

### Phase 4: Task Integration (Optional)

**Report progress**: Print "Phase 4: Creating remediation tasks in backlog..."

For each critical/high severity finding, create a backlog task:

```bash
# Example: Create task for critical vulnerability
backlog task create "Security: Fix SQL injection in login endpoint" \
  -d "Address VULN-001: SQL injection vulnerability in src/auth/login.py:45" \
  --ac "Parameterized queries implemented" \
  --ac "Input validation added" \
  --ac "Security test added" \
  -l security,critical \
  --priority critical \
  -a @backend-engineer
```

**Task Creation Strategy:**
- Create tasks for **Critical and High** findings only
- Use vulnerability ID in description for traceability
- Set priority based on severity
- Include acceptance criteria from remediation recommendations

**Phase 4 Success**: Print summary:
```
✅ Phase 4 Complete: Remediation tasks created
   Critical tasks: 3
   High tasks: 8
   Total backlog items: 11
```

---

## Workflow Complete

Display final summary:

```
================================================================================
SECURITY AUDIT REPORT COMPLETE
================================================================================

Security Posture: AT RISK

Report Generated:
- Markdown: docs/security/audit-report.md
- HTML: docs/security/audit-report.html
- PDF: docs/security/audit-report.pdf

Key Findings:
- Critical: 3
- High: 8
- Medium: 5
- Low: 2

Immediate Action Required:
1. Fix SQL injection in login endpoint (VULN-001)
2. Remediate authentication bypass (VULN-002)
3. Patch XSS vulnerability in admin panel (VULN-003)

Remediation Tasks Created: 11

Next Steps:
1. Review the audit report: docs/security/audit-report.md
2. Assign remediation tasks to engineers
3. Track progress in backlog.md
4. Re-run scan after fixes to verify remediation
================================================================================
```

---

## Command Help

**Command**: `/flow:security report [options]`

**Purpose**: Generate comprehensive security audit report from scan and triage results.

**Options**:
- `--format markdown` - Generate markdown report only (default)
- `--format html` - Generate HTML report
- `--format pdf` - Generate PDF report
- `--format all` - Generate all formats
- `--no-tasks` - Skip creating backlog tasks for findings

**Prerequisites**:
- Run `/flow:security scan` to generate scan-results.json
- Run `/flow:security triage` to generate triage-results.json

**Output Files**:
- `docs/security/audit-report.md` - Primary markdown report
- `docs/security/audit-report.html` - HTML export (optional)
- `docs/security/audit-report.pdf` - PDF export (optional)

**Examples**:

```bash
# Generate markdown report
/flow:security report

# Generate HTML and PDF reports
/flow:security report --format all

# Generate report without creating backlog tasks
/flow:security report --no-tasks
```

**Report Sections**:
1. Executive Summary (non-technical)
2. Security Assessment Summary
3. Detailed Findings by Severity
4. Security Testing Performed
5. OWASP Top 10 Compliance Checklist
6. Remediation Recommendations (prioritized)
7. Sign-off Section

**See Also**:
- `/flow:security scan` - Run security scanners
- `/flow:security triage` - Triage scan results
- `/flow:security fix` - Generate fix patches
