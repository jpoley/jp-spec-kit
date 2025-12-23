# Task Memory Injection

## Overview

Task Memory Injection is a feature that automatically loads task context into Claude Code sessions via the `@import` directive in `backlog/CLAUDE.md`. This ensures agents have immediate access to task-specific context without manual file navigation.

## How It Works

### Automatic Injection via Hooks

When you start a Claude Code session or transition a task to "In Progress", the system:

1. **Detects Active Tasks**: Identifies tasks with status "In Progress" in `backlog/backlog.md`
2. **Applies Token-Aware Truncation**: Ensures memory content stays within 2000 token limit
3. **Updates CLAUDE.md**: Injects `@import ../memory/{task-id}.md` directive
4. **Loads Context**: Claude Code automatically reads the imported file

### Token-Aware Truncation

Large task memory files are automatically truncated to prevent context overflow:

- **Token Limit**: 2000 tokens per task (configurable)
- **Estimation**: ~4 characters per token (conservative estimate)
- **Preservation Strategy**:
  - Header and metadata: Always preserved
  - Context section: Always preserved (most recent context)
  - Key Decisions: Preserved if space allows
  - Notes: Truncated from oldest content first
- **Truncation Notice**: When content is truncated, a notice is added to the file

### File Locations

```
project/
├── backlog/
│   ├── CLAUDE.md                    # Contains @import directive
│   └── memory/
│       ├── task-375.md              # Original memory file
│       └── task-375.truncated.md    # Truncated version (if needed)
```

## Configuration

### Max Tokens

The default token limit is 2000 tokens. To customize:

```python
from flowspec_cli.memory.injector import ContextInjector

# Create injector with custom limit
injector = ContextInjector(max_tokens=1000)
```

### Disable Truncation

To use the non-truncating version (not recommended):

```python
injector.update_active_task(task_id)  # No truncation
```

## Usage Examples

### Automatic Injection (Recommended)

Task memory is injected automatically when:

1. **Starting a Claude Code Session**: The session-start hook detects active tasks
2. **Task State Transitions**: When task moves to "In Progress"

```bash
# Start a task (triggers automatic injection)
backlog task edit task-375 -s "In Progress"

# Memory is now available in Claude Code session
```

### Manual Injection

You can manually trigger injection via the CLI:

```bash
# Inject specific task memory
flowspec memory inject task-375

# Clear active task context
flowspec memory clear
```

### Via Python API

```python
from pathlib import Path
from flowspec_cli.memory.injector import ContextInjector

# Initialize
injector = ContextInjector(base_path=Path.cwd())

# Inject task memory (with truncation)
injector.update_active_task_with_truncation("task-375")

# Check active task
active = injector.get_active_task_id()
print(f"Active task: {active}")

# Clear active task
injector.clear_active_task()
```

## CLAUDE.md Structure

The injection system maintains an "Active Task Context" section in `backlog/CLAUDE.md`:

```markdown
# Backlog Context

(Your existing content)

## Active Task Context

@import ../memory/task-375.md

(Or for truncated versions)
@import ../memory/task-375.truncated.md
```

## Lifecycle Integration

The injection system is integrated with task lifecycle management:

| State Transition | Memory Action | @import Status |
|------------------|---------------|----------------|
| To Do → In Progress | Create memory | Inject |
| In Progress → Done | Archive memory | Clear |
| Done → Archive | Delete memory | N/A |
| Done → In Progress | Restore memory | Inject |
| In Progress → To Do | Delete memory | Clear |

## MCP Integration

Task memory is also available via MCP resources for on-demand access:

```javascript
// Get specific task memory
const memory = await client.readResource("backlog://memory/task-375");

// Get active task memory
const active = await client.readResource("backlog://memory/active");
```

See [MCP Resources](./mcp-resources.md) for details.

## Truncation Details

### Sections Preserved (Priority Order)

1. **Header** (always): Task ID, metadata, title
2. **Context** (always): Most recent implementation context
3. **Key Decisions** (if space): Important architectural/design choices
4. **Notes** (partial): Oldest content truncated first

### Example Truncation

