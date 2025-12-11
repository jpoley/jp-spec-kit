#!/usr/bin/env bash
#
# make-branch-pr.sh - Create a branch and PR from working changes
#
# Usage: make-branch-pr.sh -b <branch-name> [options]
#
# Options:
#   -b, --branch <name>    Branch name (required)
#   -m, --message <msg>    Commit message (default: "WIP: <branch-name>")
#   -t, --title <title>    PR title (default: commit message)
#   --body <text>          PR body/description (default: empty)
#   -d, --draft            Create as draft PR
#   -s, --staged           Include only staged changes
#   -u, --unstaged         Include only unstaged changes (tracked files)
#   -n, --untracked        Include only untracked files
#   --no-signoff           Skip DCO sign-off (default: sign-off enabled)
#   -h, --help             Show this help message
#
# By default, includes all changes (staged + unstaged + untracked)
# Commits are signed off (DCO) by default using git config user.name/email

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

err() { echo -e "${RED}Error:${NC} $*" >&2; }
info() { echo -e "${GREEN}→${NC} $*"; }
warn() { echo -e "${YELLOW}Warning:${NC} $*"; }

usage() {
    sed -n '3,21p' "$0" | sed 's/^# \?//'
    exit 0
}

cleanup() {
    local exit_code=$?
    if [[ -n "${BRANCH:-}" && -n "${ORIGINAL_BRANCH:-}" ]]; then
        if git rev-parse --verify "$BRANCH" &>/dev/null; then
            warn "Cleaning up: switching back to $ORIGINAL_BRANCH"
            git checkout "$ORIGINAL_BRANCH" 2>/dev/null || true
            git branch -D "$BRANCH" 2>/dev/null || true
        fi
    fi
    exit $exit_code
}

# Defaults
BRANCH=""
MESSAGE=""
TITLE=""
BODY=""
DRAFT=""
STAGED=false
UNSTAGED=false
UNTRACKED=false
SIGNOFF=true
ORIGINAL_BRANCH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch)    BRANCH="$2"; shift 2 ;;
        -m|--message)   MESSAGE="$2"; shift 2 ;;
        -t|--title)     TITLE="$2"; shift 2 ;;
        --body)         BODY="$2"; shift 2 ;;
        -d|--draft)     DRAFT="--draft"; shift ;;
        -s|--staged)    STAGED=true; shift ;;
        -u|--unstaged)  UNSTAGED=true; shift ;;
        -n|--untracked) UNTRACKED=true; shift ;;
        --no-signoff)   SIGNOFF=false; shift ;;
        -h|--help)      usage ;;
        *)              err "Unknown option: $1"; usage ;;
    esac
done

# Validate required tools
if ! command -v gh &>/dev/null; then
    err "GitHub CLI (gh) is required but not installed"
    exit 1
fi

# Validate branch name
if [[ -z "$BRANCH" ]]; then
    err "Branch name required (-b <name>)"
    exit 1
fi

if ! git rev-parse --git-dir &>/dev/null; then
    err "Not a git repository"
    exit 1
fi

# Check if branch already exists
if git rev-parse --verify "$BRANCH" &>/dev/null 2>&1; then
    err "Branch '$BRANCH' already exists. Please choose a different name or delete the existing branch."
    exit 1
fi

# Save original branch for cleanup
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# If no specific flags, include all
if ! $STAGED && ! $UNSTAGED && ! $UNTRACKED; then
    STAGED=true
    UNSTAGED=true
    UNTRACKED=true
fi

# Check for changes based on flags
HAS_CHANGES=false

if $STAGED && [[ -n $(git diff --cached --name-only 2>/dev/null) ]]; then
    HAS_CHANGES=true
fi

if $UNSTAGED && [[ -n $(git diff --name-only 2>/dev/null) ]]; then
    HAS_CHANGES=true
fi

if $UNTRACKED && [[ -n $(git ls-files --others --exclude-standard 2>/dev/null) ]]; then
    HAS_CHANGES=true
fi

if ! $HAS_CHANGES; then
    err "No changes to commit"
    exit 1
fi

# Set defaults
MESSAGE="${MESSAGE:-WIP: $BRANCH}"
TITLE="${TITLE:-$MESSAGE}"

# Get base branch
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

info "Creating branch: $BRANCH (from $BASE)"
git checkout -b "$BRANCH"

# Set up cleanup trap after branch creation
trap cleanup ERR

# Stage changes based on flags
if $UNTRACKED; then
    info "Adding untracked files"
    git add $(git ls-files --others --exclude-standard)
fi
if $UNSTAGED; then
    info "Adding unstaged changes"
    git add --update
fi
# If only --staged, nothing to add (already staged)

# Ensure something is staged
if [[ -z $(git diff --cached --name-only) ]]; then
    err "No changes staged after processing"
    git checkout -
    git branch -D "$BRANCH"
    exit 1
fi

info "Committing: $MESSAGE"
if $SIGNOFF; then
    git commit -s -m "$MESSAGE"
else
    git commit -m "$MESSAGE"
fi

info "Pushing to origin"
git push -u origin "$BRANCH"

# Disable trap - branch is now pushed, we don't want to delete it on PR failure
trap - ERR

info "Creating PR"
set +e
gh pr create --title "$TITLE" --body "$BODY" $DRAFT
PR_CREATE_EXIT=$?
set -e

if [[ $PR_CREATE_EXIT -ne 0 ]]; then
    err "Failed to create PR. Branch '$BRANCH' has been pushed to origin."
    warn "You may create a PR manually: gh pr create"
    exit 1
fi

PR_URL=$(gh pr view --json url -q .url)
echo -e "\n${GREEN}Done!${NC} PR: $PR_URL"
