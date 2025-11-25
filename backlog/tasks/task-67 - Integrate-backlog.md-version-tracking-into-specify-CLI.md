---
id: task-67
title: Integrate backlog.md version tracking into specify CLI
status: Done
assignee:
  - '@claude'
created_date: '2025-11-25 21:42'
updated_date: '2025-11-25 23:13'
labels:
  - P0
  - integration
  - backlog-md
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add backlog.md as a tracked dependency alongside spec-kit, enabling unified version management, auto-install during init, and synchronized upgrades.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Extend .spec-kit-compatibility.yml with backlog-md section (min/max/tested/recommended versions)
- [x] #2 Add specify backlog install command that auto-detects pnpm/npm and installs validated version
- [x] #3 Add specify backlog upgrade command (or integrate into existing specify upgrade)
- [x] #4 During specify init, check for backlog.md and offer to install if missing
- [x] #5 Add --backlog-version flag to specify init for version pinning
- [x] #6 Update specify upgrade to check and sync backlog.md to validated version
- [x] #7 Add backlog.md version to specify check output
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update .spec-kit-compatibility.yml - Add backlog-md section with version tracking (min: 1.20.0, tested: 1.21.0, recommended: 1.21.0)

2. Add VersionManager utility in __init__.py:
   - load_compatibility_matrix() - parse YAML config
   - get_validated_version(dependency) - get recommended version
   - check_installed_version(tool) - run tool --version
   - is_compatible(tool, version) - semver range check

3. Add specify backlog install command:
   - Auto-detect pnpm vs npm (prefer pnpm)
   - Fetch validated version from compatibility matrix
   - Install with version pinning
   - Verify installation success

4. Add specify backlog upgrade command:
   - Check current installed version
   - Compare to recommended version
   - Upgrade if needed with pnpm/npm update

5. Enhance specify init:
   - Add --backlog-version flag
   - Check if backlog-md installed after template download
   - Offer to install if missing (confirm prompt)

6. Enhance specify upgrade:
   - Check backlog-md version after spec-kit upgrade
   - Offer to sync to validated version if out of range

7. Enhance specify check:
   - Add backlog-md to tool checks
   - Show version and compatibility status

8. Add tests for new functionality
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented comprehensive backlog-md version tracking integration:

**New Features:**
- `specify backlog install` - Auto-detect pnpm/npm, install validated version
- `specify backlog upgrade` - Upgrade to recommended version
- `specify init --backlog-version` - Pin backlog version during init
- `specify check` now shows backlog-md version and compatibility status
- `specify upgrade` now syncs backlog-md after spec-kit upgrade

**Files Modified:**
- `.spec-kit-compatibility.yml` - Added backlog-md compatibility section
- `src/specify_cli/__init__.py` - Added ~450 lines for version mgmt and commands

**Key Functions Added:**
- `load_compatibility_matrix()` - Parse YAML config
- `get_backlog_validated_version()` - Fetch recommended version
- `check_backlog_installed_version()` - Detect installed version
- `detect_package_manager()` - Auto-detect pnpm/npm
- `compare_semver()` - Simple version comparison

**Bug Fix:** Fixed version parsing to handle backlog output format (just version number).
<!-- SECTION:NOTES:END -->
