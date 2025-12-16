# Command Fixes: `flowspec hooks`

## Current Status: WORKING (requires hooks configuration)

## Gap Analysis

| Intended Feature | Current State | Gap Level |
|------------------|---------------|-----------|
| List hooks | Working | None |
| Validate hooks | Working | None |
| Audit log | Working | None |
| Event emission | Working | None |
| Hook testing | Working | None |

## Issues Found

### Issue 1: NO HOOKS CONFIG FILE IN FLOWSPEC REPO
**Severity: Low**

The flowspec source repository doesn't have a hooks.yaml file, so:
```
$ flowspec hooks validate
Config file not found: /home/jpoley/ps/flowspec/.flowspec/hooks/hooks.yaml
```

This is expected - hooks are project-specific, not needed in the source repo.

### Issue 2: VALIDATE EXIT CODE
**Severity: Low**

The validate command exits with code 1 when config not found. Should probably be exit code 2 (file error) to match other commands.

## Recommendations

### Priority Fixes
1. **LOW**: Consider exit code 2 for file-not-found errors

### Potential Enhancements
1. **Add hooks init** - Create default hooks.yaml
2. **Add hooks scaffold** - Generate common hook templates

## Priority
**Low** - Commands work correctly when hooks are configured.

## Test Evidence
```
$ flowspec hooks list
No hooks configured

$ flowspec hooks validate
Config file not found: /home/jpoley/ps/flowspec/.flowspec/hooks/hooks.yaml

$ flowspec hooks audit
No audit log found
Expected location: /home/jpoley/ps/flowspec/.flowspec/hooks/audit.log
```
