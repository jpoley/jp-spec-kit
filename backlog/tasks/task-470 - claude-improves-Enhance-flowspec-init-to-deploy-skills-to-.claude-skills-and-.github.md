---
id: task-470
title: >-
  claude-improves: Enhance flowspec init to deploy skills to .claude/skills/ and
  .github/
status: In Progress
assignee:
  - '@myself'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-22 22:54'
labels:
  - claude-improves
  - cli
  - specify-init
  - skills
  - phase-1
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend flowspec init to copy skill templates from templates/skills/ to the project's .claude/skills/ directory AND deploy GitHub Copilot prompts/skills to .github/ for dual-agent support.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 specify init copies all skills from templates/skills/ to .claude/skills/
- [ ] #2 Skills maintain proper SKILL.md directory structure
- [ ] #3 Existing skills in .claude/skills/ are not overwritten without --force flag
- [ ] #4 Add --skip-skills flag to opt out of skill deployment
- [ ] #5 Document skill deployment in init output

- [ ] #6 Deploy GitHub Copilot prompts to .github/prompts/ directory
- [ ] #7 Sync skills between .claude/skills/ and .github/ for dual-agent support
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create deploy_skills() helper function in src/flowspec_cli/__init__.py\n2. Implement directory structure preservation (templates/skills/ → .claude/skills/)\n3. Add --force flag for overwrite protection\n4. Add --skip-skills flag (default: False)\n5. Integrate with StepTracker for progress display\n6. [BLOCKED] Research GitHub Copilot prompts format for AC#6-7\n7. Write unit tests for skills deployment\n8. Update init command docstring
<!-- SECTION:PLAN:END -->
