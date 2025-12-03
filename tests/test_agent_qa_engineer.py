"""Tests for the qa-engineer agent.

This module validates the qa-engineer agent definition and template files,
ensuring they contain all required metadata, tools, and documentation sections
for effective test automation and quality assurance workflows.
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
AGENT_NAME = "qa-engineer"
EXPECTED_COLOR = "yellow"
EXPECTED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "tools", "color"]
REQUIRED_CONTENT_SECTIONS = [
    "## Core Testing Stack",
    "## Test Implementation",
    "## Quality Checklist",
]


class TestQAEngineerAgentFile:
    """Test the qa-engineer agent file exists and is valid."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "qa-engineer.md"

    @pytest.fixture
    def template_path(self) -> Path:
        """Get path to the template file."""
        return get_project_root() / "templates" / "agents" / "qa-engineer.md"

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
            f"Agent file ({agent_path}) and template file ({template_path}) "
            "should be identical. The template is the authoritative source."
        )


class TestQAEngineerFrontmatter:
    """Test the YAML frontmatter of the qa-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "qa-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> Dict[str, str]:
        """Extract and parse YAML frontmatter."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(f"Failed to parse frontmatter: {e}")

    def test_has_frontmatter(self, agent_content: str) -> None:
        """Agent file should have YAML frontmatter."""
        assert agent_content.startswith("---\n"), (
            "Agent file must start with YAML frontmatter delimiter '---\\n'"
        )
        assert "\n---\n" in agent_content, (
            "Agent file must have closing YAML frontmatter delimiter '\\n---\\n'"
        )

    def test_frontmatter_is_valid(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should be parseable as key-value pairs."""
        assert isinstance(frontmatter, dict), (
            f"Frontmatter should be a dictionary, got {type(frontmatter).__name__}"
        )
        assert len(frontmatter) > 0, "Frontmatter should have at least one field"

    def test_has_required_fields(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have all required fields."""
        for field in REQUIRED_FRONTMATTER_FIELDS:
            assert field in frontmatter, (
                f"Frontmatter must have '{field}' field. "
                f"Available fields: {', '.join(frontmatter.keys())}"
            )

    def test_name_field(self, frontmatter: Dict[str, str]) -> None:
        """Agent name should be correct."""
        assert frontmatter.get("name") == AGENT_NAME, (
            f"Agent name should be '{AGENT_NAME}', got '{frontmatter.get('name')}'"
        )

    def test_description_field(self, frontmatter: Dict[str, str]) -> None:
        """Description should be substantial."""
        description = frontmatter.get("description", "")
        assert isinstance(description, str), (
            f"Description should be a string, got {type(description).__name__}"
        )
        assert len(description) > 50, (
            f"Description should be substantial (>50 chars), "
            f"got {len(description)} chars"
        )

    def test_color_field(self, frontmatter: Dict[str, str]) -> None:
        """Color should be correct."""
        assert frontmatter.get("color") == EXPECTED_COLOR, (
            f"QA engineer color should be '{EXPECTED_COLOR}', "
            f"got '{frontmatter.get('color')}'"
        )


class TestQAEngineerTools:
    """Test the tools configuration for the qa-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "qa-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> Dict[str, str]:
        """Extract and parse YAML frontmatter."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(f"Failed to parse frontmatter: {e}")

    @pytest.fixture
    def tools(self, frontmatter: Dict[str, str]) -> list[str]:
        """Extract tools list from frontmatter."""
        tools_str = frontmatter.get("tools", "")
        return [t.strip() for t in tools_str.split(",") if t.strip()]

    def test_has_tools_configured(self, tools: list[str]) -> None:
        """Agent should have tools configured."""
        assert len(tools) > 0, (
            "Agent should have tools configured. "
            "Tools are required for agent functionality."
        )

    def test_has_all_required_tools(self, tools: list[str]) -> None:
        """Agent should have all required tools."""
        for tool in EXPECTED_TOOLS:
            assert tool in tools, (
                f"QA engineer must have '{tool}' tool. "
                f"Available tools: {', '.join(tools)}"
            )

    def test_has_file_manipulation_tools(self, tools: list[str]) -> None:
        """QA engineer should have file manipulation tools."""
        assert "Read" in tools, "QA engineer needs 'Read' tool to examine code"
        assert "Write" in tools, "QA engineer needs 'Write' tool to create test files"
        assert "Edit" in tools, "QA engineer needs 'Edit' tool to modify tests"

    def test_has_code_search_tools(self, tools: list[str]) -> None:
        """QA engineer should have code search tools."""
        assert "Glob" in tools, "QA engineer needs 'Glob' tool to find test files"
        assert "Grep" in tools, "QA engineer needs 'Grep' tool to search code"

    def test_has_bash_tool(self, tools: list[str]) -> None:
        """QA engineer should have Bash tool for running tests."""
        assert "Bash" in tools, (
            "QA engineer needs 'Bash' tool to run test commands and pytest"
        )


class TestQAEngineerDescription:
    """Test the description field matches the agent's purpose."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "qa-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> Dict[str, str]:
        """Extract and parse YAML frontmatter."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(f"Failed to parse frontmatter: {e}")

    @pytest.fixture
    def description(self, frontmatter: Dict[str, str]) -> str:
        """Get description from frontmatter."""
        return frontmatter.get("description", "").lower()

    def test_description_mentions_testing(self, description: str) -> None:
        """Description should mention testing."""
        assert "test" in description, (
            "Description must mention 'test' as core QA responsibility"
        )

    def test_description_mentions_qa(self, description: str) -> None:
        """Description should mention QA or quality assurance."""
        assert "qa" in description or "quality" in description, (
            "Description must mention 'qa' or 'quality' for QA engineering role"
        )

    def test_description_mentions_coverage(self, description: str) -> None:
        """Description should mention test coverage."""
        assert "coverage" in description, (
            "Description must mention 'coverage' as QA metric"
        )


class TestQAEngineerContent:
    """Test the content of the qa-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "qa-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    def test_has_required_sections(self, agent_content: str) -> None:
        """Agent should have all required sections."""
        for section in REQUIRED_CONTENT_SECTIONS:
            assert section in agent_content, f"Agent must have '{section}' section"

    def test_mentions_pytest(self, agent_content: str) -> None:
        """Agent should mention pytest."""
        assert "pytest" in agent_content, (
            "Agent must mention 'pytest' as the primary Python testing framework"
        )

    def test_mentions_testing_pyramid(self, agent_content: str) -> None:
        """Agent should mention testing pyramid."""
        content_lower = agent_content.lower()
        assert "pyramid" in content_lower, (
            "Agent must mention testing pyramid for test distribution strategy"
        )

    def test_mentions_unit_tests(self, agent_content: str) -> None:
        """Agent should mention unit tests."""
        content_lower = agent_content.lower()
        assert "unit test" in content_lower, (
            "Agent must mention unit tests as foundation of testing pyramid"
        )

    def test_mentions_integration_tests(self, agent_content: str) -> None:
        """Agent should mention integration tests."""
        content_lower = agent_content.lower()
        assert "integration test" in content_lower, (
            "Agent must mention integration tests for API and database testing"
        )

    def test_mentions_e2e_tests(self, agent_content: str) -> None:
        """Agent should mention E2E tests."""
        content_lower = agent_content.lower()
        assert "e2e" in content_lower or "end-to-end" in content_lower, (
            "Agent must mention E2E tests for critical user journeys"
        )

    def test_mentions_coverage_guidelines(self, agent_content: str) -> None:
        """Agent should mention coverage guidelines."""
        content_lower = agent_content.lower()
        assert "coverage" in content_lower, (
            "Agent must mention test coverage guidelines and targets"
        )

    def test_has_checkbox_items(self, agent_content: str) -> None:
        """Agent should have checkbox items for verification."""
        assert "- [ ]" in agent_content, (
            "Agent should have checkbox items '- [ ]' for task verification"
        )

    def test_mentions_fixtures(self, agent_content: str) -> None:
        """Agent should mention test fixtures."""
        content_lower = agent_content.lower()
        assert "fixture" in content_lower, (
            "Agent must mention test fixtures for test setup/teardown"
        )

    def test_mentions_mocking(self, agent_content: str) -> None:
        """Agent should mention mocking."""
        content_lower = agent_content.lower()
        assert "mock" in content_lower, (
            "Agent must mention mocking for isolating test units"
        )
