"""Context Injector - Inject task memory into AI agent context.

This module manages injection of task memory into CLAUDE.md and other agent
configuration files. It provides automatic context loading for Claude Code
and other AI agents via the @import directive.

The injector maintains an "Active Task Context" section in backlog/CLAUDE.md
that includes @import directives for active task memory files.

Example:
    ```python
    from specify_cli.memory.injector import ContextInjector

    injector = ContextInjector()
    injector.update_active_task("task-375")  # Add @import for task-375
    injector.clear_active_task()             # Remove @import
    ```
"""

import re
from pathlib import Path
from typing import Optional


class ContextInjector:
    """Manages injection of task memory into CLAUDE.md and other agent configs.

    Attributes:
        base_path: Root directory of the project
        claude_md_path: Path to backlog/CLAUDE.md file
    """

    # Template for the Active Task Context section
    ACTIVE_TASK_SECTION_TEMPLATE = """
## Active Task Context

{content}
"""

    # Regex to find the Active Task Context section
    ACTIVE_TASK_SECTION_REGEX = re.compile(
        r"^## Active Task Context\s*\n(.*?)(?=\n## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize injector with optional custom base path.

        Args:
            base_path: Root directory of the project. Defaults to current working directory.
        """
        self.base_path = base_path or Path.cwd()
        self.claude_md_path = self.base_path / "backlog" / "CLAUDE.md"

    def update_active_task(self, task_id: Optional[str] = None) -> None:
        """Update CLAUDE.md with @import for active task memory.

        This method adds or updates the "Active Task Context" section in
        backlog/CLAUDE.md with an @import directive for the specified task's
        memory file.

        Args:
            task_id: Task identifier (e.g., "task-375"). If None, clears the section.

        Raises:
            FileNotFoundError: If CLAUDE.md doesn't exist
        """
        if not self.claude_md_path.exists():
            raise FileNotFoundError(f"CLAUDE.md not found: {self.claude_md_path}")

        content = self.claude_md_path.read_text()

        if task_id is None:
            # Clear the section
            new_section = ""
        else:
            # Create import directive for the task memory file
            memory_path = f"../memory/{task_id}.md"
            new_section = self.ACTIVE_TASK_SECTION_TEMPLATE.format(
                content=f"@import {memory_path}\n"
            )

        # Replace or add the section
        if self.ACTIVE_TASK_SECTION_REGEX.search(content):
            # Section exists - replace it
            if new_section:
                new_content = self.ACTIVE_TASK_SECTION_REGEX.sub(
                    new_section.rstrip() + "\n", content
                )
            else:
                # Remove the section entirely
                new_content = self.ACTIVE_TASK_SECTION_REGEX.sub("", content)
        else:
            # Section doesn't exist - add it at the end
            if new_section:
                new_content = content.rstrip() + "\n\n" + new_section.rstrip() + "\n"
            else:
                new_content = content

        # Clean up multiple consecutive blank lines
        new_content = re.sub(r"\n{3,}", "\n\n", new_content)

        self.claude_md_path.write_text(new_content)

    def clear_active_task(self) -> None:
        """Remove task memory @import from CLAUDE.md.

        This is a convenience method equivalent to update_active_task(None).

        Raises:
            FileNotFoundError: If CLAUDE.md doesn't exist
        """
        self.update_active_task(None)

    def get_active_task_id(self) -> Optional[str]:
        """Get currently active task ID from CLAUDE.md.

        Parses the "Active Task Context" section to extract the task ID
        from the @import directive.

        Returns:
            Task ID if found (e.g., "task-375"), None otherwise

        Raises:
            FileNotFoundError: If CLAUDE.md doesn't exist
        """
        if not self.claude_md_path.exists():
            raise FileNotFoundError(f"CLAUDE.md not found: {self.claude_md_path}")

        content = self.claude_md_path.read_text()

        # Find the Active Task Context section
        match = self.ACTIVE_TASK_SECTION_REGEX.search(content)
        if not match:
            return None

        section_content = match.group(1)

        # Extract task ID from @import directive
        # Format: @import ../memory/task-XXX.md
        import_match = re.search(
            r"@import\s+\.\./memory/(task-\d+)\.md", section_content
        )
        if import_match:
            return import_match.group(1)

        return None
