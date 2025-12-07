# ADR-012: Push Rules Enforcement Architecture

**Status**: Proposed
**Date**: 2025-12-07
**Author**: @software-architect
**Context**: Git Push Rules Enforcement System (task-300)
**Parent PRD**: `docs/prd/git-push-rules-enforcement-prd.md`

---

## Context and Problem Statement

Development teams using JP Spec Kit need enforceable git workflow quality gates to prevent common issues before code reaches remote repositories:

**Current Pain Points**:
- Inconsistent rebasing creates merge commits that pollute history
- Skipped validations (lint/tests) waste CI/CD resources
- Stale branches and worktrees accumulate without cleanup
- No enforcement mechanism for documented git workflow rules

**Goal**: Design a lightweight, local-first enforcement system that validates git operations before push/PR creation without requiring infrastructure or network dependencies.

---

## Decision Drivers

1. **Simplicity**: Local CLI tool enhancement, not a distributed system
2. **Fail-Safe**: Validation failures should block destructive operations
3. **Developer Experience**: Clear error messages with actionable remediation
4. **Leverage Existing Patterns**: Reuse `.claude/hooks/` infrastructure
5. **Offline-First**: Must work without network connectivity
6. **Performance**: Hook execution <5 seconds for pre-push validation
7. **Auditability**: Track bypass usage and cleanup actions

---

## Decision

Implement a **file-based push rules enforcement system** using Claude Code hooks with the following architecture:

### 1. Configuration Layer

**Format**: Structured Markdown with YAML Frontmatter

**Location**: `./push-rules.md` (project root)

**Rationale for Structured Markdown**:
- Human-readable documentation + machine-parseable configuration
- Consistent with existing JP Spec Kit patterns (backlog.md, spec.md)
- Self-documenting (rules explanation embedded with configuration)
- Version-controllable and diff-friendly

**Schema Validation**: Pydantic model validates YAML frontmatter on load

```python
# src/specify_cli/models/push_rules.py
class RebasePolicy(BaseModel):
    enforcement: Literal["strict", "warn", "disabled"]
    base_branch: str = "main"
    allow_merge_commits: bool = False

class ValidationCommand(BaseModel):
    required: bool
    command: str
    allow_warnings: bool = False
    timeout: int = 300  # 5 minutes max

class PushRulesConfig(BaseModel):
    version: str
    enabled: bool
    bypass_flag: str = "--skip-push-rules"
    rebase_policy: RebasePolicy
    lint: ValidationCommand
    test: ValidationCommand
    branch_naming_pattern: Optional[str]
    enforce_branch_naming: bool = True
    janitor_settings: JanitorSettings
```

**Alternative Considered**: Pure YAML configuration
- **Rejected**: Less discoverable, no inline documentation, harder for humans to edit

---

### 2. Enforcement Layer

**Architecture Pattern**: Synchronous validation pipeline with fail-fast error handling

```
Pre-Push Hook Trigger
    ↓
Load push-rules.md (with caching)
    ↓
Validation Pipeline (sequential gates)
    ├─ [Gate 1] Configuration Validation
    ├─ [Gate 2] Rebase Status Check
    ├─ [Gate 3] Branch Naming Validation
    ├─ [Gate 4] Lint Execution
    └─ [Gate 5] Test Execution
    ↓
All Gates Pass? → Allow Push
Any Gate Fails? → Block Push + Show Remediation
Bypass Flag? → Log + Allow Push
```

**Implementation**: Bash script with Python helper for complex logic

**Location**: `.claude/hooks/pre-push.sh`

