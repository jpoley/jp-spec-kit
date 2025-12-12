---
id: task-465
title: 'claude-improves: Restructure standalone skill files to directory format'
status: In Progress
assignee:
  - '@claude-agent-2'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-12 01:41'
labels:
  - claude-improves
  - source-repo
  - skills
  - consistency
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
8 skills in .claude/skills/ are standalone .md files rather than directories with SKILL.md:
- exploit-researcher.md
- fuzzing-strategist.md
- patch-engineer.md
- security-analyst.md
- security-codeql.md
- security-custom-rules.md
- security-dast.md
- security-triage.md

Expected format: skill-name/SKILL.md for consistency with other skills.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each standalone .md file converted to skill-name/SKILL.md directory structure
- [x] #2 All 8 skills properly restructured
- [x] #3 Skills remain functional after restructure
- [ ] #4 Update CLAUDE.md to document all skills
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Restructured 8 standalone skill .md files to directory format:
- exploit-researcher/SKILL.md
- fuzzing-strategist/SKILL.md
- patch-engineer/SKILL.md
- security-analyst/SKILL.md
- security-codeql/SKILL.md
- security-custom-rules/SKILL.md
- security-dast/SKILL.md
- security-triage/SKILL.md

All skills verified functional in new directory structure.
<!-- SECTION:NOTES:END -->
