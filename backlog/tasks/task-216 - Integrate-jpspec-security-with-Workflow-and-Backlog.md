---
id: task-216
title: 'Integrate /jpspec:security with Workflow and Backlog'
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-04 14:20'
labels:
  - security
  - implement
  - workflow
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire /jpspec:security commands into jpspec_workflow.yml and add backlog.md task creation for findings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add optional pre-commit hook integration
- [ ] #2 Implement --create-tasks flag to auto-create backlog tasks for findings
- [ ] #3 Task format includes severity, CWE, location, AI explanation
- [ ] #4 Document workflow integration options (validate extension, dedicated state)
- [ ] #5 CI/CD integration examples (GitHub Actions, GitLab CI)
- [ ] #6 SARIF output for GitHub Code Scanning
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Integrate /jpspec:security with Workflow and Backlog

### Overview
Wire /jpspec:security commands into jpspec_workflow.yml state machine and add automatic backlog.md task creation for security findings.

### Step-by-Step Implementation

#### Step 1: Add Security State to Workflow Configuration (2 hours)
**File**: `jpspec_workflow.yml`

1. Add optional security state:
   ```yaml
   states:
     - name: "Security Reviewed"
       description: "Security scan completed, findings triaged"
       entry_criteria:
         - "All critical/high vulnerabilities fixed or exempted"
   
   workflows:
     security:
       command: "/jpspec:security"
       agents: ["security-scanner"]
       input_states: ["In Implementation", "Validated"]
       output_state: "Security Reviewed"
   ```

2. Alternative: extend validate workflow:
   ```yaml
   workflows:
     validate:
       agents:
         - quality-guardian
         - secure-by-design-engineer
         - security-scanner  # New agent
   ```

3. Document both integration patterns

#### Step 2: Implement --create-tasks Flag (3 hours)
**File**: `src/specify_cli/security/backlog_integration.py`

```python
def create_backlog_tasks_from_findings(findings: List[Finding], feature: str):
    """Create backlog tasks for security findings."""
    for finding in findings:
        if finding.severity in ["critical", "high"]:
            task_title = f"Fix {finding.severity} security issue: {finding.title}"
            
            description = f"""
Security finding from scan:
- **CWE**: {finding.cwe_id}
- **OWASP**: {finding.owasp_category}
- **Location**: {finding.location.file}:{finding.location.line}
- **Rule**: {finding.rule_id}

{finding.ai_explanation}
"""
            
            acceptance_criteria = [
                f"Fix vulnerability at {finding.location.file}:{finding.location.line}",
                "Re-run security scan to verify fix",
                "Add test to prevent regression"
            ]
            
            subprocess.run([
                "backlog", "task", "create",
                task_title,
                "-d", description,
                "--ac", acceptance_criteria[0],
                "--ac", acceptance_criteria[1],
                "--ac", acceptance_criteria[2],
                "-l", f"security,{finding.severity},{feature}",
                "--priority", "high" if finding.severity == "critical" else "medium"
            ])
```

####Step 3: Add CI/CD Integration Examples (2 hours)
**Files**: `docs/platform/security-cicd-integration.md` (already exists), update with workflow examples

1. GitHub Actions integration
2. GitLab CI integration  
3. Jenkins integration
4. Pre-commit hook setup

#### Step 4: Implement SARIF Output (2 hours)
**File**: `src/specify_cli/security/sarif_export.py`

```python
def export_to_sarif(findings: List[Finding], tool: str) -> dict:
    """Export findings to SARIF 2.1.0 format."""
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "JP Spec Kit Security",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/yourusername/jp-spec-kit"
                }
            },
            "results": [
                {
                    "ruleId": f.rule_id,
                    "level": severity_to_sarif_level(f.severity),
                    "message": {"text": f.description},
                    "locations": [{
                        "physicalLocation": {
                            "artifactLocation": {"uri": f.location.file},
                            "region": {
                                "startLine": f.location.line,
                                "startColumn": f.location.column
                            }
                        }
                    }]
                }
                for f in findings
            ]
        }]
    }
```

#### Step 5: Document Workflow Integration (1 hour)
**File**: `docs/guides/security-workflow-integration.md`

Sections:
1. Adding security to workflow states
2. Using --create-tasks for automatic backlog population
3. CI/CD integration patterns
4. SARIF upload to GitHub Security tab

#### Step 6: Testing (2 hours)
- Test workflow state transitions
- Test task creation from findings
- Test SARIF export validates against schema
- Test GitHub Security tab integration

### Dependencies
- Workflow system implementation
- Backlog.md MCP tools
- Security scan command (task-210)

### Estimated Effort
**Total**: 12 hours (1.5 days)
<!-- SECTION:PLAN:END -->
