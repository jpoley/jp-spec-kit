---
description: Submit PR and autonomously monitor CI checks and Copilot reviews until approval-ready. Iteratively fix issues and resubmit.
loop: outer
# Loop Classification: OUTER LOOP
# This command handles post-implementation CI/CD monitoring, review feedback processing,
# and iterative refinement. It bridges validated code to merge-ready state.
---

# /flow:submit-n-watch-pr - Autonomous PR Submission and Monitoring

Submit a PR and autonomously monitor CI checks and Copilot code review feedback. Iteratively fix issues and resubmit until the PR is approval-ready with zero Copilot comments.

## 🚨 CRITICAL SUCCESS CRITERIA 🚨

**Your PR is ONLY ready for merge when you see BOTH:**

1. **All CI checks pass** - No failures, no pending checks
2. **Copilot reports "reviewed N files and generated no comments"** - where N matches the count of your changed files

**Example of successful Copilot review:**
```
Copilot reviewed 5 files in this pull request and generated no comments.
```

**If you do NOT see this message OR any CI check fails:**
- ❌ **DO NOT merge the PR**
- ❌ **DO NOT request human review**
- ✅ **Close the PR**
- ✅ **Rework the branch** (fix issues, rebase if needed)
- ✅ **Create a NEW PR** with clean history

**There are NO exceptions to this rule.** A PR with Copilot comments or CI failures is NOT ready.

## ⚠️ "Outdated" Comments = Wrong Approach ⚠️

**If you see "Outdated" labels on Copilot review comments, you are doing it wrong.**

This happens when you push fixes to an existing PR instead of creating a new one. The problem:
- Copilot marks old comments as "Outdated" but **does NOT re-run its review**
- You won't get fresh feedback on your fixes
- The PR will never reach the "reviewed N files and generated no comments" state

**Correct approach when you need to fix issues:**
1. ❌ **DO NOT** push more commits to the existing PR
2. ✅ **Close the current PR** (`gh pr close #123`)
3. ✅ **Create a NEW PR** with your fixes
4. ✅ Copilot will run a fresh review on the new PR

This is why the workflow creates new PRs rather than iterating on existing ones.

## User Input

```text
$ARGUMENTS
```

**Expected Input**:
- No arguments: Uses current branch and creates/monitors PR
- `PR_URL` or `PR_NUMBER`: Resume monitoring an existing PR (e.g., `#123` or full URL)
- `--closed PR_URL`: Resume from a closed PR reference (creates new PR on same branch)

## Execution Mode

> **🧠 Ultra-Think Mode**: This command requires deep analysis for:
> - Understanding Copilot review comments in full context
> - Identifying root causes of issues (not just symptoms)
> - Capturing learnings to prevent future similar issues
> - Deciding whether to fix vs. defer vs. dispute comments

**Apply maximum reasoning depth throughout this workflow.**

**For /flow:submit-n-watch-pr**: Recommended input state is `workflow:Validated`. Can also run from `workflow:In Implementation` if skipping formal validation.

---

## Phase 0: Initialization and Context Loading

**Report progress**: Print status banner:

```
================================================================================
🚀 /flow:submit-n-watch-pr - Autonomous PR Monitor
================================================================================
Starting at: [TIMESTAMP]
Working directory: [CWD]
================================================================================
```

### Step 0.1: Parse Arguments

```bash
# Determine mode of operation
INPUT="$ARGUMENTS"

SKIP_COPILOT=false

if [ -z "$INPUT" ]; then
  MODE="new"
  echo "📋 Mode: Create new PR from current branch"
elif echo "$INPUT" | grep -Eq '^--skip-copilot'; then
  SKIP_COPILOT=true
  INPUT=$(echo "$INPUT" | sed 's/--skip-copilot[[:space:]]*//')
  if [ -z "$INPUT" ]; then
    MODE="new"
  else
    MODE="monitor"
    PR_REF="$INPUT"
  fi
  echo "📋 Mode: ${MODE} (skipping Copilot review)"
elif echo "$INPUT" | grep -Eq '^--closed'; then
  MODE="resume_closed"
  PR_REF=$(echo "$INPUT" | sed 's/^--closed[[:space:]]*//')
  echo "📋 Mode: Resume from closed PR: $PR_REF"
elif echo "$INPUT" | grep -Eq '^#?[0-9]+$|github\.com.*pull/[0-9]+'; then
  MODE="monitor"
  PR_REF="$INPUT"
  echo "📋 Mode: Monitor existing PR: $PR_REF"
else
  echo "❌ Invalid input: $INPUT"
  echo "Usage:"
  echo "  /flow:submit-n-watch-pr                    # Create new PR"
  echo "  /flow:submit-n-watch-pr #123               # Monitor existing PR"
  echo "  /flow:submit-n-watch-pr --closed #99       # Resume from closed PR"
  echo "  /flow:submit-n-watch-pr --skip-copilot     # Skip Copilot review phase"
  exit 1
fi
```

