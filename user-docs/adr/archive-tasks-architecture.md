# Architecture Document: archive-tasks.sh Script

**Author**: Enterprise Software Architect (Hohpe Principles)
**Date**: 2025-12-03
**Status**: Proposed
**Related Task**: task-281

## Executive Summary (Penthouse View)

### Business Objectives

This script addresses a critical operational gap in the Spec-Driven Development (SDD) workflow automation: **selective backlog archival based on configurable criteria**. While the existing `flush-backlog.sh` provides basic archival of "Done" tasks, enterprise-grade workflow automation requires more sophisticated lifecycle management.

**Value Proposition:**
- **Reduced Manual Effort**: Automate routine backlog maintenance that would otherwise require manual CLI invocation
- **Enhanced Automation Flexibility**: Enable agent hooks and CI/CD pipelines to archive tasks based on business rules (e.g., "archive tasks completed more than 30 days ago")
- **Improved Workflow Hygiene**: Prevent backlog bloat by systematically archiving stale tasks across all statuses
- **Operational Consistency**: Standardize archival policies across teams and projects through scriptable automation

**Organizational Impact:**
- Integrates into existing agent hook infrastructure (`.claude/hooks/`)
- Enables time-based retention policies for compliance/auditing
- Supports automated cleanup in CI/CD workflows
- Reduces cognitive load by maintaining focused, current backlogs

### Investment Justification

**Development Cost**: ~4-6 hours (initial implementation + testing)
**Maintenance Cost**: Minimal (follows established script patterns)
**Risk**: Low (non-destructive operation, dry-run capability, exit code strategy)
**ROI**: High (enables automation scenarios currently requiring manual intervention)

This is a **force multiplier** for SDD workflow adoption—automation that removes friction accelerates value delivery.

---

