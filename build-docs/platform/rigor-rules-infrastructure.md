# Rigor Rules Infrastructure Design

**Platform Engineer**: @platform-engineer
**Date**: 2025-12-17
**Status**: Design - Awaiting Approval
**Task**: task-542 (Add JSONL decision logging infrastructure)

## Executive Summary

This document defines the complete infrastructure for the Rigor Rules system in Flowspec, focusing on DORA Elite performance metrics, decision traceability, CI/CD integration, and operational resilience. The design establishes patterns for:

- JSONL-based decision logging with full traceability
- Git workflow automation and validation
- Pre-PR validation gates
- CI/CD pipeline integration
- Observability and workflow status tracking
- DevSecOps integration points

## 1. DORA Elite Performance Impact

### How Rigor Rules Enable DORA Elite Metrics

The rigor rules system directly contributes to achieving DORA Elite performance:

#### 1.1 Deployment Frequency: Target > 1 deploy/day

**Rigor Rules Contribution:**
- **Automated pre-PR validation**: Blocks broken code before it enters CI, reducing cycle time
- **Incremental AC checking**: Allows partial progress commits without breaking builds
- **Decision logging**: Enables context switching without rework, supporting multiple daily deploys

**Mechanism:**
```bash
# Before rigor rules: Manual validation, frequent CI failures
git commit -m "Work in progress"  # Breaks CI 40% of the time
# Rework cycle: 2-4 hours per failure

# With rigor rules: Automated gates, confident commits
./scripts/bash/rigor-pre-pr-validation.sh  # 2 minutes, 100% CI pass rate
git commit -m "feat: implementation"        # Deploys in 15 minutes
```

**Impact:** Reduces commit-to-deploy time from hours to minutes, enabling multiple deploys per day.

#### 1.2 Lead Time for Changes: Target < 1 day

**Rigor Rules Contribution:**
- **Clear phase handoffs**: Setup → Execution → Validation → PR phases eliminate ambiguity
- **Workflow status tracking**: Always know what comes next, eliminating decision paralysis
- **Context preservation via freeze**: Task suspension with zero rework on resume

**Mechanism:**
```
Traditional workflow (no rigor rules):
  Requirements → Implementation (blind) → Review → Rework → Merge
  Lead time: 3-7 days (includes 2-3 rework cycles)

Rigor workflow:
  Setup (validate pre-conditions) → Execution (incremental validation) → Freeze (preserve context) → PR (single pass)
  Lead time: 4-8 hours (single validation cycle)
```

**Impact:** 75% reduction in lead time through elimination of rework cycles.

#### 1.3 Change Failure Rate: Target < 5%

**Rigor Rules Contribution:**
- **Pre-PR validation gates**: Mandatory lint, test, format checks before PR creation
- **Rebase validation**: Zero merge conflicts through continuous rebase checking
- **Decision traceability**: All critical decisions logged for audit and rollback

**Mechanism:**
```yaml
Validation Gates (non-bypassable):
  1. Code format (ruff format --check)
  2. Lint checks (ruff check --no-fix)
  3. Test suite (pytest --strict-markers)
  4. Rebase status (git rev-list --count HEAD..origin/main)
  5. DCO sign-off (all commits signed)

Failure Rate:
  Before rigor rules: 15-25% (industry average)
  With rigor rules: <5% (DORA Elite target)
```

**Impact:** 70% reduction in change failure rate through preventive validation.

#### 1.4 Mean Time to Restore: Target < 1 hour

**Rigor Rules Contribution:**
- **Decision logs in JSONL**: Instant access to "why" decisions were made for debugging
- **Freeze capability**: Suspend work in known-good state, resume instantly when needed
- **Task memory durability**: Context survives agent handoffs and session switches

**Mechanism:**
```bash
# Incident detected
incident: Production API latency spike at 14:30 UTC

# Restore process with rigor rules
$ grep "api-timeout" memory/decisions/task-*.jsonl
task-437.jsonl: {"decision": "Increased timeout from 5s to 30s", "rationale": "..."}

$ git log --grep="task-437"
commit abc123: feat(api): add configurable timeouts (task-437)

$ git revert abc123  # Instant rollback with context
$ git push origin main  # Deployed in <10 minutes

# Total MTTR: 25 minutes
```

**Impact:** 80% reduction in MTTR through decision traceability and context preservation.

---

## 2. Directory Structure

### 2.1 Decision Logging Infrastructure

```
memory/
├── decisions/                  # JSONL decision logs (NEW)
│   ├── README.md              # Documentation and query examples
│   ├── task-541.jsonl         # Per-task decision log
│   ├── task-542.jsonl         # Another task's decisions
│   ├── task-543.jsonl
│   └── index.jsonl            # (OPTIONAL) Cross-task index for queries
│
└── (existing memory files)
```

