"""Integration tests for fix generation and application workflow."""

from pathlib import Path
from unittest.mock import Mock

from tests.conftest import MockConfirmationHandler

from specify_cli.security.fixer.applicator import ApplyStatus, PatchApplicator
from specify_cli.security.fixer.generator import FixGenerator
from specify_cli.security.models import Finding, Location, Severity


def create_test_finding(
    finding_id: str,
    file_path: Path,
    cwe_id: str,
    vulnerable_code: str,
    line_start: int = 1,
) -> Finding:
    """Helper to create a test finding."""
    return Finding(
        id=finding_id,
        scanner="test",
        severity=Severity.HIGH,
        title="Test Vulnerability",
        description=f"Test {cwe_id} vulnerability",
        location=Location(
            file=file_path,
            line_start=line_start,
            line_end=line_start + vulnerable_code.count("\n"),
            code_snippet=vulnerable_code,
        ),
        cwe_id=cwe_id,
    )


class TestSQLInjectionFixWorkflow:
    """End-to-end tests for SQL injection fixes."""

    def test_sql_injection_fix_with_llm(self, tmp_path):
        """Test complete workflow: detect -> generate fix -> apply patch."""
        # Step 1: Create vulnerable file
        vuln_file = tmp_path / "database.py"
        vulnerable_code = 'query = "SELECT * FROM users WHERE id = " + user_id\n'
        vuln_file.write_text(vulnerable_code, encoding="utf-8")

        # Step 2: Create finding
        finding = create_test_finding(
            finding_id="SQL-001",
            file_path=vuln_file,
            cwe_id="CWE-89",
            vulnerable_code=vulnerable_code.strip(),
        )

        # Step 3: Generate fix with mocked LLM
        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
            "explanation": "Use parameterized query to prevent SQL injection",
            "confidence": 0.95,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        assert fix_result.is_successful
        assert fix_result.patch is not None
        assert fix_result.confidence >= 0.7

        # Step 4: Apply the patch
        applicator = PatchApplicator(create_backups=True)
        apply_result = applicator.apply_fix(fix_result, confirm=False)

        assert apply_result.is_successful
        assert apply_result.backup_path is not None

        # Step 5: Verify the fix
        fixed_content = vuln_file.read_text(encoding="utf-8")
        assert "cursor.execute" in fixed_content
        assert "?" in fixed_content
        assert "user_id,)" in fixed_content

        # Step 6: Verify backup exists
        backup_content = apply_result.backup_path.read_text(encoding="utf-8")
        assert backup_content == vulnerable_code


class TestXSSFixWorkflow:
    """End-to-end tests for XSS fixes."""

    def test_xss_fix_with_llm(self, tmp_path):
        """Test XSS vulnerability fix workflow."""
        # Create vulnerable file
        vuln_file = tmp_path / "view.js"
        vulnerable_code = "element.innerHTML = userInput;\n"
        vuln_file.write_text(vulnerable_code, encoding="utf-8")

        # Create finding
        finding = create_test_finding(
            finding_id="XSS-001",
            file_path=vuln_file,
            cwe_id="CWE-79",
            vulnerable_code=vulnerable_code.strip(),
        )

        # Generate fix
        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "element.textContent = userInput;",
            "explanation": "Use textContent to prevent XSS",
            "confidence": 0.90,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        assert fix_result.is_successful

        # Apply patch
        applicator = PatchApplicator()
        apply_result = applicator.apply_fix(fix_result, confirm=False)

        assert apply_result.is_successful

        # Verify fix
        fixed_content = vuln_file.read_text(encoding="utf-8")
        assert "textContent" in fixed_content
        assert "innerHTML" not in fixed_content


