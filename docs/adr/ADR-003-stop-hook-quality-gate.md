# ADR-003: Stop Hook for Backlog Task Quality Gate

**Status**: Accepted
**Date**: 2025-12-01
**Author**: Quality Guardian Agent
**Context**: Task-189 - Implement Stop hook to enforce backlog task quality gate

---

## Context and Problem Statement

JP Spec Kit uses backlog.md to track tasks through workflows with clear acceptance criteria. When creating PRs, developers should ensure tasks are marked "Done" with all acceptance criteria complete. However, it's easy to forget this quality gate in the flow of creating a PR.

**Problems**:
- PRs created while backlog tasks still marked "In Progress"
- Acceptance criteria incomplete when PR submitted
- Backlog state becomes inconsistent with actual work
- No automated reminder before session ends
- Manual verification required after PR creation

**Goal**: Implement a Stop hook that enforces backlog task quality gates when PR creation is detected in conversation, while following fail-open principles for reliability.

---

## Decision Drivers

1. **Quality Enforcement**: Ensure backlog accuracy before PRs
2. **Developer Experience**: Non-intrusive, clear guidance
3. **Reliability**: Fail-open on errors, never block incorrectly
4. **Flexibility**: Allow bypassing for power users
5. **Integration**: Use existing backlog CLI, no new dependencies
6. **Performance**: Fast execution (<5s timeout)

---

## Considered Options

### Option 1: Pre-Commit Hook
**Approach**: Git pre-commit hook checks backlog state

**Pros**:
- Runs at commit time, closer to PR creation
- Standard Git workflow integration

**Cons**:
- Doesn't detect PR creation intent
- Blocks commits even for non-PR work
- Can be bypassed with --no-verify
- Requires separate installation step

### Option 2: Pre-Tool-Use Hook on Bash (gh pr create)
**Approach**: Intercept `gh pr create` command via Bash tool hook

**Pros**:
- Catches exact PR creation moment
- Tight integration with CLI

**Cons**:
- Misses other PR creation methods (web UI, other tools)
- Requires parsing Bash commands
- Complex pattern matching
- False negatives if PR created outside Claude

### Option 3: Stop Hook with Conversation Context (SELECTED)
**Approach**: Detect PR creation intent in conversation summary, check backlog state

**Pros**:
- Catches PR intent before session ends
- Works with all PR creation methods mentioned in conversation
- Natural checkpoint at session boundary
- Clear fail-open semantics
- User can review guidance before ending session

**Cons**:
- Requires conversation parsing (potential false negatives)
- Runs at session end, not PR creation time
- Relies on conversation mentioning PR

---

## Decision

**Selected: Option 3 - Stop Hook with Conversation Context**

Implement `.claude/hooks/stop-quality-gate.py` that:

1. **Detects PR Intent**: Parse conversation summary for PR creation phrases
2. **Checks Backlog State**: Query `backlog task list --plain -s "In Progress"`
3. **Blocks or Allows**: Return JSON with `continue: true/false`
4. **Provides Guidance**: Clear message listing incomplete tasks
5. **Fails Open**: On any error, allow stop to continue

### Implementation Details

**Hook Type**: Stop hook (runs when session ends)

**Input Protocol**:
```json
{
  "stopReason": "user_requested",
  "conversationSummary": "..."
}
```

**Output Protocol**:
```json
{
  "continue": true|false,
  "stopReason": "incomplete_tasks",
  "systemMessage": "Quality Gate: ..."
}
```

**PR Detection Patterns** (case-insensitive regex):
- `create pr`
- `open pr`
- `make pr`
- `create pull request`
- `gh pr create`
- `pull request.*create`
- `open\s+a?\s*pull\s+request`
- `pr\s+create`
- `let'?s\s+pr\b`

**Quality Gate Logic**:
1. Parse conversation for PR intent
2. If no PR detected → allow stop
3. If PR detected → check for In Progress tasks
4. If no In Progress tasks → allow stop
5. If In Progress tasks exist → block with guidance
6. If force/skip detected → allow stop (bypass)
7. On any error → allow stop (fail-open)

**Fail-Open Scenarios**:
- Backlog CLI not available
- Backlog CLI times out (>5s)
- Invalid JSON input
- Parsing errors
- Any unexpected exception

---

## Consequences

### Positive

1. **Improved Quality**: Reminds developers to complete task lifecycle
2. **Accurate Backlog**: Ensures backlog reflects actual work state
3. **Clear Guidance**: Provides actionable steps when blocking
4. **Non-Blocking**: Fail-open principle prevents workflow disruption
5. **Flexible**: Supports bypass for power users
6. **Low Overhead**: Fast execution, minimal conversation parsing

### Negative

1. **False Negatives**: May miss PR creation if not mentioned in conversation
2. **Parsing Dependency**: Relies on conversation summary quality
3. **Late Detection**: Runs at session end, not PR creation time
4. **Maintenance**: Requires updating PR patterns if new tools emerge

### Mitigations

1. **False Negatives**: Document pattern list, encourage explicit PR mentions
2. **Parsing**: Use robust regex, test with diverse phrases
3. **Late Detection**: Acceptable tradeoff for clean session boundary
4. **Maintenance**: Keep PR patterns list in hook comments

---

## Implementation Checklist

- [x] Create `.claude/hooks/stop-quality-gate.py`
- [x] Implement PR intent detection with regex patterns
- [x] Integrate backlog CLI with timeout handling
- [x] Implement fail-open error handling
- [x] Add force/skip bypass support
- [x] Create comprehensive test suite
- [x] Update `.claude/settings.json` with Stop hook
- [x] Document in CLAUDE.md hooks section
- [x] Create ADR (this document)

---

## Edge Cases Handled

1. **No conversation context** → Allow stop
2. **PR mentioned, no task assigned** → Allow with info
3. **PR mentioned, In Progress tasks** → Block with task list
4. **Task Done, AC incomplete** → Allow (backlog CLI responsibility)
5. **Backlog CLI unavailable** → Allow (fail-open)
6. **Multiple In Progress tasks** → List all in guidance
7. **Force/skip keywords** → Allow bypass
8. **Various PR phrases** → Comprehensive regex patterns
9. **Case variations** → Case-insensitive matching
10. **Timeout/errors** → Fail-open gracefully

---

## Testing Strategy

Comprehensive test suite in `.claude/hooks/test-stop-quality-gate.py`:

1. No PR mention → allow
2. PR mention, no tasks → allow
3. PR mention, 1 task → block with details
4. PR mention, multiple tasks → list all
5. CLI error/timeout → fail-open
6. Various PR phrases → detect correctly
7. Empty/null context → allow
8. Force bypass → allow
9. Case-insensitive → handle variations

---

## References

- Task-189: Create Stop Hook for Backlog Task Quality Gate
- `.claude/hooks/pre-tool-use-sensitive-files.py` - Hook pattern reference
- `.claude/hooks/pre-tool-use-git-safety.py` - Fail-open pattern reference
- `backlog task list --plain` - CLI integration

---

## Revision History

- 2025-12-01: Initial decision (v1.0)
