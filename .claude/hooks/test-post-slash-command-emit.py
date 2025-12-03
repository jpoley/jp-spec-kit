#!/usr/bin/env python3
"""Tests for post-slash-command-emit.py hook.

Tests the auto-emit functionality for /jpspec slash commands.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK_SCRIPT = Path(__file__).parent / "post-slash-command-emit.py"


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


class TestPostSlashCommandEmit(unittest.TestCase):
    """Test the auto-emit hook."""

    def test_non_slash_command_tool_allows(self):
        """Non-SlashCommand tools should be allowed without emission."""
        exit_code, output = run_hook(
            {
                "tool_name": "Bash",
                "tool_input": {"command": "ls -la"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertEqual(output["reason"], "Not a SlashCommand tool")

    def test_non_jpspec_command_allows(self):
        """Non-jpspec slash commands should be allowed without emission."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/commit fix: update readme"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertEqual(output["reason"], "Not a /jpspec command")

    def test_jpspec_assess_detected(self):
        """Test /jpspec:assess is detected and maps to workflow.assessed."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:assess my-feature"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("workflow.assessed", output.get("additionalContext", ""))

    def test_jpspec_specify_detected(self):
        """Test /jpspec:specify is detected and maps to spec.created."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {
                    "command": "/jpspec:specify auth-feature --spec-id auth"
                },
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("spec.created", output.get("additionalContext", ""))
        self.assertIn("Feature: auth", output.get("additionalContext", ""))

    def test_jpspec_implement_detected(self):
        """Test /jpspec:implement is detected and maps to implement.completed."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:implement task-229"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("implement.completed", output.get("additionalContext", ""))
        self.assertIn("Task: task-229", output.get("additionalContext", ""))

    def test_jpspec_validate_detected(self):
        """Test /jpspec:validate is detected and maps to validate.completed."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:validate"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("validate.completed", output.get("additionalContext", ""))

    def test_jpspec_operate_detected(self):
        """Test /jpspec:operate is detected and maps to deploy.completed."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:operate production"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(output["decision"], "allow")
        self.assertIn("deploy.completed", output.get("additionalContext", ""))

    def test_extract_task_id_from_command(self):
        """Test task ID extraction from command."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:implement --task-id task-123"},
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Task: task-123", output.get("additionalContext", ""))

    def test_extract_feature_from_output(self):
        """Test feature extraction from tool output."""
        exit_code, output = run_hook(
            {
                "tool_name": "SlashCommand",
                "tool_input": {"command": "/jpspec:specify"},
                "tool_output": "Feature: user-authentication\nCreating specification...",
            }
        )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "Feature: user-authentication", output.get("additionalContext", "")
        )

    def test_invalid_json_allows(self):
        """Invalid JSON input should allow (fail-open)."""
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input="not valid json",
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        output = json.loads(result.stdout)
        self.assertEqual(output["decision"], "allow")

    def test_all_jpspec_commands_mapped(self):
        """Verify all /jpspec commands have event mappings."""
        commands = [
            ("/jpspec:assess", "workflow.assessed"),
            ("/jpspec:specify", "spec.created"),
            ("/jpspec:research", "research.completed"),
            ("/jpspec:plan", "plan.created"),
            ("/jpspec:implement", "implement.completed"),
            ("/jpspec:validate", "validate.completed"),
            ("/jpspec:operate", "deploy.completed"),
        ]

        for command, expected_event in commands:
            with self.subTest(command=command):
                exit_code, output = run_hook(
                    {
                        "tool_name": "SlashCommand",
                        "tool_input": {"command": command},
                    }
                )

                self.assertEqual(exit_code, 0)
                self.assertIn(
                    expected_event,
                    output.get("additionalContext", ""),
                    f"Expected {expected_event} for {command}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
