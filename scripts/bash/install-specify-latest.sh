#!/usr/bin/env bash
set -euo pipefail

# Install specify-cli from the latest tag of a PRIVATE GitHub repo
# Resolves the latest tag using the most secure method available and installs via uv.
#
# Usage:
#   scripts/bash/install-specify-latest.sh [--ssh | --https] [--owner <owner>] [--repo <repo>]
#   env GITHUB_TOKEN=... scripts/bash/install-specify-latest.sh --https
#
# Defaults:
#   owner=jpoley repo=jp-spec-kit method=https
#
# Notes:
# - For private repos, prefer --ssh (requires GitHub SSH key) to avoid tokens in process args.
# - With --https, provide GITHUB_TOKEN with repo scope. The token may appear in process list while uv runs.
#   If you want to avoid that, ensure your Git credential helper is configured and pre-approved.

OWNER="jpoley"
REPO="jp-spec-kit"
METHOD="https"  # or ssh

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ssh) METHOD="ssh"; shift ;;
    --https) METHOD="https"; shift ;;
    --owner) OWNER="${2?}"; shift 2 ;;
    --repo) REPO="${2?}"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--ssh | --https] [--owner <owner>] [--repo <repo>]"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

command -v uv >/dev/null 2>&1 || { echo "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git not found" >&2; exit 1; }

REPO_SSH="git@github.com:${OWNER}/${REPO}.git"
REPO_HTTPS="https://github.com/${OWNER}/${REPO}.git"

# Resolve latest tag
resolve_tag_via_gh() {
  if command -v gh >/dev/null 2>&1; then
    if gh auth status -h github.com >/dev/null 2>&1; then
      gh release view -R "${OWNER}/${REPO}" --json tagName --jq .tagName 2>/dev/null || return 1
    fi
  fi
  return 1
}

resolve_tag_via_api() {
  # Requires GITHUB_TOKEN
  [[ -n "${GITHUB_TOKEN:-}" ]] || return 1
  curl -sS -H "Authorization: Bearer ${GITHUB_TOKEN}" \
       -H "Accept: application/vnd.github+json" \
       "https://api.github.com/repos/${OWNER}/${REPO}/releases/latest" \
    | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]\+\)".*/\1/p' | head -n1
}

resolve_tag_via_lsremote_ssh() {
  git ls-remote --tags "${REPO_SSH}" 2>/dev/null \
    | awk -F/ '/refs\/tags\//{print $NF}' \
    | sed 's/\^\{\}$//' \
    | sort -V \
    | tail -n1
}

resolve_tag_via_lsremote_https() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    local authed="https://x-access-token:${GITHUB_TOKEN}@github.com/${OWNER}/${REPO}.git"
    git ls-remote --tags "$authed" 2>/dev/null \
      | awk -F/ '/refs\/tags\//{print $NF}' \
      | sed 's/\^\{\}$//' \
      | sort -V \
      | tail -n1
  else
    # For private repos without token this will fail; return empty
    return 1
  fi
}

TAG=""
TAG=$(resolve_tag_via_gh || true)
if [[ -z "$TAG" ]]; then TAG=$(resolve_tag_via_api || true); fi
if [[ -z "$TAG" && "$METHOD" == "ssh" ]]; then TAG=$(resolve_tag_via_lsremote_ssh || true); fi
if [[ -z "$TAG" && "$METHOD" == "https" ]]; then TAG=$(resolve_tag_via_lsremote_https || true); fi

if [[ -z "$TAG" ]]; then
  echo "Failed to resolve latest tag for ${OWNER}/${REPO}." >&2
  echo "Tips:" >&2
  echo "  - For SSH: ensure your GitHub SSH key works: ssh -T git@github.com" >&2
  echo "  - For HTTPS: set GITHUB_TOKEN with 'repo' scope" >&2
  echo "  - Or run: gh auth login (then re-run)" >&2
  exit 1
fi

echo "Installing specify-cli @ ${TAG} from ${OWNER}/${REPO} via ${METHOD}"

if [[ "$METHOD" == "ssh" ]]; then
  UV_FROM="git+ssh://git@github.com/${OWNER}/${REPO}.git@${TAG}"
  uv tool install specify-cli --from "$UV_FROM"
else
  if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "GITHUB_TOKEN not set for private HTTPS access. Export it and retry, or use --ssh." >&2
    exit 1
  fi
  UV_FROM="git+https://x-access-token:${GITHUB_TOKEN}@github.com/${OWNER}/${REPO}.git@${TAG}"
  uv tool install specify-cli --from "$UV_FROM"
fi

echo "Done. Run: specify --help"
