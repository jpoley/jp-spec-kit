# ADR-004: PR Iteration Pattern

**Status**: Proposed
**Date**: 2025-12-17
**Decision Maker**: Software Architect
**Stakeholders**: Engineering Team, Code Review, DevOps

## Context

The Rigor Rules system enforces a "zero Copilot comments" policy before human review (PR-002). This requires an iteration workflow where developers address automated feedback, create new PRs, and close old ones. We need a standardized pattern for naming iteration branches and managing PR lifecycle.

### Problem Statement

How should we handle PR iterations when addressing automated feedback (Copilot, CI, security scans) to ensure:
1. **Lineage Tracking**: Clear relationship between original and iteration PRs
2. **Discoverability**: Easy to find latest version of a PR
3. **Cleanup**: Clear indication when old PRs should be closed
4. **Automation**: Scripts can detect iteration branches automatically

### Current Pain Points

Without a standardized pattern:
- Developers create arbitrary branch names (`feature-v2`, `feature-fixed`, `feature-final`)
- No way to programmatically determine latest version
- Old PRs left open, confusing reviewers
- PR comments reference wrong versions
- Unclear which PR to review

### Workflow Context

**Typical PR Iteration Cycle**:
1. Developer creates PR from `hostname/task-123/add-user-auth`
2. Copilot posts 5 comments (type errors, missing tests, security issues)
3. Developer fixes issues on **new branch** (not the original)
4. Developer creates **new PR**, closes old PR
5. Repeat until zero Copilot comments

**Why Not Fix on Original Branch?**
- Preserves history (old PR shows original attempt)
- Allows comparing iterations (what changed between v1 and v2?)
- Prevents force-push confusion (reviewers lose context)

### Alternatives Considered

#### Option 1: Suffix with `-fixed`, `-updated`, `-final`
**Format**: `<original-branch>-fixed`, `-updated`, `-final`

**Examples**:
```
laptop-jpoley/task-123/add-user-auth
laptop-jpoley/task-123/add-user-auth-fixed
laptop-jpoley/task-123/add-user-auth-updated
laptop-jpoley/task-123/add-user-auth-final
```

**Pros**:
- Human-readable (`-fixed` clearly indicates a fix)
- Flexible (any descriptive suffix)

