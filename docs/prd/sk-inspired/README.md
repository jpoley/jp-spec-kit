# Spec-Kitty Inspired Features

Feature specifications inspired by [spec-kitty](https://github.com/Priivacy-ai/spec-kitty), a community fork of GitHub's Spec Kit that offers unique capabilities flowspec could benefit from.

## Background

After a [deep review of spec-kitty](../../research/spec-kitty.md), we identified 5 key features that would enhance flowspec without losing any existing functionality.

## Feature Specifications

| ID | Feature | Priority | Complexity | Status |
|----|---------|----------|------------|--------|
| [SK-001](sk-001-realtime-kanban-dashboard.md) | Real-time Kanban Dashboard | P1 | High | Draft |
| [SK-002](sk-002-worktree-isolation.md) | Worktree-based Feature Isolation | P1 | Medium | Draft |
| [SK-003](sk-003-multi-agent-support.md) | Multi-Agent Support (11 agents) | P3 | Low | Draft |
| [SK-004](sk-004-mission-system.md) | Mission System (Domain Adapters) | P2 | Medium | Draft |
| [SK-005](sk-005-discovery-gates.md) | Discovery Gates (Mandatory Interviews) | P2 | Low | Draft |

## Key Design Decision: Backlog.md Integration

**Backlog.md stays.** It is MORE sophisticated than spec-kitty's approach:

- MCP server integration (AI-native access)
- Acceptance criteria with progressive tracking
- Dependencies between tasks
- Labels, filtering, search
- Richer metadata

The new features integrate WITH backlog.md, not replace it:

- **Dashboard** reads from backlog.md as data source
- **Worktrees** are orthogonal to task management (git-level isolation)
- **Missions** extend workflow config, don't replace it
- **Discovery gates** enhance commands, work with existing task creation

## Implementation Order

Recommended implementation order based on impact and dependencies:

1. **SK-001: Dashboard** (P1) - Highest user impact, no dependencies
2. **SK-002: Worktrees** (P1) - High impact, integrates with specify
3. **SK-005: Discovery Gates** (P2) - Low effort, high quality improvement
4. **SK-004: Mission System** (P2) - Extends workflow config
5. **SK-003: Multi-Agent** (P3) - Nice to have, low effort

## Summary Comparison

| Feature | Spec-Kitty | Flowspec Current | Flowspec After |
|---------|-----------|------------------|----------------|
| Real-time Dashboard | Yes | No | Yes |
| Worktree Isolation | Yes | No | Yes |
| AI Agents | 11 | 5 | 11 |
| Mission System | Yes | No | Yes |
| Discovery Gates | Yes | Partial | Yes |
| Backlog.md | Simple tasks.md | Rich MCP | Rich MCP |
| Security Scanning | No | 5+ scanners | 5+ scanners |
| State Machine | 4 lanes | 9 states | 9 states |

**Result:** Best of both worlds - spec-kitty's UX innovations + flowspec's governance depth.
