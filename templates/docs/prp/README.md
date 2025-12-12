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

3. **Use in implementation**:
   - `/flow:implement` checks for PRP and loads it as primary context
   - Agents reference the PRP for all needed information

## Key Principle

> **Self-Contained Context**: A PRP should contain everything an agent needs to implement a feature without asking clarifying questions about basic context.

## Related Documentation

- [INITIAL Template](../initial/README.md) - Feature intake documents that feed PRPs
- [Context Engineering Guide](../../guides/context-engineering.md) (coming soon)
- [Workflow Architecture](../../guides/workflow-architecture.md)

## Pattern Source

Based on context-engineering-intro patterns (archon-inspired):
- PRP as portable context bundle
- Machine-parseable sections for automation
- Validation loop for reproducible testing
