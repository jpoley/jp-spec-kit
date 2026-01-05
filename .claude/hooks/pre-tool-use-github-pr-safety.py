#!/usr/bin/env python3
"""
PreToolUse hook: GitHub PR Safety Guard

Prevents Claude from performing potentially destructive GitHub PR operations:
1. Merging PRs to main/master (default: blocked)
2. Updating any PR (default: blocked)

Configuration via environment variables:
- FLOWSPEC_BLOCK_PR_MERGE=true|false (default: true)
  Blocks mcp__github__merge_pull_request entirely

- FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN=true|false (default: true)
  Only blocks merges when target is main/master (if BLOCK_PR_MERGE is false)

- FLOWSPEC_BLOCK_PR_UPDATES=true|false (default: true)
  Blocks PR update operations (update_pull_request_branch, create_pull_request_review)

Configuration file: .flowspec/github-pr-safety.json
{
    "block_pr_merge": true,
    "block_pr_merge_to_main": true,
    "block_pr_updates": true
}

Returns JSON decision: deny, ask, or allow
"""

import json
import os
import sys
from pathlib import Path

# Add hooks directory to Python path for logging_helper import
sys.path.insert(0, str(Path(__file__).parent))

from logging_helper import setup_hook_logging

# Default configuration - secure by default
DEFAULT_CONFIG = {
    "block_pr_merge": True,
    "block_pr_merge_to_main": True,
    "block_pr_updates": True,
}

# MCP GitHub tools that merge PRs
MERGE_TOOLS = [
    "mcp__github__merge_pull_request",
]

# MCP GitHub tools that update PRs
UPDATE_TOOLS = [
    "mcp__github__update_pull_request_branch",
    "mcp__github__create_pull_request_review",
    "mcp__github__update_issue",  # Issues and PRs share API
]

# Protected branches for merge-to-main blocking
PROTECTED_BRANCHES = ["main", "master"]


def load_config() -> dict:
    """
    Load configuration from environment variables and config file.
    Environment variables take precedence over config file.
    """
    config = DEFAULT_CONFIG.copy()

    # Try to load from config file
    config_file = Path(".flowspec/github-pr-safety.json")
    if config_file.exists():
        try:
            with open(config_file) as f:
                file_config = json.load(f)
                config.update(file_config)
        except (json.JSONDecodeError, IOError):
            pass  # Use defaults on error

    # Environment variables override config file
    env_mappings = {
        "FLOWSPEC_BLOCK_PR_MERGE": "block_pr_merge",
        "FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN": "block_pr_merge_to_main",
        "FLOWSPEC_BLOCK_PR_UPDATES": "block_pr_updates",
    }

    for env_var, config_key in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            config[config_key] = env_value.lower() == "true"

    return config


def check_merge_safety(
    tool_name: str, tool_input: dict, config: dict
) -> tuple[str, str, str]:
    """
    Check if a merge operation should be blocked.

    Returns:
        (decision, reason, additional_context) tuple
        decision is one of: "deny", "ask", "allow"
    """
    if tool_name not in MERGE_TOOLS:
        return "allow", "", ""

    # Check if all merges are blocked
    if config["block_pr_merge"]:
        return (
            "deny",
            "PR merge operations are blocked by safety policy",
            "This Claude instance is configured to prevent PR merges.\n\n"
            "To allow PR merges, set FLOWSPEC_BLOCK_PR_MERGE=false\n"
            "or update .flowspec/github-pr-safety.json",
        )

    # Check if merge to main/master is blocked
    if config["block_pr_merge_to_main"]:
        # Try to determine the PR's base branch from tool_input.
        # Different tool schemas might use different field names.
        base_branch = (
            tool_input.get("base")
            or tool_input.get("base_branch")
            or tool_input.get("baseRef")
            or tool_input.get("target_branch")
        )

        if isinstance(base_branch, str):
            normalized_base = base_branch.strip().lower()
        else:
            normalized_base = None

        # Check if base branch is a protected branch
        protected_set = {b.lower() for b in PROTECTED_BRANCHES}

        if normalized_base and normalized_base in protected_set:
            # Base branch is protected (e.g., main/master) - deny the merge
            return (
                "deny",
                f"PR merge to protected branch '{base_branch}' is blocked",
                f"This Claude instance is configured to prevent PR merges to protected branches.\n\n"
                f"Detected base branch: {base_branch}\n"
                f"Protected branches: {', '.join(PROTECTED_BRANCHES)}\n\n"
                "To allow merges to protected branches, set FLOWSPEC_BLOCK_PR_MERGE_TO_MAIN=false\n"
                "or update .flowspec/github-pr-safety.json",
            )

        if normalized_base:
            # Base branch is known and not protected - allow the merge
            return "allow", "", ""

        # Cannot determine the base branch - be conservative and require confirmation
        return (
            "ask",
            "PR merge to protected branch may be blocked",
            "This Claude instance is configured to require confirmation for PR merges.\n\n"
            "The target branch could not be determined from tool_input.\n"
            "Please confirm this is not merging to main/master.\n"
            "For safety, consider using the GitHub web UI for merges.",
        )

    return "allow", "", ""


