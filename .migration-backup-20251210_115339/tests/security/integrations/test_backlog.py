"""Tests for backlog integration."""

from pathlib import Path

import pytest

from specify_cli.security.models import Finding, Location, Severity, Confidence
from specify_cli.security.integrations.backlog import (
    BacklogIntegration,
    FindingTask,
    create_tasks_from_findings,
)


@pytest.fixture
def sample_finding():
    """Create a sample finding."""
    return Finding(
        id="SEMGREP-001",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="SQL Injection",
        description="User input is concatenated into SQL query",
        location=Location(
            file=Path("src/db.py"),
            line_start=42,
            line_end=45,
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
        ),
        cwe_id="CWE-89",
        confidence=Confidence.HIGH,
        remediation="Use parameterized queries instead of string concatenation",
        references=["https://owasp.org/SQL_Injection"],
    )


@pytest.fixture
def sample_findings():
    """Create multiple sample findings."""
    return [
        Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=Location(file=Path("src/db.py"), line_start=42, line_end=45),
            cwe_id="CWE-89",
        ),
        Finding(
            id="SEMGREP-002",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="XSS Vulnerability",
            description="Cross-site scripting",
            location=Location(file=Path("src/web.py"), line_start=100, line_end=102),
            cwe_id="CWE-79",
        ),
        Finding(
            id="SEMGREP-003",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Another SQL injection",
            location=Location(file=Path("src/api.py"), line_start=50, line_end=52),
            cwe_id="CWE-89",
        ),
        Finding(
            id="SEMGREP-004",
            scanner="semgrep",
            severity=Severity.MEDIUM,
            title="Path Traversal",
            description="Path traversal vulnerability",
            location=Location(file=Path("src/files.py"), line_start=20, line_end=22),
            cwe_id="CWE-22",
        ),
    ]


class TestFindingTask:
    """Tests for FindingTask dataclass."""

    def test_to_backlog_format(self, sample_finding):
        """Test converting to backlog format."""
        task = FindingTask(
            title="Fix HIGH: SQL Injection",
            description="Vulnerability in db.py",
            severity="high",
            cwe_id="CWE-89",
            location="src/db.py:42",
            finding_id="SEMGREP-001",
            priority="high",
            labels=["security", "high", "cwe89"],
            acceptance_criteria=["Fix the vulnerability", "Add test"],
        )

        data = task.to_backlog_format()

        assert data["title"] == "Fix HIGH: SQL Injection"
        assert data["priority"] == "high"
        assert "security" in data["labels"]
        assert len(data["acceptanceCriteria"]) == 2

    def test_to_markdown(self, sample_finding):
        """Test generating markdown."""
        task = FindingTask(
            title="Fix HIGH: SQL Injection",
            description="SQL injection vulnerability",
            severity="high",
            cwe_id="CWE-89",
            location="src/db.py:42",
            finding_id="SEMGREP-001",
            priority="high",
            acceptance_criteria=["Fix vulnerability", "Add test"],
        )

        md = task.to_markdown()

        assert "## Fix HIGH: SQL Injection" in md
        assert "**Severity:** high" in md
        assert "**CWE:** CWE-89" in md
        assert "- [ ] Fix vulnerability" in md


class TestBacklogIntegration:
    """Tests for BacklogIntegration."""

    @pytest.fixture
    def integration(self):
        """Create a backlog integration instance."""
        return BacklogIntegration()

    def test_create_individual_tasks(self, integration, sample_findings):
        """Test creating individual tasks."""
        tasks = integration.create_tasks(sample_findings)

        assert len(tasks) == 4
        # First should be critical
        assert tasks[0].severity == "critical"
        assert "SQL Injection" in tasks[0].title

    def test_create_grouped_tasks(self, sample_findings):
        """Test creating grouped tasks by CWE."""
        integration = BacklogIntegration(group_by_cwe=True)

        tasks = integration.create_tasks(sample_findings)

        # Should group 2 SQL injections together
        assert len(tasks) == 3  # CWE-89 (2), CWE-79, CWE-22

        # Find CWE-89 group
        sql_task = next(t for t in tasks if "CWE-89" in t.title)
        assert "(2 occurrences)" in sql_task.title

    def test_max_tasks_limit(self, sample_findings):
        """Test max_tasks limits output."""
        integration = BacklogIntegration(max_tasks=2)

        tasks = integration.create_tasks(sample_findings)

        assert len(tasks) == 2

    def test_severity_to_priority_mapping(self, integration):
        """Test severity maps to correct priority."""
        findings = [
            Finding(
                id="F1",
                scanner="test",
                severity=Severity.CRITICAL,
                title="Critical",
                description="",
                location=Location(file=Path("a.py"), line_start=1, line_end=1),
            ),
            Finding(
                id="F2",
                scanner="test",
                severity=Severity.LOW,
                title="Low",
                description="",
                location=Location(file=Path("b.py"), line_start=1, line_end=1),
            ),
        ]

        tasks = integration.create_tasks(findings)

        assert tasks[0].priority == "high"  # Critical -> high
        assert tasks[1].priority == "low"  # Low -> low

    def test_labels_include_severity_and_cwe(self, integration, sample_finding):
        """Test labels include relevant metadata."""
        tasks = integration.create_tasks([sample_finding])

        labels = tasks[0].labels
        assert "security" in labels
        assert "high" in labels
        assert "cwe89" in labels
        assert "semgrep" in labels

    def test_acceptance_criteria_for_critical(self, integration):
        """Test critical findings get extra acceptance criteria."""
        finding = Finding(
            id="F1",
            scanner="test",
            severity=Severity.CRITICAL,
            title="Critical Issue",
            description="Very bad",
            location=Location(file=Path("app.py"), line_start=1, line_end=1),
        )

        tasks = integration.create_tasks([finding])
        criteria = tasks[0].acceptance_criteria

        # Critical should have security test requirement
        assert any("security test" in c.lower() for c in criteria)
        assert any("review" in c.lower() for c in criteria)


class TestCreateTasksFromFindings:
    """Tests for create_tasks_from_findings function."""

    def test_basic_usage(self, sample_findings):
        """Test basic task creation."""
        tasks = create_tasks_from_findings(sample_findings)

        assert len(tasks) == 4
        assert all(isinstance(t, FindingTask) for t in tasks)

    def test_with_grouping(self, sample_findings):
        """Test grouped task creation."""
        tasks = create_tasks_from_findings(sample_findings, group_by_cwe=True)

        assert len(tasks) == 3

    def test_with_max_tasks(self, sample_findings):
        """Test limited task creation."""
        tasks = create_tasks_from_findings(sample_findings, max_tasks=1)

        assert len(tasks) == 1
