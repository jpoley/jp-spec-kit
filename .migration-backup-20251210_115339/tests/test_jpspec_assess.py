"""Tests for /jpspec:assess problem-sizing assessment command.

This test module verifies that the assess command correctly implements
the problem-sizing assessment framework with scoring, recommendations,
and workflow integration.
"""

import re
import pytest
from pathlib import Path


@pytest.fixture
def assess_command_path():
    """Return the path to the assess.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "assess.md"
    )


def extract_section(content: str, start_pattern: str, end_pattern: str) -> str | None:
    """Extract a section of content between two patterns using regex.

    Returns None if patterns are not found, allowing tests to fail gracefully.
    """
    pattern = re.compile(
        rf"{re.escape(start_pattern)}(.*?){re.escape(end_pattern)}", re.DOTALL
    )
    match = pattern.search(content)
    return match.group(1) if match else None


@pytest.fixture
def assess_command_content(assess_command_path):
    """Load the assess.md command content."""
    return assess_command_path.read_text()


class TestAssessCommandStructure:
    """Tests for assess.md command structure and existence."""

    def test_command_file_exists(self, assess_command_path):
        """AC #3: Verify assess.md command file exists."""
        assert assess_command_path.exists(), "assess.md command file should exist"

    def test_has_description(self, assess_command_content):
        """Verify command has a clear description."""
        assert "description:" in assess_command_content
        assert "SDD workflow" in assess_command_content


class TestAssessmentScoringDimensions:
    """AC #1: Tests for three scoring dimensions."""

    def test_has_complexity_scoring(self, assess_command_content):
        """Verify Complexity scoring dimension exists."""
        assert "Complexity Scoring" in assess_command_content
        assert "Effort Days" in assess_command_content
        assert "Component Count" in assess_command_content
        assert "Integration Points" in assess_command_content

    def test_has_risk_scoring(self, assess_command_content):
        """Verify Risk scoring dimension exists."""
        assert "Risk Scoring" in assess_command_content
        assert "Security Implications" in assess_command_content
        assert "Compliance Requirements" in assess_command_content
        assert "Data Sensitivity" in assess_command_content

    def test_has_architecture_impact_scoring(self, assess_command_content):
        """Verify Architecture Impact scoring dimension exists."""
        assert "Architecture Impact Scoring" in assess_command_content
        assert "New Patterns" in assess_command_content
        assert "Breaking Changes" in assess_command_content
        assert "Dependencies Affected" in assess_command_content

    def test_uses_ten_point_scale(self, assess_command_content):
        """Verify scoring uses 1-10 scale."""
        assert "(1-10)" in assess_command_content
        # Should have multiple 1-10 scales (9 sub-dimensions)
        assert assess_command_content.count("(1-10)") >= 9


class TestDecisionLogic:
    """AC #2: Tests for decision logic and scoring system."""

    def test_has_recommendation_logic(self, assess_command_content):
        """Verify recommendation calculation logic is documented."""
        assert (
            "Total Score = Complexity + Risk + Architecture Impact"
            in assess_command_content
        )

    def test_has_full_sdd_threshold(self, assess_command_content):
        """Verify Full SDD threshold is documented."""
        assert "any individual score >= 7" in assess_command_content
        assert "Total Score >= 18" in assess_command_content

    def test_has_spec_light_threshold(self, assess_command_content):
        """Verify Spec-Light threshold is documented."""
        assert "any individual score >= 4" in assess_command_content
        assert "Total Score >= 10" in assess_command_content

    def test_has_skip_sdd_recommendation(self, assess_command_content):
        """Verify Skip SDD recommendation exists."""
        assert "Skip SDD" in assess_command_content
        assert "Low complexity allows direct implementation" in assess_command_content

    def test_has_workflow_recommendations(self, assess_command_content):
        """Verify workflow recommendations exist for all complexity levels."""
        assert "Full SDD" in assess_command_content
        assert "Spec-Light" in assess_command_content
        assert "Skip SDD" in assess_command_content


