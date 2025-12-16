# Command Objective: `flowspec workflow`

## Summary
Validate workflow configuration files.

## Objective
Ensure flowspec_workflow.yml files are valid through schema and semantic validation.

## Subcommands

### `flowspec workflow validate`
Validate workflow configuration file.

**Features:**
- JSON schema validation (structural)
- Semantic validation (circular dependencies, reachability)
- Support for v2.0+ and v1.x formats
- JSON output for CI/CD

**Exit Codes:**
- 0: Validation passed (warnings are non-blocking)
- 1: Validation errors (schema or semantic)
- 2: File errors (not found, invalid YAML)

**Options:**
```bash
flowspec workflow validate                    # Validate default config
flowspec workflow validate --file custom.yml  # Validate custom config
flowspec workflow validate --verbose          # Show detailed output
flowspec workflow validate --json             # JSON output for CI
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec workflow validate` | Validates config | ✓ Validation passed | PASS |
| Schema validation | Passes valid config | Working | PASS |
| Semantic validation | Runs after schema | Working | PASS |

## Acceptance Criteria
- [x] Schema validation
- [x] Semantic validation
- [x] Verbose output mode
- [x] JSON output mode
- [x] Custom file path support
- [x] Proper exit codes
