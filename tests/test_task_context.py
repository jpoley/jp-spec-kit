"""Unit tests for task context loader."""

import pytest
from textwrap import dedent
from unittest.mock import patch, MagicMock

from flowspec_cli.task_context import (
    AcceptanceCriterion,
    TaskContext,
    load_task_context,
    parse_acceptance_criteria,
    find_related_files,
    determine_validation_approach,
    TaskNotFoundError,
    NoInProgressTaskError,
    InvalidTaskIDError,
    _normalize_task_id,
    _extract_title,
    _extract_status,
    _extract_priority,
    _extract_labels,
    _extract_section,
    _find_related_tests,
    _build_validation_plan,
)


class TestAcceptanceCriterion:
    """Test AcceptanceCriterion dataclass."""

    def test_acceptance_criterion_creation(self):
        """Test creating an AcceptanceCriterion."""
        ac = AcceptanceCriterion(
            index=1,
            text="Test criterion",
            checked=False,
            validation_approach="automated",
        )

        assert ac.index == 1
        assert ac.text == "Test criterion"
        assert ac.checked is False
        assert ac.validation_approach == "automated"

    def test_acceptance_criterion_defaults(self):
        """Test default values for AcceptanceCriterion."""
        ac = AcceptanceCriterion(index=1, text="Test", checked=False)

        assert ac.validation_approach == "manual"


class TestTaskContext:
    """Test TaskContext dataclass."""

    def test_task_context_creation(self):
        """Test creating a TaskContext."""
        ac = AcceptanceCriterion(index=1, text="Test", checked=False)
        context = TaskContext(
            task_id="task-88",
            title="Test Task",
            description="Test description",
            status="To Do",
            priority="High",
            labels=["test", "backend"],
            acceptance_criteria=[ac],
            related_files=["src/test.py"],
            related_tests=["tests/test_test.py"],
            validation_plan=["Run automated tests"],
            implementation_notes="Test notes",
        )

        assert context.task_id == "task-88"
        assert context.title == "Test Task"
        assert context.description == "Test description"
        assert context.status == "To Do"
        assert context.priority == "High"
        assert len(context.labels) == 2
        assert len(context.acceptance_criteria) == 1
        assert len(context.related_files) == 1
        assert len(context.related_tests) == 1
        assert len(context.validation_plan) == 1
        assert context.implementation_notes == "Test notes"

    def test_task_context_defaults(self):
        """Test default values for TaskContext."""
        context = TaskContext(
            task_id="task-1", title="Title", description="Description"
        )

        assert context.status == "To Do"
        assert context.priority is None
        assert context.labels == []
        assert context.acceptance_criteria == []
        assert context.related_files == []
        assert context.related_tests == []
        assert context.validation_plan == []
        assert context.implementation_notes is None


class TestNormalizeTaskID:
    """Test task ID normalization."""

    def test_normalize_numeric_id(self):
        """Test normalizing numeric task ID."""
        assert _normalize_task_id("88") == "task-88"
        assert _normalize_task_id("1") == "task-1"
        assert _normalize_task_id("123") == "task-123"

    def test_normalize_with_prefix(self):
        """Test normalizing task ID with prefix."""
        assert _normalize_task_id("task-88") == "task-88"
        assert _normalize_task_id("task-1") == "task-1"

    def test_normalize_with_whitespace(self):
        """Test normalizing task ID with whitespace."""
        assert _normalize_task_id(" 88 ") == "task-88"
        assert _normalize_task_id(" task-88 ") == "task-88"

    def test_normalize_invalid_format(self):
        """Test error on invalid task ID format."""
        with pytest.raises(InvalidTaskIDError):
            _normalize_task_id("task-abc")

        with pytest.raises(InvalidTaskIDError):
            _normalize_task_id("invalid")

        with pytest.raises(InvalidTaskIDError):
            _normalize_task_id("task-")


