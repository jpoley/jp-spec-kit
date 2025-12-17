---
name: "flow-validate"
description: "Execute validation and quality assurance using QA, security, documentation, and release management agents."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Deploy to Production"
    agent: "flow-operate"
    prompt: "Validation is complete. Deploy the feature to production and configure operations."
    send: false
---
# /flow:validate - Enhanced Phased Validation Workflow

Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

## User Input

```text
$ARGUMENTS
```

**Expected Input**: Optional task ID (e.g., `task-094`). If not provided, command discovers the current in-progress task automatically.

# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "[Y] Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: flowspec init --here"
  echo "  2. Then: Run /spec:constitution to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `flowspec init --here`
- Continue with command (constitution is recommended but not required)

### 2. If Constitution Exists, Check Validation Status

```bash
# Detect tier from TIER comment (default: Medium if not found)
TIER=$(grep -o "TIER: \(Light\|Medium\|Heavy\)" memory/constitution.md | cut -d' ' -f2)
TIER=${TIER:-Medium}  # Default to Medium if not found

# Count NEEDS_VALIDATION markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md || echo 0)

# Extract section names from NEEDS_VALIDATION markers
SECTIONS=$(grep "NEEDS_VALIDATION" memory/constitution.md | sed 's/.*NEEDS_VALIDATION: /  - /')

echo "Constitution tier: $TIER"
echo "Unvalidated sections: $MARKER_COUNT"
```

### 3. Apply Tier-Based Enforcement

#### Light Tier - Warn Only

If `TIER = Light` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution has N unvalidated sections:
$SECTIONS

Consider running /spec:constitution to customize your constitution.

Proceeding with command...
```

Then continue with the command.

#### Medium Tier - Warn and Confirm

If `TIER = Medium` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
$SECTIONS

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Run /spec:constitution to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` -> Continue with command
- If user responds `n`, `no`, or empty/Enter -> Stop and show:
  ```text
  Command cancelled. Run /spec:constitution to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
[X] Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Run /spec:constitution to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**DO NOT PROCEED** with the command. Exit and wait for user to resolve.

### 4. Skip Validation Flag

If the command was invoked with `--skip-validation`:

```bash
# Check for skip flag in arguments
if [[ "$ARGUMENTS" == *"--skip-validation"* ]]; then
  echo "⚠️ Skipping constitution validation (--skip-validation)"
  # Remove the flag from arguments and continue
  ARGUMENTS="${ARGUMENTS/--skip-validation/}"
fi
```

When skip flag is present:
- Log warning
- Skip all validation checks
- Continue with command
- Note: For emergency use only

### 5. Fully Validated Constitution

If `MARKER_COUNT = 0`:

```text
[Y] Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | [Y] Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | [Y] Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | [Y] Continue |
| Heavy | >0 | [X] Block, require validation |
| Any | >0 + `--skip-validation` | ⚠️ Warn, continue |

## Integration Example

```markdown
---
description: Your command description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/commands/flow/_constitution-check.md}}

{{INCLUDE:.claude/commands/flow/_workflow-state.md}}

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| `/spec:constitution` | Interactive constitution customization |
| `flowspec constitution validate` | Check validation status and show report |
| `flowspec constitution show` | Display current constitution |


# Rigor Rules Reference

<!--
METADATA
========
Version: 1.0
Created: 2025-12-17
Last Updated: 2025-12-17

This file is the single source of truth for all rigor rules.
Include it in /flow:* commands via:
  \{\{INCLUDE:.claude/commands/flow/_rigor-rules.md\}\}

See ADR-001 for design rationale.
-->

---

## Enforcement Configuration

### Enforcement Modes

Rules can be enforced in three modes:

- **strict**: Block workflow if rule violated (default for BLOCKING rules)
- **warn**: Warn but allow continuation (use sparingly)
- **off**: Disable rule (emergency use only)

### Per-Phase Configuration

Configure enforcement in `.flowspec/rigor-config.yml`:

```yaml
enforcement:
  global: strict          # Default for all rules
  phases:
    setup: strict
    execution: strict
    freeze: warn          # Less strict for emergency freezes
    validation: strict
    pr: strict
  rules:
    EXEC-005: warn        # Advisory rules can be set to warn
    SETUP-004: warn       # Parallelization is advisory
```

If no config file exists, all BLOCKING rules default to `strict` and ADVISORY rules to `warn`.

---

## Phase: SETUP (Task Creation & Specification)

**Applies to**: `/flow:assess`, `/flow:specify`

These rules ensure tasks are well-defined before implementation begins.

---

### Rule: SETUP-001 - Clear Plan Required
**Severity**: BLOCKING
**Enforcement**: strict

Every task MUST have a documented plan of action before work begins.

**Validation**:
```bash
# Check if task has an implementation plan
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo '')}"
if [ -n "$TASK_ID" ]; then
  backlog task "$TASK_ID" --plain 2>/dev/null | grep -q "Implementation Plan:"
  if [ $? -ne 0 ]; then
    echo "[X] SETUP-001 VIOLATION: No implementation plan for $TASK_ID"
    echo "Remediation: backlog task edit $TASK_ID --plan \$'1. Step 1\n2. Step 2'"
  fi
fi
```

**Remediation**:
```bash
backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2\n3. Step 3'
```

**Rationale**: Clear plans prevent scope creep, enable accurate time estimates, and provide onboarding context for new engineers joining mid-task.

---

### Rule: SETUP-002 - Dependencies Mapped
**Severity**: BLOCKING
**Enforcement**: strict

Inter-task dependencies MUST be documented before implementation begins. Tasks cannot be worked in isolation when they have upstream or downstream dependencies.

**Validation**:
```bash
# Check for dependency documentation in task
# Note: Not all tasks have dependencies - this validates documentation exists IF dependencies exist
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo '')}"
if [ -n "$TASK_ID" ]; then
  # Check for depends-on labels or dependency notes
  HAS_DEP_LABELS=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -qE "(depends-on|blocked-by|Dependencies:)" && echo "yes" || echo "no")
  if [ "$HAS_DEP_LABELS" = "no" ]; then
    echo "INFO: SETUP-002: No dependencies documented (OK if task is independent)"
  fi
fi
```

**Remediation**:
```bash
# Add dependency label
backlog task edit <task-id> -l "depends-on:task-123"

# Or document in description/notes
backlog task edit <task-id> --append-notes "Dependencies: task-123 (API contract must be defined first)"
```

**Rationale**: Prevents parallel work on dependent tasks, reduces integration conflicts, and ensures proper task ordering.

---

### Rule: SETUP-003 - Testable Acceptance Criteria
**Severity**: BLOCKING
**Enforcement**: strict

Every task MUST have at least one acceptance criterion that is:
1. **Measurable** (not "improve performance" but "reduce latency to <100ms")
2. **Testable** (can be verified by code or manual test)
3. **Specific** (avoids vague terms like "better" or "good")

**Validation**:
```bash
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo '')}"
if [ -n "$TASK_ID" ]; then
  AC_COUNT=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -cE "^\[[ x]\]" || echo 0)
  if [ "$AC_COUNT" -eq 0 ]; then
    echo "[X] SETUP-003 VIOLATION: No acceptance criteria for $TASK_ID"
    echo "Remediation: backlog task edit $TASK_ID --ac 'Specific testable criterion'"
  fi

  # Warn about vague terms (heuristic check)
  backlog task "$TASK_ID" --plain 2>/dev/null | grep -iE "(improve|enhance|better|good|optimize|nice)" && \
    echo "WARNING: Potentially vague AC terms detected - ensure criteria are measurable"
fi
```

**Remediation**:
```bash
backlog task edit <task-id> --ac "API returns response in <200ms for 95th percentile"
backlog task edit <task-id> --ac "Unit test coverage exceeds 80%"
```

**Rationale**: Vague ACs lead to scope disputes, incomplete implementations, and "it works on my machine" situations.

---

### Rule: SETUP-004 - Sub-Agent Parallelization
**Severity**: ADVISORY
**Enforcement**: warn

Tasks SHOULD identify opportunities for parallel sub-agent work when applicable. Large tasks benefit from frontend/backend parallelization.

**Validation**:
```bash
# Check if task has parallel-work or multi-agent labels
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo '')}"
if [ -n "$TASK_ID" ]; then
  HAS_PARALLEL=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -qE "(parallel-work|frontend|backend)" && echo "yes" || echo "no")
  if [ "$HAS_PARALLEL" = "no" ]; then
    echo "INFO: SETUP-004: Consider if task can be parallelized (frontend/backend split)"
  fi
fi
```

**Remediation**:
```bash
backlog task edit <task-id> -l "parallel-work:frontend,backend"
```

**Rationale**: Parallel execution reduces critical path duration and improves throughput.

---

## Phase: EXECUTION (Implementation)

**Applies to**: `/flow:implement`

These rules ensure implementation work is traceable, organized, and follows team conventions.

---

### Rule: EXEC-001 - Git Worktree Required
**Severity**: BLOCKING
**Enforcement**: strict

All implementation work MUST be done in a git worktree with matching branch name. This prevents branch-switching overhead and enables parallel feature development.

**Validation**:
```bash
# Check if current directory is a worktree
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
IS_WORKTREE=$(git worktree list 2>/dev/null | grep -q "$WORKTREE_DIR" && echo "yes" || echo "no")

if [ "$IS_WORKTREE" = "no" ]; then
  echo "[X] EXEC-001 VIOLATION: Not in a git worktree"
  echo "Remediation: Create worktree with: git worktree add ../<worktree-name> <branch-name>"
fi

