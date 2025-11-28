#!/usr/bin/env python3
"""
Script to apply backlog.md CLI integration to implement.md command.

This script modifies .claude/commands/jpspec/implement.md to add:
1. CRITICAL task requirement section
2. Backlog integration instructions for all 5 agents (3 engineers + 2 reviewers)
"""

from pathlib import Path

# File paths
IMPLEMENT_FILE = Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "implement.md"

# Shared backlog instructions for engineers
ENGINEER_BACKLOG_SECTION = '''
---

# BACKLOG.MD INTEGRATION - CRITICAL INSTRUCTIONS

## Critical Rules

1. **NEVER edit task files directly** - Always use `backlog` CLI commands
2. **Use `--plain` flag** when viewing/listing tasks for clean AI-readable output
3. **Mark ACs complete as you finish them** - Don't batch completions
4. **Add implementation notes** before marking tasks Done

## Starting Work

**FIRST**: Pick up a task from the backlog:

```bash
# List available {agent_type} tasks
backlog task list -s "To Do" --plain
backlog search "{search_term}" --plain

# View task details
backlog task <id> --plain

# Assign yourself and set to In Progress
backlog task edit <id> -s "In Progress" -a @{agent_name}

# Add implementation plan
backlog task edit <id> --plan $'1. {plan_step_1}\\n2. {plan_step_2}\\n3. {plan_step_3}'
```

## Tracking Progress

As you complete each acceptance criterion:

```bash
# Check AC as you finish it
backlog task edit <id> --check-ac 1
backlog task edit <id> --check-ac 2

# Or check multiple at once
backlog task edit <id> --check-ac 1 --check-ac 2 --check-ac 3
```

## Completing Work

Before marking Done, verify Definition of Done:
- ✅ All acceptance criteria checked
- ✅ Implementation notes added
- ✅ Tests pass
- ✅ Code self-reviewed{extra_dod}

```bash
# Add implementation notes
backlog task edit <id> --notes $'{notes_example}'

# Mark as done
backlog task edit <id> -s Done
```

---

'''

# Code reviewer backlog instructions
REVIEWER_BACKLOG_SECTION = '''
---

# BACKLOG.MD INTEGRATION - CRITICAL FOR CODE REVIEWERS

**CRITICAL**: Code reviewers MUST verify that task acceptance criteria match the actual implementation.

## Review Workflow with Backlog

1. **Check task ACs before reviewing**:
   ```bash
   # View the task being reviewed
   backlog task <id> --plain
   ```

2. **Verify each AC matches code**:
   - For each acceptance criterion in the task
   - Verify the code actually implements it
   - If AC is checked but code doesn't implement it → UNCHECK IT
   - If AC is not checked but code implements it → CHECK IT

3. **Update ACs based on review**:
   ```bash
   # If AC not fully implemented
   backlog task edit <id> --uncheck-ac 2 --append-notes $'{review_note_example}'

   # If implementation is incomplete, revert status
   backlog task edit <id> -s "In Progress"
   ```

4. **Verify Definition of Done**:
   - ✅ All ACs checked AND verified in code
   - ✅ Implementation notes describe what was built
   - ✅ Tests exist and pass
   - ✅ No security issues
   - ✅ Performance acceptable{extra_reviewer_dod}

---

'''

# Task requirement section
TASK_REQUIREMENT_SECTION = '''
## CRITICAL: Backlog Task Requirement

**BEFORE PROCEEDING**: This command requires existing backlog tasks to work on.

1. **Check for existing tasks**:
   ```bash
   backlog task list -s "To Do" --plain
   ```

2. **If no tasks exist**:
   - Fail gracefully with message: "No backlog tasks found. Please create tasks using `/jpspec:specify` or `backlog task create` before running implementation."
   - Exit the command - do NOT proceed with implementation

3. **If tasks exist**:
   - Engineers MUST pick tasks from the backlog
   - Engineers MUST NOT implement features without corresponding backlog tasks

'''

def insert_task_requirement(content: str) -> str:
    """Insert task requirement section after user input."""
    marker = "You **MUST** consider the user input before proceeding (if not empty).\n"
    if marker in content:
        return content.replace(
            marker,
            marker + "\n" + TASK_REQUIREMENT_SECTION
        )
    return content

def insert_frontend_backlog(content: str) -> str:
    """Insert backlog integration for Frontend Engineer."""
    marker = "- **Testing**: Vitest, React Testing Library, Playwright\n"
    if marker in content:
        section = ENGINEER_BACKLOG_SECTION.format(
            agent_type="frontend",
            search_term="frontend",
            agent_name="frontend-engineer",
            plan_step_1="Create components",
            plan_step_2="Implement state",
            plan_step_3="Add tests",
            extra_dod="",
            notes_example="Implemented feature X using React hooks.\\n\\nKey changes:\\n- Added components A, B, C\\n- Integrated with API\\n- Added comprehensive tests"
        )
        insert_at = content.find(marker) + len(marker)
        return content[:insert_at] + section + "\n# TASK: Implement the frontend for: [USER INPUT FEATURE]\n\n**IMPORTANT**: All work MUST be tracked via backlog tasks. Pick tasks from backlog, assign yourself, and track AC completion.\n\n" + content[insert_at:].split("# TASK: Implement the frontend for: [USER INPUT FEATURE]\n\nContext:\n", 1)[1]
    return content

