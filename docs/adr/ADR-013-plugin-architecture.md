# ADR-013: Claude Code Plugin Architecture

**Status**: Accepted
**Date**: 2025-12-04
**Author**: Enterprise Software Architect (Kinsale Host)
**Context**: Task-081 - Claude Plugin Architecture

---

## Context and Problem Statement

JP Spec Kit currently distributes via `uv tool install specify-cli`, which provides the CLI but requires manual setup of `.claude/` directory structure (commands, skills, hooks, MCP configs). Users must run `specify init` to scaffold these files into their project.

**Problems**:
- **Two-step setup**: Install CLI + run `specify init` (friction for new users)
- **Update pain**: CLI updates via `uv`, but `.claude/` files manually copied (no auto-update)
- **Version skew**: User's `.claude/commands` may lag behind CLI capabilities
- **Discovery**: Users don't know about new slash commands without reading release notes
- **No marketplace presence**: Can't discover JP Spec Kit in Claude Code plugin marketplace

**Goal**: Create Claude Code plugin distribution alongside UV tool, enabling one-click installation, automatic updates, and marketplace discovery while preserving CLI for bootstrapping and local development.

---

## Decision Drivers

1. **Dual Distribution**: Plugin for runtime, UV tool for bootstrapping
2. **Auto-Updates**: Plugin updates don't require user intervention
3. **Marketplace Discovery**: Increase adoption via Claude Code marketplace
4. **Non-Invasive**: Plugin doesn't modify user files (commands/skills are read-only)
5. **Backward Compatibility**: Existing `uv tool install` workflow still works
6. **Clear Boundaries**: Define what belongs in plugin vs. CLI vs. project files

---

## Considered Options

### Option 1: Plugin-Only Distribution
**Approach**: Replace `uv tool install` with Claude Code plugin exclusively

**Pros**:
- Single distribution channel
- Auto-updates for all components
- Marketplace discovery built-in

**Cons**:
- Loses CLI for automation/CI (no `specify` command)
- Can't bootstrap new projects without Claude Code running
- No offline usage
- Breaks existing `uv` workflows

### Option 2: Plugin as Wrapper Around UV Tool
**Approach**: Plugin internally calls `uv tool install specify-cli` for CLI commands

**Pros**:
- Leverages existing UV distribution
- Preserves CLI for automation
- Plugin handles `.claude/` files

**Cons**:
- Complex dependency chain (plugin → uv → specify-cli)
- Requires UV installed (extra requirement)
- Harder to debug version conflicts

### Option 3: Dual Distribution (Plugin + UV Tool, Independent)
**Approach**: Plugin contains `.claude/` files only, UV tool provides CLI, both installed independently

**Pros**:
- Clear separation of concerns
- CLI works standalone (automation, CI)
- Plugin works standalone (runtime commands/skills)
- No version coupling
- Users choose their install method

**Cons**:
- Two installation steps (but each optional)
- Potential for version mismatch (mitigated by docs)

---

## Decision Outcome

**Chosen Option**: **Option 3 - Dual Distribution (Independent)**

Plugin provides runtime `.claude/` components, UV tool provides CLI. Both can be used independently or together.

### Rationale

This approach provides the best balance of:
- **Flexibility**: Users choose plugin-only (runtime), CLI-only (automation), or both
- **Auto-Updates**: Plugin updates slash commands/skills without user action
- **Offline Support**: CLI works without Claude Code running
- **CI/CD Integration**: `specify` CLI available in CI pipelines
- **Marketplace Presence**: Plugin discoverable in Claude marketplace

---

## Plugin Architecture

### Plugin Manifest

