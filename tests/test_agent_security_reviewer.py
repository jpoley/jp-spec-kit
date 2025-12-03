"""Tests for the security-reviewer agent."""

import re
from pathlib import Path

import pytest


@pytest.fixture
def agent_file_path() -> Path:
    """Return path to security-reviewer agent file."""
    return Path(".claude/agents/security-reviewer.md")


@pytest.fixture
def template_file_path() -> Path:
    """Return path to security-reviewer template file."""
    return Path("templates/agents/security-reviewer.md")


@pytest.fixture
def agent_content(agent_file_path: Path) -> str:
    """Return content of the security-reviewer agent file."""
    return agent_file_path.read_text()


@pytest.fixture
def frontmatter(agent_content: str) -> dict:
    """Extract and parse YAML frontmatter from agent content."""
    match = re.match(r"^---\n(.*?)\n---\n", agent_content, re.DOTALL)
    if not match:
        pytest.fail("No YAML frontmatter found in agent file")

    # Parse frontmatter manually since description contains colons
    frontmatter_text = match.group(1)
    result = {}

    for line in frontmatter_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


class TestSecurityReviewerAgentFile:
    """Test the security-reviewer agent file exists and is valid."""

    def test_agent_file_exists(self, agent_file_path: Path):
        """Agent file should exist in .claude/agents/."""
        assert agent_file_path.exists(), f"Agent file not found at {agent_file_path}"

    def test_template_file_exists(self, template_file_path: Path):
        """Template file should exist in templates/agents/."""
        assert template_file_path.exists(), (
            f"Template file not found at {template_file_path}"
        )

    def test_files_are_identical(self, agent_file_path: Path, template_file_path: Path):
        """Agent file and template file should be identical."""
        agent_content = agent_file_path.read_text()
        template_content = template_file_path.read_text()
        assert agent_content == template_content, (
            "Agent file and template file should be identical"
        )


class TestSecurityReviewerFrontmatter:
    """Test the YAML frontmatter of the security-reviewer agent."""

    def test_has_frontmatter(self, agent_content: str):
        """Agent file should have YAML frontmatter."""
        assert agent_content.startswith("---\n"), (
            "Agent file should start with YAML frontmatter delimiter"
        )
        assert "\n---\n" in agent_content, (
            "Agent file should have closing YAML frontmatter delimiter"
        )

    def test_frontmatter_is_valid(self, frontmatter: dict):
        """Frontmatter should be parseable as key-value pairs."""
        assert isinstance(frontmatter, dict), "Frontmatter should be a dictionary"
        assert len(frontmatter) > 0, "Frontmatter should have at least one field"

    def test_has_name_field(self, frontmatter: dict):
        """Frontmatter should have a name field."""
        assert "name" in frontmatter, "Frontmatter should have a 'name' field"
        assert frontmatter["name"] == "security-reviewer"

    def test_has_description_field(self, frontmatter: dict):
        """Frontmatter should have a description field."""
        assert "description" in frontmatter, (
            "Frontmatter should have a 'description' field"
        )
        assert isinstance(frontmatter["description"], str), (
            "Description should be a string"
        )
        assert len(frontmatter["description"]) > 50, "Description should be substantial"

    def test_has_tools_field(self, frontmatter: dict):
        """Frontmatter should have a tools field."""
        assert "tools" in frontmatter, "Frontmatter should have a 'tools' field"

    def test_has_color_field(self, frontmatter: dict):
        """Frontmatter should have a color field."""
        assert "color" in frontmatter, "Frontmatter should have a 'color' field"
        assert frontmatter["color"] == "red"


class TestSecurityReviewerTools:
    """Test the tools configuration for the security-reviewer agent."""

    def test_tools_list(self, frontmatter: dict):
        """Security reviewer should have read-only tools."""
        tools = frontmatter.get("tools", "").split(", ")
        # Security reviewer has read-only access
        expected_tools = ["Read", "Glob", "Grep", "Bash"]

        assert len(tools) > 0, "Agent should have tools configured"

        for tool in expected_tools:
            assert tool in tools, f"Security reviewer should have {tool} tool"

    def test_has_read_only_tools(self, frontmatter: dict):
        """Security reviewer should have read-only tools."""
        tools = frontmatter.get("tools", "").split(", ")

        # Security reviewers need to read code but not modify it
        assert "Read" in tools, "Security reviewer needs Read tool"
        assert "Write" not in tools, (
            "Security reviewer should NOT have Write tool (read-only)"
        )
        assert "Edit" not in tools, (
            "Security reviewer should NOT have Edit tool (read-only)"
        )

    def test_has_code_search_tools(self, frontmatter: dict):
        """Security reviewer should have code search tools."""
        tools = frontmatter.get("tools", "").split(", ")

        # Security reviewers need to search codebases for vulnerabilities
        assert "Glob" in tools, "Security reviewer needs Glob tool"
        assert "Grep" in tools, "Security reviewer needs Grep tool"

    def test_has_bash_tool(self, frontmatter: dict):
        """Security reviewer should have Bash tool for running security scans."""
        tools = frontmatter.get("tools", "").split(", ")

        # Security reviewers need to run security scanning tools
        assert "Bash" in tools, "Security reviewer needs Bash tool"


