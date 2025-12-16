# Task Memory User Guide

**Version**: 1.0
**Last Updated**: 2025-12-09

## Overview

Task Memory is a persistent, task-scoped context management system that eliminates context loss when switching machines, resuming work after interruptions, or handing off tasks to team members. Every task in "In Progress" state automatically gets a memory file that travels with the task across sessions, machines, and tools.

**Key Benefits**:
- Reduce context rebuild time from 15-30 minutes to <2 minutes
- Enable seamless mid-task handoffs between team members
- Prevent repeated mistakes by documenting what didn't work
- Build searchable institutional knowledge from archived memories
- Foundation for ML-driven task insights and suggestions

## Quick Start

### 1. Start Working on a Task

When you transition a task to "In Progress", Task Memory is created automatically:

```bash
# Start work on task-42
backlog task edit task-42 -s "In Progress"

# Memory created at: backlog/memory/task-42.md
```

### 2. View Task Memory

```bash
# View current task memory
backlog memory view task-42

# View in JSON format (for scripting)
backlog memory view task-42 --format json
```

### 3. Add Context to Memory

You can append notes directly from the CLI:

```bash
# Record a decision
backlog memory append task-42 "Decision: Use FastAPI instead of Flask for better async support"

# Record an approach that didn't work
backlog memory append task-42 "Tried using SQLite, but performance was insufficient for our scale"

# Record an open question
backlog memory append task-42 "Question: Should we use Alembic or raw SQL for migrations?"
```

Or edit the file directly with your text editor:

```bash
# Open in your preferred editor
nvim backlog/memory/task-42.md
code backlog/memory/task-42.md
```

### 4. Complete the Task

When the task is done, memory is automatically archived:

```bash
# Mark task complete
backlog task edit task-42 -s Done

# Memory moved to: backlog/memory/archive/task-42.md
```

### 5. Sync Across Machines

Task memories sync automatically with git:

```bash
# On Machine A: Commit and push
git add backlog/memory/task-42.md
git commit -m "Update task memory for task-42"
git push

# On Machine B: Pull to get latest
git pull

# Memory is now available on Machine B
cat backlog/memory/task-42.md
```

## Task Memory Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TASK MEMORY LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐                                                      │
│   │  To Do   │  Memory does not exist                               │
│   └────┬─────┘                                                      │
│        │                                                             │
│        │ backlog task edit task-42 -s "In Progress"                 │
│        │                                                             │
│        ▼                                                             │
│   ┌─────────────────┐                                               │
│   │  In Progress    │  Memory created: backlog/memory/task-42.md    │
│   └────┬────────────┘                                               │
│        │                                                             │
│        │ • Agent reads memory for context                           │
│        │ • Human adds decisions, notes                              │
│        │ • Git syncs across machines                                │
│        │                                                             │
│        │ backlog task edit task-42 -s Done                          │
│        │                                                             │
│        ▼                                                             │
│   ┌─────────────────┐                                               │
│   │     Done        │  Memory archived: backlog/memory/archive/     │
│   └────┬────────────┘         task-42.md                            │
│        │                                                             │
│        │ backlog task edit task-42 --archive                        │
│        │                                                             │
│        ▼                                                             │
│   ┌─────────────────┐                                               │
│   │    Archived     │  Memory deleted (if --delete-memory flag)     │
│   └─────────────────┘                                               │
│                                                                      │
│   ┌─────────────────┐                                               │
│   │     Done        │  Memory restored from archive                 │
│   └────┬────────────┘                                               │
│        │ backlog task edit task-42 -s "In Progress"                 │
│        ▼                                                             │
│   ┌─────────────────┐                                               │
│   │  In Progress    │  Memory restored: backlog/memory/task-42.md   │
│   └─────────────────┘                                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Memory File Structure

Every task memory follows this standard structure:

```markdown
# Task Memory: task-42

**Created**: 2025-12-09T10:30:00Z
**Last Updated**: 2025-12-09T14:22:00Z

## Context

[Brief description of what this task is about]

## Key Decisions

- YYYY-MM-DD HH:MM - [Decision made and rationale]
- YYYY-MM-DD HH:MM - [Another decision with trade-offs explained]

## Approaches Tried

### Approach: [Name of approach]
**Result**: ✓ Success / ❌ Rejected
**Reason**: [Why this worked or didn't work]

### Approach: [Another approach]
**Result**: ❌ Rejected
**Reason**: [Detailed explanation of failure]

## Open Questions

- [Question or blocker #1]
- [Question or blocker #2]

## Resources

- [Link to relevant documentation]
- [Link to ADR or spec]
- [Link to research or discussion]

## Notes

[Freeform notes section for anything that doesn't fit above]
```

## CLI Commands Reference

### View Commands

| Command | Description | Example |
|---------|-------------|---------|
| `backlog memory view <task-id>` | Display task memory | `backlog memory view task-42` |
| `backlog memory view <task-id> --format json` | Output as JSON | `backlog memory view task-42 --format json` |
| `backlog memory list` | List all active memories | `backlog memory list` |
| `backlog memory list --archived` | List archived memories | `backlog memory list --archived` |

### Edit Commands

| Command | Description | Example |
|---------|-------------|---------|
| `backlog memory append <task-id> "<text>"` | Append text to memory | `backlog memory append task-42 "Decision: Use PostgreSQL"` |
| `backlog memory clear <task-id> --confirm` | Clear all memory content | `backlog memory clear task-42 --confirm` |

### Search Commands

| Command | Description | Example |
|---------|-------------|---------|
| `backlog memory search "<query>"` | Search across all memories | `backlog memory search "authentication"` |
| `backlog memory search "<query>" --archived` | Include archived memories | `backlog memory search "API" --archived` |

### Import/Export Commands

| Command | Description | Example |
|---------|-------------|---------|
| `specify memory import <task-id> --from-pr <num>` | Import from PR description | `specify memory import task-42 --from-pr 780` |
| `specify memory import <task-id> --from-file <path>` | Import from file | `specify memory import task-42 --from-file docs/spec.md` |
| `specify memory export <task-id>` | Export to stdout | `specify memory export task-42` |
| `specify memory export <task-id> --output <path>` | Export to file | `specify memory export task-42 --output memory.md` |
| `specify memory export <task-id> --format json` | Export as JSON | `specify memory export task-42 --format json` |

### Template Commands

| Command | Description | Example |
|---------|-------------|---------|
| `specify memory template list` | List available templates | `specify memory template list` |
| `specify memory template show <name>` | Preview template | `specify memory template show feature` |
| `specify memory template apply <name> --task <id>` | Apply template | `specify memory template apply bugfix --task task-42` |

### Maintenance Commands

| Command | Description | Example |
|---------|-------------|---------|
| `backlog memory stats` | Show memory statistics | `backlog memory stats` |
| `backlog memory cleanup --archive-older-than 90d` | Archive old memories | `backlog memory cleanup --archive-older-than 90d` |
| `backlog memory cleanup --dry-run` | Preview cleanup actions | `backlog memory cleanup --dry-run` |

## Best Practices

### What to Record in Task Memory

**DO Record**:

1. **Key Decisions**
   ```markdown
   ## Key Decisions
   - 2025-12-09 14:30 - Chose FastAPI over Flask
     Rationale: Better async support, automatic OpenAPI generation
     Trade-off: Smaller ecosystem than Flask
   ```

2. **Failed Approaches**
   ```markdown
   ## Approaches Tried
   ### Approach: Use Redis for session storage
   **Result**: ❌ Rejected
   **Reason**: Added operational complexity without clear performance benefit.
   Testing showed PostgreSQL sessions performed adequately (<50ms p95).
   ```

3. **Open Questions and Blockers**
   ```markdown
   ## Open Questions
   - Should we use JWT or session cookies for auth?
     Waiting on security team review
   - Database schema: use JSONB or normalized tables?
     Need to validate with realistic data volume
   ```

4. **External Resources**
   ```markdown
   ## Resources
   - FastAPI documentation: https://fastapi.tiangolo.com/
   - ADR-015: Authentication Provider Selection
   - Research: docs/research/session-storage-analysis.md
   ```

**DON'T Record**:

