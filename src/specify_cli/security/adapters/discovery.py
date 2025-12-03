"""Tool discovery and installation for security scanners.

This module implements the Chain of Responsibility pattern for discovering
security scanning tools in multiple locations:

1. System PATH
2. Project virtual environment (.venv)
3. Tool cache (~/.specify/tools)

See ADR-005 for architectural decisions.
"""

import shutil
import sys
from pathlib import Path


class ToolDiscovery:
    """Discover and manage security scanning tools.

    This class implements a chain-of-responsibility pattern for finding
    tools in multiple locations. It searches in order of preference:

    1. System PATH (global installation)
    2. Project venv (project-specific installation)
    3. Specify cache (downloaded by this tool)

    Example:
        >>> discovery = ToolDiscovery()
        >>> semgrep_path = discovery.find_tool("semgrep")
        >>> if semgrep_path:
        ...     print(f"Found at: {semgrep_path}")
        ... else:
        ...     print("Not found - install with: pip install semgrep")
    """

    def __init__(self, cache_dir: Path | None = None):
        """Initialize tool discovery.

        Args:
            cache_dir: Directory to cache downloaded tools (default: ~/.specify/tools).
        """
        self.cache_dir = cache_dir or Path.home() / ".specify" / "tools"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def find_tool(self, tool_name: str) -> Path | None:
        """Find tool using discovery chain.

        Searches in order:
        1. System PATH
        2. Project virtual environment
        3. Tool cache (~/.specify/tools)

        Args:
            tool_name: Name of the tool to find (e.g., "semgrep").

        Returns:
            Path to executable if found, None otherwise.

        Example:
            >>> discovery = ToolDiscovery()
            >>> tool_path = discovery.find_tool("semgrep")
            >>> if tool_path:
            ...     print(f"Found: {tool_path}")
        """
        # 1. Check system PATH
        system_path = shutil.which(tool_name)
        if system_path:
            return Path(system_path)

        # 2. Check project venv
        venv_path = self._find_in_venv(tool_name)
        if venv_path:
            return venv_path

        # 3. Check specify cache
        cache_path = self.cache_dir / tool_name
        if cache_path.exists() and cache_path.is_file():
            return cache_path

        return None

    def _find_in_venv(self, tool_name: str) -> Path | None:
        """Find tool in project virtual environment.

        Args:
            tool_name: Name of the tool to find.

        Returns:
            Path to executable in venv, or None if not found.
        """
        # Check common venv locations
        venv_dirs = [
            Path.cwd() / ".venv",
            Path.cwd() / "venv",
            Path(sys.prefix),  # Current Python environment
        ]

        for venv_dir in venv_dirs:
            if not venv_dir.exists():
                continue

            # Check bin/ (Unix) and Scripts/ (Windows)
            for bin_dir in ["bin", "Scripts"]:
                tool_path = venv_dir / bin_dir / tool_name
                if tool_path.exists():
                    return tool_path

        return None

    def ensure_available(
        self, tool_name: str, auto_install: bool = False
    ) -> Path | None:
        """Ensure tool is available, optionally installing it.

        Args:
            tool_name: Name of the tool to ensure is available.
            auto_install: If True, attempt to install tool if not found.

        Returns:
            Path to executable if available or successfully installed.
            None if not found and auto_install is False.

        Raises:
            RuntimeError: If auto_install is True but installation fails.

        Example:
            >>> discovery = ToolDiscovery()
            >>> tool_path = discovery.ensure_available("semgrep", auto_install=True)
            >>> if tool_path:
            ...     print(f"Ready to use: {tool_path}")
        """
        # First, try to find existing installation
        tool_path = self.find_tool(tool_name)
        if tool_path:
            return tool_path

        # If not found and auto_install disabled, return None
        if not auto_install:
            return None

        # Attempt installation (currently only supports pip packages)
        try:
            return self._install_with_pip(tool_name)
        except Exception as e:
            msg = f"Failed to install {tool_name}: {e}"
            raise RuntimeError(msg) from e

    def _install_with_pip(self, tool_name: str) -> Path:
        """Install tool using pip.

        Args:
            tool_name: Name of the tool to install.

        Returns:
            Path to installed executable.

        Raises:
            RuntimeError: If pip installation fails.
        """
        import subprocess

        try:
            # Install using current Python interpreter's pip
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", tool_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )

            # Try to find the newly installed tool
            tool_path = self.find_tool(tool_name)
            if not tool_path:
                msg = f"Installed {tool_name} but could not locate executable"
                raise RuntimeError(msg)

            return tool_path

        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else "Unknown error"
            msg = f"pip install failed: {stderr}"
            raise RuntimeError(msg) from e

    def is_available(self, tool_name: str) -> bool:
        """Check if tool is available without installing.

        Args:
            tool_name: Name of the tool to check.

        Returns:
            True if tool is found, False otherwise.

        Example:
            >>> discovery = ToolDiscovery()
            >>> if discovery.is_available("semgrep"):
            ...     print("Semgrep is ready to use")
        """
        return self.find_tool(tool_name) is not None
