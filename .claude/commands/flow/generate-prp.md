---
description: Generate PRP (Product Requirements Prompt) context bundles from existing artifacts.
mode: agent
loop: utility
# Loop Classification: UTILITY
# This is a utility command that can be used in either loop. It generates context
# bundles from existing artifacts and doesn't modify code or workflow state.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command generates a PRP (Product Requirements Prompt) document by collecting and bundling context from:
- PRD documents
- Task memory files
- Examples
- Learnings/gotchas
- Codebase structure

A PRP is a **self-contained context packet** - if you give it to an LLM as the only context, it should have everything needed to implement the feature.

### Step 1: Identify Target Task

Determine which task to generate PRP for:

```bash
TASK_ID="${ARGUMENTS:-}"

if [ -z "$TASK_ID" ]; then
  echo "ERROR: No task ID provided"
  echo ""
  echo "Usage: /flow:generate-prp <task-id>"
  echo ""
  echo "Example:"
  echo "  /flow:generate-prp task-123"
  echo ""
  echo "Available tasks:"
  backlog task list -s "To Do" --plain | head -10
  backlog task list -s "In Progress" --plain | head -10
  exit 1
fi

# Verify task exists
backlog task $TASK_ID --plain
```

If no task ID is provided, show usage and exit.

### Step 2: Gather Context Sources

Collect all relevant context for the task:

#### 2.1 Task Information

```bash
# Get task details
backlog task $TASK_ID --plain

# Extract:
# - Task title (for FEATURE_NAME)
# - Task description (for FEATURE_SUMMARY)
# - Acceptance criteria (for ACCEPTANCE CRITERIA section)
# - Labels (for context hints)
```

#### 2.2 Task Memory File

```bash
# Check for task memory file
MEMORY_FILE="backlog/memory/$TASK_ID.md"

if [ -f "$MEMORY_FILE" ]; then
  echo "Found task memory: $MEMORY_FILE"
  # Extract: What/Why, Constraints, Examples, Docs, Gotchas
else
  echo "No task memory file found at $MEMORY_FILE"
  echo "Consider running /flow:intake first to create context"
fi
```

#### 2.3 Related PRD

```bash
# Search for related PRD by task ID or feature name
grep -rl "$TASK_ID" docs/prd/ 2>/dev/null || echo "No PRD references task"

# Also search by feature keywords from task title
# Extract: Requirements, User Stories, Dependencies
```

#### 2.4 Examples

```bash
# List examples directory
ls -la examples/ 2>/dev/null || echo "No examples directory"

# Search for relevant examples based on task labels/keywords
# Extract: Example files, their purpose, relevance
```

#### 2.5 Learnings and Gotchas

```bash
# Check memory/learnings directory for relevant lessons
ls memory/learnings/*.md 2>/dev/null || echo "No learnings files"

# Search for gotchas related to this feature area
# Extract: Known pitfalls, mitigations, sources
```

#### 2.6 Codebase Structure

```bash
# Generate bounded directory tree for relevant code areas
# Based on task labels (backend, frontend, etc.)

# For backend tasks:
find src/ -type f -name "*.py" | head -20

# For frontend tasks:
find src/ -type f -name "*.tsx" -o -name "*.ts" | head -20

# Extract: Key entry points, integration points
```

### Step 3: Generate PRP Document

Create the PRP document at `docs/prp/<task-id>.md` using the template:

