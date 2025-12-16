# Command Objective: `flowspec config`

## Summary
Manage Specify configuration settings.

## Objective
View and update workflow configuration, particularly validation settings for workflow transitions.

## Subcommands

### `flowspec config validation`
View or update workflow transition validation configuration.

**Features:**
- View current validation configuration
- Update validation mode per transition
- Configure approval keywords

**Validation Modes:**
- `none` - No validation required
- `keyword` - Requires keyword (e.g., APPROVED) in artifact
- `pull-request` - Requires PR approval

**Options:**
```bash
flowspec config validation --show                           # Show current config
flowspec config validation -t plan -m pull-request          # Set plan validation
flowspec config validation -t specify -m keyword -k PRD_APPROVED  # Custom keyword
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec config validation` | Shows config | Shows all transitions | PASS |
| Shows all transitions | Full list | Lists all 14 transitions | PASS |

## Acceptance Criteria
- [x] View validation configuration
- [x] Update transition validation mode
- [x] Configure custom keywords
- [x] Shows all workflow transitions