# Check worktree directory name matches branch (best practice)
WORKTREE_NAME=$(basename "$WORKTREE_DIR")
BRANCH_NAME=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH_NAME" ] && [ "$WORKTREE_NAME" != "$BRANCH_NAME" ] && [ "$WORKTREE_NAME" != "${BRANCH_NAME##*/}" ]; then
  echo "WARNING: EXEC-001: Worktree name '$WORKTREE_NAME' does not match branch '$BRANCH_NAME'"
fi
```

**Remediation**:
```bash
# From main repository directory:
BRANCH="$(hostname -s | tr '[:upper:]' '[:lower:]')/task-123/feature-slug"
git worktree add "../$(basename $BRANCH)" "$BRANCH"
cd "../$(basename $BRANCH)"
```

**Rationale**: Worktrees enable parallel feature development without branch switching overhead. Matching names prevent confusion.

---

### Rule: EXEC-002 - Branch Naming Convention
**Severity**: BLOCKING
**Enforcement**: strict

Branch names MUST follow the pattern: `{hostname}/task-{id}/{slug-description}`

**Examples**:
- `macbook-pro/task-541/rigor-rules-include`
- `desktop-alice/task-123/user-authentication`

**Validation**:
```bash
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -n "$BRANCH" ]; then
  if ! [[ "$BRANCH" =~ ^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$ ]]; then
    echo "[X] EXEC-002 VIOLATION: Invalid branch name: $BRANCH"
    echo "Expected format: hostname/task-NNN/slug-description"
    echo "Example: $(hostname -s | tr '[:upper:]' '[:lower:]')/task-123/add-feature"
  fi
fi
```

**Remediation**:
```bash
# Generate compliant branch name
HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
git checkout -b "${HOSTNAME}/task-123/add-user-authentication"
```

**Rationale**: Consistent naming enables automation, prevents conflicts in multi-developer teams, and provides instant task traceability. See ADR-003.

---

### Rule: EXEC-003 - Decision Logging Required
**Severity**: BLOCKING
**Enforcement**: strict

All significant decisions MUST be logged to the JSONL decision log. A "significant decision" includes:
- Technology choices (library, framework, pattern selection)
- Architecture changes
- Trade-off resolutions
- Deferred work decisions

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  DECISION_LOG="memory/decisions/${TASK_ID}.jsonl"

  if [ ! -f "$DECISION_LOG" ]; then
    echo "[X] EXEC-003 VIOLATION: No decision log found: $DECISION_LOG"
    echo "Remediation: Create the log with at least one decision entry"
  else
    ENTRY_COUNT=$(wc -l < "$DECISION_LOG" 2>/dev/null || echo 0)
    if [ "$ENTRY_COUNT" -eq 0 ]; then
      echo "[X] EXEC-003 VIOLATION: Decision log is empty"
    fi
  fi
fi
```

**Remediation**:
```bash
# Use the helper script (recommended)
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Selected JSONL format for decision logs" \
  --rationale "Append-only, git-friendly, streaming-compatible" \
  --actor "@backend-engineer" \
  --alternatives "SQLite,Plain text,YAML"

# With optional context
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Split validation into separate functions" \
  --rationale "Improves testability and single responsibility" \
  --actor "@backend-engineer" \
  --files "src/validator.py,tests/test_validator.py" \
  --tags "architecture,testing"

# Manual logging (if script not available)
TASK_ID="task-541"
mkdir -p memory/decisions
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","task_id":"'"$TASK_ID"'","phase":"execution","decision":"Using shared include pattern for rigor rules","rationale":"Single source of truth, consistent with existing patterns","alternatives":["Inline in each command","Python module"],"actor":"@backend-engineer"}' >> "memory/decisions/${TASK_ID}.jsonl"
```

**Utility Script**: `scripts/bash/rigor-decision-log.sh`

The helper script provides:
- Automatic JSONL formatting and validation
- Proper timestamp generation (ISO 8601 UTC)
- JSON escaping for special characters
- Structured optional fields (alternatives, files, tags)
- Entry count tracking

**Example Workflow**:
```bash
# 1. Make a technology choice
./scripts/bash/rigor-decision-log.sh \
  --task task-100 \
  --phase execution \
  --decision "Use FastAPI over Flask" \
  --rationale "Better async support, automatic OpenAPI docs, type hints" \
  --alternatives "Flask,Django,Starlette" \
  --actor "@backend-engineer" \
  --tags "architecture,framework"

# 2. View logged decisions
cat memory/decisions/task-100.jsonl | jq '.'

# 3. Validate during PR phase (VALID-001)
jq empty memory/decisions/task-100.jsonl
```

**Rationale**: Decision logs enable post-mortems, onboarding, and architectural reviews. See ADR-002 for JSONL schema and `memory/decisions/README.md` for query examples.

---

### Rule: EXEC-004 - Backlog Task Linkage
**Severity**: BLOCKING
**Enforcement**: strict

Implementation work MUST be linked to backlog tasks. No "rogue" coding without a task.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  backlog task "$TASK_ID" --plain > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "[X] EXEC-004 VIOLATION: No backlog task found: $TASK_ID"
    echo "Remediation: Create task first: backlog task create 'Task title' --ac 'Criterion'"
  fi
else
  echo "[X] EXEC-004 VIOLATION: Branch does not contain task ID"
  echo "Branch must follow pattern: hostname/task-NNN/slug"
fi
```

**Remediation**:
```bash
# Create task if missing
backlog task create "Feature description" \
  --ac "Criterion 1" \
  --ac "Criterion 2" \
  -l "backend" \
  --priority high
```

**Rationale**: Prevents "rogue" work that doesn't align with planned backlog, ensures all work is tracked and prioritized.

---

### Rule: EXEC-005 - Continuous Task Memory Updates
**Severity**: ADVISORY
**Enforcement**: warn

Task memory SHOULD be updated after every major decision or implementation milestone. Task memory survives context resets and enables seamless handoffs.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  MEMORY_FILE="backlog/memory/${TASK_ID}.md"
  if [ -f "$MEMORY_FILE" ]; then
    # Check last modified time
    LAST_MODIFIED=$(stat -c %Y "$MEMORY_FILE" 2>/dev/null || stat -f %m "$MEMORY_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    HOURS_AGO=$(( (NOW - LAST_MODIFIED) / 3600 ))
    if [ "$HOURS_AGO" -gt 24 ]; then
      echo "WARNING: EXEC-005: Task memory not updated in $HOURS_AGO hours"
    fi
  else
    echo "INFO: EXEC-005: No task memory file yet - consider creating one"
  fi
fi
```

**Remediation**:
```bash
# Update or create task memory
TASK_ID="task-541"
cat >> "backlog/memory/${TASK_ID}.md" << 'EOF'

## Current State (Updated: $(date +%Y-%m-%d))

### What's Complete
- Item 1
- Item 2

### What's In Progress
- Current work item

### What's Next
- Next steps

### Key Decisions
- Decision 1 and rationale

### Blockers
- None currently
EOF
```

**Rationale**: Fresh task memory enables seamless context resumption after interruptions, machine changes, or handoffs.

---

### Rule: EXEC-006 - Workflow State Tracking
**Severity**: BLOCKING
**Enforcement**: strict

Agent MUST always know and track what comes next in the workflow. The current workflow state must be reflected in task labels.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  HAS_WORKFLOW=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -q "workflow:" && echo "yes" || echo "no")
  if [ "$HAS_WORKFLOW" = "no" ]; then
    echo "[X] EXEC-006 VIOLATION: No workflow state label for $TASK_ID"
    echo "Remediation: backlog task edit $TASK_ID -l 'workflow:In Implementation'"
  fi
fi
```

**Remediation**:
```bash
# Add workflow state label
backlog task edit <task-id> -l "workflow:In Implementation"
```

**Workflow States**:
- `workflow:Assessed` - SDD suitability evaluated
- `workflow:Specified` - Requirements captured
- `workflow:Planned` - Architecture planned
- `workflow:In Implementation` - Code being written
- `workflow:Validated` - QA/security validated
- `workflow:Deployed` - Released

**Rationale**: Prevents "what do I do next?" confusion, enables workflow automation and state machine validation.

---

## Phase: FREEZE (Task Suspension)

**Applies to**: `/flow:freeze`

These rules ensure work can be safely suspended and resumed without context loss.

---

### Rule: FREEZE-001 - Task Memory Snapshot
**Severity**: BLOCKING
**Enforcement**: strict

Task memory MUST be updated with current state before freezing. This is the primary mechanism for context preservation.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  MEMORY_FILE="backlog/memory/${TASK_ID}.md"
  if [ ! -s "$MEMORY_FILE" ]; then
    echo "[X] FREEZE-001 VIOLATION: Task memory empty or missing: $MEMORY_FILE"
  else
    # Check for Current State section
    grep -q "## Current State" "$MEMORY_FILE" 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "[X] FREEZE-001 VIOLATION: No 'Current State' section in task memory"
    fi
  fi
fi
```

**Remediation**:
```bash
# Update task memory with freeze snapshot
cat >> "backlog/memory/${TASK_ID}.md" << 'EOF'

## Current State (Frozen: $(date +%Y-%m-%d %H:%M))

### Progress
- [x] Completed item 1
- [x] Completed item 2
- [ ] In progress item (50% complete)

### Resume Instructions
1. First thing to do when resuming
2. Second thing to check
3. Run these tests: pytest tests/test_feature.py

### Context
- Key decision: chose X over Y because Z
- Watch out for: gotcha description

### Blockers
- None / or describe blocker
EOF
```

**Rationale**: Ensures context preservation across time/person/machine boundaries. Enables any engineer to resume work.

---

### Rule: FREEZE-002 - Remote Sync Required
**Severity**: BLOCKING
**Enforcement**: strict

Code and task memory MUST be committed and pushed to remote before freeze. Local-only work risks loss.

