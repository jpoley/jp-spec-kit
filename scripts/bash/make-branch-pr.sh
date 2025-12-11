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
#   -d, --draft            Create as draft PR
#   -s, --staged           Include only staged changes
#   -u, --unstaged         Include only unstaged changes (tracked files)
#   -n, --untracked        Include only untracked files
#   -h, --help             Show this help message
#
# By default, includes all changes (staged + unstaged + untracked)

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
    sed -n '3,16p' "$0" | sed 's/^# \?//'
    exit 0
}

# Defaults
BRANCH=""
MESSAGE=""
TITLE=""
DRAFT=""
STAGED=false
UNSTAGED=false
UNTRACKED=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch)   BRANCH="$2"; shift 2 ;;
        -m|--message)  MESSAGE="$2"; shift 2 ;;
        -t|--title)    TITLE="$2"; shift 2 ;;
        -d|--draft)    DRAFT="--draft"; shift ;;
        -s|--staged)   STAGED=true; shift ;;
        -u|--unstaged) UNSTAGED=true; shift ;;
        -n|--untracked) UNTRACKED=true; shift ;;
        -h|--help)     usage ;;
        *)             err "Unknown option: $1"; usage ;;
    esac
done

# Validate
if [[ -z "$BRANCH" ]]; then
    err "Branch name required (-b <name>)"
    exit 1
fi

if ! git rev-parse --git-dir &>/dev/null; then
    err "Not a git repository"
    exit 1
fi

# If no specific flags, include all
if ! $STAGED && ! $UNSTAGED && ! $UNTRACKED; then
    STAGED=true
    UNSTAGED=true
    UNTRACKED=true
fi

# Check for changes based on flags
has_changes=false

if $STAGED && [[ -n $(git diff --cached --name-only 2>/dev/null) ]]; then
    has_changes=true
fi

if $UNSTAGED && [[ -n $(git diff --name-only 2>/dev/null) ]]; then
    has_changes=true
fi

if $UNTRACKED && [[ -n $(git ls-files --others --exclude-standard 2>/dev/null) ]]; then
    has_changes=true
fi

if ! $has_changes; then
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

# Stage changes based on flags
if $UNTRACKED; then
    info "Adding untracked files"
    git add --all
elif $UNSTAGED; then
    info "Adding unstaged changes"
    git add --update
fi
# If only --staged, nothing to add (already staged)

if $STAGED || $UNSTAGED || $UNTRACKED; then
    # Ensure something is staged
    if [[ -z $(git diff --cached --name-only) ]]; then
        err "No changes staged after processing"
        git checkout -
        git branch -D "$BRANCH"
        exit 1
    fi
fi

info "Committing: $MESSAGE"
git commit -s -m "$MESSAGE"

info "Pushing to origin"
git push -u origin "$BRANCH"

info "Creating PR"
gh pr create --title "$TITLE" --body "" $DRAFT

PR_URL=$(gh pr view --json url -q .url)
echo -e "\n${GREEN}Done!${NC} PR: $PR_URL"
