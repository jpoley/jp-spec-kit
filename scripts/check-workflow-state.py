#!/usr/bin/env python3
"""CLI wrapper for workflow state validation.

This script can be called from /jpspec command markdown files to validate
that a task is in an allowed state before executing a workflow.

Usage:
    python3 scripts/check-workflow-state.py <workflow> <current-state> [--skip]

Examples:
    python3 scripts/check-workflow-state.py specify "Assessed"
    python3 scripts/check-workflow-state.py plan "Specified" --skip

Exit codes:
    0 - State check passed (can proceed)
    1 - State check failed (blocked)
"""

import sys
from pathlib import Path

# Add src to path so we can import specify_cli
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from specify_cli.workflow.state_guard import check_workflow_state  # noqa: E402


def main() -> int:
    """Main entry point for state checking."""
    if len(sys.argv) < 3:
        print(
            "Usage: check-workflow-state.py <workflow> <current-state> [--skip]",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  check-workflow-state.py specify 'Assessed'", file=sys.stderr)
        print("  check-workflow-state.py plan 'Specified' --skip", file=sys.stderr)
        return 1

    workflow = sys.argv[1]
    current_state = sys.argv[2]
    skip = "--skip" in sys.argv or "--skip-state-check" in sys.argv

    # Check state
    can_proceed, message = check_workflow_state(workflow, current_state, skip=skip)

    # Print message (always useful for debugging)
    print(message)

    # Return appropriate exit code
    return 0 if can_proceed else 1


if __name__ == "__main__":
    sys.exit(main())