def check_update_safety(
    tool_name: str, tool_input: dict, config: dict
) -> tuple[str, str, str]:
    """
    Check if a PR update operation should be blocked.

    Returns:
        (decision, reason, additional_context) tuple
        decision is one of: "deny", "ask", "allow"
    """
    if tool_name not in UPDATE_TOOLS:
        return "allow", "", ""

    if not config["block_pr_updates"]:
        return "allow", "", ""

    tool_descriptions = {
        "mcp__github__update_pull_request_branch": "Update PR branch",
        "mcp__github__create_pull_request_review": "Create PR review",
        "mcp__github__update_issue": "Update issue/PR",
    }

    operation = tool_descriptions.get(tool_name, tool_name)

    return (
        "deny",
        f"PR update operation blocked: {operation}",
        f"This Claude instance is configured to prevent PR modifications.\n\n"
        f"Blocked operation: {operation}\n"
        f"Tool: {tool_name}\n\n"
        f"To allow PR updates, set FLOWSPEC_BLOCK_PR_UPDATES=false\n"
        f"or update .flowspec/github-pr-safety.json",
    )


def main():
    logger = setup_hook_logging("pre-tool-use-github-pr-safety")

    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        if logger:
            logger.info(
                f"Checking GitHub PR safety for tool: {input_data.get('tool_name', 'unknown')}"
            )

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Only check MCP GitHub tools
        if not tool_name.startswith("mcp__github__"):
            print(
                json.dumps(
                    {
                        "decision": "allow",
                        "reason": f"Tool {tool_name} not subject to GitHub PR safety checks",
                    }
                )
            )
            return 0

        # Load configuration
        config = load_config()

        if logger:
            logger.info(f"Config: {config}")

        # Check merge safety first
        decision, reason, context = check_merge_safety(tool_name, tool_input, config)
        if decision != "allow":
            if logger:
                logger.warning(f"Blocked merge operation: {tool_name}")
            print(
                json.dumps(
                    {
                        "decision": decision,
                        "reason": reason,
                        "additionalContext": context,
                    }
                )
            )
            return 0

        # Check update safety
        decision, reason, context = check_update_safety(tool_name, tool_input, config)
        if decision != "allow":
            if logger:
                logger.warning(f"Blocked update operation: {tool_name}")
            print(
                json.dumps(
                    {
                        "decision": decision,
                        "reason": reason,
                        "additionalContext": context,
                    }
                )
            )
            return 0

        # Allow operation
        print(
            json.dumps(
                {
                    "decision": "allow",
                    "reason": "GitHub PR operation allowed by safety policy",
                }
            )
        )
        return 0

    except Exception as e:
        # On error, default to "deny" for safety-critical operations
        # This is different from other hooks that fail-open
        print(
            json.dumps(
                {
                    "decision": "deny",
                    "reason": f"Hook error (defaulting to deny for safety): {str(e)}",
                }
            )
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