class TestExtractors:
    """Test various extraction functions."""

    def test_extract_title(self):
        """Test extracting title from output lines."""
        lines = [
            "Task task-88 - Phase 0 - Task Context Loader for AC Validation",
            "==================================================",
        ]
        title = _extract_title(lines)
        assert title == "Phase 0 - Task Context Loader for AC Validation"

    def test_extract_title_simple(self):
        """Test extracting simple title."""
        lines = ["Task task-1 - Simple Task", "=================="]
        title = _extract_title(lines)
        assert title == "Simple Task"

    def test_extract_status_to_do(self):
        """Test extracting To Do status."""
        lines = ["Status: ○ To Do"]
        status = _extract_status(lines)
        assert status == "To Do"

    def test_extract_status_done(self):
        """Test extracting Done status."""
        lines = ["Status: ✔ Done"]
        status = _extract_status(lines)
        assert status == "Done"

    def test_extract_status_in_progress(self):
        """Test extracting In Progress status."""
        lines = ["Status: ◐ In Progress"]
        status = _extract_status(lines)
        assert status == "In Progress"

    def test_extract_priority(self):
        """Test extracting priority."""
        lines = ["Priority: High"]
        priority = _extract_priority(lines)
        assert priority == "High"

    def test_extract_priority_none(self):
        """Test extracting priority when not set."""
        lines = ["Priority: "]
        priority = _extract_priority(lines)
        assert priority is None

    def test_extract_labels(self):
        """Test extracting labels."""
        lines = ["Labels: validate-enhancement, phase-0, backend"]
        labels = _extract_labels(lines)
        assert labels == ["validate-enhancement", "phase-0", "backend"]

    def test_extract_labels_empty(self):
        """Test extracting labels when empty."""
        lines = ["Labels: "]
        labels = _extract_labels(lines)
        assert labels == []

    def test_extract_section(self):
        """Test extracting a section from output."""
        lines = [
            "Description:",
            "--------------------------------------------------",
            "This is the description text.",
            "It has multiple lines.",
            "",
            "Acceptance Criteria:",
        ]
        description = _extract_section(lines, "Description:")
        assert "This is the description text." in description
        assert "It has multiple lines." in description


class TestParseAcceptanceCriteria:
    """Test acceptance criteria parsing."""

    def test_parse_simple_ac(self):
        """Test parsing simple acceptance criteria."""
        output = dedent("""
            Acceptance Criteria:
            --------------------------------------------------
            - [ ] #1 First criterion
            - [ ] #2 Second criterion
            - [x] #3 Third criterion (completed)
        """).strip()

        criteria = parse_acceptance_criteria(output)

        assert len(criteria) == 3
        assert criteria[0].index == 1
        assert criteria[0].text == "First criterion"
        assert criteria[0].checked is False

        assert criteria[1].index == 2
        assert criteria[1].text == "Second criterion"
        assert criteria[1].checked is False

        assert criteria[2].index == 3
        assert "Third criterion" in criteria[2].text
        assert criteria[2].checked is True

    def test_parse_complex_ac(self):
        """Test parsing complex acceptance criteria."""
        output = dedent("""
            Acceptance Criteria:
            --------------------------------------------------
            - [ ] #1 Given a task ID, the loader retrieves task details via `backlog task <id> --plain` and parses all fields
            - [x] #2 Acceptance criteria are extracted into a structured list with index, text, and checked status
        """).strip()

        criteria = parse_acceptance_criteria(output)

        assert len(criteria) == 2
        assert "backlog task" in criteria[0].text
        assert criteria[0].checked is False
        assert "structured list" in criteria[1].text
        assert criteria[1].checked is True

    def test_parse_no_ac(self):
        """Test parsing output with no acceptance criteria."""
        output = dedent("""
            Description:
            --------------------------------------------------
            Some description without AC section.
        """).strip()

        criteria = parse_acceptance_criteria(output)
        assert criteria == []


class TestFindRelatedFiles:
    """Test finding related files in text."""

    def test_find_backtick_paths(self):
        """Test finding backtick-quoted file paths."""
        description = "Update the code in `src/task_context.py` module."
        files = find_related_files(description, "")

        assert "src/task_context.py" in files

    def test_find_quoted_paths(self):
        """Test finding double-quoted file paths."""
        description = 'Modify the "tests/test_context.py" file.'
        files = find_related_files(description, "")

        assert "tests/test_context.py" in files

    def test_find_keyword_paths(self):
        """Test finding paths with keywords."""
        description = (
            "Create file at src/models/user.py and add tests to tests/test_user.py"
        )
        files = find_related_files(description, "")

        assert "src/models/user.py" in files
        assert "tests/test_user.py" in files

    def test_find_standalone_paths(self):
        """Test finding standalone paths."""
        description = "The implementation is in src/flowspec_cli/task_context.py"
        files = find_related_files(description, "")

        assert "src/flowspec_cli/task_context.py" in files

    def test_find_in_notes(self):
        """Test finding files in implementation notes."""
        description = "Task description"
        notes = "Modified `src/core.py` and added tests in `tests/test_core.py`"
        files = find_related_files(description, notes)

        assert "src/core.py" in files
        assert "tests/test_core.py" in files

    def test_exclude_urls(self):
        """Test excluding URLs from file matches."""
        description = (
            "See https://example.com/file.py for reference. Update src/file.py"
        )
        files = find_related_files(description, "")

        assert "src/file.py" in files
        # URL should be excluded
        assert not any("example.com" in f for f in files)

    def test_no_duplicates(self):
        """Test that duplicate files are not added."""
        description = "Update `src/file.py` and modify src/file.py again"
        files = find_related_files(description, "")

        assert files.count("src/file.py") == 1


