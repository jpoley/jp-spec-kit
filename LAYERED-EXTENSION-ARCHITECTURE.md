# JP Spec Kit - Layered Extension Architecture

## Overview

JP Spec Kit has been transformed from a fork into a **layered extension** of GitHub's spec-kit. This architecture allows you to:

- ✅ **Stay current** with upstream spec-kit features
- ✅ **Add custom** agents, stacks, and workflows  
- ✅ **Upgrade seamlessly** with `specify upgrade`
- ✅ **Pin versions** for reproducible builds
- ✅ **Extend without forking** the base codebase

## Architecture

### Two-Stage Download Model

```
┌─────────────────────────────────────────┐
│  Your Project                           │
│  ┌───────────────────────────────────┐  │
│  │ JP Spec Kit Extension (Layer 2)  │  │  ← Custom jpspec commands
│  │ • jpspec:* commands               │  │  ← Multi-language support  
│  │ • .languages/ expertise           │  │  ← Expert personas
│  │ • Multi-agent workflows           │  │  ← Advanced orchestration
│  └───────────────────────────────────┘  │
│           ↓ Overlays on top of ↓        │
│  ┌───────────────────────────────────┐  │
│  │ Base Spec Kit (Layer 1)          │  │  ← Core /speckit.* commands
│  │ • /speckit.* commands             │  │  ← Standard templates
│  │ • Core templates                  │  │  ← Setup scripts
│  │ • Setup scripts                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Precedence Rule**: Extension overrides base where conflicts exist.

### What Changed

#### 1. **Repository Configuration** (Step 1)

Added constants in `src/specify_cli/__init__.py`:

```python
# Repository configuration for two-stage download
BASE_REPO_OWNER = "github"
BASE_REPO_NAME = "spec-kit"
BASE_REPO_DEFAULT_VERSION = "latest"

EXTENSION_REPO_OWNER = "jpoley"
EXTENSION_REPO_NAME = "jp-spec-kit"
EXTENSION_REPO_DEFAULT_VERSION = "latest"
```

**Impact**: CLI now knows where to fetch base vs extension.

#### 2. **Two-Stage Download Function** (Step 2)

New `download_and_extract_two_stage()` function:

```python
def download_and_extract_two_stage(
    project_path: Path, 
    ai_assistant: str, 
    script_type: str, 
    is_current_dir: bool = False, 
    *, 
    verbose: bool = True, 
    tracker: StepTracker | None = None, 
    client: httpx.Client = None, 
    debug: bool = False, 
    github_token: str = None, 
    base_version: str = None, 
    extension_version: str = None
) -> Path
```

**Workflow**:
1. Download base spec-kit from `github/spec-kit`
2. Download jp-spec-kit extension from `jpoley/jp-spec-kit`
3. Extract base first
4. Extract extension on top (merges directories, overwrites files)
5. Extension wins on conflicts

**Impact**: Users get both base and extension in one command.

#### 3. **Version Pinning Support** (Step 3)

Enhanced `download_template_from_github()` to support versioning:

```python
def download_template_from_github(
    ...,
    repo_owner: str = None,
    repo_name: str = None,
    version: str = None  # ← New parameter
) -> Tuple[Path, dict]:
    # Construct API URL based on version
    if version == "latest":
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    else:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{version}"
```

**Usage**:
```bash
# Pin to specific versions
specify init my-project --base-version 0.0.20 --extension-version 0.0.20

# Always get latest
specify init my-project  # Uses "latest" by default
```

**Impact**: Reproducible builds, version control.

#### 4. **Compatibility Matrix** (Step 4)

Created `.spec-kit-compatibility.yml`:

```yaml
jp-spec-kit:
  version: "0.0.20"
  type: "layered-extension"
  
  compatible_with:
    spec-kit:
      min: "0.0.18"
      max: "0.0.22"
      tested: "0.0.20"
      recommended: "0.0.20"
      repository: "github/spec-kit"
```

**Impact**: Clear version compatibility declarations.

#### 5. **Plugin Manifest** (Step 5)

Created `.specify-plugin.yml`:

```yaml
name: jp-spec-kit
version: 0.0.20
type: layered-extension

extends:
  name: spec-kit
  repository: github/spec-kit
  version: 0.0.20
  strategy: overlay

provides:
  commands:
    - jpspec:specify
    - jpspec:plan
    - jpspec:research
    - jpspec:implement
    - jpspec:validate
    - jpspec:operate
  
  languages:
    - python, go, rust, java, kotlin, c, cpp, csharp, typescript, javascript, web, mobile, systems
