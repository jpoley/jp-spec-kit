"""Shared utilities for MCP client examples.

This module provides common utilities for connecting to MCP servers,
with proper error handling, timeouts, and security hardening.

Architecture:
    - Connection management via context managers
    - Input validation with type safety
    - Secure subprocess parameters
    - Proper timeout handling
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator

if TYPE_CHECKING:
    from mcp import ClientSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MCP_TIMEOUT = 30  # seconds
DEFAULT_FINDINGS_PREVIEW_COUNT = 3
MAX_DESCRIPTION_LENGTH = 100
SEPARATOR_WIDTH = 60
SEPARATOR_LONG = 100

# Valid scanner and severity values (whitelist)
VALID_SCANNERS = frozenset({"semgrep", "codeql", "trivy", "bandit", "safety"})
VALID_SEVERITIES = frozenset({"critical", "high", "medium", "low", "info"})


class MCPConnectionError(Exception):
    """Error connecting to MCP server."""

    pass


class MCPResponseError(Exception):
    """Error in MCP server response."""

    pass


def get_python_executable() -> str:
    """Get the current Python executable path.

    Returns:
        Path to Python executable
    """
    return sys.executable


def create_safe_env(project_root: Path | None = None) -> dict[str, str]:
    """Create minimal safe environment for subprocess.

    Only includes essential environment variables to prevent
    leaking sensitive data (API keys, tokens, etc.).

    Args:
        project_root: Optional project root path

    Returns:
        Dictionary of safe environment variables

    Note:
        PYTHONPATH is included because the MCP server subprocess needs it to
        locate the specify_cli package when running from development installs.
        This is safe because we control the subprocess being spawned (the MCP
        server), not arbitrary user commands.
    """
    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "USER": os.environ.get("USER", ""),
        # PYTHONPATH needed for dev installs to locate specify_cli package
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
    }

    if project_root:
        safe_env["PROJECT_ROOT"] = str(project_root.resolve())

    return safe_env


def validate_target_directory(target: str) -> Path:
    """Validate target path is a readable directory.

    Args:
        target: Path to validate

    Returns:
        Resolved Path object

    Raises:
        ValueError: If validation fails
    """
    target_path = Path(target).resolve()

    if not target_path.exists():
        raise ValueError(f"Target does not exist: {target}")

    if not target_path.is_dir():
        raise ValueError(f"Target is not a directory: {target}")

    if not os.access(target_path, os.R_OK):
        raise ValueError(f"Target is not readable: {target}")

    return target_path


def parse_mcp_response(
    response: Any,
    expected_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Safely parse MCP response with validation.

    Args:
        response: MCP response object (tool result or resource)
        expected_keys: Required keys in parsed JSON

    Returns:
        Parsed JSON dict

    Raises:
        MCPResponseError: If response is invalid or missing required keys
    """
    # Handle tool results (content attribute)
    if hasattr(response, "content"):
        if not response.content or len(response.content) == 0:
            raise MCPResponseError("MCP response has empty content")
        content = response.content
    # Handle resource responses (contents attribute - note plural)
    elif hasattr(response, "contents"):
        if not response.contents or len(response.contents) == 0:
            raise MCPResponseError("MCP resource has empty contents")
        content = response.contents
    else:
        raise MCPResponseError("MCP response has unknown structure")

    if not content[0]:
        raise MCPResponseError("MCP response first content item is empty")

    try:
        data = json.loads(content[0].text)
    except json.JSONDecodeError as e:
        raise MCPResponseError(f"Invalid JSON in MCP response: {e}")
    except AttributeError:
        raise MCPResponseError("MCP response content has no text attribute")

    if expected_keys:
        missing = [k for k in expected_keys if k not in data]
        if missing:
            raise MCPResponseError(f"MCP response missing required keys: {missing}")

    return data


def validate_scan_response(data: dict[str, Any]) -> bool:
    """Validate scan response has required structure.

    Args:
        data: Parsed scan response

    Returns:
        True if valid
    """
    required = [
        "findings_count",
        "by_severity",
        "should_fail",
        "fail_on",
        "findings_file",
    ]
    return all(k in data for k in required)


def validate_finding(finding: dict[str, Any]) -> None:
    """Validate finding has required fields.

    Args:
        finding: Finding dictionary

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ["id", "title", "severity", "scanner", "location"]
    missing = [f for f in required_fields if f not in finding]
    if missing:
        raise ValueError(f"Finding missing required fields: {missing}")

    # Validate location has required fields
    location = finding.get("location", {})
    location_required = ["file", "line_start"]
    location_missing = [f for f in location_required if f not in location]
    if location_missing:
        raise ValueError(
            f"Finding location missing required fields: {location_missing}"
        )


@asynccontextmanager
async def connect_to_security_mcp(
    project_root: Path | None = None,
    timeout: int = DEFAULT_MCP_TIMEOUT,
) -> AsyncIterator[ClientSession]:
    """Connect to jpspec-security MCP server with timeout.

    Args:
        project_root: Optional project root path
        timeout: Connection timeout in seconds

    Yields:
        Initialized MCP client session

    Raises:
        MCPConnectionError: If connection fails
        asyncio.TimeoutError: If connection times out
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as e:
        raise MCPConnectionError(
            "mcp package not installed. Install with: uv add mcp"
        ) from e

    python_exe = get_python_executable()
    safe_env = create_safe_env(project_root)

    server_params = StdioServerParameters(
        command=python_exe,
        args=["-m", "specify_cli.security.mcp_server"],
        env=safe_env,
    )

    try:
        async with asyncio.timeout(timeout):
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
    except asyncio.TimeoutError:
        raise MCPConnectionError(
            f"MCP server connection timeout after {timeout}s. "
            "Check server health with: ./scripts/bash/check-mcp-servers.sh"
        )
    except FileNotFoundError as e:
        raise MCPConnectionError(f"Python executable not found: {python_exe}") from e
    except Exception as e:
        logger.exception("MCP connection failed")
        raise MCPConnectionError(f"Failed to connect to MCP server: {e}") from e


def truncate_description(
    description: str, max_length: int = MAX_DESCRIPTION_LENGTH
) -> str:
    """Truncate description with ellipsis if too long.

    Args:
        description: Full description text
        max_length: Maximum length before truncation

    Returns:
        Truncated description with ellipsis if needed
    """
    if len(description) <= max_length:
        return description
    return f"{description[:max_length]}..."