**Execution Model**:
- **Sequential gates**: Fail-fast on first violation (don't run tests if lint fails)
- **Subprocess isolation**: Each validation command runs in subprocess with timeout
- **Working directory**: Always project root
- **Environment**: Inherit user environment (no sanitization needed for local dev)

**Example Hook Structure**:
```bash
#!/bin/bash
# .claude/hooks/pre-push.sh

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PUSH_RULES_FILE="$PROJECT_ROOT/push-rules.md"

# Check for bypass flag
if [[ " $* " =~ " --skip-push-rules " ]]; then
    echo "⚠ WARNING: Push rules bypassed (logged to audit.log)"
    echo "$(date -Iseconds),bypass,$(git rev-parse --abbrev-ref HEAD),$(whoami)" >> .specify/audit.log
    exit 0
fi

# Load and validate configuration
if ! python3 -c "from specify_cli.hooks import validate_push_rules; validate_push_rules('$PUSH_RULES_FILE')"; then
    echo "✗ Invalid push-rules.md configuration"
    exit 1
fi

# Execute validation pipeline
python3 -m specify_cli.hooks.pre_push \
    --rules-file "$PUSH_RULES_FILE" \
    --current-branch "$(git rev-parse --abbrev-ref HEAD)"
```

**Python Validation Module** (`src/specify_cli/hooks/pre_push.py`):
```python
def run_validation_pipeline(rules: PushRulesConfig, current_branch: str) -> ValidationResult:
    """Execute all validation gates in sequence."""

    gates = [
        ("Configuration", validate_configuration),
        ("Rebase Status", validate_rebase_status),
        ("Branch Naming", validate_branch_naming),
        ("Lint", run_lint_validation),
        ("Tests", run_test_validation),
    ]

    for gate_name, gate_func in gates:
        console.print(f"[{gate_num}/{total}] Checking {gate_name}...")

        try:
            result = gate_func(rules, current_branch)
            if not result.passed:
                print_failure(gate_name, result.error, result.remediation)
                return ValidationResult(passed=False, failed_gate=gate_name)

            print_success(gate_name, result.message)
        except ValidationError as e:
            print_failure(gate_name, str(e), e.remediation)
            return ValidationResult(passed=False, failed_gate=gate_name)

    return ValidationResult(passed=True)
```

**Rebase Detection Algorithm**:
```python
def validate_rebase_status(rules: PushRulesConfig, current_branch: str) -> GateResult:
    """Detect merge commits in branch since diverging from base."""
    base_branch = rules.rebase_policy.base_branch

    # Find merge base
    merge_base = subprocess.check_output(
        ["git", "merge-base", base_branch, current_branch],
        text=True
    ).strip()

    # List commits in branch since divergence
    commits = subprocess.check_output(
        ["git", "log", f"{merge_base}..{current_branch}", "--oneline", "--merges"],
        text=True
    ).strip()

    if commits and not rules.rebase_policy.allow_merge_commits:
        merge_commit_count = len(commits.split('\n'))
        return GateResult(
            passed=False,
            error=f"Found {merge_commit_count} merge commit(s) in branch",
            remediation=f"Run: git rebase -i {base_branch}"
        )

    return GateResult(passed=True, message="No merge commits detected")
```

**Alternative Considered**: Async validation with parallel gate execution
- **Rejected**: Added complexity, minimal performance gain (most gates are fast), harder debugging

---

### 3. Cleanup Layer (Janitor)

**Architecture**: Agent-based automation triggered by workflow completion

**Implementation**: Claude Code agent definition (not a daemon/service)

**Location**: `.claude/agents/github-janitor.md`

**Invocation Methods**:
1. **Automatic**: Triggered by `/jpspec:validate` Phase 7
2. **Manual**: Via Task tool or direct agent execution
3. **Scheduled**: (Future) Session-start check for pending cleanup

**Capabilities**:
```markdown
# AGENT CONTEXT: GitHub Janitor

## Expertise
You are an automation agent for git repository cleanup and hygiene.

## Responsibilities
1. **Branch Pruning**: Delete merged branches (check remote and local)
2. **Worktree Cleanup**: Remove orphaned git worktrees
3. **PR Status Sync**: Update backlog.md tasks based on PR state
4. **Naming Compliance**: Report branches violating naming conventions
5. **Cleanup Reporting**: Generate summary of actions taken

## Decision Logic
- Protected branches (from push-rules.md): NEVER delete
- Merged branches (confirmed via git log): SAFE to delete
- Worktrees with deleted branches: SAFE to remove
- Current worktree: NEVER delete

## Output
- List of deleted branches
- List of removed worktrees
- Warning for non-compliant branch names
- State file update (.specify/state/janitor-last-run)
```

**State Management**:
```
.specify/state/
├── janitor-last-run          # ISO 8601 timestamp
└── pending-cleanup.json      # List of items awaiting cleanup
```

**State File Format** (`pending-cleanup.json`):
```json
{
  "last_updated": "2025-12-07T10:30:00Z",
  "merged_branches": ["feature/auth-123", "fix/login-bug"],
  "orphaned_worktrees": ["/tmp/worktree-old-feature"],
  "non_compliant_branches": {
    "my-branch": "does not match pattern ^(feature|fix)/.*"
  }
}
```

**Alternative Considered**: Background daemon process
- **Rejected**: Overkill for local dev, requires process management, adds complexity

---

### 4. Warning System

**Integration Point**: `.claude/hooks/session-start.sh`

**Implementation**: State file check + console warning

**Warning Trigger Logic**:
```bash
# In session-start.sh
PENDING_CLEANUP_FILE=".specify/state/pending-cleanup.json"

if [[ -f "$PENDING_CLEANUP_FILE" ]]; then
    # Parse pending items count
    merged_count=$(jq '.merged_branches | length' "$PENDING_CLEANUP_FILE")
    worktree_count=$(jq '.orphaned_worktrees | length' "$PENDING_CLEANUP_FILE")

    if [[ $merged_count -gt 0 || $worktree_count -gt 0 ]]; then
        warnings+=("Janitor cleanup pending: $merged_count branches, $worktree_count worktrees")
    fi
fi
```

**Warning Format** (added to session-start output):
```
Environment Warnings:
  ⚠ Janitor cleanup pending: 3 merged branches, 1 worktree
    Run 'backlog task create' or /jpspec:validate to trigger cleanup
```

**Warning Clear Logic**: Delete/empty `pending-cleanup.json` after successful janitor run

**Non-Blocking**: Warnings never prevent session start (fail-open principle from ADR-006)

---

### 5. Data Flow Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Workflow                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  git push       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Pre-Push Hook   │
                    │ (.claude/hooks) │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Load     │      │ Validate │      │ Execute  │
    │ Config   │─────▶│ Pipeline │─────▶│ Checks   │
    └──────────┘      └──────────┘      └─────┬────┘
                                               │
                                   ┌───────────┴───────────┐
                                   │                       │
                                   ▼                       ▼
                            ┌──────────┐           ┌──────────┐
                            │  PASS    │           │  FAIL    │
                            │ Allow    │           │  Block   │
                            │ Push     │           │  + Error │
                            └────┬─────┘           └──────────┘
                                 │
                                 ▼
                      ┌──────────────────┐
                      │ /jpspec:validate │
                      │  (after PR)      │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │ Phase 7:         │
                      │ github-janitor   │
                      └────────┬─────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐         ┌──────────┐        ┌──────────┐
    │ Prune    │         │ Clean    │        │ Update   │
    │ Branches │         │ Worktrees│        │ State    │
    └────┬─────┘         └────┬─────┘        └────┬─────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Update State    │
                    │ Files           │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Session Start   │
                    │ (next session)  │
                    │ Check State     │
                    └─────────────────┘
```

**Data Flow Steps**:

1. **Pre-Push Validation**:
   - Input: Current branch, remote ref, commit range
   - Process: Load config → Run validation gates
   - Output: Pass/fail decision + error details

2. **Janitor Cleanup** (triggered by `/jpspec:validate`):
   - Input: Push-rules.md (protected branches list)
   - Process: Query git for merged branches and worktrees
   - Output: Cleanup actions + state file update

3. **Session Warning**:
   - Input: `.specify/state/pending-cleanup.json`
   - Process: Parse state file, count pending items
   - Output: Warning message (if items pending)

**State Persistence**: File-based (no database)
- Configuration: `push-rules.md` (user-editable)
- Runtime state: `.specify/state/*.json` (gitignored)
- Audit trail: `.specify/audit.log` (gitignored)

---

### 6. Integration Patterns

#### Hook → Git Integration
```bash
# Subprocess calls to git commands
git rev-parse --abbrev-ref HEAD           # Get current branch
git merge-base main feature/branch        # Find divergence point
git log --oneline --merges                # Detect merge commits
git remote prune origin                   # Prune remote-tracking branches
git worktree list                         # List worktrees
```

**Error Handling**: Wrap all git commands in try/except, provide helpful errors

#### Hook → Test Framework Integration
```python
def run_test_validation(rules: PushRulesConfig) -> GateResult:
    """Execute test command with timeout."""
    if not rules.test.required:
        return GateResult(passed=True, message="Tests not required")

    try:
        result = subprocess.run(
            rules.test.command,
            shell=True,  # Allow complex commands like "pytest tests/ -x -q"
            capture_output=True,
            timeout=rules.test.timeout,
            cwd=project_root,
        )

        if result.returncode != 0:
            return GateResult(
                passed=False,
                error=f"Tests failed with exit code {result.returncode}",
                remediation="Fix failing tests before pushing",
                details=result.stdout.decode()[-500:],  # Last 500 chars
            )

        return GateResult(passed=True, message="All tests passed")

    except subprocess.TimeoutExpired:
        return GateResult(
            passed=False,
            error=f"Tests timed out after {rules.test.timeout}s",
            remediation="Optimize slow tests or increase timeout in push-rules.md"
        )
```

#### Janitor → Backlog.md Integration
```python
# Via backlog CLI (subprocess calls)
def sync_pr_status_to_backlog(pr_url: str, pr_state: str):
    """Update task status based on PR state."""
    # Find task by PR URL
    result = subprocess.run(
        ["backlog", "task", "search", pr_url, "--plain"],
        capture_output=True
    )

    task_id = parse_task_id(result.stdout)

    if pr_state == "merged":
        # Mark task done
        subprocess.run(["backlog", "task", "edit", task_id, "-s", "Done"])
    elif pr_state == "closed":
        # Add note about closure
        subprocess.run([
            "backlog", "task", "edit", task_id,
            "--append-notes", f"PR closed without merge: {pr_url}"
        ])
```

#### Session-Start → State File Integration
```bash
# In .claude/hooks/session-start.sh
JANITOR_STATE=".specify/state/janitor-last-run"

if [[ -f "$JANITOR_STATE" ]]; then
    LAST_RUN=$(cat "$JANITOR_STATE")
    DAYS_AGO=$(( ($(date +%s) - $(date -d "$LAST_RUN" +%s)) / 86400 ))

    if [[ $DAYS_AGO -gt 7 ]]; then
        warnings+=("Janitor hasn't run in $DAYS_AGO days - consider cleanup")
    fi
fi
```

---

## Component Boundaries and Responsibilities

### Component 1: Configuration Loader
**Responsibility**: Parse and validate push-rules.md
**Location**: `src/specify_cli/models/push_rules.py`
**Interface**:
```python
def load_push_rules(file_path: Path) -> PushRulesConfig:
    """Load and validate push rules configuration."""

def validate_push_rules_schema(config: dict) -> bool:
    """Validate YAML frontmatter against Pydantic schema."""
```

### Component 2: Validation Pipeline
**Responsibility**: Execute validation gates in sequence
**Location**: `src/specify_cli/hooks/pre_push.py`
**Interface**:
```python
def run_validation_pipeline(
    rules: PushRulesConfig,
    current_branch: str
) -> ValidationResult:
    """Run all validation gates, return overall result."""

def validate_rebase_status(rules, branch) -> GateResult:
def validate_branch_naming(rules, branch) -> GateResult:
def run_lint_validation(rules) -> GateResult:
def run_test_validation(rules) -> GateResult:
```

### Component 3: Rebase Checker
**Responsibility**: Detect merge commits in branch history
**Location**: `src/specify_cli/hooks/rebase_checker.py`
**Interface**:
```python
def find_merge_commits(
    base_branch: str,
    current_branch: str
) -> List[MergeCommit]:
    """Return list of merge commits since divergence."""

def is_branch_rebased(base_branch: str, current_branch: str) -> bool:
    """True if branch has no merge commits."""
```

### Component 4: GitHub Janitor Agent
**Responsibility**: Repository cleanup automation
**Location**: `.claude/agents/github-janitor.md`
**Interface**: Natural language agent (no programmatic API)
**Invocation**: Via Task tool or /jpspec:validate

### Component 5: State Manager
**Responsibility**: Read/write janitor state files
**Location**: `src/specify_cli/utils/state.py`
**Interface**:
```python
def update_janitor_state(
    merged_branches: List[str],
    orphaned_worktrees: List[Path]
) -> None:
    """Update pending-cleanup.json and janitor-last-run."""

def get_pending_cleanup() -> PendingCleanup:
    """Load pending cleanup items from state file."""

def clear_pending_cleanup() -> None:
    """Clear state file after successful cleanup."""
```

### Component 6: Warning Checker
**Responsibility**: Check state and emit warnings
**Location**: `.claude/hooks/session-start.sh`
**Interface**: Bash script (integrates with existing hook)

---

## Consequences

### Positive

1. **Simple Architecture**: File-based, no services/databases/network required
2. **Reuses Existing Patterns**: Leverages `.claude/hooks/` infrastructure (ADR-006)
3. **Developer-Friendly**: Clear error messages, actionable remediation steps
4. **Auditable**: All bypasses and cleanup actions logged
5. **Fail-Safe**: Blocks pushes on validation failures (prevents CI waste)
6. **Extensible**: Easy to add new validation gates or janitor capabilities
7. **Offline-First**: Works without network connectivity

### Negative

1. **Local Enforcement Only**: Developers can bypass hooks by disabling them
   - **Mitigation**: Audit logging + CI verification as backstop
2. **Sequential Validation**: Total time = sum of gate times
   - **Mitigation**: Fail-fast (don't run slow tests if lint fails), 5s budget enforced
3. **No Network Controls**: Can't prevent janitor from making API calls
   - **Mitigation**: Document in agent context, rely on code review
4. **State File Conflicts**: Possible if multiple sessions modify state
   - **Mitigation**: Last-write-wins, state files are advisory not critical

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Developers overuse bypass flag | Medium | Medium | Audit logging, team norms, periodic review |
| Validation timeout on slow CI | Low | Medium | Configurable timeouts, optimization guidance |
| Janitor deletes wrong branch | Low | High | Protected branches list, confirmation prompts |
| State file corruption | Low | Low | JSON validation on load, graceful fallback |

---

## Alternatives Considered

### Alternative 1: Server-Side Enforcement (GitHub Branch Protection)

**Approach**: Use GitHub branch protection rules to enforce validation

**Pros**:
- Cannot be bypassed by developers
- Centralized configuration
- Works across all git clients

**Cons**:
- Requires network connectivity
- Wastes CI resources (validation happens after push)
- Slower feedback loop (remote execution)
- Not applicable to non-GitHub repositories

**Decision**: Use client-side hooks as primary enforcement, GitHub protection as backstop

### Alternative 2: Git Hooks via Husky/pre-commit

**Approach**: Use existing git hook frameworks

**Pros**:
- Mature tooling
- Large ecosystem
- Well-documented

**Cons**:
- JavaScript dependency (Husky) not relevant for Python project
- pre-commit framework uses YAML config (not markdown)
- Doesn't integrate with Claude Code agent system
- Adds external dependency

**Decision**: Implement custom hooks leveraging Claude Code infrastructure

### Alternative 3: Database-Backed State Management

**Approach**: Store janitor state in SQLite database

**Pros**:
- ACID transactions prevent corruption
- Query capabilities
- Better for complex state

**Cons**:
- Overkill for simple state (timestamps, lists)
- Adds dependency (sqlalchemy)
- Harder to inspect/debug
- JSON files are "good enough" and simpler

**Decision**: Use JSON files for v1, can migrate to DB if needed

### Alternative 4: Continuous Background Janitor

**Approach**: Run janitor as cron job or systemd timer

**Pros**:
- Automatic cleanup without manual trigger
- Regular schedule (e.g., nightly)

**Cons**:
- Requires system-level setup (cron/systemd)
- Not portable across platforms
- Overkill for local dev tool
- Cleanup on-demand is sufficient

**Decision**: On-demand janitor via /jpspec:validate, session warnings for reminders

---

## Implementation Guidance

### Phase 1: Core Validation (task-301, task-302)
1. Implement `PushRulesConfig` Pydantic model
2. Create `push-rules.md` template with schema
3. Implement pre-push hook with validation pipeline
4. Add configuration validation gate

**Deliverables**:
- `src/specify_cli/models/push_rules.py`
- `templates/push-rules-template.md`
- `.claude/hooks/pre-push.sh`
- `src/specify_cli/hooks/pre_push.py`

### Phase 2: Rebase Enforcement (task-306)
1. Implement merge commit detection algorithm
2. Add rebase validation gate to pipeline
3. Create helpful error messages with git commands
4. Test with worktree scenarios

**Deliverables**:
- `src/specify_cli/hooks/rebase_checker.py`
- Integration tests for merge detection
- Documentation for rebase workflow

### Phase 3: Janitor Agent (task-303, task-304)
1. Define github-janitor agent context
2. Integrate janitor into /jpspec:validate workflow
3. Implement state file management
4. Create cleanup report format

**Deliverables**:
- `.claude/agents/github-janitor.md`
- Updated `/jpspec:validate` command
- `src/specify_cli/utils/state.py`

### Phase 4: Warning System (task-305)
1. Add state file check to session-start.sh
2. Format warning messages
3. Add "clear warning" logic after janitor runs
4. Test warning display

**Deliverables**:
- Updated `.claude/hooks/session-start.sh`
- Warning format documentation

### Phase 5: CLI Integration (task-307)
1. Update `specify init` to generate push-rules.md
2. Add `specify validate-push-rules` command
3. Create migration guide for existing projects

**Deliverables**:
- Updated `src/specify_cli/commands/init.py`
- New validation command
- Documentation updates

---

## Testing Strategy

### Unit Tests
```python
# Test configuration loading
def test_load_push_rules_valid_config():
    config = load_push_rules("fixtures/valid-push-rules.md")
    assert config.version == "1.0"
    assert config.enabled is True

# Test rebase detection
def test_detect_merge_commits(git_repo):
    # Setup: Create branch with merge commit
    merge_commits = find_merge_commits("main", "feature-branch")
    assert len(merge_commits) == 1

# Test validation gates
def test_lint_gate_fails_on_errors():
    rules = PushRulesConfig(lint=ValidationCommand(
        required=True, command="exit 1"
    ))
    result = run_lint_validation(rules)
    assert not result.passed
```

### Integration Tests
```python
# Test full pre-push hook execution
def test_pre_push_hook_blocks_invalid_push(git_repo):
    # Setup: Branch with merge commits
    result = subprocess.run([".claude/hooks/pre-push.sh"], capture_output=True)
    assert result.returncode != 0
    assert "merge commits detected" in result.stderr.decode()

# Test janitor cleanup
def test_janitor_prunes_merged_branches():
    # Setup: Merged branch
    run_janitor_agent()
    branches = list_local_branches()
    assert "merged-feature" not in branches
```

### Manual Test Scenarios
- [ ] Push with merge commits → blocked
- [ ] Push with lint errors → blocked
- [ ] Push with failing tests → blocked
- [ ] Bypass with flag → allowed + logged
- [ ] Janitor cleanup → branches pruned
- [ ] Session start → warning displayed
- [ ] Invalid push-rules.md → clear error

---

## References

- **PRD**: `docs/prd/git-push-rules-enforcement-prd.md`
- **ADR-001**: Backlog.md CLI Integration (task lifecycle patterns)
- **ADR-006**: Hook Execution Model (security sandbox, fail-safe)
- **Related Tasks**: task-300 (parent), task-301-307 (implementation tasks)
- **Existing Hooks**: `.claude/hooks/session-start.sh`, `.claude/hooks/pre-implement.sh`

---

## Appendix: Configuration File Example

```markdown
---
version: "1.0"
enabled: true
bypass_flag: "--skip-push-rules"
---

# Git Push Rules

Enforced by Claude Code hooks before push operations.

## Rebase Policy

**Enforcement**: strict
**Base Branch**: main
**Allow Merge Commits**: false

All branches MUST be rebased on main before pushing.

## Validation Requirements

### Linting
- **Required**: true
- **Command**: `uv run ruff check .`
- **Allow Warnings**: false
- **Timeout**: 60

### Testing
- **Required**: true
- **Command**: `uv run pytest tests/ -x -q`
- **Timeout**: 300
- **Minimum Coverage**: 0

## Branch Naming

**Pattern**: `^(feature|fix|docs|refactor|test)/[a-z0-9-]+$`
**Enforce**: true

Examples: `feature/add-push-rules`, `fix/hook-timeout`

## Janitor Settings

**Run After Validation**: true
**Prune Merged Branches**: true
**Clean Stale Worktrees**: true
**Protected Branches**: [main, master, develop]

## Emergency Bypass

To bypass validation (emergency only):
```bash
git push --skip-push-rules
```

**Note**: All bypasses are logged to `.specify/audit.log`
```

---

## Revision History

- **2025-12-07**: Initial decision (v1.0) - @software-architect
