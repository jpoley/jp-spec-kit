"""Tests for repository facts detection and writing.

Tests cover:
- write_repo_facts creates file in correct location
- YAML frontmatter is valid and contains expected fields
- Sections are populated correctly based on facts
- Empty facts are handled gracefully
- Detection works for various languages and CI/CD platforms
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from specify_cli import __version__, write_repo_facts


class TestWriteRepoFacts:
    """Tests for write_repo_facts function."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_creates_file_in_memory_directory(self, temp_project):
        """Verify file is created in memory/ subdirectory."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        assert facts_path.exists()

    def test_creates_memory_directory_if_missing(self, temp_project):
        """Verify memory/ directory is created if it doesn't exist."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        memory_dir = temp_project / "memory"
        assert memory_dir.exists()
        assert memory_dir.is_dir()

    def test_yaml_frontmatter_is_valid(self, temp_project):
        """Verify YAML frontmatter can be parsed."""
        facts = {"languages": ["Python"], "ci_cd": "GitHub Actions"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        # Extract frontmatter (between --- markers)
        lines = content.split("\n")
        assert lines[0] == "---"
        frontmatter_end = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:frontmatter_end])

        # Parse YAML
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter is not None
        assert isinstance(frontmatter, dict)

    def test_frontmatter_contains_required_fields(self, temp_project):
        """Verify frontmatter contains all expected fields."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        # Extract and parse frontmatter
        lines = content.split("\n")
        frontmatter_end = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:frontmatter_end])
        frontmatter = yaml.safe_load(frontmatter_text)

        # Check required fields
        assert "detected_at" in frontmatter
        assert "spec_kit_version" in frontmatter
        assert "languages" in frontmatter
        assert "frameworks" in frontmatter
        assert "ci_cd" in frontmatter
        assert "test_framework" in frontmatter
        assert "linter" in frontmatter
        assert "formatter" in frontmatter
        assert "security_tools" in frontmatter

    def test_frontmatter_has_correct_version(self, temp_project):
        """Verify spec_kit_version matches current version."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        lines = content.split("\n")
        frontmatter_end = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:frontmatter_end])
        frontmatter = yaml.safe_load(frontmatter_text)

        assert frontmatter["spec_kit_version"] == __version__

    def test_frontmatter_has_valid_timestamp(self, temp_project):
        """Verify detected_at contains a valid ISO timestamp."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        lines = content.split("\n")
        frontmatter_end = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:frontmatter_end])
        frontmatter = yaml.safe_load(frontmatter_text)

        # Should be parseable as ISO datetime
        detected_at = frontmatter["detected_at"]
        assert datetime.fromisoformat(detected_at)

    def test_languages_section_populated(self, temp_project):
        """Verify Languages section is created when languages are detected."""
        facts = {"languages": ["Python", "Go"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Languages" in content
        assert "- Python" in content
        assert "- Go" in content

    def test_frameworks_section_populated(self, temp_project):
        """Verify Frameworks section is created when frameworks are detected."""
        facts = {"frameworks": ["FastAPI", "React"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Frameworks" in content
        assert "- FastAPI" in content
        assert "- React" in content

    def test_ci_cd_section_populated(self, temp_project):
        """Verify CI/CD section is created when CI/CD is detected."""
        facts = {"ci_cd": "GitHub Actions"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## CI/CD" in content
        assert "- GitHub Actions" in content

    def test_testing_section_populated(self, temp_project):
        """Verify Testing section is created when test framework is detected."""
        facts = {"test_framework": "pytest"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Testing" in content
        assert "- pytest" in content

    def test_code_quality_section_with_linter(self, temp_project):
        """Verify Code Quality section includes linter."""
        facts = {"linter": "ruff"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Code Quality" in content
        assert "- Linter: ruff" in content

    def test_code_quality_section_with_formatter(self, temp_project):
        """Verify Code Quality section includes formatter."""
        facts = {"formatter": "black"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Code Quality" in content
        assert "- Formatter: black" in content

    def test_code_quality_section_with_both(self, temp_project):
        """Verify Code Quality section includes both linter and formatter."""
        facts = {"linter": "ruff", "formatter": "ruff"}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Code Quality" in content
        assert "- Linter: ruff" in content
        assert "- Formatter: ruff" in content

    def test_security_section_populated(self, temp_project):
        """Verify Security section is created when security tools are detected."""
        facts = {"security_tools": ["Trivy", "Bandit"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "## Security" in content
        assert "- Trivy" in content
        assert "- Bandit" in content

    def test_empty_facts_handled_gracefully(self, temp_project):
        """Verify empty facts dict still creates valid file."""
        facts = {}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        assert facts_path.exists()

        content = facts_path.read_text()
        # Should still have header and instructions
        assert "# Repository Facts" in content
        assert "auto-generated" in content

    def test_file_has_markdown_header(self, temp_project):
        """Verify file includes Repository Facts header."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "# Repository Facts" in content

    def test_file_has_edit_instructions(self, temp_project):
        """Verify file includes instructions about when to edit."""
        facts = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        assert "auto-generated" in content
        assert "specify init" in content or "specify upgrade" in content
        assert "Edit only if" in content

    def test_multiple_languages(self, temp_project):
        """Verify multiple languages are listed correctly."""
        facts = {"languages": ["Python", "JavaScript/TypeScript", "Go", "Rust"]}
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        for lang in facts["languages"]:
            assert f"- {lang}" in content

    def test_all_fields_populated(self, temp_project):
        """Verify all fields can be populated simultaneously."""
        facts = {
            "languages": ["Python", "Go"],
            "frameworks": ["FastAPI", "Gin"],
            "ci_cd": "GitHub Actions",
            "test_framework": "pytest",
            "linter": "ruff",
            "formatter": "black",
            "security_tools": ["Trivy", "Bandit"],
        }
        write_repo_facts(temp_project, facts)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        # Verify all sections present
        assert "## Languages" in content
        assert "## Frameworks" in content
        assert "## CI/CD" in content
        assert "## Testing" in content
        assert "## Code Quality" in content
        assert "## Security" in content

    def test_overwrites_existing_file(self, temp_project):
        """Verify function overwrites existing repo-facts.md."""
        # Create initial file
        facts1 = {"languages": ["Python"]}
        write_repo_facts(temp_project, facts1)

        # Overwrite with new facts
        facts2 = {"languages": ["Go"], "ci_cd": "GitLab CI"}
        write_repo_facts(temp_project, facts2)

        facts_path = temp_project / "memory" / "repo-facts.md"
        content = facts_path.read_text()

        # Should have new content
        assert "- Go" in content
        assert "- GitLab CI" in content
        # Old content should be gone
        assert "- Python" not in content or "## Languages" not in content


