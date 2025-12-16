"""Tests for PatchApplicator."""

from pathlib import Path
from unittest.mock import patch as mock_patch, MagicMock

import pytest

from flowspec_cli.security.fixer.applicator import (
    ApplyResult,
    ApplyStatus,
    BatchApplyResult,
    PatchApplicator,
    PatchApplicatorConfig,
)
from flowspec_cli.security.fixer.models import FixResult, FixStatus, Patch


@pytest.fixture
def sample_patch(tmp_path):
    """Create a sample patch with a real file."""
    target_file = tmp_path / "vulnerable.py"
    target_file.write_text('query = "SELECT * FROM users WHERE id = " + user_id')

    return Patch(
        file_path=target_file,
        original_code='query = "SELECT * FROM users WHERE id = " + user_id',
        fixed_code='cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
        unified_diff='--- a/vulnerable.py\n+++ b/vulnerable.py\n@@ -1 +1 @@\n-query = "SELECT * FROM users WHERE id = " + user_id\n+cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
        line_start=1,
        line_end=1,
    )


@pytest.fixture
def applicator(tmp_path):
    """Create applicator with temp backup directory."""
    config = PatchApplicatorConfig(
        backup_dir=tmp_path / "backups",
        create_backups=True,
        use_git_apply=False,  # Use manual apply for predictable tests
    )
    return PatchApplicator(config=config)


class TestApplyStatus:
    """Tests for ApplyStatus enum."""

    def test_values(self):
        """Test status values."""
        assert ApplyStatus.SUCCESS.value == "success"
        assert ApplyStatus.FAILED.value == "failed"
        assert ApplyStatus.CONFLICT.value == "conflict"
        assert ApplyStatus.SKIPPED.value == "skipped"


class TestApplyResult:
    """Tests for ApplyResult dataclass."""

    def test_is_successful_true(self, sample_patch):
        """Test is_successful for success status."""
        result = ApplyResult(
            patch=sample_patch,
            status=ApplyStatus.SUCCESS,
            message="Applied",
        )
        assert result.is_successful is True

    def test_is_successful_false(self, sample_patch):
        """Test is_successful for non-success statuses."""
        for status in [ApplyStatus.FAILED, ApplyStatus.CONFLICT, ApplyStatus.SKIPPED]:
            result = ApplyResult(
                patch=sample_patch,
                status=status,
                message="Not applied",
            )
            assert result.is_successful is False

    def test_to_dict(self, sample_patch, tmp_path):
        """Test serialization."""
        backup = tmp_path / "backup.py"
        result = ApplyResult(
            patch=sample_patch,
            status=ApplyStatus.SUCCESS,
            message="Applied",
            backup_path=backup,
        )

        data = result.to_dict()

        assert "vulnerable.py" in data["file_path"]
        assert data["status"] == "success"
        assert data["message"] == "Applied"
        assert "backup.py" in data["backup_path"]


class TestBatchApplyResult:
    """Tests for BatchApplyResult dataclass."""

    def test_successful_count(self, sample_patch):
        """Test counting successful results."""
        results = [
            ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
            ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
            ApplyResult(patch=sample_patch, status=ApplyStatus.FAILED),
        ]
        batch = BatchApplyResult(results=results)

        assert batch.successful_count == 2
        assert batch.failed_count == 1

    def test_all_successful(self, sample_patch):
        """Test all_successful property."""
        all_success = BatchApplyResult(
            results=[
                ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
                ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
            ]
        )
        assert all_success.all_successful is True

        mixed = BatchApplyResult(
            results=[
                ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
                ApplyResult(patch=sample_patch, status=ApplyStatus.FAILED),
            ]
        )
        assert mixed.all_successful is False

    def test_to_dict(self, sample_patch):
        """Test serialization."""
        batch = BatchApplyResult(
            results=[
                ApplyResult(patch=sample_patch, status=ApplyStatus.SUCCESS),
            ]
        )

        data = batch.to_dict()

        assert data["total"] == 1
        assert data["successful"] == 1
        assert data["failed"] == 0
        assert "timestamp" in data


