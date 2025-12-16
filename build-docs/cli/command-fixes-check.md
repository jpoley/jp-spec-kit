# Command Fixes: `flowspec check`

## Current Status: WORKING

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Tool detection | Working | None |
| Version display | Working | None |
| Recommendations | Working | None |

## Issues Found

### Minor Issue: VERSION MISMATCH WARNING
**Severity: Low (Informational)**

Output shows:
```
backlog-md version: 1.27.1 (recommended: 1.21.0)
Run 'flowspec backlog upgrade' to sync to recommended version
```

The "recommended" version (1.21.0) is OLDER than installed (1.27.1). This is confusing - it suggests downgrading when the user has a newer version.

**Recommendation:**
- Only show warning when installed < recommended
- Or clarify "tested version" vs "recommended version"

## Recommendations

### Potential Enhancements
1. **Add --json flag** - For CI/CD integration
2. **Add --quiet flag** - Only show failures
3. **Fix version comparison logic** - Don't suggest downgrade

## Priority
**Low** - Command works, version comparison logic could be improved.

## Test Evidence
```
$ flowspec check
Check Available Tools
├── ● Git version control (available)
├── ● Claude Code (available)
[...]
└── ● backlog-md (task management) (v1.27.1)

backlog-md version: 1.27.1 (recommended: 1.21.0)
```
