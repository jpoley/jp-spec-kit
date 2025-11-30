# JPSpec Workflow Artifact Flow

**Version:** 1.0.0
**Status:** Reference Documentation
**Last Updated:** 2025-11-30

---

## Overview

This document provides a comprehensive reference for the complete JPSpec workflow, including:

- **State transitions** - How tasks progress through the development lifecycle
- **Artifact requirements** - What must be created/validated at each transition
- **Validation modes** - How transitions are gated and verified
- **Rework and rollback** - Handling failures and production issues
- **Troubleshooting** - Common validation failures and remediation

This documentation complements the programmatic workflow definition in `jpspec_workflow.yml` at the project root.

---

## Workflow State Diagram

The JPSpec workflow is a state machine with 8 states and 12 valid transitions:

```
[To Do]
   |
   | (1) /jpspec:specify
   v
[Specified]
   |
   +----> (2) /jpspec:research -----> [Researched]
   |                                       |
   |          +----------------------------+
   |          |
   |          | (4) /jpspec:plan
   +----------+
   |
   | (3) /jpspec:plan (skip research)
   v
[Planned]
   |
   | (5) /jpspec:implement
   v
[In Implementation] <-----(10) rework----+
   |                                     |
   |                                     |
   | (6) /jpspec:validate                |
   v                                     |
[Validated] <---------(11) rework--------+
   |                                     |
   |                                     |
   | (7) /jpspec:operate                 |
   v                                     |
[Deployed] <--------(12) rollback--------+
   |
   +----> (8) manual -----> [Done]
   |
   +----> (9) manual (from Validated) -----> [Done]

Note: Direct transitions to [Done] also possible from [In Implementation]
      via manual transition (not shown for clarity).
```

---

## Transition Reference Table

