"""Tests for risk scoring module."""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from flowspec_cli.security.models import Finding, Location, Severity
from flowspec_cli.security.triage.risk_scorer import (
    RiskScorer,
    calculate_risk_score,
)


def make_finding(
    severity: Severity = Severity.HIGH,
    cwe_id: str | None = None,
    file_path: str = "test.py",
    line_start: int = 10,
    metadata: dict | None = None,
) -> Finding:
    """Create a test finding."""
    return Finding(
        id="TEST-001",
        scanner="test",
        severity=severity,
        title="Test Finding",
        description="Test description",
        location=Location(
            file=Path(file_path),
            line_start=line_start,
            line_end=line_start + 2,
            code_snippet="test code",
        ),
        cwe_id=cwe_id,
        metadata=metadata or {},
    )


class TestRiskScorerInitialization:
    """Tests for RiskScorer initialization."""

    def test_initialization(self):
        """Test RiskScorer can be initialized."""
        scorer = RiskScorer()
        assert scorer is not None


class TestRiskScorerScore:
    """Tests for score method."""

    def test_score_returns_components(self):
        """Test that score returns all risk components."""
        scorer = RiskScorer()
        finding = make_finding()

        result = scorer.score(finding)

        assert result.impact > 0
        assert result.exploitability > 0
        assert result.detection_time > 0

    def test_score_with_llm_client(self):
        """Test scoring with LLM client provided."""
        scorer = RiskScorer()
        finding = make_finding()
        mock_llm = Mock()

        result = scorer.score(finding, llm_client=mock_llm)

        # Should still calculate scores even with LLM
        assert result.impact > 0
        assert result.exploitability > 0

    def test_score_different_severities(self):
        """Test scoring with different severity levels."""
        scorer = RiskScorer()

        critical_finding = make_finding(severity=Severity.CRITICAL)
        critical_result = scorer.score(critical_finding)

        info_finding = make_finding(severity=Severity.INFO)
        info_result = scorer.score(info_finding)

        # Critical should have higher impact
        assert critical_result.impact > info_result.impact


