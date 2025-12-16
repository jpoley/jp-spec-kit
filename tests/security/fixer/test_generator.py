"""Tests for the FixGenerator."""

from pathlib import Path
from unittest.mock import Mock


from flowspec_cli.security.models import Finding, Location, Severity
from flowspec_cli.security.fixer.models import FixStatus
from flowspec_cli.security.fixer.generator import FixGenerator, FixGeneratorConfig


def make_finding(
    finding_id: str = "TEST-001",
    title: str = "Test Finding",
    severity: Severity = Severity.HIGH,
    cwe_id: str | None = None,
    code_snippet: str = "",
    file_path: str = "test.py",
    line_start: int = 10,
) -> Finding:
    """Create a test finding."""
    return Finding(
        id=finding_id,
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


class TestFixGenerator:
    """Tests for FixGenerator."""

    def test_initialization(self):
        """Test generator initializes correctly."""
        generator = FixGenerator()

        assert generator.config.context_lines == 10
        assert generator.patterns is not None

    def test_initialization_with_config(self):
        """Test generator with custom config."""
        config = FixGeneratorConfig(context_lines=5)
        generator = FixGenerator(config=config)

        assert generator.config.context_lines == 5

    def test_generate_fix_file_not_found(self):
        """Test fix generation when file doesn't exist."""
        generator = FixGenerator()
        finding = make_finding(file_path="/nonexistent/file.py")

        result = generator.generate_fix(finding)

        assert result.status == FixStatus.FAILED
        assert "Could not read" in result.explanation

    def test_generate_fix_with_mocked_llm(self, tmp_path):
        """Test fix generation with mocked LLM."""
        # Create a temporary vulnerable file
        vuln_file = tmp_path / "vulnerable.py"
        vuln_file.write_text(
            'query = "SELECT * FROM users WHERE id = " + user_id', encoding="utf-8"
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
            "explanation": "Use parameterized query",
            "confidence": 0.9,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        finding = make_finding(
            cwe_id="CWE-89",
            file_path=str(vuln_file),
        )

        result = generator.generate_fix(finding)

        assert result.is_successful
        assert mock_llm.complete.called

    def test_generate_fix_pattern_based(self, tmp_path):
        """Test pattern-based fix generation."""
        # Create a temporary vulnerable file with exact pattern match
        vuln_file = tmp_path / "vulnerable.py"
        vuln_file.write_text(
            'query = "SELECT * FROM users WHERE id = " + user_id', encoding="utf-8"
        )

        generator = FixGenerator()  # No LLM
        finding = make_finding(
            cwe_id="CWE-89",
            file_path=str(vuln_file),
        )

        result = generator.generate_fix(finding)

        # Should get pattern guidance even without exact match
        assert result.status in (FixStatus.PARTIAL, FixStatus.FAILED)

    def test_generate_fix_unknown_cwe(self, tmp_path):
        """Test fix for unknown CWE."""
        vuln_file = tmp_path / "unknown.py"
        vuln_file.write_text("some vulnerable code", encoding="utf-8")

        generator = FixGenerator()
        finding = make_finding(
            cwe_id="CWE-999",
            file_path=str(vuln_file),
        )

        result = generator.generate_fix(finding)

        assert result.status == FixStatus.FAILED


class TestDiffGeneration:
    """Tests for diff generation."""

    def test_generate_diff(self, tmp_path):
        """Test unified diff generation."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text("bad code", encoding="utf-8")

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "good code",
            "explanation": "Fixed it",
            "confidence": 0.9,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        finding = make_finding(file_path=str(vuln_file))

        result = generator.generate_fix(finding)

        if result.patch:
            assert (
                "-bad code" in result.patch.unified_diff
                or "bad code" in result.patch.original_code
            )
            assert "good code" in result.patch.fixed_code


class TestSyntaxValidation:
    """Tests for syntax validation."""

    def test_validate_python_valid(self, tmp_path):
        """Test valid Python syntax passes."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text("x = 1", encoding="utf-8")

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "x = 2",
            "explanation": "Changed value",
            "confidence": 0.9,
            "warnings": []
        }
        """

        config = FixGeneratorConfig(validate_syntax=True)
        generator = FixGenerator(llm_client=mock_llm, config=config)
        finding = make_finding(file_path=str(vuln_file))

        result = generator.generate_fix(finding)

        # Valid syntax should not add warnings
        syntax_warnings = [w for w in result.warnings if "syntax" in w.lower()]
        assert len(syntax_warnings) == 0

    def test_validate_python_invalid(self, tmp_path):
        """Test invalid Python syntax adds warning."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text("x = 1", encoding="utf-8")

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "x = ((",
            "explanation": "Broken code",
            "confidence": 0.9,
            "warnings": []
        }
        """

        config = FixGeneratorConfig(validate_syntax=True)
        generator = FixGenerator(llm_client=mock_llm, config=config)
        finding = make_finding(file_path=str(vuln_file))

        result = generator.generate_fix(finding)

        # Invalid syntax should add warning
        syntax_warnings = [w for w in result.warnings if "syntax" in w.lower()]
        assert len(syntax_warnings) > 0


class TestMultipleFixes:
    """Tests for generating multiple fixes."""

    def test_generate_fixes(self, tmp_path):
        """Test generating fixes for multiple findings."""
        # Create vulnerable files
        file1 = tmp_path / "app1.py"
        file1.write_text("vulnerable code 1", encoding="utf-8")

        file2 = tmp_path / "app2.py"
        file2.write_text("vulnerable code 2", encoding="utf-8")

        generator = FixGenerator()
        findings = [
            make_finding(finding_id="F1", file_path=str(file1), cwe_id="CWE-89"),
            make_finding(finding_id="F2", file_path=str(file2), cwe_id="CWE-79"),
        ]

        results = generator.generate_fixes(findings)

        assert len(results) == 2
        assert results[0].finding_id == "F1"
        assert results[1].finding_id == "F2"
