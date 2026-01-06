# ADR-002: Upgrade-Repo Architecture Redesign

## Status

Proposed

## Context

### The Penthouse View: Business Context

Flowspec is a spec-driven development (SDD) toolkit that enables AI-assisted development workflows through slash commands like `/flow:assess`, `/flow:specify`, and `/flow:implement`. The system generates templates and configuration for target repositories, enabling them to leverage flowspec's multi-agent orchestration capabilities.

**The Problem:**

The `flowspec upgrade-repo` command is currently **completely broken**, creating a P0 blocker for the flowspec release. When users run `flowspec upgrade-repo` in their projects, the command:

1. ✅ Downloads templates from the flowspec repository
2. ✅ Creates backups of existing files
3. ❌ **Deploys templates with wrong agent naming** (hyphens instead of dots)
4. ❌ **Does NOT update `.mcp.json`** MCP server configuration
5. ❌ **Does NOT sync `.claude/skills/`** (21 skills available, only 9 deployed)
6. ❌ **Does NOT update `flowspec_workflow.yml`** to v2.0
7. ❌ **Does NOT remove deprecated files** (`.specify/`, `_DEPRECATED_*.md`)
8. ❌ **Leaves broken `{{INCLUDE:}}` directives** referencing non-existent partials
9. ❌ **Leaves `/flow:operate` references** despite command removal

**Business Impact:**

- **All downstream projects are affected**: auth.poley.dev, lincoln, axonjet, falcondev, and any other project using flowspec
- **VSCode Copilot integration is broken**: Agents don't appear correctly in the agent dropdown
- **Deployment velocity is blocked**: Manual fixes are required post-upgrade
- **User trust is eroded**: The upgrade command produces broken output
- **Release is blocked**: Cannot publish flowspec until upgrade process works

**Organizational Impact:**

- **Developer productivity**: Manual template synchronization wastes engineering time
- **Support burden**: Users require assistance troubleshooting broken upgrades
- **Adoption risk**: Broken upgrades discourage flowspec adoption
- **Technical debt**: Each project accumulates drift from the canonical template set

**Success Metrics:**

- `flowspec upgrade-repo` produces a **fully functional** flowspec integration with **zero manual intervention**
- VSCode Copilot agents appear correctly and work on first run
- MCP servers start successfully after upgrade
- Deprecated files and commands are automatically cleaned up
- Workflow configuration matches the current flowspec version

### The Engine Room View: Technical Context

The current `upgrade_repo()` function (lines 5654-5977 in `src/flowspec_cli/__init__.py`) uses a two-stage template merge strategy:

```python
def upgrade_repo(
    base_version: str = None,
    extension_version: str = None,
    dry_run: bool = False,
    templates_only: bool = False,
    skip_tls: bool = False,
    debug: bool = False,
    github_token: str = None,
    branch: str = None,
):
    """Upgrade repository templates to latest spec-kit and flowspec versions."""
    # 1. Detect AI assistant type (claude, copilot, cursor)
    # 2. Create backup with timestamp
    # 3. Call download_and_extract_two_stage()
    # 4. Check backlog-md version compatibility
```

**What `download_and_extract_two_stage()` does:**
- Downloads base-spec-kit templates from GitHub
- Downloads flowspec extension templates from GitHub
- Merges with extension precedence (flowspec overrides base-spec-kit)
- Applies merged templates to project directory

**What's Missing:**

The function **only** updates template files. It does NOT:

1. **Update agent templates correctly**: Wrong naming convention deployed
2. **Regenerate MCP configuration**: `generate_mcp_json()` exists but is not called
3. **Sync skills directory**: `.claude/skills/` templates exist but not copied
4. **Upgrade workflow config**: `flowspec_workflow.yml` v2.0 templates exist but not applied
5. **Clean deprecated artifacts**: Old files persist indefinitely
6. **Remove broken directives**: `{{INCLUDE:}}` syntax doesn't work, should be removed
7. **Purge removed commands**: `/flow:operate` was removed but references remain