**Validation**:
```bash
# Check for uncommitted changes
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  echo "[X] FREEZE-002 VIOLATION: $UNCOMMITTED uncommitted changes detected"
  echo "Remediation: git add . && git commit -s -m 'wip: freeze checkpoint'"
fi

# Check for unpushed commits
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l || echo 0)
if [ "$UNPUSHED" -gt 0 ]; then
  echo "[X] FREEZE-002 VIOLATION: $UNPUSHED unpushed commits"
  echo "Remediation: git push origin $(git branch --show-current)"
fi
```

**Remediation**:
```bash
# Commit and push all changes
git add .
git commit -s -m "wip: freeze checkpoint - $(date +%Y-%m-%d)"
git push origin $(git branch --show-current)
```

**Rationale**: Prevents work loss due to hardware failure, machine changes, or accidental deletion.

---

### Rule: FREEZE-003 - Working State Required
**Severity**: BLOCKING
**Enforcement**: strict

Code MUST be in a working state before freeze. Tests should pass, or failures should be documented.

**Validation**:
```bash
# Run basic validation
if [ -f "pyproject.toml" ]; then
  uv run ruff check . 2>/dev/null
  LINT_STATUS=$?
  uv run pytest tests/ -x -q 2>/dev/null
  TEST_STATUS=$?
  if [ $LINT_STATUS -ne 0 ] || [ $TEST_STATUS -ne 0 ]; then
    echo "WARNING: FREEZE-003: Code may not be in working state"
    echo "Document known failures in task memory if proceeding with freeze"
  fi
fi
```

**Remediation**:
```bash
# Fix issues before freeze
uv run ruff check --fix .
uv run pytest tests/ -x

# Or document known issues in task memory if they can't be fixed immediately
echo "### Known Issues at Freeze Time" >> "backlog/memory/${TASK_ID}.md"
echo "- Test X failing due to Y (not blocking)" >> "backlog/memory/${TASK_ID}.md"
```

**Rationale**: Prevents resuming work with a broken baseline. Known failures should be documented, not hidden.

---

## Phase: VALIDATION (Quality Gates)

**Applies to**: `/flow:validate`

These rules are the gateway to PR creation. ALL must pass before creating a PR.

---

### Rule: VALID-001 - Decision Traceability
**Severity**: BLOCKING
**Enforcement**: strict

All significant decisions MUST be logged in JSONL with task traceability. This is verified before PR creation.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  DECISION_LOG="memory/decisions/${TASK_ID}.jsonl"
  if [ ! -f "$DECISION_LOG" ]; then
    echo "[X] VALID-001 VIOLATION: No decision log found: $DECISION_LOG"
  else
    ENTRY_COUNT=$(wc -l < "$DECISION_LOG" 2>/dev/null || echo 0)
    if [ "$ENTRY_COUNT" -eq 0 ]; then
      echo "[X] VALID-001 VIOLATION: Decision log is empty"
    fi

    # Validate JSONL format
    while IFS= read -r line; do
      echo "$line" | jq empty 2>/dev/null
      if [ $? -ne 0 ]; then
        echo "[X] VALID-001 VIOLATION: Invalid JSONL format in decision log"
        break
      fi
    done < "$DECISION_LOG"
  fi
fi
```

**Remediation**:
```bash
# Add missing decisions to log
./scripts/bash/rigor-decision-log.sh \
  --task task-541 \
  --phase execution \
  --decision "Description of decision" \
  --rationale "Why this choice" \
  --actor "@backend-engineer"
```

**Rationale**: Enables audits, post-mortems, and knowledge transfer. Decisions without rationale are lost context.

---

### Rule: VALID-002 - Lint and SAST Required
**Severity**: BLOCKING
**Enforcement**: strict

Code MUST pass all linting and static analysis security testing (SAST) checks.

**Validation**:
```bash
# Python
if [ -f "pyproject.toml" ]; then
  echo "Running lint check..."
  uv run ruff check .
  LINT_STATUS=$?

  echo "Running SAST check..."
  uv run bandit -r src/ -ll 2>/dev/null || echo "Bandit not installed - skipping SAST"

  if [ $LINT_STATUS -ne 0 ]; then
    echo "[X] VALID-002 VIOLATION: Lint check failed"
  fi
fi
```

**Remediation**:
```bash
# Fix linting issues
uv run ruff check --fix .

# Review and fix SAST findings
uv run bandit -r src/ -ll
```

**Rationale**: Catches security vulnerabilities and code quality issues before they reach production.

---

### Rule: VALID-003 - Coding Standards Compliance
**Severity**: BLOCKING
**Enforcement**: strict

Code MUST adhere to project coding standards. Key checks:
- No unused imports
- No unused variables
- Type hints on public functions (Python)
- Defensive coding at boundaries

**Validation**:
```bash
if [ -f "pyproject.toml" ]; then
  # Check for unused imports and variables
  echo "Checking for unused imports and variables..."
  uv run ruff check --select F401,F841 .
  if [ $? -ne 0 ]; then
    echo "[X] VALID-003 VIOLATION: Unused imports or variables detected"
    echo "Remediation: uv run ruff check --select F401,F841 --fix ."
  fi
fi
```

**Remediation**:
```bash
# Remove unused imports
uv run ruff check --select F401 --fix .

# Remove unused variables
uv run ruff check --select F841 --fix .

# Add type hints to public functions
# See memory/code-standards.md for full checklist
```

**Rationale**: Consistent coding standards improve maintainability and reduce bugs.

---

### Rule: VALID-004 - Zero Merge Conflicts
**Severity**: BLOCKING
**Enforcement**: strict

Branch MUST be rebased from main with zero merge conflicts before PR creation.

**Validation**:
```bash
# Check if branch contains all commits from main
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)
if [ "$BEHIND" -gt 0 ]; then
  echo "[X] VALID-004 VIOLATION: Branch is $BEHIND commits behind main"
  echo "Remediation: git fetch origin main && git rebase origin/main"
fi
```

**Remediation**:
```bash
# Rebase from main
git fetch origin main
git rebase origin/main

# Resolve any conflicts, then continue
git rebase --continue

# Force push (with lease for safety)
git push --force-with-lease origin $(git branch --show-current)
```

**Rationale**: Prevents integration delays and merge conflicts during PR merge. PRs with conflicts waste reviewer time.

---

### Rule: VALID-005 - Acceptance Criteria Met
**Severity**: BLOCKING
**Enforcement**: strict

All acceptance criteria MUST be marked complete and verified before PR creation.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  INCOMPLETE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -c "^\[ \]" || echo 0)
  if [ "$INCOMPLETE" -gt 0 ]; then
    echo "[X] VALID-005 VIOLATION: $INCOMPLETE incomplete acceptance criteria"
    backlog task "$TASK_ID" --plain | grep "^\[ \]"
    echo "Remediation: Complete all ACs or document why they cannot be completed"
  fi
fi
```

**Remediation**:
```bash
# Check ACs as they're completed
backlog task edit <task-id> --check-ac 1
backlog task edit <task-id> --check-ac 2 --check-ac 3

# Verify all checked
backlog task <task-id> --plain | grep "^\["
```

**Rationale**: Ensures deliverables match requirements. Incomplete ACs indicate incomplete work.

---

### Rule: VALID-006 - Task Status Synchronization
**Severity**: BLOCKING
**Enforcement**: strict

Task status MUST reflect current workflow state. A PR must include task status updates.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -oP 'task-\d+' || echo "")
if [ -n "$TASK_ID" ]; then
  STATUS=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "Status:" | head -1)
  echo "Current task status: $STATUS"
  # Status should be "In Progress" during validation phase
fi
```

**Remediation**:
```bash
# Update task status
backlog task edit <task-id> -s "In Progress"

# Add implementation notes
backlog task edit <task-id> --notes $'Implementation complete.\n\nChanges:\n- File A modified\n- File B created'
```

**Rationale**: Keeps backlog as single source of truth for project state. Stale statuses cause confusion.

---

### Rule: VALID-007 - CI Readiness
**Severity**: BLOCKING
**Enforcement**: strict

All CI checks MUST pass locally before PR creation. Do NOT push and hope CI passes.

**Validation**:
```bash
if [ -f "pyproject.toml" ]; then
  echo "Running CI simulation..."

  # Format check
  uv run ruff format --check .
  FORMAT_STATUS=$?

  # Lint check
  uv run ruff check .
  LINT_STATUS=$?

  # Test check
  uv run pytest tests/ -x -q
  TEST_STATUS=$?

  if [ $FORMAT_STATUS -ne 0 ] || [ $LINT_STATUS -ne 0 ] || [ $TEST_STATUS -ne 0 ]; then
    echo "[X] VALID-007 VIOLATION: CI checks would fail"
    echo "Fix all issues before creating PR"
  else
    echo "[Y] All CI checks passed"
  fi
fi
```

**Remediation**:
```bash
# Fix formatting
uv run ruff format .

# Fix linting
uv run ruff check --fix .

# Fix tests
uv run pytest tests/ -v  # See what's failing

# Then run combined check
uv run ruff format --check . && uv run ruff check . && uv run pytest tests/ -x -q
```

**Rationale**: Prevents PR churn and CI noise. PRs that fail CI waste everyone's time.

---

## Phase: PR (Pull Request Workflow)

**Applies to**: After `/flow:validate` passes

These rules govern the PR lifecycle from creation to merge.

---

### Rule: PR-001 - DCO Sign-off Required
**Severity**: BLOCKING
**Enforcement**: strict

All commits MUST include DCO (Developer Certificate of Origin) sign-off.

**Validation**:
```bash
# Check all commits in branch for sign-off
UNSIGNED=$(git log origin/main..HEAD --format='%h %s' 2>/dev/null | while read hash msg; do
  git log -1 --format='%b' "$hash" | grep -q "Signed-off-by:" || echo "$hash"
done | wc -l)

