"""Logging configuration with dual-path resolution.

Determines whether we're in internal dev mode (working on flowspec itself)
or user project mode (using flowspec in another project), and routes logs
to the appropriate directories.
"""

import os
import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Markers that indicate we're in the flowspec repository itself
FLOWSPEC_REPO_MARKERS = frozenset(
    {
        "pyproject.toml",
        "src/flowspec_cli",
        ".flowspec",
    }
)


@dataclass(frozen=True)
class LoggingConfig:
    """Immutable logging configuration.

    Attributes:
        project_root: Root directory of the current project.
        is_internal_dev: True if working on flowspec itself.
        events_dir: Directory for event logs.
        decisions_dir: Directory for decision logs.
    """

    project_root: Path
    is_internal_dev: bool
    events_dir: Path = field(init=False)
    decisions_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        """Initialize computed paths based on mode."""
        if self.is_internal_dev:
            # Internal dev: .flowspec/logs/
            base = self.project_root / ".flowspec" / "logs"
        else:
            # User projects: ./logs/
            base = self.project_root / "logs"

        # Use object.__setattr__ since dataclass is frozen
        object.__setattr__(self, "events_dir", base / "events")
        object.__setattr__(self, "decisions_dir", base / "decisions")

    def ensure_dirs(self) -> None:
        """Create log directories if they don't exist."""
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)


def _is_flowspec_repo(path: Path) -> bool:
    """Check if the given path is the flowspec repository root.

    Detects flowspec repo by checking for:
    - pyproject.toml with flowspec package
    - src/flowspec_cli directory
    - .flowspec directory

    Args:
        path: Directory to check.

    Returns:
        True if this appears to be the flowspec repository.
    """
    # Check for src/flowspec_cli directory
    if (path / "src" / "flowspec_cli").is_dir():
        # Verify it's actually flowspec by checking pyproject.toml
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text(encoding="utf-8")
                # Check for flowspec package identifier
                if 'name = "flowspec-cli"' in content or "[tool.flowspec]" in content:
                    return True
            except OSError as exc:
                # Treat read failures as "not a flowspec repo", but log for debugging.
                logger.debug("Failed to read pyproject.toml at %s: %s", pyproject, exc)

    return False


def _find_project_root(start_path: Optional[Path] = None) -> Path:
    """Find the project root by walking up from start_path.

    Looks for common project markers:
    - .git directory
    - pyproject.toml
    - package.json
    - .flowspec directory
    - backlog directory

    Args:
        start_path: Starting path (defaults to cwd).

    Returns:
        Project root path, or cwd if not found.
    """
    current = (start_path or Path.cwd()).resolve()

    # Walk up the directory tree
    for path in [current, *current.parents]:
        # Check for project markers
        if (path / ".git").is_dir():
            return path
        if (path / "pyproject.toml").exists():
            return path
        if (path / "package.json").exists():
            return path
        if (path / ".flowspec").is_dir():
            return path
        if (path / "backlog").is_dir():
            return path

    # Fallback to current directory
    return Path.cwd().resolve()


def get_config(project_root: Optional[Path] = None) -> LoggingConfig:
    """Get logging configuration for the current project.

    Uses caching to avoid repeated filesystem checks. The cache key is
    the resolved project root path, ensuring consistent results even
    when called with None (which auto-detects the project root).

    Args:
        project_root: Explicit project root (auto-detected if None).

    Returns:
        LoggingConfig for the project.
    """
    # Resolve the path first so it can be used as a stable cache key
    if project_root is None:
        # Check environment variable first
        env_root = os.environ.get("FLOWSPEC_PROJECT_ROOT")
        if env_root:
            resolved_root = Path(env_root).resolve()
        else:
            resolved_root = _find_project_root()
    else:
        resolved_root = project_root.resolve()

    # Call the cached implementation with the resolved path
    return _get_config_cached(resolved_root)


@lru_cache(maxsize=4)
def _get_config_cached(project_root: Path) -> LoggingConfig:
    """Internal cached implementation of get_config.

    Args:
        project_root: Resolved project root path.

    Returns:
        LoggingConfig for the project.
    """
    is_internal = _is_flowspec_repo(project_root)

    if is_internal:
        logger.debug("Internal dev mode: logs to .flowspec/logs/")
    else:
        logger.debug("User project mode: logs to ./logs/")

    return LoggingConfig(project_root=project_root, is_internal_dev=is_internal)


def clear_config_cache() -> None:
    """Clear the config cache (useful for testing)."""
    _get_config_cached.cache_clear()
