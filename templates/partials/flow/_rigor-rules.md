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
| (deployment) | PR (post-merge) |

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
