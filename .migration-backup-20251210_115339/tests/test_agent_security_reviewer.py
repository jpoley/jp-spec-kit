"""Tests for the security-reviewer agent.

This module provides comprehensive testing for the security-reviewer agent,
including frontmatter validation, tool configuration, and content verification.
"""

import re
from pathlib import Path
from typing import Dict

import pytest


def read_file_safely(path: Path) -> str:
    """Read file with UTF-8 encoding and proper error handling.

    Args:
        path: Path to the file to read

    Returns:
        str: Content of the file

    Raises:
        FileNotFoundError: If the file does not exist
        UnicodeDecodeError: If the file cannot be decoded as UTF-8
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding="utf-8")


def parse_frontmatter(content: str) -> Dict[str, str]:
    """Extract and parse YAML frontmatter from agent content.

    Args:
        content: Full content of the agent file

    Returns:
        Dict[str, str]: Parsed frontmatter as key-value pairs

    Raises:
        ValueError: If no valid frontmatter is found
    """
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        raise ValueError("No YAML frontmatter found in agent file")

    # Parse frontmatter manually since description contains colons
    frontmatter_text = match.group(1)
    result: Dict[str, str] = {}

    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    if not result:
        raise ValueError("Frontmatter is empty or invalid")

    return result


def get_tools_list(frontmatter: Dict[str, str]) -> list[str]:
    """Extract tools list from frontmatter.

    Args:
        frontmatter: Parsed frontmatter dictionary

    Returns:
        list[str]: List of tool names
    """
    tools_str = frontmatter.get("tools", "")
    if not tools_str:
        return []

    # Split by comma and strip whitespace
    return [tool.strip() for tool in tools_str.split(",") if tool.strip()]


@pytest.fixture
def agent_file_path() -> Path:
    """Return path to security-reviewer agent file.

    Returns:
        Path: Path to the agent definition file
    """
    return Path(".claude/agents/security-reviewer.md")


@pytest.fixture
def template_file_path() -> Path:
    """Return path to security-reviewer template file.

    Returns:
        Path: Path to the template file
    """
    return Path("templates/agents/security-reviewer.md")


@pytest.fixture
def agent_content(agent_file_path: Path) -> str:
    """Return content of the security-reviewer agent file.

    Args:
        agent_file_path: Path to the agent file

    Returns:
        str: Content of the agent file
    """
    return read_file_safely(agent_file_path)


@pytest.fixture
def template_content(template_file_path: Path) -> str:
    """Return content of the security-reviewer template file.

    Args:
        template_file_path: Path to the template file

    Returns:
        str: Content of the template file
    """
    return read_file_safely(template_file_path)


@pytest.fixture
def frontmatter(agent_content: str) -> Dict[str, str]:
    """Extract and parse YAML frontmatter from agent content.

    Args:
        agent_content: Full content of the agent file

    Returns:
        Dict[str, str]: Parsed frontmatter
    """
    try:
        return parse_frontmatter(agent_content)
    except ValueError as e:
        pytest.fail(f"Failed to parse frontmatter: {e}")


class TestSecurityReviewerAgentFile:
    """Test the security-reviewer agent file exists and is valid."""

    def test_agent_file_exists(self, agent_file_path: Path) -> None:
        """Agent file should exist in .claude/agents/.

        Args:
            agent_file_path: Path to the agent file
        """
        assert agent_file_path.exists(), (
            f"Agent file not found at {agent_file_path}. "
            "Expected security-reviewer.md in .claude/agents/"
        )

    def test_agent_file_is_readable(self, agent_file_path: Path) -> None:
        """Agent file should be readable with UTF-8 encoding.

        Args:
            agent_file_path: Path to the agent file
        """
        try:
            content = read_file_safely(agent_file_path)
            assert len(content) > 0, "Agent file is empty"
        except UnicodeDecodeError as e:
            pytest.fail(f"Agent file is not valid UTF-8: {e}")

    def test_template_file_exists(self, template_file_path: Path) -> None:
        """Template file should exist in templates/agents/.

        Args:
            template_file_path: Path to the template file
        """
        assert template_file_path.exists(), (
            f"Template file not found at {template_file_path}. "
            "Expected security-reviewer.md in templates/agents/"
        )

    def test_files_are_identical(
        self,
        agent_content: str,
        template_content: str,
    ) -> None:
        """Agent file and template file should be identical.

        Args:
            agent_content: Content of the agent file
            template_content: Content of the template file
        """
        assert agent_content == template_content, (
            "Agent file and template file should be identical. "
            "Any changes to .claude/agents/security-reviewer.md must also "
            "be made to templates/agents/security-reviewer.md"
        )


class TestSecurityReviewerFrontmatter:
    """Test the YAML frontmatter of the security-reviewer agent."""

    def test_has_frontmatter(self, agent_content: str) -> None:
        """Agent file should have YAML frontmatter.

        Args:
            agent_content: Full content of the agent file
        """
        assert agent_content.startswith("---\n"), (
            "Agent file should start with YAML frontmatter delimiter '---'"
        )
        assert "\n---\n" in agent_content, (
            "Agent file should have closing YAML frontmatter delimiter '---'"
        )

    def test_frontmatter_is_valid(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should be parseable as key-value pairs.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        assert isinstance(frontmatter, dict), "Frontmatter should be a dictionary"
        assert len(frontmatter) > 0, "Frontmatter should have at least one field"

    def test_has_required_fields(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have all required fields.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        required_fields = ["name", "description", "tools", "color"]
        missing_fields = [f for f in required_fields if f not in frontmatter]

        assert not missing_fields, (
            f"Frontmatter is missing required fields: {', '.join(missing_fields)}. "
            f"Expected fields: {', '.join(required_fields)}"
        )

    def test_has_name_field(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have a name field with correct value.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        assert "name" in frontmatter, "Frontmatter should have a 'name' field"
        assert frontmatter["name"] == "security-reviewer", (
            f"Agent name should be 'security-reviewer', got '{frontmatter['name']}'"
        )

    def test_has_description_field(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have a description field.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        assert "description" in frontmatter, (
            "Frontmatter should have a 'description' field"
        )
        description = frontmatter["description"]

        assert isinstance(description, str), "Description should be a string"
        assert len(description) > 50, (
            f"Description should be substantial (>50 chars), "
            f"got {len(description)} chars"
        )

    def test_has_tools_field(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have a tools field.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        assert "tools" in frontmatter, "Frontmatter should have a 'tools' field"
        tools_str = frontmatter["tools"]
        assert tools_str, "Tools field should not be empty"

    def test_has_color_field(self, frontmatter: Dict[str, str]) -> None:
        """Frontmatter should have a color field.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        assert "color" in frontmatter, "Frontmatter should have a 'color' field"
        assert frontmatter["color"] == "red", (
            f"Security agent color should be 'red', got '{frontmatter['color']}'"
        )


