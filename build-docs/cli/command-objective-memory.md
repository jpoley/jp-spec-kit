# Command Objective: `flowspec memory`

## Summary
Task memory management for maintaining implementation context across sessions.

## Objective
Provide persistent memory storage for task context, allowing agents to maintain state and share information across sessions.

## Subcommands

### `flowspec memory init <task_id>`
Initialize a new task memory file from template.

**Options:**
```bash
flowspec memory init task-389                          # Basic init
flowspec memory init task-389 --title "Login feature"  # With title
flowspec memory init task-389 --force                  # Overwrite existing
```

### `flowspec memory show <task_id>`
Display task memory content.

**Options:**
```bash
flowspec memory show task-389
flowspec memory show task-389 --archived
flowspec memory show task-389 --plain
```

### `flowspec memory append <task_id>`
Append content to task memory.

### `flowspec memory list`
List all task memories.

### `flowspec memory search`
Search across task memories.

### `flowspec memory clear`
Clear task memory content.

### `flowspec memory cleanup`
Cleanup old task memories.

### `flowspec memory stats`
Show task memory statistics.

### `flowspec memory import`
Import context into task memory.

### `flowspec memory export`
Export task memory to file.

### `flowspec memory template`
Manage memory templates.

**Actions:**
```bash
flowspec memory template list                        # List templates
flowspec memory template show feature                # Show template content
flowspec memory template apply feature --task task-389  # Apply to task
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec memory list` | List memories | "No active task memories found" | PASS |
| `flowspec memory stats` | Show statistics | Shows counts (all 0) | PASS |

## Acceptance Criteria
- [x] Initialize task memories
- [x] Show memory content
- [x] Append to memories
- [x] List all memories
- [x] Search across memories
- [x] Clear memory content
- [x] Cleanup old memories
- [x] Show statistics
- [x] Import/export capabilities
- [x] Template management