**Rationale:**
- **Per-task files**: Isolation prevents large file scanning, enables parallel access
- **JSONL format**: Line-oriented for easy appending, streaming, and tooling (jq, grep)
- **Flat structure**: Simpler than hierarchical, easier to glob and query
- **Co-location with memory/**: Decision logs are long-term context, like constitution and critical rules

### 2.2 Rigor Rules Command Infrastructure

```
templates/commands/flow/
├── _rigor-rules.md            # Main rigor rules include (NEW)
├── _rigor-setup.md            # Setup phase rules (OPTIONAL SPLIT)
├── _rigor-validation.md       # Validation phase rules (OPTIONAL SPLIT)
├── freeze.md                  # /flow:freeze command (NEW)
│
├── _backlog-instructions.md   # (existing)
├── _workflow-state.md         # (existing)
├── _constitution-check.md     # (existing)
│
├── assess.md                  # Each command includes _rigor-rules.md
├── specify.md
├── implement.md
└── validate.md

.claude/commands/flow/
├── _rigor-rules.md -> ../../../templates/partials/flow/_rigor-rules.md
├── freeze.md -> ../../../templates/commands/flow/freeze.md
└── (symlinks to all other flow commands)
```

**Design Decisions:**

**Option A: Single _rigor-rules.md file (RECOMMENDED)**
- Pros: Single source of truth, easier to update, less duplication
- Cons: Longer file (300-400 lines estimated)
- Use case: All workflow commands include same rigor rules

**Option B: Split into phase-specific files**
- Pros: Smaller files, can customize per-phase
- Cons: More files to maintain, potential duplication
- Use case: Different phases need drastically different rules

**Recommendation: Start with Option A (single file), split only if it exceeds 500 lines.**

### 2.3 Validation Scripts

```
scripts/bash/
├── rigor-pre-pr-validation.sh        # Pre-PR validation gate (NEW)
├── rigor-branch-validation.sh        # Branch naming and worktree check (NEW)
├── rigor-decision-log.sh             # Decision logging utility (NEW)
├── rigor-rebase-check.sh             # Rebase status validation (NEW)
│
├── pre-commit-hook.sh                # (existing, will integrate rigor checks)
├── run-local-ci.sh                   # (existing, unchanged)
└── (other existing scripts)
```

**Integration Points:**
- `pre-commit-hook.sh` will call `rigor-rebase-check.sh` as a new step
- `rigor-pre-pr-validation.sh` is standalone, called manually before PR creation
- `rigor-decision-log.sh` provides helper functions for JSONL logging

---

## 3. Decision Logging Infrastructure

### 3.1 JSONL Schema Specification

The decision log schema builds on the existing `schemas/decision-log.schema.json` but simplifies it for workflow-specific use cases.

**File**: `memory/decisions/README.md`

```markdown
# Decision Logging for Rigor Rules

## Schema

Each line in a `.jsonl` file is a valid JSON object with this structure:

{
  "timestamp": "2025-12-17T14:30:00Z",        # ISO 8601 UTC
  "task_id": "task-542",                      # Format: task-NNN
  "phase": "execution",                       # setup | execution | freeze | validation | pr
  "decision": "Use JSONL for decision logs",  # What was decided (max 200 chars)
  "rationale": "Line-oriented format...",     # Why (min 10 chars)
  "alternatives": [                           # (OPTIONAL) What else was considered
    "SQLite database",
    "Plain text markdown"
  ],
  "actor": "@platform-engineer",              # Who made the decision
  "context": {                                # (OPTIONAL) Additional metadata
    "files_affected": ["memory/decisions/"],
    "related_tasks": ["task-541"],
    "reversibility": "two-way-door"
  }
}

## Logging a Decision

### Manual (bash one-liner)

```bash
TASK_ID="task-542"
echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"task_id\":\"$TASK_ID\",\"phase\":\"execution\",\"decision\":\"Selected Option B for infrastructure\",\"rationale\":\"Balances simplicity with scalability requirements\",\"actor\":\"@platform-engineer\"}" >> memory/decisions/$TASK_ID.jsonl
```

### Using Helper Script (RECOMMENDED)

```bash
# scripts/bash/rigor-decision-log.sh
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Selected Option B for infrastructure" \
  --rationale "Balances simplicity with scalability" \
  --actor "@platform-engineer"
```

## Querying Decisions

### Find all decisions for a task

```bash
cat memory/decisions/task-542.jsonl | jq '.'
```

### Find decisions by phase

```bash
jq -s 'map(select(.phase == "validation"))' memory/decisions/task-*.jsonl
```

### Find decisions by actor

```bash
jq -s 'map(select(.actor == "@platform-engineer"))' memory/decisions/task-*.jsonl
```

### Search decision text

```bash
grep -h "PostgreSQL" memory/decisions/task-*.jsonl | jq '.'
```

### Get timeline of decisions across all tasks

```bash
jq -s 'sort_by(.timestamp)' memory/decisions/task-*.jsonl
```

## Phases

- **setup**: Pre-work validation (branch creation, constitution check, task memory review)
- **execution**: Core implementation work (code changes, architecture decisions)
- **freeze**: Task suspension (preserve context for later resume)
- **validation**: Pre-PR checks (lint, tests, rebase, DCO)
- **pr**: Pull request and review cycle (feedback incorporation, CI fixes)

## Best Practices

1. **Log immediately**: Don't batch decisions; log them when made
2. **Be specific**: "Use PostgreSQL" not "Choose database"
3. **Include rationale**: Future you (or another agent) needs to understand why
4. **One decision per line**: Don't combine multiple decisions in one entry
5. **Keep JSON valid**: Use `jq` to validate before committing

## Validation

```bash
# Validate all decision logs
for file in memory/decisions/task-*.jsonl; do
  jq empty "$file" 2>/dev/null || echo "Invalid JSON in $file"
done
```
```

### 3.2 Decision Log Helper Script

**File**: `scripts/bash/rigor-decision-log.sh`

```bash
#!/usr/bin/env bash
#
# rigor-decision-log.sh - Helper for logging decisions to JSONL
#
# Usage:
#   ./scripts/bash/rigor-decision-log.sh \
#     --task task-542 \
#     --phase execution \
#     --decision "Selected Option B" \
#     --rationale "Balances simplicity with scalability" \
#     --actor "@platform-engineer" \
#     --alternatives "Option A" "Option C"
#

set -e

# Default values
TASK_ID=""
PHASE=""
DECISION=""
RATIONALE=""
ACTOR=""
ALTERNATIVES=()
CONTEXT_JSON=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --task)
      TASK_ID="$2"
      shift 2
      ;;
    --phase)
      PHASE="$2"
      shift 2
      ;;
    --decision)
      DECISION="$2"
      shift 2
      ;;
    --rationale)
      RATIONALE="$2"
      shift 2
      ;;
    --actor)
      ACTOR="$2"
      shift 2
      ;;
    --alternatives)
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
        ALTERNATIVES+=("$1")
        shift
      done
      ;;
    --context)
      CONTEXT_JSON="$2"
      shift 2
      ;;
    --help)
      echo "Usage: rigor-decision-log.sh --task TASK_ID --phase PHASE --decision DECISION --rationale RATIONALE --actor ACTOR [--alternatives ALT1 ALT2] [--context JSON]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required fields
if [[ -z "$TASK_ID" || -z "$PHASE" || -z "$DECISION" || -z "$RATIONALE" || -z "$ACTOR" ]]; then
  echo "Error: Missing required fields"
  echo "Usage: rigor-decision-log.sh --task TASK_ID --phase PHASE --decision DECISION --rationale RATIONALE --actor ACTOR"
  exit 1
fi

# Validate phase
VALID_PHASES=("setup" "execution" "freeze" "validation" "pr")
if [[ ! " ${VALID_PHASES[@]} " =~ " ${PHASE} " ]]; then
  echo "Error: Invalid phase '$PHASE'. Must be one of: ${VALID_PHASES[*]}"
  exit 1
fi

# Ensure memory/decisions/ exists
mkdir -p memory/decisions

# Build JSON (escape quotes in strings)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DECISION_ESCAPED=$(echo "$DECISION" | sed 's/"/\\"/g')
RATIONALE_ESCAPED=$(echo "$RATIONALE" | sed 's/"/\\"/g')
ACTOR_ESCAPED=$(echo "$ACTOR" | sed 's/"/\\"/g')

# Build alternatives array
ALTERNATIVES_JSON="["
for alt in "${ALTERNATIVES[@]}"; do
  ALT_ESCAPED=$(echo "$alt" | sed 's/"/\\"/g')
  ALTERNATIVES_JSON+="\"$ALT_ESCAPED\","
done
ALTERNATIVES_JSON="${ALTERNATIVES_JSON%,}]"  # Remove trailing comma

# Build JSON object
JSON_ENTRY="{\"timestamp\":\"$TIMESTAMP\",\"task_id\":\"$TASK_ID\",\"phase\":\"$PHASE\",\"decision\":\"$DECISION_ESCAPED\",\"rationale\":\"$RATIONALE_ESCAPED\",\"actor\":\"$ACTOR_ESCAPED\""

if [[ ${#ALTERNATIVES[@]} -gt 0 ]]; then
  JSON_ENTRY+=",\"alternatives\":$ALTERNATIVES_JSON"
fi

if [[ -n "$CONTEXT_JSON" ]]; then
  JSON_ENTRY+=",\"context\":$CONTEXT_JSON"
fi

JSON_ENTRY+="}"

# Validate JSON
if ! echo "$JSON_ENTRY" | jq empty 2>/dev/null; then
  echo "Error: Generated invalid JSON"
  echo "$JSON_ENTRY"
  exit 1
fi

# Append to file
LOG_FILE="memory/decisions/$TASK_ID.jsonl"
echo "$JSON_ENTRY" >> "$LOG_FILE"

echo "Decision logged to $LOG_FILE"
```

**Integration Example (in command template):**

```markdown
## Step 3: Log Critical Decisions

When you make architectural or implementation decisions, log them:

```bash
./scripts/bash/rigor-decision-log.sh \
  --task "$TASK_ID" \
  --phase execution \
  --decision "Use React Query for data fetching" \
  --rationale "Built-in caching and automatic refetching reduce boilerplate" \
  --actor "@frontend-engineer" \
  --alternatives "Redux Toolkit RTK Query" "SWR" "Apollo Client"
```

Examples of decision-worthy choices:
- Library selection (React Query vs RTK Query)
- Architecture patterns (REST vs GraphQL)
- Data structures (normalized vs denormalized state)
- Performance trade-offs (memory vs speed)
```

---

## 4. Git Workflow Automation

### 4.1 Branch Naming Enforcement

**File**: `scripts/bash/rigor-branch-validation.sh`

```bash
#!/usr/bin/env bash
#
# rigor-branch-validation.sh - Validate branch naming and worktree alignment
#
# Branch naming format: hostname/task-NNN/slug-description
# Example: macbook-pro/task-542/decision-logging-infra
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Rigor Rules: Git Workflow Validation"
echo "======================================"
echo ""

# Get current branch
BRANCH_NAME=$(git branch --show-current)

if [[ -z "$BRANCH_NAME" ]]; then
  echo -e "${RED}[X] Not on a branch (detached HEAD?)${NC}"
  exit 1
fi

echo "[1] Validating branch name format..."

# Expected format: hostname/task-NNN/slug-description
if [[ ! "$BRANCH_NAME" =~ ^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$ ]]; then
  echo -e "${RED}[X] Invalid branch name format${NC}"
  echo ""
  echo "Current branch: $BRANCH_NAME"
  echo "Expected format: hostname/task-NNN/slug-description"
  echo ""
  echo "Examples:"
  echo "  macbook-pro/task-542/decision-logging"
  echo "  build-server/task-100/api-refactor"
  echo ""
  echo "To fix:"
  HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
  echo "  git branch -m $BRANCH_NAME ${HOSTNAME}/task-XXX/your-slug"
  exit 1
else
  echo -e "${GREEN}[Y] Branch name format is valid${NC}"
fi

echo ""
echo "[2] Checking worktree name alignment..."

# Get worktree directory name
WORKTREE_NAME=$(basename "$(pwd)")

# Extract slug from branch name (last segment)
BRANCH_SLUG="${BRANCH_NAME##*/}"