```

**Impact**: Declarative extension system for future plugin architecture.

## New CLI Features

### `specify init` - Enhanced

**New Flags**:
- `--base-version <version>` - Pin base spec-kit version
- `--extension-version <version>` - Pin jp-spec-kit version
- `--layered/--no-layered` - Toggle two-stage download (default: `--layered`)

**Examples**:
```bash
# Two-stage with latest versions (default)
specify init my-project

# Pin to specific versions
specify init my-project --base-version 0.0.20 --extension-version 0.0.20

# Extension only (no base)
specify init my-project --no-layered
```

**Behind the Scenes**:
```python
if layered:
    # Two-stage download: base + extension
    download_and_extract_two_stage(...)
else:
    # Single-stage download (legacy or extension-only)
    download_and_extract_template(
        ...,
        repo_owner=EXTENSION_REPO_OWNER,
        repo_name=EXTENSION_REPO_NAME,
        version=extension_version
    )
```

### `specify upgrade` - New Command

Upgrade existing projects to latest base + extension.

**Flags**:
- `--base-version <version>` - Upgrade base to specific version
- `--extension-version <version>` - Upgrade extension to specific version
- `--dry-run` - Preview changes without applying
- `--templates-only` - Only update templates
- `--debug` - Verbose output

**Workflow**:
1. Auto-detect AI assistant from project (`.claude/`, `.github/`, etc.)
2. Auto-detect script type (`.sh` or `.ps1`)
3. Backup current templates to `.specify-backup/`
4. Download latest base + extension
5. Apply two-stage merge in place
6. Show summary with rollback instructions

**Examples**:
```bash
# Upgrade to latest
specify upgrade

# Preview changes
specify upgrade --dry-run

# Pin versions
specify upgrade --base-version 0.0.21 --extension-version 0.0.21

# Templates only
specify upgrade --templates-only
```

**Safety**:
- Creates `.specify-backup/` before applying changes
- Shows git diff instructions
- Provides rollback command if needed

## Usage Workflows

### Initial Setup (Layered Extension)

```bash
# Install CLI
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git

# Initialize project with two-stage download
specify init my-project --ai claude

# Result:
# - Base spec-kit templates from github/spec-kit
# - JP spec-kit extension overlay from jpoley/jp-spec-kit
# - Both /speckit.* and /jpspec:* commands available
```

### Keeping Up with Upstream

```bash
# Upgrade to latest base + extension
cd my-project
specify upgrade

# Preview first
specify upgrade --dry-run

# Pin to specific versions
specify upgrade --base-version 0.0.21 --extension-version 0.0.21
```

### Version Pinning for CI/CD

```bash
# In CI pipeline or team setup
specify init my-project \
  --base-version 0.0.20 \
  --extension-version 0.0.20 \
  --ai claude

# Everyone gets same versions → reproducible builds
```

### Extension-Only Mode

```bash
# Skip base spec-kit, use jp-spec-kit only
specify init my-project --no-layered --ai claude

# Result: Only jp-spec-kit templates (no base)
```

## Configuration Files

### `.spec-kit-compatibility.yml`

Declares version compatibility between jp-spec-kit and upstream spec-kit.

**Purpose**:
- Version matrix for testing
- Breaking change tracking
- Recommended version guidance

**Future**: CLI could read this file to warn about incompatible versions.

### `.specify-plugin.yml`

Plugin manifest declaring what jp-spec-kit provides.

**Purpose**:
- Declarative extension metadata
- Command namespace (`jpspec:*`)
- Language support list
- Merge strategy rules

**Future**: Foundation for full plugin system with `specify plugin add`.

## Migration Guide

### If You Have an Existing jp-spec-kit Project

**Before** (fork model):
```bash
# You had to manually sync from github/spec-kit
# No easy way to get upstream updates
```

**After** (layered extension):
```bash
# Upgrade to latest base + extension
cd your-project
specify upgrade

# Or pin to specific versions
specify upgrade --base-version 0.0.20 --extension-version 0.0.20
```

### If You're New to JP Spec Kit

Just use the standard workflow:
```bash
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git
specify init my-project --ai claude
```

You automatically get:
- ✅ Base spec-kit features
- ✅ JP spec-kit extensions
- ✅ Ability to upgrade both

## Technical Details

### Merge Strategy

**Directory Merging** (recursive):
```python
if dest_path.exists():
    # Merge directory contents (extension overrides base)
    for sub_item in item.rglob('*'):
        if sub_item.is_file():
            rel_path = sub_item.relative_to(item)
            dest_file = dest_path / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sub_item, dest_file)  # Overwrite
else:
    shutil.copytree(item, dest_path, dirs_exist_ok=True)
