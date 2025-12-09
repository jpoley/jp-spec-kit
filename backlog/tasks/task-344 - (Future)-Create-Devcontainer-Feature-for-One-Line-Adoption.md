---
id: task-344
title: (Future) Create Devcontainer Feature for One-Line Adoption
status: To Do
assignee: []
created_date: '2025-12-09 01:02'
labels:
  - enhancement
  - devcontainer
  - ux
dependencies:
  - task-343
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Phase 2 enhancement: Create devcontainer feature for the best possible user experience.

Repository: `devcontainer-features` (separate repo)
Feature: `ai-coding-agents`

The feature automatically:
- Configures credential volume mounts (~/.claude, ~/.ssh, ~/.gitconfig)
- Sets up environment variables
- Provides options for image variant selection
- Handles platform-specific mount paths (Linux vs Windows)

Users can adopt with single line:
```json
{
  "features": {
    "ghcr.io/jpoley/devcontainer-features/ai-coding-agents:1": {}
  }
}
```

This is Phase 2 - implement after Phase 1 (v1.0.0) is released and proven.

Depends on: task-343 (v1.0.0 release)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 devcontainer-features repository created and published
- [ ] #2 Feature auto-configures credential mounts for Linux and Windows
- [ ] #3 Feature provides options: variant (full/minimal/python/node), version pinning
- [ ] #4 Feature published to GHCR (ghcr.io/jpoley/devcontainer-features/ai-coding-agents)
- [ ] #5 Feature tested with example projects (Python, Node, minimal)
- [ ] #6 Feature documentation complete with options reference
- [ ] #7 jp-spec-kit documentation updated to recommend feature over direct image reference
<!-- AC:END -->
