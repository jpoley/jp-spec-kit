---
id: task-441
title: Update Python source code to use flowspec instead of flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - backend
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all Python source code in src/specify_cli/ to replace flowspec references:

Files with flowspec references (found via grep):
- src/specify_cli/memory/mcp.py
- src/specify_cli/security/config/models.py
- src/specify_cli/security/config/loader.py
- src/specify_cli/security/exporters/sarif.py
- src/specify_cli/security/integrations/hooks.py
- src/specify_cli/security/integrations/cicd.py
- src/specify_cli/security/mcp_server.py
- src/specify_cli/__init__.py
- src/specify_cli/hooks/events.py
- src/specify_cli/hooks/cli.py

Updates needed:
1. String literals: "flowspec" → "flowspec"
2. Variable names: flowspec_* → flowspec_*
3. Function names: *_flowspec_* → *_flowspec_*
4. Config keys: flowspec_workflow → flowspec_workflow
5. Command patterns: /flow: → /flow:
6. Path references: commands/flowspec → commands/flowspec
7. Comments and docstrings

Critical areas:
- Config loading logic (must load flowspec_workflow.yml)
- Command validation (must accept /flow: pattern)
- Path construction (must use flowspec directory)
- MCP integrations (workflow state references)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All Python source files updated to use flowspec terminology
- [ ] #2 Config loader reads flowspec_workflow.yml
- [ ] #3 Command pattern validation accepts /flow: prefix
- [ ] #4 Path construction uses flowspec directory
- [ ] #5 All unit tests pass
- [ ] #6 No 'flowspec' string literals remain except in migration/deprecation code
- [ ] #7 Type hints and docstrings updated
<!-- AC:END -->