1. **Secrets or Credentials**
   ```markdown
   # ❌ WRONG
   ## Resources
   - Database: postgresql://admin:SuperSecret123@db.example.com:5432
   - API Key: sk_live_51AbCdEfGh...

   # ✓ CORRECT
   ## Resources
   - Database: See AWS Secrets Manager: `prod/taskflow/db-credentials`
   - API Key: Stored in 1Password vault "Engineering Team"
   ```

2. **Large Code Dumps**
   ```markdown
   # ❌ WRONG
   ## Notes
   [Pasting 500 lines of code]

   # ✓ CORRECT
   ## Notes
   - Implemented authentication in src/auth/jwt.py
   - Key insight: Used refresh token rotation for security
   ```

3. **Redundant Information**
   ```markdown
   # ❌ WRONG
   ## Context
   [Copying entire task description verbatim]

   # ✓ CORRECT
   ## Context
   Task: Implement JWT authentication
   Focus: Refresh token rotation and secure storage
   ```

### Memory Hygiene

1. **Keep It Concise**
   - Aim for 1-2 KB per memory (typical: 5-10 entries)
   - Link to external docs for details
   - Archive when exceeding 1MB

2. **Use Timestamps**
   - Date all decisions and notes
   - Helps understand evolution of thinking

3. **Structure Over Freeform**
   - Use the standard sections (Context, Decisions, Approaches, etc.)
   - Makes memories searchable and scannable

4. **Update Regularly**
   - Add notes as you work, not at the end
   - Capture "why" decisions were made in the moment

## Cross-Machine Workflow

### Scenario: Switch from Desktop to Laptop

**On Desktop** (before switching):
```bash
# 1. Save your memory updates
git add backlog/memory/task-42.md

# 2. Commit with descriptive message
git commit -m "Update task-42 memory: PostgreSQL decision"

# 3. Push to remote
git push
```

**On Laptop** (picking up work):
```bash
# 1. Pull latest changes
git pull

# 2. Read task memory to rebuild context
backlog memory view task-42

# 3. Continue work with full context
```

### Scenario: Handoff Task to Team Member

**Original Developer**:
```bash
# 1. Document current state in memory
backlog memory append task-42 "Status: API endpoints implemented, tests pending"
backlog memory append task-42 "Next: Add integration tests for /auth/login endpoint"

# 2. Commit and push
git add backlog/memory/task-42.md
git commit -m "Handoff task-42 to @teammate"
git push

# 3. Reassign task
backlog task edit task-42 -a @teammate
```

**Team Member Taking Over**:
```bash
# 1. Pull latest
git pull

# 2. Review task memory
backlog memory view task-42

# 3. Understand context from decisions and notes
# 4. Continue work from documented next steps
```

## Handling Conflicts

Git conflicts in memory files are rare (single person typically works on task), but here's how to resolve them when they occur:

### Conflict Scenario

```bash
# Git merge creates conflict markers
<<<<<<< HEAD (Machine A)
- 2025-12-09 14:30 - Tried approach X, failed because of Z
=======
- 2025-12-09 14:35 - Decided to use library Y after research
>>>>>>> branch (Machine B)
```

### Resolution Strategy

**Prefer Append-Only**: Since memories are chronological, usually both changes are valid:

```markdown
# Resolved: Keep both entries
- 2025-12-09 14:30 - Tried approach X, failed because of Z
- 2025-12-09 14:35 - Decided to use library Y after research
```

**Steps**:
1. Open the conflicted file
2. Remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Keep both entries if they represent different moments
4. Reorder chronologically if needed
5. Commit the resolved file

## AI Agent Integration

Task Memory automatically injects context into AI agents working on your tasks.

### Claude Code Integration

Task Memory uses `@import` in `backlog/CLAUDE.md`:

```markdown
# backlog/CLAUDE.md

## Active Task Context

@import ../memory/task-42.md
```

When Claude Code works on task-42, it automatically has access to all decisions, approaches tried, and open questions.

### MCP Integration (VS Code Copilot, etc.)

Agents supporting MCP can query task memory:

```python
# MCP resource URI
backlog://memory/task-42

# Agent receives full memory content
```

### Generic Agent Integration

Any agent with filesystem access can read memories:

```bash
# Agent instruction
"Before implementing, read task memory from backlog/memory/task-42.md"

# Agent reads file
cat backlog/memory/task-42.md
```

## Troubleshooting

