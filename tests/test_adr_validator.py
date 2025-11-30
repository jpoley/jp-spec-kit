"""Tests for ADR validator and helper functions."""

import pytest

from specify_cli.workflow.artifact_validators import (
    ADRValidator,
    find_existing_adrs,
    get_next_adr_number,
)


@pytest.fixture
def temp_adr_dir(tmp_path):
    """Create a temporary ADR directory."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    return adr_dir


@pytest.fixture
def valid_adr_content():
    """Return valid ADR content."""
    return """# ADR-001: Use PostgreSQL for Primary Database

**Date**: 2024-01-15

## Status

Accepted

## Context

We need to select a primary database for our application. The system requires ACID
compliance, complex querying capabilities, and strong consistency guarantees.

## Decision

We will use PostgreSQL as our primary relational database.

## Consequences

### Positive

- Strong ACID compliance
- Mature ecosystem with excellent tooling
- Superior query optimizer for complex queries
- Native JSON support for flexible data

### Negative

- Higher operational complexity than NoSQL alternatives
- Vertical scaling challenges at extreme scale
- Requires careful index management for optimal performance

## Alternatives Considered

1. **MySQL**: Considered but PostgreSQL has better JSON support and more advanced features
2. **MongoDB**: Rejected due to lack of strong consistency guarantees
3. **DynamoDB**: Too expensive for our use case and vendor lock-in concerns
"""


@pytest.fixture
def minimal_adr_content():
    """Return minimal valid ADR content."""
    return """# ADR-002: Minimal Decision

## Status

Proposed

## Context

Some context here.

## Decision

We will do something.

## Consequences

Some consequences.

## Alternatives Considered

Other options were rejected.
"""


@pytest.fixture
def missing_sections_adr():
    """Return ADR content missing required sections."""
    return """# ADR-003: Incomplete Decision

## Status

Proposed

## Context

Some context.

## Decision

Some decision.
"""


class TestGetNextADRNumber:
    """Tests for get_next_adr_number function."""

    def test_no_adrs_returns_one(self, temp_adr_dir):
        """Should return 1 when no ADRs exist."""
        result = get_next_adr_number(temp_adr_dir)
        assert result == 1

    def test_nonexistent_dir_returns_one(self, tmp_path):
        """Should return 1 when directory doesn't exist."""
        nonexistent = tmp_path / "does_not_exist"
        result = get_next_adr_number(nonexistent)
        assert result == 1

    def test_single_adr_returns_two(self, temp_adr_dir):
        """Should return 2 when ADR-001 exists."""
        (temp_adr_dir / "ADR-001-first.md").touch()
        result = get_next_adr_number(temp_adr_dir)
        assert result == 2

    def test_multiple_adrs_returns_max_plus_one(self, temp_adr_dir):
        """Should return max number + 1 when multiple ADRs exist."""
        (temp_adr_dir / "ADR-001-first.md").touch()
        (temp_adr_dir / "ADR-002-second.md").touch()
        (temp_adr_dir / "ADR-005-fifth.md").touch()
        result = get_next_adr_number(temp_adr_dir)
        assert result == 6

    def test_ignores_non_adr_files(self, temp_adr_dir):
        """Should ignore files that don't match ADR pattern."""
        (temp_adr_dir / "ADR-001-first.md").touch()
        (temp_adr_dir / "README.md").touch()
        (temp_adr_dir / "notes.txt").touch()
        result = get_next_adr_number(temp_adr_dir)
        assert result == 2

    def test_handles_gaps_in_numbering(self, temp_adr_dir):
        """Should handle gaps in ADR numbering."""
        (temp_adr_dir / "ADR-001-first.md").touch()
        (temp_adr_dir / "ADR-003-third.md").touch()
        (temp_adr_dir / "ADR-010-tenth.md").touch()
        result = get_next_adr_number(temp_adr_dir)
        assert result == 11