### Step 0.2: Load Task Context

```bash
# Extract task ID from branch name
BRANCH=$(git branch --show-current 2>/dev/null)
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -n "$TASK_ID" ]; then
  echo "📌 Task: $TASK_ID"
  backlog task "$TASK_ID" --plain 2>/dev/null | head -10
else
  echo "⚠️ No task ID found in branch name"
fi
```

### Step 0.3: Mode-Specific Behavior

```bash
# Handle monitor and resume_closed modes - skip to Phase 3
if [ "$MODE" = "monitor" ] || [ "$MODE" = "resume_closed" ]; then
  # Extract PR number from PR_REF
  PR_NUMBER=$(echo "$PR_REF" | grep -Eo '[0-9]+' | tail -1)

  if [ -z "$PR_NUMBER" ]; then
    echo "❌ Could not extract PR number from: $PR_REF"
    exit 1
  fi

  echo ""
  echo "📋 Monitoring existing PR #${PR_NUMBER}"

  # Get PR details
  PR_URL=$(gh pr view "$PR_NUMBER" --json url -q '.url' 2>/dev/null)
  BRANCH=$(gh pr view "$PR_NUMBER" --json headRefName -q '.headRefName' 2>/dev/null)

  if [ -z "$PR_URL" ]; then
    echo "❌ PR #${PR_NUMBER} not found or not accessible"
    exit 1
  fi

  # If resume_closed, reopen the PR first
  if [ "$MODE" = "resume_closed" ]; then
    echo "🔄 Reopening closed PR #${PR_NUMBER}..."
    gh pr reopen "$PR_NUMBER" 2>/dev/null || echo "⚠️  PR may already be open"
  fi

  echo "   URL: $PR_URL"
  echo "   Branch: $BRANCH"
  echo ""
  echo "⏭️  Skipping Phase 1-2 (branch validation and PR creation)"
  echo "   Jumping directly to Phase 3 (CI monitoring)..."
  echo ""
  # Skip to Phase 3 by jumping past the Phase 1-2 sections
  # (The agent will continue from Phase 3 below)
fi
```

---

## Phase 1: Branch Validation and Normalization

> **Note**: This phase is skipped when using `--monitor` or `--closed` modes.

**Report progress**: Print "Phase 1: Validating branch naming convention..."

### Step 1.1: Validate Branch Name Pattern

Branch names MUST follow: `{hostname}/task-{id}/{slug-description}`

```bash
# Guard: Only run Phase 1 when creating a new PR
if [ "$MODE" = "new" ]; then

BRANCH=$(git branch --show-current 2>/dev/null)
HOSTNAME_SHORT=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')

echo "🔍 Current branch: $BRANCH"
echo "🖥️  Hostname: $HOSTNAME_SHORT"

# Pattern: hostname/task-NNN/slug-description
if echo "$BRANCH" | grep -Eq '^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'; then
  echo "✅ Branch naming convention: VALID"
  BRANCH_VALID=true
else
  echo "❌ Branch naming convention: INVALID"
  echo ""
  echo "Required format: {hostname}/task-{id}/{slug-description}"
  echo "Example: ${HOSTNAME_SHORT}/task-123/user-authentication"
  BRANCH_VALID=false
fi
```

### Step 1.2: Auto-Rename Branch if Invalid

If branch name is invalid, attempt to fix it:

```bash
if [ "$BRANCH_VALID" = "false" ]; then
  echo ""
  echo "🔧 Attempting to auto-fix branch name..."

  # Extract task ID if present anywhere in branch name
  TASK_NUM=$(echo "$BRANCH" | grep -Eo 'task-?[0-9]+' | grep -Eo '[0-9]+' | head -1)

  if [ -z "$TASK_NUM" ]; then
    # Try to get task ID from backlog (in-progress task)
    TASK_NUM=$(backlog task list -s "In Progress" --plain 2>/dev/null | grep -Eo 'task-[0-9]+' | head -1 | grep -Eo '[0-9]+')
  fi

  if [ -z "$TASK_NUM" ]; then
    echo "❌ Cannot determine task ID. Please specify:"
    echo "   backlog task list --plain"
    echo ""
    echo "Then rename branch manually:"
    echo "   git checkout -b ${HOSTNAME_SHORT}/task-<ID>/your-slug"
    exit 1
  fi

  # Generate slug from branch name (remove common prefixes, convert to lowercase kebab)
  SLUG=$(echo "$BRANCH" | sed 's|.*/||' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')

  # Construct new branch name
  NEW_BRANCH="${HOSTNAME_SHORT}/task-${TASK_NUM}/${SLUG}"

  echo "📝 Proposed new branch name: $NEW_BRANCH"
  echo ""
  echo "This will:"
  echo "  1. Create new branch: $NEW_BRANCH"
  echo "  2. Push to origin"
  echo "  3. Delete old branch: $BRANCH (local and remote)"
  echo ""

  # Rename the branch
  git branch -m "$BRANCH" "$NEW_BRANCH"

  # Check if old branch exists on remote
  if git ls-remote --heads origin "$BRANCH" | grep -q .; then
    echo "🗑️  Deleting old remote branch: $BRANCH"
    git push origin --delete "$BRANCH" 2>/dev/null || true
  fi

  # Push new branch
  git push -u origin "$NEW_BRANCH"

  BRANCH="$NEW_BRANCH"
  echo ""
  echo "✅ Branch renamed successfully to: $BRANCH"
fi
```

### Step 1.3: Ensure Branch is Rebased

```bash
echo ""
echo "🔄 Checking rebase status..."

git fetch origin main 2>/dev/null
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

if [ "$BEHIND" -gt 0 ]; then
  echo "⚠️  Branch is $BEHIND commits behind main"
  echo "🔄 Rebasing onto origin/main..."

  git rebase origin/main
  REBASE_STATUS=$?

  if [ $REBASE_STATUS -ne 0 ]; then
    echo ""
    echo "❌ REBASE CONFLICT DETECTED"
    echo ""
    echo "Merge conflicts must be resolved before proceeding."
    echo ""
    echo "Steps to resolve:"
    echo "  1. Fix conflicts in the files shown above"
    echo "  2. git add <resolved-files>"
    echo "  3. git rebase --continue"
    echo "  4. Re-run: /flow:submit-n-watch-pr"
    echo ""
    echo "To abort: git rebase --abort"
    exit 1
  fi

  echo "✅ Rebase successful"
  echo "🚀 Force pushing rebased branch..."
  git push --force-with-lease origin "$BRANCH"
else
  echo "✅ Branch is up-to-date with main"
fi

fi  # End of MODE="new" guard for Phase 1
```

**Phase 1 Complete**:
```
================================================================================
✅ Phase 1 Complete: Branch validated
   Branch: hostname/task-123/feature-slug
   Rebased: Yes (up-to-date with main)
================================================================================
```

---

## Phase 2: PR Creation or Discovery

**Report progress**: Print "Phase 2: Creating or discovering PR..."

### Step 2.1: Check for Existing PR

```bash
# Guard: Only run Phase 2 when creating a new PR
if [ "$MODE" = "new" ]; then

# Check if PR already exists for this branch
EXISTING_PR=$(gh pr view --json number,url,state 2>/dev/null || echo "")

if [ -n "$EXISTING_PR" ]; then
  PR_NUMBER=$(echo "$EXISTING_PR" | jq -r '.number')
  PR_URL=$(echo "$EXISTING_PR" | jq -r '.url')
  PR_STATE=$(echo "$EXISTING_PR" | jq -r '.state')

  echo "📋 Found existing PR: #${PR_NUMBER}"
  echo "   URL: $PR_URL"
  echo "   State: $PR_STATE"

  if [ "$PR_STATE" = "CLOSED" ] || [ "$PR_STATE" = "MERGED" ]; then
    echo ""
    echo "⚠️  PR is $PR_STATE. Creating a new PR..."
    CREATE_NEW_PR=true
  else
    CREATE_NEW_PR=false
  fi
else
  echo "📋 No existing PR found for branch: $BRANCH"
  CREATE_NEW_PR=true
fi
```

### Step 2.2: Create PR if Needed