def insert_backend_backlog(content: str) -> str:
    """Insert backlog integration for Backend Engineer."""
    marker = "- **Python**: FastAPI, SQLAlchemy, Pydantic, Click/Typer (CLI)\n"
    if marker in content:
        section = ENGINEER_BACKLOG_SECTION.format(
            agent_type="backend",
            search_term="backend",
            agent_name="backend-engineer",
            plan_step_1="Design API endpoints",
            plan_step_2="Implement business logic",
            plan_step_3="Add database layer",
            extra_dod="\n- ✅ Security validated",
            notes_example="Implemented REST API using Go with Chi router.\\n\\nKey changes:\\n- Added endpoints: POST /api/users, GET /api/users/:id\\n- Implemented validation with custom middleware\\n- Added PostgreSQL integration\\n- Added unit and integration tests"
        )
        insert_at = content.find(marker) + len(marker)
        return content[:insert_at] + section + "\n# TASK: Implement the backend for: [USER INPUT FEATURE]\n\n**IMPORTANT**: All work MUST be tracked via backlog tasks. Pick tasks from backlog, assign yourself, and track AC completion.\n\n" + content[insert_at:].split("# TASK: Implement the backend for: [USER INPUT FEATURE]\n\nContext:\n", 1)[1]
    return content

def insert_aiml_backlog(content: str) -> str:
    """Insert backlog integration for AI/ML Engineer."""
    marker = "#### AI/ML Implementation (if ML components needed)\n\nUse the Task tool to launch the **ai-ml-engineer** agent:\n\n```\n"
    if marker in content:
        section = ENGINEER_BACKLOG_SECTION.format(
            agent_type="ML",
            search_term="ml",
            agent_name="ai-ml-engineer",
            plan_step_1="Prepare training data",
            plan_step_2="Train model",
            plan_step_3="Evaluate performance",
            extra_dod="\n- ✅ Model metrics documented\n- ✅ Monitoring configured",
            notes_example="Trained classification model with 95% accuracy.\\n\\nKey changes:\\n- Prepared training dataset (10K samples)\\n- Trained XGBoost model\\n- Deployed FastAPI inference service\\n- Added Prometheus metrics\\n- Documented model performance"
        )
        insert_at = content.find(marker) + len(marker)
        return content[:insert_at] + "# AGENT CONTEXT: Senior AI/ML Engineer\n\n" + section + "\n" + content[insert_at:]
    return content

def insert_frontend_reviewer_backlog(content: str) -> str:
    """Insert backlog integration for Frontend Code Reviewer."""
    marker = "## Review Philosophy\n- Constructive and educational\n- Explain the \"why\" behind suggestions\n- Balance idealism with practical constraints\n- Categorize feedback by severity\n"
    if marker in content and "Frontend Code Reviewer" in content[:content.find(marker)]:
        section = REVIEWER_BACKLOG_SECTION.format(
            review_note_example="Code review: AC #2 not fully implemented. Missing error handling for edge case X.",
            extra_reviewer_dod=""
        )
        insert_at = content.find(marker) + len(marker)
        return content[:insert_at] + section + "\n# TASK: Review the frontend implementation for: [USER INPUT FEATURE]\n\n**IMPORTANT**: Verify that task acceptance criteria match actual code implementation. Update task ACs if discrepancies found.\n\n" + content[insert_at:].split("# TASK: Review the frontend implementation for: [USER INPUT FEATURE]\n\nCode to review:\n", 1)[1]
    return content

def insert_backend_reviewer_backlog(content: str) -> str:
    """Insert backlog integration for Backend Code Reviewer."""
    # Find second occurrence of Review Philosophy (backend reviewer)
    marker = "## Security Priority\n- SQL/NoSQL injection prevention\n- Input validation and sanitization\n- Proper authentication and authorization\n- Secure secret management\n- Dependency vulnerability scanning\n"
    if marker in content:
        section = REVIEWER_BACKLOG_SECTION.format(
            review_note_example="Code review: AC #3 has SQL injection vulnerability in user query. Fix required before completion.",
            extra_reviewer_dod="\n- ✅ Database queries efficient"
        )
        insert_at = content.find(marker) + len(marker)
        return content[:insert_at] + section + "\n# TASK: Review the backend implementation for: [USER INPUT FEATURE]\n\n**IMPORTANT**: Verify that task acceptance criteria match actual code implementation. Update task ACs if discrepancies found.\n\n" + content[insert_at:].split("# TASK: Review the backend implementation for: [USER INPUT FEATURE]\n\nCode to review:\n", 1)[1]
    return content

def update_execution_instructions(content: str) -> str:
    """Update execution instructions line."""
    old = "This command implements features using specialized engineering agents with integrated code review. Determine which implementation paths are needed based on the feature requirements."
    new = "This command implements features using specialized engineering agents with integrated code review. All engineers work exclusively from backlog tasks with acceptance criteria tracking."
    return content.replace(old, new)

def main():
    print("Applying backlog.md CLI integration to implement.md...")

    # Read file
    content = IMPLEMENT_FILE.read_text()

    # Apply all modifications
    content = insert_task_requirement(content)
    content = update_execution_instructions(content)
    content = insert_frontend_backlog(content)
    content = insert_backend_backlog(content)
    content = insert_aiml_backlog(content)
    content = insert_frontend_reviewer_backlog(content)
    content = insert_backend_reviewer_backlog(content)

    # Write back
    IMPLEMENT_FILE.write_text(content)

    print("✅ Successfully applied backlog integration!")
    print(f"Modified: {IMPLEMENT_FILE}")
    print("\nChanges applied:")
    print("1. ✅ Added CRITICAL task requirement section")
    print("2. ✅ Added backlog instructions to Frontend Engineer")
    print("3. ✅ Added backlog instructions to Backend Engineer")
    print("4. ✅ Added backlog instructions to AI/ML Engineer")
    print("5. ✅ Added backlog instructions to Frontend Reviewer")
    print("6. ✅ Added backlog instructions to Backend Reviewer")

if __name__ == "__main__":
    main()