class TestMultipleFixesWorkflow:
    """End-to-end tests for multiple fixes."""

    def test_fix_multiple_vulnerabilities(self, tmp_path):
        """Test generating and applying multiple fixes."""
        # Create multiple vulnerable files
        sql_file = tmp_path / "database.py"
        sql_file.write_text(
            'query = "SELECT * FROM users WHERE id = " + user_id\n',
            encoding="utf-8",
        )

        xss_file = tmp_path / "view.js"
        xss_file.write_text("element.innerHTML = userInput;\n", encoding="utf-8")

        # Create findings
        findings = [
            create_test_finding(
                "SQL-001",
                sql_file,
                "CWE-89",
                'query = "SELECT * FROM users WHERE id = " + user_id',
            ),
            create_test_finding(
                "XSS-001",
                xss_file,
                "CWE-79",
                "element.innerHTML = userInput;",
            ),
        ]

        # Generate fixes
        mock_llm = Mock()
        mock_llm.complete.side_effect = [
            """
            {
                "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
                "explanation": "Use parameterized query",
                "confidence": 0.95,
                "warnings": []
            }
            """,
            """
            {
                "fixed_code": "element.textContent = userInput;",
                "explanation": "Use textContent",
                "confidence": 0.90,
                "warnings": []
            }
            """,
        ]

        generator = FixGenerator(llm_client=mock_llm)
        fix_results = generator.generate_fixes(findings)

        assert len(fix_results) == 2
        assert all(r.is_successful for r in fix_results)

        # Apply all patches
        applicator = PatchApplicator()
        apply_results = applicator.apply_multiple(fix_results, confirm=False)

        assert len(apply_results) == 2
        assert all(r.is_successful for r in apply_results)

        # Verify all files were fixed
        assert "cursor.execute" in sql_file.read_text(encoding="utf-8")
        assert "textContent" in xss_file.read_text(encoding="utf-8")


