---
id: task-346
title: Build and test Dockerfile locally on both amd64 and arm64
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - testing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Validate Dockerfile builds successfully on both architectures and passes all health checks.

**Test Plan**:
1. Build image locally:
   ```bash
   docker buildx create --use
   docker buildx build --platform linux/amd64,linux/arm64 \
     -t ai-coding-agents-test:local \
     -f .devcontainer/Dockerfile .
   ```

2. Test amd64 build:
   ```bash
   docker run --rm --platform linux/amd64 ai-coding-agents-test:local /home/vscode/healthcheck.sh
   ```

3. Test arm64 build (requires QEMU or ARM machine):
   ```bash
   docker run --rm --platform linux/arm64 ai-coding-agents-test:local /home/vscode/healthcheck.sh
   ```

4. Verify CLI availability:
   ```bash
   docker run --rm ai-coding-agents-test:local bash -c 'command -v claude && command -v backlog && command -v uv'
   ```

5. Check image size:
   ```bash
   docker image inspect ai-coding-agents-test:local --format='{{.Size}}' | awk '{print $1/1024/1024 " MB"}'
   ```
   Target: < 1.5 GB

**Failure Scenarios**:
- Build fails on arm64 due to QEMU emulation
- AI CLIs not in PATH
- Health check script fails
- Image size > 2 GB
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dockerfile builds successfully on both linux/amd64 and linux/arm64
- [ ] #2 Health check passes on both platforms
- [ ] #3 All AI CLIs (claude, copilot, codex, gemini, backlog) are available in PATH
- [ ] #4 Image size is < 1.5 GB per platform
- [ ] #5 Python 3.11+ is installed and functional
- [ ] #6 uv, pnpm, gh CLIs are functional
<!-- AC:END -->