## Architectural Blueprint (Engine Room View)

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    SDD Workflow System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Agent Hooks         CI/CD Pipelines      Manual Execution  │
│      │                     │                     │           │
│      └─────────────────────┴─────────────────────┘           │
│                            │                                 │
│                            ▼                                 │
│                  ┌──────────────────────┐                   │
│                  │  archive-tasks.sh    │                   │
│                  └──────────┬───────────┘                   │
│                             │                                │
│              ┌──────────────┼──────────────┐                │
│              │              │              │                │
│              ▼              ▼              ▼                │
│      ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│      │Date      │   │Task      │   │Archive   │           │
│      │Parser    │   │Filter    │   │Executor  │           │
│      └──────────┘   └──────────┘   └──────────┘           │
│              │              │              │                │
│              └──────────────┼──────────────┘                │
│                             ▼                                │
│                  ┌──────────────────────┐                   │
│                  │  backlog CLI         │                   │
│                  │  (Integration Point) │                   │
│                  └──────────────────────┘                   │
│                             │                                │
│                             ▼                                │
│                  ┌──────────────────────┐                   │
│                  │  backlog/tasks/*.md  │                   │
│                  │  backlog/archive/    │                   │
│                  └──────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Command-Line Interface Layer

**Responsibility**: Parse user intent and validate inputs

**Parameters:**
```bash
archive-tasks.sh [OPTIONS]

OPTIONS:
  -a, --all              Archive ALL tasks regardless of status
  --done-by <DATE>       Archive tasks with status=Done and updated_date <= DATE
  --dry-run              Preview actions without executing
  --help, -h             Show usage information

DATE FORMAT: ISO 8601 (YYYY-MM-DD)
```

**Design Constraints:**
- `-a/--all` is mutually exclusive with `--done-by` (error if both specified)
- Default behavior (no flags): Archive only Done tasks (legacy compatibility)
- Date format validation occurs at parse time (fail-fast principle)

#### 2. Date Processing Component

**Responsibility**: Parse and validate date inputs, provide comparison capability

**Functions:**
```bash
validate_date_format() {
  # Input: $1 = date string (YYYY-MM-DD)
  # Output: 0 if valid, 1 if invalid
  # Side Effect: Prints error message on failure
}

date_to_epoch() {
  # Input: $1 = date string (YYYY-MM-DD)
  # Output: Unix epoch seconds (for comparison)
  # Dependency: GNU date command
}

is_date_on_or_before() {
  # Input: $1 = task_date, $2 = cutoff_date
  # Output: 0 if task_date <= cutoff_date, 1 otherwise
}
```

**Platform Consideration:**
- Primary target: GNU date (Linux)
- Fallback strategy: Pure bash date parsing if `date` unavailable
- Error handling: Validate date command availability in prerequisites

#### 3. Task Discovery and Filtering Component

**Responsibility**: Query backlog and filter tasks based on criteria

**Functions:**
```bash
get_tasks_by_criteria() {
  # Input: filter_mode (all | done | done-by-date), optional cutoff_date
  # Output: Task IDs, one per line
  # Strategy: Query all, filter in-script (see ADR-001)
}

extract_task_metadata() {
  # Input: $1 = task_id
  # Output: Associative array with id, status, updated_date
  # Data Source: Task file YAML frontmatter
}

parse_yaml_frontmatter() {
  # Input: $1 = task file path
  # Output: Key-value pairs (status, updated_date)
  # Implementation: grep/sed (no external YAML parser dependency)
}
```

**Data Flow:**
1. Query backlog CLI: `backlog task list --plain` (all tasks)
2. For each task:
   - Read task file frontmatter
   - Extract `status` and `updated_date` fields
   - Apply filter criteria
3. Return filtered task IDs

**Rationale**: See ADR-001 for filter strategy decision

#### 4. Archive Execution Component

**Responsibility**: Archive tasks via backlog CLI, track results

**Functions:**
```bash
archive_task() {
  # Input: $1 = task_id
  # Output: 0 if successful, 1 if failed
  # Side Effect: Increments counters, records failures
  # Dry-run: Print action, don't execute
}

archive_batch() {
  # Input: Array of task_ids
  # Output: None
  # Side Effect: Calls archive_task for each ID, collects statistics
}
```

**Error Handling:**
- Continue on individual failures (don't abort entire batch)
- Track failed tasks in array
- Return exit code 3 if any failures occurred

#### 5. Statistics and Reporting Component

**Responsibility**: Display results and generate reports

**Functions:**
```bash
print_summary() {
  # Input: total_tasks, archived_count, failed_count
  # Output: Formatted summary to stdout
}

generate_completion_report() {
  # Input: Task metadata array
  # Output: Optional markdown report file
  # Trigger: --report flag (future enhancement)
}
```

---

## Architecture Decision Records

### ADR-001: Filter Strategy - Query All Then Filter vs. CLI Native Filtering

**Context:**
The backlog CLI provides `--status` filtering but no date-based filtering. We need to archive tasks by completion date.

**Decision:**
Query all tasks via CLI, then filter in-script by parsing task file frontmatter.

**Options Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **CLI Query + Script Filter** | Full control over filter logic; supports complex date comparisons; can evolve independently of CLI | Reads all task files; O(n) complexity |
| **Extend Backlog CLI** | Potentially more efficient; centralized logic | Requires CLI changes; tight coupling; deployment dependency |
| **Multiple CLI Queries** | Uses existing CLI capabilities | No date filtering in CLI; would require status-by-status queries |

**Rationale:**
- **Decoupling**: Script evolution independent of CLI roadmap
- **Flexibility**: Easy to add new filter criteria (e.g., labels, assignee)
- **Performance Acceptable**: Typical backlogs have <1000 active tasks; parsing YAML frontmatter is fast
- **Maintainability**: All filtering logic in one place (script)

**Consequences:**
- Script must parse YAML frontmatter (simple grep/sed sufficient)
- Performance scales linearly with task count (acceptable for target scale)
- Future CLI enhancements can replace internal filtering if needed

**Status**: Accepted

---

### ADR-002: Date Parsing - GNU date vs. Pure Bash

**Context:**
Need to parse ISO 8601 dates and compare them. GNU `date` command provides rich date manipulation, but may not be available in all environments.

**Decision:**
Use GNU `date` command as primary implementation with validation in prerequisites.

**Options Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **GNU date Command** | Simple, reliable, handles edge cases (leap years, timezones); one-liner conversions | Linux-specific; not POSIX; requires external binary |
| **Pure Bash Parsing** | No external dependencies; fully portable | Complex, error-prone; must handle calendar logic; ~50 lines of code |
| **Python Helper** | Robust date handling; already a project dependency | Adds subprocess overhead; heavier solution |

**Rationale:**
- **Target Platform**: Linux (Ubuntu 22.04/24.04) - GNU date guaranteed available
- **Simplicity**: `date -d "$date_str" +%s` is trivial vs. complex bash arithmetic
- **Error Handling**: GNU date validates dates (e.g., "2025-02-30" fails)
- **Maintainability**: Standard tool vs. custom calendar logic
- **Precedent**: Existing scripts (`flush-backlog.sh`) use `date` command

**Implementation:**
```bash
check_prerequisites() {
    if ! command -v date &> /dev/null; then
        print_color "${RED}" "ERROR: date command not found"
        return 1
    fi

    # Verify GNU date (Linux) - try parsing a date
    if ! date -d "2025-01-01" +%s &> /dev/null; then
        print_color "${RED}" "ERROR: GNU date required (BSD date not supported)"
        print_color "${YELLOW}" "Install coreutils: apt-get install coreutils"
        return 1
    fi
}
```

**Consequences:**
- Script explicitly requires GNU date (documented in prerequisites)
- Clear error message if running on BSD systems (macOS)
- Future enhancement: Add BSD date compatibility layer if needed

**Status**: Accepted

---

### ADR-003: Relationship to flush-backlog.sh - Complement vs. Replace

**Context:**
`flush-backlog.sh` archives Done tasks and generates summary reports. Should `archive-tasks.sh` replace it or complement it?

**Decision:**
**Complement** - Maintain both scripts with distinct purposes.

**Comparison:**

| Feature | flush-backlog.sh | archive-tasks.sh |
|---------|------------------|------------------|
| **Purpose** | End-of-sprint cleanup + reporting | Flexible archival automation |
| **Filter** | Done tasks only | All tasks or date-based |
| **Report** | Detailed summary with statistics | Minimal output (automation-focused) |
| **Use Case** | Manual execution, sprint ceremonies | Agent hooks, CI/CD, automated maintenance |
| **Flags** | `--auto-commit`, `--no-summary` | `--all`, `--done-by DATE` |

**Rationale:**
- **Different User Personas**: flush-backlog.sh targets human operators (sprint masters); archive-tasks.sh targets automation (CI/CD, agents)
- **Report Semantics**: flush-backlog.sh generates business-meaningful summaries (what was accomplished); archive-tasks.sh is operational (what was cleaned up)
- **Migration Path**: Users can continue current workflows; archive-tasks.sh enables new scenarios
- **Composability**: Could call archive-tasks.sh from flush-backlog.sh in future

**Long-term Vision:**
```bash
# Human-friendly sprint cleanup
./scripts/bash/flush-backlog.sh --auto-commit

# Automated retention policy (in cron/CI)
./scripts/bash/archive-tasks.sh --done-by $(date -d '30 days ago' +%Y-%m-%d)

# Aggressive cleanup (testing/demo environments)
./scripts/bash/archive-tasks.sh --all
```

**Status**: Accepted

---

## Platform Quality Assessment (7 C's)

### 1. Clarity

**Score: ✅ High**

- **Vision**: Clear purpose as automation enabler for selective archival
- **Boundaries**: Well-defined scope (filtering + archiving, not reporting)
- **API**: Simple, orthogonal flags (`-a` XOR `--done-by`, plus `--dry-run`)

**Improvements:**
- Document integration points (agent hooks, CI/CD examples)
- Provide example retention policies

### 2. Consistency

**Score: ✅ High**

- **Follows Conventions**: Mirrors `flush-backlog.sh` structure (check_prerequisites, colored output, exit codes)
- **Naming**: Consistent with project naming (kebab-case, scripts/bash/)
- **Patterns**: Uses established backlog CLI integration patterns

**Evidence:**
```bash
# Same structure as flush-backlog.sh
check_prerequisites()
print_color()
main()
show_help()

# Same CLI integration
backlog task list --plain
backlog task archive "$task_id"
```

### 3. Compliance

**Score: ✅ High**

- **Bash Best Practices**: `set -euo pipefail`, proper quoting, error handling
- **Exit Codes**: Standard POSIX conventions (0=success, 1=error, 2=no-op, 3=partial)
- **Security**: No credential handling, read-only operations (archive via CLI), dry-run safety

**Compliance Checklist:**
- [x] Shebang: `#!/usr/bin/env bash`
- [x] Error handling: `set -euo pipefail`
- [x] Input validation: Date format, mutual exclusivity
- [x] Dry-run capability: Non-destructive preview
- [x] Help documentation: `--help` flag

### 4. Composability

**Score: ✅ High**

- **Unix Philosophy**: Does one thing well (filter + archive)
- **Chainable**: Stdout output suitable for piping
- **Exit Codes**: Enables conditional logic in scripts

**Composition Examples:**
```bash
# Chain with flush-backlog.sh
if ./scripts/bash/archive-tasks.sh --done-by 2025-11-01; then
    ./scripts/bash/flush-backlog.sh --no-summary
fi

# Use in agent hooks
# .claude/hooks/post-commit.sh
archive-tasks.sh --done-by $(date -d '7 days ago' +%Y-%m-%d) || true

# CI/CD integration
- name: Archive old tasks
  run: ./scripts/bash/archive-tasks.sh --done-by $(date -d '30 days ago' +%Y-%m-%d)
  continue-on-error: true
```

### 5. Coverage

**Score: ✅ High**

- **All Acceptance Criteria Met**: See AC mapping below
- **Edge Cases Handled**: Invalid dates, no matching tasks, partial failures
- **Platform Support**: Linux (primary), documented prerequisites

**Coverage Matrix:**

| Scenario | Supported | Test Strategy |
|----------|-----------|---------------|
| Archive all tasks | ✅ `-a` flag | Integration test |
| Archive by date | ✅ `--done-by` | Integration test |
| Dry-run preview | ✅ `--dry-run` | Verify no changes |
| Invalid date | ✅ Validation | Unit test |
| No matches | ✅ Exit code 2 | Integration test |
| Partial failure | ✅ Exit code 3 | Mock CLI failure |

### 6. Consumption (Developer Experience)

**Score: ✅ High**

- **Intuitive Flags**: Self-explanatory (`--all`, `--done-by`, `--dry-run`)
- **Error Messages**: Clear, actionable (e.g., "Invalid date format: 2025-13-01. Expected: YYYY-MM-DD")
- **Help Text**: Comprehensive with examples
- **No Configuration**: Zero-config operation (uses backlog CLI defaults)

**DX Enhancements:**
```bash
# Example help output
archive-tasks.sh - Archive backlog tasks with flexible filtering

USAGE:
    ./scripts/bash/archive-tasks.sh [OPTIONS]

OPTIONS:
    -a, --all           Archive ALL tasks (To Do, In Progress, Done, Blocked)
    --done-by <DATE>    Archive Done tasks updated on or before DATE (YYYY-MM-DD)
    --dry-run           Preview actions without making changes
    --help, -h          Show this help message

EXAMPLES:
    # Preview archiving all tasks
    ./scripts/bash/archive-tasks.sh --all --dry-run

    # Archive tasks completed before December 1st
    ./scripts/bash/archive-tasks.sh --done-by 2025-12-01

    # Archive tasks from 30 days ago
    ./scripts/bash/archive-tasks.sh --done-by $(date -d '30 days ago' +%Y-%m-%d)
```

### 7. Credibility

**Score: ✅ High**

- **Reliability**: Leverages proven backlog CLI (battle-tested)
- **Safety**: Dry-run mode, continue-on-error semantics, reversible operation (archived tasks can be unarchived)
- **Transparency**: Verbose output, statistics, exit codes
- **Trust**: Follows established script patterns (`flush-backlog.sh` as proof of concept)

**Trust Markers:**
- Dry-run flag for safety
- Clear statistics ("Archived 5 of 7 tasks, 2 failed")
- Reversible operation (archive, not delete)
- Exit codes enable error handling

---

## Implementation Recommendations

### Script Structure

```bash
#!/usr/bin/env bash
set -euo pipefail

# archive-tasks.sh - Archive backlog tasks with flexible filtering
# Usage: ./scripts/bash/archive-tasks.sh [--all | --done-by DATE] [--dry-run]

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKLOG_DIR="backlog"
TASKS_DIR="${BACKLOG_DIR}/tasks"

# Flags
ARCHIVE_ALL=false
DONE_BY_DATE=""
DRY_RUN=false

# Statistics
TOTAL_MATCHED=0
TOTAL_ARCHIVED=0
FAILED_TASKS=()

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_color() { ... }       # From flush-backlog.sh
show_help() { ... }          # Usage documentation
check_prerequisites() { ... } # Validate date, backlog CLI

# ============================================================================
# DATE PROCESSING
# ============================================================================

validate_date_format() {
    local date_str="$1"

    # Validate format (YYYY-MM-DD)
    if ! [[ "$date_str" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        print_color "${RED}" "ERROR: Invalid date format: ${date_str}"
        print_color "${RED}" "Expected: YYYY-MM-DD (e.g., 2025-12-03)"
        return 1
    fi

    # Validate date is real (handles Feb 30, etc.)
    if ! date -d "$date_str" +%s &> /dev/null; then
        print_color "${RED}" "ERROR: Invalid date: ${date_str}"
        return 1
    fi

    return 0
}

date_to_epoch() {
    date -d "$1" +%s
}

is_date_on_or_before() {
    local task_date="$1"
    local cutoff_date="$2"

    local task_epoch
    local cutoff_epoch

    task_epoch=$(date_to_epoch "$task_date") || return 1
    cutoff_epoch=$(date_to_epoch "$cutoff_date") || return 1

    [[ "$task_epoch" -le "$cutoff_epoch" ]]
}

# ============================================================================
# TASK FILTERING
# ============================================================================

extract_frontmatter_field() {
    local task_file="$1"
    local field="$2"

    # Extract field from YAML frontmatter (between --- delimiters)
    # Example: "updated_date: '2025-12-01 04:09'" -> "2025-12-01"
    grep -E "^${field}:" "$task_file" | \
        sed -E "s/^${field}:[[:space:]]*'?([^']*)'?.*/\1/" | \
        cut -d' ' -f1
}

