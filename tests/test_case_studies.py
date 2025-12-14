"""Tests for case studies documentation.

These tests validate that case studies:
- Follow the required template structure
- Have all required sections
- Are properly linked from the README
- Maintain consistent quality standards
"""

import re
from pathlib import Path
from typing import Optional

import pytest

# =============================================================================
# Constants - Avoid magic numbers, make requirements clear
# =============================================================================

# Minimum README length to ensure meaningful content (not just a title)
MIN_README_LENGTH = 100

# Minimum case study length - a real case study should be substantial
# (includes metrics, phases, feedback, recommendations, appendix)
MIN_CASE_STUDY_LENGTH = 2000

# Maximum placeholder count before content is considered mostly unfilled
# Template has ~30 placeholders, so 20 indicates mostly template
MAX_PLACEHOLDER_COUNT = 20

# Minimum placeholders expected in template for customization guidance
MIN_TEMPLATE_PLACEHOLDERS = 10

# Regex for two-digit naming convention (e.g., 01-name.md, 02-name.md)
CASE_STUDY_NAMING_PATTERN = re.compile(r"^\d{2}-[a-z0-9-]+$")

# =============================================================================
# Shared fixtures
# =============================================================================


@pytest.fixture
def case_studies_dir() -> Path:
    """Get the case studies directory path.

    Returns:
        Path to build-docs/case-studies directory.
    """
    return get_project_root() / "build-docs" / "case-studies"


# =============================================================================
# Helper functions
# =============================================================================


def get_project_root() -> Path:
    """Get the project root directory reliably.

    Returns:
        Path to the project root directory.
    """
    return Path(__file__).resolve().parent.parent


