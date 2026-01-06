---
id: task-579.04
title: 'P0.4: Fix upgrade-repo to sync .claude/skills/ directory'
status: Done
assignee: []
created_date: '2026-01-06 17:19'
updated_date: '2026-01-06 21:39'
labels:
  - phase-0
  - upgrade-repo
  - skills
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The upgrade_repo command does NOT sync skills between flowspec and target repos. Target repos end up with outdated/missing skills.

Example: auth.poley.dev has 9 skills, flowspec has 21 skills.

Missing from auth.poley.dev:
- context-extractor
- exploit-researcher, fuzzing-strategist, patch-engineer
- security-analyst, security-codeql, security-custom-rules
- security-dast, security-triage
- gather-learnings, workflow-executor

Changes needed:
1. Add skills sync step to upgrade_repo
2. Copy new skills from templates/skills/
3. Update existing skills (preserve custom modifications with backup)
4. Report which skills were added/updated
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 upgrade_repo syncs .claude/skills/ directory
- [x] #2 New skills copied from templates/skills/
- [x] #3 Existing skills updated (with backup of custom modifications)
- [x] #4 Sync report shows which skills were added/updated/unchanged
- [x] #5 Test: running upgrade-repo on project with missing skills adds them
<!-- AC:END -->
