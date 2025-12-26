"""
Meta-workflow orchestration engine.

Executes high-level workflows (research, build, run) by orchestrating
multiple sub-workflows in sequence with conditional logic and quality gates.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from flowspec_cli.workflow.config import WorkflowConfig
from flowspec_cli.workflow.state_guard import WorkflowStateGuard

logger = logging.getLogger(__name__)


class OrchestrationMode(Enum):
    """Execution mode for sub-workflows."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class QualityGateType(Enum):
    """Type of quality gate validation."""
    TEST_COVERAGE = "test_coverage"
    SECURITY_SCAN = "security_scan"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"


@dataclass
class SubWorkflowResult:
    """Result of a sub-workflow execution."""
    workflow_name: str
    success: bool
    skipped: bool
    error_message: Optional[str] = None
    artifacts_created: List[str] = None

    def __post_init__(self):
        if self.artifacts_created is None:
            self.artifacts_created = []


@dataclass
class MetaWorkflowResult:
    """Result of a meta-workflow execution."""
    meta_workflow_name: str
    success: bool
    sub_results: List[SubWorkflowResult]
    final_state: Optional[str] = None
    error_message: Optional[str] = None


class MetaWorkflowOrchestrator:
    """
    Orchestrates execution of meta-workflows by running sub-workflows in sequence.

    Responsibilities:
    - Load meta-workflow definitions from flowspec_workflow.yml
    - Validate input state before execution
    - Execute sub-workflows in configured order
    - Handle conditional logic (skip optional workflows)
    - Validate quality gates before state transitions
    - Emit consolidated events
    - Update final task state
    """

    def __init__(self, config: Optional[WorkflowConfig] = None):
        """
        Initialize meta-workflow orchestrator.

        Args:
            config: Workflow configuration instance (defaults to singleton)
        """
        self.config = config or WorkflowConfig()
        self.state_guard = WorkflowStateGuard(self.config)

    def get_meta_workflow(self, meta_name: str) -> Dict[str, Any]:
        """
        Get meta-workflow configuration by name.

        Args:
            meta_name: Name of meta-workflow (research, build, run)

        Returns:
            Meta-workflow configuration dict

        Raises:
            ValueError: If meta-workflow not found
        """
        meta_workflows = self.config.config.get("meta_workflows", {})
        if meta_name not in meta_workflows:
            available = ", ".join(meta_workflows.keys())
            raise ValueError(
                f"Meta-workflow '{meta_name}' not found. "
                f"Available: {available}"
            )
        return meta_workflows[meta_name]

    def should_skip_sub_workflow(
        self,
        sub_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate whether to skip an optional sub-workflow.

        Args:
            sub_config: Sub-workflow configuration with 'required' and 'condition'
            context: Execution context with variables for condition evaluation

        Returns:
            True if sub-workflow should be skipped, False otherwise
        """
        # Always execute required workflows
        if sub_config.get("required", True):
            return False

        # Optional workflows can be skipped
        condition = sub_config.get("condition")
        if not condition:
            # No condition means skip by default
            return True

        # Evaluate condition
        # Simple conditions supported: "complexity_score >= 7", "light_mode == false"
        try:
            # Extract variables from context
            complexity_score = context.get("complexity_score", 0)
            light_mode = context.get("light_mode", True)

            # Build evaluation namespace
            eval_namespace = {
                "complexity_score": complexity_score,
                "light_mode": light_mode,
            }

            # Evaluate condition
            result = eval(condition, {"__builtins__": {}}, eval_namespace)
            # Skip if condition is False
            return not result

        except Exception as e:
            logger.warning(
                f"Failed to evaluate condition '{condition}': {e}. "
                f"Skipping optional workflow."
            )
            return True

    def validate_quality_gates(
        self,
        gates: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate quality gates before final state transition.

        Args:
            gates: List of quality gate configurations
            context: Execution context with gate validation data

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not gates:
            return True, None

        for gate in gates:
            gate_type = gate.get("type")
            required = gate.get("required", True)

            if gate_type == "test_coverage":
                threshold = gate.get("threshold", 80)
                actual_coverage = context.get("test_coverage", 0)

                if actual_coverage < threshold:
                    msg = (
                        f"Test coverage gate failed: {actual_coverage}% < {threshold}%"
                    )
                    if required:
                        return False, msg
                    else:
                        logger.warning(msg)

            elif gate_type == "security_scan":
                severity = gate.get("severity", "HIGH")
                findings = context.get("security_findings", [])
                high_findings = [
                    f for f in findings
                    if f.get("severity", "").upper() in ["HIGH", "CRITICAL"]
                ]

                if high_findings:
                    msg = (
                        f"Security scan gate failed: "
                        f"{len(high_findings)} {severity}+ findings"
                    )
                    if required:
                        return False, msg
                    else:
                        logger.warning(msg)

            elif gate_type == "acceptance_criteria":
                coverage = gate.get("coverage", 100)
                actual_coverage = context.get("ac_coverage", 0)

                if actual_coverage < coverage:
                    msg = (
                        f"Acceptance criteria gate failed: "
                        f"{actual_coverage}% < {coverage}%"
                    )
                    if required:
                        return False, msg
                    else:
                        logger.warning(msg)

        return True, None

    def execute_sub_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any]
    ) -> SubWorkflowResult:
        """
        Execute a single sub-workflow.

        Args:
            workflow_name: Name of workflow to execute (assess, specify, etc.)
            context: Execution context

        Returns:
            SubWorkflowResult with execution outcome
        """
        logger.info(f"Executing sub-workflow: {workflow_name}")

        # This is a placeholder - actual implementation would invoke
        # the corresponding /flow:{workflow_name} command
        # For now, we return success to enable testing

        # TODO: Implement actual sub-workflow execution via:
        # 1. Load command template from templates/commands/flow/{workflow_name}.md
        # 2. Execute command logic
        # 3. Collect artifacts created
        # 4. Return result

        return SubWorkflowResult(
            workflow_name=workflow_name,
            success=True,
            skipped=False,
            artifacts_created=[]
        )

    def execute_meta_workflow(
        self,
        meta_name: str,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> MetaWorkflowResult:
        """
        Execute a meta-workflow by running sub-workflows in sequence.

        Args:
            meta_name: Name of meta-workflow (research, build, run)
            task_id: Optional task ID for backlog integration
            context: Optional execution context

        Returns:
            MetaWorkflowResult with execution outcome
        """
        if context is None:
            context = {}

        logger.info(f"Executing meta-workflow: {meta_name}")

        try:
            # Load meta-workflow config
            meta_config = self.get_meta_workflow(meta_name)

            # Validate input state
            input_state = meta_config.get("input_state")
            if input_state and task_id:
                # TODO: Get current task state from backlog
                # For now, skip validation
                pass

            # Execute sub-workflows
            sub_results = []
            orchestration = meta_config.get("orchestration", {})
            mode = OrchestrationMode(orchestration.get("mode", "sequential"))
            stop_on_error = orchestration.get("stop_on_error", True)

            for sub_config in meta_config.get("sub_workflows", []):
                workflow_name = sub_config.get("workflow")

                # Check if we should skip this workflow
                if self.should_skip_sub_workflow(sub_config, context):
                    logger.info(f"Skipping optional workflow: {workflow_name}")
                    sub_results.append(SubWorkflowResult(
                        workflow_name=workflow_name,
                        success=True,
                        skipped=True
                    ))
                    continue

                # Execute sub-workflow
                result = self.execute_sub_workflow(workflow_name, context)
                sub_results.append(result)

                # Stop on error if configured
                if not result.success and stop_on_error:
                    logger.error(
                        f"Sub-workflow '{workflow_name}' failed, stopping execution"
                    )
                    return MetaWorkflowResult(
                        meta_workflow_name=meta_name,
                        success=False,
                        sub_results=sub_results,
                        error_message=result.error_message
                    )

            # Validate quality gates
            quality_gates = meta_config.get("quality_gates", [])
            gates_passed, gate_error = self.validate_quality_gates(
                quality_gates,
                context
            )

            if not gates_passed:
                logger.error(f"Quality gates failed: {gate_error}")
                return MetaWorkflowResult(
                    meta_workflow_name=meta_name,
                    success=False,
                    sub_results=sub_results,
                    error_message=gate_error
                )

            # Update final state
            output_state = meta_config.get("output_state")
            if output_state and task_id:
                # TODO: Update task state in backlog
                pass

            logger.info(f"Meta-workflow '{meta_name}' completed successfully")
            return MetaWorkflowResult(
                meta_workflow_name=meta_name,
                success=True,
                sub_results=sub_results,
                final_state=output_state
            )

        except Exception as e:
            logger.error(f"Meta-workflow '{meta_name}' failed: {e}")
            return MetaWorkflowResult(
                meta_workflow_name=meta_name,
                success=False,
                sub_results=[],
                error_message=str(e)
            )

    def list_meta_workflows(self) -> List[Dict[str, Any]]:
        """
        List all available meta-workflows.

        Returns:
            List of meta-workflow configurations with name, description, summary
        """
        meta_workflows = self.config.config.get("meta_workflows", {})
        return [
            {
                "name": name,
                "command": config.get("command"),
                "description": config.get("description"),
                "summary": config.get("summary"),
                "input_state": config.get("input_state"),
                "output_state": config.get("output_state"),
                "sub_workflows": [
                    sw.get("workflow") for sw in config.get("sub_workflows", [])
                ]
            }
            for name, config in meta_workflows.items()
        ]


def main():
    """CLI entry point for testing meta-workflow orchestrator."""
    import sys

    orchestrator = MetaWorkflowOrchestrator()

    if len(sys.argv) < 2:
        print("Usage: python -m flowspec_cli.workflow.meta_orchestrator <meta_workflow_name>")
        print("\nAvailable meta-workflows:")
        for meta in orchestrator.list_meta_workflows():
            print(f"  {meta['name']}: {meta['summary']}")
        sys.exit(1)

    meta_name = sys.argv[1]
    result = orchestrator.execute_meta_workflow(meta_name)

    print(f"\nMeta-workflow: {result.meta_workflow_name}")
    print(f"Success: {result.success}")
    if result.final_state:
        print(f"Final state: {result.final_state}")

    print("\nSub-workflow results:")
    for sub_result in result.sub_results:
        status = "SKIPPED" if sub_result.skipped else ("OK" if sub_result.success else "FAILED")
        print(f"  [{status}] {sub_result.workflow_name}")

    if result.error_message:
        print(f"\nError: {result.error_message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
