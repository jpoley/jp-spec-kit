"""Tests for PRD validator.

Tests validation of Product Requirements Documents including:
- File existence checks
- Required section validation
- User story acceptance criteria validation
- Functional requirements numbering
- Success metrics validation
- Placeholder content detection
"""

import pytest

from specify_cli.workflow.artifact_validators import (
    PRDValidator,
    ValidationResult,
    get_validator,
)


@pytest.fixture
def prd_validator():
    """Fixture providing a PRD validator instance."""
    return PRDValidator()


@pytest.fixture
def temp_prd_file(tmp_path):
    """Fixture providing a temporary PRD file path."""
    docs_dir = tmp_path / "docs" / "prd"
    docs_dir.mkdir(parents=True)
    return docs_dir / "test-feature.md"


class TestPRDValidatorBasic:
    """Basic validation tests for PRD validator."""

    def test_validator_initialization(self, prd_validator):
        """Test PRD validator can be initialized."""
        assert prd_validator is not None
        assert prd_validator.REQUIRED_SECTIONS is not None
        assert len(prd_validator.REQUIRED_SECTIONS) == 9

    def test_get_validator_returns_prd_validator(self):
        """Test get_validator returns PRDValidator for 'prd' type."""
        validator = get_validator("prd")
        assert isinstance(validator, PRDValidator)

    def test_get_validator_case_insensitive(self):
        """Test get_validator is case insensitive."""
        validator1 = get_validator("prd")
        validator2 = get_validator("PRD")
        validator3 = get_validator("Prd")

        assert isinstance(validator1, PRDValidator)
        assert isinstance(validator2, PRDValidator)
        assert isinstance(validator3, PRDValidator)

    def test_get_validator_unknown_type_returns_none(self):
        """Test get_validator returns None for unknown types."""
        validator = get_validator("unknown")
        assert validator is None


class TestPRDValidatorFileChecks:
    """Test file existence and readability checks."""

    def test_validation_fails_if_file_not_found(self, prd_validator, tmp_path):
        """Test validation fails if PRD file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.md"
        result = prd_validator.validate(nonexistent_file)

        assert not result.valid
        assert len(result.errors) == 1
        assert "not found" in result.errors[0]

    def test_validation_fails_if_path_is_directory(self, prd_validator, tmp_path):
        """Test validation fails if path is a directory."""
        directory = tmp_path / "docs"
        directory.mkdir()

        result = prd_validator.validate(directory)

        assert not result.valid
        assert "not a file" in result.errors[0]

    def test_validation_fails_if_file_not_readable(self, prd_validator, temp_prd_file):
        """Test validation fails if file cannot be read."""
        # Create file with invalid encoding
        temp_prd_file.write_bytes(b"\x80\x81\x82\x83")

        result = prd_validator.validate(temp_prd_file)

        # File exists but cannot be read as UTF-8
        assert not result.valid
        assert len(result.errors) >= 1


class TestPRDValidatorRequiredSections:
    """Test required section validation."""

    def test_validation_fails_if_missing_all_sections(
        self, prd_validator, temp_prd_file
    ):
        """Test validation fails if all sections are missing."""
        temp_prd_file.write_text("# Incomplete PRD\n\nSome content but no sections.")

        result = prd_validator.validate(temp_prd_file)

        assert not result.valid
        assert len(result.errors) == 9  # All 9 required sections missing

    def test_validation_fails_if_missing_some_sections(
        self, prd_validator, temp_prd_file
    ):
        """Test validation fails if some required sections are missing."""
        content = """# PRD: Test Feature

## Executive Summary

Some summary content.

## Problem Statement

Some problem description.

## User Stories