```bash
if [ "$CREATE_NEW_PR" = "true" ]; then
  echo ""
  echo "🚀 Creating new PR..."

  # Get task title for PR title
  if [ -n "$TASK_ID" ]; then
    TASK_TITLE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "^Title:" | sed 's/^Title:[[:space:]]*//')
  fi

  # Generate PR title (conventional commit format)
  if [ -n "$TASK_TITLE" ]; then
    PR_TITLE="feat: ${TASK_TITLE}"
  else
    # Derive from branch slug
    SLUG=$(echo "$BRANCH" | sed 's|.*/||')
    PR_TITLE="feat: ${SLUG}"
  fi

  # Generate PR body
  PR_BODY=$(cat <<'PRBODY'
## Summary

Completes: $TASK_ID

## Changes

[Implementation changes will be summarized by Copilot]

## Test Plan

- [ ] CI checks pass
- [ ] Copilot review addressed
- [ ] Manual testing complete

---
*Submitted via `/flow:submit-n-watch-pr`*
PRBODY
)

  # Replace $TASK_ID in body.
  # Note: The PR_BODY heredoc is single-quoted to prevent inline variable expansion,
  # so we intentionally substitute $TASK_ID here via sed instead.
  # Escape special sed characters in TASK_ID to prevent injection issues.
  SAFE_TASK_ID="${TASK_ID:-N/A}"
  SAFE_TASK_ID="${SAFE_TASK_ID//\\/\\\\}"  # Escape backslashes
  SAFE_TASK_ID="${SAFE_TASK_ID//\//\\/}"   # Escape forward slashes
  SAFE_TASK_ID="${SAFE_TASK_ID//&/\\&}"    # Escape ampersands
  PR_BODY=$(echo "$PR_BODY" | sed "s/\$TASK_ID/$SAFE_TASK_ID/")

  # Create the PR
  gh pr create --title "$PR_TITLE" --body "$PR_BODY" --head "$BRANCH"

  # Get the new PR details
  PR_NUMBER=$(gh pr view --json number -q '.number')
  PR_URL=$(gh pr view --json url -q '.url')

  echo ""
  echo "✅ PR created successfully"
fi

echo ""
echo "================================================================================
📋 PR Status
================================================================================
PR Number: #${PR_NUMBER}
PR URL: ${PR_URL}
Branch: ${BRANCH}
Task: ${TASK_ID:-N/A}
================================================================================
"

fi  # End of MODE="new" guard for Phase 2
```

---

## Phase 3: CI Check Monitoring Loop

**Report progress**: Print "Phase 3: Monitoring CI checks..."

### Step 3.1: Wait for CI Checks

```bash
MAX_CI_WAIT=30  # Maximum wait iterations (30 * 30s = 15 minutes)
CI_POLL_INTERVAL=30  # Seconds between checks
CI_ITERATION=0

echo "⏳ Waiting for CI checks to complete..."
echo "   Poll interval: ${CI_POLL_INTERVAL}s"
echo "   Max wait: $((MAX_CI_WAIT * CI_POLL_INTERVAL / 60)) minutes"
echo ""

while [ $CI_ITERATION -lt $MAX_CI_WAIT ]; do
  CI_ITERATION=$((CI_ITERATION + 1))

  # Get PR status
  PR_STATUS=$(gh pr view "$PR_NUMBER" --json statusCheckRollup 2>/dev/null)

  # Parse check statuses
  PENDING=$(echo "$PR_STATUS" | jq '[.statusCheckRollup[] | select(.status == "PENDING" or .status == "IN_PROGRESS" or .status == "QUEUED")] | length')
  FAILED=$(echo "$PR_STATUS" | jq '[.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "ERROR" or .conclusion == "CANCELLED")] | length')
  PASSED=$(echo "$PR_STATUS" | jq '[.statusCheckRollup[] | select(.conclusion == "SUCCESS")] | length')
  TOTAL=$(echo "$PR_STATUS" | jq '.statusCheckRollup | length')

  # Print status
  printf "\r[%02d/%02d] CI Checks: ✅ %d passed | ❌ %d failed | ⏳ %d pending (of %d total)" \
    "$CI_ITERATION" "$MAX_CI_WAIT" "$PASSED" "$FAILED" "$PENDING" "$TOTAL"

  # Check completion conditions
  if [ "$PENDING" -eq 0 ]; then
    echo ""
    if [ "$FAILED" -gt 0 ]; then
      echo ""
      echo "❌ CI CHECKS FAILED"
      echo ""
      echo "Failed checks:"
      echo "$PR_STATUS" | jq -r '.statusCheckRollup[] | select(.conclusion == "FAILURE" or .conclusion == "ERROR") | "  - \(.name): \(.conclusion)"'

      # Get details
      echo ""
      echo "Fetching failure details..."
      gh pr checks "$PR_NUMBER" --required 2>/dev/null || true

      CI_PASSED=false
      break
    else
      echo ""
      echo "✅ All CI checks passed!"
      CI_PASSED=true
      break
    fi
  fi

  sleep $CI_POLL_INTERVAL
done

if [ $CI_ITERATION -ge $MAX_CI_WAIT ] && [ "$PENDING" -gt 0 ]; then
  echo ""
  echo "⚠️  CI check timeout reached. Some checks still pending."
  echo "You can re-run this command later to continue monitoring."
  CI_PASSED=false
fi
```

