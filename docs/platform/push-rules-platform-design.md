# Git Push Rules Enforcement - Platform Design

**Feature ID**: push-rules-enforcement
**Parent Task**: task-300
**Status**: Platform Design
**Author**: @platform-engineer
**Created**: 2025-12-07

---

## Overview

This document defines the platform engineering architecture for the Git Push Rules Enforcement System. It provides implementation patterns, state management design, hook architecture, and testing strategies following existing JP Spec Kit conventions.

## Architecture Principles

1. **Follow existing patterns**: Leverage `.claude/hooks/` conventions
2. **Fail-open for warnings**: Non-blocking validation warnings
3. **Fail-closed for errors**: Block on critical violations
4. **State persistence**: File-based state in `.specify/state/`
5. **Offline-first**: No network dependencies for core validation
6. **Performance budget**: <5 seconds total hook execution time

---

## 1. Hook Implementation Design

### 1.1 Hook Architecture

The Git Push Rules system follows the established hook pattern in `.claude/hooks/`:

```
.claude/hooks/
├── pre-push-validate.sh      # Pre-push validation (NEW)
├── session-start.sh           # Environment setup (MODIFIED)
├── pre-implement.sh           # Quality gates (REFERENCE)
└── test-pre-push-validate.sh # Hook tests (NEW)
```

### 1.2 Pre-Push Validation Hook

**Location**: `.claude/hooks/pre-push-validate.sh`

**Purpose**: Validate push-rules.md requirements before allowing `git push`

**Hook Pattern Reference**:
- Input: JSON on stdin (from Claude Code hook system)
- Output: JSON decision to stdout
- Exit code: 0 (always - use decision field to control blocking)

**Implementation Pattern**:

```bash
#!/bin/bash
# Pre-push validation hook
# Validates push-rules.md before allowing git push

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Exit codes (for internal gate tracking)
EXIT_SUCCESS=0
EXIT_FAILURE=1

# Default paths
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PUSH_RULES_FILE="${PROJECT_DIR}/push-rules.md"
STATE_DIR="${PROJECT_DIR}/.specify/state"

# Gate results
GATES_PASSED=true
GATE_ERRORS=()
GATE_WARNINGS=()

# Read JSON input from stdin
input=$(cat)

# Parse bypass flag from tool_input
SKIP_PUSH_RULES=false
if command -v jq &> /dev/null; then
    command_args=$(echo "$input" | jq -r '.tool_input.command // ""')
    if [[ "$command_args" =~ --skip-push-rules ]]; then
        SKIP_PUSH_RULES=true
    fi
else
    # Fallback Python parsing
    command_args=$(echo "$input" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('tool_input', {}).get('command', ''))")
    if [[ "$command_args" == *"--skip-push-rules"* ]]; then
        SKIP_PUSH_RULES=true
    fi
fi

# Handle bypass flag
if [[ "$SKIP_PUSH_RULES" == "true" ]]; then
    # Log bypass to audit trail
    echo "$(date -Iseconds) - Push rules bypassed by user" >> "${STATE_DIR}/audit.log"

    echo '{"decision": "allow", "reason": "Push rules bypassed with --skip-push-rules", "additionalContext": "WARNING: Quality gates were bypassed. This may lead to CI failures."}'
    exit 0
fi

echo "Push Rules Validation"
echo "====================="
echo ""

#########################################
# Gate 1: Load push-rules.md
#########################################
echo "[1/4] Checking push-rules.md..."

if [[ ! -f "$PUSH_RULES_FILE" ]]; then
    GATES_PASSED=false
    GATE_ERRORS+=("push-rules.md not found in project root")
    GATE_ERRORS+=("Run 'specify init' to create template")
else
    # Validate YAML frontmatter
    if ! head -20 "$PUSH_RULES_FILE" | grep -q "^version:"; then
        GATES_PASSED=false
        GATE_ERRORS+=("Invalid push-rules.md format (missing version field)")
    else
        echo -e "${GREEN}✓${NC} push-rules.md loaded"
    fi
fi

echo ""

#########################################
# Gate 2: Rebase Status Check
#########################################
echo "[2/4] Checking rebase status vs main..."

if [[ "$GATES_PASSED" == "true" ]]; then
    # Extract base branch from push-rules.md
    BASE_BRANCH=$(grep -A2 "Rebase Policy" "$PUSH_RULES_FILE" | grep "Base Branch:" | sed 's/.*: //' || echo "main")

    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    # Skip check if on base branch
    if [[ "$CURRENT_BRANCH" == "$BASE_BRANCH" ]]; then
        GATE_WARNINGS+=("You are on $BASE_BRANCH - push rules apply to feature branches only")
    else
        # Check for merge commits since diverging from base
        MERGE_BASE=$(git merge-base "$BASE_BRANCH" HEAD)
        MERGE_COMMITS=$(git log "$MERGE_BASE..HEAD" --merges --oneline | wc -l)

        if [[ "$MERGE_COMMITS" -gt 0 ]]; then
            GATES_PASSED=false
            GATE_ERRORS+=("Merge commits detected in branch history:")

            # Show merge commit details
            while IFS= read -r merge_line; do
                GATE_ERRORS+=("  - $merge_line")
            done < <(git log "$MERGE_BASE..HEAD" --merges --oneline)

            GATE_ERRORS+=("")
            GATE_ERRORS+=("Rebase your branch:")
            GATE_ERRORS+=("  git rebase -i $BASE_BRANCH")
        else
            echo -e "${GREEN}✓${NC} No merge commits detected"

            # Check if branch is up-to-date
            COMMITS_AHEAD=$(git rev-list --count "$MERGE_BASE..HEAD")
            echo -e "${GREEN}✓${NC} Branch is $COMMITS_AHEAD commits ahead of $BASE_BRANCH"
        fi
    fi
fi

echo ""

#########################################
# Gate 3: Lint Check
#########################################
echo "[3/4] Running lint check..."

if [[ "$GATES_PASSED" == "true" ]]; then
    # Extract lint command from push-rules.md
    LINT_REQUIRED=$(grep -A5 "### Linting" "$PUSH_RULES_FILE" | grep "Required:" | grep -q "true" && echo "true" || echo "false")

    if [[ "$LINT_REQUIRED" == "true" ]]; then
        LINT_COMMAND=$(grep -A5 "### Linting" "$PUSH_RULES_FILE" | grep "Command:" | sed 's/.*: //' | tr -d '`')

        # Run lint command
        if eval "$LINT_COMMAND" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Lint check passed (0 errors)"
        else
            GATES_PASSED=false
            GATE_ERRORS+=("Lint check failed:")

            # Capture and display lint errors
            lint_output=$(eval "$LINT_COMMAND" 2>&1 || true)
            GATE_ERRORS+=("$lint_output")
            GATE_ERRORS+=("")
            GATE_ERRORS+=("Fix linting issues and try again")
        fi
    else
        echo -e "${YELLOW}⚠${NC} Linting not required by push-rules.md"
    fi
fi

echo ""

#########################################
# Gate 4: Test Check
#########################################
echo "[4/4] Running tests..."

