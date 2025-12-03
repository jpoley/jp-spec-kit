#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
# ]
# ///
"""
Specify CLI - Setup tool for Specify projects

Usage:
    uvx specify-cli.py init <project-name>
    uvx specify-cli.py init .
    uvx specify-cli.py init --here

Or install globally:
    uv tool install --from specify-cli.py specify-cli
    specify init <project-name>
    specify init .
    specify init --here
"""

import os
import subprocess
import sys
import zipfile
import tempfile
import shutil
import shlex
from pathlib import Path
from typing import Optional, Tuple

import typer
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar
import ssl
import truststore
import yaml

ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)


def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None."""
    return ((cli_token or os.getenv("GITHUB_JPSPEC") or "").strip()) or None


def _github_headers(cli_token: str | None = None, *, skip_auth: bool = False) -> dict:
    """Return GitHub API headers including optional Authorization, Accept and User-Agent.

    Args:
        cli_token: Optional token to use (falls back to GITHUB_JPSPEC env var)
        skip_auth: If True, never include Authorization header (for public repo fallback)
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "jp-spec-kit/specify-cli",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if not skip_auth:
        token = _github_token(cli_token)
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
    },
    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
    },
    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    },
    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "qwen": {
        "name": "Qwen Code",
        "folder": ".qwen/",
        "install_url": "https://github.com/QwenLM/qwen-code",
        "requires_cli": True,
    },
    "opencode": {
        "name": "opencode",
        "folder": ".opencode/",
        "install_url": "https://opencode.ai",
        "requires_cli": True,
    },
    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    },
    "windsurf": {
        "name": "Windsurf",
        "folder": ".windsurf/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "kilocode": {
        "name": "Kilo Code",
        "folder": ".kilocode/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "auggie": {
        "name": "Auggie CLI",
        "folder": ".augment/",
        "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        "requires_cli": True,
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "folder": ".codebuddy/",
        "install_url": "https://www.codebuddy.ai/cli",
        "requires_cli": True,
    },
    "roo": {
        "name": "Roo Code",
        "folder": ".roo/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "q": {
        "name": "Amazon Q Developer CLI",
        "folder": ".amazonq/",
        "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
        "requires_cli": True,
    },
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

CONSTITUTION_TIER_CHOICES = {
    "light": "Minimal controls for startups/hobby projects",
    "medium": "Standard controls for typical business projects",
    "heavy": "Enterprise controls for regulated environments",
}

# Embedded constitution templates (bundled with package for reliable access)
CONSTITUTION_TEMPLATES = {
    "light": """# [PROJECT_NAME] Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Simplicity First
Keep things simple. Ship fast, iterate quickly. Avoid over-engineering.

### Working Software
Prioritize working software over documentation. Code that runs is better than perfect designs.

### Pragmatic Quality
<!-- SECTION:QUALITY:BEGIN -->
<!-- NEEDS_VALIDATION: Quality standards appropriate for your project -->
- Write tests for critical paths
- Fix bugs before adding features
- Code review when time permits
<!-- SECTION:QUALITY:END -->

## Development Workflow

### Git Practices
<!-- SECTION:GIT:BEGIN -->
<!-- NEEDS_VALIDATION: Git workflow matches team size -->
- Use feature branches for larger changes
- Direct commits to main acceptable for small fixes
- Commit messages should be descriptive
<!-- SECTION:GIT:END -->

### Task Management
<!-- SECTION:TASKS:BEGIN -->
<!-- NEEDS_VALIDATION: Task tracking approach -->
Tasks should have:
- Clear description of what needs to be done
- Basic acceptance criteria when scope is unclear
<!-- SECTION:TASKS:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->

## Governance

This constitution is a living document. Update it as the project evolves.

**Version**: 1.0.0 | **Created**: [DATE]
<!-- NEEDS_VALIDATION: Version and date -->
""",
    "medium": """# [PROJECT_NAME] Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Quality-Driven Development
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Adjust quality principles to team practices -->
Code quality is a shared responsibility. Every team member maintains the codebase.

- **Test Coverage**: Critical paths must have test coverage
- **Code Review**: All changes require at least one reviewer
- **Documentation**: Public APIs and complex logic must be documented
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Continuous Improvement
Regularly evaluate and improve processes. Technical debt should be tracked and addressed.

## Git Commit Requirements

### Branch Strategy
<!-- SECTION:BRANCHING:BEGIN -->
<!-- NEEDS_VALIDATION: Branch strategy matches team workflow -->
- All changes go through feature branches
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Main branch is protected - no direct commits
<!-- SECTION:BRANCHING:END -->

### Pull Request Requirements
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements appropriate for team -->
- Descriptive title following conventional commits
- Link to related issue/task when applicable
- At least one approval required before merge
- CI checks must pass
<!-- SECTION:PR_REQUIREMENTS:END -->

### DCO Sign-Off
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

Use `git commit -s` to automatically add the sign-off.

## Task Management

### Task Quality
<!-- SECTION:TASK_QUALITY:BEGIN -->
<!-- NEEDS_VALIDATION: Task requirements match team workflow -->
Every task MUST have:
- **Clear description** explaining the "why"
- **Acceptance criteria** that are testable and verifiable
- **Labels** for categorization and filtering
<!-- SECTION:TASK_QUALITY:END -->

### Definition of Done
A task is complete when:
1. All acceptance criteria are met
2. Code is reviewed and approved
3. Tests pass
4. Documentation is updated (if applicable)
5. PR is merged

## Testing Standards
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements based on project needs -->
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Minimum coverage target: 70%
<!-- SECTION:TESTING:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security practices appropriate for project -->
- No secrets in code - use environment variables
- Dependencies regularly updated for security patches
- Input validation on all external data
<!-- SECTION:SECURITY:END -->

## Governance

This constitution guides team practices. Changes require team consensus.

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
""",
    "heavy": """# [PROJECT_NAME] Constitution
<!-- TIER: Heavy - Strict controls for enterprise/regulated environments -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles (NON-NEGOTIABLE)

### Production-Grade Quality
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Verify quality standards meet regulatory requirements -->
There is no distinction between "dev code" and "production code". All code is production code.

- **Test-First Development**: TDD is mandatory - write tests, verify they fail, then implement
- **Code Review**: Minimum two reviewers required, including one senior engineer
- **Documentation**: All public APIs, architectural decisions, and complex logic must be documented
- **No Technical Debt**: Address issues immediately; do not defer quality
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Security by Design
Security is not an afterthought. Threat modeling during design phase is mandatory.

### Auditability
All changes must be traceable. Decisions must be documented and justified.

## Git Commit Requirements (NON-NEGOTIABLE)

### No Direct Commits to Main (ABSOLUTE)
**NEVER commit directly to the main branch.** All changes MUST go through a PR.

1. Create a branch for the task
2. Make changes on the branch
3. Create a PR referencing the backlog task
4. PR must pass CI before merge
5. Task marked Done only after PR is merged

**NO EXCEPTIONS.** Not for "urgent" fixes, not for "small" changes, not for any reason.

### Branch Protection
<!-- SECTION:BRANCH_PROTECTION:BEGIN -->
<!-- NEEDS_VALIDATION: Branch protection rules match security requirements -->
- Main branch: Protected, requires 2 approvals
- Release branches: Protected, requires security team approval
- Feature branches: Must be deleted after merge
- Force push: Disabled on protected branches
<!-- SECTION:BRANCH_PROTECTION:END -->

### DCO Sign-Off Required
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

**Always use `git commit -s` to automatically add the sign-off.**

Commits without sign-off will block PRs from being merged.

### Conventional Commits
All commit messages must follow conventional commit format:
```
type(scope): description

[body]

Signed-off-by: Name <email>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

## Pull Request Requirements (NON-NEGOTIABLE)
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements meet compliance needs -->
- Descriptive title following conventional commits
- Link to backlog task (mandatory)
- Security impact assessment for changes touching sensitive areas
- Minimum 2 approvals required
- CI pipeline must pass (tests, lint, security scan)
- No merge until all review comments are resolved
<!-- SECTION:PR_REQUIREMENTS:END -->

## Task Management (NON-NEGOTIABLE)

### Task Quality
Every task created MUST have:
- **At least one acceptance criterion** - Tasks without ACs are incomplete
- **Clear, testable criteria** - Each AC must be outcome-oriented and objectively verifiable
- **Proper description** - Explains the "why" and context
- **Risk assessment** - Security/compliance implications noted

Tasks without acceptance criteria will be rejected or archived.

### PR-Task Synchronization
When creating a PR that completes a backlog task:

1. **Before PR creation**: Mark all completed acceptance criteria
2. **With PR creation**: Update task status and reference the PR
3. **PR-Task coupling**: If the PR fails CI or is rejected, revert task status
4. **Traceability**: Every PR must reference its task; every task must reference its PR

## Testing Standards (NON-NEGOTIABLE)
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements meet regulatory standards -->
- **Unit Tests**: Mandatory for all business logic (minimum 80% coverage)
- **Integration Tests**: Mandatory for all API endpoints and service boundaries
- **E2E Tests**: Mandatory for all critical user journeys
- **Security Tests**: SAST, DAST, and dependency scanning on every PR
- **Performance Tests**: Load testing for user-facing endpoints
- **Contract Tests**: Required for all inter-service communication
<!-- SECTION:TESTING:END -->

## Security Requirements (NON-NEGOTIABLE)
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security controls meet compliance requirements -->
### Secrets Management
- No secrets in code, configs, or environment files checked into git
- Use approved secrets management solution
- Rotate secrets according to policy

### Access Control
- Principle of least privilege
- All access logged and auditable
- Regular access reviews (quarterly minimum)

### Vulnerability Management
- Dependencies scanned on every build
- Critical vulnerabilities: Fix within 24 hours
- High vulnerabilities: Fix within 7 days
- Security patches applied within SLA

### Data Protection
- PII/sensitive data encrypted at rest and in transit
- Data classification enforced
- Retention policies applied
<!-- SECTION:SECURITY:END -->

## Compliance
<!-- SECTION:COMPLIANCE:BEGIN -->
<!-- NEEDS_VALIDATION: Compliance frameworks applicable to project -->
This project must comply with:
- [COMPLIANCE_FRAMEWORKS]

### Audit Requirements
- All changes logged with user, timestamp, and justification
- Audit logs retained for [RETENTION_PERIOD]
- Regular compliance audits scheduled
<!-- SECTION:COMPLIANCE:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Approved Technologies
All technology choices must be from the approved list or require architecture review.

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]

### CI/CD Pipeline
<!-- NEEDS_VALIDATION: CI/CD configuration matches security requirements -->
[CI_CD_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Parallel Task Execution

### Git Worktree Requirements
When executing tasks in parallel, git worktrees MUST be used:

1. **Worktree name must match branch name**
2. **One branch per worktree**
3. **Clean isolation** - no cross-contamination between parallel work
4. **Worktree cleanup** - remove when work is complete

## Change Management
<!-- SECTION:CHANGE_MANAGEMENT:BEGIN -->
<!-- NEEDS_VALIDATION: Change management process meets requirements -->
### Standard Changes
- Pre-approved, low-risk changes
- Follow standard PR process

### Normal Changes
- Require change request documentation
- Impact assessment required
- Rollback plan documented

### Emergency Changes
- Require incident ticket reference
- Post-implementation review mandatory
- Retrospective within 48 hours
<!-- SECTION:CHANGE_MANAGEMENT:END -->

## Incident Response
<!-- SECTION:INCIDENT_RESPONSE:BEGIN -->
<!-- NEEDS_VALIDATION: Incident response meets regulatory requirements -->
- All security incidents reported within [REPORTING_WINDOW]
- Incident severity classification enforced
- Post-incident reviews mandatory
- Lessons learned documented and shared
<!-- SECTION:INCIDENT_RESPONSE:END -->

## Governance

### Constitution Authority
This constitution supersedes all other practices. Violations are escalated.

### Amendments
Changes to this constitution require:
1. Written proposal with justification
2. Impact assessment
3. Security/compliance review
4. Approval from [APPROVAL_AUTHORITY]
5. Migration plan for existing work

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version, dates, and approval authority -->
""",
}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

BANNER = """
███████╗██████╗ ███████╗ ██████╗██╗███████╗██╗   ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║██╔════╝╚██╗ ██╔╝
███████╗██████╔╝█████╗  ██║     ██║█████╗   ╚████╔╝ 
╚════██║██╔═══╝ ██╔══╝  ██║     ██║██╔══╝    ╚██╔╝  
███████║██║     ███████╗╚██████╗██║██║        ██║   
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝╚═╝        ╚═╝   
"""

# Version - keep in sync with pyproject.toml
__version__ = "0.0.213"

TAGLINE = (
    f"(jp extension v{__version__}) GitHub Spec Kit - Spec-Driven Development Toolkit"
)

# Repository configuration for two-stage download
BASE_REPO_OWNER = "github"
BASE_REPO_NAME = "spec-kit"
BASE_REPO_DEFAULT_VERSION = "latest"  # or specific version like "0.0.20"

EXTENSION_REPO_OWNER = "jpoley"
EXTENSION_REPO_NAME = "jp-spec-kit"
EXTENSION_REPO_DEFAULT_VERSION = "latest"

# Marker file that identifies the jp-spec-kit source repository
# When present, specify init/upgrade will skip to avoid clobbering source files
SOURCE_REPO_MARKER = ".jp-spec-kit-source"

# Path to compatibility matrix YAML
COMPATIBILITY_MATRIX_PATH = (
    Path(__file__).parent.parent.parent / ".spec-kit-compatibility.yml"
)


def load_compatibility_matrix() -> dict:
    """Load and parse the compatibility matrix YAML file.

    Returns:
        Parsed YAML as a dict, or empty dict if file not found/invalid
    """
    try:
        if COMPATIBILITY_MATRIX_PATH.exists():
            with open(COMPATIBILITY_MATRIX_PATH, "r") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def get_backlog_validated_version() -> Optional[str]:
    """Get the recommended backlog-md version from compatibility matrix.

    Returns:
        Recommended version string (e.g., "1.21.0") or None if not found
    """
    matrix = load_compatibility_matrix()
    backlog_config = matrix.get("backlog-md", {})
    compat = backlog_config.get("compatible_with", {})
    return compat.get("recommended")


