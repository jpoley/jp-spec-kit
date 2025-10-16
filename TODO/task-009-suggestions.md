# Claude Code Hooks Suggestions for JP Spec Kit

## Overview

This document provides suggestions for Claude Code hooks that could be used in the JP Spec Kit project. Hooks are organized by type (PreToolUse, PostToolUse, etc.) and categorized as either **GENERIC** (applicable to most projects) or **PROJECT-SPECIFIC** (tailored to jp-spec-kit or Python projects).

## Hook Types Reference

- **PreToolUse**: Executes before tool calls (can block execution)
- **PostToolUse**: Runs after tool calls complete successfully
- **UserPromptSubmit**: Triggers when users submit prompts
- **Notification**: Fires when Claude sends notifications
- **Stop**: Runs when main agent finishes responding
- **SubagentStop**: Executes when subagent completes
- **SessionStart**: At session initialization/resumption
- **SessionEnd**: During session termination
- **PreCompact**: Before context compaction

---

## PreToolUse Hooks

PreToolUse hooks execute before a tool runs and can **block execution** if they exit with non-zero status. They're ideal for validation, permission checks, and safety controls.

### 1. Sensitive File Protection

**Type**: GENERIC
**Tools**: Write, Edit
**Priority**: HIGH

**Purpose**: Prevent accidental modification of critical files that could break the project or expose secrets.

