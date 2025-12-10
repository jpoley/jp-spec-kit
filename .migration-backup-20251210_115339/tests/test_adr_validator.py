"""Tests for ADR (Architecture Decision Record) validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from specify_cli.workflow.adr_validator import (
    ADR_FILENAME_PATTERN,
    ADRValidationResult,
    ADRValidator,
    validate_adr_for_transition,
)


class TestADRFilenamePattern:
    """Tests for ADR filename pattern matching."""

    def test_valid_adr_filename(self) -> None:
        """Test valid ADR filename pattern."""
        match = ADR_FILENAME_PATTERN.match("ADR-001-auth-strategy.md")
        assert match is not None
        assert match.group(1) == "001"
        assert match.group(2) == "auth-strategy"

    def test_valid_adr_filename_simple(self) -> None:
        """Test valid ADR filename with simple slug."""
        match = ADR_FILENAME_PATTERN.match("ADR-042-database.md")
        assert match is not None
        assert match.group(1) == "042"
        assert match.group(2) == "database"

    def test_invalid_adr_filename_no_number(self) -> None:
        """Test invalid filename without number."""
        match = ADR_FILENAME_PATTERN.match("ADR-auth.md")
        assert match is None

    def test_invalid_adr_filename_two_digit_number(self) -> None:
        """Test invalid filename with 2-digit number."""
        match = ADR_FILENAME_PATTERN.match("ADR-01-auth.md")
        assert match is None

    def test_invalid_adr_filename_wrong_extension(self) -> None:
        """Test invalid filename with wrong extension."""
        match = ADR_FILENAME_PATTERN.match("ADR-001-auth.txt")
        assert match is None

    def test_invalid_adr_filename_lowercase(self) -> None:
        """Test invalid filename with lowercase ADR."""
        match = ADR_FILENAME_PATTERN.match("adr-001-auth.md")
        assert match is None


class TestADRValidationResult:
    """Tests for ADRValidationResult dataclass."""

    def test_valid_result(self) -> None:
        """Test creating a valid result."""
        result = ADRValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            adr_number=1,
            adr_title="Auth Strategy",
        )
        assert result.is_valid
        assert result.adr_number == 1
        assert result.adr_title == "Auth Strategy"

    def test_invalid_result_with_errors(self) -> None:
        """Test creating an invalid result with errors."""
        result = ADRValidationResult(
            is_valid=False,
            errors=["Missing required section: '## Status'"],
        )
        assert not result.is_valid
        assert len(result.errors) == 1

    def test_to_dict(self) -> None:
        """Test result serialization to dict."""
        result = ADRValidationResult(
            is_valid=True,
            adr_number=1,
            adr_title="Auth Strategy",
            adr_path=Path("/tmp/ADR-001-auth.md"),
        )
        d = result.to_dict()
        assert d["is_valid"] is True
        assert d["adr_number"] == 1
        assert d["adr_title"] == "Auth Strategy"
        assert d["adr_path"] == "/tmp/ADR-001-auth.md"


class TestADRValidator:
    """Tests for ADRValidator class."""

    @pytest.fixture
    def validator(self) -> ADRValidator:
        """Create a validator instance."""
        return ADRValidator()

    @pytest.fixture
    def valid_adr_content(self) -> str:
        """Return valid ADR content."""
        return """# ADR-001: Authentication Strategy

## Status

Accepted

## Context

We need to implement authentication for our API.

## Decision

We will use OAuth 2.0 with JWT tokens.

## Consequences

### Positive

- Industry standard
- Good library support

### Negative

- Added complexity
"""

    @pytest.fixture
    def adr_missing_status(self) -> str:
        """Return ADR content missing status section."""
        return """# ADR-001: Authentication Strategy

## Context

We need to implement authentication.

## Decision

Use OAuth 2.0.

## Consequences

Some consequences.
"""

    @pytest.fixture
    def adr_empty_decision(self) -> str:
        """Return ADR content with empty decision section."""
        return """# ADR-001: Authentication Strategy

## Status

Proposed

## Context

We need to implement authentication.

## Decision

## Consequences

