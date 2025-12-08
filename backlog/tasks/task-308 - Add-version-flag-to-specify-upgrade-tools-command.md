---
id: task-308
title: Add --version flag to specify upgrade-tools command
status: In Progress
assignee:
  - '@claude'
created_date: '2025-12-07 23:51'
updated_date: '2025-12-08 00:50'
labels:
  - enhancement
  - cli
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to install a specific version of the CLI tool instead of always getting latest.

**Problem:**
- User couldn't upgrade to 0.2.322 because `uv tool install` always got 0.2.321
- No way to specify version for CLI installation

**Proposed Solution:**
Add `--version` flag to `specify upgrade-tools` command:
```bash
specify upgrade-tools --version 0.2.322
```

Or consider a new `specify install` command:
```bash
specify install --version 0.2.322
```

**Implementation Notes:**
- Pass version to `uv tool install specify-cli --from git+...@vX.X.X`
- Validate version exists as a tag
- Show available versions with `specify upgrade-tools --list-versions`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Users can install specific versions with --version flag
- [ ] #2 Version is validated against available releases
- [ ] #3 Clear error message if version doesn't exist
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan

### 1. Add CLI Arguments to `upgrade_tools` command
- `--version`: Specific version to install (e.g., "0.2.325" or "v0.2.325")
- `--list-versions`: Show available releases from GitHub API

### 2. Modify `_upgrade_jp_spec_kit` function
- Accept optional `target_version` parameter
- If provided, use that version instead of latest
- Validate version exists via GitHub releases API before installing

### 3. Add `_list_available_versions` function
- Fetch releases from GitHub API
- Display in user-friendly format with release dates
- Show current installed version for comparison

### 4. Version validation
- Strip leading 'v' if user provides it
- Check version exists in releases before attempting install
- Clear error message if version not found

### Files to modify:
- `src/specify_cli/__init__.py`: Add arguments and logic
<!-- SECTION:PLAN:END -->