### Step 3.2: Handle CI Failures

If CI fails, attempt automatic fixes:

```bash
if [ "$CI_PASSED" = "false" ]; then
  echo ""
  echo "🔧 Attempting to fix CI failures..."
  echo ""

  # Run local validation suite
  echo "Running local validation..."

  NEEDS_PUSH=false

  # Fix formatting
  if command -v uv >/dev/null 2>&1 && [ -f "pyproject.toml" ]; then
    echo "  → Formatting code..."
    uv run ruff format . 2>/dev/null && NEEDS_PUSH=true

    echo "  → Fixing lint issues..."
    uv run ruff check --fix . 2>/dev/null && NEEDS_PUSH=true
  fi

  # Check for changes
  if [ "$NEEDS_PUSH" = "true" ] && ! git diff --quiet; then
    echo ""
    echo "📝 Auto-fixes applied. Committing..."
    git add .
    git commit -s -m "fix: auto-fix lint and formatting issues

Applied by /flow:submit-n-watch-pr CI remediation"

    git push origin "$BRANCH"

    echo "✅ Fixes pushed. CI will re-run automatically."
    echo ""
    echo "⏳ Waiting for CI to restart..."
    sleep 10

    # Loop back to monitoring
    # (In practice, the command should be re-run)
    echo "Re-run this command to continue monitoring: /flow:submit-n-watch-pr #${PR_NUMBER}"
    exit 0
  else
    echo ""
    echo "❌ Cannot auto-fix CI failures. Manual intervention required."
    echo ""
    echo "Review the failures above and fix them manually, then:"
    echo "  1. Fix the issues"
    echo "  2. git add . && git commit -s -m 'fix: ...' && git push"
    echo "  3. Re-run: /flow:submit-n-watch-pr #${PR_NUMBER}"
    exit 1
  fi
fi
```

**Phase 3 Complete**:
```
================================================================================
✅ Phase 3 Complete: CI checks passed
   Passed: N checks
   Duration: X minutes
================================================================================
```

---

## Phase 4: Copilot Review Monitoring Loop

**Report progress**: Print "Phase 4: Monitoring for Copilot code review..."

> **Note**: This phase is skipped when using `--skip-copilot` flag.

### Step 4.0: Check Skip Flag

```bash
if [ "$SKIP_COPILOT" = "true" ]; then
  echo ""
  echo "⏭️  Skipping Copilot review monitoring (--skip-copilot flag set)"
  echo "   Proceeding directly to Phase 5 (Analysis)..."
  echo ""
  # Skip to Phase 5 - no Copilot review processing needed
fi
```

### Step 4.1: Wait for Copilot Review

```bash
if [ "$SKIP_COPILOT" != "true" ]; then
MAX_REVIEW_WAIT=20  # Maximum wait iterations (20 * 60s = 20 minutes)
REVIEW_POLL_INTERVAL=60  # Seconds between checks
REVIEW_ITERATION=0

echo "⏳ Waiting for Copilot code review..."
echo "   Poll interval: ${REVIEW_POLL_INTERVAL}s"
echo ""

COPILOT_REVIEWED=false

while [ $REVIEW_ITERATION -lt $MAX_REVIEW_WAIT ]; do
  REVIEW_ITERATION=$((REVIEW_ITERATION + 1))

  # Check for Copilot reviews
  REVIEWS=$(gh pr view "$PR_NUMBER" --json reviews 2>/dev/null)
  COPILOT_REVIEW=$(echo "$REVIEWS" | jq '[.reviews[] | select(.author.login == "copilot" or .author.login == "github-actions[bot]" or .author.login | contains("copilot"))]')
  REVIEW_COUNT=$(echo "$COPILOT_REVIEW" | jq 'length')

  # Check for review comments
  COMMENTS=$(gh api "repos/{owner}/{repo}/pulls/${PR_NUMBER}/comments" 2>/dev/null || echo "[]")
  COPILOT_COMMENTS=$(echo "$COMMENTS" | jq '[.[] | select(.user.login == "copilot" or .user.login == "github-actions[bot]" or .user.login | contains("copilot"))]')
  COMMENT_COUNT=$(echo "$COPILOT_COMMENTS" | jq 'length')

  printf "\r[%02d/%02d] Copilot: %d reviews, %d comments" \
    "$REVIEW_ITERATION" "$MAX_REVIEW_WAIT" "$REVIEW_COUNT" "$COMMENT_COUNT"

  if [ "$REVIEW_COUNT" -gt 0 ] || [ "$COMMENT_COUNT" -gt 0 ]; then
    echo ""
    COPILOT_REVIEWED=true
    break
  fi

  sleep $REVIEW_POLL_INTERVAL
done

if [ "$COPILOT_REVIEWED" = "false" ]; then
  echo ""
  echo "ℹ️  No Copilot review received within timeout."
  echo "   This may be normal if Copilot review is not enabled for this repo."
  echo ""
  echo "Proceeding to final status check..."
fi
```