class TestPatchApplicator:
    """Tests for PatchApplicator."""

    def test_initialization(self):
        """Test applicator initializes correctly."""
        applicator = PatchApplicator()

        assert applicator.config.create_backups is True
        assert applicator.config.use_git_apply is True

    def test_initialization_with_config(self, tmp_path):
        """Test applicator with custom config."""
        config = PatchApplicatorConfig(
            backup_dir=tmp_path / "custom",
            create_backups=False,
        )
        applicator = PatchApplicator(config=config)

        assert applicator.config.backup_dir == tmp_path / "custom"
        assert applicator.config.create_backups is False

    def test_apply_patch_file_not_found(self, applicator):
        """Test applying patch when file doesn't exist."""
        patch = Patch(
            file_path=Path("/nonexistent/file.py"),
            original_code="old",
            fixed_code="new",
            unified_diff="diff",
            line_start=1,
            line_end=1,
        )

        result = applicator.apply_patch(patch)

        assert result.status == ApplyStatus.FAILED
        assert "does not exist" in result.message

    def test_apply_patch_dry_run(self, applicator, sample_patch):
        """Test dry-run validation."""
        result = applicator.apply_patch(sample_patch, dry_run=True)

        # Should validate without modifying file
        assert result.status == ApplyStatus.SKIPPED
        assert "dry-run" in result.message.lower()

        # File should be unchanged
        content = sample_patch.file_path.read_text()
        assert "SELECT * FROM users WHERE id = " in content

    def test_apply_patch_success(self, applicator, sample_patch):
        """Test successful patch application."""
        result = applicator.apply_patch(sample_patch)

        assert result.status == ApplyStatus.SUCCESS
        assert result.backup_path is not None
        assert result.backup_path.exists()

        # File should be modified
        content = sample_patch.file_path.read_text()
        assert "cursor.execute" in content

    def test_apply_patch_creates_backup(self, applicator, sample_patch):
        """Test backup creation."""
        result = applicator.apply_patch(sample_patch)

        assert result.backup_path is not None
        assert result.backup_path.exists()

        # Backup should contain original content
        backup_content = result.backup_path.read_text()
        assert "SELECT * FROM users WHERE id = " in backup_content

    def test_apply_patch_conflict(self, applicator, tmp_path):
        """Test patch with non-matching original code."""
        target_file = tmp_path / "changed.py"
        target_file.write_text("completely different code")

        patch = Patch(
            file_path=target_file,
            original_code="original code that does not exist",
            fixed_code="fixed code",
            unified_diff="diff",
            line_start=1,
            line_end=1,
        )

        result = applicator.apply_patch(patch)

        assert result.status == ApplyStatus.CONFLICT
        assert "not found" in result.message.lower()


class TestPatchApplicatorBatch:
    """Tests for batch patch application."""

    def test_apply_patches(self, applicator, tmp_path):
        """Test applying multiple patches."""
        # Create two files
        file1 = tmp_path / "file1.py"
        file1.write_text("old code 1")

        file2 = tmp_path / "file2.py"
        file2.write_text("old code 2")

        patches = [
            Patch(
                file_path=file1,
                original_code="old code 1",
                fixed_code="new code 1",
                unified_diff="diff1",
                line_start=1,
                line_end=1,
            ),
            Patch(
                file_path=file2,
                original_code="old code 2",
                fixed_code="new code 2",
                unified_diff="diff2",
                line_start=1,
                line_end=1,
            ),
        ]

        batch_result = applicator.apply_patches(patches)

        assert batch_result.successful_count == 2
        assert batch_result.all_successful is True

        assert file1.read_text() == "new code 1"
        assert file2.read_text() == "new code 2"

    def test_apply_fix_results(self, applicator, tmp_path):
        """Test applying patches from FixResults."""
        target_file = tmp_path / "vuln.py"
        target_file.write_text("vulnerable code")

        patch = Patch(
            file_path=target_file,
            original_code="vulnerable code",
            fixed_code="secure code",
            unified_diff="diff",
            line_start=1,
            line_end=1,
        )

        fix_results = [
            FixResult(
                finding_id="F1",
                status=FixStatus.SUCCESS,
                patch=patch,
                explanation="Fixed",
                confidence=0.9,
            ),
            FixResult(
                finding_id="F2",
                status=FixStatus.FAILED,
                patch=None,  # No patch for failed fix
                explanation="Could not fix",
                confidence=0.0,
            ),
        ]

        batch_result = applicator.apply_fix_results(fix_results)

        # Only one patch should be applied (F2 has no patch)
        assert len(batch_result.results) == 1
        assert batch_result.successful_count == 1


