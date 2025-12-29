---
name: "flow-implement"
description: "Execute implementation using specialized frontend and backend engineer agents with code review."
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
  - label: "Run Validation"
    agent: "flow-validate"
    prompt: "Implementation is complete. Run QA validation, security review, and documentation checks."
    send: false
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command implements features using specialized engineering agents with integrated code review. **Engineers work exclusively from backlog tasks.**

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

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

{{INCLUDE:.claude/partials/flow/_workflow-state.md}}

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
  \{\{INCLUDE:.claude/partials/flow/_rigor-rules.md\}\}

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
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"
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
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"
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
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"
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
TASK_ID="${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo '')}"
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
  if ! echo "$BRANCH" | grep -Eq '^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'; then
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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

### Rule: EXEC-007 - Backlog Accuracy Required
**Severity**: BLOCKING
**Enforcement**: strict

Backlog.md is the **human-readable source of truth** for task status. Every PR MUST update backlog task status to reflect reality. Tasks MUST have both `workflow:Current` and `workflow-next:Next` labels.

**What MUST be accurate**:
- Task status (To Do, In Progress, Done)
- Current workflow state (`workflow:In Implementation`)
- Next workflow state (`workflow-next:Validated`)
- Acceptance criteria completion status

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
if [ -n "$TASK_ID" ]; then
  TASK_OUTPUT=$(backlog task "$TASK_ID" --plain 2>/dev/null)

  # Check workflow state exists
  HAS_CURRENT=$(echo "$TASK_OUTPUT" | grep -q "workflow:" && echo "yes" || echo "no")
  HAS_NEXT=$(echo "$TASK_OUTPUT" | grep -q "workflow-next:" && echo "yes" || echo "no")

  if [ "$HAS_CURRENT" = "no" ]; then
    echo "[X] EXEC-007 VIOLATION: Missing current workflow state for $TASK_ID"
  fi
  if [ "$HAS_NEXT" = "no" ]; then
    echo "[X] EXEC-007 VIOLATION: Missing next workflow state for $TASK_ID"
  fi
fi
```

**Remediation**:
```bash
# Update task with current and next workflow states
backlog task edit <task-id> \
  -l "workflow:In Implementation" \
  -l "workflow-next:Validated" \
  -s "In Progress"

# After completing workflow step
backlog task edit <task-id> \
  -l "workflow:Validated" \
  -l "workflow-next:Deployed"
```

**Workflow State Progression**:
```
Assessed → Specified → Planned → In Implementation → Validated → Deployed
```

**Rationale**: Humans need accurate status at a glance. The backlog is the coordination point between humans and agents.

---

### Rule: EXEC-008 - Beads Agent Sync
**Severity**: BLOCKING
**Enforcement**: strict

Beads (`.beads/issues.jsonl`) is the **agent task tracking system**. It MUST be kept in sync with backlog.md for agent micro-tasks and context preservation.

**When to use Beads vs Backlog**:
- **Backlog.md**: Human-facing tasks, workflow state, acceptance criteria
- **Beads**: Agent micro-tasks, blockers, dependencies, session continuity

**Validation**:
```bash
# Check beads is initialized
if [ ! -d ".beads" ]; then
  echo "[X] EXEC-008 VIOLATION: Beads not initialized"
  echo "Remediation: bd init"
fi

# Check for stale beads (open issues with no recent activity)
if [ -f ".beads/issues.jsonl" ]; then
  OPEN_COUNT=$(bd list --status=open 2>/dev/null | wc -l || echo 0)
  IN_PROGRESS=$(bd list --status=in_progress 2>/dev/null | wc -l || echo 0)
  echo "INFO: EXEC-008: Beads status - Open: $OPEN_COUNT, In Progress: $IN_PROGRESS"
fi
```

**Remediation**:
```bash
# Initialize beads if missing
bd init

# Create agent task linked to backlog
bd create --title="Implement feature X" --type=task --priority=2

# Update status as work progresses
bd update <id> --status=in_progress
bd close <id> --reason="Completed in PR #123"

# Sync with remote at session end
bd sync
```

**Rationale**: Agents need persistent task context across sessions. Beads survives context resets and enables agent handoffs.

---

### Rule: EXEC-009 - Daily Active Work Log
**Severity**: ADVISORY
**Enforcement**: warn

Active work SHOULD be logged daily to `.flowspec/logs/active-work/<date>.jsonl`. This enables session continuity and work visibility.

**Log Format**:
```json
{"timestamp":"2024-12-19T10:30:00Z","task_id":"task-123","beads_id":"beads-456","action":"started","description":"Implementing rigor rules"}
{"timestamp":"2024-12-19T14:30:00Z","task_id":"task-123","beads_id":"beads-456","action":"progress","description":"Added 4 new rules","percent_complete":60}
{"timestamp":"2024-12-19T17:00:00Z","task_id":"task-123","beads_id":"beads-456","action":"completed","description":"PR #978 created"}
```

**Validation**:
```bash
TODAY=$(date +%Y-%m-%d)
LOG_FILE=".flowspec/logs/active-work/${TODAY}.jsonl"

if [ ! -f "$LOG_FILE" ]; then
  echo "WARNING: EXEC-009: No active work log for today: $LOG_FILE"
  echo "Remediation: Create log entry for current work"
fi
```

**Remediation**:
```bash
# Create logs directory if needed
mkdir -p .flowspec/logs/active-work

# Log work start
TODAY=$(date +%Y-%m-%d)
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","task_id":"task-123","action":"started","description":"Starting implementation"}' >> ".flowspec/logs/active-work/${TODAY}.jsonl"

# Log progress
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","task_id":"task-123","action":"progress","description":"Completed step 1","percent_complete":25}' >> ".flowspec/logs/active-work/${TODAY}.jsonl"
```

**Rationale**: Daily logs provide audit trail, enable handoffs, and help with time tracking and retrospectives.

---

### Rule: EXEC-010 - Daily Decision Log
**Severity**: BLOCKING
**Enforcement**: strict

All significant decisions MUST be logged daily to `.flowspec/logs/decisions/<date>.jsonl`. This supplements task-specific decision logs with a daily aggregate view.

**When to log**:
- Technology or library choices
- Architecture decisions
- Trade-off resolutions
- Scope changes
- Rejected approaches

**Log Format**:
```json
{"timestamp":"2024-12-19T10:30:00Z","task_id":"task-123","decision":"Use @import instead of {{INCLUDE}}","rationale":"Claude Code only processes @import in CLAUDE.md","alternatives":["Inline content","Preprocessing hook"],"actor":"@backend-engineer"}
```

**Validation**:
```bash
TODAY=$(date +%Y-%m-%d)
LOG_FILE=".flowspec/logs/decisions/${TODAY}.jsonl"