def check_backlog_installed_version() -> Optional[str]:
    """Check the currently installed backlog-md version.

    Returns:
        Version string (e.g., "1.21.0") or None if not installed
    """
    try:
        result = subprocess.run(
            ["backlog", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            # backlog --version outputs just the version number, e.g. "1.21.0"
            output = result.stdout.strip()
            # Validate it looks like a version (digits and dots)
            if output and all(c.isdigit() or c == "." for c in output):
                return output
    except FileNotFoundError:
        pass
    return None


def detect_package_manager() -> Optional[str]:
    """Detect available Node.js package manager, preferring pnpm.

    Returns:
        "pnpm" if available, "npm" if available, None if neither found
    """
    if shutil.which("pnpm"):
        return "pnpm"
    if shutil.which("npm"):
        return "npm"
    return None


def compare_semver(version1: str, version2: str) -> int:
    """Simple semantic version comparison.

    Args:
        version1: First version (e.g., "1.21.0")
        version2: Second version (e.g., "1.20.0")

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """

    def parse_version(v: str) -> Tuple[int, int, int]:
        """Parse version string into tuple of ints."""
        parts = v.lstrip("v").split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)

    v1 = parse_version(version1)
    v2 = parse_version(version2)

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """

    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {
            "pending": 0,
            "running": 1,
            "done": 2,
            "error": 3,
            "skipped": 4,
        }
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append(
                {"key": key, "label": label, "status": "pending", "detail": ""}
            )
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append(
            {"key": key, "label": key, "status": status, "detail": detail}
        )
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = (
                        f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                    )
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree


def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return "up"
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return "down"

    if key == readchar.key.ENTER:
        return "enter"

    if key == readchar.key.ESC:
        return "escape"

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key


def select_with_arrows(
    options: dict, prompt_text: str = "Select an option", default_key: str = None
) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.

    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with

    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row(
            "", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]"
        )

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(
            create_selection_panel(),
            console=console,
            transient=True,
            auto_refresh=False,
        ) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == "enter":
                        selected_key = option_keys[selected_index]
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key


def parse_agent_list(agent_str: str) -> list[str]:
    """
    Parse comma-separated agent list into individual agent names.

    Args:
        agent_str: Comma-separated string of agent names (e.g., "claude,copilot,cursor-agent")

    Returns:
        List of agent names with whitespace stripped and duplicates removed

    Examples:
        >>> parse_agent_list("claude,copilot")
        ['claude', 'copilot']
        >>> parse_agent_list("claude, copilot, cursor-agent")
        ['claude', 'copilot', 'cursor-agent']
        >>> parse_agent_list("claude")
        ['claude']
        >>> parse_agent_list("claude,copilot,claude")
        ['claude', 'copilot']
    """
    if not agent_str or not agent_str.strip():
        return []

    # Split by comma and strip whitespace from each agent name
    agents = [agent.strip() for agent in agent_str.split(",")]

    # Filter out empty strings and deduplicate while preserving order
    seen = set()
    result = []
    for agent in agents:
        if agent and agent not in seen:
            seen.add(agent)
            result.append(agent)
    return result


def select_multiple_with_checkboxes(
    options: dict,
    prompt_text: str = "Select options (space to toggle, enter to confirm)",
    default_keys: list[str] = None,
) -> list[str]:
    """
    Interactive multi-selection using checkboxes with Rich Live display.

    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_keys: List of default option keys to start with (pre-selected)

    Returns:
        List of selected option keys

    Examples:
        >>> options = {"claude": "Claude Code", "copilot": "GitHub Copilot"}
        >>> selected = select_multiple_with_checkboxes(options, "Choose AI assistants:")
        >>> # Returns list like ['claude', 'copilot'] based on user selection
    """
    option_keys = list(options.keys())
    selected_index = 0

    # Track which options are checked (selected)
    checked_keys = set(default_keys) if default_keys else set()

    # Validate default keys
    if default_keys:
        for key in default_keys:
            if key not in option_keys:
                console.print(
                    f"[yellow]Warning: Default key '{key}' not in options[/yellow]"
                )

    selected_keys = None

    def create_selection_panel():
        """Create the selection panel with checkboxes."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)  # Arrow/pointer
        table.add_column(style="white", justify="left", width=5)  # Checkbox
        table.add_column(style="white", justify="left")  # Option text

        for i, key in enumerate(option_keys):
            pointer = "▶" if i == selected_index else " "
            checkbox = "[✓]" if key in checked_keys else "[ ]"

            if i == selected_index:
                # Highlight current row
                table.add_row(
                    pointer,
                    f"[cyan]{checkbox}[/cyan]",
                    f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]",
                )
            else:
                table.add_row(
                    pointer, checkbox, f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]"
                )

        table.add_row("", "", "")
        table.add_row(
            "",
            "",
            "[dim]↑/↓: navigate | Space: toggle | Enter: confirm | Esc: cancel[/dim]",
        )

        # Show selection count
        count_text = f"[dim]Selected: {len(checked_keys)} items[/dim]"
        table.add_row("", "", count_text)

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_keys, selected_index, checked_keys
        with Live(
            create_selection_panel(),
            console=console,
            transient=True,
            auto_refresh=False,
        ) as live:
            while True:
                try:
                    key = get_key()
                    if key == "up":
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == "down":
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == " ":  # Space to toggle checkbox
                        current_key = option_keys[selected_index]
                        if current_key in checked_keys:
                            checked_keys.remove(current_key)
                        else:
                            checked_keys.add(current_key)
                    elif key == "enter":
                        selected_keys = list(checked_keys)
                        break
                    elif key == "escape":
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_keys is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_keys


console = Console()


class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


# Workflow transitions with their default validation modes
# Each transition can have a different validation mode
WORKFLOW_TRANSITIONS = [
    {"name": "assess", "from": "To Do", "to": "Assessed", "default": "NONE"},
    {"name": "research", "from": "Assessed", "to": "Researched", "default": "NONE"},
    {"name": "specify", "from": "Researched", "to": "Specified", "default": "NONE"},
    {"name": "plan", "from": "Specified", "to": "Planned", "default": "NONE"},
    {"name": "implement", "from": "Planned", "to": "Implemented", "default": "NONE"},
    {"name": "validate", "from": "Implemented", "to": "Validated", "default": "NONE"},
    {"name": "operate", "from": "Validated", "to": "Operated", "default": "NONE"},
]


def generate_jpspec_workflow_yml(
    project_path: Path,
    transition_modes: dict[str, str] | None = None,
) -> None:
    """Generate jpspec_workflow.yml with per-transition validation modes.

    Args:
        project_path: Path to the project directory.
        transition_modes: Dict mapping transition name to validation mode.
                         If None, uses defaults (all NONE).
    """
    if transition_modes is None:
        transition_modes = {}

    # Map CLI mode values to YAML format
    def format_mode(mode: str) -> str:
        mode = mode.lower()
        if mode == "none":
            return "NONE"
        elif mode == "keyword":
            return 'KEYWORD["APPROVED"]'
        elif mode == "pull-request" or mode == "pull_request":
            return "PULL_REQUEST"
        elif mode.startswith("keyword["):
            # Already in KEYWORD["..."] format
            return mode.upper()
        return "NONE"

    # Build YAML content
    lines = [
        "# JPSpec Workflow Configuration",
        "# Generated by: specify init",
        "#",
        "# Validation modes:",
        "#   NONE - No gate, immediate pass-through",
        '#   KEYWORD["<string>"] - Require user to type exact keyword',
        "#   PULL_REQUEST - Require PR to be merged",
        "",
        'version: "1.0"',
        "",
        "transitions:",
    ]

    for t in WORKFLOW_TRANSITIONS:
        name = t["name"]
        mode = transition_modes.get(name, t["default"])
        formatted_mode = format_mode(mode)

        lines.append(f"  - name: {name}")
        lines.append(f'    from: "{t["from"]}"')
        lines.append(f'    to: "{t["to"]}"')
        lines.append(f"    validation: {formatted_mode}")
        lines.append("")

    # Write the file
    workflow_file = project_path / "jpspec_workflow.yml"
    workflow_file.write_text("\n".join(lines), encoding="utf-8")


def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split("\n")
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if (
        ctx.invoked_subcommand is None
        and "--help" not in sys.argv
        and "-h" not in sys.argv
    ):
        show_banner()
        console.print(
            Align.center("[dim]Run 'specify --help' for usage information[/dim]")
        )
        console.print()


def run_command(
    cmd: list[str],
    check_return: bool = True,
    capture: bool = False,
    shell: bool = False,
) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(
                cmd, check=check_return, capture_output=True, text=True, shell=shell
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, "stderr") and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None


def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.

    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results

    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI after `claude migrate-installer`
    # See: https://github.com/github/spec-kit/issues/123
    # The migrate-installer command REMOVES the original executable from PATH
    # and creates an alias at ~/.claude/local/claude instead
    # This path should be prioritized over other claude executables in PATH
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True

    found = shutil.which(tool) is not None

    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")

    return found


def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()

    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def init_git_repo(
    project_path: Path, quiet: bool = False
) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.

    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]Initializing git repository...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from Specify template"],
            check=True,
            capture_output=True,
            text=True,
        )
        if not quiet:
            console.print("[green]✓[/green] Git repository initialized")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"

        if not quiet:
            console.print(f"[red]Error initializing git repository:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)


def download_template_from_github(
    ai_assistant: str,
    download_dir: Path,
    *,
    script_type: str = "sh",
    verbose: bool = True,
    show_progress: bool = True,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    repo_owner: str = None,
    repo_name: str = None,
    version: str = None,
) -> Tuple[Path, dict]:
    # Use provided repo or default to base spec-kit
    if repo_owner is None:
        repo_owner = BASE_REPO_OWNER
    if repo_name is None:
        repo_name = BASE_REPO_NAME
    if version is None:
        version = BASE_REPO_DEFAULT_VERSION

    if client is None:
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print(
            f"[cyan]Fetching release information from {repo_owner}/{repo_name}...[/cyan]"
        )

    # Resolve effective token once so env-based tokens are honored consistently (including fallbacks)
    effective_token = _github_token(github_token)

    def _req(url: str, retry_without_auth: bool = True) -> httpx.Response:
        """Make GitHub API request with automatic fallback for invalid tokens.

        For public repositories, if we get a 401 with authentication, retry without auth.
        This handles cases where an invalid/expired token is present.

        Args:
            url: The GitHub API URL to request.
            retry_without_auth: If True (default), retry without auth on 401 errors when a token was provided. Useful for public repos with invalid/expired tokens.

        Returns:
            The HTTP response from the GitHub API.
        """
        response = client.get(
            url,
            timeout=30,
            follow_redirects=True,
            headers=_github_headers(effective_token),
        )

        # If we got 401 with a token, the token might be invalid/expired
        # For public repos, retry without authentication
        if response.status_code == 401 and effective_token and retry_without_auth:
            if debug:
                console.print(
                    "[yellow]Got 401 with token - retrying without authentication for public repo[/yellow]"
                )
            response = client.get(
                url,
                timeout=30,
                follow_redirects=True,
                headers=_github_headers(
                    skip_auth=True
                ),  # Explicitly skip auth for retry
            )

        return response

    def _pick_latest(releases: list[dict]) -> Optional[dict]:
        filtered = [
            r for r in releases if not r.get("draft") and not r.get("prerelease")
        ]
        return filtered[0] if filtered else (releases[0] if releases else None)

    try:
        release_data = None
        last_status_code = None
        if version == "latest" or version is None:
            r = _req(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
            )
            last_status_code = r.status_code
            if r.status_code == 200:
                release_data = r.json()
            else:
                r2 = _req(
                    f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?per_page=20"
                )
                last_status_code = r2.status_code
                if r2.status_code == 200:
                    release_data = _pick_latest(r2.json())
        else:
            r = _req(
                f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{version}"
            )
            last_status_code = r.status_code
            if r.status_code == 200:
                release_data = r.json()
            else:
                alt = version[1:] if version.startswith("v") else f"v{version}"
                r2 = _req(
                    f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{alt}"
                )
                last_status_code = r2.status_code
                if r2.status_code == 200:
                    release_data = r2.json()
                else:
                    r3 = _req(
                        f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?per_page=50"
                    )
                    last_status_code = r3.status_code
                    if r3.status_code == 200:
                        for rel in r3.json():
                            tag = rel.get("tag_name", "")
                            if tag in {version, alt}:
                                release_data = rel
                                break

        if not release_data:
            error_msg = (
                f"Could not resolve release for {repo_owner}/{repo_name} (version='{version}')\n"
                f"Last HTTP status: {last_status_code}\n"
                f"Tried: /releases/latest, /releases/tags/<tag> with v/no-v, and /releases list"
            )
            # Add authentication hints for common error codes
            if last_status_code in (401, 403):
                if effective_token:
                    error_msg += (
                        "\n\n[yellow]Authentication Error:[/yellow]\n"
                        "The provided GitHub token appears to be invalid or expired.\n"
                        "The request was automatically retried without authentication, but still failed.\n\n"
                        "This could mean:\n"
                        "  1. The repository is private and requires a valid token\n"
                        "  2. The token has expired or been revoked\n"
                        "  3. The token lacks required permissions\n\n"
                        "To fix this:\n"
                        "  1. Check your token is still valid at https://github.com/settings/tokens\n"
                        "  2. Ensure it has 'repo' or 'public_repo' scope\n"
                        "  3. Remove invalid tokens from GITHUB_JPSPEC environment variable\n"
                        f"  4. If {repo_owner}/{repo_name} is private, generate a new token"
                    )
                else:
                    error_msg += (
                        "\n\n[yellow]Authentication Error:[/yellow]\n"
                        "This may be due to insufficient permissions or missing authentication.\n"
                        "Try providing a GitHub token with the following options:\n"
                        "  1. Use --github-token <token> flag\n"
                        "  2. Set GITHUB_JPSPEC environment variable\n"
                        f"  3. Ensure your token has 'repo' or 'public_repo' scope for {repo_owner}/{repo_name}"
                    )
            elif last_status_code == 404:
                if not effective_token:
                    error_msg += (
                        "\n\n[yellow]Not Found (404):[/yellow]\n"
                        "This repository or its releases may be private, or the release may not exist.\n"
                        "If this is a private repository, provide authentication:\n"
                        "  1. Use --github-token <token> flag\n"
                        "  2. Set GITHUB_JPSPEC environment variable"
                    )
                else:
                    error_msg += (
                        "\n\n[yellow]Not Found (404):[/yellow]\n"
                        "The release was not found. This could mean:\n"
                        "  1. No releases exist for this repository\n"
                        "  2. The specified version does not exist\n"
                        "  3. Your token lacks permissions to access the releases"
                    )
            raise RuntimeError(error_msg)
    except Exception as e:
        msg = str(e)
        if debug:
            try:
                meta = _req(f"https://api.github.com/repos/{repo_owner}/{repo_name}")
                msg += f"\nRepo visibility: {meta.json().get('visibility', '?')} (HTTP {meta.status_code})"
            except Exception:
                pass
        console.print("[red]Error fetching release information[/red]")
        console.print(Panel(msg, title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset
        for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(
            f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])"
        )
        asset_names = [a.get("name", "?") for a in assets]
        console.print(
            Panel(
                "\n".join(asset_names) or "(no assets)",
                title="Available Assets",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    api_asset_url = asset.get("url")
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print("[cyan]Downloading template...[/cyan]")

    try:
        # Prefer API asset URL when a token is available (works for private and public assets)
        response = None
        if effective_token and api_asset_url:
            api_headers = _github_headers(effective_token).copy()
            api_headers["Accept"] = "application/octet-stream"
            response = client.get(
                api_asset_url,
                timeout=60,
                follow_redirects=True,
                headers=api_headers,
            )
            # If API route fails (e.g., insufficient scope), fall back to browser URL
            if response.status_code != 200:
                response = client.get(
                    download_url,
                    timeout=60,
                    follow_redirects=True,
                    headers=_github_headers(effective_token),
                )
        else:
            # No token: try browser URL (public-only)
            response = client.get(
                download_url,
                timeout=60,
                follow_redirects=True,
                headers=_github_headers(effective_token),
            )
        if response.status_code != 200:
            body_sample = (getattr(response, "text", "") or "")[:400]
            hint = ""
            if response.status_code == 401:
                hint = (
                    "\n\n[yellow]Authentication Required (401):[/yellow]\n"
                    "Your GitHub token is invalid or has expired.\n"
                    "Please provide a valid token:\n"
                    "  1. Use --github-token <token> flag\n"
                    "  2. Set GITHUB_JPSPEC environment variable\n"
                    "  3. Ensure the token has not expired"
                )
            elif response.status_code == 403:
                hint = (
                    "\n\n[yellow]Access Forbidden (403):[/yellow]\n"
                    "Your token lacks the required permissions to download this asset.\n"
                    "Ensure your GitHub token has:\n"
                    "  1. 'repo' scope for private repositories\n"
                    "  2. 'public_repo' scope for public repositories\n"
                    f"  3. Access to {repo_owner}/{repo_name}"
                )
            elif response.status_code == 404:
                if not effective_token:
                    hint = (
                        "\n\n[yellow]Asset Not Found (404):[/yellow]\n"
                        "This repository or its release assets may be private.\n"
                        "Provide authentication to access private assets:\n"
                        "  1. Use --github-token <token> flag\n"
                        "  2. Set GITHUB_JPSPEC environment variable"
                    )
                else:
                    hint = (
                        "\n\n[yellow]Asset Not Found (404):[/yellow]\n"
                        "The release asset could not be found. This could mean:\n"
                        "  1. The asset has been deleted\n"
                        "  2. Your token lacks access to this repository\n"
                        "  3. The release does not contain the expected asset"
                    )
            raise RuntimeError(
                f"Download failed with HTTP {response.status_code}\n"
                f"Headers: {response.headers}\n"
                f"Body (truncated): {body_sample}{hint}"
            )
        with open(zip_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        console.print("[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)
    if verbose:
        console.print(f"Downloaded: {filename}")
    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url,
    }
    return zip_path, metadata


def download_and_extract_two_stage(
    project_path: Path,
    ai_assistants: str | list[str],
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    base_version: str = None,
    extension_version: str = None,
) -> Path:
    """Two-stage download: base spec-kit + jp-spec-kit extension overlay.

    Supports single or multiple AI assistants. When multiple assistants are specified,
    their respective agent directories are all extracted to the project.

    Returns project_path. Uses tracker if provided.
    """
    # Normalize to list for consistent handling
    if isinstance(ai_assistants, str):
        ai_assistants = [ai_assistants]

    # Validate that at least one AI assistant is specified
    if not ai_assistants:
        raise ValueError("At least one AI assistant must be specified")

    current_dir = Path.cwd()
    base_zip = None
    ext_zip = None

    # Use first agent for template download (templates contain all agent directories)
    primary_agent = ai_assistants[0]

    # Stage 1: Download base spec-kit
    if tracker:
        tracker.start(
            "fetch-base", f"downloading from {BASE_REPO_OWNER}/{BASE_REPO_NAME}"
        )

    try:
        base_zip, base_meta = download_template_from_github(
            primary_agent,  # Use primary agent for download
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token,
            repo_owner=BASE_REPO_OWNER,
            repo_name=BASE_REPO_NAME,
            version=base_version or BASE_REPO_DEFAULT_VERSION,
        )
        if tracker:
            tracker.complete(
                "fetch-base",
                f"base {base_meta['release']} ({base_meta['size']:,} bytes)",
            )
    except Exception as e:
        if tracker:
            tracker.error("fetch-base", str(e))
        # download_template_from_github already cleans up its zip on error
        raise

    # Stage 2: Download jp-spec-kit extension
    if tracker:
        tracker.start(
            "fetch-extension",
            f"downloading from {EXTENSION_REPO_OWNER}/{EXTENSION_REPO_NAME}",
        )

    try:
        ext_zip, ext_meta = download_template_from_github(
            primary_agent,  # Use primary agent for download
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token,
            repo_owner=EXTENSION_REPO_OWNER,
            repo_name=EXTENSION_REPO_NAME,
            version=extension_version or EXTENSION_REPO_DEFAULT_VERSION,
        )
        if tracker:
            tracker.complete(
                "fetch-extension",
                f"extension {ext_meta['release']} ({ext_meta['size']:,} bytes)",
            )
    except Exception as e:
        if tracker:
            tracker.error("fetch-extension", str(e))
        # download_template_from_github already cleans up its zip on error
        # But we need to clean up the base_zip since we won't reach extraction
        if base_zip and base_zip.exists():
            base_zip.unlink()
        raise

    # Extract base first
    if tracker:
        tracker.start("extract-base")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(base_zip, "r") as zip_ref:
            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_path)
            else:
                zip_ref.extractall(project_path)
                extracted_items = list(project_path.iterdir())
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"
                    shutil.move(str(nested_dir), str(temp_move_dir))
                    project_path.rmdir()
                    shutil.move(str(temp_move_dir), str(project_path))

        if tracker:
            tracker.complete("extract-base", "base templates extracted")
    except Exception as e:
        if tracker:
            tracker.error("extract-base", str(e))
        # Clean up extension zip on base extraction failure (base_zip cleaned in finally)
        if ext_zip and ext_zip.exists():
            ext_zip.unlink()
        raise
    finally:
        # Always clean up base zip after extraction attempt
        if base_zip and base_zip.exists():
            base_zip.unlink()

    # Extract extension (overlay on top of base)
    if tracker:
        tracker.start("extract-extension")

    try:
        with zipfile.ZipFile(ext_zip, "r") as zip_ref:
            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            # Recursively merge directories (extension overrides base)
                            if dest_path.exists():
                                for sub_item in item.rglob("*"):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True
                                        )
                                        shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path, dirs_exist_ok=True)
                        else:
                            # File overwrites (extension wins)
                            shutil.copy2(item, dest_path)
            else:
                # Extract to temp, then merge
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                # Merge directory contents
                                for sub_item in item.rglob("*"):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True
                                        )
                                        shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_path)

        if tracker:
            tracker.complete("extract-extension", "extension overlay applied")
            tracker.add("merge", "Merge templates (extension overrides base)")
            tracker.complete("merge", "precedence rules applied")
    except Exception as e:
        if tracker:
            tracker.error("extract-extension", str(e))
        # ext_zip cleanup happens in finally block
        raise
    finally:
        # Always clean up extension zip after extraction attempt
        if ext_zip and ext_zip.exists():
            ext_zip.unlink()

    return project_path


