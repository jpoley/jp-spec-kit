#!/bin/bash
# release.sh - Bump patch version, update package.json, tag, commit, and push

set -euo pipefail

# Ensure we’re up to date
git fetch --tags

# Check if there are ANY tags at all
all_tags=$(git tag -l)

if [ -z "$all_tags" ]; then
  echo "No tags found, creating first tag v0.0.1"
  new_version="0.0.1"
  new_tag="v$new_version"
else
  # Get latest semver tag
  latest_tag=$(git tag -l --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | head -n1)

  if [ -z "$latest_tag" ]; then
    echo "No semver tag found, starting at v0.0.0"
    latest_tag="v0.0.0"
  fi

  # Strip leading 'v' if present
  version=${latest_tag#v}
  IFS='.' read -r major minor patch <<< "$version"

  # Bump patch
  patch=$((patch + 1))
  new_version="$major.$minor.$patch"
  new_tag="v$new_version"
  
  echo "Bumping version: $version → $new_version"
fi

# Update version files
files_to_add=""

# Update pyproject.toml
if [ -f "pyproject.toml" ]; then
  echo "Updating pyproject.toml..."
  sed -i.bak 's/version = "[^"]*"/version = "'"$new_version"'"/' pyproject.toml && rm -f pyproject.toml.bak
  files_to_add="$files_to_add pyproject.toml"
  echo "Updated pyproject.toml to $new_version"
fi

# Update __version__ in src/specify_cli/__init__.py
if [ -f "src/specify_cli/__init__.py" ]; then
  echo "Updating src/specify_cli/__init__.py..."
  sed -i.bak 's/__version__ = "[^"]*"/__version__ = "'"$new_version"'"/' src/specify_cli/__init__.py && rm -f src/specify_cli/__init__.py.bak
  files_to_add="$files_to_add src/specify_cli/__init__.py"
  echo "Updated src/specify_cli/__init__.py to $new_version"
fi

# Update package.json if it exists and we have the tools
if [ -f "package.json" ]; then
  if command -v jq >/dev/null 2>&1; then
    echo "Updating package.json with jq..."
    jq --arg v "$new_version" '.version = $v' package.json > package.tmp && mv package.tmp package.json
    files_to_add="$files_to_add package.json"
  else
    echo "Warning: jq not found, trying sed fallback for package.json..."
    # Fallback: use sed to update version (basic pattern matching)
    if grep -q '"version"' package.json; then
      sed -i.bak 's/"version": *"[^"]*"/"version": "'"$new_version"'"/' package.json && rm -f package.json.bak
      files_to_add="$files_to_add package.json"
      echo "Updated package.json using sed fallback"
    else
      echo "Warning: Could not update package.json - no version field found or sed failed"
    fi
  fi
fi

# Commit version bump (only add files that were actually updated)
if [ -n "$files_to_add" ]; then
  git add $files_to_add
  git commit -m "chore(release): $new_tag"
else
  # Just create the tag without updating any files
  git commit --allow-empty -m "chore(release): $new_tag"
fi

# Tag and push
git tag "$new_tag"
git push origin main --tags