get_tasks_by_criteria() {
    local filter_mode="$1"  # all | done | done-by-date
    local cutoff_date="${2:-}"
    local task_ids=()

    # Get all task files
    local task_files=("${PROJECT_ROOT}/${TASKS_DIR}"/task-*.md)

    for task_file in "${task_files[@]}"; do
        [[ ! -f "$task_file" ]] && continue

        local task_id
        task_id=$(basename "$task_file" .md | grep -oE 'task-[0-9]+')

        # Apply filter based on mode
        case "$filter_mode" in
            all)
                task_ids+=("$task_id")
                ;;
            done)
                local status
                status=$(extract_frontmatter_field "$task_file" "status")
                [[ "$status" == "Done" ]] && task_ids+=("$task_id")
                ;;
            done-by-date)
                local status updated_date
                status=$(extract_frontmatter_field "$task_file" "status")
                updated_date=$(extract_frontmatter_field "$task_file" "updated_date")

                if [[ "$status" == "Done" ]] && is_date_on_or_before "$updated_date" "$cutoff_date"; then
                    task_ids+=("$task_id")
                fi
                ;;
        esac
    done

    printf '%s\n' "${task_ids[@]}"
}

# ============================================================================
# ARCHIVE EXECUTION
# ============================================================================

archive_task() {
    local task_id="$1"
    local numeric_id="${task_id#task-}"

    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "  [DRY RUN] Would archive: ${task_id}"
        return 0
    fi

    local output
    if output=$(cd "${PROJECT_ROOT}" && backlog task archive "${numeric_id}" 2>&1); then
        if [[ "$output" =~ [Aa]rchived ]]; then
            print_color "${GREEN}" "  ✓ Archived: ${task_id}"
            ((TOTAL_ARCHIVED++))
            return 0
        fi
    fi

    print_color "${RED}" "  ✗ Failed to archive: ${task_id}"
    FAILED_TASKS+=("${task_id}")
    return 1
}