if [ "$UNSIGNED" -gt 0 ]; then
  echo "[X] PR-001 VIOLATION: $UNSIGNED commits missing DCO sign-off"
  echo "Remediation: git rebase origin/main --exec 'git commit --amend --no-edit -s'"
fi
```

**Remediation**:
```bash
# Add sign-off to all commits (interactive rebase)
git rebase origin/main --exec "git commit --amend --no-edit -s"

# Or for single commit
git commit --amend -s

# Push with force (after rebase)
git push --force-with-lease origin $(git branch --show-current)
```

**Rationale**: DCO is a legal requirement for open-source contributions, certifying you have the right to submit the code.

---

### Rule: PR-002 - Copilot Comments Resolution
**Severity**: BLOCKING
**Enforcement**: strict

PR MUST have zero unresolved Copilot review comments before human review. Address all automated feedback first.

**Validation**:
```bash
# Check PR for unresolved Copilot comments (requires gh CLI)
PR_NUMBER=$(gh pr view --json number -q '.number' 2>/dev/null || echo "")
if [ -n "$PR_NUMBER" ]; then
  COPILOT_COMMENTS=$(gh api "repos/{owner}/{repo}/pulls/${PR_NUMBER}/comments" 2>/dev/null | \
    jq '[.[] | select(.user.login | contains("copilot"))] | length')
  if [ "$COPILOT_COMMENTS" -gt 0 ]; then
    echo "INFO: PR-002: $COPILOT_COMMENTS Copilot comments to review"
    echo "Address all comments before requesting human review"
  fi
fi
```

**Remediation**:
```bash
# Create iteration branch to address comments
git checkout -b "$(git branch --show-current)-v2"

# Make fixes
# ...

# Push new branch, create new PR, close old one
git push origin "$(git branch --show-current)"
gh pr create --title "feat: description (v2)" --body "Addresses Copilot feedback from PR #N"
gh pr close <old-pr-number>
```

**Rationale**: Maximizes human reviewer efficiency by resolving automated feedback first. See ADR-004.

---

### Rule: PR-003 - Version Iteration Naming
**Severity**: BLOCKING
**Enforcement**: strict

Iteration branches MUST follow naming pattern: `{original-branch}-v2`, `-v3`, etc.

**Validation**:
```bash
BRANCH=$(git branch --show-current 2>/dev/null)
if [[ "$BRANCH" =~ -v[0-9]+$ ]]; then
  # This is an iteration branch - validate base exists
  BASE_BRANCH=$(echo "$BRANCH" | sed 's/-v[0-9]*$//')
  git rev-parse --verify "$BASE_BRANCH" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "[X] PR-003 VIOLATION: Base branch not found: $BASE_BRANCH"
  else
    echo "[Y] PR-003: Valid iteration branch from $BASE_BRANCH"
  fi
fi
```

**Remediation**:
```bash
# Create iteration branch from current
git checkout -b "$(git branch --show-current)-v2"

# Or calculate next version
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" =~ -v([0-9]+)$ ]]; then
  VERSION="${BASH_REMATCH[1]}"
  NEXT=$((VERSION + 1))
  BASE=$(echo "$CURRENT" | sed 's/-v[0-9]*$//')
  git checkout -b "${BASE}-v${NEXT}"
else
  git checkout -b "${CURRENT}-v2"
fi
```

**Rationale**: Clear iteration tracking, prevents confusion about PR lineage. See ADR-004 for full pattern.

---

## Utilities and Helpers

### Quick Validation Commands

```bash
# Validate all rules for current phase (add to scripts/bash/)
./scripts/bash/rigor-validate.sh setup
./scripts/bash/rigor-validate.sh execution
./scripts/bash/rigor-validate.sh validation
./scripts/bash/rigor-validate.sh pr

# Generate compliant branch name
./scripts/bash/rigor-branch-name.sh task-541 "rigor-rules-include"

# Log a decision
./scripts/bash/rigor-decision-log.sh \
  --task task-541 \
  --phase execution \
  --decision "Using shared include pattern" \
  --rationale "Single source of truth" \
  --actor "@backend-engineer"
```

### Workflow Status Output Template

After each workflow command completes, output status in this format:

```
[Y] Phase: {phase-name} complete
    Current state: workflow:{State}
    Next step: /flow:{next-command}

    Progress:
    [Y] Setup phase
    [Y] Execution phase
    [ ] Validation phase (NEXT)
    [ ] PR phase

    Decisions logged: N (see memory/decisions/task-XXX.jsonl)
```

---

## Integration Points

This file is included in /flow:* commands via:

```markdown
\{\{INCLUDE:.claude/commands/flow/_rigor-rules.md\}\}
```

**Command Phase Mapping**:

| Command | Phase(s) Applied |
|---------|-----------------|
| `/flow:assess` | SETUP |
| `/flow:specify` | SETUP |
| `/flow:plan` | SETUP, EXECUTION |
| `/flow:implement` | EXECUTION |
| `/flow:freeze` | FREEZE |
| `/flow:validate` | VALIDATION |
| `/flow:operate` | PR (post-merge) |

---

## References

- **ADR-001**: Rigor Rules Include Pattern
- **ADR-002**: JSONL Decision Logging
- **ADR-003**: Branch Naming Convention
- **ADR-004**: PR Iteration Pattern
- **memory/critical-rules.md**: Absolute rules (never delete tests, etc.)
- **memory/code-standards.md**: Code quality standards

---

*Last Updated: 2025-12-17 | Version: 1.0*


# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### Light Mode Detection

First, check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".flowspec-light-mode" ]; then
  echo "Project is in LIGHT MODE (~60% faster workflow)"
fi
```

**Light Mode Behavior**:
- `/flow:research` -> **SKIPPED** (inform user and suggest `/flow:plan` instead)
- `/flow:plan` -> Uses `plan-light.md` template (high-level only)
- `/flow:specify` -> Uses `spec-light.md` template (combined stories + AC)

If in light mode and the current command is `/flow:research`, inform the user:
```text
ℹ️ This project is in Light Mode

Light mode skips the research phase for faster iteration.
Current state: workflow:Specified

Suggestions:
  - Run /flow:plan to proceed directly to planning
  - To enable research, delete .flowspec-light-mode and use full mode
  - See docs/guides/when-to-use-light-mode.md for details
```

### 1. Get Current Task and State

```bash
# Find the task you're working on
# Option A: If task ID was provided in arguments, use that
# Option B: Look for task currently "In Progress"
backlog task list -s "In Progress" --plain

# Get task details and extract workflow state from labels
TASK_ID="<task-id>"  # Replace with actual task ID
backlog task "$TASK_ID" --plain
```

### 2. Check Workflow State

Extract the `workflow:*` label from the task. The state must match one of the **Required Input States** for this command:

| Command | Required Input States | Output State |
|---------|----------------------|--------------|
| /flow:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /flow:specify | workflow:Assessed | workflow:Specified |
| /flow:research | workflow:Specified | workflow:Researched |
| /flow:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /flow:implement | workflow:Planned | workflow:In Implementation |
| /flow:validate | workflow:In Implementation | workflow:Validated |
| /flow:operate | workflow:Validated | workflow:Deployed |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /flow:<command>

Current state: "<current-workflow-label>"
Required states: <list-of-valid-input-states>

Suggestions:
  - Valid workflows for current state: <list-valid-commands>
  - Use --skip-state-check to bypass (not recommended)
```

**DO NOT PROCEED** unless:
- The task is in a valid input state, OR
- User explicitly requests to skip the check

### 4. Update State After Completion

After successful workflow completion, update the task's workflow state:

```bash
# Remove old workflow label and add new one
# Replace <output-state> with the output state from the table above
backlog task edit "$TASK_ID" -l "workflow:<output-state>"
```

## Workflow State Labels Reference

Tasks use labels with the `workflow:` prefix to track their current workflow state:

- `workflow:Assessed` - SDD suitability evaluated (/flow:assess complete)
- `workflow:Specified` - Requirements captured (/flow:specify complete)
- `workflow:Researched` - Technical research completed (/flow:research complete)
- `workflow:Planned` - Architecture planned (/flow:plan complete)
- `workflow:In Implementation` - Code being written (/flow:implement in progress)
- `workflow:Validated` - QA and security validated (/flow:validate complete)
- `workflow:Deployed` - Released to production (/flow:operate complete)

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from flowspec_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/flow:research', '/flow:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.


**For /flow:validate**: Required input state is `workflow:In Implementation`. Output state will be `workflow:Validated`.

If the task doesn't have the required workflow state, inform the user:
- If task needs implementation first: suggest running `/flow:implement`
- If validation is being re-run on deployed work: use `--skip-state-check` if appropriate

**Proceed to Phase 0 ONLY if workflow validation passes.**

### Extended Thinking Mode

> **🧠 Think Hard**: Security and quality validation require thorough analysis. Apply extended thinking to:
> - Attack vectors and vulnerability assessment
> - Data flow security and authentication boundaries
> - Test coverage gaps and edge cases
> - Compliance requirements and best practices

## Workflow Overview

This command orchestrates a phased validation workflow:

- **Phase 0: Task Discovery & Load** - Find/load target task
- **Phase 1: Automated Testing** - Run tests, linting, type checks
- **Phase 2: Agent Validation (Parallel)** - QA Guardian + Security Engineer
- **Phase 3: Documentation** - Technical Writer agent
- **Phase 4: AC Verification** - Verify all acceptance criteria
- **Phase 5: Task Completion** - Generate notes and mark Done
- **Phase 6: PR Generation** - Create pull request with approval

## Execution Instructions

Follow these phases sequentially. **Phase failures MUST halt the workflow** with clear error messages indicating which phase failed and why.

The command is **re-runnable** after fixing issues - it handles partial completion gracefully by checking task state at each phase.

---

### Phase 0: Task Discovery & Load

**Report progress**: Print "Phase 0: Discovering and loading task..."

#### Step 1: Determine Target Task ID

```bash
# If user provided task-id argument, use it
TASK_ID="$ARGUMENTS"

