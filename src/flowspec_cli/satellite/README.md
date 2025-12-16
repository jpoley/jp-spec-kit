# Satellite Mode

Remote provider integration for Backlog.md, enabling synchronization with external task trackers like GitHub Issues, Jira, and Notion.

## Overview

Satellite Mode extends Backlog.md with bidirectional sync capabilities, allowing you to:
- Pull tasks from remote providers
- Push local tasks to remote systems
- Maintain sync state and resolve conflicts
- Track compliance and audit trails

## Components

### Task Schema Migration

The migration module provides tools for upgrading Backlog.md tasks from schema v1 to v2.

**Files:**
- `migration.py` - Core migration logic

**Usage:**

```python
from specify_cli.satellite import TaskMigrator, migrate_tasks_cli

# Single file migration
migrator = TaskMigrator()
migrator.migrate(Path("backlog/tasks/task-001.md"))

# Bulk migration
results = migrator.migrate_bulk(Path("backlog/tasks"))

# CLI-friendly function
exit_code = migrate_tasks_cli(
    tasks_dir="backlog/tasks",
    dry_run=True,      # Preview changes
    verbose=True,      # Detailed output
    cleanup=False      # Keep backups
)
```

**Schema Changes (v1 → v2):**

v2 adds optional fields for remote sync and compliance:

```yaml
---
id: task-001
title: Example task
status: To Do

# NEW: Upstream sync fields (optional)
upstream:
  provider: github
  id: owner/repo#123
  url: https://github.com/owner/repo/issues/123
  synced_at: "2025-11-25T10:30:00Z"
  etag: abc123

# NEW: Compliance fields (optional)
compliance:
  spec_version: "1.2.3"
  spec_ref: "spec.md#feature-x"
  pr_url: "https://github.com/owner/repo/pull/456"
  audit_trail:
    - timestamp: "2025-11-25T10:30:00Z"
      action: "created"
      actor: "@user"

# NEW: Schema version identifier
schema_version: "2"
---
```

**Backward Compatibility:**

- v1 tasks remain valid (schema_version defaults to "1")
- All v1 fields are preserved during migration
- Only `schema_version` is added to v1 tasks
- `upstream` and `compliance` blocks are NOT added unless explicitly set
- Migration is idempotent (safe to run multiple times)

**Features:**

- Atomic file updates with automatic backup/restore
- Dry-run mode to preview changes
- Comprehensive error handling
- Batch migration with progress tracking
- Validation and verification

**Example:**

```bash
# Dry-run migration
python -c "from specify_cli.satellite import migrate_tasks_cli; \
    migrate_tasks_cli('backlog/tasks', dry_run=True, verbose=True)"

# Actual migration with cleanup
python -c "from specify_cli.satellite import migrate_tasks_cli; \
    migrate_tasks_cli('backlog/tasks', cleanup=True)"
```

## Testing

Run migration tests:

```bash
uv run pytest tests/test_migration*.py -v
uv run pytest tests/test_backward_compatibility.py -v
```

## Future Components

The following components are planned but not yet implemented:

### Provider Registry (task-018)
- Factory pattern for remote provider instances
- Auto-detection from task ID patterns
- Lazy initialization
- Extensible for custom providers

### Secret Management (task-019)
- Platform-native keychain integration
- Environment variable fallback
- CLI tool integration (gh, jira)
- Interactive token prompts

### Sync Engine (task-020)
- Bidirectional sync algorithm
- Conflict detection and resolution
- Incremental sync using ETags
- State machine for sync operations

## Design Documentation

See `backlog/docs/satellite-mode-subsystems-design.md` for detailed design specifications.

## License

Part of Flowspec - see main README for license information.
