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
    memory_app: CLI commands for memory management
"""

from specify_cli.memory.store import TaskMemoryStore
from specify_cli.memory.lifecycle import LifecycleManager
from specify_cli.memory.cleanup import CleanupManager
from specify_cli.memory.cli import memory_app

__all__ = ["TaskMemoryStore", "LifecycleManager", "CleanupManager", "memory_app"]
