---
id: task-463
title: 'claude-improves: Copy missing skills to templates/skills/'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-15 02:18'
labels:
  - claude-improves
  - source-repo
  - skills
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two skills exist in .claude/skills/ but are NOT in templates/skills/, meaning users running `specify init` won't get them:
- security-fixer
- security-workflow

These skills should be copied to templates/skills/ so they are distributed to all new projects.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 security-fixer skill directory copied to templates/skills/
- [x] #2 security-workflow skill directory copied to templates/skills/
- [x] #3 Both skills have proper SKILL.md structure
- [x] #4 Verify with: diff <(ls templates/skills/) <(ls .claude/skills/ | grep -v '\.md$')
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verify security-fixer and security-workflow skill structures
2. Copy security-fixer to templates/skills/
3. Copy security-workflow to templates/skills/
4. Verify both have proper SKILL.md structure
5. Run diff to confirm parity
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Copied security-fixer and security-workflow skills from .claude/skills/ to templates/skills/.

Both skills have proper SKILL.md structure:
- security-fixer/SKILL.md (10,523 bytes)
- security-workflow/SKILL.md (17,245 bytes)

Verification:
- diff shows no differences between templates/skills/ and .claude/skills/ (excluding standalone .md files)
- templates/skills/ now contains 11 skill directories (was 9)
<!-- SECTION:NOTES:END -->