class TestFindExistingADRs:
    """Tests for find_existing_adrs function."""

    def test_empty_directory_returns_empty_list(self, temp_adr_dir):
        """Should return empty list when no ADRs exist."""
        result = find_existing_adrs(temp_adr_dir)
        assert result == []

    def test_nonexistent_directory_returns_empty_list(self, tmp_path):
        """Should return empty list when directory doesn't exist."""
        nonexistent = tmp_path / "does_not_exist"
        result = find_existing_adrs(nonexistent)
        assert result == []

    def test_finds_single_adr(self, temp_adr_dir):
        """Should find single ADR file."""
        adr_file = temp_adr_dir / "ADR-001-first.md"
        adr_file.touch()
        result = find_existing_adrs(temp_adr_dir)
        assert len(result) == 1
        assert result[0] == adr_file

    def test_finds_multiple_adrs_sorted(self, temp_adr_dir):
        """Should find multiple ADRs sorted by number."""
        # Create out of order
        adr3 = temp_adr_dir / "ADR-003-third.md"
        adr1 = temp_adr_dir / "ADR-001-first.md"
        adr2 = temp_adr_dir / "ADR-002-second.md"

        adr3.touch()
        adr1.touch()
        adr2.touch()

        result = find_existing_adrs(temp_adr_dir)
        assert len(result) == 3
        assert result[0] == adr1
        assert result[1] == adr2
        assert result[2] == adr3

    def test_ignores_non_adr_files(self, temp_adr_dir):
        """Should ignore files that don't match ADR pattern."""
        (temp_adr_dir / "ADR-001-first.md").touch()
        (temp_adr_dir / "README.md").touch()
        (temp_adr_dir / "notes.txt").touch()
        (temp_adr_dir / "ADR-template.md").touch()

        result = find_existing_adrs(temp_adr_dir)
        assert len(result) == 1

    def test_handles_gaps_in_numbering(self, temp_adr_dir):
        """Should handle gaps in ADR numbering correctly."""
        adr1 = temp_adr_dir / "ADR-001-first.md"
        adr5 = temp_adr_dir / "ADR-005-fifth.md"
        adr10 = temp_adr_dir / "ADR-010-tenth.md"

        adr1.touch()
        adr5.touch()
        adr10.touch()

        result = find_existing_adrs(temp_adr_dir)
        assert len(result) == 3
        assert result[0] == adr1
        assert result[1] == adr5
        assert result[2] == adr10