if [[ "$GATES_PASSED" == "true" ]]; then
    # Extract test command from push-rules.md
    TEST_REQUIRED=$(grep -A5 "### Testing" "$PUSH_RULES_FILE" | grep "Required:" | grep -q "true" && echo "true" || echo "false")

    if [[ "$TEST_REQUIRED" == "true" ]]; then
        TEST_COMMAND=$(grep -A5 "### Testing" "$PUSH_RULES_FILE" | grep "Command:" | sed 's/.*: //' | tr -d '`')

        # Run test command
        if eval "$TEST_COMMAND" > /dev/null 2>&1; then
            # Count test results if pytest
            if [[ "$TEST_COMMAND" == *"pytest"* ]]; then
                test_count=$(eval "$TEST_COMMAND" 2>&1 | grep -oP '\d+(?= passed)' || echo "all")
                echo -e "${GREEN}✓${NC} Tests passed ($test_count tests)"
            else
                echo -e "${GREEN}✓${NC} Tests passed"
            fi
        else
            GATES_PASSED=false
            GATE_ERRORS+=("Test check failed:")

            # Capture and display test errors
            test_output=$(eval "$TEST_COMMAND" 2>&1 || true)
            GATE_ERRORS+=("$test_output")
            GATE_ERRORS+=("")
            GATE_ERRORS+=("Fix failing tests and try again")
        fi
    else
        echo -e "${YELLOW}⚠${NC} Testing not required by push-rules.md"
    fi
fi

echo ""
echo "=========================================="