class TestPatchFileGeneration:
    """Tests for .patch file generation workflow."""

    def test_save_patches_workflow(self, tmp_path):
        """Test generating and saving patch files."""
        # Create vulnerable file
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text(
            'query = "SELECT * FROM users WHERE id = " + user_id\n',
            encoding="utf-8",
        )

        # Generate fix
        finding = create_test_finding(
            "SQL-001",
            vuln_file,
            "CWE-89",
            'query = "SELECT * FROM users WHERE id = " + user_id',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
            "explanation": "Use parameterized query",
            "confidence": 0.95,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        # Save patch files
        patch_dir = tmp_path / "patches"
        applicator = PatchApplicator()
        patch_files = applicator.save_patches([fix_result], patch_dir)

        assert len(patch_files) == 1
        patch_file = patch_files[0]

        assert patch_file.exists()
        assert patch_file.suffix == ".patch"
        assert "SQL-001" in patch_file.name

        # Verify patch file content
        content = patch_file.read_text(encoding="utf-8")
        assert "--- a/" in content
        assert "+++ b/" in content
        assert "app.py" in content


class TestRollbackWorkflow:
    """Tests for rollback workflow."""

    def test_apply_and_rollback(self, tmp_path):
        """Test applying a fix and then rolling it back."""
        # Create vulnerable file
        vuln_file = tmp_path / "app.py"
        original_content = 'bad_code = "vulnerable"\n'
        vuln_file.write_text(original_content, encoding="utf-8")

        # Generate and apply fix
        finding = create_test_finding(
            "TEST-001",
            vuln_file,
            "CWE-89",
            'bad_code = "vulnerable"',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "good_code = \\"secure\\"",
            "explanation": "Fixed it",
            "confidence": 0.90,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        applicator = PatchApplicator(create_backups=True)
        apply_result = applicator.apply_fix(fix_result, confirm=False)

        assert apply_result.is_successful

        # Verify file was modified
        assert "good_code" in vuln_file.read_text(encoding="utf-8")

        # Rollback
        rollback_success = applicator.rollback(apply_result)

        assert rollback_success is True

        # Verify original content restored
        assert vuln_file.read_text(encoding="utf-8") == original_content


class TestDryRunWorkflow:
    """Tests for dry-run workflow."""

    def test_dry_run_no_modification(self, tmp_path):
        """Test dry-run mode doesn't modify files."""
        # Create vulnerable file
        vuln_file = tmp_path / "app.py"
        original_content = 'query = "SELECT * FROM users WHERE id = " + user_id\n'
        vuln_file.write_text(original_content, encoding="utf-8")

        # Generate fix
        finding = create_test_finding(
            "SQL-001",
            vuln_file,
            "CWE-89",
            'query = "SELECT * FROM users WHERE id = " + user_id',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
            "explanation": "Use parameterized query",
            "confidence": 0.95,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        # Apply in dry-run mode
        applicator = PatchApplicator(dry_run=True)
        apply_result = applicator.apply_fix(fix_result, confirm=False)

        assert apply_result.status == ApplyStatus.SUCCESS
        assert "dry run" in apply_result.message.lower()

        # Verify file unchanged
        assert vuln_file.read_text(encoding="utf-8") == original_content


class TestConfirmationWorkflow:
    """Tests for interactive confirmation workflow."""

    def test_confirmation_flow_accept(self, tmp_path):
        """Test user accepting a fix."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text('bad = "code"\n', encoding="utf-8")

        finding = create_test_finding(
            "TEST-001",
            vuln_file,
            "CWE-89",
            'bad = "code"',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "good = \\"code\\"",
            "explanation": "Fixed",
            "confidence": 0.90,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        # Mock confirmation handler that accepts
        handler = MockConfirmationHandler(always_confirm=True)
        applicator = PatchApplicator(confirmation_handler=handler)
        apply_result = applicator.apply_fix(fix_result, confirm=True)

        assert apply_result.is_successful
        assert len(handler.calls) == 1

    def test_confirmation_flow_reject(self, tmp_path):
        """Test user rejecting a fix."""
        vuln_file = tmp_path / "app.py"
        original_content = 'bad = "code"\n'
        vuln_file.write_text(original_content, encoding="utf-8")

        finding = create_test_finding(
            "TEST-001",
            vuln_file,
            "CWE-89",
            'bad = "code"',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "good = \\"code\\"",
            "explanation": "Fixed",
            "confidence": 0.90,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        # Mock confirmation handler that rejects
        handler = MockConfirmationHandler(always_confirm=False)
        applicator = PatchApplicator(confirmation_handler=handler)
        apply_result = applicator.apply_fix(fix_result, confirm=True)

        assert apply_result.status == ApplyStatus.SKIPPED
        # Verify file unchanged
        assert vuln_file.read_text(encoding="utf-8") == original_content


class TestFixQualityMetrics:
    """Tests for fix quality assessment."""

    def test_high_confidence_fix(self, tmp_path):
        """Test high-confidence fix."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text('query = "SELECT * " + user_id\n', encoding="utf-8")

        finding = create_test_finding(
            "SQL-001",
            vuln_file,
            "CWE-89",
            'query = "SELECT * " + user_id',
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "cursor.execute(\\"SELECT * FROM users WHERE id = ?\\", (user_id,))",
            "explanation": "Use parameterized query",
            "confidence": 0.95,
            "warnings": []
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        assert fix_result.confidence >= 0.75
        assert not fix_result.needs_review

    def test_low_confidence_fix_needs_review(self, tmp_path):
        """Test low-confidence fix requires review."""
        vuln_file = tmp_path / "app.py"
        vuln_file.write_text("complex vulnerable code\n", encoding="utf-8")

        finding = create_test_finding(
            "TEST-001",
            vuln_file,
            "CWE-89",
            "complex vulnerable code",
        )

        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "fixed_code": "attempted fix",
            "explanation": "Not sure if this is correct",
            "confidence": 0.40,
            "warnings": ["Uncertain about this fix"]
        }
        """

        generator = FixGenerator(llm_client=mock_llm)
        fix_result = generator.generate_fix(finding)

        assert fix_result.confidence < 0.75
        assert fix_result.needs_review
        assert len(fix_result.warnings) > 0