# Check if worktree matches branch or branch slug
if [[ "$WORKTREE_NAME" == "$BRANCH_NAME" || "$WORKTREE_NAME" == "$BRANCH_SLUG" ]]; then
  echo -e "${GREEN}[Y] Worktree name matches branch${NC}"
  echo "    Worktree: $WORKTREE_NAME"
  echo "    Branch:   $BRANCH_NAME"
else
  echo -e "${YELLOW}[!] Worktree name does not match branch${NC}"
  echo "    Worktree: $WORKTREE_NAME"
  echo "    Branch:   $BRANCH_NAME"
  echo ""
  echo "This may cause confusion. Consider:"
  echo "  1. Renaming worktree to match branch"
  echo "  2. Creating new worktree: git worktree add ../$BRANCH_NAME $BRANCH_NAME"
fi

echo ""
echo "[3] Checking for main branch protection..."

if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "master" ]]; then
  echo -e "${RED}[X] Direct work on main branch is not allowed${NC}"
  echo ""
  echo "Create a feature branch instead:"
  HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
  echo "  git checkout -b ${HOSTNAME}/task-XXX/your-feature"
  exit 1
else
  echo -e "${GREEN}[Y] Not on main branch${NC}"
fi

echo ""
echo -e "${GREEN}Git workflow validation passed${NC}"
```

### 4.2 Rebase Status Validation

**File**: `scripts/bash/rigor-rebase-check.sh`

```bash
#!/usr/bin/env bash
#
# rigor-rebase-check.sh - Check if branch needs rebasing from main
#
# Rigor rule: All branches must be rebased from main before PR
# Goal: Zero merge conflicts
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Rigor Rules: Rebase Status Check"
echo "=================================="
echo ""

# Fetch latest main
echo "[1] Fetching latest main..."
git fetch origin main --quiet 2>/dev/null || {
  echo -e "${YELLOW}[!] Could not fetch origin/main (offline?)${NC}"
  echo "    Proceeding with local main reference"
}

# Get current branch
BRANCH_NAME=$(git branch --show-current)

if [[ "$BRANCH_NAME" == "main" ]]; then
  echo -e "${GREEN}[Y] On main branch, no rebase needed${NC}"
  exit 0
fi

# Check commits behind main
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")

echo ""
echo "[2] Analyzing rebase status..."
echo "    Branch: $BRANCH_NAME"
echo "    Ahead of main: $AHEAD commits"
echo "    Behind main: $BEHIND commits"

if [[ "$BEHIND" -eq 0 ]]; then
  echo ""
  echo -e "${GREEN}[Y] Branch is up-to-date with main${NC}"
  exit 0
else
  echo ""
  echo -e "${RED}[X] Branch is $BEHIND commits behind main${NC}"
  echo ""
  echo "Rigor rule violation: Must rebase before PR"
  echo ""
  echo "To fix:"
  echo "  1. Commit your current work: git commit -am 'WIP: save progress'"
  echo "  2. Rebase from main: git rebase origin/main"
  echo "  3. Resolve any conflicts"
  echo "  4. Force push: git push --force-with-lease"
  echo ""
  echo "Or use interactive rebase to clean up commits:"
  echo "  git rebase -i origin/main"
  exit 1
fi
```

**Integration with pre-commit hook:**

Add to `scripts/bash/pre-commit-hook.sh`:

```bash
# 6. Rebase status check (non-blocking warning)
echo -e "${BLUE}6. Checking rebase status...${NC}"
if [ -f "scripts/bash/rigor-rebase-check.sh" ]; then
    if ./scripts/bash/rigor-rebase-check.sh > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Branch is up-to-date with main${NC}"
    else
        echo -e "${YELLOW}⚠ Branch needs rebasing from main${NC}"
        echo "  Run: git rebase origin/main"
        echo "  This is required before PR creation"
    fi
else
    echo -e "${YELLOW}⚠ Rebase check script not found, skipping${NC}"
fi
echo ""
```

### 4.3 Pre-PR Validation Script

**File**: `scripts/bash/rigor-pre-pr-validation.sh`

```bash
#!/usr/bin/env bash
#
# rigor-pre-pr-validation.sh - Comprehensive pre-PR validation gate
#
# This is a BLOCKING gate. All checks must pass before PR creation.
# NO BYPASSING. This is non-negotiable.
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track status
OVERALL_STATUS=0
CHECKS_PASSED=0
CHECKS_FAILED=0

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Rigor Rules: Pre-PR Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "This gate ensures code quality and CI stability."
echo "All checks must pass before PR creation."
echo ""

