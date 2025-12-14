# Command Taxonomy Audit - Current State

**Date**: 2025-12-10
**Purpose**: Document the current state of all slash commands across all namespaces before making corrections.

---

## Summary

There are **8 command namespaces** with **63 total command files**:

| Namespace | Command Count | Purpose |
|-----------|---------------|---------|
| `speckit` | 10 | Core SDD workflow (spec → plan → implement) |
| `flowspec` | 29 (15 active + 14 deprecated) | Extended SDD workflow with agents |
| `pm` | 3 | Product Manager role commands |
| `arch` | 3 | Architect role commands |
| `dev` | 4 | Developer role commands |
| `qa` | 3 | QA Engineer role commands |
| `sec` | 5 | Security Engineer role commands |
| `ops` | 4 | SRE/DevOps role commands |

---

## Namespace: `speckit`

**Location**: `templates/commands/speckit/`
**Commands**: 10

| Command | Description |
|---------|-------------|
| `/speckit:analyze` | Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation. |
| `/speckit:checklist` | Generate a custom checklist for the current feature based on user requirements. |
| `/speckit:clarify` | Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec. |
| `/speckit:configure` | Configure or reconfigure workflow settings including role selection and validation modes |
| `/speckit:constitution` | Analyze repository and create customized constitution.md based on detected tech stack |
| `/speckit:implement` | Execute the implementation plan by processing and executing all tasks defined in tasks.md |
| `/speckit:init` | Initialize project with constitution and role selection for personalized workflows |
| `/speckit:plan` | Execute the implementation planning workflow using the plan template to generate design artifacts. |
| `/speckit:specify` | Create or update the feature specification from a natural language feature description. |
| `/speckit:tasks` | Generate an actionable, dependency-ordered task backlog for the feature based on available design artifacts. |

**Notes**:
- Uses shell scripts for some operations (`scripts/bash/create-new-feature.sh`)
- Simpler, more lightweight implementation
- No agent-based workflow orchestration

---

## Namespace: `flowspec`

**Location**: `templates/commands/flowspec/`
**Commands**: 15 active + 14 deprecated + 3 partials

### Active Commands

| Command | Description |
|---------|-------------|
| `/flow:assess` | Evaluate if SDD workflow is appropriate for a feature. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple). |
| `/flow:implement` | Execute implementation using specialized frontend and backend engineer agents with code review. |
| `/flow:init` | Initialize or setup constitution for a project, handling both greenfield (new) and brownfield (existing) projects |
| `/flow:operate` | Execute operations workflow using SRE agent for CI/CD, Kubernetes, DevSecOps, observability, and operational excellence. |
| `/flow:plan` | Execute planning workflow using project architect and platform engineer agents (builds out /speckit.constitution). |
| `/flow:prune-branch` | Prune local branches that have been merged and deleted on remote. |
| `/flow:research` | Execute research and business validation workflow using specialized agents. |
| `/flow:reset` | Reset workflow configuration by re-asking startup questions and regenerating flowspec_workflow.yml |
| `/flow:security_fix` | Generate and apply security patches for vulnerability findings from triage results. |
| `/flow:security_report` | Generate comprehensive security audit report from scan and triage results using security-reporter skill. |
| `/flow:security_triage` | (no description in file) |
| `/flow:security_web` | (no description in file) |
| `/flow:security_workflow` | Integrate security scanning and remediation into the SDD workflow with automatic backlog task creation. |
| `/flow:specify` | Create or update feature specifications using PM planner agent (manages /speckit.tasks). |
| `/flow:validate` | Execute validation and quality assurance using QA, security, documentation, and release management agents. |

### Deprecated Commands

| Deprecated Command | Replacement | Description |
|--------------------|-------------|-------------|
| `/flow:_DEPRECATED_assess` | `/pm:assess` | Evaluate if SDD workflow is appropriate |
| `/flow:_DEPRECATED_implement` | `/dev:build` | Execute implementation with agents |
| `/flow:_DEPRECATED_operate` | `/ops:deploy` | Execute operations workflow |
| `/flow:_DEPRECATED_plan` | `/arch:design` | Execute planning workflow |
| `/flow:_DEPRECATED_prune-branch` | `/dev:cleanup` | Prune merged branches |
| `/flow:_DEPRECATED_research` | `/pm:discover` | Research and validation workflow |
| `/flow:_DEPRECATED_security_fix` | `/sec:fix` | Security patch generation |
| `/flow:_DEPRECATED_security_report` | `/sec:report` | Security audit report |
| `/flow:_DEPRECATED_security_triage` | `/sec:triage` | Security triage |
| `/flow:_DEPRECATED_security_web` | `/sec:scan` | Security scanning |
| `/flow:_DEPRECATED_security_workflow` | `/sec:audit` | Security workflow integration |
| `/flow:_DEPRECATED_specify` | `/pm:define` | Create feature specifications |
| `/flow:_DEPRECATED_validate` | `/qa:verify` | Validation and QA |