### Step 4.2: Process Copilot Feedback

If Copilot has provided feedback, analyze and address it:

```bash
if [ "$COPILOT_REVIEWED" = "true" ]; then
  echo ""
  echo "================================================================================
📝 Copilot Review Feedback
================================================================================
"

  # Display review comments
  if [ "$COMMENT_COUNT" -gt 0 ]; then
    echo "### Code Comments ($COMMENT_COUNT):"
    echo ""
    echo "$COPILOT_COMMENTS" | jq -r '.[] | "📍 \(.path):\(.line // .original_line // "N/A")\n   \(.body)\n"'
  fi

  # Display review summary
  if [ "$REVIEW_COUNT" -gt 0 ]; then
    echo ""
    echo "### Review Summary:"
    echo "$COPILOT_REVIEW" | jq -r '.[] | "State: \(.state)\n\(.body // "No summary")\n"'
  fi

  echo "================================================================================
"
fi
fi  # End of SKIP_COPILOT check from Step 4.1
```

---

## Phase 5: Ultrathink and Fix Loop

**Report progress**: Print "Phase 5: Analyzing and fixing Copilot feedback..."

> **🧠 ULTRATHINK MODE ENGAGED**
>
> For each Copilot comment, apply maximum reasoning:
> 1. What is the root cause of this feedback?
> 2. Is this a valid concern or a false positive?
> 3. What is the best fix that addresses root cause?
> 4. How can we prevent this class of issue in the future?
> 5. Should we update coding guidelines or agent instructions?

### Step 5.1: Analyze Each Comment

For each Copilot comment:

1. **Understand the concern**:
   - What specific issue is Copilot flagging?
   - Is it security, performance, style, or correctness?
   - What is the severity (critical, high, medium, low)?

2. **Evaluate validity**:
   - Is this a legitimate issue that should be fixed?
   - Is it a false positive due to context Copilot doesn't have?
   - Is it a stylistic preference vs. actual problem?

3. **Decide action**:
   - **Fix**: Make the code change
   - **Defer**: Create follow-up task for non-critical issues
   - **Dispute**: Add comment explaining why no change is needed

### Step 5.2: Apply Fixes

> **Note**: This section is skipped when using `--skip-copilot` flag.

```bash
if [ "$SKIP_COPILOT" = "true" ]; then
  echo "⏭️  Skipping fix application (--skip-copilot flag set)"
else
# For each valid comment that requires a fix:
# 1. Make the code change
# 2. Add tests if needed
# 3. Stage and commit

echo "🔧 Applying fixes..."

# Example fix workflow (implemented by agent):
# - Read the file mentioned in the comment
# - Understand the issue
# - Apply the fix
# - Add/update tests
# - Commit with reference to the comment

git add .
git commit -s -m "fix: address Copilot review feedback

Applied fixes for:
- [List of addressed comments]

Deferred/disputed:
- [Any comments not addressed with rationale]"

git push origin "$BRANCH"
fi  # End of SKIP_COPILOT check
```

### Step 5.3: Capture Learnings

**CRITICAL**: After fixing issues, capture learnings to prevent future occurrences:

