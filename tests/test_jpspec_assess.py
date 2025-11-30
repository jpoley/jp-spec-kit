"""Tests for /jpspec:assess problem-sizing assessment command.

This test module verifies that the assess command correctly implements
the problem-sizing assessment framework with scoring, recommendations,
and examples.
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


class TestAssessmentPrompts:
    """AC #1: Tests for assessment prompt design."""

    def test_has_loc_estimation_question(self, assess_command_content):
        """Verify Lines of Code estimation question exists."""
        assert "Question 1: Estimated Lines of Code (LOC)" in assess_command_content
        assert "< 100 lines" in assess_command_content
        assert "> 2000 lines" in assess_command_content
        assert "Score: A=1, B=2, C=3, D=4" in assess_command_content

    def test_has_modules_affected_question(self, assess_command_content):
        """Verify modules/components affected question exists."""
        assert (
            "Question 2: Number of Modules/Components Affected"
            in assess_command_content
        )
        assert "1 module" in assess_command_content
        assert "7+ modules" in assess_command_content

    def test_has_integration_complexity_question(self, assess_command_content):
        """Verify external integrations question exists."""
        assert "Question 3: External Integrations" in assess_command_content
        assert "0 integrations" in assess_command_content
        assert "5+ integrations" in assess_command_content

    def test_has_data_complexity_question(self, assess_command_content):
        """Verify data complexity question exists."""
        assert "Question 4: Data Complexity" in assess_command_content
        assert "No persistence" in assess_command_content
        assert "Complex persistence" in assess_command_content

    def test_has_team_size_question(self, assess_command_content):
        """Verify team coordination requirements question exists."""
        assert "Question 5: Team Coordination Requirements" in assess_command_content
        assert "Solo developer" in assess_command_content
        assert "7+ developers" in assess_command_content

    def test_has_cross_functional_question(self, assess_command_content):
        """Verify cross-functional requirements question exists."""
        assert "Question 6: Cross-Functional Requirements" in assess_command_content
        assert "Engineering only" in assess_command_content
        assert "Full cross-functional" in assess_command_content

    def test_has_technical_uncertainty_question(self, assess_command_content):
        """Verify technical uncertainty question exists."""
        assert "Question 7: Technical Uncertainty" in assess_command_content
        assert "Well-known pattern" in assess_command_content
        assert "High uncertainty" in assess_command_content

    def test_has_business_impact_question(self, assess_command_content):
        """Verify business impact question exists."""
        assert "Question 8: Business Impact and Risk" in assess_command_content
        assert "Low impact" in assess_command_content
        assert "Critical impact" in assess_command_content


class TestDecisionLogic:
    """AC #2: Tests for decision logic and scoring system."""

    def test_has_scoring_calculation(self, assess_command_content):
        """Verify scoring calculation logic is documented."""
        assert "Total Score Calculation" in assess_command_content
        assert "Sum all 8 question scores" in assess_command_content
        assert "range: 8-32" in assess_command_content

    def test_has_complexity_classification(self, assess_command_content):
        """Verify complexity classification thresholds."""
        assert "Complexity Classification" in assess_command_content
        assert (
            "Simple" in assess_command_content
            and "8-12 points" in assess_command_content
        )
        assert (
            "Medium" in assess_command_content
            and "13-20 points" in assess_command_content
        )
        assert (
            "Complex" in assess_command_content
            and "21-32 points" in assess_command_content
        )

    def test_has_workflow_recommendations(self, assess_command_content):
        """Verify workflow recommendations exist for all complexity levels."""
        assert "Workflow Recommendations" in assess_command_content
        assert "Skip SDD" in assess_command_content
        assert "Spec-Light Mode" in assess_command_content
        assert "Full SDD Workflow" in assess_command_content


