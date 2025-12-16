"""Tests for spec quality assessment."""

import json
from pathlib import Path
import pytest

from flowspec_cli.quality import QualityScorer, QualityConfig, QualityResult


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures" / "specs"


@pytest.fixture
def good_spec(fixtures_dir):
    """Return path to good quality spec."""
    return fixtures_dir / "good_spec.md"


@pytest.fixture
def poor_spec(fixtures_dir):
    """Return path to poor quality spec."""
    return fixtures_dir / "poor_spec.md"


@pytest.fixture
def medium_spec(fixtures_dir):
    """Return path to medium quality spec."""
    return fixtures_dir / "medium_spec.md"


@pytest.fixture
def default_config():
    """Return default quality configuration."""
    return QualityConfig()


class TestQualityConfig:
    """Tests for QualityConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = QualityConfig()
        assert config.passing_threshold == 70
        assert config.excellent_threshold == 90
        assert config.validate_weights()

    def test_weights_sum_to_one(self):
        """Test that default weights sum to 1.0."""
        config = QualityConfig()
        total = (
            config.completeness_weight
            + config.clarity_weight
            + config.traceability_weight
            + config.constitutional_weight
            + config.ambiguity_weight
        )
        assert abs(total - 1.0) < 0.01

    def test_load_from_file(self, tmp_path):
        """Test loading config from JSON file."""
        config_file = tmp_path / "quality-config.json"
        config_data = {
            "thresholds": {"passing": 80, "excellent": 95},
            "weights": {
                "completeness": 0.35,
                "clarity": 0.25,
                "traceability": 0.20,
                "constitutional": 0.10,
                "ambiguity": 0.10,
            },
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = QualityConfig.load_from_file(config_file)
        assert config.passing_threshold == 80
        assert config.excellent_threshold == 95
        assert config.completeness_weight == 0.35

    def test_find_config_in_specify_dir(self, tmp_path):
        """Test finding config in .specify directory."""
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()

        config_file = specify_dir / "quality-config.json"
        config_data = {"thresholds": {"passing": 85}}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        config = QualityConfig.find_config(tmp_path)
        assert config.passing_threshold == 85


class TestQualityScorer:
    """Tests for QualityScorer."""

    def test_score_good_spec(self, good_spec, default_config):
        """Test scoring a high-quality specification."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(good_spec)

        assert isinstance(result, QualityResult)
        assert result.overall_score >= 80
        assert result.passes()

        # Good spec should score well on all dimensions
        assert result.completeness.score >= 90
        assert result.clarity.score >= 70
        assert result.constitutional.score >= 80

    def test_score_poor_spec(self, poor_spec, default_config):
        """Test scoring a low-quality specification."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(poor_spec)

        assert isinstance(result, QualityResult)
        assert result.overall_score < 70
        assert not result.passes()

        # Poor spec should have low scores
        assert result.completeness.score < 80  # Missing sections
        assert result.clarity.score < 70  # Vague terms
        assert result.ambiguity.score < 80  # TBD/TODO markers

    def test_score_medium_spec(self, medium_spec, default_config):
        """Test scoring a medium-quality specification."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(medium_spec)

        assert isinstance(result, QualityResult)
        # Medium spec should be borderline
        assert 60 <= result.overall_score <= 85

    def test_invalid_spec_path(self, default_config):
        """Test error handling for non-existent spec file."""
        scorer = QualityScorer(default_config)

        with pytest.raises(FileNotFoundError):
            scorer.score_spec(Path("/nonexistent/spec.md"))

    def test_invalid_config_weights(self):
        """Test error handling for invalid weight configuration."""
        config = QualityConfig()
        config.completeness_weight = 0.5
        config.clarity_weight = 0.1
        # Weights don't sum to 1.0

        with pytest.raises(ValueError, match="weights must sum to 1.0"):
            QualityScorer(config)


