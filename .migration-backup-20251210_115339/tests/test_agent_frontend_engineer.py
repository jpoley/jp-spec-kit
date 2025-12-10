"""Tests for the frontend-engineer subagent.

These tests validate that the frontend-engineer agent:
- Has valid YAML frontmatter with required fields
- Has correct tools configured for frontend development
- Contains required sections for React/TypeScript development
- Matches the template file in templates/agents/
"""

import re
from pathlib import Path
from typing import Dict, Optional

import pytest


def get_project_root() -> Path:
    """Get the project root directory reliably.

    Returns:
        Path to the project root directory.
    """
    return Path(__file__).resolve().parent.parent


def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it doesn't exist or can't be read.

    Args:
        file_path: Path to the file to read.

    Returns:
        File contents as string, or None if the file can't be read.
    """
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
    except (OSError, IOError, PermissionError):
        # Suppress file read errors; function returns None if file can't be read
        pass
    return None


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with YAML frontmatter.

    Returns:
        Dictionary of frontmatter key-value pairs.

    Raises:
        ValueError: If no valid frontmatter is found.
    """
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found")

    frontmatter_text = match.group(1)
    result: Dict[str, str] = {}

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


# Constants
AGENT_NAME = "frontend-engineer"
EXPECTED_COLOR = "cyan"
EXPECTED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "tools", "color"]
REQUIRED_CONTENT_SECTIONS = [
    "## Core Technologies",
    "## Implementation Standards",
    "## Testing Approach",
]


