---
id: task-446
title: 'archon-inspired: Create INITIAL feature intake template'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-12 01:00'
updated_date: '2025-12-12 01:20'
labels:
  - archon-inspired
  - architecture
  - templates
  - context-engineering
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create an INITIAL-style document template for structured feature intake per the context-engineering-intro patterns. This template becomes the canonical starting point for any new feature-level change.

**Location**: `templates/docs/initial/initial-feature-template.md`

**Pattern Source**: Based on context-engineering-intro INITIAL doc structure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Template file created at templates/docs/initial/initial-feature-template.md
- [x] #2 Contains FEATURE section (problem, outcome, constraints, importance)
- [x] #3 Contains EXAMPLES section (relevant files under examples/, their purpose)
- [x] #4 Contains DOCUMENTATION section (PRDs, ADRs, README, external specs)
- [x] #5 Contains OTHER CONSIDERATIONS section (gotchas, failures, dependencies, security, performance)
- [x] #6 Template includes placeholder text explaining each section's purpose
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create templates/docs/initial/ directory structure
2. Create initial-feature-template.md with all required sections
3. Add FEATURE section with problem/outcome/constraints/importance
4. Add EXAMPLES section with examples/ file references
5. Add DOCUMENTATION section with doc links
6. Add OTHER CONSIDERATIONS section with gotchas
7. Add helpful placeholder text for each section
8. Verify all acceptance criteria met
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented INITIAL feature intake template based on archon-inspired context engineering patterns.

**Files Created:**
- `templates/docs/initial/initial-feature-template.md` - Main template with all required sections
- `templates/docs/initial/README.md` - Directory documentation

**Template Sections:**
1. **FEATURE** - Problem statement, desired outcome, key constraints, why it matters
2. **EXAMPLES** - Example files table, usage patterns, expected behavior examples
3. **DOCUMENTATION** - Internal docs table, external references, related backlog tasks
4. **OTHER CONSIDERATIONS** - Known gotchas, previous failures, dependencies, security, performance, edge cases

**Key Features:**
- Placeholder text explains purpose of each section
- HTML comments provide guidance for filling in content
- Tables for structured data (examples, docs, tasks)
- Checkbox lists for actionable items
- NEXT STEPS section guides workflow continuation
- Version and attribution footer

**Usage:** Copy template to `docs/features/<slug>-initial.md`, fill in sections, then run `/flow:intake` to create backlog task.
<!-- SECTION:NOTES:END -->