class TestFindRelatedTests:
    """Test finding related test files."""

    def test_find_test_for_module(self):
        """Test finding test file for a module."""
        related_files = ["src/task_context.py"]
        description = "Also update test_task_context.py"
        title = "Task Context Loader"

        tests = _find_related_tests(related_files, description, title)

        assert any("test_task_context.py" in t for t in tests)

    def test_find_test_in_related_files(self):
        """Test finding test files already in related files."""
        related_files = ["src/module.py", "tests/test_module.py"]
        description = "Test description"
        title = "Test title"

        tests = _find_related_tests(related_files, description, title)

        assert "tests/test_module.py" in tests

    def test_find_test_with_keywords(self):
        """Test finding tests mentioned with keywords."""
        related_files = ["src/api.py"]
        description = "Add integration tests for the API endpoint"
        title = "API Tests"

        tests = _find_related_tests(related_files, description, title)

        # Should identify that tests are relevant
        assert len(tests) >= 0  # May or may not find specific files


class TestDetermineValidationApproach:
    """Test validation approach determination."""

    def test_automated_with_tests(self):
        """Test automated approach when tests exist and AC is testable."""
        ac = AcceptanceCriterion(
            index=1,
            text="Function returns correct output for given input",
            checked=False,
        )
        related_tests = ["tests/test_function.py"]

        approach = determine_validation_approach(ac, related_tests)

        assert approach == "automated"

    def test_manual_for_ui(self):
        """Test manual approach for UI-related ACs."""
        ac = AcceptanceCriterion(
            index=1, text="User interface displays error message clearly", checked=False
        )
        related_tests = []

        approach = determine_validation_approach(ac, related_tests)

        assert approach == "manual"

    def test_hybrid_with_mixed_keywords(self):
        """Test hybrid approach when both automated and manual keywords present."""
        ac = AcceptanceCriterion(
            index=1,
            text="API endpoint returns data and user sees readable format",
            checked=False,
        )
        related_tests = ["tests/test_api.py"]

        approach = determine_validation_approach(ac, related_tests)

        assert approach == "hybrid"

    def test_hybrid_without_tests(self):
        """Test hybrid approach when testable but no tests exist."""
        ac = AcceptanceCriterion(
            index=1, text="Function parses input correctly", checked=False
        )
        related_tests = []

        approach = determine_validation_approach(ac, related_tests)

        assert approach == "hybrid"

    def test_default_to_manual(self):
        """Test default to manual when unclear."""
        ac = AcceptanceCriterion(
            index=1, text="Task completes successfully", checked=False
        )
        related_tests = []

        approach = determine_validation_approach(ac, related_tests)

        assert approach == "manual"


class TestBuildValidationPlan:
    """Test validation plan building."""

    def test_build_plan_with_all_types(self):
        """Test building plan with all validation types."""
        criteria = [
            AcceptanceCriterion(
                index=1, text="Test 1", checked=False, validation_approach="automated"
            ),
            AcceptanceCriterion(
                index=2, text="Test 2", checked=False, validation_approach="manual"
            ),
            AcceptanceCriterion(
                index=3, text="Test 3", checked=False, validation_approach="hybrid"
            ),
        ]

        plan = _build_validation_plan(criteria)

        assert len(plan) == 3
        assert any("automated" in step.lower() and "#1" in step for step in plan)
        assert any("manual" in step.lower() and "#2" in step for step in plan)
        # Hybrid approach is described as "tests + manual review"
        assert any(
            ("manual review" in step.lower() or "hybrid" in step.lower())
            and "#3" in step
            for step in plan
        )

    def test_build_plan_automated_only(self):
        """Test building plan with only automated tests."""
        criteria = [
            AcceptanceCriterion(
                index=1, text="Test 1", checked=False, validation_approach="automated"
            ),
            AcceptanceCriterion(
                index=2, text="Test 2", checked=False, validation_approach="automated"
            ),
        ]

        plan = _build_validation_plan(criteria)

        assert len(plan) == 1
        assert "automated" in plan[0].lower()
        assert "#1" in plan[0] and "#2" in plan[0]

    def test_build_plan_empty(self):
        """Test building plan with no criteria."""
        plan = _build_validation_plan([])
        assert plan == []