class TestADRValidator:
    """Tests for ADRValidator class."""

    def test_valid_adr_passes(self, temp_adr_dir, valid_adr_content):
        """Should pass validation for valid ADR."""
        adr_file = temp_adr_dir / "ADR-001-postgresql.md"
        adr_file.write_text(valid_adr_content)

        validator = ADRValidator()
        result = validator.validate(adr_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_minimal_adr_passes(self, temp_adr_dir, minimal_adr_content):
        """Should pass validation for minimal valid ADR."""
        adr_file = temp_adr_dir / "ADR-002-minimal.md"
        adr_file.write_text(minimal_adr_content)

        validator = ADRValidator()
        result = validator.validate(adr_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_file_fails(self, temp_adr_dir):
        """Should fail validation when file doesn't exist."""
        nonexistent = temp_adr_dir / "ADR-999-missing.md"

        validator = ADRValidator()
        result = validator.validate(nonexistent)

        assert result.valid is False
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]

    def test_missing_required_sections_fails(self, temp_adr_dir, missing_sections_adr):
        """Should fail validation when required sections are missing."""
        adr_file = temp_adr_dir / "ADR-003-incomplete.md"
        adr_file.write_text(missing_sections_adr)

        validator = ADRValidator()
        result = validator.validate(adr_file)

        assert result.valid is False
        assert any("Consequences" in error for error in result.errors)
        assert any("Alternatives Considered" in error for error in result.errors)

    def test_invalid_filename_warns(self, temp_adr_dir, valid_adr_content):
        """Should warn when filename doesn't follow pattern."""
        bad_name = temp_adr_dir / "decision-001.md"
        bad_name.write_text(valid_adr_content)

        validator = ADRValidator()
        result = validator.validate(bad_name)

        assert result.valid is True  # Still valid, just a warning
        assert len(result.warnings) > 0
        assert any("pattern" in warning.lower() for warning in result.warnings)

    def test_invalid_status_warns(self, temp_adr_dir):
        """Should warn when status is invalid."""
        content = """# ADR-001: Test

## Status

InvalidStatus

## Context

Test context.

## Decision

Test decision.

## Consequences

Test consequences.

## Alternatives Considered

None.
"""
        adr_file = temp_adr_dir / "ADR-001-test.md"
        adr_file.write_text(content)

        validator = ADRValidator()
        result = validator.validate(adr_file)

        assert result.valid is True
        assert len(result.warnings) > 0
        assert any("Invalid status" in warning for warning in result.warnings)

    def test_valid_statuses_accepted(self, temp_adr_dir):
        """Should accept all valid status values."""
        valid_statuses = ["Proposed", "Accepted", "Deprecated", "Superseded"]

        for status in valid_statuses:
            content = f"""# ADR-001: Test

## Status

{status}

## Context

Test context.

## Decision

Test decision.

## Consequences

Test consequences.

## Alternatives Considered

None.
"""
            adr_file = temp_adr_dir / f"ADR-001-{status.lower()}.md"
            adr_file.write_text(content)

            validator = ADRValidator()
            result = validator.validate(adr_file)

            assert result.valid is True, f"Status '{status}' should be valid"
            # No warnings about invalid status
            assert not any(
                "Invalid status" in warning for warning in result.warnings
            ), f"Status '{status}' should not trigger warning"

    def test_case_insensitive_section_matching(self, temp_adr_dir):
        """Should match sections case-insensitively."""
        content = """# ADR-001: Test

## status

Proposed

## CONTEXT

Test context.

## Decision

Test decision.

## consequences

Test consequences.

## alternatives considered

None.
"""
        adr_file = temp_adr_dir / "ADR-001-test.md"
        adr_file.write_text(content)

        validator = ADRValidator()
        result = validator.validate(adr_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_directory_not_file_fails(self, temp_adr_dir):
        """Should fail validation when path is a directory."""
        validator = ADRValidator()
        result = validator.validate(temp_adr_dir)

        assert result.valid is False
        assert any("not a file" in error for error in result.errors)


class TestADRValidatorIntegration:
    """Integration tests for ADR validator with numbering."""

    def test_create_sequence_of_adrs(self, temp_adr_dir, valid_adr_content):
        """Should validate a sequence of ADRs with correct numbering."""
        validator = ADRValidator()

        # Create first ADR
        num1 = get_next_adr_number(temp_adr_dir)
        assert num1 == 1

        adr1 = temp_adr_dir / "ADR-001-first.md"
        adr1.write_text(valid_adr_content)
        result1 = validator.validate(adr1)
        assert result1.valid is True

        # Create second ADR
        num2 = get_next_adr_number(temp_adr_dir)
        assert num2 == 2

        adr2 = temp_adr_dir / "ADR-002-second.md"
        adr2.write_text(valid_adr_content)
        result2 = validator.validate(adr2)
        assert result2.valid is True

        # Verify both exist
        adrs = find_existing_adrs(temp_adr_dir)
        assert len(adrs) == 2
        assert adrs[0].name == "ADR-001-first.md"
        assert adrs[1].name == "ADR-002-second.md"

    def test_find_and_validate_all_adrs(self, temp_adr_dir, valid_adr_content):
        """Should find and validate all ADRs in directory."""
        # Create multiple ADRs
        for i in range(1, 4):
            adr = temp_adr_dir / f"ADR-{i:03d}-decision.md"
            adr.write_text(valid_adr_content)

        # Find all ADRs
        adrs = find_existing_adrs(temp_adr_dir)
        assert len(adrs) == 3

        # Validate each
        validator = ADRValidator()
        for adr in adrs:
            result = validator.validate(adr)
            assert result.valid is True, f"ADR {adr.name} should be valid"