if [ ! -f "$LOG_FILE" ]; then
  echo "[X] EXEC-010 VIOLATION: No decision log for today: $LOG_FILE"
  echo "Remediation: Log at least one decision for today's work"
else
  ENTRY_COUNT=$(wc -l < "$LOG_FILE" 2>/dev/null || echo 0)
  if [ "$ENTRY_COUNT" -eq 0 ]; then
    echo "[X] EXEC-010 VIOLATION: Decision log exists but is empty"
  else
    echo "[Y] EXEC-010: $ENTRY_COUNT decision(s) logged today"
  fi
fi
```

**Remediation**:
```bash
# Create logs directory if needed
mkdir -p .flowspec/logs/decisions

# Log a decision
TODAY=$(date +%Y-%m-%d)
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","task_id":"task-123","decision":"Description of decision","rationale":"Why this choice was made","alternatives":["Option A","Option B"],"actor":"@backend-engineer"}' >> ".flowspec/logs/decisions/${TODAY}.jsonl"
```

**Relationship to EXEC-003**:
- **EXEC-003**: Task-specific decision log in `memory/decisions/task-XXX.jsonl`
- **EXEC-010**: Daily aggregate decision log in `.flowspec/logs/decisions/<date>.jsonl`
- Both should be kept in sync for comprehensive audit trail

**Rationale**: Daily decision logs enable quick review of what was decided, cross-task pattern recognition, and onboarding context.

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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
  echo "Remediation: git push origin \"$(git branch --show-current)\""
fi
```

**Remediation**:
```bash
# Commit and push all changes
git add .
git commit -s -m "wip: freeze checkpoint - $(date +%Y-%m-%d)"
git push origin "$(git branch --show-current)"
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
git push --force-with-lease origin "$(git branch --show-current)"
```

**Rationale**: Prevents integration delays and merge conflicts during PR merge. PRs with conflicts waste reviewer time.

---

### Rule: VALID-005 - Acceptance Criteria Met
**Severity**: BLOCKING
**Enforcement**: strict

All acceptance criteria MUST be marked complete and verified before PR creation.

**Validation**:
```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
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
git push --force-with-lease origin "$(git branch --show-current)"
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
if echo "$BRANCH" | grep -Eq '\-v[0-9][0-9]*$'; then
  # This is an iteration branch - validate base exists
  # Use [0-9][0-9]* to require at least one digit for consistency
  BASE_BRANCH=$(echo "$BRANCH" | sed 's/-v[0-9][0-9]*$//')
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

# Or calculate next version (POSIX-compliant)
CURRENT=$(git branch --show-current)
# Use sed for portable version extraction (not BASH_REMATCH)
VERSION=$(printf '%s\n' "$CURRENT" | sed -n 's/.*-v\([0-9][0-9]*\)$/\1/p')
if [ -n "$VERSION" ]; then
  NEXT=$((VERSION + 1))
  BASE=$(printf '%s\n' "$CURRENT" | sed 's/-v[0-9][0-9]*$//')
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
\{\{INCLUDE:.claude/partials/flow/_rigor-rules.md\}\}
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


**For /flow:implement**: Required input state is `workflow:Planned`. Output state will be `workflow:In Implementation`.

If the task doesn't have the required workflow state, inform the user:
- If task needs planning first: suggest running `/flow:plan`
- If task needs specification: suggest running `/flow:specify` first

**Proceed to Step 1 ONLY if workflow validation passes.**

### Step 1: Discover Backlog Tasks

**⚠️ CRITICAL: This command REQUIRES existing backlog tasks to work on.**

Discover tasks for implementation:

```bash
# Search for implementation tasks related to this feature
backlog search "$ARGUMENTS" --plain

# List available tasks to work on
backlog task list -s "To Do" --plain

# List any in-progress tasks for context
backlog task list -s "In Progress" --plain
```

**If no relevant tasks are found:**

```
⚠️ No backlog tasks found for: [FEATURE NAME]

This command requires existing backlog tasks with defined acceptance criteria.
Please run /flow:specify first to create implementation tasks, or create
tasks manually using:

  backlog task create "Implement [Feature]" --ac "Criterion 1" --ac "Criterion 2"

Then re-run /flow:implement
```

**If tasks ARE found, proceed to Step 2.**

### Step 2: Discover Related Specifications and ADRs

**⚠️ CRITICAL: Implementation MUST be informed by all relevant design documents.**

Before coding, discover ALL related PRDs, Functional Specs, Technical Specs, and ADRs:

```bash
# Search for PRDs related to this feature
ls -la docs/prd/ 2>/dev/null || echo "No PRDs found"
grep -rl "$ARGUMENTS" docs/prd/ 2>/dev/null || echo "No matching PRDs"

# Search for Functional and Technical Specs
ls -la docs/specs/ 2>/dev/null || echo "No specs found"
grep -rl "$ARGUMENTS" docs/specs/ 2>/dev/null || echo "No matching specs"

# Search for related ADRs (architecture decisions)
ls -la docs/adr/ 2>/dev/null || echo "No ADRs found"
grep -rl "$ARGUMENTS" docs/adr/ 2>/dev/null || echo "No matching ADRs"

# Search backlog task descriptions for spec/ADR references
backlog task list --plain 2>/dev/null | grep -i "prd\|spec\|adr"
```

**Read ALL discovered documents before implementation:**

The artifact progression is:
```
PRD -> Functional Spec -> Technical Spec -> ADR -> Implementation
```

| Document | What It Tells You |
|----------|-------------------|
| **PRD** | What the product must do and why the user cares |
| **Functional Spec** | What behaviors and capabilities are required |
| **Technical Spec** | How to build it (architecture, data, APIs) |
| **ADR** | Why we chose this technical path |

**If key documents are missing:**

```
⚠️ Missing design documents for: [FEATURE NAME]

Found:
- PRD: [[Y]/[N]]
- Functional Spec: [[Y]/[N]]
- Technical Spec: [[Y]/[N]]
- ADRs: [[Y]/[N]]

Recommendation:
- Run /flow:specify to create PRD and Functional Spec
- Run /flow:plan to create Technical Spec and ADRs
- Then re-run /flow:implement

