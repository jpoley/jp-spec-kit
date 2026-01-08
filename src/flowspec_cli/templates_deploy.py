"""Local template deployment for standalone flowspec.

This module provides functions to deploy templates from the bundled
package directory to a project, instead of downloading from GitHub.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_bundled_templates_dir() -> Optional[Path]:
    """Get the path to the bundled templates directory.

    Returns:
        Path to templates directory if found, None otherwise.
    """
    # Templates are bundled in the package at flowspec_cli/templates/
    templates_dir = Path(__file__).parent / "templates"
    if templates_dir.exists() and templates_dir.is_dir():
        return templates_dir
    return None


def deploy_local_templates(
    project_path: Path,
    ai_assistants: list[str],
    script_type: str,
    *,
    force: bool = False,
    verbose: bool = True,
    tracker=None,
) -> Path:
    """Deploy templates from bundled package to project directory.

    This is the standalone alternative to download_and_extract_two_stage().
    Templates are copied directly from the installed package.

    Args:
        project_path: Target project directory
        ai_assistants: List of AI assistants to configure
        script_type: Script type (sh or ps)
        force: If True, overwrite existing files
        verbose: If True, print progress messages
        tracker: Optional StepTracker for progress reporting

    Returns:
        Path to the project directory

    Raises:
        RuntimeError: If templates are not found in package
    """
    templates_dir = get_bundled_templates_dir()
    if templates_dir is None:
        raise RuntimeError(
            "Bundled templates not found. This may indicate a packaging issue.\n"
            "Please reinstall flowspec or use --branch to install from source."
        )

    # Ensure project directory exists
    project_path.mkdir(parents=True, exist_ok=True)

    if tracker:
        tracker.start("fetch-base", "locating bundled templates")

    # Copy base templates (everything except agent-specific directories)
    _copy_templates(
        templates_dir,
        project_path,
        exclude_dirs={".git", "__pycache__", "agents"},
        force=force,
    )

    if tracker:
        tracker.complete("fetch-base", "bundled templates found")
        tracker.start("fetch-extension", "configuring agent templates")

    # Copy agent-specific templates for each selected agent
    agents_dir = templates_dir / "agents"
    if agents_dir.exists():
        for agent in ai_assistants:
            agent_template = agents_dir / agent
            if agent_template.exists():
                # Deploy agent-specific files to appropriate locations
                _deploy_agent_templates(agent_template, project_path, agent)

    if tracker:
        tracker.complete("fetch-extension", f"configured {len(ai_assistants)} agent(s)")
        tracker.start("extract-base", "copying templates")

    # Mark extraction steps complete (no actual extraction needed for local)
    if tracker:
        tracker.complete("extract-base", "templates copied")
        tracker.start("extract-extension", "finalizing")
        tracker.complete("extract-extension", "complete")
        tracker.start("merge", "merging templates")
        tracker.complete("merge", "done")

    return project_path


def _copy_templates(
    src_dir: Path,
    dest_dir: Path,
    exclude_dirs: set[str] | None = None,
    force: bool = False,
):
    """Copy templates from source to destination.

    Args:
        src_dir: Source templates directory
        dest_dir: Destination project directory
        exclude_dirs: Set of directory names to exclude
        force: If True, overwrite existing files
    """
    if exclude_dirs is None:
        exclude_dirs = set()

    for item in src_dir.iterdir():
        if item.name in exclude_dirs:
            continue

        dest_item = dest_dir / item.name

        if item.is_file():
            if dest_item.exists() and not force:
                continue
            shutil.copy2(item, dest_item)

        elif item.is_dir():
            if dest_item.exists():
                # Merge directories - recursively copy contents
                _copy_templates(item, dest_item, exclude_dirs, force)
            else:
                shutil.copytree(item, dest_item)


def _deploy_agent_templates(
    agent_template_dir: Path,
    project_path: Path,
    agent: str,
):
    """Deploy agent-specific templates.

    Agent templates may contain:
    - .claude/ directory for Claude-specific configs
    - .github/ directory for Copilot-specific configs
    - Other agent-specific files

    Args:
        agent_template_dir: Source agent template directory
        project_path: Target project directory
        agent: Agent name (e.g., 'claude', 'copilot')
    """
    if not agent_template_dir.exists():
        return

    # Copy agent-specific templates, merging with existing directories
    for item in agent_template_dir.iterdir():
        dest_item = project_path / item.name

        if item.is_file():
            shutil.copy2(item, dest_item)
        elif item.is_dir():
            if dest_item.exists():
                # Merge directories
                _merge_directories(item, dest_item)
            else:
                shutil.copytree(item, dest_item)


def _merge_directories(src_dir: Path, dest_dir: Path):
    """Merge source directory into destination, preserving existing files.

    Args:
        src_dir: Source directory
        dest_dir: Destination directory
    """
    for item in src_dir.iterdir():
        dest_item = dest_dir / item.name

        if item.is_file():
            # Overwrite files from source
            shutil.copy2(item, dest_item)
        elif item.is_dir():
            if dest_item.exists():
                _merge_directories(item, dest_item)
            else:
                shutil.copytree(item, dest_item)


def is_templates_bundled() -> bool:
    """Check if templates are bundled with this installation.

    Returns:
        True if bundled templates are available, False otherwise.
    """
    return get_bundled_templates_dir() is not None
