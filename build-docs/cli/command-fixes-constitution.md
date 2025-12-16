# Command Fixes: `flowspec constitution`

## Current Status: WORKING (with minor issues)

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Validate markers | Working | None |
| Show version | Working | LOW (displays placeholders) |
| Compare to template | Working | None |
| Merge updates | Working | None |

## Issues Found

### Issue 1: VERSION SHOWS PLACEHOLDERS
**Severity: Low (Cosmetic)**

The version command shows placeholder values:
```
Version             [CONSTITUTION_VERSION]
Ratified            [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
Last Amended        [LAST_AMENDED_DATE]
```

This is because the flowspec source repo's constitution.md is a template with placeholders, not a filled-in constitution.

**Recommendation:**
- This is expected for the source repo
- Consider detecting template vs filled constitution
- Show cleaner message for template files

### Issue 2: VERSION PARSING ARTIFACT
**Severity: Low (Cosmetic)**

The "Ratified" line shows markdown formatting:
```
Ratified            [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
```

This is a parsing artifact - the markdown table row wasn't fully parsed.

**Recommendation:**
- Improve parsing to handle markdown table format
- Or strip markdown formatting from output

## Recommendations

### Priority Fixes
1. **LOW**: Improve version parsing for markdown artifacts
2. **LOW**: Detect template vs filled constitution

## Priority
**Low** - Minor cosmetic issues, core functionality works.

## Test Evidence
```
$ flowspec constitution validate
╭───────────────────────────── Validation Passed ──────────────────────────────╮
│ ✓ Constitution is fully validated                                            │
│ No NEEDS_VALIDATION markers found. Your constitution is ready to use.        │
╰──────────────────────────────────────────────────────────────────────────────╯

$ flowspec constitution version
╭──────────────────────────── Constitution Version ────────────────────────────╮
│   Version             [CONSTITUTION_VERSION]                                 │
│   Tier                Medium                                                 │
│   Ratified            [RATIFICATION_DATE] | **Last Amended**: [...]          │
│   Last Amended        [LAST_AMENDED_DATE]                                    │
│   Template Version    1.0.0                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯

⚠  Template version 1.0.0 is available
```
