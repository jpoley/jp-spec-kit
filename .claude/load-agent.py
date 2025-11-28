#!/usr/bin/env python3
"""
Agent Context Loader for Claude Code

This script loads agent context from .agents/*.md files following the agents.md specification.
It strips the YAML frontmatter and returns the agent's instruction content.

Usage:
    python .claude/load-agent.py sre-agent
    python .claude/load-agent.py software-architect-enhanced platform-engineer-enhanced
"""

import sys
from pathlib import Path
import re


def load_agent_context(agent_name: str) -> str:
    """Load agent context from .agents/{agent_name}.md file.

    Args:
        agent_name: Name of the agent (e.g., 'sre-agent', 'frontend-engineer')

    Returns:
        Agent instruction content without YAML frontmatter

    Raises:
        FileNotFoundError: If agent file doesn't exist
    """
    # Get project root (parent of .claude directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agent_file = project_root / ".agents" / f"{agent_name}.md"

    if not agent_file.exists():
        raise FileNotFoundError(
            f"Agent file not found: {agent_file}\n"
            f"Available agents: {', '.join(get_available_agents())}"
        )

    content = agent_file.read_text()

    # Remove YAML frontmatter (between --- markers)
    # agents.md spec: YAML frontmatter at top of file
    content_without_frontmatter = re.sub(
        r"^---\n.*?\n---\n",  # Match --- to --- at start of file
        "",
        content,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )

    return content_without_frontmatter.strip()


def get_available_agents() -> list[str]:
    """Get list of available agent names."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agents_dir = project_root / ".agents"

    if not agents_dir.exists():
        return []

    return [f.stem for f in agents_dir.glob("*.md")]


def load_multiple_agents(agent_names: list[str]) -> str:
    """Load multiple agent contexts and combine them.

    Args:
        agent_names: List of agent names to load

    Returns:
        Combined agent contexts separated by headers
    """
    contexts = []

    for agent_name in agent_names:
        try:
            context = load_agent_context(agent_name)
            contexts.append(f"# AGENT CONTEXT: {agent_name}\n\n{context}")
        except FileNotFoundError as e:
            print(f"Warning: {e}", file=sys.stderr)
            continue

    return "\n\n---\n\n".join(contexts)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <agent-name> [agent-name2 ...]")
        print(f"\nAvailable agents: {', '.join(get_available_agents())}")
        sys.exit(1)

    agent_names = sys.argv[1:]

    if len(agent_names) == 1:
        try:
            context = load_agent_context(agent_names[0])
            print(context)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        context = load_multiple_agents(agent_names)
        print(context)


if __name__ == "__main__":
    main()
