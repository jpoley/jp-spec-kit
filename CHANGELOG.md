## [Unreleased]

### Changed

- **File-friendly timestamp in specify-backup path**: Backup directories now include timestamp (`YYYYMMDD-HHMMSS`) format
  - Previous backups are preserved instead of being overwritten
  - Example: `.specify-backup-20251207-143052/` instead of `.specify-backup/`
  - Enables rollback to any previous backup version

## [0.2.316] - 2025-12-07

### Fixed

- **Critical: spec-kit version display showing 0.0.20 instead of 0.0.90**
  - Root cause: `.spec-kit-compatibility.yml` was not being included in the installed package
  - The file was only accessible when running from the source repo, not when installed via `uv tool install`
  - Fix: Use `importlib.resources` to properly load bundled package data files
  - Add `force-include` in `pyproject.toml` to ensure the compatibility matrix is bundled in the wheel
  - Updated default fallback version from 0.0.20 to 0.0.90
  - Call `importlib.invalidate_caches()` after reinstalling to pick up new package resources

### Added

- **Pre-push hook for security scanning**: New `scripts/hooks/pre-push` hook runs Semgrep security scan before pushing
  - Automatically catches security issues before they reach CI
  - Install with: `./scripts/hooks/install-hooks.sh`
  - Requires `semgrep` to be installed (`pip install semgrep`)

### Changed

- Improved `load_compatibility_matrix()` to use `importlib.resources.files()` for reliable package resource access
- Updated test expectations for the new default fallback version

## [0.2.315] - 2025-12-06

### Added

- **Spec-Light Mode for Medium-Complexity Features**: Streamlined SDD workflow with `--light` flag
  - Add `flowspec init --light` flag for medium-complexity features (complexity score 4-6/10)
  - Creates `.flowspec-light-mode` marker file in project root
  - New templates: `spec-light-template.md` (combined user stories + acceptance criteria) and `plan-light-template.md` (high-level approach only)
  - Skips research and analyze phases for faster iteration (~60% faster workflow; see docs/guides/when-to-use-light-mode.md for example metrics)
  - Maintains constitutional compliance requirements (security, test-first, PR workflow)
  - Documentation: `docs/guides/when-to-use-light-mode.md` and `docs/adr/ADR-006-spec-light-mode-design.md`
  - Easy upgrade path from light mode to full mode if complexity increases

- **`specify backlog migrate` Command**: Migrate legacy tasks.md files to Backlog.md format
  - Converts legacy tasks.md to individual task files in `./backlog/tasks/`
  - Preserves all task metadata: IDs, labels, dependencies, status, user stories
  - Automatic backup creation (default: enabled, can use `--no-backup`)
  - `--dry-run` flag to preview migration without writing files
  - `--force` flag to overwrite existing task files
  - `--source` and `--output` flags for custom paths
  - Comprehensive migration summary with task counts, phases, and user stories
  - Detects and preserves completed task status (checked boxes → "Done" status)

## [0.0.22] - 2025-10-29

### Fixed

- Resolve intermittent 404 errors when fetching GitHub releases by:
  - Adding proper GitHub API headers (Accept, User-Agent, API version)
  - Implementing robust fallbacks: `latest` → list releases; tag lookup with and without `v` prefix; final search in the releases list
  - Improves reliability when the `releases/latest` endpoint is unavailable or when tags are prefixed differently

### Changed

- Bump version shown in banner to `jp extension v0.0.22`.

# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to the Specify CLI and templates are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.21] - 2025-10-28

### 🎉 Major Architecture Change: Layered Extension Model

Flowspec is now a **layered extension** of GitHub's spec-kit, not a fork!

#### Added

- **Two-Stage Download Architecture**: 
  - Downloads base spec-kit from `github/spec-kit` (Layer 1)
  - Overlays flowspec extensions from `jpoley/flowspec` (Layer 2)
  - Extension overrides base where conflicts exist
  - Enabled by default with `--layered` flag

- **Version Pinning Support**:
  - `--base-version <version>` - Pin base spec-kit to specific version
  - `--extension-version <version>` - Pin flowspec extension to specific version
  - Defaults to "latest" for both
  - Enables reproducible builds and CI/CD integration