class TestPatchApplicatorRollback:
    """Tests for rollback functionality."""

    def test_rollback_single(self, applicator, sample_patch):
        """Test rolling back a single patch."""
        # Apply patch
        result = applicator.apply_patch(sample_patch)
        assert result.is_successful

        # Verify file was modified
        content = sample_patch.file_path.read_text()
        assert "cursor.execute" in content

        # Rollback
        success = applicator.rollback(result)
        assert success is True

        # Verify file was restored
        content = sample_patch.file_path.read_text()
        assert "SELECT * FROM users WHERE id = " in content

    def test_rollback_all(self, applicator, tmp_path):
        """Test rolling back all patches."""
        # Create and patch multiple files
        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.py"
            f.write_text(f"original {i}")
            files.append(f)

        patches = [
            Patch(
                file_path=f,
                original_code=f"original {i}",
                fixed_code=f"patched {i}",
                unified_diff="diff",
                line_start=1,
                line_end=1,
            )
            for i, f in enumerate(files)
        ]

        # Apply all patches
        applicator.apply_patches(patches)

        # Verify all patched
        for i, f in enumerate(files):
            assert f.read_text() == f"patched {i}"

        # Rollback all
        rolled_back = applicator.rollback_all()
        assert rolled_back == 3

        # Verify all restored
        for i, f in enumerate(files):
            assert f.read_text() == f"original {i}"

    def test_rollback_no_backup(self, sample_patch):
        """Test rollback fails when no backup exists."""
        config = PatchApplicatorConfig(create_backups=False, use_git_apply=False)
        applicator = PatchApplicator(config=config)

        result = applicator.apply_patch(sample_patch)

        # No backup was created
        success = applicator.rollback(result)
        assert success is False


class TestPatchApplicatorHistory:
    """Tests for history tracking."""

    def test_save_history(self, applicator, sample_patch, tmp_path):
        """Test saving application history."""
        applicator.apply_patch(sample_patch)

        history_file = tmp_path / "history.json"
        applicator.save_history(history_file)

        assert history_file.exists()

        import json

        history = json.loads(history_file.read_text())
        assert "timestamp" in history
        assert "applied" in history
        assert len(history["applied"]) == 1


class TestPatchApplicatorGitApply:
    """Tests for git-based patch application."""

    def test_validate_with_git_success(self, tmp_path):
        """Test git apply --check validation."""
        config = PatchApplicatorConfig(use_git_apply=True)
        applicator = PatchApplicator(config=config)

        target_file = tmp_path / "test.py"
        target_file.write_text("original")

        test_patch = Patch(
            file_path=target_file,
            original_code="original",
            fixed_code="fixed",
            unified_diff="--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n-original\n+fixed",
            line_start=1,
            line_end=1,
        )

        # Mock subprocess to simulate git not being in a repo
        with mock_patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            applicator.apply_patch(test_patch, dry_run=True)

            # Should use git apply --check
            mock_run.assert_called()
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "apply" in call_args

    def test_fallback_to_manual_when_git_unavailable(self, tmp_path):
        """Test fallback to manual application when git is not available."""
        config = PatchApplicatorConfig(use_git_apply=True)
        applicator = PatchApplicator(config=config)

        target_file = tmp_path / "test.py"
        target_file.write_text("original code")

        test_patch = Patch(
            file_path=target_file,
            original_code="original code",
            fixed_code="fixed code",
            unified_diff="diff",
            line_start=1,
            line_end=1,
        )

        # Mock subprocess to simulate git not found
        with mock_patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git not found")

            result = applicator.apply_patch(test_patch)

            # Should fall back to manual and succeed
            assert result.status == ApplyStatus.SUCCESS
            assert target_file.read_text() == "fixed code"
