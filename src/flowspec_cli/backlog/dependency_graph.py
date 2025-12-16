"""
Dependency graph builder for flowspec tasks.

Builds and visualizes task dependencies to help with planning and execution.
"""

from typing import Optional
from collections import defaultdict
from .parser import Task


class DependencyGraphBuilder:
    """Builder for task dependency graphs."""

    def __init__(self, tasks: list[Task]):
        """
        Initialize the dependency graph builder.

        Args:
            tasks: List of Task objects to build graph from
        """
        self.tasks = tasks
        self.task_map = {task.task_id: task for task in tasks}
        self.graph: dict[str, list[str]] = defaultdict(list)
        self._build_graph()

    def _build_graph(self):
        """Build adjacency list representation of dependency graph."""
        for task in self.tasks:
            # Add edges from dependencies to this task
            for dep_id in task.dependencies:
                self.graph[dep_id].append(task.task_id)

            # Ensure task has entry even if no dependents
            if task.task_id not in self.graph:
                self.graph[task.task_id] = []

    def get_dependencies(self, task_id: str) -> list[str]:
        """
        Get direct dependencies for a task.

        Args:
            task_id: Task ID (e.g., "T001")

        Returns:
            List of task IDs that this task depends on
        """
        if task_id not in self.task_map:
            return []
        return self.task_map[task_id].dependencies

    def get_dependents(self, task_id: str) -> list[str]:
        """
        Get tasks that depend on this task.

        Args:
            task_id: Task ID (e.g., "T001")

        Returns:
            List of task IDs that depend on this task
        """
        return self.graph.get(task_id, [])

    def get_all_dependencies(
        self, task_id: str, visited: Optional[set] = None
    ) -> list[str]:
        """
        Get all transitive dependencies for a task (recursively).

        Args:
            task_id: Task ID (e.g., "T001")
            visited: Set of already visited task IDs (for cycle detection)

        Returns:
            List of all task IDs that this task depends on (directly or indirectly)
        """
        if visited is None:
            visited = set()

        if task_id in visited or task_id not in self.task_map:
            return []

        visited.add(task_id)
        all_deps = []

        for dep_id in self.get_dependencies(task_id):
            all_deps.append(dep_id)
            all_deps.extend(self.get_all_dependencies(dep_id, visited))

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for dep in all_deps:
            if dep not in seen:
                seen.add(dep)
                result.append(dep)

        return result

    def get_execution_order(self) -> list[str]:
        """
        Get tasks in execution order using topological sort.

        Returns:
            List of task IDs in execution order

        Raises:
            ValueError: If circular dependency detected
        """
        # Kahn's algorithm for topological sort
        in_degree = defaultdict(int)

        # Calculate in-degrees
        for task_id in self.task_map.keys():
            in_degree[task_id] = len(self.get_dependencies(task_id))

        # Queue of tasks with no dependencies
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort by task ID to ensure consistent ordering
            queue.sort()
            task_id = queue.pop(0)
            result.append(task_id)

            # Reduce in-degree for dependent tasks
            for dependent in self.get_dependents(task_id):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycles
        if len(result) != len(self.task_map):
            missing = set(self.task_map.keys()) - set(result)
            raise ValueError(f"Circular dependency detected involving tasks: {missing}")

        return result

    def get_parallel_batches(self) -> list[list[str]]:
        """
        Get tasks grouped into parallel execution batches.

        Tasks in the same batch can be executed in parallel.
        Each batch must complete before the next batch can start.

        Returns:
            List of batches, where each batch is a list of task IDs
        """
        # Build batches using level-by-level topological sort
        in_degree = {
            task_id: len(self.get_dependencies(task_id))
            for task_id in self.task_map.keys()
        }

        batches = []
        remaining = set(self.task_map.keys())

        while remaining:
            # Find all tasks with no remaining dependencies
            current_batch = [
                task_id for task_id in remaining if in_degree[task_id] == 0
            ]

            if not current_batch:
                missing = remaining
                raise ValueError(
                    f"Circular dependency detected involving tasks: {missing}"
                )

            # Sort batch for consistent ordering
            current_batch.sort()
            batches.append(current_batch)

            # Remove batch from remaining and update in-degrees
            for task_id in current_batch:
                remaining.remove(task_id)
                for dependent in self.get_dependents(task_id):
                    in_degree[dependent] -= 1

        return batches

    def get_parallelizable_tasks(self, batch: Optional[list[str]] = None) -> list[str]:
        """
        Get tasks that are marked as parallelizable.

        Args:
            batch: Optional list of task IDs to filter from

        Returns:
            List of task IDs that are parallelizable
        """
        tasks_to_check = batch if batch else list(self.task_map.keys())

        return [
            task_id
            for task_id in tasks_to_check
            if self.task_map[task_id].is_parallelizable
        ]

    def get_critical_path(self) -> list[str]:
        """
        Get the critical path (longest path through the graph).

        Returns:
            List of task IDs on the critical path
        """
        # Use dynamic programming to find longest path
        memo = {}

        def longest_path(task_id: str) -> int:
            if task_id in memo:
                return memo[task_id]

            dependents = self.get_dependents(task_id)
            if not dependents:
                memo[task_id] = 1
                return 1

            max_length = 1 + max(longest_path(dep) for dep in dependents)
            memo[task_id] = max_length
            return max_length

        # Find task with longest path
        for task_id in self.task_map.keys():
            longest_path(task_id)

        # Reconstruct path
        if not memo:
            return []

        # Start from task with maximum path length
        current = max(memo.keys(), key=lambda k: memo[k])
        path = [current]

        # Follow longest path
        while True:
            dependents = self.get_dependents(current)
            if not dependents:
                break

            # Find dependent with longest path
            current = max(dependents, key=lambda k: memo[k])
            path.append(current)

        return path

    def to_markdown(self) -> str:
        """
        Generate markdown representation of dependency graph.

        Returns:
            Markdown string with dependency information
        """
        lines = ["# Task Dependency Graph\n"]

        # Group by phase
        tasks_by_phase = defaultdict(list)
        for task in self.tasks:
            phase = task.phase or "Unknown Phase"
            tasks_by_phase[phase].append(task)

        # Output by phase
        for phase, tasks in sorted(tasks_by_phase.items()):
            lines.append(f"\n## {phase}\n")

            for task in sorted(tasks, key=lambda t: t.task_id):
                lines.append(f"### {task.task_id}: {task.description}")

                # Dependencies
                if task.dependencies:
                    lines.append("\n**Dependencies:**")
                    for dep_id in task.dependencies:
                        dep_task = self.task_map.get(dep_id)
                        if dep_task:
                            lines.append(f"- {dep_id}: {dep_task.description}")
                        else:
                            lines.append(f"- {dep_id}")

                # Dependents
                dependents = self.get_dependents(task.task_id)
                if dependents:
                    lines.append("\n**Blocks:**")
                    for dep_id in dependents:
                        dep_task = self.task_map.get(dep_id)
                        if dep_task:
                            lines.append(f"- {dep_id}: {dep_task.description}")
                        else:
                            lines.append(f"- {dep_id}")

                # Labels
                if task.labels:
                    lines.append(f"\n**Labels:** {', '.join(task.labels)}")

                lines.append("")

        # Summary statistics
        lines.append("\n## Summary\n")
        lines.append(f"- **Total Tasks:** {len(self.tasks)}")

        batches = self.get_parallel_batches()
        lines.append(f"- **Execution Batches:** {len(batches)}")

        parallelizable = self.get_parallelizable_tasks()
        lines.append(f"- **Parallelizable Tasks:** {len(parallelizable)}")

        critical_path = self.get_critical_path()
        lines.append(f"- **Critical Path Length:** {len(critical_path)}")

        lines.append("\n### Critical Path\n")
        for task_id in critical_path:
            task = self.task_map[task_id]
            lines.append(f"1. {task_id}: {task.description}")

        lines.append("\n### Parallel Execution Batches\n")
        for i, batch in enumerate(batches, 1):
            lines.append(f"\n**Batch {i}** ({len(batch)} tasks):")
            for task_id in batch:
                task = self.task_map[task_id]
                parallel_marker = " [P]" if task.is_parallelizable else ""
                lines.append(f"- {task_id}{parallel_marker}: {task.description}")

        return "\n".join(lines)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate dependency graph for issues.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check for circular dependencies
        try:
            self.get_execution_order()
        except ValueError as e:
            errors.append(f"Circular dependency: {str(e)}")

        # Check for dangling dependencies
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in self.task_map:
                    errors.append(
                        f"Task {task.task_id} depends on non-existent task {dep_id}"
                    )

        # Check for isolated tasks (no dependencies and no dependents)
        for task_id in self.task_map.keys():
            if not self.get_dependencies(task_id) and not self.get_dependents(task_id):
                # This is just a warning, not an error
                pass

        return len(errors) == 0, errors