**Root Cause Analysis:**

The upgrade process was designed for **template-only** updates. It assumes templates are static content that can be blindly copied. This assumption breaks down with:

- **Version-specific migrations**: v1.0 → v2.0 workflow config requires semantic upgrades
- **Computed artifacts**: `.mcp.json` is generated based on tech stack, not a static template
- **Cleanup operations**: Deprecated files must be actively removed, not just ignored
- **Naming convention changes**: Agent filename refactoring requires intelligent renaming
- **Directive removal**: Broken `{{INCLUDE:}}` directives need search-and-replace, not template merge

**Architectural Gap:**

The current design lacks a **migration framework** to handle version-specific transformations, cleanups, and validations.

## Decision

**We will redesign `upgrade-repo` as a multi-phase orchestration process with validation gates and version-aware migrations.**

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Upgrade-Repo Orchestration Pipeline                       │
└─────────────────────────────────────────────────────────────┘
         │
         ├─► Phase 0: Pre-Upgrade Validation
         │   ├─ Detect current version
         │   ├─ Validate project structure
         │   ├─ Check for uncommitted changes (warn)
         │   └─ Create timestamped backup
         │
         ├─► Phase 1: Template Updates
         │   ├─ Download base-spec-kit templates
         │   ├─ Download flowspec extension templates
         │   ├─ Merge templates (extension precedence)
         │   ├─ Apply agent naming fixes (hyphen → dot)
         │   └─ Deploy merged templates
         │
         ├─► Phase 2: Configuration Synthesis
         │   ├─ Regenerate .mcp.json (tech-stack aware)
         │   ├─ Upgrade flowspec_workflow.yml to v2.0
         │   ├─ Sync .claude/skills/ directory
         │   └─ Update .vscode/extensions.json
         │
         ├─► Phase 3: Cleanup & Migrations
         │   ├─ Remove deprecated files (.specify/, _DEPRECATED_*)
         │   ├─ Purge /flow:operate references
         │   ├─ Remove {{INCLUDE:}} directives from .github/prompts/
         │   └─ Clean up legacy command namespaces
         │
         ├─► Phase 4: Post-Upgrade Validation
         │   ├─ Verify agent files use correct naming
         │   ├─ Validate flowspec_workflow.yml schema
         │   ├─ Check MCP server configuration
         │   ├─ Verify skills directory completeness
         │   └─ Run flowspec gate (if available)
         │
         └─► Phase 5: Reporting & Next Steps
             ├─ Git diff summary
             ├─ Backup location reminder
             ├─ MCP server health check offer
             └─ Suggested next actions
```

### Component Design

#### 1. Migration Registry

**Purpose:** Version-specific transformations and cleanups.

```python
@dataclass
class Migration:
    """A version-specific migration operation."""
    version: str  # Target version (e.g., "2.0")
    name: str     # Migration name
    execute: Callable[[Path], None]  # Migration function
    validate: Callable[[Path], bool] # Validation function

class MigrationRegistry:
    """Registry of all available migrations."""

    migrations: dict[str, list[Migration]] = {}

    @classmethod
    def register(cls, version: str, migration: Migration):
        """Register a migration for a specific version."""
        if version not in cls.migrations:
            cls.migrations[version] = []
        cls.migrations[version].append(migration)

    @classmethod
    def get_migrations(cls, from_version: str, to_version: str) -> list[Migration]:
        """Get all migrations needed between two versions."""
        # Semantic version comparison and migration path calculation
        ...