| # | From State | To State | Command | Input Artifacts | Output Artifacts | Validation Mode |
|---|------------|----------|---------|-----------------|------------------|-----------------|
| 1 | To Do | Specified | /jpspec:specify | None | PRD.md, backlog tasks | KEYWORD["PRD"] |
| 2 | Specified | Researched | /jpspec:research | PRD.md | research.md, validation.md | KEYWORD["research", "validation"] |
| 3 | Specified | Planned | /jpspec:plan | PRD.md | architecture.md, adr/*.md, platform.md | KEYWORD["ADR"] |
| 4 | Researched | Planned | /jpspec:plan | PRD.md, research.md | architecture.md, adr/*.md, platform.md | KEYWORD["ADR"] |
| 5 | Planned | In Implementation | /jpspec:implement | ADRs, PRD | Code, tests, review notes | KEYWORD["tests"] + AC checks |
| 6 | In Implementation | Validated | /jpspec:validate | Code, tests | QA report, security report, docs | KEYWORD["security", "test report"] |
| 7 | Validated | Deployed | /jpspec:operate | All validated artifacts | CI/CD config, K8s manifests, runbooks | KEYWORD["runbook", "pipeline"] |
| 8 | Deployed | Done | manual | Production verification | Release notes | PULL_REQUEST |
| 9 | Validated | Done | manual | Validation complete | Release notes | PULL_REQUEST |
| 10 | In Implementation | Planned | rework | Failing tests, review feedback | Updated ADRs | NONE |
| 11 | Validated | In Implementation | rework | QA/security findings | Fixed code | NONE |
| 12 | Deployed | Validated | rollback | Production incident | Incident report | NONE |

---

## Artifact Location Reference

All workflow artifacts are stored in the `.specify/` directory structure within the project:

| Artifact Type | Directory | Filename Pattern | Example |
|---------------|-----------|------------------|---------|
| PRD | `.specify/spec/` | `prd.md` | `.specify/spec/prd.md` |
| Research Report | `.specify/research/` | `research.md` | `.specify/research/research.md` |
| Business Validation | `.specify/research/` | `validation.md` | `.specify/research/validation.md` |
| Architecture Design | `.specify/design/` | `architecture.md` | `.specify/design/architecture.md` |
| ADRs | `.specify/design/adr/` | `NNN-<title>.md` | `.specify/design/adr/001-auth-protocol.md` |
| Platform Design | `.specify/design/` | `platform.md` | `.specify/design/platform.md` |
| QA Test Report | `.specify/validation/` | `qa-report.md` | `.specify/validation/qa-report.md` |
| Security Report | `.specify/validation/` | `security-report.md` | `.specify/validation/security-report.md` |
| API Documentation | `.specify/docs/` | `api.md` | `.specify/docs/api.md` |
| User Documentation | `.specify/docs/` | `user-guide.md` | `.specify/docs/user-guide.md` |
| Release Notes | `.specify/docs/` | `release-notes.md` | `.specify/docs/release-notes.md` |
| CI/CD Pipeline | `.specify/ops/` | `pipeline.yml` | `.specify/ops/pipeline.yml` |
| Kubernetes Manifests | `.specify/ops/k8s/` | `*.yaml` | `.specify/ops/k8s/deployment.yaml` |
| Runbooks | `.specify/ops/runbooks/` | `*.md` | `.specify/ops/runbooks/high-latency.md` |
| Incident Reports | `.specify/ops/incidents/` | `YYYY-MM-DD-<title>.md` | `.specify/ops/incidents/2025-11-30-payment-outage.md` |

**Directory Structure**:
```
.specify/
├── spec/               # Requirements and specifications
│   └── prd.md
├── research/           # Market research and business validation
│   ├── research.md
│   └── validation.md
├── design/             # Architecture and platform design
│   ├── architecture.md
│   ├── platform.md
│   └── adr/            # Architecture Decision Records
│       ├── 001-auth-protocol.md
│       └── 002-database-choice.md
├── validation/         # QA and security reports
│   ├── qa-report.md
│   └── security-report.md
├── docs/               # Documentation
│   ├── api.md
│   ├── user-guide.md
│   └── release-notes.md
└── ops/                # Operational artifacts
    ├── pipeline.yml
    ├── k8s/            # Kubernetes manifests
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── runbooks/       # Operational runbooks
    │   ├── high-latency.md
    │   └── payment-failure.md
    └── incidents/      # Incident reports
        └── 2025-11-30-payment-outage.md
```

---

## Validation Modes

Each transition can be validated using one of three modes:

### 1. NONE (No Validation)

**Description**: Transition is allowed without artifact validation.

**When Used**:
- Rework transitions (failures expected, no artifact validation needed)
- Rollback transitions (emergency situations, validation would slow recovery)

**Examples**:
- Transition #10: In Implementation → Planned (rework)
- Transition #11: Validated → In Implementation (rework)
- Transition #12: Deployed → Validated (rollback)

**Behavior**:
```bash
# No artifact checks performed
# Transition allowed immediately
backlog task edit 42 -s "Planned"  # From "In Implementation" (rework)
```

---

### 2. KEYWORD["..."] (Keyword Validation)

**Description**: Transition requires specific artifacts to exist with keyword presence in content.

**When Used**:
- Forward workflow transitions (normal progression)
- Ensures required artifacts are created before progression

**Validation Logic**:
```python
def validate_keyword_transition(transition, keywords):
    """Validate transition requires specific keywords in artifacts."""
    for keyword in keywords:
        artifact_path = get_artifact_path(transition, keyword)
        if not os.path.exists(artifact_path):
            raise ValidationError(f"Missing artifact: {artifact_path}")

        content = read_file(artifact_path)
        if keyword.lower() not in content.lower():
            raise ValidationError(f"Keyword '{keyword}' not found in {artifact_path}")

    return True
```

**Examples**:

#### Transition #1: To Do → Specified
```yaml
validation:
  mode: KEYWORD
  keywords: ["PRD"]
  artifacts:
    - path: ".specify/spec/prd.md"
      required_sections:
        - "Executive Summary"
        - "User Stories"
        - "Acceptance Criteria"
```

**Validation Check**:
```bash
# Verifies:
# 1. File exists: .specify/spec/prd.md
# 2. Content contains "PRD" keyword
# 3. Required sections present
```

#### Transition #2: Specified → Researched
```yaml
validation:
  mode: KEYWORD
  keywords: ["research", "validation"]
  artifacts:
    - path: ".specify/research/research.md"
      required_sections:
        - "Market Analysis"
        - "Competitive Landscape"
    - path: ".specify/research/validation.md"
      required_sections:
        - "Business Viability"
        - "Go/No-Go Recommendation"
```

#### Transition #3, #4: Planned
```yaml
validation:
  mode: KEYWORD
  keywords: ["ADR"]
  artifacts:
    - path: ".specify/design/architecture.md"
    - path: ".specify/design/adr/*.md"  # At least one ADR
      min_count: 1
```

#### Transition #5: Planned → In Implementation
```yaml
validation:
  mode: KEYWORD
  keywords: ["tests"]
  artifacts:
    - code: "src/**/*.{ts,go,py}"
    - tests: "tests/**/*.{test.ts,_test.go,test_*.py}"
      min_coverage: 80
  acceptance_criteria:
    all_checked: true  # All ACs must be checked