Proceeding without specs may result in:
- Misaligned implementation
- Undefined edge cases
- Inconsistent architecture
- Undocumented decisions
```

**If documents ARE found, read them and proceed to Phase 0.**

### Checkpoint Reminder

> **💡 Safety Tip**: Claude creates checkpoints before each code change. If implementation doesn't work as expected, you can press `Esc Esc` to instantly undo changes, or use `/rewind` for interactive rollback. This is especially useful for:
> - Multi-file refactoring
> - Experimental approaches
> - Complex migrations

### Phase 0: Quality Gate (MANDATORY)

**⚠️ CRITICAL: Spec quality must pass before implementation begins.**

Before starting implementation, you MUST run the quality gate:

```bash
# Run quality gate on spec.md
flowspec gate

# Alternative: Override threshold if needed
flowspec gate --threshold 60

# Emergency bypass (NOT RECOMMENDED - use only with explicit user approval)
flowspec gate --force
```

**Quality Gate Exit Codes:**
- `0` = PASSED - Proceed to Phase 1
- `1` = FAILED - Spec quality below threshold
- `2` = ERROR - Missing spec.md or validation error

**If gate PASSES (exit code 0):**
```
✅ Quality gate passed
Proceeding with implementation...
```

**If gate FAILS (exit code 1):**
```
[X] Quality gate failed: Spec quality is X/100 (minimum: 70)

Recommendations:
  • Add missing section: ## Description
  • Add missing section: ## User Story
  • Reduce vague terms (currently: Y instances)
  • Add measurable acceptance criteria

Action Required:
1. Improve spec quality using recommendations
2. Re-run: flowspec quality .flowspec/spec.md
3. When quality ≥70, re-run: /flow:implement

OR (not recommended without user approval):
  flowspec gate --force
```

**--force Bypass:**
- Only use with explicit user approval
- Warns that bypassing quality checks may lead to unclear requirements
- Logs the bypass decision

**Proceed to Phase 0.1 ONLY if quality gate passes or user explicitly approves --force bypass.**

### Phase 0.1: Rigor Rules Enforcement (MANDATORY)

**⚠️ CRITICAL: Branch naming and worktree conventions MUST be validated before implementation begins.**

These rules enforce consistency and enable automation across the team.

#### Validation: Branch Naming Convention

Branch names MUST follow the pattern: `{hostname}/task-{id}/{slug-description}`

```bash
# Validate branch naming (EXEC-002)
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$BRANCH" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Not on a git branch"
  echo "Fix: Create a branch following the pattern: hostname/task-NNN/slug-description"
  exit 1
fi

if ! echo "$BRANCH" | grep -Eq '^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Branch name must follow format: hostname/task-NNN/slug-description"
  echo "Current branch: $BRANCH"
  echo ""
  echo "Examples of valid branch names:"
  echo "  - macbook-pro/task-543/rigor-rules-integration"
  echo "  - desktop-alice/task-123/user-authentication"
  echo "  - laptop-bob/task-456/api-endpoints"
  echo ""
  echo "Fix: Create a new branch with compliant naming:"
  HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
  # Extract task number if present in current branch, otherwise prompt user
  TASK_NUM=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")
  if [ -z "$TASK_NUM" ]; then
    echo "  # First, identify your task ID from the backlog:"
    echo "  backlog task list --plain"
    echo "  # Then create branch with that task ID:"
    echo "  git checkout -b ${HOSTNAME}/task-<ID>/your-feature-slug"
  else
    echo "  git checkout -b ${HOSTNAME}/${TASK_NUM}/your-feature-slug"
  fi
  exit 1
fi

echo "✅ Branch naming validation passed: $BRANCH"
```

**Why this matters**:
- **Traceability**: Branch name instantly shows which task it implements
- **Conflict Prevention**: Hostname prefix prevents naming collisions in multi-developer teams
- **Automation**: Enables automated task-to-branch linking in CI/CD
- **Consistency**: Team-wide standard reduces cognitive overhead

#### Validation: Git Worktree

Implementation work MUST be done in a git worktree with matching task ID.

```bash
# Validate worktree usage (EXEC-001)
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
BRANCH=$(git branch --show-current 2>/dev/null)
# Use exact path matching to avoid substring false positives
IS_WORKTREE=$(git worktree list 2>/dev/null | awk '{print $1}' | grep -Fxq "$WORKTREE_DIR" && echo "yes" || echo "no")

if [ "$IS_WORKTREE" = "no" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-001): Not in a git worktree"
  echo ""
  echo "Why worktrees matter:"
  echo "  - Enable parallel feature development"
  echo "  - No branch-switching overhead"
  echo "  - Isolate dependencies and state"
  echo ""
  echo "Fix: Create worktree matching your branch:"
  # BRANCH already defined at start of this code block
  WORKTREE_NAME=$(basename "$BRANCH")
  echo "  cd $(git rev-parse --show-toplevel)"
  echo "  git worktree add ../${WORKTREE_NAME} ${BRANCH}"
  echo "  cd ../${WORKTREE_NAME}"
  exit 1
fi

# Check worktree directory name contains task ID (best practice)
WORKTREE_NAME=$(basename "$WORKTREE_DIR")
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "⚠️  WARNING (EXEC-001): Branch does not contain task ID"
  echo "Worktree name should match task ID for clarity"
elif ! echo "$WORKTREE_NAME" | grep -q "$TASK_ID"; then
  echo "⚠️  WARNING (EXEC-001): Worktree name '$WORKTREE_NAME' does not contain task ID '$TASK_ID'"
  echo "Consider renaming worktree directory to match task ID"
else
  echo "✅ Worktree validation passed: $WORKTREE_NAME"
fi
```

**Why this matters**:
- **Parallel Development**: Work on multiple features without branch switching
- **State Isolation**: Each worktree has independent working directory and index
- **Dependency Isolation**: Different virtual environments per worktree
- **Reduced Context Switching**: No git checkout overhead

#### Validation: Backlog Task Linkage

```bash
# Validate backlog task exists (EXEC-004)
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): No task ID in branch name"
  echo "All implementation work must be linked to a backlog task"
  exit 1
fi

backlog task "$TASK_ID" --plain > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): Backlog task not found: $TASK_ID"
  echo ""
  echo "Fix: Create the backlog task first:"
  echo "  backlog task create 'Feature description' \\"
  echo "    --ac 'Acceptance criterion 1' \\"
  echo "    --ac 'Acceptance criterion 2' \\"
  echo "    -l 'backend' \\"
  echo "    --priority high"
  exit 1
