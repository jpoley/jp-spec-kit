"""Tests for patch application."""

from pathlib import Path

from tests.conftest import MockConfirmationHandler

from specify_cli.security.fixer.applicator import (
    ApplyResult,
    ApplyStatus,
    PatchApplicator,
)
from specify_cli.security.fixer.models import FixResult, FixStatus, Patch


class TestPatchApplicator:
    """Tests for PatchApplicator."""

    def test_initialization_defaults(self):
        """Test default initialization."""
        applicator = PatchApplicator()

        assert applicator.create_backups is True
        assert applicator.dry_run is False

    def test_initialization_custom(self):
        """Test custom initialization."""
        handler = MockConfirmationHandler()
        applicator = PatchApplicator(
            confirmation_handler=handler,
            create_backups=False,
            dry_run=True,
        )

        assert applicator.confirmation_handler == handler
        assert applicator.create_backups is False
        assert applicator.dry_run is True

    def test_apply_patch_success(self, tmp_path):
        """Test successfully applying a patch."""
        # Create source file
        source_file = tmp_path / "app.py"
        source_file.write_text(
            'query = "SELECT * FROM users WHERE id = " + user_id\n',
            encoding="utf-8",
        )

        # Create patch
        patch = Patch(
            file_path=source_file,
            original_code='query = "SELECT * FROM users WHERE id = " + user_id',
            fixed_code='cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        # Apply patch
        applicator = PatchApplicator(create_backups=True)
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.status == ApplyStatus.SUCCESS
        assert result.is_successful
        assert result.file_path == source_file
        assert result.backup_path is not None
        assert result.backup_path.exists()

        # Verify file was patched
        content = source_file.read_text(encoding="utf-8")
        assert "cursor.execute" in content
        assert "SELECT * FROM users WHERE id = ?" in content

    def test_apply_patch_file_not_found(self):
        """Test applying patch to non-existent file."""
        patch = Patch(
            file_path=Path("/nonexistent/file.py"),
            original_code="bad",
            fixed_code="good",
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator()
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.status == ApplyStatus.FAILED
        assert "not found" in result.message.lower()

    def test_apply_patch_conflict(self, tmp_path):
        """Test applying patch when code has changed."""
        source_file = tmp_path / "app.py"
        source_file.write_text(
            "# Code has been modified\nnew_code = 'different'\n",
            encoding="utf-8",
        )

        patch = Patch(
            file_path=source_file,
            original_code='old_code = "original"',
            fixed_code='new_code = "fixed"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator()
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.status == ApplyStatus.CONFLICT
        assert "conflict" in result.message.lower()

    def test_apply_patch_dry_run(self, tmp_path):
        """Test dry run mode doesn't modify files."""
        source_file = tmp_path / "app.py"
        original_content = 'query = "SELECT * FROM users WHERE id = " + user_id\n'
        source_file.write_text(original_content, encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='query = "SELECT * FROM users WHERE id = " + user_id',
            fixed_code='cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator(dry_run=True)
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.status == ApplyStatus.SUCCESS
        assert "dry run" in result.message.lower()

        # Verify file unchanged
        content = source_file.read_text(encoding="utf-8")
        assert content == original_content

    def test_apply_patch_creates_backup(self, tmp_path):
        """Test backup file is created."""
        source_file = tmp_path / "app.py"
        original_content = 'bad_code = "vulnerable"\n'
        source_file.write_text(original_content, encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='bad_code = "vulnerable"',
            fixed_code='good_code = "secure"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator(create_backups=True)
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.is_successful
        assert result.backup_path is not None
        assert result.backup_path.exists()

        # Verify backup contains original content
        backup_content = result.backup_path.read_text(encoding="utf-8")
        assert backup_content == original_content

    def test_apply_patch_no_backup(self, tmp_path):
        """Test patch application without backup."""
        source_file = tmp_path / "app.py"
        source_file.write_text('bad_code = "vulnerable"\n', encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='bad_code = "vulnerable"',
            fixed_code='good_code = "secure"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator(create_backups=False)
        result = applicator.apply_patch(patch, "FINDING-001")

        assert result.is_successful
        assert result.backup_path is None
        assert not Path(f"{source_file}.orig").exists()


class TestApplyFix:
    """Tests for apply_fix method."""

    def test_apply_fix_with_confirmation_accepted(self, tmp_path):
        """Test applying fix with user confirmation."""
        source_file = tmp_path / "app.py"
        source_file.write_text('bad = "code"\n', encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='bad = "code"',
            fixed_code='good = "code"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        fix_result = FixResult(
            finding_id="F-001",
            status=FixStatus.SUCCESS,
            patch=patch,
            explanation="Fixed",
            confidence=0.9,
        )

        handler = MockConfirmationHandler(always_confirm=True)
        applicator = PatchApplicator(confirmation_handler=handler)
        result = applicator.apply_fix(fix_result, confirm=True)

        assert result.is_successful
        assert len(handler.calls) == 1

    def test_apply_fix_with_confirmation_rejected(self, tmp_path):
        """Test applying fix with user rejection."""
        source_file = tmp_path / "app.py"
        source_file.write_text('bad = "code"\n', encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='bad = "code"',
            fixed_code='good = "code"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        fix_result = FixResult(
            finding_id="F-001",
            status=FixStatus.SUCCESS,
            patch=patch,
            explanation="Fixed",
            confidence=0.9,
        )

        handler = MockConfirmationHandler(always_confirm=False)
        applicator = PatchApplicator(confirmation_handler=handler)
        result = applicator.apply_fix(fix_result, confirm=True)

        assert result.status == ApplyStatus.SKIPPED
        assert len(handler.calls) == 1

    def test_apply_fix_without_confirmation(self, tmp_path):
        """Test applying fix without confirmation."""
        source_file = tmp_path / "app.py"
        source_file.write_text('bad = "code"\n', encoding="utf-8")

        patch = Patch(
            file_path=source_file,
            original_code='bad = "code"',
            fixed_code='good = "code"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        fix_result = FixResult(
            finding_id="F-001",
            status=FixStatus.SUCCESS,
            patch=patch,
            explanation="Fixed",
            confidence=0.9,
        )

        handler = MockConfirmationHandler()
        applicator = PatchApplicator(confirmation_handler=handler)
        result = applicator.apply_fix(fix_result, confirm=False)

        assert result.is_successful
        assert len(handler.calls) == 0  # No confirmation requested

    def test_apply_fix_no_patch(self):
        """Test applying fix with no patch."""
        fix_result = FixResult(
            finding_id="F-001",
            status=FixStatus.FAILED,
            patch=None,
            explanation="No patch",
            confidence=0.0,
        )

        applicator = PatchApplicator()
        result = applicator.apply_fix(fix_result)

        assert result.status == ApplyStatus.FAILED
        assert "no patch" in result.message.lower()


class TestApplyMultiple:
    """Tests for applying multiple patches."""

    def test_apply_multiple_all_success(self, tmp_path):
        """Test applying multiple patches successfully."""
        # Create multiple files
        file1 = tmp_path / "app1.py"
        file1.write_text('code1 = "bad"\n', encoding="utf-8")

        file2 = tmp_path / "app2.py"
        file2.write_text('code2 = "bad"\n', encoding="utf-8")

        # Create fix results
        fix_results = [
            FixResult(
                finding_id="F-001",
                status=FixStatus.SUCCESS,
                patch=Patch(
                    file_path=file1,
                    original_code='code1 = "bad"',
                    fixed_code='code1 = "good"',
                    unified_diff="...",
                    line_start=1,
                    line_end=1,
                ),
                explanation="Fixed 1",
                confidence=0.9,
            ),
            FixResult(
                finding_id="F-002",
                status=FixStatus.SUCCESS,
                patch=Patch(
                    file_path=file2,
                    original_code='code2 = "bad"',
                    fixed_code='code2 = "good"',
                    unified_diff="...",
                    line_start=1,
                    line_end=1,
                ),
                explanation="Fixed 2",
                confidence=0.9,
            ),
        ]

        handler = MockConfirmationHandler(always_confirm=True)
        applicator = PatchApplicator(confirmation_handler=handler)
        results = applicator.apply_multiple(fix_results, confirm=True)

        assert len(results) == 2
        assert all(r.is_successful for r in results)

    def test_apply_multiple_mixed_results(self, tmp_path):
        """Test applying multiple patches with mixed results."""
        file1 = tmp_path / "app1.py"
        file1.write_text('code1 = "bad"\n', encoding="utf-8")

        fix_results = [
            FixResult(
                finding_id="F-001",
                status=FixStatus.SUCCESS,
                patch=Patch(
                    file_path=file1,
                    original_code='code1 = "bad"',
                    fixed_code='code1 = "good"',
                    unified_diff="...",
                    line_start=1,
                    line_end=1,
                ),
                explanation="Fixed",
                confidence=0.9,
            ),
            FixResult(
                finding_id="F-002",
                status=FixStatus.FAILED,
                patch=None,
                explanation="No patch",
                confidence=0.0,
            ),
        ]

        handler = MockConfirmationHandler(always_confirm=True)
        applicator = PatchApplicator(confirmation_handler=handler)
        results = applicator.apply_multiple(fix_results, confirm=False)

        assert len(results) == 2
        assert results[0].is_successful
        assert results[1].status == ApplyStatus.FAILED


class TestRollback:
    """Tests for rollback functionality."""

    def test_rollback_success(self, tmp_path):
        """Test successfully rolling back a patch."""
        source_file = tmp_path / "app.py"
        original_content = 'original = "code"\n'
        source_file.write_text(original_content, encoding="utf-8")

        # Apply a patch
        patch = Patch(
            file_path=source_file,
            original_code='original = "code"',
            fixed_code='modified = "code"',
            unified_diff="...",
            line_start=1,
            line_end=1,
        )

        applicator = PatchApplicator(create_backups=True)
        apply_result = applicator.apply_patch(patch, "F-001")

        assert apply_result.is_successful

        # Verify file was modified
        assert 'modified = "code"' in source_file.read_text(encoding="utf-8")

        # Rollback
        success = applicator.rollback(apply_result)

        assert success is True
        # Verify original content restored
        assert source_file.read_text(encoding="utf-8") == original_content

    def test_rollback_no_backup(self, tmp_path):
        """Test rollback fails when no backup exists."""
        result = ApplyResult(
            finding_id="F-001",
            file_path=tmp_path / "app.py",
            status=ApplyStatus.SUCCESS,
            message="Done",
            backup_path=None,
        )

        applicator = PatchApplicator()
        success = applicator.rollback(result)

        assert success is False


class TestSavePatchFiles:
    """Tests for saving patches to .patch files."""

    def test_save_patch_file(self, tmp_path):
        """Test saving a single patch file."""
        output_dir = tmp_path / "patches"

        patch = Patch(
            file_path=Path("src/app.py"),
            original_code="bad",
            fixed_code="good",
            unified_diff="--- original\n+++ fixed\n@@ -1 +1 @@\n-bad\n+good",
            line_start=10,
            line_end=10,
        )

        applicator = PatchApplicator()
        patch_file = applicator.save_patch_file(patch, output_dir, "FINDING-001")

        assert patch_file.exists()
        assert patch_file.parent == output_dir
        assert "FINDING-001" in patch_file.name
        assert patch_file.suffix == ".patch"

        # Verify content
        content = patch_file.read_text(encoding="utf-8")
        assert "--- a/src/app.py" in content
        assert "+++ b/src/app.py" in content

    def test_save_patches_multiple(self, tmp_path):
        """Test saving multiple patches."""
        output_dir = tmp_path / "patches"

        fix_results = [
            FixResult(
                finding_id="F-001",
                status=FixStatus.SUCCESS,
                patch=Patch(
                    file_path=Path("app1.py"),
                    original_code="bad1",
                    fixed_code="good1",
                    unified_diff="diff1",
                    line_start=1,
                    line_end=1,
                ),
                explanation="Fix 1",
                confidence=0.9,
            ),
            FixResult(
                finding_id="F-002",
                status=FixStatus.SUCCESS,
                patch=Patch(
                    file_path=Path("app2.py"),
                    original_code="bad2",
                    fixed_code="good2",
                    unified_diff="diff2",
                    line_start=1,
                    line_end=1,
                ),
                explanation="Fix 2",
                confidence=0.9,
            ),
            FixResult(
                finding_id="F-003",
                status=FixStatus.FAILED,
                patch=None,
                explanation="No patch",
                confidence=0.0,
            ),
        ]

        applicator = PatchApplicator()
        patch_files = applicator.save_patches(fix_results, output_dir)

        assert len(patch_files) == 2  # Only 2 have patches
        assert all(f.exists() for f in patch_files)
        assert all(f.suffix == ".patch" for f in patch_files)


class TestApplyResult:
    """Tests for ApplyResult dataclass."""

    def test_is_successful_true(self):
        """Test is_successful property."""
        result = ApplyResult(
            finding_id="F-001",
            file_path=Path("app.py"),
            status=ApplyStatus.SUCCESS,
            message="Done",
        )

        assert result.is_successful is True

    def test_is_successful_false(self):
        """Test is_successful for failed status."""
        result = ApplyResult(
            finding_id="F-001",
            file_path=Path("app.py"),
            status=ApplyStatus.FAILED,
            message="Error",
        )

        assert result.is_successful is False

    def test_to_dict(self):
        """Test serialization."""
        result = ApplyResult(
            finding_id="F-001",
            file_path=Path("app.py"),
            status=ApplyStatus.SUCCESS,
            message="Applied successfully",
            backup_path=Path("app.py.orig"),
        )

        data = result.to_dict()

        assert data["finding_id"] == "F-001"
        assert data["file_path"] == "app.py"
        assert data["status"] == "success"
        assert data["backup_path"] == "app.py.orig"
        assert "applied_at" in data