# Otherwise, discover in-progress task
if [ -z "$TASK_ID" ]; then
  # Find tasks in "In Progress" status
  backlog task list -s "In Progress" --plain
fi
```

**Task Selection Logic**:
- If user provided task ID: Use it directly
- If no argument: Find the single "In Progress" task
- If multiple "In Progress" tasks: Ask user which one to validate
- If no "In Progress" tasks: Error and halt

**Error Handling**:
- If task ID not found: "[X] Phase 0 Failed: Task {task-id} does not exist."
- If no in-progress tasks: "[X] Phase 0 Failed: No tasks in 'In Progress' status. Please specify a task ID."
- If multiple in-progress tasks: List them and ask user to specify which one

#### Step 2: Load Full Task Details

```bash
# Load complete task data
backlog task <task-id> --plain
```

**Parse critical fields**:
- Task ID
- Title
- Description
- Acceptance Criteria (list with checked status)
- Current Status
- Implementation Plan (if exists)
- Implementation Notes (if exists)

**Phase 0 Success**: Print task summary:
```
✅ Phase 0 Complete: Loaded task-094
   Title: Integration - Enhanced /flow:validate Command
   Status: In Progress
   ACs: 0/8 complete
```

---

### Phase 1: Automated Testing

**Report progress**: Print "Phase 1: Running automated tests, linting, and type checks..."

**Important**: Only run tests if code changes are involved. Skip for documentation-only tasks.

#### Step 1: Detect Project Type

```bash
# Check for test frameworks
if [ -f "pyproject.toml" ]; then
  # Python project
  echo "Detected Python project"
elif [ -f "package.json" ]; then
  # Node.js project
  echo "Detected Node.js project"
fi
```

#### Step 2: Run Test Suite

**For Python projects**:
```bash
# Run pytest with coverage
pytest tests/ -v --cov=src/flowspec_cli --cov-report=term-missing

# Run linting
ruff check . --output-format=concise

# Run type checks (if mypy configured)
if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml; then
  mypy src/
fi
```

**For Node.js projects**:
```bash
# Run tests
npm test  # or bun test, pnpm test

# Run linting
npm run lint  # or eslint .

# Run type checks
npm run typecheck  # or tsc --noEmit
```

#### Step 3: Evaluate Results

**Success criteria**:
- All tests pass (exit code 0)
- No critical linting errors
- Type checks pass (if applicable)

**Error Handling**:
- If tests fail: "[X] Phase 1 Failed: {N} test(s) failed. Fix tests before continuing."
- If linting fails: "⚠️  Phase 1 Warning: Linting issues detected. Review before continuing."
- If type checks fail: "[X] Phase 1 Failed: Type check errors found."

#### Step 4: Document Skipped Tests

**IMPORTANT**: If any tests are skipped, document them for the PR body.

```bash
# Capture skipped tests with reasons
pytest tests/ -v 2>&1 | grep -E "SKIPPED" > /tmp/skipped_tests.txt
```

For each skipped test, categorize and document the reason:
- **Benchmark tests**: Require full dataset or extended runtime
- **Performance tests**: Require specific environment or resources
- **Integration tests**: Require external services (databases, APIs, web servers)
- **E2E tests**: Require full environment setup
- **Platform-specific tests**: Require specific OS or architecture
- **Flaky tests**: Known intermittent failures (should reference issue if exists)

Store this information for Phase 6 PR generation.

**Phase 1 Success**: Print test summary:
```
✅ Phase 1 Complete: All automated checks passed
   Tests: 45 passed, 17 skipped
   Coverage: 87%
   Linting: No issues
   Type checks: Passed
   Skipped tests: Documented for PR
```

**Re-run handling**: If tests already passed in previous run, skip and print:
```
⏭️  Phase 1 Skipped: Tests already validated in previous run
```

---

### Phase 2: Agent Validation (Parallel Execution)

**Report progress**: Print "Phase 2: Launching QA Guardian and Security Engineer agents (parallel)..."

**IMPORTANT**: Launch QA and Security agents in parallel for efficiency using the Task tool.

#### Backlog Instructions Template

Each validator agent context below includes `{{BACKLOG_INSTRUCTIONS}}` which must be replaced with the content from `.claude/commands/flow/_backlog-instructions.md`. This ensures all agents have consistent backlog task management instructions.

**When executing this command, include the full content of `_backlog-instructions.md` in place of each `{{BACKLOG_INSTRUCTIONS}}` marker.**

#### Agent 1: Quality Guardian (QA Testing)

Use the Task tool to launch a **general-purpose** agent (Quality Guardian context):

```
# AGENT CONTEXT: Quality Guardian

You are the Quality Guardian, a vigilant protector of system integrity, user trust, and organizational reputation. You are the constructive skeptic who sees failure modes others miss, anticipates edge cases others ignore, and champions excellence as the minimum acceptable standard.

## Core Philosophy
- **Constructive Skepticism**: Question everything with intent to improve
- **Risk Intelligence**: See potential failures as opportunities for resilience
- **User-Centric**: Champion end user experience above all else
- **Long-Term Thinking**: Consider maintenance, evolution, technical debt from day one
- **Security-First**: Every feature is a potential vulnerability until proven otherwise

## Analysis Framework
1. **Failure Imagination Exercise**: List failure modes, assess impact/likelihood, plan detection/recovery
2. **Edge Case Exploration**: Test at zero, infinity, malformed input, extreme load, hostile users
3. **Three-Layer Critique**: Acknowledge value -> Identify risk -> Suggest mitigation
4. **Risk Classification**: Critical, High, Medium, Low

## Risk Dimensions

{{BACKLOG_INSTRUCTIONS}}
- Technical: Scalability, performance, reliability, concurrency
- Security: Vulnerabilities, attack surfaces, data exposure
- Business: Cost overruns, market timing, operational complexity
- User: Usability issues, adoption barriers, accessibility
- Operational: Maintenance burden, monitoring, debugging

# TASK: Conduct comprehensive quality validation for: [USER INPUT FEATURE]

Code and Artifacts:


Backlog Context:
[Include backlog task details from discovery phase if applicable]

Validation Requirements:

1. **Functional Testing & Acceptance Criteria Validation**
   - **Verify all backlog task acceptance criteria are met**
   - Cross-reference test results with AC requirements
   - **Mark ACs complete via backlog CLI as validation succeeds**
   - Test user workflows end-to-end
   - Validate edge cases and boundary conditions
   - Test error handling and recovery

2. **API and Contract Testing**
   - API endpoint testing (REST/GraphQL/gRPC)
   - Contract testing for API compatibility
   - Response validation
   - Error response testing

3. **Integration Testing**
   - Frontend-backend integration
   - Third-party service integration
   - Database integration
   - Message queue/event processing

4. **Performance Testing**
   - Load testing (expected traffic)
   - Stress testing (peak traffic)
   - Latency measurement (p50, p95, p99)
   - Resource utilization
   - Scalability validation

5. **Non-Functional Requirements**
   - Accessibility (WCAG 2.1 AA compliance)
   - Cross-browser/platform compatibility
   - Mobile responsiveness
   - Internationalization (if applicable)

6. **Risk Analysis**
   - Identify failure modes
   - Assess impact and likelihood
   - Validate monitoring and alerting
   - Verify rollback procedures

Deliver comprehensive test report with:
- Test results (passed/failed)
- Quality metrics
- Risk assessment
- Issues categorized by severity
- Recommendations for production readiness
```

**Phase 2 Success**: Print summary when both agents complete:
```
✅ Phase 2 Complete: Agent validation passed
   QA Guardian: 15 test scenarios validated
   Security Engineer: No critical vulnerabilities found
```

#### Agent 2: Security Engineer

Use the Task tool to launch a **general-purpose** agent (Secure-by-Design Engineer context):

```
# AGENT CONTEXT: Secure-by-Design Engineer

You are a Secure-by-Design Engineer, an experienced security specialist focused on building security into the development lifecycle from the ground up. Security is not a feature to be added later, but a fundamental quality built into every aspect of the system from the beginning.

## Core Principles
- **Assume Breach**: Design as if systems will be compromised
- **Defense in Depth**: Multiple security layers
- **Principle of Least Privilege**: Minimum necessary access
- **Fail Securely**: Failures don't compromise security
- **Security by Default**: Secure out of the box

## Security Analysis Process
1. **Risk Assessment**: Identify assets, threats, business impact
2. **Threat Modeling**: Assets, threats, attack vectors
3. **Architecture Analysis**: Security weaknesses in design
4. **Code Review**: Vulnerability patterns (SQL injection, XSS, etc.)
5. **Access Control Review**: Authentication, authorization, privilege management
6. **Data Flow Analysis**: Sensitive information handling
7. **Dependency Security**: Third-party vulnerabilities
8. **Incident Response**: Monitoring and detection capabilities

## Severity Classification
- **Critical**: Authentication bypass, SQL injection, RCE
- **High**: XSS, privilege escalation, data exposure
- **Medium**: Information disclosure, DoS, weak crypto
- **Low**: Config issues, missing headers

{{BACKLOG_INSTRUCTIONS}}

# TASK: Conduct comprehensive security assessment for: [USER INPUT FEATURE]

Code and Infrastructure:
[Include implementation code, infrastructure configs, dependencies]

Backlog Context:
[Include backlog task details with security-related acceptance criteria]

Security Validation Requirements:

0. **Backlog Task Security Validation**
   - Validate security-related acceptance criteria
   - Cross-reference security tests with task ACs
   - Mark security ACs complete via backlog CLI as validations pass
   - Update task notes with security findings