class TestSecurityReviewerTools:
    """Test the tools configuration for the security-reviewer agent."""

    def test_tools_list(self, frontmatter: Dict[str, str]) -> None:
        """Security reviewer should have required read-only tools.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        tools = get_tools_list(frontmatter)
        expected_tools = ["Read", "Glob", "Grep", "Bash"]

        assert len(tools) > 0, "Agent should have tools configured"

        missing_tools = [t for t in expected_tools if t not in tools]
        assert not missing_tools, (
            f"Security reviewer is missing required tools: "
            f"{', '.join(missing_tools)}. "
            f"Expected: {', '.join(expected_tools)}, "
            f"Got: {', '.join(tools)}"
        )

    def test_has_read_only_tools(self, frontmatter: Dict[str, str]) -> None:
        """Security reviewer should have read-only tools.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        tools = get_tools_list(frontmatter)

        # Security reviewers need to read code but not modify it
        assert "Read" in tools, "Security reviewer needs Read tool for code inspection"

        write_tools = [t for t in tools if t in ["Write", "Edit"]]
        assert not write_tools, (
            f"Security reviewer should NOT have write tools (read-only access). "
            f"Found: {', '.join(write_tools)}"
        )

    def test_has_code_search_tools(self, frontmatter: Dict[str, str]) -> None:
        """Security reviewer should have code search tools.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        tools = get_tools_list(frontmatter)

        # Security reviewers need to search codebases for vulnerabilities
        search_tools = ["Glob", "Grep"]
        missing_search_tools = [t for t in search_tools if t not in tools]

        assert not missing_search_tools, (
            f"Security reviewer needs search tools to find vulnerabilities. "
            f"Missing: {', '.join(missing_search_tools)}"
        )

    def test_has_bash_tool(self, frontmatter: Dict[str, str]) -> None:
        """Security reviewer should have Bash tool for running security scans.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        tools = get_tools_list(frontmatter)

        # Security reviewers need to run security scanning tools
        assert "Bash" in tools, (
            "Security reviewer needs Bash tool to run security scanners "
            "(bandit, safety, pip-audit, etc.)"
        )


class TestSecurityReviewerDescription:
    """Test the description field matches the agent's purpose."""

    def test_description_mentions_security(
        self,
        frontmatter: Dict[str, str],
    ) -> None:
        """Description should mention security.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        description = frontmatter["description"].lower()
        assert "security" in description, (
            "Description should mention 'security' to clearly indicate agent purpose"
        )

    def test_description_mentions_vulnerability(
        self,
        frontmatter: Dict[str, str],
    ) -> None:
        """Description should mention vulnerability assessment.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        description = frontmatter["description"].lower()
        has_vuln = "vulnerability" in description or "vulnerabilities" in description

        assert has_vuln, (
            "Description should mention 'vulnerability' or 'vulnerabilities' "
            "to indicate vulnerability assessment capability"
        )

    def test_description_mentions_review(
        self,
        frontmatter: Dict[str, str],
    ) -> None:
        """Description should mention security review.

        Args:
            frontmatter: Parsed frontmatter dictionary
        """
        description = frontmatter["description"].lower()
        assert "review" in description, (
            "Description should mention 'review' to indicate code review capability"
        )


