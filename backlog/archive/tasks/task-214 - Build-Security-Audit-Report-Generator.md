---
id: task-214
title: Build Security Audit Report Generator
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-05 16:43'
labels:
  - security
  - implement
  - reporting
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate comprehensive security audit reports using security-report-template.md. Implements /jpspec:security audit command.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Aggregate data from scan and triage results
- [x] #2 Populate security-report-template.md with findings
- [x] #3 Calculate security posture (Secure/Conditional/At Risk)
- [x] #4 Generate OWASP Top 10 compliance checklist
- [x] #5 Support multiple output formats (markdown, HTML, PDF)
- [x] #6 Include remediation recommendations with priority
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Security Audit Report Generator

### Architecture Reference
- ADR-006: AI Triage Engine Design (reporting section)
- Existing: src/specify_cli/security/reporter/generator.py (skeleton exists)
- Pattern: Template Method (GoF) + Message Translator (EIP)

### Current State Analysis
Report generator has:
- ReportGenerator class with generate() method
- FindingSummary calculation
- Security posture determination
- OWASP compliance checking (via owasp.py)
- Remediation generation

### Implementation Steps

#### Step 1: Complete Security Report Template (3-4 hours)
**Files:**
- templates/security-report-template.md (create/enhance)
- src/specify_cli/security/reporter/template.py (new)

**Tasks:**
1. Design comprehensive template structure
   ```markdown
   # Security Audit Report
   
   ## Executive Summary
   - Security Posture: [Secure/Conditional/At Risk]
   - Total Findings: X (Critical: Y, High: Z, ...)
   - True Positives: X, False Positives: Y
   - Scan Date: [timestamp]
   - Scanners Used: [Semgrep, CodeQL, ...]
   
   ## Risk Assessment
   - Overall Risk Score: X/100
   - Critical Issues Requiring Immediate Action: X
   - High-Priority Issues: X
   
   ## Findings Summary
   ### By Severity
   [Table: Severity | Count | Status]
   
   ### By CWE Category
   [Table: CWE | Description | Count | Risk]
   
   ### By File/Module
   [Table: File | Findings | Risk Score]
   
   ## OWASP Top 10 Compliance
   [Checklist with status for each category]
   
   ## Detailed Findings
   [For each critical/high finding: full details]
   
   ## Remediation Roadmap
   [Prioritized list of fixes with effort estimates]
   
   ## Appendices
   - A: Scan Configuration
   - B: Tool Versions
   - C: False Positive Analysis
   ```

2. Create Jinja2 template processor
   - Load template from file
   - Support variable substitution
   - Support loops and conditionals
   - Handle missing data gracefully

3. Add template validation
   - Check all required sections present
   - Verify Jinja2 syntax
   - Test with sample data

**Validation:**
- Generate report from template with test data
- Verify all sections render correctly

#### Step 2: Enhance OWASP Top 10 Compliance Checker (3-4 hours)
**Files:**
- src/specify_cli/security/reporter/owasp.py

**Tasks:**
1. Implement OWASP Top 10 2021 mapping
   - A01:2021 - Broken Access Control
   - A02:2021 - Cryptographic Failures
   - A03:2021 - Injection
   - A04:2021 - Insecure Design
   - A05:2021 - Security Misconfiguration
   - A06:2021 - Vulnerable and Outdated Components
   - A07:2021 - Identification and Authentication Failures
   - A08:2021 - Software and Data Integrity Failures
   - A09:2021 - Security Logging and Monitoring Failures
   - A10:2021 - Server-Side Request Forgery (SSRF)

2. Create CWE → OWASP mapping
   ```python
   OWASP_MAPPING = {
       "A03:2021": ["CWE-89", "CWE-79", "CWE-78", ...],  # Injection
       "A02:2021": ["CWE-327", "CWE-328", ...],          # Crypto
       ...
   }
   ```

3. Implement compliance status logic
   - Compliant: No findings in category
   - Partially Compliant: Low/medium findings only
   - Non-Compliant: Critical/high findings present

4. Add recommendations per category
   - Specific guidance for each OWASP category
   - Link to OWASP documentation
   - Reference internal security policies

**Validation:**
- Test with findings covering all 10 categories
- Verify status determination is accurate

#### Step 3: Implement Security Posture Calculator (2-3 hours)
**Files:**
- src/specify_cli/security/reporter/generator.py
- src/specify_cli/security/reporter/models.py

**Tasks:**
1. Refine posture determination algorithm
   ```python
   def calculate_posture(summary: FindingSummary, owasp: list) -> SecurityPosture:
       score = 100
       score -= summary.critical * 20  # Critical = -20 each
       score -= summary.high * 10      # High = -10 each
       score -= summary.medium * 3     # Medium = -3 each
       
       non_compliant = count_non_compliant(owasp)
       score -= non_compliant * 5      # -5 per category
       
       if score >= 90: return SECURE
       if score >= 70: return CONDITIONAL
       return AT_RISK
   ```

2. Add trend analysis (if historical data available)
   - Compare to previous scan
   - Show improvement/regression
   - Calculate velocity (findings fixed per week)

3. Add risk quantification
   - Estimate potential impact ($)
   - Time to remediate (hours)
   - Probability of exploitation (%)

