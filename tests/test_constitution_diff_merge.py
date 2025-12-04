#!/usr/bin/env python3
"""Tests for constitution diff and merge commands."""

from typer.testing import CliRunner

from specify_cli import (
    app,
    detect_constitution_tier,
    extract_sections,
    is_non_negotiable_section,
)

runner = CliRunner()


class TestConstitutionHelpers:
    """Test helper functions for constitution operations."""

    def test_detect_tier_light(self):
        """Test detecting light tier from constitution content."""
        content = "# Constitution\n<!-- TIER: Light - Minimal controls -->"
        assert detect_constitution_tier(content) == "light"

    def test_detect_tier_medium(self):
        """Test detecting medium tier from constitution content."""
        content = "# Constitution\n<!-- TIER: Medium - Standard controls -->"
        assert detect_constitution_tier(content) == "medium"

    def test_detect_tier_heavy(self):
        """Test detecting heavy tier from constitution content."""
        content = "# Constitution\n<!-- TIER: Heavy - Enterprise controls -->"
        assert detect_constitution_tier(content) == "heavy"

    def test_detect_tier_case_insensitive(self):
        """Test tier detection is case insensitive."""
        content = "# Constitution\n<!-- TIER: MEDIUM -->"
        assert detect_constitution_tier(content) == "medium"

    def test_detect_tier_none_when_missing(self):
        """Test returns None when tier marker is missing."""
        content = "# Constitution\nNo tier marker here"
        assert detect_constitution_tier(content) is None

    def test_extract_sections_single(self):
        """Test extracting a single section from constitution."""
        content = """
# Constitution
<!-- SECTION:QUALITY:BEGIN -->
Test quality standards
<!-- SECTION:QUALITY:END -->
"""
        sections = extract_sections(content)
        assert "QUALITY" in sections
        assert "Test quality standards" in sections["QUALITY"]

    def test_extract_sections_multiple(self):
        """Test extracting multiple sections from constitution."""
        content = """
# Constitution
<!-- SECTION:QUALITY:BEGIN -->
Quality content
<!-- SECTION:QUALITY:END -->

<!-- SECTION:GIT:BEGIN -->
Git content
<!-- SECTION:GIT:END -->
"""
        sections = extract_sections(content)
        assert len(sections) == 2
        assert "QUALITY" in sections
        assert "GIT" in sections
        assert "Quality content" in sections["QUALITY"]
        assert "Git content" in sections["GIT"]

    def test_extract_sections_with_multiline(self):
        """Test extracting sections with multiline content."""
        content = """
<!-- SECTION:TEST:BEGIN -->
Line 1
Line 2
Line 3
<!-- SECTION:TEST:END -->
"""
        sections = extract_sections(content)
        assert "TEST" in sections
        assert "Line 1" in sections["TEST"]
        assert "Line 2" in sections["TEST"]
        assert "Line 3" in sections["TEST"]

    def test_extract_sections_empty_content(self):
        """Test extracting sections from empty content."""
        sections = extract_sections("")
        assert len(sections) == 0

    def test_is_non_negotiable_section_true(self):
        """Test detecting NON-NEGOTIABLE sections."""
        content = """
## Git Requirements (NON-NEGOTIABLE)

<!-- SECTION:GIT:BEGIN -->
All commits must be signed
<!-- SECTION:GIT:END -->
"""
        assert is_non_negotiable_section(content, "GIT") is True

    def test_is_non_negotiable_section_false(self):
        """Test detecting regular sections."""
        content = """
## Git Requirements

<!-- SECTION:GIT:BEGIN -->
All commits should be signed
<!-- SECTION:GIT:END -->
"""
        assert is_non_negotiable_section(content, "GIT") is False


class TestConstitutionDiff:
    """Test constitution diff command."""

    def test_diff_no_constitution(self, tmp_path, monkeypatch):
        """Test diff command when no constitution exists."""
        # Change to temp directory without constitution
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "diff"])

        assert result.exit_code == 1
        assert "No constitution found" in result.stdout

    def test_diff_identical_constitution(self, tmp_path, monkeypatch):
        """Test diff when constitution matches template exactly."""
        # Create memory directory and light constitution
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Use the light template
        from specify_cli import CONSTITUTION_TEMPLATES

        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(CONSTITUTION_TEMPLATES["light"])

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "diff"])

        assert result.exit_code == 0
        assert "up to date" in result.stdout.lower()

    def test_diff_with_modifications(self, tmp_path, monkeypatch):
        """Test diff when constitution has modifications."""
        # Create memory directory
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create a modified light constitution
        content = """# My Project Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->

## Core Principles

### Simplicity First
Keep things simple. Ship fast, iterate quickly. Avoid over-engineering.

### Working Software
Prioritize working software over documentation. Code that runs is better than perfect designs.

### Pragmatic Quality
<!-- SECTION:QUALITY:BEGIN -->
- Write tests for critical paths ONLY
- Fix bugs eventually
- Code review is optional
<!-- SECTION:QUALITY:END -->
"""
        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "diff"])

        assert result.exit_code == 0
        assert "section(s) differ" in result.stdout.lower()
        assert "QUALITY" in result.stdout

    def test_diff_with_explicit_tier(self, tmp_path, monkeypatch):
        """Test diff with explicit tier specification."""
        # Create memory directory and constitution without tier marker
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create constitution without tier marker
        content = """# My Project Constitution

## Core Principles

### Quality-Driven Development
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
Code quality is important
<!-- SECTION:QUALITY_PRINCIPLES:END -->
"""
        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "diff", "--tier", "medium"])

        # Should work with explicit tier
        assert result.exit_code == 0

    def test_diff_invalid_tier(self, tmp_path, monkeypatch):
        """Test diff with invalid tier specification."""
        # Create memory directory and constitution
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text("# Constitution\n<!-- TIER: Light -->")

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "diff", "--tier", "invalid"])

        assert result.exit_code == 1
        assert "Invalid tier" in result.stdout


