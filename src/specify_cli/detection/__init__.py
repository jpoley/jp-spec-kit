"""Project detection module for Specify CLI."""

from .project_detector import (
    ProjectDetector,
    is_existing_project,
    has_constitution,
)

__all__ = [
    "ProjectDetector",
    "is_existing_project",
    "has_constitution",
]
