---
id: task-281
title: Create archive-tasks.sh script for agent hooks
status: To Do
assignee: []
created_date: '2025-12-04 03:26'
updated_date: '2025-12-04 03:33'
labels:
  - backend
  - script
  - bash
  - hooks
  - infrastructure
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a bash script that can archive backlog tasks with flexible filtering options. The script will support archiving all tasks (-a) or tasks completed by a specific date (--done-by DATE). This enables automated backlog maintenance as part of agent hooks, allowing workflows to clean up completed tasks based on configurable criteria.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script accepts -a/--all flag to archive ALL tasks (not just Done)
- [ ] #2 Script accepts --done-by DATE flag to archive tasks completed on or before the specified date
- [ ] #3 Date parsing handles ISO 8601 format (YYYY-MM-DD)
- [ ] #4 Validates date format and provides clear error messages for invalid dates
- [ ] #5 Supports --dry-run flag to preview what would be archived without making changes
- [ ] #6 Integrates with backlog CLI for task querying and archiving
- [ ] #7 Script is executable and follows existing script conventions in scripts/bash/
- [ ] #8 Returns appropriate exit codes (0=success, 1=error, 2=no tasks matched)
- [ ] #9 Documentation includes usage examples and hook integration guidance
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### Phase 1: Core Script (task-281.01)
1. Create `scripts/bash/archive-tasks.sh` with CLI parsing
2. Implement date parsing and validation using GNU `date`
3. Add task filtering logic (all, done-by, default done-only)
4. Integrate with backlog CLI for archiving
5. Add dry-run support and exit code strategy

### Phase 2: GitHub Actions (task-282)
1. Create `.github/workflows/backlog-archive.yml`
2. Configure manual dispatch, scheduled, and keyword triggers
3. Implement mode selection (done/all/date)

### Phase 3: Hook Integration (task-283 - BLOCKED)
- Requires: task-198, task-201, task-202 (event model)
- Creates post-workflow-archive.sh hook

### Phase 4: Documentation (task-284)
1. User guide for script usage
2. Hook integration guide
3. Troubleshooting runbook

### Key ADRs
- ADR-001: Query all tasks then filter in-script
- ADR-002: Use GNU `date` for date parsing
- ADR-003: Complement (not replace) flush-backlog.sh
<!-- SECTION:PLAN:END -->
