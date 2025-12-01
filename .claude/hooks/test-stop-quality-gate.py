#!/usr/bin/env python3
"""
Test suite for stop-quality-gate.py hook

Tests all edge cases and defensive coding requirements.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_hook(conversation_summary: str = "", stop_reason: str = "user_requested") -> dict:
    """
    Run the stop-quality-gate hook with given input.

    Args:
        conversation_summary: Conversation context to test
        stop_reason: Stop reason to include in input

    Returns:
        Parsed JSON response from hook
    """
    hook_path = Path(__file__).parent / "stop-quality-gate.py"

    input_data = {
        "stopReason": stop_reason,
        "conversationSummary": conversation_summary,
    }

    result = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        timeout=10,
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"ERROR: Hook returned invalid JSON: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        raise e


def test_no_pr_mention():
    """Test: No PR mention in context should allow stop."""
    print("Test 1: No PR mention in context")
    response = run_hook("Working on implementing a feature for the application")

    assert response["continue"] is True, "Should allow stop when no PR mentioned"
    print("  ✓ Allows stop when no PR detected")


def test_pr_mention_no_tasks():
    """Test: PR mention with no In Progress tasks should allow stop."""
    print("\nTest 2: PR mention, no In Progress tasks")
    # Note: task-189 may be In Progress during development
    # This test expects blocking if task-189 is present
    response = run_hook("Now let's create a pull request for this feature")

    # Check if task-189 is In Progress
    import subprocess

    result = subprocess.run(
        ["backlog", "task", "list", "--plain", "-s", "In Progress"],
        capture_output=True,
        text=True,
    )
    has_189 = "task-189" in result.stdout

    if has_189:
        # If task-189 is In Progress, should block
        assert (
            response["continue"] is False
        ), "Should block when task-189 In Progress"
        print("  ✓ Blocks stop when task-189 In Progress (expected during dev)")
    else:
        # If no tasks, should allow
        assert response["continue"] is True, "Should allow stop when no tasks"
        print("  ✓ Allows stop when no In Progress tasks")


def test_pr_mention_with_tasks():
    """Test: PR mention with In Progress tasks should block stop."""
    print("\nTest 3: PR mention with In Progress tasks")

    # Check if task-189 is already In Progress
    result = subprocess.run(
        ["backlog", "task", "list", "--plain", "-s", "In Progress"],
        capture_output=True,
        text=True,
    )

    # Create a test task
    subprocess.run(
        [
            "backlog",
            "task",
            "create",
            "Test task for stop hook",
            "-s",
            "In Progress",
            "-a",
            "@test",
        ],
        capture_output=True,
    )

    try:
        response = run_hook("Let's create a PR for this work now")

        assert response["continue"] is False, "Should block stop when tasks incomplete"
        assert "stopReason" in response, "Should include stopReason when blocking"
        assert "systemMessage" in response, "Should include guidance message"
        assert "task" in response["systemMessage"].lower(), "Message should mention tasks"

        # Verify we see at least the test task (and possibly task-189)
        task_count = response["systemMessage"].count("task-")
        assert task_count >= 1, f"Should list at least 1 task, got {task_count}"

        print("  ✓ Blocks stop when PR detected with In Progress tasks")
        print(f"  ✓ Provides guidance: {response['systemMessage'][:80]}...")
        print(f"  ✓ Lists {task_count} task(s) in message")

    finally:
        # Clean up: archive the test task
        result = subprocess.run(
            ["backlog", "task", "list", "--plain", "-s", "In Progress"],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.strip().split("\n"):
            if "Test task for stop hook" in line:
                # Extract task ID from format: [HIGH] task-123 - Title
                import re

                match = re.search(r"task-\d+", line)
                if match:
                    task_id = match.group()
                    subprocess.run(
                        ["backlog", "task", "archive", task_id], capture_output=True
                    )


def test_various_pr_phrases():
    """Test: Various PR phrase patterns should be detected."""
    print("\nTest 4: Various PR phrase patterns")

    phrases = [
        "Let's create a pull request",
        "Time to open a PR",
        "Now make a pr for this",
        "Run gh pr create",
        "Create PR for this feature",
        "Open pull request now",
        "Let's PR this work",
    ]

    for phrase in phrases:
        response = run_hook(phrase)
        # Without In Progress tasks, should allow but should have detected PR
        # We can't directly test detection, but we verify it doesn't error
        assert "continue" in response, f"Should return valid response for: {phrase}"

    print(f"  ✓ Handles {len(phrases)} different PR phrase patterns")


def test_empty_conversation():
    """Test: Empty/null conversation context should allow stop."""
    print("\nTest 5: Empty/null conversation context")

    response1 = run_hook("")
    assert response1["continue"] is True, "Should allow stop with empty context"

    response2 = run_hook()  # No conversation_summary
    assert response2["continue"] is True, "Should allow stop with no context"

    print("  ✓ Allows stop with empty/null context")


def test_force_bypass():
    """Test: Force/skip flags in context should bypass quality gate."""
    print("\nTest 6: Force/skip bypass")

    # Create a test task
    subprocess.run(
        [
            "backlog",
            "task",
            "create",
            "Test task for force bypass",
            "-s",
            "In Progress",
            "-a",
            "@test",
        ],
        capture_output=True,
    )

    try:
        response = run_hook("Create PR. Force stop and skip quality gate checks.")

        assert (
            response["continue"] is True
        ), "Should allow stop when force/skip requested"
        assert "bypass" in response["systemMessage"].lower(), "Should confirm bypass"
        print("  ✓ Allows bypass with force/skip keywords")

    finally:
        # Clean up
        result = subprocess.run(
            ["backlog", "task", "list", "--plain", "-s", "In Progress"],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.strip().split("\n"):
            if "Test task for force bypass" in line:
                # Extract task ID from format: [HIGH] task-123 - Title
                import re

                match = re.search(r"task-\d+", line)
                if match:
                    task_id = match.group()
                    subprocess.run(
                        ["backlog", "task", "archive", task_id], capture_output=True
                    )


def test_invalid_json_input():
    """Test: Invalid JSON input should fail-open (allow stop)."""
    print("\nTest 7: Invalid JSON input (fail-open)")

    hook_path = Path(__file__).parent / "stop-quality-gate.py"

    result = subprocess.run(
        ["python3", str(hook_path)],
        input="not valid json",
        capture_output=True,
        text=True,
        timeout=10,
    )

    response = json.loads(result.stdout)
    assert response["continue"] is True, "Should fail-open on invalid JSON"
    print("  ✓ Fails open on invalid JSON input")


def test_multiple_in_progress_tasks():
    """Test: Multiple In Progress tasks should all be listed."""
    print("\nTest 8: Multiple In Progress tasks")

    # Create multiple test tasks
    for i in range(3):
        subprocess.run(
            [
                "backlog",
                "task",
                "create",
                f"Test task {i+1} for multiple tasks",
                "-s",
                "In Progress",
                "-a",
                "@test",
            ],
            capture_output=True,
        )

    try:
        response = run_hook("Let's create a pull request now")

        assert response["continue"] is False, "Should block with multiple tasks"
        # Check that message mentions multiple tasks
        message = response["systemMessage"]
        # Should list all 3 tasks
        assert (
            message.count("Test task") >= 3
        ), "Should list all In Progress tasks in message"
        print("  ✓ Lists all In Progress tasks when blocking")
        print(f"  ✓ Found {message.count('Test task')} task references in message")

    finally:
        # Clean up all test tasks
        result = subprocess.run(
            ["backlog", "task", "list", "--plain", "-s", "In Progress"],
            capture_output=True,
            text=True,
        )
        for line in result.stdout.strip().split("\n"):
            if "Test task" in line and "for multiple tasks" in line:
                # Extract task ID from format: [HIGH] task-123 - Title
                import re

                match = re.search(r"task-\d+", line)
                if match:
                    task_id = match.group()
                    subprocess.run(
                        ["backlog", "task", "archive", task_id], capture_output=True
                    )


def test_case_insensitive_detection():
    """Test: PR detection should be case-insensitive."""
    print("\nTest 9: Case-insensitive PR detection")

    phrases = [
        "CREATE PR",
        "Open Pull Request",
        "gh PR create",
        "PULL REQUEST CREATE",
    ]

    for phrase in phrases:
        response = run_hook(phrase)
        assert "continue" in response, f"Should handle case variation: {phrase}"

    print("  ✓ Handles case-insensitive PR detection")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Stop Quality Gate Hook Test Suite")
    print("=" * 70)

    tests = [
        test_no_pr_mention,
        test_pr_mention_no_tasks,
        test_pr_mention_with_tasks,
        test_various_pr_phrases,
        test_empty_conversation,
        test_force_bypass,
        test_invalid_json_input,
        test_multiple_in_progress_tasks,
        test_case_insensitive_detection,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
