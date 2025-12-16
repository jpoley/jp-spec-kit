# Command Fixes: `flowspec tasks`

## Current Status: PARTIALLY WORKING

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| Task generation (backlog) | Working when spec exists | None |
| Task generation (markdown) | NOT IMPLEMENTED | HIGH |
| Dry-run mode | Working | None |
| Source flexibility | Working | None |
| Error handling | Working | None |

## Issues Found

### Issue 1: LEGACY MARKDOWN FORMAT NOT IMPLEMENTED
**Severity: Medium**

The help text says:
```
2. markdown: Generates a single tasks.md file (legacy format)
```

But when you try to use it:
```
$ flowspec tasks generate --format markdown
[yellow]Legacy markdown format is not yet implemented.[/yellow]
```

**Recommendation:**
- Either implement the markdown format
- OR remove it from the help text
- OR clearly mark it as "Coming soon" in help

### Issue 2: ERROR MESSAGE CLARITY
**Severity: Low**

When no spec.md found, the error is clear:
```
Error: No spec.md or tasks.md found
```

This is appropriate behavior.

## Recommendations

### Priority Fixes
1. **MEDIUM**: Implement or remove markdown format option
2. **LOW**: Consider adding more detailed help for spec.md format expectations

## Priority
**Medium** - Feature advertised but not implemented.

## Test Evidence
```
$ flowspec tasks generate --dry-run
Source: /home/jpoley/ps/flowspec
Output: /home/jpoley/ps/flowspec/backlog
Format: backlog
DRY RUN MODE - No files will be created

Error: No spec.md or tasks.md found
```
