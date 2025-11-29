"""Task context loader for AC validation in /jpspec:validate command.

This module provides the foundational capability to load backlog tasks,
parse acceptance criteria into structured format, and determine validation
approach (automated vs manual) for each AC.
"""

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class TaskContextError(Exception):
    """Base exception for task context loading errors."""

    pass


class TaskNotFoundError(TaskContextError):
    """Raised when a task cannot be found."""

    pass


class NoInProgressTaskError(TaskContextError):
    """Raised when no in-progress task exists."""

    pass


class InvalidTaskIDError(TaskContextError):
    """Raised when task ID format is invalid."""

    pass


@dataclass
class AcceptanceCriterion:
    """Represents a single acceptance criterion with validation metadata.

    Attributes:
        index: The AC index number (e.g., 1, 2, 3)
        text: The AC description text
        checked: Whether the AC is marked as complete
        validation_approach: How to validate ('automated', 'manual', 'hybrid')
    """

    index: int
    text: str
    checked: bool
    validation_approach: str = "manual"  # default to manual


@dataclass
class TaskContext:
    """Complete context for a task including metadata and validation plan.

    Attributes:
        task_id: Task identifier (e.g., 'task-88')
        title: Task title
        description: Task description
        status: Current task status
        priority: Task priority level
        labels: List of task labels
        acceptance_criteria: List of AcceptanceCriterion objects
        related_files: List of related code file paths
        related_tests: List of related test file paths
        validation_plan: List of validation steps/approaches
        implementation_notes: Optional implementation notes from task
    """

    task_id: str
    title: str
    description: str
    status: str = "To Do"
    priority: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriterion] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    related_tests: List[str] = field(default_factory=list)
    validation_plan: List[str] = field(default_factory=list)
    implementation_notes: Optional[str] = None


def load_task_context(task_id: Optional[str] = None) -> TaskContext:
    """Load task context from backlog.

    Args:
        task_id: Optional task ID (e.g., '88' or 'task-88'). If None,
                finds the current in-progress task.

    Returns:
        TaskContext object with all parsed task information

    Raises:
        TaskNotFoundError: If the specified task doesn't exist
        NoInProgressTaskError: If no task ID provided and no in-progress task found
        InvalidTaskIDError: If task ID format is invalid
    """
    # If no task ID provided, find in-progress task
    if task_id is None:
        task_id = _find_in_progress_task()

    # Normalize task ID (handle both 'task-88' and '88' formats)
    task_id = _normalize_task_id(task_id)

    # Retrieve task details via backlog CLI
    raw_output = _get_task_output(task_id)

    # Parse the output
    return _parse_task_output(raw_output, task_id)


