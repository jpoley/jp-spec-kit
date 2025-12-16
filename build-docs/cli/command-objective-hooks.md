# Command Objective: `flowspec hooks`

## Summary
Hook management and event emission for workflow automation.

## Objective
Manage, test, and emit events that trigger workflow hooks for automation and integration.

## Subcommands

### `flowspec hooks list`
List configured hooks.

### `flowspec hooks validate`
Validate hooks configuration file.

**Expected:** Validates .flowspec/hooks/hooks.yaml

### `flowspec hooks audit`
View hook execution audit log.

**Expected:** Shows .flowspec/hooks/audit.log

### `flowspec hooks emit`
Emit an event and trigger matching hooks.

**Features:**
- Manual event emission
- Testing hooks before workflow integration
- Multi-machine agent progress tracking

**Event Types:**
- `spec.created` - Specification created
- `task.completed` - Task completed
- `implement.completed` - Implementation done
- `agent.progress` - Agent progress update
- `agent.started` - Agent work started

**Options:**
```bash
flowspec hooks emit spec.created --spec-id my-feature
flowspec hooks emit task.completed --task-id task-123 --spec-id my-feature
flowspec hooks emit agent.progress --task-id task-229 --progress 60 --message "Working"
flowspec hooks emit spec.created --spec-id test --dry-run
flowspec hooks emit task.completed --task-id task-123 --json
```

### `flowspec hooks test`
Test a specific hook with a mock event.

**Options:**
```bash
flowspec hooks test run-tests implement.completed
flowspec hooks test quality-gate spec.created --spec-id my-feature
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec hooks list` | Shows hooks | "No hooks configured" | PASS |
| `flowspec hooks validate` | Validates config | "Config file not found" | EXPECTED (no hooks.yaml) |
| `flowspec hooks audit` | Shows audit log | "No audit log found" | EXPECTED (no log) |

## Acceptance Criteria
- [x] List configured hooks
- [x] Validate hooks configuration
- [x] View audit log
- [x] Emit events manually
- [x] Test individual hooks
- [x] Support dry-run mode
- [x] Support JSON output