fi

echo "✅ Backlog task validation passed: $TASK_ID"
```

**Why this matters**:
- **No Rogue Work**: All coding aligns with planned backlog
- **Prioritization**: Work is tracked and prioritized
- **Context Preservation**: Task contains acceptance criteria and context

**Proceed to Phase 0.5 ONLY if all rigor validations pass.**

### Phase 0.5: Load PRP Context (PRP-First Workflow)

**⚠️ CRITICAL: PRPs (Product Requirements Prompts) provide self-contained context for implementation.**

Before starting implementation, check for a PRP document for the active task:

```bash
# Extract task ID from arguments - handles both task IDs and feature descriptions
INPUT="${ARGUMENTS}"

# If no input provided, show active tasks and prompt
if [ -z "$INPUT" ]; then
  echo "⚠️ No task ID or feature description provided."
  echo "Searching for active 'In Progress' tasks..."
  backlog task list -s "In Progress" --plain | head -5
  echo ""
  echo "Please specify a task ID or feature description:"
  echo "  /flow:implement task-123"
  echo "  /flow:implement \"Add user authentication\""
  exit 1
fi

# Determine if input is already a task ID or needs resolution
if echo "$INPUT" | grep -Eq '^task-[0-9]+$'; then
  TASK_ID="$INPUT"
  echo "✅ Using task ID: $TASK_ID"
else
  # Treat input as a feature description - try to resolve via backlog search
  echo "🔍 '$INPUT' is not a task ID. Searching backlog for matching tasks..."
  RESOLVED_ID=$(backlog search "$INPUT" --plain 2>/dev/null | awk '/^task-[0-9]+/ {print $1; exit}')

  if [ -n "$RESOLVED_ID" ]; then
    TASK_ID="$RESOLVED_ID"
    echo "✅ Resolved feature description to: $TASK_ID"
  else
    echo "❌ Could not resolve a task ID from: \"$INPUT\""
    echo ""
    echo "Active tasks you can choose from:"
    backlog task list -s "In Progress" --plain | head -5
    echo ""
    echo "Please specify a valid task ID:"
    echo "  /flow:implement task-123"
    exit 1
  fi
fi

# Check for PRP file
PRP_PATH="docs/prp/${TASK_ID}.md"

if [ -f "$PRP_PATH" ]; then
  echo "✅ PRP found: $PRP_PATH"
  echo "Loading PRP as primary context..."
else
  echo "⚠️ No PRP found at: $PRP_PATH"
fi
```

**If PRP exists:**

```bash
# Read the PRP file
cat "$PRP_PATH"

# Confirm PRP loaded
echo ""
echo "✅ PRP loaded successfully"
echo ""
echo "The PRP contains:"
echo "  • Feature summary and acceptance criteria"
echo "  • Code files to review"
echo "  • Related documentation"
echo "  • Examples and known gotchas"
echo "  • Validation commands"
echo ""
echo "Proceeding to implementation with full context..."
```

**If PRP missing:**

```
⚠️ No PRP found for task: ${TASK_ID}

A PRP (Product Requirements Prompt) is a self-contained context bundle that includes:
  • All code files to read
  • Related documentation and specs
  • Examples demonstrating patterns
  • Known gotchas and pitfalls
  • Validation commands and success criteria

Without a PRP, you may be missing critical context.

Recommendation:
  1. Generate PRP first: /flow:generate-prp ${TASK_ID}
  2. Review the generated PRP: docs/prp/${TASK_ID}.md
  3. Then re-run: /flow:implement ${TASK_ID}

Continue without PRP? [y/N]
```

**Ask user to confirm if they want to proceed without PRP.** If user says no or doesn't respond, suggest running `/flow:generate-prp` first.

**PRP-First Workflow Benefits**:

| With PRP | Without PRP |
|----------|-------------|
| All context gathered upfront | Must discover context during implementation |
| Known gotchas highlighted | May miss edge cases |
| Clear validation commands | Unclear how to test |
| Focused implementation | May read irrelevant files |
| Faster onboarding for agents | More exploration needed |

**Proceed to Phase 1 ONLY after:**
- PRP is loaded (if available), OR
- User explicitly confirms proceeding without PRP

### Phase 1: Implementation (Parallel Execution)

**IMPORTANT**: Launch applicable engineer agents in parallel for maximum efficiency.

**⚠️ RIGOR RULE (EXEC-003)**: Log all significant decisions during implementation using:

```bash
./scripts/bash/rigor-decision-log.sh \
  --task $TASK_ID \
  --phase execution \
  --decision "What was decided" \
  --rationale "Why this choice" \
  --actor "@<agent-name>" \
  --alternatives "Alternative1,Alternative2"  # Optional
```

**When to log a decision**:
- **Technology choices**: Selected library, framework, or pattern
- **Architecture changes**: Changed data model, API design, or system structure
- **Trade-off resolutions**: Chose performance over simplicity, etc.
- **Deferred work**: Decided to defer optimization, feature, or refactor

**Examples**:
```bash
# Example 1: Library selection
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Use FastAPI for REST API" \
  --rationale "Better async support, OpenAPI generation" \
  --actor "@backend-engineer" \
  --alternatives "Flask,Django"

# Example 2: Architecture decision
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Split validation into separate phase" \
  --rationale "Clearer separation of concerns, easier to test" \
  --actor "@backend-engineer"

# Example 3: Deferred work
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Defer performance optimization to task-600" \
  --rationale "Current performance meets requirements, avoid premature optimization" \
  --actor "@backend-engineer" \
  --related "task-600"
```

#### Frontend Implementation (if UI/mobile components needed)

Use the Task tool to launch a **general-purpose** agent (Frontend Engineer context):

```
# AGENT CONTEXT: Senior Frontend Engineer

You are a Senior Frontend Engineer with deep expertise in React, React Native, modern web standards, and mobile development. You build user interfaces that are performant, accessible, maintainable, and delightful to use.

## Core Expertise
- **Modern React Development**: React 18+ with hooks, concurrent features, server components
- **Mobile Excellence**: React Native for native-quality mobile apps
- **Performance Optimization**: Fast load times, smooth interactions, efficient rendering
- **Accessibility First**: WCAG 2.1 AA compliance, inclusive interfaces
- **Type Safety**: TypeScript for error prevention and code quality

## Key Technologies
- **State Management**: Zustand, Jotai, TanStack Query, Context API
- **Styling**: Tailwind CSS, CSS Modules, Styled Components
- **Performance**: Code splitting, memoization, virtualization, Suspense
- **Testing**: Vitest, React Testing Library, Playwright

