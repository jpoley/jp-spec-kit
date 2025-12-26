"""Skill deployment for flowspec init.

This module provides skill directory copying functionality
that deploys skills from templates/skills/ to .claude/skills/
when users run `flowspec init`.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _find_templates_skills_dir() -> Path | None:
    """Locate the templates/skills directory.

    Tries multiple locations:
    1. Package resources (for installed flowspec-cli)
    2. Source repo structure (for development mode)

    Returns:
        Path to templates/skills directory, or None if not found.
    """
    # Try package resources first (for installed flowspec-cli)
    # Note: We require Python 3.11+ (see pyproject.toml), so importlib.resources.files()
    # is available and preferred over the deprecated importlib_resources backport.
    # Security scanner warnings about Python 3.7 compatibility are false positives.
    try:
        import importlib.resources  # nosemgrep: python.lang.compatibility.python37.python37-compatibility-importlib2

        templates_ref = importlib.resources.files("flowspec_cli").joinpath(
            "templates/skills"
        )
        if templates_ref.is_dir():
            # For standard filesystem-based installations (pip install, editable installs),
            # the Traversable can be converted directly to a Path.
            #
            # Note on alternative approaches:
            # - importlib.resources.as_file() provides a context manager for safer access
            #   across package formats, but requires managing the context lifecycle.
            # - Path(str()) works for filesystem-based packages but not for zip archives.
            #
            # Flowspec currently only supports standard pip/editable installs (not
            # zipimport), so Path conversion is sufficient. If zip package support is
            # needed in the future, consider using as_file() with appropriate context
            # management.
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
        logger.warning(
            "Skills templates directory not found. This may indicate a missing or "
            "corrupted flowspec installation. Skills deployment skipped."
        )
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
            try:
                shutil.rmtree(dest_skill_dir)
            except OSError as exc:
                raise RuntimeError(
                    f"Failed to remove existing skill directory '{dest_skill_dir}'. "
                    "Please check file permissions and whether any files are in use."
                ) from exc

        shutil.copytree(skill_dir, dest_skill_dir)
        deployed.append(dest_skill_dir)

    return deployed


__all__ = ["deploy_skills"]