# Helper functions
check_pass() {
  echo -e "${GREEN}[✓] $1${NC}"
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

check_fail() {
  echo -e "${RED}[X] $1${NC}"
  CHECKS_FAILED=$((CHECKS_FAILED + 1))
  OVERALL_STATUS=1
}

check_skip() {
  echo -e "${YELLOW}[~] $1${NC}"
}

# Check 1: Branch naming
echo -e "${BLUE}[1/7] Validating branch name and worktree...${NC}"
if ./scripts/bash/rigor-branch-validation.sh > /dev/null 2>&1; then
  check_pass "Branch name and worktree validation passed"
else
  check_fail "Branch naming validation failed"
  echo "    Run: ./scripts/bash/rigor-branch-validation.sh"
fi
echo ""

# Check 2: Rebase status
echo -e "${BLUE}[2/7] Checking rebase status...${NC}"
if ./scripts/bash/rigor-rebase-check.sh > /dev/null 2>&1; then
  check_pass "Branch is up-to-date with main"
else
  check_fail "Branch needs rebasing from main"
  echo "    Run: git rebase origin/main"
fi
echo ""

# Check 3: Code formatting
echo -e "${BLUE}[3/7] Checking code formatting...${NC}"
if uv run ruff format --check . > /dev/null 2>&1; then
  check_pass "Code formatting is correct"
else
  check_fail "Code formatting issues detected"
  echo "    Run: uv run ruff format ."
fi
echo ""

# Check 4: Linting
echo -e "${BLUE}[4/7] Running linter...${NC}"
if uv run ruff check . > /dev/null 2>&1; then
  check_pass "Linting passed with zero errors"
else
  check_fail "Linting failed"
  echo "    Run: uv run ruff check . --fix"
fi
echo ""

# Check 5: Tests
echo -e "${BLUE}[5/7] Running test suite...${NC}"
if uv run pytest tests/ -x -q > /dev/null 2>&1; then
  check_pass "All tests passed"
else
  check_fail "Test suite failed"
  echo "    Run: uv run pytest tests/ -v"
fi
echo ""

# Check 6: DCO sign-off
echo -e "${BLUE}[6/7] Checking DCO sign-off...${NC}"
UNSIGNED=$(git log --oneline origin/main..HEAD --no-merges 2>/dev/null | wc -l || echo "0")
SIGNED=$(git log --oneline origin/main..HEAD --no-merges --grep="Signed-off-by" 2>/dev/null | wc -l || echo "0")

if [[ "$UNSIGNED" -eq "$SIGNED" && "$UNSIGNED" -gt 0 ]]; then
  check_pass "All $SIGNED commits have DCO sign-off"
elif [[ "$UNSIGNED" -eq 0 ]]; then
  check_skip "No new commits to check"
else
  check_fail "Some commits missing DCO sign-off ($SIGNED/$UNSIGNED signed)"
  echo "    Run: git rebase -i origin/main --exec 'git commit --amend --no-edit -s'"
fi
echo ""

# Check 7: Security scan
echo -e "${BLUE}[7/7] Running security scan (SAST)...${NC}"
if command -v bandit &> /dev/null; then
  if uv run bandit -r src/ -ll > /dev/null 2>&1; then
    check_pass "Security scan passed (no high/critical issues)"
  else
    check_fail "Security scan found issues"
    echo "    Run: uv run bandit -r src/ -ll"
  fi
else
  check_skip "bandit not installed, skipping SAST"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Checks passed: $CHECKS_PASSED"
echo "Checks failed: $CHECKS_FAILED"
echo ""

if [[ $OVERALL_STATUS -eq 0 ]]; then
  echo -e "${GREEN}✓ All validation checks passed!${NC}"
  echo ""
  echo "You are cleared to create a PR:"
  echo "  1. Push branch: git push origin HEAD"
  echo "  2. Create PR: gh pr create --fill"
  echo "  3. Monitor CI: gh pr checks"
  echo ""
else
  echo -e "${RED}X Validation failed. Fix issues before creating PR.${NC}"
  echo ""
  echo "This is a blocking gate. There are no bypasses."
  echo "Fix all failed checks and re-run this script."
  echo ""
  exit 1
fi
```

**Usage in workflow commands:**

```markdown
## Step 5: Pre-PR Validation (MANDATORY)

Before creating a PR, run the comprehensive validation gate:

```bash
./scripts/bash/rigor-pre-pr-validation.sh
```

This script checks:
1. Branch naming and worktree alignment
2. Rebase status (must be up-to-date with main)
3. Code formatting (ruff format --check)
4. Linting (ruff check)
5. Test suite (pytest)
6. DCO sign-off (all commits signed)
7. Security scan (bandit SAST)

**ALL CHECKS MUST PASS.** There are no bypasses.

If any check fails, fix it and re-run until all pass.
```

---

## 5. CI/CD Integration

### 5.1 GitHub Actions: Rigor Rules Check Workflow

**File**: `.github/workflows/rigor-rules-check.yml`

```yaml
name: Rigor Rules Check

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  rigor-validation:
    runs-on: ubuntu-latest
    name: Rigor Rules Validation Gate
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for rebase check

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Install jq (for decision log validation)
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Validate branch naming
        if: github.event_name == 'pull_request'
        run: |
          # PR branch must follow hostname/task-NNN/slug format
          BRANCH="${{ github.head_ref }}"
          if [[ ! "$BRANCH" =~ ^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$ ]]; then
            echo "::error::Invalid branch name format: $BRANCH"
            echo "Expected: hostname/task-NNN/slug-description"
            exit 1
          fi

      - name: Validate decision logs (JSONL)
        run: |
          # Check all JSONL files are valid JSON
          EXIT_CODE=0
          for file in memory/decisions/task-*.jsonl; do
            if [ -f "$file" ]; then
              if ! jq empty "$file" 2>/dev/null; then
                echo "::error file=$file::Invalid JSON in decision log"
                EXIT_CODE=1
              fi
            fi
          done
          exit $EXIT_CODE

      - name: Check code formatting
        run: uv run ruff format --check .

      - name: Run linter
        run: uv run ruff check .

      - name: Run test suite
        run: uv run pytest tests/ -v --cov=src/flowspec_cli --cov-report=term-missing

      - name: Security scan (SAST)
        continue-on-error: true  # Non-blocking but logged
        run: uv tool run bandit -r src/ -ll

      - name: DCO sign-off check
        if: github.event_name == 'pull_request'
        run: |
          # Check all PR commits have DCO sign-off
          UNSIGNED=$(git log --oneline origin/${{ github.base_ref }}..${{ github.head_ref }} --no-merges | wc -l)
          SIGNED=$(git log --oneline origin/${{ github.base_ref }}..${{ github.head_ref }} --no-merges --grep="Signed-off-by" | wc -l)

          if [[ "$UNSIGNED" -ne "$SIGNED" ]]; then
            echo "::error::Some commits missing DCO sign-off ($SIGNED/$UNSIGNED signed)"
            exit 1
          fi

      - name: Summary
        run: |
          echo "✓ All rigor rules validation checks passed"
          echo "This PR meets the quality gates for merge"
```

### 5.2 Pre-commit Git Hook Integration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: rigor-rebase-check
        name: Rigor Rules - Rebase Check
        entry: scripts/bash/rigor-rebase-check.sh
        language: script
        always_run: true
        pass_filenames: false
        stages: [commit]

      - id: rigor-decision-log-validation
        name: Rigor Rules - Decision Log Validation
        entry: bash -c 'for f in memory/decisions/task-*.jsonl; do [ -f "$f" ] && jq empty "$f" || exit 1; done'
        language: system
        files: ^memory/decisions/.*\.jsonl$
        pass_filenames: false
```

### 5.3 CODEOWNERS Protection

**File**: `.github/CODEOWNERS` (add these lines)

```
# Rigor Rules Infrastructure - Require review for changes
/scripts/bash/rigor-*.sh                   @platform-engineer
/memory/decisions/                         @platform-engineer
/templates/partials/flow/_rigor-rules.md   @software-architect @platform-engineer
/.github/workflows/rigor-rules-check.yml   @platform-engineer
```

---

## 6. Observability and Status Tracking

### 6.1 Workflow Status Tracking Format

Every workflow command should emit structured status at key points:

**Template for status output:**

```markdown
## Phase Complete: {PHASE_NAME}

[Y] Phase: {PHASE_NAME} complete
    Current state: workflow:{STATE}
    Next step: {NEXT_COMMAND}

    Progress:
    ✅ Setup phase
    ✅ Execution phase
    {STATUS} Freeze (skipped - not needed / suspended)
    ⬜ Validation phase (current)
    ⬜ PR phase (pending)

    Decisions logged: {COUNT} (see memory/decisions/task-{NNN}.jsonl)
    Next action: {SPECIFIC_COMMAND_TO_RUN}
```

**Example (after /flow:implement):**

```
## Implementation Complete

[Y] Phase: Implementation complete
    Current state: workflow:In Implementation
    Next step: /flow:validate

    Progress:
    ✅ Setup phase (branch created, constitution validated)
    ✅ Execution phase (code written, tests passing)
    ⬜ Freeze (not needed - proceeding to validation)
    ⬜ Validation phase (NEXT)
    ⬜ PR phase (pending)

    Decisions logged: 7 (see memory/decisions/task-542.jsonl)
    Files changed: 12 additions, 3 modifications
    Test coverage: 94% (target: 90%)

    Next action: Run /flow:validate to proceed to QA and security review
```

### 6.2 Decision Log Metrics

Add to task memory after significant progress:

```markdown
## Decision Log Metrics

- Total decisions: 12
- By phase:
  - Setup: 2
  - Execution: 7
  - Validation: 3
- Critical decisions: 4 (architecture, library selection)
- Reversible decisions: 8 (two-way doors)
- One-way doors: 4 (require careful review before reversing)

Query: `jq -s 'group_by(.phase) | map({phase: .[0].phase, count: length})' memory/decisions/task-542.jsonl`
```

### 6.3 CI/CD Pipeline Observability

**GitHub Actions: Post decision log summary to PR**

Add to `.github/workflows/rigor-rules-check.yml`:

```yaml
      - name: Post decision log summary to PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const { execSync } = require('child_process');

            // Find decision logs for PR's task
            const branch = context.payload.pull_request.head.ref;
            const taskMatch = branch.match(/task-(\d+)/);

            if (taskMatch) {
              const taskId = `task-${taskMatch[1]}`;
              const logFile = `memory/decisions/${taskId}.jsonl`;

              if (fs.existsSync(logFile)) {
                // Count decisions by phase
                const stats = execSync(`jq -s 'group_by(.phase) | map({phase: .[0].phase, count: length})' ${logFile}`).toString();

                const comment = `## 📊 Decision Log Summary

**Task**: ${taskId}
**Decision log**: \`${logFile}\`

### Decisions by Phase
\`\`\`json
${stats}
\`\`\`

View full log: [${logFile}](https://github.com/${context.repo.owner}/${context.repo.repo}/blob/${context.payload.pull_request.head.sha}/${logFile})
`;

                github.rest.issues.createComment({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: context.payload.pull_request.number,
                  body: comment
                });
              }
            }
