# ADR-009: Resolution of task-198 Unified Vulnerability Scanner

**Status:** Accepted
**Date:** 2025-12-03
**Author:** Platform Engineer
**Context:** Resolution of task-220 - Clarifying relationship between task-198 and /flow:security
**Supersedes:** None
**Amended by:** None

---

## Context

Task-220 was created to "Resolve Relationship with task-198 Unified Vulnerability Scanner" and determine integration strategy between `/flow:security` commands and a planned Trivy + Snyk scanner design.

During investigation, we discovered:

1. **Task-198 was repurposed** - It now covers "Define Event Model Schema for flowspec Hooks" (completed 2025-12-03), not a unified vulnerability scanner
2. **No separate scanner task exists** - The "Trivy + Snyk unified scanner" was a conceptual reference, not a tracked task
3. **Native implementation supersedes** - The `/flow:security` architecture (ADR-005 through ADR-008) provides unified scanning through the adapter pattern

## Decision

**Close task-220 as resolved with the following determinations:**

### 1. Task-198 Identity
- Task-198 is the **Event Model Schema for Hooks** (completed)
- There is no conflict with security scanning - these are separate concerns

### 2. Unified Scanner Architecture
The native `/flow:security` implementation provides unified scanning through:

| ADR | Component | Description |
|-----|-----------|-------------|
| ADR-005 | Scanner Orchestration Pattern | Adapter-based scanner integration |
| ADR-006 | AI Triage Engine Design | AI-powered vulnerability classification |
| ADR-007 | Unified Security Finding Format | Cross-scanner normalized findings |
| ADR-008 | Security MCP Server Architecture | External tool integration |

### 3. Scanner Roadmap
The adapter pattern (ADR-005) supports incremental scanner addition:

| Scanner | Status | Priority |
|---------|--------|----------|
| Semgrep (SAST) | ✅ Implemented | P0 |
| CodeQL (SAST) | 🔲 Planned (task-225) | P1 |
| Trivy (SCA/Container) | 🔲 Planned | P2 |
| Snyk (SCA) | 🔲 Planned | P2 |
| Playwright DAST | 🔲 Planned (task-222) | P2 |

### 4. No Supersession Needed
Since task-198 was never about security scanning, there is nothing to supersede, integrate, or keep separate.

## Consequences

### Positive
- Eliminates confusion about task-198's purpose
- Confirms architectural direction is sound
- Documents scanner roadmap for future work

### Negative
- Task-220 was based on incorrect assumptions about task-198

### Neutral
- Future scanner additions follow ADR-005 adapter pattern
- No changes required to existing security implementation

## Implementation

1. ✅ Document this decision (this ADR)
2. ✅ Update task-220 with resolution
3. ✅ No code changes required

## References

- task-198: Define Event Model Schema for flowspec Hooks (Done)
- task-220: Resolve Relationship with task-198 (This resolution)
- ADR-005: Scanner Orchestration Pattern
- ADR-006: AI Triage Engine Design
- ADR-007: Unified Security Finding Format
- ADR-008: Security MCP Server Architecture
