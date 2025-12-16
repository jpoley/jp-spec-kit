# Command Objective: `flowspec constitution`

## Summary
Constitution management commands for project governance documents.

## Objective
Manage, validate, and update project constitution files that define governance rules and project standards.

## Subcommands

### `flowspec constitution validate`
Validate constitution for NEEDS_VALIDATION markers.

**Features:**
- Scans for NEEDS_VALIDATION markers
- Reports uncustomized sections
- CI-friendly exit codes

**Exit Codes:**
- 0: Validation passed (no markers)
- 1: Validation failed (markers found or file not found)

**Options:**
```bash
flowspec constitution validate                 # Validate default location
flowspec constitution validate --path my.md    # Custom file path
flowspec constitution validate --verbose       # Detailed output
```

### `flowspec constitution version`
Show constitution version information.

**Features:**
- Shows constitution version
- Shows tier (light/medium/heavy)
- Shows ratification dates
- Shows template version comparison

**Options:**
```bash
flowspec constitution version
```

### `flowspec constitution diff`
Compare project constitution against template.

**Features:**
- Shows differences from template
- Identifies customizations
- Compares against specific tier

**Options:**
```bash
flowspec constitution diff                     # Compare to medium tier
flowspec constitution diff --tier heavy        # Compare to heavy tier
flowspec constitution diff --tier light --verbose
flowspec constitution diff --path /path/to/project
```

### `flowspec constitution merge`
Merge template updates into project constitution.

**Features:**
- Preserves customized sections (SECTION markers)
- Updates non-customized sections
- Adds new sections from template
- Dry-run preview mode

**Options:**
```bash
flowspec constitution merge                    # Merge from medium tier
flowspec constitution merge --tier heavy       # Merge from heavy tier
flowspec constitution merge --dry-run          # Preview changes
flowspec constitution merge --output /tmp/const.md
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec constitution validate` | Checks markers | "Validation Passed" | PASS |
| `flowspec constitution version` | Shows version info | Shows version, tier, dates | PASS |
| Help for diff | Shows options | Shows options | PASS |
| Help for merge | Shows options | Shows options | PASS |

## Acceptance Criteria
- [x] Validate for NEEDS_VALIDATION markers
- [x] Show constitution version info
- [x] Compare against templates
- [x] Merge template updates
- [x] Preserve customizations during merge
- [x] Support dry-run mode