class TestRecommendationOutput:
    """AC #4: Tests for clear recommendations and output format."""

    def test_has_assessment_report_template(self, assess_command_content):
        """Verify assessment report template exists."""
        assert "# Feature Assessment:" in assess_command_content
        assert "## Feature Overview" in assess_command_content
        assert "## Scoring Analysis" in assess_command_content
        assert "## Overall Assessment" in assess_command_content

    def test_has_next_steps_section(self, assess_command_content):
        """Verify next steps section exists."""
        assert "## Next Steps" in assess_command_content
        assert "### Full SDD Path" in assess_command_content
        assert "### Spec-Light Path" in assess_command_content
        assert "### Skip SDD Path" in assess_command_content

    def test_has_output_format(self, assess_command_content):
        """Verify output format is documented."""
        assert "## Assessment Complete" in assess_command_content
        assert "Scoring Summary" in assess_command_content


class TestOverrideSupport:
    """AC #5: Tests for override mode support."""

    def test_has_override_section(self, assess_command_content):
        """Verify override section exists."""
        assert "Override" in assess_command_content
        assert "--mode full" in assess_command_content
        assert "--mode light" in assess_command_content
        assert "--mode skip" in assess_command_content

    def test_has_override_handling(self, assess_command_content):
        """Verify override handling is documented."""
        assert "Support Override Mode" in assess_command_content
        assert "Skip scoring analysis" in assess_command_content


class TestWorkflowIntegration:
    """AC #6: Tests for workflow integration."""

    def test_state_transition_documented(self, assess_command_content):
        """Verify state transition is documented."""
        assert "State Transition" in assess_command_content
        assert '"To Do" → "Assessed"' in assess_command_content

    def test_artifact_path_documented(self, assess_command_content):
        """Verify artifact output path is documented."""
        assert "./docs/assess/{feature}-assessment.md" in assess_command_content

    def test_validation_mode_documented(self, assess_command_content):
        """Verify validation mode is documented."""
        assert "Validation Mode" in assess_command_content
        assert "NONE" in assess_command_content

    def test_has_workflow_commands(self, assess_command_content):
        """Verify workflow commands are referenced."""
        assert "/jpspec:specify" in assess_command_content


class TestQualityChecks:
    """AC #7: Tests for quality check checklist."""

    def test_has_quality_checks_section(self, assess_command_content):
        """Verify quality checks section exists."""
        assert "Quality Checks" in assess_command_content

    def test_has_checklist_items(self, assess_command_content):
        """Verify checklist items exist."""
        assert "Assessment report exists" in assess_command_content
        assert "scoring dimensions are documented" in assess_command_content
        assert "Recommendation is clear" in assess_command_content
        assert "Next steps are specific" in assess_command_content


class TestErrorHandling:
    """Tests for error handling documentation."""

    def test_has_error_handling_section(self, assess_command_content):
        """Verify error handling section exists."""
        assert "Error Handling" in assess_command_content

    def test_handles_missing_directory(self, assess_command_content):
        """Verify missing directory handling is documented."""
        assert "./docs/assess/" in assess_command_content
        assert "doesn't exist" in assess_command_content

    def test_handles_existing_assessment(self, assess_command_content):
        """Verify existing assessment handling is documented."""
        assert "assessment already exists" in assess_command_content


class TestScoringConsistency:
    """Tests for scoring system consistency."""

    def test_all_dimensions_have_scoring_formula(self, assess_command_content):
        """Verify each dimension has a scoring formula."""
        assert "Complexity Score =" in assess_command_content
        assert "Risk Score =" in assess_command_content
        assert "Architecture Impact Score =" in assess_command_content

    def test_score_ranges_documented(self, assess_command_content):
        """Verify score ranges are documented for sub-dimensions."""
        # Effort Days ranges
        assert "1-2:" in assess_command_content
        assert "9-10:" in assess_command_content


class TestScoringDetails:
    """Tests for detailed scoring criteria."""

    def test_effort_days_criteria(self, assess_command_content):
        """Verify Effort Days scoring criteria."""
        assert "Single day or less" in assess_command_content
        assert "Multiple weeks" in assess_command_content

    def test_component_count_criteria(self, assess_command_content):
        """Verify Component Count scoring criteria."""
        assert "Single component" in assess_command_content
        assert "7+ components" in assess_command_content

    def test_security_criteria(self, assess_command_content):
        """Verify Security scoring criteria."""
        assert "No security concerns" in assess_command_content
        assert "Critical security controls" in assess_command_content

    def test_data_sensitivity_criteria(self, assess_command_content):
        """Verify Data Sensitivity scoring criteria."""
        assert "Public/non-sensitive data" in assess_command_content
        assert "Financial/health" in assess_command_content