**Cons**:
- No ordering (is `-fixed` before or after `-updated`?)
- No version number (can't tell if this is the 2nd or 5th iteration)
- Hard to parse (`-fixed` vs `-fixes` vs `-fix` → inconsistent)
- No clear "latest" indicator

**Verdict**: Rejected due to lack of ordering and parsing difficulty.

---

#### Option 2: Timestamp Suffix
**Format**: `<original-branch>-<timestamp>`

**Examples**:
```
laptop-jpoley/task-123/add-user-auth
laptop-jpoley/task-123/add-user-auth-20251217150000
laptop-jpoley/task-123/add-user-auth-20251217160000
```

**Pros**:
- Unambiguous ordering (timestamp sorts chronologically)
- Unique (no duplicate names possible)
- Automation-friendly (parse timestamp)

**Cons**:
- Not human-readable (what does `20251217150000` mean?)
- Very long (adds 14 chars)
- No semantic meaning (doesn't indicate "iteration")
- Hard to remember (can't type from memory)

**Verdict**: Rejected due to poor readability.

---

#### Option 3: Semantic Versioning (v1.2.3)
**Format**: `<original-branch>-v<major>.<minor>.<patch>`

**Examples**:
```
laptop-jpoley/task-123/add-user-auth-v1.0.0
laptop-jpoley/task-123/add-user-auth-v1.1.0
laptop-jpoley/task-123/add-user-auth-v2.0.0
```

**Pros**:
- Clear versioning semantics (major, minor, patch)
- Industry standard (semver is widely adopted)
- Sortable (v1.1.0 < v1.2.0 < v2.0.0)

**Cons**:
- Overkill (PR iterations don't need major/minor/patch distinctions)
- Longer (adds 7 chars minimum)
- Ambiguous meaning (what's a "major" PR iteration vs "minor"?)
- Requires decision overhead (is this a patch or minor?)

**Verdict**: Rejected due to unnecessary complexity.

---

#### Option 4: Sequential Version Numbers (-v2, -v3, -v4)
**Format**: `<original-branch>-v<N>` where N = 2, 3, 4, ...

**Examples**:
```
laptop-jpoley/task-123/add-user-auth         # v1 (implicit)
laptop-jpoley/task-123/add-user-auth-v2      # 2nd iteration
laptop-jpoley/task-123/add-user-auth-v3      # 3rd iteration
laptop-jpoley/task-123/add-user-auth-v4      # 4th iteration
```

**Pros**:
- **Simple**: Just increment a number (v2, v3, v4)
- **Clear ordering**: v2 < v3 < v4 (unambiguous)
- **Human-readable**: "v2" means "second version"
- **Short**: Adds only 3 chars (`-v2`)
- **Easy to parse**: Regex `^(.+)-v(\d+)$` extracts base and version
- **Industry convention**: v2, v3 are common in software (API v2, UI v3)

**Cons**:
- First version has no suffix (inconsistent with later versions)
  - **Mitigation**: Acceptable - first attempt is the "canonical" name
- Requires manual tracking (developer must remember "I'm on v3")
  - **Mitigation**: Provide helper script to detect latest version

**Verdict**: **SELECTED** - Best balance of simplicity, readability, and parsability.

---

## Decision

**We will use sequential version numbers (`-v2`, `-v3`, `-v4`, ...) for PR iteration branches.**

### Format Specification

```
Original branch:  <hostname>/task-<id>/<slug>
Iteration 2:      <hostname>/task-<id>/<slug>-v2
Iteration 3:      <hostname>/task-<id>/<slug>-v3
Iteration N:      <hostname>/task-<id>/<slug>-vN

Where:
  N = 2, 3, 4, 5, ... (no upper limit)
  v1 is implicit (original branch has no suffix)
```

### Examples

**Single Iteration Cycle**:
```bash
# 1. Create original branch
git checkout -b laptop-jpoley/task-123/add-user-auth

# 2. Create PR, Copilot comments received
gh pr create --title "Add user authentication"

# 3. Create iteration branch to address comments
git checkout -b laptop-jpoley/task-123/add-user-auth-v2

# 4. Fix issues, create new PR
gh pr create --title "Add user authentication (v2)"

# 5. Close old PR
gh pr close 42 --comment "Superseded by #43"
```

**Multiple Iteration Cycle**:
```bash
laptop-jpoley/task-123/add-user-auth         # PR #42 (5 Copilot comments)
laptop-jpoley/task-123/add-user-auth-v2      # PR #43 (2 Copilot comments)
laptop-jpoley/task-123/add-user-auth-v3      # PR #44 (0 comments, ready for human review)
```

### Regex Patterns

**Detect Iteration Branch**:
```bash
# Pattern: ends with -vN where N is a digit
^(.+)-v(\d+)$

# Extract base branch and version
BRANCH="laptop-jpoley/task-123/add-user-auth-v3"
BASE=$(echo "$BRANCH" | sed 's/-v[0-9]*$//')
VERSION=$(echo "$BRANCH" | grep -oP '(?<=-v)\d+$')

# Result:
# BASE="laptop-jpoley/task-123/add-user-auth"
# VERSION="3"
```

**Find All Iterations**:
```bash
# List all branches for a task
BASE="laptop-jpoley/task-123/add-user-auth"
git branch -a | grep -E "^${BASE}(-v\d+)?$"

# Output:
# laptop-jpoley/task-123/add-user-auth
# laptop-jpoley/task-123/add-user-auth-v2
# laptop-jpoley/task-123/add-user-auth-v3
```

### Primary Reasons

1. **Clear Ordering**: v2 < v3 < v4 is unambiguous, no confusion about "latest version"

2. **Human-Readable**: "v2" is immediately understood as "second version"

3. **Simple Naming**: Increment a number, no decisions about major/minor or descriptive suffixes

4. **Automation-Friendly**: Easy regex extraction of base branch and version number

5. **Industry Convention**: v2, v3 are used in API versioning (REST API v2), UI versions (Material UI v3), etc.

6. **Short**: Adds only 3 chars (`-v2`) vs 7+ with semantic versioning

### Trade-offs Accepted

1. **Manual Version Tracking**: Developer must remember "I'm on v3".
   - **Impact**: Possible confusion ("What version am I on?")
   - **Mitigation**: Provide `get-iteration-version.sh` script:
     ```bash
     ./scripts/bash/get-iteration-version.sh
     # Output: Current branch: laptop-jpoley/task-123/add-user-auth-v3
     #         Base branch: laptop-jpoley/task-123/add-user-auth
     #         Iteration: 3
     ```

2. **No Version in Original Branch**: First version has no `-v1` suffix.
   - **Impact**: Inconsistency (original has no suffix, but v2+ do)
   - **Rationale**: Original branch is the "canonical" name, matches convention (we don't say "API v1", we say "API")
   - **Accepted**: This is industry standard (APIs, libraries)

3. **Potential for Large Version Numbers**: If many iterations, could reach v10, v20, etc.
   - **Impact**: Indicates excessive rework (red flag)
   - **Mitigation**: If v5+ is reached, stop and reassess approach (likely architectural issue)

## Implementation Details

### Helper Scripts

#### Create Iteration Branch

**File**: `scripts/bash/create-iteration-branch.sh`

```bash
#!/usr/bin/env bash
# Create next iteration branch
set -euo pipefail

CURRENT=$(git branch --show-current)

# Check if already on an iteration branch
if [[ "$CURRENT" =~ -v([0-9]+)$ ]]; then
  # Extract base and increment version
  BASE=$(echo "$CURRENT" | sed 's/-v[0-9]*$//')
  VERSION=${BASH_REMATCH[1]}
  NEXT_VERSION=$((VERSION + 1))
else
  # First iteration (original → v2)
  BASE="$CURRENT"
  NEXT_VERSION=2
fi

NEW_BRANCH="${BASE}-v${NEXT_VERSION}"

echo "Creating iteration branch: $NEW_BRANCH"
git checkout -b "$NEW_BRANCH"

echo "✅ Now on: $NEW_BRANCH"
echo ""
echo "Next steps:"
echo "  1. Address Copilot comments"
echo "  2. Commit changes: git commit -s -m 'fix: address review comments'"
echo "  3. Push: git push origin $NEW_BRANCH"
echo "  4. Create PR: gh pr create --title '...(v${NEXT_VERSION})'"
echo "  5. Close old PR: gh pr close <old-pr-number> --comment 'Superseded by #<new-pr-number>'"
```

**Usage**:
```bash
# On original branch
git checkout laptop-jpoley/task-123/add-user-auth

# Create v2
./scripts/bash/create-iteration-branch.sh
# Output: Creating iteration branch: laptop-jpoley/task-123/add-user-auth-v2

# Later, create v3
./scripts/bash/create-iteration-branch.sh
# Output: Creating iteration branch: laptop-jpoley/task-123/add-user-auth-v3
```

#### Get Iteration Info

**File**: `scripts/bash/get-iteration-version.sh`

```bash
#!/usr/bin/env bash
# Get iteration version information
set -euo pipefail

CURRENT=$(git branch --show-current)

if [[ "$CURRENT" =~ -v([0-9]+)$ ]]; then
  VERSION=${BASH_REMATCH[1]}
  BASE=$(echo "$CURRENT" | sed 's/-v[0-9]*$//')
  echo "Current branch: $CURRENT"
  echo "Base branch: $BASE"
  echo "Iteration: $VERSION"
else
  echo "Current branch: $CURRENT"
  echo "Base branch: $CURRENT"
  echo "Iteration: 1 (original)"
fi

# List all iterations
echo ""
echo "All iterations:"
git branch -a | grep -E "^.*${BASE}(-v\d+)?$" | sed 's/^[ *]*//'
```

#### Close Old PR and Create New One

**File**: `scripts/bash/iterate-pr.sh`

```bash
#!/usr/bin/env bash
# Create iteration PR and close old one
set -euo pipefail

OLD_PR="${1:?Old PR number required}"
TITLE="${2:?PR title required}"

# Get current branch and version
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" =~ -v([0-9]+)$ ]]; then
  VERSION=${BASH_REMATCH[1]}
  TITLE_WITH_VERSION="${TITLE} (v${VERSION})"
else
  TITLE_WITH_VERSION="${TITLE}"
fi

# Create new PR
echo "Creating new PR: $TITLE_WITH_VERSION"
NEW_PR=$(gh pr create --title "$TITLE_WITH_VERSION" --body "Iteration of PR #${OLD_PR} addressing review comments." | grep -oP '#\d+')

# Close old PR
echo "Closing old PR #${OLD_PR}"
gh pr close "$OLD_PR" --comment "Superseded by ${NEW_PR}"

echo ""
echo "✅ PR iteration complete"
echo "   Old PR #${OLD_PR}: Closed"
echo "   New PR ${NEW_PR}: Open"
```

**Usage**:
```bash
# After creating iteration branch and committing fixes
git push origin laptop-jpoley/task-123/add-user-auth-v2

# Create new PR and close old one
./scripts/bash/iterate-pr.sh 42 "Add user authentication"

# Output:
# Creating new PR: Add user authentication (v2)
# Closing old PR #42
# ✅ PR iteration complete
#    Old PR #42: Closed
#    New PR #43: Open
```

### PR Workflow Integration

**Complete PR Iteration Workflow**:
```bash
# 1. Original PR created, received 5 Copilot comments
git checkout laptop-jpoley/task-123/add-user-auth
gh pr create --title "Add user authentication"  # PR #42

# 2. Create iteration branch
./scripts/bash/create-iteration-branch.sh
# Now on: laptop-jpoley/task-123/add-user-auth-v2

# 3. Address Copilot comments (fix code)
vim src/auth/login.py
git add src/auth/login.py
git commit -s -m "fix: address type errors and add tests"

# 4. Push and create new PR, close old PR
git push origin laptop-jpoley/task-123/add-user-auth-v2
./scripts/bash/iterate-pr.sh 42 "Add user authentication"
# New PR #43 created, old PR #42 closed

# 5. If needed, repeat for v3
# PR #43 still has 2 comments...
./scripts/bash/create-iteration-branch.sh  # Creates v3
# ... fix issues, push, iterate PR
./scripts/bash/iterate-pr.sh 43 "Add user authentication"
# New PR #44 created, old PR #43 closed

# 6. PR #44 has zero comments → ready for human review
```

### Git Cleanup

**Delete Old Iteration Branches After Merge**:
```bash
# After PR #44 is merged, delete iteration branches
git branch -D laptop-jpoley/task-123/add-user-auth-v2
git branch -D laptop-jpoley/task-123/add-user-auth-v3

# Keep original branch (optional)
# git branch -D laptop-jpoley/task-123/add-user-auth
```

**Automated Cleanup** (post-merge hook):
```bash
#!/usr/bin/env bash
# .git/hooks/post-merge
# Clean up iteration branches after merge

MERGED_BRANCH=$(git reflog -1 | grep -oP 'merge \K[^:]+')

if [[ "$MERGED_BRANCH" =~ ^(.+)-v(\d+)$ ]]; then
  BASE=${BASH_REMATCH[1]}
  VERSION=${BASH_REMATCH[2]}

  echo "Merged iteration branch $MERGED_BRANCH"
  echo "Cleaning up old iterations..."

  # Delete all iterations except the merged one
  for ((i=2; i<VERSION; i++)); do
    BRANCH="${BASE}-v${i}"
    if git branch | grep -q "$BRANCH"; then
      echo "  Deleting $BRANCH"
      git branch -D "$BRANCH"
    fi
  done
fi
```

## Consequences

### Positive

1. **Clear Lineage**: Easy to see iteration history (v1 → v2 → v3)
2. **Simple Naming**: Just increment a number (no decisions needed)
3. **Automation-Friendly**: Regex extraction is trivial
4. **Human-Readable**: "v2" is immediately understood
5. **Industry Standard**: Aligns with API/library versioning conventions
6. **Short**: Adds only 3 chars per iteration

### Negative

1. **Manual Tracking**: Developer must track version number
2. **Branch Proliferation**: Multiple branches for one feature (mitigated by cleanup script)
3. **PR Noise**: Multiple PRs for one feature (accepted trade-off for quality)

### Mitigation Strategies

1. **Helper Scripts**: `create-iteration-branch.sh` automates version increment
2. **Git Cleanup**: Post-merge hook deletes old iteration branches
3. **PR Linking**: New PR references old PR in description (provides context)

## Validation

### Success Criteria

1. **Zero Ambiguity**: Always clear which is the latest version
2. **Automatic Detection**: Scripts successfully extract version number 100% of time
3. **PR Traceability**: Each new PR links to superseded PR
4. **Clean History**: Old iteration branches deleted after merge

### Metrics

- **Version Extraction Success**: 100% (simple regex always works)
- **Average Iterations**: <3 per feature (most features need v2, few need v3)
- **Cleanup Rate**: 100% (automated post-merge hook)

### Red Flags

- **v5+ Iterations**: Indicates excessive rework → reassess approach
- **Long-lived iteration branches**: May indicate blocked work

## Related Decisions

- **ADR-001**: [Rigor Rules Include Pattern](./ADR-001-rigor-rules-include-pattern.md) - Enforces PR iteration via PR-002, PR-003
- **ADR-002**: [JSONL Decision Logging](./ADR-002-jsonl-decision-logging.md) - Tracks PR iteration decisions
- **ADR-003**: [Branch Naming Convention](./ADR-003-branch-naming-convention.md) - Base branch format that iteration extends

## References

- GitHub PR workflow: https://docs.github.com/en/pull-requests
- Git branch management: https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- Semantic Versioning (for comparison): https://semver.org/

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-17 | 1.0 | Software Architect | Initial decision |
