"""Task Memory module - Persistent storage for task implementation context.

This module provides components for managing task memory files that track:
- Implementation context and decisions
- Approaches tried and outcomes
- Open questions and resources
- Freeform notes during development

Components:
    TaskMemoryStore: Core CRUD operations for memory files
    LifecycleManager: Orchestrates memory operations on task state changes
    CleanupManager: Automated archiving and deletion of old memories
    ContextInjector: Injects memory into agent context via CLAUDE.md
    register_memory_resources: Registers MCP resources
    create_memory_mcp_server: Creates MCP server for memory access
"""

from flowspec_cli.memory.store import TaskMemoryStore
from flowspec_cli.memory.lifecycle import LifecycleManager
from flowspec_cli.memory.cleanup import CleanupManager
from flowspec_cli.memory.injector import ContextInjector
from flowspec_cli.memory.mcp import register_memory_resources, create_memory_mcp_server

__all__ = [
    "TaskMemoryStore",
    "LifecycleManager",
    "CleanupManager",
    "ContextInjector",
    "register_memory_resources",
    "create_memory_mcp_server",
]
