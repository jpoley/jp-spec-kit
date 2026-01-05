#!/usr/bin/env python3
"""
Test suite for pre-tool-use-github-pr-safety.py hook.

Run with: python .claude/hooks/test-github-pr-safety.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK_PATH = Path(__file__).parent / "pre-tool-use-github-pr-safety.py"
CONFIG_PATH = Path(".flowspec/github-pr-safety.json")


def run_hook(
    tool_name: str, tool_input: dict = None, env_overrides: dict = None
) -> dict:
    """Run the hook with given input and return the parsed JSON response."""
    input_data = {"tool_name": tool_name, "tool_input": tool_input or {}}

    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)

    result = subprocess.run(
        ["python3", str(HOOK_PATH)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        env=env,
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout, "stderr": result.stderr}


def test_non_github_tools_allowed():
    """Non-GitHub MCP tools should be allowed."""
    print("Test: Non-GitHub tools allowed...", end=" ")

    for tool in ["Bash", "Read", "Write", "mcp__other__something"]:
        response = run_hook(tool)
        assert response.get("decision") == "allow", f"Tool {tool} should be allowed"

    print("PASS")


def test_merge_blocked_by_default():
    """PR merge should be blocked by default."""
    print("Test: Merge blocked by default...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1},
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"
    assert "blocked" in response.get("reason", "").lower()

    print("PASS")


def test_merge_allowed_when_disabled():
    """PR merge should be allowed when FLOWSPEC_BLOCK_PR_MERGE=false."""
    print("Test: Merge allowed when disabled...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1},
        env_overrides={
            "FLOWSPEC_BLOCK_PR_MERGE": "false",
            "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "false",
        },
    )

    assert response.get("decision") == "allow", f"Expected allow, got {response}"

    print("PASS")


def test_merge_asks_for_main_protection():
    """When merge is allowed but main protection is on and base branch unknown, should ask."""
    print("Test: Merge asks for main protection (unknown base)...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1},
        env_overrides={
            "FLOWSPEC_BLOCK_PR_MERGE": "false",
            "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "true",
        },
    )

    assert response.get("decision") == "ask", f"Expected ask, got {response}"

    print("PASS")


def test_merge_denied_to_main_branch():
    """When merge to main is blocked and base branch IS main, should deny."""
    print("Test: Merge denied to main branch...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1, "base": "main"},
        env_overrides={
            "FLOWSPEC_BLOCK_PR_MERGE": "false",
            "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "true",
        },
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"
    assert "main" in response.get("reason", "").lower()

    print("PASS")


def test_merge_denied_to_master_branch():
    """When merge to main is blocked and base branch IS master, should deny."""
    print("Test: Merge denied to master branch...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1, "base": "master"},
        env_overrides={
            "FLOWSPEC_BLOCK_PR_MERGE": "false",
            "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "true",
        },
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"
    assert "master" in response.get("reason", "").lower()

    print("PASS")


def test_merge_allowed_to_feature_branch():
    """When merge to main is blocked but base branch is NOT protected, should allow."""
    print("Test: Merge allowed to feature branch...", end=" ")

    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1, "base": "feature-branch"},
        env_overrides={
            "FLOWSPEC_BLOCK_PR_MERGE": "false",
            "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "true",
        },
    )

    assert response.get("decision") == "allow", f"Expected allow, got {response}"

    print("PASS")


def test_update_branch_blocked_by_default():
    """Update PR branch should be blocked by default."""
    print("Test: Update branch blocked by default...", end=" ")

    response = run_hook(
        "mcp__github__update_pull_request_branch",
        {"owner": "test", "repo": "test", "pull_number": 1},
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"

    print("PASS")


def test_create_review_blocked_by_default():
    """Create PR review should be blocked by default."""
    print("Test: Create review blocked by default...", end=" ")

    response = run_hook(
        "mcp__github__create_pull_request_review",
        {
            "owner": "test",
            "repo": "test",
            "pull_number": 1,
            "body": "LGTM",
            "event": "APPROVE",
        },
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"

    print("PASS")


def test_update_issue_blocked_by_default():
    """Update issue (can be PR) should be blocked by default."""
    print("Test: Update issue blocked by default...", end=" ")

    response = run_hook(
        "mcp__github__update_issue",
        {"owner": "test", "repo": "test", "issue_number": 1},
    )

    assert response.get("decision") == "deny", f"Expected deny, got {response}"

    print("PASS")


def test_updates_allowed_when_disabled():
    """PR updates should be allowed when FLOWSPEC_BLOCK_PR_UPDATES=false."""
    print("Test: Updates allowed when disabled...", end=" ")

    for tool in [
        "mcp__github__update_pull_request_branch",
        "mcp__github__create_pull_request_review",
        "mcp__github__update_issue",
    ]:
        response = run_hook(
            tool,
            {"owner": "test", "repo": "test", "pull_number": 1},
            env_overrides={"FLOWSPEC_BLOCK_PR_UPDATES": "false"},
        )
        assert response.get("decision") == "allow", f"Tool {tool} should be allowed"

    print("PASS")


def test_safe_github_operations_allowed():
    """Read-only GitHub operations should always be allowed."""
    print("Test: Safe GitHub operations allowed...", end=" ")

    safe_tools = [
        "mcp__github__get_pull_request",
        "mcp__github__list_pull_requests",
        "mcp__github__get_issue",
        "mcp__github__list_issues",
        "mcp__github__get_file_contents",
        "mcp__github__search_repositories",
        "mcp__github__search_code",
        "mcp__github__list_commits",
    ]

    for tool in safe_tools:
        response = run_hook(tool, {"owner": "test", "repo": "test"})
        assert response.get("decision") == "allow", f"Tool {tool} should be allowed"

    print("PASS")


def test_create_pr_allowed():
    """Creating a PR should be allowed (not the same as merging)."""
    print("Test: Create PR allowed...", end=" ")

    response = run_hook(
        "mcp__github__create_pull_request",
        {
            "owner": "test",
            "repo": "test",
            "title": "Test PR",
            "head": "feature",
            "base": "main",
        },
    )

    assert response.get("decision") == "allow", f"Expected allow, got {response}"

    print("PASS")


def test_config_file_respected():
    """Configuration file should be respected."""
    print("Test: Config file respected...", end=" ")

    # Create temp config
    config_path = Path(".flowspec/github-pr-safety.json")
    backup_path = Path(".flowspec/github-pr-safety.json.bak")

    # Backup existing config if present
    if config_path.exists():
        config_path.rename(backup_path)

    try:
        # Write permissive config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(
                {
                    "block_pr_merge": False,
                    "block_pr_merge_to_main": False,
                    "block_pr_updates": False,
                }
            )
        )

        # Clear env vars to ensure config file is used
        response = run_hook(
            "mcp__github__merge_pull_request",
            {"owner": "test", "repo": "test", "pull_number": 1},
            env_overrides={
                "FLOWSPEC_BLOCK_PR_MERGE": "",
                "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "",
                "FLOWSPEC_BLOCK_PR_UPDATES": "",
            },
        )

        assert response.get("decision") == "allow", (
            f"Expected allow with permissive config, got {response}"
        )

    finally:
        # Restore original config
        config_path.unlink(missing_ok=True)
        if backup_path.exists():
            backup_path.rename(config_path)

    print("PASS")


def test_env_overrides_config():
    """Environment variables should override config file."""
    print("Test: Env overrides config...", end=" ")

    # Even if config file says allow, env var should block
    response = run_hook(
        "mcp__github__merge_pull_request",
        {"owner": "test", "repo": "test", "pull_number": 1},
        env_overrides={"FLOWSPEC_BLOCK_PR_MERGE": "true"},
    )

    assert response.get("decision") == "deny", (
        f"Expected deny with env override, got {response}"
    )

    print("PASS")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GitHub PR Safety Hook Tests")
    print("=" * 60)
    print()

    tests = [
        test_non_github_tools_allowed,
        test_merge_blocked_by_default,
        test_merge_allowed_when_disabled,
        test_merge_asks_for_main_protection,
        test_merge_denied_to_main_branch,
        test_merge_denied_to_master_branch,
        test_merge_allowed_to_feature_branch,
        test_update_branch_blocked_by_default,
        test_create_review_blocked_by_default,
        test_update_issue_blocked_by_default,
        test_updates_allowed_when_disabled,
        test_safe_github_operations_allowed,
        test_create_pr_allowed,
        test_config_file_respected,
        test_env_overrides_config,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
