# ADR-003: Branch Naming Convention

**Status**: Proposed
**Date**: 2025-12-17
**Decision Maker**: Software Architect
**Stakeholders**: Engineering Team, DevOps, Release Management

## Context

The Rigor Rules system needs a standardized branch naming convention that enables:
1. **Task Traceability**: Link branches to backlog tasks automatically
2. **Multi-Developer Collaboration**: Prevent branch name conflicts in teams
3. **Automation**: Extract task IDs, feature names from branch names
4. **Discoverability**: Understand branch purpose from name alone
5. **Workspace Isolation**: Support git worktrees with matching names

### Problem Statement

How should we name branches to balance:
- **Uniqueness**: No collisions in multi-developer teams
- **Traceability**: Automatic task ID extraction
- **Readability**: Human-understandable purpose
- **Automation-Friendly**: Parseable by scripts
- **Length**: Not too long (git branch name limit is 255 chars)

### Current State

Flowspec projects currently have inconsistent branch naming:
```
main
feature/user-auth
fix/login-bug
jpoley-add-validation
task-123
implement-oauth
```

**Problems**:
- No task ID → Can't link to backlog automatically
- No developer identification → Conflicts when multiple devs work on similar features
- Inconsistent format → Hard to parse with scripts
- No slug → Can't understand purpose from name alone

### Alternatives Considered

#### Option 1: Conventional Commits Style
**Format**: `<type>/<description>`

**Examples**:
```
feat/user-authentication
fix/login-validation
refactor/database-layer
```

**Pros**:
- Industry standard (widely adopted)
- Clear type prefix (feat, fix, refactor, docs)
- Human-readable

