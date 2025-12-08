---
id: task-241
title: Create tiered constitution templates (light/medium/heavy)
status: Done
assignee:
  - '@myself'
created_date: '2025-12-03 02:36'
updated_date: '2025-12-03 03:00'
labels:
  - cli
  - templates
  - constitution
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create three constitution template files with different levels of controls for project initialization
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create templates/constitutions/constitution-light.md with minimal controls (startup/hobby level)
- [x] #2 Create templates/constitutions/constitution-medium.md with standard controls (typical business)
- [x] #3 Create templates/constitutions/constitution-heavy.md with strict controls (bank/enterprise level)
- [x] #4 Each template has clear section markers for LLM customization
- [x] #5 Templates include NEEDS_VALIDATION comment markers for auto-generated sections
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via PR #252

Status: Pending CI verification

Changes:
- Created templates/constitutions/constitution-light.md (50 lines)
- Created templates/constitutions/constitution-medium.md (95 lines)
- Created templates/constitutions/constitution-heavy.md (211 lines)
- All templates include SECTION and NEEDS_VALIDATION markers
<!-- SECTION:NOTES:END -->