### Memory Not Created Automatically

**Symptom**: Task moved to "In Progress" but no memory file exists

**Causes & Solutions**:
1. **Lifecycle hooks not installed**
   ```bash
   # Reinstall hooks
   flowspec init
   ```

2. **Manual state change in task file**
   ```bash
   # Use CLI instead
   backlog task edit task-42 -s "In Progress"
   ```

3. **Permissions issue**
   ```bash
   # Check permissions
   ls -la backlog/memory/
   chmod 755 backlog/memory/
   ```

### Memory Not Syncing Between Machines

**Symptom**: Changes made on Machine A don't appear on Machine B

**Causes & Solutions**:
1. **Forgot to commit and push**
   ```bash
   # On Machine A
   git status  # Check for uncommitted changes
   git add backlog/memory/task-42.md
   git commit -m "Update task memory"
   git push
   ```

2. **Forgot to pull on Machine B**
   ```bash
   # On Machine B
   git pull
   ```

3. **Working on different branches**
   ```bash
   # Check branch
   git branch --show-current

   # Switch to correct branch
   git checkout main
   git pull
   ```

### Memory File Too Large

**Symptom**: Memory file exceeds 1MB, operations slow

**Solutions**:
1. **Archive large memory**
   ```bash
   # Manual archive
   mv backlog/memory/task-42.md backlog/memory/archive/task-42.md

   # Create fresh memory
   backlog task edit task-42 -s "To Do"
   backlog task edit task-42 -s "In Progress"
   ```

2. **Extract details to separate docs**
   ```markdown
   # Move large content to external file
   ## Research
   - Detailed analysis: docs/research/task-42-analysis.md

   # Keep summary in memory
   ## Key Decisions
   - After analysis (see docs/research/task-42-analysis.md), chose PostgreSQL
   ```

### Accidentally Committed Secrets

**Symptom**: Pre-commit hook caught secrets or secrets were committed

**Solutions**:
1. **Remove from staging (before commit)**
   ```bash
   # Edit memory to remove secrets
   nvim backlog/memory/task-42.md

   # Restage clean file
   git add backlog/memory/task-42.md
   ```

2. **Remove from commit (after commit, before push)**
   ```bash
   # Edit memory to remove secrets
   nvim backlog/memory/task-42.md

   # Amend commit
   git add backlog/memory/task-42.md
   git commit --amend
   ```

3. **Remove from history (after push)**
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # See: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
   ```

### Agent Not Seeing Memory Context

**Symptom**: AI agent asks for context that's already in memory

**Solutions**:
1. **Verify memory file exists**
   ```bash
   ls -la backlog/memory/task-42.md
   ```

2. **Check CLAUDE.md @import**
   ```bash
   # Verify active task ID
   cat backlog/CLAUDE.md | grep "@import"
   ```

3. **Manually point agent to memory**
   ```
   "Please read context from backlog/memory/task-42.md before proceeding"
   ```

## Advanced Usage

### Import Context from Pull Requests

When starting work on a task that has a related PR, import the PR description for context:

```bash
# Import PR description into task memory
specify memory import task-42 --from-pr 780

# Append PR context to existing memory
specify memory import task-42 --from-pr 780 --append
```

Import from a file (spec, ADR, or other documentation):

```bash
# Import from a spec file
specify memory import task-42 --from-file docs/prd/feature-x.md

# Import from ADR
specify memory import task-42 --from-file docs/adr/ADR-015.md --append
```

### Export Memory Content

Export task memory for sharing, analysis, or backup:

```bash
# Export as markdown (default)
specify memory export task-42 --output task-42-memory.md

# Export as JSON for scripting
specify memory export task-42 --format json

# Export without metadata
specify memory export task-42 --no-metadata

# Export archived memory
specify memory export task-42 --archived --format json
```

### Use Memory Templates

Templates provide task-type-specific structures:

```bash
# List available templates
specify memory template list

# Output:
# ┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
# ┃ Name     ┃ Description                                 ┃ Location  ┃
# ┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
# │ default  │ Standard task memory template               │ ✓ builtin │
# │ feature  │ Feature with user stories and requirements  │ ✓ builtin │
# │ bugfix   │ Bug fix with root cause analysis            │ ✓ builtin │
# │ research │ Research spike with findings                │ ✓ builtin │
# └──────────┴─────────────────────────────────────────────┴───────────┘