class TestGetImpact:
    """Tests for _get_impact method."""

    def test_impact_from_cvss_score(self):
        """Test impact calculation from CVSS score."""
        scorer = RiskScorer()
        finding = make_finding(metadata={"cvss_score": 8.5})

        impact = scorer._get_impact(finding)

        assert impact == 8.5

    def test_impact_from_severity_critical(self):
        """Test impact calculation for critical severity."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.CRITICAL)

        impact = scorer._get_impact(finding)

        assert impact == 9.5

    def test_impact_from_severity_high(self):
        """Test impact calculation for high severity."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.HIGH)

        impact = scorer._get_impact(finding)

        assert impact == 7.5

    def test_impact_from_severity_medium(self):
        """Test impact calculation for medium severity."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.MEDIUM)

        impact = scorer._get_impact(finding)

        assert impact == 5.0

    def test_impact_from_severity_low(self):
        """Test impact calculation for low severity."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.LOW)

        impact = scorer._get_impact(finding)

        assert impact == 2.5

    def test_impact_from_severity_info(self):
        """Test impact calculation for info severity."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.INFO)

        impact = scorer._get_impact(finding)

        assert impact == 0.5

    def test_impact_cvss_overrides_severity(self):
        """Test that CVSS score takes precedence over severity."""
        scorer = RiskScorer()
        # Low severity but high CVSS
        finding = make_finding(severity=Severity.LOW, metadata={"cvss_score": 9.0})

        impact = scorer._get_impact(finding)

        assert impact == 9.0  # Uses CVSS, not severity mapping


class TestGetExploitability:
    """Tests for _get_exploitability method."""

    def test_exploitability_command_injection(self):
        """Test exploitability for command injection (CWE-78)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-78")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 9.0

    def test_exploitability_hardcoded_credentials(self):
        """Test exploitability for hardcoded credentials (CWE-798)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-798")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 9.0

    def test_exploitability_sql_injection(self):
        """Test exploitability for SQL injection (CWE-89)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-89")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 8.5

    def test_exploitability_xss(self):
        """Test exploitability for XSS (CWE-79)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-79")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 8.0

    def test_exploitability_path_traversal(self):
        """Test exploitability for path traversal (CWE-22)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-22")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 7.0

    def test_exploitability_ssrf(self):
        """Test exploitability for SSRF (CWE-918)."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-918")

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 6.5

    def test_exploitability_unknown_cwe_uses_severity(self):
        """Test exploitability falls back to severity for unknown CWE."""
        scorer = RiskScorer()
        finding = make_finding(cwe_id="CWE-9999", severity=Severity.CRITICAL)

        exploitability = scorer._get_exploitability(finding)

        # Should use severity-based mapping
        assert exploitability == 8.0  # Critical -> 8.0

    def test_exploitability_no_cwe_uses_severity(self):
        """Test exploitability uses severity when no CWE provided."""
        scorer = RiskScorer()
        finding = make_finding(severity=Severity.HIGH)

        exploitability = scorer._get_exploitability(finding)

        assert exploitability == 6.5  # High -> 6.5

    def test_exploitability_severity_mapping(self):
        """Test complete severity-based exploitability mapping."""
        scorer = RiskScorer()

        severities = [
            (Severity.CRITICAL, 8.0),
            (Severity.HIGH, 6.5),
            (Severity.MEDIUM, 4.5),
            (Severity.LOW, 2.5),
            (Severity.INFO, 1.0),
        ]

        for severity, expected_exploit in severities:
            finding = make_finding(severity=severity)
            exploitability = scorer._get_exploitability(finding)
            assert exploitability == expected_exploit


class TestGetDetectionTime:
    """Tests for _get_detection_time method."""

    def test_detection_time_no_file_path(self):
        """Test detection time when no file path is provided."""
        scorer = RiskScorer()
        finding = make_finding(file_path="")

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default

    def test_detection_time_no_line_start(self):
        """Test detection time when no line number is provided."""
        scorer = RiskScorer()
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=Location(
                file=Path("test.py"),
                line_start=None,
                line_end=None,
                code_snippet="test",
            ),
        )

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default

    def test_detection_time_file_not_exists(self, tmp_path):
        """Test detection time when file doesn't exist."""
        scorer = RiskScorer()
        finding = make_finding(file_path=str(tmp_path / "nonexistent.py"))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default

    @patch("subprocess.run")
    def test_detection_time_git_blame_success(self, mock_run, tmp_path):
        """Test detection time with successful git blame."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Create .git directory to simulate git repo
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Mock git blame output
        # 30 days ago
        timestamp = int((datetime.now() - timedelta(days=30)).timestamp())
        mock_run.return_value = Mock(
            returncode=0, stdout=f"abc123 1 1 1\ncommitter-time {timestamp}\n"
        )

        scorer = RiskScorer()
        finding = make_finding(file_path=str(test_file))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30

    @patch("subprocess.run")
    def test_detection_time_git_blame_minimum_one_day(self, mock_run, tmp_path):
        """Test detection time is minimum 1 day."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Today's timestamp (0 days ago)
        timestamp = int(datetime.now().timestamp())
        mock_run.return_value = Mock(
            returncode=0, stdout=f"abc123 1 1 1\ncommitter-time {timestamp}\n"
        )

        scorer = RiskScorer()
        finding = make_finding(file_path=str(test_file))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 1  # Minimum 1 day

    @patch("subprocess.run")
    def test_detection_time_git_blame_failure(self, mock_run, tmp_path):
        """Test detection time when git blame fails."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        mock_run.return_value = Mock(returncode=1, stdout="")

        scorer = RiskScorer()
        finding = make_finding(file_path=str(test_file))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default on failure

    @patch("subprocess.run")
    def test_detection_time_git_timeout(self, mock_run, tmp_path):
        """Test detection time when git blame times out."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)

        scorer = RiskScorer()
        finding = make_finding(file_path=str(test_file))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default on timeout

    def test_detection_time_no_git_repo(self, tmp_path):
        """Test detection time when file is not in a git repo."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        scorer = RiskScorer()
        finding = make_finding(file_path=str(test_file))

        detection_time = scorer._get_detection_time(finding)

        assert detection_time == 30  # Default when no .git


class TestFindGitRoot:
    """Tests for _find_git_root method."""

    def test_find_git_root_in_same_directory(self, tmp_path):
        """Test finding git root in same directory as file."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        test_file = tmp_path / "test.py"
        test_file.touch()

        scorer = RiskScorer()
        git_root = scorer._find_git_root(test_file)

        assert git_root == tmp_path

    def test_find_git_root_in_parent_directory(self, tmp_path):
        """Test finding git root in parent directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        subdir = tmp_path / "src" / "deep" / "nested"
        subdir.mkdir(parents=True)
        test_file = subdir / "test.py"
        test_file.touch()

        scorer = RiskScorer()
        git_root = scorer._find_git_root(test_file)

        assert git_root == tmp_path

    def test_find_git_root_not_found(self, tmp_path):
        """Test when git root is not found."""
        test_file = tmp_path / "test.py"
        test_file.touch()

        scorer = RiskScorer()
        git_root = scorer._find_git_root(test_file)

        assert git_root is None

    def test_find_git_root_with_directory(self, tmp_path):
        """Test finding git root when given a directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        subdir = tmp_path / "src"
        subdir.mkdir()

        scorer = RiskScorer()
        git_root = scorer._find_git_root(subdir)

        assert git_root == tmp_path

    def test_find_git_root_stops_at_filesystem_root(self, tmp_path):
        """Test that search stops at filesystem root."""
        # Use a temp file that's definitely not in a git repo
        test_file = tmp_path / "test.py"
        test_file.touch()

        scorer = RiskScorer()
        git_root = scorer._find_git_root(test_file)

        # Should return None if no .git found before reaching root
        assert git_root is None


