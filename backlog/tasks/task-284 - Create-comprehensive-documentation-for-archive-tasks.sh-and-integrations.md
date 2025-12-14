---
id: task-284
title: Create comprehensive documentation for archive-tasks.sh and integrations
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-14 20:20'
labels:
  - documentation
dependencies:
  - task-281
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write user and developer documentation for archive script, GitHub Actions workflow, and hook integration.

**Documentation Files**:

1. **User Guide**: `docs/guides/backlog-archive.md`
   - Script purpose and use cases
   - Command-line arguments and flags
   - Examples for common scenarios
   - Exit codes and error handling
   - Troubleshooting common issues

2. **Workflow Guide**: `docs/guides/backlog-archive-workflow.md`
   - Workflow trigger modes (manual, scheduled, commit keyword)
   - How to run workflow manually via GitHub UI
   - Scheduled archiving schedule and behavior
   - Commit keyword syntax
   - Viewing workflow logs and results

3. **Hook Guide**: `docs/guides/backlog-archive-hook.md`
   - Hook trigger events (validate.completed, workflow.completed)
   - Enabling/disabling the hook
   - Hook behavior (dry-run only, fail-open)
   - Customizing hook configuration
   - Troubleshooting hook execution

4. **Troubleshooting Runbook**: `docs/runbooks/backlog-archive-troubleshooting.md`
   - Common error messages and solutions
   - Debugging workflow failures
   - Recovering from partial archive failures
   - Performance tuning
   - Escalation paths

5. **CLAUDE.md Update**:
   - Add archive-tasks.sh to scripts reference table
   - Link to documentation guides

**References**:
- Existing docs: `docs/guides/backlog-flush.md`
- Platform design: `docs/platform/archive-tasks-integration.md`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 User guide exists at docs/guides/backlog-archive.md
- [x] #2 Workflow guide exists at docs/guides/backlog-archive-workflow.md
- [x] #3 Hook guide exists at docs/guides/backlog-archive-hook.md
- [x] #4 Troubleshooting runbook exists at docs/runbooks/backlog-archive-troubleshooting.md
- [x] #5 All guides have examples and command-line usage
- [x] #6 CLAUDE.md updated with script reference
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-12-14)

Created comprehensive documentation for archive-tasks.sh:

1. **User Guide** (AC#1): `docs/guides/backlog-archive.md`
   - Script usage, options, examples, exit codes

2. **Workflow Guide** (AC#2): `docs/guides/backlog-archive-workflow.md`
   - GitHub Actions triggers, customization, troubleshooting

3. **Hook Guide** (AC#3): `docs/guides/backlog-archive-hook.md`
   - Claude Code hook configuration, fail-open design

4. **Troubleshooting Runbook** (AC#4): `docs/runbooks/backlog-archive-troubleshooting.md`
   - Common errors, recovery procedures, escalation

5. **Examples** (AC#5): All guides include command-line examples

6. **scripts/CLAUDE.md** (AC#6): Added archive-tasks.sh to scripts reference
<!-- SECTION:NOTES:END -->
