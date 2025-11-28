"""Pytest configuration and fixtures for jp-spec-kit tests."""

import pytest
from textwrap import dedent


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def sample_tasks_content():
    """Sample tasks.md content for testing."""
    return dedent("""
        # Tasks for Feature X

        ## Phase 1: Setup

        - [ ] T001 Initialize project structure
        - [ ] T002 [P] Set up testing framework in tests/ directory
        - [ ] T003 Configure linting tools

        ## Phase 2: Foundational

        - [ ] T004 Create base classes in src/base.py
        - [ ] T005 [P] [P1] Implement utility functions in src/utils.py
        - [x] T006 Add logging configuration

        ## Phase 3: User Story 1

        - [ ] T007 [US1] Implement user authentication in auth.py
        - [ ] T008 [US1] Create login form
        - [ ] T009 [US1] Add session management

        ## Phase 4: User Story 2

        - [ ] T010 [US2] Build dashboard component
        - [ ] T011 [US2] [P] Add data visualization
    """).strip()


@pytest.fixture
def sample_tasks_file(temp_project_dir, sample_tasks_content):
    """Create a sample tasks.md file."""
    tasks_file = temp_project_dir / "tasks.md"
    tasks_file.write_text(sample_tasks_content)
    return tasks_file


@pytest.fixture
def sample_spec_content():
    """Sample spec.md content for testing."""
    return dedent("""
        # Feature X Specification

        ## User Story 1

        As a user, I want to authenticate so that I can access my account.

        ## User Story 2

        As a user, I want to view my dashboard so that I can see my data.
    """).strip()


@pytest.fixture
def sample_spec_file(temp_project_dir, sample_spec_content):
    """Create a sample spec.md file."""
    spec_file = temp_project_dir / "spec.md"
    spec_file.write_text(sample_spec_content)
    return spec_file


@pytest.fixture
def sample_plan_content():
    """Sample plan.md content for testing."""
    return dedent("""
        # Implementation Plan

        ## Tech Stack

        - Python 3.11+
        - FastAPI
        - PostgreSQL

        ## Project Structure

        - src/
        - tests/
        - docs/

        ## Libraries

        - pydantic
        - sqlalchemy
    """).strip()


@pytest.fixture
def sample_plan_file(temp_project_dir, sample_plan_content):
    """Create a sample plan.md file."""
    plan_file = temp_project_dir / "plan.md"
    plan_file.write_text(sample_plan_content)
    return plan_file


@pytest.fixture
def backlog_dir(temp_project_dir):
    """Create backlog directory."""
    backlog = temp_project_dir / "backlog"
    backlog.mkdir()
    return backlog


@pytest.fixture
def invalid_tasks_content():
    """Invalid tasks.md content for error testing."""
    return dedent("""
        # Tasks with Issues

        ## Phase 1

        - [ ] T001 Valid task
        - [ ] INVALID No task ID
        - [ ] T002 Task depends on T999
    """).strip()


@pytest.fixture
def circular_dependency_content():
    """Tasks content with circular dependencies."""
    return dedent("""
        # Tasks with Circular Dependencies

        ## Phase 1

        - [ ] T001 Task A
        - [ ] T002 Task B (depends on T003)
        - [ ] T003 Task C (depends on T002)
    """).strip()


@pytest.fixture
def empty_tasks_content():
    """Empty tasks.md content."""
    return "# Empty Tasks\n\nNo tasks here."
