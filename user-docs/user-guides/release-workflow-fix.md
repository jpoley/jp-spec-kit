# Release Workflow Fix Guide

## Problem Summary

The current release workflow is broken due to multiple interconnected issues:

1. **Create Release workflow fails** - GitHub Actions cannot create PRs
2. **Deploy Documentation fails** - GitHub Pages not enabled
3. **Excessive releases** - Every push to main creates a release (343+ versions)
4. **Two-commit problem** - CI tries to bump version (commit 1) then tag (commit 2)

### Root Cause Analysis

```
Push to main
    ↓
Release workflow triggers
    ↓
Tries to bump version in pyproject.toml
    ↓
Cannot push directly to main (branch protection)
    ↓
Falls back to creating PR
    ↓
FAILS: "GitHub Actions is not permitted to create or approve pull requests"
```

## Recommended Solution: Dynamic Version from Git Tags

**The cleanest approach**: Remove hardcoded version entirely. Version is derived from git tags at build time using `hatch-vcs`.

**Benefits:**
- **Zero version files to sync** - no pyproject.toml version, no __init__.py version
- **Tag IS the version** - single source of truth
- **No CI commits needed** - workflow just builds and publishes
- **Industry standard** - used by pip, setuptools, hatch, and many major projects

---

## Option A: Dynamic Version with hatch-vcs (Recommended)

### Step 1: Update pyproject.toml

```toml
[project]
name = "flowspec-cli"
dynamic = ["version"]  # Version comes from git tags
description = "..."

[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/specify_cli/_version.py"
```

### Step 2: Update __init__.py

```python
# src/specify_cli/__init__.py
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"  # Fallback for editable installs without build
```

### Step 3: Add _version.py to .gitignore

```
# Generated version file
src/specify_cli/_version.py
```