class TestQualityResult:
    """Tests for QualityResult."""

    def test_passes_with_default_threshold(self, good_spec, default_config):
        """Test passing check with default threshold."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(good_spec)

        assert result.passes()

    def test_passes_with_custom_threshold(self, medium_spec, default_config):
        """Test passing check with custom threshold."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(medium_spec)

        # Should pass with lower threshold
        assert result.passes(threshold=50)

        # May not pass with higher threshold
        # (depends on actual score, so we just test the method works)
        result.passes(threshold=90)

    def test_is_excellent(self, good_spec, default_config):
        """Test excellence check."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(good_spec)

        # Good spec might be excellent
        if result.overall_score >= 90:
            assert result.is_excellent()

    def test_get_recommendations(self, poor_spec, default_config):
        """Test recommendation generation."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(poor_spec)

        recommendations = result.get_recommendations()
        assert len(recommendations) > 0
        assert isinstance(recommendations[0], str)

        # Poor spec should have multiple recommendations
        assert len(recommendations) >= 3

    def test_recommendations_for_good_spec(self, good_spec, default_config):
        """Test that good specs get positive feedback."""
        scorer = QualityScorer(default_config)
        result = scorer.score_spec(good_spec)

        recommendations = result.get_recommendations()
        assert len(recommendations) >= 1

        # If score is high, should mention it meets standards
        if result.overall_score >= 90:
            assert any(
                "meets" in rec.lower() or "excellent" in rec.lower()
                for rec in recommendations
            )


class TestDimensionScoring:
    """Tests for individual dimension scoring."""

    def test_completeness_scoring(self, good_spec, poor_spec, default_config):
        """Test completeness dimension scoring."""
        scorer = QualityScorer(default_config)

        good_result = scorer.score_spec(good_spec)
        poor_result = scorer.score_spec(poor_spec)

        # Good spec has all required sections
        assert good_result.completeness.score > poor_result.completeness.score
        assert len(good_result.completeness.details["missing_sections"]) == 0
        assert len(poor_result.completeness.details["missing_sections"]) > 0

    def test_clarity_scoring(self, good_spec, poor_spec, default_config):
        """Test clarity dimension scoring."""
        scorer = QualityScorer(default_config)

        good_result = scorer.score_spec(good_spec)
        poor_result = scorer.score_spec(poor_spec)

        # Poor spec has more vague terms
        assert good_result.clarity.score > poor_result.clarity.score
        assert poor_result.clarity.details["vague_count"] > 0

    def test_ambiguity_scoring(self, good_spec, poor_spec, default_config):
        """Test ambiguity dimension scoring."""
        scorer = QualityScorer(default_config)

        good_result = scorer.score_spec(good_spec)
        poor_result = scorer.score_spec(poor_spec)

        # Poor spec has TBD/TODO markers
        assert good_result.ambiguity.score > poor_result.ambiguity.score
        assert poor_result.ambiguity.details["marker_count"] > 0

    def test_constitutional_scoring(self, good_spec, poor_spec, default_config):
        """Test constitutional compliance scoring."""
        scorer = QualityScorer(default_config)

        good_result = scorer.score_spec(good_spec)
        poor_result = scorer.score_spec(poor_spec)

        # Good spec mentions required tools
        assert good_result.constitutional.score > poor_result.constitutional.score
        assert len(good_result.constitutional.details["found_patterns"]) > 0


class TestWeightedScoring:
    """Tests for weighted score calculation."""

    def test_weighted_calculation(self, good_spec):
        """Test that overall score is correctly weighted."""
        config = QualityConfig()
        scorer = QualityScorer(config)
        result = scorer.score_spec(good_spec)

        # Manually calculate expected score
        expected = (
            result.completeness.score * config.completeness_weight
            + result.clarity.score * config.clarity_weight
            + result.traceability.score * config.traceability_weight
            + result.constitutional.score * config.constitutional_weight
            + result.ambiguity.score * config.ambiguity_weight
        )

        assert abs(result.overall_score - expected) < 0.1

    def test_custom_weights(self, good_spec):
        """Test scoring with custom weights."""
        config = QualityConfig()
        # Emphasize completeness
        config.completeness_weight = 0.50
        config.clarity_weight = 0.20
        config.traceability_weight = 0.15
        config.constitutional_weight = 0.10
        config.ambiguity_weight = 0.05

        scorer = QualityScorer(config)
        result = scorer.score_spec(good_spec)

        # Should still produce valid score
        assert 0 <= result.overall_score <= 100
        assert result.passes()
