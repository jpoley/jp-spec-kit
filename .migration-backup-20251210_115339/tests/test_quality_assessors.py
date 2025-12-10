"""Tests for individual quality assessors."""

from specify_cli.quality.assessors import (
    assess_completeness,
    assess_clarity,
    assess_traceability,
    assess_constitutional_compliance,
    assess_ambiguity,
    AssessmentResult,
)


class TestCompletenessAssessment:
    """Tests for completeness assessment."""

    def test_all_sections_present(self):
        """Test spec with all required sections."""
        spec_content = """
# Feature

## Description
Some description here.

## User Story
As a user...

## Acceptance Criteria
1. Criterion one
2. Criterion two

## Technical Requirements
- Requirement one
- Requirement two
"""
        required_sections = [
            "## Description",
            "## User Story",
            "## Acceptance Criteria",
            "## Technical Requirements",
        ]

        result = assess_completeness(spec_content, required_sections)

        assert result.score == 100.0
        assert "All required sections present" in result.findings[0]
        assert len(result.details["missing_sections"]) == 0

    def test_missing_sections(self):
        """Test spec with missing sections."""
        spec_content = """
# Feature

## Description
Some description here.

## User Story
As a user...
"""
        required_sections = [
            "## Description",
            "## User Story",
            "## Acceptance Criteria",
            "## Technical Requirements",
        ]

        result = assess_completeness(spec_content, required_sections)

        assert result.score == 50.0  # 2 out of 4 sections
        assert "Missing 2 section(s)" in result.findings[0]
        assert "## Acceptance Criteria" in result.details["missing_sections"]
        assert "## Technical Requirements" in result.details["missing_sections"]

    def test_case_insensitive_matching(self):
        """Test that section matching is case-insensitive."""
        spec_content = """
## DESCRIPTION
Content here

## user story
Content here

## acceptance criteria
Content here
"""
        required_sections = [
            "## Description",
            "## User Story",
            "## Acceptance Criteria",
        ]

        result = assess_completeness(spec_content, required_sections)

        assert result.score == 100.0


class TestClarityAssessment:
    """Tests for clarity assessment."""

    def test_no_vague_terms(self):
        """Test spec with clear, specific language."""
        spec_content = """
Implement user authentication with JWT tokens.
The system will authenticate 1000 users per second.
Response time must be under 100ms for 95% of requests.
"""
        vague_terms = ["etc", "various", "some", "maybe"]

        result = assess_clarity(spec_content, vague_terms)

        assert result.score >= 95  # High score, may get bonus for measurable criteria
        assert (
            "No clarity issues" in result.findings[0]
            or "measurable" in result.findings[0].lower()
        )

    def test_multiple_vague_terms(self):
        """Test spec with vague language."""
        spec_content = """
The system should handle various file types and maybe validate them.
We'll probably need some error handling, etc.
This could potentially work with different databases.
"""
        vague_terms = [
            "etc",
            "various",
            "some",
            "maybe",
            "probably",
            "could",
            "potentially",
        ]

        result = assess_clarity(spec_content, vague_terms)

        assert result.score < 80  # Penalty for vague terms
        assert result.details["vague_count"] >= 5
        assert "vague term(s) found" in result.findings[0]

    def test_passive_voice_detection(self):
        """Test detection of passive voice patterns."""
        spec_content = """
The data is processed by the system.
Users are authenticated by the service.
Tokens are generated and stored.
Results were validated by the tests.
"""
        vague_terms = []

        result = assess_clarity(spec_content, vague_terms)

        # Should detect passive voice
        assert result.details["passive_count"] > 0
        assert any("passive voice" in finding.lower() for finding in result.findings)

    def test_measurable_criteria_bonus(self):
        """Test bonus for measurable criteria."""
        spec_content = """
System must handle 5000 requests/sec with 99.9% uptime.
Response time under 200ms for 95% of requests.
Database size limited to 100GB.
Process 1 million records per hour.
"""
        vague_terms = []

        result = assess_clarity(spec_content, vague_terms)

        # Should get bonus for measurable criteria
        assert result.details["measurable_count"] >= 3
        assert any("measurable" in finding.lower() for finding in result.findings)


