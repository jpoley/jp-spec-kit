---
id: task-309
title: Sync .agents/ and .claude/agents/ directories
status: To Do
assignee:
  - '@galway'
created_date: '2025-12-08 01:25'
updated_date: '2025-12-15 02:17'
labels:
  - technical-debt
  - agents
  - testing
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The two agent directories have diverged significantly and need to be synchronized.

## Current State

| Directory | Files | Purpose |
|-----------|-------|---------|
| `.agents/` | 15 | Enhanced agents for Flowspec workflows (MCP tools, loop classification, detailed prompts) |
| `.claude/agents/` | 5 | Claude Code Task tool agents (simpler prompts, basic tools) |

## Issues Found

### 1. Missing agents in `.claude/agents/`
These agents exist in `.agents/` but not in `.claude/agents/`:
- ai-ml-engineer.md
- backend-code-reviewer.md
- business-validator.md
- frontend-code-reviewer.md
- platform-engineer-enhanced.md
- product-requirements-manager-enhanced.md
- release-manager.md
- researcher.md
- software-architect-enhanced.md
- sre-agent.md
- tech-writer.md

### 2. Missing agents in `.agents/`
These agents exist in `.claude/agents/` but not in `.agents/`:
- project-manager-backlog.md

### 3. Overlapping agents with different content
- **backend-engineer.md**: `.agents/` is Go/TS/Python (440 lines), `.claude/agents/` is Python-only (200 lines)
- **frontend-engineer.md**: `.agents/` has React Native/mobile (380 lines), `.claude/agents/` is web-only (140 lines)
- **qa-engineer vs quality-guardian**: Different focus (testing vs risk analysis)
- **security-reviewer vs secure-by-design-engineer**: Different scope (simpler vs comprehensive)

## Proposed Solution

### Option A: Consolidate to single source of truth
1. Keep `.agents/` as canonical source
2. Generate `.claude/agents/` from `.agents/` with transformations:
   - Simplify descriptions for Claude Code Task tool format
   - Reduce tool lists to basic set (Read, Write, Edit, Glob, Grep, Bash)
   - Remove loop classification and model fields
3. Add test to verify sync

### Option B: Keep both but add sync test
1. Maintain both manually for different use cases
2. Add test to verify common agents have consistent core content
3. Document the intentional differences

## Implementation Tasks
1. Decide on consolidation strategy (Option A or B)
2. Create sync script or test
3. Add to CI/CD to prevent drift
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AC1: A test exists that runs in CI to verify agent directories are in sync
- [ ] #2 AC2: Clear decision documented on which directory is source of truth
- [ ] #3 AC3: Either sync script exists OR intentional differences are documented
- [ ] #4 AC4: No silent drift can occur - CI will fail if directories diverge unexpectedly
<!-- AC:END -->