class TestConstitutionMerge:
    """Test constitution merge command."""

    def test_merge_no_constitution(self, tmp_path, monkeypatch):
        """Test merge command when no constitution exists."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "merge"])

        assert result.exit_code == 1
        assert "No constitution found" in result.stdout

    def test_merge_preserves_customizations(self, tmp_path, monkeypatch):
        """Test merge preserves user customizations in regular sections."""
        # Create memory directory
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create a light constitution with custom QUALITY section
        content = """# My Project Constitution
<!-- TIER: Light - Minimal controls for startups/hobby projects -->

## Core Principles

### Simplicity First
Keep things simple. Ship fast, iterate quickly. Avoid over-engineering.

### Working Software
Prioritize working software over documentation. Code that runs is better than perfect designs.

### Pragmatic Quality
<!-- SECTION:QUALITY:BEGIN -->
- Custom rule 1
- Custom rule 2
- Custom rule 3
<!-- SECTION:QUALITY:END -->

## Development Workflow

### Git Practices
<!-- SECTION:GIT:BEGIN -->
- Custom git workflow
<!-- SECTION:GIT:END -->

### Task Management
<!-- SECTION:TASKS:BEGIN -->
Tasks should have:
- Clear description of what needs to be done
- Basic acceptance criteria when scope is unclear
<!-- SECTION:TASKS:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
Python 3.11
<!-- SECTION:TECH_STACK:END -->

## Governance

This constitution is a living document. Update it as the project evolves.

**Version**: 1.0.0 | **Created**: 2025-01-01
"""
        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "merge", "--auto"])

        assert result.exit_code == 0
        assert "Merged constitution written to" in result.stdout

        # Check merged file exists
        merged_path = memory_dir / "constitution-merged.md"
        assert merged_path.exists()

        # Check merged content
        merged_content = merged_path.read_text()
        assert "MERGED:" in merged_content
        assert "REVIEW REQUIRED:" in merged_content

        # Verify custom sections are preserved
        assert "Custom rule 1" in merged_content
        assert "Custom git workflow" in merged_content
        assert "Python 3.11" in merged_content

    def test_merge_preserves_custom_sections(self, tmp_path, monkeypatch):
        """Test merge preserves custom sections not in template."""
        # Create memory directory
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create constitution with custom section
        from specify_cli import CONSTITUTION_TEMPLATES

        content = (
            CONSTITUTION_TEMPLATES["light"]
            + """

## Custom Section
<!-- SECTION:CUSTOM:BEGIN -->
This is my custom section
<!-- SECTION:CUSTOM:END -->
"""
        )

        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "merge", "--auto"])

        assert result.exit_code == 0

        # Check merged file
        merged_path = memory_dir / "constitution-merged.md"
        merged_content = merged_path.read_text()

        # Custom section should be preserved
        assert "SECTION:CUSTOM:BEGIN" in merged_content
        assert "This is my custom section" in merged_content
        assert "Preserved custom section" in result.stdout

    def test_merge_summary_output(self, tmp_path, monkeypatch):
        """Test merge command produces correct summary output."""
        # Create memory directory
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create a constitution with some modifications
        from specify_cli import CONSTITUTION_TEMPLATES

        content = CONSTITUTION_TEMPLATES["medium"].replace(
            "Critical paths must have test coverage",
            "All paths must have test coverage",
        )

        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["constitution", "merge", "--auto"])

        assert result.exit_code == 0
        assert "Merge Summary:" in result.stdout
        assert "Next steps:" in result.stdout
        assert "Review the merged constitution" in result.stdout


class TestConstitutionIntegration:
    """Integration tests for constitution commands."""

    def test_diff_then_merge_workflow(self, tmp_path, monkeypatch):
        """Test complete workflow: diff shows changes, merge applies them."""
        # Create memory directory
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        # Create a modified constitution
        from specify_cli import CONSTITUTION_TEMPLATES

        content = CONSTITUTION_TEMPLATES["light"].replace(
            "Write tests for critical paths", "Write ALL the tests!"
        )

        constitution_path = memory_dir / "constitution.md"
        constitution_path.write_text(content)

        monkeypatch.chdir(tmp_path)

        # First, run diff to see changes
        diff_result = runner.invoke(app, ["constitution", "diff"])
        assert diff_result.exit_code == 0
        assert "differ" in diff_result.stdout.lower()

        # Then run merge
        merge_result = runner.invoke(app, ["constitution", "merge", "--auto"])
        assert merge_result.exit_code == 0

        # Verify merged file exists
        merged_path = memory_dir / "constitution-merged.md"
        assert merged_path.exists()

        # Verify custom content is preserved
        merged_content = merged_path.read_text()
        assert "Write ALL the tests!" in merged_content