# ============================================================================
# MAIN FUNCTION
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -a|--all)
                ARCHIVE_ALL=true
                shift
                ;;
            --done-by)
                DONE_BY_DATE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                print_color "${RED}" "ERROR: Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate mutually exclusive flags
    if [[ "$ARCHIVE_ALL" == true && -n "$DONE_BY_DATE" ]]; then
        print_color "${RED}" "ERROR: --all and --done-by are mutually exclusive"
        exit 1
    fi

    # Validate date if provided
    if [[ -n "$DONE_BY_DATE" ]]; then
        validate_date_format "$DONE_BY_DATE" || exit 1
    fi

    # Check prerequisites
    check_prerequisites || exit 1

    # Determine filter mode
    local filter_mode
    if [[ "$ARCHIVE_ALL" == true ]]; then
        filter_mode="all"
        print_color "${BLUE}" "==> Archiving ALL tasks..."
    elif [[ -n "$DONE_BY_DATE" ]]; then
        filter_mode="done-by-date"
        print_color "${BLUE}" "==> Archiving Done tasks completed on or before ${DONE_BY_DATE}..."
    else
        filter_mode="done"
        print_color "${BLUE}" "==> Archiving Done tasks..."
    fi

    # Get tasks to archive
    local task_ids=()
    mapfile -t task_ids < <(get_tasks_by_criteria "$filter_mode" "$DONE_BY_DATE")
    TOTAL_MATCHED=${#task_ids[@]}

    if [[ $TOTAL_MATCHED -eq 0 ]]; then
        print_color "${YELLOW}" "No tasks matched criteria."
        exit 2
    fi

    print_color "${GREEN}" "Found ${TOTAL_MATCHED} task(s) matching criteria"

    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN MODE - No changes will be made"
    fi

    # Archive tasks
    for task_id in "${task_ids[@]}"; do
        archive_task "$task_id" || true
    done

    # Print summary
    echo ""
    if [[ "$DRY_RUN" == true ]]; then
        print_color "${YELLOW}" "==> DRY RUN completed"
        print_color "${YELLOW}" "Would archive ${TOTAL_MATCHED} task(s)"
        exit 0
    fi

    if [[ ${#FAILED_TASKS[@]} -gt 0 ]]; then
        print_color "${RED}" "==> Completed with errors"
        print_color "${RED}" "Successfully archived: ${TOTAL_ARCHIVED}"
        print_color "${RED}" "Failed to archive: ${#FAILED_TASKS[@]} (${FAILED_TASKS[*]})"
        exit 3
    else
        print_color "${GREEN}" "==> Successfully archived ${TOTAL_ARCHIVED} task(s)"
        exit 0
    fi
}

main "$@"
```

### Testing Strategy

#### Unit Tests (via BATS or manual testing)

1. **Date Validation**
   - Valid dates: `2025-12-03`, `2025-01-01`, `2025-12-31`
   - Invalid formats: `12-03-2025`, `2025/12/03`, `03-12-2025`
   - Invalid dates: `2025-02-30`, `2025-13-01`, `2025-00-01`

2. **Date Comparison**
   - Equal dates: `2025-12-03 <= 2025-12-03` → true
   - Before: `2025-12-01 <= 2025-12-03` → true
   - After: `2025-12-05 <= 2025-12-03` → false

3. **YAML Frontmatter Parsing**
   - Extract `status: Done` correctly
   - Extract `updated_date: '2025-12-01 04:09'` → `2025-12-01`
   - Handle missing fields gracefully

#### Integration Tests

1. **Filter Modes**
   - `--all`: Archives tasks in all statuses (To Do, In Progress, Done)
   - `--done-by 2025-12-01`: Archives only Done tasks updated before/on Dec 1
   - No flags: Archives only Done tasks (default)

2. **Dry Run**
   - Verify no task files are moved to archive/
   - Verify correct output ("Would archive X tasks")
   - Verify exit code 0

3. **Error Handling**
   - Invalid date format → exit code 1
   - No matching tasks → exit code 2
   - Partial failure (mock CLI error) → exit code 3

4. **Edge Cases**
   - Empty backlog → exit code 2
   - All tasks already archived → exit code 2
   - Mutually exclusive flags → exit code 1

#### Manual Testing Checklist

```bash
# 1. Create test environment
cd /home/jpoley/ps/flowspec
git worktree add /tmp/archive-test-env main
cd /tmp/archive-test-env

# 2. Test dry-run
./scripts/bash/archive-tasks.sh --all --dry-run
# Expected: Lists tasks, no changes

# 3. Test date filtering
./scripts/bash/archive-tasks.sh --done-by 2025-11-01 --dry-run
# Expected: Only tasks completed before Nov 1

# 4. Test invalid date
./scripts/bash/archive-tasks.sh --done-by 2025-13-01
# Expected: Error message, exit code 1

# 5. Test mutual exclusivity
./scripts/bash/archive-tasks.sh --all --done-by 2025-12-01
# Expected: Error message, exit code 1

# 6. Test actual archival
./scripts/bash/archive-tasks.sh --done-by 2025-11-01
# Expected: Tasks archived, exit code 0

# 7. Cleanup
cd /home/jpoley/ps/flowspec
git worktree remove /tmp/archive-test-env
```

### Agent Hook Integration Example

**File**: `.claude/hooks/post-commit.sh`

```bash
#!/usr/bin/env bash
# Post-commit hook - Archive old tasks after successful commits

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Archive tasks completed more than 7 days ago
CUTOFF_DATE=$(date -d '7 days ago' +%Y-%m-%d)

"${PROJECT_ROOT}/scripts/bash/archive-tasks.sh" --done-by "$CUTOFF_DATE" --dry-run

# Only archive if dry-run shows matches
if [[ $? -eq 0 ]]; then
    echo "Auto-archiving tasks completed before ${CUTOFF_DATE}..."
    "${PROJECT_ROOT}/scripts/bash/archive-tasks.sh" --done-by "$CUTOFF_DATE" || true
fi
```

### CI/CD Integration Example

**File**: `.github/workflows/weekly-maintenance.yml`

```yaml
name: Weekly Backlog Maintenance

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
  workflow_dispatch:

jobs:
  archive-old-tasks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install backlog CLI
        run: npm install -g @backlog-md/cli

      - name: Archive tasks completed >30 days ago
        run: |
          CUTOFF_DATE=$(date -d '30 days ago' +%Y-%m-%d)
          ./scripts/bash/archive-tasks.sh --done-by "$CUTOFF_DATE"
        continue-on-error: true

      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add backlog/
          git commit -m "chore(backlog): auto-archive tasks >30 days old" || echo "No changes"
          git push
```

---

## Acceptance Criteria Mapping

| AC # | Requirement | Implementation | Status |
|------|-------------|----------------|--------|
| #1 | Script accepts -a/--all flag to archive ALL tasks | `ARCHIVE_ALL` flag, `filter_mode="all"` | ✅ |
| #2 | Script accepts --done-by DATE flag | `DONE_BY_DATE` parameter, `filter_mode="done-by-date"` | ✅ |
| #3 | Date parsing handles ISO 8601 format | `validate_date_format()` with regex check | ✅ |
| #4 | Validates date format with clear errors | Error messages in `validate_date_format()` | ✅ |
| #5 | Supports --dry-run flag | `DRY_RUN` flag, preview mode in `archive_task()` | ✅ |
| #6 | Integrates with backlog CLI | `backlog task archive` calls | ✅ |
| #7 | Follows existing script conventions | Mirrors `flush-backlog.sh` structure | ✅ |
| #8 | Returns appropriate exit codes | 0=success, 1=error, 2=no matches, 3=partial | ✅ |
| #9 | Documentation includes examples | `show_help()`, hook/CI examples | ✅ |

---

## Option Value Analysis (Hohpe's Option Theory)

### Architectural Options Created

This script **sells options** by enabling future capabilities without forcing commitment:

1. **Retention Policy Option**
   - **Strike Price**: Implementation of configurable retention policies (e.g., YAML config)
   - **Volatility**: Organizational requirements may change (compliance, auditing)
   - **Value**: Script provides foundation; can extend to read config file for retention rules

2. **Reporting Option**
   - **Strike Price**: Enhanced reporting (similar to flush-backlog.sh summaries)
   - **Volatility**: User feedback may demand audit trails
   - **Value**: Architecture supports adding `--report` flag with minimal refactoring

3. **Filter Extension Option**
   - **Strike Price**: Additional filter criteria (labels, assignee, priority)
   - **Volatility**: Unknown future automation needs
   - **Value**: `get_tasks_by_criteria()` designed for easy extension

### Technical Debt Avoided

- **Decoupling from CLI**: Independent evolution paths (ADR-001)
- **Composable Design**: Can chain with other scripts without modification
- **Dry-run Safety**: Experimentation without risk

### Volatility Management

**High Volatility Areas** (invest more in architecture):
- Filter criteria (likely to expand) → Clean abstraction in `get_tasks_by_criteria()`
- Date handling (may need timezone support) → Isolated in date functions

**Low Volatility Areas** (pragmatic implementation):
- Output formatting (stable) → Reuse from flush-backlog.sh
- CLI integration (stable) → Simple subprocess calls

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **GNU date unavailable** | Low | High | Prerequisites check, clear error message |
| **Malformed task files** | Medium | Low | Defensive parsing, skip invalid files |
| **Backlog CLI changes** | Low | Medium | Integration tests, version pinning |
| **Date parsing edge cases** | Low | Low | GNU date handles complexity |
| **Performance (1000+ tasks)** | Low | Low | Linear O(n) acceptable for target scale |

---

## Conclusion

This architecture delivers a **production-grade automation tool** that:

1. **Solves Immediate Need**: Enables selective archival for agent hooks and CI/CD
2. **Maintains Consistency**: Follows established patterns and conventions
3. **Enables Future Options**: Extensible design for retention policies, reporting, filters
4. **Minimizes Risk**: Dry-run capability, defensive error handling, reversible operations
5. **Promotes Automation**: Unlocks new workflow automation scenarios

**Recommended Next Steps:**
1. Implement script following structure above
2. Add integration tests (create test tasks, archive, verify)
3. Document agent hook integration in `docs/guides/agent-hooks.md`
4. Consider adding `--report` flag in future iteration based on user feedback

---

**Architectural Principle Applied:**
> "Good architecture maximizes the number of decisions not made." — Robert C. Martin

This script defers decisions on retention policies, reporting formats, and filter extensions while providing a solid foundation for all scenarios.