Story content.
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert not result.valid
        # Missing: Functional Requirements, Non-Functional Requirements,
        # Success Metrics, Dependencies, Risks and Mitigations, Out of Scope
        assert len(result.errors) == 6

    def test_validation_passes_with_all_required_sections(
        self, prd_validator, temp_prd_file
    ):
        """Test validation passes when all required sections present."""
        content = """# PRD: Test Feature

## Executive Summary

Executive summary content.

## Problem Statement

Problem description.

## User Stories

### User Story 1 - Login (Priority: P1)

**As a** user
**I want** to log in
**So that** I can access the system

**Acceptance Criteria**:

1. **Given** valid credentials, **When** user logs in, **Then** access is granted

## Functional Requirements

- **FR-001**: System MUST authenticate users
- **FR-002**: System MUST validate credentials
- **FR-003**: System MUST log login attempts

## Non-Functional Requirements

- **NFR-001**: Login MUST complete in under 2 seconds
- **NFR-002**: System MUST encrypt credentials in transit

## Success Metrics

- **SM-001**: 95% of login attempts succeed within 2 seconds
- **SM-002**: Zero credential leaks

## Dependencies

- **DEP-001**: Requires authentication service v2.0

## Risks and Mitigations

| Risk ID | Risk Description | Impact | Probability | Mitigation Strategy |
|---------|------------------|--------|-------------|---------------------|
| RISK-001 | Auth service down | High | Low | Implement retry logic |

## Out of Scope

- Single sign-on (SSO) integration
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert result.valid
        assert len(result.errors) == 0

    def test_section_detection_is_case_insensitive(self, prd_validator, temp_prd_file):
        """Test section headers are matched case-insensitively."""
        content = """# PRD

## executive summary
Content
## PROBLEM STATEMENT
Content
## User Stories
Content
## functional requirements
- **FR-001**: Requirement
## Non-Functional Requirements
- **NFR-001**: Requirement
## success metrics
- **SM-001**: Metric
## dependencies
Content
## RISKS AND MITIGATIONS
Content
## out of scope
Content
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        # All sections present despite case variations
        assert result.valid or len(result.errors) == 0


class TestPRDValidatorAcceptanceCriteria:
    """Test user story acceptance criteria validation."""

    def test_warning_if_user_story_missing_acceptance_criteria(
        self, prd_validator, temp_prd_file
    ):
        """Test warning if user story has no acceptance criteria section."""
        content = """# PRD

## User Stories

### User Story 1 - Feature A

Description of the story but no acceptance criteria.

### User Story 2 - Feature B

Another story without criteria.
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        # Warnings don't fail validation
        assert len(result.warnings) >= 2
        assert "Acceptance Criteria" in result.warnings[0]

    def test_warning_if_acceptance_criteria_lacks_given_when_then(
        self, prd_validator, temp_prd_file
    ):
        """Test warning if AC exists but lacks Given-When-Then format."""
        content = """# PRD

## User Stories

### User Story 1 - Feature A

**Acceptance Criteria**:

- User can do X
- System does Y
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        assert "Given-When-Then" in result.warnings[0]

    def test_no_warning_if_acceptance_criteria_properly_formatted(
        self, prd_validator, temp_prd_file
    ):
        """Test no warning when AC uses Given-When-Then format."""
        content = """# PRD

## User Stories

### User Story 1 - Feature A

**Acceptance Criteria**:

1. **Given** initial state, **When** action, **Then** outcome
2. **Given** another state, **When** different action, **Then** result
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        # No warnings about this story's acceptance criteria
        ac_warnings = [w for w in result.warnings if "Acceptance Criteria" in w]
        assert len(ac_warnings) == 0


class TestPRDValidatorFunctionalRequirements:
    """Test functional requirements validation."""

    def test_warning_if_no_numbered_functional_requirements(
        self, prd_validator, temp_prd_file
    ):
        """Test warning if functional requirements aren't numbered."""
        content = """# PRD

## Functional Requirements

- System should do X
- System should do Y
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        assert "no numbered requirements" in result.warnings[0]

    def test_warning_if_too_few_functional_requirements(
        self, prd_validator, temp_prd_file
    ):
        """Test warning if fewer than 3 functional requirements."""
        content = """# PRD

## Functional Requirements

- **FR-001**: System MUST do X
- **FR-002**: System MUST do Y
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        assert "Only 2 functional requirements" in result.warnings[0]

    def test_no_warning_if_sufficient_functional_requirements(
        self, prd_validator, temp_prd_file
    ):
        """Test no warning when 3+ numbered requirements present."""
        content = """# PRD

## Functional Requirements

- **FR-001**: System MUST do X
- **FR-002**: System MUST do Y
- **FR-003**: System MUST do Z
- **FR-004**: System MUST do W
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        fr_warnings = [
            w for w in result.warnings if "functional requirements" in w.lower()
        ]
        assert len(fr_warnings) == 0


class TestPRDValidatorSuccessMetrics:
    """Test success metrics validation."""

    def test_warning_if_no_numbered_success_metrics(self, prd_validator, temp_prd_file):
        """Test warning if success metrics aren't numbered."""
        content = """# PRD

## Success Metrics

- Users will be happy
- System will be fast
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        assert "no numbered metrics" in result.warnings[0]

    def test_warning_if_too_few_success_metrics(self, prd_validator, temp_prd_file):
        """Test warning if only one success metric."""
        content = """# PRD