1. **Code Security Review**
   - Authentication and authorization implementation
   - Input validation and sanitization
   - SQL/NoSQL injection prevention
   - XSS/CSRF prevention
   - Secure error handling (no sensitive data exposure)

2. **Dependency Security**
   - Scan for known vulnerabilities (CVEs)
   - Check dependency licenses
   - Validate supply chain security
   - Review SBOM (Software Bill of Materials)

3. **Infrastructure Security**
   - Secrets management validation
   - Network security configuration
   - Access controls and IAM
   - Encryption at rest and in transit
   - Container security (if applicable)

4. **Compliance**
   - GDPR compliance (if handling EU data)
   - SOC2 requirements
   - Industry-specific regulations
   - Data privacy requirements

5. **Threat Modeling**
   - Identify attack vectors
   - Assess exploitability
   - Validate security controls
   - Test defense in depth

6. **Penetration Testing** (for critical features)
   - Manual security testing
   - Automated vulnerability scanning
   - Authentication bypass attempts
   - Authorization escalation tests

Deliver comprehensive security report with:
- Security findings by severity (Critical/High/Medium/Low)
- Vulnerability details with remediation steps
- Compliance status
- Risk assessment
- Security gate approval status (Pass/Fail)
```

---

### Phase 3: Documentation

**Report progress**: Print "Phase 3: Launching Technical Writer agent for documentation..."

Use the Task tool to launch a **general-purpose** agent (Technical Writer context):

```
# AGENT CONTEXT: Senior Technical Writer

You are a Senior Technical Writer with deep expertise in creating clear, accurate, and audience-appropriate technical documentation. You transform complex technical concepts into accessible content that enables users, developers, and stakeholders to understand and effectively use software systems.

## Core Goals
- **Enable Users**: Help users accomplish their goals efficiently
- **Reduce Support**: Answer questions before they're asked
- **Build Trust**: Accurate, tested, up-to-date content
- **Scale Knowledge**: Transfer knowledge across teams and time
- **Support Different Audiences**: Technical and non-technical readers

## Documentation Types
- **API Documentation**: REST/GraphQL endpoints, parameters, examples, responses
- **User Guides**: Getting started, tutorials, how-to guides
- **Technical Documentation**: Architecture, components, configuration, deployment
- **Release Notes**: Features, breaking changes, migration guides
- **Operational Documentation**: Runbooks, monitoring, troubleshooting

## Quality Standards
- Clear structure and hierarchy
- Audience-appropriate language
- Tested, working examples
- Comprehensive but concise
- Searchable and navigable
- Accessible (alt text, headings, etc.)

{{BACKLOG_INSTRUCTIONS}}

# TASK: Create comprehensive documentation for: [USER INPUT FEATURE]

Context:
[Include feature description, implementation details, API specs, test results, security findings]

Backlog Context:
[Include backlog task details for documentation requirements]

## Documentation Task Management

Create backlog tasks for major documentation work:

```bash
# Example: Create documentation task
backlog task create "Documentation: API Reference for [Feature]" \
  -d "Complete API documentation for the feature" \
  --ac "API documentation complete" \
  --ac "Code examples provided and tested" \
  --ac "Error responses documented" \
  -l docs,api \
  --priority medium \
  -a @tech-writer
```

As you complete documentation sections, mark corresponding ACs:
```bash
backlog task edit <id> --check-ac 1  # API documentation complete
```

Documentation Deliverables:

1. **API Documentation** (if API changes)
   - Endpoint documentation
   - Request/response examples
   - Authentication requirements
   - Error codes and messages
   - Rate limiting and quotas

2. **User Documentation**
   - Feature overview and benefits
   - Getting started guide
   - Step-by-step tutorials
   - Screenshots/diagrams
   - Troubleshooting guide

3. **Technical Documentation**
   - Architecture overview
   - Component documentation
   - Configuration options
   - Deployment instructions
   - Monitoring and alerting setup

4. **Release Notes**
   - Feature summary
   - Breaking changes (if any)
   - Migration guide (if needed)
   - Known limitations
   - Bug fixes

5. **Internal Documentation**
   - Code comments for complex logic
   - Runbooks for operations
   - Incident response procedures
   - Rollback procedures

Ensure all documentation is:
- Accurate and up-to-date
- Clear and audience-appropriate
- Well-formatted with proper structure
- Accessible (alt text, headings, etc.)
- Ready for publication
```

**Phase 3 Success**: Print summary:
```
✅ Phase 3 Complete: Documentation updated
   Files updated: 3
   Sections added: User Guide, API Reference
```

---

### Phase 4: Acceptance Criteria Verification

**Report progress**: Print "Phase 4: Verifying acceptance criteria completion..."

This phase systematically verifies all task acceptance criteria are met.

#### Step 1: Load Current Task State

```bash
# Reload task to get latest AC status
backlog task <task-id> --plain
```

#### Step 2: Parse Acceptance Criteria

Extract the list of acceptance criteria with their checked status:
```json
{
  "acceptanceCriteria": [
    {"text": "Command accepts optional task-id argument", "checked": false},
    {"text": "Executes phases in order", "checked": false},
    ...
  ]
}
```

#### Step 3: Verify Each AC

For each unchecked acceptance criterion:

**Automated ACs** (can be verified by test results):
- Check if corresponding tests passed in Phase 1
- If tests passed, mark AC complete: `backlog task edit <task-id> --check-ac N`

**Manual ACs** (require human verification):
- Present AC to user
- Show relevant evidence (test output, code changes, agent reports)
- Ask user: "Has this acceptance criterion been met? [y/N]"
- If yes, mark complete: `backlog task edit <task-id> --check-ac N`
- If no, halt and report which AC failed

#### Step 4: Verify 100% Completion

After verification loop:
```bash
# Reload task to confirm all ACs checked
backlog task <task-id> --plain
```

**Success criteria**: All ACs must have `"checked": true`

**Error Handling**:
- If any AC unchecked: "[X] Phase 4 Failed: {N} acceptance criteria not yet verified. Cannot proceed to completion."
- List unchecked ACs by index and text

**Phase 4 Success**: Print summary:
```
✅ Phase 4 Complete: All acceptance criteria verified
   Total ACs: 8
   Verified: 8
   Status: 100% complete
```

---

### Phase 5: Task Completion

**Report progress**: Print "Phase 5: Generating implementation notes and marking task complete..."

#### Step 1: Generate Implementation Summary

Create comprehensive implementation notes based on:
- What was implemented (from task description and changes)
- How it was tested (from Phase 1 test results)
- Key decisions made (from agent reports)
- Validation results (from Phases 2-3)

**Example implementation notes format**:
```markdown
## Implementation Summary (2025-12-01 15:30:00)

### What Was Implemented
Enhanced the /flow:validate command with phased orchestration workflow.
Implemented 7 distinct phases with progress reporting and error handling.

### Testing
- All unit tests passing (45/45)
- Integration tests passing (12/12)
- Linting: No issues
- Type checks: Passed

### Key Decisions
- Used TaskCompletionHandler pattern for AC verification
- Implemented re-runnable workflow with state checks
- Added progress reporting at each phase
- Parallel agent execution in Phase 2 for efficiency

### Validation Results
- QA Guardian: 15 scenarios validated, all passed
- Security Engineer: No critical vulnerabilities
- Documentation: Updated 2 command files
```

#### Step 2: Add Implementation Notes

```bash
backlog task edit <task-id> --notes $'<implementation-summary>'
```

#### Step 3: Mark Task as Done

**Important**: Only mark Done if task status is currently "In Progress"

```bash
# Check current status first
backlog task <task-id> --plain

# If status is "In Progress", mark Done
if [ "$status" == "In Progress" ]; then
  backlog task edit <task-id> -s Done
fi
```

**Re-run handling**: If task already "Done", skip this step:
```
⏭️  Phase 5 Skipped: Task already marked Done
```

**Phase 5 Success**: Print summary:
```
✅ Phase 5 Complete: Task marked as Done
   Task ID: task-094
   Final Status: Done
   Implementation notes: Added
```

---

### Phase 6: Pull Request Generation

**Report progress**: Print "Phase 6: Generating pull request with human approval..."

This phase creates a well-formatted pull request using the PRGenerator pattern.

#### Step 0: Pre-PR Validation Gate (MANDATORY - NO EXCEPTIONS)

**⚠️ CRITICAL: Before creating any PR, ALL validation checks MUST pass.**

This is a blocking gate. Do NOT proceed to PR creation until ALL checks pass.

```bash
# CI Pre-flight Validation (RIGOR: VALID-007)
echo "Running CI pre-flight validation..."
echo ""

# 1. Format check - MUST pass with ZERO errors
echo "1. Format check..."
uv run ruff format --check .
FORMAT_STATUS=$?
if [ $FORMAT_STATUS -ne 0 ]; then
  echo "[X] Format check failed"
  echo "Fix: uv run ruff format ."
else
  echo "[Y] Format check passed"
fi

# 2. Lint check - MUST pass with ZERO errors
echo ""
echo "2. Lint check..."
uv run ruff check .
LINT_STATUS=$?
if [ $LINT_STATUS -ne 0 ]; then
  echo "[X] Lint check failed"
  echo "Fix: uv run ruff check --fix ."
else
  echo "[Y] Lint check passed"
fi

# 3. Test suite - MUST pass with ZERO failures
echo ""
echo "3. Test suite..."
uv run pytest tests/ -x -q
TEST_STATUS=$?
if [ $TEST_STATUS -ne 0 ]; then
  echo "[X] Tests failed"
  echo "Fix: uv run pytest tests/ -v (see detailed output)"
else
  echo "[Y] Tests passed"
fi

# 4. Unused imports/variables check
echo ""
echo "4. Unused imports/variables..."
uv run ruff check --select F401,F841 .
UNUSED_STATUS=$?
if [ $UNUSED_STATUS -ne 0 ]; then
  echo "[X] Unused imports/variables detected"
  echo "Fix: uv run ruff check --select F401,F841 --fix ."