def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it doesn't exist.

    Args:
        file_path: Path to the file to read.

    Returns:
        File contents as string, or None if file cannot be read.
    """
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
    except (OSError, IOError, PermissionError):
        # Suppress file read errors; function returns None if file can't be read
        pass
    return None


def get_case_study_files(case_studies_dir: Path) -> list[Path]:
    """Get all case study markdown files (excluding README and template).

    Args:
        case_studies_dir: Path to the case studies directory.

    Returns:
        List of paths to case study files.
    """
    if not case_studies_dir.is_dir():
        return []
    return [
        f
        for f in case_studies_dir.glob("*.md")
        if f.name not in ("README.md", "_template.md")
    ]


# Required sections that every case study must have
REQUIRED_SECTIONS = [
    "## Overview",
    "## Metrics",
    "## Workflow Execution",
    "## Developer Feedback",
    "## Recommendations",
    "## Appendix",
]

# Required overview table attributes
REQUIRED_OVERVIEW_ATTRS = [
    "Domain",
    "Duration",
    "Team Size",
    "Complexity",
    "SDD Phases Used",
]


class TestCaseStudyStructure:
    """Tests for case study directory and file structure."""

    def test_case_studies_directory_exists(self, case_studies_dir: Path) -> None:
        """Case studies directory should exist at build-docs/case-studies."""
        assert case_studies_dir.exists(), (
            f"Case studies directory not found at {case_studies_dir}"
        )
        assert case_studies_dir.is_dir(), (
            f"Expected {case_studies_dir} to be a directory"
        )

    def test_readme_exists(self, case_studies_dir: Path) -> None:
        """README.md should exist in case studies directory with meaningful content."""
        readme = case_studies_dir / "README.md"
        assert readme.exists(), f"README.md not found at {readme}"

        content = safe_read_file(readme)
        assert content is not None, f"Could not read {readme}"
        assert len(content) > MIN_README_LENGTH, (
            f"README.md appears too short ({len(content)} chars, min {MIN_README_LENGTH})"
        )

    def test_template_exists(self, case_studies_dir: Path) -> None:
        """Template file should exist for creating new case studies."""
        template = case_studies_dir / "_template.md"
        assert template.exists(), f"Template not found at {template}"

        content = safe_read_file(template)
        assert content is not None, f"Could not read {template}"

    def test_at_least_one_case_study_exists(self, case_studies_dir: Path) -> None:
        """At least one case study should exist to demonstrate the template."""
        case_studies = get_case_study_files(case_studies_dir)
        assert len(case_studies) >= 1, (
            "No case studies found. Expected at least one case study file."
        )

    def test_case_study_naming_convention(self, case_studies_dir: Path) -> None:
        """Case studies should follow XX-name.md naming convention for ordering.

        The naming convention requires:
        - Two-digit prefix (01, 02, etc.) for consistent ordering
        - Dash separator after the number
        - Lowercase alphanumeric name with dashes
        """
        case_studies = get_case_study_files(case_studies_dir)

        for cs in case_studies:
            name = cs.stem  # filename without extension
            assert CASE_STUDY_NAMING_PATTERN.match(name), (
                f"Case study {cs.name} doesn't follow naming convention. "
                f"Expected format: XX-name.md (e.g., 01-workflow-hook-system.md)"
            )


class TestCaseStudyContent:
    """Tests for case study content quality and completeness."""

    def test_case_studies_have_required_sections(self, case_studies_dir: Path) -> None:
        """Each case study should have all required sections for completeness."""
        case_studies = get_case_study_files(case_studies_dir)

        for cs in case_studies:
            content = safe_read_file(cs)
            assert content is not None, f"Could not read {cs}"

            for section in REQUIRED_SECTIONS:
                assert section in content, (
                    f"Case study {cs.name} missing required section: {section}"
                )

    def test_case_studies_have_overview_table(self, case_studies_dir: Path) -> None:
        """Each case study should have an overview table with required attributes."""
        case_studies = get_case_study_files(case_studies_dir)

        for cs in case_studies:
            content = safe_read_file(cs)
            assert content is not None, f"Could not read {cs}"

            for attr in REQUIRED_OVERVIEW_ATTRS:
                assert attr in content, (
                    f"Case study {cs.name} missing overview attribute: {attr}"
                )

    def test_case_studies_have_metrics_tables(self, case_studies_dir: Path) -> None:
        """Each case study should have time and quality metrics tables."""
        case_studies = get_case_study_files(case_studies_dir)

        for cs in case_studies:
            content = safe_read_file(cs)
            assert content is not None, f"Could not read {cs}"

            # Should have time metrics
            assert "Time Metrics" in content or "### Time" in content, (
                f"Case study {cs.name} missing time metrics section"
            )

            # Should have quality metrics
            assert "Quality Metrics" in content or "### Quality" in content, (
                f"Case study {cs.name} missing quality metrics section"
            )

    def test_case_studies_have_meaningful_content(self, case_studies_dir: Path) -> None:
        """Case studies should have substantial content, not just placeholders."""
        case_studies = get_case_study_files(case_studies_dir)

        for cs in case_studies:
            content = safe_read_file(cs)
            assert content is not None, f"Could not read {cs}"

            # Should be reasonably long for a real case study
            assert len(content) > MIN_CASE_STUDY_LENGTH, (
                f"Case study {cs.name} appears too short ({len(content)} chars). "
                f"Expected at least {MIN_CASE_STUDY_LENGTH} chars for substantial documentation."
            )

            # Should not have excessive template placeholders
            # Use word boundary for XX- to avoid matching task-XXX
            placeholder_patterns = [
                r"\[e\.g\.,",  # Template placeholder hints
                r"X hours",  # Time placeholders
                r"\bXX-\w+",  # Filename placeholders like XX-name.md
            ]
            placeholder_count = sum(
                len(re.findall(pattern, content)) for pattern in placeholder_patterns
            )
            assert placeholder_count < MAX_PLACEHOLDER_COUNT, (
                f"Case study {cs.name} has {placeholder_count} placeholder patterns. "
                f"Max allowed: {MAX_PLACEHOLDER_COUNT}. Appears to be mostly unfilled template."
            )


class TestCaseStudyReadme:
    """Tests for the case studies README file."""

    def test_readme_has_case_study_table(self, case_studies_dir: Path) -> None:
        """README should have a table listing all case studies."""
        readme = case_studies_dir / "README.md"
        content = safe_read_file(readme)
        assert content is not None, f"Could not read {readme}"

        # Should have a markdown table
        assert "| Case Study |" in content or "|------------|" in content, (
            "README should have a case studies table"
        )

    def test_readme_links_are_valid(self, case_studies_dir: Path) -> None:
        """Links in README should point to existing case study files."""
        readme = case_studies_dir / "README.md"
        content = safe_read_file(readme)
        assert content is not None, f"Could not read {readme}"

        # Extract markdown links [text](file.md)
        links = re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", content)

        for link_text, link_path in links:
            if link_path.startswith("http"):
                continue  # Skip external links

            target = case_studies_dir / link_path
            assert target.exists(), (
                f"README links to non-existent file: {link_path} (link text: {link_text})"
            )

    def test_readme_table_matches_files(self, case_studies_dir: Path) -> None:
        """README table should list all case study files that exist."""
        readme = case_studies_dir / "README.md"
        content = safe_read_file(readme)
        assert content is not None, f"Could not read {readme}"

        # Get all case study files
        case_studies = get_case_study_files(case_studies_dir)

        # Extract links from README
        links = re.findall(r"\[([^\]]+)\]\(([^)]+\.md)\)", content)
        linked_files = {
            link_path
            for _, link_path in links
            if not link_path.startswith("http") and link_path != "_template.md"
        }

        # Check that all case studies are linked in README
        for cs in case_studies:
            assert cs.name in linked_files, (
                f"Case study {cs.name} exists but is not linked in README"
            )


class TestCaseStudyTemplate:
    """Tests for the case study template file."""

    @pytest.fixture
    def template_path(self) -> Path:
        """Get the template file path.

        Returns:
            Path to _template.md file.
        """
        return get_project_root() / "build-docs" / "case-studies" / "_template.md"

    def test_template_has_all_required_sections(self, template_path: Path) -> None:
        """Template should have all required sections as a guide."""
        content = safe_read_file(template_path)
        assert content is not None, f"Could not read {template_path}"

        for section in REQUIRED_SECTIONS:
            assert section in content, f"Template missing required section: {section}"

    def test_template_has_placeholder_markers(self, template_path: Path) -> None:
        """Template should have placeholder markers for customization."""
        content = safe_read_file(template_path)
        assert content is not None, f"Could not read {template_path}"

        # Should have placeholders like [Project Name], [e.g., ...]
        assert "[" in content and "]" in content, (
            "Template should have placeholder markers in brackets"
        )

        # Should have several placeholders for guidance
        placeholders = re.findall(r"\[([^\]]+)\]", content)
        assert len(placeholders) >= MIN_TEMPLATE_PLACEHOLDERS, (
            f"Template should have at least {MIN_TEMPLATE_PLACEHOLDERS} placeholders "
            f"for customization guidance, found {len(placeholders)}"
        )

    def test_template_has_overview_attributes(self, template_path: Path) -> None:
        """Template should have all overview attributes as a guide."""
        content = safe_read_file(template_path)
        assert content is not None, f"Could not read {template_path}"

        for attr in REQUIRED_OVERVIEW_ATTRS:
            assert attr in content, f"Template missing overview attribute: {attr}"

    def test_template_has_metrics_sections(self, template_path: Path) -> None:
        """Template should have time and quality metrics sections."""
        content = safe_read_file(template_path)
        assert content is not None, f"Could not read {template_path}"

        assert "Time Metrics" in content, "Template missing time metrics section"
        assert "Quality Metrics" in content, "Template missing quality metrics section"

    def test_template_has_workflow_phases(self, template_path: Path) -> None:
        """Template should include all SDD workflow phases."""
        content = safe_read_file(template_path)
        assert content is not None, f"Could not read {template_path}"

        phases = ["Assess", "Specify", "Plan", "Implement", "Validate"]
        for phase in phases:
            assert f"#### {phase}" in content, (
                f"Template missing workflow phase: {phase}"
            )