# TASK: Implement the frontend for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include architecture, PRD, design specs, API contracts from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @frontend-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @frontend-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **Component Development**
   - Build React/React Native components
   - Implement proper TypeScript types
   - Follow component composition patterns
   - Ensure accessibility (WCAG 2.1 AA)

2. **State Management**
   - Choose appropriate state solution (local, Context, Zustand, TanStack Query)
   - Implement efficient data fetching
   - Handle loading and error states

3. **Styling and Responsiveness**
   - Implement responsive design
   - Use design system/tokens
   - Ensure cross-browser/platform compatibility

4. **Performance Optimization**
   - Code splitting and lazy loading
   - Proper memoization
   - Optimized rendering

5. **Testing**
   - Unit tests for components
   - Integration tests for user flows
   - Accessibility tests

Deliver production-ready frontend code with tests.
```

#### Backend Implementation (if API/services needed)

Use the Task tool to launch a **general-purpose** agent (Backend Engineer context):

```
# AGENT CONTEXT: Senior Backend Engineer

You are a Senior Backend Engineer with deep expertise in Go, TypeScript (Node.js), and Python. You build scalable, reliable, and maintainable backend systems including CLI tools, RESTful APIs, GraphQL services, and middleware.

## Core Expertise
- **API Development**: RESTful, GraphQL, gRPC services
- **CLI Tools**: Command-line interfaces and developer tools
- **Database Design**: Efficient data modeling and query optimization
- **System Architecture**: Scalable, resilient distributed systems
- **Performance**: High-throughput, low-latency services

## Language-Specific Expertise
- **Go**: Concurrency with goroutines, error handling, standard library
- **TypeScript/Node.js**: Async/await, event loop, modern ESM modules
- **Python**: Type hints, asyncio, modern dependency management

## Key Technologies
- **Go**: net/http, Gin, cobra (CLI), pgx (database)
- **TypeScript**: Express, Fastify, Prisma, Zod validation
- **Python**: FastAPI, SQLAlchemy, Pydantic, Click/Typer (CLI)

## Code Hygiene Requirements (MANDATORY)

Before completing ANY implementation, you MUST:

1. **Remove Unused Imports**
   - Run language-specific linter to detect unused imports
   - Delete ALL unused imports before completion
   - This is a blocking requirement - do not proceed with unused imports

2. **Language-Specific Linting**
   - **Python**: Run `ruff check --select F401,F841` (unused imports/variables)
   - **Go**: Run `go vet ./...` and check for unused imports
   - **TypeScript**: Run `tsc --noEmit` and check eslint rules

## Defensive Coding Requirements (MANDATORY)

1. **Input Validation at Boundaries**
   - Validate ALL function inputs at API/service boundaries
   - Never trust external data (API responses, file contents, env vars, user input)
   - Fail fast with clear error messages on invalid input

2. **Type Safety**
   - Use type hints/annotations on ALL public functions
   - Handle None/null/undefined explicitly - never assume values exist
   - Use union types for optional values, not implicit None

3. **Error Handling**
   - Handle all error cases explicitly
   - Provide meaningful error messages with context
   - Log errors with sufficient detail for debugging

## Language-Specific Rules

### Python (CRITICAL - Enforce Strictly)
- **Imports**: Run `ruff check --select F401` before completion
- **Types**: Type hints required on all public functions and methods
- **Validation**: Use Pydantic models or dataclasses for data validation
- **None Handling**: Use `Optional[T]` and explicit None checks
- **Example validation**:
  ```python
  from typing import Any, Dict

  def process_user(user_id: int, data: Dict[str, Any]) -> User:
      if not isinstance(user_id, int) or user_id <= 0:
          raise ValueError(f"Invalid user_id: {user_id}")
      if not data:
          raise ValueError("Data cannot be empty")
      # ... implementation
  ```

### Go
- **Imports**: Compiler enforces no unused imports (will not compile)
- **Errors**: Check ALL errors - never use `_` to ignore errors
- **Validation**: Validate struct fields, use constructor functions
- **Example validation**:
  ```go
  func NewUser(id int, name string) (*User, error) {
      if id <= 0 {
          return nil, fmt.Errorf("invalid id: %d", id)
      }
      if strings.TrimSpace(name) == "" {
          return nil, errors.New("name cannot be empty")
      }
      return &User{ID: id, Name: name}, nil
  }
  ```

### TypeScript
- **Imports**: Enable `noUnusedLocals` in tsconfig.json
- **Types**: Use strict mode, avoid `any` type
- **Validation**: Use Zod, io-ts, or similar for runtime validation
- **Example validation**:
  ```typescript
  const UserSchema = z.object({
    id: z.number().positive(),
    name: z.string().min(1),
  });

  function processUser(input: unknown): User {
    return UserSchema.parse(input); // Throws on invalid input
  }
  ```

# TASK: Implement the backend for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include architecture, PRD, API specs, data models from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @backend-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @backend-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **API Development** (choose applicable)
   - RESTful endpoints with proper HTTP methods
   - GraphQL schema and resolvers
   - gRPC services and protocol buffers
   - CLI commands and interfaces

2. **Business Logic**
   - Implement core feature logic
   - Input validation and sanitization
   - Error handling and logging
   - Transaction management

3. **Database Integration**
   - Data models and migrations
   - Efficient queries with proper indexing
   - Connection pooling
   - Data validation

4. **Security**
   - Authentication and authorization
   - Input validation
   - SQL/NoSQL injection prevention
   - Secure secret management

5. **Testing**
   - Unit tests for business logic
   - Integration tests for APIs
   - Database tests

Choose language: Go, TypeScript/Node.js, or Python based on architecture decisions.

## Pre-Completion Checklist (BLOCKING)

Before marking implementation complete, verify ALL items:

- [ ] **No unused imports** - Run linter, remove ALL unused imports
- [ ] **No unused variables** - Remove or use all declared variables
- [ ] **All inputs validated** - Boundary functions validate their inputs
- [ ] **Edge cases handled** - Empty values, None/null, invalid types
- [ ] **Types annotated** - All public functions have type hints/annotations
- [ ] **Errors handled** - All error paths have explicit handling
- [ ] **Tests pass** - All unit and integration tests pass
- [ ] **Linter passes** - No linting errors or warnings

⚠️ DO NOT proceed if any checklist item is incomplete.