```

**Example Migrations:**

```python
# Migration: Upgrade workflow config v1.0 → v2.0
def migrate_workflow_config_v2(project_path: Path) -> None:
    """Upgrade flowspec_workflow.yml from v1.0 to v2.0."""
    workflow_path = project_path / "flowspec_workflow.yml"
    if not workflow_path.exists():
        return

    with open(workflow_path) as f:
        config = yaml.safe_load(f)

    # Add v2.0 sections
    if "roles" not in config:
        config["roles"] = load_default_roles()
    if "custom_workflows" not in config:
        config["custom_workflows"] = load_default_custom_workflows()
    if "agent_loops" not in config:
        config["agent_loops"] = load_default_agent_loops()

    # Remove deprecated sections
    if "operate" in config.get("workflows", {}):
        del config["workflows"]["operate"]

    # Update version
    config["version"] = "2.0"

    with open(workflow_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

# Migration: Remove /flow:operate references
def remove_flow_operate_references(project_path: Path) -> None:
    """Remove all /flow:operate references from project."""
    operate_patterns = [
        r'/flow:operate',
        r'operate transition',
        r'workflow.*operate',
    ]

    files_to_clean = [
        ".claude/commands/**/*.md",
        ".github/prompts/**/*.md",
        "CLAUDE.md",
        "flowspec_workflow.yml",
    ]

    for pattern in files_to_clean:
        for file_path in project_path.glob(pattern):
            clean_file_content(file_path, operate_patterns)

# Migration: Fix agent naming convention
def fix_agent_naming_convention(project_path: Path) -> None:
    """Rename agent files from hyphen to dot notation."""
    agents_dir = project_path / ".github" / "agents"
    if not agents_dir.exists():
        return

    rename_map = {
        "flow-assess.agent.md": "flow.assess.agent.md",
        "flow-specify.agent.md": "flow.specify.agent.md",
        "flow-plan.agent.md": "flow.plan.agent.md",
        "flow-implement.agent.md": "flow.implement.agent.md",
        "flow-validate.agent.md": "flow.validate.agent.md",
        "flow-submit-n-watch-pr.agent.md": "flow.submit-n-watch-pr.agent.md",
    }

    for old_name, new_name in rename_map.items():
        old_path = agents_dir / old_name
        new_path = agents_dir / new_name
        if old_path.exists():
            old_path.rename(new_path)
            # Also fix frontmatter name field
            fix_agent_frontmatter(new_path)
```

#### 2. Artifact Synchronizer

**Purpose:** Keep generated/computed artifacts in sync with templates.

```python
class ArtifactSynchronizer:
    """Synchronize generated artifacts during upgrade."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.tech_stack = detect_tech_stack(project_path)

    def sync_mcp_config(self) -> bool:
        """Regenerate .mcp.json with comprehensive MCP servers."""
        mcp_path = self.project_path / ".mcp.json"

        # Build comprehensive config
        mcp_servers = self._build_mcp_servers()
        mcp_config = {"mcpServers": mcp_servers}

        # Write atomically
        with atomic_write(mcp_path) as f:
            json.dump(mcp_config, f, indent=2)

        return True

    def _build_mcp_servers(self) -> dict:
        """Build MCP server configuration based on tech stack."""
        servers = {
            # Core servers (always included)
            "backlog": {
                "command": "backlog",
                "args": ["mcp", "start"],
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
            },
            "serena": {
                "command": "uvx",
                "args": ["--from", "git+https://github.com/oraios/serena",
                        "serena-mcp-server", "--project", "${PWD}"],
            },
        }

        # Add tech-stack-specific servers
        if "Python" in self.tech_stack["languages"]:
            servers["flowspec-security"] = {
                "command": "uv",
                "args": ["--directory", ".", "run", "python",
                        "-m", "flowspec_cli.security.mcp_server"],
            }

        if self._has_frontend():
            servers["playwright-test"] = {
                "command": "npx",
                "args": ["-y", "@playwright/mcp"],
            }

        # Add security servers
        servers.update({
            "trivy": {
                "command": "npx",
                "args": ["-y", "@aquasecurity/trivy-mcp"],
            },
            "semgrep": {
                "command": "npx",
                "args": ["-y", "@returntocorp/semgrep-mcp"],
            },
        })

        return servers

    def sync_skills(self) -> int:
        """Sync .claude/skills/ from templates."""
        template_skills = Path(__file__).parent / "templates" / ".claude" / "skills"
        target_skills = self.project_path / ".claude" / "skills"

        target_skills.mkdir(parents=True, exist_ok=True)

        synced_count = 0
        for skill_file in template_skills.glob("**/*.md"):
            relative_path = skill_file.relative_to(template_skills)
            target_path = target_skills / relative_path

            # Copy if newer or missing
            if not target_path.exists() or \
               skill_file.stat().st_mtime > target_path.stat().st_mtime:
                shutil.copy2(skill_file, target_path)
                synced_count += 1

        return synced_count

    def upgrade_workflow_config(self) -> bool:
        """Upgrade flowspec_workflow.yml to latest version."""
        # Use migration registry
        migration = MigrationRegistry.get_migration("workflow_config_v2")
        migration.execute(self.project_path)
        return migration.validate(self.project_path)
```

#### 3. Cleanup Orchestrator

**Purpose:** Remove deprecated files and clean up legacy artifacts.

```python
class CleanupOrchestrator:
    """Orchestrate cleanup of deprecated files and content."""

    DEPRECATED_DIRECTORIES = [
        ".specify/",  # Old command namespace
    ]

    DEPRECATED_FILES = [
        ".claude/commands/flow/_DEPRECATED_operate.md",
    ]

    DEPRECATED_PATTERNS = [
        "_DEPRECATED_*.md",
    ]

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.removed_items = []

    def cleanup_directories(self) -> int:
        """Remove deprecated directories."""
        count = 0
        for dir_name in self.DEPRECATED_DIRECTORIES:
            dir_path = self.project_path / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.removed_items.append(f"directory: {dir_name}")
                count += 1
        return count

    def cleanup_files(self) -> int:
        """Remove deprecated files."""
        count = 0
        for file_name in self.DEPRECATED_FILES:
            file_path = self.project_path / file_name
            if file_path.exists():
                file_path.unlink()
                self.removed_items.append(f"file: {file_name}")
                count += 1
        return count

    def cleanup_patterns(self) -> int:
        """Remove files matching deprecated patterns."""
        count = 0
        for pattern in self.DEPRECATED_PATTERNS:
            for file_path in self.project_path.rglob(pattern):
                file_path.unlink()
                self.removed_items.append(f"file: {file_path.relative_to(self.project_path)}")
                count += 1
        return count

    def remove_broken_includes(self) -> int:
        """Remove {{INCLUDE:}} directives from prompt files."""
        prompt_dir = self.project_path / ".github" / "prompts"
        if not prompt_dir.exists():
            return 0

        count = 0
        include_pattern = re.compile(r'\{\{INCLUDE:.*?\}\}')

        for prompt_file in prompt_dir.glob("*.prompt.md"):
            content = prompt_file.read_text()
            if include_pattern.search(content):
                # Remove all {{INCLUDE:}} directives
                cleaned = include_pattern.sub('', content)
                # Clean up multiple blank lines
                cleaned = re.sub(r'\n\n\n+', '\n\n', cleaned)
                prompt_file.write_text(cleaned)
                self.removed_items.append(f"cleaned includes: {prompt_file.name}")
                count += 1

        return count

    def execute_all(self) -> dict[str, int]:
        """Execute all cleanup operations."""
        return {
            "directories": self.cleanup_directories(),
            "files": self.cleanup_files(),
            "patterns": self.cleanup_patterns(),
            "includes": self.remove_broken_includes(),
        }
```

#### 4. Validation Framework

**Purpose:** Verify upgrade success and catch issues early.

```python
@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    severity: str  # "error", "warning", "info"

class UpgradeValidator:
    """Validate upgrade operations."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.results: list[ValidationResult] = []

    def validate_agent_naming(self) -> ValidationResult:
        """Verify agents use dot notation."""
        agents_dir = self.project_path / ".github" / "agents"
        if not agents_dir.exists():
            return ValidationResult(
                passed=False,
                message="No .github/agents/ directory found",
                severity="error"
            )

        # Check for hyphen-notation agents
        hyphen_agents = list(agents_dir.glob("flow-*.agent.md"))
        if hyphen_agents:
            return ValidationResult(
                passed=False,
                message=f"Found {len(hyphen_agents)} agents with hyphen notation",
                severity="error"
            )

        # Check for dot-notation agents
        dot_agents = list(agents_dir.glob("flow.*.agent.md"))
        expected_count = 6  # assess, specify, plan, implement, validate, submit-pr

        if len(dot_agents) != expected_count:
            return ValidationResult(
                passed=False,
                message=f"Expected {expected_count} agents, found {len(dot_agents)}",
                severity="error"
            )

        return ValidationResult(
            passed=True,
            message=f"All {expected_count} agents use correct dot notation",
            severity="info"
        )

    def validate_workflow_config(self) -> ValidationResult:
        """Verify workflow config is v2.0 and valid."""
        workflow_path = self.project_path / "flowspec_workflow.yml"
        if not workflow_path.exists():
            return ValidationResult(
                passed=False,
                message="No flowspec_workflow.yml found",
                severity="error"
            )

        with open(workflow_path) as f:
            config = yaml.safe_load(f)

        # Check version
        if config.get("version") != "2.0":
            return ValidationResult(
                passed=False,
                message=f"Workflow config is v{config.get('version')}, expected v2.0",
                severity="error"
            )

        # Check for deprecated workflows
        if "operate" in config.get("workflows", {}):
            return ValidationResult(
                passed=False,
                message="Workflow config still contains deprecated 'operate' workflow",
                severity="error"
            )

        # Check for required v2.0 sections
        required_sections = ["roles", "custom_workflows", "agent_loops"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            return ValidationResult(
                passed=False,
                message=f"Workflow config missing v2.0 sections: {', '.join(missing)}",
                severity="error"
            )

        return ValidationResult(
            passed=True,
            message="Workflow config is valid v2.0",
            severity="info"
        )

    def validate_mcp_config(self) -> ValidationResult:
        """Verify MCP configuration is complete."""
        mcp_path = self.project_path / ".mcp.json"
        if not mcp_path.exists():
            return ValidationResult(
                passed=False,
                message="No .mcp.json found",
                severity="error"
            )

        with open(mcp_path) as f:
            config = json.load(f)

        # Check for required servers
        required_servers = ["backlog", "github", "serena"]
        servers = config.get("mcpServers", {})
        missing = [s for s in required_servers if s not in servers]

        if missing:
            return ValidationResult(
                passed=False,
                message=f"MCP config missing required servers: {', '.join(missing)}",
                severity="error"
            )

        return ValidationResult(
            passed=True,
            message=f"MCP config has {len(servers)} servers configured",
            severity="info"
        )

    def validate_skills(self) -> ValidationResult:
        """Verify skills directory is synced."""
        skills_dir = self.project_path / ".claude" / "skills"
        if not skills_dir.exists():
            return ValidationResult(
                passed=False,
                message="No .claude/skills/ directory found",
                severity="warning"
            )

        skill_files = list(skills_dir.glob("**/*.md"))
        expected_count = 21  # Based on flowspec template count

        if len(skill_files) < expected_count:
            return ValidationResult(
                passed=False,
                message=f"Skills directory has {len(skill_files)} skills, expected {expected_count}",
                severity="warning"
            )

        return ValidationResult(
            passed=True,
            message=f"Skills directory has {len(skill_files)} skills",
            severity="info"
        )

    def validate_all(self) -> bool:
        """Run all validations and return overall pass/fail."""
        self.results = [
            self.validate_agent_naming(),
            self.validate_workflow_config(),
            self.validate_mcp_config(),
            self.validate_skills(),
        ]

        # Fail if any error-level validation failed
        return all(r.passed or r.severity != "error" for r in self.results)
```

#### 5. Upgraded `upgrade_repo()` Function

**Purpose:** Orchestrate the multi-phase upgrade process.

```python
def upgrade_repo(
    base_version: str = None,
    extension_version: str = None,
    dry_run: bool = False,
    templates_only: bool = False,
    skip_tls: bool = False,
    debug: bool = False,
    github_token: str = None,
    branch: str = None,
):
    """
    Upgrade repository templates to latest spec-kit and flowspec versions.

    This is a comprehensive upgrade that:
    1. Updates templates
    2. Regenerates configuration
    3. Removes deprecated artifacts
    4. Validates the result
    """
    show_banner()
    project_path = Path.cwd()

    # Pre-flight checks
    check_not_source_repo(project_path)
    ai_assistant = detect_ai_assistant(project_path)
    current_version = detect_flowspec_version(project_path)

    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = create_backup(project_path, timestamp)

    # Initialize components
    synchronizer = ArtifactSynchronizer(project_path)
    cleanup = CleanupOrchestrator(project_path)
    validator = UpgradeValidator(project_path)
    migrations = MigrationRegistry.get_migrations(current_version, TARGET_VERSION)

    tracker = StepTracker("Upgrade Flowspec Repository")

    # Phase 0: Pre-Upgrade Validation
    tracker.add("pre-validate", "Pre-upgrade validation")
    tracker.start("pre-validate")
    pre_validation = validator.validate_all()
    tracker.complete("pre-validate", "ready" if pre_validation else "issues detected")

    # Phase 1: Template Updates
    tracker.add("templates", "Update templates")
    tracker.start("templates")
    download_and_extract_two_stage(
        project_path,
        ai_assistant,
        script_type="sh",
        is_current_dir=True,
        verbose=debug,
        tracker=tracker,
        client=http_client,
        debug=debug,
        github_token=github_token,
        base_version=base_version,
        extension_version=extension_version,
        branch=branch,
    )
    tracker.complete("templates", "updated")

    # Phase 2: Configuration Synthesis
    tracker.add("config", "Regenerate configuration")
    tracker.start("config")

    mcp_updated = synchronizer.sync_mcp_config()
    workflow_updated = synchronizer.upgrade_workflow_config()
    skills_synced = synchronizer.sync_skills()

    tracker.complete("config", f"MCP, workflow v2.0, {skills_synced} skills")

    # Phase 3: Cleanup & Migrations
    tracker.add("cleanup", "Clean deprecated artifacts")
    tracker.start("cleanup")

    cleanup_results = cleanup.execute_all()
    total_removed = sum(cleanup_results.values())

    # Run version-specific migrations
    for migration in migrations:
        migration.execute(project_path)

    tracker.complete("cleanup", f"{total_removed} items removed, {len(migrations)} migrations")

    # Phase 4: Post-Upgrade Validation
    tracker.add("validate", "Validate upgrade")
    tracker.start("validate")

    validation_passed = validator.validate_all()

    if validation_passed:
        tracker.complete("validate", "all checks passed")
    else:
        errors = [r for r in validator.results if not r.passed and r.severity == "error"]
        tracker.error("validate", f"{len(errors)} errors")

    # Phase 5: Reporting
    console.print(tracker.render())

    if validation_passed:
        console.print("\n[bold green]Upgrade completed successfully![/bold green]")
    else:
        console.print("\n[bold yellow]Upgrade completed with issues[/bold yellow]")
        console.print("\nValidation results:")
        for result in validator.results:
            if not result.passed:
                icon = "❌" if result.severity == "error" else "⚠️"
                console.print(f"  {icon} {result.message}")

    console.print(f"\n[dim]Backup location: {backup_dir}[/dim]")
    console.print("\n[cyan]Next steps:[/cyan]")
    console.print("  1. Review changes: [cyan]git diff[/cyan]")
    console.print("  2. Test MCP servers: [cyan]./scripts/check-mcp-servers.sh[/cyan]")
    console.print("  3. Verify agents in VSCode Copilot dropdown")
    console.print(f"  4. If issues, restore: [cyan]cp -r {backup_dir}/* .[/cyan]")

    # Offer backlog-md sync
    sync_backlog_version_if_needed()

    # Update version tracking
    write_version_tracking_file(project_path, is_upgrade=True)
```

### Data Flow

```
User runs: flowspec upgrade-repo
    │
    ├─► Detect current state
    │   ├─ AI assistant type
    │   ├─ Current flowspec version
    │   ├─ Tech stack
    │   └─ Uncommitted changes (warning)
    │
    ├─► Create backup
    │   └─ .flowspec-backup-{timestamp}/
    │
    ├─► Download templates
    │   ├─ base-spec-kit (GitHub release)
    │   ├─ flowspec extension (GitHub release or branch)
    │   └─ Merge (extension precedence)
    │
    ├─► Apply templates
    │   ├─ .github/agents/ (with dot notation)
    │   ├─ .claude/commands/
    │   ├─ .flowspec/
    │   └─ templates/
    │
    ├─► Regenerate configuration
    │   ├─ .mcp.json (tech-stack aware)
    │   ├─ flowspec_workflow.yml v2.0
    │   ├─ .claude/skills/ (21 skills)
    │   └─ .vscode/extensions.json
    │
    ├─► Run migrations
    │   ├─ v1.0 → v2.0 workflow config
    │   ├─ Agent naming hyphen → dot
    │   ├─ Remove /flow:operate
    │   └─ Remove {{INCLUDE:}} directives
    │
    ├─► Cleanup deprecated
    │   ├─ .specify/ directory
    │   ├─ _DEPRECATED_*.md files
    │   └─ Broken directives
    │
    ├─► Validate
    │   ├─ Agent naming correct?
    │   ├─ Workflow config v2.0?
    │   ├─ MCP servers configured?
    │   └─ Skills synced?
    │
    └─► Report
        ├─ Validation results
        ├─ Backup location
        ├─ Git diff summary
        └─ Next steps
```

## Consequences

### Positive

1. **Upgrade Actually Works**: Users get a fully functional flowspec integration post-upgrade
2. **Zero Manual Intervention**: No manual fixes required after running `upgrade-repo`
3. **Version-Aware Migrations**: Smooth upgrade paths between flowspec versions
4. **Validation Safety Net**: Catches issues before they cause user pain
5. **Automatic Cleanup**: Deprecated files removed automatically
6. **Tech-Stack Awareness**: MCP configuration tailored to project's language/framework
7. **Rollback Safety**: Timestamped backups enable easy rollback
8. **Comprehensive Reporting**: Users see exactly what changed and why
9. **Testable**: Each phase can be unit tested independently
10. **Extensible**: New migrations and validations can be added easily

### Negative

1. **Increased Complexity**: Multi-phase orchestration is more complex than simple template copy
2. **Migration Registry Maintenance**: Each breaking change requires a migration definition
3. **Testing Burden**: Need integration tests covering upgrade paths
4. **Performance Impact**: More operations = longer upgrade time
5. **Debugging Difficulty**: More moving parts to debug when issues occur
6. **Backward Compatibility**: Must maintain migrations for older versions
7. **Documentation Debt**: Need to document migration framework for contributors

### Neutral

1. **Code Size**: Upgrade logic grows from ~300 lines to ~1000+ lines
2. **Dependency Count**: May need additional libraries (e.g., semantic versioning)
3. **CLI API**: User-facing command signature remains unchanged

## Alternatives Considered

### Alternative 1: Template-Only Approach (Status Quo)

**Keep the current approach and document manual steps.**

- **Pros:**
  - Minimal code changes
  - Simple implementation
  - Fast execution
- **Cons:**
  - Upgrade remains broken
  - Users must manually fix post-upgrade
  - No version-aware migrations
  - Cannot release flowspec
- **Why rejected:** Does not solve the P0 blocker. Manual steps are error-prone and scale poorly.

### Alternative 2: Destructive Replace Strategy

**Delete all flowspec-managed files and recreate from scratch.**

- **Pros:**
  - Guaranteed consistency
  - Simple logic (no merging)
  - No migration complexity
- **Cons:**
  - Loses user customizations
  - Breaks projects with modified templates
  - No incremental upgrade path
  - Dangerous for production systems
- **Why rejected:** Too aggressive. Users need to preserve customizations.

### Alternative 3: Configuration Management Tool (Ansible/Chef)

**Use a configuration management tool to orchestrate upgrades.**

- **Pros:**
  - Industry-standard tooling
  - Rich ecosystem of modules
  - Idempotent operations
- **Cons:**
  - Additional dependency
  - Learning curve for contributors
  - Overkill for single-tool upgrades
  - Complicates installation
- **Why rejected:** Adds heavyweight dependency for a relatively simple upgrade process.

### Alternative 4: Git-Based Templating (Cookiecutter)

**Use cookiecutter or similar to manage template updates via Git.**

- **Pros:**
  - Standard templating approach
  - Version control for templates
  - Diff-based updates
- **Cons:**
  - Requires Git in project
  - Complex merge conflicts
  - Cannot handle computed artifacts (MCP config)
  - No cleanup or migration logic
- **Why rejected:** Cannot handle the full range of upgrade operations (cleanup, config generation, migrations).

## Implementation Notes

### Phase Ordering

**Critical Dependencies:**

1. **Templates BEFORE Config**: MCP config generation depends on detecting tech stack from templates
2. **Migrations AFTER Templates**: Migrations operate on deployed templates
3. **Cleanup AFTER Migrations**: Some migrations may reference deprecated files
4. **Validation LAST**: Validates the final state after all operations

### Rollback Strategy

**Automatic Rollback Triggers:**
- Post-validation fails with error-level issues
- User aborts mid-upgrade (Ctrl+C)
- Exception during any phase

**Rollback Process:**
```python
def rollback_upgrade(backup_dir: Path, project_path: Path):
    """Rollback upgrade by restoring backup."""
    console.print("[yellow]Rolling back upgrade...[/yellow]")

    # Restore from backup
    for item in backup_dir.iterdir():
        target = project_path / item.name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        shutil.copytree(item, target) if item.is_dir() else shutil.copy2(item, target)

    console.print("[green]Rollback complete[/green]")
```

### Migration Authoring Guide

**Creating a New Migration:**

```python
# 1. Define the migration function
def migrate_feature_x(project_path: Path) -> None:
    """Migrate feature X from old format to new format."""
    # Implementation...

# 2. Define the validation function
def validate_feature_x(project_path: Path) -> bool:
    """Verify feature X migration succeeded."""
    # Validation logic...
    return True

# 3. Register the migration
MigrationRegistry.register(
    version="2.1",
    migration=Migration(
        version="2.1",
        name="migrate_feature_x",
        execute=migrate_feature_x,
        validate=validate_feature_x,
    )
)
```

### Testing Strategy

**Unit Tests:**
- Test each migration function in isolation
- Test artifact synchronizer components
- Test cleanup operations
- Test validators

**Integration Tests:**
- End-to-end upgrade from v1.0 → v2.0
- Upgrade with user customizations
- Upgrade with missing files
- Rollback scenarios

**Smoke Tests:**
- Post-upgrade: VSCode Copilot agents appear
- Post-upgrade: MCP servers start
- Post-upgrade: `flowspec gate` passes

## References

- [ADR-001: VSCode Copilot Agent Naming Convention](./ADR-001-vscode-copilot-agent-naming-convention.md)
- [Fix Flowspec Plan](../../building/fix-flowspec-plan.md) - Root cause analysis
- [Task 579 Epic](../../../backlog/tasks/task-579%20-%20EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md)
- [Flowspec Workflow Config v2.0](../../../flowspec_workflow.yml)
- [Gregor Hohpe - Architecture Patterns](https://architectelevator.com/)

---

*This ADR follows the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).*
