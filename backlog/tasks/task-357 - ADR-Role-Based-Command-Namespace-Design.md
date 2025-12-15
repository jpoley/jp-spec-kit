---
id: task-357
title: 'ADR: Role-Based Command Namespace Design'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:10'
updated_date: '2025-12-15 02:17'
labels:
  - architecture
  - adr
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Document architecture decision for transitioning from flat /flowspec and /speckit namespaces to role-based command organization (pm, dev, sec, qa, ops)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define role namespaces (pm, dev, sec, qa, ops)
- [x] #2 Create command mapping matrix from current to new structure
- [x] #3 Document trade-offs and alternatives considered
- [x] #4 Define namespace hierarchy and naming conventions
- [x] #5 Specify backwards compatibility strategy
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
# ADR: Role-Based Command Namespace Design

## Deliverable
Created comprehensive ADR at: /home/jpoley/ps/flowspec/docs/adr/ADR-role-based-command-namespaces.md

## Key Design Decisions

### 1. Namespace Structure
Chose hierarchical namespaces with aliases over flat namespace with prefixes:
- `/pm:*` - Product Manager commands
- `/dev:*` - Developer commands  
- `/sec:*` - Security commands
- `/qa:*` - QA commands
- `/ops:*` - Operations commands
- `/speckit:*` - Cross-role utilities

### 2. Command Mapping Matrix
Mapped all 18+ existing commands to new role-based structure:
- 3 PM commands (assess, specify, research)
- 8 Dev commands (plan, implement, operate, init, reset, prune-branch, implement-light, plan-light)
- 5 Security commands (fix, report, triage, scan-web, workflow)
- 3 QA commands (validate, checklist, analyze)
- 1+ Ops commands (deploy, monitor, incident, runbook)

### 3. Naming Conventions
Established standards:
- Format: `/{role}:{action}[:{qualifier}]`
- Role prefix: 2-5 chars, lowercase, unique
- Action verb: imperative, clear intent
- Qualifiers: hyphen-separated, purpose-driven

### 4. Trade-offs Analyzed
Evaluated 3 options:
1. Status quo (rejected - no improvement)
2. Hierarchical namespaces with aliases (SELECTED - best balance)
3. Tag-based filtering (rejected - too IDE-dependent)

### 5. Backwards Compatibility
12-month deprecation timeline:
- Months 0-6: Soft deprecation (awareness)
- Months 6-9: Hard deprecation (urgency)
- Months 9-12: Final warning
- Month 12+: Removal with helpful errors

## Consequences
**Positive**:
- Improved discoverability (3-8 commands vs 18+)
- Better onboarding experience
- Reduced cognitive load
- Team structure alignment

**Negative**:
- Migration effort for existing users
- Documentation debt during transition
- Eventual breaking change

## Next Steps
- Review and approve ADR
- Implement role selection mechanism (task-358)
- Build migration tooling (task-359)
- Define constitutional standards (task-360)
<!-- SECTION:NOTES:END -->