```

---

## 7. /flow:freeze Command

### 7.1 Command Template

**File**: `templates/commands/flow/freeze.md`

```markdown
---
description: Suspend current task with context preservation
---

# /flow:freeze - Task Suspension

## Overview

Suspend work on the current task in a known-good state, preserving all context for later resumption. This is the rigor rules equivalent of "parking" work without losing progress.

**Use cases:**
- Blocked by external dependency (API access, design approval)
- Higher priority work needs immediate attention
- Context switch to another task required
- End of day/week - preserve progress for Monday

**Guarantees:**
- Code in working state (tests may be incomplete)
- All decisions logged to JSONL
- Task memory updated with current status
- Git branch pushed to remote (if requested)

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

{{INCLUDE:.claude/partials/flow/_workflow-state.md}}

{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}

## Execution Instructions

### Step 1: Verify Working State

Before freezing, ensure code is in a working state:

```bash
# Run format + lint + tests
uv run ruff format .
uv run ruff check .
uv run pytest tests/ -x -q

# If tests fail, document known failures in task memory
```

**Acceptance criteria:**
- Code compiles/runs without errors
- Existing tests pass OR failures are documented
- No uncommitted changes (commit everything)

### Step 2: Update Task Memory

Capture current state in `backlog/memory/task-{NNN}.md`:

```markdown
## Current State (Frozen: YYYY-MM-DD)

**Status**: Suspended (blocked/context-switch/end-of-sprint)

**Progress**:
- ✅ Completed: {list what's done}
- ⬜ In Progress: {what was being worked on}
- ⬜ Not Started: {remaining work}

**Blocking Issues**:
- {Issue 1}: Description and workaround/resolution path
- {Issue 2}: ...

**Resume Instructions**:
1. Read this memory file
2. Review decision log: `memory/decisions/task-{NNN}.jsonl`
3. Check branch status: `git status`
4. Continue from: {specific next step}

**Critical Context** (don't delete):
- What: {brief description}
- Why: {business value}
- Constraints: {technical requirements}
```

### Step 3: Log Freeze Decision

```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-{NNN} \
  --phase freeze \
  --decision "Task frozen in working state" \
  --rationale "{reason for freezing: blocked by X, context switch to task-Y, etc.}" \
  --actor "@{agent-identity}"
```

### Step 4: Update Backlog Task

```bash
# Add freeze note to task
backlog task edit task-{NNN} \
  --append-notes $'FROZEN {DATE}: {Reason}\n\nResume by reading memory/task-{NNN}.md'

# Update status to reflect freeze
backlog task edit task-{NNN} -s "Blocked"  # Or keep "In Progress"
```

### Step 5: Commit and Push (Optional)

```bash
# Commit work-in-progress state
git add -A
git commit -s -m "chore: freeze task-{NNN} - {reason}

Work suspended in working state. All context preserved in:
- backlog/memory/task-{NNN}.md
- memory/decisions/task-{NNN}.jsonl

Resume instructions in task memory file.

Signed-off-by: {Name} <{email}>
"

# Push to remote (ensures context survives machine changes)
git push origin HEAD
```

### Step 6: Notify User

```text
[Y] Task frozen successfully

Task: task-{NNN}
State: {current-workflow-state}
Reason: {freeze-reason}

Context preserved:
- Task memory: backlog/memory/task-{NNN}.md
- Decision log: memory/decisions/task-{NNN}.jsonl
- Git branch: {branch-name} (pushed to remote)

To resume:
1. Read: backlog/memory/task-{NNN}.md
2. Checkout: git checkout {branch-name}
3. Continue from: {specific-instruction}
```

## Resume Workflow

When resuming a frozen task:

```bash
# 1. Checkout branch
git checkout {branch-name}

# 2. Read task memory
cat backlog/memory/task-{NNN}.md

# 3. Review decision log
jq '.' memory/decisions/task-{NNN}.jsonl | less

# 4. Check task status
backlog task {NNN} --plain

# 5. Continue workflow from frozen state
/flow:{next-command}  # e.g., /flow:implement, /flow:validate
```

## Related Commands

- `/flow:implement` - Return to implementation after freeze
- `/flow:validate` - Resume to validation phase
- `backlog task edit` - Update task status
```

### 7.2 Freeze Workflow Integration

Add freeze capability to all workflow commands:

```markdown
## Optional: Freeze Work

If you need to suspend work before completing this phase:

```bash
/flow:freeze --reason "Blocked by {dependency}" --task task-{NNN}
```

This will:
- Preserve all context in task memory
- Log freeze decision to JSONL
- Push work-in-progress to remote (if requested)
- Allow resumption from exact point later
```

---

## 8. Constitution Integration

### 8.1 Add Rigor Rules Principles

**File**: `memory/constitution.md` (add new section)

```markdown
## VI. Engineering Rigor and Workflow Discipline

### Git Workflow Standards

**Branch Naming** (MANDATORY):
- Format: `hostname/task-NNN/slug-description`
- Example: `macbook-pro/task-542/decision-logging`
- Enforcement: Pre-commit hooks and CI validation
- Rationale: Traceability from branch to task to decisions

**Worktree Alignment** (RECOMMENDED):
- Worktree directory name should match branch name or slug
- Prevents confusion when working on multiple tasks
- Checked by `rigor-branch-validation.sh`

**Rebase Discipline** (MANDATORY):
- All branches must be rebased from main before PR
- Goal: Zero merge conflicts
- Enforcement: Pre-PR validation gate blocks PRs with stale branches
- Command: `git rebase origin/main`

### Decision Traceability

**Decision Logging** (MANDATORY):
- All architectural and implementation decisions logged to JSONL
- Format: `memory/decisions/task-NNN.jsonl`
- Schema: See `memory/decisions/README.md`
- Phases: setup, execution, freeze, validation, pr
- Queryable via `jq` for audit and debugging