class TestFrontendEngineerAgentFile:
    """Test the frontend-engineer agent file exists and is valid."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "frontend-engineer.md"

    @pytest.fixture
    def template_path(self) -> Path:
        """Get path to the template file."""
        return get_project_root() / "templates" / "agents" / "frontend-engineer.md"

    def test_agent_file_exists(self, agent_path: Path) -> None:
        """Agent file should exist in .claude/agents/."""
        assert agent_path.exists(), f"Agent file not found at {agent_path}"
        assert agent_path.is_file(), f"Expected {agent_path} to be a file"

    def test_agent_file_is_readable(self, agent_path: Path) -> None:
        """Agent file should be readable with UTF-8 encoding."""
        content = safe_read_file(agent_path)
        assert content is not None, f"Could not read agent file at {agent_path}"
        assert len(content) > 100, "Agent file appears to be too short"

    def test_template_file_exists(self, template_path: Path) -> None:
        """Template file should exist in templates/agents/."""
        assert template_path.exists(), f"Template file not found at {template_path}"
        assert template_path.is_file(), f"Expected {template_path} to be a file"

    def test_files_are_identical(self, agent_path: Path, template_path: Path) -> None:
        """Agent file and template file should be identical."""
        agent_content = safe_read_file(agent_path)
        template_content = safe_read_file(template_path)

        assert agent_content is not None, "Could not read agent file"
        assert template_content is not None, "Could not read template file"
        assert agent_content == template_content, (
            "Agent file and template file should be identical"
        )


class TestFrontendEngineerFrontmatter:
    """Test the YAML frontmatter of the frontend-engineer agent."""

    @pytest.fixture
    def agent_content(self) -> str:
        """Get agent file content."""
        path = get_project_root() / ".claude" / "agents" / "frontend-engineer.md"
        content = safe_read_file(path)
        if content is None:
            pytest.fail(f"Could not read agent file at {path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> Dict[str, str]:
        """Parse frontmatter from agent content."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(str(e))

    def test_has_frontmatter(self, agent_content: str) -> None:
        """Agent file should have YAML frontmatter."""
        assert agent_content.startswith("---\n"), (
            "Agent file should start with YAML frontmatter delimiter"
        )
        assert "\n---\n" in agent_content, (
            "Agent file should have closing YAML frontmatter delimiter"
        )

    def test_has_required_fields(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have all required fields."""
        for field in REQUIRED_FRONTMATTER_FIELDS:
            assert field in frontmatter, f"Frontmatter missing required field: {field}"

    def test_name_is_correct(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter name should be 'frontend-engineer'."""
        assert frontmatter.get("name") == AGENT_NAME, (
            f"Expected name '{AGENT_NAME}', got '{frontmatter.get('name')}'"
        )

    def test_color_is_correct(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter color should be 'cyan'."""
        assert frontmatter.get("color") == EXPECTED_COLOR, (
            f"Expected color '{EXPECTED_COLOR}', got '{frontmatter.get('color')}'"
        )

    def test_description_is_substantial(self, frontmatter: Dict[str, str]) -> None:
        """Description should be substantial (>50 characters)."""
        description = frontmatter.get("description", "")
        assert len(description) > 50, (
            f"Description too short ({len(description)} chars), should be >50"
        )


class TestFrontendEngineerTools:
    """Test the tools configuration for the frontend-engineer agent."""

    @pytest.fixture
    def tools_list(self) -> list[str]:
        """Get the list of tools from frontmatter."""
        path = get_project_root() / ".claude" / "agents" / "frontend-engineer.md"
        content = safe_read_file(path)
        if content is None:
            pytest.fail(f"Could not read agent file at {path}")

        try:
            frontmatter = parse_frontmatter(content)
        except ValueError as e:
            pytest.fail(str(e))

        tools_str = frontmatter.get("tools", "")
        return [t.strip() for t in tools_str.split(",") if t.strip()]

    def test_has_all_expected_tools(self, tools_list: list[str]) -> None:
        """Frontend engineer should have all expected tools."""
        for tool in EXPECTED_TOOLS:
            assert tool in tools_list, (
                f"Frontend engineer missing expected tool: {tool}"
            )

    def test_has_file_manipulation_tools(self, tools_list: list[str]) -> None:
        """Frontend engineer should have file manipulation tools."""
        file_tools = ["Read", "Write", "Edit"]
        for tool in file_tools:
            assert tool in tools_list, (
                f"Frontend engineer needs {tool} tool for file manipulation"
            )

    def test_has_code_search_tools(self, tools_list: list[str]) -> None:
        """Frontend engineer should have code search tools."""
        search_tools = ["Glob", "Grep"]
        for tool in search_tools:
            assert tool in tools_list, (
                f"Frontend engineer needs {tool} tool for code search"
            )


class TestFrontendEngineerDescription:
    """Test the description field matches the agent's purpose."""

    @pytest.fixture
    def description(self) -> str:
        """Get the description from frontmatter."""
        path = get_project_root() / ".claude" / "agents" / "frontend-engineer.md"
        content = safe_read_file(path)
        if content is None:
            pytest.fail(f"Could not read agent file at {path}")

        try:
            frontmatter = parse_frontmatter(content)
        except ValueError as e:
            pytest.fail(str(e))

        return frontmatter.get("description", "").lower()

    def test_mentions_frontend(self, description: str) -> None:
        """Description should mention frontend development."""
        assert "frontend" in description, (
            "Description should mention 'frontend' development"
        )

    def test_mentions_react_or_components(self, description: str) -> None:
        """Description should mention React or component development."""
        assert "react" in description or "component" in description, (
            "Description should mention React or component development"
        )

    def test_mentions_typescript_or_type_safety(self, description: str) -> None:
        """Description should mention TypeScript or type safety."""
        assert "typescript" in description or "type" in description, (
            "Description should mention TypeScript or type safety"
        )


class TestFrontendEngineerContent:
    """Test the content sections of the frontend-engineer agent."""

    @pytest.fixture
    def agent_content(self) -> str:
        """Get agent file content."""
        path = get_project_root() / ".claude" / "agents" / "frontend-engineer.md"
        content = safe_read_file(path)
        if content is None:
            pytest.fail(f"Could not read agent file at {path}")
        return content

    def test_has_required_sections(self, agent_content: str) -> None:
        """Agent should have all required content sections."""
        for section in REQUIRED_CONTENT_SECTIONS:
            assert section in agent_content, (
                f"Agent missing required section: {section}"
            )

    def test_mentions_react(self, agent_content: str) -> None:
        """Agent content should mention React."""
        assert "React" in agent_content, "Agent should mention React"

    def test_mentions_nextjs(self, agent_content: str) -> None:
        """Agent content should mention Next.js."""
        assert "Next.js" in agent_content or "NextJS" in agent_content, (
            "Agent should mention Next.js"
        )

    def test_mentions_typescript(self, agent_content: str) -> None:
        """Agent content should mention TypeScript."""
        assert "TypeScript" in agent_content, "Agent should mention TypeScript"

    def test_mentions_accessibility(self, agent_content: str) -> None:
        """Agent content should mention accessibility."""
        content_lower = agent_content.lower()
        assert "accessibility" in content_lower or "a11y" in content_lower, (
            "Agent should mention accessibility"
        )

    def test_mentions_performance(self, agent_content: str) -> None:
        """Agent content should mention performance."""
        assert "performance" in agent_content.lower(), (
            "Agent should mention performance"
        )

    def test_has_checkbox_items(self, agent_content: str) -> None:
        """Agent should have checkbox items for verification."""
        assert "- [ ]" in agent_content, (
            "Agent should have checkbox items for code quality checklist"
        )