### Partial/Include Files

| File | Purpose |
|------|---------|
| `_backlog-instructions.md` | Backlog CLI usage instructions (included in other commands) |
| `_constitution-check.md` | Constitution validation logic (included in other commands) |
| `_workflow-state.md` | Workflow state management (included in other commands) |

---

## Namespace: `pm` (Product Manager)

**Location**: `templates/commands/pm/`
**Commands**: 3

| Command | Description |
|---------|-------------|
| `/pm:assess` | Evaluate if SDD workflow is appropriate for a feature. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple). |
| `/pm:define` | Create or update feature specifications using PM planner agent (manages /speckit.tasks). |
| `/pm:discover` | Execute research and business validation workflow using specialized agents. |

---

## Namespace: `arch` (Architect)

**Location**: `templates/commands/arch/`
**Commands**: 3

| Command | Description |
|---------|-------------|
| `/arch:decide` | Create Architecture Decision Records (ADRs) for technical decisions. |
| `/arch:design` | Execute planning workflow using project architect and platform engineer agents (builds out /speckit.constitution). |
| `/arch:model` | Create data models, API contracts, and system diagrams. |

---

## Namespace: `dev` (Developer)

**Location**: `templates/commands/dev/`
**Commands**: 4

| Command | Description |
|---------|-------------|
| `/dev:build` | Execute implementation using specialized frontend and backend engineer agents with code review. |
| `/dev:cleanup` | Prune local branches that have been merged and deleted on remote. |
| `/dev:debug` | Debugging assistance for troubleshooting issues and errors. |
| `/dev:refactor` | Code refactoring guidance for improving code quality and maintainability. |

---

## Namespace: `qa` (QA Engineer)

**Location**: `templates/commands/qa/`
**Commands**: 3

| Command | Description |
|---------|-------------|
| `/qa:review` | Generate a custom checklist for the current feature based on user requirements. |
| `/qa:test` | Execute tests and generate test coverage reports. |
| `/qa:verify` | Execute validation and quality assurance using QA, security, documentation, and release management agents. |

---

## Namespace: `sec` (Security Engineer)

**Location**: `templates/commands/sec/`
**Commands**: 5

| Command | Description |
|---------|-------------|
| `/sec:audit` | Integrate security scanning and remediation into the SDD workflow with automatic backlog task creation. |
| `/sec:fix` | Generate and apply security patches for vulnerability findings from triage results. |
| `/sec:report` | Generate comprehensive security audit report from scan and triage results using security-reporter skill. |
| `/sec:scan` | (no description found) |
| `/sec:triage` | (no description found) |

---

## Namespace: `ops` (SRE/DevOps)

**Location**: `templates/commands/ops/`
**Commands**: 4

| Command | Description |
|---------|-------------|
| `/ops:deploy` | Execute operations workflow using SRE agent for CI/CD, Kubernetes, DevSecOps, observability, and operational excellence. |
| `/ops:monitor` | Set up monitoring, alerting, and observability for deployed systems. |
| `/ops:respond` | Incident response guidance for production issues and outages. |
| `/ops:scale` | Scale infrastructure and applications to handle load. |

---

## Command Overlap Analysis

### Commands with Same Name in Multiple Namespaces

| Command Name | speckit | flowspec | Role-Based | Same Implementation? |
|--------------|---------|----------|------------|---------------------|
| `init` | `/speckit:init` | `/flow:init` | - | **NO** - Different implementations |
| `specify` | `/speckit:specify` | `/flow:specify` | `/pm:define` | **NO** - speckit is simpler, flowspec/pm are agent-based |
| `plan` | `/speckit:plan` | `/flow:plan` | `/arch:design` | **UNKNOWN** - Need to verify |
| `implement` | `/speckit:implement` | `/flow:implement` | `/dev:build` | **UNKNOWN** - Need to verify |
| `assess` | - | `/flow:assess` | `/pm:assess` | Likely same |
| `research` | - | `/flow:research` | `/pm:discover` | Likely same |
| `validate` | - | `/flow:validate` | `/qa:verify` | Likely same |
| `operate` | - | `/flow:operate` | `/ops:deploy` | Likely same |
| `checklist` | `/speckit:checklist` | - | `/qa:review` | **UNKNOWN** |