else
  echo "[Y] No unused imports/variables"
fi

# 5. Type check (if mypy configured)
echo ""
echo "5. Type check..."
if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml 2>/dev/null; then
  uv run mypy src/ 2>/dev/null
  TYPE_STATUS=$?
  if [ $TYPE_STATUS -ne 0 ]; then
    echo "[X] Type check failed"
    echo "Fix: Review mypy errors and add type hints"
  else
    echo "[Y] Type check passed"
  fi
else
  echo "⏭️  Type check skipped (mypy not configured)"
  TYPE_STATUS=0
fi

# Evaluate overall status
echo ""
if [ $FORMAT_STATUS -ne 0 ] || [ $LINT_STATUS -ne 0 ] || [ $TEST_STATUS -ne 0 ] || [ $UNUSED_STATUS -ne 0 ] || [ $TYPE_STATUS -ne 0 ]; then
  echo "[X] Pre-PR Gate Failed: CI checks must pass before PR creation"
  echo ""
  echo "Failed checks:"
  [ $FORMAT_STATUS -ne 0 ] && echo "  - Format check"
  [ $LINT_STATUS -ne 0 ] && echo "  - Lint check"
  [ $TEST_STATUS -ne 0 ] && echo "  - Test suite"
  [ $UNUSED_STATUS -ne 0 ] && echo "  - Unused imports/variables"
  [ $TYPE_STATUS -ne 0 ] && echo "  - Type check"
  echo ""
  echo "Fix all issues and re-run /flow:validate"
  exit 1
fi

echo "[Y] All CI checks passed"
```

**Validation Checklist (ALL REQUIRED)**:

- [ ] `ruff format --check .` passes with zero errors
- [ ] `ruff check .` passes with zero errors
- [ ] `pytest tests/ -x -q` passes with zero failures
- [ ] No unused imports (`ruff check --select F401`)
- [ ] No unused variables (`ruff check --select F841`)
- [ ] Type check passes (if mypy configured)

**If ANY check fails**:
```
[X] Pre-PR Gate Failed: Validation checks must pass before PR creation.

Failures:
- [List failed checks]

Fix all issues and re-run /flow:validate
```

**⚠️ DO NOT proceed to Step 0.5 if ANY validation check fails.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

#### Step 0.5: Rebase Enforcement (RIGOR: VALID-004)

**MANDATORY**: Branch MUST be rebased from main with zero commits behind before PR creation.

```bash
# Check if branch is behind main
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

# Validate BEHIND is numeric before comparison
if ! [[ "$BEHIND" =~ ^[0-9]+$ ]]; then
  echo "[!] Warning: Could not determine commits behind main (origin/main may not exist)"
  BEHIND=0
fi

if [ "$BEHIND" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-004): Branch is $BEHIND commits behind main"
  echo "Fix: git fetch origin main && git rebase origin/main"
  echo ""
  echo "After rebasing:"
  echo "  1. Resolve any conflicts"
  echo "  2. Run tests: uv run pytest tests/ -x"
  echo "  3. Push: git push --force-with-lease origin \$(git branch --show-current)"
  exit 1
fi

echo "[Y] Branch is up-to-date with main (zero commits behind)"
```

**This is BLOCKING** - do not proceed to Step 1 if branch is behind main.

#### Step 0.6: DCO Sign-off Verification (RIGOR: PR-001)

**MANDATORY**: All commits MUST have DCO (Developer Certificate of Origin) sign-off.

```bash
# Check all commits in branch for DCO sign-off
echo "Checking DCO sign-off for all commits..."

# Use process substitution to avoid subshell variable scope issues
UNSIGNED_COMMITS=""
while read -r hash msg; do
  # Check for Signed-off-by anywhere in commit body (not just at line start)
  if ! git log -1 --format='%B' "$hash" 2>/dev/null | grep -q "Signed-off-by:"; then
    UNSIGNED_COMMITS="${UNSIGNED_COMMITS}${hash} ${msg}\n"
  fi
done < <(git log origin/main..HEAD --format='%h %s' 2>/dev/null)

# Count unsigned commits (wc -w counts words; wc -l on empty string returns 1)
if [ -n "$UNSIGNED_COMMITS" ]; then
  UNSIGNED_COUNT=$(echo -e "$UNSIGNED_COMMITS" | grep -c .)
  echo "[X] RIGOR VIOLATION (PR-001): $UNSIGNED_COUNT commits missing DCO sign-off"
  echo ""
  echo "Unsigned commits:"
  echo -e "$UNSIGNED_COMMITS" | while read -r line; do
    [ -n "$line" ] && echo "  $line"
  done
  echo ""
  echo "Fix: Add sign-off to all commits:"
  echo "  git rebase origin/main --exec 'git commit --amend --no-edit -s'"
  echo "  git push --force-with-lease origin \$(git branch --show-current)"
  exit 1
fi

echo "[Y] All commits have DCO sign-off"
```

**DCO Certification**: By signing off, you certify that you wrote the code or otherwise have the right to submit it under the project's license.

**This is BLOCKING** - do not proceed to Step 1 if any commits lack DCO sign-off.

#### Step 1: Check Branch Status and Merge Conflicts

```bash
# Verify current branch is pushed to remote
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null

# Check for merge conflicts with main/master
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -q "^<<<<<<<" && echo "CONFLICTS"
```

**If branch not pushed**:
```
⚠️  Warning: Current branch is not pushed to remote.
Please push your branch first:
  git push -u origin $(git branch --show-current)

[X] Phase 6 Failed: Branch not pushed to remote
```

**If merge conflicts exist** (MANDATORY - NO EXCEPTIONS):
```
[X] Phase 6 Failed: Merge conflicts detected with main branch.

You MUST resolve conflicts before creating a PR:
  git fetch origin main
  git rebase origin/main
  # Resolve any conflicts
  git push --force-with-lease

DO NOT submit PRs with merge conflicts.
```

Halt and wait for user to resolve conflicts and rebase.

#### Step 2: Generate PR Title

Use conventional commit format derived from task title:
```
# Task title: "Integration - Enhanced /flow:validate Command"
# PR title: "feat: enhanced /flow:validate command"
```

**PR Type Detection**:
- If task has label "feature": `feat:`
- If task has label "fix" or "bug": `fix:`
- If task has label "docs": `docs:`
- If task has label "refactor": `refactor:`
- Default: `feat:`

#### Step 3: Generate PR Body

Create comprehensive PR body with sections:

```markdown
## Summary
Completes task: task-094

[Implementation notes from Phase 5]

## Acceptance Criteria

1. [x] Command accepts optional task-id argument; defaults to current in-progress task if not provided
2. [x] Executes phases in order: 0 (load) -> 1 (test) -> 2 (agents, parallel) -> 3 (docs) -> 4 (verify) -> 5 (complete) -> 6 (PR)
3. [x] Each phase reports progress to user before execution
4. [x] Phase failures halt workflow with clear error message
5. [x] Command can be re-run after fixing issues
6. [x] Updates .claude/commands/flow/validate.md
7. [x] Updates templates/commands/flowspec/validate.md
8. [x] Includes comprehensive help text

## Test Plan

- ✅ Unit tests: 45 passed
- ✅ Integration tests: 12 passed
- ✅ Linting: No issues
- ✅ Type checks: Passed
- ✅ Manual testing: Validated all phases execute correctly

## Skipped Tests

**REQUIRED**: If any tests were skipped during validation, document them here with explanations.

<details>
<summary>N skipped tests - click to expand</summary>

**[Category] tests** (reason):
- `test_file.py::TestClass::test_name` - [specific reason]

</details>

**Note**: All skipped tests are pre-existing and unrelated to this PR. [Or explain if any are related]

## Validation Results

- **QA Guardian**: 15 scenarios validated, all passed
- **Security Engineer**: No critical vulnerabilities found
- **Documentation**: Command files updated and validated
```

#### Step 4: Present PR Preview

Display formatted PR preview to user:
```
================================================================================
PR PREVIEW
================================================================================

Title: feat: enhanced /flow:validate command

Body:
--------------------------------------------------------------------------------
[Full PR body as shown above]
--------------------------------------------------------------------------------
```

#### Step 5: Request Human Approval

**Critical**: Must get explicit approval before creating PR.

```
Create this pull request? [y/N]:
```

- If user enters `y` or `yes`: Proceed to Step 6
- If user enters anything else: Cancel PR creation

**If cancelled**:
```
[X] Phase 6 Cancelled: PR creation cancelled by user

Next steps:
- Review PR preview above
- Make any needed changes
- Re-run /flow:validate to try again
```

Exit gracefully without error.

#### Step 6: Create PR Using gh CLI

```bash
gh pr create --title "<pr-title>" --body "<pr-body>"
```

**Error Handling**:
- If `gh` not found: "[X] Phase 6 Failed: GitHub CLI not installed. Install from https://cli.github.com/"
- If `gh pr create` fails: Display gh error message and halt
- If PR already exists for branch: Display existing PR URL

#### Step 7: Extract PR URL

Parse PR URL from `gh` output and display to user.

**Phase 6 Success**: Print summary:
```
✅ Phase 6 Complete: Pull request created successfully

PR URL: https://github.com/owner/repo/pull/123
Task: task-094 (Done)

Next: Monitor for Copilot review comments (see Phase 6.5 for iteration guidance)
```

---

### Phase 6.5: Copilot Comment Resolution (Post-PR Iteration)

**Report progress**: Print "Phase 6.5: Monitoring for Copilot review comments..."

**IMPORTANT**: This phase is executed AFTER PR creation when GitHub Copilot provides review comments.

#### When to Execute Phase 6.5

Execute this phase when:
- PR has been created successfully
- GitHub Copilot has posted review comments on the PR
- Comments suggest code improvements, security issues, or best practice violations

#### Step 1: Review Copilot Comments

```bash
# View Copilot comments on the PR
gh pr view <pr-number> --comments

