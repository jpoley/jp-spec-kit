#!/usr/bin/env python3
"""
Demonstration of full workflow execution using the orchestrator.

This script shows how the workflow executor skill would work when invoked
by an agent in Claude Code context.
"""

from pathlib import Path
from datetime import datetime
import sys

# Add src to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator


def demo_workflow_execution(workflow_name: str = "quick_build"):
    """Demonstrate workflow execution."""
    print("=" * 70)
    print("WORKFLOW AUTO-EXECUTOR DEMONSTRATION")
    print("=" * 70)
    print()

    # Initialize orchestrator
    workspace_root = Path.cwd()
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"🚀 Auto-executing workflow: {workflow_name}")
    print(f"   Workspace: {workspace_root}")
    print(f"   Session: {session_id}")
    print()

    try:
        orchestrator = WorkflowOrchestrator(workspace_root, session_id)
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        return False

    # Get execution plan
    print("📋 Preparing execution plan...")
    try:
        result = orchestrator.execute_custom_workflow(workflow_name, context={})
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nAvailable workflows:")
        for wf in orchestrator.list_custom_workflows():
            print(f"  - {wf}")
        return False

    if not result.success:
        print(f"❌ Workflow planning failed: {result.error}")
        return False

    print("✓ Plan prepared")
    print(f"  Steps to execute: {result.steps_executed}")
    print(f"  Steps to skip: {result.steps_skipped}")
    print()

    # Execute each step
    print("🔄 Executing workflow steps...")
    print("-" * 70)

    executed_count = 0
    skipped_count = 0

    for i, step_result in enumerate(result.step_results, 1):
        workflow = step_result.workflow_name

        if step_result.skipped:
            print(f"\n[{i}] ⏭️  SKIPPED: {workflow}")
            print(f"    Reason: {step_result.skip_reason}")
            skipped_count += 1
            continue

        if not step_result.command:
            print(f"\n[{i}] ❌ ERROR: No command for {workflow}")
            continue

        command = step_result.command
        print(f"\n[{i}] ▶️  {command}")
        print(f"    Workflow: {workflow}")

        # In agent context, this would invoke:
        # result = await Skill(skill=command.lstrip("/"))
        print("    ✓ Ready for execution")
        print(f"    [Agent would invoke: Skill(skill='{command.lstrip('/')}')]")

        executed_count += 1

    print()
    print("-" * 70)
    print(f"\n✅ Workflow execution complete: {workflow_name}")
    print(f"   ✓ Executed: {executed_count}")
    print(f"   ⏭  Skipped: {skipped_count}")
    print("\n📁 Logs:")
    print(f"   Decision log: .logs/decisions/session-{session_id}.jsonl")
    print(f"   Event log: .logs/events/session-{session_id}.jsonl")
    print()

    # Demonstrate MCP integration
    print("📝 MCP Backlog Integration:")
    print("   [Agent context would update task via MCP]")
    print("   Example:")
    print("     mcp__backlog__task_edit(")
    print("       id='task-123',")
    print("       status='In Progress',")
    print(f"       notesAppend=['Executing workflow: {workflow_name}']")
    print("     )")
    print()

    return True


if __name__ == "__main__":
    workflow_name = sys.argv[1] if len(sys.argv) > 1 else "quick_build"

    success = demo_workflow_execution(workflow_name)

    print("=" * 70)
    if success:
        print("✅ DEMONSTRATION COMPLETE")
        print()
        print("This demonstrates the full workflow execution pattern.")
        print("In Claude Code agent context, each command would be")
        print("actually invoked using the Skill tool.")
    else:
        print("❌ DEMONSTRATION FAILED")
    print("=" * 70)

    sys.exit(0 if success else 1)
