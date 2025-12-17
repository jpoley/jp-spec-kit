# Product Requirements Prompt (PRP) Templates

This directory contains templates for PRP (Product Requirements Prompt) documents.

## Purpose

A PRP is a **self-contained context packet** for a feature. If you give a PRP to an LLM as the only context, it should have everything needed to work on the feature.

PRPs bundle together:
- All needed context (code files, docs, examples, gotchas, related tasks)
- Codebase snapshot (bounded directory tree)
- Validation loop (specific commands and success criteria)
- Acceptance criteria
- Loop classification (inner vs outer loop tasks)

## Template

- `prp-base-flowspec.md` - The main PRP template

## Structure

PRPs have a consistent, machine-parseable structure:

```
## ALL NEEDED CONTEXT
### Code Files          - Table format: Path | Purpose | Priority
### Docs / Specs        - Table format: Document | Link | Key Sections
### Examples            - Table format: Example | Location | What It Shows
### Known Gotchas       - Table format: Gotcha | Impact | Mitigation | Source
### Related Tasks       - Table format: Task ID | Title | Relationship | Status

## CODEBASE SNAPSHOT
- Directory tree structure
### Key Entry Points    - Table format: Entry Point | Location | Purpose
### Integration Points  - Table format: Integration | File | Function | Notes

## VALIDATION LOOP
### Commands            - Bash code blocks with specific commands
### Expected Success    - Table format: Validation | Success Criteria
### Known Failure Modes - Table format: Failure | Meaning | Fix

## ACCEPTANCE CRITERIA
- Checkbox list copied from backlog task

## LOOP CLASSIFICATION
### Inner Loop          - Implementation tasks
### Outer Loop          - Planning/review tasks
```

## Usage

1. **Generate automatically** using `/flow:generate-prp`:
   ```bash
   /flow:generate-prp task-123
   ```
   This collects context from PRD, specs, examples, and learnings.

2. **Or create manually** by copying the template:
   ```bash
   cp templates/docs/prp/prp-base-flowspec.md docs/prp/<task-id>.md
   ```

3. **Use in implementation** (PRP-First Workflow):
   - `/flow:implement` automatically checks for `docs/prp/<task-id>.md`
   - If PRP exists: Loads it as **primary context** for implementation agents
   - If PRP missing: Recommends running `/flow:generate-prp` first
   - Agents reference the PRP for all needed information (code files, gotchas, validation)

## Key Principle

> **Self-Contained Context**: A PRP should contain everything an agent needs to implement a feature without asking clarifying questions about basic context.

## PRP-First Workflow

Starting with `/flow:implement` in version 0.3.x, Flowspec uses a **PRP-first** approach:

1. **Before Implementation**: Generate PRP with `/flow:generate-prp task-123`
2. **During Implementation**: `/flow:implement task-123` checks for PRP automatically
3. **If PRP Found**: Loads it as primary context (no need to discover docs/specs manually)
4. **If PRP Missing**: Warns and suggests generating PRP first

### Benefits

| With PRP | Without PRP |
|----------|-------------|
| All context gathered upfront | Must discover context during implementation |
| Known gotchas highlighted | May miss edge cases |
| Clear validation commands | Unclear how to test |
| Focused implementation | May read irrelevant files |
| Faster agent onboarding | More exploration needed |

### Workflow Example

```bash
# 1. Run /flow:specify to create task with acceptance criteria
/flow:specify "Add user authentication"
# Creates: task-456 with ACs

# 2. Generate PRP for the task
/flow:generate-prp task-456
# Creates: docs/prp/task-456.md

# 3. Review PRP (optional but recommended)
cat docs/prp/task-456.md

# 4. Run implementation with PRP context
/flow:implement task-456
# Loads PRP automatically, proceeds with full context
```

## Related Documentation

- [INITIAL Template](../initial/README.md) - Feature intake documents that feed PRPs
- [Context Engineering Guide](../../guides/context-engineering.md) (coming soon)
- [Workflow Architecture](../../guides/workflow-architecture.md)

## Pattern Source

Based on context-engineering-intro patterns (archon-inspired):
- PRP as portable context bundle
- Machine-parseable sections for automation
- Validation loop for reproducible testing
