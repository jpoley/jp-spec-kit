#!/usr/bin/env python3
"""
Demonstration of conditional workflow execution with context.

Shows how complexity scores and other context values affect workflow execution.
"""

from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator


def demo_conditional_workflow(complexity: int = 5):
    """Demonstrate conditional workflow execution."""
    print("=" * 70)
    print("CONDITIONAL WORKFLOW EXECUTION DEMONSTRATION")
    print("=" * 70)
    print()

    workspace_root = Path.cwd()
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    print("🚀 Workflow: full_design")
    print(f"   Context: complexity={complexity}")
    print()

    orchestrator = WorkflowOrchestrator(workspace_root, session_id)

    # Execute with context
    context = {"complexity": complexity}
    result = orchestrator.execute_custom_workflow("full_design", context)

    print("📋 Execution Plan:")
    print(f"   Total steps in workflow: {len(result.step_results)}")
    print(f"   Steps to execute: {result.steps_executed}")
    print(f"   Steps to skip: {result.steps_skipped}")
    print()

    print("🔄 Step-by-step execution:")
    print("-" * 70)

    for i, step_result in enumerate(result.step_results, 1):
        workflow = step_result.workflow_name

        if step_result.skipped:
            print(f"\n[{i}] ⏭️  SKIPPED: {workflow}")
            print(f"    Reason: {step_result.skip_reason}")
        else:
            print(f"\n[{i}] ▶️  EXECUTE: {workflow}")
            print(f"    Command: {step_result.command}")

    print()
    print("-" * 70)
    print()

    # Show conditional logic explanation
    print("📊 Conditional Logic:")
    print("   Complexity threshold: >= 7")
    print(f"   Current complexity: {complexity}")
    print()

    if complexity >= 7:
        print("   ✓ Research step INCLUDED (complexity >= 7)")
    else:
        print("   ⏭  Research step SKIPPED (complexity < 7)")

    print()
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TEST 1: Low Complexity (complexity=5)")
    print("=" * 70)
    demo_conditional_workflow(complexity=5)

    print("\n\n" + "=" * 70)
    print("TEST 2: High Complexity (complexity=8)")
    print("=" * 70)
    demo_conditional_workflow(complexity=8)

    print("\n" + "=" * 70)
    print("✅ CONDITIONAL EXECUTION DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("Key Takeaway:")
    print("  - Workflows can conditionally execute steps based on context")
    print("  - Rigor enforcement logs all decisions and conditions")
    print("  - Orchestrator handles complex conditional logic automatically")
    print()
