---
id: task-214
title: Build Security Audit Report Generator
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-04 21:20'
labels:
  - 'workflow:Planned'
  - security
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
## CORRECTED Implementation Plan

**CRITICAL: AI generates markdown, Python formats output.**

### Phase 1: AI Skill Creation
- Create `.claude/skills/security-reporter.md`
  - Instructions for audit report structure
  - Executive summary format
  - Technical details section
  - Remediation roadmap
  - Compliance mapping
- Skill is markdown prompt, NOT Python code

### Phase 2: Slash Command
- Create `.claude/commands/jpspec-security-report.md`
  - Invokes security-reporter skill
  - Reads triage-results.json and patches/
  - AI coding tool generates markdown
  - Writes `docs/security/audit-report.md`

### Phase 3: Python Formatting (Optional)
- Create `src/specify_cli/commands/security_report.py`
  - Read audit-report.md
  - Convert to HTML using Pandoc
  - Convert to PDF using wkhtmltopdf
  - **NO AI logic, just format conversion**

### Phase 4: Report Templates
- Create report sections:
  - Executive Summary
  - Finding Overview
  - Risk Analysis
  - Remediation Plan
  - Compliance Status

### Success Criteria
- [ ] security-reporter.md skill created
- [ ] Slash command invokes skill
- [ ] AI generates markdown report
- [ ] Optional HTML/PDF export
- [ ] **ZERO API DEPENDENCIES**

### Files Created
- `.claude/skills/security-reporter.md`
- `.claude/commands/jpspec-security-report.md`
- `src/specify_cli/commands/security_report.py`
- `docs/security/audit-report.md` (generated)
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary (2025-12-04)

### What Was Implemented

Created the Security Audit Report Generator for JP Spec Kit, implementing the /jpspec:security report command. This completes Wave 2 of the security implementation, building on task-212 (Triage Engine).

**Core Components:**
1. **Security Reporter Skill** (`.claude/skills/security-reporter/SKILL.md`)
   - Comprehensive AI skill for generating security audit reports
   - Includes OWASP Top 10 compliance assessment framework
   - Security posture calculation logic (SECURE/CONDITIONAL/AT RISK)
   - Detailed remediation roadmap generation

2. **Slash Command** (`/jpspec:security report`)
   - Command template with 4-phase workflow
   - Reads scan-results.json and triage-results.json
   - Invokes security-reporter skill for AI-powered analysis
   - Generates markdown, HTML, and PDF formats
   - Creates backlog tasks for critical/high findings

3. **Report Guidelines** (`memory/security/report-guidelines.md`)
   - Security posture calculation rules
   - CVSS to severity mapping
   - OWASP Top 10 2021 category definitions
   - Report structure standards
   - Quality checklist

4. **Template Integration**
   - Symlink created: `.claude/commands/jpspec/security_report.md`
   - Uses existing `templates/security-report-template.md`

### Key Design Decisions

1. **Zero API Dependencies**: All AI logic in markdown skills, Python only for format conversion
2. **OWASP Top 10 2021**: Used latest OWASP categories for compliance mapping
3. **Three-Tier Posture**: SECURE/CONDITIONAL/AT RISK based on critical/high vulnerability presence
4. **Multi-Format Output**: Markdown (primary), HTML, PDF (optional via Pandoc/wkhtmltopdf)
5. **Backlog Integration**: Auto-creates tasks for critical/high findings

### Files Created

- `.claude/skills/security-reporter/SKILL.md` - AI skill for report generation
- `templates/skills/security-reporter/SKILL.md` - Template copy
- `templates/commands/jpspec/security_report.md` - Command template
- `.claude/commands/jpspec/security_report.md` - Symlink to template
- `memory/security/report-guidelines.md` - Report standards and guidelines

### Testing Performed

- ✅ Skill structure validated (follows existing patterns)
- ✅ Command template validated (follows /jpspec pattern)
- ✅ Symlink created correctly
- ✅ OWASP Top 10 categories verified against 2021 standard
- ✅ Security posture formula validated

### Validation Results

**Architecture Compliance:**
- ✅ Zero API calls - all AI logic in skills
- ✅ Follows existing skill/command patterns
- ✅ Integrates with backlog.md workflow
- ✅ Uses existing security-report-template.md

**Quality Standards:**
- ✅ Comprehensive OWASP Top 10 coverage
- ✅ Clear security posture calculation
- ✅ Executive summary guidance for non-technical stakeholders
- ✅ Detailed remediation roadmap structure
- ✅ Consistent terminology with existing security docs

### Next Steps

1. Implement task-215: /jpspec:security CLI commands (scan, triage, fix, report)
2. Test complete workflow: scan → triage → report → remediation
3. Create integration tests for report generation
4. Add example security report to documentation
<!-- SECTION:NOTES:END -->
