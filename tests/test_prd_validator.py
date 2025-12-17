"""Tests for PRD (Product Requirements Document) validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from flowspec_cli.workflow.prd_validator import (
    PRD_FILENAME_PATTERN,
    PRDValidationResult,
    PRDValidator,
    validate_prd_for_transition,
)


class TestPRDFilenamePattern:
    """Tests for PRD filename pattern matching."""

    def test_valid_prd_filename(self) -> None:
        """Test valid PRD filename pattern."""
        match = PRD_FILENAME_PATTERN.match("user-authentication.md")
        assert match is not None

    def test_valid_prd_filename_simple(self) -> None:
        """Test valid PRD filename with simple name."""
        match = PRD_FILENAME_PATTERN.match("auth.md")
        assert match is not None

    def test_valid_prd_filename_underscores(self) -> None:
        """Test valid filename with underscores."""
        match = PRD_FILENAME_PATTERN.match("user_auth.md")
        assert match is not None

    def test_invalid_prd_filename_spaces(self) -> None:
        """Test invalid filename with spaces."""
        match = PRD_FILENAME_PATTERN.match("user auth.md")
        assert match is None

    def test_invalid_prd_filename_wrong_extension(self) -> None:
        """Test invalid filename with wrong extension."""
        match = PRD_FILENAME_PATTERN.match("auth.txt")
        assert match is None


class TestPRDValidationResult:
    """Tests for PRDValidationResult dataclass."""

    def test_valid_result(self) -> None:
        """Test creating a valid result."""
        result = PRDValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            feature_name="User Authentication",
            user_story_count=3,
            ac_count=10,
        )
        assert result.is_valid
        assert result.feature_name == "User Authentication"
        assert result.user_story_count == 3
        assert result.ac_count == 10

    def test_invalid_result_with_errors(self) -> None:
        """Test creating an invalid result with errors."""
        result = PRDValidationResult(
            is_valid=False,
            errors=["Missing required section: '## Executive Summary'"],
        )
        assert not result.is_valid
        assert len(result.errors) == 1

    def test_to_dict(self) -> None:
        """Test result serialization to dict."""
        result = PRDValidationResult(
            is_valid=True,
            feature_name="Auth",
            prd_path=Path("/tmp/auth.md"),
            user_story_count=2,
            ac_count=5,
        )
        d = result.to_dict()
        assert d["is_valid"] is True
        assert d["feature_name"] == "Auth"
        assert d["prd_path"] == "/tmp/auth.md"
        assert d["user_story_count"] == 2
        assert d["ac_count"] == 5


class TestPRDValidator:
    """Tests for PRDValidator class."""

    @pytest.fixture
    def validator(self) -> PRDValidator:
        """Create a validator instance."""
        return PRDValidator()

    @pytest.fixture
    def valid_prd_content(self) -> str:
        """Return valid PRD content."""
        return """# PRD: User Authentication

## Executive Summary

This PRD describes the user authentication feature.

## Problem Statement

Users need secure authentication.

## User Stories

### US1: Login

As a user, I want to login so that I can access my account.

- AC1: User can enter email and password
- AC2: User sees error for invalid credentials

## Functional Requirements

User must be able to login with email/password.

## Non-Functional Requirements

System must respond within 200ms.

## Success Metrics

- Login success rate > 99%

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Demonstrates authentication patterns |
"""

    @pytest.fixture
    def prd_missing_section(self) -> str:
        """Return PRD content missing a required section."""
        return """# PRD: User Authentication

## Executive Summary

This is the summary.

## Problem Statement

The problem.

## User Stories

As a user, I want to login so that I can access my account.

## Functional Requirements

Requirements here.

## Non-Functional Requirements

NFR here.
"""

    @pytest.fixture
    def prd_no_user_stories(self) -> str:
        """Return PRD content with no user stories."""
        return """# PRD: User Authentication

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