**Protected Files**:
- `.env`, `.env.local`, `*.env*` (environment/secrets)
- `package-lock.json`, `uv.lock`, `Cargo.lock` (dependency locks)
- `.git/config`, `.git/HEAD` (git internals)
- `pyproject.toml` (project configuration - warn only, don't block)
- `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md` (legal/policy docs)

**Implementation Example**:
```bash
# Check if file being modified is in protected list
echo "$tool_input" | jq -r '.file_path' | grep -E '\.(env|lock)$|\.git/|LICENSE|SECURITY\.md' && exit 1 || exit 0
```

**Benefits**:
- Prevents accidental secrets commits
- Protects dependency lock files from corruption
- Safeguards legal/policy documents

---

### 2. Git Command Safety Validator

**Type**: GENERIC
**Tools**: Bash
**Priority**: HIGH

**Purpose**: Prevent dangerous git commands that could cause data loss or violate best practices.

**Blocked Operations**:
- `git push --force` to main/master branches
- `git reset --hard` without confirmation
- `git clean -fd` without dry-run first
- `git rebase -i` (not supported in non-interactive contexts)
- `git commit --amend` to commits authored by others
- `--no-verify`, `--no-gpg-sign` flags (bypasses pre-commit hooks)

**Implementation Example**:
```bash
# Extract command from hook input
cmd=$(echo "$tool_input" | jq -r '.command')

# Check for dangerous patterns
if echo "$cmd" | grep -qE 'git push.*(--force|-f).*main|master'; then
  echo "ERROR: Force push to main/master is not allowed"
  exit 1
fi

if echo "$cmd" | grep -qE 'git.*--no-verify'; then
  echo "WARNING: Bypassing pre-commit hooks is discouraged"
  exit 1
fi

exit 0
```

**Benefits**:
- Prevents accidental data loss
- Enforces git workflow best practices
- Maintains commit integrity

---

### 3. Version Consistency Checker

**Type**: PROJECT-SPECIFIC (Python)
**Tools**: Write, Edit
**Priority**: MEDIUM

**Purpose**: When editing version-related files, ensure version numbers are consistent across `pyproject.toml` and `src/specify_cli/__init__.py`.

**Triggers When**:
- Editing `pyproject.toml` (version field)
- Editing `src/specify_cli/__init__.py` (__version__)

**Implementation Example**:
```python
#!/usr/bin/env python3
import json
import sys
import re

# Read hook input
hook_data = json.load(sys.stdin)
file_path = hook_data.get('tool_input', {}).get('file_path', '')
new_content = hook_data.get('tool_input', {}).get('new_string', '')

if 'pyproject.toml' in file_path or '__init__.py' in file_path:
    # Extract version from pyproject.toml
    with open('pyproject.toml', 'r') as f:
        pyproject_version = re.search(r'version\s*=\s*"([^"]+)"', f.read())

    # Extract version from __init__.py
    with open('src/specify_cli/__init__.py', 'r') as f:
        init_version = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', f.read())

    if pyproject_version and init_version:
        if pyproject_version.group(1) != init_version.group(1):
            print(f"ERROR: Version mismatch!")
            print(f"  pyproject.toml: {pyproject_version.group(1)}")
            print(f"  __init__.py: {init_version.group(1)}")
            print("Please update both files to have the same version.")
            sys.exit(1)

sys.exit(0)
```

**Benefits**:
- Prevents version inconsistencies
- Enforces project versioning policy
- Reduces release errors

---

### 4. Bash Command Logger (Pre-execution)

**Type**: GENERIC
**Tools**: Bash
**Priority**: LOW

**Purpose**: Log all bash commands before execution for audit trail and debugging.

**Implementation Example**:
```bash
# Log to file with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - PLANNED: $(echo "$tool_input" | jq -r '.command')" >> ~/.claude/bash-command-log.txt
exit 0  # Always allow execution
```

**Benefits**:
- Audit trail for compliance
- Debugging assistance
- Command history for analysis

---

### 5. Destructive Command Confirmation

**Type**: GENERIC
**Tools**: Bash
**Priority**: MEDIUM

**Purpose**: Block potentially destructive commands unless explicitly confirmed by user.

**Dangerous Patterns**:
- `rm -rf`
- `dd if=`
- `mkfs`
- `fdisk`
- `> /dev/sd*`

**Implementation Example**:
```bash
cmd=$(echo "$tool_input" | jq -r '.command')

if echo "$cmd" | grep -qE 'rm\s+-[rf]{1,2}\s+/|dd\s+if=|mkfs|fdisk'; then
  echo "ERROR: Potentially destructive command detected: $cmd"
  echo "This command has been blocked for safety."
  exit 1
fi

exit 0
```

**Benefits**:
- Prevents catastrophic data loss
- Safety net for automation
- User protection

---

## PostToolUse Hooks

PostToolUse hooks execute after a tool completes successfully. They're ideal for automation, formatting, validation, and notifications.

### 6. Auto-format Python Files

**Type**: PROJECT-SPECIFIC (Python)
**Tools**: Write, Edit
**Priority**: HIGH

**Purpose**: Automatically format Python files with `ruff format` after editing to ensure consistent code style.

**Triggers When**:
- Any `.py` file is written or edited

**Implementation Example**:
```bash
file_path=$(echo "$tool_input" | jq -r '.file_path')

if [[ "$file_path" == *.py ]]; then
  ruff format "$file_path" 2>&1
  if [ $? -eq 0 ]; then
    echo "✓ Auto-formatted: $file_path"
  else
    echo "⚠ Formatting failed for: $file_path"
  fi
fi

exit 0  # Don't fail even if formatting has issues
```

**Benefits**:
- Consistent code style
- Saves manual formatting step
- Immediate feedback

---

### 7. Auto-lint Python Files

**Type**: PROJECT-SPECIFIC (Python)
**Tools**: Write, Edit
**Priority**: HIGH

**Purpose**: Automatically run `ruff check --fix` on Python files after editing to fix auto-fixable linting issues.

**Triggers When**:
- Any `.py` file is written or edited

**Implementation Example**:
```bash
file_path=$(echo "$tool_input" | jq -r '.file_path')

if [[ "$file_path" == *.py ]]; then
  ruff check --fix "$file_path" 2>&1
  if [ $? -eq 0 ]; then
    echo "✓ Auto-linted: $file_path"
  else
    echo "⚠ Linting issues remain in: $file_path (run 'ruff check $file_path' for details)"
  fi
fi

exit 0
```

**Benefits**:
- Automatic code quality fixes
- Reduces manual linting effort
- Immediate issue detection

---

### 8. Run Affected Tests

**Type**: PROJECT-SPECIFIC (Python/pytest)
**Tools**: Write, Edit
**Priority**: MEDIUM

**Purpose**: Automatically run tests related to the modified Python file to provide immediate feedback.

**Triggers When**:
- Any `.py` file in `src/` is written or edited

**Implementation Example**:
```bash
file_path=$(echo "$tool_input" | jq -r '.file_path')

if [[ "$file_path" == src/*.py ]]; then
  # Derive test file path
  test_file=$(echo "$file_path" | sed 's|src/|tests/|; s|\.py$|_test.py|')

  if [ -f "$test_file" ]; then
    echo "Running tests for modified file..."
    python -m pytest "$test_file" -v

    if [ $? -ne 0 ]; then
      echo "⚠ Tests failed for: $test_file"
    fi
  fi
fi

exit 0
```

**Benefits**:
- Immediate test feedback
- Catches regressions early
- Encourages TDD workflow

**Note**: This can slow down development for large test suites. Consider making it optional or running only fast tests.

---

### 9. CHANGELOG Reminder

**Type**: GENERIC
**Tools**: Write, Edit
**Priority**: LOW

**Purpose**: Remind developer to update CHANGELOG.md when significant code changes are made.

**Triggers When**:
- Files in `src/` are modified
- `pyproject.toml` is modified (version changes)

**Implementation Example**:
```bash
file_path=$(echo "$tool_input" | jq -r '.file_path')

if [[ "$file_path" == src/* ]] || [[ "$file_path" == *pyproject.toml ]]; then
  echo "📝 Reminder: Consider updating CHANGELOG.md if this is a notable change"
fi

exit 0
```

**Benefits**:
- Keeps CHANGELOG current
- Improves release documentation
- Gentle reminder without blocking

---

### 10. Bash Command Logger (Post-execution)

**Type**: GENERIC
**Tools**: Bash
**Priority**: LOW

**Purpose**: Log all successfully executed bash commands with their output for audit and debugging.

**Implementation Example**:
```bash
# Log command, description, and timestamp
{
  echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
  echo "Command: $(echo "$tool_input" | jq -r '.command')"
  echo "Description: $(echo "$tool_input" | jq -r '.description // "No description"')"
  echo "Status: SUCCESS"
  echo ""
} >> ~/.claude/bash-command-log.txt

exit 0
```

**Benefits**:
- Complete audit trail
- Debugging assistance
- Command history analysis

---

### 11. Git Commit Message Validator

**Type**: GENERIC
**Tools**: Bash
**Priority**: MEDIUM

**Purpose**: After a git commit, verify that the commit message follows conventional commit format.

**Triggers When**:
- Bash command contains `git commit`

**Implementation Example**:
```bash
cmd=$(echo "$tool_input" | jq -r '.command')

if echo "$cmd" | grep -q 'git commit'; then
  # Get the last commit message
  commit_msg=$(git log -1 --pretty=%B)

  # Check conventional commit format: type(scope): description
  if ! echo "$commit_msg" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+'; then
    echo "⚠ WARNING: Commit message doesn't follow conventional commit format"
    echo "Expected: type(scope): description"
    echo "Examples: feat(cli): add new command, fix(auth): handle null response"
    echo ""
    echo "Your commit: $commit_msg"
  else
    echo "✓ Commit message follows conventional commit format"
  fi
fi

exit 0
```

**Benefits**:
- Enforces commit conventions
- Improves changelog generation
- Better git history

---

### 12. Package Build Verification

**Type**: PROJECT-SPECIFIC (Python/uv)
**Tools**: Bash
**Priority**: LOW

**Purpose**: After running `uv build`, verify that the package was built correctly and artifacts exist.

**Triggers When**:
- Bash command is `uv build`

**Implementation Example**:
```bash
cmd=$(echo "$tool_input" | jq -r '.command')

if [[ "$cmd" == *"uv build"* ]]; then
  if [ -d "dist/" ]; then
    wheel_count=$(ls -1 dist/*.whl 2>/dev/null | wc -l)
    tar_count=$(ls -1 dist/*.tar.gz 2>/dev/null | wc -l)

    echo "✓ Build artifacts created:"
    echo "  - Wheels: $wheel_count"
    echo "  - Source distributions: $tar_count"
    ls -lh dist/
  else
    echo "⚠ No dist/ directory found after build"
  fi
fi

exit 0
```

**Benefits**:
- Build verification
- Immediate feedback
- Artifact validation

---

## Other Hook Types

### 13. UserPromptSubmit: Context Injection

**Type**: PROJECT-SPECIFIC (jp-spec-kit agents)
**Priority**: LOW

**Purpose**: Automatically inject project-specific context when users submit prompts related to agents.

**Implementation Example**:
```bash
prompt=$(echo "$tool_input" | jq -r '.prompt')

if echo "$prompt" | grep -qiE 'agent|spec-driven|jpspec'; then
  echo "ℹ️ Note: Relevant agent documentation is in .agents/ directory"
  echo "Use /jpspec commands for agent workflows"
fi

exit 0
```

**Benefits**:
- Helps users discover features
- Provides context
- Guides workflow usage

---

### 14. SessionStart: Prerequisites Check

**Type**: GENERIC
**Priority**: MEDIUM

**Purpose**: At session start, verify that required tools and dependencies are available.

**Implementation Example**:
```bash
#!/bin/bash

echo "Checking prerequisites..."

# Check Python
if ! command -v python &> /dev/null; then
  echo "⚠ Python not found"
fi

# Check uv
if ! command -v uv &> /dev/null; then
  echo "⚠ uv not found (run: pip install uv)"
fi

# Check ruff
if ! command -v ruff &> /dev/null; then
  echo "⚠ ruff not found (run: uv tool install ruff)"
fi

# Check pytest
if ! python -c "import pytest" 2>/dev/null; then
  echo "⚠ pytest not installed (run: uv sync)"
fi

echo "✓ Prerequisites check complete"
exit 0
```

**Benefits**:
- Early problem detection
- Better user experience
- Prevents confusing errors

---

### 15. SubagentStop: Result Aggregation

**Type**: PROJECT-SPECIFIC (jp-spec-kit agents)
**Priority**: LOW

**Purpose**: After a jpspec subagent completes, aggregate and summarize results.

**Implementation Example**:
```bash
agent_type=$(echo "$tool_input" | jq -r '.agent_type // "unknown"')

echo "📊 Subagent '$agent_type' completed"
echo "Review results above and consider next steps in the workflow"

# Could also log to a session summary file
exit 0
```

**Benefits**:
- Better workflow visibility
- Result tracking
- User guidance

---

### 16. Stop: Session Summary

**Type**: GENERIC
**Priority**: LOW

**Purpose**: When Claude finishes responding, provide a summary of actions taken.

**Implementation Example**:
```bash
# Could analyze transcript and provide summary
echo "Session response complete. Review above for actions taken."
exit 0
```

**Benefits**:
- Session awareness
- Action tracking
- User clarity

---

### 17. Notification: Desktop Notifications

**Type**: GENERIC
**Priority**: LOW

**Purpose**: Send desktop notifications when Claude needs user input or permission.

**Implementation Example**:
```bash
# macOS
if command -v osascript &> /dev/null; then
  osascript -e 'display notification "Claude Code needs your attention" with title "Claude Code"'
fi

# Linux (notify-send)
if command -v notify-send &> /dev/null; then
  notify-send "Claude Code" "Needs your attention"
fi

exit 0
```

**Benefits**:
- User awareness
- Reduces waiting
- Better UX for long operations

---

## Recommended Priority Implementation Order

Based on impact and utility for jp-spec-kit:

### Phase 1: High Priority (Implement First)
1. **Sensitive File Protection** (PreToolUse) - Prevents critical mistakes
2. **Git Command Safety Validator** (PreToolUse) - Prevents data loss
3. **Auto-format Python Files** (PostToolUse) - Saves time, ensures consistency
4. **Auto-lint Python Files** (PostToolUse) - Automatic code quality

### Phase 2: Medium Priority
5. **Version Consistency Checker** (PreToolUse) - Prevents release errors
6. **Git Commit Message Validator** (PostToolUse) - Better git history
7. **Destructive Command Confirmation** (PreToolUse) - Safety net
8. **Prerequisites Check** (SessionStart) - Better DX

### Phase 3: Low Priority (Nice to Have)
9. **Bash Command Logger** (Pre/Post) - Audit trail
10. **CHANGELOG Reminder** (PostToolUse) - Documentation reminder
11. **Run Affected Tests** (PostToolUse) - Fast feedback (if performance acceptable)
12. **Desktop Notifications** (Notification) - UX improvement
13. **Context Injection** (UserPromptSubmit) - User guidance
14. **Package Build Verification** (PostToolUse) - Build validation

---

## Implementation Notes

### Configuration Location

Hooks can be configured in:
- `~/.claude/settings.json` - User-wide hooks (generic hooks)
- `.claude/settings.json` - Project-specific hooks (jp-spec-kit specific)
- `.claude/settings.local.json` - Local overrides (gitignored)

### Performance Considerations

- Keep hooks fast (< 1 second for PreToolUse)
- Use async operations where possible
- Consider making heavy hooks (tests, builds) optional
- Log to files rather than databases for speed

### Testing Hooks

Before enabling hooks in production:
1. Test with dry-run mode
2. Verify exit codes work correctly
3. Check timeout behavior
4. Test with various tool inputs
5. Ensure error messages are clear

### Hook Debugging

If hooks misbehave:
- Check `~/.claude/logs/` for hook execution logs
- Test hooks manually with sample JSON input
- Use `set -x` in bash hooks for debugging
- Verify file permissions on hook scripts

---

## Example Configuration Snippets

### High-Priority Hooks Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$tool_input\" | jq -r '.file_path' | grep -E '\\.(env|lock)$|\\.git/|LICENSE|SECURITY\\.md' && echo 'ERROR: Cannot modify protected file' && exit 1 || exit 0",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=$(echo \"$tool_input\" | jq -r '.command'); echo \"$cmd\" | grep -qE 'git push.*(--force|-f).*(main|master)' && echo 'ERROR: Force push to main/master blocked' && exit 1 || exit 0",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "file=$(echo \"$tool_input\" | jq -r '.file_path'); [[ \"$file\" == *.py ]] && ruff format \"$file\" && ruff check --fix \"$file\" || exit 0",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

---

## Summary

This document provides **17 hook suggestions** covering:
- **5 PreToolUse hooks** - Validation and safety
- **7 PostToolUse hooks** - Automation and verification
- **5 Other hook types** - Session management and notifications

Each hook is categorized as:
- **GENERIC** (10 hooks) - Applicable to most projects
- **PROJECT-SPECIFIC** (7 hooks) - Tailored to jp-spec-kit/Python projects

The hooks focus on:
- Safety and data protection
- Code quality and consistency
- Developer experience
- Workflow automation
- Audit and compliance

Start with **Phase 1 high-priority hooks** for maximum immediate impact, then expand to medium and low priority hooks based on team needs and feedback.
