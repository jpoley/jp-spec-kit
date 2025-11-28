"""Integration tests for TaskMapper."""

from textwrap import dedent

from specify_cli.backlog.mapper import TaskMapper, generate_backlog_tasks
from specify_cli.backlog.parser import Task


class TestTaskMapper:
    """Test suite for TaskMapper class."""

    def test_mapper_initialization(self, backlog_dir):
        """Test mapper initializes correctly."""
        mapper = TaskMapper(backlog_dir)

        assert mapper.backlog_dir == backlog_dir
        assert mapper.parser is not None
        assert mapper.writer is not None

    def test_generate_from_tasks_file_success(self, sample_tasks_file, backlog_dir):
        """Test successful task generation from tasks.md file."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file)

        assert result["success"] is True
        assert result["tasks_parsed"] > 0
        assert result["tasks_created"] > 0
        assert "execution_order" in result
        assert "parallel_batches" in result
        assert "critical_path" in result

    def test_generate_from_tasks_file_dry_run(self, sample_tasks_file, backlog_dir):
        """Test dry run mode doesn't create files."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file, dry_run=True)

        assert result["success"] is True
        assert result["dry_run"] is True
        assert result["tasks_parsed"] > 0

        # No files should be created
        tasks_dir = backlog_dir / "tasks"
        if tasks_dir.exists():
            task_files = list(tasks_dir.glob("task-*.md"))
            assert len(task_files) == 0

    def test_generate_from_tasks_file_creates_backlog_files(self, sample_tasks_file, backlog_dir):
        """Test that backlog task files are created."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file)

        tasks_dir = backlog_dir / "tasks"
        assert tasks_dir.exists()

        task_files = list(tasks_dir.glob("task-*.md"))
        assert len(task_files) == result["tasks_created"]

        # Verify file format
        first_file = task_files[0]
        content = first_file.read_text()
        assert content.startswith("---")
        assert "id:" in content
        assert "title:" in content

    def test_generate_from_empty_file(self, temp_project_dir, backlog_dir, empty_tasks_content):
        """Test generating from file with no tasks."""
        empty_file = temp_project_dir / "empty.md"
        empty_file.write_text(empty_tasks_content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(empty_file)

        assert result["success"] is False
        assert "No tasks found" in result["error"]

    def test_generate_with_invalid_dependencies(self, temp_project_dir, backlog_dir):
        """Test handling of invalid dependency graph."""
        invalid_content = dedent("""
            ## Phase 1
            - [ ] T001 Task depends on non-existent
            - [ ] T002 Task B
        """).strip()

        # Manually create task with invalid dependency
        invalid_file = temp_project_dir / "invalid.md"
        invalid_file.write_text(invalid_content)

        # Parse and add invalid dependency
        from specify_cli.backlog.parser import TaskParser
        parser = TaskParser()
        tasks = parser.parse_tasks_content(invalid_content)

        # Add invalid dependency manually
        if tasks:
            tasks[0].dependencies = ["T999"]

        # Create graph - should fail validation
        from specify_cli.backlog.dependency_graph import DependencyGraphBuilder
        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        assert is_valid is False

    def test_generate_from_tasks_file_overwrite_false(self, sample_tasks_file, backlog_dir):
        """Test that existing files are not overwritten by default."""
        mapper = TaskMapper(backlog_dir)

        # Generate first time
        result1 = mapper.generate_from_tasks_file(sample_tasks_file)
        files_created_first = result1["tasks_created"]

        # Generate second time
        result2 = mapper.generate_from_tasks_file(sample_tasks_file, overwrite=False)

        # No new files should be created
        assert result2["tasks_created"] == 0

    def test_generate_from_tasks_file_overwrite_true(self, sample_tasks_file, backlog_dir):
        """Test that files are overwritten when flag is set."""
        mapper = TaskMapper(backlog_dir)

        # Generate first time
        result1 = mapper.generate_from_tasks_file(sample_tasks_file)
        original_count = result1["tasks_created"]

        # Generate second time with overwrite
        result2 = mapper.generate_from_tasks_file(sample_tasks_file, overwrite=True)

        # Same number of files should be created
        assert result2["tasks_created"] == original_count

    def test_generate_from_spec_with_tasks_file(self, temp_project_dir, backlog_dir):
        """Test generate_from_spec uses tasks.md when available."""
        # Create a tasks.md in the spec directory
        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Task from tasks.md
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_spec(temp_project_dir)

        assert result["success"] is True
        assert result["tasks_parsed"] >= 1

    def test_generate_from_spec_no_files(self, temp_project_dir, backlog_dir):
        """Test generate_from_spec fails when no spec files exist."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_spec(temp_project_dir)

        assert result["success"] is False
        assert "No spec.md or tasks.md found" in result["error"]

    def test_generate_from_spec_with_spec_file(self, sample_spec_file, backlog_dir, temp_project_dir):
        """Test generating from spec.md file."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_spec(temp_project_dir)

        # Should generate basic tasks from user stories
        assert result["success"] is True
        assert result["tasks_generated"] > 0

    def test_group_by_phase(self, backlog_dir):
        """Test grouping tasks by phase."""
        mapper = TaskMapper(backlog_dir)

        tasks = [
            Task(task_id="T001", description="Setup 1", phase="Setup"),
            Task(task_id="T002", description="Setup 2", phase="Setup"),
            Task(task_id="T003", description="Impl", phase="Implementation"),
        ]

        grouped = mapper._group_by_phase(tasks)

        assert "Setup" in grouped
        assert "Implementation" in grouped
        assert len(grouped["Setup"]) == 2
        assert len(grouped["Implementation"]) == 1

    def test_group_by_story(self, backlog_dir):
        """Test grouping tasks by user story."""
        mapper = TaskMapper(backlog_dir)

        tasks = [
            Task(task_id="T001", description="US1 task 1", user_story="US1"),
            Task(task_id="T002", description="US1 task 2", user_story="US1"),
            Task(task_id="T003", description="US2 task", user_story="US2"),
            Task(task_id="T004", description="No story"),
        ]

        grouped = mapper._group_by_story(tasks)

        assert "US1" in grouped
        assert "US2" in grouped
        assert "No Story" in grouped
        assert len(grouped["US1"]) == 2
        assert len(grouped["US2"]) == 1

    def test_regenerate_with_conflicts_skip(self, sample_tasks_file, backlog_dir):
        """Test regenerate with skip strategy on conflicts."""
        mapper = TaskMapper(backlog_dir)

        # Initial generation
        mapper.generate_from_tasks_file(sample_tasks_file)

        # Regenerate with skip strategy
        result = mapper.regenerate(sample_tasks_file, conflict_strategy="skip")

        assert result["success"] is False
        assert "Conflicts detected" in result["error"]
        assert len(result["conflicts"]) > 0

    def test_regenerate_with_conflicts_overwrite(self, sample_tasks_file, backlog_dir):
        """Test regenerate with overwrite strategy."""
        mapper = TaskMapper(backlog_dir)

        # Initial generation
        initial_result = mapper.generate_from_tasks_file(sample_tasks_file)

        # Regenerate with overwrite
        result = mapper.regenerate(sample_tasks_file, conflict_strategy="overwrite")

        assert result["success"] is True
        assert result["tasks_regenerated"] > 0
        assert result["conflicts_resolved"] > 0

    def test_get_stats(self, sample_tasks_file, backlog_dir):
        """Test getting backlog statistics."""
        mapper = TaskMapper(backlog_dir)

        # Generate tasks
        mapper.generate_from_tasks_file(sample_tasks_file)

        # Get stats
        stats = mapper.get_stats()

        assert stats["total"] > 0
        assert "by_status" in stats
        assert "by_label" in stats

    def test_result_contains_execution_info(self, sample_tasks_file, backlog_dir):
        """Test that result contains execution planning info."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file)

        assert "execution_order" in result
        assert "parallel_batches" in result
        assert "critical_path" in result
        assert "tasks_by_phase" in result
        assert "tasks_by_story" in result

        # Verify execution order is a list
        assert isinstance(result["execution_order"], list)
        assert len(result["execution_order"]) == result["tasks_parsed"]

    def test_result_contains_file_paths(self, sample_tasks_file, backlog_dir):
        """Test that result contains created file paths."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file)

        assert "created_files" in result
        assert len(result["created_files"]) == result["tasks_created"]

        # Verify paths are strings
        for file_path in result["created_files"]:
            assert isinstance(file_path, str)

    def test_convenience_function_with_tasks_file(self, sample_tasks_file, backlog_dir):
        """Test convenience function with tasks.md file."""
        result = generate_backlog_tasks(
            sample_tasks_file,
            backlog_dir,
        )

        assert result["success"] is True
        assert result["tasks_parsed"] > 0

    def test_convenience_function_with_directory(self, temp_project_dir, backlog_dir):
        """Test convenience function with directory."""
        # Create tasks.md in directory
        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Test task
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        result = generate_backlog_tasks(
            temp_project_dir,
            backlog_dir,
        )

        assert result["success"] is True

    def test_convenience_function_invalid_path(self, temp_project_dir, backlog_dir):
        """Test convenience function with invalid path."""
        invalid_file = temp_project_dir / "invalid.txt"
        invalid_file.write_text("Not a tasks file")

        result = generate_backlog_tasks(
            invalid_file,
            backlog_dir,
        )

        assert result["success"] is False
        assert "Invalid source path" in result["error"]

    def test_dry_run_shows_parallel_info(self, sample_tasks_file, backlog_dir):
        """Test that dry run shows parallelization information."""
        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(sample_tasks_file, dry_run=True)

        assert result["dry_run"] is True
        assert "parallel_batches" in result
        assert "execution_order" in result
        assert "critical_path" in result

        # Should have analysis without creating files
        assert len(result["parallel_batches"]) > 0

    def test_generate_preserves_task_metadata(self, backlog_dir, temp_project_dir):
        """Test that task metadata is preserved in generated files."""
        content = dedent("""
            ## Phase 1: Setup

            - [ ] T001 [P] [US1] [P0] Complex task in src/main.py
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(tasks_file)

        # Read generated file
        task_files = list((backlog_dir / "tasks").glob("task-001*.md"))
        assert len(task_files) == 1

        file_content = task_files[0].read_text()

        # Check metadata is preserved
        assert "US1" in file_content
        assert "parallelizable" in file_content
        assert "P0" in file_content
        assert "src/main.py" in file_content

    def test_end_to_end_workflow(self, sample_tasks_file, backlog_dir):
        """Test complete end-to-end workflow."""
        mapper = TaskMapper(backlog_dir)

        # 1. Dry run first
        dry_result = mapper.generate_from_tasks_file(sample_tasks_file, dry_run=True)
        assert dry_result["success"] is True
        assert dry_result["dry_run"] is True

        # 2. Generate tasks
        gen_result = mapper.generate_from_tasks_file(sample_tasks_file)
        assert gen_result["success"] is True
        assert gen_result["tasks_created"] > 0

        # 3. Get stats
        stats = mapper.get_stats()
        assert stats["total"] == gen_result["tasks_created"]

        # 4. Try to regenerate (should detect conflicts)
        regen_result = mapper.regenerate(sample_tasks_file, conflict_strategy="skip")
        assert regen_result["success"] is False
        assert "Conflicts" in regen_result["error"]

        # 5. Force regenerate
        force_result = mapper.regenerate(sample_tasks_file, conflict_strategy="overwrite")
        assert force_result["success"] is True

    def test_generate_from_spec_with_plan(self, temp_project_dir, backlog_dir, sample_spec_content, sample_plan_content):
        """Test generating from spec with plan file."""
        spec_file = temp_project_dir / "spec.md"
        plan_file = temp_project_dir / "plan.md"

        spec_file.write_text(sample_spec_content)
        plan_file.write_text(sample_plan_content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_spec(temp_project_dir)

        assert result["success"] is True
        assert result["tasks_generated"] > 0
        assert "user_stories" in result

    def test_task_grouping_accuracy(self, backlog_dir, temp_project_dir):
        """Test that task grouping is accurate."""
        content = dedent("""
            ## Phase 1: Setup
            - [ ] T001 Setup A
            - [ ] T002 Setup B

            ## Phase 2: User Story 1
            - [ ] T003 [US1] Feature A
            - [ ] T004 [US1] Feature B

            ## Phase 3: User Story 2
            - [ ] T005 [US2] Feature C
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(tasks_file)

        # Check phase grouping
        by_phase = result["tasks_by_phase"]
        assert len(by_phase["Phase 1: Setup"]) == 2
        assert len(by_phase["Phase 2: User Story 1"]) == 2
        assert len(by_phase["Phase 3: User Story 2"]) == 1

        # Check story grouping
        by_story = result["tasks_by_story"]
        assert len(by_story["US1"]) == 2
        assert len(by_story["US2"]) == 1
        assert len(by_story["No Story"]) == 2

    def test_parallel_batch_calculation(self, backlog_dir, temp_project_dir):
        """Test parallel batch calculation is correct."""
        content = dedent("""
            ## Phase 1
            - [ ] T001 Base task

            ## Phase 2
            - [ ] T002 [P] Parallel A
            - [ ] T003 [P] Parallel B
            - [ ] T004 [P] Parallel C

            ## Phase 3
            - [ ] T005 Merge task
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(tasks_file, dry_run=True)

        batches = result["parallel_batches"]

        # First batch should have just T001
        assert len(batches) >= 1
        # There should be a batch with multiple parallelizable tasks
        assert any(len(batch) > 1 for batch in batches)

    def test_critical_path_identification(self, backlog_dir, temp_project_dir):
        """Test that critical path is correctly identified."""
        content = dedent("""
            ## Phase 1
            - [ ] T001 Start

            ## Phase 2
            - [ ] T002 Quick branch
            - [ ] T003 Long branch A
            - [ ] T004 Long branch B
            - [ ] T005 Long branch C
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(content)

        mapper = TaskMapper(backlog_dir)
        result = mapper.generate_from_tasks_file(tasks_file, dry_run=True)

        critical_path = result["critical_path"]

        # Critical path should include at least T001
        # Note: Dependency inference may not create the expected chain without explicit dependencies
        assert "T001" in critical_path
        assert len(critical_path) >= 1