def download_and_extract_template(
    project_path: Path,
    ai_assistants: str | list[str],
    script_type: str,
    is_current_dir: bool = False,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    client: httpx.Client = None,
    debug: bool = False,
    github_token: str = None,
    repo_owner: str = None,
    repo_name: str = None,
    version: str = None,
) -> Path:
    """Download the latest release and extract it to create a new project.

    Supports single or multiple AI assistants. When multiple assistants are specified,
    their respective agent directories are all extracted to the project.

    Returns project_path. Uses tracker if provided (with keys: fetch, download, extract, cleanup)
    """
    # Normalize to list for consistent handling
    if isinstance(ai_assistants, str):
        ai_assistants = [ai_assistants]

    # Validate that at least one AI assistant is specified
    if not ai_assistants:
        raise ValueError("At least one AI assistant must be specified")

    # Use first agent for template download (templates contain all agent directories)
    primary_agent = ai_assistants[0]
    current_dir = Path.cwd()

    if tracker:
        tracker.start("fetch", "contacting GitHub API")
    try:
        zip_path, meta = download_template_from_github(
            primary_agent,  # Use primary agent for download
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            version=version,
        )
        if tracker:
            tracker.complete(
                "fetch", f"release {meta['release']} ({meta['size']:,} bytes)"
            )
            tracker.add("download", "Download template")
            tracker.complete("download", meta["filename"])
    except Exception as e:
        if tracker:
            tracker.error("fetch", str(e))
        else:
            if verbose:
                console.print(f"[red]Error downloading template:[/red] {e}")
        raise

    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete(
                            "extracted-summary", f"temp {len(extracted_items)} items"
                        )
                    elif verbose:
                        console.print(
                            f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]"
                        )

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(
                                "[cyan]Found nested directory structure[/cyan]"
                            )

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(
                                        f"[yellow]Merging directory:[/yellow] {item.name}"
                                    )
                                for sub_item in item.rglob("*"):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True
                                        )
                                        shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(
                                    f"[yellow]Overwriting file:[/yellow] {item.name}"
                                )
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(
                            "[cyan]Template files merged into current directory[/cyan]"
                        )
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete(
                        "extracted-summary", f"{len(extracted_items)} top-level items"
                    )
                elif verbose:
                    console.print(
                        f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]"
                    )
                    for item in extracted_items:
                        console.print(
                            f"  - {item.name} ({'dir' if item.is_dir() else 'file'})"
                        )

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(
                            "[cyan]Flattened nested directory structure[/cyan]"
                        )

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(
                        Panel(str(e), title="Extraction Error", border_style="red")
                    )

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def ensure_executable_scripts(
    project_path: Path, tracker: StepTracker | None = None
) -> None:
    """Ensure POSIX .sh scripts under .specify/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".specify" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat()
            mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400:
                new_mode |= 0o100
            if mode & 0o040:
                new_mode |= 0o010
            if mode & 0o004:
                new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (
            f", {len(failures)} failed" if failures else ""
        )
        tracker.add("chmod", "Set script permissions recursively")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(
                f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]"
            )
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")


@app.command()
def init(
    project_name: str = typer.Argument(
        None,
        help="Name for your new project directory (optional if using --here, or use '.' for current directory)",
    ),
    ai_assistant: str = typer.Option(
        None,
        "--ai",
        help="AI assistant(s) to use (comma-separated for multiple): claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, roo, or q. Example: --ai claude,copilot",
    ),
    script_type: str = typer.Option(
        None, "--script", help="Script type to use: sh or ps"
    ),
    ignore_agent_tools: bool = typer.Option(
        False,
        "--ignore-agent-tools",
        help="Skip checks for AI agent tools like Claude Code",
    ),
    no_git: bool = typer.Option(
        False, "--no-git", help="Skip git repository initialization"
    ),
    here: bool = typer.Option(
        False,
        "--here",
        help="Initialize project in the current directory instead of creating a new one",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force merge/overwrite when using --here (skip confirmation)",
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show verbose diagnostic output for network and extraction failures",
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GITHUB_JPSPEC environment variable)",
    ),
    base_version: str = typer.Option(
        None,
        "--base-version",
        help="Specific version of base spec-kit to use (default: latest)",
    ),
    extension_version: str = typer.Option(
        None,
        "--extension-version",
        help="Specific version of jp-spec-kit extension to use (default: latest)",
    ),
    layered: bool = typer.Option(
        True,
        "--layered/--no-layered",
        help="Use two-stage layered download (base + extension). Default: True",
    ),
    backlog_version: str = typer.Option(
        None,
        "--backlog-version",
        help="Specific version of backlog-md to install (default: recommended from compatibility matrix)",
    ),
    # Per-transition validation mode flags
    validation_assess: str = typer.Option(
        "none",
        "--validation-assess",
        help="Validation mode for assess transition: none, keyword, or pull-request",
    ),
    validation_research: str = typer.Option(
        "none",
        "--validation-research",
        help="Validation mode for research transition: none, keyword, or pull-request",
    ),
    validation_specify: str = typer.Option(
        "none",
        "--validation-specify",
        help="Validation mode for specify transition: none, keyword, or pull-request",
    ),
    validation_plan: str = typer.Option(
        "none",
        "--validation-plan",
        help="Validation mode for plan transition: none, keyword, or pull-request",
    ),
    validation_implement: str = typer.Option(
        "none",
        "--validation-implement",
        help="Validation mode for implement transition: none, keyword, or pull-request",
    ),
    validation_validate: str = typer.Option(
        "none",
        "--validation-validate",
        help="Validation mode for validate transition: none, keyword, or pull-request",
    ),
    validation_operate: str = typer.Option(
        "none",
        "--validation-operate",
        help="Validation mode for operate transition: none, keyword, or pull-request",
    ),
    no_validation_prompts: bool = typer.Option(
        False,
        "--no-validation-prompts",
        help="Skip validation prompts and use NONE for all transitions",
    ),
    light: bool = typer.Option(
        False,
        "--light",
        help="Use spec-light mode for medium-complexity features (~60% faster workflow)",
    ),
    constitution: str = typer.Option(
        None,
        "--constitution",
        help="Constitution tier: light (startup), medium (business), heavy (enterprise). Omit to be prompted.",
    ),
):
    """
    Initialize a new Specify project from the latest template.

    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Download the appropriate template from GitHub (two-stage: base + extension)
    4. Extract and merge templates to a new project directory or current directory
    5. Initialize a fresh git repository (if not --no-git and no existing repo)
    6. Optionally set up AI assistant commands

    Examples:
        specify init my-project
        specify init my-project --ai claude
        specify init my-project --ai claude,copilot  # Multiple agents
        specify init my-project --ai copilot --no-git
        specify init --ignore-agent-tools my-project
        specify init . --ai claude         # Initialize in current directory
        specify init . --ai claude,cursor-agent,copilot  # Multiple agents in current dir
        specify init .                     # Initialize in current directory (interactive AI selection)
        specify init --here --ai claude    # Alternative syntax for current directory
        specify init --here --ai codex
        specify init --here --ai codebuddy,claude
        specify init --here
        specify init --here --force  # Skip confirmation when current directory not empty
        specify init my-project --constitution medium  # Specific constitution tier
        specify init my-project --ai claude --constitution light  # Startup tier
        specify init my-project --ai claude --constitution heavy  # Enterprise tier
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print(
            "[red]Error:[/red] Cannot specify both project name and --here flag"
        )
        raise typer.Exit(1)

    if not here and not project_name:
        console.print(
            "[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag"
        )
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        # Check for source repository marker FIRST, before any other prompts
        marker_path = project_path / SOURCE_REPO_MARKER
        if marker_path.exists():
            error_panel = Panel(
                f"[yellow]This directory contains '{SOURCE_REPO_MARKER}'[/yellow]\n\n"
                "This indicates it is the jp-spec-kit source repository.\n"
                "Running 'specify init' here would overwrite source files.\n\n"
                "[cyan]If you want to use jp-spec-kit commands in this repo:[/cyan]\n"
                "  Run 'specify dev-setup' to set up for development.\n\n"
                "[cyan]If you want to test 'specify init' on a new project:[/cyan]\n"
                "  Create a new directory and run 'specify init' there instead.",
                title="[yellow]Source Repository Detected[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(
                f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)"
            )
            console.print(
                "[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]"
            )
            if force:
                console.print(
                    "[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]"
                )
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print(
                "[yellow]Git not found - will skip repository initialization[/yellow]"
            )

    # Parse and validate AI assistant selection(s)
    selected_agents = []
    if ai_assistant:
        # Parse comma-separated list
        selected_agents = parse_agent_list(ai_assistant)

        # Ensure at least one agent was provided
        if not selected_agents:
            console.print(
                "[red]Error:[/red] No AI assistants specified. Please provide at least one."
            )
            console.print(
                f"[cyan]Valid options:[/cyan] {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)

        # Validate all agents
        invalid_agents = [
            agent for agent in selected_agents if agent not in AGENT_CONFIG
        ]
        if invalid_agents:
            console.print(
                f"[red]Error:[/red] Invalid AI assistant(s): {', '.join(invalid_agents)}"
            )
            console.print(
                f"[cyan]Valid options:[/cyan] {', '.join(AGENT_CONFIG.keys())}"
            )
            raise typer.Exit(1)
    else:
        # Interactive selection: use multi-select UI
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        console.print(
            "[cyan]Tip:[/cyan] You can select multiple AI assistants (use Space to toggle, Enter to confirm)"
        )
        console.print()
        selected_agents = select_multiple_with_checkboxes(
            ai_choices,
            "Choose your AI assistant(s):",
            default_keys=["copilot"],  # Default to copilot pre-selected
        )

        # Ensure at least one agent is selected
        if not selected_agents:
            console.print(
                "[yellow]No AI assistants selected. Please select at least one.[/yellow]"
            )
            raise typer.Exit(1)

    # Check tools for all selected agents that require CLI
    if not ignore_agent_tools:
        missing_tools = []
        for agent in selected_agents:
            agent_config = AGENT_CONFIG.get(agent)
            if agent_config and agent_config["requires_cli"]:
                if not check_tool(agent):
                    missing_tools.append((agent, agent_config))

        if missing_tools:
            # Display error panel for missing tools
            error_lines = []
            for agent, config in missing_tools:
                install_url = config["install_url"]
                error_lines.append(f"[cyan]{agent}[/cyan] ({config['name']})")
                error_lines.append(f"  Install from: [cyan]{install_url}[/cyan]")
                error_lines.append("")

            error_panel = Panel(
                "\n".join(error_lines)
                + "\nThese AI assistants require CLI tools to continue.\n\n"
                "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                title="[red]Missing Agent Tools[/red]",
                border_style="red",
                padding=(1, 2),
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(
                SCRIPT_TYPE_CHOICES,
                "Choose script type (or press Enter)",
                default_script,
            )
        else:
            selected_script = default_script

    # Handle constitution tier selection
    if constitution:
        if constitution not in CONSTITUTION_TIER_CHOICES:
            console.print(
                f"[red]Error:[/red] Invalid constitution tier '{constitution}'. "
                f"Choose from: {', '.join(CONSTITUTION_TIER_CHOICES.keys())}"
            )
            raise typer.Exit(1)
        selected_constitution = constitution
    else:
        default_constitution = "medium"
        if sys.stdin.isatty():
            selected_constitution = select_with_arrows(
                CONSTITUTION_TIER_CHOICES,
                "Choose constitution tier (or press Enter for medium)",
                default_constitution,
            )
        else:
            selected_constitution = default_constitution

    # Display selected agents
    agents_display = ", ".join(selected_agents)
    if len(selected_agents) == 1:
        console.print(f"[cyan]Selected AI assistant:[/cyan] {agents_display}")
    else:
        console.print(f"[cyan]Selected AI assistants:[/cyan] {agents_display}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")
    console.print(f"[cyan]Selected constitution tier:[/cyan] {selected_constitution}")

    tracker = StepTracker("Initialize Specify Project")

    sys._specify_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant(s)")
    tracker.complete("ai-select", f"{agents_display}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    tracker.add("constitution-select", "Select constitution tier")
    tracker.complete("constitution-select", selected_constitution)

    # Different tracking keys based on layered mode
    if layered:
        for key, label in [
            ("fetch-base", "Fetch base spec-kit"),
            ("fetch-extension", "Fetch jp-spec-kit extension"),
            ("extract-base", "Extract base template"),
            ("extract-extension", "Extract extension (overlay)"),
            ("merge", "Merge templates (extension overrides base)"),
            ("chmod", "Ensure scripts executable"),
            ("cleanup", "Cleanup"),
            ("git", "Initialize git repository"),
            ("hooks", "Scaffold hooks"),
            ("constitution", "Set up constitution"),
            ("final", "Finalize"),
        ]:
            tracker.add(key, label)
    else:
        for key, label in [
            ("fetch", "Fetch latest release"),
            ("download", "Download template"),
            ("extract", "Extract template"),
            ("zip-list", "Archive contents"),
            ("extracted-summary", "Extraction summary"),
            ("chmod", "Ensure scripts executable"),
            ("cleanup", "Cleanup"),
            ("git", "Initialize git repository"),
            ("hooks", "Scaffold hooks"),
            ("constitution", "Set up constitution"),
            ("final", "Finalize"),
        ]:
            tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(
        tracker.render(), console=console, refresh_per_second=8, transient=True
    ) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            if layered:
                # Two-stage download: base + extension (supports multiple agents)
                download_and_extract_two_stage(
                    project_path,
                    selected_agents,  # Now a list
                    selected_script,
                    here,
                    verbose=False,
                    tracker=tracker,
                    client=local_client,
                    debug=debug,
                    github_token=github_token,
                    base_version=base_version,
                    extension_version=extension_version,
                )
            else:
                # Single-stage download (legacy mode or base-only, supports multiple agents)
                download_and_extract_template(
                    project_path,
                    selected_agents,  # Now a list
                    selected_script,
                    here,
                    verbose=False,
                    tracker=tracker,
                    client=local_client,
                    debug=debug,
                    github_token=github_token,
                    repo_owner=EXTENSION_REPO_OWNER,
                    repo_name=EXTENSION_REPO_NAME,
                    version=extension_version,
                )

            ensure_executable_scripts(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            # Handle light mode setup
            if light:
                light_marker = project_path / ".jpspec-light-mode"
                light_marker.write_text(
                    "# Light mode enabled - ~60% faster workflow (example: 135 min → 50 min)\n# See docs/guides/when-to-use-light-mode.md for details\n"
                )
                tracker.add("light-mode", "Light mode enabled")
                tracker.complete("light-mode", "marker created")

            # Scaffold hooks directory structure
            tracker.start("hooks")
            try:
                from .hooks.scaffold import scaffold_hooks

                created_files = scaffold_hooks(project_path)
                if created_files:
                    tracker.complete(
                        "hooks", f"created {len(created_files)} example hook files"
                    )
                else:
                    tracker.complete("hooks", "hooks already configured")
            except Exception as hook_error:
                # Non-fatal error - continue with project initialization
                tracker.error("hooks", f"scaffolding failed: {hook_error}")

            # Set up constitution template
            tracker.start("constitution")
            try:
                # Get constitution template from embedded templates
                if selected_constitution in CONSTITUTION_TEMPLATES:
                    memory_dir = project_path / "memory"
                    constitution_dest = memory_dir / "constitution.md"
                    memory_dir.mkdir(parents=True, exist_ok=True)
                    constitution_dest.write_text(
                        CONSTITUTION_TEMPLATES[selected_constitution]
                    )
                    tracker.complete(
                        "constitution",
                        f"{selected_constitution} tier → memory/constitution.md",
                    )
                else:
                    tracker.error(
                        "constitution",
                        f"unknown tier: {selected_constitution}",
                    )
            except Exception as const_error:
                tracker.error("constitution", f"setup failed: {const_error}")

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(
                Panel(
                    f"Initialization failed: {e}", title="Failure", border_style="red"
                )
            )
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [
                    f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]"
                    for k, v in _env_pairs
                ]
                console.print(
                    Panel(
                        "\n".join(env_lines),
                        title="Debug Environment",
                        border_style="magenta",
                    )
                )
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")

    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f'[cyan]git commit -m "Initial commit"[/cyan]',
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(git_error_panel)

    # Agent folder security notice (for all selected agents)
    agent_folders = []
    for agent in selected_agents:
        agent_config = AGENT_CONFIG.get(agent)
        if agent_config:
            agent_folders.append(agent_config["folder"])

    if agent_folders:
        if len(agent_folders) == 1:
            folders_text = f"[cyan]{agent_folders[0]}[/cyan]"
        else:
            folders_text = ", ".join(
                [f"[cyan]{folder}[/cyan]" for folder in agent_folders]
            )

        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in their agent folders within your project.\n"
            f"Consider adding {folders_text} (or parts of them) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(security_notice)

    # Check for backlog-md and offer to install if missing
    current_backlog_version = check_backlog_installed_version()
    if not current_backlog_version:
        console.print()
        install_backlog = typer.confirm(
            "[cyan]backlog-md[/cyan] is not installed. Would you like to install it for task management?",
            default=True,
        )
        if install_backlog:
            target_version = backlog_version or get_backlog_validated_version()
            if target_version:
                pkg_manager = detect_package_manager()
                if pkg_manager:
                    console.print(
                        f"\n[cyan]Installing backlog-md@{target_version}...[/cyan]"
                    )
                    try:
                        if pkg_manager == "pnpm":
                            cmd = ["pnpm", "add", "-g", f"backlog-md@{target_version}"]
                        else:
                            cmd = [
                                "npm",
                                "install",
                                "-g",
                                f"backlog-md@{target_version}",
                            ]

                        subprocess.run(cmd, check=True, capture_output=True, text=True)

                        installed_version = check_backlog_installed_version()
                        if installed_version:
                            console.print(
                                f"[green]backlog-md {installed_version} installed successfully![/green]"
                            )
                        else:
                            console.print(
                                "[yellow]Installation completed but verification failed[/yellow]"
                            )
                    except subprocess.CalledProcessError as e:
                        console.print(
                            f"[yellow]Installation failed:[/yellow] {e.stderr}"
                        )
                        console.print(
                            "[dim]You can install it manually later: specify backlog install[/dim]"
                        )
                else:
                    console.print(
                        "[yellow]No Node.js package manager found (pnpm or npm required)[/yellow]"
                    )
                    console.print(
                        "[dim]Install backlog-md manually: specify backlog install[/dim]"
                    )
            else:
                console.print(
                    "[yellow]Could not determine backlog-md version to install[/yellow]"
                )
                console.print(
                    "[dim]You can install it manually later: specify backlog install[/dim]"
                )
        else:
            console.print(
                "[dim]You can install backlog-md later with: specify backlog install[/dim]"
            )
    elif backlog_version:
        # User specified a version but backlog is already installed
        console.print()
        console.print(
            f"[yellow]backlog-md is already installed (version {current_backlog_version})[/yellow]"
        )
        console.print(
            f"[dim]To change version: specify backlog upgrade --version {backlog_version}[/dim]"
        )

    # Generate workflow configuration file with per-transition validation modes
    if no_validation_prompts:
        # Use NONE for all transitions
        transition_modes = {}
    else:
        # Build per-transition mode dict from CLI flags
        transition_modes = {
            "assess": validation_assess,
            "research": validation_research,
            "specify": validation_specify,
            "plan": validation_plan,
            "implement": validation_implement,
            "validate": validation_validate,
            "operate": validation_operate,
        }

    generate_jpspec_workflow_yml(project_path, transition_modes)
    console.print()
    console.print("[green]Generated jpspec_workflow.yml[/green]")

    # Show non-default validation modes
    non_default = {k: v for k, v in transition_modes.items() if v.lower() != "none"}
    if non_default:
        console.print("[dim]Custom validation modes:[/dim]")
        for name, mode in non_default.items():
            console.print(f"  [dim]{name}: {mode.upper()}[/dim]")

    steps_lines = []
    if not here:
        steps_lines.append(
            f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]"
        )
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if "codex" in selected_agents:
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"

        steps_lines.append(
            f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]"
        )
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append(
        "   2.1 [cyan]/speckit.constitution[/] - Establish project principles"
    )
    steps_lines.append(
        "   2.2 [cyan]/speckit.specify[/] - Create baseline specification"
    )
    steps_lines.append("   2.3 [cyan]/speckit.plan[/] - Create implementation plan")
    steps_lines.append("   2.4 [cyan]/speckit.tasks[/] - Generate actionable tasks")
    steps_lines.append("   2.5 [cyan]/speckit.implement[/] - Execute implementation")

    steps_panel = Panel(
        "\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1, 2)
    )
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
        "",
        "○ [cyan]/speckit.clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/speckit.plan[/] if used)",
        "○ [cyan]/speckit.analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/speckit.tasks[/], before [cyan]/speckit.implement[/])",
        "○ [cyan]/speckit.checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/speckit.plan[/])",
    ]
    enhancements_panel = Panel(
        "\n".join(enhancement_lines),
        title="Enhancement Commands",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(enhancements_panel)


@app.command()
def upgrade(
    base_version: str = typer.Option(
        None,
        "--base-version",
        help="Specific version of base spec-kit to upgrade to (default: latest)",
    ),
    extension_version: str = typer.Option(
        None,
        "--extension-version",
        help="Specific version of jp-spec-kit extension to upgrade to (default: latest)",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be upgraded without making changes"
    ),
    templates_only: bool = typer.Option(
        False, "--templates-only", help="Only update templates, skip other files"
    ),
    skip_tls: bool = typer.Option(
        False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"
    ),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output"),
    github_token: str = typer.Option(
        None,
        "--github-token",
        help="GitHub token to use for API requests (or set GITHUB_JPSPEC environment variable)",
    ),
):
    """
    Upgrade an existing Specify project to the latest (or specified) versions of base spec-kit and jp-spec-kit extension.

    This command will:
    1. Detect the AI assistant type from the project
    2. Download latest base spec-kit templates
    3. Download latest jp-spec-kit extension
    4. Merge with precedence (extension overrides base)
    5. Apply updates to current project

    Examples:
        specify upgrade                                    # Upgrade to latest base + extension
        specify upgrade --dry-run                          # Preview changes
        specify upgrade --base-version 0.0.20              # Pin base to specific version
        specify upgrade --extension-version 0.0.21         # Pin extension to specific version
        specify upgrade --templates-only                   # Only update template files
    """
    show_banner()

    project_path = Path.cwd()

    # Check for source repository marker to prevent clobbering jp-spec-kit source
    marker_path = project_path / SOURCE_REPO_MARKER
    if marker_path.exists():
        error_panel = Panel(
            f"[yellow]This directory contains '{SOURCE_REPO_MARKER}'[/yellow]\n\n"
            "This indicates it is the jp-spec-kit source repository.\n"
            "Running 'specify upgrade' here would overwrite source files.\n\n"
            "[cyan]To update jp-spec-kit itself:[/cyan]\n"
            "  Use git pull or standard development workflow.\n\n"
            "[cyan]To test 'specify upgrade' on a project:[/cyan]\n"
            "  Navigate to a project initialized with 'specify init'.",
            title="[yellow]Source Repository Detected[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print()
        console.print(error_panel)
        raise typer.Exit(1)

    # Detect AI assistant from existing project
    ai_assistant = None
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_folder = project_path / agent_config["folder"]
        if agent_folder.exists():
            ai_assistant = agent_key
            break

    if not ai_assistant:
        console.print(
            "[red]Error:[/red] Could not detect AI assistant type in current directory"
        )
        console.print(
            "[yellow]Tip:[/yellow] Make sure you're in a Specify project directory"
        )
        raise typer.Exit(1)

    # Detect script type (look for .sh or .ps1 scripts)
    script_type = "sh"  # default
    specify_scripts = project_path / ".specify" / "scripts"
    if specify_scripts.exists():
        if list(specify_scripts.glob("**/*.ps1")):
            script_type = "ps"

    console.print("[cyan]Detected configuration:[/cyan]")
    console.print(f"  AI Assistant: [green]{ai_assistant}[/green]")
    console.print(f"  Script Type:  [green]{script_type}[/green]")
    console.print()

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")

    tracker = StepTracker("Upgrade Specify Project")

    tracker.add("detect", "Detect project configuration")
    tracker.complete("detect", f"{ai_assistant}, {script_type}")
    tracker.add("fetch-base", "Fetch base spec-kit")
    tracker.add("fetch-extension", "Fetch jp-spec-kit extension")
    tracker.add("backup", "Backup current templates")
    tracker.add("apply", "Apply updates")
    tracker.add("final", "Finalize")

    if dry_run:
        # In dry run, just fetch and report what would change
        console.print(tracker.render())
        console.print(
            "\n[green]Dry run completed. Use without --dry-run to apply changes.[/green]"
        )
        return

    with Live(
        tracker.render(), console=console, refresh_per_second=8, transient=True
    ) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            # Create backup of existing templates
            tracker.start("backup")
            backup_dir = project_path / ".specify-backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            backup_dir.mkdir(parents=True)

            # Backup key directories
            for dir_name in [".specify", ".claude", ".github", "templates"]:
                src = project_path / dir_name
                if src.exists():
                    shutil.copytree(src, backup_dir / dir_name, dirs_exist_ok=True)

            tracker.complete("backup", f"saved to {backup_dir.name}")

            # Apply two-stage upgrade
            tracker.start("apply")
            download_and_extract_two_stage(
                project_path,
                ai_assistant,
                script_type,
                is_current_dir=True,  # Upgrade in place
                verbose=False,
                tracker=tracker,
                client=local_client,
                debug=debug,
                github_token=github_token,
                base_version=base_version,
                extension_version=extension_version,
            )

            tracker.complete("apply", "templates updated")
            tracker.complete("final", "upgrade complete")

        except Exception as e:
            tracker.error("final", str(e))
            console.print(f"\n[red]Upgrade failed:[/red] {e}")
            console.print(f"[yellow]Backup available at:[/yellow] {backup_dir}")
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Upgrade completed successfully![/bold green]")
    console.print(f"[dim]Backup of previous templates: {backup_dir}[/dim]")

    # Check and offer to sync backlog-md version
    current_backlog_version = check_backlog_installed_version()
    recommended_version = get_backlog_validated_version()

    if current_backlog_version and recommended_version:
        if current_backlog_version != recommended_version:
            console.print()
            console.print(
                f"[yellow]backlog-md version mismatch:[/yellow] "
                f"current={current_backlog_version}, recommended={recommended_version}"
            )
            sync_backlog = typer.confirm(
                "Would you like to sync backlog-md to the recommended version?",
                default=True,
            )
            if sync_backlog:
                pkg_manager = detect_package_manager()
                if pkg_manager:
                    console.print(
                        f"\n[cyan]Syncing backlog-md to {recommended_version}...[/cyan]"
                    )
                    try:
                        if pkg_manager == "pnpm":
                            cmd = [
                                "pnpm",
                                "add",
                                "-g",
                                f"backlog-md@{recommended_version}",
                            ]
                        else:
                            cmd = [
                                "npm",
                                "install",
                                "-g",
                                f"backlog-md@{recommended_version}",
                            ]

                        subprocess.run(cmd, check=True, capture_output=True, text=True)

                        new_version = check_backlog_installed_version()
                        if new_version == recommended_version:
                            console.print(
                                f"[green]backlog-md synced to {new_version}![/green]"
                            )
                        else:
                            console.print(
                                "[yellow]Sync completed but verification failed[/yellow]"
                            )
                    except subprocess.CalledProcessError as e:
                        console.print(f"[yellow]Sync failed:[/yellow] {e.stderr}")
                        console.print(
                            "[dim]You can sync manually: specify backlog upgrade[/dim]"
                        )
                else:
                    console.print("[yellow]No Node.js package manager found[/yellow]")
                    console.print(
                        "[dim]You can sync manually: specify backlog upgrade[/dim]"
                    )
            else:
                console.print(
                    "[dim]You can sync backlog-md later with: specify backlog upgrade[/dim]"
                )
    elif not current_backlog_version and recommended_version:
        console.print()
        console.print("[yellow]backlog-md is not installed[/yellow]")
        console.print("[dim]Install with: specify backlog install[/dim]")

    console.print()
    console.print("[cyan]Next steps:[/cyan]")
    console.print("  1. Review changes with: [cyan]git diff[/cyan]")
    console.print("  2. Test your project to ensure everything works")
    console.print(
        f"  3. If needed, restore from backup: [cyan]cp -r {backup_dir}/* .[/cyan]"
    )


@app.command()
def check():
    """Check that all required tools are installed."""
    show_banner()
    console.print("[bold]Checking for installed tools...[/bold]\n")

    tracker = StepTracker("Check Available Tools")

    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_name = agent_config["name"]

        tracker.add(agent_key, agent_name)
        agent_results[agent_key] = check_tool(agent_key, tracker=tracker)

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    check_tool("code-insiders", tracker=tracker)

    # Check backlog-md
    tracker.add("backlog", "backlog-md (task management)")
    backlog_version = check_backlog_installed_version()
    if backlog_version:
        tracker.complete("backlog", f"v{backlog_version}")
    else:
        tracker.skip("backlog", "not installed")

    console.print(tracker.render())

    # Show backlog-md version compatibility info if installed
    if backlog_version:
        recommended_version = get_backlog_validated_version()
        if recommended_version:
            console.print()
            if backlog_version == recommended_version:
                console.print(
                    f"[green]backlog-md is at recommended version ({backlog_version})[/green]"
                )
            else:
                console.print(
                    f"[yellow]backlog-md version:[/yellow] {backlog_version} "
                    f"[dim](recommended: {recommended_version})[/dim]"
                )
                console.print(
                    "[dim]Run 'specify backlog upgrade' to sync to recommended version[/dim]"
                )

    console.print("\n[bold green]Specify CLI is ready to use![/bold green]")

    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")

    if not backlog_version:
        console.print(
            "[dim]Tip: Install backlog-md for task management: specify backlog install[/dim]"
        )


@app.command(name="dev-setup")
def dev_setup(
    force: bool = typer.Option(
        False,
        "--force",
        help="Recreate symlinks even if they already exist",
    ),
):
    """
    Set up jp-spec-kit source repository for development.

    This command prepares the jp-spec-kit source repository to use its own
    /speckit:* and /jpspec:* commands during development. It creates symlinks
    for multiple AI agents:

    - Claude Code: .claude/commands/speckit/ and .claude/commands/jpspec/
      (symlinks to templates/commands/)
    - VS Code Copilot: .github/prompts/ (symlinks as speckit.*.prompt.md
      and jpspec.*.prompt.md)

    It also creates .vscode/settings.json with chat.promptFiles enabled for Copilot.

    This is only useful when developing jp-spec-kit itself. For normal
    projects, use 'specify init' instead.

    Examples:
        specify dev-setup           # Set up for development
        specify dev-setup --force   # Recreate symlinks if they exist
    """
    show_banner()

    project_path = Path.cwd()

    # Check that we're in the jp-spec-kit source repository
    marker_path = project_path / SOURCE_REPO_MARKER
    if not marker_path.exists():
        console.print(
            "[red]Error:[/red] This command is only for the jp-spec-kit source repository."
        )
        console.print(
            f"[yellow]Tip:[/yellow] The '{SOURCE_REPO_MARKER}' marker file was not found."
        )
        console.print(
            "[yellow]Tip:[/yellow] If this IS the jp-spec-kit repo, create the marker file first."
        )
        raise typer.Exit(1)

    templates_dir = project_path / "templates" / "commands"
    jpspec_templates_dir = templates_dir / "jpspec"
    if not templates_dir.exists():
        console.print(
            f"[red]Error:[/red] Templates directory not found: {templates_dir}"
        )
        raise typer.Exit(1)

    # Get list of template command files
    speckit_files = list(templates_dir.glob("*.md"))
    jpspec_files = (
        list(jpspec_templates_dir.glob("*.md")) if jpspec_templates_dir.exists() else []
    )

    if not speckit_files and not jpspec_files:
        console.print(
            f"[yellow]Warning:[/yellow] No command templates found in {templates_dir}"
        )
        raise typer.Exit(1)

    console.print(
        "[cyan]Setting up development environment for jp-spec-kit...[/cyan]\n"
    )

    tracker = StepTracker("Dev Setup")
    tracker.add("check", "Check prerequisites")
    tracker.complete("check", "jp-spec-kit source repository detected")

    all_errors = []

    # === Claude Code Setup - speckit commands ===
    tracker.add("claude_speckit", "Set up Claude Code speckit commands")

    speckit_commands_dir = project_path / ".claude" / "commands" / "speckit"
    speckit_commands_dir.mkdir(parents=True, exist_ok=True)

    claude_speckit_created = 0
    claude_speckit_skipped = 0
    claude_speckit_errors = []

    for template_file in speckit_files:
        symlink_path = speckit_commands_dir / template_file.name
        relative_target = (
            Path("..") / ".." / ".." / "templates" / "commands" / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    claude_speckit_created += 1
                else:
                    claude_speckit_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                claude_speckit_created += 1
        except OSError as e:
            claude_speckit_errors.append(f"speckit/{template_file.name}: {e}")

    if claude_speckit_errors:
        tracker.fail("claude_speckit", f"{len(claude_speckit_errors)} errors")
        all_errors.extend(claude_speckit_errors)
    else:
        tracker.complete(
            "claude_speckit",
            f"{claude_speckit_created} created, {claude_speckit_skipped} skipped",
        )

    # === Claude Code Setup - jpspec commands ===
    tracker.add("claude_jpspec", "Set up Claude Code jpspec commands")

    jpspec_commands_dir = project_path / ".claude" / "commands" / "jpspec"
    jpspec_commands_dir.mkdir(parents=True, exist_ok=True)

    claude_jpspec_created = 0
    claude_jpspec_skipped = 0
    claude_jpspec_errors = []

    for template_file in jpspec_files:
        symlink_path = jpspec_commands_dir / template_file.name
        relative_target = (
            Path("..")
            / ".."
            / ".."
            / "templates"
            / "commands"
            / "jpspec"
            / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    claude_jpspec_created += 1
                else:
                    claude_jpspec_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                claude_jpspec_created += 1
        except OSError as e:
            claude_jpspec_errors.append(f"jpspec/{template_file.name}: {e}")

    if claude_jpspec_errors:
        tracker.fail("claude_jpspec", f"{len(claude_jpspec_errors)} errors")
        all_errors.extend(claude_jpspec_errors)
    else:
        tracker.complete(
            "claude_jpspec",
            f"{claude_jpspec_created} created, {claude_jpspec_skipped} skipped",
        )

    # === VS Code Copilot Setup ===
    tracker.add("copilot", "Set up VS Code Copilot prompts")

    prompts_dir = project_path / ".github" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    copilot_created = 0
    copilot_skipped = 0
    copilot_errors = []

    # Create speckit.*.prompt.md symlinks for speckit commands
    for template_file in speckit_files:
        # VS Code Copilot uses speckit.*.prompt.md format
        prompt_name = f"speckit.{template_file.stem}.prompt.md"
        symlink_path = prompts_dir / prompt_name
        relative_target = (
            Path("..") / ".." / "templates" / "commands" / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    copilot_created += 1
                else:
                    copilot_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                copilot_created += 1
        except OSError as e:
            copilot_errors.append(f"{prompt_name}: {e}")

    # Create jpspec.*.prompt.md symlinks for jpspec commands
    for template_file in jpspec_files:
        # VS Code Copilot uses jpspec.*.prompt.md format
        prompt_name = f"jpspec.{template_file.stem}.prompt.md"
        symlink_path = prompts_dir / prompt_name
        relative_target = (
            Path("..") / ".." / "templates" / "commands" / "jpspec" / template_file.name
        )

        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                if force:
                    symlink_path.unlink()
                    symlink_path.symlink_to(relative_target)
                    copilot_created += 1
                else:
                    copilot_skipped += 1
            else:
                symlink_path.symlink_to(relative_target)
                copilot_created += 1
        except OSError as e:
            copilot_errors.append(f"{prompt_name}: {e}")

    if copilot_errors:
        tracker.fail("copilot", f"{len(copilot_errors)} errors")
        all_errors.extend(copilot_errors)
    else:
        tracker.complete(
            "copilot", f"{copilot_created} created, {copilot_skipped} skipped"
        )

    # === VS Code Settings Setup ===
    tracker.add("vscode", "Configure VS Code settings")

    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    settings_file = vscode_dir / "settings.json"

    try:
        # Read existing settings or start fresh
        existing_settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    import json

                    content = f.read()
                    # Handle jsonc (with comments) by stripping single-line comments
                    import re

                    content = re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)
                    existing_settings = json.loads(content) if content.strip() else {}
            except (json.JSONDecodeError, ValueError):
                existing_settings = {}

        # Merge with required settings for Copilot prompt files
        existing_settings["chat.promptFiles"] = True

        # Write updated settings
        with open(settings_file, "w") as f:
            import json

            json.dump(existing_settings, f, indent=4)
            f.write("\n")

        tracker.complete("vscode", "chat.promptFiles enabled")
    except OSError as e:
        tracker.fail("vscode", str(e))
        all_errors.append(f"settings.json: {e}")

    # === Verify Symlinks ===
    tracker.add("verify", "Verify symlinks")

    valid = 0
    broken = 0

    # Check Claude speckit symlinks
    for symlink_path in speckit_commands_dir.glob("*.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    # Check Claude jpspec symlinks
    for symlink_path in jpspec_commands_dir.glob("*.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    # Check Copilot symlinks
    for symlink_path in prompts_dir.glob("*.prompt.md"):
        if symlink_path.is_symlink():
            if symlink_path.resolve().exists():
                valid += 1
            else:
                broken += 1

    if broken > 0:
        tracker.fail("verify", f"{broken} broken symlinks")
    else:
        tracker.complete("verify", f"{valid} valid symlinks")

    tracker.add("final", "Dev setup complete")
    tracker.complete("final", "ready for development")

    console.print(tracker.render())

    console.print("\n[bold green]Development setup complete![/bold green]")

    console.print(
        "\n[bold]Claude Code[/bold] - The following commands are now available:"
    )
    console.print("  [dim]speckit:[/dim]")
    for template_file in sorted(speckit_files):
        console.print(f"    [cyan]/speckit:{template_file.stem}[/cyan]")
    console.print("  [dim]jpspec:[/dim]")
    for template_file in sorted(jpspec_files):
        console.print(f"    [cyan]/jpspec:{template_file.stem}[/cyan]")

    console.print(
        "\n[bold]VS Code Copilot[/bold] - The following prompts are now available:"
    )
    for template_file in sorted(speckit_files):
        console.print(f"  [cyan]/speckit.{template_file.stem}[/cyan]")
    for template_file in sorted(jpspec_files):
        console.print(f"  [cyan]/jpspec.{template_file.stem}[/cyan]")

    console.print(
        "\n[dim]Note: Restart your AI assistant to pick up the new commands.[/dim]"
    )

    if all_errors:
        console.print("\n[yellow]Warning:[/yellow] Some operations failed:")
        for error in all_errors:
            console.print(f"  [red]•[/red] {error}")
        console.print(
            "[yellow]On Windows, you may need to enable Developer Mode or run as Administrator.[/yellow]"
        )
        raise typer.Exit(1)


# Create backlog subcommand group
backlog_app = typer.Typer(
    name="backlog",
    help="Manage Backlog.md format tasks",
    add_completion=False,
)
app.add_typer(backlog_app, name="backlog")


@backlog_app.command("migrate")
def backlog_migrate(
    source: Optional[str] = typer.Option(
        None,
        "--source",
        help="Path to tasks.md file (default: ./tasks.md)",
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output backlog directory (default: ./backlog)",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backup of original tasks.md (default: true)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview migration without writing files",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing backlog tasks",
    ),
):
    """
    Migrate existing tasks.md file to Backlog.md format.

    This command converts legacy tasks.md files to the new Backlog.md format
    with individual task files. It preserves all task metadata including IDs,
    labels, dependencies, status, and user stories.

    Examples:
        specify backlog migrate                          # Migrate ./tasks.md to ./backlog
        specify backlog migrate --source ../tasks.md     # Migrate from specific file
        specify backlog migrate --dry-run                # Preview migration
        specify backlog migrate --force                  # Overwrite existing tasks
        specify backlog migrate --no-backup              # Skip backup creation
    """
    show_banner()

    # Determine paths
    source_path = Path(source) if source else Path.cwd() / "tasks.md"
    output_dir = Path(output) if output else Path.cwd() / "backlog"

    # Validate source file
    if not source_path.exists():
        console.print(f"[red]Error:[/red] Source file not found: {source_path}")
        raise typer.Exit(1)

    if not source_path.is_file():
        console.print(f"[red]Error:[/red] Source must be a file: {source_path}")
        raise typer.Exit(1)

    if source_path.name != "tasks.md":
        console.print(
            f"[yellow]Warning:[/yellow] Source file is not named 'tasks.md': {source_path.name}"
        )
        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(0)

    console.print(f"[cyan]Source:[/cyan] {source_path}")
    console.print(f"[cyan]Output:[/cyan] {output_dir}")
    console.print(f"[cyan]Backup:[/cyan] {backup}")

    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")

    console.print()

    # Import migration module
    from .backlog import TaskMapper

    # Create mapper
    mapper = TaskMapper(output_dir)

    try:
        # Check for existing tasks
        existing_count = 0
        if (output_dir / "tasks").exists():
            existing_count = len(list((output_dir / "tasks").glob("task-*.md")))
            if existing_count > 0 and not force and not dry_run:
                console.print(
                    f"[yellow]Warning:[/yellow] Found {existing_count} existing task files in {output_dir / 'tasks'}"
                )
                console.print(
                    "[yellow]Use --force to overwrite existing tasks[/yellow]"
                )
                if not typer.confirm("Continue (will skip existing tasks)?"):
                    raise typer.Exit(0)

        # Create backup if requested
        backup_path = None
        if backup and not dry_run:
            backup_path = source_path.with_suffix(".md.backup")
            backup_counter = 1
            while backup_path.exists():
                backup_path = source_path.with_suffix(f".md.backup.{backup_counter}")
                backup_counter += 1

            import shutil

            shutil.copy2(source_path, backup_path)
            console.print(f"[green]Created backup:[/green] {backup_path}\n")

        # Perform migration
        result = mapper.generate_from_tasks_file(
            source_path,
            overwrite=force,
            dry_run=dry_run,
        )

        # Handle results
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            console.print(f"[red]Migration failed:[/red] {error_msg}")

            # Show validation errors if present
            if "validation_errors" in result:
                console.print("\n[yellow]Validation Errors:[/yellow]")
                for error in result["validation_errors"]:
                    console.print(f"  - {error}")

            # Remove backup on failure (if created)
            if backup_path and backup_path.exists():
                backup_path.unlink()
                console.print("[dim]Removed backup (migration failed)[/dim]")

            raise typer.Exit(1)

        # Show success message
        if dry_run:
            console.print("[bold green]Migration preview completed![/bold green]\n")
        else:
            console.print("[bold green]Migration complete![/bold green]\n")

        # Display statistics
        stats_lines = []

        if "tasks_parsed" in result:
            stats_lines.append(
                f"{'Tasks Found':<20} [green]{result['tasks_parsed']}[/green]"
            )

        if "tasks_created" in result and not dry_run:
            stats_lines.append(
                f"{'Tasks Created':<20} [green]{result['tasks_created']}[/green]"
            )

        # Count completed vs pending
        from .backlog.parser import TaskParser

        parser = TaskParser()
        tasks = parser.parse_tasks_file(source_path)
        completed = sum(1 for t in tasks if t.is_completed)
        pending = len(tasks) - completed

        if completed > 0:
            stats_lines.append(f"{'Completed Tasks':<20} [green]{completed}[/green]")
        if pending > 0:
            stats_lines.append(f"{'Pending Tasks':<20} [cyan]{pending}[/cyan]")

        # Count user stories
        user_stories = set(t.user_story for t in tasks if t.user_story)
        if user_stories:
            stats_lines.append(
                f"{'User Stories':<20} [cyan]{len(user_stories)}[/cyan] ({', '.join(sorted(user_stories))})"
            )

        # Show groupings
        if "tasks_by_phase" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Phase:[/bold]")
            for phase, task_ids in sorted(result["tasks_by_phase"].items()):
                stats_lines.append(f"  {phase:<18} {len(task_ids)} tasks")

        if "tasks_by_story" in result and len(result["tasks_by_story"]) > 1:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Story:[/bold]")
            for story, task_ids in sorted(result["tasks_by_story"].items()):
                if story != "No Story":
                    stats_lines.append(f"  {story:<18} {len(task_ids)} tasks")

        if stats_lines:
            console.print(
                Panel(
                    "\n".join(stats_lines),
                    title="Migration Summary",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

        # Show next steps
        if not dry_run:
            console.print()
            next_steps = [
                f"1. Review migrated tasks in: [cyan]{output_dir / 'tasks'}[/cyan]",
                "2. Original tasks.md remains unchanged",
            ]

            if backup_path:
                next_steps.append(f"3. Backup created at: [cyan]{backup_path}[/cyan]")

            next_steps.extend(
                [
                    "",
                    "[dim]You can now track task progress by updating status in task frontmatter[/dim]",
                    "[dim]Use 'specify tasks generate' to regenerate tasks from spec[/dim]",
                ]
            )

            console.print(
                Panel(
                    "\n".join(next_steps),
                    title="Next Steps",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--debug" in sys.argv:
            import traceback

            console.print("\n[yellow]Debug trace:[/yellow]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def tasks(
    action: str = typer.Argument(
        "generate", help="Action to perform (currently only 'generate' is supported)"
    ),
    format: str = typer.Option(
        "backlog",
        "--format",
        help="Output format: 'backlog' (Backlog.md format) or 'markdown' (legacy tasks.md)",
    ),
    source: Optional[str] = typer.Option(
        None,
        "--source",
        help="Path to source file or directory (default: current directory)",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output",
        help="Output directory for backlog format (default: ./backlog)",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing task files"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be generated without creating files",
    ),
):
    """
    Generate tasks from spec/plan/tasks.md files.

    This command can generate tasks in two formats:

    1. backlog (default): Creates individual task files in ./backlog/tasks/ directory
       following the Backlog.md format specification

    2. markdown: Generates a single tasks.md file (legacy format)

    The command automatically detects the source files (spec.md, plan.md, tasks.md)
    from the current directory or specified source path.

    Examples:
        specify tasks generate                           # Generate backlog tasks from current dir
        specify tasks generate --format markdown         # Generate legacy tasks.md format
        specify tasks generate --source ./feature-x      # Generate from specific directory
        specify tasks generate --dry-run                 # Preview without writing files
        specify tasks generate --overwrite               # Overwrite existing tasks
    """
    show_banner()

    # Only support 'generate' action for now
    if action != "generate":
        console.print(
            f"[red]Error:[/red] Unsupported action '{action}'. Currently only 'generate' is supported."
        )
        raise typer.Exit(1)

    # Validate format
    if format not in ["backlog", "markdown"]:
        console.print(
            f"[red]Error:[/red] Invalid format '{format}'. Must be 'backlog' or 'markdown'."
        )
        raise typer.Exit(1)

    # Determine source path
    source_path = Path(source) if source else Path.cwd()
    if not source_path.exists():
        console.print(f"[red]Error:[/red] Source path does not exist: {source_path}")
        raise typer.Exit(1)

    # Handle markdown format (legacy)
    if format == "markdown":
        console.print("[yellow]Legacy markdown format is not yet implemented.[/yellow]")
        console.print(
            "[dim]Tip: Use --format backlog for the new Backlog.md format[/dim]"
        )
        raise typer.Exit(1)

    # Handle backlog format
    from .backlog import TaskMapper

    # Determine backlog directory
    backlog_dir = (
        Path(output_dir)
        if output_dir
        else (
            source_path / "backlog" if source_path.is_dir() else Path.cwd() / "backlog"
        )
    )

    console.print(f"[cyan]Source:[/cyan] {source_path}")
    console.print(f"[cyan]Output:[/cyan] {backlog_dir}")
    console.print(f"[cyan]Format:[/cyan] {format}")
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be created[/yellow]")
    console.print()

    # Create mapper and generate tasks
    mapper = TaskMapper(backlog_dir)

    try:
        # Determine if source is a file or directory
        if source_path.is_file():
            if source_path.name != "tasks.md":
                console.print(
                    f"[red]Error:[/red] Source file must be named 'tasks.md', got: {source_path.name}"
                )
                raise typer.Exit(1)
            result = mapper.generate_from_tasks_file(
                source_path, overwrite=overwrite, dry_run=dry_run
            )
        elif source_path.is_dir():
            result = mapper.generate_from_spec(
                source_path, overwrite=overwrite, dry_run=dry_run
            )
        else:
            console.print(f"[red]Error:[/red] Invalid source path: {source_path}")
            raise typer.Exit(1)

        # Handle results
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            console.print(f"[red]Error:[/red] {error_msg}")

            # Show validation errors if present
            if "validation_errors" in result:
                console.print("\n[yellow]Validation Errors:[/yellow]")
                for error in result["validation_errors"]:
                    console.print(f"  - {error}")

            raise typer.Exit(1)

        # Show success message and statistics
        if dry_run:
            console.print("[bold green]Dry run completed successfully![/bold green]\n")
        else:
            console.print("[bold green]Tasks generated successfully![/bold green]\n")

        # Display statistics
        stats_lines = []

        if "tasks_parsed" in result:
            stats_lines.append(
                f"{'Tasks Parsed':<20} [green]{result['tasks_parsed']}[/green]"
            )

        if "tasks_created" in result and not dry_run:
            stats_lines.append(
                f"{'Tasks Created':<20} [green]{result['tasks_created']}[/green]"
            )

        if "user_stories" in result:
            stats_lines.append(
                f"{'User Stories':<20} [cyan]{result['user_stories']}[/cyan]"
            )

        # Show groupings
        if "tasks_by_phase" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Phase:[/bold]")
            for phase, task_ids in sorted(result["tasks_by_phase"].items()):
                stats_lines.append(f"  {phase:<18} {len(task_ids)} tasks")

        if "tasks_by_story" in result:
            stats_lines.append("")
            stats_lines.append("[bold]Tasks by Story:[/bold]")
            for story, task_ids in sorted(result["tasks_by_story"].items()):
                stats_lines.append(f"  {story:<18} {len(task_ids)} tasks")

        # Show execution order
        if "execution_order" in result:
            execution_order = result["execution_order"]
            stats_lines.append("")
            stats_lines.append(
                f"[bold]Execution Order:[/bold] {', '.join(execution_order[:5])}"
                + (
                    f"... ({len(execution_order)} total)"
                    if len(execution_order) > 5
                    else ""
                )
            )

        # Show parallel batches
        if "parallel_batches" in result:
            parallel_batches = result["parallel_batches"]
            stats_lines.append(
                f"[bold]Parallel Batches:[/bold] {len(parallel_batches)}"
            )

        # Show critical path
        if "critical_path" in result:
            critical_path = result["critical_path"]
            stats_lines.append(
                f"[bold]Critical Path Length:[/bold] {len(critical_path)}"
            )

        if stats_lines:
            console.print(
                Panel(
                    "\n".join(stats_lines),
                    title="Task Generation Summary",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

        # Show created files (if not dry run)
        if "created_files" in result and not dry_run:
            console.print()
            console.print("[bold]Created Files:[/bold]")
            for file_path in result["created_files"][:10]:  # Show first 10
                console.print(f"  [dim]{file_path}[/dim]")
            if len(result["created_files"]) > 10:
                console.print(
                    f"  [dim]... and {len(result['created_files']) - 10} more[/dim]"
                )

        # Next steps
        if not dry_run:
            console.print()
            next_steps = [
                f"1. Review generated tasks in: [cyan]{backlog_dir / 'tasks'}[/cyan]",
                "2. Edit task files as needed (add assignees, notes, etc.)",
                "3. Track progress by updating task status in frontmatter",
            ]
            console.print(
                Panel(
                    "\n".join(next_steps),
                    title="Next Steps",
                    border_style="cyan",
                    padding=(1, 2),
                )
            )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] File not found: {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if "--debug" in sys.argv:
            import traceback

            console.print("\n[yellow]Debug trace:[/yellow]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


# Create backlog subcommand group
backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog-md installation and upgrades",
)
app.add_typer(backlog_app, name="backlog")


@backlog_app.command("install")
def backlog_install(
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Specific version to install (default: recommended version from compatibility matrix)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force reinstall even if already installed",
    ),
):
    """
    Install backlog-md CLI tool with validated version.

    This command will:
    1. Auto-detect pnpm or npm package manager
    2. Fetch the recommended version from compatibility matrix
    3. Install backlog-md globally with version pinning
    4. Verify installation success

    Examples:
        specify backlog install                    # Install recommended version
        specify backlog install --version 1.21.0   # Install specific version
        specify backlog install --force            # Force reinstall
    """
    show_banner()

    # Check if already installed
    current_version = check_backlog_installed_version()
    if current_version and not force:
        console.print(
            f"[yellow]backlog-md is already installed (version {current_version})[/yellow]"
        )
        console.print("[dim]Use --force to reinstall[/dim]")
        raise typer.Exit(0)

    # Determine version to install
    target_version = version or get_backlog_validated_version()
    if not target_version:
        console.print(
            "[red]Error:[/red] Could not determine version to install. "
            "Compatibility matrix may be missing or invalid."
        )
        raise typer.Exit(1)

    # Detect package manager
    pkg_manager = detect_package_manager()
    if not pkg_manager:
        console.print(
            "[red]Error:[/red] No Node.js package manager found (pnpm or npm required)"
        )
        console.print(
            "[dim]Install pnpm: https://pnpm.io/installation[/dim]\n"
            "[dim]Or install npm: https://nodejs.org/[/dim]"
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Package Manager:[/cyan] {pkg_manager}")
    console.print(f"[cyan]Target Version:[/cyan] {target_version}\n")

    tracker = StepTracker("Install backlog-md")

    # Install
    tracker.add("install", f"Installing backlog-md@{target_version}")
    tracker.start("install")

    try:
        if pkg_manager == "pnpm":
            cmd = ["pnpm", "add", "-g", f"backlog-md@{target_version}"]
        else:  # npm
            cmd = ["npm", "install", "-g", f"backlog-md@{target_version}"]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        tracker.complete("install", "installed successfully")
    except subprocess.CalledProcessError as e:
        tracker.error("install", "installation failed")
        console.print(tracker.render())
        console.print(f"\n[red]Installation failed:[/red] {e.stderr}")
        raise typer.Exit(1)

    # Verify
    tracker.add("verify", "Verifying installation")
    tracker.start("verify")

    installed_version = check_backlog_installed_version()
    if installed_version:
        tracker.complete("verify", f"version {installed_version}")
    else:
        tracker.error("verify", "verification failed")

    console.print(tracker.render())

    if installed_version:
        console.print("\n[bold green]backlog-md installed successfully![/bold green]")
        console.print(f"[dim]Version: {installed_version}[/dim]")
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("  Run [cyan]backlog --help[/cyan] to get started")
    else:
        console.print(
            "\n[yellow]Installation completed but verification failed[/yellow]"
        )
        console.print("[dim]Try running: backlog --version[/dim]")
        raise typer.Exit(1)


@backlog_app.command("upgrade")
def backlog_upgrade(
    version: Optional[str] = typer.Option(
        None,
        "--version",
        help="Specific version to upgrade to (default: recommended version from compatibility matrix)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Force upgrade even if current version matches",
    ),
):
    """
    Upgrade backlog-md to validated version.

    This command will:
    1. Check currently installed version
    2. Compare to recommended version from compatibility matrix
    3. Upgrade if needed using detected package manager
    4. Verify upgrade success

    Examples:
        specify backlog upgrade                    # Upgrade to recommended version
        specify backlog upgrade --version 1.22.0   # Upgrade to specific version
        specify backlog upgrade --force            # Force upgrade
    """
    show_banner()

    # Check if installed
    current_version = check_backlog_installed_version()
    if not current_version:
        console.print("[yellow]backlog-md is not installed[/yellow]")
        console.print("[dim]Run: specify backlog install[/dim]")
        raise typer.Exit(1)

    # Determine target version
    target_version = version or get_backlog_validated_version()
    if not target_version:
        console.print(
            "[red]Error:[/red] Could not determine version to upgrade to. "
            "Compatibility matrix may be missing or invalid."
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Current Version:[/cyan] {current_version}")
    console.print(f"[cyan]Target Version:[/cyan] {target_version}\n")

    # Check if upgrade needed
    if current_version == target_version and not force:
        console.print("[green]backlog-md is already at the recommended version[/green]")
        raise typer.Exit(0)

    # Detect package manager
    pkg_manager = detect_package_manager()
    if not pkg_manager:
        console.print(
            "[red]Error:[/red] No Node.js package manager found (pnpm or npm required)"
        )
        raise typer.Exit(1)

    console.print(f"[cyan]Package Manager:[/cyan] {pkg_manager}\n")

    tracker = StepTracker("Upgrade backlog-md")

    # Upgrade
    tracker.add("upgrade", f"Upgrading to {target_version}")
    tracker.start("upgrade")

    try:
        if pkg_manager == "pnpm":
            cmd = ["pnpm", "add", "-g", f"backlog-md@{target_version}"]
        else:  # npm
            cmd = ["npm", "install", "-g", f"backlog-md@{target_version}"]

        subprocess.run(cmd, check=True, capture_output=True, text=True)
        tracker.complete("upgrade", "upgraded successfully")
    except subprocess.CalledProcessError as e:
        tracker.error("upgrade", "upgrade failed")
        console.print(tracker.render())
        console.print(f"\n[red]Upgrade failed:[/red] {e.stderr}")
        raise typer.Exit(1)

    # Verify
    tracker.add("verify", "Verifying upgrade")
    tracker.start("verify")

    new_version = check_backlog_installed_version()
    if new_version == target_version:
        tracker.complete("verify", f"version {new_version}")
    else:
        tracker.error("verify", "verification failed")

    console.print(tracker.render())

    if new_version == target_version:
        console.print("\n[bold green]backlog-md upgraded successfully![/bold green]")
        console.print(f"[dim]Version: {new_version}[/dim]")
    else:
        console.print("\n[yellow]Upgrade completed but verification failed[/yellow]")
        console.print(
            f"[dim]Expected: {target_version}, Got: {new_version or 'not found'}[/dim]"
        )
        raise typer.Exit(1)


@app.command()
def quality(
    spec_path: str = typer.Argument(
        None, help="Path to specification file (defaults to .specify/spec.md)"
    ),
    config_path: str = typer.Option(
        None, "--config", help="Path to custom quality config file"
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
    threshold: int = typer.Option(
        None, "--threshold", help="Minimum passing score (overrides config)"
    ),
    check_only: bool = typer.Option(
        False, "--check-only", help="Exit non-zero if below threshold (for CI)"
    ),
):
    """Assess specification quality with automated scoring.

    Analyzes specification files across multiple quality dimensions:
    - Completeness: Required sections present
    - Clarity: Vague terms, passive voice, measurable criteria
    - Traceability: Requirements → plan → tasks linkage
    - Constitutional: Project conventions and tool usage
    - Ambiguity: TBD/TODO markers and uncertainty

    Returns a 0-100 score with detailed recommendations.
    """
    from pathlib import Path
    import json as json_lib
    from rich.table import Table

    from specify_cli.quality import QualityScorer, QualityConfig

    # Determine spec path
    if spec_path is None:
        spec_file = Path.cwd() / ".specify" / "spec.md"
        if not spec_file.exists():
            # Try current directory
            spec_file = Path.cwd() / "spec.md"
    else:
        spec_file = Path(spec_path)

    if not spec_file.exists():
        console.print(f"[red]Error: Specification file not found: {spec_file}[/red]")
        console.print("\nUsage:")
        console.print("  specify quality [SPEC_PATH]")
        console.print("  specify quality .specify/spec.md")
        raise typer.Exit(1)

    # Load configuration
    if config_path:
        config = QualityConfig.load_from_file(Path(config_path))
    else:
        config = QualityConfig.find_config(spec_file.parent)

    # Override threshold if provided
    if threshold is not None:
        config.passing_threshold = threshold

    # Create scorer and assess
    try:
        scorer = QualityScorer(config)
        result = scorer.score_spec(spec_file)
    except Exception as e:
        console.print(f"[red]Error assessing quality: {e}[/red]")
        raise typer.Exit(1)

    # Output results
    if json_output:
        # JSON output
        output = {
            "overall_score": result.overall_score,
            "passing": result.passes(),
            "excellent": result.is_excellent(),
            "dimensions": {
                "completeness": {
                    "score": result.completeness.score,
                    "findings": result.completeness.findings,
                },
                "clarity": {
                    "score": result.clarity.score,
                    "findings": result.clarity.findings,
                },
                "traceability": {
                    "score": result.traceability.score,
                    "findings": result.traceability.findings,
                },
                "constitutional": {
                    "score": result.constitutional.score,
                    "findings": result.constitutional.findings,
                },
                "ambiguity": {
                    "score": result.ambiguity.score,
                    "findings": result.ambiguity.findings,
                },
            },
            "recommendations": result.get_recommendations(),
        }
        console.print(json_lib.dumps(output, indent=2))
    else:
        # Rich table output
        show_banner()
        console.print(f"\n[bold]Quality Assessment:[/bold] {spec_file}\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Dimension", style="cyan", width=20)
        table.add_column("Score", justify="right", width=10)
        table.add_column("Findings", width=50)

        # Add dimension rows
        dimensions = [
            ("Completeness", result.completeness),
            ("Clarity", result.clarity),
            ("Traceability", result.traceability),
            ("Constitutional", result.constitutional),
            ("Ambiguity", result.ambiguity),
        ]

        for name, assessment in dimensions:
            score_str = f"{assessment.score:.0f}/100"
            findings_str = "\n".join(assessment.findings[:3])  # First 3 findings

            # Color code score
            if assessment.score >= 90:
                score_color = "green"
            elif assessment.score >= 70:
                score_color = "yellow"
            else:
                score_color = "red"

            table.add_row(
                name, f"[{score_color}]{score_str}[/{score_color}]", findings_str
            )

        # Add separator and overall
        table.add_section()

        overall_str = f"{result.overall_score:.0f}/100"
        if result.is_excellent():
            status = "[green]EXCELLENT ✓✓[/green]"
            overall_color = "green"
        elif result.passes():
            status = "[green]PASSING ✓[/green]"
            overall_color = "yellow"
        else:
            status = "[red]NEEDS IMPROVEMENT ✗[/red]"
            overall_color = "red"

        table.add_row(
            "[bold]OVERALL[/bold]",
            f"[bold {overall_color}]{overall_str}[/bold {overall_color}]",
            status,
        )

        console.print(table)

        # Show recommendations
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(result.get_recommendations(), 1):
            console.print(f"  {i}. {rec}")

        console.print()

    # Exit with status code if check-only
    if check_only:
        effective_threshold = (
            threshold if threshold is not None else config.passing_threshold
        )
        if not result.passes(threshold):
            console.print(
                f"[red]Quality check failed: {result.overall_score:.0f} < {effective_threshold}[/red]"
            )
            raise typer.Exit(1)
        else:
            console.print(
                f"[green]Quality check passed: {result.overall_score:.0f} >= {effective_threshold}[/green]"
            )
            raise typer.Exit(0)


@app.command()
def gate(
    threshold: int = typer.Option(
        None, "--threshold", help="Override minimum quality score (default: 70)"
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass gate even if quality check fails"
    ),
):
    """Pre-implementation quality gate.

    Validates spec quality before implementation begins.
    Exit codes: 0=passed, 1=failed, 2=error

    This command is designed to be run before starting implementation
    (e.g., in CI/CD pipelines or as part of /jpspec:implement workflow).

    Example usage:
        specify gate                    # Check with default threshold (70)
        specify gate --threshold 80     # Custom threshold
        specify gate --force            # Bypass failed gate (not recommended)
    """
    from pathlib import Path
    from specify_cli.quality import QualityScorer, QualityConfig

    project_root = Path.cwd()
    spec_path = project_root / ".specify" / "spec.md"

    if not spec_path.exists():
        console.print("[red]Error:[/red] No spec.md found at .specify/spec.md")
        raise typer.Exit(2)

    # Load config and override threshold if provided
    config = QualityConfig.find_config(project_root / ".specify")
    min_threshold = threshold if threshold is not None else config.passing_threshold

    console.print("🔍 Running pre-implementation quality gate...\n")

    # Run quality assessment
    try:
        scorer = QualityScorer(config)
        result = scorer.score_spec(spec_path)
    except Exception as e:
        console.print(f"[red]Error during quality assessment: {e}[/red]")
        raise typer.Exit(2)

    overall_score = result.overall_score
    passed = overall_score >= min_threshold

    # Display result
    if passed:
        console.print(
            f"Quality Score: [green]{overall_score:.0f}/100[/green] ✅ PASSED\n"
        )
        console.print("[green]Proceeding with implementation...[/green]")
        raise typer.Exit(0)
    else:
        console.print(
            f"Quality Score: [red]{overall_score:.0f}/100[/red] ❌ FAILED (minimum: {min_threshold})\n"
        )

        # Show top 5 recommendations
        recommendations = result.get_recommendations()
        if recommendations:
            console.print("[yellow]Recommendations:[/yellow]")
            for rec in recommendations[:5]:
                console.print(f"  • {rec}")
            console.print()

        if force:
            console.print(
                "[yellow]⚠️  Bypassing gate with --force (not recommended)[/yellow]"
            )
            raise typer.Exit(0)
        else:
            console.print("[dim]Run with --force to bypass (not recommended)[/dim]")
            raise typer.Exit(1)


@app.command(name="ac-coverage")
def ac_coverage_command(
    feature: str = typer.Option(
        None,
        "--feature",
        "-f",
        help="Feature name (defaults to current feature from context)",
    ),
    prd_path: str = typer.Option(
        None,
        "--prd",
        help="Path to PRD file (defaults to docs/prd/{feature}.md)",
    ),
    test_dirs: str = typer.Option(
        "tests",
        "--test-dirs",
        help="Comma-separated list of test directories",
    ),
    output: str = typer.Option(
        "tests/ac-coverage.json",
        "--output",
        "-o",
        help="Output path for coverage report",
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Check coverage and exit with error if not 100%",
    ),
    allow_partial_coverage: bool = typer.Option(
        False,
        "--allow-partial-coverage",
        help="Allow partial coverage (for exceptional cases)",
    ),
):
    """Generate acceptance criteria test coverage report.

    Scans PRD for acceptance criteria and checks that all have
    corresponding test markers (@pytest.mark.ac).

    Examples:
        specify ac-coverage --check
        specify ac-coverage --feature auth --output coverage.json
        specify ac-coverage --allow-partial-coverage
    """
    from pathlib import Path

    from specify_cli.workflow.ac_coverage import (
        generate_coverage_report,
        validate_ac_coverage,
    )

    # Determine feature name
    if not feature:
        from specify_cli.task_context import TaskContext

        try:
            context = TaskContext.detect()
            feature = context.feature_name
        except Exception:
            console.print(
                "[red]Error:[/red] Could not detect feature name. Use --feature option."
            )
            raise typer.Exit(1)

    # Determine PRD path
    if not prd_path:
        prd_path = f"docs/prd/{feature}.md"

    prd_file = Path(prd_path)
    if not prd_file.exists():
        console.print(f"[red]Error:[/red] PRD not found: {prd_path}")
        raise typer.Exit(1)

    # Parse test directories
    test_dir_list = [Path(d.strip()) for d in test_dirs.split(",")]

    # Generate coverage report
    console.print(f"[cyan]Scanning PRD:[/cyan] {prd_path}")
    console.print(
        f"[cyan]Test directories:[/cyan] {', '.join(str(d) for d in test_dir_list)}"
    )
    console.print()

    try:
        report = generate_coverage_report(
            feature=feature,
            prd_path=prd_file,
            test_dirs=test_dir_list,
        )
    except Exception as e:
        console.print(f"[red]Error generating coverage report:[/red] {e}")
        raise typer.Exit(1)

    # Save report
    output_path = Path(output)
    report.save(output_path)
    console.print(f"[green]✓[/green] Coverage report saved: {output_path}")
    console.print()

    # Display summary
    summary = report.summary
    console.print("[bold]Coverage Summary:[/bold]")
    console.print(f"  Total ACs: {summary.total_acs}")
    console.print(f"  Covered: {summary.covered}")
    console.print(f"  Uncovered: {summary.uncovered}")

    # Color code coverage percentage
    coverage_color = "green" if summary.coverage_percent >= 100.0 else "yellow"
    if summary.coverage_percent < 50.0:
        coverage_color = "red"

    console.print(
        f"  Coverage: [{coverage_color}]{summary.coverage_percent:.1f}%[/{coverage_color}]"
    )
    console.print()

    # Show uncovered ACs if any
    if summary.uncovered > 0:
        console.print("[yellow]Uncovered acceptance criteria:[/yellow]")
        for ac in report.get_uncovered_acs():
            console.print(f"  - [dim]{ac.id}:[/dim] {ac.description}")
        console.print()

        console.print("[dim]To fix:[/dim]")
        console.print('  1. Add @pytest.mark.ac("ACX: Description") to test functions')
        console.print("  2. Ensure tests are in configured test directories")
        console.print("  3. Run: specify ac-coverage --check")
        console.print()

    # Validate coverage if --check flag is set
    if check:
        is_valid, error_msg = validate_ac_coverage(report, allow_partial_coverage)
        if not is_valid:
            console.print("[red]✗ Coverage check failed[/red]")
            console.print()
            console.print(error_msg)
            raise typer.Exit(1)

        console.print("[green]✓ All acceptance criteria are covered by tests[/green]")


# Workflow subcommand
workflow_app = typer.Typer(
    name="workflow",
    help="Validate workflow configuration files",
    add_completion=False,
)
app.add_typer(workflow_app, name="workflow")

# Hooks app (event emission and hook management)
from specify_cli.hooks.cli import hooks_app  # noqa: E402

app.add_typer(hooks_app, name="hooks")


# Security scanning sub-app
security_app = typer.Typer(
    name="security",
    help="Security scanning commands",
    add_completion=False,
)
app.add_typer(security_app, name="security")


@security_app.command("scan")
def security_scan(
    target: Path = typer.Argument(
        Path("."),
        help="Directory or file to scan",
        exists=True,
    ),
    tool: list[str] = typer.Option(
        ["semgrep"],
        "--tool",
        "-t",
        help="Scanner(s) to use (semgrep, etc)",
    ),
    config: str = typer.Option(
        "auto",
        "--config",
        "-c",
        help="Scanner config to use",
    ),
    fail_on: str = typer.Option(
        "high",
        "--fail-on",
        help="Fail on severity threshold (critical|high|medium|low|info)",
    ),
    format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="Output format (text|json|sarif)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file (defaults to stdout)",
    ),
):
    """Run security scan on target directory.

    This command scans your code for security vulnerabilities using
    configured security scanners (e.g., Semgrep).

    Exit codes:
    - 0: No findings at or above fail-on threshold
    - 1: Findings found at or above fail-on threshold
    - 2: Error during scan

    Examples:
        specify security scan                           # Scan current directory
        specify security scan /path/to/code             # Scan specific path
        specify security scan --tool semgrep            # Specify scanner
        specify security scan --fail-on critical        # Fail only on critical
        specify security scan --format json -o out.json # JSON output to file
    """
    import json
    from specify_cli.security.orchestrator import ScannerOrchestrator
    from specify_cli.security.adapters.semgrep import SemgrepAdapter
    from specify_cli.security.exporters.sarif import SARIFExporter
    from specify_cli.security.exporters.json import JSONExporter
    from specify_cli.security.exporters.markdown import MarkdownExporter
    from specify_cli.security.models import Severity

    # Validate fail-on severity
    try:
        fail_severity = Severity(fail_on.lower())
    except ValueError:
        console.print(
            f"[red]Invalid severity level: {fail_on}[/red]",
        )
        console.print(
            "Valid levels: critical, high, medium, low, info",
        )
        raise typer.Exit(2)

    # Initialize orchestrator
    orchestrator = ScannerOrchestrator()

    # Register scanners based on --tool flags
    scanner_map = {
        "semgrep": SemgrepAdapter,
    }

    for tool_name in tool:
        if tool_name not in scanner_map:
            console.print(
                f"[yellow]⚠ Unknown scanner: {tool_name}[/yellow]",
            )
            continue

        adapter_class = scanner_map[tool_name]
        adapter = adapter_class()

        # Check tool availability
        if not adapter.is_available():
            console.print(
                f"[yellow]⚠ {adapter.name} not available[/yellow]",
            )
            console.print(adapter.get_install_instructions())
            raise typer.Exit(2)

        orchestrator.register(adapter)

    if not orchestrator.list_scanners():
        console.print("[red]No scanners available[/red]")
        raise typer.Exit(2)

    # Build scanner config
    scanner_config = {}
    if config != "auto":
        # Parse config as JSON or file path
        try:
            scanner_config = json.loads(config)
        except json.JSONDecodeError:
            # Try as file path
            config_path = Path(config)
            if config_path.exists():
                scanner_config = json.loads(config_path.read_text())
            else:
                console.print(f"[red]Invalid config: {config}[/red]")
                raise typer.Exit(2)

    # Run scan with progress indicator
    try:
        with console.status(
            "[bold blue]Scanning for security vulnerabilities...[/bold blue]"
        ):
            findings = orchestrator.scan(
                target=target,
                scanners=tool,
                deduplicate=True,
                config=scanner_config,
            )
    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")
        raise typer.Exit(2)

    # Output results based on format
    if format == "sarif":
        exporter = SARIFExporter()
        result = exporter.export(findings)  # Returns dict
        output_text = json.dumps(result, indent=2)

        if output:
            output.write_text(output_text)
            console.print(f"[green]✓ SARIF output written to {output}[/green]")
        else:
            console.print_json(data=result)

    elif format == "json":
        exporter = JSONExporter(pretty=True)
        result = exporter.export_dict(findings)  # Returns dict
        output_text = json.dumps(result, indent=2)

        if output:
            output.write_text(output_text)
            console.print(f"[green]✓ JSON output written to {output}[/green]")
        else:
            console.print_json(data=result)

    else:
        # Text format with table
        _print_findings_table(console, findings)

        if output:
            # Export as markdown for text format
            exporter = MarkdownExporter()
            markdown = exporter.export(findings)
            output.write_text(markdown)
            console.print(f"\n[green]✓ Markdown report written to {output}[/green]")

    # Determine exit code based on fail_on threshold
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }

    has_failures = any(
        severity_order[f.severity] <= severity_order[fail_severity] for f in findings
    )

    if has_failures:
        failing_count = sum(
            1
            for f in findings
            if severity_order[f.severity] <= severity_order[fail_severity]
        )
        console.print(
            f"\n[red]✗ Found {failing_count} findings at or above {fail_on} severity[/red]"
        )
        raise typer.Exit(1)
    elif findings:
        console.print(
            f"\n[yellow]Found {len(findings)} findings below {fail_on} threshold[/yellow]"
        )
        raise typer.Exit(0)
    else:
        console.print("\n[green]✓ No security issues found[/green]")
        raise typer.Exit(0)


def _print_findings_table(console: Console, findings: list) -> None:
    """Print findings as a rich table.

    Args:
        console: Rich console for output
        findings: List of Finding objects to display
    """
    if not findings:
        console.print("[green]✓ No security issues found[/green]")
        return

    from rich.table import Table

    table = Table(title="Security Findings", show_lines=False)
    table.add_column("Severity", style="bold", width=10)
    table.add_column("Title", style="", width=40)
    table.add_column("Location", style="cyan", width=30)
    table.add_column("CWE", style="dim", width=10)

    severity_colors = {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "blue",
        "info": "dim",
    }

    for f in findings:
        color = severity_colors.get(f.severity.value, "white")
        title_text = f.title[:40] + "..." if len(f.title) > 40 else f.title
        location_text = f"{f.location.file.name}:{f.location.line_start}"

        table.add_row(
            f"[{color}]{f.severity.value.upper()}[/{color}]",
            title_text,
            location_text,
            f.cwe_id or "-",
        )

    console.print()
    console.print(table)
    console.print(f"\nTotal: {len(findings)} findings")


@security_app.command("triage")
def security_triage(
    findings_file: Path = typer.Argument(
        ...,
        help="Findings JSON file to triage",
        exists=True,
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="Interactive triage mode",
    ),
    min_severity: str = typer.Option(
        "low",
        "--min-severity",
        help="Minimum severity to show (critical|high|medium|low|info)",
    ),
):
    """AI-assisted triage of security findings.

    This command helps you triage security findings with AI assistance.
    (Currently a placeholder for future implementation)

    Examples:
        specify security triage findings.json
        specify security triage findings.json --min-severity high
    """
    console.print("[yellow]Triage command coming in Phase 2[/yellow]")
    console.print(f"Would triage: {findings_file}")
    console.print(f"Interactive: {interactive}, Min severity: {min_severity}")


@security_app.command("fix")
def security_fix(
    finding_id: Optional[str] = typer.Argument(
        None,
        help="Finding ID to fix",
    ),
    apply: bool = typer.Option(
        False,
        "--apply",
        help="Apply fix automatically",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run",
        help="Show fix without applying",
    ),
):
    """Generate and optionally apply security fixes.

    This command generates fixes for security findings with AI assistance.
    (Currently a placeholder for future implementation)

    Examples:
        specify security fix SEMGREP-001 --dry-run
        specify security fix SEMGREP-001 --apply
    """
    console.print("[yellow]Fix command coming in Phase 2[/yellow]")
    if finding_id:
        console.print(f"Would fix: {finding_id}")
        console.print(f"Apply: {apply}, Dry run: {dry_run}")
    else:
        console.print("No finding ID provided")


@security_app.command("audit")
def security_audit(
    target: Path = typer.Argument(
        Path("."),
        help="Directory to audit",
        exists=True,
    ),
    format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Report format (markdown|html|json)",
    ),
    compliance: Optional[str] = typer.Option(
        None,
        "--compliance",
        help="Compliance framework (owasp|pci|hipaa)",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file",
    ),
):
    """Generate security audit report.

    This command generates a comprehensive security audit report.
    (Currently a placeholder for future implementation)

    Examples:
        specify security audit
        specify security audit --format html --output audit.html
        specify security audit --compliance owasp
    """
    console.print("[yellow]Audit command coming in Phase 2[/yellow]")
    console.print(f"Would audit: {target}")
    console.print(f"Format: {format}, Compliance: {compliance}")
    if output:
        console.print(f"Output: {output}")


@workflow_app.command("validate")
def workflow_validate(
    file: Optional[str] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to workflow config file (defaults to jpspec_workflow.yml in standard locations)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation output",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format (for CI/automation)",
    ),
):
    """Validate workflow configuration file.

    Validates jpspec_workflow.yml against:
    1. JSON schema (structural validation)
    2. Semantic validation (circular dependencies, reachability, etc.)

    Exit codes:
    - 0: Validation passed (warnings are non-blocking)
    - 1: Validation errors (schema or semantic)
    - 2: File errors (not found, invalid YAML)

    Examples:
        specify workflow validate                    # Validate default config
        specify workflow validate --file custom.yml  # Validate custom config
        specify workflow validate --verbose          # Show detailed output
        specify workflow validate --json             # JSON output for CI
    """
    import json
    from pathlib import Path

    from specify_cli.workflow.config import WorkflowConfig
    from specify_cli.workflow.exceptions import (
        WorkflowConfigError,
        WorkflowConfigNotFoundError,
        WorkflowConfigValidationError,
    )
    from specify_cli.workflow.validator import WorkflowValidator

    # Track results for JSON output
    json_result = {
        "valid": False,
        "config_file": None,
        "schema_validation": {"passed": False, "error": None},
        "semantic_validation": {"passed": False, "errors": [], "warnings": []},
    }

    # Human-readable output (unless --json)
    if not json_output:
        console.print("[cyan]Validating workflow configuration...[/cyan]\n")

    # Load and validate config
    try:
        if file:
            config = WorkflowConfig.load(path=Path(file), validate=True, cache=False)
        else:
            config = WorkflowConfig.load(validate=True, cache=False)

        json_result["config_file"] = str(config.config_path)
        json_result["schema_validation"]["passed"] = True

        if not json_output:
            console.print("[green]✓[/green] Schema validation passed")
            if verbose:
                console.print(f"  Config file: {config.config_path}")
                console.print(f"  Version: {config.version}")
                console.print(f"  States: {len(config.states)}")
                console.print(f"  Workflows: {len(config.workflows)}")
                console.print()

    except WorkflowConfigNotFoundError as e:
        json_result["schema_validation"]["error"] = {
            "type": "file_not_found",
            "message": e.message,
            "path": e.path,
            "searched_paths": e.searched_paths,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Config file not found:[/red] {e.path}")
            if e.searched_paths:
                console.print("[dim]Searched paths:[/dim]")
                for path in e.searched_paths:
                    console.print(f"  [dim]- {path}[/dim]")
        raise typer.Exit(2)

    except WorkflowConfigValidationError as e:
        json_result["schema_validation"]["error"] = {
            "type": "schema_validation",
            "message": e.message,
            "errors": e.errors,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Schema validation failed:[/red] {e.message}")
            if e.errors:
                for err in e.errors:
                    console.print(f"  [red]•[/red] {err}")
        raise typer.Exit(1)

    except WorkflowConfigError as e:
        json_result["schema_validation"]["error"] = {
            "type": "config_error",
            "message": str(e),
            "details": e.details,
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Config error:[/red] {e}")
        raise typer.Exit(2)

    except Exception as e:
        json_result["schema_validation"]["error"] = {
            "type": "unexpected_error",
            "message": str(e),
        }
        if json_output:
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]✗ Unexpected error:[/red] {e}")
        raise typer.Exit(2)

    # Run semantic validation
    if not json_output:
        console.print("[cyan]Running semantic validation...[/cyan]\n")

    validator = WorkflowValidator(config._data)
    result = validator.validate()

    # Populate JSON result with semantic validation data
    json_result["semantic_validation"]["passed"] = result.is_valid
    json_result["semantic_validation"]["errors"] = [
        {"code": e.code, "message": e.message, "context": e.context}
        for e in result.errors
    ]
    json_result["semantic_validation"]["warnings"] = [
        {"code": w.code, "message": w.message, "context": w.context}
        for w in result.warnings
    ]
    json_result["valid"] = result.is_valid

    # JSON output mode (use print() to avoid Rich formatting)
    if json_output:
        print(json.dumps(json_result, indent=2))
        raise typer.Exit(0 if result.is_valid else 1)

    # Human-readable output
    if result.is_valid:
        console.print(
            "[bold green]✓ Validation passed: workflow configuration is valid[/bold green]"
        )

        if verbose and result.warnings:
            console.print(f"\n[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning.message}")

        raise typer.Exit(0)
    else:
        console.print(
            f"[bold red]✗ Validation failed: {len(result.errors)} errors found[/bold red]\n"
        )

        # Display errors
        for error in result.errors:
            console.print(f"[red]ERROR [{error.code}]:[/red] {error.message}")
            if verbose and error.context:
                console.print(f"  [dim]Context: {error.context}[/dim]")
            console.print()

        # Display warnings if verbose
        if verbose and result.warnings:
            console.print(f"[yellow]Warnings ({len(result.warnings)}):[/yellow]")
            for warning in result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning.message}")
            console.print()

        console.print("[dim]Fix the errors above and run validation again.[/dim]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
