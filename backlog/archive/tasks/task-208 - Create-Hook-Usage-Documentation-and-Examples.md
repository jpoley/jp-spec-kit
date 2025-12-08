---
id: task-208
title: Create Hook Usage Documentation and Examples
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-03 01:47'
labels:
  - documentation
  - hooks
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive user guide with use cases, patterns, best practices, and troubleshooting for the hook system.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 User guide at docs/guides/hooks-user-guide.md (getting started, concepts, examples)
- [x] #2 Reference doc at docs/reference/hooks-api.md (event types, payload schemas, CLI commands)
- [x] #3 Example hooks library with 10+ real-world examples
- [ ] #4 Security best practices guide for hook authors
- [ ] #5 Troubleshooting guide with common issues and solutions
- [ ] #6 Update CLAUDE.md with hook system overview
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created comprehensive docs/guides/hooks-quickstart.md with:

1. Getting Started section - How to initialize, review, enable, test, and validate hooks

2. Event Types Reference - Complete catalog of all 12+ workflow events (spec, plan, task, implement, validate, deploy)

3. Common Use Cases - 5 real-world examples:
   - Run tests after implementation
   - Update documentation on spec creation
   - Quality gate before validation
   - Run linter on task completion
   - Notify external systems on deployment

4. Event Data Access - How to parse HOOK_EVENT JSON in scripts with examples

5. CLI Commands - Complete reference for all 5 CLI commands (list, emit, audit, test, validate)

6. Configuration Options - Global defaults, hook config, and fail modes

7. Security - Sandboxing, audit logging, and best practices

8. Troubleshooting - Common issues and solutions

9. Language-specific examples - Python, JavaScript/Node.js, and Go

10. Next Steps and additional resources
<!-- SECTION:NOTES:END -->