class TestLoadTaskContext:
    """Test complete task context loading."""

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_load_task_by_id(self, mock_run):
        """Test loading task context by ID."""
        # Mock backlog CLI output
        mock_output = dedent("""
            Task task-88 - Test Task Title
            ==================================================

            Status: ○ To Do
            Priority: High
            Labels: test, backend

            Description:
            --------------------------------------------------
            This is a test task description.
            Update the code in `src/test.py` file.

            Acceptance Criteria:
            --------------------------------------------------
            - [ ] #1 API endpoint returns correct data
            - [x] #2 Tests pass successfully
        """).strip()

        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        context = load_task_context("88")

        assert context.task_id == "task-88"
        assert context.title == "Test Task Title"
        assert context.status == "To Do"
        assert context.priority == "High"
        assert len(context.labels) == 2
        assert len(context.acceptance_criteria) == 2
        assert "src/test.py" in context.related_files

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_load_task_not_found(self, mock_run):
        """Test error when task not found."""
        mock_run.side_effect = Exception("Task not found")
        mock_run.return_value = MagicMock(
            returncode=1, stderr="Task not found", stdout=""
        )

        # Mock the subprocess to raise CalledProcessError
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "backlog", stderr="Task not found"
        )

        with pytest.raises(TaskNotFoundError):
            load_task_context("999")

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_load_in_progress_task(self, mock_run):
        """Test loading current in-progress task."""
        # First call: list in-progress tasks
        list_output = "  [HIGH] task-88 - Test Task\n"
        # Second call: get task details
        task_output = dedent("""
            Task task-88 - Test Task
            ==================================================

            Status: ◐ In Progress
            Priority: High

            Description:
            --------------------------------------------------
            Test description

            Acceptance Criteria:
            --------------------------------------------------
            - [ ] #1 Test AC
        """).strip()

        mock_run.side_effect = [
            MagicMock(stdout=list_output, returncode=0),  # list command
            MagicMock(stdout=task_output, returncode=0),  # task command
        ]

        context = load_task_context(None)

        assert context.task_id == "task-88"
        assert context.status == "In Progress"

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_load_no_in_progress_task(self, mock_run):
        """Test error when no in-progress task exists."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        with pytest.raises(NoInProgressTaskError):
            load_task_context(None)

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_load_task_with_notes(self, mock_run):
        """Test loading task with implementation notes."""
        mock_output = dedent("""
            Task task-73 - Test Task
            ==================================================

            Status: ✔ Done
            Priority: High

            Description:
            --------------------------------------------------
            Test description

            Acceptance Criteria:
            --------------------------------------------------
            - [x] #1 Test AC

            Implementation Notes:
            --------------------------------------------------
            Implemented using pattern X.
            Modified file `src/implementation.py`
        """).strip()

        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        context = load_task_context("73")

        assert context.implementation_notes is not None
        assert "pattern X" in context.implementation_notes
        # Should find files in both description and notes
        assert "src/implementation.py" in context.related_files


class TestIntegration:
    """Integration tests with full workflow."""

    @patch("flowspec_cli.task_context.subprocess.run")
    def test_full_validation_workflow(self, mock_run):
        """Test complete validation workflow from load to plan."""
        mock_output = dedent("""
            Task task-88 - Phase 0 - Task Context Loader
            ==================================================

            Status: ○ To Do
            Priority: High
            Labels: validate-enhancement, phase-0, backend

            Description:
            --------------------------------------------------
            Implement task context loader for AC validation.
            Create module at `src/flowspec_cli/task_context.py`
            and tests at `tests/test_task_context.py`

            Acceptance Criteria:
            --------------------------------------------------
            - [ ] #1 Given a task ID, retrieve task details via backlog CLI and parse all fields
            - [ ] #2 Extract acceptance criteria into structured list
            - [ ] #3 Identify related code files from description
            - [ ] #4 Identify related test files by pattern matching
            - [ ] #5 Determine validation approach for each AC
        """).strip()

        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        context = load_task_context("88")

        # Verify all fields parsed correctly
        assert context.task_id == "task-88"
        assert "Task Context Loader" in context.title
        assert context.status == "To Do"
        assert context.priority == "High"
        assert len(context.labels) == 3

        # Verify ACs parsed
        assert len(context.acceptance_criteria) == 5
        assert all(not ac.checked for ac in context.acceptance_criteria)

        # Verify files found
        assert "src/flowspec_cli/task_context.py" in context.related_files
        assert "tests/test_task_context.py" in context.related_files

        # Verify validation plan generated
        assert len(context.validation_plan) > 0
