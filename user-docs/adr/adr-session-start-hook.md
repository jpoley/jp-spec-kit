# ADR: SessionStart Hook for Environment Setup

**Status**: Accepted
**Date**: 2025-12-01
**Decision Makers**: Backend Engineering Team
**Consulted**: Claude Code Users

## Context and Problem Statement

Claude Code users working on Flowspec projects need immediate context when starting or resuming a session. Without this context:

1. Users don't know if critical dependencies (uv, backlog CLI) are available
2. Users don't see which backlog tasks are actively in progress
3. Session startup requires manual commands to check environment state
4. New contributors lack visibility into required tooling

**Problem**: How can we automatically provide session context and verify the development environment when starting Claude Code?

## Decision Drivers

- **User Experience**: Immediate visibility of session context improves workflow
- **Fail-Open Principle**: Environment checks must never block session startup
- **Performance**: Hook execution must be fast (<5s ideal, <60s max)
- **Graceful Degradation**: Missing dependencies should warn but not fail
- **Consistency**: Follow existing hook patterns in `.claude/hooks/`

## Considered Options

### Option 1: SessionStart Hook (Chosen)

**Description**: Implement a SessionStart hook that runs when Claude Code sessions start/resume

**Pros**:
- Automatic execution - no user action required
- Follows existing hook patterns (Python/Bash scripts)
- Non-blocking with timeout protection
- Graceful degradation when tools are missing
- Displays active backlog tasks for immediate context

**Cons**:
- Adds ~1-2s to session startup time
- Requires SessionStart hook support in Claude Code
- Additional maintenance overhead for hook script

### Option 2: Manual Startup Script

**Description**: Provide a shell script users must manually run at session start

**Pros**:
- Simple implementation (no hook configuration needed)
- Users control when to run it
- No impact on session startup time

**Cons**:
- Requires manual user action (easy to forget)
- Inconsistent execution across users
- No automatic task context display
- Poor developer experience

### Option 3: .zshrc/.bashrc Integration

**Description**: Add environment checks to user shell configuration files

**Pros**:
- Runs on any terminal session
- No Claude Code-specific configuration

**Cons**:
- Not Claude Code-specific (shows in all terminals)
- Pollutes shell initialization
- Doesn't integrate with Claude Code workflow
- Can't display backlog tasks (no project context)

### Option 4: Claude Code Extension/Plugin

**Description**: Build a Claude Code extension to show environment status

**Pros**:
- Rich UI integration possibilities
- Could show persistent status indicator

**Cons**:
- Requires extension development infrastructure
- More complex than hook scripts
- Harder to maintain and distribute
- Overkill for simple environment checks

## Decision Outcome

**Chosen Option**: SessionStart Hook (Option 1)

**Rationale**:
- Aligns with existing hook patterns in Flowspec
- Automatic execution provides best UX
- Fail-open design ensures sessions never block
- Fast performance meets timeout constraints
- Graceful degradation handles missing dependencies
- Displays active backlog tasks for immediate context

### Implementation Details

1. **Hook Script**: `.claude/hooks/session-start.sh`
   - Checks for `uv` and `backlog` CLI tools
   - Displays versions when available
   - Lists active "In Progress" backlog tasks
   - Always exits with code 0 (fail-open)
   - Completes in <5s (well under 60s timeout)

2. **Configuration**: `.claude/settings.json`
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "type": "command",
           "command": "bash .claude/hooks/session-start.sh",
           "timeout": 60
         }
       ]
     }
   }
   ```

3. **Output Format**: JSON with decision and context
   ```json
   {
     "decision": "allow",
     "reason": "Session started - environment verified",
     "additionalContext": "Session Context:\n  ✓ uv: uv 0.9.11\n  ✓ backlog: 1.22.0\n  ✓ Active tasks: 2 in progress"
   }
   ```

### Edge Cases Handled

1. **Missing uv**: Warning displayed, continues
2. **Missing backlog CLI**: Warning displayed, continues
3. **No backlog.md file**: Informational message
4. **No In Progress tasks**: Shows "No active tasks"
5. **Multiple In Progress tasks**: Lists all with count
6. **Backlog CLI timeout**: Gracefully handled with 5s timeout
7. **Invalid CLAUDE_PROJECT_DIR**: Fallback to current directory
8. **Malformed backlog output**: Graceful degradation

### Testing

Comprehensive test suite at `.claude/hooks/test-session-start.sh`:
- Happy path: all dependencies present
- Missing dependencies: graceful degradation
- Performance: completes in <5s
- Exit code: always 0 (fail-open)
- JSON structure: valid output
- CLAUDE_PROJECT_DIR fallback: works without env var

## Consequences

### Positive

- **Better UX**: Users immediately see session context
- **Proactive Warnings**: Missing dependencies detected early
- **Task Visibility**: Active backlog tasks shown at session start
- **Fail-Open Design**: Never blocks session startup
- **Fast Execution**: <5s typical, <60s worst case
- **Consistent Patterns**: Follows existing hook conventions

### Negative

- **Startup Delay**: Adds 1-2s to session initialization
- **Maintenance**: Additional script to maintain
- **Dependency**: Requires SessionStart hook support in Claude Code

### Neutral

- **Documentation**: Requires updates to CLAUDE.md
- **Testing**: Test suite adds coverage requirements

## Related Decisions

- **ADR: Pre-Tool-Use Hooks**: Establishes hook patterns
- **ADR: Fail-Open Principle**: Defines error handling strategy

## Implementation Notes

### Hook Design Principles

1. **Fail-Open**: Always exit 0, never block sessions
2. **Fast**: Complete in <5s ideal, <60s maximum
3. **Graceful**: Handle missing dependencies without errors
4. **Informative**: Provide clear context to users
5. **Consistent**: Follow existing hook patterns

### Future Enhancements

- Show git branch and status in session context
- Display Python version and virtual environment
- Check for uncommitted changes in In Progress tasks
- Integrate with CI/CD status checks
- Add project-specific health checks

## References

- [Claude Code Hooks Documentation](https://docs.anthropic.com/claude-code/hooks)
- [Flowspec CLAUDE.md](../../CLAUDE.md)
- [Backlog User Guide](../guides/backlog-user-guide.md)
- [Hook Test Patterns](.claude/hooks/test-hooks.sh)