4. Generate executive summary text
   - AI-generated natural language summary
   - Highlight key risks
   - Provide actionable recommendations

**Validation:**
- Test with various finding sets
- Verify posture aligns with intuition

#### Step 4: Implement Multi-Format Export (4-5 hours)
**Files:**
- src/specify_cli/security/exporters/ (existing)
- Add: html_exporter.py, pdf_exporter.py
- Enhance: markdown.py, sarif.py, json.py

**Tasks:**
1. Enhance Markdown exporter
   - Use report template
   - Add syntax highlighting for code snippets
   - Generate table of contents
   - Include charts (using ASCII art or mermaid)

2. Implement HTML exporter
   - Convert Markdown to HTML (using markdown library)
   - Add CSS styling (professional report style)
   - Include interactive charts (Chart.js or similar)
   - Add filtering/sorting for findings table
   - Support dark/light mode

3. Implement PDF exporter
   - Use weasyprint or reportlab
   - Generate from HTML (easiest path)
   - Include title page, headers, footers
   - Page numbers and table of contents
   - Professional formatting

4. Enhance SARIF exporter
   - Ensure GitHub Code Scanning compatibility
   - Include all metadata
   - Validate against SARIF schema
   - Add tool version info

5. Add format selection
   - --format flag: markdown|html|pdf|sarif|json
   - --format all: generate all formats
   - Save to docs/security/{feature}-audit-report.{ext}

**Validation:**
- Generate all formats from same data
- Verify content is consistent across formats
- Test SARIF upload to GitHub Code Scanning

#### Step 5: Implement Remediation Roadmap (3-4 hours)
**Files:**
- src/specify_cli/security/reporter/generator.py
- src/specify_cli/security/reporter/remediation.py (new)

**Tasks:**
1. Enhance remediation prioritization
   - Consider: severity, exploitability, detection time
   - Group by cluster (systemic fixes first)
   - Estimate effort (hours/days)
   - Suggest order (dependencies, quick wins)

2. Add effort estimation
   ```python
   EFFORT_MAP = {
       "critical": "8-16 hours",
       "high": "4-8 hours", 
       "medium": "2-4 hours",
       "low": "1-2 hours"
   }
   ```
   - Adjust based on complexity (clustering factor)
   - Consider automated fix availability

3. Generate sprint plan
   - Week 1: Critical + high-impact quick wins
   - Week 2-3: Remaining high + systemic fixes
   - Week 4: Medium priority
   - Backlog: Low priority

4. Add success metrics
   - Vulnerability reduction target
   - Time to secure baseline
   - Resources required (person-days)

**Validation:**
- Generate roadmap for 50 findings
- Verify prioritization makes sense

#### Step 6: Add Compliance Mode Support (2-3 hours)
**Files:**
- src/specify_cli/security/reporter/compliance.py (new)
- src/specify_cli/security/reporter/generator.py

**Tasks:**
1. Implement SOC2 compliance mode
   - Map findings to SOC2 controls
   - Generate evidence of scanning
   - Include timestamps and tool versions
   - Add auditor-friendly formatting

2. Implement ISO 27001 mode
   - Map to ISO 27001 controls
   - Include risk assessment
   - Document remediation process

3. Implement HIPAA mode
   - Focus on data protection
   - Highlight PHI exposure risks
   - Document encryption status

4. Add compliance flag
   - --compliance soc2|iso27001|hipaa|none
   - Adjust report sections accordingly
   - Include relevant attestations

**Validation:**
- Generate reports in each compliance mode
- Verify appropriate sections included

#### Step 7: Integration and Testing (3-4 hours)
**Files:**
- tests/security/test_report_generator.py
- tests/security/test_exporters.py

**Tasks:**
1. Create end-to-end test
   - Scan → Triage → Generate report → Verify content
2. Test all export formats
   - Verify content consistency
   - Check file generation
   - Validate SARIF schema
3. Test error handling
   - Missing findings data
   - Invalid template
   - Export failures
4. Performance testing
   - 100 findings → report in <30 seconds
5. Visual regression testing
   - Generate HTML/PDF samples
   - Manual review for formatting

**Validation:**
- All tests pass
- Reports are professional and readable

### Dependencies
- Jinja2 (template engine)
- markdown (Markdown → HTML conversion)
- weasyprint or reportlab (PDF generation)
- Chart.js or plotly (charts in HTML)
- SARIF JSON schema (validation)

### Success Criteria
- [ ] Report includes all required sections per template
- [ ] OWASP Top 10 compliance checker covers all categories
- [ ] Security posture calculation is accurate
- [ ] Multi-format export works (Markdown, HTML, PDF, SARIF)
- [ ] Compliance modes (SOC2, ISO27001, HIPAA) supported
- [ ] Remediation roadmap is prioritized and actionable
- [ ] Report generation completes in <30 seconds

### Risks & Mitigations
**Risk:** PDF generation failures due to weasyprint dependencies
**Mitigation:** Provide HTML export as alternative, document PDF setup

**Risk:** SARIF export incompatible with GitHub Code Scanning
**Mitigation:** Validate against official schema, test upload to GitHub

**Risk:** Reports too technical for executives
**Mitigation:** Executive summary with natural language, risk quantification

### Estimated Effort
**Total: 20-27 hours (2.5-3.5 days)**
<!-- SECTION:PLAN:END -->
