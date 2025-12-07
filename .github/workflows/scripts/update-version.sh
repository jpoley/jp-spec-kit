#!/usr/bin/env bash
set -euo pipefail

# update-version.sh
# Update version in pyproject.toml and __init__.py
# Usage: update-version.sh <version>
#
# This script MUST succeed - no silent failures.
# If files are missing or updates fail, the script exits with error.

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi

VERSION="$1"

# Remove 'v' prefix for Python versioning
PYTHON_VERSION=${VERSION#v}

# Validate version format (X.Y.Z only - no special regex chars)
if ! [[ "$PYTHON_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: Invalid version format '$PYTHON_VERSION'. Expected X.Y.Z (e.g., 0.2.313)" >&2
  exit 1
fi

echo "Updating version to: $PYTHON_VERSION"

# Update pyproject.toml - REQUIRED
if [[ ! -f "pyproject.toml" ]]; then
  echo "ERROR: pyproject.toml not found" >&2
  exit 1
fi

# Use perl for cross-platform sed replacement (macOS sed -i requires extension)
# Version is validated above to contain only digits and dots (safe for regex)
perl -i -pe "s/^version = \"[^\"]*\"/version = \"$PYTHON_VERSION\"/" pyproject.toml

# Verify the change was applied using fixed string match (-F)
if ! grep -qF "version = \"$PYTHON_VERSION\"" pyproject.toml; then
  echo "ERROR: Failed to update version in pyproject.toml" >&2
  exit 1
fi
echo "Updated pyproject.toml to $PYTHON_VERSION"

# Update src/specify_cli/__init__.py - REQUIRED
INIT_FILE="src/specify_cli/__init__.py"
if [[ ! -f "$INIT_FILE" ]]; then
  echo "ERROR: $INIT_FILE not found" >&2
  exit 1
fi

# Version is validated above to contain only digits and dots (safe for regex)
perl -i -pe "s/__version__ = \"[^\"]*\"/__version__ = \"$PYTHON_VERSION\"/" "$INIT_FILE"

# Verify the change was applied using fixed string match (-F)
if ! grep -qF "__version__ = \"$PYTHON_VERSION\"" "$INIT_FILE"; then
  echo "ERROR: Failed to update version in $INIT_FILE" >&2
  exit 1
fi
echo "Updated $INIT_FILE to $PYTHON_VERSION"

echo "Version update complete: $PYTHON_VERSION"