### speckit-only Commands (no equivalent elsewhere)

| Command | Description |
|---------|-------------|
| `/speckit:analyze` | Cross-artifact consistency analysis |
| `/speckit:clarify` | Clarification questions for spec |
| `/speckit:configure` | Workflow settings configuration |
| `/speckit:constitution` | Constitution generation |
| `/speckit:tasks` | Task backlog generation |

### flowspec-only Commands (no equivalent elsewhere)

| Command | Description |
|---------|-------------|
| `/flow:reset` | Reset workflow configuration |
| `/flow:prune-branch` | Git branch cleanup (also `/dev:cleanup`) |
| `/flow:security_*` | Security workflow commands |

### Role-based-only Commands (no equivalent in speckit/flowspec)

| Command | Description |
|---------|-------------|
| `/arch:decide` | ADR creation |
| `/arch:model` | Data model/API contract creation |
| `/dev:debug` | Debugging assistance |
| `/dev:refactor` | Refactoring guidance |
| `/ops:monitor` | Monitoring setup |
| `/ops:respond` | Incident response |
| `/ops:scale` | Scaling guidance |
| `/qa:test` | Test execution |

---

## Key Implementation Differences

### `/speckit:specify` vs `/flow:specify`

| Aspect | speckit | flowspec |
|--------|---------|----------|
| Implementation | Shell script (`create-new-feature.sh`) | Agent-based (PM Planner) |
| Output | Simple spec from template | Full PRD with SVPG methodology |
| Backlog integration | No | Yes (creates tasks via CLI) |
| Workflow state | No | Yes (requires `workflow:Assessed` state) |
| Complexity | Lower | Higher |

### `/speckit:init` vs `/flow:init`

| Aspect | speckit | flowspec |
|--------|---------|----------|
| Purpose | Initialize with constitution + role selection | Initialize constitution for greenfield/brownfield |
| Workflow config | Generates `flowspec_workflow.yml` | Similar |
| Complexity | Simpler | More comprehensive |

---

## Deprecation Mapping Summary

The current deprecation files map flowspec commands to role-based commands:

```
/flow:assess     → /pm:assess
/flow:specify    → /pm:define
/flow:research   → /pm:discover
/flow:plan       → /arch:design
/flow:implement  → /dev:build
/flow:validate   → /qa:verify
/flow:operate    → /ops:deploy
/flow:prune-branch → /dev:cleanup
/flow:security_* → /sec:*
```

---

## Files in .claude/commands/

The `.claude/commands/` directory contains symlinks to templates:

```
.claude/commands/
├── arch -> ../../templates/commands/arch       (symlink to dir)
├── dev -> ../../templates/commands/dev         (symlink to dir)
├── ops -> ../../templates/commands/ops         (symlink to dir)
├── pm -> ../../templates/commands/pm           (symlink to dir)
├── qa -> ../../templates/commands/qa           (symlink to dir)
├── sec -> ../../templates/commands/sec         (symlink to dir)
├── flowspec/                                   (directory with symlinks)
│   ├── assess.md -> ../../../templates/commands/flowspec/assess.md
│   ├── _DEPRECATED_*.md -> ...
│   └── ... (individual file symlinks)
└── speckit/                                    (directory with symlinks)
    ├── analyze.md -> ../../../templates/commands/speckit/analyze.md
    └── ... (individual file symlinks)
```

**Note**: Role-based namespaces are directory symlinks, while speckit/flowspec contain individual file symlinks.

---

## Questions for Clarification

1. **What is the intended relationship between speckit and flowspec?**
   - Are they separate products/modes?
   - Should flowspec contain ALL speckit functionality plus more?
   - Or are they independent workflows?

2. **Should flowspec be the "primary" namespace with role-based as aliases?**
   - Current deprecation suggests role-based are primary
   - But user indicated flowspec should be primary

3. **What happens to speckit commands that don't exist in flowspec?**
   - `/speckit:analyze`
   - `/speckit:clarify`
   - `/speckit:configure`
   - `/speckit:constitution`
   - `/speckit:tasks`

4. **Should the two `specify` implementations be unified or kept separate?**
   - speckit version: simple, script-based
   - flowspec version: complex, agent-based with PRD methodology

---

*This document describes the CURRENT STATE only. Corrections and desired state to be defined separately.*