```bash
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")
LEARNING_FILE="memory/learnings/copilot-feedback-${TASK_ID:-$(date +%Y%m%d)}.md"

mkdir -p memory/learnings

cat >> "$LEARNING_FILE" << 'LEARNING'
## Learning: [DATE]

### Issue Type
[e.g., Security, Performance, Code Style, Error Handling]

### What Copilot Flagged
[Describe the issue]

### Root Cause
[Why did this happen in the first place?]

### Fix Applied
[What was the fix?]

### Prevention Strategy
[How to avoid this in future - update to agents, guidelines, or templates]

### Affected Files
[List files]

---
LEARNING

echo "📚 Learning captured: $LEARNING_FILE"
```

### Step 5.4: Update Agent Guidelines (if applicable)

If the issue reveals a gap in agent instructions:

```bash
# Identify which agent should be updated
# Examples:
# - Backend validation issue → Update .claude/agents/backend-engineer.md
# - Security issue → Update .claude/agents/security-reviewer.md
# - Test coverage gap → Update .claude/agents/qa-engineer.md

echo "🔄 Consider updating agent guidelines if this is a recurring issue pattern."
echo ""
echo "Relevant files:"
echo "  - .claude/agents/backend-engineer.md"
echo "  - .claude/agents/frontend-engineer.md"
echo "  - .claude/agents/qa-engineer.md"
echo "  - templates/commands/flow/implement.md"
echo "  - templates/commands/flow/validate.md"
```

---

## Phase 6: PR Resubmission Loop

**Report progress**: Print "Phase 6: Checking if resubmission is needed..."

### Step 6.1: Determine if New PR Needed

After applying fixes, decide whether to:
- **Keep current PR**: If fixes are minor and commit history is clean
- **Create new PR**: If significant changes warrant a fresh review

```bash
# Count commits since PR creation
# Use the merge base with the PR's base branch (e.g., main) instead of the PR number itself.
COMMITS_SINCE_PR=0

if [ -n "${PR_NUMBER:-}" ]; then
  # Try to determine the base branch of the PR (requires GitHub CLI `gh`)
  BASE_BRANCH=$(gh pr view "$PR_NUMBER" --json baseRefName -q .baseRefName 2>/dev/null || echo "")

  if [ -n "${BASE_BRANCH:-}" ] && git rev-parse --verify "origin/$BASE_BRANCH" >/dev/null 2>&1; then
    MERGE_BASE=$(git merge-base HEAD "origin/$BASE_BRANCH" 2>/dev/null || echo "")
    if [ -n "${MERGE_BASE:-}" ]; then
      COMMITS_SINCE_PR=$(git rev-list --count "${MERGE_BASE}..HEAD" 2>/dev/null || echo "0")
    fi
  fi
fi
# If many fix commits, consider squashing and new PR
if [ "$COMMITS_SINCE_PR" -gt 3 ]; then
  echo "⚠️  Multiple fix commits detected ($COMMITS_SINCE_PR commits)"
  echo "Consider squashing and creating a clean PR."
  SHOULD_RESUBMIT=true
else
  SHOULD_RESUBMIT=false
fi
```

### Step 6.2: Create New PR (if needed)

```bash
if [ "$SHOULD_RESUBMIT" = "true" ]; then
  echo ""
  echo "🔄 Creating new PR with clean history..."

  # Determine version number
  CURRENT_VERSION=$(echo "$BRANCH" | grep -Eo '\-v[0-9]+$' | grep -Eo '[0-9]+' || echo "0")
  NEXT_VERSION=$((CURRENT_VERSION + 1))

  # Close current PR
  OLD_PR_NUMBER=$PR_NUMBER
  gh pr close "$PR_NUMBER" --comment "Superseded by next iteration with Copilot feedback addressed. See new PR."

  # Create new branch with version suffix if not already versioned
  if ! echo "$BRANCH" | grep -Eq '\-v[0-9]+$'; then
    NEW_BRANCH="${BRANCH}-v${NEXT_VERSION}"
  else
    BRANCH_PREFIX=$(echo "$BRANCH" | sed 's/-v[0-9]*$//')
    NEW_BRANCH="${BRANCH_PREFIX}-v${NEXT_VERSION}"
  fi

  git checkout -b "$NEW_BRANCH"
  git push -u origin "$NEW_BRANCH"

  # Create new PR
  gh pr create --title "$(gh pr view $OLD_PR_NUMBER --json title -q '.title') (v${NEXT_VERSION})" \
    --body "## Summary

Supersedes #${OLD_PR_NUMBER} with Copilot feedback addressed.

## Changes from Previous PR

[List changes]

## Previous PR
See #${OLD_PR_NUMBER} for original context.

---
*Iteration ${NEXT_VERSION} via \`/flow:submit-n-watch-pr\`*"

  PR_NUMBER=$(gh pr view --json number -q '.number')
  PR_URL=$(gh pr view --json url -q '.url')
  BRANCH="$NEW_BRANCH"

  echo ""
  echo "✅ New PR created: #${PR_NUMBER}"
  echo "   Old PR #${OLD_PR_NUMBER} closed"
fi
```

