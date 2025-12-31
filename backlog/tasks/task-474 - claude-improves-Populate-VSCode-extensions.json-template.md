---
id: task-474
title: 'claude-improves: Populate VSCode extensions.json template'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-31 22:05'
labels:
  - claude-improves
  - templates
  - vscode
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
.vscode/extensions.json template has empty recommendations array. Should include standard extensions based on detected project type.

Python projects should get:
- ms-python.python, ms-python.vscode-pylance
- charliermarsh.ruff
- ms-azuretools.vscode-docker

All projects should get:
- GitHub.copilot (or anthropics.claude-code when available)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 extensions.json template includes base recommendations
- [x] #2 Python-specific extensions added when Python detected
- [x] #3 TypeScript/Node extensions added when package.json detected
- [x] #4 Docker extension added when Dockerfile detected
- [x] #5 Template is customizable based on project type detection
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented generate_vscode_extensions() function that creates .vscode/extensions.json during flowspec init with tech-stack specific recommendations: Python (python, pylance, ruff), JS/TS (eslint, prettier), Go, Rust, Java, and Docker extensions when detected.
<!-- SECTION:NOTES:END -->
