#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
# ]
# ///
"""
Specify CLI - Setup tool for Specify projects

Usage:
    uvx flowspec-cli.py init <project-name>
    uvx flowspec-cli.py init .
    uvx flowspec-cli.py init --here

Or install globally:
    uv tool install --from flowspec-cli.py flowspec-cli
    flowspec init <project-name>
    flowspec init .
    flowspec init --here
"""

import json
import logging
import os
import shlex
import shutil
import ssl
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import httpx
import readchar
import truststore
import typer
import yaml
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from typer.core import TyperGroup

from flowspec_cli.placeholders import (
    detect_project_metadata,
    replace_placeholders,
)
from flowspec_cli.telemetry.cli import telemetry_app

# Module-level logger
logger = logging.getLogger(__name__)

ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)


def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None.

    Checks in order: cli_token, GITHUB_TOKEN env var, GITHUB_FLOWSPEC env var.
    """
    token = cli_token or os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_FLOWSPEC") or ""
    return token.strip() or None


def _github_headers(cli_token: str | None = None, *, skip_auth: bool = False) -> dict:
    """Return GitHub API headers including optional Authorization, Accept and User-Agent.

    Args:
        cli_token: Optional token to use (falls back to GITHUB_FLOWSPEC env var)
        skip_auth: If True, never include Authorization header (for public repo fallback)
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "flowspec/flowspec-cli",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if not skip_auth:
        token = _github_token(cli_token)
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
    },
    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
    },
    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    },
    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "qwen": {
        "name": "Qwen Code",
        "folder": ".qwen/",
        "install_url": "https://github.com/QwenLM/qwen-code",
        "requires_cli": True,
    },
    "opencode": {
        "name": "opencode",
        "folder": ".opencode/",
        "install_url": "https://opencode.ai",
        "requires_cli": True,
    },
    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    },
    "windsurf": {
        "name": "Windsurf",
        "folder": ".windsurf/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "kilocode": {
        "name": "Kilo Code",
        "folder": ".kilocode/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "auggie": {
        "name": "Auggie CLI",
        "folder": ".augment/",
        "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        "requires_cli": True,
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "folder": ".codebuddy/",
        "install_url": "https://www.codebuddy.ai/cli",
        "requires_cli": True,
    },
    "roo": {
        "name": "Roo Code",
        "folder": ".roo/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "q": {
        "name": "Amazon Q Developer CLI",
        "folder": ".amazonq/",
        "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
        "requires_cli": True,
    },
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

CONSTITUTION_TIER_CHOICES = {
    "light": "Minimal controls for startups/hobby projects",
    "medium": "Standard controls for typical business projects",
    "heavy": "Enterprise controls for regulated environments",
}

# Embedded VS Code Copilot agent templates (bundled with package for reliable access)
# These are the 6 key workflow commands that appear in VS Code's agent menu
COPILOT_AGENT_TEMPLATES = {
    "flow.assess.agent.md": """---
name: FlowAssess
description: "Evaluate feature complexity and determine SDD workflow approach (full SDD, spec-light, or skip)."
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

handoffs:
  - label: "Create Specification"
    agent: "flow.specify"
    prompt: "Assessment complete. Create the feature specification and PRD."
    send: false
---

# /flow:assess - Feature Assessment

Evaluate feature complexity and recommend the appropriate SDD workflow mode.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command evaluates whether a feature requires the full SDD workflow, a lighter approach, or can skip formal specification entirely.

**Purpose:**
- Analyze feature complexity and scope
- Recommend appropriate workflow mode
- Create initial backlog task for tracking

**Workflow Modes:**

| Mode | When to Use | Artifacts |
|------|-------------|-----------|
| **Full SDD** | Complex features, multiple components, significant risk | PRD, ADRs, full spec |
| **Spec-Light** | Medium complexity, clear requirements | Light spec, tasks |
| **Skip SDD** | Simple changes, bug fixes, trivial updates | Just tasks |

**Assessment Criteria:**
1. **Scope**: How many files/components affected?
2. **Risk**: Security, data, or user-facing impact?
3. **Complexity**: New patterns, integrations, or dependencies?
4. **Clarity**: Are requirements well-defined?
5. **Duration**: Single session or multi-session work?

**Workflow:**
1. Gather feature description from user
2. Search codebase for related code and patterns
3. Assess complexity using criteria above
4. Recommend workflow mode with rationale
5. Create initial backlog task

**Key Commands:**
```bash
# Search for related code
grep -r "feature_keyword" src/

# Check existing tasks
backlog search "$ARGUMENTS" --plain

# Create assessment task
backlog task create "Assess: [Feature Name]" \\
  -d "Complexity assessment for feature" \\
  --ac "Determine workflow mode" \\
  --ac "Create initial task structure" \\
  -l assess \\
  --priority medium
```

**Output:**
- Assessment report with recommended mode
- Initial backlog task created
- Workflow state set to `Assessed`

After assessment, suggest running `/flow:specify` for Full SDD or Spec-Light modes.
""",
    "flow.specify.agent.md": """---
name: FlowSpecify
description: "Create or update feature specifications using PM planner agent (manages /spec.tasks)."
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

handoffs:
  - label: "Create Technical Design"
    agent: "flow.plan"
    prompt: "The specification is complete. Create the technical architecture and platform design."
    send: false
---

# /flow:specify - Feature Specification

Create comprehensive Product Requirements Documents (PRDs) using the PM Planner agent.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command creates feature specifications following SVPG product management principles.

**Prerequisites:**
1. Run `/flow:assess` first to evaluate complexity and create initial task
2. Have a clear feature description or user problem to solve

**Workflow:**
1. Discover existing backlog tasks related to this feature
2. Create a comprehensive PRD with:
   - Executive summary and problem statement
   - User stories with acceptance criteria
   - DVF+V risk assessment (Value, Usability, Feasibility, Viability)
   - Functional and non-functional requirements
   - Task breakdown using backlog CLI
3. Create implementation tasks in the backlog

**Key Commands:**
```bash
# Search for existing tasks
backlog search "$ARGUMENTS" --plain

# Create implementation tasks
backlog task create "Implement [Feature]" \
  -d "Description" \
  --ac "Acceptance criterion 1" \
  --ac "Acceptance criterion 2" \
  -l implement,backend \
  --priority high
```

**Output:**
- PRD document in `docs/prd/`
- Implementation tasks in backlog with acceptance criteria
- Workflow state updated to `Specified`

After completion, suggest running `/flow:plan` to create technical design.
""",
    "flow.plan.agent.md": """---
name: FlowPlan
description: "Execute planning workflow using project architect and platform engineer agents to create ADRs and platform design."
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

handoffs:
  - label: "Start Implementation"
    agent: "flow.implement"
    prompt: "The technical design is complete. Start implementing the feature."
    send: false
---

# /flow:plan - Technical Planning

Create comprehensive architectural and platform planning using specialized agents.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command creates technical architecture and platform design following Gregor Hohpe's principles.

**Prerequisites:**
1. Run `/flow:specify` first to create PRD
2. Have specification with clear requirements

**Workflow:**
1. Discover existing backlog tasks and PRD documents
2. Launch parallel planning agents:
   - **System Architecture**: ADRs, component design, integration patterns
   - **Platform & Infrastructure**: CI/CD, DevSecOps, observability
3. Create planning artifacts in `docs/adr/` and `docs/platform/`
4. Update backlog with planning tasks

**Key Principles:**
- Architecture as selling options (defer decisions until maximum information)
- Enterprise Integration Patterns for service communication
- Platform Quality Framework (7 C's)
- DORA Elite Performance targets

**Output:**
- Architecture Decision Records (ADRs) in `docs/adr/`
- Platform design document in `docs/platform/`
- API contracts and data models
- Workflow state updated to `Planned`

After completion, suggest running `/flow:implement` to start coding.
""",
    "flow.implement.agent.md": """---
name: FlowImplement
description: "Execute implementation using specialized frontend and backend engineer agents with code review."
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

handoffs:
  - label: "Run Validation"
    agent: "flow.validate"
    prompt: "Implementation is complete. Run validation and quality assurance."
    send: false
---

# /flow:implement - Implementation

Execute implementation using specialized engineering agents with integrated code review.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command implements features from backlog tasks with quality gates and code review.

**Prerequisites:**
1. Run `/flow:plan` first to create technical design
2. Have backlog tasks with acceptance criteria
3. Be on a properly named branch: `{hostname}/task-{id}/{slug}`

**Workflow:**
1. Discover backlog tasks and related specs/ADRs
2. Run quality gate on spec (`flowspec gate`)
3. Load PRP context if available (`docs/prp/{task-id}.md`)
4. Launch implementation agents:
   - **Frontend Engineer**: React, TypeScript, accessibility
   - **Backend Engineer**: APIs, databases, business logic
5. Run code reviews (frontend and backend reviewers)
6. Pre-PR validation (lint, tests, format)

**Key Commands:**
```bash
# Assign yourself to task
backlog task edit <task-id> -s "In Progress" -a @backend-engineer

# Check acceptance criteria as you complete them
backlog task edit <task-id> --check-ac 1

# Run pre-PR validation
uv run ruff check .
uv run pytest tests/ -x -q
```

**Deliverables (ALL REQUIRED):**
- Production code with all ACs satisfied
- Updated documentation
- Complete test coverage

After completion, run `/flow:validate` for comprehensive QA.
""",
    "flow.validate.agent.md": """---
name: FlowValidate
description: "Execute validation and quality assurance using QA, security, documentation, and release management agents."
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

handoffs:
  - label: "Submit PR"
    agent: "flow.submit-n-watch-pr"
    prompt: "Validation is complete. Submit PR and monitor CI/reviews."
    send: false
---

# /flow:validate - Quality Assurance

Execute comprehensive validation with automated testing, security scanning, and AC verification.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command performs thorough validation before PR submission.

**Prerequisites:**
1. Run `/flow:implement` first to complete coding
2. All acceptance criteria should be checked in backlog
3. Code should pass local tests

**Validation Phases:**

### Phase 1: Code Quality
- Lint check: `ruff check .` (Python), `go vet` (Go), `npm run lint` (TS)
- Format check: `ruff format --check .`
- Type check: `pyright`/`tsc --noEmit`

### Phase 2: Test Suite
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`
- Coverage verification

### Phase 3: Security Scan
- SAST: `bandit -r src/` (Python)
- Dependency audit: `npm audit`, `safety check`
- Secret detection

### Phase 4: AC Verification
- Verify all acceptance criteria are met
- Review implementation notes
- Confirm test coverage for each AC

### Phase 5: Documentation
- API documentation updated
- README current
- CHANGELOG entry added

**Output:**
- QA report in `docs/qa/`
- Security scan results
- Workflow state updated to `Validated`

After validation passes, run `/flow:submit-n-watch-pr` to create and monitor PR.
""",
    "flow.submit-n-watch-pr.agent.md": """---
name: FlowSubmitNWatchPR
description: "Submit PR and autonomously monitor CI checks and Copilot reviews until approval-ready. Iteratively fix issues and resubmit."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__github__*"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
---

# /flow:submit-n-watch-pr - Autonomous PR Management

Submit a PR and autonomously monitor CI checks and code review feedback until approval-ready.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Critical Success Criteria

Your PR is ONLY ready for merge when you see BOTH:
1. **All CI checks pass** (green checkmarks)
2. **Zero Copilot review comments** or all addressed

## Instructions

**Prerequisites:**
1. Run `/flow:validate` first to ensure quality
2. All local tests pass
3. Branch is rebased from main

**Workflow:**

### Step 1: Pre-Submit Validation
```bash
# Verify branch is up to date
git fetch origin main
git rebase origin/main

# Run final validation
uv run ruff check .
uv run pytest tests/ -x -q
```

### Step 2: Create PR
```bash
# Push branch
git push origin $(git branch --show-current)

# Create PR with proper description
gh pr create \
  --title "feat(scope): description" \
  --body "## Summary
1. Wait for CI checks to complete
2. Check for Copilot review comments: `gh pr view --comments`
3. If issues found:
   - Fix the issues locally
   - Push updates: `git push`
   - Wait for re-check
4. Repeat until all checks pass and no comments remain

### Step 4: Request Review
```bash
# When ready, request human review
gh pr ready
gh pr edit --add-reviewer <reviewer>
```

**Key Commands:**
```bash
# Check PR status
gh pr status
gh pr checks

# View review comments
gh pr view --comments

# Update PR after fixes
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Exit Conditions:**
- All CI checks green
- Zero unresolved Copilot comments
- PR marked ready for review
""",
}

# Embedded constitution templates (bundled with package for reliable access)
CONSTITUTION_TEMPLATES = {
    "light": """# [PROJECT_NAME] Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Simplicity First
Keep things simple. Ship fast, iterate quickly. Avoid over-engineering.

### Working Software
Prioritize working software over documentation. Code that runs is better than perfect designs.

### Pragmatic Quality
<!-- SECTION:QUALITY:BEGIN -->
<!-- NEEDS_VALIDATION: Quality standards appropriate for your project -->
- Write tests for critical paths
- Fix bugs before adding features
- Code review when time permits
<!-- SECTION:QUALITY:END -->

## Development Workflow

### Git Practices
<!-- SECTION:GIT:BEGIN -->
<!-- NEEDS_VALIDATION: Git workflow matches team size -->
- Feature branches encouraged for all changes
- Direct commits to main allowed if you prefer ("yolo mode")
- Commit messages should be descriptive
- DCO sign-off required (automated via git hooks): `git commit -s`
<!-- SECTION:GIT:END -->

### Task Management
<!-- SECTION:TASKS:BEGIN -->
<!-- NEEDS_VALIDATION: Task tracking approach -->
Tasks should have:
- Clear description of what needs to be done
- Basic acceptance criteria when scope is unclear
<!-- SECTION:TASKS:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->

## Governance

This constitution is a living document. Update it as the project evolves.

**Version**: 1.0.0
**Ratified**: [DATE]
**Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
""",
    "medium": """# [PROJECT_NAME] Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Quality-Driven Development
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Adjust quality principles to team practices -->
Code quality is a shared responsibility. Every team member maintains the codebase.

- **Test Coverage**: Critical paths must have test coverage
- **Code Review**: All changes require at least one reviewer
- **Documentation**: Public APIs and complex logic must be documented
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Continuous Improvement
Regularly evaluate and improve processes. Technical debt should be tracked and addressed.

## Git Commit Requirements

### Branch Strategy
<!-- SECTION:BRANCHING:BEGIN -->
<!-- NEEDS_VALIDATION: Branch strategy matches team workflow -->
- All changes go through feature branches
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Main branch is protected - no direct commits
<!-- SECTION:BRANCHING:END -->

### Pull Request Requirements
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements appropriate for team -->
- Descriptive title following conventional commits
- Link to related issue/task when applicable
- At least one approval required before merge
- CI checks must pass
<!-- SECTION:PR_REQUIREMENTS:END -->

### DCO Sign-Off
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

Use `git commit -s` to automatically add the sign-off.

## Task Management

### Task Quality
<!-- SECTION:TASK_QUALITY:BEGIN -->
<!-- NEEDS_VALIDATION: Task requirements match team workflow -->
Every task MUST have:
- **Clear description** explaining the "why"
- **Acceptance criteria** that are testable and verifiable
- **Labels** for categorization and filtering
<!-- SECTION:TASK_QUALITY:END -->

### Definition of Done
A task is complete when:
1. All acceptance criteria are met
2. Code is reviewed and approved
3. Tests pass
4. Documentation is updated (if applicable)
5. PR is merged

## Testing Standards
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements based on project needs -->
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Minimum coverage target: 70%
<!-- SECTION:TESTING:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security practices appropriate for project -->
- No secrets in code - use environment variables
- Dependencies regularly updated for security patches
- Input validation on all external data
<!-- SECTION:SECURITY:END -->

## Governance

This constitution guides team practices. Changes require team consensus.

**Version**: 1.0.0
**Ratified**: [DATE]
**Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
""",
    "heavy": """# [PROJECT_NAME] Constitution
<!-- TIER: Heavy - Strict controls for enterprise/regulated environments -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles (NON-NEGOTIABLE)

### Production-Grade Quality
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Verify quality standards meet regulatory requirements -->
There is no distinction between "dev code" and "production code". All code is production code.

- **Test-First Development**: TDD is mandatory - write tests, verify they fail, then implement
- **Code Review**: Minimum two reviewers required, including one senior engineer
- **Documentation**: All public APIs, architectural decisions, and complex logic must be documented
- **No Technical Debt**: Address issues immediately; do not defer quality
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Security by Design
Security is not an afterthought. Threat modeling during design phase is mandatory.

### Auditability
All changes must be traceable. Decisions must be documented and justified.

## Git Commit Requirements (NON-NEGOTIABLE)

### No Direct Commits to Main (ABSOLUTE)
**NEVER commit directly to the main branch.** All changes MUST go through a PR.

1. Create a branch for the task
2. Make changes on the branch
3. Create a PR referencing the backlog task
4. PR must pass CI before merge
5. Task marked Done only after PR is merged

**NO EXCEPTIONS.** Not for "urgent" fixes, not for "small" changes, not for any reason.

### Branch Protection
<!-- SECTION:BRANCH_PROTECTION:BEGIN -->
<!-- NEEDS_VALIDATION: Branch protection rules match security requirements -->
- Main branch: Protected, requires 2 approvals
- Release branches: Protected, requires security team approval
- Feature branches: Must be deleted after merge
- Force push: Disabled on protected branches
<!-- SECTION:BRANCH_PROTECTION:END -->

### DCO Sign-Off Required
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

**Always use `git commit -s` to automatically add the sign-off.**

Commits without sign-off will block PRs from being merged.

### Conventional Commits
All commit messages must follow conventional commit format:
```
type(scope): description

[body]

Signed-off-by: Name <email>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

## Pull Request Requirements (NON-NEGOTIABLE)
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements meet compliance needs -->
- Descriptive title following conventional commits
- Link to backlog task (mandatory)
- Security impact assessment for changes touching sensitive areas
- Minimum 2 approvals required
- CI pipeline must pass (tests, lint, security scan)
- No merge until all review comments are resolved
<!-- SECTION:PR_REQUIREMENTS:END -->

## Task Management (NON-NEGOTIABLE)

### Task Quality
Every task created MUST have:
- **At least one acceptance criterion** - Tasks without ACs are incomplete
- **Clear, testable criteria** - Each AC must be outcome-oriented and objectively verifiable
- **Proper description** - Explains the "why" and context
- **Risk assessment** - Security/compliance implications noted

Tasks without acceptance criteria will be rejected or archived.

### PR-Task Synchronization
When creating a PR that completes a backlog task:

1. **Before PR creation**: Mark all completed acceptance criteria
2. **With PR creation**: Update task status and reference the PR
3. **PR-Task coupling**: If the PR fails CI or is rejected, revert task status
4. **Traceability**: Every PR must reference its task; every task must reference its PR

## Testing Standards (NON-NEGOTIABLE)
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements meet regulatory standards -->
- **Unit Tests**: Mandatory for all business logic (minimum 80% coverage)
- **Integration Tests**: Mandatory for all API endpoints and service boundaries
- **E2E Tests**: Mandatory for all critical user journeys
- **Security Tests**: SAST, DAST, and dependency scanning on every PR
- **Performance Tests**: Load testing for user-facing endpoints
- **Contract Tests**: Required for all inter-service communication
<!-- SECTION:TESTING:END -->

## Security Requirements (NON-NEGOTIABLE)
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security controls meet compliance requirements -->
### Secrets Management
- No secrets in code, configs, or environment files checked into git
- Use approved secrets management solution
- Rotate secrets according to policy

### Access Control
- Principle of least privilege
- All access logged and auditable
- Regular access reviews (quarterly minimum)

### Vulnerability Management
- Dependencies scanned on every build
- Critical vulnerabilities: Fix within 24 hours
- High vulnerabilities: Fix within 7 days
- Security patches applied within SLA

### Data Protection
- PII/sensitive data encrypted at rest and in transit
- Data classification enforced
- Retention policies applied
<!-- SECTION:SECURITY:END -->

## Compliance
<!-- SECTION:COMPLIANCE:BEGIN -->
<!-- NEEDS_VALIDATION: Compliance frameworks applicable to project -->
This project must comply with:
- [COMPLIANCE_FRAMEWORKS]

### Audit Requirements
- All changes logged with user, timestamp, and justification
- Audit logs retained for [RETENTION_PERIOD]
- Regular compliance audits scheduled
<!-- SECTION:COMPLIANCE:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Approved Technologies
All technology choices must be from the approved list or require architecture review.

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]

### CI/CD Pipeline
<!-- NEEDS_VALIDATION: CI/CD configuration matches security requirements -->
[CI_CD_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Parallel Task Execution

### Git Worktree Requirements
When executing tasks in parallel, git worktrees MUST be used:

1. **Worktree name must match branch name**
2. **One branch per worktree**
3. **Clean isolation** - no cross-contamination between parallel work
4. **Worktree cleanup** - remove when work is complete

## Change Management
<!-- SECTION:CHANGE_MANAGEMENT:BEGIN -->
<!-- NEEDS_VALIDATION: Change management process meets requirements -->
### Standard Changes
- Pre-approved, low-risk changes
- Follow standard PR process

### Normal Changes
- Require change request documentation
- Impact assessment required
- Rollback plan documented

### Emergency Changes
- Require incident ticket reference
- Post-implementation review mandatory
- Retrospective within 48 hours
<!-- SECTION:CHANGE_MANAGEMENT:END -->

## Incident Response
<!-- SECTION:INCIDENT_RESPONSE:BEGIN -->
<!-- NEEDS_VALIDATION: Incident response meets regulatory requirements -->
- All security incidents reported within [REPORTING_WINDOW]
- Incident severity classification enforced
- Post-incident reviews mandatory
- Lessons learned documented and shared
<!-- SECTION:INCIDENT_RESPONSE:END -->

## Governance

### Constitution Authority
This constitution supersedes all other practices. Violations are escalated.

### Amendments
Changes to this constitution require:
1. Written proposal with justification
2. Impact assessment
3. Security/compliance review
4. Approval from [APPROVAL_AUTHORITY]
5. Migration plan for existing work

**Version**: 1.0.0
**Ratified**: [DATE]
**Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version, dates, and approval authority -->
""",
}

# Project detection markers for existing project identification
PROJECT_MARKERS = [
    ".git",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
]


def is_existing_project(path: Path) -> bool:
    """Check if a directory is an existing project by looking for common project markers.

    Args:
        path: Directory to check

    Returns:
        True if any project marker is found
    """
    for marker in PROJECT_MARKERS:
        if (path / marker).exists():
            return True
    return False


def has_constitution(path: Path) -> bool:
    """Check if a project has a constitution file.

    Args:
        path: Project directory to check

    Returns:
        True if memory/constitution.md exists
    """
    constitution_path = path / "memory" / "constitution.md"
    return constitution_path.exists()


def _detect_tier_from_content(content: str) -> str:
    """Detect tier from constitution content string.

    Args:
        content: Constitution file content

    Returns:
        Tier level: "Light", "Medium", or "Heavy" (defaults to "Medium")
    """
    import re

    match = re.search(r"<!-- TIER: (Light|Medium|Heavy) -->", content)
    return match.group(1) if match else "Medium"


def _count_markers_from_content(content: str) -> int:
    """Count NEEDS_VALIDATION markers in content.

    Uses regex to match actual comment markers, avoiding false positives
    from the text appearing in documentation or examples.

    Args:
        content: Constitution file content

    Returns:
        Number of NEEDS_VALIDATION markers found
    """
    import re

    # Match actual HTML comment markers, not plain text
    return len(re.findall(r"<!-- NEEDS_VALIDATION:", content))


def _extract_sections_from_content(content: str) -> list[str]:
    """Extract section names from NEEDS_VALIDATION markers.

    Args:
        content: Constitution file content

    Returns:
        List of section descriptions needing validation
    """
    import re

    pattern = r"<!-- NEEDS_VALIDATION: (.+?) -->"
    return re.findall(pattern, content)


def detect_constitution_tier(constitution_path: Path) -> str:
    """Detect the tier from a constitution file.

    Args:
        constitution_path: Path to constitution.md file

    Returns:
        Tier level: "Light", "Medium", or "Heavy" (defaults to "Medium")
    """
    if not constitution_path.exists():
        return "Medium"

    content = constitution_path.read_text()
    return _detect_tier_from_content(content)


def count_validation_markers(constitution_path: Path) -> int:
    """Count NEEDS_VALIDATION markers in constitution.

    Args:
        constitution_path: Path to constitution.md file

    Returns:
        Number of NEEDS_VALIDATION markers found
    """
    if not constitution_path.exists():
        return 0

    content = constitution_path.read_text()
    return _count_markers_from_content(content)


def extract_validation_sections(constitution_path: Path) -> list[str]:
    """Extract section names from NEEDS_VALIDATION markers.

    Args:
        constitution_path: Path to constitution.md file

    Returns:
        List of section descriptions needing validation
    """
    if not constitution_path.exists():
        return []

    content = constitution_path.read_text()
    return _extract_sections_from_content(content)


class ConstitutionEnforcementResult:
    """Result of constitution enforcement check."""

    def __init__(
        self,
        tier: str,
        marker_count: int,
        section_names: list[str],
        can_proceed: bool,
        requires_confirmation: bool = False,
        warning: str | None = None,
        blocking_reason: str | None = None,
    ):
        self.tier = tier
        self.marker_count = marker_count
        self.section_names = section_names
        self.can_proceed = can_proceed
        self.requires_confirmation = requires_confirmation
        self.warning = warning
        self.blocking_reason = blocking_reason


def check_constitution_tier(
    constitution_path: Path, skip_validation: bool = False
) -> ConstitutionEnforcementResult:
    """Check constitution tier and enforce validation rules.

    Args:
        constitution_path: Path to constitution.md file
        skip_validation: If True, bypass all enforcement checks

    Returns:
        ConstitutionEnforcementResult with enforcement decision
    """
    if skip_validation:
        return ConstitutionEnforcementResult(
            tier="Skipped",
            marker_count=0,
            section_names=[],
            can_proceed=True,
            warning="Skipping constitution validation (--skip-validation)",
        )

    if not constitution_path.exists():
        return ConstitutionEnforcementResult(
            tier="Unknown",
            marker_count=0,
            section_names=[],
            can_proceed=True,
            warning="Constitution not found - consider running 'flowspec init --here'",
        )

    # Read file once and extract all data (efficiency fix per Copilot review)
    content = constitution_path.read_text()
    tier = _detect_tier_from_content(content)
    marker_count = _count_markers_from_content(content)
    section_names = _extract_sections_from_content(content)

    # Fully validated - always proceed
    if marker_count == 0:
        return ConstitutionEnforcementResult(
            tier=tier,
            marker_count=0,
            section_names=[],
            can_proceed=True,
        )

    # Light tier: warn but proceed
    if tier == "Light":
        sections_list = "\n".join(f"  - {name}" for name in section_names)
        warning = (
            f"Constitution has {marker_count} unvalidated sections:\n{sections_list}\n\n"
            "Consider running /spec:constitution to customize your constitution."
        )
        return ConstitutionEnforcementResult(
            tier=tier,
            marker_count=marker_count,
            section_names=section_names,
            can_proceed=True,
            warning=warning,
        )

    # Medium tier: warn and require confirmation
    if tier == "Medium":
        sections_list = "\n".join(f"  - {name}" for name in section_names)
        warning = (
            f"Constitution has {marker_count} unvalidated sections:\n{sections_list}\n\n"
            "Medium tier projects should validate their constitution before workflow commands."
        )
        return ConstitutionEnforcementResult(
            tier=tier,
            marker_count=marker_count,
            section_names=section_names,
            can_proceed=False,
            requires_confirmation=True,
            warning=warning,
        )

    # Heavy tier: block until validated
    sections_list = "\n".join(f"  - {name}" for name in section_names)
    blocking_reason = (
        f"Constitution has {marker_count} unvalidated sections:\n{sections_list}\n\n"
        "Heavy tier constitutions require full validation before workflow commands.\n\n"
        "To resolve:\n"
        "  1. Run /spec:constitution to customize your constitution\n"
        "  2. Run flowspec constitution validate to verify\n"
        "  3. Remove all NEEDS_VALIDATION markers\n\n"
        "Or use --skip-validation to bypass (not recommended)."
    )
    return ConstitutionEnforcementResult(
        tier=tier,
        marker_count=marker_count,
        section_names=section_names,
        can_proceed=False,
        blocking_reason=blocking_reason,
    )


CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

BANNER = """
███████╗██╗      ██████╗ ██╗    ██╗███████╗██████╗ ███████╗ ██████╗
██╔════╝██║     ██╔═══██╗██║    ██║██╔════╝██╔══██╗██╔════╝██╔════╝
█████╗  ██║     ██║   ██║██║ █╗ ██║███████╗██████╔╝█████╗  ██║
██╔══╝  ██║     ██║   ██║██║███╗██║╚════██║██╔═══╝ ██╔══╝  ██║
██║     ███████╗╚██████╔╝╚███╔███╔╝███████║██║     ███████╗╚██████╗
╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝
"""

# Version - keep in sync with pyproject.toml

__version__ = "0.3.025"


# Constitution template version
CONSTITUTION_VERSION = "1.0.0"

TAGLINE = f"(flowspec v{__version__}) with backlog.md & beads - Spec-Driven Development"

# Repository configuration (standalone - no external dependencies)
REPO_OWNER = "jpoley"
REPO_NAME = "flowspec"
REPO_DEFAULT_VERSION = "latest"

BEADS_REPO_OWNER = "jpoley"
BEADS_REPO_NAME = "beads"

# Marker file that identifies the flowspec source repository
# When present, flowspec init/upgrade will skip to avoid clobbering source files
SOURCE_REPO_MARKER = ".flowspec-source"

# Compatibility configuration (embedded in code, no external file needed)


def get_backlog_validated_version() -> Optional[str]:
    """Get the recommended backlog-md version.

    Returns:
        Recommended version string (e.g., "1.21.0")
    """
    # Hardcoded recommended version - update as needed
    return "1.21.0"