```

**File Overwriting**:
```python
# Extension file always wins
shutil.copy2(item, dest_path)  # Overwrites base
```

**Examples**:
- Base has `.specify/plan-template.md`
- Extension has `.specify/jpspec-plan-template.md`
- Result: Both files present (extension adds, doesn't replace)

- Base has `.claude/commands/plan.md`
- Extension has `.claude/commands/plan.md` (enhanced)
- Result: Extension version wins

### Tracking in StepTracker

**Layered Mode**:
```python
tracker.add("fetch-base", "Fetch base spec-kit")
tracker.add("fetch-extension", "Fetch jp-spec-kit extension")
tracker.add("extract-base", "Extract base template")
tracker.add("extract-extension", "Extract extension (overlay)")
tracker.add("merge", "Merge templates (extension overrides base)")
```

**Legacy Mode** (`--no-layered`):
```python
tracker.add("fetch", "Fetch latest release")
tracker.add("download", "Download template")
tracker.add("extract", "Extract template")
```

## Benefits

### For Users

1. **Always Up-to-Date**: `specify upgrade` syncs with latest upstream
2. **Version Control**: Pin to specific versions for reproducibility
3. **Customization**: Keep jp-spec-kit extensions while getting base updates
4. **Safety**: Automatic backups before upgrades
5. **Transparency**: See exactly what's being downloaded (base vs extension)

### For Maintainers

1. **No Fork Drift**: Don't maintain full fork of spec-kit
2. **Clear Boundaries**: Base vs extension clearly separated
3. **Easier Testing**: Test compatibility with multiple spec-kit versions
4. **Plugin Foundation**: `.specify-plugin.yml` enables future plugin system
5. **Version Matrix**: `.spec-kit-compatibility.yml` tracks tested versions

### For Ecosystem

1. **Composable**: Future extensions can layer on jp-spec-kit
2. **Interoperable**: Standard plugin manifest format
3. **Discoverable**: Extensions declare what they provide
4. **Upgradeable**: Users control when to adopt new versions

## Future Enhancements

### Plugin System

```bash
# Install multiple extensions
specify plugin add jpoley/jp-spec-kit
specify plugin add acme/custom-workflow
specify plugin list
specify plugin update jp-spec-kit
```

### Compatibility Checking

```bash
# CLI reads .spec-kit-compatibility.yml
specify init my-project --extension-version 0.0.30

# Warning: jp-spec-kit 0.0.30 not tested with spec-kit 0.0.20
# Recommended: upgrade to spec-kit 0.0.25
# Continue anyway? (y/N)
```

### Selective Features

```yaml
# .specify-config.yml
base: github/spec-kit@0.0.20
extensions:
  - jpoley/jp-spec-kit@0.0.20
    features:
      - jpspec-commands
      - multi-language
      exclude:
        - stacks  # Don't need stack templates
```

### Bidirectional Sync

```bash
# Pull from both upstream AND extension
specify sync

# Push customizations back to extension repo (if you're a contributor)
specify sync --push
```

## Troubleshooting

### "Could not detect AI assistant type"

**Problem**: Running `specify upgrade` in non-Specify directory.

**Solution**:
```bash
cd <your-specify-project>
specify upgrade
```

### Version Mismatch

**Problem**: Extension requires newer base version.

**Solution**:
```bash
# Upgrade both to latest
specify upgrade

# Or pin to compatible versions (see .spec-kit-compatibility.yml)
specify upgrade --base-version 0.0.20 --extension-version 0.0.20
```

### Merge Conflicts

**Problem**: Local changes conflict with upgrade.

**Solution**:
```bash
# Preview first
specify upgrade --dry-run

# Backup is automatic, but you can restore:
cp -r .specify-backup/* .

# Or use git to see changes:
git diff
```

### Network Issues

**Problem**: Can't download from GitHub.

**Solution**:
```bash
# Use GitHub token
specify upgrade --github-token ghp_your_token

# Or skip TLS (not recommended)
specify upgrade --skip-tls

# Enable debug output
specify upgrade --debug
```

## Summary

JP Spec Kit is now a **true layered extension** that:

1. ✅ Downloads base spec-kit from `github/spec-kit`
2. ✅ Overlays jp-spec-kit extensions from `jpoley/jp-spec-kit`
3. ✅ Merges with clear precedence (extension overrides base)
4. ✅ Supports version pinning for reproducibility
5. ✅ Provides `specify upgrade` for syncing with upstream

This architecture enables you to:

- Keep up with spec-kit features automatically
- Add custom agents and stacks without forking
- Upgrade seamlessly with confidence
- Pin versions for stable builds
- Extend further with plugins (future)

**Next Steps**:

1. Try it: `specify init test-project --ai claude`
2. Explore jpspec commands: `/jpspec:plan`, `/jpspec:implement`
3. Upgrade regularly: `specify upgrade`
4. Report issues: https://github.com/jpoley/jp-spec-kit/issues