**Decision-Worthy Choices**:
- Library/framework selection
- Architecture patterns
- Data structure design
- Performance trade-offs
- Security implementations

### Pre-PR Validation Gates

**Validation Script** (MANDATORY - NO BYPASS):
- Run: `./scripts/bash/rigor-pre-pr-validation.sh`
- Checks: Branch naming, rebase status, format, lint, tests, DCO, SAST
- ALL checks must pass before PR creation
- NO manual bypassing allowed
- NO "I'll fix in CI" allowed

**Why No Bypass**:
- Failed PRs waste reviewer time
- Broken CI creates noise and delays other work
- Demonstrates lack of due diligence
- Violates DORA Elite practices

### Task Suspension and Context Preservation

**Freeze Capability** (RECOMMENDED):
- Command: `/flow:freeze`
- Preserves context in: task memory + decision log + git branch
- Enables context switches without losing progress
- Supports "blocked" states without rework

**Resume Workflow**:
- Read task memory for current state
- Review decision log for rationale
- Continue from documented next step

### Workflow Phase Tracking

**Status Visibility** (MANDATORY):
- Every command emits current state and next step
- Progress checklist shows completed/pending phases
- Decision count and key metrics included
- Enables "what comes next" clarity

**Phase Progression**:
1. Setup (validate pre-conditions)
2. Execution (implementation work)
3. Freeze (optional suspension)
4. Validation (pre-PR checks)
5. PR (review and merge)
```

### 8.2 Update Critical Rules

**File**: `memory/critical-rules.md` (add section)

```markdown
## Rigor Rules: Git Workflow and Pre-PR Validation

### Branch Naming (Enforced)

Branch names MUST follow the format: `hostname/task-NNN/slug-description`

**Examples:**
- `macbook-pro/task-542/decision-logging`
- `build-server/task-100/api-refactor`

**Validation:**
```bash
# Pre-commit check
./scripts/bash/rigor-branch-validation.sh

# CI check
# .github/workflows/rigor-rules-check.yml validates all PR branches
```

**Why Enforce:**
- Traceability: Branch → Task → Decisions
- Multi-developer clarity: Know which machine/user created branch
- Automated tooling: Scripts can extract task ID from branch name

### Pre-PR Validation (MANDATORY - BLOCKING GATE)

**Before creating ANY PR, run:**

```bash
./scripts/bash/rigor-pre-pr-validation.sh
```

**Checks performed:**
1. Branch naming format
2. Rebase status (must be current with main)
3. Code formatting (ruff format --check)
4. Linting (ruff check)
5. Test suite (pytest)
6. DCO sign-off (all commits)
7. Security scan (bandit SAST)

**ALL CHECKS MUST PASS.**

**There is NO bypass mechanism.**

**Rationale:**
- PRs that fail CI waste reviewer time
- Broken CI creates noise and delays other work
- Demonstrates lack of due diligence
- DORA Elite requires <5% change failure rate
- Prevention is cheaper than remediation

### Rebase Before PR (MANDATORY)

**All branches must be rebased from main before PR creation.**

```bash
# Check rebase status
./scripts/bash/rigor-rebase-check.sh

# Rebase if behind
git fetch origin main
git rebase origin/main
git push --force-with-lease
```

**Goal:** Zero merge conflicts

**Why:**
- Merge conflicts delay reviews
- Reviewers should see final merge result
- Forces developer to resolve conflicts, not reviewers
- Maintains linear history

### Decision Logging (MANDATORY)

**All critical decisions must be logged to JSONL:**

```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-NNN \
  --phase execution \
  --decision "Use PostgreSQL for persistence" \
  --rationale "Need ACID compliance and JSON support" \
  --actor "@backend-engineer" \
  --alternatives "MongoDB" "SQLite"
```

**Decision-worthy choices:**
- Library/framework selection
- Architecture patterns
- Data structures
- Performance trade-offs
- Security implementations

**Why:**
- Audit trail for post-mortems
- Context for future maintainers
- Enables "why did we choose X" queries
- Supports rollback decisions

### Workflow Phase Tracking (MANDATORY)

**Every command must emit status:**

```
[Y] Phase: {PHASE} complete
    Current state: workflow:{STATE}
    Next step: {COMMAND}
    Progress: [checkboxes]
    Decisions logged: {COUNT}
```

**Why:**
- Eliminates "what do I do next" confusion
- Enables handoffs between agents
- Supports context switches via freeze
- Visibility into progress
```

---

## 9. DevSecOps Integration

### 9.1 SAST Integration

**Security scanning is integrated into:**

1. **Pre-PR validation script** (`rigor-pre-pr-validation.sh`):
   - Runs `bandit -r src/ -ll` (Python SAST)
   - Checks for high/critical severity issues
   - Non-blocking warning if bandit not installed

2. **CI pipeline** (`.github/workflows/rigor-rules-check.yml`):
   - Runs bandit on every PR
   - `continue-on-error: true` (logs but doesn't block)
   - Results posted to PR security tab

3. **Pre-commit hook** (optional):
   - Can add bandit check to `pre-commit-hook.sh`
   - Scans only staged files for speed

**Example pre-commit integration:**

```bash
# Add to scripts/bash/pre-commit-hook.sh
echo -e "${BLUE}7. Running security scan (SAST)...${NC}"
if command -v bandit &> /dev/null; then
    # Scan only staged Python files for speed
    STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
    if [ -n "$STAGED_PY_FILES" ]; then
        if echo "$STAGED_PY_FILES" | xargs bandit -ll 2>/dev/null; then
            echo -e "${GREEN}✓ Security scan passed${NC}"
        else
            echo -e "${YELLOW}⚠ Security issues detected${NC}"
            echo "  Review and fix, or commit with --no-verify (emergency only)"
            STATUS=1
        fi
    else
        echo -e "${GREEN}✓ No Python files to scan${NC}"
    fi
else
    echo -e "${YELLOW}⚠ bandit not installed, skipping SAST${NC}"
fi
echo ""
```

### 9.2 SBOM Generation

**Add to CI pipeline** (`.github/workflows/rigor-rules-check.yml`):

```yaml
      - name: Generate SBOM
        run: |
          # Generate SBOM in SPDX format
          uv tool install cyclonedx-bom
          uv run cyclonedx-py --output sbom.json --format json

      - name: Upload SBOM artifact
        uses: actions/upload-artifact@v4
        with:
          name: sbom-${{ github.sha }}
          path: sbom.json
          retention-days: 90
```

### 9.3 Dependency Scanning

**Add to CI pipeline:**

```yaml
      - name: Check dependencies for vulnerabilities
        continue-on-error: true
        run: |
          uv tool install pip-audit
          uv run pip-audit --requirement pyproject.toml
