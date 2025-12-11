# Claude Code Checkpoints

Checkpoints are automatic save points created before each code change, enabling instant rollback without Git operations.

## How Checkpoints Work

- **Automatic Creation**: Claude creates a checkpoint before every file modification
- **Instant Rewind**: Press `Esc Esc` (double escape) to undo the last change
- **Selective Restore**: Choose to restore code, conversation, or both
- **No Git Required**: Works independently of version control

## When to Use Checkpoints

### Recommended for:

| Scenario | Why |
|----------|-----|
| **Experimental refactoring** | Try new patterns without commitment |
| **Multi-file changes** | Easily undo if something breaks |
| **Learning/exploration** | Experiment freely, rewind mistakes |
| **Proof of concepts** | Quickly test ideas |
| **Complex migrations** | Safety net for risky changes |

### Less useful for:

- Simple, atomic changes (just use Git)
- Changes you're confident about
- Documentation-only updates

## Quick Reference

| Action | How |
|--------|-----|
| **Rewind last change** | Press `Esc` twice quickly |
| **Rewind interactively** | Type `/rewind` |
| **Restore code only** | Select "Code" in rewind dialog |
| **Restore conversation** | Select "Conversation" in rewind dialog |
| **Restore both** | Select "Both" in rewind dialog |

## Best Practices

### 1. Create Mental Checkpoints

Before risky operations, note: "If this doesn't work, I can Esc Esc to undo."

### 2. Checkpoint + Git Together

```
1. Checkpoint: Try experimental change
2. If good -> git commit
3. If bad -> Esc Esc to undo
```

### 3. Checkpoint Before Large Changes

Before implementing features that touch many files:
- Tell Claude: "I'm going to experiment with refactoring the auth module"
- Claude will create checkpoints at each step
- Undo any step that doesn't work

## Example Workflows

### Experimental Refactoring

```
User: Let's refactor the database layer to use SQLAlchemy 2.0 syntax

Claude: [Makes changes to 5 files]

User: *Tests fail* Let me try Esc Esc to undo

[Checkpoint restored - all 5 files back to original state]

User: Let's try a different approach...
```

### Proof of Concept

```
User: Add a caching layer to the API, I want to see if it improves performance

Claude: [Implements caching]

User: Performance is worse, please undo

[Esc Esc or /rewind to restore original state]
```

### Learning by Doing

```
User: Show me how to implement the visitor pattern here

Claude: [Implements pattern across 3 classes]

User: I understand now, but I prefer the original. Undo please.

[Checkpoint restored]
```

## Limitations

- **Code only**: Checkpoints don't undo bash commands or external effects
- **Session-scoped**: Checkpoints don't persist across Claude Code sessions
- **Not a backup**: Use Git for permanent history

## Integration with SDD Workflow

### During /flow:implement

Before risky implementation:
1. Ensure Git is clean (commit or stash)
2. Tell Claude about the experimental nature
3. Implement incrementally
4. Use checkpoints to undo failed attempts
5. Commit when satisfied

### Checkpoint Reminder

For complex implementations, Claude should remind:
> "This change affects multiple files. Remember you can press Esc Esc to undo if needed."
