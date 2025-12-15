---
id: task-360
title: 'For speckit.constitution: Role-Based Command Standards'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:10'
updated_date: '2025-12-15 02:17'
labels:
  - architecture
  - constitution
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define constitutional standards for role-based command namespaces to be included in speckit.constitution
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command namespace standards documented
- [x] #2 Role-to-command mapping rules defined
- [x] #3 Naming conventions established
- [x] #4 Extensibility guidelines for future roles
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# For speckit.constitution: Role-Based Command Standards

## Deliverable
Created constitutional standards document at: /home/jpoley/ps/flowspec/docs/adr/constitution-role-based-command-standards.md

## Constitutional Principles Defined

### 1. Role-Based Organization Mandate
All commands MUST use `/{role}:{action}[:{qualifier}]` format

### 2. Namespace Stability Contract
Role namespaces are first-class citizens:
- Adding commands: minor version
- Renaming namespace: major version + 12-month deprecation
- Minimum deprecation: 12 months

### 3. Role-to-Command Mapping Rules
Each command has exactly ONE primary role:
- /pm → Product Manager
- /dev → Developer  
- /sec → Security Engineer
- /qa → QA Engineer
- /ops → SRE/DevOps
- /speckit → Cross-role utilities

### 4. Naming Convention Standards
**Role Prefix**: 2-5 chars, lowercase, unique
**Action Verb**: Imperative, clear, 1-2 words
**Qualifiers**: Hyphen-separated, purpose-driven

Approved verbs by category:
- Creation: assess, specify, research, plan, init
- Execution: implement, deploy, operate, run
- Validation: validate, test, scan, check, review
- Modification: fix, update, reset, prune
- Information: report, analyze, status, list

### 5. Command Documentation Standards
Required frontmatter: description, role, agents, mode, states
Required sections: User Input, Instructions, Agent Context, Deliverables, Examples

### 6. Extensibility Guidelines
**New Commands**: Follow naming conventions, add to namespace
**New Roles**: Minimum 3 commands, 1 dedicated agent, ADR approval

### 7. Backwards Compatibility Requirements
Breaking changes MUST follow deprecation protocol:
1. Announcement (Month 0)
2. Soft deprecation (0-6)
3. Hard deprecation (6-9)
4. Final warning (9-12)
5. Removal (12+)

### 8. Quality Gates
Pre-commit: naming validation, doc completeness, agent sync
CI/CD: regex validation, integration tests, drift detection
Review: checklist enforcement

## Constitutional Amendment Process
1. Propose ADR with rationale
2. Community feedback
3. Core team review (2+ approvals)
4. Implementation plan
5. Update constitution
6. Publish announcement

## Enforcement
- Automated: pre-commit hooks, CI/CD pipeline, linters
- Manual: code review checklist verification

## Quick Reference Table
All principles summarized in easy-to-scan format

## Next Steps
- Review and approve constitutional standards
- Incorporate into /speckit.constitution
- Update tooling to enforce standards
- Train team on new conventions
<!-- SECTION:NOTES:END -->
