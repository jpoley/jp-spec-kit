# ADR-003: Task Memory Lifecycle Trigger Mechanism

**Status**: Accepted
**Date**: 2025-12-09
**Decision Makers**: Architecture Team, Enterprise Software Architect

## Context

Task Memory storage (ADR-001) and context injection (ADR-002) define *what* and *how*. This ADR addresses *when*: **how and when are task memory files created, archived, and deleted?**

### Requirements

1. **Automatic lifecycle management**: No manual memory file management
2. **Deterministic triggers**: Clear, predictable behavior
3. **Reliable operations**: Must work offline, no external dependencies
4. **Visible operations**: Developers understand what happened
5. **State consistency**: Memory lifecycle matches task lifecycle

### Key Questions

1. When is memory created?
2. When is memory archived?
3. When is memory deleted?
4. What happens on state transitions (Done → In Progress)?
5. How do we ensure operations are reliable?

## Decision

**Use CLI hooks triggered by backlog state transitions**

### Lifecycle State Machine

```
                   create memory
    ┌─────────────────────────────────┐
    │                                 │
    │  backlog task edit -s "In Progress"
    │                                 │
    ▼                                 │
┌────────┐                     ┌──────────────┐
│ To Do  │────────────────────▶│ In Progress  │
└────────┘                     └──────────────┘
                                       │
                                       │ backlog task edit -s "Done"
                                       │ (archive memory)
                                       │
                                       ▼
                               ┌──────────────┐
                               │     Done     │
                               └──────────────┘
                                       │
                                       │ backlog task archive
                                       │ (delete memory)
                                       │
                                       ▼
                               ┌──────────────┐
                               │   Archive    │
                               └──────────────┘
```

### Trigger Points

| State Transition | Memory Action | Hook Location |
|------------------|---------------|---------------|
| `To Do → In Progress` | **Create** `backlog/memory/task-{id}.md` | `on_task_start()` |
| `In Progress → Done` | **Archive** to `backlog/memory/archive/task-{id}.md` | `on_task_complete()` |
| `Done → Archive` | **Delete** memory file | `on_task_archive()` |
| `Done → In Progress` | **Restore** from archive if exists | `on_task_reopen()` |
| `In Progress → In Progress` (reopen) | **Restore** from archive if exists | `on_task_reopen()` |

### Implementation: CLI Lifecycle Hooks

**Location**: `src/specify_cli/commands/task_edit.py`

```python
# Hook integration in backlog task edit command

def handle_state_change(task_id: str, old_state: str, new_state: str):
    """Execute lifecycle hooks on task state changes."""
    lifecycle = LifecycleManager()

    # Trigger appropriate hook
    if old_state == "To Do" and new_state == "In Progress":
        lifecycle.on_task_start(task_id)

    elif old_state == "In Progress" and new_state == "Done":
        lifecycle.on_task_complete(task_id)

    elif old_state == "Done" and new_state == "Archive":
        lifecycle.on_task_archive(task_id)

    elif new_state == "In Progress" and old_state in ["Done", "Archive"]:
        lifecycle.on_task_reopen(task_id)
```

**Lifecycle Manager Implementation**:

```python
# backlog/lifecycle.py

class LifecycleManager:
    def on_task_start(self, task_id: str):
        """Create task memory when task starts."""
        # 1. Create memory file from template
        memory_path = memory_store.create(task_id)

        # 2. Update CLAUDE.md with @import reference
        self._update_claude_md(task_id)

        # 3. Log operation
        logger.info(f"Created task memory: {memory_path}")

    def on_task_complete(self, task_id: str):
        """Archive task memory when task completes."""
        # 1. Move memory to archive/
        archive_path = memory_store.archive(task_id)

        # 2. Clear active task reference in CLAUDE.md
        self._update_claude_md(None)

        # 3. Log operation
        logger.info(f"Archived task memory: {archive_path}")

    def on_task_archive(self, task_id: str):
        """Delete task memory when task is archived."""
        # 1. Delete archived memory file
        memory_store.delete(task_id)

        # 2. Log operation
        logger.info(f"Deleted task memory: {task_id}")

    def on_task_reopen(self, task_id: str):
        """Restore task memory when task is reopened."""
        # 1. Check if archived memory exists
        if memory_store.has_archived(task_id):
            # 2. Restore from archive
            memory_path = memory_store.restore(task_id)
        else:
            # 3. Create new memory if no archive
            memory_path = memory_store.create(task_id)

        # 4. Update CLAUDE.md
        self._update_claude_md(task_id)

        # 5. Log operation
        logger.info(f"Restored task memory: {memory_path}")

    def _update_claude_md(self, task_id: Optional[str]):
        """Update CLAUDE.md with active task reference."""
        claude_md_path = Path("backlog/CLAUDE.md")

        if task_id:
            import_line = f"@import memory/{task_id}.md"
        else:
            import_line = "<!-- No active task -->"

        # Replace placeholder with import line
        content = claude_md_path.read_text()
        updated = re.sub(
            r"@import memory/task-\d+\.md|<!-- No active task -->",
            import_line,
            content
        )
        claude_md_path.write_text(updated)
```

## Rationale

### Why CLI Hooks?

1. **Deterministic**: Triggers fire only on explicit state changes
2. **Reliable**: No external services, works offline
3. **Transparent**: Operations visible in CLI output
4. **Simple**: No daemon processes or background jobs
5. **Testable**: Unit test lifecycle manager independently

### Why Not Alternative Approaches?

