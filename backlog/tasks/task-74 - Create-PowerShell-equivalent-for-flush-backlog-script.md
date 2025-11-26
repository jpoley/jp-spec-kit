---
id: task-74
title: Create PowerShell equivalent for flush-backlog script
status: To Do
assignee: []
created_date: '2025-11-26 16:50'
labels:
  - script
  - powershell
  - windows
dependencies:
  - task-69
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create PowerShell version of flush-backlog.sh for Windows users, maintaining feature parity with the bash version. This enables cross-platform support for the jp-spec-kit distribution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script accepts equivalent flags: -DryRun, -NoSummary, -AutoCommit, -Help
- [ ] #2 Implements same validation logic using PowerShell cmdlets (Test-Path, Where-Object)
- [ ] #3 Generates identical summary format to bash version for consistency
- [ ] #4 Handles Windows path separators correctly (backslash vs forward slash)
- [ ] #5 Works on both PowerShell 5.1 (Windows) and PowerShell 7+ (cross-platform)
<!-- AC:END -->
