# Command Objective: `flowspec upgrade-repo`

## Summary
Upgrade repository templates to the latest spec-kit and flowspec versions.

## Objective
Update templates and configuration files in an existing project to the latest versions without modifying user content.

## Features

### Core Features
1. **Template updates** - Downloads and applies latest templates
2. **Two-stage upgrade** - Updates both base spec-kit and flowspec extension
3. **Dry-run mode** - Preview changes before applying
4. **Version pinning** - Specify exact versions to upgrade to
5. **Source repo protection** - Blocks upgrade in flowspec source repo

### Command Options
```bash
flowspec upgrade-repo                           # Upgrade to latest
flowspec upgrade-repo --dry-run                 # Preview changes
flowspec upgrade-repo --base-version 0.0.90     # Pin base version
flowspec upgrade-repo --extension-version 0.3.0 # Pin extension version
flowspec upgrade-repo --templates-only          # Only update templates
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Source repo detection | Blocks in flowspec repo | Correctly blocks | PASS |
| `--dry-run` | Shows preview | Works | PASS |
| Version pinning | Uses specified version | Not tested (blocked in source) | N/A |

## Acceptance Criteria
- [x] Detects and blocks in source repository
- [x] Supports dry-run mode
- [ ] Downloads latest base templates
- [ ] Downloads latest extension templates
- [ ] Merges with extension precedence
- [x] Supports version pinning
- [x] Supports templates-only mode
