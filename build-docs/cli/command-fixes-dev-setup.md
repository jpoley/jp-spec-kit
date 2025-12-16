# Command Fixes: `flowspec dev-setup`

## Current Status: WORKING (but documentation misleading)

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Symlink creation | Working | None |
| Source repo detection | Working | None |
| VS Code settings | Working | None |

## Issues Found

### Issue 1: DOCUMENTATION MISLEADING
**Severity: Medium (Documentation)**

The CLAUDE.md says:
> "dev-setup is ONLY for building flowspec - no one else"

But the help text doesn't make this sufficiently clear to users. Users might confuse this with project setup.

**Recommendation:**
- Update help text to be EXPLICIT: "FOR FLOWSPEC DEVELOPERS ONLY"
- Add warning banner when running
- Consider renaming to `flowspec dev:setup` or `flowspec internal-dev-setup`

### Issue 2: BROKEN SYMLINKS WARNING
**Severity: Low (Cosmetic)**

The command reports "44 broken symlinks" but doesn't explain what this means or if it's a problem.

**Output observed:**
```
├── ● Verify symlinks (44 broken symlinks)
```

**Recommendation:**
- Clarify if broken symlinks are expected or need action
- Provide details on which symlinks are broken

## Recommendations

### Priority Fixes
1. **HIGH**: Update documentation to be explicit about scope
2. **LOW**: Clarify broken symlinks warning

## Priority
**Medium** - Documentation clarification needed.

## Test Evidence
```
$ flowspec dev-setup --force
[...]
├── ● Verify symlinks (44 broken symlinks)
└── ● Dev setup complete (ready for development)
```