# Preview a template
specify memory template show feature

# Apply template to a task
specify memory template apply feature --task task-42
```

**Creating Custom Templates**:

Place custom templates in `.specify/templates/memory/`:

```bash
# Create custom template directory
mkdir -p .specify/templates/memory

# Create your template
cat > .specify/templates/memory/api-endpoint.md << 'EOF'
---
task_id: {task_id}
created: {created_date}
updated: {updated_date}
template: api-endpoint
---
# Task Memory: {task_id}

{task_title}

## Endpoint Specification

**Method**:
**Path**:
**Authentication**:

### Request

### Response

## Implementation Notes

## Testing Checklist

- [ ] Unit tests
- [ ] Integration tests
- [ ] Load testing

## Progress

## Open Questions
EOF
```

### Search Across All Memories

Find patterns across active and archived tasks:

```bash
# Search for authentication-related decisions
backlog memory search "authentication" --archived

# Search for failed approaches to learn from
backlog memory search "rejected" --archived

# Find tasks that used a specific library
backlog memory search "FastAPI" --archived
```

### Memory Analytics

Track memory usage patterns:

```bash
backlog memory stats

# Output:
# Task Memory Analytics (Last 30 Days)
# =====================================
# Active memories: 23
# Archived memories: 156
# Average memory size: 187 KB
# Largest memory: 943 KB (task-245)
# Conflict rate: 2.3%
# Search queries: 234
# Average read time: 12ms
```

### Cleanup Old Memories

Keep repository lean with automated cleanup:

```bash
# Archive memories for tasks completed >90 days ago
backlog memory cleanup --archive-older-than 90d

# Delete archived memories >365 days old
backlog memory cleanup --delete-archived-older-than 365d --confirm

# Dry-run to preview cleanup
backlog memory cleanup --archive-older-than 90d --dry-run
```

### Export Memory for Analysis

```bash
# Export single memory as JSON
backlog memory view task-42 --format json > task-42-memory.json

# Export all memories for ML training
for task in $(backlog memory list --plain); do
  backlog memory view "$task" --format json >> memories-export.jsonl
done
```

## FAQ

**Q: Will Task Memory slow down my backlog commands?**
A: No. Memory operations are designed to complete in <50ms (p95). Lifecycle hooks run asynchronously and don't block task transitions.

**Q: What happens if I manually edit a memory file?**
A: That's perfectly fine! Memory files are human-readable markdown designed to be edited directly. Just commit your changes to sync them.

**Q: Can I disable Task Memory for specific tasks?**
A: Not currently. Task Memory is lightweight enough that it doesn't need per-task configuration. If you don't need memory for a task, simply don't add content to it.

**Q: How do I migrate existing tasks to use Task Memory?**
A: Move tasks to "In Progress" state using `backlog task edit`, and memories will be created automatically. You can then populate them with historical context.

**Q: What's the retention policy for archived memories?**
A: Archived memories are retained indefinitely by default. You can manually delete them or use `backlog memory cleanup --delete-archived-older-than <days>`.

**Q: Can I use Task Memory with private/sensitive projects?**
A: Yes. Memory files follow your repository's access controls. Just ensure you follow the guideline: no secrets or credentials in memory files.

**Q: Does Task Memory work offline?**
A: Yes. All operations work offline. Sync happens via standard git push/pull when you're back online.

## Related Documentation

- [Task Memory Architecture](../architecture/task-memory-detailed.md) - Technical implementation details
- [Constitution: Principle 13](../../memory/constitution.md#principle-13-task-memory---persistent-context-management) - Requirements and guidelines
- [Backlog Quick Start](backlog-quickstart.md) - Getting started with backlog.md
- [Backlog User Guide](backlog-user-guide.md) - Complete backlog.md documentation

## Feedback

Found an issue or have a suggestion? Open an issue or contribute to the documentation:
- GitHub Issues: [flowspec/issues](https://github.com/yourusername/flowspec/issues)
- Documentation: `docs/guides/task-memory-user-guide.md`

---

**Version**: 1.1 | **Last Updated**: 2025-12-11
