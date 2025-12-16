# Command Objective: `flowspec tasks`

## Summary
Generate tasks from spec/plan/tasks.md files into backlog format.

## Objective
Convert specification files into actionable tasks in the Backlog.md format, enabling proper task tracking and workflow integration.

## Features

### Core Features
1. **Task generation** - Parses spec/plan files to create tasks
2. **Multiple formats** - Supports backlog (default) and markdown (legacy)
3. **Dry-run mode** - Preview without creating files
4. **Overwrite control** - Option to overwrite existing tasks
5. **Source flexibility** - Can specify source file or directory

### Command Options
```bash
flowspec tasks generate                           # Generate from current dir
flowspec tasks generate --format backlog          # Default: Backlog.md format
flowspec tasks generate --format markdown         # Legacy tasks.md format
flowspec tasks generate --source ./feature-x      # From specific directory
flowspec tasks generate --dry-run                 # Preview without writing
flowspec tasks generate --overwrite               # Overwrite existing tasks
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec tasks generate --dry-run` | Shows preview | Error: No spec.md found | EXPECTED |
| `--format markdown` | Legacy format | "Not yet implemented" | KNOWN GAP |
| Source detection | Finds spec.md/tasks.md | Works when files exist | PASS |

## Acceptance Criteria
- [x] Supports 'generate' action
- [x] Generates backlog format tasks
- [ ] Generates legacy markdown format (NOT IMPLEMENTED)
- [x] Supports dry-run mode
- [x] Supports source path specification
- [x] Supports overwrite flag
- [x] Handles missing files gracefully