### Step 4: Update release.yml (Tag-Based)

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.0.0)'
        required: true
        type: string

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for hatch-vcs to work

      - name: Determine version
        id: version
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            VERSION="${{ inputs.version }}"
          else
            VERSION="${GITHUB_REF#refs/tags/}"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Releasing version: $VERSION"

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build

      - name: Build package
        run: python -m build

      - name: Create release packages
        run: |
          chmod +x .github/workflows/scripts/create-release-packages.sh
          .github/workflows/scripts/create-release-packages.sh ${{ steps.version.outputs.version }}

      - name: Generate release notes
        run: |
          chmod +x .github/workflows/scripts/generate-release-notes.sh
          PREV_TAG=$(git tag --sort=-v:refname | grep -E '^v[0-9]' | sed -n '2p' || echo "")
          .github/workflows/scripts/generate-release-notes.sh ${{ steps.version.outputs.version }} "$PREV_TAG"

      - name: Create GitHub Release
        run: |
          chmod +x .github/workflows/scripts/create-github-release.sh
          .github/workflows/scripts/create-github-release.sh ${{ steps.version.outputs.version }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Release Process with hatch-vcs

```bash
# That's it! Just tag and push.
git tag v1.0.0
git push origin main --tags

# The build system automatically:
# - Detects the tag
# - Generates _version.py with "1.0.0"
# - Builds the package with correct version
```

---

## Option B: Simple Tag-Based (Manual Version Sync)

If you prefer to keep explicit version in pyproject.toml:

### Single-Commit Release Flow

```bash
# 1. Update version (one commit, everything in sync)
sed -i 's/version = ".*"/version = "1.0.0"/' pyproject.toml
sed -i 's/__version__ = ".*"/__version__ = "1.0.0"/' src/specify_cli/__init__.py

# 2. Commit with the version change
git add pyproject.toml src/specify_cli/__init__.py
git commit -m "chore: release v1.0.0"

# 3. Tag THAT commit (tag points to commit with correct version)
git tag v1.0.0

# 4. Push both together
git push origin main --tags
```

**Key insight**: The tag points to the commit that contains the version. No second commit needed.

### Release Script (scripts/release.py)

A comprehensive Python script is provided at `scripts/release.py`:

```bash
# Auto-increment patch version (0.2.343 → 0.2.344)
./scripts/release.py

# Specific version
./scripts/release.py 1.0.0

# Bump minor (0.2.343 → 0.3.0)
./scripts/release.py --minor

# Bump major (0.2.343 → 1.0.0)
./scripts/release.py --major

# Preview without making changes
./scripts/release.py --dry-run

# Skip confirmation prompts
./scripts/release.py --push
```

The script automatically:
1. Validates you're on main branch
2. Checks for uncommitted changes
3. Updates pyproject.toml and __init__.py
4. Creates a single commit with the version
5. Tags that commit
6. Pushes everything to origin

**Example output:**
```
🚀 Flowspec Release Script
==================================================

📋 Current state:
  Version in pyproject.toml: 0.2.343
  Latest git tag: v0.2.343

📦 New version: 0.2.344
   Tag name: v0.2.344

🔍 Safety checks:
  ✓ On main branch
  ✓ Tag v0.2.344 does not exist
  ✓ Working directory is clean

⚠️  This will release v0.2.344
   Continue? [y/N]: y

📝 Updating version files:
  pyproject.toml: updated to 0.2.344
  src/specify_cli/__init__.py: updated to 0.2.344

📦 Creating commit and tag:
  $ git add pyproject.toml src/specify_cli/__init__.py
  $ git commit -m "chore: release v0.2.344"
  $ git tag v0.2.344

🚀 Pushing to origin:
  $ git push origin main --tags

✅ Successfully released v0.2.344!
   GitHub Actions will create the release automatically.
```

### Workflow for Option B

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get version from tag
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

      - name: Verify version sync
        run: |
          TAG_VER="${{ steps.version.outputs.version }}"
          TAG_VER="${TAG_VER#v}"
          TOML_VER=$(grep -Po '(?<=^version = ")[^"]*' pyproject.toml)
          if [ "$TAG_VER" != "$TOML_VER" ]; then
            echo "::error::Tag ($TAG_VER) doesn't match pyproject.toml ($TOML_VER)"
            exit 1
          fi

      # ... rest of release steps
```

---

## GitHub Repository Settings Required

### 1. Enable GitHub Pages

**Path**: Repository → Settings → Pages

1. Go to https://github.com/jpoley/flowspec/settings/pages
2. Under "Build and deployment":
   - Source: **GitHub Actions**
3. Save

### 2. (Optional) Allow Actions to Create PRs

Only needed if you want to keep the current workflow pattern.

**Path**: Repository → Settings → Actions → General

1. Go to https://github.com/jpoley/flowspec/settings/actions
2. Scroll to "Workflow permissions"
3. Check: **Allow GitHub Actions to create and approve pull requests**
4. Save

### 3. (Optional) Bypass Branch Protection for Releases

Only needed if you want the workflow to push directly to main.

**Path**: Repository → Settings → Branches → main → Edit

1. Go to https://github.com/jpoley/flowspec/settings/branches
2. Click "Edit" on the main branch rule
3. Under "Bypass list", add the GitHub Actions bot
4. Save

---

## Comparison: Option A vs Option B

| Aspect | Option A (hatch-vcs) | Option B (Manual) |
|--------|---------------------|-------------------|
| Version source | Git tag only | pyproject.toml + tag |
| Files to update | None | 2 files per release |
| Sync issues possible | No | Yes (if tag != toml) |
| Local dev version | `0.0.0.dev0+g<hash>` | Static version |
| Release command | `git tag v1.0.0 && git push --tags` | `./scripts/release.sh` |
| Complexity | Lower | Higher |
| Industry adoption | pip, setuptools, hatch | Many projects |

**Recommendation**: Option A (hatch-vcs) is cleaner but requires a one-time migration. Option B works if you prefer explicit version control.

---

## Migration Checklist

### For Option A (hatch-vcs)

- [ ] Enable GitHub Pages in repository settings (see above)
- [ ] Add `hatch-vcs` to build dependencies in pyproject.toml
- [ ] Change `version = "X.Y.Z"` to `dynamic = ["version"]`
- [ ] Add `[tool.hatch.version]` and `[tool.hatch.build.hooks.vcs]` sections
- [ ] Update `__init__.py` to import from `_version.py`
- [ ] Add `src/specify_cli/_version.py` to `.gitignore`
- [ ] Update `.github/workflows/release.yml` to tag-based trigger
- [ ] Remove old version bump scripts
- [ ] Test: `uv build` should show version from latest tag
- [ ] Test release: `git tag v0.3.0 && git push --tags`

### For Option B (Manual Sync)

- [ ] Enable GitHub Pages in repository settings (see above)
- [ ] Update `.github/workflows/release.yml` to tag-based trigger
- [ ] Create `scripts/release.sh` helper script
- [ ] Remove CI version bump logic
- [ ] Update CONTRIBUTING.md with new release process
- [ ] Test: `./scripts/release.sh 0.2.345`

---

## FAQ

**Q: What about the 343+ existing releases?**
A: They can stay. Future releases will be intentional and meaningful.

**Q: How does hatch-vcs handle dev versions?**
A: Between tags, version is `0.2.343.dev5+g1234abc` (5 commits after v0.2.343, hash 1234abc). On a tag, it's clean `0.2.343`.

**Q: What if I forget to tag before releasing?**
A: Use `workflow_dispatch` to manually trigger with a version, or just create the tag.

**Q: Can I release from GitHub UI?**
A: Yes, use `workflow_dispatch` - go to Actions → Create Release → Run workflow.

**Q: What happens if I create a tag without a PR?**
A: Works fine! Tags don't require PRs. You can tag any commit on main.

**Q: How do I do a hotfix release?**
A: Same process - make your fix, merge to main, then `git tag v0.2.344 && git push --tags`.

---

## Quick Start: Implementing the Fix

### Step 1: Enable GitHub Pages (Manual - Repository Settings)

1. Go to https://github.com/jpoley/flowspec/settings/pages
2. Set Source to **GitHub Actions**
3. Save

### Step 2: Replace the Release Workflow

```bash
# Replace the old workflow with the new tag-based one
mv .github/workflows/release.yml .github/workflows/release.yml.old
mv .github/workflows/release.yml.new .github/workflows/release.yml

# Commit the changes
git add .github/workflows/
git commit -m "fix(ci): switch to tag-based releases

- Trigger releases only on tag push (v*)
- Remove CI version bumping (avoids branch protection issues)
- Add version sync verification
- Support manual workflow_dispatch for emergency releases

Resolves release workflow failures caused by:
- Branch protection blocking direct pushes
- GitHub Actions unable to create PRs"

git push origin main
```

### Step 3: Test a Release

```bash
# Do a dry run first
./scripts/release.py --dry-run

# When ready, create a real release
./scripts/release.py
```

### Files Changed

| File | Action |
|------|--------|
| `.github/workflows/release.yml` | Replace with tag-based workflow |
| `scripts/release.py` | New release helper script |
| `docs/guides/release-workflow-fix.md` | This documentation |

### Cleanup (Optional)

After verifying the new workflow works:

```bash
# Remove old workflow scripts that are no longer needed
rm .github/workflows/scripts/get-next-version.sh
rm .github/workflows/scripts/update-version.sh
rm .github/workflows/scripts/check-release-exists.sh
rm .github/workflows/release.yml.old
```
