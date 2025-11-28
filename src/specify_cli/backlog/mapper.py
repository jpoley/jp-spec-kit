"""
Task mapper for converting jp-spec-kit format to Backlog.md format.

Provides high-level API for the complete conversion process.
"""

from pathlib import Path
from .parser import TaskParser, Task
from .writer import BacklogWriter
from .dependency_graph import DependencyGraphBuilder


class TaskMapper:
    """Maps jp-spec-kit tasks to Backlog.md format."""

    def __init__(self, backlog_dir: Path):
        """
        Initialize the mapper.

        Args:
            backlog_dir: Path to the backlog directory (e.g., ./backlog)
        """
        self.backlog_dir = Path(backlog_dir)
        self.parser = TaskParser()
        self.writer = BacklogWriter(backlog_dir)

    def generate_from_tasks_file(
        self,
        tasks_file: Path,
        *,
        overwrite: bool = False,
        dry_run: bool = False
    ) -> dict:
        """
        Generate Backlog.md tasks from a jp-spec-kit tasks.md file.

        Args:
            tasks_file: Path to tasks.md file
            overwrite: Whether to overwrite existing task files
            dry_run: If True, parse and validate but don't write files

        Returns:
            Dictionary with generation results and statistics
        """
        # Parse tasks
        tasks = self.parser.parse_tasks_file(tasks_file)

        if not tasks:
            return {
                'success': False,
                'error': 'No tasks found in file',
                'tasks_parsed': 0,
            }

        # Build dependency graph and validate
        graph = DependencyGraphBuilder(tasks)
        is_valid, errors = graph.validate()

        if not is_valid:
            return {
                'success': False,
                'error': 'Invalid dependency graph',
                'validation_errors': errors,
                'tasks_parsed': len(tasks),
            }

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'tasks_parsed': len(tasks),
                'tasks_by_phase': self._group_by_phase(tasks),
                'tasks_by_story': self._group_by_story(tasks),
                'execution_order': graph.get_execution_order(),
                'parallel_batches': graph.get_parallel_batches(),
                'critical_path': graph.get_critical_path(),
            }

        # Write tasks
        created_files = self.writer.write_tasks(
            tasks,
            overwrite=overwrite
        )

        # Generate summary
        return {
            'success': True,
            'tasks_parsed': len(tasks),
            'tasks_created': len(created_files),
            'tasks_by_phase': self._group_by_phase(tasks),
            'tasks_by_story': self._group_by_story(tasks),
            'execution_order': graph.get_execution_order(),
            'parallel_batches': graph.get_parallel_batches(),
            'critical_path': graph.get_critical_path(),
            'created_files': [str(f) for f in created_files],
        }

    def generate_from_spec(
        self,
        spec_dir: Path,
        *,
        overwrite: bool = False,
        dry_run: bool = False
    ) -> dict:
        """
        Generate Backlog.md tasks from spec directory.

        Args:
            spec_dir: Path to directory containing spec.md, plan.md, etc.
            overwrite: Whether to overwrite existing task files
            dry_run: If True, parse and validate but don't write files

        Returns:
            Dictionary with generation results and statistics
        """
        # Look for tasks.md first
        tasks_file = spec_dir / "tasks.md"

        if tasks_file.exists():
            return self.generate_from_tasks_file(
                tasks_file,
                overwrite=overwrite,
                dry_run=dry_run
            )

        # If no tasks.md, try to parse from spec.md and plan.md
        spec_file = spec_dir / "spec.md"
        plan_file = spec_dir / "plan.md"

        if not spec_file.exists():
            return {
                'success': False,
                'error': 'No spec.md or tasks.md found',
            }

        # Parse user stories from spec
        user_stories = self.parser.parse_spec_file(spec_file)

        # Parse plan if available
        plan_info = {}
        if plan_file.exists():
            plan_info = self.parser.parse_plan_file(plan_file)

        # Generate tasks from user stories
        # This is a simplified version - full implementation would need more sophisticated task generation
        tasks = self._generate_tasks_from_stories(user_stories, plan_info)

        if not tasks:
            return {
                'success': False,
                'error': 'No tasks could be generated from spec',
                'user_stories': len(user_stories),
            }

        # Build dependency graph
        graph = DependencyGraphBuilder(tasks)

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'tasks_generated': len(tasks),
                'user_stories': len(user_stories),
                'tasks_by_story': self._group_by_story(tasks),
            }

        # Write tasks
        created_files = self.writer.write_tasks(
            tasks,
            overwrite=overwrite
        )

        return {
            'success': True,
            'tasks_generated': len(tasks),
            'tasks_created': len(created_files),
            'user_stories': len(user_stories),
            'tasks_by_story': self._group_by_story(tasks),
            'created_files': [str(f) for f in created_files],
        }

    def _generate_tasks_from_stories(
        self,
        user_stories: dict,
        plan_info: dict
    ) -> list[Task]:
        """
        Generate tasks from parsed user stories and plan.

        This is a simplified implementation - full version would need more
        sophisticated task generation logic based on project type, tech stack, etc.

        Args:
            user_stories: Dictionary of user stories from spec.md
            plan_info: Dictionary of plan information from plan.md

        Returns:
            List of generated Task objects
        """
        tasks = []
        task_counter = 1

        # Generate setup tasks
        tasks.append(Task(
            task_id=f"T{task_counter:03d}",
            description="Set up project structure and dependencies",
            phase="Setup",
        ))
        task_counter += 1

        # Generate tasks for each user story
        for story_id, story_data in sorted(user_stories.items()):
            story_title = story_data.get('title', story_id)

            # Create task for the user story
            tasks.append(Task(
                task_id=f"T{task_counter:03d}",
                description=f"Implement {story_title}",
                user_story=story_id,
                phase=f"User Story {story_id.replace('US', '')}",
            ))
            task_counter += 1

        return tasks

    def _group_by_phase(self, tasks: list[Task]) -> dict:
        """Group tasks by phase."""
        by_phase = {}
        for task in tasks:
            phase = task.phase or "Unknown"
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(task.task_id)
        return by_phase

    def _group_by_story(self, tasks: list[Task]) -> dict:
        """Group tasks by user story."""
        by_story = {}
        for task in tasks:
            story = task.user_story or "No Story"
            if story not in by_story:
                by_story[story] = []
            by_story[story].append(task.task_id)
        return by_story

    def regenerate(
        self,
        tasks_file: Path,
        *,
        conflict_strategy: str = "skip"
    ) -> dict:
        """
        Regenerate tasks with conflict detection.

        Args:
            tasks_file: Path to tasks.md file
            conflict_strategy: How to handle conflicts ("skip", "overwrite", "merge")

        Returns:
            Dictionary with regeneration results
        """
        # Parse new tasks
        new_tasks = self.parser.parse_tasks_file(tasks_file)

        # Check for existing tasks
        existing_files = list(self.writer.tasks_dir.glob("task-*.md"))

        conflicts = []
        for task in new_tasks:
            task_file = self.writer._get_task_file_path(task)
            if task_file.exists():
                conflicts.append(task.task_id)

        if conflicts and conflict_strategy == "skip":
            return {
                'success': False,
                'error': 'Conflicts detected',
                'conflicts': conflicts,
                'message': 'Use conflict_strategy="overwrite" to force regeneration',
            }

        # Write based on strategy
        overwrite = conflict_strategy == "overwrite"
        created_files = self.writer.write_tasks(new_tasks, overwrite=overwrite)

        return {
            'success': True,
            'tasks_regenerated': len(created_files),
            'conflicts_resolved': len(conflicts) if overwrite else 0,
            'conflicts_skipped': len(conflicts) if not overwrite else 0,
        }

    def get_stats(self) -> dict:
        """
        Get statistics about current backlog.

        Returns:
            Dictionary with task statistics
        """
        return self.writer.get_task_stats()


def generate_backlog_tasks(
    source_path: Path,
    backlog_dir: Path,
    *,
    overwrite: bool = False,
    dry_run: bool = False
) -> dict:
    """
    Convenience function to generate Backlog.md tasks.

    Args:
        source_path: Path to tasks.md file or spec directory
        backlog_dir: Path to backlog directory
        overwrite: Whether to overwrite existing tasks
        dry_run: If True, parse and validate but don't write files

    Returns:
        Dictionary with generation results
    """
    mapper = TaskMapper(backlog_dir)

    if source_path.is_file() and source_path.name == "tasks.md":
        return mapper.generate_from_tasks_file(
            source_path,
            overwrite=overwrite,
            dry_run=dry_run
        )
    elif source_path.is_dir():
        return mapper.generate_from_spec(
            source_path,
            overwrite=overwrite,
            dry_run=dry_run
        )
    else:
        return {
            'success': False,
            'error': f'Invalid source path: {source_path}',
        }
