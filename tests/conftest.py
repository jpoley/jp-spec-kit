"""Pytest configuration and fixtures for jp-spec-kit tests.

IMPORTANT: All test fixtures use tmp_path for isolation - files are auto-cleaned after tests.
Mock task DESCRIPTIONS contain "MOCK" to distinguish from real tasks.
Task IDs use T001 format for parser regex compatibility.
"""

import pytest
from textwrap import dedent


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing.

    Uses pytest tmp_path - automatically cleaned up after test.
    """
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def mock_tasks_content():
    """MOCK tasks.md content for testing task parsing.

    Task IDs use T001 format (parser regex requirement).
    All descriptions contain MOCK to identify as test data.
    """
    return dedent("""
        # MOCK Tasks for Testing

        ## Phase 1: MOCK Setup

        - [ ] T001 MOCK setup task
        - [ ] T002 [P] MOCK parallel task
        - [ ] T003 MOCK config task

        ## Phase 2: MOCK Foundational

        - [ ] T004 MOCK base task
        - [ ] T005 [P] [P1] MOCK utility task
        - [x] T006 MOCK completed task

        ## Phase 3: MOCK User Story 1

        - [ ] T007 [US1] MOCK auth task
        - [ ] T008 [US1] MOCK form task
        - [ ] T009 [US1] MOCK session task

        ## Phase 4: MOCK User Story 2

        - [ ] T010 [US2] MOCK component task
        - [ ] T011 [US2] [P] MOCK viz task
    """).strip()


# Keep old name as alias for backward compatibility during transition
@pytest.fixture
def sample_tasks_content(mock_tasks_content):
    """Alias for mock_tasks_content (deprecated, use mock_tasks_content)."""
    return mock_tasks_content


@pytest.fixture
def mock_tasks_file(temp_project_dir, mock_tasks_content):
    """Create a MOCK tasks.md file in temp directory.

    File is automatically cleaned up after test via tmp_path.
    Uses 'tasks.md' filename for compatibility with code that expects it.
    """
    tasks_file = temp_project_dir / "tasks.md"
    tasks_file.write_text(mock_tasks_content)
    return tasks_file


# Keep old name as alias for backward compatibility
@pytest.fixture
def sample_tasks_file(mock_tasks_file):
    """Alias for mock_tasks_file (deprecated, use mock_tasks_file)."""
    return mock_tasks_file


@pytest.fixture
def mock_spec_content():
    """MOCK spec.md content for testing."""
    return dedent("""
        # MOCK Feature Specification

        ## User Story 1

        As a test user, I want MOCK authentication for testing.

        ## User Story 2

        As a test user, I want MOCK dashboard for testing.
    """).strip()


# Alias for compatibility
@pytest.fixture
def sample_spec_content(mock_spec_content):
    """Alias for mock_spec_content."""
    return mock_spec_content


@pytest.fixture
def mock_spec_file(temp_project_dir, mock_spec_content):
    """Create a MOCK spec.md file.

    Uses 'spec.md' filename for compatibility with code that expects it.
    """
    spec_file = temp_project_dir / "spec.md"
    spec_file.write_text(mock_spec_content)
    return spec_file


@pytest.fixture
def sample_spec_file(mock_spec_file):
    """Alias for mock_spec_file."""
    return mock_spec_file


@pytest.fixture
def mock_plan_content():
    """MOCK plan.md content for testing."""
    return dedent("""
        # MOCK Implementation Plan

        ## Tech Stack

        - Python 3.11+
        - MockFramework
        - MockDB

        ## Project Structure

        - src/
        - tests/
        - docs/
    """).strip()


@pytest.fixture
def sample_plan_content(mock_plan_content):
    """Alias for mock_plan_content."""
    return mock_plan_content


@pytest.fixture
def mock_plan_file(temp_project_dir, mock_plan_content):
    """Create a MOCK plan.md file.

    Uses 'plan.md' filename for compatibility with code that expects it.
    """
    plan_file = temp_project_dir / "plan.md"
    plan_file.write_text(mock_plan_content)
    return plan_file


@pytest.fixture
def sample_plan_file(mock_plan_file):
    """Alias for mock_plan_file."""
    return mock_plan_file


@pytest.fixture
def backlog_dir(temp_project_dir):
    """Create MOCK backlog directory in temp path.

    Automatically cleaned up after test via tmp_path.
    """
    backlog = temp_project_dir / "backlog"
    backlog.mkdir()
    return backlog


@pytest.fixture
def mock_invalid_tasks_content():
    """MOCK invalid tasks.md content for error testing."""
    return dedent("""
        # MOCK Tasks with Issues

        ## Phase 1

        - [ ] T901 Valid MOCK task
        - [ ] INVALID No task ID
        - [ ] T902 MOCK task depends on T999
    """).strip()


@pytest.fixture
def invalid_tasks_content(mock_invalid_tasks_content):
    """Alias for mock_invalid_tasks_content."""
    return mock_invalid_tasks_content


@pytest.fixture
def mock_circular_dependency_content():
    """MOCK tasks content with circular dependencies."""
    return dedent("""
        # MOCK Tasks with Circular Dependencies

        ## Phase 1

        - [ ] T801 MOCK Task A
        - [ ] T802 MOCK Task B (depends on T803)
        - [ ] T803 MOCK Task C (depends on T802)
    """).strip()


@pytest.fixture
def circular_dependency_content(mock_circular_dependency_content):
    """Alias for mock_circular_dependency_content."""
    return mock_circular_dependency_content


@pytest.fixture
def empty_tasks_content():
    """Empty tasks.md content."""
    return "# Empty MOCK Tasks\n\nNo tasks here."


# Security Fixer Test Fixtures


class MockConfirmationHandler:
    """Mock confirmation handler for testing patch application.

    This is a shared test fixture used across multiple test modules
    to avoid importing test utilities from other test files.
    """

    def __init__(self, always_confirm: bool = True):
        """Initialize with default confirmation behavior.

        Args:
            always_confirm: If True, always confirm patches. If False, always reject.
        """
        self.always_confirm = always_confirm
        self.calls: list[tuple] = []  # List of (patch, confidence) tuples

    def confirm_patch(self, patch, confidence: float) -> bool:
        """Record call and return configured response.

        Args:
            patch: The patch to confirm.
            confidence: Confidence score (0.0-1.0).

        Returns:
            The configured confirmation response.
        """
        self.calls.append((patch, confidence))
        return self.always_confirm


@pytest.fixture
def mock_confirmation_handler():
    """Fixture providing a MockConfirmationHandler that always confirms."""
    return MockConfirmationHandler(always_confirm=True)


@pytest.fixture
def mock_rejection_handler():
    """Fixture providing a MockConfirmationHandler that always rejects."""
    return MockConfirmationHandler(always_confirm=False)
