"""Tests for the TriageEngine."""

from pathlib import Path
from unittest.mock import Mock


from specify_cli.security.models import Finding, Location, Severity
from specify_cli.security.triage.models import Classification, ClusterType
from specify_cli.security.triage.engine import TriageEngine, TriageConfig


def make_finding(
    id: str = "TEST-001",
    title: str = "Test Finding",
    severity: Severity = Severity.HIGH,
    cwe_id: str | None = None,
    code_snippet: str = "",
    file_path: str = "test.py",
    line_start: int = 10,
) -> Finding:
    """Create a test finding."""
    return Finding(
        id=id,
        scanner="test",
        severity=severity,
        title=title,
        description="Test description",
        location=Location(
            file=Path(file_path),
            line_start=line_start,
            line_end=line_start + 2,
            code_snippet=code_snippet,
        ),
        cwe_id=cwe_id,
    )


class TestTriageEngine:
    """Tests for TriageEngine."""

    def test_initialization(self):
        """Test engine initializes with default config."""
        engine = TriageEngine()

        assert engine.config.min_cluster_size == 3
        assert "sql_injection" in engine.classifiers
        assert "default" in engine.classifiers

    def test_initialization_with_config(self):
        """Test engine with custom config."""
        config = TriageConfig(min_cluster_size=5)
        engine = TriageEngine(config=config)

        assert engine.config.min_cluster_size == 5

    def test_get_classifier_sql_injection(self):
        """Test correct classifier selected for SQL injection."""
        engine = TriageEngine()
        classifier = engine.get_classifier("CWE-89")

        assert classifier == engine.classifiers["sql_injection"]

    def test_get_classifier_xss(self):
        """Test correct classifier selected for XSS."""
        engine = TriageEngine()
        classifier = engine.get_classifier("CWE-79")

        assert classifier == engine.classifiers["xss"]

    def test_get_classifier_unknown_cwe(self):
        """Test default classifier for unknown CWE."""
        engine = TriageEngine()
        classifier = engine.get_classifier("CWE-999")

        assert classifier == engine.classifiers["default"]

    def test_triage_single_finding(self):
        """Test triaging a single finding."""
        engine = TriageEngine()
        finding = make_finding(
            cwe_id="CWE-89",
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
        )

        results = engine.triage([finding])

        assert len(results) == 1
        assert results[0].finding_id == "TEST-001"
        assert results[0].classification == Classification.TRUE_POSITIVE
        assert results[0].risk_score > 0
        assert results[0].explanation is not None

    def test_triage_multiple_findings(self):
        """Test triaging multiple findings."""
        engine = TriageEngine()
        findings = [
            make_finding(id="F1", cwe_id="CWE-89"),
            make_finding(id="F2", cwe_id="CWE-79"),
            make_finding(id="F3", cwe_id="CWE-22"),
        ]

        results = engine.triage(findings)

        assert len(results) == 3
        finding_ids = {r.finding_id for r in results}
        assert finding_ids == {"F1", "F2", "F3"}

    def test_results_sorted_by_risk_score(self):
        """Test results are sorted by risk score descending."""
        engine = TriageEngine()
        findings = [
            make_finding(id="LOW", severity=Severity.LOW),
            make_finding(id="HIGH", severity=Severity.HIGH),
            make_finding(id="CRITICAL", severity=Severity.CRITICAL),
        ]

        results = engine.triage(findings)

        # Results should be sorted highest risk first
        assert results[0].finding_id == "CRITICAL"
        assert results[-1].finding_id == "LOW"


class TestClustering:
    """Tests for finding clustering."""

    def test_cluster_by_cwe(self):
        """Test findings clustered by CWE."""
        config = TriageConfig(min_cluster_size=2)  # Lower threshold for test
        engine = TriageEngine(config=config)

        # 3 SQL injection findings - should cluster
        findings = [
            make_finding(id="SQL1", cwe_id="CWE-89", file_path="file1.py"),
            make_finding(id="SQL2", cwe_id="CWE-89", file_path="file2.py"),
            make_finding(id="SQL3", cwe_id="CWE-89", file_path="file3.py"),
        ]

        results = engine.triage(findings)

        # All should be in same cluster
        cluster_ids = {r.cluster_id for r in results}
        assert len(cluster_ids) == 1
        assert "CWE-89" in list(cluster_ids)[0]

        # All should have CWE cluster type
        for result in results:
            assert result.cluster_type == ClusterType.CWE

    def test_cluster_by_file(self):
        """Test findings clustered by file when not in CWE cluster."""
        config = TriageConfig(min_cluster_size=5, min_file_cluster_size=2)
        engine = TriageEngine(config=config)

        # 2 findings in same file with different CWEs
        findings = [
            make_finding(id="F1", cwe_id="CWE-89", file_path="vulnerable.py"),
            make_finding(id="F2", cwe_id="CWE-79", file_path="vulnerable.py"),
        ]

        results = engine.triage(findings)

        # Should be in file cluster (not enough for CWE cluster)
        cluster_ids = {r.cluster_id for r in results if r.cluster_id}
        assert len(cluster_ids) == 1
        assert "FILE" in list(cluster_ids)[0]

    def test_no_cluster_single_finding(self):
        """Test single finding doesn't form cluster."""
        engine = TriageEngine()
        findings = [make_finding(id="LONE", cwe_id="CWE-999")]

        results = engine.triage(findings)

        assert results[0].cluster_id is None
        assert results[0].cluster_type is None


class TestExplanation:
    """Tests for explanation generation."""

    def test_heuristic_explanation(self):
        """Test explanation generated without LLM."""
        engine = TriageEngine()
        finding = make_finding(cwe_id="CWE-89", title="SQL Injection")

        results = engine.triage([finding])
        explanation = results[0].explanation

        assert explanation.what is not None
        assert explanation.why_it_matters is not None
        assert explanation.how_to_fix is not None

    def test_explanation_with_mocked_llm(self):
        """Test explanation generation with mocked LLM."""
        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "what": "AI-generated description",
            "why_it_matters": "AI-generated impact",
            "how_to_exploit": "AI attack scenario",
            "how_to_fix": "AI fix guidance"
        }
        """
        engine = TriageEngine(llm_client=mock_llm)
        finding = make_finding()

        results = engine.triage([finding])

        # LLM should be called for explanation
        assert mock_llm.complete.called
        # Verify explanation was generated
        assert results[0].explanation is not None


class TestRiskScoring:
    """Tests for risk scoring integration."""

    def test_risk_components_in_metadata(self):
        """Test risk components stored in metadata."""
        engine = TriageEngine()
        finding = make_finding(severity=Severity.HIGH)

        results = engine.triage([finding])
        metadata = results[0].metadata

        assert "impact" in metadata
        assert "exploitability" in metadata
        assert "detection_time" in metadata

    def test_high_severity_high_risk(self):
        """Test high severity gets high risk score."""
        engine = TriageEngine()
        high = make_finding(id="HIGH", severity=Severity.CRITICAL)
        low = make_finding(id="LOW", severity=Severity.LOW)

        results = engine.triage([high, low])

        high_result = next(r for r in results if r.finding_id == "HIGH")
        low_result = next(r for r in results if r.finding_id == "LOW")

        assert high_result.risk_score > low_result.risk_score