class TestCalculateRiskScore:
    """Tests for calculate_risk_score function."""

    def test_calculate_risk_score_basic(self):
        """Test basic risk score calculation."""
        score = calculate_risk_score(impact=8.0, exploitability=9.0, detection_time=30)

        expected = (8.0 * 9.0) / 30
        assert score == round(expected, 2)

    def test_calculate_risk_score_high_risk(self):
        """Test high risk scenario (recent, severe, exploitable)."""
        score = calculate_risk_score(impact=9.5, exploitability=9.0, detection_time=1)

        # Very high score for day-old critical issue
        assert score > 80.0

    def test_calculate_risk_score_low_risk(self):
        """Test low risk scenario (old, low severity, hard to exploit)."""
        score = calculate_risk_score(impact=2.0, exploitability=2.0, detection_time=365)

        # Very low score for old, minor issue
        assert score < 1.0

    def test_calculate_risk_score_zero_detection_time(self):
        """Test that zero detection time is treated as 1."""
        score = calculate_risk_score(impact=8.0, exploitability=8.0, detection_time=0)

        # Should use 1 instead of 0 to avoid division by zero
        expected = (8.0 * 8.0) / 1
        assert score == round(expected, 2)

    def test_calculate_risk_score_rounding(self):
        """Test that score is rounded to 2 decimal places."""
        score = calculate_risk_score(
            impact=7.333, exploitability=6.666, detection_time=13
        )

        # Check it's rounded to 2 decimals
        assert isinstance(score, float)
        assert len(str(score).split(".")[-1]) <= 2


class TestRiskScorerIntegration:
    """Integration tests for complete risk scoring workflow."""

    def test_score_sql_injection_finding(self, tmp_path):
        """Test scoring a SQL injection finding."""
        # Create a test file
        test_file = tmp_path / "app.py"
        test_file.write_text("query = f'SELECT * FROM users WHERE id={user_id}'")

        scorer = RiskScorer()
        finding = make_finding(
            severity=Severity.HIGH,
            cwe_id="CWE-89",  # SQL Injection
            file_path=str(test_file),
            metadata={"cvss_score": 8.5},
        )

        result = scorer.score(finding)

        # SQL injection should have high exploitability
        assert result.impact == 8.5  # From CVSS
        assert result.exploitability == 8.5  # High for SQL injection
        assert result.detection_time > 0

    def test_score_hardcoded_secret_finding(self, tmp_path):
        """Test scoring a hardcoded secret finding."""
        test_file = tmp_path / "config.py"
        test_file.write_text("API_KEY = 'sk-1234567890abcdef'")

        scorer = RiskScorer()
        finding = make_finding(
            severity=Severity.CRITICAL,
            cwe_id="CWE-798",  # Hardcoded credentials
            file_path=str(test_file),
        )

        result = scorer.score(finding)

        # Hardcoded secrets are critical and trivially exploitable
        assert result.impact == 9.5  # Critical severity
        assert result.exploitability == 9.0  # Trivial to exploit

    def test_score_info_level_finding(self, tmp_path):
        """Test scoring a low-priority info finding."""
        test_file = tmp_path / "utils.py"
        test_file.write_text("# TODO: Add input validation")

        scorer = RiskScorer()
        finding = make_finding(severity=Severity.INFO, file_path=str(test_file))

        result = scorer.score(finding)

        # Info findings should have low impact and exploitability
        assert result.impact == 0.5
        assert result.exploitability == 1.0