```

#### Transition #6: In Implementation → Validated
```yaml
validation:
  mode: KEYWORD
  keywords: ["security", "test report"]
  artifacts:
    - path: ".specify/validation/qa-report.md"
      required_sections:
        - "Test Results"
        - "Performance Metrics"
    - path: ".specify/validation/security-report.md"
      required_sections:
        - "Security Findings"
        - "Compliance Status"
```

#### Transition #7: Validated → Deployed
```yaml
validation:
  mode: KEYWORD
  keywords: ["runbook", "pipeline"]
  artifacts:
    - path: ".specify/ops/pipeline.yml"
    - path: ".specify/ops/runbooks/*.md"
      min_count: 1  # At least one runbook per alert
    - path: ".specify/ops/k8s/*.yaml"
      min_count: 2  # At least deployment + service
```

---

### 3. PULL_REQUEST (PR Validation)

**Description**: Transition requires a merged pull request as evidence of completion.

**When Used**:
- Terminal transitions to "Done" state
- Ensures all work is code-reviewed and CI-validated before completion

**Validation Logic**:
```python
def validate_pr_transition(task_id):
    """Validate transition requires merged PR."""
    task = get_task(task_id)

    # Check for PR reference in task notes
    pr_pattern = r'PR #(\d+)'
    match = re.search(pr_pattern, task.notes)

    if not match:
        raise ValidationError("No PR reference found in task notes")

    pr_number = match.group(1)

    # Verify PR is merged (using GitHub API)
    pr = github.get_pr(pr_number)
    if not pr.merged:
        raise ValidationError(f"PR #{pr_number} not merged")

    # Verify CI passed
    if not pr.ci_passed:
        raise ValidationError(f"PR #{pr_number} CI checks failed")

    return True
```

**Examples**:

#### Transition #8: Deployed → Done
```yaml
validation:
  mode: PULL_REQUEST
  requires:
    - pr_merged: true
    - ci_passed: true
    - approvals: 1  # Release manager approval
    - production_verified: true
