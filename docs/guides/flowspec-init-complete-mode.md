# Flowspec Init: Complete Mode

## Overview

The `flowspec init` command supports a `--complete` flag that enables **ALL optional features** in one command, making it ideal for setting up production-ready projects with comprehensive tooling.

## Default vs Complete Mode

### Default Mode

When you run `flowspec init` without flags, you get:

- **Project structure**: Core directories and files
- **Skills**: Deployed to `.claude/skills/` (opt-out with `--skip-skills`)
- **Hooks**: 3 hooks enabled by default (opt-out with `--no-hooks`)
- **Git**: Repository initialized (opt-out with `--no-git`)
- **Constitution**: Basic project constitution

### Complete Mode

When you run `flowspec init --complete`, you get **everything** from default mode plus:

- **CI/CD Templates**: Full GitHub Actions workflows with lint, test, security scanning, SBOM generation, and deployment stages
- **VSCode Extensions**: Comprehensive `extensions.json` with recommended extensions for Python, testing, security, and more
- **MCP Configuration**: Model Context Protocol config (`.mcp.json`) for AI tool integrations

## Usage

### Basic Complete Mode

```bash
# Initialize new project with all features
flowspec init my-project --complete

# Initialize in current directory with all features
flowspec init --here --complete

# Complete mode with specific AI assistant
flowspec init my-project --ai claude --complete
```

### Complete Mode Overrides

The `--complete` flag **overrides** opt-out flags:

```bash
# This will ENABLE skills despite --skip-skills
flowspec init my-project --skip-skills --complete

# This will ENABLE hooks despite --no-hooks
flowspec init my-project --no-hooks --complete

# This will INITIALIZE git despite --no-git
flowspec init my-project --no-git --complete
```

**Design rationale**: Complete mode is an explicit request for maximum features, so it takes precedence over individual opt-out flags.

## What Gets Deployed

### 1. Skills (`.claude/skills/`)

Claude Code skills for specialized tasks:
- Code analysis and refactoring
- Testing and quality checks
- Security scanning
- Documentation generation

**Location**: `.claude/skills/`

### 2. Hooks (`.flowspec/hooks/`)

Three hooks enabled by default:
- `run-tests`: Runs test suite after implementation
- `lint-code`: Runs linter and formatter on task completion
- `quality-gate`: Checks code quality before validation

**Location**: `.flowspec/hooks/hooks.yaml`

### 3. CI/CD Templates (`.github/workflows/`)

Complete GitHub Actions workflows for:
- **Build**: Lint, format check, type check, tests with coverage
- **Security**: SAST (Bandit), SCA (pip-audit, Safety)
- **SBOM**: Software Bill of Materials generation (CycloneDX)
- **Container**: Docker image build with attestation (if Dockerfile present)
- **Attestation**: SLSA provenance signing
- **Deploy**: Staging and production deployment stages

**Location**: `.github/workflows/python-ci-cd.yml` (and others)

### 4. VSCode Extensions (`.vscode/extensions.json`)

Recommended extensions for:
- **AI assistants**: GitHub Copilot
- **Python**: Python extension, Pylance, Ruff
- **Testing**: Test adapter
- **Git**: GitLens
- **Markdown**: All-in-one, linter
- **YAML**: Red Hat YAML support
- **Security**: Snyk vulnerability scanner
- **Formatting**: Prettier, EditorConfig

**Location**: `.vscode/extensions.json`

### 5. MCP Configuration (`.mcp.json`)

Model Context Protocol server configuration for:
- **GitHub**: Repos, issues, PRs, code search
- **Serena**: LSP-grade code understanding
- **Playwright**: Browser automation
- **Trivy**: Container/IaC security scanning
- **Semgrep**: SAST code scanning
- **Backlog**: Task management
- **Flowspec Security**: Security scanner with AI assistance

**Location**: `.mcp.json`

## When to Use Complete Mode

Use `--complete` when:
- Starting a production-ready project
- Setting up a repository with full CI/CD from day one
- Working in a team environment with standardized tooling
- Building a project that requires comprehensive security and compliance

Use **default mode** when:
- Prototyping or experimenting
- Working on a small personal project
- You want minimal setup and will add features incrementally

## Acceptance Criteria Validation

| AC | Criterion | Status |
|----|-----------|--------|
| #1 | `--complete` flag enables all optional features | ✓ |
| #2 | Skills deployed to `.claude/skills/` | ✓ |
| #3 | All hooks enabled in `hooks.yaml` | ✓ |
| #4 | Full CI/CD template with lint, test, security jobs | ✓ |
| #5 | Complete VSCode settings and extensions | ✓ |
| #6 | MCP configuration created | ✓ |
| #7 | Documentation explains `--complete` vs default behavior | ✓ |

## Examples

### Example 1: New Production Project

```bash
# Create production-ready project with all features
flowspec init my-production-app --complete --ai claude

# Result:
# - Full project structure
# - All skills deployed
# - Hooks enabled
# - CI/CD workflows configured
# - VSCode extensions configured
# - MCP config ready
# - Git initialized with initial commit
```

### Example 2: Existing Repository Enhancement

```bash
# Add complete tooling to existing repository
cd my-existing-project
flowspec init --here --complete --force

# Result:
# - All features merged into existing directory
# - Existing files preserved (or overwritten if using --force)
# - Complete tooling stack added
```

### Example 3: Team-Standardized Setup

```bash
# Consistent setup across team
flowspec init team-project --ai claude,copilot --complete --constitution medium

# Result:
# - Multi-agent setup (Claude + Copilot)
# - Medium-tier constitution (business-focused)
# - All tooling standardized
```

## Post-Initialization

After running `flowspec init --complete`, customize:

1. **CI/CD workflows**: Update template placeholders in `.github/workflows/*.yml`
2. **VSCode extensions**: Add/remove extensions in `.vscode/extensions.json`
3. **MCP config**: Enable/disable servers in `.mcp.json`
4. **Hooks**: Customize scripts in `.flowspec/hooks/*.sh`

## See Also

- [Hooks Quickstart](hooks-quickstart.md)
- [Pre-commit Hooks](pre-commit-hooks.md)
- [Backlog Git Hooks](backlog-git-hooks.md)
- [MCP Configuration](../../memory/mcp-configuration.md)