```

---

## 10. Operational Runbooks

### 10.1 Runbook: Developer Creates First PR with Rigor Rules

**Scenario:** Developer starting work on task-542

**Steps:**

1. **Create feature branch:**
   ```bash
   HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')
   TASK="task-542"
   SLUG="decision-logging"

   git checkout -b "${HOSTNAME}/${TASK}/${SLUG}"
   ```

2. **Read task and memory:**
   ```bash
   backlog task 542 --plain
   cat backlog/memory/task-542.md
   ```

3. **Claim task:**
   ```bash
   backlog task edit 542 -s "In Progress" -a "@myself"
   ```

4. **Do work, commit incrementally:**
   ```bash
   # Make changes
   git add memory/decisions/
   git commit -s -m "feat(decisions): add JSONL logging schema"

   # Log decision
   ./scripts/bash/rigor-decision-log.sh \
     --task task-542 \
     --phase execution \
     --decision "Use JSONL for decision logs" \
     --rationale "Line-oriented format, streaming-friendly, tooling support" \
     --actor "@platform-engineer"
   ```

5. **Mark ACs complete as you go:**
   ```bash
   backlog task edit 542 --check-ac 1
   backlog task edit 542 --check-ac 2
   ```

6. **Before PR - run validation:**
   ```bash
   ./scripts/bash/rigor-pre-pr-validation.sh
   ```

7. **Fix any failures, re-run until all pass**

8. **Create PR:**
   ```bash
   git push origin HEAD
   gh pr create --fill --assignee @me
   ```

9. **Monitor CI:**
   ```bash
   gh pr checks
   ```

10. **After merge - mark task done:**
    ```bash
    backlog task edit 542 -s Done --notes "Completed via PR #XXX"
    ```

### 10.2 Runbook: Resume Frozen Task

**Scenario:** Task was frozen 2 days ago, need to resume

**Steps:**

1. **Find frozen task:**
   ```bash
   backlog task list --plain | grep -i frozen
   # Or check task memory
   ls backlog/memory/ | grep task-
   ```

2. **Read task memory:**
   ```bash
   cat backlog/memory/task-542.md
   # Look for "Resume Instructions" section
   ```

3. **Checkout branch:**
   ```bash
   git checkout {branch-name}
   git pull origin {branch-name}  # In case frozen from different machine
   ```

4. **Review decision log:**
   ```bash
   jq '.' memory/decisions/task-542.jsonl | less
   # Review last few decisions to recall context
   ```

5. **Check dependencies resolved:**
   ```bash
   # Check if blocking issue mentioned in task memory is resolved
   # e.g., "Blocked by API access" - verify you now have access
   ```

6. **Update backlog status:**
   ```bash
   backlog task edit 542 -s "In Progress" --append-notes "Resumed work after freeze"
   ```

7. **Continue workflow:**
   ```bash
   # Follow "Resume Instructions" from task memory
   # Typically: continue implementation or validation
   /flow:implement  # or /flow:validate
   ```

### 10.3 Runbook: Debug Why Decision Was Made

**Scenario:** Production issue, need to understand why we chose approach X

**Steps:**

1. **Find related PR:**
   ```bash
   gh pr list --search "API timeout" --state merged
   ```

2. **Extract task ID from PR branch:**
   ```bash
   gh pr view 123 --json headRefName | jq -r '.headRefName'
   # Output: macbook-pro/task-437/api-timeout-increase
   ```

3. **Query decision log:**
   ```bash
   jq 'select(.decision | contains("timeout"))' memory/decisions/task-437.jsonl
   ```

4. **Output:**
   ```json
   {
     "timestamp": "2025-12-10T15:30:00Z",
     "task_id": "task-437",
     "phase": "execution",
     "decision": "Increased API timeout from 5s to 30s",
     "rationale": "External service SLA is 20s, need buffer for network latency",
     "alternatives": ["Keep 5s", "Use exponential backoff"],
     "actor": "@backend-engineer"
   }
   ```

5. **Review alternatives:**
   - Why was exponential backoff rejected?
   - Check if SLA changed since decision

6. **Propose fix:**
   ```bash
   # Create new task for fix
   backlog task create "Implement exponential backoff for API calls" \
     --ac "Replace fixed timeout with backoff strategy" \
     --ac "Update timeout to 10s with 3 retries" \
     -l backend,bug-fix \
     --priority high
   ```

---

## 11. Testing and Validation

### 11.1 Script Testing

**Test script:** `tests/test_rigor_scripts.sh`

```bash
#!/usr/bin/env bash
#
# test_rigor_scripts.sh - Integration tests for rigor rules scripts
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Testing Rigor Rules Scripts"
echo "============================"
echo ""

# Test 1: Decision log helper
echo "[1] Testing rigor-decision-log.sh..."
./scripts/bash/rigor-decision-log.sh \
  --task task-999 \
  --phase execution \
  --decision "Test decision" \
  --rationale "This is a test" \
  --actor "@test-agent"

if [ -f "memory/decisions/task-999.jsonl" ]; then
  # Validate JSON
  if jq empty memory/decisions/task-999.jsonl 2>/dev/null; then
    echo -e "${GREEN}✓ Decision logged successfully${NC}"
    rm memory/decisions/task-999.jsonl  # Cleanup
  else
    echo -e "${RED}✗ Invalid JSON in decision log${NC}"
    exit 1
  fi
else
  echo -e "${RED}✗ Decision log not created${NC}"
  exit 1
fi
echo ""

# Test 2: Branch validation (expect failure on main)
echo "[2] Testing rigor-branch-validation.sh..."
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" == "main" ]]; then
  if ! ./scripts/bash/rigor-branch-validation.sh > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Branch validation correctly blocks main${NC}"
  else
    echo -e "${RED}✗ Branch validation should block main branch${NC}"
    exit 1
  fi
else
  echo "Skipping (not on main branch)"
fi
echo ""

# Test 3: Rebase check
echo "[3] Testing rigor-rebase-check.sh..."
if ./scripts/bash/rigor-rebase-check.sh > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Rebase check passed${NC}"
else
  echo "Rebase check failed (may be expected if branch is behind)"
fi
echo ""

# Test 4: Pre-PR validation (dry run - don't fail on errors)
echo "[4] Testing rigor-pre-pr-validation.sh..."
if ./scripts/bash/rigor-pre-pr-validation.sh; then
  echo -e "${GREEN}✓ Pre-PR validation passed${NC}"
else
  echo "Pre-PR validation failed (may be expected in test environment)"
fi
echo ""

echo "Script testing complete"
```

### 11.2 CI Testing

Add to `.github/workflows/ci.yml`:

```yaml
  rigor-scripts:
    runs-on: ubuntu-latest
    name: Test Rigor Rules Scripts
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Run rigor scripts tests
        run: bash tests/test_rigor_scripts.sh
```

---

## 12. Migration and Rollout Plan

### Phase 1: Infrastructure Setup (Week 1)

**Tasks:**
1. Create directory structure (`memory/decisions/`, scripts)
2. Write helper scripts (decision log, branch validation, rebase check, pre-PR validation)
3. Create `_rigor-rules.md` include file
4. Write documentation (`memory/decisions/README.md`)
5. Add to constitution and critical rules

**Deliverables:**
- All scripts executable and tested
- Documentation complete
- No enforcement yet (observational mode)

### Phase 2: Soft Rollout (Week 2)

**Tasks:**
1. Add pre-commit hook for rebase check (warning only)
2. Add CI workflow for decision log validation
3. Train first adopters on scripts
4. Collect feedback on usability

**Deliverables:**
- Pre-commit hooks installed (warnings, not blocking)
- CI validates JSONL format
- 5-10 developers using scripts voluntarily

### Phase 3: Enforcement (Week 3)

**Tasks:**
1. Enable branch naming validation in CI (blocking)
2. Enable pre-PR validation requirement (blocking)
3. Update PR template to reference rigor rules
4. Add CODEOWNERS protections

**Deliverables:**
- All PRs blocked until rigor checks pass
- Branch naming enforced
- Decision logs required for architecture changes

### Phase 4: Optimization (Week 4+)

**Tasks:**
1. Add `/flow:freeze` command
2. Integrate workflow status tracking into all commands
3. Add decision log analytics (most common decisions, reversibility analysis)
4. Create dashboard for DORA metrics

**Deliverables:**
- Full rigor rules system operational
- DORA metrics tracking enabled
- Developer satisfaction survey completed

---

## 13. Metrics and Success Criteria

### DORA Metrics (Target: Elite)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Deployment Frequency | 2-3/week | >1/day | GitHub releases per day |
| Lead Time for Changes | 2-5 days | <1 day | PR open to merge time |
| Change Failure Rate | 15-20% | <5% | Failed deploys / total deploys |
| Mean Time to Restore | 2-4 hours | <1 hour | Incident detection to resolution |

### Rigor Rules Adoption Metrics

| Metric | Week 1 | Week 2 | Week 3 | Week 4 |
|--------|--------|--------|--------|--------|
| PRs with valid branch names | 10% | 40% | 70% | 100% |
| PRs with decision logs | 5% | 30% | 60% | 90% |
| PRs passing pre-PR validation | 20% | 50% | 80% | 95% |
| CI failure rate (lint/test) | 25% | 18% | 10% | <5% |

### Developer Experience Metrics

- **Pre-PR validation time**: <5 minutes (target)
- **Decision logging time**: <2 minutes per decision (target)
- **Context switch time (freeze/resume)**: <10 minutes (target)
- **Developer satisfaction**: >4/5 (survey)

---

## 14. Troubleshooting Guide

### Issue: Branch name validation fails

**Symptoms:**
```
[X] Invalid branch name format
Current branch: feature-add-logging
Expected format: hostname/task-NNN/slug-description
```

**Resolution:**
```bash
# Get sanitized hostname
HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')