**Cons**:
- No task traceability (can't extract task ID)
- No developer identification (name conflicts in teams)
- No hostname (can't identify machine)
- Requires manual workaround for task linking

**Verdict**: Rejected due to lack of task traceability.

---

#### Option 2: Task ID Only
**Format**: `task-<id>`

**Examples**:
```
task-123
task-456
task-789
```

**Pros**:
- Maximum traceability (task ID is the entire branch name)
- Easy to parse (`git branch --show-current`)
- Short (minimal typing)

**Cons**:
- No human-readable context (must look up task to understand purpose)
- No developer identification (conflicts if two devs work on same task)
- No hostname (can't identify machine in multi-machine workflows)
- Git worktree names don't match (worktree: `task-123`, branch: `task-123` → naming confusion)

**Verdict**: Rejected due to lack of context and developer identification.

---

#### Option 3: Developer/Task/Description
**Format**: `<developer>/<task-id>/<slug-description>`

**Examples**:
```
jpoley/task-123/add-user-authentication
alice/task-456/fix-login-bug
bob/task-789/refactor-database
```

**Pros**:
- Developer identification (no name conflicts)
- Task traceability (extract `task-123`)
- Human-readable (slug describes purpose)
- Git worktree compatible (worktree: `jpoley-task-123-add-user-authentication`)

**Cons**:
- Uses developer name (not hostname)
  - Problem: Same developer, different machines → no distinction
  - Example: `jpoley` works on both laptop and desktop → confusion
- Length can be long (developer + task + slug = 50+ chars)

**Verdict**: Close, but hostname is better than developer name for machine isolation.

---

#### Option 4: Hostname/Task/Description (SELECTED)
**Format**: `<hostname>/task-<id>/<slug-description>`

**Examples**:
```
laptop-jpoley/task-123/add-user-authentication
desktop-alice/task-456/fix-login-bug
server-bob/task-789/refactor-database
```

**Pros**:
- **Machine identification**: Each machine has unique hostname → zero branch conflicts
- **Task traceability**: Easy to extract `task-123` from branch name
- **Human-readable**: Slug describes purpose
- **Git worktree compatible**: Worktree name matches branch name
- **Automation-friendly**: Regex `hostname/task-(\d+)/(.+)` extracts all parts
- **Multi-machine workflows**: Same developer, different machines → no confusion

**Cons**:
- Hostname may be long (e.g., `developers-macbook-pro-2023`)
  - **Mitigation**: Use short hostname alias (e.g., `mbp2023`)
- Non-standard (not widely adopted in industry)
  - **Mitigation**: Document clearly, provide helper scripts

**Verdict**: **SELECTED** - Best balance of traceability, machine isolation, and readability.

---

#### Option 5: ISO Date Prefix
**Format**: `<date>/<developer>/<task-id>/<slug>`

**Examples**:
```
2025-12-17/jpoley/task-123/add-user-auth
2025-12-18/alice/task-456/fix-login-bug
```

**Pros**:
- Time-based grouping (branches sorted by date)
- All benefits of Option 3

**Cons**:
- Very long (date adds 10 chars)
- Date is low-value information (git commit dates are sufficient)
- Hard to parse (4 slashes, complex regex)

**Verdict**: Rejected due to excessive length and complexity.

---

## Decision

**We will adopt the `<hostname>/task-<id>/<slug-description>` branch naming convention.**

### Format Specification

```
<hostname>/task-<id>/<slug-description>

Where:
  <hostname>       = lowercase alphanumeric + hyphens (a-z0-9-), no underscores
  task-<id>        = literal "task-" followed by numeric ID (task-123, task-456)
  <slug-description> = lowercase kebab-case description (a-z0-9-), max 50 chars
```

### Examples

**Valid**:
```
laptop-jpoley/task-123/add-user-authentication
desktop-alice/task-456/fix-login-validation-bug
server-bob/task-789/refactor-database-layer
mbp/task-100/implement-oauth-flow
```

**Invalid**:
```
LAPTOP-JPOLEY/task-123/add-user-auth   # Uppercase (must be lowercase)
laptop_jpoley/task-123/add-user-auth   # Underscore (must be hyphen)
laptop-jpoley/123/add-user-auth        # Missing "task-" prefix
laptop-jpoley/task-123/Add-User-Auth   # Mixed case (must be lowercase)
laptop-jpoley/task-123/add_user_auth   # Underscore (must be hyphen)
laptop-jpoley/task-abc/add-user-auth   # Non-numeric ID (must be digits)
```

### Regex Validation

```bash
# Branch name validation regex
^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$
```

```bash
# Extract task ID
git branch --show-current | grep -oP 'task-\d+'
# Output: task-123

# Extract slug
git branch --show-current | awk -F'/' '{print $3}'
# Output: add-user-authentication

# Extract hostname
git branch --show-current | awk -F'/' '{print $1}'
# Output: laptop-jpoley
```

### Primary Reasons

1. **Machine Isolation**: Each machine has a unique hostname, preventing branch conflicts even when the same developer works on multiple machines.

   **Scenario**: Developer `jpoley` works on laptop and desktop simultaneously:
   ```
   laptop-jpoley/task-123/add-user-auth
   desktop-jpoley/task-123/add-user-auth
   ```

   No conflict - different hostnames create distinct branches.

2. **Task Traceability**: The `task-<id>` component enables automatic linkage:
   ```bash
   # Extract task ID from current branch
   TASK_ID=$(git branch --show-current | grep -oP 'task-\d+')

   # View task details
   backlog task "$TASK_ID" --plain

   # Log decision to task-specific log
   echo '{"decision":"..."}' >> backlog/decisions/${TASK_ID}.jsonl
   ```

3. **Human-Readable**: The slug component provides context:
   ```
   laptop-jpoley/task-123/add-user-authentication
                          ^^^^^^^^^^^^^^^^^^^^^^^^
                          Immediately understand purpose
   ```

4. **Git Worktree Compatible**: Worktree directory name matches branch name:
   ```bash
   # Create worktree
   git worktree add ../laptop-jpoley-task-123-add-user-auth laptop-jpoley/task-123/add-user-auth

   # Directory structure:
   flowspec/                           # Main repo
   laptop-jpoley-task-123-add-user-auth/  # Worktree (name matches branch)
   ```

5. **Automation-Friendly**: Simple regex extraction:
   ```bash
   # Phase detection from branch
   BRANCH=$(git branch --show-current)
   TASK_ID=$(echo "$BRANCH" | grep -oP 'task-\d+')
   SLUG=$(echo "$BRANCH" | awk -F'/' '{print $3}')
   ```

### Trade-offs Accepted

1. **Length**: Branch names are longer than minimal formats (e.g., `task-123`).
   - **Impact**: More typing (50-70 chars vs 10 chars)
   - **Mitigation**: Provide `generate-branch-name.sh` script to auto-generate:
     ```bash
     ./scripts/bash/generate-branch-name.sh task-123 add-user-auth
     # Output: laptop-jpoley/task-123/add-user-auth
     ```

2. **Non-Standard**: Not a widely-adopted industry convention.
   - **Impact**: New team members need training
   - **Mitigation**: Document clearly, provide examples, enforce with git hooks

3. **Hostname Dependency**: Requires hostname to be meaningful.
   - **Impact**: Generic hostnames (e.g., `localhost`) are not useful
   - **Mitigation**: Require developers to set meaningful hostnames or use aliases

## Implementation Details

### Branch Name Generator Script

**File**: `scripts/bash/generate-branch-name.sh`

```bash
#!/usr/bin/env bash
# Generate compliant branch name
set -euo pipefail

TASK_ID="${1:?Task ID required (e.g., task-123)}"
SLUG="${2:?Slug required (e.g., add-user-auth)}"

# Validate task ID format
if ! [[ "$TASK_ID" =~ ^task-[0-9]+$ ]]; then
  echo "Error: Task ID must match 'task-NNN' format" >&2
  exit 1
fi

# Validate slug format
if ! [[ "$SLUG" =~ ^[a-z0-9-]+$ ]]; then
  echo "Error: Slug must be lowercase alphanumeric + hyphens" >&2
  exit 1
fi

# Get hostname (lowercase, replace non-alphanumeric with hyphens)
HOSTNAME=$(hostname | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')

# Truncate slug if too long (max 50 chars)
if [ ${#SLUG} -gt 50 ]; then
  SLUG="${SLUG:0:50}"
  echo "Warning: Slug truncated to 50 chars" >&2
fi

# Generate branch name
BRANCH="${HOSTNAME}/${TASK_ID}/${SLUG}"

echo "$BRANCH"
```

**Usage**:
```bash
# Generate branch name
BRANCH=$(./scripts/bash/generate-branch-name.sh task-123 add-user-authentication)

# Create and checkout branch
git checkout -b "$BRANCH"

# Or combine:
git checkout -b $(./scripts/bash/generate-branch-name.sh task-123 add-user-auth)
```

### Branch Validation Script

**File**: `scripts/bash/validate-branch-name.sh`

```bash
#!/usr/bin/env bash
# Validate branch name against rigor rules
set -euo pipefail

BRANCH="${1:-$(git branch --show-current)}"

# Regex pattern
PATTERN='^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'

if [[ "$BRANCH" =~ $PATTERN ]]; then
  echo "✅ Valid branch name: $BRANCH"
  exit 0
else
  echo "❌ Invalid branch name: $BRANCH" >&2
  echo "" >&2
  echo "Required format: <hostname>/task-<id>/<slug>" >&2
  echo "Example: laptop-jpoley/task-123/add-user-authentication" >&2
  echo "" >&2
  echo "Rules:" >&2
  echo "  • hostname: lowercase alphanumeric + hyphens" >&2
  echo "  • task ID: 'task-' followed by digits" >&2
  echo "  • slug: lowercase alphanumeric + hyphens, max 50 chars" >&2
  exit 1
fi
```

### Git Hook Integration

**Pre-commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/usr/bin/env bash
# Validate branch name before commit

BRANCH=$(git branch --show-current)

# Allow main branch
if [ "$BRANCH" = "main" ]; then
  exit 0
fi

# Validate feature branches
./scripts/bash/validate-branch-name.sh "$BRANCH" || {
  echo "" >&2
  echo "To fix:" >&2
  echo "  1. Create correct branch: git checkout -b \$(./scripts/bash/generate-branch-name.sh task-123 feature-slug)" >&2
  echo "  2. Cherry-pick commits: git cherry-pick <commit-sha>" >&2
  echo "  3. Delete old branch: git branch -D $BRANCH" >&2
  exit 1
}
```

### Worktree Integration

**Create Worktree with Matching Name**:
```bash
# Generate branch name
TASK_ID="task-123"
SLUG="add-user-auth"
BRANCH=$(./scripts/bash/generate-branch-name.sh "$TASK_ID" "$SLUG")

# Create worktree (directory name matches branch name)
# Convert slashes to hyphens for directory name
WORKTREE_DIR="../$(echo "$BRANCH" | tr '/' '-')"
git worktree add "$WORKTREE_DIR" "$BRANCH"

# Result:
# Directory: ../laptop-jpoley-task-123-add-user-auth
# Branch:    laptop-jpoley/task-123/add-user-auth
```

### Backlog Integration

**Auto-link Task from Branch Name**:
```bash
# Extract task ID
TASK_ID=$(git branch --show-current | grep -oP 'task-\d+')

# Update task status
backlog task edit "$TASK_ID" -s "In Progress" -a "@backend-engineer"

# Log decision
./scripts/bash/log-decision.sh "Decision text" "Rationale" "alternatives" "@backend-engineer"
# Automatically logs to: backlog/decisions/${TASK_ID}.jsonl
```

## Consequences

### Positive

1. **Zero Branch Conflicts**: Unique hostname per machine eliminates collisions
2. **Automatic Task Linking**: Extract task ID with simple regex
3. **Human-Readable**: Understand branch purpose without context lookup
4. **Worktree-Friendly**: Directory and branch names match
5. **Automation-Friendly**: Easy to parse with bash, Python, etc.
6. **Multi-Machine Workflows**: Same developer, multiple machines → no confusion

### Negative

1. **Longer Names**: 50-70 chars vs 10-20 chars with simpler formats
2. **Typing Overhead**: More characters to type (mitigated with generator script)
3. **Non-Standard**: Requires team training and documentation

### Mitigation Strategies

1. **Generator Script**: `generate-branch-name.sh` eliminates typing overhead
2. **Git Aliases**: Create shortcuts:
   ```bash
   # .gitconfig
   [alias]
   newbranch = "!f() { git checkout -b $(./scripts/bash/generate-branch-name.sh $1 $2); }; f"

   # Usage: git newbranch task-123 add-user-auth
   ```
3. **IDE Integration**: VS Code extension to generate branch names
4. **Documentation**: Clear examples in `docs/guides/branch-naming.md`

## Validation

### Success Criteria

1. **100% Compliance**: All feature branches follow convention (enforced by pre-commit hook)
2. **Zero Conflicts**: No branch name collisions in multi-developer team
3. **Automatic Extraction**: Scripts successfully extract task ID from 100% of branches
4. **Worktree Compatibility**: All worktrees have matching directory/branch names

### Metrics

- **Branch Name Length**: Average 60 chars (acceptable, <255 char limit)
- **Parsing Success Rate**: 100% (simple regex always works)
- **Collision Rate**: 0% (hostname uniqueness guarantees)
- **Adoption Rate**: 95% within 4 weeks (enforced by git hooks)

## Related Decisions

- **ADR-001**: [Rigor Rules Include Pattern](./ADR-001-rigor-rules-include-pattern.md) - Enforces branch naming via EXEC-002
- **ADR-002**: [JSONL Decision Logging](./ADR-002-jsonl-decision-logging.md) - Uses task ID extraction from branch name
- **ADR-004**: [PR Iteration Pattern](./ADR-004-pr-iteration-pattern.md) - Extends this convention with version suffixes

## References

- Git Worktree Documentation: https://git-scm.com/docs/git-worktree
- Conventional Commits: https://www.conventionalcommits.org/
- Flowspec Backlog Integration: `docs/guides/flowspec-backlog-workflow.md`

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-17 | 1.0 | Software Architect | Initial decision |
