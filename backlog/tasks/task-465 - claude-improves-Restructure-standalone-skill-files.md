---
id: task-465
title: "claude-improves: Restructure standalone skill files to directory format"
status: To Do
assignee: []
created_date: '2025-12-12 01:15'
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
- [ ] #1 Each standalone .md file converted to skill-name/SKILL.md directory structure
- [ ] #2 All 8 skills properly restructured
- [ ] #3 Skills remain functional after restructure
- [ ] #4 Update CLAUDE.md to document all skills
<!-- AC:END -->
