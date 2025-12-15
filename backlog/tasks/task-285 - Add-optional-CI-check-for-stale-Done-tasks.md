---
id: task-285
title: Add optional CI check for stale Done tasks
status: To Do
assignee:
  - '@adare'
created_date: '2025-12-04 03:32'
updated_date: '2025-12-15 02:17'
labels:
  - infrastructure
  - ci-cd
  - quality-gate
dependencies:
  - task-281
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add optional CI job to ci.yml that warns (but doesn't fail) if Done tasks exist that should be archived.

**Implementation**:

Add job to `.github/workflows/ci.yml`:

```yaml
jobs:
  backlog-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install backlog CLI
        run: npm install -g backlog.md

      - name: Check for archivable tasks
        continue-on-error: true  # Don't fail CI
        run: |
          ./scripts/bash/archive-tasks.sh --dry-run || exit_code=$?

          if [[ "${exit_code:-0}" -eq 0 ]]; then
            echo "::notice::Found Done tasks. Consider archiving with: ./scripts/bash/flush-backlog.sh"
          fi
```

**Behavior**:
- Runs on every PR and main push
- Outputs notice if Done tasks found
- Does NOT fail CI (advisory only)
- Uses continue-on-error: true

**Rationale**:
- Nudges developers to maintain clean backlog
- Doesn't block PR workflow (respects autonomy)
- Provides visibility into backlog hygiene

**Trade-offs**:
- Pro: Encourages good backlog hygiene
- Con: May be noise if team doesn't prioritize archiving

**References**:
- Platform design: `docs/platform/archive-tasks-integration.md` Section 3
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI job added to .github/workflows/ci.yml
- [ ] #2 Job runs archive-tasks.sh with --dry-run
- [ ] #3 Job uses continue-on-error: true (advisory, not blocking)
- [ ] #4 Job outputs notice message if Done tasks found
- [ ] #5 Job has descriptive name: Check for archivable tasks
<!-- AC:END -->
