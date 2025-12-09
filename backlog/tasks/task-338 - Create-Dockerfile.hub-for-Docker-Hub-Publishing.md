---
id: task-338
title: Create Dockerfile.hub for Docker Hub Publishing
status: To Do
assignee: []
created_date: '2025-12-09 01:00'
labels:
  - infrastructure
  - devcontainer
  - docker
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create multi-stage Dockerfile optimized for Docker Hub distribution with all AI CLIs pre-installed (Claude Code, GitHub Copilot, OpenAI Codex, Google Gemini, backlog.md).

File location: `.devcontainer/Dockerfile.hub`

Multi-stage structure:
- Stage 1: Base with system dependencies (Node.js, pnpm)
- Stage 2: AI tools (all CLIs via pnpm global)
- Stage 3: Python tooling (uv, ruff, pytest)
- Stage 4: Runtime image with vscode user

Four build targets:
- `runtime` (full, default) - All tools
- `minimal` - Claude + backlog only
- `python` - Full + Python tools (mypy, black, bandit)
- `node` - Full + Node tools (eslint, prettier, vitest)

Layer optimization for caching, multi-arch support (amd64, arm64).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dockerfile builds successfully for all 4 variants (runtime, minimal, python, node)
- [ ] #2 Multi-arch builds work (linux/amd64, linux/arm64) tested with docker buildx
- [ ] #3 Layer caching optimized - base layers change rarely, tool layers separate
- [ ] #4 All AI CLIs verified installed and in PATH: claude, copilot, codex, gemini, backlog
- [ ] #5 Image size targets met: full < 1.5GB, minimal < 900MB
- [ ] #6 Health check included to verify critical tools (claude, backlog, uv) available
- [ ] #7 Metadata labels included: title, description, version, source URL, license
<!-- AC:END -->
