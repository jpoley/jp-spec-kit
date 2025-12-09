---
id: task-350
title: Create automated test suite for published image
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - testing
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement comprehensive test suite to validate published image functionality on both amd64 and arm64 platforms.

**Test Matrix**:
- Platforms: linux/amd64, linux/arm64

**Test Categories**:

1. **Health Check Test**:
   ```bash
   docker run --rm --platform <platform> <image> /home/vscode/healthcheck.sh
   ```
   Expected: Exit code 0

2. **CLI Availability Test**:
   ```bash
   docker run --rm --platform <platform> <image> bash -c '
     command -v claude || exit 1
     command -v backlog || exit 1
     command -v uv || exit 1
     command -v pnpm || exit 1
     command -v gh || exit 1
   '
   ```
   Expected: All CLIs found

3. **Python Environment Test**:
   ```bash
   docker run --rm --platform <platform> <image> bash -c '
     python --version
     python -c "import sys; assert sys.version_info >= (3, 11)"
     uv --version
   '
   ```
   Expected: Python 3.11+, uv available

4. **Node Environment Test**:
   ```bash
   docker run --rm --platform <platform> <image> bash -c '
     node --version | grep "v20"
     pnpm --version
   '
   ```
   Expected: Node 20.x, pnpm available

5. **PATH Configuration Test**:
   ```bash
   docker run --rm --platform <platform> <image> bash -c '
     echo $PATH | grep -q "/home/vscode/.local/share/pnpm"
     echo $PATH | grep -q "/home/vscode/.cargo/bin"
   '
   ```
   Expected: Both paths present

6. **Shell Configuration Test**:
   ```bash
   docker run --rm --platform <platform> <image> zsh -c 'echo $PATH'
   ```
   Expected: PATH set correctly in zsh

**Performance Tests**:
- Container start time: < 5 seconds
- Health check execution: < 10 seconds

**Failure Handling**:
- If any test fails, mark build as failed
- Upload test logs as artifacts
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All tests pass on linux/amd64 platform
- [ ] #2 All tests pass on linux/arm64 platform
- [ ] #3 Test suite completes in < 3 minutes for both platforms
- [ ] #4 Test failures are properly reported with clear error messages
- [ ] #5 Test logs uploaded as artifacts on failure
<!-- AC:END -->