```

**Workflow**:
```bash
# 1. Create PR with deployment artifacts
git checkout -b deploy-user-auth
git add .specify/ops/*
git commit -s -m "feat: deploy user authentication to production"
git push -u origin deploy-user-auth

# 2. Create PR
gh pr create --title "Deploy: User Authentication" --body "..."

# 3. After PR merge, update task
backlog task edit 42 --notes "Completed via PR #123" -s Done
```

#### Transition #9: Validated → Done
```yaml
validation:
  mode: PULL_REQUEST
  requires:
    - pr_merged: true
    - ci_passed: true
    - approvals: 1
  note: "Used when deployment is deferred but validation is complete"
```

---

## Rework and Rollback Transitions

### Rework Transitions (Backward, Quality Issues)

**Purpose**: Handle quality issues discovered during validation or implementation.

**Characteristics**:
- **No validation required** (NONE mode) - failures expected
- **Backward state progression** - return to earlier phase
- **Preserve context** - implementation notes explain failure reason

#### Transition #10: In Implementation → Planned (Rework)

**Trigger**: Implementation reveals architectural flaws requiring redesign.

**Common Scenarios**:
- Performance bottleneck discovered during implementation
- Integration pattern doesn't scale
- Security architecture inadequate

**Workflow**:
```bash
# 1. Identify architectural issue during implementation
# Engineer adds notes explaining problem
backlog task edit 42 --notes $'Implementation Issue: Database design does not support required query patterns

Problem:
- Current schema requires N+1 queries for user dashboard
- Performance unacceptable (>5s load time)

Recommendation:
- Rework data model to use denormalized view
- Add caching layer
- Update ADR-003 with decision rationale'

# 2. Transition back to Planned (rework)
backlog task edit 42 -s "Planned"

# 3. Architect updates design
# - Revise architecture.md
# - Create new ADR-004 for caching strategy
# - Update platform.md with cache infrastructure

# 4. Resume implementation after design fixes
backlog task edit 42 -s "In Implementation"
```

**Validation**: NONE (no artifact checks)

---

#### Transition #11: Validated → In Implementation (Rework)

**Trigger**: QA or security validation reveals critical issues requiring code changes.

**Common Scenarios**:
- Security vulnerability discovered (SQL injection, XSS, auth bypass)
- Critical functional bug (payment processing fails, data loss)
- Performance regression (p95 latency >1s)

**Workflow**:
```bash
# 1. Security Engineer finds critical vulnerability
backlog task edit 42 --notes $'Security Review: CRITICAL - SQL Injection Vulnerability

Finding:
- User input not sanitized in search endpoint
- CVE severity: Critical (CVSS 9.8)
- Attack vector: /api/search?q=<payload>

Recommendation:
- Use parameterized queries (REQUIRED)
- Add input validation
- Implement rate limiting'

# 2. Transition back to In Implementation (rework)
backlog task edit 42 -s "In Implementation"
backlog task edit 42 --uncheck-ac 2  # Security AC no longer satisfied

# 3. Engineer fixes vulnerability
# - Update search endpoint to use parameterized queries
# - Add input validation
# - Add security tests

# 4. Re-check AC after fix
backlog task edit 42 --check-ac 2

# 5. Resume validation
backlog task edit 42 -s "Validated"
```

**Validation**: NONE (no artifact checks)

---

### Rollback Transition (Emergency, Production)

#### Transition #12: Deployed → Validated (Rollback)

**Trigger**: Production incident requires immediate rollback.

**Common Scenarios**:
- Critical bug in production (payment processing fails, auth bypass)
- Performance degradation (p95 latency >5s, error rate >5%)
- Security incident (breach detected, vulnerability exploited)

**Workflow**:
```bash
# 1. Incident detected in production
# SRE creates incident report
cat > .specify/ops/incidents/2025-11-30-payment-failure.md <<EOF
# Incident Report: Payment Processing Failure

**Date**: 2025-11-30 14:23 UTC
**Severity**: Critical
**Impact**: 100% payment failures
**Duration**: 14:23 - 14:45 UTC (22 minutes)

## Timeline
- 14:23 - Alert: Payment success rate dropped to 0%
- 14:25 - Incident declared, on-call paged
- 14:28 - Root cause identified: Database connection pool exhausted
- 14:30 - Decision: Rollback deployment
- 14:35 - Rollback completed
- 14:40 - Payment processing restored
- 14:45 - Incident resolved

## Root Cause
- New deployment increased database connections 10x
- Connection pool size not increased
- All connections exhausted under load

## Action Items
- [ ] Increase connection pool size (task-123)
- [ ] Add connection pool monitoring (task-124)
- [ ] Load test before deployment (task-125)
EOF

# 2. Rollback deployment
kubectl rollout undo deployment/payment-service

# 3. Update task status (rollback)
backlog task edit 42 -s "Validated"
backlog task edit 42 --notes $'ROLLBACK: Production incident

Incident: Payment processing failure (100% error rate)
Root Cause: Database connection pool exhaustion
Action: Rolled back deployment
Status: Incident resolved, deployment rolled back

Next Steps:
- Fix connection pool configuration
- Add load testing to validation phase
- Re-deploy after fixes verified'

# 4. Create follow-up tasks for fixes
backlog task create "Fix: Increase database connection pool" \
  --ac "Update connection pool configuration" \
  --ac "Add connection pool monitoring" \
  --ac "Load test with 10x traffic" \
  -l bugfix,production \
  --priority high
```

**Validation**: NONE (emergency situation, speed critical)

**Post-Rollback**:
- Incident report created (`.specify/ops/incidents/`)
- Root cause analysis documented
- Follow-up tasks created to fix underlying issue
- Re-deploy after fixes validated

---

## Troubleshooting

### Validation Failure: Missing Artifact

**Symptom**:
```
ERROR: Transition validation failed
Missing artifact: .specify/spec/prd.md
Transition: To Do → Specified requires PRD
```

**Diagnosis**:
```bash
# Check if artifact directory exists
ls -la .specify/spec/

# Check if file exists
ls -la .specify/spec/prd.md
```

**Resolution**:
```bash
# Ensure agent created the artifact
# Re-run the workflow command to generate missing artifact
/jpspec:specify User authentication system

# Verify artifact was created
ls -la .specify/spec/prd.md

# Retry transition
backlog task edit 42 -s "Specified"
```

**Prevention**:
- Ensure workflow commands complete successfully before transition
- Verify agent output includes artifact creation messages
- Use validation checklist before attempting transition

---

### Validation Failure: Missing Keyword

**Symptom**:
```
ERROR: Transition validation failed
Keyword 'ADR' not found in .specify/design/architecture.md
Transition: Researched → Planned requires ADR keyword
```

**Diagnosis**:
```bash
# Check if keyword is present
grep -i "ADR" .specify/design/architecture.md

# Check if ADRs were created
ls -la .specify/design/adr/
```

**Resolution**:
```bash
# If no ADRs exist, agent didn't create them
# Re-run planning workflow with explicit ADR requirement
/jpspec:plan User authentication architecture

# Ensure Software Architect creates ADRs
# Expected output: ADR-001-auth-protocol.md, ADR-002-session-management.md

# Verify ADRs were created
ls -la .specify/design/adr/

# Verify architecture.md references ADRs
grep -i "ADR" .specify/design/architecture.md

# Retry transition
backlog task edit 42 -s "Planned"
```

**Prevention**:
- Review agent context to ensure ADR creation is explicit responsibility
- Verify agent output includes ADR creation messages
- Use architecture checklist requiring minimum 2 ADRs per feature

---

### Validation Failure: Missing PR Reference

**Symptom**:
```
ERROR: Transition validation failed
No PR reference found in task notes
Transition: Deployed → Done requires merged PR
```

**Diagnosis**:
```bash
# Check task notes for PR reference
backlog task 42 --plain | grep "PR #"

# Expected format: "Completed via PR #123" or "PR #123"
```

**Resolution**:
```bash
# Add PR reference to task notes
backlog task edit 42 --notes "Completed via PR #123"

# Verify PR is merged
gh pr view 123

# Retry transition
backlog task edit 42 -s "Done"
```

**Prevention**:
- Always create PR before marking task Done
- Include PR reference in task notes using format: "PR #NNN"
- Verify PR is merged before transition

---

### Validation Failure: PR Not Merged

**Symptom**:
```
ERROR: Transition validation failed
PR #123 not merged
Transition: Deployed → Done requires merged PR
```

**Diagnosis**:
```bash
# Check PR status
gh pr view 123

# Check PR checks
gh pr checks 123
```

**Resolution**:
```bash
# If PR checks failing, fix issues
# If PR awaiting review, get approval

# After PR merged:
backlog task edit 42 -s "Done"
```

**Prevention**:
- Ensure CI passes before attempting transition
- Get required approvals before transition
- Verify PR merge status: `gh pr view 123 | grep "State: MERGED"`

---

### Validation Failure: Acceptance Criteria Not Checked

**Symptom**:
```
ERROR: Transition validation failed
Acceptance criteria not complete
Transition: Planned → In Implementation requires all ACs checked
```

**Diagnosis**:
```bash
# Check AC status
backlog task 42 --plain

# Look for unchecked ACs: [ ] instead of [x]
```

**Resolution**:
```bash
# Complete missing ACs
# Then check them:
backlog task edit 42 --check-ac 3

# Verify all ACs checked
backlog task 42 --plain

# Retry transition
backlog task edit 42 -s "In Implementation"
```

**Prevention**:
- Check ACs progressively during implementation
- Use checklist before transition
- Code reviewers verify AC completion

---

### Validation Failure: Test Coverage Below Threshold

**Symptom**:
```
ERROR: Transition validation failed
Test coverage: 65% (threshold: 80%)
Transition: Planned → In Implementation requires 80% coverage
```

**Diagnosis**:
```bash
# Run coverage report
pytest --cov=src tests/
# or
go test -coverprofile=coverage.out ./...

# Check coverage by file
pytest --cov=src --cov-report=term-missing tests/
```

**Resolution**:
```bash
# Add tests for uncovered code
# Focus on files with <80% coverage

# Re-run coverage
pytest --cov=src tests/

# Verify coverage meets threshold (≥80%)

# Retry transition
backlog task edit 42 -s "In Implementation"
```

**Prevention**:
- Write tests during implementation (not after)
- Monitor coverage during development
- Use TDD to ensure coverage from start

---

### Validation Failure: Runbook Missing

**Symptom**:
```
ERROR: Transition validation failed
Missing runbook: .specify/ops/runbooks/
Transition: Validated → Deployed requires runbooks
```

**Diagnosis**:
```bash
# Check if runbooks directory exists
ls -la .specify/ops/runbooks/

# Check if runbooks created for alerts
ls -la .specify/ops/runbooks/*.md
```

**Resolution**:
```bash
# Create runbook for each alert
# Example: High latency alert

cat > .specify/ops/runbooks/high-latency.md <<EOF
# Runbook: High Latency Alert

## Alert
- **Name**: HighLatency
- **Condition**: p95 latency >1s for 5 minutes
- **Severity**: Medium

## Initial Triage
1. Check service status: kubectl get pods -n payment
2. Check error rate: Check Grafana dashboard
3. Check upstream dependencies: Verify database and cache

## Common Causes
1. Database slow queries (N+1, missing indexes)
2. Cache miss rate high (cold cache)
3. Upstream service degradation

## Resolution Steps
1. Scale up pods: kubectl scale deployment/payment --replicas=5
2. Restart pods: kubectl rollout restart deployment/payment
3. Clear cache if needed: redis-cli FLUSHDB

## Escalation
- Primary: @sre-team
- Secondary: @backend-team
- Executive: @engineering-manager

## Rollback Procedure
kubectl rollout undo deployment/payment
EOF

# Verify runbook created
ls -la .specify/ops/runbooks/high-latency.md

# Retry transition
backlog task edit 42 -s "Deployed"
```

**Prevention**:
- SRE agent must create runbook for each alert
- Use runbook template for consistency
- Verify runbook creation before deployment

---

## Programmatic Access

The authoritative workflow definition is available in `jpspec_workflow.yml` at the project root. Tools and scripts can programmatically access workflow configuration:

### Python Example

```python
import yaml
from pathlib import Path

def load_workflow_config(path: Path = Path("jpspec_workflow.yml")) -> dict:
    """Load workflow configuration."""
    with open(path) as f:
        return yaml.safe_load(f)

def get_valid_transitions(current_state: str) -> list[dict]:
    """Get valid transitions from current state."""
    config = load_workflow_config()
    transitions = config["transitions"]

    return [t for t in transitions if t["from"] == current_state]

def validate_transition(from_state: str, to_state: str) -> bool:
    """Validate if transition is allowed."""
    valid = get_valid_transitions(from_state)
    return any(t["to"] == to_state for t in valid)

# Usage
if validate_transition("To Do", "Specified"):
    print("Transition allowed")
else:
    print("Invalid transition")

# Get next states
next_states = [t["to"] for t in get_valid_transitions("Specified")]
print(f"Valid next states: {next_states}")
# Output: Valid next states: ['Researched', 'Planned']
```

### Bash Example

```bash
#!/bin/bash
# Get valid transitions from current state

get_valid_transitions() {
    local current_state="$1"

    # Use yq to query workflow YAML
    yq eval ".transitions[] | select(.from == \"$current_state\") | .to" jpspec_workflow.yml
}

# Usage
current_state="Specified"
echo "Valid transitions from $current_state:"
get_valid_transitions "$current_state"

# Output:
# Researched
# Planned
```

### TypeScript Example

```typescript
import yaml from 'js-yaml';
import fs from 'fs';
import path from 'path';

interface Transition {
  from: string;
  to: string;
  via: string;
  description?: string;
}

interface WorkflowConfig {
  version: string;
  states: string[];
  workflows: Record<string, any>;
  transitions: Transition[];
  agent_loops: {
    inner: { agents: string[] };
    outer: { agents: string[] };
  };
  metadata: Record<string, any>;
}

function loadWorkflowConfig(filePath = 'jpspec_workflow.yml'): WorkflowConfig {
  const content = fs.readFileSync(filePath, 'utf8');
  return yaml.load(content) as WorkflowConfig;
}

function getValidTransitions(currentState: string): Transition[] {
  const config = loadWorkflowConfig();
  return config.transitions.filter(t => t.from === currentState);
}

function validateTransition(fromState: string, toState: string): boolean {
  const validTransitions = getValidTransitions(fromState);
  return validTransitions.some(t => t.to === toState);
}

// Usage
const nextStates = getValidTransitions('Specified').map(t => t.to);
console.log('Valid next states:', nextStates);
// Output: Valid next states: [ 'Researched', 'Planned' ]

if (validateTransition('To Do', 'Specified')) {
  console.log('Transition allowed');
}
```

### Validation Script

```python
#!/usr/bin/env python3
"""Validate workflow artifacts before transition."""

import sys
import yaml
from pathlib import Path

def validate_keyword_transition(transition: dict) -> bool:
    """Validate KEYWORD transition mode."""
    keywords = transition.get("keywords", [])

    for keyword in keywords:
        # Map keyword to artifact path
        artifact_map = {
            "PRD": ".specify/spec/prd.md",
            "research": ".specify/research/research.md",
            "validation": ".specify/research/validation.md",
            "ADR": ".specify/design/adr/",
            "tests": "tests/",
            "security": ".specify/validation/security-report.md",
            "test report": ".specify/validation/qa-report.md",
            "runbook": ".specify/ops/runbooks/",
            "pipeline": ".specify/ops/pipeline.yml",
        }

        artifact_path = Path(artifact_map.get(keyword, ""))

        # Check if artifact exists
        if not artifact_path.exists():
            print(f"ERROR: Missing artifact: {artifact_path}")
            return False

        # For files, check keyword presence
        if artifact_path.is_file():
            content = artifact_path.read_text()
            if keyword.lower() not in content.lower():
                print(f"ERROR: Keyword '{keyword}' not found in {artifact_path}")
                return False

        # For directories, check at least one file exists
        elif artifact_path.is_dir():
            files = list(artifact_path.glob("*.md"))
            if not files:
                print(f"ERROR: No files in directory: {artifact_path}")
                return False

    return True

def validate_pr_transition(task_notes: str) -> bool:
    """Validate PULL_REQUEST transition mode."""
    import re

    # Check for PR reference
    pr_pattern = r'PR #(\d+)'
    match = re.search(pr_pattern, task_notes)

    if not match:
        print("ERROR: No PR reference found in task notes")
        return False

    pr_number = match.group(1)
    print(f"Found PR reference: #{pr_number}")

    # TODO: Verify PR is merged using GitHub API
    # For now, just verify reference exists

    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: validate-transition.py <from_state> <to_state>")
        sys.exit(1)

    from_state = sys.argv[1]
    to_state = sys.argv[2]

    # Load workflow config
    config = yaml.safe_load(Path("jpspec_workflow.yml").read_text())

    # Find transition
    transition = None
    for t in config["transitions"]:
        if t["from"] == from_state and t["to"] == to_state:
            transition = t
            break

    if not transition:
        print(f"ERROR: Invalid transition: {from_state} → {to_state}")
        sys.exit(1)

    print(f"Validating transition: {from_state} → {to_state}")

    # Determine validation mode (would be in extended config)
    # For demo, use keyword validation for forward transitions
    if transition["via"] in ["rework", "rollback", "manual"]:
        print("Validation mode: NONE (no checks required)")
        sys.exit(0)

    # Keyword validation
    print("Validation mode: KEYWORD")
    if not validate_keyword_transition(transition):
        sys.exit(1)

    print("Validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
# Validate transition before attempting
./validate-transition.py "To Do" "Specified"

# If validation passes, transition allowed
backlog task edit 42 -s "Specified"
```

---

## Related Documentation

- **JPSpec Workflow Schema**: `docs/reference/workflow-schema.md` - Complete schema definition
- **JPSpec Workflow Guide**: `docs/guides/jpspec-workflow-guide.md` - User-facing workflow guide
- **Workflow Configuration**: `jpspec_workflow.yml` - Authoritative workflow definition
- **Agent Loop Classification**: `docs/reference/agent-loop-classification.md` - Inner/outer loop agents
- **Backlog User Guide**: `docs/guides/backlog-user-guide.md` - Task management

---

**Maintenance Notes**:
- This document should be updated when `jpspec_workflow.yml` changes
- Validation examples should be tested with actual workflow commands
- Artifact location table should match template directory structure
- Troubleshooting section should be expanded based on common issues

---

**Version History**:
- 1.0.0 (2025-11-30): Initial release with 8 states, 12 transitions, 3 validation modes