**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "jp-spec-kit",
  "version": "0.0.250",
  "display_name": "JP Spec Kit - Spec-Driven Development",
  "description": "Slash commands, agents, and tools for Spec-Driven Development (SDD) methodology",
  "author": "JP Spec Kit Contributors",
  "license": "MIT",
  "homepage": "https://github.com/jpoley/jp-spec-kit",
  "repository": "https://github.com/jpoley/jp-spec-kit",
  "icon": ".claude-plugin/icon.png",
  "keywords": [
    "spec-driven-development",
    "sdd",
    "workflow",
    "architecture",
    "quality",
    "testing"
  ],
  "compatibility": {
    "claude_code_version": ">=2.0.0"
  },
  "components": {
    "commands": {
      "path": ".claude/commands",
      "pattern": "**/*.md"
    },
    "skills": {
      "path": ".claude/skills",
      "pattern": "**/*.md"
    },
    "hooks": {
      "path": ".claude/hooks",
      "config": ".claude/hooks/hooks.json"
    },
    "mcp": {
      "config": ".mcp.json"
    }
  },
  "permissions": {
    "filesystem": {
      "read": ["memory/**", "backlog/**", "docs/**"],
      "write": ["memory/**", "backlog/**", "docs/**", ".claude/hooks/logs/**"]
    },
    "network": {
      "allowed_domains": ["github.com", "pypi.org"]
    },
    "commands": {
      "execute": ["backlog", "specify", "git", "gh"]
    }
  },
  "configuration": {
    "workflow_mode": {
      "type": "enum",
      "default": "full-sdd",
      "options": ["full-sdd", "spec-light", "custom"],
      "description": "SDD workflow complexity level"
    },
    "quality_threshold": {
      "type": "number",
      "default": 70,
      "min": 0,
      "max": 100,
      "description": "Minimum spec quality score for implementation"
    },
    "enable_quality_gates": {
      "type": "boolean",
      "default": true,
      "description": "Run quality gates before /jpspec:implement"
    }
  }
}
```

### Marketplace Manifest

**File**: `.claude-plugin/marketplace.json`

```json
{
  "listing": {
    "title": "JP Spec Kit - Spec-Driven Development Workflow",
    "tagline": "Professional SDD workflow with slash commands, agents, and quality gates",
    "category": "Development Workflow",
    "tags": ["architecture", "testing", "workflow", "quality", "documentation"],
    "icon_url": "https://raw.githubusercontent.com/jpoley/jp-spec-kit/main/.claude-plugin/icon.png",
    "screenshots": [
      {
        "url": "https://raw.githubusercontent.com/jpoley/jp-spec-kit/main/.claude-plugin/screenshots/jpspec-workflow.png",
        "caption": "Full SDD workflow from assess to deploy"
      },
      {
        "url": "https://raw.githubusercontent.com/jpoley/jp-spec-kit/main/.claude-plugin/screenshots/quality-gates.png",
        "caption": "Automated quality gates before implementation"
      },
      {
        "url": "https://raw.githubusercontent.com/jpoley/jp-spec-kit/main/.claude-plugin/screenshots/backlog-integration.png",
        "caption": "Integrated backlog task management"
      }
    ]
  },
  "readme": "README-MARKETPLACE.md",
  "changelog": "CHANGELOG.md",
  "documentation": "https://github.com/jpoley/jp-spec-kit/tree/main/docs",
  "support": {
    "issues": "https://github.com/jpoley/jp-spec-kit/issues",
    "discussions": "https://github.com/jpoley/jp-spec-kit/discussions",
    "email": "support@jpspeckit.dev"
  },
  "pricing": {
    "model": "free",
    "license": "MIT"
  },
  "stats": {
    "min_installs_for_display": 10
  }
}
```

---

## Component Distribution

### What Goes in Plugin

**Included** (read-only runtime components):
- `/jpspec:*` commands (assess, specify, research, plan, implement, validate, operate)
- `/speckit:*` commands (specify, constitution, plan, tasks, analyze, clarify, checklist, implement)
- Skills (5 core SDD skills: sdd-methodology, architect, pm-planner, qa-validator, security-reviewer)
- Hooks configuration (`hooks.json`)
- MCP server configurations (`.mcp.json`)
- Agent context templates (for launching specialized agents)

**Excluded** (project-specific, user-managed):
- Constitution (`memory/constitution.md`)
- Project-specific specs (`memory/spec.md`, `memory/plan.md`)
- Backlog tasks (`backlog/tasks/`)
- Project documentation (`docs/`)
- Custom hooks (`.claude/hooks/*.sh` scripts)
- Workflow configuration (`jpspec_workflow.yml`)

### What Stays in UV Tool

**Included** (CLI and scaffolding):
- `specify` CLI command
- Project initialization (`specify init`)
- Workflow validation (`specify workflow validate`)
- Quality analysis (`specify quality`)
- Constitution management (`specify constitution validate`)
- Template rendering
- Project detection and scaffolding

**Excluded**:
- Claude Code slash commands (moved to plugin)
- Agent skills (moved to plugin)

---

## Installation Flows

### Flow 1: Plugin-Only (Runtime User)

**Use Case**: Developer only uses Claude Code, doesn't need CLI automation

```bash
# In Claude Code
> /install jp-spec-kit

Installing JP Spec Kit plugin...
✓ Downloaded v0.0.250
✓ Registered 15 slash commands
✓ Registered 5 skills
✓ Configured hooks
✓ Configured MCP servers

Available commands:
  /jpspec:assess     - Evaluate if SDD workflow appropriate
  /jpspec:specify    - Create feature specification
  /jpspec:plan       - Generate architecture and implementation plan
  /jpspec:implement  - Execute implementation with code review
  /jpspec:validate   - Run QA, security, and docs validation
  /jpspec:operate    - Configure CI/CD, K8s, observability

Try: /jpspec:assess --feature your-feature-name
```

**Result**: User can run `/jpspec:*` and `/speckit:*` commands, but has no `specify` CLI.

### Flow 2: CLI-Only (Automation User)

**Use Case**: CI pipeline needs `specify` commands, no Claude Code runtime

```bash
# Install CLI
uv tool install specify-cli

# Bootstrap project
specify init my-project

# Use in CI
specify workflow validate
specify quality --json > quality-report.json
specify constitution validate || exit 1
```

**Result**: User has `specify` CLI for automation, but no Claude Code slash commands.

### Flow 3: Both (Full Experience)

**Use Case**: Developer wants CLI for automation + plugin for runtime

```bash
# Install CLI
uv tool install specify-cli

# Bootstrap project
specify init my-project

# In Claude Code, install plugin
> /install jp-spec-kit

# Now has both:
# - CLI: specify quality, specify init, etc.
# - Runtime: /jpspec:*, /speckit:*, skills
```

**Result**: User has full capabilities (CLI + runtime commands).

---

## Version Management

### Plugin Versioning

**Version**: Matches JP Spec Kit release version (e.g., `v0.0.250`)

**Update Mechanism**: Claude Code auto-updates plugins (user can disable)

**Version Display**:
```bash
> /jpspec:version

JP Spec Kit Plugin
Version: v0.0.250
Released: 2025-12-04
Changelog: https://github.com/jpoley/jp-spec-kit/releases/tag/v0.0.250

Installed Components:
  Commands: 15
  Skills: 5
  Hooks: 3
  MCP Servers: 2
```

### CLI Versioning

**Version**: Independent of plugin (both track JP Spec Kit releases)

**Update Mechanism**: Manual via `uv tool upgrade specify-cli`

**Version Check**:
```bash
$ specify version

Specify CLI v0.0.250
Released: 2025-12-04

To upgrade: uv tool upgrade specify-cli
```

### Version Compatibility

**Compatibility Matrix**:

| Plugin Version | Compatible CLI Versions | Notes |
|----------------|-------------------------|-------|
| v0.0.250 | v0.0.240 - v0.0.250 | Full compatibility |
| v0.1.x | v0.1.x | Breaking changes in v0.1.0 |

**Compatibility Check**:
```bash
> /jpspec:check-compatibility

Plugin Version: v0.0.250
CLI Version: v0.0.245 (installed)

Status: ✓ Compatible

Note: CLI v0.0.250 available. Run 'uv tool upgrade specify-cli' to update.
```

---

## Plugin Directory Structure

```
jp-spec-kit/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest
│   ├── marketplace.json         # Marketplace listing
│   ├── icon.png                 # Plugin icon (256x256)
│   ├── screenshots/             # Marketplace screenshots
│   │   ├── jpspec-workflow.png
│   │   ├── quality-gates.png
│   │   └── backlog-integration.png
│   └── README-MARKETPLACE.md    # Marketplace description
├── .claude/
│   ├── commands/
│   │   ├── jpspec/              # /jpspec:* commands
│   │   │   ├── assess.md
│   │   │   ├── specify.md
│   │   │   ├── research.md
│   │   │   ├── plan.md
│   │   │   ├── implement.md
│   │   │   ├── validate.md
│   │   │   └── operate.md
│   │   └── speckit/             # /speckit:* commands
│   │       ├── specify.md
│   │       ├── constitution.md
│   │       ├── plan.md
│   │       ├── tasks.md
│   │       ├── analyze.md
│   │       ├── clarify.md
│   │       ├── checklist.md
│   │       └── implement.md
│   ├── skills/
│   │   ├── sdd-methodology.md   # Workflow guidance skill
│   │   ├── architect.md         # Architecture decisions skill
│   │   ├── pm-planner.md        # Task decomposition skill
│   │   ├── qa-validator.md      # Quality validation skill
│   │   └── security-reviewer.md # Security review skill
│   ├── hooks/
│   │   └── hooks.json           # Hook configuration (not scripts)
│   └── agents/
│       └── contexts/            # Agent context templates
│           ├── researcher.md
│           ├── business-validator.md
│           ├── software-architect.md
│           ├── platform-engineer.md
│           ├── frontend-engineer.md
│           ├── backend-engineer.md
│           ├── code-reviewer.md
│           ├── quality-guardian.md
│           ├── secure-by-design-engineer.md
│           ├── tech-writer.md
│           ├── release-manager.md
│           └── sre-agent.md
├── .mcp.json                    # MCP server configurations
├── src/specify_cli/             # CLI source code (UV tool)
├── templates/                   # Project templates (CLI)
└── docs/                        # Documentation
```

---

## Hooks Architecture

### Plugin Hook Configuration

**File**: `.claude/hooks/hooks.json`

```json
{
  "version": "1.0",
  "hooks": {
    "pre-implement": {
      "description": "Run quality gates before implementation",
      "script": ".claude/hooks/pre-implement.sh",
      "enabled": true,
      "timeout_ms": 30000
    },
    "session-start": {
      "description": "Display project context on session start",
      "script": ".claude/hooks/session-start.sh",
      "enabled": true,
      "timeout_ms": 10000
    },
    "pre-commit": {
      "description": "Verify DCO sign-off on commits",
      "script": ".claude/hooks/pre-commit.sh",
      "enabled": true,
      "timeout_ms": 5000
    }
  },
  "environment": {
    "SPECIFY_FEATURE": "",
    "SPECIFY_QUALITY_THRESHOLD": "70"
  }
}
```

**Note**: Plugin includes `hooks.json` configuration but NOT hook scripts (`.sh` files). Hook scripts are project-specific and installed by CLI (`specify init`).

**Rationale**: Configuration is read-only and global, scripts are writable and project-customizable.

---

## MCP Server Integration

**File**: `.mcp.json`

```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp"],
      "env": {}
    },
    "github": {
      "command": "gh",
      "args": ["mcp"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Plugin Behavior**: Plugin includes MCP configurations that reference external CLIs (`backlog`, `gh`). If CLIs not installed, plugin warns but doesn't block.

**Installation Check**:
```bash
> /jpspec:check-dependencies

Checking dependencies...

Required CLIs:
  ✓ git (2.43.0)
  ✓ gh (2.40.0)
  ✗ backlog (not installed)

MCP Servers:
  ✗ backlog (CLI not found)
  ✓ github (authenticated)

Warning: backlog CLI not installed. Task management features unavailable.
Install: https://backlog.md/install
```

---

## Command Migration Strategy

### Phase 1: Dual Distribution (Current Release)

**Goal**: Introduce plugin without breaking existing workflows

**Changes**:
- Publish plugin to marketplace
- Keep commands in both CLI (`templates/.claude/commands/`) and plugin (`.claude/commands/`)
- CLI `specify init` still copies commands to project
- Plugin provides same commands (read-only)

**User Impact**: None (backward compatible)

### Phase 2: Encourage Plugin Adoption (3 months)

**Goal**: Guide users toward plugin for commands, CLI for automation

**Changes**:
- CLI `specify init` prints: "Install JP Spec Kit plugin for auto-updating commands: /install jp-spec-kit"
- Documentation emphasizes plugin-first approach
- CLI `specify upgrade` offers to remove local commands if plugin detected

**User Impact**: Soft migration encouragement

### Phase 3: Plugin-First (6 months)

**Goal**: Plugin becomes primary command distribution

**Changes**:
- CLI `specify init` no longer copies commands by default
- Add `--legacy` flag to copy commands (for offline/air-gapped environments)
- Documentation shows plugin installation first

**User Impact**: New users default to plugin, existing users unaffected

---

## Decision Tree: Plugin vs. CLI

**When to use Plugin**:
- ✅ Interactive Claude Code sessions
- ✅ Want auto-updates for commands/skills
- ✅ Discover new features via marketplace
- ✅ Don't need offline access

**When to use CLI**:
- ✅ CI/CD pipelines (automation)
- ✅ Offline/air-gapped environments
- ✅ Project bootstrapping (`specify init`)
- ✅ Workflow validation (`specify workflow validate`)
- ✅ Quality analysis (`specify quality`)

**When to use Both**:
- ✅ Development team (plugin for runtime, CLI for CI)
- ✅ Want both auto-updates and automation
- ✅ Full feature access

---

## Testing Strategy

### Plugin Integration Tests

```python
def test_plugin_installation():
    """Verify plugin installs and registers components."""
    result = claude_code.install_plugin("jp-spec-kit")

    assert result.success
    assert result.version == "v0.0.250"
    assert len(result.commands) == 15
    assert len(result.skills) == 5

def test_plugin_command_execution():
    """Verify /jpspec:assess command works after plugin install."""
    claude_code.install_plugin("jp-spec-kit")

    result = claude_code.run_command("/jpspec:assess", feature="user-auth")

    assert result.success
    assert "Assessment Report" in result.output

def test_plugin_update():
    """Verify plugin auto-updates to newer version."""
    # Install v0.0.240
    claude_code.install_plugin("jp-spec-kit", version="v0.0.240")

    # Simulate update available
    claude_code.check_updates()

    # Verify updated to v0.0.250
    plugin = claude_code.get_plugin("jp-spec-kit")
    assert plugin.version == "v0.0.250"
```

### CLI Integration Tests

```python
def test_cli_standalone():
    """Verify CLI works without plugin installed."""
    # Uninstall plugin
    claude_code.uninstall_plugin("jp-spec-kit")

    # CLI should still work
    result = subprocess.run(["specify", "init", "test-project"], capture_output=True)
    assert result.returncode == 0

    # Verify commands copied to project
    assert Path("test-project/.claude/commands/jpspec/assess.md").exists()

def test_cli_with_plugin():
    """Verify CLI detects plugin and skips command copying."""
    claude_code.install_plugin("jp-spec-kit")

    result = subprocess.run(["specify", "init", "test-project"], capture_output=True)

    assert "JP Spec Kit plugin detected" in result.stdout
    assert "Commands provided by plugin (not copied)" in result.stdout
```

### End-to-End Tests

```python
def test_full_workflow_with_plugin():
    """Verify complete SDD workflow using plugin commands."""
    # Install plugin
    claude_code.install_plugin("jp-spec-kit")

    # Run workflow
    claude_code.run_command("/jpspec:assess", feature="user-auth")
    claude_code.run_command("/jpspec:specify", feature="user-auth")
    claude_code.run_command("/jpspec:plan", feature="user-auth")
    claude_code.run_command("/jpspec:implement", feature="user-auth")

    # Verify artifacts created
    assert Path("memory/spec.md").exists()
    assert Path("memory/plan.md").exists()
    assert Path("docs/adr/").exists()
```

---

## Consequences

### Positive

- **Auto-Updates**: Commands/skills update automatically via plugin
- **Marketplace Discovery**: Increases adoption (10x discoverability boost expected)
- **Reduced Setup Friction**: One-click install vs. multi-step CLI setup
- **Separation of Concerns**: Plugin = runtime, CLI = automation/scaffolding
- **Offline Support**: CLI still works without Claude Code
- **CI/CD Integration**: CLI available in pipelines without plugin dependency

### Negative

- **Dual Maintenance**: Must keep plugin and CLI templates in sync
- **Version Confusion**: Users may wonder "plugin vs. CLI" differences
- **Documentation Split**: Need to document both installation paths
- **Potential Divergence**: Plugin and CLI could drift over time

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Plugin and CLI diverge | Inconsistent behavior | Automated tests verify command parity |
| Users install both and have conflicts | Confusing errors | Detection logic warns if both detected |
| Plugin updates break user workflows | Trust erosion | Semantic versioning, test suite, gradual rollout |
| CLI becomes unmaintained | Offline users stranded | Commitment to dual distribution in docs |
| Marketplace rejection | No distribution channel | Pre-review with Claude team, follow guidelines |

---

## References

- **Task-081**: Claude Plugin Architecture
- **Claude Code Plugin Specification**: https://claude.ai/docs/plugins
- **UV Tool Distribution**: https://docs.astral.sh/uv/
- **Semantic Versioning**: https://semver.org/

---

**Decision**: The dual distribution model (plugin + CLI) provides the best user experience across interactive development (plugin), automation (CLI), and offline scenarios, with clear boundaries and auto-update capabilities.
