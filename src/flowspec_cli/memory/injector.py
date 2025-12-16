"""Context Injector - Inject task memory into AI agent context.

This module manages injection of task memory into CLAUDE.md and other agent
configuration files. It provides automatic context loading for Claude Code
and other AI agents via the @import directive.

The injector maintains an "Active Task Context" section in backlog/CLAUDE.md
that includes @import directives for active task memory files.

Token-aware injection ensures memory doesn't exceed 2000 tokens per task,
truncating from oldest content when necessary to preserve recent context.

Example:
    ```python
    from flowspec_cli.memory.injector import ContextInjector

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
        max_tokens: Maximum tokens allowed per task (default: 2000)
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

    # Token estimation: approximately 4 characters per token
    # This is a conservative estimate based on GPT tokenization
    CHARS_PER_TOKEN = 4

    def __init__(self, base_path: Optional[Path] = None, max_tokens: int = 2000):
        """Initialize injector with optional custom base path.

        Args:
            base_path: Root directory of the project. Defaults to current working directory.
            max_tokens: Maximum tokens allowed per task memory (default: 2000)
        """
        self.base_path = base_path or Path.cwd()
        self.claude_md_path = self.base_path / "backlog" / "CLAUDE.md"
        self.max_tokens = max_tokens

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

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using character-based approximation.

        Uses a conservative estimate of ~4 characters per token, which is
        typical for English text with GPT-style tokenization.

        Args:
            text: Text to estimate token count for

        Returns:
            Estimated token count
        """
        return len(text) // self.CHARS_PER_TOKEN

    def truncate_memory_content(self, content: str) -> str:
        """Truncate memory content to stay within token limit.

        Preserves recent content by truncating from the oldest sections.
        The strategy:
        1. Always keep the header (Task Memory: {task_id}, metadata)
        2. Truncate from the Notes section first (oldest content)
        3. If still too large, truncate from Key Decisions
        4. Always preserve Context section (recent context)

        Args:
            content: Full memory content to truncate

        Returns:
            Truncated content within token limit
        """
        # Check if content is within limit
        estimated_tokens = self.estimate_tokens(content)
        if estimated_tokens <= self.max_tokens:
            return content

        max_chars = self.max_tokens * self.CHARS_PER_TOKEN

        # Try to preserve structure by keeping header and recent sections
        lines = content.split("\n")

        # Find section boundaries
        header_end = 0
        context_start = None
        key_decisions_start = None
        notes_start = None

        for i, line in enumerate(lines):
            if line.startswith("## Context"):
                context_start = i
            elif line.startswith("## Key Decisions"):
                key_decisions_start = i
            elif line.startswith("## Notes"):
                notes_start = i
            elif i < 10 and (
                line.startswith("**") or line.startswith("# Task Memory:")
            ):
                header_end = max(header_end, i)

        # Strategy: Keep header + Context, truncate Notes and Key Decisions if needed
        preserved_lines = []

        # Always keep header (first few lines with metadata)
        preserved_lines.extend(lines[: header_end + 1])

        # Always keep Context section if it exists
        if context_start is not None:
            context_end = (
                key_decisions_start
                if key_decisions_start
                else notes_start
                if notes_start
                else len(lines)
            )
            preserved_lines.extend(lines[context_start:context_end])

        # Add Key Decisions if we have space
        if key_decisions_start is not None:
            decisions_end = notes_start if notes_start else len(lines)
            decisions_section = lines[key_decisions_start:decisions_end]

            # Check if adding decisions keeps us within limit
            test_content = "\n".join(preserved_lines + decisions_section)
            if len(test_content) <= max_chars:
                preserved_lines.extend(decisions_section)

        # Add Notes section if we still have space
        # Reserve space for truncation notice (approximately 60 chars)
        truncation_notice = (
            f"*[Content truncated - exceeded {self.max_tokens} token limit]*"
        )
        reserved_space = len(truncation_notice) + 10  # +10 for newlines

        if notes_start is not None:
            notes_section = lines[notes_start:]

            # Try to add as much of notes as we can
            test_content = "\n".join(preserved_lines + notes_section)
            if len(test_content) <= max_chars - reserved_space:
                # All notes fit
                preserved_lines.extend(notes_section)
            else:
                # Add notes line by line until we hit the limit
                notes_added = False
                for line in notes_section:
                    test_content = "\n".join(preserved_lines + [line])
                    if len(test_content) > max_chars - reserved_space:
                        # Hit limit - add truncation notice
                        if notes_added:
                            preserved_lines.append("")
                            preserved_lines.append(truncation_notice)
                        break
                    preserved_lines.append(line)
                    notes_added = True

        truncated = "\n".join(preserved_lines)

        # Final safety check - hard truncate if still too large
        if len(truncated) > max_chars:
            truncated = truncated[: max_chars - len(truncation_notice) - 5]
            truncated += f"\n\n{truncation_notice}"

        return truncated

    def get_memory_path(self, task_id: str) -> Path:
        """Get the path to a task's memory file.

        Args:
            task_id: Task identifier (e.g., "task-375")

        Returns:
            Path to the memory file
        """
        return self.base_path / "backlog" / "memory" / f"{task_id}.md"

    def update_active_task_with_truncation(self, task_id: Optional[str] = None) -> None:
        """Update CLAUDE.md with @import for active task, applying token truncation.

        This method reads the task memory, applies token-aware truncation if needed,
        and writes a truncated copy for injection. The original memory file remains
        unchanged.

        Args:
            task_id: Task identifier (e.g., "task-375"). If None, clears the section.

        Raises:
            FileNotFoundError: If CLAUDE.md or memory file doesn't exist
        """
        if task_id is None:
            self.update_active_task(None)
            return

        # Read the memory file
        memory_path = self.get_memory_path(task_id)
        if not memory_path.exists():
            # Memory file doesn't exist - just add the @import anyway
            # (file might be created later, or this is intentional)
            self.update_active_task(task_id)
            return

        content = memory_path.read_text()

        # Check if truncation needed
        estimated_tokens = self.estimate_tokens(content)
        if estimated_tokens <= self.max_tokens:
            # No truncation needed - use standard injection
            self.update_active_task(task_id)
            return

        # Truncate content and write to a temporary injection file
        truncated = self.truncate_memory_content(content)

        # Write truncated version to a temp file for injection
        truncated_path = self.get_memory_path(f"{task_id}.truncated")
        truncated_path.write_text(truncated)

        # Update CLAUDE.md to import the truncated version
        if not self.claude_md_path.exists():
            raise FileNotFoundError(f"CLAUDE.md not found: {self.claude_md_path}")

        claude_content = self.claude_md_path.read_text()

        # Create import directive for the truncated file
        memory_path_rel = f"../memory/{task_id}.truncated.md"
        new_section = self.ACTIVE_TASK_SECTION_TEMPLATE.format(
            content=f"@import {memory_path_rel}\n"
        )

        # Replace or add the section
        if self.ACTIVE_TASK_SECTION_REGEX.search(claude_content):
            new_content = self.ACTIVE_TASK_SECTION_REGEX.sub(
                new_section.rstrip() + "\n", claude_content
            )
        else:
            new_content = claude_content.rstrip() + "\n\n" + new_section.rstrip() + "\n"

        # Clean up multiple consecutive blank lines
        new_content = re.sub(r"\n{3,}", "\n\n", new_content)

        self.claude_md_path.write_text(new_content)
