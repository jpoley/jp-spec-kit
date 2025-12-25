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

    Currently, templates are expected to live in the source repository
    at the top-level templates/skills/ path (for development mode and
    local usage).

    Returns:
        Path to templates/skills directory, or None if not found.
    """
    # Look for templates in source repo structure
    # This handles development mode where templates are at repo root.
    # Note: templates/ is not packaged with flowspec_cli, so we do not
    # use importlib.resources here.
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
            "Skills templates directory not found. "
            "This may indicate an installation issue if running from a package."
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

        try:
            shutil.copytree(skill_dir, dest_skill_dir)
        except OSError as exc:
            raise RuntimeError(
                f"Failed to copy skill directory '{skill_dir}' to '{dest_skill_dir}'. "
                "Please check file permissions, available disk space, and whether any "
                "files are in use."
            ) from exc
        deployed.append(dest_skill_dir)

    return deployed


__all__ = ["deploy_skills"]
