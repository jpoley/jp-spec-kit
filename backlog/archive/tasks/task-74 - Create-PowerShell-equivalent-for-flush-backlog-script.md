---
id: task-74
title: Create PowerShell equivalent for flush-backlog script
status: Done
assignee:
  - '@claude'
created_date: '2025-11-26 16:50'
updated_date: '2025-11-26 17:04'
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
- [x] #1 Script accepts equivalent flags: -DryRun, -NoSummary, -AutoCommit, -Help
- [x] #2 Implements same validation logic using PowerShell cmdlets (Test-Path, Where-Object)
- [x] #3 Generates identical summary format to bash version for consistency
- [x] #4 Handles Windows path separators correctly (backslash vs forward slash)
- [x] #5 Works on both PowerShell 5.1 (Windows) and PowerShell 7+ (cross-platform)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review task-69 and task-70 requirements to understand bash script functionality
2. Create scripts/powershell directory if needed
3. Implement flush-backlog.ps1 with PowerShell-native cmdlets
4. Ensure parameter compatibility (Help, DryRun, NoSummary, AutoCommit)
5. Test on PowerShell Core (cross-platform compatibility)
6. Verify path handling works on both Windows and Linux
7. Document any platform-specific considerations
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented PowerShell equivalent of flush-backlog script with full feature parity:

- Created scripts/powershell/flush-backlog.ps1 with comprehensive help documentation
- Implemented all required flags: -DryRun, -NoSummary, -AutoCommit, -Help
- Used PowerShell-native cmdlets: Test-Path, Get-Command, Join-Path, Get-ChildItem, Where-Object
- Generates identical summary format to bash version including task metadata, statistics, and relative links
- Handles path separators using Join-Path for cross-platform compatibility
- Compatible with both PowerShell 5.1 (Windows) and PowerShell 7+ (cross-platform)
- Follows exit code specification: 0=success, 1=validation error, 2=no tasks, 3=partial failures
- Includes verbose logging support via -Verbose flag
- Properly parses backlog CLI output and handles YAML frontmatter
- URL-encodes filenames in markdown links for special characters

Script structure follows existing PowerShell scripts in the repository with consistent error handling, help documentation, and parameter validation.
<!-- SECTION:NOTES:END -->