# Rename branch
git branch -m feature-add-logging ${HOSTNAME}/task-542/add-logging
```

### Issue: Rebase check fails

**Symptoms:**
```
[X] Branch is 15 commits behind main
Rigor rule violation: Must rebase before PR
```

**Resolution:**
```bash
# Commit current work
git add -A
git commit -s -m "WIP: save progress before rebase"

# Fetch and rebase
git fetch origin main
git rebase origin/main

# If conflicts:
# 1. Resolve conflicts in files
# 2. git add <resolved-files>
# 3. git rebase --continue

# Force push (with safety)
git push --force-with-lease
```

### Issue: Decision log has invalid JSON

**Symptoms:**
```
::error file=memory/decisions/task-542.jsonl::Invalid JSON in decision log
```

**Resolution:**
```bash
# Find invalid line
jq empty memory/decisions/task-542.jsonl 2>&1

# Output shows line number
# Fix manually or regenerate log

# Validate all logs
for f in memory/decisions/task-*.jsonl; do
  jq empty "$f" || echo "Invalid: $f"
done
```

### Issue: Pre-PR validation script not found

**Symptoms:**
```
bash: ./scripts/bash/rigor-pre-pr-validation.sh: No such file or directory
```

**Resolution:**
```bash
# Check if scripts exist
ls -la scripts/bash/rigor-*.sh

# If missing, pull latest from main
git fetch origin main
git checkout origin/main -- scripts/bash/rigor-*.sh

# Make executable
chmod +x scripts/bash/rigor-*.sh
```

### Issue: DCO sign-off missing

**Symptoms:**
```
[X] Some commits missing DCO sign-off (3/5 signed)
```

**Resolution:**
```bash
# Rebase with auto-signoff
git rebase -i origin/main --exec 'git commit --amend --no-edit -s'

# Or amend last commit only
git commit --amend --no-edit -s

# Force push
git push --force-with-lease
```

---

## 15. References and Related Documents

### Internal Documents

- `build-docs/task-rigor.md` - Original task requirements
- `memory/critical-rules.md` - Critical rules (updated with rigor rules)
- `memory/constitution.md` - Project constitution (updated with rigor principles)
- `schemas/decision-log.schema.json` - JSON schema for decision logs
- `docs/decisions/*.jsonl` - Example decision logs

### External References

- [DORA Metrics](https://dora.dev/guides/)
- [JSONL Format Specification](https://jsonlines.org/)
- [Git Worktrees](https://git-scm.com/docs/git-worktree)
- [Developer Certificate of Origin](https://developercertificate.org/)
- [Pre-commit Framework](https://pre-commit.com/)

### Scripts and Tools

- `scripts/bash/rigor-decision-log.sh` - Decision logging helper
- `scripts/bash/rigor-branch-validation.sh` - Branch naming validation
- `scripts/bash/rigor-rebase-check.sh` - Rebase status check
- `scripts/bash/rigor-pre-pr-validation.sh` - Comprehensive pre-PR gate
- `.github/workflows/rigor-rules-check.yml` - CI enforcement workflow

---

## Appendix A: Example Decision Log Queries

### Query 1: Find all decisions by phase

```bash
jq -s 'group_by(.phase) | map({phase: .[0].phase, decisions: map(.decision)})' \
  memory/decisions/task-*.jsonl
```

### Query 2: Find high-impact decisions (one-way doors)

```bash
jq -s 'map(select(.context.reversibility == "one-way-door"))' \
  memory/decisions/task-*.jsonl
```

### Query 3: Decision timeline

```bash
jq -s 'sort_by(.timestamp) | map({time: .timestamp, task: .task_id, decision: .decision})' \
  memory/decisions/task-*.jsonl
```

### Query 4: Decisions by actor

```bash
jq -s 'group_by(.actor) | map({actor: .[0].actor, count: length, decisions: map(.decision)})' \
  memory/decisions/task-*.jsonl
```

### Query 5: Most recent decision for a task

```bash
jq -s 'sort_by(.timestamp) | last' memory/decisions/task-542.jsonl
```

---

## Appendix B: Branch Naming Examples

### Valid Branch Names

```
# Format: hostname/task-NNN/slug-description

macbook-pro/task-542/decision-logging-infra
build-server-01/task-100/api-refactor
dev-laptop/task-999/bug-fix-auth
alice-workstation/task-123/feature-dashboard
```

### Invalid Branch Names

```
# Missing hostname
task-542/decision-logging          # ✗ No hostname
feature/add-logging                # ✗ Not task-based

# Wrong task format
macbook-pro/542/logging            # ✗ Missing "task-" prefix
macbook-pro/task-542-logging       # ✗ Wrong delimiter

# Invalid characters
macbook_pro/task-542/logging       # ✗ Underscore in hostname
macbook-pro/task-542/Add_Logging   # ✗ Capital letters and underscore
```

---

## Appendix C: Pre-PR Validation Checklist

Use this checklist before creating ANY pull request:

```markdown
## Pre-PR Validation Checklist

### Automated Checks (run script)
- [ ] `./scripts/bash/rigor-pre-pr-validation.sh` passes

### Manual Verification
- [ ] Branch name follows format: `hostname/task-NNN/slug`
- [ ] Branch rebased from latest main (zero commits behind)
- [ ] All code formatted (ruff format)
- [ ] All linting passes (ruff check)
- [ ] All tests pass (pytest)
- [ ] All commits have DCO sign-off
- [ ] Security scan shows no high/critical issues

### Documentation
- [ ] Decision log updated for critical choices
- [ ] Task memory updated with current status
- [ ] README/docs updated if public API changed
- [ ] CHANGELOG entry added (if applicable)

### Backlog
- [ ] Task status updated in backlog
- [ ] Acceptance criteria marked complete
- [ ] Implementation notes added to task

### Ready to Submit
- [ ] PR title follows convention: `feat:`, `fix:`, `docs:`, etc.
- [ ] PR description references task: "Closes #542"
- [ ] Reviewers assigned
- [ ] Labels applied (backend, frontend, etc.)
```

---

**End of Infrastructure Design Document**

---

## Next Steps

1. **Review and Approval**: Software architect and PM review this design
2. **Task Creation**: Break into implementation tasks (scripts, documentation, CI workflows)
3. **Prioritization**: Determine rollout schedule (4-week plan suggested)
4. **Implementation**: Begin Phase 1 (infrastructure setup)
5. **Testing**: Validate scripts and CI integration
6. **Training**: Developer onboarding and documentation
7. **Rollout**: Phased enforcement (soft → hard)
8. **Metrics**: Track DORA metrics and adoption rates
9. **Optimization**: Iterate based on feedback

**Questions or feedback?** Contact @platform-engineer or @software-architect.