# Or view in browser
gh pr view <pr-number> --web
```

**Evaluation criteria**:
- Is the suggestion valid and improves code quality?
- Does it address a real issue (security, performance, maintainability)?
- Is it aligned with project coding standards?

#### Step 2: Decide on Action

**If ALL Copilot comments are invalid/not applicable**:
- Add a comment explaining why suggestions are not being applied
- Proceed to request human review
- No iteration needed

**If ANY Copilot comments are valid**:
- Proceed to Step 3 to create iteration branch

#### Step 3: Create Iteration Branch

**RIGOR: PR-003 - Version Iteration Naming**

```bash
# Determine current iteration version
CURRENT_BRANCH=$(git branch --show-current)

# Calculate next version using portable extraction (works in bash 3.2+)
# Extract version number using sed for better portability
VERSION=$(echo "$CURRENT_BRANCH" | sed -n 's/.*-v\([0-9]*\)$/\1/p')

if [ -n "$VERSION" ]; then
  # Already an iteration branch (e.g., hostname/task-123/feature-v2)
  NEXT_VERSION=$((VERSION + 1))
  BASE_BRANCH=$(echo "$CURRENT_BRANCH" | sed 's/-v[0-9]*$//')
  ITERATION_BRANCH="${BASE_BRANCH}-v${NEXT_VERSION}"
else
  # First iteration (e.g., hostname/task-123/feature -> hostname/task-123/feature-v2)
  ITERATION_BRANCH="${CURRENT_BRANCH}-v2"
fi

# Create iteration branch
git checkout -b "$ITERATION_BRANCH"
echo "Created iteration branch: $ITERATION_BRANCH"
```

**Branch naming pattern**:
- Original: `hostname/task-NNN/feature-slug`
- First iteration: `hostname/task-NNN/feature-slug-v2`
- Second iteration: `hostname/task-NNN/feature-slug-v3`
- Nth iteration: `hostname/task-NNN/feature-slug-v{N+1}`

#### Step 4: Apply Fixes

Address each valid Copilot comment:

1. **Make code changes** to resolve the issue
2. **Add tests** if new logic introduced
3. **Update documentation** if behavior changed
4. **Verify locally** with CI pre-flight checks:

```bash
# Run full validation suite
uv run ruff format .
uv run ruff check --fix .
uv run pytest tests/ -x -q

# Verify no issues
if [ $? -eq 0 ]; then
  echo "[Y] Fixes validated locally"
else
  echo "[X] Fixes introduced new issues - resolve before pushing"
fi
```

#### Step 5: Commit and Push Iteration

```bash
# Stage all changes
git add .

# Commit with DCO sign-off
git commit -s -m "fix: address Copilot feedback from PR #<old-pr-number>

- Fix 1: Description
- Fix 2: Description
- Fix 3: Description

Resolves Copilot comments: <comment-links>"

# Push iteration branch
git push -u origin "$ITERATION_BRANCH"
```

#### Step 6: Create New PR and Close Old PR

**RIGOR: PR-002 - Copilot Comments Resolution**

```bash
# Get old PR number
OLD_PR=$(gh pr view --json number -q '.number' 2>/dev/null)

# Create new PR with iteration branch
gh pr create \
  --title "feat: <feature-description> (v2)" \
  --body "$(cat <<'EOF'
## Summary
Supersedes PR #<old-pr-number> with Copilot feedback addressed.

## Changes from Previous PR
- Addressed Copilot comment: <summary of fix 1>
- Addressed Copilot comment: <summary of fix 2>
- Addressed Copilot comment: <summary of fix 3>

## Previous PR
See #<old-pr-number> for original context and acceptance criteria.

## Test Plan
- ✅ All tests passing
- ✅ Copilot suggestions implemented
- ✅ CI pre-flight checks passed

<Include full test plan from original PR>
EOF
)"

# Close old PR with reference to new one
NEW_PR=$(gh pr view --json number -q '.number' 2>/dev/null)
gh pr close "$OLD_PR" --comment "Superseded by PR #${NEW_PR} with Copilot feedback addressed"

echo "Old PR #${OLD_PR} closed, new PR #${NEW_PR} created"
```

#### Step 7: Iterate Until Zero Copilot Comments

**Repeat Phase 6.5 until**:
- Zero unresolved Copilot comments remain, OR
- All remaining comments are documented as "will not fix" with rationale

**Maximum iterations**: If exceeding 5 iterations, escalate to human review to discuss whether Copilot suggestions are appropriate.

#### Phase 6.5 Success

```
✅ Phase 6.5 Complete: Copilot feedback addressed

Iteration: v3
PR URL: https://github.com/owner/repo/pull/125
Previous PRs: #123 (v1, closed), #124 (v2, closed)
Unresolved Copilot comments: 0

Ready for human review!
```

---

## Workflow Complete

After all phases complete successfully, display final summary:

```
================================================================================
VALIDATION WORKFLOW COMPLETE
================================================================================

Task: task-094 - Integration - Enhanced /flow:validate Command
Status: Done ✅

Phase Summary:
✅ Phase 0: Task loaded successfully
✅ Phase 1: All automated tests passed
✅ Phase 2: Agent validation passed (QA + Security)
✅ Phase 3: Documentation updated
✅ Phase 4: All acceptance criteria verified (8/8)
✅ Phase 5: Task marked Done with implementation notes
✅ Phase 6: Pull request created

Pull Request: https://github.com/owner/repo/pull/123

Next steps:
1. Wait for CI/CD pipeline to complete
2. Request code review if needed
3. Merge PR once approved and all checks pass
4. Delete feature branch after merge
================================================================================
```

---

## Error Recovery

If any phase fails, the workflow halts with a clear error message. To recover:

1. **Review the error message** - Identifies which phase failed and why
2. **Fix the issue** - Address the root cause (failing tests, unchecked ACs, etc.)
3. **Re-run the command** - Execute `/flow:validate <task-id>` again
4. **Resume from where it left off** - Workflow is idempotent and handles partial completion

**Example error recovery**:
```bash
# Phase 1 failed due to test failures
[X] Phase 1 Failed: 3 test(s) failed. Fix tests before continuing.

# Developer fixes tests
# Re-run validate command
/flow:validate task-094

# Workflow detects tests now pass and continues from Phase 2
```

---

## Help Text

**Command**: `/flow:validate [task-id]`

**Purpose**: Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

**Arguments**:
- `task-id` (optional): Specific task ID to validate (e.g., `task-094`)
- If not provided: Automatically discovers the single "In Progress" task

**Workflow Phases**:
1. **Phase 0: Task Discovery & Load** - Find and load target task
2. **Phase 1: Automated Testing** - Run tests, linting, type checks
3. **Phase 2: Agent Validation** - Launch QA Guardian and Security Engineer (parallel)
4. **Phase 3: Documentation** - Launch Technical Writer agent
5. **Phase 4: AC Verification** - Verify all acceptance criteria met
6. **Phase 5: Task Completion** - Generate notes and mark task Done
7. **Phase 6: PR Generation** - Create pull request with human approval

**Examples**:

```bash
# Validate specific task
/flow:validate task-094

# Auto-discover in-progress task
/flow:validate
```

**Features**:
- ✅ Phased execution with progress reporting
- ✅ Phase failures halt workflow with clear error messages
- ✅ Re-runnable after fixing issues (handles partial completion)
- ✅ Automated test execution and validation
- ✅ Parallel agent execution for efficiency
- ✅ Systematic AC verification (automated + manual)
- ✅ Comprehensive implementation notes generation
- ✅ PR generation with human approval gate

**Requirements**:
- Task must be in "In Progress" status
- Tests must pass before proceeding
- All acceptance criteria must be verified
- Branch must be pushed to remote before PR creation
- **No merge conflicts with main branch** (rebase and resolve before PR creation)
- GitHub CLI (`gh`) must be installed for PR creation
- **Skipped tests must be documented in PR body with explanations** (category and reason for each)

**Error Recovery**:
If a phase fails, fix the issue and re-run the command. The workflow will resume from where it left off.

**See Also**:
- `/flow:implement` - Implementation workflow
- `/flow:plan` - Planning workflow
- `backlog task` - Task management commands

## Post-Completion: Emit Workflow Event

After successfully completing this command (all validation phases passed, PR created), emit the workflow event:

```bash
flowspec hooks emit validate.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/qa/$FEATURE_ID-qa-report.md \
  -f docs/security/$FEATURE_ID-security-report.md
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, deployment triggers).

## Telemetry: Track Agent Invocations

After validation completes, track the agents that were invoked for analytics (if telemetry is enabled):

```bash
# Track each agent that was invoked during this command (silently, will be no-op if disabled)

# Track the command execution with user's role
flowspec telemetry track-role "$CURRENT_ROLE" --command /flow:validate -q

# QA Guardian agent was invoked in Phase 2:
flowspec telemetry track-agent quality-guardian --command /flow:validate -q

# Security Engineer agent was invoked in Phase 2:
flowspec telemetry track-agent secure-by-design-engineer --command /flow:validate -q

# Technical Writer agent was invoked in Phase 3:
flowspec telemetry track-agent technical-writer --command /flow:validate -q
```

Replace `$CURRENT_ROLE` with the user's current role (dev, pm, qa, etc.).

This enables workflow analytics for understanding agent usage patterns. The tracking is:
- **Opt-in only**: Only recorded if user has enabled telemetry via `flowspec telemetry enable`
- **Privacy-first**: Project names are hashed, no PII collected
- **Fail-safe**: Commands will not fail if telemetry is unavailable