```markdown
# Product Requirements Prompt (PRP): {{FEATURE_NAME}}

> **Purpose**: This PRP is a self-contained context packet. If you give this document to an LLM as the only context, it should have everything needed to work on this feature.
>
> **Generated From**: `/flow:generate-prp` command
> **Task ID**: {{TASK_ID}}
> **Generated Date**: {{DATE}}

---

## FEATURE SUMMARY

{{FEATURE_SUMMARY_FROM_TASK}}

---

## ALL NEEDED CONTEXT

> This section contains every piece of context required to implement this feature.

### Code Files

| File Path | Purpose | Read Priority |
|-----------|---------|---------------|
{{CODE_FILES_TABLE}}

### Docs / Specs

| Document | Link | Key Sections |
|----------|------|--------------|
{{DOCS_TABLE}}

### Examples

| Example | Location | What It Demonstrates |
|---------|----------|---------------------|
{{EXAMPLES_TABLE}}

### Known Gotchas

| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
{{GOTCHAS_TABLE}}

### Related Backlog Tasks

| Task ID | Title | Relationship | Status |
|---------|-------|--------------|--------|
{{RELATED_TASKS_TABLE}}

---

## CODEBASE SNAPSHOT

{{DIRECTORY_TREE}}

### Key Entry Points

| Entry Point | Location | Purpose |
|-------------|----------|---------|
{{ENTRY_POINTS_TABLE}}

### Integration Points

| Integration | File | Function/Method | Notes |
|-------------|------|-----------------|-------|
{{INTEGRATION_POINTS_TABLE}}

---

## VALIDATION LOOP

### Commands

```bash
# Run feature-specific tests
{{TEST_COMMANDS}}

# Run linting for affected files
{{LINT_COMMANDS}}

# Run integration tests (if applicable)
{{INTEGRATION_TEST_COMMANDS}}
```

### Expected Success

| Validation | Success Criteria |
|------------|------------------|
{{SUCCESS_CRITERIA_TABLE}}

### Known Failure Modes

| Failure Pattern | What It Means | How to Fix |
|-----------------|---------------|------------|
{{FAILURE_MODES_TABLE}}

---

## ACCEPTANCE CRITERIA

{{ACCEPTANCE_CRITERIA_FROM_TASK}}

---

## LOOP CLASSIFICATION

### Inner Loop Responsibilities

{{INNER_LOOP_TASKS}}

### Outer Loop Responsibilities

{{OUTER_LOOP_TASKS}}

---

## IMPLEMENTATION NOTES

### Decisions Made

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| | | |

### Blockers Encountered

| Blocker | Status | Resolution |
|---------|--------|------------|
| | | |

### Follow-up Tasks

- [ ]

---

*PRP Generated from: /flow:generate-prp {{TASK_ID}}*
*Generated at: {{TIMESTAMP}}*
```

### Step 4: Write PRP File

```bash
# Ensure docs/prp directory exists
mkdir -p docs/prp

# Write PRP file
PRP_PATH="docs/prp/$TASK_ID.md"
echo "Writing PRP to: $PRP_PATH"
```

### Step 5: Output Summary

After generating, display summary:

```
PRP Generated Successfully!

Created:
  PRP: docs/prp/<task-id>.md

Context Sources Used:
  - Task: <task-id> - "<title>"
  - Memory: backlog/memory/<task-id>.md [found/not found]
  - PRD: docs/prd/<filename>.md [found/not found]
  - Examples: X files referenced
  - Gotchas: Y entries included

Next Steps:
  1. Review the generated PRP: docs/prp/<task-id>.md
  2. Fill in any missing sections manually
  3. Run implementation: /flow:implement <task-id>

Tip: The PRP can be used as standalone context for any LLM.
```

### Context Collection Guidelines

When gathering context, prioritize:

1. **High Priority (Must Include)**:
   - Task description and acceptance criteria
   - Directly related code files
   - Known gotchas for this feature area
   - Test files and commands

2. **Medium Priority (Include if Available)**:
   - PRD sections related to this feature
   - Example files demonstrating patterns
   - Related task information
   - Architecture documentation

3. **Low Priority (Include if Space Allows)**:
   - General project documentation
   - Tangentially related code
   - Historical context

### Handling Missing Context

If context sources are not found:

- **No PRD**: Use task description as primary context
- **No Memory File**: Extract from task description only
- **No Examples**: Note "No examples available" in section
- **No Learnings**: Leave gotchas section empty with placeholder

```markdown
### Known Gotchas

| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| *No known gotchas documented* | - | - | - |
```

## Deliverables

This command produces:
1. **PRP Document**: Self-contained context bundle at `docs/prp/<task-id>.md`
2. **Summary**: Clear output showing what was generated and sources used

## Integration with Workflow

The generated PRP can be used:
- As input to `/flow:implement` for focused implementation
- As standalone context for any LLM
- As documentation of feature context
- For onboarding new contributors to a feature
