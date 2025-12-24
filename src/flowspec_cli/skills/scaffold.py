"""Skill deployment for flowspec init.

This module provides skill directory copying functionality
that deploys skills from templates/skills/ to .claude/skills/
when users run `flowspec init`.
"""

from __future__ import annotations

import shutil
from pathlib import Path


def _find_templates_skills_dir() -> Path | None:
    """Locate the templates/skills directory.

    Tries multiple locations:
    1. Package resources (for installed flowspec-cli)
    2. Source repo structure (for development mode)

    Returns:
        Path to templates/skills directory, or None if not found.
    """
    # Try package resources first (for installed flowspec-cli)
    # Note: We require Python 3.11+, so importlib.resources.files() is available
    try:
        import importlib.resources

        templates_ref = importlib.resources.files("flowspec_cli").joinpath(
            "templates/skills"
        )
        if templates_ref.is_dir():
            # For standard filesystem-based installations (pip install, editable installs),
            # the Traversable can be converted directly to a Path.
            # Note: This won't work for zip-packaged distributions, but flowspec
            # doesn't support that installation method currently.
            templates_path = Path(str(templates_ref))
            if templates_path.exists():
                return templates_path
    except (ImportError, AttributeError, TypeError, OSError):
        # importlib.resources may fail in various edge cases:
        # - Package not installed or malformed
        # - Running from unusual environment
        # - Path conversion failed for non-filesystem resources
        pass

    # Fallback: look for templates in source repo structure
    # This handles development mode where templates are at repo root
    src_dir = Path(__file__).parent.parent.parent.parent  # Go up to repo root
    potential_templates = src_dir / "templates" / "skills"
    if potential_templates.exists():
        return potential_templates

    return None


def deploy_skills(
    project_root: Path,
    *,
    force: bool = False,
    skip_skills: bool = False,
) -> list[Path]:
    """Deploy skills from templates/skills/ to .claude/skills/.

    Args:
        project_root: Root directory of the project
        force: If True, overwrite existing skills
        skip_skills: If True, skip skill deployment entirely

    Returns:
        List of paths to deployed skill directories
    """
    if skip_skills:
        return []

    templates_skills_dir = _find_templates_skills_dir()
    if templates_skills_dir is None:
        return []

    # Create .claude/skills directory
    skills_dir = project_root / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    deployed = []

    # Copy each skill directory from templates/skills/ to .claude/skills/
    for skill_dir in templates_skills_dir.iterdir():
        # Skip symlinks first - important because symlinks to directories
        # would pass is_dir() check. Example: context-extractor symlink
        # points back to .claude/skills, which we don't want to copy.
        if skill_dir.is_symlink():
            continue

        # Only process directories (non-symlinks already filtered above)
        if not skill_dir.is_dir():
            continue

        # Only process directories that contain SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        # Destination path
        dest_skill_dir = skills_dir / skill_dir.name

        # Check if skill already exists
        if dest_skill_dir.exists() and not force:
            # Skip existing skills unless --force
            continue

        # Copy skill directory
        if dest_skill_dir.exists():
            # Remove existing if force=True
            shutil.rmtree(dest_skill_dir)

        shutil.copytree(skill_dir, dest_skill_dir)
        deployed.append(dest_skill_dir)

    return deployed


__all__ = ["deploy_skills"]