- **`flowspec upgrade` Command**:
  - Upgrade existing projects to latest base + extension
  - `--dry-run` - Preview changes without applying
  - `--templates-only` - Only update templates
  - `--base-version` / `--extension-version` - Pin upgrade versions
  - Automatic backup to `.specify-backup/` before applying changes
  - Auto-detects AI assistant and script type from project

- **Configuration Files**:
  - `.spec-kit-compatibility.yml` - Version compatibility matrix
  - `.specify-plugin.yml` - Plugin manifest for future extension system

- **Repository Configuration Constants**:
  ```python
  BASE_REPO_OWNER = "github"
  BASE_REPO_NAME = "spec-kit"
  EXTENSION_REPO_OWNER = "jpoley"
  EXTENSION_REPO_NAME = "flowspec"
  ```

#### Changed

- **`flowspec init` Now Uses Two-Stage Download by Default**:
  - Automatically downloads both base spec-kit and flowspec extension
  - Use `--no-layered` to download only flowspec (legacy mode)
  - Tracker shows separate stages: fetch-base, fetch-extension, extract-base, extract-extension, merge

- **Enhanced `download_template_from_github()`**:
  - Added `repo_owner`, `repo_name`, `version` parameters
  - Supports both "latest" and specific version tags
  - Configurable source repository

- **New `download_and_extract_two_stage()` Function**:
  - Orchestrates two-stage download workflow
  - Downloads base → Extract base → Download extension → Extract extension → Merge
  - Smart directory merging with extension precedence

#### Benefits

- ✅ **Stay current** with upstream spec-kit features via `flowspec upgrade`
- ✅ **Customizable** - Keep flowspec extensions while getting base updates
- ✅ **Reproducible** - Pin versions for stable CI/CD builds
- ✅ **Safe** - Automatic backups before upgrades
- ✅ **Transparent** - See exactly what's downloaded (base vs extension)
- ✅ **Extendable** - Foundation for future plugin system

#### Documentation

- Updated README with layered extension architecture diagram
- Added comprehensive flowspec command documentation
- Created `LAYERED-EXTENSION-ARCHITECTURE.md` with implementation details
- Updated installation and upgrade workflows

#### Migration

Existing flowspec projects can upgrade:
```bash
cd your-project
flowspec upgrade
```

New projects automatically use layered architecture:
```bash
flowspec init my-project --ai claude
```

See `LAYERED-EXTENSION-ARCHITECTURE.md` for complete details.

## [0.0.20] - 2025-10-14

### Added

