"""
Demonstration: How Claude Code executes workflows with MCP integration.

This script shows the pattern Claude Code follows when asked to "execute workflow X".
It cannot actually be run as a standalone script because the Skill and MCP tools
are only available in Claude Code agent context.

This is DOCUMENTATION, not executable code.
"""

from pathlib import Path


def execute_workflow_from_claude_code(workflow_name: str, task_id: str | None = None):
    """
    Pattern for Claude Code to execute workflows.

    When user says "execute workflow quick_build", Claude Code follows this pattern:

    1. Import the agent_executor module
    2. Get the workflow steps
    3. For each step:
       a. Invoke the Skill tool manually
       b. Update backlog task via MCP tool
       c. Track results

    Args:
        workflow_name: Name of workflow (e.g., "quick_build")
        task_id: Optional backlog task to update (e.g., "task-123")
    """
    # Step 1: Get workflow steps
    from flowspec_cli.workflow.agent_executor import execute_workflow_as_agent

    steps = execute_workflow_as_agent(workflow_name, workspace_root=Path("."))

    print(f"Executing workflow: {workflow_name}")
    print(f"Steps: {len(steps)}")

    # Step 2: Update task - Starting
    if task_id:
        # Claude Code invokes: mcp__backlog__task_edit(...)
        # Cannot be called from Python - must be invoked by Claude Code
        print("[Claude Code would call] mcp__backlog__task_edit(")
        print(f"    id='{task_id}',")
        print("    status='In Progress',")
        print(f"    notesAppend=['Starting workflow: {workflow_name}']")
        print(")")

    # Step 3: Execute each step
    for i, step in enumerate(steps, 1):
        if step.skipped:
            print(f"\n[{i}] SKIPPED: {step.workflow_name}")
            print(f"    Reason: {step.skip_reason}")
            continue

        if not step.command:
            print(f"\n[{i}] ERROR: No command for {step.workflow_name}")
            continue

        skill_name = step.command.lstrip("/")
        print(f"\n[{i}] EXECUTING: {step.command}")
        print(f"    Workflow: {step.workflow_name}")

        # Claude Code invokes: Skill(skill=skill_name)
        # Cannot be called from Python - must be invoked by Claude Code
        print(f"[Claude Code would call] Skill(skill='{skill_name}')")

        # Update task for this step
        if task_id:
            print("[Claude Code would call] mcp__backlog__task_edit(")
            print(f"    id='{task_id}',")
            print(f"    notesAppend=['✓ Completed: {step.workflow_name}']")
            print(")")

    # Step 4: Update task - Complete
    if task_id:
        print("\n[Claude Code would call] mcp__backlog__task_edit(")
        print(f"    id='{task_id}',")
        print("    status='Done',")
        print(f"    notesAppend=['✓ Workflow {workflow_name} complete']")
        print(")")

    print("\n✓ Workflow execution complete")


# DEMONSTRATION ONLY
# This shows the pattern but cannot actually execute
# because Skill and MCP tools are agent-only

if __name__ == "__main__":
    import sys

    workflow_name = sys.argv[1] if len(sys.argv) > 1 else "quick_build"
    task_id = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 70)
    print("DEMONSTRATION: Claude Code Workflow Execution Pattern")
    print("=" * 70)
    print()
    print("NOTE: This is a demonstration of the execution pattern.")
    print("      Actual execution requires Claude Code agent context.")
    print()
    print("=" * 70)
    print()

    execute_workflow_from_claude_code(workflow_name, task_id)

    print()
    print("=" * 70)
    print("To actually execute workflows:")
    print("  1. Open Claude Code (claude.ai/code)")
    print("  2. Say: 'execute workflow quick_build'")
    print("  3. Claude Code will invoke Skill and MCP tools")
    print("=" * 70)