Deliver production-ready backend code with tests.
```

#### AI/ML Implementation (if ML components needed)

Use the Task tool to launch the **ai-ml-engineer** agent:

```
Implement AI/ML components for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include model requirements, data sources, performance targets from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @ai-ml-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @ai-ml-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **Model Development**
   - Training pipeline implementation
   - Feature engineering
   - Model evaluation and validation

2. **MLOps Infrastructure**
   - Experiment tracking (MLflow)
   - Model versioning
   - Training automation

3. **Model Deployment**
   - Inference service implementation
   - Model optimization (quantization, pruning)
   - Scalable serving architecture

4. **Monitoring**
   - Performance metrics
   - Data drift detection
   - Model quality tracking

Deliver production-ready ML system with monitoring.
```

### Phase 2: Code Review (Sequential after implementation)

#### Frontend Code Review

After frontend implementation, use the Task tool to launch a **general-purpose** agent (Frontend Code Reviewer context):

```
# AGENT CONTEXT: Principal Frontend Code Reviewer

You are a Principal Frontend Engineer conducting thorough code reviews for React and React Native applications. Your reviews focus on code quality, performance, accessibility, security, and maintainability.

## Review Focus Areas
1. **Functionality**: Correctness, edge cases, error handling, Hook rules
2. **Performance**: Re-renders, bundle size, code splitting, memoization, Web Vitals
3. **Accessibility**: WCAG 2.1 AA compliance, semantic HTML, keyboard navigation, ARIA
4. **Code Quality**: Readability, TypeScript types, component architecture
5. **Testing**: Coverage, test quality, integration tests
6. **Security**: XSS prevention, input validation, dependency vulnerabilities

## Review Philosophy
- Constructive and educational
- Explain the "why" behind suggestions
- Balance idealism with practical constraints
- Categorize feedback by severity

# TASK: Review the frontend implementation for: [USER INPUT FEATURE]

Code to review:
[PASTE FRONTEND CODE FROM PHASE 1]

## Backlog AC Verification (REQUIRED)

**Your Agent Identity**: @frontend-code-reviewer

Before approving code, you MUST:
1. **Review task ACs**: `backlog task <task-id> --plain`
2. **Verify AC completion matches code**: For each checked AC, confirm the code implements it
3. **Uncheck ACs if not satisfied**: `backlog task edit <task-id> --uncheck-ac <N>`
4. **Add review notes**: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...\n- Suggestion: ...'`

**AC Verification Checklist**:
- [ ] Each checked AC has corresponding code changes
- [ ] Implementation notes accurately describe changes
- [ ] No undocumented functionality added
- [ ] Tests cover AC requirements

Conduct comprehensive review covering:

1. **Functionality**: Correctness, edge cases, error handling
2. **Performance**: Re-renders, bundle size, runtime performance
3. **Accessibility**: WCAG compliance, keyboard navigation, screen readers
4. **Code Quality**: Readability, maintainability, TypeScript types
5. **Testing**: Coverage, test quality
6. **Security**: XSS prevention, input validation

Provide categorized feedback:
- Critical (must fix before merge)
- High (should fix before merge)
- Medium (address soon)
- Low (nice to have)

Include specific, actionable suggestions.
```

#### Backend Code Review

After backend implementation, use the Task tool to launch a **general-purpose** agent (Backend Code Reviewer context):

```
# AGENT CONTEXT: Principal Backend Code Reviewer

You are a Principal Backend Engineer conducting thorough code reviews for Go, TypeScript (Node.js), and Python backend systems. Your reviews focus on code quality, security, performance, scalability, and maintainability.

## Review Focus Areas
1. **Security**: Authentication, authorization, injection prevention, data protection, secrets management
2. **Performance**: Database optimization (N+1 queries, indexes), scalability, resource management
3. **Code Quality**: Error handling, type safety, readability, maintainability
4. **API Design**: RESTful/GraphQL patterns, versioning, error responses
5. **Database**: Schema design, migrations, query efficiency, transactions
6. **Testing**: Coverage, integration tests, edge cases, error scenarios

## Security Priority
- SQL/NoSQL injection prevention
- Input validation and sanitization
- Proper authentication and authorization
- Secure secret management
- Dependency vulnerability scanning

## Code Hygiene Checks (CRITICAL - Must Block Merge if Failed)

### Unused Imports and Variables
- **BLOCK MERGE** if ANY unused imports exist
- **BLOCK MERGE** if ANY unused variables exist
- Run language-specific checks:
  - Python: `ruff check --select F401,F841`
  - Go: `go vet ./...` (compiler enforces)
  - TypeScript: `tsc --noEmit` with `noUnusedLocals`

