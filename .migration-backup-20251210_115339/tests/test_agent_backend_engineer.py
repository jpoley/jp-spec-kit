"""Tests for the backend-engineer subagent.

These tests validate that the backend-engineer agent:
- Has valid YAML frontmatter with required fields
- Has correct tools configured for backend development
- Contains required sections for Python/API development
- Matches the template file in templates/agents/
"""

import re
from pathlib import Path
from typing import Optional

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


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse YAML frontmatter from markdown content.

    Handles the specific format used by Claude agent files where description
    values may contain unquoted colons (e.g., "user: text"). Uses simple
    key: value parsing with split on first colon.

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
    result: dict[str, str] = {}

    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("#"):
            # Split on first colon only to handle values containing colons
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


# Constants
AGENT_NAME = "backend-engineer"
EXPECTED_COLOR = "green"
EXPECTED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "tools", "color"]
REQUIRED_CONTENT_SECTIONS = [
    "## Core Technologies",
    "## Implementation Standards",
    "## Testing Approach",
]


class TestBackendEngineerAgentFile:
    """Test the backend-engineer agent file exists and is valid."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "backend-engineer.md"

    @pytest.fixture
    def template_path(self) -> Path:
        """Get path to the template file."""
        return get_project_root() / "templates" / "agents" / "backend-engineer.md"

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


class TestBackendEngineerFrontmatter:
    """Test the YAML frontmatter of the backend-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "backend-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> dict[str, str]:
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

    def test_frontmatter_is_valid(self, frontmatter: dict[str, str]) -> None:
        """Frontmatter should be parseable as key-value pairs."""
        assert isinstance(frontmatter, dict), (
            f"Frontmatter should be a dictionary, got {type(frontmatter).__name__}"
        )
        assert len(frontmatter) > 0, "Frontmatter should have at least one field"

    def test_has_required_fields(self, frontmatter: dict[str, str]) -> None:
        """Frontmatter should have all required fields."""
        for field in REQUIRED_FRONTMATTER_FIELDS:
            assert field in frontmatter, (
                f"Frontmatter must have '{field}' field. "
                f"Available fields: {', '.join(frontmatter.keys())}"
            )

    def test_name_field(self, frontmatter: dict[str, str]) -> None:
        """Agent name should be correct."""
        assert frontmatter.get("name") == AGENT_NAME, (
            f"Agent name should be '{AGENT_NAME}', got '{frontmatter.get('name')}'"
        )

    def test_description_field(self, frontmatter: dict[str, str]) -> None:
        """Description should be substantial."""
        description = frontmatter.get("description", "")
        assert isinstance(description, str), (
            f"Description should be a string, got {type(description).__name__}"
        )
        assert len(description) > 50, (
            f"Description should be substantial (>50 chars), "
            f"got {len(description)} chars"
        )

    def test_color_field(self, frontmatter: dict[str, str]) -> None:
        """Color should be correct."""
        assert frontmatter.get("color") == EXPECTED_COLOR, (
            f"Backend engineer color should be '{EXPECTED_COLOR}', "
            f"got '{frontmatter.get('color')}'"
        )


class TestBackendEngineerTools:
    """Test the tools configuration for the backend-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "backend-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> dict[str, str]:
        """Extract and parse YAML frontmatter."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(f"Failed to parse frontmatter: {e}")

    @pytest.fixture
    def tools(self, frontmatter: dict[str, str]) -> list[str]:
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
                f"Backend engineer must have '{tool}' tool. "
                f"Available tools: {', '.join(tools)}"
            )

    def test_has_file_manipulation_tools(self, tools: list[str]) -> None:
        """Backend engineer should have file manipulation tools."""
        assert "Read" in tools, "Backend engineer needs 'Read' tool to examine code"
        assert "Write" in tools, "Backend engineer needs 'Write' tool to create files"
        assert "Edit" in tools, "Backend engineer needs 'Edit' tool to modify code"

    def test_has_code_search_tools(self, tools: list[str]) -> None:
        """Backend engineer should have code search tools."""
        assert "Glob" in tools, "Backend engineer needs 'Glob' tool to find files"
        assert "Grep" in tools, "Backend engineer needs 'Grep' tool to search content"

    def test_has_bash_tool(self, tools: list[str]) -> None:
        """Backend engineer should have Bash tool for running commands."""
        assert "Bash" in tools, (
            "Backend engineer needs 'Bash' tool to run migrations, tests, and servers"
        )


