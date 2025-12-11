"""MCP Resource - Expose task memory via MCP protocol.

This module extends the JP Spec Kit MCP server to expose task memory files
as resources via the Model Context Protocol. This enables MCP-compatible
AI agents (like VS Code Copilot) to access task context on demand.

Resource URIs:
    - backlog://memory/{task_id}  - Get specific task memory
    - backlog://memory/active     - Get currently active task memory

Example:
    ```python
    from specify_cli.memory.mcp import register_memory_resources
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("flowspec-backlog")
    register_memory_resources(mcp)
    ```
"""

import json
from pathlib import Path
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from specify_cli.memory.store import TaskMemoryStore
from specify_cli.memory.injector import ContextInjector


def register_memory_resources(
    server: "FastMCP", base_path: Optional[Path] = None
) -> None:
    """Register task memory resources with MCP server.

    This function adds resource endpoints for task memory to an existing
    MCP server. It provides both specific task memory access and active
    task memory access.

    Args:
        server: MCP server instance to register resources with
        base_path: Base path for the project (defaults to current directory)

    Raises:
        ImportError: If MCP package is not available
    """
    if not MCP_AVAILABLE:
        raise ImportError("MCP package not available. Install with: uv add mcp")

    store = TaskMemoryStore(base_path)
    injector = ContextInjector(base_path)

    @server.resource("backlog://memory/{task_id}")
    async def get_task_memory(task_id: str) -> str:
        """Return task memory content via MCP.

        Args:
            task_id: Task identifier (e.g., "task-375")

        Returns:
            JSON string containing task memory content and metadata
        """
        try:
            # Validate task_id format (basic security check)
            if not task_id.startswith("task-"):
                return json.dumps(
                    {
                        "error": "Invalid task ID format",
                        "detail": "Task ID must start with 'task-'",
                    }
                )

            # Check if memory exists
            if not store.exists(task_id):
                return json.dumps(
                    {
                        "error": "Task memory not found",
                        "task_id": task_id,
                        "suggestion": "Create task memory with: backlog memory create",
                    }
                )

            # Read memory content
            content = store.read(task_id)
            memory_path = store.get_path(task_id)

            return json.dumps(
                {
                    "task_id": task_id,
                    "content": content,
                    "path": str(memory_path.relative_to(store.base_path)),
                    "exists": True,
                },
                indent=2,
            )

        except Exception as e:
            return json.dumps(
                {
                    "error": "Failed to retrieve task memory",
                    "task_id": task_id,
                    "detail": str(e),
                }
            )

    @server.resource("backlog://memory/active")
    async def get_active_memory() -> str:
        """Return currently active task memory.

        This resource reads the active task ID from CLAUDE.md and returns
        its memory content. This is useful for agents that want to access
        the current task context without knowing the task ID.

        Returns:
            JSON string containing active task memory content and metadata
        """
        try:
            # Get active task ID from CLAUDE.md
            active_task_id = injector.get_active_task_id()

            if active_task_id is None:
                return json.dumps(
                    {
                        "active_task": None,
                        "message": "No active task set in CLAUDE.md",
                    }
                )

            # Check if memory exists
            if not store.exists(active_task_id):
                return json.dumps(
                    {
                        "active_task": active_task_id,
                        "error": "Active task memory not found",
                        "suggestion": f"Create memory for {active_task_id}",
                    }
                )

            # Read memory content
            content = store.read(active_task_id)
            memory_path = store.get_path(active_task_id)

            return json.dumps(
                {
                    "active_task": active_task_id,
                    "content": content,
                    "path": str(memory_path.relative_to(store.base_path)),
                    "exists": True,
                },
                indent=2,
            )

        except FileNotFoundError:
            return json.dumps(
                {
                    "error": "CLAUDE.md not found",
                    "detail": "backlog/CLAUDE.md is required for active task tracking",
                }
            )
        except Exception as e:
            return json.dumps(
                {
                    "error": "Failed to retrieve active task memory",
                    "detail": str(e),
                }
            )


def create_memory_mcp_server(base_path: Optional[Path] = None) -> Optional["FastMCP"]:
    """Create a standalone MCP server for task memory.

    This is a convenience function for creating a dedicated MCP server
    that only serves task memory resources. For most use cases, you should
    use register_memory_resources() to add memory to an existing server.

    Args:
        base_path: Base path for the project (defaults to current directory)

    Returns:
        MCP server instance if MCP is available, None otherwise
    """
    if not MCP_AVAILABLE:
        return None

    server = FastMCP("flowspec-memory")
    register_memory_resources(server, base_path)
    return server
