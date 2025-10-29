#!/usr/bin/env bash
set -euo pipefail

# update-version.sh
# Update version in pyproject.toml (for release artifacts only)
# Usage: update-version.sh <version>

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi

VERSION="$1"

# Remove 'v' prefix for Python versioning
PYTHON_VERSION=${VERSION#v}

if [ -f "pyproject.toml" ]; then
  sed -i "s/version = \".*\"/version = \"$PYTHON_VERSION\"/" pyproject.toml
  echo "Updated pyproject.toml version to $PYTHON_VERSION (for release artifacts only)"
else
  echo "Warning: pyproject.toml not found, skipping version update"
fi

# Update version in src/specify_cli/__init__.py
if [ -f "src/specify_cli/__init__.py" ]; then
  sed -i "s/__version__ = \".*\"/__version__ = \"$PYTHON_VERSION\"/" src/specify_cli/__init__.py
  echo "Updated src/specify_cli/__init__.py version to $PYTHON_VERSION"
else
  echo "Warning: src/specify_cli/__init__.py not found, skipping version update"
fi