def _find_in_progress_task() -> str:
    """Find the current in-progress task.

    Returns:
        Task ID of the in-progress task

    Raises:
        NoInProgressTaskError: If no in-progress task found
    """
    try:
        result = subprocess.run(
            ["backlog", "task", "list", "-s", "In Progress", "--plain"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        # Parse the output to find first task ID
        # Format: "  [HIGH] task-88 - Task Title"
        pattern = r"task-(\d+)"
        match = re.search(pattern, result.stdout)

        if not match:
            raise NoInProgressTaskError("No in-progress task found")

        return f"task-{match.group(1)}"

    except subprocess.TimeoutExpired:
        raise TaskContextError("Timeout while listing in-progress tasks")
    except subprocess.CalledProcessError as e:
        stderr = getattr(e, "stderr", "")
        raise TaskContextError(f"Failed to list in-progress tasks: {stderr}")


def _normalize_task_id(task_id: str) -> str:
    """Normalize task ID to standard format.

    Args:
        task_id: Task ID in various formats ('88', 'task-88', etc.)

    Returns:
        Normalized task ID in 'task-NNN' format

    Raises:
        InvalidTaskIDError: If task ID format is invalid
    """
    # Remove whitespace
    task_id = task_id.strip()

    # If it's just a number, prepend 'task-'
    if task_id.isdigit():
        return f"task-{task_id}"

    # If it already has 'task-' prefix, validate format
    if task_id.startswith("task-"):
        # Extract number part
        num_part = task_id[5:]  # Skip 'task-'
        if num_part.isdigit():
            return task_id
        raise InvalidTaskIDError(f"Invalid task ID format: {task_id}")

    raise InvalidTaskIDError(f"Invalid task ID format: {task_id}")


def _get_task_output(task_id: str) -> str:
    """Get task output from backlog CLI.

    Args:
        task_id: Normalized task ID

    Returns:
        Raw output from backlog CLI

    Raises:
        TaskNotFoundError: If task doesn't exist
        TaskContextError: If CLI command fails
    """
    try:
        # Extract just the number for the CLI command
        task_num = task_id.split("-")[1]

        result = subprocess.run(
            ["backlog", "task", task_num, "--plain"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        return result.stdout

    except subprocess.TimeoutExpired:
        raise TaskContextError(f"Timeout while retrieving task {task_id}")
    except subprocess.CalledProcessError as e:
        stderr = getattr(e, "stderr", "")
        if "not found" in stderr.lower():
            raise TaskNotFoundError(f"Task {task_id} not found")
        raise TaskContextError(f"Failed to retrieve task {task_id}: {stderr}")


def _parse_task_output(raw_output: str, task_id: str) -> TaskContext:
    """Parse backlog task output into TaskContext.

    Args:
        raw_output: Raw output from backlog CLI
        task_id: Task ID for reference

    Returns:
        Parsed TaskContext object
    """
    lines = raw_output.split("\n")

    # Parse header (first line contains task ID and title)
    title = _extract_title(lines)
    status = _extract_status(lines)
    priority = _extract_priority(lines)
    labels = _extract_labels(lines)
    description = _extract_section(lines, "Description:")
    acceptance_criteria = parse_acceptance_criteria(raw_output)
    implementation_notes = _extract_section(lines, "Implementation Notes:")

    # Find related files from description and notes
    related_files = find_related_files(description, implementation_notes or "")

    # Find related tests
    related_tests = _find_related_tests(related_files, description, title)

    # Determine validation approach for each AC
    for ac in acceptance_criteria:
        ac.validation_approach = determine_validation_approach(ac, related_tests)

    # Build validation plan
    validation_plan = _build_validation_plan(acceptance_criteria)

    return TaskContext(
        task_id=task_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        labels=labels,
        acceptance_criteria=acceptance_criteria,
        related_files=related_files,
        related_tests=related_tests,
        validation_plan=validation_plan,
        implementation_notes=implementation_notes,
    )


def _extract_title(lines: List[str]) -> str:
    """Extract task title from output lines."""
    # Title is in first line after "Task task-NNN - "
    for line in lines:
        if line.startswith("Task task-"):
            # Format: "Task task-88 - Phase 0 - Task Context Loader for AC Validation"
            parts = line.split(" - ", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return "Unknown Title"


def _extract_status(lines: List[str]) -> str:
    """Extract task status from output lines."""
    for line in lines:
        if line.startswith("Status:"):
            # Format: "Status: ○ To Do" or "Status: ✔ Done"
            status_text = line.split(":", 1)[1].strip()
            # Remove status symbols
            status_text = status_text.lstrip("○✔●◐ ").strip()
            return status_text
    return "To Do"


def _extract_priority(lines: List[str]) -> Optional[str]:
    """Extract task priority from output lines."""
    for line in lines:
        if line.startswith("Priority:"):
            priority = line.split(":", 1)[1].strip()
            return priority if priority else None
    return None


def _extract_labels(lines: List[str]) -> List[str]:
    """Extract task labels from output lines."""
    for line in lines:
        if line.startswith("Labels:"):
            labels_text = line.split(":", 1)[1].strip()
            if labels_text:
                return [label.strip() for label in labels_text.split(",")]
    return []


def _extract_section(lines: List[str], section_header: str) -> str:
    """Extract a section from task output.

    Args:
        lines: All output lines
        section_header: Section header to look for (e.g., "Description:")

    Returns:
        Section content as string
    """
    content_lines = []
    in_section = False
    separator_line = "-" * 50

    for line in lines:
        # Start of section
        if line.startswith(section_header):
            in_section = True
            continue

        # Skip separator lines
        if line.strip() == separator_line:
            continue

        # End of section (next header or separator)
        if in_section and line.strip() and not line.startswith(" ") and ":" in line:
            # Check if this is a new section header
            if line.endswith(":") and line.strip() and line.strip()[0].isupper():
                break

        # Collect content
        if in_section and line.strip():
            content_lines.append(line.strip())

    return "\n".join(content_lines).strip()


def parse_acceptance_criteria(raw_output: str) -> List[AcceptanceCriterion]:
    """Parse acceptance criteria from task output.

    Args:
        raw_output: Raw output from backlog CLI

    Returns:
        List of AcceptanceCriterion objects
    """
    criteria = []

    # Find the Acceptance Criteria section
    lines = raw_output.split("\n")
    in_ac_section = False

    # Pattern: "- [ ] #1 Some criterion text" or "- [x] #2 Completed criterion"
    ac_pattern = re.compile(r"^-\s+\[([x ])\]\s+#(\d+)\s+(.+)$")

    for line in lines:
        # Start of AC section
        if line.startswith("Acceptance Criteria:"):
            in_ac_section = True
            continue

        # End of AC section (next section header)
        if (
            in_ac_section
            and line.strip()
            and line.strip()[0].isupper()
            and line.endswith(":")
        ):
            break

        # Parse AC line
        if in_ac_section:
            match = ac_pattern.match(line.strip())
            if match:
                checked = match.group(1).lower() == "x"
                index = int(match.group(2))
                text = match.group(3).strip()

                criteria.append(
                    AcceptanceCriterion(
                        index=index,
                        text=text,
                        checked=checked,
                        validation_approach="manual",
                    )
                )

    return criteria


def find_related_files(description: str, notes: str) -> List[str]:
    """Find related code files mentioned in task description or notes.

    Args:
        description: Task description text
        notes: Implementation notes text

    Returns:
        List of file paths found in the text
    """
    files = []
    combined_text = f"{description}\n{notes}"

    # Pattern to match file paths (various formats)
    patterns = [
        # Backtick quoted paths
        r"`([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)`",
        # Double quoted paths
        r'"([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)"',
        # Common file path references
        r"(?:in|to|at|from|file|module)\s+([a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)",
        # Standalone paths with extensions
        r"\b([a-zA-Z0-9_]+/[a-zA-Z0-9_/.-]+\.[a-zA-Z0-9]+)\b",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, combined_text)
        for match in matches:
            file_path = match.group(1)
            # Filter out common false positives
            if not any(
                exclude in file_path
                for exclude in ["http://", "https://", "www.", ".com", ".org"]
            ):
                if file_path not in files:
                    files.append(file_path)

    return files


def _find_related_tests(
    related_files: List[str], description: str, title: str
) -> List[str]:
    """Find related test files based on code files and task context.

    Args:
        related_files: List of related code files
        description: Task description
        title: Task title

    Returns:
        List of related test file paths
    """
    tests = []

    # For each code file, try to find corresponding test file
    for file_path in related_files:
        # Skip if it's already a test file
        if "test" in file_path.lower():
            tests.append(file_path)
            continue

        # Extract module name and extension
        path_obj = Path(file_path)
        module_name = path_obj.stem  # filename without extension
        extension = path_obj.suffix

        # Common test file patterns
        test_patterns = [
            f"test_{module_name}{extension}",  # test_module.py
            f"{module_name}.test{extension}",  # module.test.py
            f"{module_name}_test{extension}",  # module_test.py
            f"test{extension}",  # test.py in same directory
        ]

        for pattern in test_patterns:
            # Check if pattern exists in related files or description
            if pattern in description.lower() or pattern in title.lower():
                test_path = str(path_obj.parent / pattern)
                if test_path not in tests:
                    tests.append(test_path)

    # Also look for test file references in description/title directly
    test_keywords = ["test", "spec", "e2e", "integration"]
    for keyword in test_keywords:
        if keyword in description.lower() or keyword in title.lower():
            # Try to extract test file names
            for file_ref in related_files:
                if keyword in file_ref.lower() and file_ref not in tests:
                    tests.append(file_ref)

    return tests


def determine_validation_approach(
    ac: AcceptanceCriterion, related_tests: List[str]
) -> str:
    """Determine validation approach for an acceptance criterion.

    Args:
        ac: Acceptance criterion to evaluate
        related_tests: List of related test files

    Returns:
        Validation approach: 'automated', 'manual', or 'hybrid'
    """
    ac_lower = ac.text.lower()

    # Keywords indicating automated testing is possible
    automated_keywords = [
        "api",
        "endpoint",
        "function",
        "returns",
        "output",
        "response",
        "parse",
        "calculate",
        "validate",
        "process",
    ]

    # Keywords indicating manual validation required
    manual_keywords = [
        "user",
        "ui",
        "interface",
        "design",
        "readable",
        "understandable",
        "experience",
        "displays",
        "shows",
    ]

    has_automated_keywords = any(keyword in ac_lower for keyword in automated_keywords)
    has_manual_keywords = any(keyword in ac_lower for keyword in manual_keywords)

    # If we have test files and AC has automated keywords
    if related_tests and has_automated_keywords:
        if has_manual_keywords:
            return "hybrid"
        return "automated"

    # If only manual keywords
    if has_manual_keywords:
        return "manual"

    # If has automated keywords but no tests
    if has_automated_keywords:
        return "hybrid"

    # Default to manual
    return "manual"


def _build_validation_plan(criteria: List[AcceptanceCriterion]) -> List[str]:
    """Build validation plan based on acceptance criteria.

    Args:
        criteria: List of acceptance criteria

    Returns:
        List of validation steps
    """
    plan = []

    automated = [ac for ac in criteria if ac.validation_approach == "automated"]
    manual = [ac for ac in criteria if ac.validation_approach == "manual"]
    hybrid = [ac for ac in criteria if ac.validation_approach == "hybrid"]

    if automated:
        plan.append(
            f"Run automated tests for ACs: {', '.join(f'#{ac.index}' for ac in automated)}"
        )

    if hybrid:
        plan.append(
            f"Run tests + manual review for ACs: {', '.join(f'#{ac.index}' for ac in hybrid)}"
        )

    if manual:
        plan.append(
            f"Manual validation required for ACs: {', '.join(f'#{ac.index}' for ac in manual)}"
        )

    return plan
