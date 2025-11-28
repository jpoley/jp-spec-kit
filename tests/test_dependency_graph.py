"""Unit tests for DependencyGraphBuilder."""

import pytest

from specify_cli.backlog.dependency_graph import DependencyGraphBuilder
from specify_cli.backlog.parser import Task


class TestDependencyGraphBuilder:
    """Test suite for DependencyGraphBuilder class."""

    def test_graph_initialization(self):
        """Test graph builder initializes correctly."""
        tasks = [
            Task(task_id="T001", description="Task 1"),
            Task(task_id="T002", description="Task 2"),
        ]

        graph = DependencyGraphBuilder(tasks)

        assert len(graph.tasks) == 2
        assert len(graph.task_map) == 2
        assert "T001" in graph.task_map
        assert "T002" in graph.task_map

    def test_simple_dependency_chain(self):
        """Test simple linear dependency chain."""
        tasks = [
            Task(task_id="T001", description="Task 1", dependencies=[]),
            Task(task_id="T002", description="Task 2", dependencies=["T001"]),
            Task(task_id="T003", description="Task 3", dependencies=["T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        # Check dependencies
        assert graph.get_dependencies("T001") == []
        assert graph.get_dependencies("T002") == ["T001"]
        assert graph.get_dependencies("T003") == ["T002"]

        # Check dependents
        assert "T002" in graph.get_dependents("T001")
        assert "T003" in graph.get_dependents("T002")
        assert graph.get_dependents("T003") == []

    def test_get_all_dependencies_transitive(self):
        """Test getting all transitive dependencies."""
        tasks = [
            Task(task_id="T001", description="Base", dependencies=[]),
            Task(task_id="T002", description="Depends on T001", dependencies=["T001"]),
            Task(task_id="T003", description="Depends on T002", dependencies=["T002"]),
            Task(task_id="T004", description="Depends on T003", dependencies=["T003"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        all_deps = graph.get_all_dependencies("T004")

        # T004 should depend on T003, T002, and T001 (transitively)
        assert "T003" in all_deps
        assert "T002" in all_deps
        assert "T001" in all_deps

    def test_get_execution_order_simple(self):
        """Test topological sort for execution order."""
        tasks = [
            Task(task_id="T001", description="First"),
            Task(task_id="T002", description="Second", dependencies=["T001"]),
            Task(task_id="T003", description="Third", dependencies=["T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        order = graph.get_execution_order()

        assert order == ["T001", "T002", "T003"]

    def test_get_execution_order_parallel_tasks(self):
        """Test execution order with parallel tasks."""
        tasks = [
            Task(task_id="T001", description="Base"),
            Task(task_id="T002", description="Branch A", dependencies=["T001"]),
            Task(task_id="T003", description="Branch B", dependencies=["T001"]),
            Task(task_id="T004", description="Merge", dependencies=["T002", "T003"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        order = graph.get_execution_order()

        # T001 must be first, T004 must be last
        assert order[0] == "T001"
        assert order[-1] == "T004"

        # T002 and T003 can be in any order
        assert set(order[1:3]) == {"T002", "T003"}

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected."""
        tasks = [
            Task(task_id="T001", description="A", dependencies=["T003"]),
            Task(task_id="T002", description="B", dependencies=["T001"]),
            Task(task_id="T003", description="C", dependencies=["T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        with pytest.raises(ValueError, match="Circular dependency"):
            graph.get_execution_order()

    def test_self_referencing_task(self):
        """Test task that depends on itself."""
        tasks = [
            Task(task_id="T001", description="Self-ref", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        with pytest.raises(ValueError, match="Circular dependency"):
            graph.get_execution_order()

    def test_get_parallel_batches_linear(self):
        """Test parallel batches for linear dependency chain."""
        tasks = [
            Task(task_id="T001", description="First"),
            Task(task_id="T002", description="Second", dependencies=["T001"]),
            Task(task_id="T003", description="Third", dependencies=["T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        batches = graph.get_parallel_batches()

        # Should have 3 batches, one task each
        assert len(batches) == 3
        assert batches[0] == ["T001"]
        assert batches[1] == ["T002"]
        assert batches[2] == ["T003"]

    def test_get_parallel_batches_with_parallelism(self):
        """Test parallel batches identifies parallelizable tasks."""
        tasks = [
            Task(task_id="T001", description="Base"),
            Task(task_id="T002", description="Branch A", dependencies=["T001"]),
            Task(task_id="T003", description="Branch B", dependencies=["T001"]),
            Task(task_id="T004", description="Branch C", dependencies=["T001"]),
            Task(task_id="T005", description="Merge", dependencies=["T002", "T003", "T004"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        batches = graph.get_parallel_batches()

        # Should have 3 batches: [T001], [T002, T003, T004], [T005]
        assert len(batches) == 3
        assert batches[0] == ["T001"]
        assert set(batches[1]) == {"T002", "T003", "T004"}
        assert batches[2] == ["T005"]

    def test_get_parallelizable_tasks(self):
        """Test getting tasks marked as parallelizable."""
        tasks = [
            Task(task_id="T001", description="Sequential"),
            Task(task_id="T002", description="Parallel A", is_parallelizable=True),
            Task(task_id="T003", description="Parallel B", is_parallelizable=True),
            Task(task_id="T004", description="Sequential"),
        ]

        graph = DependencyGraphBuilder(tasks)
        parallelizable = graph.get_parallelizable_tasks()

        assert set(parallelizable) == {"T002", "T003"}

    def test_get_parallelizable_tasks_from_batch(self):
        """Test getting parallelizable tasks from specific batch."""
        tasks = [
            Task(task_id="T001", description="Base"),
            Task(task_id="T002", description="Parallel", is_parallelizable=True, dependencies=["T001"]),
            Task(task_id="T003", description="Sequential", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        batches = graph.get_parallel_batches()

        # Get parallelizable from second batch
        parallelizable = graph.get_parallelizable_tasks(batch=batches[1])

        assert "T002" in parallelizable
        assert "T003" not in parallelizable

    def test_get_critical_path_linear(self):
        """Test critical path for linear chain."""
        tasks = [
            Task(task_id="T001", description="First"),
            Task(task_id="T002", description="Second", dependencies=["T001"]),
            Task(task_id="T003", description="Third", dependencies=["T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        critical_path = graph.get_critical_path()

        # Critical path should be the entire chain
        assert "T001" in critical_path
        assert "T002" in critical_path
        assert "T003" in critical_path

    def test_get_critical_path_with_branches(self):
        """Test critical path identifies longest path."""
        tasks = [
            Task(task_id="T001", description="Base"),
            # Short branch
            Task(task_id="T002", description="Short", dependencies=["T001"]),
            # Long branch
            Task(task_id="T003", description="Long A", dependencies=["T001"]),
            Task(task_id="T004", description="Long B", dependencies=["T003"]),
            Task(task_id="T005", description="Long C", dependencies=["T004"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        critical_path = graph.get_critical_path()

        # Critical path should go through the longest branch
        assert "T001" in critical_path
        assert "T003" in critical_path
        assert "T004" in critical_path
        assert "T005" in critical_path
        # T002 should not be in critical path (shorter branch)
        assert "T002" not in critical_path

    def test_validate_valid_graph(self):
        """Test validation passes for valid graph."""
        tasks = [
            Task(task_id="T001", description="First"),
            Task(task_id="T002", description="Second", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        assert is_valid is True
        assert errors == []

    def test_validate_circular_dependency(self):
        """Test validation detects circular dependencies."""
        tasks = [
            Task(task_id="T001", description="A", dependencies=["T002"]),
            Task(task_id="T002", description="B", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        assert is_valid is False
        assert len(errors) > 0
        assert any("Circular" in err for err in errors)

    def test_validate_dangling_dependency(self):
        """Test validation detects non-existent dependencies."""
        tasks = [
            Task(task_id="T001", description="Valid"),
            Task(task_id="T002", description="Invalid", dependencies=["T999"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        assert is_valid is False
        assert len(errors) > 0
        assert any("T999" in err for err in errors)

    def test_validate_multiple_errors(self):
        """Test validation reports multiple errors."""
        tasks = [
            Task(task_id="T001", description="Dangling dep 1", dependencies=["T999"]),
            Task(task_id="T002", description="Dangling dep 2", dependencies=["T888"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        assert is_valid is False
        # Should have at least 2 dangling dependency errors (may also detect circular)
        assert len(errors) >= 2

    def test_to_markdown_output(self):
        """Test markdown generation."""
        tasks = [
            Task(
                task_id="T001",
                description="First task",
                phase="Setup",
            ),
            Task(
                task_id="T002",
                description="Second task",
                phase="Implementation",
                dependencies=["T001"],
            ),
        ]

        graph = DependencyGraphBuilder(tasks)
        markdown = graph.to_markdown()

        # Check structure
        assert "# Task Dependency Graph" in markdown
        assert "## Setup" in markdown or "## Phase" in markdown
        assert "T001" in markdown
        assert "T002" in markdown
        assert "## Summary" in markdown
        assert "Total Tasks:" in markdown
        assert "Critical Path" in markdown

    def test_to_markdown_shows_dependencies(self):
        """Test markdown shows task dependencies."""
        tasks = [
            Task(task_id="T001", description="Base", phase="Setup"),
            Task(task_id="T002", description="Dependent", phase="Setup", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)
        markdown = graph.to_markdown()

        assert "Dependencies:" in markdown or "**Dependencies:**" in markdown

    def test_to_markdown_shows_labels(self):
        """Test markdown shows task labels."""
        tasks = [
            Task(
                task_id="T001",
                description="Task with labels",
                phase="Implementation",
                user_story="US1",
                is_parallelizable=True,
            ),
        ]

        graph = DependencyGraphBuilder(tasks)
        markdown = graph.to_markdown()

        assert "Labels:" in markdown or "**Labels:**" in markdown

    def test_empty_graph(self):
        """Test graph with no tasks."""
        tasks = []
        graph = DependencyGraphBuilder(tasks)

        assert graph.get_execution_order() == []
        assert graph.get_parallel_batches() == []
        assert graph.get_critical_path() == []

    def test_single_task_graph(self):
        """Test graph with single independent task."""
        tasks = [Task(task_id="T001", description="Only task")]

        graph = DependencyGraphBuilder(tasks)

        assert graph.get_execution_order() == ["T001"]
        assert graph.get_parallel_batches() == [["T001"]]
        assert graph.get_critical_path() == ["T001"]

    def test_independent_tasks(self):
        """Test graph with multiple independent tasks."""
        tasks = [
            Task(task_id="T001", description="Independent A"),
            Task(task_id="T002", description="Independent B"),
            Task(task_id="T003", description="Independent C"),
        ]

        graph = DependencyGraphBuilder(tasks)

        # All tasks can run in parallel
        batches = graph.get_parallel_batches()
        assert len(batches) == 1
        assert set(batches[0]) == {"T001", "T002", "T003"}

    def test_complex_dependency_graph(self):
        """Test complex graph with multiple dependency patterns."""
        tasks = [
            Task(task_id="T001", description="Init"),
            Task(task_id="T002", description="Setup A", dependencies=["T001"]),
            Task(task_id="T003", description="Setup B", dependencies=["T001"]),
            Task(task_id="T004", description="Feature A", dependencies=["T002"]),
            Task(task_id="T005", description="Feature B", dependencies=["T002", "T003"]),
            Task(task_id="T006", description="Integration", dependencies=["T004", "T005"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        # Validate
        is_valid, errors = graph.validate()
        assert is_valid is True

        # Check execution order is valid
        order = graph.get_execution_order()
        assert len(order) == 6
        assert order[0] == "T001"
        assert order[-1] == "T006"

        # Check critical path
        critical_path = graph.get_critical_path()
        assert len(critical_path) >= 4

    def test_get_dependencies_nonexistent_task(self):
        """Test getting dependencies for non-existent task."""
        tasks = [Task(task_id="T001", description="Exists")]

        graph = DependencyGraphBuilder(tasks)
        deps = graph.get_dependencies("T999")

        assert deps == []

    def test_get_dependents_nonexistent_task(self):
        """Test getting dependents for non-existent task."""
        tasks = [Task(task_id="T001", description="Exists")]

        graph = DependencyGraphBuilder(tasks)
        dependents = graph.get_dependents("T999")

        assert dependents == []

    def test_diamond_dependency_pattern(self):
        """Test diamond-shaped dependency pattern."""
        tasks = [
            Task(task_id="T001", description="Top"),
            Task(task_id="T002", description="Left", dependencies=["T001"]),
            Task(task_id="T003", description="Right", dependencies=["T001"]),
            Task(task_id="T004", description="Bottom", dependencies=["T002", "T003"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        # Validate
        is_valid, errors = graph.validate()
        assert is_valid is True

        # Check batches
        batches = graph.get_parallel_batches()
        assert batches[0] == ["T001"]
        assert set(batches[1]) == {"T002", "T003"}  # Can run in parallel
        assert batches[2] == ["T004"]

    def test_multiple_starting_points(self):
        """Test graph with multiple tasks that have no dependencies."""
        tasks = [
            Task(task_id="T001", description="Start A"),
            Task(task_id="T002", description="Start B"),
            Task(task_id="T003", description="Merge", dependencies=["T001", "T002"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        batches = graph.get_parallel_batches()
        assert set(batches[0]) == {"T001", "T002"}
        assert batches[1] == ["T003"]

    def test_task_with_multiple_dependencies(self):
        """Test task that depends on multiple other tasks."""
        tasks = [
            Task(task_id="T001", description="Dep A"),
            Task(task_id="T002", description="Dep B"),
            Task(task_id="T003", description="Dep C"),
            Task(task_id="T004", description="Main", dependencies=["T001", "T002", "T003"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        deps = graph.get_dependencies("T004")
        assert set(deps) == {"T001", "T002", "T003"}

        is_valid, errors = graph.validate()
        assert is_valid is True

    def test_execution_order_consistency(self):
        """Test that execution order is consistent across multiple calls."""
        tasks = [
            Task(task_id="T001", description="Base"),
            Task(task_id="T002", description="A", dependencies=["T001"]),
            Task(task_id="T003", description="B", dependencies=["T001"]),
        ]

        graph = DependencyGraphBuilder(tasks)

        order1 = graph.get_execution_order()
        order2 = graph.get_execution_order()
        order3 = graph.get_execution_order()

        # Should be consistent (deterministic)
        assert order1 == order2 == order3