## Success Metrics

- **SM-001**: 95% user satisfaction
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        assert "Only 1 success metrics" in result.warnings[0]

    def test_no_warning_if_multiple_success_metrics(self, prd_validator, temp_prd_file):
        """Test no warning when 2+ success metrics present."""
        content = """# PRD

## Success Metrics

- **SM-001**: 95% user satisfaction
- **SM-002**: Response time under 200ms
- **SM-003**: Zero security incidents
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        sm_warnings = [w for w in result.warnings if "success metrics" in w.lower()]
        assert len(sm_warnings) == 0


class TestPRDValidatorPlaceholders:
    """Test placeholder content detection."""

    def test_warning_for_placeholder_feature_name(self, prd_validator, temp_prd_file):
        """Test warning when [FEATURE NAME] placeholder is present."""
        content = """# PRD: [FEATURE NAME]

## Executive Summary

Some content.
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert len(result.warnings) >= 1
        placeholder_warnings = [
            w for w in result.warnings if "placeholder" in w.lower()
        ]
        assert len(placeholder_warnings) > 0

    def test_warning_for_placeholder_dates(self, prd_validator, temp_prd_file):
        """Test warning when [DATE] placeholder is present."""
        content = """# PRD

**Created**: [DATE]

## Executive Summary

Content
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        placeholder_warnings = [
            w for w in result.warnings if "placeholder" in w.lower()
        ]
        assert len(placeholder_warnings) > 0

    def test_warning_for_instruction_placeholders(self, prd_validator, temp_prd_file):
        """Test warning for instructional placeholders like [Provide a...]."""
        content = """# PRD

## Executive Summary

[Provide a 2-3 paragraph summary here]

## Problem Statement

[Describe the problem]
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        placeholder_warnings = [
            w for w in result.warnings if "placeholder" in w.lower()
        ]
        assert len(placeholder_warnings) >= 1

    def test_no_warning_when_placeholders_replaced(self, prd_validator, temp_prd_file):
        """Test no placeholder warnings when content is filled in."""
        content = """# PRD: User Authentication

**Created**: 2025-11-30

## Executive Summary

This feature enables secure user authentication using OAuth 2.0.
Users will be able to log in with email/password or social providers.
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        placeholder_warnings = [
            w for w in result.warnings if "placeholder" in w.lower()
        ]
        assert len(placeholder_warnings) == 0


class TestValidationResult:
    """Test ValidationResult dataclass behavior."""

    def test_validation_result_bool_conversion(self):
        """Test ValidationResult can be used in boolean context."""
        valid_result = ValidationResult(
            valid=True, errors=[], warnings=[], artifact_path="/path/to/prd.md"
        )
        invalid_result = ValidationResult(
            valid=False, errors=["error"], warnings=[], artifact_path="/path/to/prd.md"
        )

        assert bool(valid_result) is True
        assert bool(invalid_result) is False

    def test_add_error_marks_invalid(self):
        """Test add_error() sets valid to False."""
        result = ValidationResult(
            valid=True, errors=[], warnings=[], artifact_path="/path"
        )

        result.add_error("Something went wrong")

        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Something went wrong"

    def test_add_warning_does_not_invalidate(self):
        """Test add_warning() doesn't change valid status."""
        result = ValidationResult(
            valid=True, errors=[], warnings=[], artifact_path="/path"
        )

        result.add_warning("Consider improving X")

        assert result.valid is True
        assert len(result.warnings) == 1


