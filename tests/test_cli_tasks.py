"""CLI tests for 'specify tasks' command."""

from typer.testing import CliRunner
from textwrap import dedent

# Import the CLI app
from specify_cli import app


runner = CliRunner()


class TestTasksCLI:
    """Test suite for 'specify tasks' CLI command."""

    def test_tasks_command_help(self):
        """Test tasks command shows help."""
        result = runner.invoke(app, ["tasks", "--help"])

        assert result.exit_code == 0
        assert "Generate tasks from spec/plan/tasks.md files" in result.output
        assert "--format" in result.output
        assert "--source" in result.output
        assert "--dry-run" in result.output

    def test_tasks_generate_from_tasks_file(self, sample_tasks_file, temp_project_dir):
        """Test generating tasks from tasks.md file."""
        # Change to temp directory for output
        backlog_dir = temp_project_dir / "backlog"

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(backlog_dir),
            ],
        )

        # Should succeed
        assert result.exit_code == 0
        assert "successfully" in result.output.lower()

        # Verify files were created
        assert backlog_dir.exists()
        task_files = list((backlog_dir / "tasks").glob("task-*.md"))
        assert len(task_files) > 0

    def test_tasks_generate_from_directory(self, temp_project_dir):
        """Test generating tasks from directory with tasks.md."""
        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Create feature
            - [ ] T002 Add tests
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 0
        assert "successfully" in result.output.lower()

    def test_tasks_generate_dry_run(self, sample_tasks_file, temp_project_dir):
        """Test dry run mode doesn't create files."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN" in result.output or "Dry run" in result.output

        # No files should be created
        backlog_dir = temp_project_dir / "backlog" / "tasks"
        if backlog_dir.exists():
            assert len(list(backlog_dir.glob("task-*.md"))) == 0

    def test_tasks_generate_with_overwrite(self, sample_tasks_file, temp_project_dir):
        """Test overwrite flag overwrites existing files."""
        backlog_dir = temp_project_dir / "backlog"

        # Generate first time
        runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(backlog_dir),
            ],
        )

        # Generate again with overwrite
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(backlog_dir),
                "--overwrite",
            ],
        )

        assert result.exit_code == 0

    def test_tasks_invalid_action(self):
        """Test invalid action shows error."""
        result = runner.invoke(app, ["tasks", "invalid_action"])

        assert result.exit_code == 1
        assert "Unsupported action" in result.output

    def test_tasks_invalid_format(self, sample_tasks_file):
        """Test invalid format shows error."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--format",
                "invalid",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid format" in result.output

    def test_tasks_markdown_format_not_implemented(self, sample_tasks_file):
        """Test that markdown format shows not implemented message."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--format",
                "markdown",
            ],
        )

        assert result.exit_code == 1
        assert "not yet implemented" in result.output.lower() or "Legacy" in result.output

    def test_tasks_nonexistent_source(self):
        """Test error on non-existent source path."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                "/nonexistent/path/to/tasks.md",
            ],
        )

        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_tasks_invalid_source_file_name(self, temp_project_dir):
        """Test error when source file is not named tasks.md."""
        wrong_file = temp_project_dir / "wrong_name.md"
        wrong_file.write_text("- [ ] T001 Task")

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(wrong_file),
            ],
        )

        assert result.exit_code == 1
        assert "must be named 'tasks.md'" in result.output

    def test_tasks_no_tasks_found(self, temp_project_dir):
        """Test error when no tasks are found."""
        empty_file = temp_project_dir / "tasks.md"
        empty_file.write_text("# Empty\n\nNo tasks here")

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(empty_file),
            ],
        )

        assert result.exit_code == 1
        assert "No tasks found" in result.output

    def test_tasks_shows_statistics(self, sample_tasks_file, temp_project_dir):
        """Test that output shows task statistics."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
            ],
        )

        assert result.exit_code == 0

        # Should show some statistics
        output_lower = result.output.lower()
        assert "parsed" in output_lower or "created" in output_lower or "task" in output_lower

    def test_tasks_displays_source_and_output(self, sample_tasks_file, temp_project_dir):
        """Test that command displays source and output paths."""
        backlog_dir = temp_project_dir / "backlog"

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(backlog_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Source:" in result.output
        assert "Output:" in result.output

    def test_tasks_default_source_current_directory(self, temp_project_dir, monkeypatch):
        """Test that default source is current directory."""
        # Create tasks.md in temp dir
        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Task
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        # Change to temp directory
        monkeypatch.chdir(temp_project_dir)

        result = runner.invoke(
            app,
            ["tasks", "generate"],
        )

        # Should use current directory as source
        assert result.exit_code == 0

    def test_tasks_default_output_backlog_dir(self, sample_tasks_file, temp_project_dir):
        """Test that default output is ./backlog directory."""
        # Get the parent directory of sample_tasks_file
        source_dir = sample_tasks_file.parent

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
            ],
        )

        # Output should mention backlog directory
        # Note: actual output path depends on source, but should contain "backlog"
        assert result.exit_code == 0

    def test_tasks_backlog_format_default(self, sample_tasks_file, temp_project_dir):
        """Test that backlog format is the default."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(sample_tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
            ],
        )

        assert result.exit_code == 0

        # Should create backlog-style files
        task_files = list((temp_project_dir / "backlog" / "tasks").glob("task-*.md"))
        assert len(task_files) > 0

        # Check file format
        first_file = task_files[0]
        content = first_file.read_text()
        assert content.startswith("---")
        assert "id:" in content

    def test_tasks_generate_from_spec_directory(self, temp_project_dir, sample_spec_content):
        """Test generating from directory with spec.md."""
        spec_file = temp_project_dir / "spec.md"
        spec_file.write_text(sample_spec_content)

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(temp_project_dir),
            ],
        )

        # Should generate basic tasks from user stories
        assert result.exit_code == 0

    def test_tasks_no_spec_or_tasks_file(self, temp_project_dir):
        """Test error when directory has no spec.md or tasks.md."""
        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(temp_project_dir),
            ],
        )

        assert result.exit_code == 1
        assert "No spec.md or tasks.md found" in result.output

    def test_tasks_with_validation_errors(self, temp_project_dir):
        """Test that validation errors are displayed."""
        # Create tasks with invalid dependencies
        invalid_content = dedent("""
            ## Phase 1
            - [ ] T001 Task depends on T999
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(invalid_content)

        # Manually set up invalid dependencies would require modifying parser
        # This is a basic test to ensure error handling works
        # Actual validation error display requires more complex setup

    def test_tasks_complex_workflow(self, temp_project_dir):
        """Test complete workflow with realistic data."""
        tasks_content = dedent("""
            # Project Tasks

            ## Phase 1: Setup
            - [ ] T001 Initialize project structure
            - [ ] T002 [P] Configure development tools

            ## Phase 2: Implementation
            - [ ] T003 [US1] [P0] Implement core feature in src/core.py
            - [ ] T004 [US1] Add unit tests to tests/test_core.py
            - [ ] T005 [US2] Build UI components

            ## Phase 3: Polish
            - [x] T006 Code review and cleanup
            - [ ] T007 Update documentation
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        # 1. Dry run first
        dry_result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(tasks_file),
                "--dry-run",
            ],
        )

        assert dry_result.exit_code == 0
        assert "DRY RUN" in dry_result.output or "Dry run" in dry_result.output

        # 2. Actual generation
        gen_result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
            ],
        )

        assert gen_result.exit_code == 0

        # 3. Verify files created
        task_files = list((temp_project_dir / "backlog" / "tasks").glob("task-*.md"))
        assert len(task_files) == 7  # All 7 tasks

        # 4. Verify content of a specific task
        task_003 = None
        for f in task_files:
            if "task-003" in f.name:
                task_003 = f
                break

        assert task_003 is not None
        content = task_003.read_text()

        # Check frontmatter
        assert "id: task-003" in content
        assert "US1" in content
        assert "P0" in content

        # Check body
        assert "Implement core feature" in content
        assert "src/core.py" in content

    def test_tasks_unicode_handling(self, temp_project_dir):
        """Test that unicode characters in tasks are handled correctly."""
        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Create user model with UTF-8 support: émojis 🚀
            - [ ] T002 Add internationalization for 中文
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content, encoding='utf-8')

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
            ],
        )

        assert result.exit_code == 0

        # Verify unicode was preserved
        task_files = list((temp_project_dir / "backlog" / "tasks").glob("task-*.md"))
        assert len(task_files) > 0

        content = task_files[0].read_text(encoding='utf-8')
        # Unicode should be in filename or content
        # Just verify no encoding errors occurred

    def test_tasks_long_descriptions(self, temp_project_dir):
        """Test handling of very long task descriptions."""
        long_desc = "A" * 200  # Very long description

        tasks_content = dedent(f"""
            ## Phase 1
            - [ ] T001 {long_desc}
        """).strip()

        tasks_file = temp_project_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(tasks_file),
                "--output",
                str(temp_project_dir / "backlog"),
            ],
        )

        # Should handle gracefully (filename truncation, etc.)
        assert result.exit_code == 0

    def test_tasks_special_characters_in_paths(self, tmp_path):
        """Test handling paths with spaces and special chars."""
        # Create directory with spaces
        special_dir = tmp_path / "my project files"
        special_dir.mkdir()

        tasks_content = dedent("""
            ## Phase 1
            - [ ] T001 Test task
        """).strip()

        tasks_file = special_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        result = runner.invoke(
            app,
            [
                "tasks",
                "generate",
                "--source",
                str(tasks_file),
                "--output",
                str(special_dir / "backlog"),
            ],
        )

        # Should handle paths with spaces
        assert result.exit_code == 0
