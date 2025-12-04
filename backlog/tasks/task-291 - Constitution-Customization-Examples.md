---
id: task-291
title: Constitution Customization Examples
status: Done
assignee: []
created_date: '2025-12-04 16:16'
updated_date: '2025-12-04 17:51'
labels:
  - constitution-cleanup
dependencies:
  - task-244
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Real-world examples of customized constitutions for different tech stacks
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Example: Python project with pytest, ruff, GitHub Actions
- [x] #2 Example: TypeScript project with jest, eslint, prettier
- [x] #3 Example: Go project with golangci-lint, Go modules
- [x] #4 Example: Rust project with cargo, clippy
- [x] #5 Each example shows before/after LLM customization
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created comprehensive constitution customization examples for 4 major tech stacks.

Files Created:
- docs/examples/constitutions/README.md - Index and usage guide
- docs/examples/constitutions/python-fastapi-example.md - Python/FastAPI example
- docs/examples/constitutions/typescript-react-example.md - TypeScript/React example
- docs/examples/constitutions/go-api-example.md - Go API example
- docs/examples/constitutions/rust-cli-example.md - Rust CLI example

Each example shows:
1. Detection process (how LLM identifies tech stack)
2. Before/after template transformation
3. What was auto-detected vs what needs validation
4. Additional customization options
5. Commands to verify configuration

All examples demonstrate realistic projects with proper tooling:
- Python: pytest, ruff, GitHub Actions
- TypeScript: jest, eslint, prettier, pnpm
- Go: golangci-lint, Go modules, table-driven tests
- Rust: clippy, rustfmt, cargo-dist

The README provides:
- Overview of when to use each example
- Common patterns across all examples
- Customization tips
- Multi-language project guidance
<!-- SECTION:NOTES:END -->
