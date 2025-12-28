"""
Agent-side workflow executor.

This module provides the actual execution entry point for Claude Code agent.
It bridges the executor.py module with real Skill and MCP tool access.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from flowspec_cli.workflow.executor import (
    ExecutionResult,
)
from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


def execute_workflow_as_agent(
    workflow_name: str,
    task_id: Optional[str] = None,
    workspace_root: Optional[Path] = None,
) -> List[ExecutionResult]:
    """
    Execute a workflow from Claude Code agent context.

    This function should be called by Claude Code when it wants to
    execute a custom workflow. It has access to Skill and MCP tools.

    Args:
        workflow_name: Name of workflow to execute (e.g., "quick_build")
        task_id: Optional backlog task ID to track progress
        workspace_root: Optional workspace root (defaults to current directory)

    Returns:
        List of ExecutionResult for each workflow step

    Example:
        >>> results = execute_workflow_as_agent("quick_build", task_id="task-123")
        >>> for r in results:
        ...     print(f"{r.workflow_name}: {'✓' if r.success else '✗'}")
    """
    # Default to current directory if not specified
    if workspace_root is None:
        workspace_root = Path.cwd()

    # Generate session ID
    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Load and orchestrate the workflow
    orchestrator = WorkflowOrchestrator(workspace_root, session_id)
    result = orchestrator.execute_custom_workflow(workflow_name, context={})

    logger.info(
        f"Orchestrated {len(result.step_results)} steps for workflow: {workflow_name}"
    )

    # Return the step results
    return result.step_results


def get_execution_instructions(
    workflow_name: str, workspace_root: Optional[Path] = None
) -> str:
    """
    Get instructions for Claude Code to execute a workflow.

    Returns a formatted string that Claude Code can follow to
    manually execute each workflow step using the Skill tool.

    Args:
        workflow_name: Name of workflow to get instructions for
        workspace_root: Optional workspace root (defaults to current directory)

    Returns:
        Formatted execution instructions as markdown
    """
    # Default to current directory if not specified
    if workspace_root is None:
        workspace_root = Path.cwd()

    # Generate session ID
    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    orchestrator = WorkflowOrchestrator(workspace_root, session_id)
    result = orchestrator.execute_custom_workflow(workflow_name, context={})
    steps = result.step_results

    instructions = [
        f"# Workflow Execution Instructions: {workflow_name}",
        "",
        f"Execute the following {len(steps)} steps using the Skill tool:",
        "",
    ]

    for i, step in enumerate(steps, 1):
        if step.skipped:
            instructions.append(
                f"{i}. ⏭️  **Skip**: {step.workflow_name} - {step.skip_reason}"
            )
        elif step.command:
            instructions.append(
                f"{i}. ▶️  **Execute**: `Skill(skill='{step.command.lstrip('/')}')`"
            )
            instructions.append(f"   - Workflow: {step.workflow_name}")
        else:
            instructions.append(
                f"{i}. ❌ **Error**: No command for {step.workflow_name}"
            )

    instructions.extend(
        [
            "",
            "## Execution Steps",
            "",
            "For each step:",
            "1. Invoke the Skill tool with the specified skill name",
            "2. Wait for completion",
            "3. Check for errors",
            "4. Proceed to next step",
            "",
        ]
    )

    return "\n".join(instructions)
