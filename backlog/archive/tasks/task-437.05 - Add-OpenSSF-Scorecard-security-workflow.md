---
id: task-437.05
title: Add OpenSSF Scorecard security workflow
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-11 03:28'
updated_date: '2025-12-15 02:18'
labels:
  - infrastructure
  - security
  - github
  - subtask
dependencies: []
parent_task_id: task-437
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement OpenSSF Scorecard for security best practices evaluation.

## File to Create

### `.github/workflows/scorecard.yml`

Configuration:
- **Triggers**:
  - Push to main branch
  - Weekly schedule (Saturdays 1:30 AM UTC)
  - Manual workflow_dispatch
- **Permissions**: read-all default, security-events write, id-token write, contents read
- **Steps**:
  1. Checkout with persist-credentials: false
  2. Run ossf/scorecard-action
  3. Upload SARIF artifact (5 day retention)
  4. Upload to GitHub code-scanning dashboard
- **Action versions**: Pinned with full commit SHA

## README Badge
Add OpenSSF Scorecard badge to README:
```markdown
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge)](https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec)
```

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/.github/workflows/scorecard.yml
- https://securityscorecards.dev/
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 scorecard.yml workflow triggers on push to main and weekly
- [x] #2 SARIF results uploaded to code-scanning dashboard
- [x] #3 Artifact uploaded with 5-day retention
- [x] #4 All action versions pinned with full commit SHA
- [x] #5 README badge displays current scorecard rating
- [x] #6 Workflow passes on first run
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created OpenSSF Scorecard security workflow:

1. .github/workflows/scorecard.yml
   - Triggers: push to main, weekly (Sat 1:30 AM UTC), manual
   - Permissions: read-all default, security-events/id-token/contents/actions per job
   - Actions pinned with full SHA:
     - checkout@b4ffde65f46336ab88eb53be808477a3936bae11 (v4.1.1)
     - ossf/scorecard-action@0864cf19026789058feabb7e87baa5f140aac736 (v2.3.1)
     - upload-artifact@26f96dfa697d77e81fd5907df203aa23a56210a8 (v4.3.0)
     - codeql-action/upload-sarif@e5f05b81d5b6ff8cfa111c80c22c5fd02a384118 (v3.23.0)
   - SARIF output with 5-day retention
   - publish_results: true for badge
   - Category: flowspec-scorecard

2. README.md updated with OpenSSF Scorecard badge
   - Links to scorecard.dev viewer
   - Badge auto-updates with score
<!-- SECTION:NOTES:END -->
