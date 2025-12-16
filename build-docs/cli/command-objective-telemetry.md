# Command Objective: `flowspec telemetry`

## Summary
Manage telemetry settings and view usage statistics.

## Objective
Provide privacy-respecting telemetry for understanding workflow usage patterns, with full user control over data collection.

## Subcommands

### `flowspec telemetry enable`
Enable telemetry with opt-in consent.

### `flowspec telemetry disable`
Disable telemetry and revoke consent.

### `flowspec telemetry status`
Show current telemetry status and configuration.

### `flowspec telemetry stats`
Show telemetry statistics and usage patterns.

### `flowspec telemetry view`
View recent telemetry events.

### `flowspec telemetry clear`
Clear all collected telemetry data.

### `flowspec telemetry export`
Export telemetry data as JSON.

### `flowspec telemetry track-role`
Track a role selection event.

### `flowspec telemetry track-agent`
Track an agent invocation event.

### `flowspec telemetry track-handoff`
Track a handoff click event.

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec telemetry status` | Shows config | Shows disabled status | PASS |
| `flowspec telemetry stats` | Shows statistics | "No telemetry data found" | PASS |

## Acceptance Criteria
- [x] Enable/disable telemetry
- [x] Show telemetry status
- [x] Show usage statistics
- [x] View recent events
- [x] Clear telemetry data
- [x] Export data as JSON
- [x] Track role events
- [x] Track agent events
- [x] Track handoff events
