"""Tests for triage data models."""

import pytest

from specify_cli.security.triage.models import (
    Classification,
    ClusterType,
    Explanation,
    RiskComponents,
    TriageResult,
)


class TestClassification:
    """Tests for Classification enum."""

    def test_values(self):
        """Test classification values."""
        assert Classification.TRUE_POSITIVE.value == "TP"
        assert Classification.FALSE_POSITIVE.value == "FP"
        assert Classification.NEEDS_INVESTIGATION.value == "NI"

    def test_from_value(self):
        """Test creating classification from value."""
        assert Classification("TP") == Classification.TRUE_POSITIVE
        assert Classification("FP") == Classification.FALSE_POSITIVE
        assert Classification("NI") == Classification.NEEDS_INVESTIGATION


class TestRiskComponents:
    """Tests for RiskComponents dataclass."""

    def test_risk_score_calculation(self):
        """Test Raptor formula calculation."""
        # High impact, high exploitability, short detection time
        components = RiskComponents(impact=9.0, exploitability=8.0, detection_time=1)
        assert components.risk_score == 72.0

    def test_risk_score_with_longer_detection(self):
        """Test risk score decreases with longer detection time."""
        components = RiskComponents(impact=9.0, exploitability=8.0, detection_time=10)
        assert components.risk_score == 7.2

    def test_risk_score_minimum_detection_time(self):
        """Test risk_score calculation uses minimum detection_time of 1.

        The risk_score property clamps detection_time to at least 1 in its
        calculation, but does not modify the stored detection_time value.
        """
        components = RiskComponents(impact=9.0, exploitability=8.0, detection_time=0)
        # risk_score uses max(detection_time, 1) = max(0, 1) = 1
        assert components.risk_score == 72.0
        # Verify stored value is unchanged
        assert components.detection_time == 0


class TestExplanation:
    """Tests for Explanation dataclass."""

    def test_creation(self):
        """Test creating an explanation."""
        exp = Explanation(
            what="SQL injection vulnerability",
            why_it_matters="Data theft possible",
            how_to_exploit="Use ' OR 1=1 --",
            how_to_fix="Use parameterized queries",
        )
        assert exp.what == "SQL injection vulnerability"
        assert exp.how_to_exploit == "Use ' OR 1=1 --"

    def test_optional_exploit(self):
        """Test explanation without exploit info (for FP)."""
        exp = Explanation(
            what="False positive",
            why_it_matters="N/A",
            how_to_exploit=None,
            how_to_fix="No fix needed",
        )
        assert exp.how_to_exploit is None


class TestTriageResult:
    """Tests for TriageResult dataclass."""

    @pytest.fixture
    def sample_result(self):
        """Create a sample triage result."""
        return TriageResult(
            finding_id="finding-001",
            classification=Classification.TRUE_POSITIVE,
            confidence=0.95,
            risk_score=45.0,
            explanation=Explanation(
                what="SQL injection in login",
                why_it_matters="Authentication bypass",
                how_to_exploit="Inject SQL",
                how_to_fix="Use prepared statements",
            ),
            cluster_id="CLUSTER-CWE-89",
            cluster_type=ClusterType.CWE,
            ai_reasoning="High confidence SQL injection",
        )

    def test_is_actionable_tp(self, sample_result):
        """Test is_actionable for true positive."""
        assert sample_result.is_actionable is True

    def test_is_actionable_fp(self, sample_result):
        """Test is_actionable for false positive."""
        sample_result.classification = Classification.FALSE_POSITIVE
        assert sample_result.is_actionable is False

    def test_requires_review_ni(self, sample_result):
        """Test requires_review for needs investigation."""
        sample_result.classification = Classification.NEEDS_INVESTIGATION
        assert sample_result.requires_review is True

    def test_requires_review_tp(self, sample_result):
        """Test requires_review for true positive."""
        assert sample_result.requires_review is False

    def test_to_dict(self, sample_result):
        """Test serialization to dict."""
        data = sample_result.to_dict()

        assert data["finding_id"] == "finding-001"
        assert data["classification"] == "TP"
        assert data["confidence"] == 0.95
        assert data["risk_score"] == 45.0
        assert data["explanation"]["what"] == "SQL injection in login"
        assert data["cluster_id"] == "CLUSTER-CWE-89"
        assert data["cluster_type"] == "cwe"

    def test_from_dict(self, sample_result):
        """Test deserialization from dict."""
        data = sample_result.to_dict()
        restored = TriageResult.from_dict(data)

        assert restored.finding_id == sample_result.finding_id
        assert restored.classification == sample_result.classification
        assert restored.confidence == sample_result.confidence
        assert restored.explanation.what == sample_result.explanation.what