### Defensive Coding Violations
- **BLOCK MERGE** if boundary functions lack input validation
- **BLOCK MERGE** if None/null not handled explicitly
- **BLOCK MERGE** if public functions lack type annotations (Python especially)
- Check for:
  - Functions accepting external data without validation
  - Missing type hints on public APIs
  - Implicit None handling (using value without checking)
  - Ignored errors (especially Go's `_` pattern)

# TASK: Review the backend implementation for: [USER INPUT FEATURE]

Code to review:
[PASTE BACKEND CODE FROM PHASE 1]

## Backlog AC Verification (REQUIRED)

**Your Agent Identity**: @backend-code-reviewer

Before approving code, you MUST:
1. **Review task ACs**: `backlog task <task-id> --plain`
2. **Verify AC completion matches code**: For each checked AC, confirm the code implements it
3. **Uncheck ACs if not satisfied**: `backlog task edit <task-id> --uncheck-ac <N>`
4. **Add review notes**: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...\n- Suggestion: ...'`

**AC Verification Checklist**:
- [ ] Each checked AC has corresponding code changes
- [ ] Implementation notes accurately describe changes
- [ ] No undocumented functionality added
- [ ] Tests cover AC requirements
- [ ] Security requirements met

Conduct comprehensive review covering:

1. **Code Hygiene (BLOCKING)**:
   - Unused imports - MUST be zero
   - Unused variables - MUST be zero
   - Run: `ruff check --select F401,F841` (Python), `go vet` (Go), `tsc --noEmit` (TS)

2. **Defensive Coding (BLOCKING)**:
   - Input validation at boundaries - REQUIRED
   - Type annotations on public functions - REQUIRED
   - Explicit None/null handling - REQUIRED
   - No ignored errors - REQUIRED

3. **Security**: Authentication, authorization, injection prevention, secrets
4. **Performance**: Query optimization, scalability, resource management
5. **Code Quality**: Readability, error handling, type safety
6. **API Design**: RESTful/GraphQL patterns, error responses
7. **Database**: Schema design, migrations, query efficiency
8. **Testing**: Coverage, integration tests, edge cases

Provide categorized feedback:
- **Critical (BLOCK MERGE)**: Unused imports, missing validation, type safety violations
- High (fix before merge)
- Medium (address soon)
- Low (nice to have)

⚠️ ALWAYS flag as Critical:
- Any unused import or variable
- Missing input validation on boundary functions
- Missing type hints on public Python functions
- Ignored errors in Go code
- Missing runtime validation for external data

Include specific, actionable suggestions with examples.
```

### Phase 3: Iteration and Integration

1. **Address Review Feedback**
   - Fix critical and high-priority issues
   - Re-review if significant changes made

2. **Integration Testing**
   - Verify frontend-backend integration
   - Test complete user workflows
   - Validate API contracts

3. **Documentation**
   - Update API documentation
   - Add code comments for complex logic
   - Document configuration and deployment

### Phase 4: Pre-PR Validation (MANDATORY - NO EXCEPTIONS)

**⚠️ CRITICAL: Before creating any PR, you MUST run and pass ALL validation checks.**

This is a blocking gate enforced by rigor rules (VALID-001 through VALID-007). Do NOT create a PR until ALL checks pass.

#### Step 1: Verify Decision Logging (VALID-001 - BLOCKING)

All significant decisions MUST be logged before PR creation.

```bash
# Check decision log exists and has entries (VALID-001)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
DECISION_LOG="memory/decisions/${TASK_ID}.jsonl"

if [ ! -f "$DECISION_LOG" ]; then
  echo "[X] RIGOR VIOLATION (VALID-001): No decision log found: $DECISION_LOG"
  echo ""
  echo "You must log at least one decision. Examples of decisions to log:"
  echo "  - Technology choices (library, framework, pattern selection)"
  echo "  - Architecture changes"
  echo "  - Trade-off resolutions"
  echo "  - Deferred work decisions"
  echo ""
  echo "Fix: Log decisions using:"
  echo "  ./scripts/bash/rigor-decision-log.sh \\"
  echo "    --task ${TASK_ID} \\"
  echo "    --phase execution \\"
  echo "    --decision 'What was decided' \\"
  echo "    --rationale 'Why this choice' \\"
  echo "    --actor '@backend-engineer'"
  exit 1
fi

ENTRY_COUNT=$(wc -l < "$DECISION_LOG" 2>/dev/null || echo 0)
if [ "$ENTRY_COUNT" -eq 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-001): Decision log is empty"
  exit 1
fi

echo "✅ Decision traceability passed: $ENTRY_COUNT decisions logged"
```

#### Step 2: Run Lint Check (VALID-002 - BLOCKING)

```bash
# Python projects (VALID-002)
if [ -f "pyproject.toml" ]; then
  echo "Running lint check..."
  uv run ruff check .
  LINT_STATUS=$?

  if [ $LINT_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): Lint check failed"
    echo "Fix: uv run ruff check --fix ."
    exit 1
  fi

  echo "✅ Lint check passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  go vet ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): go vet failed"
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  npm run lint
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): npm lint failed"
    exit 1
  fi
fi
```

**MUST pass with ZERO errors.** Fix all linting issues before proceeding.

#### Step 3: Run SAST Check (VALID-002 - BLOCKING)

```bash
# Python SAST check (VALID-002)
if [ -f "pyproject.toml" ]; then
  echo "Running SAST check..."
  if command -v bandit >/dev/null 2>&1; then
    uv run bandit -r src/ -ll
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-002): SAST check failed"
      echo "Review and fix security findings"
      exit 1
    fi
    echo "✅ SAST check passed"
  else
    echo "⚠️  WARNING: bandit not installed - skipping SAST"
  fi
fi
```

#### Step 4: Verify Coding Standards (VALID-003 - BLOCKING)

```bash
# Check for unused imports and variables (VALID-003)
if [ -f "pyproject.toml" ]; then
  echo "Checking coding standards compliance..."
  uv run ruff check --select F401,F841 .
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): Unused imports or variables detected"
    echo "Fix: uv run ruff check --select F401,F841 --fix ."
    exit 1
  fi
  echo "✅ Coding standards check passed"
fi

# Go - compiler enforces
if [ -f "go.mod" ]; then
  go build ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): Build failed"
    exit 1
  fi
fi

# TypeScript
if [ -f "tsconfig.json" ]; then
  npx tsc --noEmit
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): TypeScript check failed"
    exit 1
  fi
fi
```

**MUST have ZERO unused imports or variables.**

#### Step 5: Run Test Suite (VALID-007 - BLOCKING)

```bash
# Python projects (VALID-007)
if [ -f "pyproject.toml" ]; then
  echo "Running test suite..."
  uv run pytest tests/ -x -q
  TEST_STATUS=$?

  if [ $TEST_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    echo "Fix failing tests before creating PR"
    exit 1
  fi

  echo "✅ Test suite passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  go test ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  npm test
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    exit 1
  fi
fi
```

**MUST pass with ZERO failures.** Fix all failing tests before proceeding.

#### Step 6: Format Code (VALID-007 - BLOCKING)

```bash
# Python projects
if [ -f "pyproject.toml" ]; then
  echo "Checking code formatting..."
  uv run ruff format --check .
  FORMAT_STATUS=$?

  if [ $FORMAT_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
    echo "Fix: uv run ruff format ."
    exit 1
  fi

  echo "✅ Code formatting check passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  UNFORMATTED_FILES="$(gofmt -l .)"
  if [ -n "$UNFORMATTED_FILES" ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
    echo "The following files need formatting:"
    echo "$UNFORMATTED_FILES"
    echo "Fix: gofmt -w ."
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  if grep -q '"format:check"' package.json; then
    # Use format:check if available
    npm run format:check
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
      echo "Fix: npm run format"
      exit 1
    fi
  elif command -v prettier >/dev/null 2>&1; then
    # Fall back to prettier --check if available
    prettier --check . 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
      echo "Fix: prettier --write ."
      exit 1
    fi
  fi
fi
```

#### Step 7: Verify Rebase Status (VALID-004 - BLOCKING)

```bash
# Check branch is rebased from main (VALID-004)
echo "Checking rebase status..."
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)

if [ "$BEHIND" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-004): Branch is $BEHIND commits behind main"
  echo ""
  echo "Fix: Rebase from main:"
  echo "  git fetch origin main"
  echo "  git rebase origin/main"
  echo "  # Resolve conflicts if any"
  echo "  git push --force-with-lease origin $(git branch --show-current)"
  exit 1
fi

echo "✅ Rebase status check passed"
```

#### Step 8: Verify Acceptance Criteria (VALID-005 - BLOCKING)

```bash
# Check all ACs are complete (VALID-005)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")

if [ -n "$TASK_ID" ]; then
  echo "Verifying acceptance criteria..."
  INCOMPLETE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -c "^\[ \]" || echo 0)

  if [ "$INCOMPLETE" -gt 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-005): $INCOMPLETE incomplete acceptance criteria"
    backlog task "$TASK_ID" --plain | grep "^\[ \]"
    echo ""
    echo "Fix: Complete all ACs or document why they cannot be completed"
    echo "  backlog task edit ${TASK_ID} --check-ac <N>"
    exit 1
  fi

  echo "✅ All acceptance criteria met"
fi
```

#### Step 9: Verify Task Status (VALID-006 - BLOCKING)

```bash
# Verify task status is current (VALID-006)
# Extract TASK_ID from branch (each code block is independent in markdown)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")

if [ -n "$TASK_ID" ]; then
  echo "Verifying task status..."
  # Extract full status (handles multi-word statuses like "In Progress")
  STATUS=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "Status:" | head -1 | sed 's/^Status:[[:space:]]*//')

  if [ "$STATUS" != "In Progress" ]; then
    echo "⚠️  WARNING (VALID-006): Task status may be stale: $STATUS"
    echo "Update task status before PR:"
    echo "  backlog task edit ${TASK_ID} -s 'In Progress'"
  else
    echo "✅ Task status current"
  fi
