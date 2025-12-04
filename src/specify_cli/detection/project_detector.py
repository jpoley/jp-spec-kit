"""
Project detection logic for Specify CLI.

This module detects whether a directory is an existing project
and whether it has a constitution configured.
"""

from pathlib import Path
from typing import List


# File markers that indicate an existing project
PROJECT_MARKERS: List[str] = [
    ".git",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "Makefile",
    "setup.py",
    "requirements.txt",
    "pom.xml",  # Maven
    "build.gradle",  # Gradle
    "Gemfile",  # Ruby
    "composer.json",  # PHP
]


class ProjectDetector:
    """Detects project characteristics for Specify CLI initialization."""

    def __init__(self, path: Path):
        """
        Initialize the project detector.

        Args:
            path: Path to the directory to check
        """
        self.path = path.resolve()

    def is_existing_project(self) -> bool:
        """
        Check if the directory is an existing project.

        Returns:
            True if any project markers are found, False otherwise
        """
        return is_existing_project(self.path)

    def has_constitution(self) -> bool:
        """
        Check if the project has a constitution file.

        Returns:
            True if memory/constitution.md exists, False otherwise
        """
        return has_constitution(self.path)

    def needs_constitution_prompt(self) -> bool:
        """
        Determine if user should be prompted to create a constitution.

        Returns:
            True if this is an existing project without a constitution
        """
        return self.is_existing_project() and not self.has_constitution()

    def get_detected_markers(self) -> List[str]:
        """
        Get list of detected project markers.

        Returns:
            List of marker filenames that were found
        """
        markers = []
        for marker in PROJECT_MARKERS:
            if (self.path / marker).exists():
                markers.append(marker)
        return markers


def is_existing_project(path: Path) -> bool:
    """
    Check if a directory is an existing project.

    Args:
        path: Path to check

    Returns:
        True if any project markers are found, False otherwise
    """
    return any((path / marker).exists() for marker in PROJECT_MARKERS)


def has_constitution(path: Path) -> bool:
    """
    Check if a project has a constitution file.

    Args:
        path: Path to check

    Returns:
        True if memory/constitution.md exists, False otherwise
    """
    constitution_path = path / "memory" / "constitution.md"
    return constitution_path.exists() and constitution_path.is_file()