# Build decision output
if [[ "$GATES_PASSED" == "true" ]]; then
    echo -e "${GREEN}✅ All push rules satisfied. Proceeding with push.${NC}"

    # Show warnings if any
    if [[ ${#GATE_WARNINGS[@]} -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}Warnings:${NC}"
        for warning in "${GATE_WARNINGS[@]}"; do
            echo -e "  ${YELLOW}⚠${NC} $warning"
        done
    fi

    echo '{"decision": "allow", "reason": "All push rules satisfied"}'
    exit 0
else
    echo -e "${RED}❌ Push blocked. Fix the following issues:${NC}"
    echo ""
    for error in "${GATE_ERRORS[@]}"; do
        echo -e "${RED}${error}${NC}"
    done
    echo ""
    echo -e "${YELLOW}To bypass (emergency only):${NC}"
    echo "  git push --skip-push-rules"

    # Build error context for JSON
    error_context=$(printf "%s\n" "${GATE_ERRORS[@]}")

    python3 <<EOF
import json

decision = {
    "decision": "deny",
    "reason": "Push rules validation failed",
    "additionalContext": """$error_context"""
}

print(json.dumps(decision))
EOF

    exit 0  # Always exit 0, decision field controls blocking
fi
```

### 1.3 Session-Start Hook Modification

**Location**: `.claude/hooks/session-start.sh`

**Modification**: Add janitor warning section after line 92

```bash
# After backlog.md check (around line 92), add:

# Check for pending janitor cleanup
if [[ -f "$PROJECT_DIR/.specify/state/pending-cleanup.json" ]]; then
    # Parse pending cleanup state
    if command -v jq &> /dev/null; then
        pending_branches=$(jq -r '.pending_branches | length' "$PROJECT_DIR/.specify/state/pending-cleanup.json" 2>/dev/null || echo "0")
        pending_worktrees=$(jq -r '.pending_worktrees | length' "$PROJECT_DIR/.specify/state/pending-cleanup.json" 2>/dev/null || echo "0")
    else
        # Fallback: count items manually
        pending_branches=$(grep -c '"pending_branches"' "$PROJECT_DIR/.specify/state/pending-cleanup.json" 2>/dev/null || echo "0")
        pending_worktrees=$(grep -c '"pending_worktrees"' "$PROJECT_DIR/.specify/state/pending-cleanup.json" 2>/dev/null || echo "0")
    fi

    total_pending=$((pending_branches + pending_worktrees))

    if [[ "$total_pending" -gt 0 ]]; then
        warnings+=("Janitor cleanup pending: $pending_branches merged branches, $pending_worktrees stale worktrees")
        warnings+=("Run /jpspec:validate or github-janitor to cleanup")
    fi
fi
```

---

## 2. State Management Design

### 2.1 State Directory Structure

**Location**: `.specify/state/`

**Purpose**: Persistent state tracking for janitor warnings and audit trail

**Structure**:
```
.specify/state/
├── janitor-last-run        # ISO timestamp of last janitor execution
├── pending-cleanup.json    # List of items pending cleanup
└── audit.log               # Audit trail for bypass events
```

### 2.2 State File Formats

#### janitor-last-run

**Format**: Plain text, single ISO 8601 timestamp

```
2025-12-07T20:15:30Z
```

**Update pattern**:
```bash
# After successful janitor run
date -Iseconds > "${STATE_DIR}/janitor-last-run"
```

#### pending-cleanup.json

**Format**: JSON with pending cleanup items

```json
{
  "last_updated": "2025-12-07T20:15:30Z",
  "pending_branches": [
    {
      "name": "feature/old-feature",
      "merged_at": "2025-11-30T14:22:00Z",
      "pr_number": 123
    }
  ],
  "pending_worktrees": [
    {
      "path": "/path/to/worktree",
      "branch": "feature/deleted-remote",
      "orphaned_since": "2025-12-01T10:00:00Z"
    }
  ]
}
```

**Write pattern**:
```bash
# After janitor analysis, before cleanup
python3 <<EOF
import json
from datetime import datetime

state = {
    "last_updated": datetime.utcnow().isoformat() + "Z",
    "pending_branches": [],
    "pending_worktrees": []
}

# Populate from janitor scan results
# ...

with open("${STATE_DIR}/pending-cleanup.json", "w") as f:
    json.dump(state, f, indent=2)
EOF
```

**Clear pattern**:
```bash
# After successful cleanup
echo '{"last_updated": "'$(date -Iseconds)'", "pending_branches": [], "pending_worktrees": []}' > "${STATE_DIR}/pending-cleanup.json"
```

#### audit.log

**Format**: Plain text log, one event per line

```
2025-12-07T20:15:30Z - Push rules bypassed by user (branch: feature/urgent-fix)
2025-12-07T20:22:15Z - Janitor cleanup executed (3 branches pruned)
2025-12-07T21:00:00Z - Pre-push validation blocked (lint failed)
```

**Append pattern**:
```bash
# Log audit event
echo "$(date -Iseconds) - Event description here" >> "${STATE_DIR}/audit.log"
```

### 2.3 State Directory Initialization

**When**: During `specify init` execution

**Implementation** (in `specify init` CLI):

```python
# In src/specify_cli/__init__.py, init() function
import os
from pathlib import Path

def init_state_directory(project_dir: Path):
    """Initialize .specify/state directory with default files."""
    state_dir = project_dir / ".specify" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Create janitor-last-run (empty initially)
    (state_dir / "janitor-last-run").touch()

    # Create pending-cleanup.json with empty state
    import json
    from datetime import datetime

    initial_state = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "pending_branches": [],
        "pending_worktrees": []
    }

    with open(state_dir / "pending-cleanup.json", "w") as f:
        json.dump(initial_state, f, indent=2)

    # Create audit.log with initialization event
    with open(state_dir / "audit.log", "w") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z - State directory initialized\n")

    # Add to .gitignore
    gitignore_path = project_dir / ".gitignore"
    gitignore_entry = "\n# JP Spec Kit state files\n.specify/state/\n"

    if gitignore_path.exists():
        with open(gitignore_path, "a") as f:
            f.write(gitignore_entry)
    else:
        with open(gitignore_path, "w") as f:
            f.write(gitignore_entry)
```

---

## 3. CLI Integration Design

### 3.1 specify init Extension

**Modification**: Add push-rules.md template installation to init workflow

**Implementation Steps**:

1. **Copy push-rules.md template** to project root
2. **Initialize state directory** (see Section 2.3)
3. **Display setup confirmation** with next steps

**Code Location**: `src/specify_cli/__init__.py`, `init()` function

**Implementation**:

```python
# After existing template copying (around line 2700)

# Copy push-rules.md template
push_rules_template = template_dir / "push-rules-template.md"
push_rules_dest = project_dir / "push-rules.md"

if push_rules_template.exists():
    shutil.copy(push_rules_template, push_rules_dest)
    typer.echo(f"✓ Created push-rules.md")
else:
    typer.echo("⚠ Warning: push-rules.md template not found", err=True)

# Initialize state directory
init_state_directory(project_dir)
typer.echo(f"✓ Initialized .specify/state/")

# Display setup confirmation
typer.echo("\n" + "=" * 60)
typer.echo("Git Push Rules Enforcement Setup")
typer.echo("=" * 60)
typer.echo(f"\n✓ push-rules.md created at project root")
typer.echo(f"✓ State directory initialized at .specify/state/")
typer.echo(f"\nNext steps:")
typer.echo(f"  1. Review push-rules.md and customize for your project")
typer.echo(f"  2. Pre-push hook will automatically validate rules")
typer.echo(f"  3. Run /jpspec:validate to trigger janitor cleanup")
typer.echo("=" * 60 + "\n")
```

### 3.2 Template Structure

**Location**: `templates/push-rules-template.md`

**Content**: See PRD Appendix A for full template

**Key sections**:
- YAML frontmatter (version, enabled, bypass_flag)
- Rebase Policy
- Validation Requirements (Linting, Testing)
- Branch Naming Convention
- Janitor Settings

---

## 4. Test Strategy

### 4.1 Unit Tests (pytest)

**Location**: `tests/platform/`

**Test Files**:

#### `tests/platform/test_push_rules_parser.py`

```python
"""Unit tests for push-rules.md parser."""
import pytest
from pathlib import Path

def test_parse_valid_push_rules():
    """Test parsing valid push-rules.md."""
    # Given: Valid push-rules.md content
    content = """---
version: "1.0"
enabled: true
---
# Git Push Rules
"""

    # When: Parsed
    config = parse_push_rules(content)

    # Then: Config is valid
    assert config["version"] == "1.0"
    assert config["enabled"] is True

def test_parse_invalid_yaml_frontmatter():
    """Test error on invalid YAML frontmatter."""
    # Given: Invalid YAML
    content = """---
version: 1.0
invalid: [unclosed
---
"""

    # When/Then: Raises validation error
    with pytest.raises(ValueError, match="Invalid YAML"):
        parse_push_rules(content)

def test_extract_lint_command():
    """Test extracting lint command from push-rules.md."""
    # Given: push-rules.md with lint config
    content = """
### Linting
- **Required**: true
- **Command**: `uv run ruff check .`
"""

    # When: Extract command
    command = extract_lint_command(content)

    # Then: Correct command
    assert command == "uv run ruff check ."
```

#### `tests/platform/test_rebase_detector.py`

```python
"""Unit tests for rebase detection logic."""
import pytest
from git import Repo

def test_detect_merge_commits_in_branch(tmp_path):
    """Test detection of merge commits in feature branch."""
    # Given: Git repo with merge commit
    repo = Repo.init(tmp_path)
    # ... create commits and merge

    # When: Check for merge commits
    has_merges = has_merge_commits(repo, "main", "feature/test")

    # Then: Detects merge commits
    assert has_merges is True

def test_no_merge_commits_in_rebased_branch(tmp_path):
    """Test clean branch passes rebase check."""
    # Given: Git repo with rebased branch
    repo = Repo.init(tmp_path)
    # ... create rebased commits

    # When: Check for merge commits
    has_merges = has_merge_commits(repo, "main", "feature/test")

    # Then: No merge commits
    assert has_merges is False
```

#### `tests/platform/test_janitor_state.py`

```python
"""Unit tests for janitor state management."""
import pytest
import json
from pathlib import Path
from datetime import datetime

def test_write_pending_cleanup_state(tmp_path):
    """Test writing pending cleanup state."""
    # Given: State directory
    state_dir = tmp_path / ".specify" / "state"
    state_dir.mkdir(parents=True)

    # When: Write pending cleanup
    pending = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "pending_branches": [
            {"name": "feature/old", "merged_at": "2025-11-30T00:00:00Z"}
        ],
        "pending_worktrees": []
    }

    write_pending_cleanup(state_dir, pending)

    # Then: File exists with correct content
    state_file = state_dir / "pending-cleanup.json"
    assert state_file.exists()

    with open(state_file) as f:
        loaded = json.load(f)

    assert len(loaded["pending_branches"]) == 1
    assert loaded["pending_branches"][0]["name"] == "feature/old"

def test_read_janitor_last_run(tmp_path):
    """Test reading janitor last run timestamp."""
    # Given: janitor-last-run file
    state_dir = tmp_path / ".specify" / "state"
    state_dir.mkdir(parents=True)

    timestamp = "2025-12-07T20:00:00Z"
    (state_dir / "janitor-last-run").write_text(timestamp)

    # When: Read timestamp
    last_run = read_janitor_last_run(state_dir)

    # Then: Correct timestamp
    assert last_run == timestamp
```

### 4.2 Integration Tests (bash)

**Location**: `.claude/hooks/test-pre-push-validate.sh`

**Pattern**: Follow `test-hooks.sh` pattern for hook testing

```bash
#!/bin/bash
#
# Test script for pre-push-validate.sh hook
#
# Tests pre-push validation with various scenarios
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Test function
run_test() {
    local test_name="$1"
    local hook_script="$2"
    local input_json="$3"
    local expected_decision="$4"
    local description="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -e "\n${YELLOW}Test $TESTS_RUN: $test_name${NC}"
    echo "Description: $description"

    # Run hook and capture output
    output=$(echo "$input_json" | "$SCRIPT_DIR/$hook_script" 2>&1)
    exit_code=$?

    # Verify exit code is 0
    if [[ $exit_code -ne 0 ]]; then
        echo -e "${RED}FAIL: Non-zero exit code${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Extract decision from JSON
    decision=$(echo "$output" | python3 -c "
import json, sys
for line in sys.stdin:
    try:
        data = json.loads(line.strip())
        if 'decision' in data:
            print(data['decision'])
            break
    except: continue
" 2>/dev/null || echo "")

    # Verify decision matches expected
    if [[ "$decision" == "$expected_decision" ]]; then
        echo -e "${GREEN}PASS: Decision = $decision${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAIL: Expected '$expected_decision', got '$decision'${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

echo "========================================"
echo "Pre-Push Validate Hook Test Suite"
echo "========================================"

# Test 1: Missing push-rules.md
run_test \
    "Missing push-rules.md" \
    "pre-push-validate.sh" \
    '{"tool_name": "Bash", "tool_input": {"command": "git push origin feature/test"}}' \
    "deny" \
    "Should deny when push-rules.md is missing"

# Test 2: Bypass flag
run_test \
    "Bypass with --skip-push-rules" \
    "pre-push-validate.sh" \
    '{"tool_name": "Bash", "tool_input": {"command": "git push --skip-push-rules origin feature/test"}}' \
    "allow" \
    "Should allow when bypass flag is used"

# Test 3: Valid push (all gates pass)
run_test \
    "Valid push - all gates pass" \
    "pre-push-validate.sh" \
    '{"tool_name": "Bash", "tool_input": {"command": "git push origin feature/test"}}' \
    "allow" \
    "Should allow when all validation gates pass"

# Test 4: Lint failure
run_test \
    "Lint check fails" \
    "pre-push-validate.sh" \
    '{"tool_name": "Bash", "tool_input": {"command": "git push origin feature/lint-fail"}}' \
    "deny" \
    "Should deny when lint check fails"

# Test 5: Test failure
run_test \
    "Test check fails" \
    "pre-push-validate.sh" \
    '{"tool_name": "Bash", "tool_input": {"command": "git push origin feature/test-fail"}}' \
    "deny" \
    "Should deny when test check fails"

# Summary
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
if [[ $TESTS_FAILED -gt 0 ]]; then
    echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
```

### 4.3 End-to-End Tests

**Scenario**: Full workflow validation

**Location**: `tests/e2e/test_push_rules_workflow.py`

```python
"""End-to-end tests for push rules workflow."""
import pytest
from pathlib import Path
import subprocess

def test_full_push_rules_workflow(tmp_path):
    """Test complete workflow: init -> validate -> push."""
    # Given: New project
    project_dir = tmp_path / "test-project"

    # When: Initialize with specify init
    subprocess.run(["specify", "init", str(project_dir)], check=True)

    # Then: push-rules.md exists
    assert (project_dir / "push-rules.md").exists()

    # And: State directory initialized
    assert (project_dir / ".specify" / "state").exists()
    assert (project_dir / ".specify" / "state" / "janitor-last-run").exists()

    # When: Create feature branch with valid changes
    # ... git operations

    # And: Run pre-push validation
    result = subprocess.run(
        ["bash", ".claude/hooks/pre-push-validate.sh"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    # Then: Validation passes
    assert "allow" in result.stdout
```

### 4.4 Test Coverage Requirements

**Minimum Coverage**: 80% for new code

**Key Coverage Areas**:
- Push-rules.md parsing (100%)
- Rebase detection logic (90%)
- State management (100%)
- Hook execution flow (85%)

**Coverage Tools**:
```bash
# Python unit tests
pytest tests/platform/ --cov=src/specify_cli --cov-report=term --cov-report=html

# Bash integration tests
# Use shellcheck for static analysis
shellcheck .claude/hooks/pre-push-validate.sh
```

---

## 5. Performance Optimization

### 5.1 Performance Budget

**Total Hook Execution Time**: <5 seconds

**Budget Breakdown**:
- push-rules.md parsing: <100ms
- Rebase check (git operations): <1s
- Lint execution: <2s (project-dependent)
- Test execution: <2s (fast test subset)

### 5.2 Optimization Strategies

#### Fast Fail Pattern

```bash
# Exit early on first failure
if [[ ! -f "$PUSH_RULES_FILE" ]]; then
    echo '{"decision": "deny", ...}'
    exit 0  # Don't run remaining gates
fi
```

#### Parallel Execution

```bash
# Run lint and tests in parallel (if independent)
lint_output=$(eval "$LINT_COMMAND" 2>&1) &
lint_pid=$!

test_output=$(eval "$TEST_COMMAND" 2>&1) &
test_pid=$!

# Wait for both
wait $lint_pid
lint_exit=$?

wait $test_pid
test_exit=$?
```

#### Caching

```bash
# Cache git merge-base results
MERGE_BASE_CACHE="${STATE_DIR}/merge-base-cache"
if [[ -f "$MERGE_BASE_CACHE" ]]; then
    MERGE_BASE=$(cat "$MERGE_BASE_CACHE")
else
    MERGE_BASE=$(git merge-base "$BASE_BRANCH" HEAD)
    echo "$MERGE_BASE" > "$MERGE_BASE_CACHE"
fi
```

---

## 6. Security Considerations

### 6.1 Command Injection Prevention

**Risk**: Extracted commands from push-rules.md could be malicious

**Mitigation**:

```bash
# Sanitize commands before eval
sanitize_command() {
    local cmd="$1"

    # Remove dangerous patterns
    if [[ "$cmd" =~ (rm -rf|mkfs|dd if=|>|curl.*\|) ]]; then
        echo "ERROR: Dangerous command detected in push-rules.md" >&2
        return 1
    fi

    echo "$cmd"
}

# Use sanitized command
LINT_COMMAND=$(sanitize_command "$LINT_COMMAND")
```

### 6.2 State File Permissions

**Requirement**: State files should not be world-readable

**Implementation**:

```bash
# Set restrictive permissions on state directory
chmod 700 "${STATE_DIR}"
chmod 600 "${STATE_DIR}/audit.log"
chmod 600 "${STATE_DIR}/pending-cleanup.json"
```

### 6.3 Audit Trail

**Requirement**: All bypass events must be logged

**Implementation**: See audit.log format in Section 2.2

---

## 7. Error Handling and Recovery

### 7.1 Graceful Degradation

**Principle**: Hooks should fail-open on unexpected errors

```bash
# Wrap gate execution in error handler
execute_gate() {
    local gate_name="$1"
    local gate_function="$2"

    if ! "$gate_function" 2>&1; then
        echo -e "${YELLOW}⚠ Warning: $gate_name failed unexpectedly${NC}" >&2
        echo -e "${YELLOW}  Proceeding with caution...${NC}" >&2
        return 0  # Don't block on unexpected errors
    fi
}
```

### 7.2 Recovery Procedures

**Scenario**: State files corrupted

**Recovery**:
```bash
# Reinitialize state directory
rm -rf .specify/state/
specify init --here --force
```

**Scenario**: Hook causing false positives

**Recovery**:
```bash
# Temporarily disable push-rules.md
sed -i 's/enabled: true/enabled: false/' push-rules.md
```

---

## 8. Documentation Requirements

### 8.1 User-Facing Documentation

**Location**: `docs/guides/push-rules-guide.md`

**Sections**:
1. Quick Start
2. Configuration Reference
3. Troubleshooting
4. FAQ

### 8.2 Developer Documentation

**Location**: `docs/platform/push-rules-platform-design.md` (this document)

**Sections**: (current structure)

### 8.3 Runbook

**Location**: `docs/runbooks/push-rules-troubleshooting.md`

**Scenarios**:
- Hook blocking valid pushes
- Performance issues
- State corruption
- Bypass flag misuse

---

## 9. Rollout Plan

### Phase 1: Foundation (task-301, task-302)
- Create push-rules.md template
- Implement pre-push hook
- Unit tests for parsing and validation

### Phase 2: Integration (task-303, task-304)
- Define github-janitor agent
- Integrate with /jpspec:validate
- Integration tests

### Phase 3: Monitoring (task-305)
- Implement warning system in session-start.sh
- State management
- E2E tests

### Phase 4: Polish (task-306, task-307)
- Rebase enforcement refinement
- CLI integration
- Documentation

---

## 10. Success Criteria

### Implementation Quality
- [ ] All unit tests passing (>80% coverage)
- [ ] All integration tests passing
- [ ] Hook execution time <5 seconds
- [ ] No regressions in existing hooks

### User Experience
- [ ] Clear, actionable error messages
- [ ] One-command setup (`specify init`)
- [ ] Non-intrusive warnings
- [ ] Emergency bypass available

### Documentation
- [ ] User guide published
- [ ] Platform design documented
- [ ] Runbook created
- [ ] ADR written for major decisions

---

## Appendix A: File Paths Reference

| Component | Path |
|-----------|------|
| Pre-push hook | `.claude/hooks/pre-push-validate.sh` |
| Hook tests | `.claude/hooks/test-pre-push-validate.sh` |
| Session-start hook | `.claude/hooks/session-start.sh` |
| push-rules.md template | `templates/push-rules-template.md` |
| State directory | `.specify/state/` |
| Janitor state | `.specify/state/pending-cleanup.json` |
| Audit log | `.specify/state/audit.log` |
| Python unit tests | `tests/platform/` |
| CLI init function | `src/specify_cli/__init__.py` |

---

## Appendix B: Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| bash | 4.0+ | Hook execution |
| git | 2.20+ | Repository operations |
| Python | 3.11+ | State management, JSON parsing |
| jq | 1.6+ | JSON parsing (optional, fallback to Python) |
| ruff | Latest | Default lint command |
| pytest | Latest | Default test runner |

---

## Appendix C: Related Documentation

- **PRD**: `docs/prd/git-push-rules-enforcement-prd.md`
- **Existing Hooks**: `.claude/hooks/`
- **Test Patterns**: `.claude/hooks/test-hooks.sh`
- **CLI Reference**: `src/specify_cli/__init__.py`

---

**End of Platform Design Document**
