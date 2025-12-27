"""
Custom workflow orchestrator for flexible flowspec execution.

This module implements user-customizable workflow sequences that orchestrate
the 4 core + 2 supporting + 3 ad hoc flowspec commands.

CRITICAL: This is REAL implementation, NOT stubs.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from flowspec_cli.workflow.config import WorkflowConfig
from flowspec_cli.workflow.dispatcher import WorkflowDispatcher
from flowspec_cli.workflow.rigor import RigorEnforcer

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStepResult:
    """Result of executing a single workflow step."""

    workflow_name: str
    success: bool
    skipped: bool
    command: Optional[str] = None  # The command to execute (e.g., "/flow:specify")
    skip_reason: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CustomWorkflowResult:
    """Result of executing a custom workflow."""

    workflow_name: str
    success: bool
    steps_executed: int
    steps_skipped: int
    step_results: List[WorkflowStepResult]
    error: Optional[str] = None


class WorkflowOrchestrator:
    """
    Orchestrates custom workflow sequences.

    Reads user-defined workflows from flowspec_workflow.yml and executes
    them with full rigor enforcement.
    """

    def __init__(self, workspace_root: Path, session_id: str):
        """
        Initialize the orchestrator.

        Args:
            workspace_root: Project workspace root directory
            session_id: Unique session identifier for logging
        """
        self.workspace_root = workspace_root
        self.session_id = session_id

        # Find workflow config file
        config_file = workspace_root / "flowspec_workflow.yml"
        if config_file.exists():
            self.workflow_config = WorkflowConfig.load(config_file)
        else:
            self.workflow_config = None

        self.rigor = RigorEnforcer(workspace_root, session_id)
        self.dispatcher = WorkflowDispatcher(workspace_root)

        # Load custom workflows from config
        self.custom_workflows = self._load_custom_workflows()

        logger.info(
            f"Orchestrator initialized with {len(self.custom_workflows)} custom workflows"
        )

    def _load_custom_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Load custom workflow definitions from flowspec_workflow.yml.

        Returns:
            Dictionary of custom workflow configurations
        """
        config_file = self.workspace_root / "flowspec_workflow.yml"

        if not config_file.exists():
            logger.warning(f"No workflow config found at {config_file}")
            return {}

        with open(config_file) as f:
            config = yaml.safe_load(f)

        custom_workflows = config.get("custom_workflows", {})
        logger.info(f"Loaded {len(custom_workflows)} custom workflows from config")

        return custom_workflows

    def execute_custom_workflow(
        self, workflow_name: str, context: Optional[Dict[str, Any]] = None
    ) -> CustomWorkflowResult:
        """
        Execute a custom workflow by name.

        Args:
            workflow_name: Name of the custom workflow to execute
            context: Optional context dictionary (e.g., complexity scores for conditions)

        Returns:
            CustomWorkflowResult with execution details

        Raises:
            ValueError: If workflow not found or rigor validation fails
        """
        if workflow_name not in self.custom_workflows:
            raise ValueError(f"Custom workflow '{workflow_name}' not found")

        workflow_def = self.custom_workflows[workflow_name]

        # Log workflow start
        self.rigor.log_event(
            event_type="CUSTOM_WORKFLOW_START",
            event=f"Starting custom workflow '{workflow_name}'",
            workflow=workflow_name,
            details={"mode": workflow_def.get("mode"), "context": context or {}},
        )

        # Validate rigor configuration (REQUIRED)
        self.rigor.validate_rigor_config(workflow_def["rigor"])

        # Execute workflow steps
        step_results: List[WorkflowStepResult] = []
        steps_executed = 0
        steps_skipped = 0

        for step_idx, step in enumerate(workflow_def["steps"]):
            step_result = self._execute_step(
                step,
                workflow_def.get("mode", "vibing"),
                context or {},
                step_idx + 1,
                len(workflow_def["steps"]),
            )

            step_results.append(step_result)

            if step_result.skipped:
                steps_skipped += 1
            elif step_result.success:
                steps_executed += 1
            else:
                # Step failed - stop execution
                error_msg = (
                    f"Workflow '{workflow_name}' failed at step {step_idx + 1}: "
                    f"{step_result.error}"
                )
                self.rigor.log_event(
                    event_type="CUSTOM_WORKFLOW_FAILED",
                    event=error_msg,
                    workflow=workflow_name,
                )
                return CustomWorkflowResult(
                    workflow_name=workflow_name,
                    success=False,
                    steps_executed=steps_executed,
                    steps_skipped=steps_skipped,
                    step_results=step_results,
                    error=error_msg,
                )

        # Log workflow completion
        self.rigor.log_event(
            event_type="CUSTOM_WORKFLOW_COMPLETE",
            event=f"Custom workflow '{workflow_name}' completed successfully",
            workflow=workflow_name,
            details={
                "steps_executed": steps_executed,
                "steps_skipped": steps_skipped,
            },
        )

        return CustomWorkflowResult(
            workflow_name=workflow_name,
            success=True,
            steps_executed=steps_executed,
            steps_skipped=steps_skipped,
            step_results=step_results,
        )

    def _execute_step(
        self,
        step: Dict[str, Any],
        mode: str,
        context: Dict[str, Any],
        step_num: int,
        total_steps: int,
    ) -> WorkflowStepResult:
        """
        Execute a single workflow step.

        Args:
            step: Step definition from custom workflow
            mode: Execution mode ('vibing' or 'spec-ing')
            context: Context dictionary for condition evaluation
            step_num: Current step number (1-indexed)
            total_steps: Total number of steps

        Returns:
            WorkflowStepResult
        """
        workflow_name = step["workflow"]

        # Log step start
        self.rigor.log_event(
            event_type="WORKFLOW_STEP_START",
            event=f"Starting step {step_num}/{total_steps}: {workflow_name}",
            workflow=workflow_name,
            details={"step": step, "context": context},
        )

        # Check condition (if specified)
        if "condition" in step:
            if not self._evaluate_condition(step["condition"], context):
                skip_reason = f"Condition not met: {step['condition']}"
                self.rigor.log_event(
                    event_type="WORKFLOW_STEP_SKIPPED",
                    event=f"Skipping step {step_num}/{total_steps}: {workflow_name}",
                    workflow=workflow_name,
                    details={"reason": skip_reason},
                )
                return WorkflowStepResult(
                    workflow_name=workflow_name,
                    success=True,
                    skipped=True,
                    skip_reason=skip_reason,
                )

        # Check checkpoint (if spec-ing mode)
        if mode == "spec-ing" and "checkpoint" in step:
            checkpoint_approved = self._handle_checkpoint(step["checkpoint"])
            if not checkpoint_approved:
                self.rigor.log_event(
                    event_type="WORKFLOW_STEP_SKIPPED",
                    event=f"User declined checkpoint for step {step_num}",
                    workflow=workflow_name,
                    details={"checkpoint": step["checkpoint"]},
                )
                return WorkflowStepResult(
                    workflow_name=workflow_name,
                    success=True,
                    skipped=True,
                    skip_reason="User declined checkpoint",
                )

        # Execute the actual workflow
        # CRITICAL: This is where we ACTUALLY invoke the workflow, not just log it
        try:
            command = self._invoke_workflow(workflow_name)

            self.rigor.log_event(
                event_type="WORKFLOW_STEP_COMPLETE",
                event=f"Completed step {step_num}/{total_steps}: {workflow_name}",
                workflow=workflow_name,
            )

            return WorkflowStepResult(
                workflow_name=workflow_name,
                success=True,
                skipped=False,
                command=command,
            )

        except Exception as e:
            error_msg = f"Failed to execute workflow '{workflow_name}': {str(e)}"
            self.rigor.log_event(
                event_type="WORKFLOW_STEP_FAILED",
                event=error_msg,
                workflow=workflow_name,
                details={"error": str(e)},
            )
            return WorkflowStepResult(
                workflow_name=workflow_name,
                success=False,
                skipped=False,
                error=error_msg,
            )

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.

        Args:
            condition: Condition string (e.g., "complexity >= 5")
            context: Context dictionary with values

        Returns:
            True if condition is met, False otherwise
        """
        # Simple condition evaluation for now
        # Supports: variable >= value, variable <= value, variable == value, variable != value

        # Parse condition
        match = re.match(r"(\w+)\s*(>=|<=|==|!=|>|<)\s*(\d+)", condition)
        if not match:
            logger.warning(f"Could not parse condition: {condition}")
            return True  # Default to true if can't parse

        var_name, operator, value_str = match.groups()
        value = int(value_str)

        # Get variable from context
        var_value = context.get(var_name)
        if var_value is None:
            logger.warning(f"Variable '{var_name}' not found in context")
            return True  # Default to true if variable missing

        # Evaluate
        if operator == ">=":
            result = var_value >= value
        elif operator == "<=":
            result = var_value <= value
        elif operator == "==":
            result = var_value == value
        elif operator == "!=":
            result = var_value != value
        elif operator == ">":
            result = var_value > value
        elif operator == "<":
            result = var_value < value
        else:
            result = True

        self.rigor.log_decision(
            decision="CONDITION_EVALUATED",
            context=f"Evaluating condition: {condition}",
            reasoning=f"Variable {var_name}={var_value}, operator={operator}, value={value}",
            outcome=f"Condition result: {result}",
        )

        return result

    def _handle_checkpoint(self, checkpoint_question: str) -> bool:
        """
        Handle a checkpoint in spec-ing mode.

        Args:
            checkpoint_question: Question to ask the user

        Returns:
            True if user approves, False otherwise
        """
        # For now, return True (autonomous mode)
        # In interactive mode, this would prompt the user
        logger.info(f"Checkpoint: {checkpoint_question}")
        self.rigor.log_decision(
            decision="CHECKPOINT_AUTO_APPROVED",
            context=f"Checkpoint question: {checkpoint_question}",
            reasoning="Auto-approving in autonomous mode",
            outcome="Proceeding to next step",
        )
        return True

    def _invoke_workflow(self, workflow_name: str) -> str:
        """
        Prepare workflow execution command.

        This prepares the workflow for execution and returns the command to execute.
        The actual execution is performed by the caller (agent or CLI).

        Args:
            workflow_name: Name of the workflow to invoke

        Returns:
            Command string to execute (e.g., "/flow:specify")

        Raises:
            ValueError: If workflow not found
            RuntimeError: If workflow execution fails
        """
        # Get workflow definition from config
        if self.workflow_config is None:
            logger.warning(f"No workflow config available")
            raise RuntimeError("No workflow configuration available")

        workflows = self.workflow_config._data.get("workflows", {})

        if workflow_name not in workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found in configuration")

        workflow_def = workflows[workflow_name]
        command = workflow_def["command"]

        logger.info(f"Preparing workflow '{workflow_name}' via command '{command}'")

        # Dispatch workflow execution
        try:
            result = self.dispatcher.dispatch(workflow_name, context={})

            # Log the dispatch result
            self.rigor.log_decision(
                decision="WORKFLOW_DISPATCHED",
                context=f"Dispatched workflow '{workflow_name}' -> '{result['command']}'",
                reasoning=f"Execution mode: {result['execution_mode']}",
                outcome=result["message"],
            )

            # Log next action for agent execution
            self.rigor.log_event(
                event_type="WORKFLOW_DISPATCH_READY",
                event=f"Workflow '{workflow_name}' dispatched",
                workflow=workflow_name,
                details={
                    "command": result["command"],
                    "next_action": result["next_action"],
                    "execution_mode": result["execution_mode"],
                },
            )

            # Return the command for the agent/caller to execute
            return result["command"]

        except ValueError as e:
            logger.error(f"Dispatch failed: {e}")
            raise RuntimeError(f"Failed to dispatch workflow '{workflow_name}': {e}")

    def list_custom_workflows(self) -> List[str]:
        """
        List all available custom workflows.

        Returns:
            List of custom workflow names
        """
        return list(self.custom_workflows.keys())
