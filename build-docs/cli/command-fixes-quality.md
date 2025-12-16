# Command Fixes: `flowspec quality`

## Current Status: WORKING (but defaults to wrong path)

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Quality scoring | Working when file exists | None |
| Multi-dimensional analysis | Working | None |
| JSON output | Working | None |
| Threshold validation | Working | None |
| CI integration | Working | None |

## Issues Found

### Issue 1: DEFAULT PATH INCONSISTENCY
**Severity: Low**

The help text says:
```
SPEC_PATH  Path to specification file (defaults to .flowspec/spec.md)
```

But the error shows:
```
Error: Specification file not found: /home/jpoley/ps/flowspec/spec.md
```

The default seems to look for `spec.md` in current directory, not `.flowspec/spec.md`.

**Recommendation:**
- Either fix the default path to match documentation
- OR update help text to reflect actual behavior

### Issue 2: EXIT CODE DOCUMENTATION
**Severity: Low**

Help mentions exit codes but doesn't list them. The gate command shows:
```
Exit codes: 0=passed, 1=failed, 2=error
```

Quality should have similar documentation.

## Recommendations

### Priority Fixes
1. **LOW**: Clarify default path behavior
2. **LOW**: Add exit code documentation to help

## Priority
**Low** - Minor documentation inconsistencies.

## Test Evidence
```
$ flowspec quality
Error: Specification file not found: /home/jpoley/ps/flowspec/spec.md

Usage:
  flowspec quality [SPEC_PATH]
  flowspec quality .flowspec/spec.md
```