Some consequences.
"""

    def test_validate_valid_adr(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating a valid ADR file."""
        adr_file = tmp_path / "ADR-001-auth-strategy.md"
        adr_file.write_text(valid_adr_content)

        result = validator.validate_adr(adr_file)

        assert result.is_valid
        assert result.adr_number == 1
        assert result.adr_title == "Auth Strategy"
        assert result.status == "Accepted"
        assert "Status" in result.sections_found
        assert "Context" in result.sections_found
        assert "Decision" in result.sections_found
        assert "Consequences" in result.sections_found

    def test_validate_missing_file(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating a non-existent file."""
        adr_file = tmp_path / "ADR-001-missing.md"

        result = validator.validate_adr(adr_file)

        assert not result.is_valid
        assert "not found" in result.errors[0].lower()

    def test_validate_invalid_filename(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating ADR with invalid filename."""
        adr_file = tmp_path / "adr-01-auth.md"
        adr_file.write_text(valid_adr_content)

        result = validator.validate_adr(adr_file)

        assert not result.is_valid
        assert any("filename" in e.lower() for e in result.errors)

    def test_validate_missing_status_section(
        self,
        validator: ADRValidator,
        adr_missing_status: str,
        tmp_path: Path,
    ) -> None:
        """Test validating ADR missing status section."""
        adr_file = tmp_path / "ADR-001-auth.md"
        adr_file.write_text(adr_missing_status)

        result = validator.validate_adr(adr_file)

        assert not result.is_valid
        assert any("status" in e.lower() for e in result.errors)

    def test_validate_empty_section(
        self,
        validator: ADRValidator,
        adr_empty_decision: str,
        tmp_path: Path,
    ) -> None:
        """Test validating ADR with empty required section."""
        adr_file = tmp_path / "ADR-001-auth.md"
        adr_file.write_text(adr_empty_decision)

        result = validator.validate_adr(adr_file)

        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_invalid_status_value(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating ADR with invalid status value."""
        content = """# ADR-001: Auth

## Status

Invalid

## Context

Some context.

## Decision

Some decision.

## Consequences

Some consequences.
"""
        adr_file = tmp_path / "ADR-001-auth.md"
        adr_file.write_text(content)

        result = validator.validate_adr(adr_file)

        assert not result.is_valid
        assert any("invalid status" in e.lower() for e in result.errors)

    def test_validate_superseded_status(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating ADR with superseded status."""
        content = """# ADR-001: Auth

## Status

Superseded by ADR-002

## Context

Some context.

## Decision

Some decision.

## Consequences

Some consequences.
"""
        adr_file = tmp_path / "ADR-001-auth.md"
        adr_file.write_text(content)

        result = validator.validate_adr(adr_file)

        assert result.is_valid
        assert result.status == "Superseded by ADR-002"

    def test_validate_directory_valid(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating a directory with valid ADRs."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        adr1 = adr_dir / "ADR-001-auth.md"
        adr1.write_text(valid_adr_content)

        adr2_content = valid_adr_content.replace("001", "002").replace("Auth", "DB")
        adr2 = adr_dir / "ADR-002-database.md"
        adr2.write_text(adr2_content)

        result = validator.validate_directory(adr_dir)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_directory_missing(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating a non-existent directory."""
        adr_dir = tmp_path / "missing-adr"

        result = validator.validate_directory(adr_dir)

        assert not result.is_valid
        assert "not found" in result.errors[0].lower()

    def test_validate_directory_empty(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating an empty directory."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        result = validator.validate_directory(adr_dir)

        assert not result.is_valid
        assert "no adr files" in result.errors[0].lower()

    def test_validate_directory_min_count(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating directory with minimum count requirement."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        adr1 = adr_dir / "ADR-001-auth.md"
        adr1.write_text(valid_adr_content)

        result = validator.validate_directory(adr_dir, min_count=2)

        assert not result.is_valid
        assert any("expected at least 2" in e.lower() for e in result.errors)

    def test_validate_directory_duplicate_numbers(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating directory with duplicate ADR numbers."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        # Two ADRs with same number
        (adr_dir / "ADR-001-auth.md").write_text(valid_adr_content)
        (adr_dir / "ADR-001-database.md").write_text(valid_adr_content)

        result = validator.validate_directory(adr_dir)

        assert not result.is_valid
        assert any("duplicate" in e.lower() for e in result.errors)

    def test_get_next_adr_number_empty_dir(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test getting next ADR number from empty directory."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        number = validator.get_next_adr_number(adr_dir)

        assert number == 1

    def test_get_next_adr_number_nonexistent_dir(
        self,
        validator: ADRValidator,
        tmp_path: Path,
    ) -> None:
        """Test getting next ADR number from non-existent directory."""
        adr_dir = tmp_path / "missing-adr"

        number = validator.get_next_adr_number(adr_dir)

        assert number == 1

    def test_get_next_adr_number_existing_adrs(
        self,
        validator: ADRValidator,
        valid_adr_content: str,
        tmp_path: Path,
    ) -> None:
        """Test getting next ADR number with existing ADRs."""
        adr_dir = tmp_path / "adr"
        adr_dir.mkdir()

        (adr_dir / "ADR-001-auth.md").write_text(valid_adr_content)
        (adr_dir / "ADR-002-db.md").write_text(valid_adr_content)
        (adr_dir / "ADR-005-api.md").write_text(valid_adr_content)

        number = validator.get_next_adr_number(adr_dir)

        assert number == 6

    def test_strict_mode(
        self,
        tmp_path: Path,
    ) -> None:
        """Test strict mode treats warnings as errors."""
        content = """# ADR-001: Auth

## Status

Accepted

## Context

Some context.

## Decision

Some decision.

## Consequences

Some consequences.
"""
        adr_file = tmp_path / "ADR-001-auth.md"
        adr_file.write_text(content)

        # Normal mode - missing "alternatives considered" is warning
        validator = ADRValidator(strict=False)
        result = validator.validate_adr(adr_file)
        assert result.is_valid
        assert len(result.warnings) > 0

        # Strict mode - warnings become errors
        strict_validator = ADRValidator(strict=True)
        strict_result = strict_validator.validate_adr(adr_file)
        assert not strict_result.is_valid
        assert len(strict_result.errors) > 0
        assert len(strict_result.warnings) == 0


class TestValidateADRForTransition:
    """Tests for convenience function."""

    def test_validate_adr_for_transition(
        self,
        tmp_path: Path,
    ) -> None:
        """Test convenience function for transition validation."""
        adr_dir = tmp_path / "docs" / "adr"
        adr_dir.mkdir(parents=True)

        content = """# ADR-001: Auth

## Status

Accepted

## Context

Context.

## Decision

Decision.

## Consequences

Consequences.
"""
        (adr_dir / "ADR-001-auth.md").write_text(content)

        result = validate_adr_for_transition(adr_dir)

        assert result.is_valid
