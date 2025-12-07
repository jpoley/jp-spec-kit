#!/usr/bin/env bash
set -euo pipefail

# prune-releases.sh
# Delete old GitHub releases and tags below a specified version threshold
#
# Usage:
#   ./prune-releases.sh <threshold>              # Dry-run (show what would be deleted)
#   ./prune-releases.sh <threshold> --execute    # Actually delete
#
# Examples:
#   ./prune-releases.sh 0.0.100                  # Show releases below v0.0.100
#   ./prune-releases.sh 0.0.100 --execute        # Delete releases below v0.0.100
#   ./prune-releases.sh 0.1.0 --execute          # Delete all 0.0.x releases

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <threshold-version> [--execute]"
  echo ""
  echo "Examples:"
  echo "  $0 0.0.100              # Dry-run: show releases below v0.0.100"
  echo "  $0 0.0.100 --execute    # Delete releases below v0.0.100"
  echo "  $0 0.1.0 --execute      # Delete all 0.0.x releases"
  exit 1
fi

THRESHOLD="$1"
EXECUTE="${2:-}"

# Validate threshold version format (must be X.Y.Z)
if [[ $(echo "$THRESHOLD" | grep -o '\.' | wc -l) -ne 2 ]]; then
  echo "ERROR: Invalid version format '$THRESHOLD'. Expected exactly X.Y.Z format (e.g., 0.0.100)" >&2
  exit 1
fi
# Parse threshold version
IFS='.' read -r THRESH_MAJOR THRESH_MINOR THRESH_PATCH <<< "$THRESHOLD"

# Validate threshold
if ! [[ "$THRESH_MAJOR" =~ ^[0-9]+$ && "$THRESH_MINOR" =~ ^[0-9]+$ && "$THRESH_PATCH" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Invalid version format '$THRESHOLD'. Expected X.Y.Z (e.g., 0.0.100)" >&2
  exit 1
fi

echo "=========================================="
echo "Release Pruning Script"
echo "=========================================="
echo "Threshold: v$THRESHOLD"
echo "Mode: $([ "$EXECUTE" == "--execute" ] && echo "EXECUTE (will delete!)" || echo "DRY-RUN (preview only)")"
echo ""

# Get all releases using JSON output (reliable parsing)
echo "Fetching releases..."
mapfile -t RELEASES < <(gh release list --limit 500 --json tagName -q '.[].tagName' | sed 's/^v//')

# Count releases to delete
TO_DELETE=()

for VERSION in "${RELEASES[@]}"; do
  # Parse version
  IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

  # Skip invalid versions
  if ! [[ "$MAJOR" =~ ^[0-9]+$ && "$MINOR" =~ ^[0-9]+$ && "$PATCH" =~ ^[0-9]+$ ]]; then
    echo "Skipping invalid version: $VERSION"
    continue
  fi

  # Compare versions (below threshold = delete)
  DELETE=false
  if [[ $MAJOR -lt $THRESH_MAJOR ]]; then
    DELETE=true
  elif [[ $MAJOR -eq $THRESH_MAJOR && $MINOR -lt $THRESH_MINOR ]]; then
    DELETE=true
  elif [[ $MAJOR -eq $THRESH_MAJOR && $MINOR -eq $THRESH_MINOR && $PATCH -lt $THRESH_PATCH ]]; then
    DELETE=true
  fi

  if [[ "$DELETE" == "true" ]]; then
    TO_DELETE+=("$VERSION")
  fi
done

echo ""
echo "=========================================="
echo "Releases to delete: ${#TO_DELETE[@]}"
echo "=========================================="

if [[ ${#TO_DELETE[@]} -eq 0 ]]; then
  echo "No releases found below v$THRESHOLD"
  exit 0
fi

# Show releases to delete
for VERSION in "${TO_DELETE[@]}"; do
  echo "  - v$VERSION"
done

echo ""

if [[ "$EXECUTE" != "--execute" ]]; then
  echo "DRY-RUN: No changes made."
  echo "Run with --execute to delete these releases."
  exit 0
fi

# Confirm before deletion
echo "⚠️  WARNING: This will permanently delete ${#TO_DELETE[@]} releases and tags!"
read -p "Type 'DELETE' to confirm: " CONFIRM

if [[ "$CONFIRM" != "DELETE" ]]; then
  echo "Aborted."
  exit 1
fi

echo ""
echo "Deleting releases and tags..."

DELETED=0
FAILED=0

for VERSION in "${TO_DELETE[@]}"; do
  TAG="v$VERSION"
  echo -n "  Deleting $TAG... "

  # Delete GitHub release and git tag (remote) together
  if gh release delete "$TAG" --yes 2>/dev/null && git push origin --delete "$TAG" 2>/dev/null; then
    echo "release ✓ tag ✓"
    ((DELETED++))
  else
    echo "release/tag ✗"
    ((FAILED++))
  fi
done

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Deleted: $DELETED"
echo "Failed: $FAILED"
echo "=========================================="