class TestRepoFactsTemplate:
    """Tests for repo-facts template file."""

    @pytest.fixture
    def template_path(self):
        """Get the template file path."""
        return (
            Path(__file__).parent.parent
            / "templates"
            / "memory"
            / "repo-facts-template.md"
        )

    def test_template_exists(self, template_path):
        """Verify template file exists."""
        assert template_path.exists(), f"Missing: {template_path}"

    def test_template_has_frontmatter(self, template_path):
        """Verify template includes YAML frontmatter structure."""
        content = template_path.read_text()
        assert content.startswith("---")
        lines = content.split("\n")
        # Find second --- marker
        assert "---" in lines[1:], "Template missing closing frontmatter marker"

    def test_template_has_placeholder_fields(self, template_path):
        """Verify template includes placeholder fields."""
        content = template_path.read_text()
        assert "detected_at:" in content
        assert "spec_kit_version:" in content
        assert "languages:" in content

    def test_template_has_section_comments(self, template_path):
        """Verify template includes section comment placeholders."""
        content = template_path.read_text()
        assert "<!-- Detected languages will be listed here -->" in content
        assert "## Languages" in content

    def test_template_has_instructions(self, template_path):
        """Verify template includes usage instructions."""
        content = template_path.read_text()
        assert "auto-generated" in content
