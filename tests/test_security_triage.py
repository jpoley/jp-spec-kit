"""Tests for AI-powered triage engine.

This module tests:
1. Classification accuracy (TP/FP/NI)
2. Risk scoring using Raptor formula
3. Finding clustering by CWE and file
4. Explanation generation
"""

import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from flowspec_cli.security.triage.engine import TriageEngine, TriageConfig
from flowspec_cli.security.triage.models import (
    Classification,
    ClusterType,
    Explanation,
)
from flowspec_cli.security.triage.classifiers.base import (
    ClassificationResult,
    LLMClient,
)
from flowspec_cli.security.triage.risk_scorer import RiskScorer
from flowspec_cli.security.models import (
    Finding,
    Location,
    Severity,
    Confidence,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = Mock(spec=LLMClient)
    llm.complete.return_value = json.dumps(
        {
            "what": "SQL injection vulnerability in user input",
            "why_it_matters": "Attacker can access or modify database",
            "how_to_exploit": "Inject malicious SQL in user_id parameter",
            "how_to_fix": "Use parameterized queries",
        }
    )
    return llm


@pytest.fixture
def sql_injection_finding():
    """Create a SQL injection finding for testing."""
    return Finding(
        id="SEMGREP-001",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="SQL Injection",
        description="User input is passed directly to SQL query",
        location=Location(
            file=Path("app.py"),
            line_start=42,
            line_end=45,
            code_snippet='cursor.execute("SELECT * FROM users WHERE id = " + user_id)',
        ),
        cwe_id="CWE-89",
        confidence=Confidence.HIGH,
    )


@pytest.fixture
def xss_finding():
    """Create an XSS finding for testing."""
    return Finding(
        id="SEMGREP-002",
        scanner="semgrep",
        severity=Severity.MEDIUM,
        title="Cross-Site Scripting",
        description="Unescaped user input in HTML output",
        location=Location(
            file=Path("templates/user.html"),
            line_start=10,
            line_end=10,
            code_snippet="<div>{{ user_input }}</div>",
        ),
        cwe_id="CWE-79",
        confidence=Confidence.MEDIUM,
    )


@pytest.fixture
def hardcoded_secret_finding():
    """Create a hardcoded secret finding for testing."""
    return Finding(
        id="SEMGREP-003",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="Hardcoded Password",
        description="Password hardcoded in source code",
        location=Location(
            file=Path("config.py"),
            line_start=5,
            line_end=5,
            code_snippet='PASSWORD = "secret123"',
        ),
        cwe_id="CWE-798",
        confidence=Confidence.HIGH,
    )


# ============================================================================
# TriageEngine Tests
# ============================================================================


class TestTriageEngineBasics:
    """Test basic TriageEngine functionality."""

    def test_init_without_llm(self):
        """Test initializing engine without LLM (heuristic mode)."""
        engine = TriageEngine(llm_client=None)
        assert engine.llm is None
        assert engine.config is not None
        assert engine.risk_scorer is not None
        assert len(engine.classifiers) == 6  # 5 specialized + 1 default

    def test_init_with_llm(self, mock_llm):
        """Test initializing engine with LLM."""
        engine = TriageEngine(llm_client=mock_llm)
        assert engine.llm == mock_llm

    def test_init_with_custom_config(self):
        """Test initializing with custom configuration."""
        config = TriageConfig(
            min_cluster_size=5,
            min_file_cluster_size=3,
        )
        engine = TriageEngine(config=config)
        assert engine.config.min_cluster_size == 5
        assert engine.config.min_file_cluster_size == 3

    def test_cwe_classifier_mapping(self):
        """Test that CWEs map to correct classifiers."""
        engine = TriageEngine()

        # SQL injection CWEs
        sql_classifier = engine.get_classifier("CWE-89")
        assert "CWE-89" in sql_classifier.supported_cwes
        assert engine.get_classifier("CWE-564") == sql_classifier

        # XSS CWEs
        xss_classifier = engine.get_classifier("CWE-79")
        assert "CWE-79" in xss_classifier.supported_cwes

        # Path traversal CWEs
        path_classifier = engine.get_classifier("CWE-22")
        assert "CWE-22" in path_classifier.supported_cwes

        # Hardcoded secrets CWEs
        secret_classifier = engine.get_classifier("CWE-798")
        assert "CWE-798" in secret_classifier.supported_cwes

        # Weak crypto CWEs
        crypto_classifier = engine.get_classifier("CWE-327")
        assert "CWE-327" in crypto_classifier.supported_cwes

        # Unknown CWE defaults to default classifier
        default_classifier = engine.get_classifier("CWE-999")
        assert default_classifier == engine.classifiers["default"]


class TestClassification:
    """Test finding classification."""

    def test_classify_sql_injection(self, sql_injection_finding):
        """Test classification of SQL injection finding."""
        engine = TriageEngine()

        # Use internal method to get classification
        result = engine._classify(sql_injection_finding)

        assert result.classification in [
            Classification.TRUE_POSITIVE,
            Classification.FALSE_POSITIVE,
            Classification.NEEDS_INVESTIGATION,
        ]
        assert 0.0 <= result.confidence <= 1.0

    def test_classify_with_llm(self, mock_llm, sql_injection_finding):
        """Test classification with LLM assistance."""
        # Mock LLM response - use enum value "TP" not "TRUE_POSITIVE"
        mock_llm.complete.return_value = json.dumps(
            {
                "classification": "TP",
                "confidence": 0.95,
                "reasoning": "Direct SQL concatenation detected",
            }
        )

        engine = TriageEngine(llm_client=mock_llm)
        result = engine._classify(sql_injection_finding)

        # Verify LLM was called
        assert mock_llm.complete.called

        # Verify classification matches mocked LLM response
        assert result.classification == Classification.TRUE_POSITIVE
        assert result.confidence == pytest.approx(0.95)


class TestTriageSingle:
    """Test triaging individual findings."""

    def test_triage_single_finding(self, sql_injection_finding):
        """Test triaging a single finding."""
        engine = TriageEngine()
        result = engine._triage_single(sql_injection_finding)

        assert result.finding_id == "SEMGREP-001"
        assert result.classification in Classification
        assert 0.0 <= result.confidence <= 1.0
        assert result.risk_score >= 0.0
        assert isinstance(result.explanation, Explanation)
        assert result.explanation.what is not None
        assert result.explanation.why_it_matters is not None

    def test_triage_single_with_llm(self, mock_llm, sql_injection_finding):
        """Test triaging with LLM."""
        engine = TriageEngine(llm_client=mock_llm)
        result = engine._triage_single(sql_injection_finding)

        assert result.finding_id == "SEMGREP-001"
        assert mock_llm.complete.called


class TestTriageBatch:
    """Test triaging multiple findings."""

    def test_triage_empty_list(self):
        """Test triaging empty findings list."""
        engine = TriageEngine()
        results = engine.triage([])
        assert results == []

    def test_triage_single(self, sql_injection_finding):
        """Test triaging single finding."""
        engine = TriageEngine()
        results = engine.triage([sql_injection_finding])

        assert len(results) == 1
        assert results[0].finding_id == "SEMGREP-001"

    def test_triage_multiple(
        self, sql_injection_finding, xss_finding, hardcoded_secret_finding
    ):
        """Test triaging multiple findings."""
        engine = TriageEngine()
        findings = [sql_injection_finding, xss_finding, hardcoded_secret_finding]
        results = engine.triage(findings)

        assert len(results) == 3

        # Results should be sorted by risk score (highest first)
        for i in range(len(results) - 1):
            assert results[i].risk_score >= results[i + 1].risk_score

    def test_triage_results_sorted_by_risk(self):
        """Test that results are sorted by risk score descending."""
        engine = TriageEngine()

        # Create findings with different severities
        high_finding = Finding(
            id="HIGH-001",
            scanner="test",
            severity=Severity.CRITICAL,
            title="Critical Issue",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id="CWE-89",
        )

        low_finding = Finding(
            id="LOW-001",
            scanner="test",
            severity=Severity.LOW,
            title="Low Issue",
            description="Test",
            location=Location(file=Path("test.py"), line_start=10, line_end=10),
            cwe_id="CWE-79",
        )

        results = engine.triage([low_finding, high_finding])

        # High severity should be first
        assert results[0].risk_score >= results[1].risk_score


class TestClustering:
    """Test finding clustering."""

    def test_cluster_by_cwe(self):
        """Test clustering findings by CWE category."""
        engine = TriageEngine(config=TriageConfig(min_cluster_size=2))

        # Create multiple SQL injection findings
        findings = [
            Finding(
                id=f"SQL-{i}",
                scanner="test",
                severity=Severity.HIGH,
                title="SQL Injection",
                description="Test",
                location=Location(
                    file=Path(f"file{i}.py"),
                    line_start=i,
                    line_end=i,
                ),
                cwe_id="CWE-89",
            )
            for i in range(3)
        ]

        results = engine.triage(findings)

        # All should be clustered together
        cluster_ids = [r.cluster_id for r in results]
        assert cluster_ids[0] is not None
        assert all(cid == cluster_ids[0] for cid in cluster_ids)
        assert all(r.cluster_type == ClusterType.CWE for r in results)
        assert "CWE-89" in results[0].cluster_id

    def test_cluster_by_file(self):
        """Test clustering findings by file."""
        engine = TriageEngine(
            config=TriageConfig(
                min_cluster_size=10,  # Won't trigger CWE clustering
                min_file_cluster_size=2,
            )
        )

        # Create multiple findings in same file
        findings = [
            Finding(
                id=f"ISSUE-{i}",
                scanner="test",
                severity=Severity.MEDIUM,
                title=f"Issue {i}",
                description="Test",
                location=Location(
                    file=Path("app.py"),
                    line_start=i * 10,
                    line_end=i * 10,
                ),
                cwe_id=f"CWE-{i}",  # Different CWEs
            )
            for i in range(3)
        ]

        results = engine.triage(findings)

        # Should be clustered by file
        cluster_ids = [r.cluster_id for r in results]
        assert cluster_ids[0] is not None
        assert all(cid == cluster_ids[0] for cid in cluster_ids)
        assert all(r.cluster_type == ClusterType.FILE for r in results)
        assert "app" in results[0].cluster_id

    def test_no_clustering_below_threshold(self):
        """Test that small groups don't get clustered."""
        engine = TriageEngine(
            config=TriageConfig(min_cluster_size=5, min_file_cluster_size=5)
        )

        # Create only 2 findings (below threshold)
        findings = [
            Finding(
                id="ISSUE-1",
                scanner="test",
                severity=Severity.HIGH,
                title="Issue",
                description="Test",
                location=Location(file=Path("app.py"), line_start=1, line_end=1),
                cwe_id="CWE-89",
            ),
            Finding(
                id="ISSUE-2",
                scanner="test",
                severity=Severity.HIGH,
                title="Issue",
                description="Test",
                location=Location(file=Path("app.py"), line_start=10, line_end=10),
                cwe_id="CWE-89",
            ),
        ]

        results = engine.triage(findings)

        # Should not be clustered
        assert all(r.cluster_id is None for r in results)


class TestExplanationGeneration:
    """Test explanation generation."""

    def test_generate_heuristic_explanation(self, sql_injection_finding):
        """Test heuristic explanation generation (no LLM)."""
        engine = TriageEngine(llm_client=None)

        classification = ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.9,
            reasoning="Direct SQL concatenation",
        )

        explanation = engine._generate_heuristic_explanation(
            sql_injection_finding, classification
        )

        assert explanation.what is not None
        assert explanation.why_it_matters is not None
        assert explanation.how_to_fix is not None
        assert "SQL injection" in explanation.why_it_matters
        assert "parameterized" in explanation.how_to_fix

    def test_generate_heuristic_explanation_false_positive(self, sql_injection_finding):
        """Test heuristic explanation for false positive."""
        engine = TriageEngine(llm_client=None)

        classification = ClassificationResult(
            classification=Classification.FALSE_POSITIVE,
            confidence=0.8,
            reasoning="Test",
        )

        explanation = engine._generate_heuristic_explanation(
            sql_injection_finding, classification
        )

        # False positive shouldn't have exploit guidance
        assert explanation.how_to_exploit is None

    def test_generate_ai_explanation(self, mock_llm, sql_injection_finding):
        """Test AI-powered explanation generation."""
        mock_llm.complete.return_value = json.dumps(
            {
                "what": "SQL injection in user query",
                "why_it_matters": "Database compromise possible",
                "how_to_exploit": "Inject ' OR 1=1 --",
                "how_to_fix": "Use prepared statements",
            }
        )

        engine = TriageEngine(llm_client=mock_llm)

        classification = ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.95,
            reasoning="Test",
        )

        explanation = engine._generate_ai_explanation(
            sql_injection_finding, classification
        )

        assert "SQL injection" in explanation.what
        assert "Database compromise" in explanation.why_it_matters
        assert "prepared statements" in explanation.how_to_fix

    def test_generate_ai_explanation_fallback_on_error(
        self, mock_llm, sql_injection_finding
    ):
        """Test fallback to heuristic when AI fails."""
        mock_llm.complete.side_effect = Exception("API error")

        engine = TriageEngine(llm_client=mock_llm)

        classification = ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.9,
            reasoning="Test",
        )

        explanation = engine._generate_ai_explanation(
            sql_injection_finding, classification
        )

        # Should fall back to heuristic
        assert explanation.what is not None
        assert explanation.why_it_matters is not None

    def test_generate_ai_explanation_with_markdown_fence(
        self, mock_llm, sql_injection_finding
    ):
        """Test parsing AI response with markdown code fence."""
        mock_llm.complete.return_value = """```json
{
    "what": "SQL injection vulnerability",
    "why_it_matters": "Data theft risk",
    "how_to_exploit": "Inject malicious SQL",
    "how_to_fix": "Use parameterized queries"
}
```"""

        engine = TriageEngine(llm_client=mock_llm)

        classification = ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.9,
            reasoning="Test",
        )

        explanation = engine._generate_ai_explanation(
            sql_injection_finding, classification
        )

        assert "SQL injection" in explanation.what
        assert "parameterized queries" in explanation.how_to_fix

    def test_explanation_truncation(self):
        """Test that long explanations are truncated."""
        engine = TriageEngine(config=TriageConfig(explanation_max_length=50))

        long_description = "x" * 100
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description=long_description,
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
        )

        classification = ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.9,
            reasoning="Test",
        )

        explanation = engine._generate_heuristic_explanation(finding, classification)

        assert len(explanation.what) <= 50


