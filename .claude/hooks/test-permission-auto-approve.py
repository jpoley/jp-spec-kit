#!/usr/bin/env python3
"""Tests for permission-auto-approve.py hook.

Tests the auto-approval functionality for safe read operations.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK_SCRIPT = Path(__file__).parent / "permission-auto-approve.py"


def run_hook(input_data: dict) -> tuple[int, dict]:
    """Run the hook with given input data.

    Returns:
        Tuple of (exit_code, parsed_output_json)
    """
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"raw": result.stdout, "stderr": result.stderr}

    return result.returncode, output


class TestPermissionAutoApprove(unittest.TestCase):
    """Test the auto-approve hook."""

    # --- Read tool tests ---

    def test_read_docs_approved(self):
        """Read in docs/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "docs/guides/hooks-quickstart.md"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("safe directory", output.get("reason", ""))

    def test_read_backlog_approved(self):
        """Read in backlog/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "backlog/tasks/task-123.md"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_read_templates_approved(self):
        """Read in templates/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "templates/spec-template.md"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_read_specify_approved(self):
        """Read in .specify/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": ".specify/hooks/hooks.yaml"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_read_src_passes(self):
        """Read in src/ should use normal approval flow."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "src/main.py"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    def test_read_root_passes(self):
        """Read at root should use normal approval flow."""
        exit_code, output = run_hook(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "pyproject.toml"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    # --- Bash tool tests ---

    def test_backlog_command_approved(self):
        """backlog CLI commands should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "backlog task list --plain"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("safe command", output.get("reason", ""))

    def test_backlog_task_edit_approved(self):
        """backlog task edit should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "backlog task edit 123 -s Done"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_git_status_approved(self):
        """git status should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git status"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_git_log_approved(self):
        """git log should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git log --oneline -10"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_git_diff_approved(self):
        """git diff should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git diff HEAD~1"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_dangerous_bash_passes(self):
        """Dangerous bash commands should use normal approval."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "rm -rf /"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    def test_git_push_passes(self):
        """git push should use normal approval."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "git push origin main"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    # --- Glob/Grep tool tests ---

    def test_glob_docs_approved(self):
        """Glob in docs/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Glob",
                "tool_input": {"path": "docs/", "pattern": "**/*.md"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    def test_grep_backlog_approved(self):
        """Grep in backlog/ should be auto-approved."""
        exit_code, output = run_hook(
            {
                "tool_name": "Grep",
                "tool_input": {"path": "backlog/tasks/", "pattern": "task-"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")

    # --- Other tools ---

    def test_write_passes(self):
        """Write tool should use normal approval."""
        exit_code, output = run_hook(
            {
                "tool_name": "Write",
                "tool_input": {"file_path": "docs/test.md", "content": "test"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    def test_edit_passes(self):
        """Edit tool should use normal approval."""
        exit_code, output = run_hook(
            {
                "tool_name": "Edit",
                "tool_input": {"file_path": "docs/test.md"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "pass")

    def test_invalid_json_passes(self):
        """Invalid JSON should pass through."""
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="not valid json",
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "pass")


if __name__ == "__main__":
    unittest.main(verbosity=2)