class TestSecurityReviewerContent:
    """Test the content of the security-reviewer agent."""

    def test_has_security_review_scope(self, agent_content: str) -> None:
        """Agent should document security review scope.

        Args:
            agent_content: Full content of the agent file
        """
        has_scope = (
            "## Security Review Scope" in agent_content
            or "Security Review" in agent_content
        )
        assert has_scope, (
            "Agent should have 'Security Review Scope' section to define "
            "what areas are covered in security reviews"
        )

    def test_mentions_owasp(self, agent_content: str) -> None:
        """Agent should mention OWASP Top 10.

        Args:
            agent_content: Full content of the agent file
        """
        assert "OWASP" in agent_content, (
            "Agent should mention OWASP to reference industry-standard "
            "security vulnerability categories"
        )

    def test_has_owasp_checklist(self, agent_content: str) -> None:
        """Agent should have OWASP Top 10 checklist.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        has_owasp_top = "owasp top 10" in content_lower or "owasp top" in content_lower

        assert has_owasp_top, (
            "Agent should have 'OWASP Top 10' checklist to ensure "
            "comprehensive coverage of common vulnerabilities"
        )

    def test_mentions_injection(self, agent_content: str) -> None:
        """Agent should mention injection vulnerabilities.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        assert "injection" in content_lower, (
            "Agent should mention 'injection' vulnerabilities "
            "(SQL injection, command injection, etc.)"
        )

    def test_mentions_authentication(self, agent_content: str) -> None:
        """Agent should mention authentication security.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        assert "authentication" in content_lower, (
            "Agent should mention 'authentication' to cover auth security issues"
        )

    def test_mentions_cryptography(self, agent_content: str) -> None:
        """Agent should mention cryptography.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        assert "crypt" in content_lower, (
            "Agent should mention cryptographic security "
            "(encryption, hashing, key management)"
        )

    def test_has_vulnerability_report_format(self, agent_content: str) -> None:
        """Agent should have vulnerability report format.

        Args:
            agent_content: Full content of the agent file
        """
        has_report_format = (
            "Vulnerability Report" in agent_content or "Finding:" in agent_content
        )
        assert has_report_format, (
            "Agent should have vulnerability report format template "
            "for consistent reporting"
        )

    def test_mentions_severity(self, agent_content: str) -> None:
        """Agent should mention severity levels.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        assert "severity" in content_lower, (
            "Agent should mention 'severity' classification "
            "(Critical, High, Medium, Low)"
        )

    def test_mentions_cwe(self, agent_content: str) -> None:
        """Agent should mention CWE (Common Weakness Enumeration).

        Args:
            agent_content: Full content of the agent file
        """
        assert "CWE" in agent_content, (
            "Agent should mention CWE (Common Weakness Enumeration) "
            "for vulnerability classification"
        )

    def test_mentions_slsa(self, agent_content: str) -> None:
        """Agent should mention SLSA (Supply-chain Levels for Software Artifacts).

        Args:
            agent_content: Full content of the agent file
        """
        assert "SLSA" in agent_content, (
            "Agent should mention SLSA (Supply-chain Levels for Software Artifacts) "
            "for supply chain security"
        )

    def test_has_security_scanning_commands(self, agent_content: str) -> None:
        """Agent should have security scanning commands.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        has_scanning = "scanning" in content_lower or "scan" in content_lower

        assert has_scanning, (
            "Agent should have security scanning guidance "
            "(bandit, safety, pip-audit, npm audit, etc.)"
        )

    def test_has_review_checklist(self, agent_content: str) -> None:
        """Agent should have a review checklist.

        Args:
            agent_content: Full content of the agent file
        """
        has_checklist = (
            "## Review Checklist" in agent_content or "Checklist" in agent_content
        )
        assert has_checklist, (
            "Agent should have review checklist to ensure systematic security reviews"
        )

    def test_has_checkbox_items(self, agent_content: str) -> None:
        """Agent should have checkbox items for verification.

        Args:
            agent_content: Full content of the agent file
        """
        checkbox_count = agent_content.count("- [ ]")
        assert checkbox_count > 0, (
            "Agent should have checkbox items (- [ ]) for tracking "
            "security review progress"
        )
        assert checkbox_count >= 10, (
            f"Agent should have at least 10 checkbox items, found {checkbox_count}. "
            "More checkboxes ensure comprehensive security coverage."
        )

    def test_mentions_read_only_access(self, agent_content: str) -> None:
        """Agent should mention it has read-only access.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        has_read_only = "read-only" in content_lower or "readonly" in content_lower

        assert has_read_only, (
            "Agent should mention 'read-only' access to clarify that "
            "it analyzes but does not modify code"
        )

    def test_provides_remediation_guidance(self, agent_content: str) -> None:
        """Agent should provide remediation guidance.

        Args:
            agent_content: Full content of the agent file
        """
        content_lower = agent_content.lower()
        assert "remediation" in content_lower, (
            "Agent should provide 'remediation' guidance for fixing "
            "identified security issues"
        )
