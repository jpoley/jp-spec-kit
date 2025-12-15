---
id: task-283
title: Create post-workflow-archive.sh hook for agent-triggered archiving
status: To Do
assignee:
  - '@adare'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-15 02:17'
labels:
  - infrastructure
  - agent-hooks
  - claude-code
dependencies:
  - task-281
  - task-198
  - task-201
  - task-202
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Claude Code hook that runs archive-tasks.sh in dry-run mode after workflow completion (validate.completed event).

**Hook Location**: `.claude/hooks/post-workflow-archive.sh`

**Hook Behavior**:
- Triggered by: validate.completed event (end of /flow:validate)
- Reads event from stdin (standard hook interface)
- Parses event_type, feature, project_root from JSON
- Runs archive-tasks.sh with --dry-run flag (preview only)
- Exits 0 (fail-open) even if script fails
- Logs execution to stdout for debugging

**Rationale**:
- Dry-run only in hooks to avoid modifying backlog mid-session
- Fail-open ensures archiving issues don't block workflow
- Provides visibility into archivable tasks at workflow completion

**Security**:
- Hook sandboxed by Claude Code hook system (ADR-006)
- Script must be in .claude/hooks/ directory (path allowlist)
- Timeout: 30 seconds
- Minimal environment variables

**References**:
- Hook examples: `.claude/hooks/session-start.sh`, `.claude/hooks/stop-quality-gate.py`
- Platform design: `docs/platform/archive-tasks-integration.md`
- Hook execution model: `docs/adr/ADR-006-hook-execution-model.md`

**Blocker**: Depends on event model and hook runner implementation (tasks 198, 201, 202)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Hook script exists at .claude/hooks/post-workflow-archive.sh
- [ ] #2 Hook reads event from stdin (standard hook interface)
- [ ] #3 Hook parses event_type, feature, project_root from JSON
- [ ] #4 Hook runs archive-tasks.sh with --dry-run flag
- [ ] #5 Hook exits 0 (fail-open) even if script fails
- [ ] #6 Hook logs execution to stdout for debugging
- [ ] #7 Hook is executable and passes shellcheck
<!-- AC:END -->
