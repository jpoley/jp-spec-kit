"""
Workflow dispatcher for custom workflow orchestration.

Maps workflow names to execution strategies. Since /flow commands are Claude Code
agent commands (not CLI commands), this dispatcher provides the integration layer
between the orchestrator and the actual workflow execution.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class WorkflowDispatcher:
    """
    Dispatches workflow execution to appropriate handlers.

    For Claude Code agent workflows (/flow:specify, /flow:plan, etc.),
    this dispatcher generates skill invocation instructions.
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize the dispatcher.

        Args:
            workspace_root: Project workspace root directory
        """
        self.workspace_root = workspace_root
        self.handlers = self._build_handler_map()

    def _build_handler_map(self) -> Dict[str, str]:
        """
        Build mapping of workflow names to their slash command syntax.

        Returns:
            Dictionary mapping workflow names to slash commands
        """
        return {
            # Core workflows (THE MISSION - Inner Loop)
            "specify": "/flow:specify",
            "plan": "/flow:plan",
            "implement": "/flow:implement",
            "validate": "/flow:validate",
            # Supporting workflows (Pre-Spec Helpers)
            "assess": "/flow:assess",
            "research": "/flow:research",
            # Ad hoc utilities (Standalone Tools)
            "submit-n-watch-pr": "/flow:submit-n-watch-pr",
        }

    def dispatch(
        self, workflow_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatch workflow execution.

        For agent workflows, this returns execution metadata that the orchestrator
        can use to invoke the skill or output instructions.

        Args:
            workflow_name: Name of workflow to execute
            context: Optional execution context

        Returns:
            Result dictionary with success, command, and metadata

        Raises:
            ValueError: If workflow name not found
        """
        if workflow_name not in self.handlers:
            raise ValueError(
                f"Unknown workflow: {workflow_name}. "
                f"Available: {list(self.handlers.keys())}"
            )

        command = self.handlers[workflow_name]

        logger.info(f"Dispatching workflow '{workflow_name}' -> '{command}'")

        # Return execution metadata
        # The orchestrator will use this to generate skill invocations or output instructions
        return {
            "success": True,
            "workflow": workflow_name,
            "command": command,
            "execution_mode": "agent",  # These are agent commands, not CLI
            "message": f"Workflow '{workflow_name}' ready for execution",
            "next_action": f"Execute: {command}",
        }

    def can_execute_programmatically(self, workflow_name: str) -> bool:
        """
        Check if a workflow can be executed programmatically (vs requiring agent).

        Args:
            workflow_name: Name of workflow

        Returns:
            True if workflow can be executed via subprocess/API, False if agent-only
        """
        # Currently all workflows are agent-based (Claude Code commands)
        # In the future, some might be CLI-based
        return False

    def get_execution_instructions(self, workflow_name: str) -> str:
        """
        Get human/agent-readable execution instructions for a workflow.

        Args:
            workflow_name: Name of workflow

        Returns:
            Formatted execution instructions
        """
        if workflow_name not in self.handlers:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        command = self.handlers[workflow_name]

        instructions = f"""
To execute the '{workflow_name}' workflow:

1. Ensure you're in the project workspace
2. Execute the command: {command}
3. Follow the workflow prompts and requirements
4. Verify completion artifacts are created

Command: {command}
Workspace: {self.workspace_root}
"""
        return instructions.strip()