def check_backlog_installed_version() -> Optional[str]:
    """Check the currently installed backlog-md version.

    Returns:
        Version string (e.g., "1.21.0") or None if not installed
    """
    try:
        result = subprocess.run(
            ["backlog", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            # backlog --version outputs just the version number, e.g. "1.21.0"
            output = result.stdout.strip()
            # Validate it looks like a version (digits and dots)
            if output and all(c.isdigit() or c == "." for c in output):
                return output
    except FileNotFoundError:
        # 'backlog' CLI not in PATH - expected when not installed
        pass
    return None


def check_beads_installed_version() -> Optional[str]:
    """Check the currently installed beads version.

    Returns:
        Version string (e.g., "0.29.0") or None if not installed
    """
    try:
        result = subprocess.run(
            ["bd", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            # bd --version outputs "bd version 0.29.0 (c9eeecf0)"
            output = result.stdout.strip()
            # Extract version number from "bd version X.Y.Z (hash)"
            if output.startswith("bd version "):
                parts = output.split()
                if len(parts) >= 3:
                    version = parts[2]
                    # Validate it looks like a version (digits and dots)
                    if version and all(c.isdigit() or c == "." for c in version):
                        return version
    except FileNotFoundError:
        # 'bd' CLI not in PATH - expected when not installed
        pass
    return None


def detect_package_manager() -> Optional[str]:
    """Detect available Node.js package manager, preferring pnpm.

    Returns:
        "pnpm" if available, "npm" if available, None if neither found
    """
    if shutil.which("pnpm"):
        return "pnpm"
    if shutil.which("npm"):
        return "npm"
    return None


def get_available_package_managers() -> list[str]:
    """Get list of available Node.js package managers.

    Returns:
        List of available package managers in order of preference (pnpm first, then npm)
    """
    pkg_managers = []
    if shutil.which("pnpm"):
        pkg_managers.append("pnpm")
    if shutil.which("npm"):
        pkg_managers.append("npm")
    return pkg_managers


def _run_npm_global_install(
    package: str, version: str
) -> tuple[bool, str, Optional[str]]:
    """Install an npm package globally, with fallback from pnpm to npm.

    Args:
        package: npm package name (e.g., "backlog.md" or "@beads/bd")
        version: version to install (e.g., "1.28.1")

    Returns:
        Tuple of (success, message, package_manager_used)
        - success: True if installation succeeded
        - message: Success/error message
        - package_manager_used: "pnpm", "npm", or None if both failed
    """
    pkg_managers = get_available_package_managers()

    if not pkg_managers:
        return False, "No Node.js package manager found (npm or pnpm required)", None

    errors = []
    for pkg_manager in pkg_managers:
        try:
            if pkg_manager == "pnpm":
                cmd = ["pnpm", "add", "-g", f"{package}@{version}"]
            else:
                cmd = ["npm", "install", "-g", f"{package}@{version}"]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, f"Installed with {pkg_manager}", pkg_manager
        except subprocess.CalledProcessError as e:
            # Capture both stdout and stderr for error message
            error_output = (e.stderr or e.stdout or "").strip()
            if not error_output:
                error_output = f"Command failed with exit code {e.returncode}"
            errors.append(f"{pkg_manager}: {error_output}")
            # Continue to try next package manager
        except FileNotFoundError:
            errors.append(f"{pkg_manager}: binary not found")

    # All package managers failed
    return False, "; ".join(errors), None


def compare_semver(version1: str, version2: str) -> int:
    """Simple semantic version comparison.

    Args:
        version1: First version (e.g., "1.21.0")
        version2: Second version (e.g., "1.20.0")

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """

    def parse_version(v: str) -> Tuple[int, int, int]:
        """Parse version string into tuple of ints."""
        parts = v.lstrip("v").split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)

    v1 = parse_version(version1)
    v2 = parse_version(version2)

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


# =============================================================================
# Version Detection and Display
# =============================================================================


def get_github_latest_release(owner: str, repo: str) -> Optional[str]:
    """Fetch the latest release version from GitHub API.

    Args:
        owner: Repository owner (e.g., "jpoley")
        repo: Repository name (e.g., "flowspec")

    Returns:
        Version string (e.g., "0.0.311") or None if fetch fails
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = client.get(url, headers=_github_headers(skip_auth=True), timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            tag_name = data.get("tag_name", "")
            return tag_name.lstrip("v") if tag_name else None
        # Non-200 response - likely no releases or repo not found
        logger.debug(f"GitHub API returned {response.status_code} for {owner}/{repo}")
    except httpx.TimeoutException:
        logger.debug(f"Timeout fetching GitHub release for {owner}/{repo}")
    except httpx.HTTPError as e:
        logger.debug(f"HTTP error fetching GitHub release for {owner}/{repo}: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error fetching GitHub release: {e}")
    return None


def get_github_releases(owner: str, repo: str, limit: int = 10) -> list[dict[str, str]]:
    """Fetch available releases from GitHub API.

    Args:
        owner: Repository owner (e.g., "jpoley")
        repo: Repository name (e.g., "flowspec")
        limit: Maximum number of releases to return

    Returns:
        List of dicts with 'version', 'published_at', 'prerelease' keys
    """
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        response = client.get(
            url,
            headers=_github_headers(skip_auth=True),
            timeout=5.0,
            params={"per_page": limit},
        )
        if response.status_code == 200:
            releases = []
            for release in response.json():
                tag = release.get("tag_name", "")
                version = tag.lstrip("v") if tag else ""
                if version:
                    releases.append(
                        {
                            "version": version,
                            "published_at": release.get("published_at", "")[:10],
                            "prerelease": release.get("prerelease", False),
                        }
                    )
            return releases
        logger.debug(f"GitHub API returned {response.status_code} for {owner}/{repo}")
    except httpx.TimeoutException:
        logger.debug(f"Timeout fetching GitHub releases for {owner}/{repo}")
    except httpx.HTTPError as e:
        logger.debug(f"HTTP error fetching GitHub releases for {owner}/{repo}: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error fetching GitHub releases: {e}")
    return []


def version_exists_in_releases(owner: str, repo: str, version: str) -> bool:
    """Check if a version exists in GitHub releases.

    Args:
        owner: Repository owner
        repo: Repository name
        version: Version to check (with or without 'v' prefix)

    Returns:
        True if version exists, False otherwise
    """
    version = version.lstrip("v")
    releases = get_github_releases(owner, repo, limit=100)
    return any(r["version"] == version for r in releases)


def get_npm_latest_version(package: str) -> Optional[str]:
    """Fetch the latest version of an npm package from the registry.

    Args:
        package: npm package name (e.g., "backlog.md")

    Returns:
        Version string (e.g., "1.26.4") or None if fetch fails
    """
    try:
        url = f"https://registry.npmjs.org/{package}/latest"
        response = client.get(url, timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            version = data.get("version")
            if version:
                return version
            logger.debug(f"npm response missing 'version' field for {package}")
        else:
            logger.debug(f"npm registry returned {response.status_code} for {package}")
    except httpx.TimeoutException:
        logger.debug(f"Timeout fetching npm version for {package}")
    except httpx.HTTPError as e:
        logger.debug(f"HTTP error fetching npm version for {package}: {e}")
    except Exception as e:
        logger.debug(f"Unexpected error fetching npm version: {e}")
    return None


def get_all_component_versions() -> dict:
    """Get installed and available versions for all components.

    Returns:
        Dictionary with the following structure:
        {
            "flowspec": {"installed": str, "available": str | None},
            "backlog_md": {"installed": str | None, "available": str | None},
            "beads": {"installed": str | None, "available": str | None}
        }
    """
    return {
        "flowspec": {
            "installed": __version__,
            "available": get_github_latest_release(REPO_OWNER, REPO_NAME),
        },
        "backlog_md": {
            "installed": check_backlog_installed_version(),
            "available": get_npm_latest_version("backlog.md"),
        },
        "beads": {
            "installed": check_beads_installed_version(),
            "available": get_npm_latest_version("@beads/bd"),
        },
    }


def write_version_tracking_file(
    project_path: Path,
    flowspec_version: str | None = None,
    backlog_version: str | None = None,
    beads_version: str | None = None,
    is_upgrade: bool = False,
) -> None:
    """Write or update the .flowspec/.version tracking file.

    Args:
        project_path: Path to the project root
        flowspec_version: flowspec version to record (uses __version__ if None)
        backlog_version: backlog-md version to record (auto-detects if None)
        beads_version: beads version to record (auto-detects if None)
        is_upgrade: True if this is an upgrade operation (updates upgraded_at timestamp)

    Note:
        This function never raises exceptions - failures are logged as warnings.
        Version tracking is non-critical and should not block init/upgrade operations.
    """
    try:
        flowspec_dir = project_path / ".flowspec"
        version_file = flowspec_dir / ".version"

        # Get current versions if not provided
        if flowspec_version is None:
            flowspec_version = __version__
        if backlog_version is None:
            backlog_version = check_backlog_installed_version()
        if beads_version is None:
            beads_version = check_beads_installed_version()

        # Load existing data if file exists (use our TOML parser, not YAML)
        existing_data = {}
        if version_file.exists():
            parsed = read_version_tracking_file(project_path)
            if parsed:
                existing_data = parsed

        # Build the version data
        versions = {"flowspec": flowspec_version or "unknown"}
        if backlog_version:
            versions["backlog"] = backlog_version
        if beads_version:
            versions["beads"] = beads_version

        # Build metadata with UTC timestamps
        now = datetime.now(timezone.utc).isoformat()
        metadata = existing_data.get("metadata", {})

        if is_upgrade:
            # For upgrade, preserve installed_at and update upgraded_at
            # If installed_at is missing (pre-existing repo without version file), set it too
            if "installed_at" not in metadata:
                metadata["installed_at"] = now
            metadata["upgraded_at"] = now
        else:
            # For init, always set installed_at (fresh install)
            metadata["installed_at"] = now

        # Write to file in TOML format
        flowspec_dir.mkdir(parents=True, exist_ok=True)

        with open(version_file, "w") as f:
            f.write("[versions]\n")
            for key, value in versions.items():
                f.write(f'{key} = "{value}"\n')
            f.write("\n[metadata]\n")
            for key, value in metadata.items():
                f.write(f'{key} = "{value}"\n')
    except PermissionError as e:
        # Don't fail init/upgrade if version tracking fails - just log warning
        logger.warning(
            "Could not write version tracking file (permission denied): %s",
            e,
        )
    except FileNotFoundError as e:
        # Underlying directory structure is missing or inaccessible
        logger.warning(
            "Could not write version tracking file (path not found): %s",
            e,
        )
    except OSError as e:
        # Don't fail init/upgrade if version tracking fails - just log warning
        logger.warning(
            "Could not write version tracking file (OS error): %s",
            e,
        )


def read_version_tracking_file(project_path: Path) -> dict | None:
    """Read the .flowspec/.version tracking file.

    Args:
        project_path: Path to the project root

    Returns:
        Dictionary with versions and metadata, or None if file doesn't exist or is invalid
    """
    version_file = project_path / ".flowspec" / ".version"
    if not version_file.exists():
        return None

    try:
        # Use tomllib for robust TOML parsing (Python 3.11+ built-in)
        with open(version_file, "rb") as f:
            data = tomllib.load(f)

        # Normalize to expected structure
        return {
            "versions": data.get("versions", {}),
            "metadata": data.get("metadata", {}),
        }
    except (tomllib.TOMLDecodeError, OSError):
        # Return None if file is invalid or unreadable
        return None


def _has_upgrade(versions: dict) -> bool:
    """Check if a component has an available upgrade.

    Args:
        versions: Dictionary with "installed" and "available" keys

    Returns:
        True if available version is newer than installed
    """
    return bool(
        versions.get("available")
        and versions.get("installed")
        and compare_semver(versions["installed"], versions["available"]) < 0
    )


def _add_version_row(
    table: Table,
    name: str,
    versions: dict,
    not_installed_msg: str = "-",
) -> bool:
    """Add a component row to the version table.

    Args:
        table: Rich Table to add the row to
        name: Component display name
        versions: Dictionary with "installed" and "available" keys
        not_installed_msg: Message to show when not installed

    Returns:
        True if an upgrade is available
    """
    has_upgrade = _has_upgrade(versions)
    status = " [yellow]↑[/yellow]" if has_upgrade else ""
    installed = versions.get("installed") or not_installed_msg
    available = versions.get("available") or "-"

    table.add_row(f"{name}{status}", installed, available)
    return has_upgrade


def show_version_info(detailed: bool = False, centered: bool = False) -> None:
    """Display version information for all components.

    Args:
        detailed: If True, show table with installed and available versions
        centered: If True, center the output (for banner display)
    """
    versions = get_all_component_versions()

    if detailed:
        table = Table(show_header=True, box=None, padding=(0, 2))
        table.add_column("Component", style="cyan")
        table.add_column("Installed", style="green")
        table.add_column("Available", style="dim")

        # Track if any upgrades are available
        upgrades_available = []

        # Add all component rows
        upgrades_available.append(
            _add_version_row(table, "flowspec", versions["flowspec"])
        )
        upgrades_available.append(
            _add_version_row(
                table, "backlog.md", versions["backlog_md"], "[dim]not installed[/dim]"
            )
        )
        upgrades_available.append(
            _add_version_row(
                table, "beads", versions["beads"], "[dim]not installed[/dim]"
            )
        )

        if centered:
            console.print(Align.center(table))
        else:
            console.print(table)

        # Show upgrade hint if any upgrades available
        if any(upgrades_available):
            hint = "[dim]Run 'flowspec upgrade-tools' to update CLI tools[/dim]"
            if centered:
                console.print(Align.center(hint))
            else:
                console.print(hint)
    else:
        console.print(f"flowspec {versions['flowspec']['installed']}")


def version_callback(value: bool) -> None:
    """Callback for --version flag."""
    if value:
        show_version_info(detailed=False)
        raise typer.Exit()


def write_repo_facts(project_path: Path) -> None:
    """Write repository facts to memory/repo-facts.md with YAML frontmatter.

    Detects:
    - Languages from package manager files
    - CI/CD systems from workflow files
    - Git repository status

    Args:
        project_path: Path to the project directory
    """
    from datetime import datetime

    # Detect languages
    languages = []
    package_files = {
        "Python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
        "JavaScript/TypeScript": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
        "Go": ["go.mod", "go.sum"],
        "Rust": ["Cargo.toml", "Cargo.lock"],
        "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "Ruby": ["Gemfile", "Gemfile.lock"],
        "PHP": ["composer.json", "composer.lock"],
        "C#": ["*.csproj", "*.sln"],  # Use glob patterns for C#
    }

    for lang, files in package_files.items():
        if lang == "C#":
            # Check for any file ending with .csproj or .sln
            if any(project_path.glob("*.csproj")) or any(project_path.glob("*.sln")):
                if lang not in languages:
                    languages.append(lang)
        else:
            for file in files:
                if (project_path / file).exists():
                    if lang not in languages:
                        languages.append(lang)
                    break

    # Detect CI/CD
    cicd_systems = []
    cicd_markers = {
        "GitHub Actions": [".github/workflows"],
        "GitLab CI": [".gitlab-ci.yml"],
        "CircleCI": [".circleci/config.yml"],
        "Travis CI": [".travis.yml"],
        "Jenkins": ["Jenkinsfile"],
    }

    for system, markers in cicd_markers.items():
        for marker in markers:
            marker_path = project_path / marker
            if marker_path.exists():
                if marker_path.is_dir() and any(marker_path.iterdir()):
                    cicd_systems.append(system)
                    break
                elif marker_path.is_file():
                    cicd_systems.append(system)
                    break

    # Check if git repo
    is_git = (project_path / ".git").exists()

    # Build YAML frontmatter
    frontmatter = {
        "generated": datetime.now().isoformat(),
        "languages": languages if languages else ["Unknown"],
        "cicd": cicd_systems if cicd_systems else ["None detected"],
        "git_repo": is_git,
    }

    # Build markdown content
    content_lines = [
        "---",
        f"generated: {frontmatter['generated']}",
        f"languages: [{', '.join(frontmatter['languages'])}]",
        f"cicd: [{', '.join(frontmatter['cicd'])}]",
        f"git_repo: {str(frontmatter['git_repo']).lower()}",
        "---",
        "",
        "# Repository Facts",
        "",
        "This file contains automatically detected facts about your repository.",
        "It is generated during `flowspec init`. Regeneration via `flowspec check` is a planned feature.",
        "",
        "## Languages",
        "",
    ]

    for lang in frontmatter["languages"]:
        content_lines.append(f"- {lang}")

    content_lines.extend(
        [
            "",
            "## CI/CD",
            "",
        ]
    )

    for cicd in frontmatter["cicd"]:
        content_lines.append(f"- {cicd}")

    content_lines.extend(
        [
            "",
            "## Git Repository",
            "",
            f"Git repository: {'Yes' if frontmatter['git_repo'] else 'No'}",
            "",
            "---",
            "",
            "*This file is automatically generated. Manual edits will be preserved but may be overwritten.*",
        ]
    )

    # Write to memory/repo-facts.md
    memory_dir = project_path / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    repo_facts_path = memory_dir / "repo-facts.md"
    repo_facts_path.write_text("\n".join(content_lines))


def detect_tech_stack(project_path: Path) -> dict:
    """Detect project tech stack from package manager files.

    Returns:
        dict with keys:
            - languages: List of detected languages
            - frameworks: List of detected frameworks
            - test_framework: Detected test framework
            - package_manager: Detected package manager
    """
    tech_stack = {
        "languages": [],
        "frameworks": [],
        "test_framework": None,
        "package_manager": None,
    }

    # Python detection
    pyproject_toml = project_path / "pyproject.toml"
    requirements_txt = project_path / "requirements.txt"
    setup_py = project_path / "setup.py"
    pipfile = project_path / "Pipfile"

    if (
        pyproject_toml.exists()
        or requirements_txt.exists()
        or setup_py.exists()
        or pipfile.exists()
    ):
        tech_stack["languages"].append("Python")
        tech_stack["test_framework"] = "pytest"

        # Check for frameworks in pyproject.toml
        if pyproject_toml.exists():
            try:
                with open(pyproject_toml, "rb") as f:
                    data = tomllib.load(f)
                    deps = []
                    if "project" in data and "dependencies" in data["project"]:
                        deps.extend(data["project"]["dependencies"])
                    if (
                        "tool" in data
                        and "poetry" in data["tool"]
                        and "dependencies" in data["tool"]["poetry"]
                    ):
                        deps.extend(data["tool"]["poetry"]["dependencies"].keys())

                    deps_str = " ".join(str(d).lower() for d in deps)
                    # Use `if` not `elif` to detect multiple frameworks
                    if "fastapi" in deps_str:
                        tech_stack["frameworks"].append("FastAPI")
                    if "flask" in deps_str:
                        tech_stack["frameworks"].append("Flask")
                    if "django" in deps_str:
                        tech_stack["frameworks"].append("Django")
            except Exception:
                pass  # Skip if toml parsing fails

        # Set Python package manager
        if pipfile.exists():
            tech_stack["package_manager"] = "pipenv"
        elif pyproject_toml.exists():
            tech_stack["package_manager"] = "uv"
        else:
            # Default to pip when Python is detected but no specific package manager
            tech_stack["package_manager"] = "pip"

    # JavaScript/TypeScript detection
    package_json = project_path / "package.json"
    if package_json.exists():
        tech_stack["languages"].append("JavaScript/TypeScript")

        try:
            import json

            with open(package_json) as f:
                data = json.load(f)
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }

                if "react" in deps:
                    tech_stack["frameworks"].append("React")
                if "next" in deps:
                    tech_stack["frameworks"].append("Next.js")
                if "vue" in deps:
                    tech_stack["frameworks"].append("Vue")
                if "express" in deps:
                    tech_stack["frameworks"].append("Express")

                # Only set test framework if not already set (polyglot support)
                if tech_stack["test_framework"] is None:
                    if "vitest" in deps:
                        tech_stack["test_framework"] = "vitest"
                    elif "jest" in deps:
                        tech_stack["test_framework"] = "jest"
                    elif "mocha" in deps:
                        tech_stack["test_framework"] = "mocha"
        except Exception:
            pass  # Skip if JSON parsing fails

        # Only set package manager if not already set (polyglot support)
        if tech_stack["package_manager"] is None:
            if (project_path / "pnpm-lock.yaml").exists():
                tech_stack["package_manager"] = "pnpm"
            elif (project_path / "yarn.lock").exists():
                tech_stack["package_manager"] = "yarn"
            else:
                tech_stack["package_manager"] = "npm"

    # Go detection
    if (project_path / "go.mod").exists():
        tech_stack["languages"].append("Go")
        if tech_stack["test_framework"] is None:
            tech_stack["test_framework"] = "go test"

    # Rust detection
    cargo_toml = project_path / "Cargo.toml"
    if cargo_toml.exists():
        tech_stack["languages"].append("Rust")
        if tech_stack["test_framework"] is None:
            tech_stack["test_framework"] = "cargo test"

    # Java detection
    if (project_path / "pom.xml").exists():
        tech_stack["languages"].append("Java")
        if tech_stack["package_manager"] is None:
            tech_stack["package_manager"] = "maven"
        if tech_stack["test_framework"] is None:
            tech_stack["test_framework"] = "junit"
    elif (project_path / "build.gradle").exists() or (
        project_path / "build.gradle.kts"
    ).exists():
        tech_stack["languages"].append("Java")
        if tech_stack["package_manager"] is None:
            tech_stack["package_manager"] = "gradle"
        if tech_stack["test_framework"] is None:
            tech_stack["test_framework"] = "junit"

    return tech_stack


def generate_claude_md(project_path: Path, project_name: str) -> None:
    """Generate root CLAUDE.md file with project-specific configuration.

    Args:
        project_path: Path to the project directory
        project_name: Name of the project
    """
    claude_md_path = project_path / "CLAUDE.md"

    # Skip if CLAUDE.md already exists
    if claude_md_path.exists():
        return

    # Detect tech stack
    tech_stack = detect_tech_stack(project_path)

    # Build tech stack section
    tech_lines = []
    if tech_stack["languages"]:
        tech_lines.append("## Tech Stack")
        tech_lines.append("")
        tech_lines.append("**Languages**:")
        for lang in tech_stack["languages"]:
            tech_lines.append(f"- {lang}")
        tech_lines.append("")

    if tech_stack["frameworks"]:
        tech_lines.append("**Frameworks**:")
        for framework in tech_stack["frameworks"]:
            tech_lines.append(f"- {framework}")
        tech_lines.append("")

    tech_stack_section = "\n".join(tech_lines) if tech_lines else ""

    # Build commands section based on detected tooling
    commands = []
    has_development_header = False

    # Python commands
    if "Python" in tech_stack["languages"]:
        # Use language-specific header in polyglot projects
        header = "# Python" if len(tech_stack["languages"]) > 1 else "# Development"
        has_development_header = True
        commands.extend(
            [
                header,
                "pytest tests/                    # Run tests",
                "ruff check . --fix               # Lint and auto-fix",
                "ruff format .                    # Format code",
            ]
        )
        if tech_stack["package_manager"] == "uv":
            commands.append("uv sync                          # Install dependencies")
        elif tech_stack["package_manager"] == "pipenv":
            commands.append("pipenv install                   # Install dependencies")
        else:
            commands.append("pip install -r requirements.txt  # Install dependencies")
        commands.append("")

    # JavaScript/TypeScript commands
    if "JavaScript/TypeScript" in tech_stack["languages"]:
        # Determine JS package manager locally (don't use global which may be Python's)
        if (project_path / "pnpm-lock.yaml").exists():
            js_pm = "pnpm"
        elif (project_path / "yarn.lock").exists():
            js_pm = "yarn"
        else:
            js_pm = "npm"
        test_cmd = tech_stack["test_framework"] or "test"
        header = (
            "# JavaScript/TypeScript"
            if len(tech_stack["languages"]) > 1
            else "# Development"
        )
        has_development_header = True
        commands.extend(
            [
                header,
                f"{js_pm} install                       # Install dependencies",
                f"{js_pm} run {test_cmd}                # Run tests",
                f"{js_pm} run build                     # Build project",
                f"{js_pm} run dev                       # Start dev server",
                "",
            ]
        )

    # Go commands
    if "Go" in tech_stack["languages"]:
        header = "# Go" if len(tech_stack["languages"]) > 1 else "# Development"
        has_development_header = True
        commands.extend(
            [
                header,
                "go mod download                  # Download dependencies",
                "go test ./...                    # Run tests",
                "go build                         # Build project",
                "",
            ]
        )

    # Rust commands
    if "Rust" in tech_stack["languages"]:
        header = "# Rust" if len(tech_stack["languages"]) > 1 else "# Development"
        has_development_header = True
        commands.extend(
            [
                header,
                "cargo build                      # Build project",
                "cargo test                       # Run tests",
                "cargo clippy                     # Lint code",
                "cargo fmt                        # Format code",
                "",
            ]
        )

    # Java commands
    if "Java" in tech_stack["languages"]:
        header = "# Java" if len(tech_stack["languages"]) > 1 else "# Development"
        has_development_header = True
        if tech_stack["package_manager"] == "maven":
            commands.extend(
                [
                    header,
                    "mvn clean install                # Build and install",
                    "mvn test                         # Run tests",
                    "",
                ]
            )
        elif tech_stack["package_manager"] == "gradle":
            commands.extend(
                [
                    header,
                    "./gradlew build                  # Build project",
                    "./gradlew test                   # Run tests",
                    "",
                ]
            )

    # Add generic development section if no language-specific commands were added
    if not has_development_header:
        commands.extend(
            [
                "# Development",
                "# Add your project-specific commands here",
                "",
            ]
        )

    # Always add backlog commands
    commands.extend(
        [
            "# Backlog (NEVER edit task files directly!)",
            "backlog task list --plain        # List tasks (AI-friendly output)",
            "backlog task 42 --plain          # View task details",
            'backlog task edit 42 -s "In Progress" -a @myself  # Start work',
            "backlog task edit 42 --check-ac 1  # Mark acceptance criterion done",
            "backlog task edit 42 -s Done     # Complete task",
        ]
    )

    commands_section = "\n".join(commands)

    # Build workflow section
    workflow_section = """## Workflow Commands

```bash
# Workflow Commands (stateful, sequential stages)
/flow:assess    # Evaluate SDD workflow suitability
/flow:specify   # Create/update feature specs
/flow:research  # Research and validation
/flow:plan      # Execute planning workflow
/flow:implement # Implementation with code review
/flow:validate  # QA, security, docs validation
/flow:submit-n-watch-pr  # Submit PR and watch CI/reviews

# Setup & Configuration Commands
/flow:init      # Initialize constitution (greenfield/brownfield)
/flow:reset     # Re-run workflow configuration prompts
/flow:intake    # Process INITIAL docs to create backlog tasks with context
```"""

    # Build memory imports section
    memory_imports = """## Memory Imports

This project uses flowspec's memory system for structured context. The following files provide context to Claude Code:

```
@import memory/constitution.md
@import memory/code-standards.md
@import memory/test-quality-standards.md
```

See the `memory/` directory for all available context files."""

    # Build troubleshooting section
    troubleshooting = []
    if "Python" in tech_stack["languages"]:
        if tech_stack["package_manager"] == "uv":
            troubleshooting.append("# Dependencies issues\nuv sync --force")
        else:
            troubleshooting.append(
                "# Dependencies issues\npip install -r requirements.txt --force-reinstall"
            )
        troubleshooting.append("\n# Check Python version\npython --version")

    if "JavaScript/TypeScript" in tech_stack["languages"]:
        # Determine JS package manager locally (don't use global which may be Python's)
        if (project_path / "pnpm-lock.yaml").exists():
            js_pm = "pnpm"
        elif (project_path / "yarn.lock").exists():
            js_pm = "yarn"
        else:
            js_pm = "npm"
        troubleshooting.append(
            f"# Dependencies issues\nrm -rf node_modules\n{js_pm} install"
        )

    if not troubleshooting:
        troubleshooting.append("# Add project-specific troubleshooting commands here")

    troubleshooting_section = "\n\n".join(troubleshooting)

    # Build project structure
    project_structure = [
        "├── docs/                   # Documentation",
        "├── memory/                 # Claude Code context files",
        "├── backlog/                # Task management",
        "├── .claude/                # Claude Code configuration",
    ]

    # Add common source and test directories once if any supported language is present
    has_code_dirs = any(
        lang in tech_stack["languages"]
        for lang in ("Python", "JavaScript/TypeScript", "Go", "Rust", "Java")
    )
    if has_code_dirs:
        project_structure.extend(
            [
                "├── src/                    # Source code",
                "├── tests/                  # Test suite",
            ]
        )

    # Add language-specific config files
    if "Python" in tech_stack["languages"]:
        project_structure.append("├── pyproject.toml          # Python project config")

    if "JavaScript/TypeScript" in tech_stack["languages"]:
        project_structure.append("├── package.json            # Node.js project config")

    if "Go" in tech_stack["languages"]:
        project_structure.append("├── go.mod                  # Go module config")

    if "Rust" in tech_stack["languages"]:
        project_structure.append("├── Cargo.toml              # Rust project config")

    if "Java" in tech_stack["languages"]:
        if tech_stack["package_manager"] == "maven":
            project_structure.append(
                "├── pom.xml                 # Maven project config"
            )
        elif tech_stack["package_manager"] == "gradle":
            project_structure.append(
                "├── build.gradle            # Gradle project config"
            )

    project_structure_section = "\n".join(project_structure)

    # Read template and substitute placeholders
    # Go up 3 levels: __init__.py -> flowspec_cli -> src -> flowspec (project root)
    template_path = (
        Path(__file__).parent.parent.parent / "templates" / "claude-md-template.md"
    )

    if template_path.exists():
        template_content = template_path.read_text()
    else:
        # Fallback template if file doesn't exist
        template_content = """# {PROJECT_NAME} - Claude Code Configuration

## Project Overview

**{PROJECT_NAME}** is a project initialized with flowspec.

{TECH_STACK_SECTION}

## Essential Commands

```bash
{COMMANDS_SECTION}
```

## Project Structure

```
{PROJECT_NAME}/
{PROJECT_STRUCTURE}
```

{WORKFLOW_SECTION}

{MEMORY_IMPORTS}

## Quick Troubleshooting

```bash
{TROUBLESHOOTING_SECTION}
```

---

*Generated by flowspec init. Customize this file for your project's specific needs.*
"""

    # Substitute placeholders
    content = template_content.replace("{PROJECT_NAME}", project_name)
    content = content.replace(
        "{PROJECT_DESCRIPTION}", "a project initialized with flowspec"
    )
    content = content.replace("{TECH_STACK_SECTION}", tech_stack_section)
    content = content.replace("{COMMANDS_SECTION}", commands_section)
    content = content.replace("{PROJECT_STRUCTURE}", project_structure_section)
    content = content.replace("{WORKFLOW_SECTION}", workflow_section)
    content = content.replace("{MEMORY_IMPORTS}", memory_imports)
    content = content.replace("{TROUBLESHOOTING_SECTION}", troubleshooting_section)

    # Write CLAUDE.md
    claude_md_path.write_text(content)


def generate_mcp_json(project_path: Path) -> bool:
    """Generate .mcp.json file with MCP server configurations.

    Includes common servers (backlog) and tech-stack-specific servers
    (e.g., flowspec-security for Python projects).

    Args:
        project_path: Path to the project directory

    Returns:
        True if file was created, False if it already existed (skipped).
    """
    mcp_json_path = project_path / ".mcp.json"

    # Skip if .mcp.json already exists
    if mcp_json_path.exists():
        return False

    # Detect tech stack to customize MCP servers
    tech_stack = detect_tech_stack(project_path)

    # Build MCP servers configuration
    mcp_servers = {
        "backlog": {
            "command": "backlog",
            "args": ["mcp"],
        }
    }

    # Add Python-specific servers
    if "Python" in tech_stack["languages"]:
        # Add flowspec security server for Python projects
        mcp_servers["flowspec-security"] = {
            "command": "uv",
            "args": [
                "--directory",
                ".",
                "run",
                "python",
                "-m",
                "flowspec_cli.security.mcp_server",
            ],
        }

    # Build the complete config
    mcp_config = {"mcpServers": mcp_servers}

    with open(mcp_json_path, "w", encoding="utf-8") as f:
        json.dump(mcp_config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return True


# Required MCP servers that must be present for flowspec workflows to function
REQUIRED_MCP_SERVERS = {
    "backlog": {
        "command": "backlog",
        "args": ["mcp"],
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@anthropic/claude-mcp-server-github"],
    },
    "serena": {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/oraios/serena",
            "serena-mcp-server",
            "--project",
            "${PWD}",
        ],
    },
}

# Recommended MCP servers that enhance agent capabilities
RECOMMENDED_MCP_SERVERS = {
    "playwright-test": {
        "command": "npx",
        "args": ["-y", "@anthropic/claude-mcp-server-playwright"],
    },
    "trivy": {
        "command": "npx",
        "args": ["-y", "@anthropic/claude-mcp-server-trivy"],
    },
    "semgrep": {
        "command": "npx",
        "args": ["-y", "@anthropic/claude-mcp-server-semgrep"],
    },
}


def update_mcp_json(
    project_path: Path,
    include_recommended: bool = False,
) -> tuple[bool, dict[str, list[str]]]:
    """Update .mcp.json with required MCP servers, preserving existing configuration.

    This function is designed for upgrades. Unlike generate_mcp_json() which skips
    existing files, this function merges new servers into existing configuration
    while preserving user customizations.

    Args:
        project_path: Path to the project directory
        include_recommended: If True, also add recommended servers (playwright, trivy, semgrep)

    Returns:
        Tuple of:
        - bool: True if file was modified, False if no changes needed
        - dict: Summary of changes {"added": [...], "unchanged": [...]}
    """
    mcp_json_path = project_path / ".mcp.json"

    # Load existing configuration if present
    existing_config: dict = {}
    if mcp_json_path.exists():
        try:
            with open(mcp_json_path, encoding="utf-8") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, OSError):
            # If file is corrupted, start fresh but log warning
            pass

    # Get existing servers or initialize empty dict
    existing_servers = existing_config.get("mcpServers", {})

    # Detect tech stack for conditional servers
    tech_stack = detect_tech_stack(project_path)

    # Build the set of servers to add
    servers_to_add = dict(REQUIRED_MCP_SERVERS)

    # Add tech-stack-specific required servers
    if "Python" in tech_stack["languages"]:
        servers_to_add["flowspec-security"] = {
            "command": "uv",
            "args": [
                "--directory",
                ".",
                "run",
                "python",
                "-m",
                "flowspec_cli.security.mcp_server",
            ],
        }

    # Add recommended servers if requested
    if include_recommended:
        servers_to_add.update(RECOMMENDED_MCP_SERVERS)

    # Track changes
    added: list[str] = []
    unchanged: list[str] = []

    # Merge: add new servers, preserve existing
    for server_name, server_config in servers_to_add.items():
        if server_name not in existing_servers:
            existing_servers[server_name] = server_config
            added.append(server_name)
        else:
            unchanged.append(server_name)

    # Build final config
    final_config = {"mcpServers": existing_servers}

    # Only write if there were changes
    if added:
        with open(mcp_json_path, "w", encoding="utf-8") as f:
            json.dump(final_config, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return True, {"added": added, "unchanged": unchanged}

    return False, {"added": [], "unchanged": list(existing_servers.keys())}


def check_mcp_server_availability(
    server_name: str,
    server_config: dict,
) -> tuple[bool, str]:
    """Check if an MCP server command is available.

    Performs a lightweight check to see if the server's command is executable.
    Does not actually start the server, just verifies the command exists.

    Args:
        server_name: Name of the server (for error messages)
        server_config: Server configuration with 'command' and optional 'args'

    Returns:
        Tuple of (is_available, message)
    """
    import shutil

    command = server_config.get("command", "")

    if not command:
        return False, f"{server_name}: No command specified"

    # For npx/uvx commands, check if npx/uvx is available
    if command in ("npx", "uvx"):
        if shutil.which(command) is None:
            return False, f"{server_name}: '{command}' not found in PATH"
        return True, f"{server_name}: {command} available"

    # For other commands, check if they're in PATH
    if shutil.which(command) is None:
        return False, f"{server_name}: '{command}' not found in PATH"

    return True, f"{server_name}: available"


def check_mcp_servers(
    project_path: Path,
    check_recommended: bool = False,
    console: Console | None = None,
) -> tuple[bool, dict[str, list[str]]]:
    """Check MCP server availability for a project.

    Verifies that required MCP servers are available and optionally checks
    recommended servers as well.

    Args:
        project_path: Path to the project directory
        check_recommended: If True, also check recommended servers
        console: Rich console for output (optional)

    Returns:
        Tuple of:
        - bool: True if all required servers are available
        - dict: {"available": [...], "missing_required": [...], "missing_recommended": [...]}
    """
    if console is None:
        console = Console()

    available: list[str] = []
    missing_required: list[str] = []
    missing_recommended: list[str] = []

    console.print("\n[bold]Checking MCP Server Availability[/bold]\n")

    # Check required servers
    console.print("[cyan]Required Servers:[/cyan]")
    for server_name, server_config in REQUIRED_MCP_SERVERS.items():
        is_available, message = check_mcp_server_availability(
            server_name, server_config
        )
        if is_available:
            console.print(f"  [green]✓[/green] {message}")
            available.append(server_name)
        else:
            console.print(f"  [red]✗[/red] {message}")
            missing_required.append(server_name)

    # Check tech-stack specific servers
    tech_stack = detect_tech_stack(project_path)
    if "Python" in tech_stack["languages"]:
        python_server = {
            "command": "python",
            "args": ["-m", "flowspec_cli.security.mcp_server"],
        }
        is_available, message = check_mcp_server_availability(
            "flowspec-security", python_server
        )
        if is_available:
            console.print(f"  [green]✓[/green] {message}")
            available.append("flowspec-security")
        else:
            console.print(f"  [yellow]⚠[/yellow] {message} (Python project, optional)")

    # Check recommended servers if requested
    if check_recommended:
        console.print("\n[cyan]Recommended Servers:[/cyan]")
        for server_name, server_config in RECOMMENDED_MCP_SERVERS.items():
            is_available, message = check_mcp_server_availability(
                server_name, server_config
            )
            if is_available:
                console.print(f"  [green]✓[/green] {message}")
                available.append(server_name)
            else:
                console.print(f"  [yellow]⚠[/yellow] {message}")
                missing_recommended.append(server_name)

    console.print()

    # Summary
    all_required_available = len(missing_required) == 0

    if all_required_available:
        console.print("[green]✓ All required MCP servers are available[/green]")
    else:
        console.print(
            f"[red]✗ Missing {len(missing_required)} required server(s): "
            f"{', '.join(missing_required)}[/red]"
        )

    if missing_recommended:
        console.print(
            f"[yellow]⚠ Missing {len(missing_recommended)} recommended server(s): "
            f"{', '.join(missing_recommended)}[/yellow]"
        )

    return all_required_available, {
        "available": available,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
    }


def generate_vscode_extensions(project_path: Path) -> bool:
    """Generate .vscode/extensions.json with tech-stack specific recommendations.

    Args:
        project_path: Path to the project directory

    Returns:
        True if file was created, False if it was updated (already existed).
    """
    vscode_dir = project_path / ".vscode"
    extensions_path = vscode_dir / "extensions.json"

    # Track if file existed before for return value
    file_existed = extensions_path.exists()

    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(parents=True, exist_ok=True)

    # Load existing extensions.json if it exists
    existing_recommendations = []
    if file_existed:
        try:
            with open(extensions_path, encoding="utf-8") as f:
                existing_config = json.load(f)
                existing_recommendations = existing_config.get("recommendations", [])
        except (json.JSONDecodeError, OSError):
            # If the existing file is unreadable/corrupted or contains invalid JSON,
            # ignore it and fall back to an empty recommendation list.
            pass

    # Detect tech stack
    tech_stack = detect_tech_stack(project_path)

    # Build recommendations list
    recommendations = set(existing_recommendations)

    # Base extensions for all projects
    base_extensions = [
        "github.copilot",
        "github.copilot-chat",
        "editorconfig.editorconfig",
    ]
    recommendations.update(base_extensions)

    # Python-specific extensions
    if "Python" in tech_stack["languages"]:
        python_extensions = [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "charliermarsh.ruff",
        ]
        recommendations.update(python_extensions)

    # JavaScript/TypeScript-specific extensions
    if "JavaScript/TypeScript" in tech_stack["languages"]:
        js_extensions = [
            "dbaeumer.vscode-eslint",
            "esbenp.prettier-vscode",
        ]
        recommendations.update(js_extensions)

    # Go-specific extensions
    if "Go" in tech_stack["languages"]:
        go_extensions = [
            "golang.go",
        ]
        recommendations.update(go_extensions)

    # Rust-specific extensions
    if "Rust" in tech_stack["languages"]:
        rust_extensions = [
            "rust-lang.rust-analyzer",
        ]
        recommendations.update(rust_extensions)

    # Java-specific extensions
    if "Java" in tech_stack["languages"]:
        java_extensions = [
            "redhat.java",
            "vscjava.vscode-java-pack",
        ]
        recommendations.update(java_extensions)

    # Docker extension if Dockerfile or docker-compose configuration exists
    if (
        (project_path / "Dockerfile").exists()
        or (project_path / "docker-compose.yml").exists()
        or (project_path / "docker-compose.yaml").exists()
    ):
        recommendations.add("ms-azuretools.vscode-docker")

    # Build config
    extensions_config = {"recommendations": sorted(recommendations)}

    # Write extensions.json
    with open(extensions_path, "w", encoding="utf-8") as f:
        json.dump(extensions_config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return not file_existed


class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """

    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {
            "pending": 0,
            "running": 1,
            "done": 2,
            "error": 3,
            "skipped": 4,
        }
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append(
                {"key": key, "label": label, "status": "pending", "detail": ""}
            )
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append(
            {"key": key, "label": key, "status": status, "detail": detail}
        )
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = (
                        f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                    )
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree


def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return "up"
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return "down"

    if key == readchar.key.ENTER:
        return "enter"

    if key == readchar.key.ESC:
        return "escape"

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key


def select_with_arrows(
    options: dict, prompt_text: str = "Select an option", default_key: str = None
) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.

    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with

    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row(
            "", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]"
        )

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(
            create_selection_panel(),
            console=console,
            transient=True,
            auto_refresh=False,
        ) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == "enter":
                        selected_key = option_keys[selected_index]
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key


def parse_agent_list(agent_str: str) -> list[str]:
    """
    Parse comma-separated agent list into individual agent names.

    Args:
        agent_str: Comma-separated string of agent names (e.g., "claude,copilot,cursor-agent")

    Returns:
        List of agent names with whitespace stripped and duplicates removed

    Examples:
        >>> parse_agent_list("claude,copilot")
        ['claude', 'copilot']
        >>> parse_agent_list("claude, copilot, cursor-agent")
        ['claude', 'copilot', 'cursor-agent']
        >>> parse_agent_list("claude")
        ['claude']
        >>> parse_agent_list("claude,copilot,claude")
        ['claude', 'copilot']
    """
    if not agent_str or not agent_str.strip():
        return []

    # Split by comma and strip whitespace from each agent name
    agents = [agent.strip() for agent in agent_str.split(",")]

    # Filter out empty strings and deduplicate while preserving order
    seen = set()
    result = []
    for agent in agents:
        if agent and agent not in seen:
            seen.add(agent)
            result.append(agent)
    return result


def select_multiple_with_checkboxes(
    options: dict,
    prompt_text: str = "Select options (space to toggle, enter to confirm)",
    default_keys: list[str] = None,
) -> list[str]:
    """
    Interactive multi-selection using checkboxes with Rich Live display.

    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_keys: List of default option keys to start with (pre-selected)

    Returns:
        List of selected option keys

    Examples:
        >>> options = {"claude": "Claude Code", "copilot": "GitHub Copilot"}
        >>> selected = select_multiple_with_checkboxes(options, "Choose AI assistants:")
        >>> # Returns list like ['claude', 'copilot'] based on user selection
    """
    option_keys = list(options.keys())
    selected_index = 0

    # Track which options are checked (selected)
    checked_keys = set(default_keys) if default_keys else set()

    # Validate default keys
    if default_keys:
        for key in default_keys:
            if key not in option_keys:
                console.print(
                    f"[yellow]Warning: Default key '{key}' not in options[/yellow]"
                )

    selected_keys = None

    def create_selection_panel():
        """Create the selection panel with checkboxes."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)  # Arrow/pointer
        table.add_column(style="white", justify="left", width=5)  # Checkbox
        table.add_column(style="white", justify="left")  # Option text

        for i, key in enumerate(option_keys):
            pointer = "▶" if i == selected_index else " "
            checkbox = "[✓]" if key in checked_keys else "[ ]"

            if i == selected_index:
                # Highlight current row
                table.add_row(
                    pointer,
                    f"[cyan]{checkbox}[/cyan]",
                    f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]",
                )
            else:
                table.add_row(
                    pointer, checkbox, f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]"
                )

        table.add_row("", "", "")
        table.add_row(
            "",
            "",
            "[dim]↑/↓: navigate | Space: toggle | Enter: confirm | Esc: cancel[/dim]",
        )

        # Show selection count
        count_text = f"[dim]Selected: {len(checked_keys)} items[/dim]"
        table.add_row("", "", count_text)

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_keys, selected_index, checked_keys
        with Live(
            create_selection_panel(),
            console=console,
            transient=True,
            auto_refresh=False,
        ) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == " ":  # Space to toggle checkbox
                        current_key = option_keys[selected_index]
                        if current_key in checked_keys:
                            checked_keys.remove(current_key)
                        else:
                            checked_keys.add(current_key)
                    elif key == "enter":
                        selected_keys = list(checked_keys)
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_keys is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_keys


console = Console()


class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


# Workflow transitions with their default validation modes
# Each transition can have a different validation mode
# NOTE: operate removed - deployment is outer loop (use /ops:* commands)
WORKFLOW_TRANSITIONS = [
    {"name": "assess", "from": "To Do", "to": "Assessed", "default": "NONE"},
    {"name": "research", "from": "Assessed", "to": "Researched", "default": "NONE"},
    {"name": "specify", "from": "Researched", "to": "Specified", "default": "NONE"},
    {"name": "plan", "from": "Specified", "to": "Planned", "default": "NONE"},
    {"name": "implement", "from": "Planned", "to": "Implemented", "default": "NONE"},
    {"name": "validate", "from": "Implemented", "to": "Validated", "default": "NONE"},
]


def prompt_validation_modes() -> dict[str, str]:
    """Interactively prompt for validation mode on each transition.

    Returns:
        Dict mapping transition name to validation mode string.
        Example: {"assess": "none", "specify": 'KEYWORD["PRD_APPROVED"]'}

    Raises:
        typer.Exit: If user cancels with Ctrl+C.
    """
    # Transitions to configure with descriptions
    transitions_info = [
        ("assess", "To Do → Assessed", "after /flow:assess"),
        ("specify", "Assessed → Specified", "after /flow:specify, produces PRD"),
        ("research", "Specified → Researched", "after /flow:research"),
        ("plan", "Researched → Planned", "after /flow:plan, produces ADRs"),
        ("implement", "Planned → In Implementation", "after /flow:implement"),
        ("validate", "In Implementation → Validated", "after /flow:validate"),
        # NOTE: operate removed - deployment is outer loop
    ]

    modes: dict[str, str] = {}

    console.print()
    console.print("[cyan]== Workflow Transition Validation Configuration ==[/cyan]")
    console.print()
    console.print("For each workflow transition, choose a validation mode:")
    console.print("  - [green]NONE[/green]: No gate, proceed immediately (default)")
    console.print("  - [yellow]KEYWORD[/yellow]: Require user to type approval keyword")
    console.print("  - [blue]PULL_REQUEST[/blue]: Require PR to be merged")
    console.print()

    try:
        for i, (name, state_change, description) in enumerate(transitions_info, 1):
            console.print(f"[dim]{i}. {state_change}[/dim] ({description})")
            console.print("   [1] NONE (default)")
            console.print("   [2] KEYWORD")
            console.print("   [3] PULL_REQUEST")

            choice = typer.prompt("   > ", default="1")

            # Validate and normalize choice
            if choice not in ["1", "2", "3"]:
                console.print(
                    f"   [yellow]Invalid choice '{choice}', using NONE[/yellow]"
                )
                choice = "1"

            if choice == "2":
                keyword = typer.prompt("   Enter approval keyword", default="APPROVED")
                if not keyword or not keyword.strip():
                    console.print(
                        "   [yellow]Empty keyword, using default 'APPROVED'[/yellow]"
                    )
                    keyword = "APPROVED"
                modes[name] = f'KEYWORD["{keyword.strip()}"]'
            elif choice == "3":
                modes[name] = "pull-request"
            else:
                modes[name] = "none"

            console.print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Validation mode configuration cancelled[/yellow]")
        raise typer.Exit(1)

    return modes


def display_validation_summary(modes: dict[str, str]) -> None:
    """Display a formatted summary of configured validation modes.

    Args:
        modes: Dict mapping transition name to validation mode string.
    """
    console.print()
    console.print("[cyan]== Validation Mode Summary ==[/cyan]")
    console.print()

    # Filter to show only non-default modes
    non_default = {k: v for k, v in modes.items() if v.lower() != "none"}

    if non_default:
        console.print("[green]Custom validation modes:[/green]")
        for name, mode in non_default.items():
            # Format the mode for display
            if mode.lower().startswith("keyword["):
                display_mode = mode.upper()
            elif mode.lower() == "pull-request":
                display_mode = "PULL_REQUEST"
            else:
                display_mode = mode.upper()

            console.print(f"  [cyan]{name:12}[/cyan] → {display_mode}")
    else:
        console.print("[dim]All transitions using NONE (default)[/dim]")

    console.print()


def generate_flowspec_workflow_yml(
    project_path: Path,
    transition_modes: dict[str, str] | None = None,
) -> None:
    """Generate flowspec_workflow.yml with per-transition validation modes.

    Args:
        project_path: Path to the project directory.
        transition_modes: Dict mapping transition name to validation mode.
                         If None, uses defaults (all NONE).
    """
    if transition_modes is None:
        transition_modes = {}

    # Map CLI mode values to YAML format
    def format_mode(mode: str) -> str:
        mode = mode.lower()
        if mode == "none":
            return "NONE"
        elif mode == "keyword":
            return 'KEYWORD["APPROVED"]'
        elif mode == "pull-request" or mode == "pull_request":
            return "PULL_REQUEST"
        elif mode.startswith("keyword["):
            # Already in KEYWORD["..."] format
            return mode.upper()
        return "NONE"

    # Build YAML content
    lines = [
        "# Flowspec Workflow Configuration",
        "# Generated by: flowspec init",
        "#",
        "# Validation modes:",
        "#   NONE - No gate, immediate pass-through",
        '#   KEYWORD["<string>"] - Require user to type exact keyword',
        "#   PULL_REQUEST - Require PR to be merged",
        "",
        'version: "1.0"',
        "",
        "transitions:",
    ]

    for t in WORKFLOW_TRANSITIONS:
        name = t["name"]
        mode = transition_modes.get(name, t["default"])
        formatted_mode = format_mode(mode)

        lines.append(f"  - name: {name}")
        lines.append(f'    from: "{t["from"]}"')
        lines.append(f'    to: "{t["to"]}"')
        lines.append(f"    validation: {formatted_mode}")
        lines.append("")

    # Write the file
    workflow_file = project_path / "flowspec_workflow.yml"
    workflow_file.write_text("\n".join(lines), encoding="utf-8")


def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split("\n")
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


@app.callback()
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Show banner when no subcommand is provided."""
    if (
        ctx.invoked_subcommand is None
        and "--help" not in sys.argv
        and "-h" not in sys.argv
    ):
        show_banner()
        show_version_info(detailed=True, centered=True)
        console.print()
        console.print(
            Align.center("[dim]Run 'flowspec --help' for usage information[/dim]")
        )
        console.print()


@app.command()
def version():
    """Show detailed version information for all components."""
    show_version_info(detailed=True)


@app.command(name="repo-version")
def repo_version():
    """Show version information for tools installed in the current repository.

    Reads the .flowspec/.version file to show which versions of flowspec,
    backlog-md, and beads were used to initialize or upgrade this repository.

    This is useful for troubleshooting version mismatches or understanding
    what tools were used to set up the project.
    """
    show_banner()

    # Detect project root
    project_path = Path.cwd()
    version_data = read_version_tracking_file(project_path)

    if not version_data:
        console.print("[yellow]No version tracking file found.[/yellow]")
        console.print()
        console.print("This could mean:")
        console.print("  • This repository was not initialized with flowspec")
        console.print(
            "  • The repository was initialized before version tracking was added"
        )
        console.print("  • You are not in a flowspec-initialized directory")
        console.print()
        console.print(
            "[cyan]Run 'flowspec upgrade-repo' to update and create version tracking.[/cyan]"
        )
        return

    versions = version_data.get("versions", {})
    metadata = version_data.get("metadata", {})

    # Build version table
    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")

    # Add rows for each component
    if "flowspec" in versions:
        table.add_row("flowspec", versions["flowspec"])
    if "backlog" in versions:
        table.add_row("backlog-md", versions["backlog"])
    if "beads" in versions:
        table.add_row("beads", versions["beads"])

    console.print()
    console.print(table)
    console.print()

    # Show metadata if available
    if metadata:
        meta_table = Table(show_header=True, box=None, padding=(0, 2))
        meta_table.add_column("Metadata", style="cyan")
        meta_table.add_column("Value", style="dim")

        if "installed_at" in metadata:
            meta_table.add_row("Installed at", metadata["installed_at"])
        if "upgraded_at" in metadata:
            meta_table.add_row("Last upgraded", metadata["upgraded_at"])
        if "last_checked" in metadata:
            meta_table.add_row("Last checked", metadata["last_checked"])

        console.print(meta_table)
        console.print()

    # Show comparison with currently installed tools
    console.print("[cyan]Currently installed tools:[/cyan]")
    current_table = Table(show_header=True, box=None, padding=(0, 2))
    current_table.add_column("Component", style="cyan")
    current_table.add_column("Installed", style="green")
    current_table.add_column("In Repo", style="dim")
    current_table.add_column("Status", style="yellow")

    # Check flowspec
    current_flowspec = __version__
    repo_flowspec = versions.get("flowspec", "-")
    if current_flowspec == repo_flowspec:
        status = "[green]✓ Match[/green]"
    elif current_flowspec and repo_flowspec != "-":
        status = "[yellow]⚠ Mismatch[/yellow]"
    else:
        status = "[dim]-[/dim]"
    current_table.add_row("flowspec", current_flowspec, repo_flowspec, status)

    # Check backlog
    current_backlog = check_backlog_installed_version() or "-"
    repo_backlog = versions.get("backlog", "-")
    if current_backlog == repo_backlog:
        status = "[green]✓ Match[/green]"
    elif current_backlog != "-" and repo_backlog != "-":
        status = "[yellow]⚠ Mismatch[/yellow]"
    else:
        status = "[dim]-[/dim]"
    current_table.add_row("backlog-md", current_backlog, repo_backlog, status)

    # Check beads
    current_beads = check_beads_installed_version() or "-"
    repo_beads = versions.get("beads", "-")
    if current_beads == repo_beads:
        status = "[green]✓ Match[/green]"
    elif current_beads != "-" and repo_beads != "-":
        status = "[yellow]⚠ Mismatch[/yellow]"
    else:
        status = "[dim]-[/dim]"
    current_table.add_row("beads", current_beads, repo_beads, status)

    console.print(current_table)
    console.print()

    console.print("[dim]Use 'flowspec version' to see available updates[/dim]")


def run_command(
    cmd: list[str],
    check_return: bool = True,
    capture: bool = False,
    shell: bool = False,
) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(
                cmd, check=check_return, capture_output=True, text=True, shell=shell
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, "stderr") and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None


def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.

    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results

    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI after `claude migrate-installer`
    # See: https://github.com/github/spec-kit/issues/123
    # The migrate-installer command REMOVES the original executable from PATH
    # and creates an alias at ~/.claude/local/claude instead
    # This path should be prioritized over other claude executables in PATH
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True

    found = shutil.which(tool) is not None

    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")

    return found


def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()

    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def init_git_repo(
    project_path: Path, quiet: bool = False
) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.

    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]Initializing git repository...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from Specify template"],
            check=True,
            capture_output=True,
            text=True,
        )
        if not quiet:
            console.print("[green]✓[/green] Git repository initialized")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"

        if not quiet:
            console.print(f"[red]Error initializing git repository:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)


def download_template_from_github(
    ai_assistant: str,
    download_dir: Path,
    *,
    script_type: str = "sh",
    verbose: bool = True,
    show_progress: bool = True,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    repo_owner: str = None,
    repo_name: str = None,
    version: str = None,
) -> Tuple[Path, dict]:
    # Use provided repo or default to flowspec
    if repo_owner is None:
        repo_owner = REPO_OWNER
    if repo_name is None:
        repo_name = REPO_NAME
    if version is None:
        version = REPO_DEFAULT_VERSION

    if client is None:
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print(
            f"[cyan]Fetching release information from {repo_owner}/{repo_name}...[/cyan]"
        )

    # Resolve effective token once so env-based tokens are honored consistently (including fallbacks)
    effective_token = _github_token(github_token)

    def _req(url: str, retry_without_auth: bool = True) -> httpx.Response:
        """Make GitHub API request with automatic fallback for invalid tokens.

        For public repositories, if we get a 401 with authentication, retry without auth.
        This handles cases where an invalid/expired token is present.

        Args:
            url: The GitHub API URL to request.
            retry_without_auth: If True (default), retry without auth on 401 errors when a token was provided. Useful for public repos with invalid/expired tokens.

        Returns:
            The HTTP response from the GitHub API.
        """
        response = client.get(
            url,
            timeout=30,
            follow_redirects=True,
            headers=_github_headers(effective_token),
        )

        # If we got 401/403 with a token, the token might be invalid/expired
        # For public repos, retry without authentication
        # 401 = Invalid credentials, 403 = Rate limited or forbidden (can happen with bad tokens)
        if (
            response.status_code in (401, 403)
            and effective_token
            and retry_without_auth
        ):
            if debug:
                console.print(
                    f"[yellow]Got {response.status_code} with token - retrying without authentication for public repo[/yellow]"
                )
            response = client.get(
                url,
                timeout=30,
                follow_redirects=True,
                headers=_github_headers(
                    skip_auth=True
                ),  # Explicitly skip auth for retry
            )

        return response

    def _pick_latest(releases: list[dict]) -> Optional[dict]:
        filtered = [
            r for r in releases if not r.get("draft") and not r.get("prerelease")
        ]
        return filtered[0] if filtered else (releases[0] if releases else None)

    try:
        release_data = None
        last_status_code = None
        if version == "latest" or version is None:
            r = _req(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
            )
            last_status_code = r.status_code
            if r.status_code == 200:
                release_data = r.json()
            else:
                r2 = _req(
                    f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?per_page=20"
                )
                last_status_code = r2.status_code
                if r2.status_code == 200:
                    release_data = _pick_latest(r2.json())
        else:
            r = _req(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{version}"
            )
            last_status_code = r.status_code
            if r.status_code == 200:
                release_data = r.json()
            else:
                alt = version[1:] if version.startswith("v") else f"v{version}"
                r2 = _req(
                    f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{alt}"
                )
                last_status_code = r2.status_code
                if r2.status_code == 200:
                    release_data = r2.json()
                else:
                    r3 = _req(
                        f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?per_page=50"
                    )
                    last_status_code = r3.status_code
                    if r3.status_code == 200:
                        for rel in r3.json():
                            tag = rel.get("tag_name", "")
                            if tag in {version, alt}:
                                release_data = rel
                                break

        if not release_data:
            error_msg = (
                f"Could not resolve release for {repo_owner}/{repo_name} (version='{version}')\n"
                f"Last HTTP status: {last_status_code}\n"
                f"Tried: /releases/latest, /releases/tags/<tag> with v/no-v, and /releases list"
            )
            # Add authentication hints for common error codes
            if last_status_code in (401, 403):
                if effective_token:
                    if last_status_code == 403:
                        error_msg += (
                            "\n\n[yellow]Rate Limit or Auth Error (403):[/yellow]\n"
                            "The request was retried without your token, but still failed.\n"
                            "This is likely due to GitHub API rate limiting (60 requests/hour per IP).\n\n"
                            "To fix this:\n"
                            "  1. Wait ~30-60 minutes for the rate limit to reset, OR\n"
                            "  2. Use a DIFFERENT GitHub token (your current token may be rate-limited)\n"
                            "  3. Check your token at https://github.com/settings/tokens\n"
                            f"  4. If {repo_owner}/{repo_name} is private, ensure token has 'repo' scope"
                        )
                    else:
                        error_msg += (
                            "\n\n[yellow]Authentication Error:[/yellow]\n"
                            "The provided GitHub token appears to be invalid or expired.\n"
                            "The request was automatically retried without authentication, but still failed.\n\n"
                            "This could mean:\n"
                            "  1. The repository is private and requires a valid token\n"
                            "  2. The token has expired or been revoked\n"
                            "  3. The token lacks required permissions\n\n"
                            "To fix this:\n"
                            "  1. Check your token is still valid at https://github.com/settings/tokens\n"
                            "  2. Ensure it has 'repo' or 'public_repo' scope\n"
                            "  3. Remove invalid tokens from GITHUB_FLOWSPEC environment variable\n"
                            f"  4. If {repo_owner}/{repo_name} is private, generate a new token"
                        )
                else:
                    # 403 without a token is almost always rate limiting
                    if last_status_code == 403:
                        error_msg += (
                            "\n\n[yellow]Rate Limit Exceeded (403):[/yellow]\n"
                            "GitHub limits unauthenticated API requests to 60/hour per IP.\n"
                            "Your IP has likely exceeded this limit.\n\n"
                            "To fix this:\n"
                            "  1. Wait ~30-60 minutes for the rate limit to reset, OR\n"
                            "  2. Provide a GitHub token for 5000 requests/hour:\n"
                            "     - Use --github-token <token> flag\n"
                            "     - Or set GITHUB_FLOWSPEC environment variable\n"
                            "     - Create a token at https://github.com/settings/tokens\n"
                            "       (only 'public_repo' scope needed for public repos)"
                        )
                    else:
                        error_msg += (
                            "\n\n[yellow]Authentication Error:[/yellow]\n"
                            "This may be due to insufficient permissions or missing authentication.\n"
                            "Try providing a GitHub token with the following options:\n"
                            "  1. Use --github-token <token> flag\n"
                            "  2. Set GITHUB_FLOWSPEC environment variable\n"
                            f"  3. Ensure your token has 'repo' or 'public_repo' scope for {repo_owner}/{repo_name}"
                        )
            elif last_status_code == 404:
                if not effective_token:
                    error_msg += (
                        "\n\n[yellow]Not Found (404):[/yellow]\n"
                        "This repository or its releases may be private, or the release may not exist.\n"
                        "If this is a private repository, provide authentication:\n"
                        "  1. Use --github-token <token> flag\n"
                        "  2. Set GITHUB_FLOWSPEC environment variable"
                    )
                else:
                    error_msg += (
                        "\n\n[yellow]Not Found (404):[/yellow]\n"
                        "The release was not found. This could mean:\n"
                        "  1. No releases exist for this repository\n"
                        "  2. The specified version does not exist\n"
                        "  3. Your token lacks permissions to access the releases"
                    )
            raise RuntimeError(error_msg)
    except Exception as e:
        msg = str(e)
        if debug:
            try:
                meta = _req(f"https://api.github.com/repos/{repo_owner}/{repo_name}")
                msg += f"\nRepo visibility: {meta.json().get('visibility', '?')} (HTTP {meta.status_code})"
            except Exception:
                pass
        console.print("[red]Error fetching release information[/red]")
        console.print(Panel(msg, title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset
        for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(
            f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])"
        )
        asset_names = [a.get("name", "?") for a in assets]
        console.print(
            Panel(
                "\n".join(asset_names) or "(no assets)",
                title="Available Assets",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    api_asset_url = asset.get("url")
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print("[cyan]Downloading template...[/cyan]")

    try:
        # Prefer API asset URL when a token is available (works for private and public assets)
        response = None
        if effective_token and api_asset_url:
            api_headers = _github_headers(effective_token).copy()
            api_headers["Accept"] = "application/octet-stream"
            response = client.get(
                api_asset_url,
                timeout=60,
                follow_redirects=True,
                headers=api_headers,
            )
            # If API route fails (e.g., insufficient scope), fall back to browser URL
            if response.status_code != 200:
                response = client.get(
                    download_url,
                    timeout=60,
                    follow_redirects=True,
                    headers=_github_headers(effective_token),
                )
        else:
            # No token: try browser URL (public-only)
            response = client.get(
                download_url,
                timeout=60,
                follow_redirects=True,
                headers=_github_headers(effective_token),
            )
        if response.status_code != 200:
            body_sample = (getattr(response, "text", "") or "")[:400]
            hint = ""
            if response.status_code == 401:
                hint = (
                    "\n\n[yellow]Authentication Required (401):[/yellow]\n"
                    "Your GitHub token is invalid or has expired.\n"
                    "Please provide a valid token:\n"
                    "  1. Use --github-token <token> flag\n"
                    "  2. Set GITHUB_FLOWSPEC environment variable\n"
                    "  3. Ensure the token has not expired"
                )
            elif response.status_code == 403:
                hint = (
                    "\n\n[yellow]Access Forbidden (403):[/yellow]\n"
                    "Your token lacks the required permissions to download this asset.\n"
                    "Ensure your GitHub token has:\n"
                    "  1. 'repo' scope for private repositories\n"
                    "  2. 'public_repo' scope for public repositories\n"
                    f"  3. Access to {repo_owner}/{repo_name}"
                )
            elif response.status_code == 404:
                if not effective_token:
                    hint = (
                        "\n\n[yellow]Asset Not Found (404):[/yellow]\n"
                        "This repository or its release assets may be private.\n"
                        "Provide authentication to access private assets:\n"
                        "  1. Use --github-token <token> flag\n"
                        "  2. Set GITHUB_FLOWSPEC environment variable"
                    )
                else:
                    hint = (
                        "\n\n[yellow]Asset Not Found (404):[/yellow]\n"
                        "The release asset could not be found. This could mean:\n"
                        "  1. The asset has been deleted\n"
                        "  2. Your token lacks access to this repository\n"
                        "  3. The release does not contain the expected asset"
                    )
            raise RuntimeError(
                f"Download failed with HTTP {response.status_code}\n"
                f"Headers: {response.headers}\n"
                f"Body (truncated): {body_sample}{hint}"
            )
        with open(zip_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        console.print("[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)
    if verbose:
        console.print(f"Downloaded: {filename}")
    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url,
    }
    return zip_path, metadata


def download_and_build_from_branch(
    branch: str,
    ai_assistant: str,
    script_type: str = "sh",
    download_dir: Path = None,
    *,
    verbose: bool = True,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    repo_owner: str = None,
    repo_name: str = None,
) -> Tuple[Path, dict]:
    """Download repo from a branch and build template ZIP locally.

    This is used for testing branches before release. It:
    1. Downloads the repo zipball from the branch
    2. Extracts to a temp directory
    3. Runs create-release-packages.sh to build agent-specific ZIPs
    4. Returns path to the built ZIP

    Args:
        branch: Git branch name to download from
        ai_assistant: AI assistant type (claude, copilot, etc.)
        script_type: Script type (sh or ps)
        download_dir: Directory for downloads (uses temp if None)
        verbose: Show progress messages
        client: HTTP client to use
        debug: Show debug output
        github_token: GitHub token for API requests
        repo_owner: Repository owner
        repo_name: Repository name

    Returns:
        Tuple of (zip_path, metadata_dict)

    Raises:
        typer.Exit: On download or build errors
    """
    import subprocess

    if repo_owner is None:
        repo_owner = REPO_OWNER
    if repo_name is None:
        repo_name = REPO_NAME
    if download_dir is None:
        download_dir = Path(tempfile.mkdtemp())
    if client is None:
        client = httpx.Client(verify=ssl_context)

    effective_token = _github_token(github_token)

    if verbose:
        console.print(
            f"[cyan]Downloading {repo_owner}/{repo_name} branch '{branch}'...[/cyan]"
        )

    # Download zipball from branch
    zipball_url = (
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{branch}"
    )

    try:
        response = client.get(
            zipball_url,
            timeout=120,
            follow_redirects=True,
            headers=_github_headers(effective_token),
        )

        if response.status_code == 404:
            console.print(
                f"[red]Branch '{branch}' not found in {repo_owner}/{repo_name}[/red]"
            )
            raise typer.Exit(1)

        if response.status_code != 200:
            console.print(
                f"[red]Failed to download branch: HTTP {response.status_code}[/red]"
            )
            if debug:
                console.print(f"Response: {response.text[:500]}")
            raise typer.Exit(1)

        # Save zipball
        branch_zip = download_dir / f"{repo_name}-{branch}.zip"
        with open(branch_zip, "wb") as f:
            f.write(response.content)

        if verbose:
            console.print(f"[cyan]Downloaded:[/cyan] {len(response.content):,} bytes")

    except httpx.RequestError as e:
        console.print(f"[red]Network error downloading branch:[/red] {e}")
        raise typer.Exit(1)

    # Extract zipball
    extract_dir = download_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(branch_zip, "r") as zf:
            zf.extractall(extract_dir)
    except zipfile.BadZipFile:
        console.print("[red]Downloaded file is not a valid ZIP[/red]")
        raise typer.Exit(1)

    # Find the extracted directory (GitHub adds a prefix like 'jpoley-flowspec-abc123/')
    extracted_items = list(extract_dir.iterdir())
    if len(extracted_items) != 1 or not extracted_items[0].is_dir():
        console.print("[red]Unexpected ZIP structure[/red]")
        raise typer.Exit(1)

    source_dir = extracted_items[0]

    if verbose:
        console.print(f"[cyan]Extracted to:[/cyan] {source_dir.name}")

    # Run create-release-packages.sh to build the template
    build_script = (
        source_dir / ".github" / "workflows" / "scripts" / "create-release-packages.sh"
    )

    if not build_script.exists():
        console.print(
            "[red]Build script not found in branch[/red]\n"
            f"Expected: {build_script.relative_to(source_dir)}"
        )
        raise typer.Exit(1)

    if verbose:
        console.print(
            f"[cyan]Building templates for {ai_assistant} ({script_type})...[/cyan]"
        )

    try:
        # Run the build script with limited agent/script to speed up
        env = os.environ.copy()
        env["AGENTS"] = ai_assistant
        env["SCRIPTS"] = script_type

        # Pass branch name without "v" prefix - script handles versioning
        result = subprocess.run(
            ["bash", str(build_script), branch],
            cwd=str(source_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            console.print("[red]Template build failed[/red]")
            if result.stderr:
                console.print(
                    Panel(result.stderr[:1000], title="Build Error", border_style="red")
                )
            raise typer.Exit(1)

        if verbose and debug:
            console.print(f"[dim]{result.stdout}[/dim]")

    except subprocess.TimeoutExpired:
        console.print("[red]Template build timed out[/red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(
            "[red]bash not found - required for building templates from branch[/red]"
        )
        raise typer.Exit(1)

    # Find the built ZIP
    genreleases_dir = source_dir / ".genreleases"
    expected_zip = f"spec-kit-template-{ai_assistant}-{script_type}-v{branch}.zip"
    built_zip = genreleases_dir / expected_zip

    if not built_zip.exists():
        # Try finding any matching ZIP (version might differ)
        pattern = f"spec-kit-template-{ai_assistant}-{script_type}-*.zip"
        matches = list(genreleases_dir.glob(pattern))
        if matches:
            built_zip = matches[0]
        else:
            console.print(f"[red]Built template not found:[/red] {expected_zip}")
            if genreleases_dir.exists():
                console.print(f"Available: {list(genreleases_dir.glob('*.zip'))}")
            raise typer.Exit(1)

    # Copy to download_dir for consistent handling
    final_zip = download_dir / built_zip.name
    shutil.copy2(built_zip, final_zip)

    if verbose:
        console.print(f"[green]✓[/green] Built template: {final_zip.name}")

    metadata = {
        "filename": final_zip.name,
        "size": final_zip.stat().st_size,
        "release": f"branch:{branch}",
        "branch": branch,
        "source_dir": str(source_dir),
    }

    return final_zip, metadata


def _cleanup_legacy_speckit_files(project_path: Path, ai_assistants: list[str]) -> None:
    """Remove legacy speckit.* files from base spec-kit after flowspec overlay.

    The base spec-kit uses flat speckit.* file naming (e.g., speckit.specify.md)
    in the commands directory. The flowspec extension uses a spec/ subdirectory
    structure (e.g., spec/specify.md) which provides the /spec:* command namespace.

    After the flowspec extension overlays the base, both structures exist:
    - .claude/commands/speckit.*.md (legacy, should be removed)
    - .claude/commands/spec/*.md (flowspec, should remain)

    This function removes the legacy files to avoid confusion.
    """
    # Map of AI assistant to their commands directory
    agent_command_dirs = {
        "claude": ".claude/commands",
        "cursor-agent": ".cursor/commands",
        "gemini": ".gemini/commands",
        "copilot": ".github/prompts",
        "qwen": ".qwen/commands",
        "opencode": ".opencode/command",
        "windsurf": ".windsurf/workflows",
        "codex": ".codex/prompts",
        "kilocode": ".kilocode/workflows",
        "auggie": ".augment/commands",
        "roo": ".roo/commands",
        "codebuddy": ".codebuddy/commands",
        "q": ".amazonq/prompts",
    }

    for agent in ai_assistants:
        if agent not in agent_command_dirs:
            continue

        commands_dir = project_path / agent_command_dirs[agent]
        if not commands_dir.exists():
            continue

        # Find and remove legacy speckit.* files
        for item in commands_dir.iterdir():
            if item.is_file() and item.name.startswith("speckit."):
                item.unlink()


def _extract_zip_to_project(
    zip_path: Path,
    project_path: Path,
) -> None:
    """Extract ZIP contents to project directory, handling nested structures.

    Automatically merges directories recursively when destination exists to avoid
    FileExistsError with shutil.copytree(..., dirs_exist_ok=True), which allows
    the target directory to exist but will still raise FileExistsError if files
    in the source already exist at their destination paths.

    Args:
        zip_path: Path to the ZIP file to extract
        project_path: Target project directory
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        # Always extract to temp dir first to check for nested structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_ref.extractall(temp_path)
            extracted_items = list(temp_path.iterdir())

            # Check if ZIP has nested directory structure (like spec-kit-v0.0.90/)
            # Only unwrap if it's a spec-kit/flowspec release directory, not agent directories like .claude/
            if (
                len(extracted_items) == 1
                and extracted_items[0].is_dir()
                and (
                    extracted_items[0].name.startswith("spec-kit-")
                    or extracted_items[0].name.startswith("flowspec-")
                )
            ):
                source_dir = extracted_items[0]
            else:
                source_dir = temp_path

            # Copy from source to project directory
            for item in source_dir.iterdir():
                dest_path = project_path / item.name
                if item.is_dir():
                    if dest_path.exists():
                        # Directory exists - always use recursive merge to avoid FileExistsError
                        # (dirs_exist_ok=True allows the destination directory to exist but will
                        #  still raise FileExistsError if files in the source already exist in
                        #  the destination)
                        for sub_item in item.rglob("*"):
                            if sub_item.is_file():
                                rel_path = sub_item.relative_to(item)
                                dest_file = dest_path / rel_path
                                dest_file.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(sub_item, dest_file)
                    else:
                        # Directory doesn't exist - safe to use copytree
                        shutil.copytree(item, dest_path, dirs_exist_ok=True)
                else:
                    # File overwrites (new file or existing file)
                    shutil.copy2(item, dest_path)


def download_and_extract_two_stage(
    project_path: Path,
    ai_assistants: str | list[str],
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    base_version: str = None,
    extension_version: str = None,
    branch: str = None,
) -> Path:
    """Two-stage download: base spec-kit + flowspec extension overlay.

    Supports single or multiple AI assistants. When multiple assistants are specified,
    their respective agent directories are all extracted to the project.

    When `branch` is specified, the flowspec extension is downloaded and built from
    that git branch instead of from releases. This is useful for testing branches
    before release. The base spec-kit still comes from releases.

    Returns project_path. Uses tracker if provided.
    """
    # Normalize to list for consistent handling
    if isinstance(ai_assistants, str):
        ai_assistants = [ai_assistants]

    # Validate that at least one AI assistant is specified
    if not ai_assistants:
        raise ValueError("At least one AI assistant must be specified")

    current_dir = Path.cwd()

    # Create project directory if needed (do this once, not per-agent)
    if not is_current_dir:
        project_path.mkdir(parents=True, exist_ok=True)

    # Process each AI assistant: download and extract both base and extension
    # NOTE: Each agent requires separate base + extension downloads because:
    # 1. Each agent has different file structures (.claude/, .github/, .gemini/, etc.)
    # 2. Base spec-kit provides agent-specific formatting (md vs toml vs json)
    # 3. The ZIPs are built per agent (they include agent-specific directories) and
    #    therefore cannot be blindly re-used between agents, even though they may
    #    also contain shared directories (e.g., .flowspec/) whose contents are meant
    #    to be merged safely across agents
    #
    # NOTE: If an error occurs during agent N (where N > 1), agents 1 through N-1
    # will remain installed. This is intentional - partial installations are still
    # usable, and rolling back would require complex state tracking.
    for agent in ai_assistants:
        # Initialize to None for exception handlers (may reference before assignment)
        base_zip = None
        ext_zip = None

        # Stage 1: Download base templates (flowspec is standalone, no separate base repo)
        step_name = f"fetch-base-{agent}" if len(ai_assistants) > 1 else "fetch-base"
        if tracker:
            tracker.start(
                step_name,
                f"downloading {agent} templates from {REPO_OWNER}/{REPO_NAME}",
            )

        try:
            base_zip, base_meta = download_template_from_github(
                agent,
                current_dir,
                script_type=script_type,
                verbose=verbose and tracker is None,
                show_progress=(tracker is None),
                client=client,
                debug=debug,
                github_token=github_token,
                repo_owner=REPO_OWNER,
                repo_name=REPO_NAME,
                version=base_version or REPO_DEFAULT_VERSION,
            )
            if tracker:
                tracker.complete(
                    step_name,
                    f"{agent} templates {base_meta['release']} ({base_meta['size']:,} bytes)",
                )
        except Exception as e:
            if tracker:
                tracker.error(step_name, str(e))
            # download_template_from_github already cleans up its zip on error
            raise

        # Stage 2: Download flowspec extension for this agent
        # When branch is specified, download and build from branch instead of release
        step_name = (
            f"fetch-extension-{agent}" if len(ai_assistants) > 1 else "fetch-extension"
        )
        if branch:
            if tracker:
                tracker.start(
                    step_name,
                    f"building {agent} extension from branch '{branch}'",
                )
            try:
                ext_zip, ext_meta = download_and_build_from_branch(
                    branch=branch,
                    ai_assistant=agent,
                    script_type=script_type,
                    download_dir=current_dir,
                    verbose=verbose and tracker is None,
                    client=client,
                    debug=debug,
                    github_token=github_token,
                    repo_owner=REPO_OWNER,
                    repo_name=REPO_NAME,
                )
                if tracker:
                    tracker.complete(
                        step_name,
                        f"{agent} extension from branch:{branch} ({ext_meta['size']:,} bytes)",
                    )
            except Exception as e:
                if tracker:
                    tracker.error(step_name, str(e))
                # Clean up base_zip since we won't reach extraction
                if base_zip and base_zip.exists():
                    base_zip.unlink()
                raise
        else:
            if tracker:
                tracker.start(
                    step_name,
                    f"downloading {agent} extension from {REPO_OWNER}/{REPO_NAME}",
                )

            try:
                ext_zip, ext_meta = download_template_from_github(
                    agent,
                    current_dir,
                    script_type=script_type,
                    verbose=verbose and tracker is None,
                    show_progress=(tracker is None),
                    client=client,
                    debug=debug,
                    github_token=github_token,
                    repo_owner=REPO_OWNER,
                    repo_name=REPO_NAME,
                    version=extension_version or REPO_DEFAULT_VERSION,
                )
                if tracker:
                    tracker.complete(
                        step_name,
                        f"{agent} extension {ext_meta['release']} ({ext_meta['size']:,} bytes)",
                    )
            except Exception as e:
                if tracker:
                    tracker.error(step_name, str(e))
                # download_template_from_github already cleans up its zip on error
                # But we need to clean up the base_zip since we won't reach extraction
                if base_zip and base_zip.exists():
                    base_zip.unlink()
                raise

        # Extract base for this agent
        step_name = (
            f"extract-base-{agent}" if len(ai_assistants) > 1 else "extract-base"
        )
        if tracker:
            tracker.start(step_name, f"extracting {agent} base")

        try:
            _extract_zip_to_project(base_zip, project_path)
            if tracker:
                tracker.complete(step_name, f"{agent} base extracted")
        except Exception as e:
            if tracker:
                tracker.error(step_name, str(e))
            # Clean up extension zip on base extraction failure (base_zip cleaned in finally)
            if ext_zip and ext_zip.exists():
                ext_zip.unlink()
            raise
        finally:
            # Always clean up base zip after extraction attempt
            if base_zip and base_zip.exists():
                base_zip.unlink()

        # CRITICAL: Wipe .github/agents/ COMPLETELY after base extraction
        # Base spec-kit has spec.*.agent.md files - we want NONE of them
        # Flowspec extension will write fresh flow.*.agent.md files
        github_agents_dir = project_path / ".github" / "agents"
        if github_agents_dir.exists():
            shutil.rmtree(github_agents_dir)

        # Extract extension for this agent (overlay on top of base)
        step_name = (
            f"extract-extension-{agent}"
            if len(ai_assistants) > 1
            else "extract-extension"
        )
        if tracker:
            tracker.start(step_name, f"extracting {agent} extension")

        try:
            _extract_zip_to_project(ext_zip, project_path)
            if tracker:
                tracker.complete(step_name, f"{agent} extension extracted")
        except Exception as e:
            if tracker:
                tracker.error(step_name, str(e))
            # ext_zip cleanup happens in finally block
            raise
        finally:
            # Always clean up extension zip after extraction attempt
            if ext_zip and ext_zip.exists():
                ext_zip.unlink()

    # Add merge completion message (only once at the end, not per-agent)
    if tracker:
        if len(ai_assistants) > 1:
            tracker.add("merge", f"Merge templates for {len(ai_assistants)} agents")
        else:
            tracker.add("merge", "Merge templates (extension overrides base)")
        tracker.complete("merge", "precedence rules applied")

    # Clean up legacy speckit.* files from base spec-kit that are now in spec/ directory
    # The flowspec extension uses spec/ subdirectory (e.g., .claude/commands/spec/specify.md)
    # but the base spec-kit may have flat speckit.* files (e.g., .claude/commands/speckit.specify.md)
    _cleanup_legacy_speckit_files(project_path, ai_assistants)

    return project_path


def download_and_extract_template(
    project_path: Path,
    ai_assistants: str | list[str],
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    repo_owner: str = None,
    repo_name: str = None,
    version: str = None,
) -> Path:
    """Download the latest release and extract it to create a new project.

    Supports single or multiple AI assistants. When multiple assistants are specified,
    their respective agent directories are all extracted to the project.

    Returns project_path. Uses tracker if provided (with keys: fetch, download, extract, cleanup)
    """
    # Normalize to list for consistent handling
    if isinstance(ai_assistants, str):
        ai_assistants = [ai_assistants]

    # Validate that at least one AI assistant is specified
    if not ai_assistants:
        raise ValueError("At least one AI assistant must be specified")

    # Use first agent for template download (templates contain all agent directories)
    primary_agent = ai_assistants[0]
    current_dir = Path.cwd()

    if tracker:
        tracker.start("fetch", "contacting GitHub API")
    try:
        zip_path, meta = download_template_from_github(
            primary_agent,  # Use primary agent for download
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            version=version,
        )
        if tracker:
            tracker.complete(
                "fetch", f"release {meta['release']} ({meta['size']:,} bytes)"
            )
            tracker.add("download", "Download template")
            tracker.complete("download", meta["filename"])
    except Exception as e:
        if tracker:
            tracker.error("fetch", str(e))
        else:
            if verbose:
                console.print(f"[red]Error downloading template:[/red] {e}")
        raise

    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete(
                            "extracted-summary", f"temp {len(extracted_items)} items"
                        )
                    elif verbose:
                        console.print(
                            f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]"
                        )

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(
                                "[cyan]Found nested directory structure[/cyan]"
                            )

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(
                                        f"[yellow]Merging directory:[/yellow] {item.name}"
                                    )
                                for sub_item in item.rglob("*"):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True
                                        )
                                        shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(
                                    f"[yellow]Overwriting file:[/yellow] {item.name}"
                                )
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(
                            "[cyan]Template files merged into current directory[/cyan]"
                        )
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete(
                        "extracted-summary", f"{len(extracted_items)} top-level items"
                    )
                elif verbose:
                    console.print(
                        f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]"
                    )
                    for item in extracted_items:
                        console.print(
                            f"  - {item.name} ({'dir' if item.is_dir() else 'file'})"
                        )

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(
                            "[cyan]Flattened nested directory structure[/cyan]"
                        )

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(
                        Panel(str(e), title="Extraction Error", border_style="red")
                    )

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def ensure_executable_scripts(
    project_path: Path, tracker: StepTracker | None = None
) -> None:
    """Ensure POSIX .sh scripts under .flowspec/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".flowspec" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat()
            mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400:
                new_mode |= 0o100
            if mode & 0o040:
                new_mode |= 0o010
            if mode & 0o004:
                new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (
            f", {len(failures)} failed" if failures else ""
        )
        tracker.add("chmod", "Set script permissions recursively")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(
                f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]"
            )
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")


@app.command()
def init(
    project_name: str = typer.Argument(
        None,
        help="Name for your new project directory (optional if using --here, or use '.' for current directory)",
    ),
    ai_assistant: str = typer.Option(
        None,
        "--ai",
        help="AI assistant(s) to use (comma-separated for multiple): claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, roo, or q. Example: --ai claude,copilot",
    ),
    script_type: str = typer.Option(
        None, "--script", help="Script type to use: sh or ps"
    ),
    ignore_agent_tools: bool = typer.Option(
        False,
        "--ignore-agent-tools",
        help="Skip checks for AI agent tools like Claude Code",
    ),
    no_git: bool = typer.Option(
        False, "--no-git", help="Skip git repository initialization"
    ),
    here: bool = typer.Option(
        False,
        "--here",
        help="Initialize project in the current directory instead of creating a new one",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force merge/overwrite when using --here (skip confirmation)",
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show verbose diagnostic output for network and extraction failures",
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GITHUB_FLOWSPEC environment variable)",
    ),
    base_version: str = typer.Option(
        None,
        "--base-version",
        help="Specific version of base spec-kit to use (default: latest)",
    ),
    extension_version: str = typer.Option(
        None,
        "--extension-version",
        help="Specific version of flowspec extension to use (default: latest)",
    ),
    branch: str = typer.Option(
        None,
        "--branch",
        "-b",
        help="Install flowspec templates from a git branch (for testing). Builds templates locally.",
    ),
    layered: bool = typer.Option(
        True,
        "--layered/--no-layered",
        help="Use two-stage layered download (base + extension). Default: True",
    ),
    backlog_version: str = typer.Option(
        None,
        "--backlog-version",
        help="Specific version of backlog-md to install (default: recommended from compatibility matrix)",
    ),
    # Per-transition validation mode flags
    validation_assess: str = typer.Option(
        "none",
        "--validation-assess",
        help="Validation mode for assess transition: none, keyword, or pull-request",
    ),
    validation_research: str = typer.Option(
        "none",
        "--validation-research",
        help="Validation mode for research transition: none, keyword, or pull-request",
    ),
    validation_specify: str = typer.Option(
        "none",
        "--validation-specify",
        help="Validation mode for specify transition: none, keyword, or pull-request",
    ),
    validation_plan: str = typer.Option(
        "none",
        "--validation-plan",
        help="Validation mode for plan transition: none, keyword, or pull-request",
    ),
    validation_implement: str = typer.Option(
        "none",
        "--validation-implement",
        help="Validation mode for implement transition: none, keyword, or pull-request",
    ),
    validation_validate: str = typer.Option(
        "none",
        "--validation-validate",
        help="Validation mode for validate transition: none, keyword, or pull-request",
    ),
    validation_operate: str = typer.Option(
        "none",
        "--validation-operate",
        help="Validation mode for operate transition: none, keyword, or pull-request",
    ),
    no_validation_prompts: bool = typer.Option(
        False,
        "--no-validation-prompts",
        help="Skip validation prompts and use NONE for all transitions",
    ),
    validation_mode: str = typer.Option(
        None,
        "--validation-mode",
        help="Set validation mode for ALL transitions: none, keyword, or pull-request. Per-transition flags override this.",
    ),
    light: bool = typer.Option(
        False,
        "--light",
        help="Use spec-light mode for medium-complexity features (~60% faster workflow)",
    ),
    constitution: str = typer.Option(
        None,
        "--constitution",
        help="Constitution tier: light (startup), medium (business), heavy (enterprise). Omit to be prompted.",
    ),
    no_hooks: bool = typer.Option(
        False,
        "--no-hooks",
        help="Initialize with all hooks disabled. Hooks can be enabled later in .flowspec/hooks/hooks.yaml",
    ),
    skip_claude_md: bool = typer.Option(
        False,
        "--skip-claude-md",
        help="Skip CLAUDE.md file generation",
    ),
    skip_skills: bool = typer.Option(
        False,
        "--skip-skills",
        help="Skip deployment of skills from templates/skills/ to .claude/skills/",
    ),
    check_mcp: bool = typer.Option(
        False,
        "--check-mcp",
        help="Check MCP server availability after initialization",
    ),
    check_mcp_recommended: bool = typer.Option(
        False,
        "--check-mcp-recommended",
        help="Also check recommended MCP servers (requires --check-mcp)",
    ),
    check_mcp_fail_on_missing: bool = typer.Option(
        False,
        "--check-mcp-fail-on-missing",
        help="Fail if required MCP servers are missing (requires --check-mcp)",
    ),
):
    """
    Initialize a new Specify project from the latest template.

    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Download the appropriate template from GitHub (two-stage: base + extension)
    4. Extract and merge templates to a new project directory or current directory
    5. Initialize a fresh git repository (if not --no-git and no existing repo)
    6. Optionally set up AI assistant commands

    Examples:
        flowspec init my-project
        flowspec init my-project --ai claude
        flowspec init my-project --ai claude,copilot  # Multiple agents
        flowspec init my-project --ai copilot --no-git
        flowspec init --ignore-agent-tools my-project
        flowspec init . --ai claude         # Initialize in current directory
        flowspec init . --ai claude,cursor-agent,copilot  # Multiple agents in current dir
        flowspec init .                     # Initialize in current directory (interactive AI selection)
        flowspec init --here --ai claude    # Alternative syntax for current directory
        flowspec init --here --ai codex
        flowspec init --here --ai codebuddy,claude
        flowspec init --here
        flowspec init --here --force  # Skip confirmation when current directory not empty
        flowspec init my-project --constitution medium  # Specific constitution tier
        flowspec init my-project --ai claude --constitution light  # Startup tier
        flowspec init my-project --ai claude --constitution heavy  # Enterprise tier
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print(
            "[red]Error:[/red] Cannot specify both project name and --here flag"
        )
        raise typer.Exit(1)

    if not here and not project_name:
        console.print(
            "[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag"
        )
        raise typer.Exit(1)

    # Branch mode requires layered download (two-stage: base + extension from branch)
    if branch and not layered:
        console.print(
            "[red]Error:[/red] --branch requires --layered mode (the default). "
            "Branch mode builds the extension from a git branch."
        )
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        # Check for source repository marker FIRST, before any other prompts
        marker_path = project_path / SOURCE_REPO_MARKER
        if marker_path.exists():
            error_panel = Panel(
                f"[yellow]This directory contains '{SOURCE_REPO_MARKER}'[/yellow]\n\n"
                "This indicates it is the flowspec source repository.\n"
                "Running 'flowspec init' here would overwrite source files.\n\n"
                "[cyan]If you want to use flowspec commands in this repo:[/cyan]\n"
                "  Run 'flowspec dev-setup' to set up for development.\n\n"
                "[cyan]If you want to test 'flowspec init' on a new project:[/cyan]\n"
                "  Create a new directory and run 'flowspec init' there instead.",
                title="[yellow]Source Repository Detected[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(
                f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)"
            )
            console.print(
                "[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]"
            )
            if force:
                console.print(
                    "[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]"
                )
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)

            # Check if this is an existing project without a constitution
            if is_existing_project(project_path) and not has_constitution(project_path):
                console.print()
                console.print(
                    "[yellow]⚠ No constitution found in existing project[/yellow]"
                )
                console.print()

                # Check if --constitution was provided or prompt user
                if not constitution:
                    # Interactive mode: prompt for tier
                    if sys.stdin.isatty():
                        tier_choices = list(CONSTITUTION_TIER_CHOICES.keys())

                        console.print(
                            "[cyan]Select a constitution tier for your project:[/cyan]"
                        )
                        for i, (tier, desc) in enumerate(
                            CONSTITUTION_TIER_CHOICES.items()
                        ):
                            console.print(f"  {i + 1}. [green]{tier}[/green] - {desc}")

                        # Simple input for tier selection
                        tier_input = typer.prompt(
                            "Enter tier number (1-3)", default="2"
                        )
                        try:
                            tier_idx = int(tier_input) - 1
                            if 0 <= tier_idx < len(tier_choices):
                                constitution = tier_choices[tier_idx]
                            else:
                                constitution = "medium"
                        except ValueError:
                            constitution = "medium"
                    else:
                        # Non-interactive: use default
                        console.print(
                            "[yellow]Non-interactive mode: using 'medium' constitution tier[/yellow]"
                        )
                        constitution = "medium"
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print(
                "[yellow]Git not found - will skip repository initialization[/yellow]"
            )

    # Parse and validate AI assistant selection(s)
    selected_agents = []
    if ai_assistant:
        # Parse comma-separated list
        selected_agents = parse_agent_list(ai_assistant)

        # Ensure at least one agent was provided
        if not selected_agents:
            console.print(
                "[red]Error:[/red] No AI assistants specified. Please provide at least one."
            )
            console.print(
                f"[cyan]Valid options:[/cyan] {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)

        # Validate all agents
        invalid_agents = [
            agent for agent in selected_agents if agent not in AGENT_CONFIG
        ]
        if invalid_agents:
            console.print(
                f"[red]Error:[/red] Invalid AI assistant(s): {', '.join(invalid_agents)}"
            )
            console.print(
                f"[cyan]Valid options:[/cyan] {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)
    else:
        # Interactive selection: use multi-select UI
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        console.print(
            "[cyan]Tip:[/cyan] You can select multiple AI assistants (use Space to toggle, Enter to confirm)"
        )
        console.print()
        selected_agents = select_multiple_with_checkboxes(
            ai_choices,
            "Choose your AI assistant(s):",
            default_keys=["copilot"],  # Default to copilot pre-selected
        )

        # Ensure at least one agent is selected
        if not selected_agents:
            console.print(
                "[yellow]No AI assistants selected. Please select at least one.[/yellow]"
            )
            raise typer.Exit(1)

    # Check tools for all selected agents that require CLI
    if not ignore_agent_tools:
        missing_tools = []
        for agent in selected_agents:
            agent_config = AGENT_CONFIG.get(agent)
            if agent_config and agent_config["requires_cli"]:
                if not check_tool(agent):
                    missing_tools.append((agent, agent_config))

        if missing_tools:
            # Display error panel for missing tools
            error_lines = []
            for agent, config in missing_tools:
                install_url = config["install_url"]
                error_lines.append(f"[cyan]{agent}[/cyan] ({config['name']})")
                error_lines.append(f"  Install from: [cyan]{install_url}[/cyan]")
                error_lines.append("")

            error_panel = Panel(
                "\n".join(error_lines)
                + "\nThese AI assistants require CLI tools to continue.\n\n"
                "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                title="[red]Missing Agent Tools[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(
                SCRIPT_TYPE_CHOICES,
                "Choose script type (or press Enter)",
                default_script,
            )
        else:
            selected_script = default_script

    # Handle constitution tier selection
    if constitution:
        if constitution not in CONSTITUTION_TIER_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid constitution tier '{constitution}'. "
                f"Choose from: {', '.join(CONSTITUTION_TIER_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_constitution = constitution
    else:
        default_constitution = "medium"
        if sys.stdin.isatty():
            selected_constitution = select_with_arrows(
                CONSTITUTION_TIER_CHOICES,
                "Choose constitution tier (or press Enter for medium)",
                default_constitution,
            )
        else:
            selected_constitution = default_constitution

    # Display selected agents
    agents_display = ", ".join(selected_agents)
    if len(selected_agents) == 1:
        console.print(f"[cyan]Selected AI assistant:[/cyan] {agents_display}")
    else:
        console.print(f"[cyan]Selected AI assistants:[/cyan] {agents_display}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")
    console.print(f"[cyan]Selected constitution tier:[/cyan] {selected_constitution}")

    tracker = StepTracker("Initialize Specify Project")

    sys._specify_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant(s)")
    tracker.complete("ai-select", f"{agents_display}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    tracker.add("constitution-select", "Select constitution tier")
    tracker.complete("constitution-select", selected_constitution)

    # Different tracking keys based on layered mode
    if layered:
        for key, label in [
            ("fetch-base", "Fetch base spec-kit"),
            ("fetch-extension", "Fetch flowspec extension"),
            ("extract-base", "Extract base template"),
            ("extract-extension", "Extract extension (overlay)"),
            ("merge", "Merge templates (extension overrides base)"),
            ("chmod", "Ensure scripts executable"),
            ("cleanup", "Cleanup"),
            ("git", "Initialize git repository"),
            ("hooks", "Scaffold hooks"),
            ("skills", "Deploy skills"),
            ("constitution", "Set up constitution"),
            ("final", "Finalize"),
        ]:
            tracker.add(key, label)
    else:
        for key, label in [
            ("fetch", "Fetch latest release"),
            ("download", "Download template"),
            ("extract", "Extract template"),
            ("zip-list", "Archive contents"),
            ("extracted-summary", "Extraction summary"),
            ("chmod", "Ensure scripts executable"),
            ("cleanup", "Cleanup"),
            ("git", "Initialize git repository"),
            ("hooks", "Scaffold hooks"),
            ("skills", "Deploy skills"),
            ("constitution", "Set up constitution"),
            ("final", "Finalize"),
        ]:
            tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None
    constitution_was_created = False

    with Live(
        tracker.render(), console=console, refresh_per_second=8, transient=True
    ) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            if layered:
                # Two-stage download: base + extension (supports multiple agents)
                download_and_extract_two_stage(
                    project_path,
                    selected_agents,  # Now a list
                    selected_script,
                    here,
                    verbose=False,
                    tracker=tracker,
                    client=local_client,
                    debug=debug,
                    github_token=github_token,
                    base_version=base_version,
                    extension_version=extension_version,
                    branch=branch,
                )
            else:
                # Single-stage download (legacy mode or base-only, supports multiple agents)
                download_and_extract_template(
                    project_path,
                    selected_agents,  # Now a list
                    selected_script,
                    here,
                    verbose=False,
                    tracker=tracker,
                    client=local_client,
                    debug=debug,
                    github_token=github_token,
                    repo_owner=REPO_OWNER,
                    repo_name=REPO_NAME,
                    version=extension_version,
                )

            ensure_executable_scripts(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            # Handle light mode setup
            if light:
                light_marker = project_path / ".flowspec-light-mode"
                light_marker.write_text(
                    "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n# See user-docs/guides/when-to-use-light-mode.md for details\n"
                )
                tracker.add("light-mode", "Light mode enabled")
                tracker.complete("light-mode", "marker created")

            # Scaffold hooks directory structure
            tracker.start("hooks")
            try:
                from .hooks.scaffold import scaffold_hooks

                created_files = scaffold_hooks(project_path, no_hooks=no_hooks)
                if created_files:
                    if no_hooks:
                        tracker.complete(
                            "hooks",
                            f"created {len(created_files)} hook files (all disabled via --no-hooks)",
                        )
                    else:
                        tracker.complete(
                            "hooks",
                            f"created {len(created_files)} hook files (3 enabled by default)",
                        )
                else:
                    tracker.complete("hooks", "hooks already configured")
            except Exception as hook_error:
                # Non-fatal error - continue with project initialization
                tracker.error("hooks", f"scaffolding failed: {hook_error}")

            # Deploy skills from templates/skills/ to .claude/skills/
            tracker.start("skills")
            try:
                from .skills import deploy_skills

                deployed_skills = deploy_skills(
                    project_path, force=force, skip_skills=skip_skills
                )
                if skip_skills:
                    tracker.skip("skills", "--skip-skills flag")
                elif deployed_skills:
                    tracker.complete(
                        "skills",
                        f"deployed {len(deployed_skills)} skills to .claude/skills/",
                    )
                else:
                    tracker.complete("skills", "no new skills deployed")
            except PermissionError as skills_error:
                # Non-fatal error - continue with project initialization
                tracker.error(
                    "skills",
                    f"deployment failed due to permission error: {skills_error}",
                )
            except OSError as skills_error:
                # Non-fatal error - continue with project initialization
                tracker.error(
                    "skills",
                    f"deployment failed due to OS error: {skills_error}",
                )
            except Exception as skills_error:
                # Non-fatal error - continue with project initialization
                tracker.error(
                    "skills",
                    f"deployment failed ({type(skills_error).__name__}): {skills_error}",
                )

            # Install VS Code Copilot agents from embedded templates
            tracker.add("copilot-agents", "Install VS Code Copilot agents")
            tracker.start("copilot-agents")
            try:
                # Destination: .github/agents/ in the target project
                agents_dest_dir = project_path / ".github" / "agents"
                agents_dest_dir.mkdir(parents=True, exist_ok=True)

                # Write agent files from embedded templates
                for filename, content in COPILOT_AGENT_TEMPLATES.items():
                    dest_file = agents_dest_dir / filename
                    dest_file.write_text(content)

                tracker.complete(
                    "copilot-agents",
                    f"installed {len(COPILOT_AGENT_TEMPLATES)} agents in .github/agents/",
                )
            except PermissionError as agents_error:
                tracker.error(
                    "copilot-agents",
                    f"installation failed due to permission error: {agents_error}",
                )
            except Exception as agents_error:
                tracker.error(
                    "copilot-agents",
                    f"installation failed ({type(agents_error).__name__}): {agents_error}",
                )

            # Set up constitution template
            tracker.start("constitution")
            try:
                # Get constitution template from embedded templates
                if selected_constitution in CONSTITUTION_TEMPLATES:
                    memory_dir = project_path / "memory"
                    constitution_dest = memory_dir / "constitution.md"
                    memory_dir.mkdir(parents=True, exist_ok=True)

                    # Detect project metadata for placeholder replacement
                    metadata = detect_project_metadata(
                        project_path, project_name_override=project_name
                    )

                    # Replace placeholders in template
                    template_content = CONSTITUTION_TEMPLATES[selected_constitution]
                    processed_content = replace_placeholders(template_content, metadata)

                    constitution_dest.write_text(processed_content)
                    constitution_was_created = True
                    tracker.complete(
                        "constitution",
                        f"{selected_constitution} tier → memory/constitution.md",
                    )
                else:
                    tracker.error(
                        "constitution",
                        f"unknown tier: {selected_constitution}",
                    )
            except Exception as const_error:
                tracker.error("constitution", f"setup failed: {const_error}")

            # Write repository facts to memory bank
            tracker.start("repo-facts")
            try:
                write_repo_facts(project_path)
                tracker.complete("repo-facts", "memory/repo-facts.md created")
            except Exception as facts_error:
                tracker.error("repo-facts", f"generation failed: {facts_error}")

            # Generate CLAUDE.md file
            if not skip_claude_md:
                tracker.start("claude-md")
                try:
                    # Use project_path.name to get just the directory name
                    generate_claude_md(project_path, project_path.name)
                    tracker.complete("claude-md", "CLAUDE.md created")
                except Exception as claude_error:
                    tracker.error("claude-md", f"generation failed: {claude_error}")
            else:
                tracker.add("claude-md", "Generate CLAUDE.md")
                tracker.skip("claude-md", "--skip-claude-md flag")

            # Generate .mcp.json file
            tracker.add("mcp-json", "Generate .mcp.json")
            tracker.start("mcp-json")
            try:
                # generate_mcp_json returns False when .mcp.json already exists
                if generate_mcp_json(project_path):
                    tracker.complete("mcp-json", ".mcp.json created")
                else:
                    tracker.skip("mcp-json", ".mcp.json already exists")
            except Exception as mcp_error:
                tracker.error(
                    "mcp-json",
                    f"MCP JSON generation failed ({type(mcp_error).__name__}): {mcp_error}",
                )

            # Generate .vscode/extensions.json
            tracker.add("vscode-ext", "Generate VSCode extensions")
            tracker.start("vscode-ext")
            try:
                # generate_vscode_extensions returns True if created, False if updated
                if generate_vscode_extensions(project_path):
                    tracker.complete("vscode-ext", ".vscode/extensions.json created")
                else:
                    tracker.complete("vscode-ext", ".vscode/extensions.json updated")
            except Exception as ext_error:
                tracker.error(
                    "vscode-ext",
                    f"VSCode extensions generation failed ({type(ext_error).__name__}): {ext_error}",
                )

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(
                Panel(
                    f"Initialization failed: {e}", title="Failure", border_style="red"
                )
            )
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [
                    f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]"
                    for k, v in _env_pairs
                ]
                console.print(
                    Panel(
                        "\n".join(env_lines),
                        title="Debug Environment",
                        border_style="magenta",
                    )
                )
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")

    # Show constitution customization message if we created a constitution for an existing project
    if here and constitution_was_created and is_existing_project(project_path):
        console.print()
        constitution_panel = Panel(
            "Constitution template created at [cyan]memory/constitution.md[/cyan]\n\n"
            "[yellow]Next step:[/yellow] Customize it for your repository using:\n"
            "[green]/flow:init[/green]\n\n"
            "This will tailor the constitution to your project's specific needs.",
            title="[green]Constitution Created[/green]",
            border_style="green",
            padding=(1, 2),
        )
        console.print(constitution_panel)

    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f'[cyan]git commit -m "Initial commit"[/cyan]',
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(git_error_panel)

    # Agent folder security notice (for all selected agents)
    agent_folders = []
    for agent in selected_agents:
        agent_config = AGENT_CONFIG.get(agent)
        if agent_config:
            agent_folders.append(agent_config["folder"])

    if agent_folders:
        if len(agent_folders) == 1:
            folders_text = f"[cyan]{agent_folders[0]}[/cyan]"
        else:
            folders_text = ", ".join(
                [f"[cyan]{folder}[/cyan]" for folder in agent_folders]
            )

        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in their agent folders within your project.\n"
            f"Consider adding {folders_text} (or parts of them) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(security_notice)

    # Check for backlog-md and offer to install if missing
    current_backlog_version = check_backlog_installed_version()
    if not current_backlog_version and not no_validation_prompts and sys.stdin.isatty():
        console.print()
        install_backlog = typer.confirm(
            "backlog-md is not installed. Would you like to install it for task management?",
            default=True,
        )
        if install_backlog:
            target_version = backlog_version or get_backlog_validated_version()
            if target_version:
                pkg_manager = detect_package_manager()
                if pkg_manager:
                    console.print(
                        f"\n[cyan]Installing backlog-md@{target_version}...[/cyan]"
                    )
                    try:
                        if pkg_manager == "pnpm":
                            cmd = ["pnpm", "add", "-g", f"backlog.md@{target_version}"]
                        else:
                            cmd = [
                                "npm",
                                "install",
                                "-g",
                                f"backlog.md@{target_version}",
                            ]

                        subprocess.run(cmd, check=True, capture_output=True, text=True)

                        installed_version = check_backlog_installed_version()
                        if installed_version:
                            console.print(
                                f"[green]backlog-md {installed_version} installed successfully![/green]"
                            )
                        else:
                            console.print(
                                "[yellow]Installation completed but verification failed[/yellow]"
                            )
                    except subprocess.CalledProcessError as e:
                        console.print(
                            f"[yellow]Installation failed:[/yellow] {e.stderr}"
                        )
                        console.print(
                            "[dim]You can install it manually later: flowspec backlog install[/dim]"
                        )
                else:
                    console.print(
                        "[yellow]No Node.js package manager found (pnpm or npm required)[/yellow]"
                    )
                    console.print(
                        "[dim]Install backlog-md manually: flowspec backlog install[/dim]"
                    )
            else:
                console.print(
                    "[yellow]Could not determine backlog-md version to install[/yellow]"
                )
                console.print(
                    "[dim]You can install it manually later: flowspec backlog install[/dim]"
                )
        else:
            console.print(
                "[dim]You can install backlog-md later with: flowspec backlog install[/dim]"
            )
    elif backlog_version:
        # User specified a version but backlog is already installed
        console.print()
        console.print(
            f"[yellow]backlog-md is already installed (version {current_backlog_version})[/yellow]"
        )
        console.print(
            f"[dim]To change version: flowspec backlog upgrade --version {backlog_version}[/dim]"
        )

    # Check for beads and offer to install if missing
    current_beads_version = check_beads_installed_version()
    if not current_beads_version and not no_validation_prompts and sys.stdin.isatty():
        console.print()
        install_beads = typer.confirm(
            "beads is not installed. Would you like to install it for issue tracking?",
            default=True,
        )
        if install_beads:
            pkg_manager = detect_package_manager()
            if pkg_manager:
                console.print("\n[cyan]Installing @beads/bd...[/cyan]")
                try:
                    if pkg_manager == "pnpm":
                        cmd = ["pnpm", "add", "-g", "@beads/bd"]
                    else:
                        cmd = ["npm", "install", "-g", "@beads/bd"]

                    subprocess.run(cmd, check=True, capture_output=True, text=True)

                    installed_version = check_beads_installed_version()
                    if installed_version:
                        console.print(
                            f"[green]beads {installed_version} installed successfully![/green]"
                        )
                    else:
                        console.print(
                            "[yellow]Installation completed but verification failed[/yellow]"
                        )
                except subprocess.CalledProcessError as e:
                    console.print(f"[yellow]Installation failed:[/yellow] {e.stderr}")
                    console.print(
                        "[dim]You can install it manually: npm install -g @beads/bd[/dim]"
                    )
            else:
                console.print(
                    "[yellow]No Node.js package manager found (pnpm or npm required)[/yellow]"
                )
                console.print(
                    "[dim]Install beads manually: npm install -g @beads/bd[/dim]"
                )
        else:
            console.print(
                "[dim]You can install beads later: npm install -g @beads/bd[/dim]"
            )

    # Generate workflow configuration file with per-transition validation modes
    # Priority order:
    # 1. --no-validation-prompts: all NONE, no prompts
    # 2. Per-transition flags (--validation-assess, etc.): explicit overrides
    # 3. --validation-mode: batch mode for all transitions
    # 4. Interactive prompts: if TTY and no explicit configuration

    transition_names = [
        "assess",
        "research",
        "specify",
        "plan",
        "implement",
        "validate",
        "operate",
    ]
    per_transition_flags = {
        "assess": validation_assess,
        "research": validation_research,
        "specify": validation_specify,
        "plan": validation_plan,
        "implement": validation_implement,
        "validate": validation_validate,
        "operate": validation_operate,
    }

    if no_validation_prompts:
        # Highest priority: --no-validation-prompts means all NONE
        transition_modes: dict[str, str] = {}
    elif validation_mode is not None:
        # Batch mode: set all transitions to the specified mode
        # But per-transition flags can still override
        valid_batch_modes = {"none", "keyword", "pull-request"}
        if validation_mode.lower() not in valid_batch_modes:
            console.print(
                f"[red]Error:[/red] Invalid --validation-mode '{validation_mode}'. "
                f"Must be one of: {', '.join(valid_batch_modes)}"
            )
            raise typer.Exit(1)

        # Start with batch mode for all transitions
        transition_modes = {name: validation_mode.lower() for name in transition_names}

        # Per-transition flags override batch mode
        for name, flag_value in per_transition_flags.items():
            if flag_value.lower() != "none":  # Only override if explicitly set
                transition_modes[name] = flag_value
    else:
        # Check if any per-transition flag was explicitly set (non-default)
        any_explicit = any(v.lower() != "none" for v in per_transition_flags.values())

        if any_explicit:
            # Use per-transition flags as specified
            transition_modes = per_transition_flags.copy()
        elif sys.stdin.isatty() and sys.stdout.isatty():
            # Interactive mode: prompt user for each transition
            transition_modes = prompt_validation_modes()
        else:
            # Non-interactive with no explicit flags: use defaults (all NONE)
            transition_modes = {}

    generate_flowspec_workflow_yml(project_path, transition_modes)
    console.print()
    console.print("[green]Generated flowspec_workflow.yml[/green]")

    # Write version tracking file
    write_version_tracking_file(project_path, is_upgrade=False)
    console.print("[green]Created version tracking file[/green]")

    # Display validation summary
    display_validation_summary(transition_modes)

    steps_lines = []
    if not here:
        steps_lines.append(
            f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]"
        )
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if "codex" in selected_agents:
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"

        steps_lines.append(
            f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]"
        )
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append(
        "   2.1 [cyan]/flow:init[/] - Establish project principles (constitution)"
    )
    steps_lines.append("   2.2 [cyan]/flow:specify[/] - Create baseline specification")
    steps_lines.append("   2.3 [cyan]/flow:plan[/] - Create implementation plan")
    steps_lines.append("   2.4 [cyan]/flow:implement[/] - Execute implementation")
    steps_lines.append("   2.5 [cyan]/flow:validate[/] - QA and security review")

    steps_panel = Panel(
        "\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1, 2)
    )
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands [bright_black](improve quality & confidence)[/bright_black]",
        "",
        "○ [cyan]/flow:assess[/] - Evaluate complexity and recommend workflow mode",
        "○ [cyan]/flow:research[/] - Research and business validation (after specify)",
        "○ [cyan]/flow:submit-n-watch-pr[/] - Submit PR and watch CI/reviews",
    ]
    enhancements_panel = Panel(
        "\n".join(enhancement_lines),
        title="Additional Commands",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(enhancements_panel)

    # MCP server health check if requested
    if check_mcp:
        all_available, status = check_mcp_servers(
            project_path,
            check_recommended=check_mcp_recommended,
            console=console,
        )
        if not all_available and check_mcp_fail_on_missing:
            console.print(
                "\n[red]Error: Required MCP servers are missing. "
                "Install them or remove --check-mcp-fail-on-missing flag.[/red]"
            )
            raise typer.Exit(1)


@app.command(name="upgrade-repo")
def upgrade_repo(
    base_version: str = typer.Option(
        None,
        "--base-version",
        help="Specific version of base spec-kit to upgrade to (default: latest)",
    ),
    extension_version: str = typer.Option(
        None,
        "--extension-version",
        help="Specific version of flowspec extension to upgrade to (default: latest)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be upgraded without making changes"
    ),
    templates_only: bool = typer.Option(
        False, "--templates-only", help="Only update templates, skip other files"
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output"),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GITHUB_FLOWSPEC environment variable)",
    ),
    branch: str = typer.Option(
        None,
        "--branch",
        "-b",
        help="Upgrade templates from a git branch (for testing). Builds templates locally.",
    ),
    recommended_servers: bool = typer.Option(
        False,
        "--recommended-servers",
        help="Include recommended MCP servers (playwright-test, trivy, semgrep) in .mcp.json",
    ),
    check_mcp: bool = typer.Option(
        False,
        "--check-mcp",
        help="Check MCP server availability after upgrade",
    ),
    check_mcp_recommended: bool = typer.Option(
        False,
        "--check-mcp-recommended",
        help="Also check recommended MCP servers (requires --check-mcp)",
    ),
    check_mcp_fail_on_missing: bool = typer.Option(
        False,
        "--check-mcp-fail-on-missing",
        help="Fail if required MCP servers are missing (requires --check-mcp)",
    ),
):
    """
    Upgrade repository templates to latest spec-kit and flowspec versions.

    This upgrades the templates and configuration files in your current project directory.
    It does NOT upgrade the globally installed CLI tools (use 'flowspec upgrade-tools' for that).

    This command will:
    1. Detect the AI assistant type from the project
    2. Download latest base spec-kit templates
    3. Download latest flowspec extension (or from branch if --branch specified)
    4. Merge with precedence (extension overrides base)
    5. Apply updates to current project
    6. Update .mcp.json with required MCP servers

    Examples:
        flowspec upgrade-repo                               # Upgrade repo to latest templates
        flowspec upgrade-repo --dry-run                     # Preview changes
        flowspec upgrade-repo --base-version 0.0.20         # Pin base to specific version
        flowspec upgrade-repo --extension-version 0.0.21    # Pin extension to specific version
        flowspec upgrade-repo --templates-only              # Only update template files
        flowspec upgrade-repo --branch fix3                 # Upgrade from git branch
        flowspec upgrade-repo --recommended-servers         # Include additional MCP servers

    See also:
        flowspec upgrade-tools    # Upgrade globally installed CLI tools
    """
    show_banner()

    project_path = Path.cwd()

    # Check for source repository marker to prevent clobbering flowspec source
    marker_path = project_path / SOURCE_REPO_MARKER
    if marker_path.exists():
        error_panel = Panel(
            f"[yellow]This directory contains '{SOURCE_REPO_MARKER}'[/yellow]\n\n"
            "This indicates it is the flowspec source repository.\n"
            "Running 'flowspec upgrade-repo' here would overwrite source files.\n\n"
            "[cyan]To update flowspec itself:[/cyan]\n"
            "  Use git pull or standard development workflow.\n\n"
            "[cyan]To test 'flowspec upgrade-repo' on a project:[/cyan]\n"
            "  Navigate to a project initialized with 'flowspec init'.",
            title="[yellow]Source Repository Detected[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(error_panel)
        raise typer.Exit(1)

    # Detect AI assistant from existing project
    ai_assistant = None
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_folder = project_path / agent_config["folder"]
        if agent_folder.exists():
            ai_assistant = agent_key
            break

    if not ai_assistant:
        console.print(
            "[red]Error:[/red] Could not detect AI assistant type in current directory"
        )
        console.print(
            "[yellow]Tip:[/yellow] Make sure you're in a Specify project directory"
        )
        raise typer.Exit(1)

    # Detect script type (look for .sh or .ps1 scripts)
    script_type = "sh"  # default
    specify_scripts = project_path / ".flowspec" / "scripts"
    if specify_scripts.exists():
        if list(specify_scripts.glob("**/*.ps1")):
            script_type = "ps"

    console.print("[cyan]Detected configuration:[/cyan]")
    console.print(f"  AI Assistant: [green]{ai_assistant}[/green]")
    console.print(f"  Script Type:  [green]{script_type}[/green]")
    console.print()

    # Check for missing constitution in existing project
    if is_existing_project(project_path) and not has_constitution(project_path):
        console.print()
        console.print("[yellow]⚠ No constitution found in this project[/yellow]")

        if sys.stdin.isatty():
            # Interactive mode: offer to add constitution
            add_constitution = typer.confirm(
                "Would you like to add a constitution now?", default=True
            )

            if add_constitution:
                tier_choices = list(CONSTITUTION_TIER_CHOICES.keys())

                console.print("[cyan]Select a constitution tier:[/cyan]")
                for i, (tier, desc) in enumerate(CONSTITUTION_TIER_CHOICES.items()):
                    console.print(f"  {i + 1}. [green]{tier}[/green] - {desc}")

                tier_input = typer.prompt("Enter tier number (1-3)", default="2")
                try:
                    tier_idx = int(tier_input) - 1
                    if 0 <= tier_idx < len(tier_choices):
                        selected_tier = tier_choices[tier_idx]
                    else:
                        selected_tier = "medium"
                except ValueError:
                    selected_tier = "medium"

                # Create constitution
                memory_dir = project_path / "memory"
                memory_dir.mkdir(parents=True, exist_ok=True)
                constitution_path = memory_dir / "constitution.md"

                template = CONSTITUTION_TEMPLATES.get(
                    selected_tier, CONSTITUTION_TEMPLATES["medium"]
                )

                # Detect project metadata and replace placeholders
                metadata = detect_project_metadata(
                    project_path, project_name_override=project_path.name
                )
                processed_content = replace_placeholders(template, metadata)

                constitution_path.write_text(processed_content)

                console.print()
                constitution_panel = Panel(
                    "Constitution template created at [cyan]memory/constitution.md[/cyan]\n\n"
                    "[yellow]Next step:[/yellow] Customize it for your repository using:\n"
                    "[green]/flow:init[/green]\n\n"
                    "This will tailor the constitution to your project's specific needs.",
                    title="[green]Constitution Created[/green]",
                    border_style="green",
                    padding=(1, 2),
                )
                console.print(constitution_panel)
                console.print()
        else:
            console.print(
                "[yellow]Run 'flowspec init --here' in interactive mode to add a constitution[/yellow]"
            )
        console.print()

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    tracker = StepTracker("Upgrade Specify Project")

    tracker.add("detect", "Detect project configuration")
    tracker.complete("detect", f"{ai_assistant}, {script_type}")
    tracker.add("fetch-base", "Fetch base spec-kit")
    tracker.add("fetch-extension", "Fetch flowspec extension")
    tracker.add("backup", "Backup current templates")
    tracker.add("apply", "Apply updates")
    tracker.add("skills", "Sync skills")
    tracker.add("workflow", "Migrate workflow config")
    tracker.add("mcp", "Update MCP configuration")
    tracker.add("cleanup", "Remove deprecated files")
    tracker.add("final", "Finalize")

    if dry_run:
        # In dry run, just fetch and report what would change
        console.print(tracker.render())
        console.print(
            "\n[green]Dry run completed. Use without --dry-run to apply changes.[/green]"
        )
        return

    with Live(
        tracker.render(), console=console, refresh_per_second=8, transient=True
    ) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            # Create backup of existing templates with timestamp
            tracker.start("backup")
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_dir = project_path / f".flowspec-backup-{timestamp}"
            backup_dir.mkdir(parents=True)

            # Backup key directories (including deprecated ones for recovery)
            for dir_name in [
                ".flowspec",
                ".claude",
                ".github",
                "templates",
                ".specify",
            ]:
                src = project_path / dir_name
                if src.exists():
                    shutil.copytree(src, backup_dir / dir_name, dirs_exist_ok=True)

            # Backup workflow config file
            workflow_file = project_path / "flowspec_workflow.yml"
            if workflow_file.exists():
                shutil.copy2(workflow_file, backup_dir / "flowspec_workflow.yml")

            tracker.complete("backup", f"saved to {backup_dir.name}")

            # Apply two-stage upgrade
            tracker.start("apply")
            download_and_extract_two_stage(
                project_path,
                ai_assistant,
                script_type,
                is_current_dir=True,  # Upgrade in place
                verbose=False,
                tracker=tracker,
                client=local_client,
                debug=debug,
                github_token=github_token,
                base_version=base_version,
                extension_version=extension_version,
                branch=branch,
            )

            tracker.complete("apply", "templates updated")

            # Sync skills and report changes
            tracker.start("skills")
            from .skills import compare_skills_after_extraction

            skills_result = compare_skills_after_extraction(project_path, backup_dir)
            if skills_result.has_changes:
                skills_summary = skills_result.summary()
                tracker.complete("skills", skills_summary)
            else:
                tracker.complete("skills", "no changes")

            # Migrate workflow configuration to v2.0
            tracker.start("workflow")
            from .workflow import migrate_workflow_config

            workflow_result = migrate_workflow_config(
                project_path, backup_dir=backup_dir
            )
            if workflow_result.migrated:
                workflow_summary = workflow_result.summary()
                tracker.complete("workflow", workflow_summary)
            elif workflow_result.errors:
                tracker.complete("workflow", f"error: {workflow_result.errors[0]}")
            else:
                tracker.complete("workflow", workflow_result.summary())

            # Update MCP configuration with required servers
            tracker.start("mcp")
            mcp_modified, mcp_changes = update_mcp_json(
                project_path, include_recommended=recommended_servers
            )
            if mcp_modified:
                added_servers = ", ".join(mcp_changes["added"])
                tracker.complete("mcp", f"added: {added_servers}")
            else:
                tracker.complete("mcp", "already up to date")

            # Remove deprecated files and directories
            tracker.start("cleanup")
            from .deprecated import cleanup_deprecated_files

            cleanup_result = cleanup_deprecated_files(
                project_path, backup_dir=backup_dir
            )
            if cleanup_result.has_changes:
                cleanup_summary = cleanup_result.summary()
                tracker.complete("cleanup", cleanup_summary)
            elif cleanup_result.errors:
                tracker.complete("cleanup", f"error: {cleanup_result.errors[0]}")
            else:
                tracker.complete("cleanup", "no deprecated items")

            tracker.complete("final", "upgrade complete")

        except Exception as e:
            tracker.error("final", str(e))
            console.print(f"\n[red]Upgrade failed:[/red] {e}")
            console.print(f"[yellow]Backup available at:[/yellow] {backup_dir}")
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Upgrade completed successfully![/bold green]")
    console.print(f"[dim]Backup of previous templates: {backup_dir}[/dim]")

    # Update version tracking file
    write_version_tracking_file(project_path, is_upgrade=True)

    # Check and offer to sync backlog-md version
    current_backlog_version = check_backlog_installed_version()
    recommended_version = get_backlog_validated_version()

    if current_backlog_version and recommended_version:
        if current_backlog_version != recommended_version:
            console.print()
            console.print(
                f"[yellow]backlog-md version mismatch:[/yellow] "
                f"current={current_backlog_version}, recommended={recommended_version}"
            )
            sync_backlog = typer.confirm(
                "Would you like to sync backlog-md to the recommended version?",
                default=True,
            )
            if sync_backlog:
                pkg_manager = detect_package_manager()
                if pkg_manager:
                    console.print(
                        f"\n[cyan]Syncing backlog-md to {recommended_version}...[/cyan]"
                    )
                    try:
                        if pkg_manager == "pnpm":
                            cmd = [
                                "pnpm",
                                "add",
                                "-g",
                                f"backlog.md@{recommended_version}",
                            ]
                        else:
                            cmd = [
                                "npm",
                                "install",
                                "-g",
                                f"backlog.md@{recommended_version}",
                            ]

                        subprocess.run(cmd, check=True, capture_output=True, text=True)

                        new_version = check_backlog_installed_version()
                        if new_version == recommended_version:
                            console.print(
                                f"[green]backlog-md synced to {new_version}![/green]"
                            )
                        else:
                            console.print(
                                "[yellow]Sync completed but verification failed[/yellow]"
                            )
                    except subprocess.CalledProcessError as e:
                        console.print(f"[yellow]Sync failed:[/yellow] {e.stderr}")
                        console.print(
                            "[dim]You can sync manually: flowspec backlog upgrade[/dim]"
                        )
                else:
                    console.print("[yellow]No Node.js package manager found[/yellow]")
                    console.print(
                        "[dim]You can sync manually: flowspec backlog upgrade[/dim]"
                    )
            else:
                console.print(
                    "[dim]You can sync backlog-md later with: flowspec backlog upgrade[/dim]"
                )
    elif not current_backlog_version and recommended_version:
        console.print()
        console.print("[yellow]backlog-md is not installed[/yellow]")
        console.print("[dim]Install with: flowspec backlog install[/dim]")

    console.print()
    console.print("[cyan]Next steps:[/cyan]")
    console.print("  1. Review changes with: [cyan]git diff[/cyan]")
    console.print("  2. Test your project to ensure everything works")
    console.print(
        f"  3. If needed, restore from backup: [cyan]cp -r {backup_dir}/* .[/cyan]"
    )

    # MCP server health check if requested
    if check_mcp:
        all_available, status = check_mcp_servers(
            project_path,
            check_recommended=check_mcp_recommended,
            console=console,
        )
        if not all_available and check_mcp_fail_on_missing:
            console.print(
                "\n[red]Error: Required MCP servers are missing. "
                "Install them or remove --check-mcp-fail-on-missing flag.[/red]"
            )
            raise typer.Exit(1)


# Valid component names for upgrade-tools
UPGRADE_TOOLS_COMPONENTS = ["flowspec", "backlog", "beads"]


def _get_installed_flowspec_version() -> Optional[str]:
    """Get the actual installed flowspec version by running the binary.

    This queries the installed binary rather than using the in-memory __version__,
    which is necessary after upgrades since the Python process still has the old value.

    Returns:
        Version string (e.g., "0.2.317") or None if not installed/error
    """
    import re

    # Regex for semantic version: digits, at least one dot, more digits
    version_pattern = re.compile(r"^\d+(\.\d+)+$")

    try:
        result = subprocess.run(
            ["specify", "version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Parse "flowspec X.Y.Z" from output
            for line in result.stdout.strip().split("\n"):
                if "flowspec" in line.lower():
                    # Extract version number matching semver pattern
                    parts = line.split()
                    for part in parts:
                        if version_pattern.match(part):
                            return part
    except FileNotFoundError:
        # 'specify' CLI not in PATH - expected when not installed via uv tool
        pass
    return None


def _detect_duplicate_flowspec_installations() -> list[tuple[str, str]]:
    """Detect multiple flowspec installations that could cause version conflicts.

    Checks for flowspec in:
    - uv tools (respects UV_TOOL_BIN_DIR, defaults to ~/.local/bin)
    - pip/pyenv installations (resolves shims to actual paths)
    - Other PATH locations

    Returns:
        List of (path, source) tuples for each installation found.
        Example: [("/Users/x/.local/bin/flowspec", "uv"), ("/Users/x/.pyenv/.../flowspec", "pip/pyenv")]
    """
    installations: list[tuple[str, str]] = []
    seen_paths: set[str] = set()

    # Check uv tools locations - respect UV_TOOL_BIN_DIR if set
    uv_tool_bin_dir = os.environ.get("UV_TOOL_BIN_DIR")
    uv_candidates: list[Path] = []

    if uv_tool_bin_dir:
        uv_candidates.append(Path(uv_tool_bin_dir) / "flowspec")

    # Also check the default uv tools location
    uv_candidates.append(Path.home() / ".local" / "bin" / "flowspec")

    for candidate in uv_candidates:
        if candidate.exists():
            try:
                resolved_candidate = candidate.resolve()
            except OSError:
                # Path resolution can fail if the target was removed, is a broken symlink,
                # or is inaccessible due to permissions; fall back to the raw candidate.
                resolved_candidate = candidate
            candidate_str = str(resolved_candidate)
            if candidate_str not in seen_paths:
                seen_paths.add(candidate_str)
                installations.append((candidate_str, "uv"))

    # Check if pyenv has flowspec - resolve shim to actual path
    try:
        result = subprocess.run(
            ["pyenv", "which", "flowspec"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            pyenv_path_raw = result.stdout.strip()
            # Normalize and resolve the path to match PATH-based resolution
            pyenv_path_obj = Path(pyenv_path_raw)
            if pyenv_path_obj.exists():
                try:
                    pyenv_path = str(pyenv_path_obj.resolve())
                except OSError:
                    # Path resolution can fail if target was removed or is inaccessible
                    pyenv_path = pyenv_path_raw
            else:
                # If the path no longer exists, fall back to the raw path
                pyenv_path = pyenv_path_raw
            if pyenv_path not in seen_paths:
                seen_paths.add(pyenv_path)
                installations.append((pyenv_path, "pip/pyenv"))
    except FileNotFoundError:
        # pyenv not installed - this is normal on many systems
        pass

    # Check PATH using cross-platform shutil.which()
    which_path = shutil.which("flowspec")
    if which_path:
        # Resolve symlinks and normalize path
        path_obj = Path(which_path)
        if path_obj.exists():
            try:
                resolved_path = str(path_obj.resolve())
            except OSError:
                # Path resolution can fail if the target was removed, is a broken symlink,
                # or is inaccessible due to permissions; fall back to the raw PATH entry.
                resolved_path = which_path
        else:
            # If the path no longer exists, fall back to the raw PATH entry.
            resolved_path = which_path

        # If this is a pyenv shim, try to resolve to actual path
        if ".pyenv/shims" in which_path or ".pyenv\\shims" in which_path:
            # Already handled by pyenv which above, skip to avoid duplicates
            pass
        elif resolved_path not in seen_paths:
            seen_paths.add(resolved_path)
            installations.append((resolved_path, "PATH"))

    return installations


def _warn_duplicate_installations() -> bool:
    """Check for and warn about duplicate flowspec installations.

    Returns:
        True if duplicates were found and warning was shown.
    """
    installations = _detect_duplicate_flowspec_installations()

    if len(installations) <= 1:
        return False

    console.print(
        "[yellow]⚠ Warning: Multiple flowspec installations detected![/yellow]\n"
    )

    for path, source in installations:
        console.print(f"  • {path} [dim]({source})[/dim]")

    console.print()
    console.print(
        "[dim]This can cause version conflicts. The first one in PATH takes precedence.[/dim]"
    )
    console.print(
        "[dim]To fix: remove the unwanted installation based on the paths above.[/dim]\n"
    )

    return True


def _upgrade_flowspec(
    dry_run: bool = False,
    target_version: str | None = None,
    branch: str | None = None,
) -> tuple[bool, str]:
    """Upgrade flowspec (flowspec-cli) via uv tool.

    Args:
        dry_run: If True, only show what would be done
        target_version: Specific version to install (e.g., "0.2.325"). If None, uses latest.
        branch: Git branch to install from (for testing). Mutually exclusive with target_version.

    Returns:
        Tuple of (success, message)
    """
    current_version = __version__

    if not current_version:
        return False, "flowspec not installed via uv tool"

    # Branch install mode - install from git branch
    if branch:
        # Check if there's a newer release available - user might want to upgrade
        latest_release = get_github_latest_release(REPO_OWNER, REPO_NAME)
        if latest_release and compare_semver(current_version, latest_release) < 0:
            console.print(
                f"[yellow]Note:[/yellow] Release v{latest_release} available "
                f"(current: {current_version})"
            )
            console.print(
                "[dim]Run 'flowspec upgrade-tools' without --branch to upgrade to release[/dim]\n"
            )

        if dry_run:
            return True, f"Would install from branch '{branch}'"

        git_url = f"git+https://github.com/{REPO_OWNER}/{REPO_NAME}.git"
        git_url = f"{git_url}@{branch}"

        try:
            subprocess.run(
                [
                    "uv",
                    "tool",
                    "install",
                    "--force",
                    "flowspec-cli",
                    "--from",
                    git_url,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Installed from branch '{branch}'"
        except subprocess.CalledProcessError as e:
            return False, f"Install failed: {e.stderr}"
        except FileNotFoundError:
            return False, "uv not found - install uv first"

    # Normal version-based upgrade
    if target_version:
        # Validate that the requested version exists
        target_version = target_version.lstrip("v")
        if not version_exists_in_releases(REPO_OWNER, REPO_NAME, target_version):
            return False, f"Version {target_version} not found in releases"
        install_version = target_version
    else:
        install_version = get_github_latest_release(REPO_OWNER, REPO_NAME)
        if not install_version:
            return False, "Could not determine latest version"

    # Check if already at target version
    if current_version == install_version:
        return True, f"Already at version {current_version}"

    # For latest upgrades only, skip if current is newer
    if not target_version and compare_semver(current_version, install_version) >= 0:
        return True, f"Already at latest version ({current_version})"

    if dry_run:
        return (
            True,
            f"Would install version {install_version} (current: {current_version})",
        )

    # Always use git-based installation since flowspec-cli is installed from git, not PyPI
    # Using 'uv tool upgrade' returns 0 but doesn't actually upgrade git-sourced packages

    # Install from git at the specific release tag
    git_url = f"git+https://github.com/{REPO_OWNER}/{REPO_NAME}.git"
    git_url = f"{git_url}@v{install_version}"

    try:
        subprocess.run(
            [
                "uv",
                "tool",
                "install",
                "--force",
                "flowspec-cli",
                "--from",
                git_url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # After successful install, trust the version we just installed
        # rather than re-detecting which may return stale results due to shell caching
        return True, f"Upgraded from {current_version} to {install_version}"
    except subprocess.CalledProcessError as e:
        return False, f"Install failed: {e.stderr}"
    except FileNotFoundError:
        return False, "uv not found - install uv first"


def _upgrade_backlog_md(dry_run: bool = False) -> tuple[bool, str]:
    """Upgrade or install backlog-md via npm/pnpm.

    Uses _run_npm_global_install which tries pnpm first, then falls back to npm.

    Args:
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (success, message)
    """
    current_version = check_backlog_installed_version()
    available_version = get_npm_latest_version("backlog.md")

    if not available_version:
        return False, "Could not determine latest version"

    # Not installed - install it
    if not current_version:
        if dry_run:
            return True, f"Would install version {available_version}"

        success, message, _ = _run_npm_global_install("backlog.md", available_version)
        if not success:
            return False, f"Install failed: {message}"

        new_version = check_backlog_installed_version()
        if new_version:
            return True, f"Installed version {new_version}"
        return False, "Install completed but version check failed"

    # Already at latest
    if compare_semver(current_version, available_version) >= 0:
        return True, f"Already at latest version ({current_version})"

    if dry_run:
        return True, f"Would upgrade from {current_version} to {available_version}"

    success, message, _ = _run_npm_global_install("backlog.md", available_version)
    if not success:
        return False, f"Upgrade failed: {message}"

    new_version = check_backlog_installed_version()
    if new_version == available_version:
        return True, f"Upgraded from {current_version} to {new_version}"
    return True, f"Upgrade completed (version: {new_version or 'unknown'})"


def _upgrade_beads(dry_run: bool = False) -> tuple[bool, str]:
    """Upgrade or install beads via npm/pnpm.

    Uses _run_npm_global_install which tries pnpm first, then falls back to npm.

    Args:
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (success, message)
    """
    current_version = check_beads_installed_version()
    available_version = get_npm_latest_version("@beads/bd")

    if not available_version:
        return False, "Could not determine latest version"

    # Not installed - install it
    if not current_version:
        if dry_run:
            return True, f"Would install version {available_version}"

        success, message, _ = _run_npm_global_install("@beads/bd", available_version)
        if not success:
            return False, f"Install failed: {message}"

        new_version = check_beads_installed_version()
        if new_version:
            return True, f"Installed version {new_version}"
        return False, "Install completed but version check failed"

    # Already at latest
    if compare_semver(current_version, available_version) >= 0:
        return True, f"Already at latest version ({current_version})"

    if dry_run:
        return True, f"Would upgrade from {current_version} to {available_version}"

    success, message, _ = _run_npm_global_install("@beads/bd", available_version)
    if not success:
        return False, f"Upgrade failed: {message}"

    new_version = check_beads_installed_version()
    if new_version == available_version:
        return True, f"Upgraded from {current_version} to {new_version}"
    return True, f"Upgrade completed (version: {new_version or 'unknown'})"


def _list_flowspec_versions() -> None:
    """List available flowspec versions from GitHub releases."""
    console.print("[cyan]Fetching available flowspec versions...[/cyan]\n")

    releases = get_github_releases(REPO_OWNER, REPO_NAME, limit=20)

    if not releases:
        console.print("[red]Could not fetch releases from GitHub[/red]")
        raise typer.Exit(1)

    current_version = __version__

    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Version", style="cyan")
    table.add_column("Released", style="dim")
    table.add_column("Status", style="green")

    for release in releases:
        version = release["version"]
        published = release["published_at"]
        prerelease = release.get("prerelease", False)

        status = ""
        if version == current_version:
            status = "← installed"
        elif prerelease:
            status = "(prerelease)"

        table.add_row(version, published, status)

    console.print(table)
    console.print()
    console.print(f"[dim]Current installed version: {current_version}[/dim]")
    console.print(
        "[dim]Use 'flowspec upgrade-tools --version X.X.X' to install a specific version[/dim]"
    )


@app.command(name="upgrade-tools")
def upgrade_tools(
    component: str = typer.Option(
        None,
        "--component",
        "-c",
        help="Specific component (flowspec, backlog, beads). All if not specified.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be upgraded without making changes"
    ),
    version: str = typer.Option(
        None,
        "--version",
        "-v",
        help="Install specific flowspec version (e.g., 0.2.325). Only applies to flowspec component.",
    ),
    list_versions: bool = typer.Option(
        False,
        "--list-versions",
        "-l",
        help="List available flowspec versions and exit.",
    ),
    branch: str = typer.Option(
        None,
        "--branch",
        "-b",
        help="Install flowspec from a git branch (for testing). Upgrades to releases when available.",
    ),
):
    """
    Install or upgrade CLI tools (flowspec, backlog-md, beads).

    This installs missing tools and upgrades existing ones to their latest versions.

    Tools managed:
    - flowspec (flowspec-cli): via uv tool
    - backlog-md: via npm/pnpm global install
    - beads: via npm/pnpm global install

    Examples:
        flowspec upgrade-tools                    # Install/upgrade all tools
        flowspec upgrade-tools -c flowspec        # Upgrade only flowspec
        flowspec upgrade-tools -c backlog         # Install/upgrade backlog-md
        flowspec upgrade-tools -c beads           # Install/upgrade beads
        flowspec upgrade-tools --dry-run          # Preview what would happen
        flowspec upgrade-tools --version 0.2.325  # Install specific flowspec version
        flowspec upgrade-tools --list-versions    # Show available versions
        flowspec upgrade-tools --branch fix-bug   # Install from a git branch (testing)

    See also:
        flowspec upgrade-repo    # Upgrade repository templates
    """
    show_banner()

    # Handle --list-versions
    if list_versions:
        _list_flowspec_versions()
        return

    # Version and branch are mutually exclusive
    if version and branch:
        console.print("[red]Error:[/red] --version and --branch are mutually exclusive")
        raise typer.Exit(1)

    # Version/branch flags only apply to flowspec
    if (version or branch) and component and component != "flowspec":
        console.print(
            "[red]Error:[/red] --version and --branch only apply to flowspec component"
        )
        raise typer.Exit(1)

    # If version or branch specified without component, assume flowspec only
    if (version or branch) and not component:
        component = "flowspec"

    _run_upgrade_tools(
        dry_run=dry_run, component=component, target_version=version, branch=branch
    )


def _run_upgrade_tools(
    dry_run: bool = False,
    component: str | None = None,
    target_version: str | None = None,
    branch: str | None = None,
) -> None:
    """Internal helper to run upgrade-tools logic.

    Args:
        dry_run: If True, only show what would be done
        component: Optional specific component to upgrade
        target_version: Optional specific version for flowspec
        branch: Optional git branch to install from (for testing)
    """
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    if target_version:
        console.print(f"[cyan]Target version: {target_version}[/cyan]\n")

    if branch:
        console.print(f"[cyan]Installing from branch: {branch}[/cyan]\n")

    # Check for duplicate installations that could cause version conflicts
    if not component or component == "flowspec":
        _warn_duplicate_installations()

    # Validate component if specified
    if component and component not in UPGRADE_TOOLS_COMPONENTS:
        console.print(
            f"[red]Error:[/red] Unknown component '{component}'. "
            f"Valid options: {', '.join(UPGRADE_TOOLS_COMPONENTS)}"
        )
        raise typer.Exit(1)

    # Get current versions for display (involves network calls)
    with console.status("[cyan]Checking available versions...[/cyan]"):
        versions = get_all_component_versions()

    # Build table of components to upgrade
    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("Component", style="cyan")
    table.add_column("Current", style="green")
    table.add_column("Available", style="dim")
    table.add_column("Status", style="yellow")

    results = []

    # flowspec
    if not component or component == "flowspec":
        jp_current = versions["flowspec"].get("installed", "-")
        jp_available = (
            branch or target_version or versions["flowspec"].get("available", "-")
        )

        with console.status("[cyan]Upgrading flowspec...[/cyan]"):
            success, message = _upgrade_flowspec(
                dry_run=dry_run, target_version=target_version, branch=branch
            )
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        results.append(("flowspec", success, message))

        table.add_row("flowspec", jp_current, jp_available, f"{status} {message}")

    # backlog-md
    if not component or component == "backlog":
        bl_current = versions["backlog_md"].get("installed", "-")
        bl_available = versions["backlog_md"].get("available", "-")

        with console.status("[cyan]Upgrading backlog-md...[/cyan]"):
            success, message = _upgrade_backlog_md(dry_run=dry_run)
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        results.append(("backlog-md", success, message))

        table.add_row("backlog-md", bl_current, bl_available, f"{status} {message}")

    # beads
    if not component or component == "beads":
        bd_current = versions["beads"].get("installed", "-")
        bd_available = versions["beads"].get("available", "-")

        with console.status("[cyan]Upgrading beads...[/cyan]"):
            success, message = _upgrade_beads(dry_run=dry_run)
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        results.append(("beads", success, message))

        table.add_row("beads", bd_current, bd_available, f"{status} {message}")

    console.print(table)
    console.print()

    # Summary
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)

    if dry_run:
        console.print("[dim]Run without --dry-run to apply upgrades[/dim]")
    elif successful == total:
        console.print("[bold green]All tools upgraded successfully![/bold green]")
    else:
        console.print(
            f"[yellow]Upgraded {successful}/{total} tools. "
            "Check messages above for details.[/yellow]"
        )


def _run_upgrade_repo(dry_run: bool = False) -> None:
    """Internal helper to run upgrade-repo logic.

    Note: This is a simplified version. The full upgrade_repo command has
    additional options that are not exposed through the dispatcher.

    Args:
        dry_run: If True, only show what would be done
    """
    console.print(
        "[yellow]Note:[/yellow] For full options, use 'flowspec upgrade-repo' directly.\n"
    )
    console.print(
        "[dim]This simplified mode upgrades to latest versions. "
        "Use 'flowspec upgrade-repo --help' for version pinning options.[/dim]\n"
    )

    # For the dispatcher, we just inform the user about the dedicated command
    # since upgrade_repo has many options not easily passed through
    console.print("[cyan]To upgrade repository templates, run:[/cyan]")
    console.print("  flowspec upgrade-repo")
    console.print()
    console.print("[cyan]Options available:[/cyan]")
    console.print("  --dry-run              Preview changes")
    console.print("  --base-version X       Pin base spec-kit version")
    console.print("  --extension-version X  Pin flowspec version")
    console.print("  --templates-only       Only update templates")


@app.command()
def upgrade(
    tools: bool = typer.Option(
        False, "--tools", "-t", help="Upgrade globally installed CLI tools"
    ),
    repo: bool = typer.Option(
        False, "--repo", "-r", help="Upgrade repository templates"
    ),
    all_components: bool = typer.Option(
        False, "--all", "-a", help="Upgrade both tools and repository"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be upgraded without making changes"
    ),
):
    """
    Upgrade flowspec components (dispatcher for upgrade-tools and upgrade-repo).

    By default, shows upgrade options interactively. Use flags to specify what to upgrade:

    Examples:
        flowspec upgrade              # Interactive: choose what to upgrade
        flowspec upgrade --tools      # Same as 'flowspec upgrade-tools'
        flowspec upgrade --repo       # Same as 'flowspec upgrade-repo'
        flowspec upgrade --all        # Upgrade both tools and repo

    See also:
        flowspec upgrade-tools    # Upgrade globally installed CLI tools
        flowspec upgrade-repo     # Upgrade repository templates
    """
    show_banner()

    # Handle explicit flags
    if all_components:
        # Upgrade both
        console.print("[cyan]Upgrading CLI tools...[/cyan]\n")
        _run_upgrade_tools(dry_run=dry_run)

        console.print("\n" + "=" * 50 + "\n")
        console.print("[cyan]Upgrading repository templates...[/cyan]\n")
        _run_upgrade_repo(dry_run=dry_run)
        return

    if tools:
        # Delegate to upgrade-tools
        _run_upgrade_tools(dry_run=dry_run)
        return

    if repo:
        # Delegate to upgrade-repo
        _run_upgrade_repo(dry_run=dry_run)
        return

    # Interactive mode - show options
    console.print("[cyan]What would you like to upgrade?[/cyan]\n")
    console.print("  [bold]1.[/bold] CLI Tools (flowspec, backlog-md)")
    console.print("       Upgrades the globally installed command-line tools")
    console.print()
    console.print("  [bold]2.[/bold] Repository Templates")
    console.print("       Upgrades templates and config files in current project")
    console.print()
    console.print("  [bold]3.[/bold] Both")
    console.print("       Upgrades CLI tools and repository templates")
    console.print()

    if not sys.stdin.isatty():
        console.print(
            "[yellow]Non-interactive mode. Use --tools, --repo, or --all flag.[/yellow]"
        )
        raise typer.Exit(1)

    choice = typer.prompt("Enter choice (1/2/3)", default="1")

    console.print()

    if choice == "1":
        _run_upgrade_tools(dry_run=dry_run)
    elif choice == "2":
        _run_upgrade_repo(dry_run=dry_run)
    elif choice == "3":
        console.print("[cyan]Upgrading CLI tools...[/cyan]\n")
        _run_upgrade_tools(dry_run=dry_run)

        console.print("\n" + "=" * 50 + "\n")
        console.print("[cyan]Upgrading repository templates...[/cyan]\n")
        _run_upgrade_repo(dry_run=dry_run)
    else:
        console.print(f"[red]Invalid choice:[/red] {choice}")
        raise typer.Exit(1)


@app.command()
def check():
    """Check that all required tools are installed."""
    show_banner()
    console.print("[bold]Checking for installed tools...[/bold]\n")

    tracker = StepTracker("Check Available Tools")

    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_name = agent_config["name"]

        tracker.add(agent_key, agent_name)
        agent_results[agent_key] = check_tool(agent_key, tracker=tracker)

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    check_tool("code-insiders", tracker=tracker)

    # Check backlog-md
    tracker.add("backlog", "backlog-md (task management)")
    backlog_version = check_backlog_installed_version()
    if backlog_version:
        tracker.complete("backlog", f"v{backlog_version}")
    else:
        tracker.skip("backlog", "not installed")

    console.print(tracker.render())

    # Show backlog-md version compatibility info if installed
    if backlog_version:
        recommended_version = get_backlog_validated_version()
        if recommended_version:
            console.print()
            if backlog_version == recommended_version:
                console.print(
                    f"[green]backlog-md is at recommended version ({backlog_version})[/green]"
                )
            else:
                console.print(
                    f"[yellow]backlog-md version:[/yellow] {backlog_version} "
                    f"[dim](recommended: {recommended_version})[/dim]"
                )
                console.print(
                    "[dim]Run 'flowspec backlog upgrade' to sync to recommended version[/dim]"
                )

    console.print("\n[bold green]Specify CLI is ready to use![/bold green]")

    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")

    if not backlog_version:
        console.print(
            "[dim]Tip: Install backlog-md for task management: flowspec backlog install[/dim]"
        )


@app.command(name="dev-setup")
def dev_setup(
    force: bool = typer.Option(
        False,
        "--force",
        help="Recreate symlinks even if they already exist",
    ),
):
    """
    Set up flowspec source repository for development.

    This command prepares the flowspec source repository to use its own
    /spec:* and /flow:* commands during development. It creates symlinks
    for multiple AI agents:

    - Claude Code: .claude/commands/spec/ and .claude/commands/flow/
      (symlinks to templates/commands/)
    - VS Code Copilot: .github/prompts/ (symlinks as spec.*.prompt.md
      and flowspec.*.prompt.md)

    It also creates .vscode/settings.json with chat.promptFiles enabled for Copilot.

    This is only useful when developing flowspec itself. For normal
    projects, use 'flowspec init' instead.

    Examples:
        flowspec dev-setup           # Set up for development
        flowspec dev-setup --force   # Recreate symlinks if they exist
    """
    show_banner()

    project_path = Path.cwd()

    # Check that we're in the flowspec source repository
    marker_path = project_path / SOURCE_REPO_MARKER
    if not marker_path.exists():
        console.print(
            "[red]Error:[/red] This command is only for the flowspec source repository."
        )
        console.print(
            f"[yellow]Tip:[/yellow] The '{SOURCE_REPO_MARKER}' marker file was not found."
        )
        console.print(
            "[yellow]Tip:[/yellow] If this IS the flowspec repo, create the marker file first."
        )
        raise typer.Exit(1)

    templates_dir = project_path / "templates" / "commands"
    flow_templates_dir = templates_dir / "flow"
    spec_templates_dir = templates_dir / "spec"
    if not templates_dir.exists():
        console.print(
            f"[red]Error:[/red] Templates directory not found: {templates_dir}"
        )
        raise typer.Exit(1)

    # Get list of template command files
    spec_files = (
        list(spec_templates_dir.glob("*.md")) if spec_templates_dir.exists() else []
    )
    flow_files = (
        list(flow_templates_dir.glob("*.md")) if flow_templates_dir.exists() else []
    )

    if not spec_files and not flow_files:
        console.print(
            f"[yellow]Warning:[/yellow] No command templates found in {templates_dir}"
        )
        raise typer.Exit(1)

    console.print("[cyan]Setting up development environment for flowspec...[/cyan]\n")

    tracker = StepTracker("Dev Setup")
    tracker.add("check", "Check prerequisites")
    tracker.complete("check", "flowspec source repository detected")

    all_errors = []

    # === Claude Code Setup - spec commands ===
    tracker.add("claude_spec", "Set up Claude Code spec commands")

    spec_commands_dir = project_path / ".claude" / "commands" / "spec"
    spec_commands_dir.mkdir(parents=True, exist_ok=True)

    claude_spec_created = 0
    claude_spec_skipped = 0
    claude_spec_errors = []

    for template_file in spec_files:
        symlink_path = spec_commands_dir / template_file.name
        relative_target = (
            Path("..")
            / ".."
            / ".."
            / "templates"
            / "commands"
            / "spec"
            / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    claude_spec_created += 1
                else:
                    claude_spec_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                claude_spec_created += 1
        except OSError as e:
            claude_spec_errors.append(f"spec/{template_file.name}: {e}")

    if claude_spec_errors:
        tracker.error("claude_spec", f"{len(claude_spec_errors)} errors")
        all_errors.extend(claude_spec_errors)
    else:
        tracker.complete(
            "claude_spec",
            f"{claude_spec_created} created, {claude_spec_skipped} skipped",
        )

    # === Claude Code Setup - flowspec commands ===
    tracker.add("claude_flow", "Set up Claude Code flow commands")

    flow_commands_dir = project_path / ".claude" / "commands" / "flow"
    flow_commands_dir.mkdir(parents=True, exist_ok=True)

    claude_flow_created = 0
    claude_flow_skipped = 0
    claude_flow_errors = []

    for template_file in flow_files:
        symlink_path = flow_commands_dir / template_file.name
        relative_target = (
            Path("..")
            / ".."
            / ".."
            / "templates"
            / "commands"
            / "flow"
            / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    claude_flow_created += 1
                else:
                    claude_flow_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                claude_flow_created += 1
        except OSError as e:
            claude_flow_errors.append(f"flowspec/{template_file.name}: {e}")

    if claude_flow_errors:
        tracker.error("claude_flow", f"{len(claude_flow_errors)} errors")
        all_errors.extend(claude_flow_errors)
    else:
        tracker.complete(
            "claude_flow",
            f"{claude_flow_created} created, {claude_flow_skipped} skipped",
        )

    # === VS Code Copilot Setup ===
    tracker.add("copilot", "Set up VS Code Copilot prompts")

    prompts_dir = project_path / ".github" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    copilot_created = 0
    copilot_skipped = 0
    copilot_errors = []

    # Create spec.*.prompt.md symlinks for spec commands
    for template_file in spec_files:
        # VS Code Copilot uses spec.*.prompt.md format
        prompt_name = f"spec.{template_file.stem}.prompt.md"
        symlink_path = prompts_dir / prompt_name
        relative_target = (
            Path("..") / ".." / "templates" / "commands" / "spec" / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    copilot_created += 1
                else:
                    copilot_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                copilot_created += 1
        except OSError as e:
            copilot_errors.append(f"{prompt_name}: {e}")

    # Create flowspec.*.prompt.md symlinks for flowspec commands
    for template_file in flow_files:
        # VS Code Copilot uses flowspec.*.prompt.md format
        prompt_name = f"flowspec.{template_file.stem}.prompt.md"
        symlink_path = prompts_dir / prompt_name
        relative_target = (
            Path("..") / ".." / "templates" / "commands" / "flow" / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    copilot_created += 1
                else:
                    copilot_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                copilot_created += 1
        except OSError as e:
            copilot_errors.append(f"{prompt_name}: {e}")

    if copilot_errors:
        tracker.error("copilot", f"{len(copilot_errors)} errors")
        all_errors.extend(copilot_errors)
    else:
        tracker.complete(
            "copilot", f"{copilot_created} created, {copilot_skipped} skipped"
        )

    # === VS Code Settings Setup ===
    tracker.add("vscode", "Configure VS Code settings")

    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    settings_file = vscode_dir / "settings.json"

    try:
        # Read existing settings or start fresh
        existing_settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    import json

                    content = f.read()
                    # Handle jsonc (with comments) by stripping single-line comments
                    import re

                    content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
                    existing_settings = json.loads(content) if content.strip() else {}
            except (json.JSONDecodeError, ValueError):
                existing_settings = {}

        # Merge with required settings for Copilot prompt files
        existing_settings["chat.promptFiles"] = True

        # Write updated settings
        with open(settings_file, "w") as f:
            import json

            json.dump(existing_settings, f, indent=4)
            f.write("\n")

        tracker.complete("vscode", "chat.promptFiles enabled")
    except OSError as e:
        tracker.error("vscode", str(e))
        all_errors.append(f"settings.json: {e}")

    # === Verify Symlinks ===
    tracker.add("verify", "Verify symlinks")

    valid = 0
    broken = 0

    # Check Claude spec symlinks
    for symlink_path in spec_commands_dir.glob("*.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    # Check Claude flowspec symlinks
    for symlink_path in flow_commands_dir.glob("*.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    # Check Copilot symlinks
    for symlink_path in prompts_dir.glob("*.prompt.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    if broken > 0:
        tracker.error("verify", f"{broken} broken symlinks")
    else:
        tracker.complete("verify", f"{valid} valid symlinks")

    tracker.add("final", "Dev setup complete")
    tracker.complete("final", "ready for development")

    console.print(tracker.render())

    console.print("\n[bold green]Development setup complete![/bold green]")

    console.print(
        "\n[bold]Claude Code[/bold] - The following commands are now available:"
    )
    console.print("  [dim]spec:[/dim]")
    for template_file in sorted(spec_files):
        console.print(f"    [cyan]/spec:{template_file.stem}[/cyan]")
    console.print("  [dim]flow:[/dim]")
    for template_file in sorted(flow_files):
        console.print(f"    [cyan]/flow:{template_file.stem}[/cyan]")

    console.print(
        "\n[bold]VS Code Copilot[/bold] - The following prompts are now available:"
    )
    for template_file in sorted(spec_files):
        console.print(f"  [cyan]/spec.{template_file.stem}[/cyan]")
    for template_file in sorted(flow_files):
        console.print(f"  [cyan]/flowspec.{template_file.stem}[/cyan]")

    console.print(
        "\n[dim]Note: Restart your AI assistant to pick up the new commands.[/dim]"
    )

    if all_errors:
        console.print("\n[yellow]Warning:[/yellow] Some operations failed:")
        for error in all_errors:
            console.print(f"  [red]•[/red] {error}")
        console.print(
            "[yellow]On Windows, you may need to enable Developer Mode or run as Administrator.[/yellow]"
        )
        raise typer.Exit(1)


# Create backlog subcommand group
backlog_app = typer.Typer(
    name="backlog",
    help="Manage Backlog.md format tasks",
    add_completion=False,
)
app.add_typer(backlog_app, name="backlog")


@backlog_app.command("migrate")
def backlog_migrate(
    source: Optional[str] = typer.Option(
        None,
        "--source",
        help="Path to tasks.md file (default: ./tasks.md)",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output backlog directory (default: ./backlog)",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backup of original tasks.md (default: true)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview migration without writing files",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing backlog tasks",
    ),
):
    """
    Migrate existing tasks.md file to Backlog.md format.

    This command converts legacy tasks.md files to the new Backlog.md format
    with individual task files. It preserves all task metadata including IDs,
    labels, dependencies, status, and user stories.

    Examples:
        flowspec backlog migrate                          # Migrate ./tasks.md to ./backlog
        flowspec backlog migrate --source ../tasks.md     # Migrate from specific file
        flowspec backlog migrate --dry-run                # Preview migration
        flowspec backlog migrate --force                  # Overwrite existing tasks
        flowspec backlog migrate --no-backup              # Skip backup creation
    """
    show_banner()

    # Determine paths
    source_path = Path(source) if source else Path.cwd() / "tasks.md"
    output_dir = Path(output) if output else Path.cwd() / "backlog"

    # Validate source file
    if not source_path.exists():
        console.print(f"[red]Error:[/red] Source file not found: {source_path}")
        raise typer.Exit(1)

    if not source_path.is_file():
        console.print(f"[red]Error:[/red] Source must be a file: {source_path}")
        raise typer.Exit(1)

    if source_path.name != "tasks.md":
        console.print(
            f"[yellow]Warning:[/yellow] Source file is not named 'tasks.md': {source_path.name}"
        )
        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(0)

    console.print(f"[cyan]Source:[/cyan] {source_path}")
    console.print(f"[cyan]Output:[/cyan] {output_dir}")
    console.print(f"[cyan]Backup:[/cyan] {backup}")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")

    console.print()

    # Import migration module
    from .backlog import TaskMapper

    # Create mapper
    mapper = TaskMapper(output_dir)

    try:
        # Check for existing tasks
        existing_count = 0
        if (output_dir / "tasks").exists():
            existing_count = len(list((output_dir / "tasks").glob("task-*.md")))
            if existing_count > 0 and not force and not dry_run:
                console.print(
                    f"[yellow]Warning:[/yellow] Found {existing_count} existing task files in {output_dir / 'tasks'}"
                )
                console.print(
                    "[yellow]Use --force to overwrite existing tasks[/yellow]"
                )
                if not typer.confirm("Continue (will skip existing tasks)?"):
                    raise typer.Exit(0)

        # Create backup if requested
        backup_path = None
        if backup and not dry_run:
            backup_path = source_path.with_suffix(".md.backup")
            backup_counter = 1
            while backup_path.exists():
                backup_path = source_path.with_suffix(f".md.backup.{backup_counter}")
                backup_counter += 1

            import shutil

            shutil.copy2(source_path, backup_path)
            console.print(f"[green]Created backup:[/green] {backup_path}\n")

        # Perform migration
        result = mapper.generate_from_tasks_file(
            source_path,
            overwrite=force,
            dry_run=dry_run,
        )

        # Handle results
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            console.print(f"[red]Migration failed:[/red] {error_msg}")

            # Show validation errors if present
            if "validation_errors" in result:
                console.print("\n[yellow]Validation Errors:[/yellow]")
                for error in result["validation_errors"]:
                    console.print(f"  - {error}")

            # Remove backup on failure (if created)
            if backup_path and backup_path.exists():
                backup_path.unlink()
                console.print("[dim]Removed backup (migration failed)[/dim]")

            raise typer.Exit(1)

        # Show success message
        if dry_run:
            console.print("[bold green]Migration preview completed![/bold green]\n")
        else:
            console.print("[bold green]Migration complete![/bold green]\n")

        # Display statistics
        stats_lines = []

        if "tasks_parsed" in result:
            stats_lines.append(
                f"{'Tasks Found':<20} [green]{result['tasks_parsed']}[/green]"
            )

        if "tasks_created" in result and not dry_run:
            stats_lines.append(
                f"{'Tasks Created':<20} [green]{result['tasks_created']}[/green]"
            )

        # Count completed vs pending
        from .backlog.parser import TaskParser

        parser = TaskParser()
        tasks = parser.parse_tasks_file(source_path)
        completed = sum(1 for t in tasks if t.is_completed)
        pending = len(tasks) - completed

        if completed > 0:
            stats_lines.append(f"{'Completed Tasks':<20} [green]{completed}[/green]")
        if pending > 0:
            stats_lines.append(f"{'Pending Tasks':<20} [cyan]{pending}[/cyan]")

        # Count user stories
        user_stories = set(t.user_story for t in tasks if t.user_story)
        if user_stories:
            stats_lines.append(
                f"{'User Stories':<20} [cyan]{len(user_stories)}[/cyan] ({', '.join(sorted(user_stories))})"
            )

        # Show groupings
        if "tasks_by_phase" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Phase:[/bold]")
            for phase, task_ids in sorted(result["tasks_by_phase"].items()):
                stats_lines.append(f"  {phase:<18} {len(task_ids)} tasks")

        if "tasks_by_story" in result and len(result["tasks_by_story"]) > 1:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Story:[/bold]")
            for story, task_ids in sorted(result["tasks_by_story"].items()):
                if story != "No Story":
                    stats_lines.append(f"  {story:<18} {len(task_ids)} tasks")

        if stats_lines:
            console.print(
                Panel(
                    "\n".join(stats_lines),
                    title="Migration Summary",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

        # Show next steps
        if not dry_run:
            console.print()
            next_steps = [
                f"1. Review migrated tasks in: [cyan]{output_dir / 'tasks'}[/cyan]",
                "2. Original tasks.md remains unchanged",
            ]

            if backup_path:
                next_steps.append(f"3. Backup created at: [cyan]{backup_path}[/cyan]")

            next_steps.extend(
                [
                    "",
                    "[dim]You can now track task progress by updating status in task frontmatter[/dim]",
                    "[dim]Use 'flowspec tasks generate' to regenerate tasks from spec[/dim]",
                ]
            )

            console.print(
                Panel(
                    "\n".join(next_steps),
                    title="Next Steps",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--debug" in sys.argv:
            import traceback

            console.print("\n[yellow]Debug trace:[/yellow]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def tasks(
    action: str = typer.Argument(
        "generate", help="Action to perform (currently only 'generate' is supported)"
    ),
    format: str = typer.Option(
        "backlog",
        "--format",
        help="Output format: 'backlog' (Backlog.md format) or 'markdown' (legacy tasks.md)",
    ),
    source: Optional[str] = typer.Option(
        None,
        "--source",
        help="Path to source file or directory (default: current directory)",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output directory for backlog format (default: ./backlog)",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing task files"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be generated without creating files",
    ),
):
    """
    Generate tasks from spec/plan/tasks.md files.

    This command can generate tasks in two formats:

    1. backlog (default): Creates individual task files in ./backlog/tasks/ directory
       following the Backlog.md format specification

    2. markdown: Generates a single tasks.md file (legacy format)

    The command automatically detects the source files (spec.md, plan.md, tasks.md)
    from the current directory or specified source path.

    Examples:
        flowspec tasks generate                           # Generate backlog tasks from current dir
        flowspec tasks generate --format markdown         # Generate legacy tasks.md format
        flowspec tasks generate --source ./feature-x      # Generate from specific directory
        flowspec tasks generate --dry-run                 # Preview without writing files
        flowspec tasks generate --overwrite               # Overwrite existing tasks
    """
    show_banner()

    # Only support 'generate' action for now
    if action != "generate":
        console.print(
            f"[red]Error:[/red] Unsupported action '{action}'. Currently only 'generate' is supported."
        )
        raise typer.Exit(1)

    # Validate format
    if format not in ["backlog", "markdown"]:
        console.print(
            f"[red]Error:[/red] Invalid format '{format}'. Must be 'backlog' or 'markdown'."
        )
        raise typer.Exit(1)

    # Determine source path
    source_path = Path(source) if source else Path.cwd()
    if not source_path.exists():
        console.print(f"[red]Error:[/red] Source path does not exist: {source_path}")
        raise typer.Exit(1)

    # Handle markdown format (legacy)
    if format == "markdown":
        console.print("[yellow]Legacy markdown format is not yet implemented.[/yellow]")
        console.print(
            "[dim]Tip: Use --format backlog for the new Backlog.md format[/dim]"
        )
        raise typer.Exit(1)

    # Handle backlog format
    from .backlog import TaskMapper

    # Determine backlog directory
    backlog_dir = (
        Path(output_dir)
        if output_dir
        else (
            source_path / "backlog" if source_path.is_dir() else Path.cwd() / "backlog"
        )
    )

    console.print(f"[cyan]Source:[/cyan] {source_path}")
    console.print(f"[cyan]Output:[/cyan] {backlog_dir}")
    console.print(f"[cyan]Format:[/cyan] {format}")
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
    console.print()

    # Create mapper and generate tasks
    mapper = TaskMapper(backlog_dir)

    try:
        # Determine if source is a file or directory
        if source_path.is_file():
            if source_path.name != "tasks.md":
                console.print(
                    f"[red]Error:[/red] Source file must be named 'tasks.md', got: {source_path.name}"
                )
                raise typer.Exit(1)
            result = mapper.generate_from_tasks_file(
                source_path, overwrite=overwrite, dry_run=dry_run
            )
        elif source_path.is_dir():
            result = mapper.generate_from_spec(
                source_path, overwrite=overwrite, dry_run=dry_run
            )
        else:
            console.print(f"[red]Error:[/red] Invalid source path: {source_path}")
            raise typer.Exit(1)

        # Handle results
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            console.print(f"[red]Error:[/red] {error_msg}")

            # Show validation errors if present
            if "validation_errors" in result:
                console.print("\n[yellow]Validation Errors:[/yellow]")
                for error in result["validation_errors"]:
                    console.print(f"  - {error}")

            raise typer.Exit(1)

        # Show success message and statistics
        if dry_run:
            console.print("[bold green]Dry run completed successfully![/bold green]\n")
        else:
            console.print("[bold green]Tasks generated successfully![/bold green]\n")

        # Display statistics
        stats_lines = []

        if "tasks_parsed" in result:
            stats_lines.append(
                f"{'Tasks Parsed':<20} [green]{result['tasks_parsed']}[/green]"
            )

        if "tasks_created" in result and not dry_run:
            stats_lines.append(
                f"{'Tasks Created':<20} [green]{result['tasks_created']}[/green]"
            )

        if "user_stories" in result:
            stats_lines.append(
                f"{'User Stories':<20} [cyan]{result['user_stories']}[/cyan]"
            )

        # Show groupings
        if "tasks_by_phase" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Phase:[/bold]")
            for phase, task_ids in sorted(result["tasks_by_phase"].items()):
                stats_lines.append(f"  {phase:<18} {len(task_ids)} tasks")

        if "tasks_by_story" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Story:[/bold]")
            for story, task_ids in sorted(result["tasks_by_story"].items()):
                stats_lines.append(f"  {story:<18} {len(task_ids)} tasks")

        # Show execution order
        if "execution_order" in result:
            execution_order = result["execution_order"]
            stats_lines.append("")
            stats_lines.append(
                f"[bold]Execution Order:[/bold] {', '.join(execution_order[:5])}"
                + (
                    f"... ({len(execution_order)} total)"
                    if len(execution_order) > 5
                    else ""
                )
            )

        # Show parallel batches
        if "parallel_batches" in result:
            parallel_batches = result["parallel_batches"]
            stats_lines.append(
                f"[bold]Parallel Batches:[/bold] {len(parallel_batches)}"
            )

        # Show critical path
        if "critical_path" in result:
            critical_path = result["critical_path"]
            stats_lines.append(
                f"[bold]Critical Path Length:[/bold] {len(critical_path)}"
            )

        if stats_lines:
            console.print(
                Panel(
                    "\n".join(stats_lines),
                    title="Task Generation Summary",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

        # Show created files (if not dry run)
        if "created_files" in result and not dry_run:
            console.print()
            console.print("[bold]Created Files:[/bold]")
            for file_path in result["created_files"][:10]:  # Show first 10
                console.print(f"  [dim]{file_path}[/dim]")
            if len(result["created_files"]) > 10:
                console.print(
                    f"  [dim]... and {len(result['created_files']) - 10} more[/dim]"
                )

        # Next steps
        if not dry_run:
            console.print()
            next_steps = [
                f"1. Review generated tasks in: [cyan]{backlog_dir / 'tasks'}[/cyan]",
                "2. Edit task files as needed (add assignees, notes, etc.)",
                "3. Track progress by updating task status in frontmatter",
            ]
            console.print(
                Panel(
                    "\n".join(next_steps),
                    title="Next Steps",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--debug" in sys.argv:
            import traceback

            console.print("\n[yellow]Debug trace:[/yellow]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


# Create backlog subcommand group
backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog-md installation and upgrades",
)
app.add_typer(backlog_app, name="backlog")


@backlog_app.command("install")
def backlog_install(
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Specific version to install (default: recommended version from compatibility matrix)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force reinstall even if already installed",
    ),
):
    """
    Install backlog-md CLI tool with validated version.

    This command will:
    1. Auto-detect pnpm or npm package manager
    2. Fetch the recommended version from compatibility matrix
    3. Install backlog-md globally with version pinning
    4. Verify installation success

    Examples:
        flowspec backlog install                    # Install recommended version
        flowspec backlog install --version 1.21.0   # Install specific version
        flowspec backlog install --force            # Force reinstall
    """
    show_banner()

    # Check if already installed
    current_version = check_backlog_installed_version()
    if current_version and not force:
        console.print(
            f"[yellow]backlog-md is already installed (version {current_version})[/yellow]"
        )
        console.print("[dim]Use --force to reinstall[/dim]")
        raise typer.Exit(0)

    # Determine version to install
    target_version = version or get_backlog_validated_version()
    if not target_version:
        console.print(
            "[red]Error:[/red] Could not determine version to install. "
            "Compatibility matrix may be missing or invalid."
        )
        raise typer.Exit(1)

    # Detect package manager
    pkg_manager = detect_package_manager()
    if not pkg_manager:
        console.print(
            "[red]Error:[/red] No Node.js package manager found (pnpm or npm required)"
        )
        console.print(
            "[dim]Install pnpm: https://pnpm.io/installation[/dim]\n"
            "[dim]Or install npm: https://nodejs.org/[/dim]"
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Package Manager:[/cyan] {pkg_manager}")
    console.print(f"[cyan]Target Version:[/cyan] {target_version}\n")

    tracker = StepTracker("Install backlog-md")

    # Install
    tracker.add("install", f"Installing backlog-md@{target_version}")
    tracker.start("install")

    try:
        if pkg_manager == "pnpm":
            cmd = ["pnpm", "add", "-g", f"backlog.md@{target_version}"]
        else:  # npm
            cmd = ["npm", "install", "-g", f"backlog.md@{target_version}"]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        tracker.complete("install", "installed successfully")
    except subprocess.CalledProcessError as e:
        tracker.error("install", "installation failed")
        console.print(tracker.render())
        console.print(f"\n[red]Installation failed:[/red] {e.stderr}")
        raise typer.Exit(1)

    # Verify
    tracker.add("verify", "Verifying installation")
    tracker.start("verify")

    installed_version = check_backlog_installed_version()
    if installed_version:
        tracker.complete("verify", f"version {installed_version}")
    else:
        tracker.error("verify", "verification failed")

    console.print(tracker.render())

    if installed_version:
        console.print("\n[bold green]backlog-md installed successfully![/bold green]")
        console.print(f"[dim]Version: {installed_version}[/dim]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  Run [cyan]backlog --help[/cyan] to get started")
    else:
        console.print(
            "\n[yellow]Installation completed but verification failed[/yellow]"
        )
        console.print("[dim]Try running: backlog --version[/dim]")
        raise typer.Exit(1)


@backlog_app.command("upgrade")
def backlog_upgrade(
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Specific version to upgrade to (default: recommended version from compatibility matrix)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force upgrade even if current version matches",
    ),
):
    """
    Upgrade backlog-md to validated version.

    This command will:
    1. Check currently installed version
    2. Compare to recommended version from compatibility matrix
    3. Upgrade if needed using detected package manager
    4. Verify upgrade success

    Examples:
        flowspec backlog upgrade                    # Upgrade to recommended version
        flowspec backlog upgrade --version 1.22.0   # Upgrade to specific version
        flowspec backlog upgrade --force            # Force upgrade
    """
    show_banner()

    # Check if installed
    current_version = check_backlog_installed_version()
    if not current_version:
        console.print("[yellow]backlog-md is not installed[/yellow]")
        console.print("[dim]Run: flowspec backlog install[/dim]")
        raise typer.Exit(1)

    # Determine target version
    target_version = version or get_backlog_validated_version()
    if not target_version:
        console.print(
            "[red]Error:[/red] Could not determine version to upgrade to. "
            "Compatibility matrix may be missing or invalid."
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Current Version:[/cyan] {current_version}")
    console.print(f"[cyan]Target Version:[/cyan] {target_version}\n")

    # Check if upgrade needed (don't downgrade unless forced)
    version_cmp = compare_semver(current_version, target_version)
    if version_cmp > 0 and not force:
        console.print(
            f"[green]backlog-md is already at a newer version ({current_version})[/green]"
        )
        console.print(
            "[dim]Use --force to downgrade, or update .spec-kit-compatibility.yml[/dim]"
        )
        # Exit 0: This is a successful outcome (already up-to-date), not an error
        raise typer.Exit(0)
    if version_cmp == 0 and not force:
        console.print("[green]backlog-md is already at the recommended version[/green]")
        # Exit 0: This is a successful outcome (already up-to-date), not an error
        raise typer.Exit(0)

    # Detect package manager
    pkg_manager = detect_package_manager()
    if not pkg_manager:
        console.print(
            "[red]Error:[/red] No Node.js package manager found (pnpm or npm required)"
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Package Manager:[/cyan] {pkg_manager}\n")

    tracker = StepTracker("Upgrade backlog-md")

    # Upgrade
    tracker.add("upgrade", f"Upgrading to {target_version}")
    tracker.start("upgrade")

    try:
        if pkg_manager == "pnpm":
            cmd = ["pnpm", "add", "-g", f"backlog.md@{target_version}"]
        else:  # npm
            cmd = ["npm", "install", "-g", f"backlog.md@{target_version}"]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        tracker.complete("upgrade", "upgraded successfully")
    except subprocess.CalledProcessError as e:
        tracker.error("upgrade", "upgrade failed")
        console.print(tracker.render())
        console.print(f"\n[red]Upgrade failed:[/red] {e.stderr}")
        raise typer.Exit(1)

    # Verify
    tracker.add("verify", "Verifying upgrade")
    tracker.start("verify")

    new_version = check_backlog_installed_version()
    if new_version == target_version:
        tracker.complete("verify", f"version {new_version}")
    else:
        tracker.error("verify", "verification failed")

    console.print(tracker.render())

    if new_version == target_version:
        console.print("\n[bold green]backlog-md upgraded successfully![/bold green]")
        console.print(f"[dim]Version: {new_version}[/dim]")
    else:
        console.print("\n[yellow]Upgrade completed but verification failed[/yellow]")
        console.print(
            f"[dim]Expected: {target_version}, Got: {new_version or 'not found'}[/dim]"
        )
        raise typer.Exit(1)


@app.command()
def quality(
    spec_path: str = typer.Argument(
        None, help="Path to specification file (defaults to docs/prd/spec.md)"
    ),
    config_path: str = typer.Option(
        None, "--config", help="Path to custom quality config file"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
    threshold: int = typer.Option(
        None, "--threshold", help="Minimum passing score (overrides config)"
    ),
    check_only: bool = typer.Option(
        False, "--check-only", help="Exit non-zero if below threshold (for CI)"
    ),
):
    """Assess specification quality with automated scoring.

    Analyzes specification files across multiple quality dimensions:
    - Completeness: Required sections present
    - Clarity: Vague terms, passive voice, measurable criteria
    - Traceability: Requirements → plan → tasks linkage
    - Constitutional: Project conventions and tool usage
    - Ambiguity: TBD/TODO markers and uncertainty

    Returns a 0-100 score with detailed recommendations.
    """
    import json as json_lib
    from pathlib import Path

    from rich.table import Table

    from flowspec_cli.quality import QualityConfig, QualityScorer

    # Determine spec path
    if spec_path is None:
        spec_file = Path.cwd() / "docs" / "prd" / "spec.md"
        if not spec_file.exists():
            # Try current directory
            spec_file = Path.cwd() / "spec.md"
    else:
        spec_file = Path(spec_path)

    if not spec_file.exists():
        console.print(f"[red]Error: Specification file not found: {spec_file}[/red]")
        console.print("\nUsage:")
        console.print("  flowspec quality [SPEC_PATH]")
        console.print("  flowspec quality docs/prd/spec.md")
        raise typer.Exit(1)

    # Load configuration
    if config_path:
        config = QualityConfig.load_from_file(Path(config_path))
    else:
        config = QualityConfig.find_config(spec_file.parent)

    # Override threshold if provided
    if threshold is not None:
        config.passing_threshold = threshold

    # Create scorer and assess
    try:
        scorer = QualityScorer(config)
        result = scorer.score_spec(spec_file)
    except Exception as e:
        console.print(f"[red]Error assessing quality: {e}[/red]")
        raise typer.Exit(1)

    # Output results
    if json_output:
        # JSON output
        output = {
            "overall_score": result.overall_score,
            "passing": result.passes(),
            "excellent": result.is_excellent(),
            "dimensions": {
                "completeness": {
                    "score": result.completeness.score,
                    "findings": result.completeness.findings,
                },
                "clarity": {
                    "score": result.clarity.score,
                    "findings": result.clarity.findings,
                },
                "traceability": {
                    "score": result.traceability.score,
                    "findings": result.traceability.findings,
                },
                "constitutional": {
                    "score": result.constitutional.score,
                    "findings": result.constitutional.findings,
                },
                "ambiguity": {
                    "score": result.ambiguity.score,
                    "findings": result.ambiguity.findings,
                },
            },
            "recommendations": result.get_recommendations(),
        }
        console.print(json_lib.dumps(output, indent=2))
    else:
        # Rich table output
        show_banner()
        console.print(f"\n[bold]Quality Assessment:[/bold] {spec_file}\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Dimension", style="cyan", width=20)
        table.add_column("Score", justify="right", width=10)
        table.add_column("Findings", width=50)

        # Add dimension rows
        dimensions = [
            ("Completeness", result.completeness),
            ("Clarity", result.clarity),
            ("Traceability", result.traceability),
            ("Constitutional", result.constitutional),
            ("Ambiguity", result.ambiguity),
        ]

        for name, assessment in dimensions:
            score_str = f"{assessment.score:.0f}/100"
            findings_str = "\n".join(assessment.findings[:3])  # First 3 findings

            # Color code score
            if assessment.score >= 90:
                score_color = "green"
            elif assessment.score >= 70:
                score_color = "yellow"
            else:
                score_color = "red"

            table.add_row(
                name, f"[{score_color}]{score_str}[/{score_color}]", findings_str
            )

        # Add separator and overall
        table.add_section()

        overall_str = f"{result.overall_score:.0f}/100"
        if result.is_excellent():
            status = "[green]EXCELLENT ✓✓[/green]"
            overall_color = "green"
        elif result.passes():
            status = "[green]PASSING ✓[/green]"
            overall_color = "yellow"
        else:
            status = "[red]NEEDS IMPROVEMENT ✗[/red]"
            overall_color = "red"

        table.add_row(
            "[bold]OVERALL[/bold]",
            f"[bold {overall_color}]{overall_str}[/bold {overall_color}]",
            status,
        )

        console.print(table)

        # Show recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(result.get_recommendations(), 1):
            console.print(f"  {i}. {rec}")

        console.print()

    # Exit with status code if check-only
    if check_only:
        effective_threshold = (
            threshold if threshold is not None else config.passing_threshold
        )
        if not result.passes(threshold):
            console.print(
                f"[red]Quality check failed: {result.overall_score:.0f} < {effective_threshold}[/red]"
            )
            raise typer.Exit(1)
        else:
            console.print(
                f"[green]Quality check passed: {result.overall_score:.0f} >= {effective_threshold}[/green]"
            )
            raise typer.Exit(0)


@app.command()
def gate(
    threshold: int = typer.Option(
        None, "--threshold", help="Override minimum quality score (default: 70)"
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass gate even if quality check fails"
    ),
):
    """Pre-implementation quality gate.

    Validates spec quality before implementation begins.
    Exit codes: 0=passed, 1=failed, 2=error

    This command is designed to be run before starting implementation
    (e.g., in CI/CD pipelines or as part of /flow:implement workflow).

    Example usage:
        flowspec gate                    # Check with default threshold (70)
        flowspec gate --threshold 80     # Custom threshold
        flowspec gate --force            # Bypass failed gate (not recommended)
    """
    from pathlib import Path

    from flowspec_cli.quality import QualityConfig, QualityScorer

    project_root = Path.cwd()
    spec_path = project_root / "docs" / "prd" / "spec.md"

    if not spec_path.exists():
        console.print("[red]Error:[/red] No spec.md found at docs/prd/spec.md")
        raise typer.Exit(2)

    # Load config and override threshold if provided
    config = QualityConfig.find_config(project_root / ".flowspec")
    min_threshold = threshold if threshold is not None else config.passing_threshold

    console.print("🔍 Running pre-implementation quality gate...\n")

    # Run quality assessment
    try:
        scorer = QualityScorer(config)
        result = scorer.score_spec(spec_path)
    except Exception as e:
        console.print(f"[red]Error during quality assessment: {e}[/red]")
        raise typer.Exit(2)

    overall_score = result.overall_score
    passed = overall_score >= min_threshold

    # Display result
    if passed:
        console.print(
            f"Quality Score: [green]{overall_score:.0f}/100[/green] ✅ PASSED\n"
        )
        console.print("[green]Proceeding with implementation...[/green]")
        raise typer.Exit(0)
    else:
        console.print(
            f"Quality Score: [red]{overall_score:.0f}/100[/red] ❌ FAILED (minimum: {min_threshold})\n"
        )

        # Show top 5 recommendations
        recommendations = result.get_recommendations()
        if recommendations:
            console.print("[yellow]Recommendations:[/yellow]")
            for rec in recommendations[:5]:
                console.print(f"  • {rec}")
            console.print()

        if force:
            console.print(
                "[yellow]⚠️  Bypassing gate with --force (not recommended)[/yellow]"
            )
            raise typer.Exit(0)
        else:
            console.print("[dim]Run with --force to bypass (not recommended)[/dim]")
            raise typer.Exit(1)


@app.command(name="ac-coverage")
def ac_coverage_command(
    feature: str = typer.Option(
        None,
        "--feature",
        "-f",
        help="Feature name (defaults to current feature from context)",
    ),
    prd_path: str = typer.Option(
        None,
        "--prd",
        help="Path to PRD file (defaults to docs/prd/{feature}.md)",
    ),
    test_dirs: str = typer.Option(
        "tests",
        "--test-dirs",
        help="Comma-separated list of test directories",
    ),
    output: str = typer.Option(
        "tests/ac-coverage.json",
        "--output",
        "-o",
        help="Output path for coverage report",
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Check coverage and exit with error if not 100%",
    ),
    allow_partial_coverage: bool = typer.Option(
        False,
        "--allow-partial-coverage",
        help="Allow partial coverage (for exceptional cases)",
    ),
):
    """Generate acceptance criteria test coverage report.

    Scans PRD for acceptance criteria and checks that all have
    corresponding test markers (@pytest.mark.ac).

    Examples:
        flowspec ac-coverage --check
        flowspec ac-coverage --feature auth --output coverage.json
        flowspec ac-coverage --allow-partial-coverage
    """
    from pathlib import Path

    from flowspec_cli.workflow.ac_coverage import (
        generate_coverage_report,
        validate_ac_coverage,
    )

    # Determine feature name
    if not feature:
        from flowspec_cli.task_context import TaskContext

        try:
            context = TaskContext.detect()
            feature = context.feature_name
        except Exception:
            console.print(
                "[red]Error:[/red] Could not detect feature name. Use --feature option."
            )
            raise typer.Exit(1)

    # Determine PRD path
    if not prd_path:
        prd_path = f"docs/prd/{feature}.md"

    prd_file = Path(prd_path)
    if not prd_file.exists():
        console.print(f"[red]Error:[/red] PRD not found: {prd_path}")
        raise typer.Exit(1)

    # Parse test directories
    test_dir_list = [Path(d.strip()) for d in test_dirs.split(",")]

    # Generate coverage report
    console.print(f"[cyan]Scanning PRD:[/cyan] {prd_path}")
    console.print(
        f"[cyan]Test directories:[/cyan] {', '.join(str(d) for d in test_dir_list)}"
    )
    console.print()

    try:
        report = generate_coverage_report(
            feature=feature,
            prd_path=prd_file,
            test_dirs=test_dir_list,
        )
    except Exception as e:
        console.print(f"[red]Error generating coverage report:[/red] {e}")
        raise typer.Exit(1)

    # Save report
    output_path = Path(output)
    report.save(output_path)
    console.print(f"[green]✓[/green] Coverage report saved: {output_path}")
    console.print()

    # Display summary
    summary = report.summary
    console.print("[bold]Coverage Summary:[/bold]")
    console.print(f"  Total ACs: {summary.total_acs}")
    console.print(f"  Covered: {summary.covered}")
    console.print(f"  Uncovered: {summary.uncovered}")

    # Color code coverage percentage
    coverage_color = "green" if summary.coverage_percent >= 100.0 else "yellow"
    if summary.coverage_percent < 50.0:
        coverage_color = "red"

    console.print(
        f"  Coverage: [{coverage_color}]{summary.coverage_percent:.1f}%[/{coverage_color}]"
    )
    console.print()

    # Show uncovered ACs if any
    if summary.uncovered > 0:
        console.print("[yellow]Uncovered acceptance criteria:[/yellow]")
        for ac in report.get_uncovered_acs():
            console.print(f"  - [dim]{ac.id}:[/dim] {ac.description}")
        console.print()

        console.print("[dim]To fix:[/dim]")
        console.print('  1. Add @pytest.mark.ac("ACX: Description") to test functions')
        console.print("  2. Ensure tests are in configured test directories")
        console.print("  3. Run: flowspec ac-coverage --check")
        console.print()

    # Validate coverage if --check flag is set
    if check:
        is_valid, error_msg = validate_ac_coverage(report, allow_partial_coverage)
        if not is_valid:
            console.print("[red]✗ Coverage check failed[/red]")
            console.print()
            console.print(error_msg)
            raise typer.Exit(1)

        console.print("[green]✓ All acceptance criteria are covered by tests[/green]")


# Workflow subcommand
workflow_app = typer.Typer(
    name="workflow",
    help="Validate workflow configuration files",
    add_completion=False,
)
app.add_typer(workflow_app, name="workflow")

# Flow subcommand group for workflow orchestration commands
flow_app = typer.Typer(
    name="flow",
    help="Custom workflow orchestration commands",
    add_completion=False,
)
app.add_typer(flow_app, name="flow")


@flow_app.command("custom")
def flow_custom(
    workflow_name: str = typer.Argument(
        None, help="Name of custom workflow to execute"
    ),
    list_workflows: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List available custom workflows",
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        "-e",
        help="Actually execute the workflow (requires agent context or manual command execution)",
    ),
    task_id: str = typer.Option(
        None,
        "--task",
        "-t",
        help="Backlog task ID to update during execution",
    ),
) -> None:
    """Execute a custom workflow sequence from flowspec_workflow.yml.

    Examples:
        flowspec flow custom quick_build
        flowspec flow custom --list
        flowspec flow custom quick_build --execute
        flowspec flow custom quick_build --execute --task task-123
    """
    from datetime import datetime
    from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator

    workspace_root = Path.cwd()
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    try:
        orchestrator = WorkflowOrchestrator(workspace_root, session_id)
    except Exception as e:
        console.print(f"[red]✗ Error initializing orchestrator: {e}[/red]")
        raise typer.Exit(1)

    # List workflows if requested or no workflow specified
    if list_workflows or not workflow_name:
        workflows = orchestrator.list_custom_workflows()
        if not workflows:
            console.print(
                "[yellow]No custom workflows defined in flowspec_workflow.yml[/yellow]"
            )
            console.print("\nSee: docs/guides/custom-workflows.md")
            raise typer.Exit(0)

        console.print(f"[bold]Available custom workflows ({len(workflows)}):[/bold]\n")
        for wf_name in workflows:
            wf_def = orchestrator.custom_workflows[wf_name]
            console.print(f"  [cyan]{wf_name}[/cyan]")
            console.print(f"    Name: {wf_def.get('name', 'N/A')}")
            console.print(f"    Mode: {wf_def.get('mode', 'N/A')}")
            console.print(f"    Steps: {len(wf_def.get('steps', []))}")
            if "description" in wf_def:
                console.print(f"    Description: {wf_def['description']}")
            console.print()
        raise typer.Exit(0)

    # Execute the custom workflow
    try:
        # TODO: Load context (e.g., complexity from assess)
        context = {}

        console.print(f"[bold]Executing custom workflow: {workflow_name}[/bold]")
        result = orchestrator.execute_custom_workflow(workflow_name, context)

        if result.success:
            console.print(
                f"\n[green]✓ Custom workflow '{workflow_name}' execution plan prepared[/green]"
            )
            console.print(f"  Steps to execute: {result.steps_executed}")
            console.print(f"  Steps skipped: {result.steps_skipped}")

            # Update task: Starting
            if task_id:
                import subprocess

                try:
                    subprocess.run(
                        [
                            "backlog",
                            "task",
                            "edit",
                            task_id,
                            "--notes-append",
                            f"Starting workflow: {workflow_name} (session: {session_id})",
                        ],
                        check=True,
                        capture_output=True,
                    )
                    console.print(
                        f"\n[dim]Updated task {task_id}: Starting execution[/dim]"
                    )
                except subprocess.CalledProcessError as e:
                    console.print(
                        f"\n[yellow]Warning: Could not update task {task_id}: {e}[/yellow]"
                    )

            if execute:
                # Execute workflows
                console.print("\n[bold]Executing workflow steps:[/bold]")

                executed_count = 0
                failed_count = 0

                for i, step_result in enumerate(result.step_results, 1):
                    if step_result.skipped:
                        console.print(
                            f"  [{i}] [yellow]SKIPPED[/yellow]: {step_result.workflow_name}"
                        )
                        console.print(f"      Reason: {step_result.skip_reason}")
                        continue

                    if not step_result.command:
                        console.print(
                            f"  [{i}] [red]ERROR[/red]: No command for {step_result.workflow_name}"
                        )
                        failed_count += 1
                        continue

                    console.print(f"\n  [{i}] [cyan]{step_result.command}[/cyan]")
                    console.print(f"      Workflow: {step_result.workflow_name}")

                    # NOTE: /flow commands are agent commands (Skill tool invocations)
                    # They cannot be executed from CLI subprocess
                    # For actual execution, user must run in Claude Code agent context
                    console.print(
                        "      [yellow]⚠ Agent command - cannot execute from CLI subprocess[/yellow]"
                    )
                    console.print(
                        "      [dim]To execute: Ask Claude Code to run this workflow[/dim]"
                    )
                    console.print(
                        f"      [dim]Claude Code command: execute workflow '{workflow_name}'[/dim]"
                    )

                    # Update task for this step
                    if task_id:
                        try:
                            subprocess.run(
                                [
                                    "backlog",
                                    "task",
                                    "edit",
                                    task_id,
                                    "--notes-append",
                                    f"Prepared: {step_result.workflow_name} ({step_result.command})",
                                ],
                                check=True,
                                capture_output=True,
                            )
                        except subprocess.CalledProcessError:
                            pass  # Silently continue if task update fails

                    executed_count += 1

                console.print("\n[bold]Execution Summary:[/bold]")
                console.print(f"  Prepared for execution: {executed_count}")
                console.print(f"  Failed: {failed_count}")

                # Update task: Complete preparation
                if task_id:
                    try:
                        subprocess.run(
                            [
                                "backlog",
                                "task",
                                "edit",
                                task_id,
                                "--notes-append",
                                f"Workflow {workflow_name} execution plan prepared. Run in agent context to execute.",
                            ],
                            check=True,
                            capture_output=True,
                        )
                        console.print(
                            f"\n[dim]Updated task {task_id}: Execution plan complete[/dim]"
                        )
                    except subprocess.CalledProcessError:
                        pass

                console.print(
                    "\n[yellow]NOTE:[/yellow] Workflow commands prepared but not executed from CLI."
                )
                console.print(
                    "[yellow]Reason:[/yellow] CLI runs in subprocess without access to Claude Code Skill tool."
                )
                console.print("\n[bold]To actually execute this workflow:[/bold]")
                console.print(
                    "  1. Open Claude Code (claude.ai/code or VS Code with Claude)"
                )
                console.print(f"  2. Say: \"execute workflow '{workflow_name}'\"")
                console.print(
                    "  3. Claude Code will use agent_executor module to run each step"
                )
                console.print(
                    "\n[dim]OR manually invoke each Skill command shown above in Claude Code[/dim]"
                )

            else:
                # Display commands only (no execution)
                console.print("\n[bold]Workflow execution steps:[/bold]")
                for i, step_result in enumerate(result.step_results, 1):
                    if step_result.skipped:
                        console.print(
                            f"  [{i}] [yellow]SKIPPED[/yellow]: {step_result.workflow_name}"
                        )
                        console.print(f"      Reason: {step_result.skip_reason}")
                    elif step_result.command:
                        console.print(f"  [{i}] [cyan]{step_result.command}[/cyan]")
                        console.print(f"      Workflow: {step_result.workflow_name}")
                    else:
                        console.print(
                            f"  [{i}] [red]ERROR[/red]: No command for {step_result.workflow_name}"
                        )

                console.print(
                    "\n[yellow]NOTE:[/yellow] Add --execute flag to run workflow preparation"
                )
                console.print(
                    "[yellow]NOTE:[/yellow] In Claude Code, use the Skill tool to execute each command above."
                )

            console.print(
                f"\n[dim]Decision log: .logs/decisions/session-{session_id}.jsonl[/dim]"
            )
            console.print(
                f"[dim]Event log: .logs/events/session-{session_id}.jsonl[/dim]"
            )
        else:
            console.print(f"\n[red]✗ Custom workflow '{workflow_name}' failed[/red]")
            console.print(f"  Error: {result.error}")
            console.print(f"  Steps completed: {result.steps_executed}")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        console.print("\n[bold]Available workflows:[/bold]")
        for wf_name in orchestrator.list_custom_workflows():
            console.print(f"  - {wf_name}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1)


# Config subcommand group for managing configuration
config_app = typer.Typer(
    name="config",
    help="Manage Specify configuration",
    add_completion=False,
)
app.add_typer(config_app, name="config")


@config_app.command("validation")
def config_validation(
    show: bool = typer.Option(
        False,
        "--show",
        help="Show current validation configuration",
    ),
    transition: str = typer.Option(
        None,
        "--transition",
        "-t",
        help="Transition to update (assess, specify, research, plan, implement, validate, operate)",
    ),
    mode: str = typer.Option(
        None,
        "--mode",
        "-m",
        help="Validation mode: none, keyword, or pull-request",
    ),
    keyword: str = typer.Option(
        "APPROVED",
        "--keyword",
        "-k",
        help="Approval keyword for KEYWORD mode (default: APPROVED)",
    ),
) -> None:
    """View or update workflow transition validation configuration.

    Examples:
        flowspec config validation --show
        flowspec config validation -t plan -m pull-request
        flowspec config validation -t specify -m keyword -k PRD_APPROVED
    """

    workflow_path = Path.cwd() / "flowspec_workflow.yml"

    if not workflow_path.exists():
        console.print(
            "[red]Error:[/red] No flowspec_workflow.yml found in current directory"
        )
        console.print("[dim]Run 'flowspec init' first to create a project[/dim]")
        raise typer.Exit(1)

    # Load current config
    with workflow_path.open() as f:
        config = yaml.safe_load(f)

    transitions = config.get("transitions", [])
    valid_transitions = {t["name"] for t in transitions}

    # Default behavior: show configuration
    if not transition and not mode:
        show = True

    # Show current configuration
    if show:
        console.print()
        console.print("[cyan]== Validation Configuration ==[/cyan]")
        console.print()

        for t in transitions:
            name = t["name"]
            validation = t.get("validation", "NONE")

            # Color code based on mode
            if validation == "NONE":
                mode_display = "[green]NONE[/green]"
            elif validation.startswith("KEYWORD"):
                mode_display = f"[yellow]{validation}[/yellow]"
            elif validation == "PULL_REQUEST":
                mode_display = "[blue]PULL_REQUEST[/blue]"
            else:
                mode_display = validation

            from_state = t.get("from", "?")
            to_state = t.get("to", "?")
            console.print(
                f"  [cyan]{name:12}[/cyan] {from_state} → {to_state}: {mode_display}"
            )

        console.print()
        return

    # Validate update parameters
    if transition and not mode:
        console.print(
            "[red]Error:[/red] --mode is required when --transition is specified"
        )
        raise typer.Exit(1)

    if mode and not transition:
        console.print(
            "[red]Error:[/red] --transition is required when --mode is specified"
        )
        raise typer.Exit(1)

    # Validate transition name
    if transition not in valid_transitions:
        console.print(f"[red]Error:[/red] Unknown transition '{transition}'")
        console.print(
            f"[dim]Valid transitions: {', '.join(sorted(valid_transitions))}[/dim]"
        )
        raise typer.Exit(1)

    # Validate mode
    valid_modes = {"none", "keyword", "pull-request"}
    if mode.lower() not in valid_modes:
        console.print(f"[red]Error:[/red] Invalid mode '{mode}'")
        console.print(f"[dim]Valid modes: {', '.join(valid_modes)}[/dim]")
        raise typer.Exit(1)

    # Format the mode for YAML
    if mode.lower() == "none":
        formatted_mode = "NONE"
    elif mode.lower() == "keyword":
        formatted_mode = f'KEYWORD["{keyword}"]'
    else:
        formatted_mode = "PULL_REQUEST"

    # Update the transition
    for t in transitions:
        if t["name"] == transition:
            t["validation"] = formatted_mode
            break

    # Write back to file
    with workflow_path.open("w") as f:
        # Write header comments
        f.write("# Flowspec Workflow Configuration\n")
        f.write('version: "1.0"\n\n')
        f.write("transitions:\n")

        for t in transitions:
            f.write(f"  - name: {t['name']}\n")
            f.write(f'    from: "{t["from"]}"\n')
            f.write(f'    to: "{t["to"]}"\n')
            f.write(f"    validation: {t['validation']}\n\n")

    console.print(f"[green]Updated[/green] {transition} → {formatted_mode}")


# Hooks app (event emission and hook management)
from flowspec_cli.hooks.cli import hooks_app  # noqa: E402

app.add_typer(hooks_app, name="hooks")

# Memory CLI (task memory management)
from flowspec_cli.memory.cli import memory_app  # noqa: E402

app.add_typer(memory_app, name="memory")


# VS Code integration sub-app
vscode_app = typer.Typer(
    name="vscode",
    help="VS Code integration commands",
    add_completion=False,
)
app.add_typer(vscode_app, name="vscode")

# Telemetry sub-app
app.add_typer(telemetry_app, name="telemetry")


@vscode_app.command("generate")
def vscode_generate(
    role: Optional[str] = typer.Option(
        None,
        "--role",
        "-r",
        help="Role to generate settings for (overrides workflow config)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for settings.json (default: .vscode/settings.json)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force overwrite existing settings without merging",
    ),
    no_merge: bool = typer.Option(
        False,
        "--no-merge",
        help="Don't merge with existing settings",
    ),
) -> None:
    """Generate VS Code settings for role-based agent pinning.

    This command generates .vscode/settings.json with role-appropriate
    GitHub Copilot agent configuration. Agents for your selected role
    will be pinned to the top of suggestions.

    Examples:
        flowspec vscode generate                    # Use primary role from config
        flowspec vscode generate --role dev         # Generate for dev role
        flowspec vscode generate --force            # Overwrite without merging
        flowspec vscode generate -o custom.json     # Custom output path
    """
    from flowspec_cli.vscode.settings_generator import VSCodeSettingsGenerator
    from flowspec_cli.workflow.config import WorkflowConfig
    from flowspec_cli.workflow.exceptions import WorkflowConfigError

    # Load workflow config
    try:
        config = WorkflowConfig.load()
    except WorkflowConfigError as e:
        console.print(f"[red]Error loading workflow config:[/red] {e}")
        console.print("[dim]Run 'flowspec init' to create workflow configuration[/dim]")
        raise typer.Exit(1)

    # Determine output path
    if output is None:
        output = VSCodeSettingsGenerator.get_default_settings_path()

    # Create generator
    generator = VSCodeSettingsGenerator(workflow_config=config, primary_role=role)

    # Determine role for display
    try:
        display_role = generator.primary_role
    except WorkflowConfigError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Generate settings
    console.print()
    console.print(f"[cyan]Generating VS Code settings for role:[/cyan] {display_role}")
    console.print(f"[cyan]Output path:[/cyan] {output}")
    console.print()

    try:
        merge_existing = not no_merge
        result_path = generator.write_settings(
            output,
            role=role,
            force=force,
            merge_existing=merge_existing,
        )

        # Show success message
        console.print(f"[green]✓[/green] Settings generated: {result_path}")
        console.print()

        # Show pinned agents
        settings = generator.generate(role=role, merge_existing=False)
        pinned_agents = settings["github.copilot.chat.agents"]["pinnedAgents"]

        console.print("[cyan]Pinned agents (top priority):[/cyan]")
        for agent in pinned_agents:
            console.print(f"  • {agent}")

        console.print()
        console.print(
            "[dim]These agents will appear first in VS Code Copilot suggestions.[/dim]"
        )

    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print(
            "[dim]Use --force to overwrite or --no-merge to replace entirely[/dim]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error generating settings:[/red] {e}")
        raise typer.Exit(1)


# Security scanning sub-app
security_app = typer.Typer(
    name="security",
    help="Security scanning commands",
    add_completion=False,
)
app.add_typer(security_app, name="security")


@security_app.command("scan")
def security_scan(
    target: Path = typer.Argument(
        Path("."),
        help="Directory or file to scan",
        exists=True,
    ),
    tool: list[str] = typer.Option(
        ["semgrep"],
        "--tool",
        "-t",
        help="Scanner(s) to use (semgrep, etc)",
    ),
    config: str = typer.Option(
        "auto",
        "--config",
        "-c",
        help="Scanner config to use",
    ),
    fail_on: str = typer.Option(
        "high",
        "--fail-on",
        help="Fail on severity threshold (critical|high|medium|low|info)",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text|json|sarif)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (defaults to stdout)",
    ),
):
    """Run security scan on target directory.

    This command scans your code for security vulnerabilities using
    configured security scanners (e.g., Semgrep).

    Exit codes:
    - 0: No findings at or above fail-on threshold
    - 1: Findings found at or above fail-on threshold
    - 2: Error during scan

    Examples:
        flowspec security scan                           # Scan current directory
        flowspec security scan /path/to/code             # Scan specific path
        flowspec security scan --tool semgrep            # Specify scanner
        flowspec security scan --fail-on critical        # Fail only on critical
        flowspec security scan --format json -o out.json # JSON output to file
    """

    from flowspec_cli.security.adapters.semgrep import SemgrepAdapter
    from flowspec_cli.security.exporters.json import JSONExporter
    from flowspec_cli.security.exporters.markdown import MarkdownExporter
    from flowspec_cli.security.exporters.sarif import SARIFExporter
    from flowspec_cli.security.models import Severity
    from flowspec_cli.security.orchestrator import ScannerOrchestrator

    # Validate fail-on severity
    try:
        fail_severity = Severity(fail_on.lower())
    except ValueError:
        console.print(
            f"[red]Invalid severity level: {fail_on}[/red]",
        )
        console.print(
            "Valid levels: critical, high, medium, low, info",
        )
        raise typer.Exit(2)

    # Initialize orchestrator
    orchestrator = ScannerOrchestrator()

    # Register scanners based on --tool flags
    scanner_map = {
        "semgrep": SemgrepAdapter,
    }

    for tool_name in tool:
        if tool_name not in scanner_map:
            console.print(
                f"[yellow]⚠ Unknown scanner: {tool_name}[/yellow]",
            )
            continue

        adapter_class = scanner_map[tool_name]
        adapter = adapter_class()

        # Check tool availability
        if not adapter.is_available():
            console.print(
                f"[yellow]⚠ {adapter.name} not available[/yellow]",
            )
            console.print(adapter.get_install_instructions())
            raise typer.Exit(2)

        orchestrator.register(adapter)

    if not orchestrator.list_scanners():
        console.print("[red]No scanners available[/red]")
        raise typer.Exit(2)

    # Build scanner config
    scanner_config = {}
    if config != "auto":
        # Parse config as JSON or file path
        try:
            scanner_config = json.loads(config)
        except json.JSONDecodeError:
            # Try as file path
            config_path = Path(config)
            if config_path.exists():
                scanner_config = json.loads(config_path.read_text())
            else:
                console.print(f"[red]Invalid config: {config}[/red]")
                raise typer.Exit(2)

    # Run scan with progress indicator
    try:
        with console.status(
            "[bold blue]Scanning for security vulnerabilities...[/bold blue]"
        ):
            findings = orchestrator.scan(
                target=target,
                scanners=tool,
                deduplicate=True,
                config=scanner_config,
            )
    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")
        raise typer.Exit(2)

    # Output results based on format
    if format == "sarif":
        exporter = SARIFExporter()
        result = exporter.export(findings)  # Returns dict
        output_text = json.dumps(result, indent=2)

        if output:
            output.write_text(output_text)
            console.print(f"[green]✓ SARIF output written to {output}[/green]")
        else:
            console.print_json(data=result)

    elif format == "json":
        exporter = JSONExporter(pretty=True)
        result = exporter.export_dict(findings)  # Returns dict
        output_text = json.dumps(result, indent=2)

        if output:
            output.write_text(output_text)
            console.print(f"[green]✓ JSON output written to {output}[/green]")
        else:
            console.print_json(data=result)

    else:
        # Text format with table
        _print_findings_table(console, findings)

        if output:
            # Export as markdown for text format
            exporter = MarkdownExporter()
            markdown = exporter.export(findings)
            output.write_text(markdown)
            console.print(f"\n[green]✓ Markdown report written to {output}[/green]")

    # Determine exit code based on fail_on threshold
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }

    has_failures = any(
        severity_order[f.severity] <= severity_order[fail_severity] for f in findings
    )

    if has_failures:
        failing_count = sum(
            1
            for f in findings
            if severity_order[f.severity] <= severity_order[fail_severity]
        )
        console.print(
            f"\n[red]✗ Found {failing_count} findings at or above {fail_on} severity[/red]"
        )
        raise typer.Exit(1)
    elif findings:
        console.print(
            f"\n[yellow]Found {len(findings)} findings below {fail_on} threshold[/yellow]"
        )
        raise typer.Exit(0)
    else:
        console.print("\n[green]✓ No security issues found[/green]")
        raise typer.Exit(0)


def _print_findings_table(console: Console, findings: list) -> None:
    """Print findings as a rich table.

    Args:
        console: Rich console for output
        findings: List of Finding objects to display
    """
    if not findings:
        console.print("[green]✓ No security issues found[/green]")
        return

    from rich.table import Table

    table = Table(title="Security Findings", show_lines=False)
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Title", style="", width=40)
    table.add_column("Location", style="cyan", width=30)
    table.add_column("CWE", style="dim", width=10)

    severity_colors = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "blue",
        "info": "dim",
    }

    for f in findings:
        color = severity_colors.get(f.severity.value, "white")
        title_text = f.title[:40] + "..." if len(f.title) > 40 else f.title
        location_text = f"{f.location.file.name}:{f.location.line_start}"

        table.add_row(
            f"[{color}]{f.severity.value.upper()}[/{color}]",
            title_text,
            location_text,
            f.cwe_id or "-",
        )

    console.print()
    console.print(table)
    console.print(f"\nTotal: {len(findings)} findings")


@security_app.command("triage")
def security_triage(
    findings_file: Path = typer.Argument(
        ...,
        help="Findings JSON file to triage",
        exists=True,
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Interactive triage mode",
    ),
    min_severity: str = typer.Option(
        "low",
        "--min-severity",
        help="Minimum severity to show (critical|high|medium|low|info)",
    ),
):
    """AI-assisted triage of security findings.

    This command helps you triage security findings with AI assistance.
    (Currently a placeholder for future implementation)

    Examples:
        flowspec security triage findings.json
        flowspec security triage findings.json --min-severity high
    """
    console.print("[yellow]Triage command coming in Phase 2[/yellow]")
    console.print(f"Would triage: {findings_file}")
    console.print(f"Interactive: {interactive}, Min severity: {min_severity}")


@security_app.command("fix")
def security_fix(
    finding_id: Optional[str] = typer.Argument(
        None,
        help="Finding ID to fix",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Apply fix automatically",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run",
        help="Show fix without applying",
    ),
):
    """Generate and optionally apply security fixes.

    This command generates fixes for security findings with AI assistance.
    (Currently a placeholder for future implementation)

    Examples:
        flowspec security fix SEMGREP-001 --dry-run
        flowspec security fix SEMGREP-001 --apply
    """
    console.print("[yellow]Fix command coming in Phase 2[/yellow]")
    if finding_id:
        console.print(f"Would fix: {finding_id}")
        console.print(f"Apply: {apply}, Dry run: {dry_run}")
    else:
        console.print("No finding ID provided")


@security_app.command("audit")
def security_audit(
    target: Path = typer.Argument(
        Path("."),
        help="Directory to audit",
        exists=True,
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Report format (markdown|html|json)",
    ),
    compliance: Optional[str] = typer.Option(
        None,
        "--compliance",
        help="Compliance framework (owasp|pci|hipaa)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file",
    ),
):
    """Generate security audit report.

    This command generates a comprehensive security audit report.
    (Currently a placeholder for future implementation)

    Examples:
        flowspec security audit
        flowspec security audit --format html --output audit.html
        flowspec security audit --compliance owasp
    """
    console.print("[yellow]Audit command coming in Phase 2[/yellow]")
    console.print(f"Would audit: {target}")
    console.print(f"Format: {format}, Compliance: {compliance}")
    if output:
        console.print(f"Output: {output}")


# Constitution management sub-app
constitution_app = typer.Typer(
    name="constitution",
    help="Constitution management commands",
    add_completion=False,
)
app.add_typer(constitution_app, name="constitution")


@constitution_app.command("validate")
def constitution_validate_cmd(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to constitution file (defaults to memory/constitution.md)",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Show detailed validation output",
    ),
):
    """Validate constitution for NEEDS_VALIDATION markers.

    Scans your constitution file for NEEDS_VALIDATION markers that indicate
    sections requiring customization. A fully validated constitution has no
    markers remaining.

    Exit codes:
    - 0: Validation passed (no markers found)
    - 1: Validation failed (markers found or file not found)

    Examples:
        flowspec constitution validate                 # Validate default location
        flowspec constitution validate --path my.md    # Validate custom file
        flowspec constitution validate --verbose       # Show detailed output
    """
    show_banner()

    # Determine constitution path
    constitution_path = path or Path.cwd() / "memory" / "constitution.md"

    if not constitution_path.exists():
        console.print(
            f"[red]Error:[/red] Constitution not found at {constitution_path}"
        )
        console.print("[yellow]Tip:[/yellow] Run 'flowspec init --here' to create one")
        raise typer.Exit(1)

    # Read constitution content
    content = constitution_path.read_text()

    # Find NEEDS_VALIDATION markers
    import re

    pattern = r"<!-- NEEDS_VALIDATION: (.+?) -->"
    markers = re.findall(pattern, content)

    if not markers:
        # Success: no markers found
        panel = Panel(
            "[green]✓ Constitution is fully validated[/green]\n\n"
            "No NEEDS_VALIDATION markers found. Your constitution is ready to use.",
            title="[green]Validation Passed[/green]",
            border_style="green",
        )
        console.print(panel)
        raise typer.Exit(0)

    # Failure: markers found
    console.print(
        f"\n[yellow]Found {len(markers)} section(s) requiring validation:[/yellow]\n"
    )
    for i, marker in enumerate(markers, 1):
        console.print(f"  {i}. [cyan]{marker}[/cyan]")

    if verbose:
        console.print(
            f"\n[dim]Constitution location:[/dim] [cyan]{constitution_path}[/cyan]"
        )

    console.print()
    panel = Panel(
        "1. Review each section listed above in your constitution\n"
        "2. Update placeholder values to match your project\n"
        "3. Remove the NEEDS_VALIDATION comment when complete\n\n"
        "[dim]Example:[/dim]\n"
        "[dim]<!-- NEEDS_VALIDATION: Update team size -->[/dim]\n"
        "[dim]Team size: 5 engineers  [strike](was: [Your team size])[/strike][/dim]\n"
        "[dim][strike]<!-- NEEDS_VALIDATION: Update team size -->[/strike][/dim]",
        title="[yellow]Action Required[/yellow]",
        border_style="yellow",
    )
    console.print(panel)
    raise typer.Exit(1)


@constitution_app.command("version")
def constitution_version_cmd(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to constitution file (default: memory/constitution.md)",
    ),
) -> None:
    """Show constitution version information."""
    import re

    show_banner()

    constitution_path = path or Path.cwd() / "memory" / "constitution.md"

    if not constitution_path.exists():
        console.print(
            f"[red]Error:[/red] Constitution not found at {constitution_path}"
        )
        console.print("\n[yellow]Run 'flowspec init --here' to create one[/yellow]")
        raise typer.Exit(1)

    content = constitution_path.read_text()

    # Extract version information
    version_match = re.search(r"\*\*Version\*\*:\s*(\S+)", content)
    ratified_match = re.search(r"\*\*Ratified\*\*:\s*(.+?)(?:\n|$)", content)
    amended_match = re.search(r"\*\*Last Amended\*\*:\s*(.+?)(?:\n|$)", content)

    # Detect tier from comment
    tier = "Medium"
    if "<!-- TIER: Light" in content:
        tier = "Light"
    elif "<!-- TIER: Heavy" in content:
        tier = "Heavy"

    # Build version info table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Version", version_match.group(1) if version_match else "Unknown")
    table.add_row("Tier", tier)
    table.add_row(
        "Ratified", ratified_match.group(1).strip() if ratified_match else "Unknown"
    )
    table.add_row(
        "Last Amended", amended_match.group(1).strip() if amended_match else "Unknown"
    )
    table.add_row("Template Version", CONSTITUTION_VERSION)

    console.print(Panel(table, title="[cyan]Constitution Version[/cyan]"))

    # Check for upgrade available
    if version_match and version_match.group(1) != CONSTITUTION_VERSION:
        console.print(
            f"\n[yellow]⚠  Template version {CONSTITUTION_VERSION} is available[/yellow]"
        )
        console.print(
            "[dim]Consider reviewing template updates at templates/constitutions/[/dim]"
        )


@constitution_app.command("diff")
def constitution_diff(
    tier: str = typer.Option(
        "medium",
        "--tier",
        "-t",
        help="Constitution tier to compare against (light|medium|heavy)",
    ),
    project_path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Project path to check",
        exists=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed diff output",
    ),
):
    """Compare project constitution against template.

    This command compares your project's memory/constitution.md
    against the specified tier template to identify customizations
    and differences.

    Examples:
        flowspec constitution diff
        flowspec constitution diff --tier heavy
        flowspec constitution diff --tier light --verbose
        flowspec constitution diff --path /path/to/project
    """
    from difflib import unified_diff

    # Validate tier
    if tier not in CONSTITUTION_TIER_CHOICES:
        console.print(
            f"[red]Error:[/red] Invalid tier '{tier}'. "
            f"Choose from: {', '.join(CONSTITUTION_TIER_CHOICES.keys())}"
        )
        raise typer.Exit(1)

    # Check if project has a constitution
    constitution_path = project_path / "memory" / "constitution.md"
    if not constitution_path.exists():
        console.print(f"[red]Error:[/red] No constitution found at {constitution_path}")
        console.print("\nTo initialize a constitution, run:")
        console.print(f"  flowspec init --here --constitution {tier}")
        raise typer.Exit(1)

    # Get template content from file (not embedded templates)
    # Templates are in project root: flowspec/templates/
    # __file__ is at: flowspec/src/flowspec_cli/__init__.py
    templates_dir = Path(__file__).parent.parent.parent / "templates" / "constitutions"
    template_file = templates_dir / f"constitution-{tier}.md"

    if not template_file.exists():
        console.print(
            f"[red]Error:[/red] Template for tier '{tier}' not found at {template_file}"
        )
        raise typer.Exit(1)

    template_content = template_file.read_text()

    # Read project constitution
    project_content = constitution_path.read_text()

    # Generate diff
    template_lines = template_content.splitlines(keepends=True)
    project_lines = project_content.splitlines(keepends=True)

    diff_lines = list(
        unified_diff(
            template_lines,
            project_lines,
            fromfile=f"template ({tier})",
            tofile="project constitution",
            lineterm="",
        )
    )

    if not diff_lines:
        console.print(
            f"[green]✓[/green] Project constitution matches {tier} tier template"
        )
        raise typer.Exit(0)

    # Display results
    console.print(f"[cyan]Constitution diff:[/cyan] {tier} tier template vs project\n")

    if verbose:
        # Show full unified diff
        for line in diff_lines:
            if line.startswith("---") or line.startswith("+++"):
                console.print(f"[bold]{line}[/bold]")
            elif line.startswith("@@"):
                console.print(f"[cyan]{line}[/cyan]")
            elif line.startswith("-"):
                console.print(f"[red]{line}[/red]")
            elif line.startswith("+"):
                console.print(f"[green]{line}[/green]")
            else:
                console.print(line)
    else:
        # Show summary
        additions = sum(
            1
            for line in diff_lines
            if line.startswith("+") and not line.startswith("+++")
        )
        deletions = sum(
            1
            for line in diff_lines
            if line.startswith("-") and not line.startswith("---")
        )

        console.print(
            f"[green]+{additions}[/green] additions, [red]-{deletions}[/red] deletions"
        )
        console.print("\nRun with --verbose to see full diff")

    console.print(
        "\n[dim]Tip: Use 'flowspec constitution merge' to update from template[/dim]"
    )
    raise typer.Exit(1)  # Exit with error code when differences exist


@constitution_app.command("merge")
def constitution_merge(
    tier: str = typer.Option(
        "medium",
        "--tier",
        "-t",
        help="Constitution tier to merge from (light|medium|heavy)",
    ),
    project_path: Path = typer.Option(
        Path("."),
        "--path",
        "-p",
        help="Project path",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: memory/constitution.merged.md)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show merge preview without writing file",
    ),
):
    """Merge template updates into project constitution.

    This command creates a merged constitution file that:
    1. Preserves your customized sections (marked with SECTION markers)
    2. Updates non-customized sections from the template
    3. Adds new sections from the template

    The merged file is written to memory/constitution.merged.md by default.
    Review the merged file before replacing your constitution.

    Examples:
        flowspec constitution merge
        flowspec constitution merge --tier heavy
        flowspec constitution merge --dry-run
        flowspec constitution merge --output /tmp/constitution.md
    """
    import re

    # Validate tier
    if tier not in CONSTITUTION_TIER_CHOICES:
        console.print(
            f"[red]Error:[/red] Invalid tier '{tier}'. "
            f"Choose from: {', '.join(CONSTITUTION_TIER_CHOICES.keys())}"
        )
        raise typer.Exit(1)

    # Check if project has a constitution
    constitution_path = project_path / "memory" / "constitution.md"
    if not constitution_path.exists():
        console.print(f"[red]Error:[/red] No constitution found at {constitution_path}")
        console.print("\nTo initialize a constitution, run:")
        console.print(f"  flowspec init --here --constitution {tier}")
        raise typer.Exit(1)

    # Get template content from file
    # Templates are in project root: flowspec/templates/
    # __file__ is at: flowspec/src/flowspec_cli/__init__.py
    templates_dir = Path(__file__).parent.parent.parent / "templates" / "constitutions"
    template_file = templates_dir / f"constitution-{tier}.md"

    if not template_file.exists():
        console.print(
            f"[red]Error:[/red] Template for tier '{tier}' not found at {template_file}"
        )
        raise typer.Exit(1)

    template_content = template_file.read_text()

    # Read project constitution
    project_content = constitution_path.read_text()

    # Extract customized sections from project
    section_pattern = re.compile(
        r"<!-- SECTION:(\w+):BEGIN -->(.*?)<!-- SECTION:\1:END -->",
        re.DOTALL,
    )

    customized_sections = {}
    for match in section_pattern.finditer(project_content):
        section_name = match.group(1)
        section_content = match.group(2)
        customized_sections[section_name] = section_content

    # Merge: Replace sections in template with customized versions
    merged_content = template_content
    for section_name, custom_content in customized_sections.items():
        # Find and replace the section in template
        section_regex = re.compile(
            rf"(<!-- SECTION:{section_name}:BEGIN -->).*?(<!-- SECTION:{section_name}:END -->)",
            re.DOTALL,
        )
        if section_regex.search(merged_content):
            merged_content = section_regex.sub(
                rf"\1{custom_content}\2",
                merged_content,
            )

    # Determine output path
    if output is None:
        output = project_path / "memory" / "constitution.merged.md"

    # Display merge info
    console.print(f"[cyan]Merging constitution:[/cyan] {tier} tier template")
    console.print(f"[cyan]Project:[/cyan] {constitution_path}")
    console.print(f"[cyan]Output:[/cyan] {output}")
    console.print()

    if customized_sections:
        console.print(
            f"[green]✓[/green] Preserved {len(customized_sections)} customized sections:"
        )
        for section_name in customized_sections:
            console.print(f"  - {section_name}")
        console.print()

    if dry_run:
        console.print("[yellow]Dry run - no files written[/yellow]")
        console.print("\n[dim]Merged content preview:[/dim]\n")
        console.print(merged_content[:500] + "...")
        raise typer.Exit(0)

    # Write merged file
    output.write_text(merged_content)
    console.print(f"[green]✓[/green] Merged constitution written to {output}")
    console.print()
    console.print("[yellow]Next steps:[/yellow]")
    console.print("1. Review the merged file:")
    console.print(f"   cat {output}")
    console.print("2. If satisfied, replace your constitution:")
    console.print(f"   mv {output} {constitution_path}")


@workflow_app.command("validate")
def workflow_validate(
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to workflow config file (defaults to flowspec_workflow.yml or flowspec_workflow.yml in standard locations)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation output",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format (for CI/automation)",
    ),
):
    """Validate workflow configuration file.

    Validates flowspec_workflow.yml (v2.0+) or flowspec_workflow.yml (v1.x) against:
    1. JSON schema (structural validation)
    2. Semantic validation (circular dependencies, reachability, etc.)

    Exit codes:
    - 0: Validation passed (warnings are non-blocking)
    - 1: Validation errors (schema or semantic)
    - 2: File errors (not found, invalid YAML)

    Examples:
        flowspec workflow validate                    # Validate default config
        flowspec workflow validate --file custom.yml  # Validate custom config
        flowspec workflow validate --verbose          # Show detailed output
        flowspec workflow validate --json             # JSON output for CI
    """
    from pathlib import Path

    from flowspec_cli.workflow.config import WorkflowConfig
    from flowspec_cli.workflow.exceptions import (
        WorkflowConfigError,
        WorkflowConfigNotFoundError,
        WorkflowConfigValidationError,
    )
    from flowspec_cli.workflow.validator import WorkflowValidator

    # Track results for JSON output
    json_result = {
        "valid": False,
        "config_file": None,
        "schema_validation": {"passed": False, "error": None},
        "semantic_validation": {"passed": False, "errors": [], "warnings": []},
    }

    # Human-readable output (unless --json)
    if not json_output:
        console.print("[cyan]Validating workflow configuration...[/cyan]\n")

    # Load and validate config
    try:
        if file:
            config = WorkflowConfig.load(path=Path(file), validate=True, cache=False)
        else:
            config = WorkflowConfig.load(validate=True, cache=False)

        json_result["config_file"] = str(config.config_path)
        json_result["schema_validation"]["passed"] = True

        if not json_output:
            console.print("[green]✓[/green] Schema validation passed")
            if verbose:
                console.print(f"  Config file: {config.config_path}")
                console.print(f"  Version: {config.version}")
                console.print(f"  States: {len(config.states)}")
                console.print(f"  Workflows: {len(config.workflows)}")
                console.print()

    except WorkflowConfigNotFoundError as e:
        json_result["schema_validation"]["error"] = {
            "type": "file_not_found",
            "message": e.message,
            "path": e.path,
            "searched_paths": e.searched_paths,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Config file not found:[/red] {e.path}")
            if e.searched_paths:
                console.print("[dim]Searched paths:[/dim]")
                for path in e.searched_paths:
                    console.print(f"  [dim]- {path}[/dim]")
        raise typer.Exit(2)

    except WorkflowConfigValidationError as e:
        json_result["schema_validation"]["error"] = {
            "type": "schema_validation",
            "message": e.message,
            "errors": e.errors,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Schema validation failed:[/red] {e.message}")
            if e.errors:
                for err in e.errors:
                    console.print(f"  [red]•[/red] {err}")
        raise typer.Exit(1)

    except WorkflowConfigError as e:
        json_result["schema_validation"]["error"] = {
            "type": "config_error",
            "message": str(e),
            "details": e.details,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Config error:[/red] {e}")
        raise typer.Exit(2)

    except Exception as e:
        json_result["schema_validation"]["error"] = {
            "type": "unexpected_error",
            "message": str(e),
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Unexpected error:[/red] {e}")
        raise typer.Exit(2)

    # Run semantic validation
    if not json_output:
        console.print("[cyan]Running semantic validation...[/cyan]\n")

    validator = WorkflowValidator(config._data)
    result = validator.validate()

    # Populate JSON result with semantic validation data
    json_result["semantic_validation"]["passed"] = result.is_valid
    json_result["semantic_validation"]["errors"] = [
        {"code": e.code, "message": e.message, "context": e.context}
        for e in result.errors
    ]
    json_result["semantic_validation"]["warnings"] = [
        {"code": w.code, "message": w.message, "context": w.context}
        for w in result.warnings
    ]
    json_result["valid"] = result.is_valid

    # JSON output mode (use print() to avoid Rich formatting)
    if json_output:
        print(json.dumps(json_result, indent=2))
        raise typer.Exit(0 if result.is_valid else 1)

    # Human-readable output
    if result.is_valid:
        console.print(
            "[bold green]✓ Validation passed: workflow configuration is valid[/bold green]"
        )

        if verbose and result.warnings:
            console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning.message}")

        raise typer.Exit(0)
    else:
        console.print(
            f"[bold red]✗ Validation failed: {len(result.errors)} errors found[/bold red]\n"
        )

        # Display errors
        for error in result.errors:
            console.print(f"[red]ERROR [{error.code}]:[/red] {error.message}")
            if verbose and error.context:
                console.print(f"  [dim]Context: {error.context}[/dim]")
            console.print()

        # Display warnings if verbose
        if verbose and result.warnings:
            console.print(f"[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning.message}")
            console.print()

        console.print("[dim]Fix the errors above and run validation again.[/dim]")
        raise typer.Exit(1)


def _get_dir_size(path: Path) -> tuple[int, int]:
    """Get total size and file count for a directory.

    Returns:
        Tuple of (total_bytes, file_count)
    """
    total_size = 0
    file_count = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                    file_count += 1
                except (OSError, PermissionError):
                    # Skip files we can't stat (permission issues or transient errors)
                    pass
    except (OSError, PermissionError):
        # Skip directories we can't traverse; return best-effort size/count
        pass
    return total_size, file_count


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


@app.command()
def uninstall(
    keep_docs: bool = typer.Option(
        False, "--keep-docs", help="Preserve docs/ directory"
    ),
    keep_memory: bool = typer.Option(
        False, "--keep-memory", help="Preserve memory/ directory"
    ),
    keep_workflows: bool = typer.Option(
        False, "--keep-workflows", help="Preserve .github/workflows/"
    ),
    keep_all_github: bool = typer.Option(
        False, "--keep-all-github", help="Preserve entire .github/ directory"
    ),
    keep_claude: bool = typer.Option(
        False, "--keep-claude", help="Preserve .claude/ directory (user customizations)"
    ),
    keep_vscode: bool = typer.Option(
        False, "--keep-vscode", help="Preserve .vscode/ files (user customizations)"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be removed without removing"
    ),
) -> None:
    """Remove flowspec from the current project.

    This command removes all flowspec-generated files and directories
    from the current project. Use flags to preserve specific content.

    Examples:
        flowspec uninstall --dry-run          # Preview what will be removed
        flowspec uninstall --keep-docs        # Remove flowspec but keep docs/
        flowspec uninstall --keep-memory      # Preserve memory/ (constitution)
        flowspec uninstall --keep-claude      # Preserve .claude/ customizations
        flowspec uninstall --force            # Remove without confirmation
    """
    project_root = Path.cwd()

    # Check if this is a flowspec project
    flowspec_dir = project_root / ".flowspec"
    workflow_file = project_root / "flowspec_workflow.yml"

    if not flowspec_dir.exists() and not workflow_file.exists():
        console.print(
            "[red]Error:[/red] This doesn't appear to be a flowspec project.\n"
            "No .flowspec/ directory or flowspec_workflow.yml found."
        )
        raise typer.Exit(1)

    # Build list of items to remove
    items_to_remove: list[tuple[Path, str]] = []  # (path, description)

    # Core flowspec files (always removed)
    core_items = [
        (project_root / ".flowspec", "Flowspec configuration"),
        (project_root / "flowspec_workflow.yml", "Workflow configuration"),
        (project_root / ".mcp.json", "MCP server configuration"),
        (project_root / "CLAUDE.md", "Claude configuration guide"),
        (project_root / ".flowspec-light-mode", "Light mode marker"),
    ]

    for path, desc in core_items:
        if path.exists():
            items_to_remove.append((path, desc))

    # Conditionally remove .claude/ (unless --keep-claude)
    # Note: May contain user customizations beyond flowspec templates
    if not keep_claude:
        claude_dir = project_root / ".claude"
        if claude_dir.exists():
            items_to_remove.append((claude_dir, "Claude Code configuration"))

    # Conditionally remove .vscode/extensions.json (unless --keep-vscode)
    # Note: May contain user-added extension recommendations
    if not keep_vscode:
        vscode_ext = project_root / ".vscode" / "extensions.json"
        if vscode_ext.exists():
            items_to_remove.append((vscode_ext, "VS Code extensions"))

    # Conditionally remove .github/agents/ (unless --keep-all-github)
    if not keep_all_github:
        agents_dir = project_root / ".github" / "agents"
        if agents_dir.exists():
            items_to_remove.append((agents_dir, "VS Code Copilot agents"))

    # Conditionally remove docs/ (unless --keep-docs)
    if not keep_docs:
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            items_to_remove.append((docs_dir, "Documentation"))

    # Conditionally remove memory/ (unless --keep-memory)
    if not keep_memory:
        memory_dir = project_root / "memory"
        if memory_dir.exists():
            items_to_remove.append((memory_dir, "Memory (constitution)"))

    # Conditionally remove .github/workflows/ (unless --keep-workflows or --keep-all-github)
    if not keep_workflows and not keep_all_github:
        workflows_dir = project_root / ".github" / "workflows"
        if workflows_dir.exists():
            items_to_remove.append((workflows_dir, "GitHub workflows"))

    if not items_to_remove:
        console.print("[yellow]Nothing to remove.[/yellow]")
        raise typer.Exit(0)

    # Calculate sizes and display preview
    console.print("\n[bold]Flowspec Uninstall Preview[/bold]")
    console.print("=" * 40 + "\n")

    total_size = 0
    total_files = 0

    console.print("[bold red]The following will be REMOVED:[/bold red]")
    for path, desc in items_to_remove:
        if path.is_dir():
            size, count = _get_dir_size(path)
            total_size += size
            total_files += count
            console.print(
                f"  {path.relative_to(project_root)}/".ljust(30)
                + f"({_format_size(size)}, {count} files) - {desc}"
            )
        else:
            try:
                size = path.stat().st_size
                total_size += size
                total_files += 1
            except (OSError, PermissionError):
                size = 0
            console.print(
                f"  {path.relative_to(project_root)}".ljust(30)
                + f"({_format_size(size)}) - {desc}"
            )

    # Show what's preserved
    preserved = []
    if keep_docs and (project_root / "docs").exists():
        preserved.append("docs/ (--keep-docs)")
    if keep_memory and (project_root / "memory").exists():
        preserved.append("memory/ (--keep-memory)")
    if keep_workflows and (project_root / ".github" / "workflows").exists():
        preserved.append(".github/workflows/ (--keep-workflows)")
    if keep_all_github and (project_root / ".github").exists():
        preserved.append(".github/ (--keep-all-github)")
    if keep_claude and (project_root / ".claude").exists():
        preserved.append(".claude/ (--keep-claude)")
    if keep_vscode and (project_root / ".vscode").exists():
        preserved.append(".vscode/ (--keep-vscode)")

    if preserved:
        console.print("\n[bold green]The following will be PRESERVED:[/bold green]")
        for item in preserved:
            console.print(f"  {item}")

    console.print(
        f"\n[bold]Total: {_format_size(total_size)} ({total_files} files)[/bold]\n"
    )

    # Dry run - exit here
    if dry_run:
        console.print("[cyan]Dry run - no changes made.[/cyan]")
        raise typer.Exit(0)

    # Confirmation
    if not force:
        confirm = typer.confirm("Continue with removal?", default=False)
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    # Execute removal
    console.print("\n[bold]Removing files...[/bold]\n")
    removed_count = 0
    error_count = 0

    for path, desc in items_to_remove:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            console.print(
                f"  [green]✓[/green] Removed {path.relative_to(project_root)}"
            )
            removed_count += 1
        except Exception as e:
            console.print(
                f"  [red]✗[/red] Failed to remove {path.relative_to(project_root)}: {e}"
            )
            error_count += 1

    # Clean up empty .github/ directory if it's now empty
    github_dir = project_root / ".github"
    if github_dir.exists() and not any(github_dir.iterdir()):
        try:
            github_dir.rmdir()
            console.print("  [green]✓[/green] Removed empty .github/")
        except Exception:
            # Best effort: ignore failures to remove empty directory
            pass

    # Clean up empty .vscode/ directory if it's now empty
    vscode_dir = project_root / ".vscode"
    if vscode_dir.exists() and not any(vscode_dir.iterdir()):
        try:
            vscode_dir.rmdir()
            console.print("  [green]✓[/green] Removed empty .vscode/")
        except Exception:
            # Best effort: ignore failures to remove empty directory
            pass

    # Summary
    console.print()
    if error_count == 0:
        console.print(
            f"[bold green]✓ Flowspec removed successfully[/bold green] "
            f"({removed_count} items removed)"
        )
    else:
        console.print(
            f"[bold yellow]⚠ Flowspec partially removed[/bold yellow] "
            f"({removed_count} removed, {error_count} errors)"
        )
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
