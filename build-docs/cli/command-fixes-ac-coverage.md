# Command Fixes: `flowspec ac-coverage`

## Current Status: WORKING (requires feature context)

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| AC extraction | Working | None |
| Test marker scanning | Working | None |
| Coverage calculation | Working | None |
| Feature detection | Requires --feature flag | LOW |

## Issues Found

### Issue 1: NO AUTO-DETECTION FALLBACK
**Severity: Low**

When run without --feature flag in a directory without feature context:
```
Error: Could not detect feature name. Use --feature option.
```

This is expected behavior, but the documentation could be clearer about what constitutes "feature context."

**Recommendation:**
- Document what files/paths are checked for feature detection
- Consider looking at .flowspec/config or backlog for current feature

## Recommendations

### Potential Enhancements
1. **Improve feature detection** - Check more sources for current feature
2. **Add verbose mode** - Show AC matching details

## Priority
**Low** - Requires explicit feature name, which is reasonable.

## Test Evidence
```
$ flowspec ac-coverage
Error: Could not detect feature name. Use --feature option.
```
