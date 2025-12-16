"""
Task parser for flowspec format.

Parses tasks from spec.md, plan.md, and tasks.md files following the
flowspec task format conventions.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Task:
    """Represents a single task parsed from flowspec format."""

    task_id: str  # e.g., "T001", "T002"
    description: str  # Task description
    file_path: Optional[str] = None  # File path mentioned in description
    is_parallelizable: bool = False  # Has [P] marker
    user_story: Optional[str] = None  # e.g., "US1", "US2"
    phase: Optional[str] = None  # e.g., "Setup", "Foundational", "User Story 1"
    is_completed: bool = False  # Checkbox state
    dependencies: list[str] = field(
        default_factory=list
    )  # List of task IDs this depends on
    priority: Optional[str] = None  # e.g., "P0", "P1", "P2"

    @property
    def labels(self) -> list[str]:
        """Generate labels for Backlog.md format."""
        labels = []

        if self.user_story:
            labels.append(self.user_story)

        if self.is_parallelizable:
            labels.append("parallelizable")

        if self.priority:
            labels.append(self.priority)

        # Infer phase-based labels
        if self.phase:
            phase_lower = self.phase.lower()
            if "setup" in phase_lower:
                labels.append("setup")
            elif "foundational" in phase_lower:
                labels.append("foundational")
            elif "polish" in phase_lower:
                labels.append("polish")
            elif "user story" in phase_lower or self.user_story:
                labels.append("implementation")

        return labels


class TaskParser:
    """Parser for flowspec task format."""

    # Regex pattern for task format:
    # - [ ] T001 [P] [US1] Task description with file path
    TASK_PATTERN = re.compile(
        r"^-\s+\[(?P<checked>[ xX])\]\s+"  # Checkbox
        r"(?P<task_id>T\d+)\s+"  # Task ID (T001, T002, etc.)
        r"(?:\[P\]\s+)?"  # Optional [P] marker
        r"(?:\[(?P<user_story>US\d+)\]\s+)?"  # Optional [US#] label
        r"(?P<description>.+)$"  # Description (rest of line)
    )

    # Pattern to extract file path from description
    FILE_PATH_PATTERN = re.compile(r'(?:in|to|at|from)\s+([`"]?)([^\s`"]+\.[\w]+)\1')

    # Pattern to extract priority from labels
    PRIORITY_PATTERN = re.compile(r"\[P(\d+)\]")

    def __init__(self):
        """Initialize the parser."""
        self.tasks: list[Task] = []
        self.current_phase: Optional[str] = None

    def parse_tasks_file(self, file_path: Path) -> list[Task]:
        """
        Parse tasks from a tasks.md file.

        Args:
            file_path: Path to the tasks.md file

        Returns:
            List of parsed Task objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Tasks file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_tasks_content(content)

    def parse_tasks_content(self, content: str) -> list[Task]:
        """
        Parse tasks from markdown content.

        Args:
            content: Markdown content containing tasks

        Returns:
            List of parsed Task objects
        """
        self.tasks = []
        self.current_phase = None

        lines = content.split("\n")

        for line in lines:
            # Check for phase headers
            if line.startswith("## Phase") or line.startswith("### Phase"):
                self.current_phase = line.strip("#").strip()
                continue

            # Try to parse task
            task = self._parse_task_line(line)
            if task:
                task.phase = self.current_phase
                self.tasks.append(task)

        # Build dependency graph based on task order and phases
        self._infer_dependencies()

        return self.tasks

    def _parse_task_line(self, line: str) -> Optional[Task]:
        """
        Parse a single task line.

        Args:
            line: A single line of markdown content

        Returns:
            Task object if line matches pattern, None otherwise
        """
        match = self.TASK_PATTERN.match(line.strip())
        if not match:
            return None

        # Extract basic fields
        is_completed = match.group("checked").lower() == "x"
        task_id = match.group("task_id")
        user_story = match.group("user_story")
        description = match.group("description").strip()

        # Check for [P] marker (parallelizable)
        is_parallelizable = "[P]" in line

        # Extract file path from description
        file_path = self._extract_file_path(description)

        # Extract priority from description or task ID context
        priority = self._extract_priority(description)

        return Task(
            task_id=task_id,
            description=description,
            file_path=file_path,
            is_parallelizable=is_parallelizable,
            user_story=user_story,
            is_completed=is_completed,
            priority=priority,
        )

    def _extract_file_path(self, description: str) -> Optional[str]:
        """Extract file path from task description."""
        match = self.FILE_PATH_PATTERN.search(description)
        if match:
            return match.group(2)
        return None

    def _extract_priority(self, description: str) -> Optional[str]:
        """Extract priority label from description."""
        match = self.PRIORITY_PATTERN.search(description)
        if match:
            return f"P{match.group(1)}"
        return None

    def _infer_dependencies(self):
        """
        Infer task dependencies based on:
        1. Phase order (Setup → Foundational → User Stories → Polish)
        2. Same user story tasks depend on earlier tasks in that story
        3. Cross-phase dependencies (foundational blocks all user stories)
        """
        phase_order = {
            "setup": 0,
            "foundational": 1,
            "user story": 2,
            "polish": 3,
        }

        # Group tasks by phase
        tasks_by_phase = {}
        for task in self.tasks:
            if not task.phase:
                continue

            phase_key = None
            for key in phase_order.keys():
                if key in task.phase.lower():
                    phase_key = key
                    break

            if phase_key not in tasks_by_phase:
                tasks_by_phase[phase_key] = []
            tasks_by_phase[phase_key].append(task)

        # Foundational tasks depend on setup tasks
        if "setup" in tasks_by_phase and "foundational" in tasks_by_phase:
            last_setup_task = tasks_by_phase["setup"][-1]
            for task in tasks_by_phase["foundational"]:
                if not task.is_parallelizable:
                    task.dependencies.append(last_setup_task.task_id)

        # User story tasks depend on foundational tasks
        if "foundational" in tasks_by_phase and "user story" in tasks_by_phase:
            last_foundational_task = tasks_by_phase["foundational"][-1]
            for task in tasks_by_phase["user story"]:
                # Only add dependency if it's the first task of a user story
                if task.user_story and not any(
                    t.user_story == task.user_story and t.task_id < task.task_id
                    for t in self.tasks
                ):
                    task.dependencies.append(last_foundational_task.task_id)

    def parse_spec_file(self, file_path: Path) -> dict:
        """
        Parse user stories from spec.md file.

        Args:
            file_path: Path to spec.md

        Returns:
            Dictionary mapping user story IDs to their details
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Spec file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple user story extraction
        # Look for patterns like "## User Story 1", "## User Story 2", etc.
        user_stories = {}
        current_story = None

        for line in content.split("\n"):
            if line.startswith("## User Story"):
                # Extract story number
                match = re.search(r"User Story\s+(\d+)", line)
                if match:
                    story_num = match.group(1)
                    current_story = f"US{story_num}"
                    user_stories[current_story] = {
                        "title": line.strip("#").strip(),
                        "content": [],
                    }
            elif current_story and line.strip():
                user_stories[current_story]["content"].append(line)

        return user_stories

    def parse_plan_file(self, file_path: Path) -> dict:
        """
        Parse implementation plan from plan.md file.

        Args:
            file_path: Path to plan.md

        Returns:
            Dictionary with plan details (tech stack, structure, etc.)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Plan file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        plan_info = {"tech_stack": [], "project_structure": [], "libraries": []}

        # Extract tech stack, libraries, project structure
        # This is a simplified extraction - can be enhanced based on actual plan.md format
        current_section = None

        for line in content.split("\n"):
            line_lower = line.lower()

            if "tech stack" in line_lower or "technology" in line_lower:
                current_section = "tech_stack"
            elif "project structure" in line_lower or "directory" in line_lower:
                current_section = "project_structure"
            elif "libraries" in line_lower or "dependencies" in line_lower:
                current_section = "libraries"
            elif line.strip().startswith("-") and current_section:
                item = line.strip("- ").strip()
                if item:
                    plan_info[current_section].append(item)

        return plan_info


# Convenience function for quick parsing
def parse_tasks(file_path: Path) -> list[Task]:
    """
    Parse tasks from a flowspec tasks.md file.

    Args:
        file_path: Path to tasks.md file

    Returns:
        List of parsed Task objects
    """
    parser = TaskParser()
    return parser.parse_tasks_file(file_path)
