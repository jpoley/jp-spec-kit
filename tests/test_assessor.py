"""Tests for workflow assessor module.

This module tests feature assessment functionality including:
- Dimension and category scoring
- Recommendation logic
- Report generation
- Override mode support
"""

from __future__ import annotations


import pytest

from flowspec_cli.workflow.assessor import (
    CategoryScore,
    Confidence,
    DimensionScore,
    FeatureAssessment,
    WorkflowRecommendation,
    create_architecture_impact_assessment,
    create_complexity_assessment,
    create_risk_assessment,
)


class TestDimensionScore:
    """Tests for DimensionScore class."""

    def test_valid_dimension_score(self):
        """Test creating a valid dimension score."""
        # Arrange & Act
        dim = DimensionScore(
            name="Effort Days",
            score=7,
            rationale="Estimated 1-2 weeks of development",
        )

        # Assert
        assert dim.name == "Effort Days"
        assert dim.score == 7
        assert dim.rationale == "Estimated 1-2 weeks of development"
        assert dim.max_score == 10

    def test_score_validation_too_low(self):
        """Test that score below 1 raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Score must be between 1 and 10"):
            DimensionScore(name="Test", score=0, rationale="Invalid")

    def test_score_validation_too_high(self):
        """Test that score above max raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Score must be between 1 and 10"):
            DimensionScore(name="Test", score=11, rationale="Invalid")

    def test_empty_name_validation(self):
        """Test that empty name raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Dimension name cannot be empty"):
            DimensionScore(name="", score=5, rationale="Valid rationale")

    def test_empty_rationale_validation(self):
        """Test that empty rationale raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Rationale cannot be empty"):
            DimensionScore(name="Valid Name", score=5, rationale="")

    def test_to_dict(self):
        """Test converting dimension to dictionary."""
        # Arrange
        dim = DimensionScore(name="Security", score=8, rationale="High security needs")

        # Act
        result = dim.to_dict()

        # Assert
        assert result == {
            "name": "Security",
            "score": 8,
            "rationale": "High security needs",
            "max_score": 10,
        }

    def test_from_dict(self):
        """Test creating dimension from dictionary."""
        # Arrange
        data = {
            "name": "Components",
            "score": 6,
            "rationale": "Multiple services affected",
            "max_score": 10,
        }

        # Act
        dim = DimensionScore.from_dict(data)

        # Assert
        assert dim.name == "Components"
        assert dim.score == 6
        assert dim.rationale == "Multiple services affected"
        assert dim.max_score == 10


class TestCategoryScore:
    """Tests for CategoryScore class."""

    def test_empty_category(self):
        """Test creating empty category."""
        # Arrange & Act
        category = CategoryScore(category="Complexity")

        # Assert
        assert category.category == "Complexity"
        assert category.dimensions == []
        assert category.average_score == 0.0
        assert category.max_dimension_score == 0

    def test_add_dimension(self):
        """Test adding dimensions to category."""
        # Arrange
        category = CategoryScore(category="Risk")

        # Act
        category.add_dimension("Security", 8, "High security requirements")
        category.add_dimension("Compliance", 5, "Standard compliance needs")

        # Assert
        assert len(category.dimensions) == 2
        assert category.dimensions[0].name == "Security"
        assert category.dimensions[1].name == "Compliance"

    def test_average_score_calculation(self):
        """Test average score calculation."""
        # Arrange
        category = CategoryScore(category="Complexity")
        category.add_dimension("Effort", 6, "Medium effort")
        category.add_dimension("Components", 4, "Few components")
        category.add_dimension("Integrations", 8, "Many integrations")

        # Act
        avg = category.average_score

        # Assert
        assert avg == pytest.approx((6 + 4 + 8) / 3)

    def test_max_dimension_score(self):
        """Test finding maximum dimension score."""
        # Arrange
        category = CategoryScore(category="Risk")
        category.add_dimension("Security", 3, "Low")
        category.add_dimension("Compliance", 9, "High")
        category.add_dimension("Data", 5, "Medium")

        # Act
        max_score = category.max_dimension_score

        # Assert
        assert max_score == 9

    def test_weighted_score(self):
        """Test weighted score calculation."""
        # Arrange
        category = CategoryScore(category="Impact", weight=1.5)
        category.add_dimension("Patterns", 6, "New patterns")
        category.add_dimension("Breaking", 4, "Minor breaking changes")

        # Act
        weighted = category.weighted_score

        # Assert
        expected = ((6 + 4) / 2) * 1.5
        assert weighted == pytest.approx(expected)

    def test_empty_category_name_validation(self):
        """Test that empty category name raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Category name cannot be empty"):
            CategoryScore(category="")

    def test_negative_weight_validation(self):
        """Test that negative weight raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Weight must be positive"):
            CategoryScore(category="Test", weight=-1.0)

    def test_to_dict(self):
        """Test converting category to dictionary."""
        # Arrange
        category = CategoryScore(category="Complexity")
        category.add_dimension("Effort", 7, "One week")
        category.add_dimension("Components", 5, "Few modules")

        # Act
        result = category.to_dict()

        # Assert
        assert result["category"] == "Complexity"
        assert result["average_score"] == pytest.approx(6.0)
        assert result["weight"] == 1.0
        assert len(result["dimensions"]) == 2

    def test_from_dict(self):
        """Test creating category from dictionary."""
        # Arrange
        data = {
            "category": "Risk",
            "dimensions": [
                {"name": "Security", "score": 8, "rationale": "High", "max_score": 10},
                {"name": "Data", "score": 6, "rationale": "Medium", "max_score": 10},
            ],
            "weight": 1.0,
        }

        # Act
        category = CategoryScore.from_dict(data)

        # Assert
        assert category.category == "Risk"
        assert len(category.dimensions) == 2
        assert category.weight == 1.0


