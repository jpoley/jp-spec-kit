---
id: task-440
title: Rename test files and update test fixtures for flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - testing
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename and update all test files containing 'flowspec' in their names or content:

Test files to rename (14 files):
- test_flowspec_assess.py → test_flowspec_assess.py
- test_flowspec_backlog_integration.py → test_flowspec_backlog_integration.py
- test_flowspec_e2e.py → test_flowspec_e2e.py
- test_flowspec_implement_backlog.py → test_flowspec_implement_backlog.py
- test_flowspec_operate_backlog.py → test_flowspec_operate_backlog.py
- test_flowspec_plan_backlog.py → test_flowspec_plan_backlog.py
- test_flowspec_research_backlog.py → test_flowspec_research_backlog.py
- test_flowspec_specify_backlog.py → test_flowspec_specify_backlog.py
- test_flowspec_validate_backlog.py → test_flowspec_validate_backlog.py
- test_flowspec_workflow_integration.py → test_flowspec_workflow_integration.py
- test_flowspec_workflow_roles.py → test_flowspec_workflow_roles.py

Test fixture updates:
- tests/fixtures/workflow/*.yml (update content to use /flow: commands)
- Update test assertions for new paths
- Update docstrings and comments

Content updates in tests:
1. Update path references: .claude/commands/flowspec → .claude/commands/flowspec
2. Update command patterns: /flow: → /flow:
3. Update schema references: flowspec_workflow → flowspec_workflow
4. Update fixture data and expected outputs
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All test files renamed from test_flowspec_* to test_flowspec_*
- [ ] #2 Test fixtures updated to use /flow: commands
- [ ] #3 All path assertions updated for flowspec directory
- [ ] #4 Test suite passes completely with new names
- [ ] #5 Code coverage maintained or improved
- [ ] #6 No references to flowspec in test code except migration comments
<!-- AC:END -->