### Step 6.3: Iteration Control

```bash
MAX_ITERATIONS=5

# Load iteration count from persistent state file
# This allows the iteration counter to persist across script re-runs
ITERATION_STATE_FILE=".github/pr-${PR_NUMBER}-iteration.txt"

if [ -f "$ITERATION_STATE_FILE" ]; then
  ITERATION=$(cat "$ITERATION_STATE_FILE")
else
  ITERATION=0
fi

# Increment for this run
ITERATION=$((ITERATION + 1))

# Persist updated iteration count
mkdir -p "$(dirname "$ITERATION_STATE_FILE")"
echo "$ITERATION" > "$ITERATION_STATE_FILE"

if [ $ITERATION -ge $MAX_ITERATIONS ]; then
  echo ""
  echo "⚠️  Maximum iterations ($MAX_ITERATIONS) reached."
  echo ""
  echo "This PR has gone through multiple review cycles."
  echo "Consider:"
  echo "  1. Requesting human review to resolve remaining issues"
  echo "  2. Discussing with team if Copilot suggestions are appropriate"
  echo "  3. Marking remaining comments as 'won't fix' with rationale"
  echo ""
  echo "Current PR: #${PR_NUMBER} - ${PR_URL}"
  exit 0
fi

# Check if there are still unresolved comments
UNRESOLVED=$(gh api "repos/{owner}/{repo}/pulls/${PR_NUMBER}/comments" 2>/dev/null | jq '[.[] | select(.in_reply_to_id == null)] | length')

if [ "$UNRESOLVED" -gt 0 ]; then
  echo ""
  echo "🔄 $UNRESOLVED unresolved comments remain."
  echo ""
  echo "To continue iteration $((ITERATION + 1)):"
  echo "  1. Address the remaining Copilot feedback in your code"
  echo "  2. Commit and push your fixes"
  echo "  3. Re-run: /flow:submit-n-watch-pr #${PR_NUMBER}"
  echo ""
  echo "This will resume monitoring from Phase 3 (CI checks)."
  # Exit here - the next iteration requires re-running the command
  exit 0
else
  echo ""
  echo "✅ All Copilot comments resolved!"
fi
```

---

## Phase 7: Final Status Report

**Report progress**: Print final status banner:

```
================================================================================
🎉 /flow:submit-n-watch-pr COMPLETE
================================================================================

PR Status:        Ready for human review
PR Number:        #${PR_NUMBER}
PR URL:           ${PR_URL}
Branch:           ${BRANCH}
Task:             ${TASK_ID:-N/A}

CI Checks:        ✅ All passed
Copilot Review:   ✅ All comments resolved
Iterations:       ${ITERATION}

Learnings:        memory/learnings/copilot-feedback-${TASK_ID}.md

================================================================================

Next Steps:
1. Request human review if required
2. Merge when approved
3. Delete feature branch after merge

================================================================================
```

---

## Error Recovery

If any phase fails:

1. **Branch naming issues**: The command will attempt auto-fix. If it fails, follow the manual instructions provided.

2. **Rebase conflicts**: Resolve conflicts manually, then re-run the command.

3. **CI failures**: The command attempts auto-fix for lint/format issues. For other failures, fix manually and re-run.

4. **Copilot feedback loop**: If stuck in iteration loop, use `--skip-copilot` flag or request human review.

5. **Network/API issues**: Re-run the command. It's idempotent and will resume from the current state.

---

## Command Reference

```bash
# Create new PR and monitor
/flow:submit-n-watch-pr

# Monitor existing PR
/flow:submit-n-watch-pr #123
/flow:submit-n-watch-pr https://github.com/owner/repo/pull/123

# Resume from closed PR
/flow:submit-n-watch-pr --closed #99

# Skip Copilot feedback loop (emergency)
/flow:submit-n-watch-pr --skip-copilot
```

---

## Post-Completion: Emit Workflow Event

```bash
flowspec hooks emit submit-pr.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  --pr-number "$PR_NUMBER"
```

## Telemetry: Track Command Execution

```bash
flowspec telemetry track-role "$CURRENT_ROLE" --command /flow:submit-n-watch-pr -q
```