**Git hooks**:
- ❌ Fire on git operations, not task state changes
- ❌ Complex to test
- ❌ Bypassed by `--no-verify`

**Background daemon**:
- ❌ Additional process to manage
- ❌ Complexity (startup, shutdown, monitoring)
- ❌ Resource overhead

**Manual commands**:
- ❌ High cognitive burden
- ❌ Error-prone (forget to create/archive)
- ❌ Defeats purpose of automation

**File system watchers**:
- ❌ Platform-specific
- ❌ Unreliable (events can be missed)
- ❌ Doesn't work on remote filesystems

### Why Archive Before Delete?

- **Safety**: Two-step deletion prevents accidental loss
- **Recoverability**: Can restore if task reopened
- **Audit trail**: Historical context preserved
- **User control**: Explicit "archive" action for final deletion

## Consequences

### Positive

- ✅ **Automatic**: Developers don't manage memory files manually
- ✅ **Deterministic**: Predictable behavior, easy to reason about
- ✅ **Reliable**: Works offline, no external dependencies
- ✅ **Visible**: CLI output shows memory operations
- ✅ **Testable**: Lifecycle manager can be unit tested
- ✅ **Safe**: Two-step deletion (archive then delete)

### Negative

- ⚠️ **Requires backlog CLI**: Only source of state changes
- ⚠️ **No cross-tool consistency**: Direct file edits bypass hooks
- ⚠️ **Hook execution time**: Adds ~10-50ms to CLI operations

### Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Hook execution fails | High | Low | Transaction rollback, error logging |
| Developer bypasses CLI | Medium | Low | Documentation, linting |
| Multiple concurrent tasks | Low | Medium | CLI validates single active task |
| Hook adds latency | Low | Medium | Async operations, <50ms target |

## Alternatives Considered

### Alternative 1: Manual Memory Management

Require developers to explicitly create/archive memory files.

**Rejected because**:
- High cognitive burden
- Error-prone
- Defeats automation purpose
- Not scalable

### Alternative 2: Git Hooks

Use git pre-commit/post-commit hooks to trigger memory operations.

**Rejected because**:
- Fires on git operations, not task operations
- Can be bypassed with `--no-verify`
- Complex to test and debug
- Not guaranteed to fire (offline work)

### Alternative 3: File System Watchers

Watch task files for changes, trigger memory operations.

**Rejected because**:
- Platform-specific implementations
- Unreliable (events can be dropped)
- Doesn't work on network filesystems
- Requires background daemon

### Alternative 4: Database Triggers

Use SQLite triggers if we adopted database storage.

**Rejected because**:
- Requires database (ADR-001 chose file-based)
- Complex migrations
- Not human-readable
- Overkill for lifecycle management

## Implementation Considerations

### Error Handling

**Challenge**: What if memory creation fails?

**Solution**: Transactional rollback

```python
def on_task_start(self, task_id: str):
    try:
        # Create memory
        memory_path = memory_store.create(task_id)

        # Update CLAUDE.md
        self._update_claude_md(task_id)

    except Exception as e:
        # Rollback: delete memory if created
        memory_store.delete_if_exists(task_id)

        # Clear CLAUDE.md import
        self._update_claude_md(None)

        # Re-raise with context
        raise LifecycleError(f"Failed to start task {task_id}") from e
```

### Concurrency

**Challenge**: What if multiple tasks in progress simultaneously?

**Solution**: CLI validation

```python
def validate_single_active_task(new_task_id: str):
    """Ensure only one task is active at a time."""
    state = read_backlog_state()

    if state.active_task and state.active_task != new_task_id:
        raise ValidationError(
            f"Task {state.active_task} is already in progress. "
            f"Complete it before starting {new_task_id}."
        )
```

### Idempotency

**Challenge**: What if hook is triggered multiple times?

**Solution**: Idempotent operations

```python
def create(self, task_id: str) -> Path:
    """Create memory file (idempotent)."""
    memory_path = self._get_path(task_id)

    if memory_path.exists():
        # Already exists, log and return
        logger.debug(f"Memory already exists: {memory_path}")
        return memory_path

    # Create from template
    template = self._load_template()
    memory_path.write_text(template.render(task_id=task_id))

    return memory_path
```

### Performance

**Target**: Hook execution < 50ms

**Operations**:
- File creation: ~5-10ms
- CLAUDE.md update: ~5-10ms
- Total: ~10-20ms (well under target)

## Success Criteria

1. **Automatic creation**: Memory created when task starts, 100% of time
2. **Automatic archival**: Memory archived when task completes, 100% of time
3. **Deterministic**: Same input always produces same output
4. **Fast**: Hook execution < 50ms
5. **Visible**: CLI output confirms operations
6. **Recoverable**: Failed operations can be retried

## Integration with Other ADRs

- **ADR-001**: Defines memory file locations that hooks manage
- **ADR-002**: Hooks update CLAUDE.md @import for context injection
- **ADR-004**: Hooks create files that sync via git

## References

- [Task Memory System Architecture](../architecture/task-memory-system.md)
- [ADR-001: Storage Mechanism](./ADR-001-task-memory-storage.md)
- [ADR-002: Context Injection](./ADR-002-task-memory-context-injection.md)
- [Backlog.md CLI Documentation](https://github.com/jpoley/backlog.md)

## Notes

This ADR establishes the lifecycle automation that makes Task Memory seamless for developers. The CLI hook approach balances simplicity, reliability, and transparency.

**Implementation tracked in**:
- task-384 (LifecycleManager component)
- task-385 (CLI lifecycle hooks integration)