class TestRecommendationOutput:
    """AC #4: Tests for clear recommendations with examples."""

    def test_simple_features_recommendation(self, assess_command_content):
        """Verify simple features recommendation is clear."""
        assert "Simple Features (8-12 points)" in assess_command_content
        assert "Skip Spec-Driven Development" in assess_command_content
        assert "Suggested Approach:" in assess_command_content
        assert "Example Features:" in assess_command_content
        assert "Bug fixes" in assess_command_content

    def test_medium_features_recommendation(self, assess_command_content):
        """Verify medium features recommendation is clear."""
        assert "Medium Features (13-20 points)" in assess_command_content
        assert "Spec-Light Mode" in assess_command_content
        assert "lightweight specification" in assess_command_content
        assert "Skip These SDD Phases:" in assess_command_content
        assert "Use These SDD Phases:" in assess_command_content

    def test_complex_features_recommendation(self, assess_command_content):
        """Verify complex features recommendation is clear."""
        assert "Complex Features (21-32 points)" in assess_command_content
        assert "Full Spec-Driven Development Workflow" in assess_command_content
        assert "/jpspec:specify" in assess_command_content
        assert "/jpspec:research" in assess_command_content
        assert "/jpspec:plan" in assess_command_content
        assert "/jpspec:implement" in assess_command_content
        assert "/jpspec:validate" in assess_command_content
        assert "/jpspec:operate" in assess_command_content

    def test_has_output_format_section(self, assess_command_content):
        """Verify output format section exists."""
        assert "### Output Format" in assess_command_content
        assert "Feature Complexity Assessment" in assess_command_content
        assert "Complexity Score:" in assess_command_content
        assert "## Recommendation:" in assess_command_content


class TestSpecifyInitIntegration:
    """AC #5: Tests for integration with specify init workflow."""

    def test_has_specify_init_integration_section(self, assess_command_content):
        """Verify specify init integration is documented."""
        assert "Integration with `specify init`" in assess_command_content

    def test_has_assessment_offer_prompt(self, assess_command_content):
        """Verify assessment offer prompt exists."""
        assert "Before initializing, would you like to assess" in assess_command_content
        assert "[Y/n]:" in assess_command_content


class TestDocumentation:
    """AC #6: Tests for documentation about when to use SDD."""

    def test_simple_features_why_skip(self, assess_command_content):
        """Verify documentation explains why to skip SDD for simple features."""
        assert "Why Skip SDD?" in assess_command_content
        assert (
            "Overhead of specification would slow down delivery"
            in assess_command_content
        )

    def test_medium_features_why_spec_light(self, assess_command_content):
        """Verify documentation explains why spec-light for medium features."""
        assert "Why Spec-Light?" in assess_command_content
        assert (
            "Captures key decisions without excessive documentation"
            in assess_command_content
        )

    def test_complex_features_why_full_sdd(self, assess_command_content):
        """Verify documentation explains why full SDD for complex features."""
        assert "Why Full SDD?" in assess_command_content
        assert (
            "High coordination overhead requires clear specifications"
            in assess_command_content
        )

    def test_has_validation_and_calibration_section(self, assess_command_content):
        """Verify validation and calibration guidance exists."""
        assert "Validation and Calibration" in assess_command_content
        assert "calibrate this assessment tool" in assess_command_content

    def test_has_final_notes(self, assess_command_content):
        """Verify final notes about tool usage exist."""
        assert "This assessment is a tool, not a mandate" in assess_command_content
        assert (
            "When in doubt, err on the side of more planning" in assess_command_content
        )


class TestExampleScenarios:
    """AC #7: Tests for various feature complexity example scenarios."""

    def test_has_simple_bug_fix_example(self, assess_command_content):
        """Verify simple bug fix example exists."""
        assert "Example 1: Simple Bug Fix" in assess_command_content
        assert "Fix button alignment" in assess_command_content
        assert "Total: 8/32 (Simple)" in assess_command_content
        assert "Skip SDD, implement directly" in assess_command_content

    def test_has_api_endpoint_example(self, assess_command_content):
        """Verify API endpoint (medium complexity) example exists."""
        assert "Example 2: New API Endpoint" in assess_command_content
        assert "user preferences API" in assess_command_content
        assert "Total: 15/32 (Medium)" in assess_command_content
        assert "Spec-Light Mode" in assess_command_content

    def test_has_payment_integration_example(self, assess_command_content):
        """Verify payment integration (complex) example exists."""
        assert "Example 3: Payment Integration" in assess_command_content
        assert "Stripe payment processing" in assess_command_content
        assert "Total: 27/32 (Complex)" in assess_command_content
        assert "Full SDD Workflow" in assess_command_content

    def test_example_scenarios_section_exists(self, assess_command_content):
        """Verify example scenarios section exists."""
        assert "### Example Scenarios" in assess_command_content


