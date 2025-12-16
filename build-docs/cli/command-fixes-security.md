# Command Fixes: `flowspec security`

## Current Status: PARTIALLY IMPLEMENTED

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Security scan | Working (requires semgrep) | None |
| Triage | PLACEHOLDER | HIGH |
| Fix | PLACEHOLDER | HIGH |
| Audit | PLACEHOLDER ("Phase 2") | HIGH |

## Issues Found

### Issue 1: TRIAGE COMMAND IS PLACEHOLDER
**Severity: High (Feature Not Implemented)**

The help text describes full functionality, but running it shows it's not implemented:
```
(Currently a placeholder for future implementation)
```

**Impact:** Users expecting AI-assisted triage will be disappointed.

**Recommendation:**
- Either implement the feature
- OR clearly mark as "Coming Soon" in help text
- OR remove from CLI until implemented

### Issue 2: FIX COMMAND IS PLACEHOLDER
**Severity: High (Feature Not Implemented)**

Same as triage - help describes functionality that doesn't exist.

**Recommendation:** Same as above.

### Issue 3: AUDIT COMMAND IS PLACEHOLDER
**Severity: High (Feature Not Implemented)**

Output explicitly says:
```
Audit command coming in Phase 2
```

**Recommendation:**
- Mark clearly in help text that this is coming in Phase 2
- OR hide command until implemented

### Issue 4: SEMGREP NOT BUNDLED
**Severity: Medium (External Dependency)**

The scan command requires semgrep to be installed separately:
```
⚠ semgrep not available
To install Semgrep: [installation instructions]
```

**Recommendation:**
- This is acceptable but could provide pre-check before init
- Consider bundling or auto-installing

## Recommendations

### Priority Fixes
1. **HIGH**: Either implement or clearly mark placeholders in help text
2. **MEDIUM**: Consider auto-installing semgrep or bundling

### Documentation Updates Needed
- Clearly mark which security commands are implemented vs placeholder
- Update help text to show "Coming in Phase 2" for audit

## Priority
**High** - Three major features are placeholders with misleading help text.

## Test Evidence
```
$ flowspec security scan .
⚠ semgrep not available
[installation instructions]

$ flowspec security audit .
Audit command coming in Phase 2
Would audit: .
Format: markdown, Compliance: None
```