No stories here.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Example authentication patterns |
"""

    def test_validate_valid_prd(
        self,
        validator: PRDValidator,
        valid_prd_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating a valid PRD file."""
        prd_file = tmp_path / "user-authentication.md"
        prd_file.write_text(valid_prd_content)

        result = validator.validate_prd(prd_file)

        assert result.is_valid
        assert result.feature_name == "User Authentication"
        assert result.user_story_count >= 1
        assert result.ac_count >= 1
        assert "Executive Summary" in result.sections_found
        assert "Problem Statement" in result.sections_found

    def test_validate_missing_file(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating a non-existent file."""
        prd_file = tmp_path / "missing.md"

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert "not found" in result.errors[0].lower()

    def test_validate_invalid_filename(
        self,
        validator: PRDValidator,
        valid_prd_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD with invalid filename."""
        prd_file = tmp_path / "user auth.md"
        prd_file.write_text(valid_prd_content)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("filename" in e.lower() for e in result.errors)

    def test_validate_missing_section(
        self,
        validator: PRDValidator,
        prd_missing_section: str,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD missing required section."""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(prd_missing_section)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("success metrics" in e.lower() for e in result.errors)

    def test_validate_no_user_stories(
        self,
        validator: PRDValidator,
        prd_no_user_stories: str,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD with no user stories."""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(prd_no_user_stories)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("user stories" in e.lower() for e in result.errors)

    def test_validate_missing_all_needed_context(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD missing All Needed Context section (includes Examples)."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("all needed context" in e.lower() for e in result.errors)

    def test_validate_missing_example_references(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD with All Needed Context but no example references."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

No examples provided yet.
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("example references" in e.lower() for e in result.errors)
        assert result.example_count == 0

    def test_validate_placeholder_example_references_excluded(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test that placeholder rows with curly braces are excluded from example count."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| {Example name} | `examples/{path}` | {How this example relates} |
| {Another example} | examples/{another/path} | {Description} |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        # Placeholder rows should be excluded, so example_count should be 0
        assert result.example_count == 0
        assert not result.is_valid
        assert any("example references" in e.lower() for e in result.errors)

    def test_validate_placeholder_in_single_column_excluded(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test that rows with curly braces in ANY column are excluded.

        This tests edge cases where:
        - Placeholder in name column only: | {Example} | examples/real/path.py | Desc |
        - Placeholder in description only: | Example | examples/real/path.py | {Desc} |
        - Real path but placeholder name/desc should be excluded
        """
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| {Example name} | `examples/auth/real-file.py` | Real description here |
| Real Example | `examples/auth/login.py` | {Placeholder description} |
| {Placeholder} | examples/valid/path.py | {Both placeholders} |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        # All rows have curly braces in at least one column, so none should count
        assert result.example_count == 0
        assert not result.is_valid
        assert any("example references" in e.lower() for e in result.errors)

    def test_validate_closing_brace_only_excluded(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test that rows with only closing braces } are also excluded.

        This verifies that both opening { and closing } braces trigger exclusion,
        not just opening braces. Catches malformed placeholders like "}Description}"
        or incomplete template rows.
        """
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Example} | `examples/auth/file.py` | Description here |
| Name | `examples/auth/}path.py` | Description |
| Valid Name | `examples/auth/valid.py` | }Broken description |
| Real Example | `examples/auth/handler.py` | Correct description |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        # Only the last row (Real Example) has no braces in any column
        assert result.example_count == 1
        assert result.is_valid  # Has the one required example

    def test_validate_mixed_placeholder_and_real_examples(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test that real examples are counted even when mixed with placeholders."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| {Example name} | `examples/{path}` | {Placeholder row} |
| Auth Handler | `examples/auth/handler.py` | Shows authentication patterns |
| {Another placeholder} | examples/fake/{path} | {Desc} |
| Login Flow | `examples/auth/login.py` | Demonstrates login implementation |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        # Only the 2 real examples should count (Auth Handler and Login Flow)
        assert result.example_count == 2
        assert result.is_valid  # Has required examples

    def test_validate_html_comments_excluded(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test that example tables inside HTML comments are not counted.

        This verifies that demo/example tables wrapped in HTML comments
        (like those in prd-template.md) don't inflate the example count.
        """
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Real Example | `examples/auth/handler.py` | Shows real authentication patterns |

<!-- Example of a Good Reference (wrapped in HTML comment to prevent validator from counting it):
| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Demo Example | `examples/demo/file.py` | This should NOT be counted |
-->

<!-- Another commented table that should not count:
| Hidden Example | `examples/hidden/path.py` | Should be excluded |
-->
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        # Only the real example outside HTML comments should count
        assert result.example_count == 1
        assert result.is_valid  # Has the one required example

    def test_validate_empty_section(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD with empty required section."""
        content = """# PRD: Auth

## Executive Summary

## Problem Statement

Some problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Example authentication patterns |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_for_feature(
        self,
        validator: PRDValidator,
        valid_prd_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD for a specific feature."""
        prd_dir = tmp_path / "docs" / "prd"
        prd_dir.mkdir(parents=True)

        prd_file = prd_dir / "user-authentication.md"
        prd_file.write_text(valid_prd_content)

        result = validator.validate_for_feature(prd_dir, "user-authentication")

        assert result.is_valid

    def test_validate_for_feature_with_spaces(
        self,
        validator: PRDValidator,
        valid_prd_content: str,
        tmp_path: Path,
    ) -> None:
        """Test validating PRD for feature name with spaces."""
        prd_dir = tmp_path / "docs" / "prd"
        prd_dir.mkdir(parents=True)

        prd_file = prd_dir / "user-authentication.md"
        prd_file.write_text(valid_prd_content)

        result = validator.validate_for_feature(prd_dir, "user authentication")

        assert result.is_valid

    def test_strict_mode(
        self,
        tmp_path: Path,
    ) -> None:
        """Test strict mode treats warnings as errors."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

- AC1: Criterion

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Example authentication patterns |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        # Normal mode - missing recommended sections are warnings
        validator = PRDValidator(strict=False)
        result = validator.validate_prd(prd_file)
        assert result.is_valid
        assert len(result.warnings) > 0

        # Strict mode - warnings become errors
        strict_validator = PRDValidator(strict=True)
        strict_result = strict_validator.validate_prd(prd_file)
        assert not strict_result.is_valid
        assert len(strict_result.errors) > 0
        assert len(strict_result.warnings) == 0

    def test_user_story_variations(
        self,
        validator: PRDValidator,
        tmp_path: Path,
    ) -> None:
        """Test various user story formats are recognized."""
        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

US1: As a user, I want to login so that I can access my account.
As an admin, I want to manage users in order to maintain the system.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Example authentication patterns |
"""
        prd_file = tmp_path / "auth.md"
        prd_file.write_text(content)

        result = validator.validate_prd(prd_file)

        assert result.is_valid
        assert result.user_story_count == 2


class TestValidatePRDForTransition:
    """Tests for convenience function."""

    def test_validate_prd_for_transition(
        self,
        tmp_path: Path,
    ) -> None:
        """Test convenience function for transition validation."""
        prd_dir = tmp_path / "docs" / "prd"
        prd_dir.mkdir(parents=True)

        content = """# PRD: Auth

## Executive Summary

Summary.

## Problem Statement

Problem.

## User Stories

As a user, I want to login so that I can access.

## Functional Requirements

Requirements.

## Non-Functional Requirements

NFR.

## Success Metrics

Metrics.

## All Needed Context

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Auth Example | `examples/auth/login.py` | Example authentication patterns |
"""
        (prd_dir / "auth.md").write_text(content)

        result = validate_prd_for_transition(prd_dir, "auth")

        assert result.is_valid