class TestScoringConsistency:
    """Tests for scoring system consistency."""

    def test_all_questions_have_4_point_scale(self, assess_command_content):
        """Verify all questions use consistent A=1, B=2, C=3, D=4 scoring."""
        # Count score definitions - should be 8 (one per question)
        score_definitions = assess_command_content.count("Score: A=1, B=2, C=3, D=4")
        assert score_definitions == 8, (
            f"Expected 8 score definitions, found {score_definitions}"
        )

    def test_all_questions_have_4_options(self, assess_command_content):
        """Verify all questions have 4 options (A, B, C, D)."""
        # Each question should have Options: section with A, B, C, D
        options_sections = assess_command_content.count("Options:")
        assert options_sections >= 8, (
            f"Expected at least 8 Options sections, found {options_sections}"
        )


class TestRecommendationExamples:
    """Tests for recommendation examples in each workflow type."""

    def test_skip_sdd_has_example_features(self, assess_command_content):
        """Verify Skip SDD recommendation includes example features."""
        skip_sdd_section = extract_section(
            assess_command_content, "Simple Features (8-12 points)", "Medium Features"
        )
        assert skip_sdd_section is not None, "Could not find Simple Features section"
        assert "Bug fixes" in skip_sdd_section
        assert "Configuration changes" in skip_sdd_section
        assert "Minor UI tweaks" in skip_sdd_section

    def test_spec_light_has_example_features(self, assess_command_content):
        """Verify Spec-Light recommendation includes example features."""
        spec_light_section = extract_section(
            assess_command_content, "Medium Features (13-20 points)", "Complex Features"
        )
        assert spec_light_section is not None, "Could not find Medium Features section"
        assert "New API endpoint" in spec_light_section
        assert "UI component with business logic" in spec_light_section
        assert "Service integration" in spec_light_section

    def test_full_sdd_has_example_features(self, assess_command_content):
        """Verify Full SDD recommendation includes example features."""
        full_sdd_section = extract_section(
            assess_command_content,
            "Complex Features (21-32 points)",
            "### Output Format",
        )
        assert full_sdd_section is not None, "Could not find Complex Features section"
        assert "New product capabilities" in full_sdd_section
        assert "System-wide architectural changes" in full_sdd_section
        assert "Multi-team integration projects" in full_sdd_section


class TestPhaseInclusions:
    """Tests for which SDD phases are included in each recommendation."""

    def test_spec_light_phases_documented(self, assess_command_content):
        """Verify Spec-Light mode documents which phases to skip and use."""
        spec_light_section = extract_section(
            assess_command_content, "Medium Features (13-20 points)", "Complex Features"
        )
        assert spec_light_section is not None, "Could not find Medium Features section"
        # Phases to skip
        assert "/jpspec:research" in spec_light_section
        assert "/jpspec:plan" in spec_light_section
        assert "/jpspec:validate" in spec_light_section
        # Phases to use
        assert "/jpspec:specify" in spec_light_section
        assert "/jpspec:implement" in spec_light_section

    def test_full_sdd_includes_all_phases(self, assess_command_content):
        """Verify Full SDD includes all phases in order."""
        full_sdd_section = extract_section(
            assess_command_content,
            "Complex Features (21-32 points)",
            "### Output Format",
        )
        assert full_sdd_section is not None, "Could not find Complex Features section"
        # Verify all phases are mentioned
        assert "/jpspec:specify" in full_sdd_section
        assert "/jpspec:research" in full_sdd_section
        assert "/jpspec:plan" in full_sdd_section
        assert "/jpspec:implement" in full_sdd_section
        assert "/jpspec:validate" in full_sdd_section
        assert "/jpspec:operate" in full_sdd_section
