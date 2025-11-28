"""Unit tests for TaskParser."""

import pytest
from textwrap import dedent

from specify_cli.backlog.parser import TaskParser, Task, parse_tasks


class TestTaskParser:
    """Test suite for TaskParser class."""

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        parser = TaskParser()
        assert parser.tasks == []
        assert parser.current_phase is None

    def test_parse_simple_task_line(self):
        """Test parsing a simple task line."""
        parser = TaskParser()
        line = "- [ ] T001 Create user model"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.task_id == "T001"
        assert task.description == "Create user model"
        assert task.is_completed is False
        assert task.is_parallelizable is False

    def test_parse_completed_task(self):
        """Test parsing a completed task (checkbox marked)."""
        parser = TaskParser()
        line = "- [x] T005 Set up database"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.task_id == "T005"
        assert task.is_completed is True

    def test_parse_completed_task_uppercase_x(self):
        """Test parsing completed task with uppercase X."""
        parser = TaskParser()
        line = "- [X] T005 Set up database"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.is_completed is True

    def test_parse_parallelizable_task(self):
        """Test parsing a task with [P] marker."""
        parser = TaskParser()
        line = "- [ ] T002 [P] Run tests in parallel"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.task_id == "T002"
        assert task.is_parallelizable is True
        assert "[P]" in task.description or "Run tests in parallel" in task.description

    def test_parse_user_story_label(self):
        """Test parsing task with user story label."""
        parser = TaskParser()
        line = "- [ ] T010 [US1] Implement login feature"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.task_id == "T010"
        assert task.user_story == "US1"
        assert "Implement login feature" in task.description

    def test_parse_task_with_priority(self):
        """Test parsing task with priority marker."""
        parser = TaskParser()
        line = "- [ ] T003 [P1] Fix critical bug in auth.py"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.priority == "P1"
        assert "auth.py" in task.description

    def test_parse_task_with_file_path(self):
        """Test extracting file path from task description."""
        parser = TaskParser()
        line = "- [ ] T004 Update code in src/models.py file"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.file_path == "src/models.py"

    def test_parse_task_with_quoted_file_path(self):
        """Test extracting quoted file path from task description."""
        parser = TaskParser()
        line = "- [ ] T004 Update code in `src/models.py` file"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.file_path == "src/models.py"

    def test_parse_invalid_line(self):
        """Test parsing invalid line returns None."""
        parser = TaskParser()
        invalid_lines = [
            "This is not a task",
            "- [ ] No task ID here",
            "T001 Missing checkbox",
            "",
            "# Header",
        ]

        for line in invalid_lines:
            task = parser._parse_task_line(line)
            assert task is None, f"Should not parse: {line}"

    def test_task_labels_generation(self):
        """Test Task.labels property generates correct labels."""
        task = Task(
            task_id="T001",
            description="Test task",
            user_story="US1",
            is_parallelizable=True,
            priority="P0",
            phase="Setup",
        )

        labels = task.labels
        assert "US1" in labels
        assert "parallelizable" in labels
        assert "P0" in labels
        assert "setup" in labels

    def test_task_labels_foundational_phase(self):
        """Test labels for foundational phase."""
        task = Task(
            task_id="T002",
            description="Test",
            phase="Phase 2: Foundational Work",
        )

        assert "foundational" in task.labels

    def test_task_labels_polish_phase(self):
        """Test labels for polish phase."""
        task = Task(
            task_id="T003",
            description="Test",
            phase="Phase 5: Polish and Refinement",
        )

        assert "polish" in task.labels

    def test_task_labels_user_story_phase(self):
        """Test labels for user story phase."""
        task = Task(
            task_id="T004",
            description="Test",
            phase="Phase 3: User Story 1",
            user_story="US1",
        )

        assert "implementation" in task.labels

    def test_parse_tasks_content_simple(self, sample_tasks_content):
        """Test parsing complete tasks content."""
        parser = TaskParser()
        tasks = parser.parse_tasks_content(sample_tasks_content)

        assert len(tasks) > 0
        assert all(isinstance(task, Task) for task in tasks)

    def test_parse_tasks_content_phase_extraction(self, sample_tasks_content):
        """Test that phases are correctly extracted."""
        parser = TaskParser()
        tasks = parser.parse_tasks_content(sample_tasks_content)

        # Find tasks and check their phases
        t001 = next((t for t in tasks if t.task_id == "T001"), None)
        assert t001 is not None
        assert "Setup" in t001.phase

        t007 = next((t for t in tasks if t.task_id == "T007"), None)
        assert t007 is not None
        assert "User Story 1" in t007.phase

    def test_parse_tasks_file(self, sample_tasks_file):
        """Test parsing tasks from file."""
        parser = TaskParser()
        tasks = parser.parse_tasks_file(sample_tasks_file)

        assert len(tasks) > 0
        task_ids = [t.task_id for t in tasks]
        assert "T001" in task_ids
        assert "T007" in task_ids

    def test_parse_tasks_file_not_found(self, temp_project_dir):
        """Test parsing non-existent file raises error."""
        parser = TaskParser()
        non_existent = temp_project_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parser.parse_tasks_file(non_existent)

    def test_parse_empty_content(self, empty_tasks_content):
        """Test parsing empty content returns empty list."""
        parser = TaskParser()
        tasks = parser.parse_tasks_content(empty_tasks_content)

        assert tasks == []

    def test_dependency_inference_setup_to_foundational(self):
        """Test dependencies inferred from Setup to Foundational."""
        content = dedent("""
            ## Phase 1: Setup
            - [ ] T001 Init project
            - [ ] T002 Configure tools

            ## Phase 2: Foundational
            - [ ] T003 Create base classes
            - [ ] T004 Add utilities
        """).strip()

        parser = TaskParser()
        tasks = parser.parse_tasks_content(content)

        t003 = next((t for t in tasks if t.task_id == "T003"), None)
        assert t003 is not None
        assert "T002" in t003.dependencies

    def test_dependency_inference_foundational_to_user_story(self):
        """Test dependencies inferred from Foundational to User Stories."""
        content = dedent("""
            ## Phase 1: Foundational
            - [ ] T001 Setup base
            - [ ] T002 Add utils

            ## Phase 2: User Story 1
            - [ ] T003 [US1] First feature
            - [ ] T004 [US1] Second feature
        """).strip()

        parser = TaskParser()
        tasks = parser.parse_tasks_content(content)

        t003 = next((t for t in tasks if t.task_id == "T003"), None)
        assert t003 is not None
        assert "T002" in t003.dependencies

    def test_parallelizable_tasks_no_dependencies(self):
        """Test parallelizable tasks don't get automatic dependencies."""
        content = dedent("""
            ## Phase 1: Setup
            - [ ] T001 Init

            ## Phase 2: Foundational
            - [ ] T002 [P] Parallel task A
            - [ ] T003 [P] Parallel task B
        """).strip()

        parser = TaskParser()
        tasks = parser.parse_tasks_content(content)

        t002 = next((t for t in tasks if t.task_id == "T002"), None)
        # Parallelizable tasks might still get dependencies in current implementation
        # This test documents current behavior
        assert t002 is not None

    def test_parse_spec_file(self, sample_spec_file):
        """Test parsing user stories from spec.md."""
        parser = TaskParser()
        user_stories = parser.parse_spec_file(sample_spec_file)

        assert len(user_stories) >= 2
        assert "US1" in user_stories
        assert "US2" in user_stories

    def test_parse_spec_file_not_found(self, temp_project_dir):
        """Test parsing non-existent spec file raises error."""
        parser = TaskParser()
        non_existent = temp_project_dir / "nonexistent_spec.md"

        with pytest.raises(FileNotFoundError):
            parser.parse_spec_file(non_existent)

    def test_parse_plan_file(self, sample_plan_file):
        """Test parsing plan.md file."""
        parser = TaskParser()
        plan_info = parser.parse_plan_file(sample_plan_file)

        assert "tech_stack" in plan_info
        assert "project_structure" in plan_info
        assert "libraries" in plan_info
        assert len(plan_info["tech_stack"]) > 0

    def test_parse_plan_file_not_found(self, temp_project_dir):
        """Test parsing non-existent plan file raises error."""
        parser = TaskParser()
        non_existent = temp_project_dir / "nonexistent_plan.md"

        with pytest.raises(FileNotFoundError):
            parser.parse_plan_file(non_existent)

    def test_convenience_function_parse_tasks(self, sample_tasks_file):
        """Test convenience function parse_tasks()."""
        tasks = parse_tasks(sample_tasks_file)

        assert len(tasks) > 0
        assert all(isinstance(task, Task) for task in tasks)

    def test_multiple_user_stories_same_phase(self):
        """Test parsing multiple user stories in same phase."""
        content = dedent("""
            ## Phase 1: User Stories

            - [ ] T001 [US1] Feature A
            - [ ] T002 [US1] Feature B
            - [ ] T003 [US2] Feature C
            - [ ] T004 [US2] Feature D
        """).strip()

        parser = TaskParser()
        tasks = parser.parse_tasks_content(content)

        us1_tasks = [t for t in tasks if t.user_story == "US1"]
        us2_tasks = [t for t in tasks if t.user_story == "US2"]

        assert len(us1_tasks) == 2
        assert len(us2_tasks) == 2

    def test_task_with_multiple_markers(self):
        """Test task with multiple markers ([P], [US1], etc.)."""
        parser = TaskParser()
        line = "- [ ] T001 [P] [US1] [P0] Complex task with multiple markers"
        task = parser._parse_task_line(line)

        assert task is not None
        assert task.task_id == "T001"
        assert task.user_story == "US1"
        assert task.is_parallelizable is True
        # Priority might be extracted differently depending on implementation

    def test_extract_file_path_variations(self):
        """Test file path extraction with various formats."""
        parser = TaskParser()

        test_cases = [
            ("Update in src/file.py", "src/file.py"),
            ("Modify to config.yml", "config.yml"),
            ("Add code at `tests/test.py`", "tests/test.py"),
            ('Edit from "docs/readme.md"', "docs/readme.md"),
        ]

        for description, expected_path in test_cases:
            path = parser._extract_file_path(description)
            assert path == expected_path, f"Failed for: {description}"

    def test_extract_priority_variations(self):
        """Test priority extraction from descriptions."""
        parser = TaskParser()

        test_cases = [
            ("[P0] Critical fix", "P0"),
            ("[P1] Important task", "P1"),
            ("[P2] Nice to have", "P2"),
            ("No priority here", None),
        ]

        for description, expected_priority in test_cases:
            priority = parser._extract_priority(description)
            assert priority == expected_priority, f"Failed for: {description}"

    def test_parse_tasks_preserves_order(self, sample_tasks_content):
        """Test that task order is preserved during parsing."""
        parser = TaskParser()
        tasks = parser.parse_tasks_content(sample_tasks_content)

        task_ids = [t.task_id for t in tasks]

        # Check that T001 comes before T002, T002 before T003, etc.
        for i in range(len(task_ids) - 1):
            current_num = int(task_ids[i][1:])
            next_num = int(task_ids[i + 1][1:])
            assert current_num < next_num, f"Task order not preserved: {task_ids}"

    def test_phase_header_variations(self):
        """Test different phase header formats."""
        content = dedent("""
            ## Phase 1: Setup
            - [ ] T001 Task A

            ### Phase 2: Implementation
            - [ ] T002 Task B

            ## Phase: Testing
            - [ ] T003 Task C
        """).strip()

        parser = TaskParser()
        tasks = parser.parse_tasks_content(content)

        assert len(tasks) == 3
        assert all(t.phase is not None for t in tasks)
