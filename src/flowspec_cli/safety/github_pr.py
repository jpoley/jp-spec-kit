"""GitHub PR Safety configuration for Claude Code hooks.

This module handles configuration for GitHub PR safety guards that prevent
Claude from performing destructive PR operations like merging or updating PRs.

Configuration file: .flowspec/github-pr-safety.json

GitHub Copilot Equivalent:
- Repository branch protection rules via Settings > Rules > Rulesets
- Copilot Automatic Code Review can block merges at repository level
- Unlike Claude hooks, Copilot operates server-side at repository level
"""

import json
import sys
from pathlib import Path

# Default configuration - secure by default
GITHUB_PR_SAFETY_DEFAULTS = {
    "block_pr_merge": True,
    "block_pr_merge_to_main": True,
    "block_pr_updates": True,
}

# Configuration file path relative to project root
CONFIG_FILE = ".flowspec/github-pr-safety.json"


def get_config_path(project_root: Path) -> Path:
    """Get the path to the GitHub PR safety configuration file."""
    return project_root / CONFIG_FILE


def has_github_pr_safety_config(project_root: Path) -> bool:
    """Check if GitHub PR safety configuration exists.

    Args:
        project_root: Root directory of the project

    Returns:
        True if configuration file exists
    """
    return get_config_path(project_root).exists()


def get_github_pr_safety_config(project_root: Path) -> dict:
    """Load GitHub PR safety configuration.

    Args:
        project_root: Root directory of the project

    Returns:
        Configuration dictionary, or defaults if file doesn't exist
    """
    config_path = get_config_path(project_root)

    if not config_path.exists():
        return GITHUB_PR_SAFETY_DEFAULTS.copy()

    try:
        with open(config_path) as f:
            config = json.load(f)
            # Merge with defaults for any missing keys
            result = GITHUB_PR_SAFETY_DEFAULTS.copy()
            result.update(config)
            return result
    except (json.JSONDecodeError, IOError):
        return GITHUB_PR_SAFETY_DEFAULTS.copy()


def configure_github_pr_safety(
    project_root: Path,
    block_pr_merge: bool = True,
    block_pr_merge_to_main: bool = True,
    block_pr_updates: bool = True,
) -> Path:
    """Write GitHub PR safety configuration to file.

    Args:
        project_root: Root directory of the project
        block_pr_merge: Block all PR merge operations
        block_pr_merge_to_main: Block merges to main/master branches
        block_pr_updates: Block PR update operations

    Returns:
        Path to the created configuration file
    """
    config_path = get_config_path(project_root)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "_comment": "GitHub PR Safety Configuration for Claude Code hooks",
        "_docs": "See .claude/hooks/pre-tool-use-github-pr-safety.py for details",
        "block_pr_merge": block_pr_merge,
        "block_pr_merge_to_main": block_pr_merge_to_main,
        "block_pr_updates": block_pr_updates,
    }

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return config_path


def resolve_pr_safety_settings(
    block_pr_merge: bool | None,
    block_pr_updates: bool | None,
    no_prompts: bool,
    console=None,
    prompt_func=None,
) -> tuple[bool, bool]:
    """Resolve PR safety settings from CLI flags, prompts, or defaults.

    This function handles the logic for determining PR safety settings,
    consolidating duplicated code from init and upgrade_repo commands.

    Args:
        block_pr_merge: CLI flag value (None if not provided)
        block_pr_updates: CLI flag value (None if not provided)
        no_prompts: If True, skip prompts and use secure defaults
        console: Rich console for output (required if prompting)
        prompt_func: Function to call for interactive prompts (optional override)

    Returns:
        Tuple of (block_pr_merge, block_pr_updates) settings
    """
    pr_merge_setting = block_pr_merge
    pr_updates_setting = block_pr_updates

    # If both settings are already provided, return them directly
    if pr_merge_setting is not None and pr_updates_setting is not None:
        return pr_merge_setting, pr_updates_setting

    # Need to resolve missing settings
    if no_prompts:
        # Use secure defaults for missing values
        pr_merge_setting = True if pr_merge_setting is None else pr_merge_setting
        pr_updates_setting = True if pr_updates_setting is None else pr_updates_setting
    elif sys.stdin.isatty() and console is not None:
        # Interactive mode - prompt for missing values
        actual_prompt_func = prompt_func or prompt_github_pr_safety
        pr_merge_prompt, pr_updates_prompt = actual_prompt_func(
            console,
            default_block_merge=True,
            default_block_updates=True,
        )
        pr_merge_setting = (
            pr_merge_setting if pr_merge_setting is not None else pr_merge_prompt
        )
        pr_updates_setting = (
            pr_updates_setting if pr_updates_setting is not None else pr_updates_prompt
        )
    else:
        # Non-interactive: use secure defaults
        pr_merge_setting = True if pr_merge_setting is None else pr_merge_setting
        pr_updates_setting = True if pr_updates_setting is None else pr_updates_setting

    return pr_merge_setting, pr_updates_setting


def prompt_github_pr_safety(
    console, default_block_merge: bool = True, default_block_updates: bool = True
) -> tuple[bool, bool]:
    """Interactive prompts for GitHub PR safety configuration.

    Args:
        console: Rich console for output
        default_block_merge: Default value for blocking PR merges
        default_block_updates: Default value for blocking PR updates

    Returns:
        Tuple of (block_pr_merge, block_pr_updates)
    """
    import typer

    console.print()
    console.print("[cyan]GitHub PR Safety Configuration[/cyan]")
    console.print()
    console.print(
        "Claude Code can perform GitHub operations via MCP tools. These settings\n"
        "control which PR operations Claude is allowed to perform.\n"
    )

    # Only prompt if in interactive mode
    if not sys.stdin.isatty():
        return default_block_merge, default_block_updates

    console.print(
        "[dim]GitHub Copilot equivalent: Repository branch protection rules[/dim]"
    )
    console.print()

    # Prompt for blocking PR merges
    console.print(
        "[yellow]Block PR Merges:[/yellow] Prevents Claude from merging pull requests."
    )
    console.print(
        "  This is the safest option - merges should typically be done by humans."
    )
    block_merge = typer.confirm(
        "Block Claude from merging PRs?",
        default=default_block_merge,
    )

    console.print()

    # Prompt for blocking PR updates
    console.print(
        "[yellow]Block PR Updates:[/yellow] Prevents Claude from updating PRs "
        "(branch updates, reviews, issue updates)."
    )
    console.print(
        "  Enable this to ensure all PR modifications go through human review."
    )
    block_updates = typer.confirm(
        "Block Claude from updating PRs?",
        default=default_block_updates,
    )

    return block_merge, block_updates