fi
```

#### Validation Checklist (ALL REQUIRED)

Before creating the PR, verify ALL of these:

- [ ] **VALID-001**: Decision log exists with entries
- [ ] **VALID-002**: Lint check passes (`ruff check .`)
- [ ] **VALID-002**: SAST check passes (if bandit installed)
- [ ] **VALID-003**: No unused imports (`ruff check --select F401`)
- [ ] **VALID-003**: No unused variables (`ruff check --select F841`)
- [ ] **VALID-007**: Test suite passes (`pytest tests/ -x -q`)
- [ ] **VALID-007**: Code is formatted (`ruff format --check .`)
- [ ] **VALID-004**: Branch rebased from main (zero commits behind)
- [ ] **VALID-005**: All acceptance criteria are marked complete
- [ ] **VALID-006**: Task status reflects current state
- [ ] **PR-001**: All commits have DCO sign-off

**⚠️ DO NOT proceed to create a PR if ANY checklist item is incomplete.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

#### Step 10: Verify DCO Sign-off (PR-001 - BLOCKING)

```bash
# Check all commits have DCO sign-off (PR-001)
echo "Checking DCO sign-off..."
# POSIX-compliant iteration over commit hashes (avoids bash-specific process substitution)
UNSIGNED_COMMITS=""
for hash in $(git log origin/main..HEAD --format='%h' 2>/dev/null); do
  if ! git log -1 --format='%B' "$hash" 2>/dev/null | grep -q "Signed-off-by:"; then
    UNSIGNED_COMMITS="$UNSIGNED_COMMITS $hash"
  fi
done
UNSIGNED_COUNT=$(echo "$UNSIGNED_COMMITS" | wc -w)

if [ "$UNSIGNED_COUNT" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (PR-001): $UNSIGNED_COUNT commits missing DCO sign-off"
  echo ""
  echo "Fix: Add sign-off to all commits:"
  echo "  git rebase origin/main --exec 'git commit --amend --no-edit -s'"
  echo "  git push --force-with-lease origin $(git branch --show-current)"
  exit 1
fi

echo "✅ DCO sign-off check passed"
```

#### Step 11: Create PR (Only After All Checks Pass)

Once all validation passes:

```bash
# Commit changes with DCO sign-off
git add .
git commit -s -m "feat(scope): description"

# Push and create PR
git push origin <branch-name>
gh pr create --title "feat: description" --body "..."
```

### Deliverables (ALL THREE REQUIRED)

Implementation is **code + documents + tests**. All three are mandatory deliverables.

#### 1. Production Code
- Fully implemented, reviewed source code
- All acceptance criteria satisfied
- Code review feedback addressed
- Pre-PR validation passing (lint, format, tests)

#### 2. Key Documents
- Updated/created API documentation
- Code comments for complex logic
- Configuration and deployment docs
- Any new ADRs for implementation decisions

#### 3. Complete Tests
- Unit tests for all new functions/methods
- Integration tests for API endpoints
- Edge case coverage (empty inputs, errors, boundaries)
- Test coverage meeting project minimum (typically 80%)

**Implementation is NOT complete until all three are delivered.**

| Deliverable | Verification |
|-------------|--------------|
| Code | PR passes CI, code review approved |
| Documents | API docs updated, comments added |
| Tests | `pytest`/`go test`/`npm test` passes, coverage met |

## Post-Completion: Emit Workflow Event

After successfully completing this command (implementation done, reviews passed, pre-PR validation complete), emit the workflow event:

```bash
flowspec hooks emit implement.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f src/$FEATURE_ID/
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., running tests, quality gates, notifications).

## Telemetry: Track Agent Invocations

After implementation completes, track the agents that were invoked for analytics (if telemetry is enabled):

```bash
# Track each agent that was invoked during this command (silently, will be no-op if disabled)

# Track the command execution
flowspec telemetry track-role "$CURRENT_ROLE" --command /flow:implement -q

# If frontend work was done:
flowspec telemetry track-agent frontend-engineer --command /flow:implement -q

# If backend work was done:
flowspec telemetry track-agent backend-engineer --command /flow:implement -q

# If AI/ML work was done:
flowspec telemetry track-agent ai-ml-engineer --command /flow:implement -q

# If code reviews were performed:
flowspec telemetry track-agent frontend-code-reviewer --command /flow:implement -q
flowspec telemetry track-agent backend-code-reviewer --command /flow:implement -q
```

Replace `$CURRENT_ROLE` with the user's current role (dev, pm, qa, etc.).

This enables workflow analytics for understanding agent usage patterns. The tracking is:
- **Opt-in only**: Only recorded if user has enabled telemetry via `flowspec telemetry enable`
- **Privacy-first**: Project names are hashed, no PII collected
- **Fail-safe**: Commands will not fail if telemetry is unavailable
