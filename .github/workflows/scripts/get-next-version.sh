#!/usr/bin/env bash
set -euo pipefail

# get-next-version.sh
# Determine next semantic version tag by bumping the patch (Z) of the latest existing tag.
# Outputs two GitHub Actions variables:
#   latest_tag=<vX.Y.Z>  # current latest tag (or v0.0.0 if none)
#   new_version=<vX.Y.Z> # next version with patch auto-incremented
#
# Usage: get-next-version.sh

# Ensure we have tags locally (in CI, checkout@v4 with fetch-depth: 0 already fetches tags)
git fetch --tags --quiet || true

# Find the latest semver tag (prefer v-prefixed)
find_latest_tag() {
  local latest
  latest=$(git tag -l 'v[0-9]*.[0-9]*.[0-9]*' --sort=v:refname | tail -n1 || true)
  if [[ -z "$latest" ]]; then
    # Fallback: allow non-v tags and normalize by adding v for internal use
    latest=$(git tag -l '[0-9]*.[0-9]*.[0-9]*' --sort=v:refname | tail -n1 || true)
    if [[ -n "$latest" ]]; then
      echo "v$latest"
      return 0
    fi
    echo "v0.0.0"
  else
    echo "$latest"
  fi
}

LATEST_TAG=$(find_latest_tag)
echo "latest_tag=$LATEST_TAG" >> "$GITHUB_OUTPUT"

# Parse X.Y.Z from latest tag (strip leading v if present)
BASE=${LATEST_TAG#v}
IFS='.' read -r MAJOR MINOR PATCH <<< "$BASE"

# Validate numeric parts; default to 0.0.0 if parsing fails
if ! [[ $MAJOR =~ ^[0-9]+$ && $MINOR =~ ^[0-9]+$ && $PATCH =~ ^[0-9]+$ ]]; then
  MAJOR=0; MINOR=0; PATCH=0
fi

# Increment patch (Z)
PATCH=$((PATCH + 1))

NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"
echo "new_version=$NEW_VERSION" >> "$GITHUB_OUTPUT"

echo "Latest tag: $LATEST_TAG"
echo "Next version: $NEW_VERSION (auto-bumped patch)"