- **Intelligent Branch Naming**: `create-new-feature` scripts now support `--short-name` parameter for custom branch names
  - When `--short-name` provided: Uses the custom name directly (cleaned and formatted)
  - When omitted: Automatically generates meaningful names using stop word filtering and length-based filtering
  - Filters out common stop words (I, want, to, the, for, etc.)
  - Removes words shorter than 3 characters (unless they're uppercase acronyms)
  - Takes 3-4 most meaningful words from the description
  - **Enforces GitHub's 244-byte branch name limit** with automatic truncation and warnings
  - Examples:
    - "I want to create user authentication" → `001-create-user-authentication`
    - "Implement OAuth2 integration for API" → `001-implement-oauth2-integration-api`
    - "Fix payment processing bug" → `001-fix-payment-processing`
    - Very long descriptions are automatically truncated at word boundaries to stay within limits
  - Designed for AI agents to provide semantic short names while maintaining standalone usability

### Changed

- Enhanced help documentation for `create-new-feature.sh` and `create-new-feature.ps1` scripts with examples
- Branch names now validated against GitHub's 244-byte limit with automatic truncation if needed

## [0.0.19] - 2025-10-10

### Added

- Support for CodeBuddy (thank you to [@lispking](https://github.com/lispking) for the contribution).
- You can now see Git-sourced errors in the Specify CLI.

### Changed

- Fixed the path to the constitution in `plan.md` (thank you to [@lyzno1](https://github.com/lyzno1) for spotting).
- Fixed backslash escapes in generated TOML files for Gemini (thank you to [@hsin19](https://github.com/hsin19) for the contribution).
- Implementation command now ensures that the correct ignore files are added (thank you to [@sigent-amazon](https://github.com/sigent-amazon) for the contribution).

## [0.0.18] - 2025-10-06

### Added

- Support for using `.` as a shorthand for current directory in `flowspec init .` command, equivalent to `--here` flag but more intuitive for users.
- Use the `/speckit.` command prefix to easily discover Spec Kit-related commands.
- Refactor the prompts and templates to simplify their capabilities and how they are tracked. No more polluting things with tests when they are not needed.
- Ensure that tasks are created per user story (simplifies testing and validation).
- Add support for Visual Studio Code prompt shortcuts and automatic script execution.

### Changed

- All command files now prefixed with `speckit.` (e.g., `speckit.specify.md`, `speckit.plan.md`) for better discoverability and differentiation in IDE/CLI command palettes and file explorers

## [0.0.17] - 2025-09-22

### Added

- New `/clarify` command template to surface up to 5 targeted clarification questions for an existing spec and persist answers into a Clarifications section in the spec.
- New `/analyze` command template providing a non-destructive cross-artifact discrepancy and alignment report (spec, clarifications, plan, tasks, constitution) inserted after `/tasks` and before `/implement`.
	- Note: Constitution rules are explicitly treated as non-negotiable; any conflict is a CRITICAL finding requiring artifact remediation, not weakening of principles.

## [0.0.16] - 2025-09-22

### Added

- `--force` flag for `init` command to bypass confirmation when using `--here` in a non-empty directory and proceed with merging/overwriting files.

## [0.0.15] - 2025-09-21

### Added

- Support for Roo Code.

## [0.0.14] - 2025-09-21

### Changed

- Error messages are now shown consistently.

## [0.0.13] - 2025-09-21

### Added

- Support for Kilo Code. Thank you [@shahrukhkhan489](https://github.com/shahrukhkhan489) with [#394](https://github.com/github/spec-kit/pull/394).
- Support for Auggie CLI. Thank you [@hungthai1401](https://github.com/hungthai1401) with [#137](https://github.com/github/spec-kit/pull/137).
- Agent folder security notice displayed after project provisioning completion, warning users that some agents may store credentials or auth tokens in their agent folders and recommending adding relevant folders to `.gitignore` to prevent accidental credential leakage.

### Changed

- Warning displayed to ensure that folks are aware that they might need to add their agent folder to `.gitignore`.
- Cleaned up the `check` command output.

## [0.0.12] - 2025-09-21

### Changed

- Added additional context for OpenAI Codex users - they need to set an additional environment variable, as described in [#417](https://github.com/github/spec-kit/issues/417).

## [0.0.11] - 2025-09-20

### Added

- Codex CLI support (thank you [@honjo-hiroaki-gtt](https://github.com/honjo-hiroaki-gtt) for the contribution in [#14](https://github.com/github/spec-kit/pull/14))
- Codex-aware context update tooling (Bash and PowerShell) so feature plans refresh `AGENTS.md` alongside existing assistants without manual edits.

## [0.0.10] - 2025-09-20

### Fixed

- Addressed [#378](https://github.com/github/spec-kit/issues/378) where a GitHub token may be attached to the request when it was empty.

## [0.0.9] - 2025-09-19

### Changed

- Improved agent selector UI with cyan highlighting for agent keys and gray parentheses for full names

## [0.0.8] - 2025-09-19

### Added

- Windsurf IDE support as additional AI assistant option (thank you [@raedkit](https://github.com/raedkit) for the work in [#151](https://github.com/github/spec-kit/pull/151))
- GitHub token support for API requests to handle corporate environments and rate limiting (contributed by [@zryfish](https://github.com/@zryfish) in [#243](https://github.com/github/spec-kit/pull/243))

### Changed

- Updated README with Windsurf examples and GitHub token usage
- Enhanced release workflow to include Windsurf templates

## [0.0.7] - 2025-09-18

### Changed

- Updated command instructions in the CLI.
- Cleaned up the code to not render agent-specific information when it's generic.


## [0.0.6] - 2025-09-17

### Added

- opencode support as additional AI assistant option

## [0.0.5] - 2025-09-17

### Added

- Qwen Code support as additional AI assistant option

## [0.0.4] - 2025-09-14

### Added

- SOCKS proxy support for corporate environments via `httpx[socks]` dependency

### Fixed

N/A

### Changed

N/A