class TestPRDValidatorIntegration:
    """Integration tests with complete PRD documents."""

    def test_minimal_valid_prd(self, prd_validator, temp_prd_file):
        """Test a minimal but valid PRD passes validation."""
        content = """# Product Requirements Document: Minimal Feature

## Executive Summary
Summary content.

## Problem Statement
Problem content.

## User Stories
### User Story 1 - Feature (Priority: P1)
**Acceptance Criteria**:
1. **Given** state, **When** action, **Then** outcome

## Functional Requirements
- **FR-001**: Requirement 1
- **FR-002**: Requirement 2
- **FR-003**: Requirement 3

## Non-Functional Requirements
- **NFR-001**: Performance requirement

## Success Metrics
- **SM-001**: Metric 1
- **SM-002**: Metric 2

## Dependencies
None

## Risks and Mitigations
None identified

## Out of Scope
Not applicable
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert result.valid
        assert len(result.errors) == 0

    def test_comprehensive_prd_with_all_features(self, prd_validator, temp_prd_file):
        """Test a comprehensive PRD with all features."""
        content = """# Product Requirements Document: User Authentication

**Feature**: user-authentication
**Created**: 2025-11-30
**Status**: Draft
**Version**: 1.0

## Executive Summary

This feature implements secure user authentication using OAuth 2.0 and JWT tokens.
It addresses the critical need for secure access control in our application.
Expected impact includes improved security posture and better user experience.

## Problem Statement

### Current State
Users currently have no way to securely access the application.

### Desired State
Secure, seamless authentication with multiple providers.

### Impact if Not Addressed
Security vulnerabilities and poor user experience.

## User Stories

### User Story 1 - Email Login (Priority: P1)

**As a** user
**I want** to log in with email and password
**So that** I can securely access my account

**Why this priority**: Core authentication flow

**Independent Test**: Can be tested by attempting login with valid credentials

**Acceptance Criteria**:

1. **Given** valid credentials, **When** user submits login form, **Then** user is authenticated
2. **Given** invalid credentials, **When** user submits login form, **Then** error is displayed
3. **Given** successful auth, **When** user navigates, **Then** session persists

### User Story 2 - Social Login (Priority: P2)

**As a** user
**I want** to log in with Google or GitHub
**So that** I don't need to create another password

**Acceptance Criteria**:

1. **Given** user clicks Google, **When** OAuth completes, **Then** user is authenticated

## Functional Requirements

### Core Functionality
- **FR-001**: System MUST authenticate users via email/password
- **FR-002**: System MUST support OAuth 2.0 providers (Google, GitHub)
- **FR-003**: System MUST issue JWT tokens upon successful authentication
- **FR-004**: System MUST validate JWT tokens on protected endpoints
- **FR-005**: System MUST implement refresh token rotation

### Security
- **FR-006**: System MUST hash passwords using bcrypt with salt
- **FR-007**: System MUST enforce HTTPS for all auth endpoints

## Non-Functional Requirements

### Performance
- **NFR-001**: Authentication MUST complete within 2 seconds
- **NFR-002**: System MUST handle 1000 concurrent auth requests

### Security
- **NFR-003**: Passwords MUST be hashed with bcrypt (cost factor 12)
- **NFR-004**: JWT tokens MUST expire after 15 minutes
- **NFR-005**: Refresh tokens MUST expire after 7 days

## Success Metrics

### User Adoption
- **SM-001**: 90% of users successfully authenticate on first attempt
- **SM-002**: Login completion time under 2 seconds for 95th percentile

### Security
- **SM-003**: Zero credential leaks in first 6 months
- **SM-004**: Brute force attacks blocked within 3 failed attempts

## Dependencies

### Technical
- **DEP-001**: Requires PostgreSQL database v14+
- **DEP-002**: Requires Redis for session storage

### External Services
- **DEP-003**: Google OAuth 2.0 API access
- **DEP-004**: GitHub OAuth App credentials

## Risks and Mitigations

| Risk ID | Risk Description | Impact | Probability | Mitigation Strategy |
|---------|------------------|--------|-------------|---------------------|
| RISK-001 | OAuth provider outage | High | Low | Implement email/password fallback |
| RISK-002 | JWT token leakage | High | Medium | Short token expiry + refresh rotation |
| RISK-003 | Brute force attacks | Medium | High | Rate limiting + account lockout |

## Out of Scope

The following are explicitly OUT OF SCOPE:

- Multi-factor authentication (MFA) - deferred to v2.0
- Passwordless authentication (magic links)
- Enterprise SSO (SAML)
- Biometric authentication
"""
        temp_prd_file.write_text(content)

        result = prd_validator.validate(temp_prd_file)

        assert result.valid
        assert len(result.errors) == 0
        # May have some warnings but should be valid
