# Claude Code Hooks

Flowspec uses Claude Code hooks to provide automated safety checks and code quality enforcement.

## Implemented Hooks

### 1. SessionStart Hook (SessionStart)

**Hook**: `.claude/hooks/session-start.sh`

Runs when starting or resuming a Claude Code session to verify environment and display context:
- Checks for `uv` (Python package manager)
- Checks for `backlog` CLI (task management)
- Displays versions of installed tools
- Shows active "In Progress" backlog tasks
- Provides warnings for missing dependencies

**Output Example**:
```json
{
  "decision": "allow",
  "reason": "Session started - environment verified",
  "additionalContext": "Session Context:\n  ✓ uv: uv 0.9.11\n  ✓ backlog: 1.22.0\n  ✓ Active tasks: 2 in progress"
}
```

**Behavior**: Always returns `"decision": "allow"` with contextual information. Never blocks session startup (fail-open principle).

**Performance**: Completes in <5 seconds typical, <60 seconds maximum (timeout configured).

### 2. Sensitive File Protection (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-sensitive-files.py`

Asks for confirmation before modifying sensitive files:
- `.env` files (including `.env.*`)
- `.secrets` files
- `package-lock.json`
- `uv.lock`
- `.git/` directory
- `CLAUDE.md` files

**Behavior**: Returns `"decision": "ask"` for sensitive files, prompting Claude to get user confirmation.

### 3. Git Command Safety Validator (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-git-safety.py`

Warns on dangerous Git commands:
- `git push --force` / `-f` (asks for confirmation)
- `git push origin +branch` (force push syntax, asks for confirmation)
- `git reset --hard` (asks for confirmation)
- `git rebase -i` (DENIES - interactive commands not supported)
- `git clean -fd` (asks for confirmation)

**Special handling**: Force pushes to `main`/`master` branches receive extra warnings.

**Behavior**: Returns `"decision": "ask"` for dangerous commands, or `"decision": "deny"` for unsupported interactive commands.

### 4. Auto-format Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-format-python.sh`

Automatically runs `ruff format` on Python files after Edit/Write operations.

**Behavior**: Silently formats Python files and reports if formatting was applied.

### 5. Auto-lint Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-lint-python.sh`

Automatically runs `ruff check --fix` on Python files after Edit/Write operations.

**Behavior**: Attempts to auto-fix linting issues and reports results. Manual fixes may be needed for complex issues.

### 6. Pre-Implementation Quality Gates

**Hook**: `.claude/hooks/pre-implement.sh`

Runs automated quality gates before `/flow:implement` can proceed. Ensures specifications are complete and high-quality before implementation begins.

**Gates Enforced**:
1. **Required Files**: Validates `spec.md`, `plan.md`, and `tasks.md` exist
2. **Spec Completeness**: Detects unresolved markers (`NEEDS CLARIFICATION`, `[TBD]`, `[TODO]`, `???`, `PLACEHOLDER`, `<insert>`)
3. **Constitutional Compliance**: Verifies DCO sign-off, testing requirements, and acceptance criteria are mentioned
4. **Quality Threshold**: Requires spec quality score >= 70/100 using `specify quality` scorer

**Override**: Use `--skip-quality-gates` flag to bypass (NOT RECOMMENDED).

**Testing**: Run `.claude/hooks/test-pre-implement.sh` (14 comprehensive tests).

**Documentation**: See `docs/adr/adr-pre-implementation-quality-gates.md` for full ADR.

**Example Output**:
```bash
# Pass state
✅ All quality gates passed. Proceeding with implementation.

# Fail state with remediation
❌ Quality gates failed:

✗ Unresolved markers found in spec.md:
  - Line 45: NEEDS CLARIFICATION: authentication method
  → Resolve all markers before implementation

✗ Quality score: 58/100 (threshold: 70)
  Recommendations:
  - Add missing section: ## User Story
  - Reduce vague terms (currently: 12 instances)
  → Improve spec quality using /spec:clarify

Run with --skip-quality-gates to bypass (NOT RECOMMENDED).
```

### 7. Backlog Task Quality Gate (Stop)

**Hook**: `.claude/hooks/stop-quality-gate.py`

Enforces backlog task quality gate before session ends when PR creation is detected:
- Detects PR creation intent in conversation context (e.g., "create PR", "gh pr create")
- Checks for In Progress tasks via `backlog task list --plain -s "In Progress"`
- Blocks session end if incomplete tasks exist with clear guidance
- Provides list of incomplete tasks and remediation steps
- Supports bypass with force/skip keywords

**Behavior**: Returns `"continue": false` when PR detected with In Progress tasks. Returns `"continue": true` on errors (fail-open) or when quality gate passes.

**Bypass**: Include "force stop" or "skip quality gate" in conversation to bypass.

**Test**: Run `.claude/hooks/test-stop-quality-gate.py` to verify all edge cases.

**Documentation**: See `docs/adr/ADR-003-stop-hook-quality-gate.md` for full ADR.

**Example Output (blocking)**:
```
Quality Gate: Incomplete Backlog Tasks Detected

You have 2 task(s) still marked as "In Progress":

  - task-189: Create Stop Hook for Backlog Task Quality Gate
  - task-190: Another task

Before creating a PR, please:

1. Complete all acceptance criteria for each task
2. Mark tasks as Done using:
   backlog task edit <task-id> -s Done --check-ac 1 --check-ac 2 ...

To bypass this quality gate (not recommended):
- Use force stop or explicitly request to skip the quality gate
```

## Testing Hooks

Run the test suite to verify all hooks are working correctly:

```bash
# Run all hook tests
.claude/hooks/test-hooks.sh

# Test SessionStart hook
.claude/hooks/test-session-start.sh

# Test a specific hook manually
echo '{"tool_name": "Write", "tool_input": {"file_path": ".env"}}' | \
  python .claude/hooks/pre-tool-use-sensitive-files.py

# Test SessionStart hook manually
.claude/hooks/session-start.sh | python3 -m json.tool

# Test Stop quality gate hook
python .claude/hooks/test-stop-quality-gate.py
```

## Customizing Hook Behavior

Hooks are configured in `.claude/settings.json`. To customize:

1. **Modify sensitive file patterns**: Edit `SENSITIVE_PATTERNS` in `pre-tool-use-sensitive-files.py`
2. **Add/remove dangerous git patterns**: Edit `DANGEROUS_GIT_PATTERNS` in `pre-tool-use-git-safety.py`
3. **Adjust timeouts**: Modify timeout values in `.claude/settings.json`
4. **Disable specific hooks**: Remove or comment out hooks in `.claude/settings.json`

## Hook Design Principles

- **Fail open**: Hooks default to "allow" on errors to avoid breaking Claude's workflow
- **Fast execution**: All hooks complete in <5 seconds (10s for PostToolUse)
- **Clear communication**: Hooks provide detailed reasons and context for decisions
- **Non-blocking**: Only interactive commands (like `git rebase -i`) are denied; everything else asks for confirmation
