"""Tests for fix generator models."""

from pathlib import Path

import pytest

from specify_cli.security.fixer.models import (
    FixResult,
    FixStatus,
    Patch,
    FixPattern,
)


class TestFixStatus:
    """Tests for FixStatus enum."""

    def test_values(self):
        """Test status values."""
        assert FixStatus.SUCCESS.value == "success"
        assert FixStatus.PARTIAL.value == "partial"
        assert FixStatus.FAILED.value == "failed"
        assert FixStatus.SKIPPED.value == "skipped"


class TestPatch:
    """Tests for Patch dataclass."""

    @pytest.fixture
    def sample_patch(self):
        """Create a sample patch."""
        return Patch(
            file_path=Path("src/app.py"),
            original_code='query = "SELECT * FROM users WHERE id = " + user_id',
            fixed_code='cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
            unified_diff="--- original\n+++ fixed\n@@ -1 +1 @@\n-query = ...\n+cursor.execute...",
            line_start=42,
            line_end=42,
        )

    def test_to_patch_file(self, sample_patch):
        """Test generating patch file content."""
        content = sample_patch.to_patch_file()

        assert "--- a/src/app.py" in content
        assert "+++ b/src/app.py" in content
        assert sample_patch.unified_diff in content

    def test_to_dict(self, sample_patch):
        """Test serialization."""
        data = sample_patch.to_dict()

        assert data["file_path"] == "src/app.py"
        assert data["line_start"] == 42
        assert "original_code" in data
        assert "fixed_code" in data


class TestFixResult:
    """Tests for FixResult dataclass."""

    @pytest.fixture
    def successful_result(self):
        """Create a successful fix result."""
        patch = Patch(
            file_path=Path("app.py"),
            original_code="bad code",
            fixed_code="good code",
            unified_diff="diff...",
            line_start=1,
            line_end=1,
        )
        return FixResult(
            finding_id="FINDING-001",
            status=FixStatus.SUCCESS,
            patch=patch,
            explanation="Fixed the issue",
            confidence=0.95,
        )

    @pytest.fixture
    def partial_result(self):
        """Create a partial fix result."""
        return FixResult(
            finding_id="FINDING-002",
            status=FixStatus.PARTIAL,
            patch=None,
            explanation="Guidance provided",
            confidence=0.5,
            warnings=["Manual review required"],
        )

    def test_is_successful_true(self, successful_result):
        """Test is_successful for success status."""
        assert successful_result.is_successful is True

    def test_is_successful_partial(self, partial_result):
        """Test is_successful for partial status."""
        assert partial_result.is_successful is True

    def test_is_successful_false(self):
        """Test is_successful for failed status."""
        result = FixResult(
            finding_id="F1",
            status=FixStatus.FAILED,
            patch=None,
            explanation="Failed",
            confidence=0.0,
        )
        assert result.is_successful is False

    def test_needs_review_low_confidence(self, successful_result):
        """Test needs_review with low confidence."""
        successful_result.confidence = 0.5
        assert successful_result.needs_review is True

    def test_needs_review_partial(self, partial_result):
        """Test needs_review for partial status."""
        assert partial_result.needs_review is True

    def test_needs_review_high_confidence(self, successful_result):
        """Test needs_review with high confidence."""
        assert successful_result.needs_review is False

    def test_to_dict(self, successful_result):
        """Test serialization."""
        data = successful_result.to_dict()

        assert data["finding_id"] == "FINDING-001"
        assert data["status"] == "success"
        assert data["patch"] is not None
        assert data["confidence"] == 0.95


class TestFixPattern:
    """Tests for FixPattern dataclass."""

    def test_creation(self):
        """Test creating a fix pattern."""
        pattern = FixPattern(
            cwe_id="CWE-89",
            name="SQL Injection",
            description="Use parameterized queries",
            vulnerable_pattern=r"query.*\+",
            fix_template="Use ? placeholders",
            examples=[{"before": "bad", "after": "good", "language": "python"}],
        )

        assert pattern.cwe_id == "CWE-89"
        assert len(pattern.examples) == 1

    def test_to_dict(self):
        """Test serialization."""
        pattern = FixPattern(
            cwe_id="CWE-79",
            name="XSS",
            description="Escape output",
            vulnerable_pattern="innerHTML",
            fix_template="Use textContent",
        )

        data = pattern.to_dict()

        assert data["cwe_id"] == "CWE-79"
        assert data["name"] == "XSS"
