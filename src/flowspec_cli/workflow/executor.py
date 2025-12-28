"""
Real workflow execution with Skill tool integration.

This module provides ACTUAL workflow execution, not just planning.
"""

import logging
from typing import Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a workflow step."""

    workflow_name: str
    command: str
    success: bool
    output: str = ""
    error: str = ""


def execute_workflow_in_agent_context(
    workflow_name: str,
    steps: List[Any],  # List[WorkflowStepResult]
    task_id: Optional[str] = None,
    mcp_task_edit: Optional[Any] = None,
    skill_invoker: Optional[Any] = None,
) -> List[ExecutionResult]:
    """
    Execute workflow steps in agent context.

    This function returns execution instructions that Claude Code
    should execute using the Skill tool and MCP tools.

    Args:
        workflow_name: Name of workflow being executed
        steps: List of WorkflowStepResult from orchestrator
        task_id: Optional backlog task ID to update
        mcp_task_edit: Optional MCP tool function for task updates
        skill_invoker: Optional Skill tool function for executing /flow commands

    Returns:
        List of ExecutionResult for each step, or execution instructions
        if called without tool functions

    Note:
        This function is designed to be called by Claude Code agent.
        It will return instructions if tool functions aren't provided.
    """
    results: List[ExecutionResult] = []

    logger.info(f"Executing workflow: {workflow_name} ({len(steps)} steps)")

    # Check if we have the necessary tools
    can_execute = skill_invoker is not None

    # Update task: Starting
    if task_id and mcp_task_edit:
        try:
            mcp_task_edit(
                id=task_id,
                status="In Progress",
                notesAppend=[f"Starting workflow: {workflow_name}"],
            )
            logger.info(f"Updated task {task_id}: Starting workflow {workflow_name}")
        except Exception as e:
            logger.warning(f"Could not update task {task_id}: {e}")

    for i, step in enumerate(steps, 1):
        if step.skipped:
            logger.info(f"Step {i}/{len(steps)}: Skipped {step.workflow_name}")
            results.append(
                ExecutionResult(
                    workflow_name=step.workflow_name,
                    command=step.command or "",
                    success=True,
                    output=f"Skipped: {step.skip_reason}",
                )
            )
            continue

        if not step.command:
            logger.error(f"Step {i}/{len(steps)}: No command for {step.workflow_name}")
            results.append(
                ExecutionResult(
                    workflow_name=step.workflow_name,
                    command="",
                    success=False,
                    error="No command defined",
                )
            )
            continue

        logger.info(f"Step {i}/{len(steps)}: Executing {step.command}")

        # ACTUAL EXECUTION POINT
        if can_execute:
            try:
                # Extract skill name from command
                skill_name = step.command.lstrip("/")

                # Invoke the Skill tool via provided function
                logger.info(f"Invoking Skill(skill='{skill_name}')")
                _ = skill_invoker(skill=skill_name)  # Result captured for side effects

                results.append(
                    ExecutionResult(
                        workflow_name=step.workflow_name,
                        command=step.command,
                        success=True,
                        output=f"Executed: {skill_name}",
                    )
                )

                # Update task for this step
                if task_id and mcp_task_edit:
                    mcp_task_edit(
                        id=task_id, notesAppend=[f"✓ Completed: {step.workflow_name}"]
                    )

            except Exception as e:
                logger.error(f"Failed to execute {step.command}: {e}")
                results.append(
                    ExecutionResult(
                        workflow_name=step.workflow_name,
                        command=step.command,
                        success=False,
                        error=str(e),
                    )
                )
        else:
            # Return instructions for Claude Code to execute manually
            results.append(
                ExecutionResult(
                    workflow_name=step.workflow_name,
                    command=step.command,
                    success=False,
                    error="Cannot execute from subprocess - must be run by Claude Code agent",
                )
            )

    # Update task: Complete
    if task_id and mcp_task_edit:
        all_success = all(r.success for r in results)
        if all_success:
            mcp_task_edit(
                id=task_id,
                status="Done",
                notesAppend=[f"✓ Workflow {workflow_name} complete"],
            )
            logger.info(f"Updated task {task_id}: Workflow {workflow_name} complete")
        else:
            mcp_task_edit(
                id=task_id, notesAppend=[f"✗ Workflow {workflow_name} had errors"]
            )

    return results


def is_agent_context() -> bool:
    """
    Check if running in agent context.

    Returns:
        True if Skill tool and MCP tools are available
    """
    # Try to detect agent context
    # In agent context, certain modules/functions would be available
    # For now, we return False from subprocess

    try:
        # This would only exist in agent context
        import claude_code  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False