class TestBackendEngineerDescription:
    """Test the description field matches the agent's purpose."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "backend-engineer.md"

    @pytest.fixture
    def agent_content(self, agent_path: Path) -> str:
        """Return content of the agent file."""
        content = safe_read_file(agent_path)
        if content is None:
            pytest.skip(f"Agent file not found: {agent_path}")
        return content

    @pytest.fixture
    def frontmatter(self, agent_content: str) -> dict[str, str]:
        """Extract and parse YAML frontmatter."""
        try:
            return parse_frontmatter(agent_content)
        except ValueError as e:
            pytest.fail(f"Failed to parse frontmatter: {e}")

    @pytest.fixture
    def description(self, frontmatter: dict[str, str]) -> str:
        """Get description from frontmatter."""
        return frontmatter.get("description", "").lower()

    def test_description_mentions_backend(self, description: str) -> None:
        """Description should mention backend development."""
        assert "backend" in description, (
            "Description must mention 'backend' development to clarify agent purpose"
        )

    def test_description_mentions_api(self, description: str) -> None:
        """Description should mention API work."""
        assert "api" in description, (
            "Description should mention 'API' work as a core backend responsibility"
        )

    def test_description_mentions_database(self, description: str) -> None:
        """Description should mention database work."""
        assert "database" in description or "db" in description, (
            "Description should mention 'database' or 'db' work as a core backend skill"
        )

    def test_description_mentions_python(self, description: str) -> None:
        """Description should mention Python."""
        assert "python" in description, (
            "Description should mention 'Python' as the primary backend language"
        )


class TestBackendEngineerContent:
    """Test the content of the backend-engineer agent."""

    @pytest.fixture
    def agent_path(self) -> Path:
        """Get path to the agent file."""
        return get_project_root() / ".claude" / "agents" / "backend-engineer.md"

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

    def test_mentions_python(self, agent_content: str) -> None:
        """Agent should mention Python."""
        assert "Python" in agent_content, (
            "Agent must mention 'Python' as the primary backend language"
        )

    def test_mentions_web_framework(self, agent_content: str) -> None:
        """Agent should mention a web framework."""
        assert "FastAPI" in agent_content or "Flask" in agent_content, (
            "Agent should mention 'FastAPI' or 'Flask' as web frameworks"
        )

    def test_mentions_databases(self, agent_content: str) -> None:
        """Agent should mention database systems."""
        assert "PostgreSQL" in agent_content or "SQLite" in agent_content, (
            "Agent should mention database systems like 'PostgreSQL' or 'SQLite'"
        )

    def test_mentions_security(self, agent_content: str) -> None:
        """Agent should mention security."""
        content_lower = agent_content.lower()
        assert "security" in content_lower, (
            "Agent must mention 'security' best practices. "
            "Security is critical for backend development."
        )

    def test_mentions_validation(self, agent_content: str) -> None:
        """Agent should mention input validation."""
        content_lower = agent_content.lower()
        assert "validation" in content_lower or "validate" in content_lower, (
            "Agent must mention input 'validation'. "
            "Validating user input is essential for security and data integrity."
        )

    def test_has_code_quality_section(self, agent_content: str) -> None:
        """Agent should have a code quality section."""
        assert (
            "## Code Quality Checklist" in agent_content
            or "Code Quality" in agent_content
        ), "Agent should have a 'Code Quality Checklist' section"

    def test_has_checkbox_items(self, agent_content: str) -> None:
        """Agent should have checkbox items for verification."""
        assert "- [ ]" in agent_content, (
            "Agent should have checkbox items '- [ ]' for task verification"
        )

    def test_mentions_type_hints(self, agent_content: str) -> None:
        """Agent should mention Python type hints."""
        assert "type hint" in agent_content.lower() or "Type hints" in agent_content, (
            "Agent must mention 'type hints' as a Python best practice"
        )