**Original (3000 tokens):**
```markdown
# Task Memory: task-375
**Created**: 2025-12-20
**Task**: Implement authentication

## Context
Current sprint focuses on OAuth2 implementation.

## Key Decisions
- Use Authorization Code flow
- Store tokens in HttpOnly cookies
- Implement PKCE for public clients

## Notes
- 2025-12-20: Started research
- 2025-12-21: Designed token storage
... (hundreds of lines)
```

**Truncated (2000 tokens):**
```markdown
# Task Memory: task-375
**Created**: 2025-12-20
**Task**: Implement authentication

## Context
Current sprint focuses on OAuth2 implementation.

## Key Decisions
- Use Authorization Code flow
- Store tokens in HttpOnly cookies
- Implement PKCE for public clients

## Notes
- 2025-12-20: Started research
- 2025-12-21: Designed token storage
... (only recent notes included)

*[Content truncated - exceeded 2000 token limit]*
```

## Troubleshooting

### Memory Not Loading

**Symptom**: Task memory not visible in Claude Code session

**Solutions**:
1. Check CLAUDE.md contains `@import` directive:
   ```bash
   cat backlog/CLAUDE.md | grep "@import"
   ```

2. Verify memory file exists:
   ```bash
   ls -la backlog/memory/task-*.md
   ```

3. Manually trigger injection:
   ```bash
   flowspec memory inject task-375
   ```

### Token Limit Exceeded

**Symptom**: Warning about truncation in logs

**Solutions**:
1. Review and clean up old notes in memory file
2. Archive completed work to separate documentation
3. Increase token limit (if appropriate):
   ```python
   injector = ContextInjector(max_tokens=3000)
   ```

### Truncated File Not Cleaned Up

**Symptom**: Old `.truncated.md` files accumulate

**Expected Behavior**: Truncated files are overwritten on re-injection, not deleted on clear (preserved for archival)

**Cleanup**: Run memory cleanup command:
```bash
flowspec memory cleanup --truncated
```

## Security Considerations

- **Token Limits**: Prevent context overflow attacks
- **File Permissions**: Memory files inherit standard permissions
- **Content Validation**: No content validation (trusted source)
- **Path Traversal**: Task IDs validated (format: `task-\d+`)

## Performance

- **Token Estimation**: O(1) character-based approximation
- **Truncation**: O(n) line-by-line processing
- **Injection**: O(1) file write
- **Typical Overhead**: < 50ms per injection

## Best Practices

1. **Keep Context Current**: Update Context section frequently
2. **Archive Old Notes**: Move completed work to docs
3. **Use Key Decisions**: Document important choices for AI context
4. **Monitor Size**: Review memory files that hit truncation limit
5. **Clear When Done**: Tasks completed should archive (auto-clears import)

## Related Documentation

- [Backlog User Guide](../guides/backlog-user-guide.md)
- [Task Memory CLI](../guides/backlog-quickstart.md#task-memory)
- [MCP Resources](./mcp-resources.md)
- [Workflow Integration](../guides/flowspec-backlog-workflow.md)

## API Reference

### ContextInjector

```python
class ContextInjector:
    """Manages injection of task memory into CLAUDE.md."""

    def __init__(self, base_path: Path = None, max_tokens: int = 2000):
        """Initialize with optional base path and token limit."""

    def update_active_task_with_truncation(self, task_id: str | None) -> None:
        """Update CLAUDE.md with token-aware truncation."""

    def update_active_task(self, task_id: str | None) -> None:
        """Update CLAUDE.md without truncation (not recommended)."""

    def clear_active_task(self) -> None:
        """Remove @import from CLAUDE.md."""

    def get_active_task_id(self) -> str | None:
        """Get currently active task ID."""

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (~4 chars/token)."""

    def truncate_memory_content(self, content: str) -> str:
        """Truncate content to max_tokens, preserving important sections."""
```

### LifecycleManager

```python
class LifecycleManager:
    """Manages task memory lifecycle on state changes."""

    def on_state_change(
        self,
        task_id: str,
        old_state: str,
        new_state: str,
        task_title: str = ""
    ) -> None:
        """Handle task state transition (auto-injects with truncation)."""

    def update_active_task_import(self, task_id: str | None) -> None:
        """Manually update active task import (uses truncation)."""
```

## Version History

- **v0.4.0** (2025-12-22): Added token-aware truncation
- **v0.3.0** (2025-12-20): Initial @import injection support