class TestCWEGuidance:
    """Test CWE-specific guidance methods."""

    def test_get_cwe_impact(self):
        """Test CWE impact descriptions."""
        engine = TriageEngine()

        assert "SQL injection" in engine._get_cwe_impact("CWE-89")
        assert "XSS" in engine._get_cwe_impact("CWE-79")
        assert "Path traversal" in engine._get_cwe_impact("CWE-22")
        assert "secrets" in engine._get_cwe_impact("CWE-798")
        assert "crypto" in engine._get_cwe_impact("CWE-327")

        # Unknown CWE
        assert "compromise security" in engine._get_cwe_impact("CWE-999")

    def test_get_cwe_exploit_guidance(self):
        """Test CWE exploit scenarios."""
        engine = TriageEngine()

        assert "OR 1=1" in engine._get_cwe_exploit_guidance("CWE-89")
        assert "<script>" in engine._get_cwe_exploit_guidance("CWE-79")
        assert "../" in engine._get_cwe_exploit_guidance("CWE-22")
        assert "credentials" in engine._get_cwe_exploit_guidance("CWE-798")
        assert "rainbow" in engine._get_cwe_exploit_guidance("CWE-327")

    def test_get_cwe_fix_guidance(self):
        """Test CWE remediation guidance."""
        engine = TriageEngine()

        assert "parameterized" in engine._get_cwe_fix_guidance("CWE-89")
        assert "Escape" in engine._get_cwe_fix_guidance("CWE-79")
        assert "Validate" in engine._get_cwe_fix_guidance("CWE-22")
        assert "environment" in engine._get_cwe_fix_guidance("CWE-798")
        assert "AES" in engine._get_cwe_fix_guidance("CWE-327")


class TestRiskScorer:
    """Test risk scoring functionality."""

    def test_score_high_severity(self):
        """Test risk scoring for high severity finding."""
        scorer = RiskScorer()

        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.CRITICAL,
            title="Critical Issue",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cvss_score=9.8,
        )

        components = scorer.score(finding, llm_client=None)

        assert components.risk_score > 0
        assert components.impact > 0
        assert components.exploitability > 0
        assert 0 <= components.detection_time <= 365 * 10  # Max 10 years

    def test_score_low_severity(self):
        """Test risk scoring for low severity finding."""
        scorer = RiskScorer()

        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.LOW,
            title="Low Issue",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
        )

        components = scorer.score(finding, llm_client=None)

        assert components.risk_score >= 0

    def test_score_with_cvss(self):
        """Test that CVSS score is used when available."""
        scorer = RiskScorer()

        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cvss_score=8.5,
        )

        components = scorer.score(finding, llm_client=None)

        # CVSS should influence the score
        assert components.impact > 0