class TestTraceabilityAssessment:
    """Tests for traceability assessment."""

    def test_no_related_files(self, tmp_path):
        """Test when no plan or tasks files exist."""
        spec_file = tmp_path / "spec.md"
        spec_file.write_text("## Description\nSome content")

        result = assess_traceability(
            spec_file,
            spec_file.read_text(),
            tmp_path / "plan.md",
            tmp_path / "tasks.md",
        )

        assert result.score == 80.0  # Partial score
        assert not result.details["plan_exists"]
        assert not result.details["tasks_exist"]

    def test_with_plan_file(self, tmp_path):
        """Test traceability with plan file."""
        spec_file = tmp_path / "spec.md"
        spec_content = """
## Description
Feature description

## Acceptance Criteria
1. First criterion
2. Second criterion
"""
        spec_file.write_text(spec_content)

        plan_file = tmp_path / "plan.md"
        plan_file.write_text("""
# Implementation Plan

This plan addresses the acceptance criteria from the specification.
We will implement each requirement according to the user story.
""")

        result = assess_traceability(spec_file, spec_content, plan_file, None)

        assert result.details["plan_exists"]
        assert result.details["plan_references_spec"]
        assert result.details["has_acceptance_criteria"]

    def test_missing_acceptance_criteria(self, tmp_path):
        """Test penalty for missing acceptance criteria."""
        spec_file = tmp_path / "spec.md"
        spec_content = "## Description\nJust a description"
        spec_file.write_text(spec_content)

        result = assess_traceability(spec_file, spec_content)

        assert not result.details["has_acceptance_criteria"]
        assert result.score < 100


class TestConstitutionalCompliance:
    """Tests for constitutional compliance assessment."""

    def test_all_patterns_present(self):
        """Test spec mentioning all required patterns."""
        spec_content = """
Implementation will use pytest for testing with ruff for linting.
Dependencies managed with uv. CLI built with typer and rich for output.
"""
        patterns = ["pytest", "ruff", "uv", "typer", "rich"]

        result = assess_constitutional_compliance(spec_content, patterns)

        assert result.score == 100.0
        assert len(result.details["found_patterns"]) == 5
        assert len(result.details["missing_patterns"]) == 0

    def test_missing_patterns(self):
        """Test spec missing some required patterns."""
        spec_content = """
We'll use pytest for testing and ruff for linting.
"""
        patterns = ["pytest", "ruff", "uv", "typer", "rich"]

        result = assess_constitutional_compliance(spec_content, patterns)

        assert result.score == 40.0  # 2 out of 5
        assert len(result.details["found_patterns"]) == 2
        assert len(result.details["missing_patterns"]) == 3

    def test_dco_sign_off_bonus(self):
        """Test bonus for DCO sign-off mention."""
        spec_content = """
Use pytest for testing.
All commits must include DCO sign-off using git commit -s.
"""
        patterns = ["pytest"]

        result = assess_constitutional_compliance(spec_content, patterns)

        # Should get bonus for DCO mention
        assert any("DCO" in finding for finding in result.findings)
        assert result.score >= 100  # 100% + bonus, capped at 100

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        spec_content = """
Use PYTEST for testing and RUFF for linting.
"""
        patterns = ["pytest", "ruff"]

        result = assess_constitutional_compliance(spec_content, patterns)

        assert result.score == 100.0


class TestAmbiguityAssessment:
    """Tests for ambiguity assessment."""

    def test_no_ambiguity_markers(self):
        """Test spec with no ambiguity markers."""
        spec_content = """
Implement user authentication with clear requirements.
All components are well-defined and understood.
"""
        markers = ["TBD", "TODO", "FIXME", "unclear", "???"]

        result = assess_ambiguity(spec_content, markers)

        assert result.score == 100.0
        assert "No ambiguity markers detected" in result.findings[0]
        assert result.details["marker_count"] == 0

    def test_multiple_markers(self):
        """Test spec with multiple ambiguity markers."""
        spec_content = """
Database selection: TBD
TODO: Add validation rules
Implementation details are unclear
FIXME: Resolve performance issues
??? What about error handling?
"""
        markers = ["TBD", "TODO", "FIXME", "unclear", "???"]

        result = assess_ambiguity(spec_content, markers)

        assert result.score <= 60  # Heavy penalty for multiple markers
        assert result.details["marker_count"] >= 4
        assert "ambiguity marker(s) found" in result.findings[0]

    def test_case_insensitive_matching(self):
        """Test case-insensitive marker detection."""
        spec_content = """
Database: tbd
todo: Add tests
This is Unclear
"""
        markers = ["TBD", "TODO", "unclear"]

        result = assess_ambiguity(spec_content, markers)

        assert result.details["marker_count"] == 3

    def test_line_number_reporting(self):
        """Test that line numbers are reported for markers."""
        spec_content = """Line 1
Line 2
TODO: Fix this
Line 4
TBD: Decide
"""
        markers = ["TODO", "TBD"]

        result = assess_ambiguity(spec_content, markers)

        # Check that findings include line numbers
        assert any("line" in finding.lower() for finding in result.findings[1:])


class TestAssessmentResult:
    """Tests for AssessmentResult dataclass."""

    def test_result_structure(self):
        """Test AssessmentResult structure."""
        result = AssessmentResult(
            score=85.5, findings=["Finding 1", "Finding 2"], details={"key": "value"}
        )

        assert result.score == 85.5
        assert len(result.findings) == 2
        assert result.details["key"] == "value"

    def test_result_with_no_details(self):
        """Test AssessmentResult with default details."""
        result = AssessmentResult(score=100.0, findings=["All good"])

        assert result.details == {}