class TestSecurityReviewerDescription:
    """Test the description field matches the agent's purpose."""

    def test_description_mentions_security(self, frontmatter: dict):
        """Description should mention security."""
        description = frontmatter["description"].lower()
        assert "security" in description, "Description should mention security"

    def test_description_mentions_vulnerability(self, frontmatter: dict):
        """Description should mention vulnerability assessment."""
        description = frontmatter["description"].lower()
        assert "vulnerability" in description or "vulnerabilities" in description, (
            "Description should mention vulnerabilities"
        )

    def test_description_mentions_review(self, frontmatter: dict):
        """Description should mention security review."""
        description = frontmatter["description"].lower()
        assert "review" in description, "Description should mention review"


class TestSecurityReviewerContent:
    """Test the content of the security-reviewer agent."""

    def test_has_security_review_scope(self, agent_content: str):
        """Agent should document security review scope."""
        assert (
            "## Security Review Scope" in agent_content
            or "Security Review" in agent_content
        ), "Agent should have Security Review Scope section"

    def test_mentions_owasp(self, agent_content: str):
        """Agent should mention OWASP Top 10."""
        assert "OWASP" in agent_content, "Agent should mention OWASP"

    def test_has_owasp_checklist(self, agent_content: str):
        """Agent should have OWASP Top 10 checklist."""
        content_lower = agent_content.lower()
        assert "owasp top 10" in content_lower or "owasp top" in content_lower, (
            "Agent should have OWASP Top 10 checklist"
        )

    def test_mentions_injection(self, agent_content: str):
        """Agent should mention injection vulnerabilities."""
        content_lower = agent_content.lower()
        assert "injection" in content_lower, "Agent should mention injection"

    def test_mentions_authentication(self, agent_content: str):
        """Agent should mention authentication security."""
        content_lower = agent_content.lower()
        assert "authentication" in content_lower, "Agent should mention authentication"

    def test_mentions_cryptography(self, agent_content: str):
        """Agent should mention cryptography."""
        content_lower = agent_content.lower()
        assert "crypt" in content_lower, "Agent should mention cryptographic security"

    def test_has_vulnerability_report_format(self, agent_content: str):
        """Agent should have vulnerability report format."""
        assert "Vulnerability Report" in agent_content or "Finding:" in agent_content, (
            "Agent should have vulnerability report format"
        )

    def test_mentions_severity(self, agent_content: str):
        """Agent should mention severity levels."""
        content_lower = agent_content.lower()
        assert "severity" in content_lower, (
            "Agent should mention severity classification"
        )

    def test_mentions_cwe(self, agent_content: str):
        """Agent should mention CWE (Common Weakness Enumeration)."""
        assert "CWE" in agent_content, "Agent should mention CWE"

    def test_mentions_slsa(self, agent_content: str):
        """Agent should mention SLSA (Supply-chain Levels for Software Artifacts)."""
        assert "SLSA" in agent_content, "Agent should mention SLSA"

    def test_has_security_scanning_commands(self, agent_content: str):
        """Agent should have security scanning commands."""
        content_lower = agent_content.lower()
        assert "scanning" in content_lower or "scan" in content_lower, (
            "Agent should have security scanning guidance"
        )

    def test_has_review_checklist(self, agent_content: str):
        """Agent should have a review checklist."""
        assert "## Review Checklist" in agent_content or "Checklist" in agent_content, (
            "Agent should have review checklist"
        )

    def test_has_checkbox_items(self, agent_content: str):
        """Agent should have checkbox items for verification."""
        assert "- [ ]" in agent_content, "Agent should have checkbox items"

    def test_mentions_read_only_access(self, agent_content: str):
        """Agent should mention it has read-only access."""
        content_lower = agent_content.lower()
        assert "read-only" in content_lower or "readonly" in content_lower, (
            "Agent should mention read-only access"
        )

    def test_provides_remediation_guidance(self, agent_content: str):
        """Agent should provide remediation guidance."""
        content_lower = agent_content.lower()
        assert "remediation" in content_lower, (
            "Agent should provide remediation guidance"
        )