class TestFeatureAssessment:
    """Tests for FeatureAssessment class."""

    def test_minimal_assessment(self):
        """Test creating minimal feature assessment."""
        # Arrange & Act
        assessment = FeatureAssessment(
            feature_name="Test Feature",
            description="A simple test feature",
        )

        # Assert
        assert assessment.feature_name == "Test Feature"
        assert assessment.description == "A simple test feature"
        assert assessment.complexity is not None
        assert assessment.risk is not None
        assert assessment.architecture_impact is not None

    def test_empty_feature_name_validation(self):
        """Test that empty feature name raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Feature name cannot be empty"):
            FeatureAssessment(feature_name="")

    def test_total_score_calculation(self):
        """Test total score calculation across categories."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 6, "Medium")
        assessment.complexity.add_dimension("Components", 4, "Low")
        assessment.risk.add_dimension("Security", 8, "High")
        assessment.architecture_impact.add_dimension("Patterns", 5, "Medium")

        # Act
        total = assessment.total_score

        # Assert
        complexity_avg = (6 + 4) / 2  # 5.0
        risk_avg = 8.0
        impact_avg = 5.0
        expected = complexity_avg + risk_avg + impact_avg
        assert total == pytest.approx(expected)

    def test_max_category_score(self):
        """Test finding maximum category score."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 3, "Low")
        assessment.risk.add_dimension("Security", 9, "High")
        assessment.architecture_impact.add_dimension("Patterns", 5, "Medium")

        # Act
        max_score = assessment.max_category_score

        # Assert
        assert max_score == 9.0

    def test_recommendation_full_sdd_by_category_score(self):
        """Test Full SDD recommendation when category score >= 7."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 8, "High complexity")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.FULL_SDD
        assert confidence == Confidence.HIGH

    def test_recommendation_full_sdd_by_total_score(self):
        """Test Full SDD recommendation when total >= 18."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 6, "Medium")
        assessment.complexity.add_dimension("Components", 6, "Medium")
        assessment.risk.add_dimension("Security", 6, "Medium")
        # Total: (6+6)/2 + 6 + 0 = 12, need more
        assessment.architecture_impact.add_dimension("Patterns", 6, "Medium")
        # Total: 6 + 6 + 6 = 18

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.FULL_SDD
        assert confidence == Confidence.HIGH

    def test_recommendation_spec_light_by_category_score(self):
        """Test Spec-Light recommendation when category score >= 4."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 5, "Moderate")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SPEC_LIGHT
        assert confidence == Confidence.MEDIUM

    def test_recommendation_spec_light_by_total_score(self):
        """Test Spec-Light recommendation when total >= 10."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 3, "Low")
        assessment.complexity.add_dimension("Components", 3, "Low")
        assessment.risk.add_dimension("Security", 3, "Low")
        assessment.architecture_impact.add_dimension("Patterns", 5, "Medium")
        # Total: 3 + 3 + 4 = 10

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SPEC_LIGHT
        assert confidence == Confidence.MEDIUM

    def test_recommendation_skip_sdd(self):
        """Test Skip SDD recommendation for low complexity."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 2, "Low")
        assessment.risk.add_dimension("Security", 1, "None")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SKIP_SDD
        assert confidence == Confidence.HIGH

    def test_override_mode_full(self):
        """Test override mode forcing Full SDD."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="full",
        )
        assessment.complexity.add_dimension("Effort", 2, "Low")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.FULL_SDD
        assert confidence == Confidence.MEDIUM

    def test_override_mode_light(self):
        """Test override mode forcing Spec-Light."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="light",
        )
        assessment.complexity.add_dimension("Effort", 8, "High")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SPEC_LIGHT
        assert confidence == Confidence.MEDIUM

    def test_override_mode_skip(self):
        """Test override mode forcing Skip SDD."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="skip",
        )
        assessment.complexity.add_dimension("Effort", 8, "High")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SKIP_SDD
        assert confidence == Confidence.MEDIUM

    def test_get_rationale_full_sdd(self):
        """Test rationale generation for Full SDD."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Test")
        assessment.complexity.add_dimension("Effort", 9, "Very high")

        # Act
        rationale = assessment.get_rationale()

        # Assert
        assert "full sdd workflow" in rationale.lower()
        assert "9.0/10" in rationale

    def test_get_rationale_override(self):
        """Test rationale generation with override mode."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="full",
        )

        # Act
        rationale = assessment.get_rationale()

        # Assert
        assert "overridden" in rationale.lower()
        assert "bypassed" in rationale.lower()

    def test_get_next_steps_full_sdd(self):
        """Test next steps for Full SDD."""
        # Arrange
        assessment = FeatureAssessment(feature_name="User Auth")
        assessment.complexity.add_dimension("Effort", 8, "High")

        # Act
        next_steps = assessment.get_next_steps()

        # Assert
        assert "/flow:specify User Auth" in next_steps

    def test_get_next_steps_spec_light(self):
        """Test next steps for Spec-Light."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Simple Feature")
        assessment.complexity.add_dimension("Effort", 5, "Medium")

        # Act
        next_steps = assessment.get_next_steps()

        # Assert
        assert "./docs/prd/simple-feature-spec.md" in next_steps
        assert "lightweight spec" in next_steps.lower()

    def test_get_next_steps_skip_sdd(self):
        """Test next steps for Skip SDD."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Bug Fix")
        assessment.complexity.add_dimension("Effort", 2, "Low")

        # Act
        next_steps = assessment.get_next_steps()

        # Assert
        assert "direct" in next_steps.lower()
        assert "implementation" in next_steps.lower()

    def test_to_dict(self):
        """Test converting assessment to dictionary."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test Feature",
            description="Test description",
        )
        assessment.complexity.add_dimension("Effort", 5, "Medium")

        # Act
        result = assessment.to_dict()

        # Assert
        assert result["feature_name"] == "Test Feature"
        assert result["description"] == "Test description"
        assert "complexity" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert "next_steps" in result

    def test_from_dict(self):
        """Test creating assessment from dictionary."""
        # Arrange
        data = {
            "feature_name": "Test",
            "description": "Description",
            "assessed_by": "Test Agent",
            "assessed_at": "2025-01-15T10:30:00",
            "override_mode": None,
            "complexity": {
                "category": "Complexity",
                "dimensions": [
                    {
                        "name": "Effort",
                        "score": 6,
                        "rationale": "Medium",
                        "max_score": 10,
                    }
                ],
                "weight": 1.0,
            },
            "risk": {"category": "Risk", "dimensions": [], "weight": 1.0},
            "architecture_impact": {
                "category": "Architecture Impact",
                "dimensions": [],
                "weight": 1.0,
            },
        }

        # Act
        assessment = FeatureAssessment.from_dict(data)

        # Assert
        assert assessment.feature_name == "Test"
        assert assessment.description == "Description"
        assert assessment.assessed_by == "Test Agent"
        assert len(assessment.complexity.dimensions) == 1

    def test_generate_report_markdown(self):
        """Test generating markdown report."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test Feature",
            description="A test feature for validation",
        )
        assessment.complexity.add_dimension("Effort", 6, "Medium effort required")
        assessment.risk.add_dimension("Security", 7, "High security needs")

        # Act
        report = assessment.generate_report_markdown()

        # Assert
        assert "# Feature Assessment: Test Feature" in report
        assert "A test feature for validation" in report
        assert "## Scoring Analysis" in report
        assert "Complexity Score" in report
        assert "Risk Score" in report
        assert "## Overall Assessment" in report
        assert "## Next Steps" in report
        assert "## Override" in report

    def test_generate_report_with_override(self):
        """Test generating report with override mode."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="full",
        )

        # Act
        report = assessment.generate_report_markdown()

        # Assert
        assert "## Override Mode" in report
        assert "--mode full" in report
        assert "## Scoring Analysis" not in report

    def test_save_report(self, tmp_path):
        """Test saving report to file."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="User Authentication",
            description="OAuth integration",
        )
        assessment.complexity.add_dimension("Effort", 7, "Week of work")

        # Act
        report_path = assessment.save_report(tmp_path)

        # Assert
        assert report_path.exists()
        assert report_path.name == "user-authentication-assessment.md"
        content = report_path.read_text()
        assert "User Authentication" in content


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_complexity_assessment(self):
        """Test creating complexity assessment."""
        # Arrange & Act
        category = create_complexity_assessment(
            effort_score=6,
            effort_rationale="One week effort",
            component_score=4,
            component_rationale="3 components",
            integration_score=5,
            integration_rationale="2 integrations",
        )

        # Assert
        assert category.category == "Complexity"
        assert len(category.dimensions) == 3
        assert category.dimensions[0].name == "Effort Days"
        assert category.dimensions[1].name == "Component Count"
        assert category.dimensions[2].name == "Integration Points"
        assert category.average_score == pytest.approx((6 + 4 + 5) / 3)

    def test_create_risk_assessment(self):
        """Test creating risk assessment."""
        # Arrange & Act
        category = create_risk_assessment(
            security_score=8,
            security_rationale="High security needs",
            compliance_score=5,
            compliance_rationale="Standard compliance",
            data_score=7,
            data_rationale="Customer PII",
        )

        # Assert
        assert category.category == "Risk"
        assert len(category.dimensions) == 3
        assert category.dimensions[0].name == "Security Implications"
        assert category.dimensions[1].name == "Compliance Requirements"
        assert category.dimensions[2].name == "Data Sensitivity"
        assert category.average_score == pytest.approx((8 + 5 + 7) / 3)

    def test_create_architecture_impact_assessment(self):
        """Test creating architecture impact assessment."""
        # Arrange & Act
        category = create_architecture_impact_assessment(
            patterns_score=6,
            patterns_rationale="New auth pattern",
            breaking_score=3,
            breaking_rationale="Minor breaking changes",
            dependencies_score=4,
            dependencies_rationale="2 services affected",
        )

        # Assert
        assert category.category == "Architecture Impact"
        assert len(category.dimensions) == 3
        assert category.dimensions[0].name == "New Patterns"
        assert category.dimensions[1].name == "Breaking Changes"
        assert category.dimensions[2].name == "Dependencies Affected"
        assert category.average_score == pytest.approx((6 + 3 + 4) / 3)


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_assessment_with_no_dimensions(self):
        """Test assessment with empty categories."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Empty Test")

        # Act
        recommendation, confidence = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.SKIP_SDD
        assert confidence == Confidence.HIGH
        assert assessment.total_score == 0.0

    def test_assessment_boundary_score_18(self):
        """Test boundary at total score = 18."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Boundary Test")
        # Create exact score of 18
        assessment.complexity.add_dimension("Effort", 6, "Medium")
        assessment.risk.add_dimension("Security", 6, "Medium")
        assessment.architecture_impact.add_dimension("Patterns", 6, "Medium")

        # Act
        recommendation, _ = assessment.get_recommendation()

        # Assert
        assert assessment.total_score == pytest.approx(18.0)
        assert recommendation == WorkflowRecommendation.FULL_SDD

    def test_assessment_boundary_score_17_9(self):
        """Test just below boundary at total score = 17.9."""
        # Arrange
        assessment = FeatureAssessment(feature_name="Below Boundary")
        assessment.complexity.add_dimension("Effort", 5, "Low")
        assessment.complexity.add_dimension("Components", 6, "Medium")
        assessment.risk.add_dimension("Security", 6, "Medium")
        assessment.architecture_impact.add_dimension("Patterns", 6, "Medium")
        # Total: 5.5 + 6 + 6 = 17.5

        # Act
        recommendation, _ = assessment.get_recommendation()

        # Assert
        assert assessment.total_score < 18.0
        assert recommendation == WorkflowRecommendation.SPEC_LIGHT

    def test_feature_name_with_spaces_and_special_chars(self):
        """Test feature names with special characters."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="User Auth (OAuth 2.0)",
        )
        assessment.complexity.add_dimension("Effort", 5, "Medium")

        # Act
        next_steps = assessment.get_next_steps()

        # Assert
        assert "user-auth-(oauth-2.0)" in next_steps.lower()

    def test_invalid_override_mode(self):
        """Test invalid override mode defaults to Full SDD."""
        # Arrange
        assessment = FeatureAssessment(
            feature_name="Test",
            override_mode="invalid",
        )

        # Act
        recommendation, _ = assessment.get_recommendation()

        # Assert
        assert recommendation == WorkflowRecommendation.FULL_SDD
