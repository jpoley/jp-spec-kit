# Architecture Deliverables - Flowspec Upgrade-Repo Fix

**Date:** 2026-01-06
**Architect:** Enterprise Software Architect (Hohpe's Principles Expert)
**Request:** Design system architecture for Flowspec Release Alignment effort

---

## Documents Created

### 1. ADR-001: VSCode Copilot Agent Naming Convention
**Location:** `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-001-vscode-copilot-agent-naming-convention.md`

**Purpose:** Architecture Decision Record for the agent naming convention change.

**Key Decision:** Standardize on dot-notation filenames (`flow.specify.agent.md`) with PascalCase names (`FlowSpecify`) to align with VSCode Copilot agent discovery patterns.

**Contents:**
- Status: Accepted
- Context: Two competing naming conventions, VSCode integration requirements
- Decision rationale: Why dots and PascalCase are correct
- Consequences: Breaking change but enables VSCode integration
- Alternatives considered: 4 alternatives with detailed pros/cons
- Migration strategy: Automatic via upgrade-repo

---

### 2. ADR-002: Upgrade-Repo Architecture Redesign
**Location:** `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-002-upgrade-repo-architecture-redesign.md`

**Purpose:** Comprehensive architectural blueprint for the upgrade-repo fix.

**Key Decision:** Redesign upgrade-repo as a multi-phase orchestration pipeline with validation gates and version-aware migrations.

**Contents:**
- **Penthouse View (Strategic):**
  - Business value: Unblock flowspec release, improve user trust
  - Organizational impact: All downstream projects affected
  - Risk if not fixed: Manual fixes required, support burden
  - Success metrics: Zero manual intervention, agents work correctly

- **Engine Room View (Technical):**
  - Component design: MigrationRegistry, ArtifactSynchronizer, CleanupOrchestrator, UpgradeValidator
  - Integration patterns: 5-phase pipeline (Pre-Validate → Templates → Config → Cleanup → Validate)
  - Data flow: Complete upgrade pipeline from detection to reporting
  - Technology stack: Python stdlib + existing dependencies, no new deps

- **Architecture Decision Record:**
  - Status: Proposed
  - Context: Current upgrade-repo only copies templates, missing 6 critical capabilities
  - Decision: Multi-phase orchestration with validation
  - Consequences: Robust but more complex
  - Alternatives: 4 alternatives with rejection rationale

---

### 3. ADR-003: Upgrade-Repo Implementation Approach
**Location:** `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-003-upgrade-repo-implementation-approach.md`

**Purpose:** Defines implementation order, dependencies, and timeline.

**Key Decision:** Implement in strict dependency-ordered sequence with validation gates between phases.

**Contents:**
- **Phase Breakdown:**
  - Phase 0 (P0): Foundation - Remove broken elements (6 tasks, 2-3 days)
  - Phase 1 (P1): Agent Templates - Fix naming convention (6 tasks, 3-4 days)
  - Phase 2 (P2): MCP Configuration - Comprehensive config (3 tasks, 2-3 days)
  - Phase 4 (P4): Documentation - Update docs (2 tasks, 1-2 days)
  - Phase 5 (P5): Verification - E2E testing (1 task, 2-3 days)

- **Dependency Graph:**
  - Critical path: 9 tasks spanning all phases
  - Parallel work opportunities identified
  - 2-person team can complete in 8-10 days vs 14-18 days solo

- **Implementation Guidelines:**
  - Task execution process
  - Conventional commit format
  - Testing strategy (unit, integration, E2E)
  - Verification gates per phase
  - Risk mitigation strategies

- **Success Criteria:**
  - All Phase 0-2 tasks complete
  - E2E test passes on auth.poley.dev
  - VSCode Copilot agents work correctly
  - MCP servers start without errors

---

### 4. Upgrade-Repo Architecture Summary
**Location:** `/Users/jasonpoley/prj/jp/flowspec/docs/building/upgrade-repo-architecture-summary.md`

**Purpose:** Executive summary combining strategic and tactical views in one document.

**Key Points:**
- **Penthouse View:** Business context, organizational impact, success metrics
- **Engine Room View:** Technical architecture, component design, data flow
- **Implementation Approach:** Phase breakdown, critical path, timeline
- **Risk Assessment:** Probability/impact matrix with mitigation strategies

**Use Case:** Present to stakeholders or as quick reference for the full architecture.

---

## Architecture Principles Applied

This architecture follows Gregor Hohpe's enterprise architecture principles:

1. **Penthouse + Engine Room:** Strategic business view + tactical technical view
2. **Decision Capture:** ADRs document rationale, alternatives, and consequences
3. **Technology Alignment:** Matches proven patterns (migration registry, validation gates)
4. **Risk-Aware:** Explicit risk assessment with mitigation strategies
5. **Implementation Focus:** Clear dependency ordering, parallel work identification
6. **Measurable Success:** Concrete verification gates and success criteria

---

## File Organization

```
/Users/jasonpoley/prj/jp/flowspec/
├── docs/
│   ├── adr/
│   │   ├── ADR-001-vscode-copilot-agent-naming-convention.md     ← Decision: Agent naming
│   │   ├── ADR-002-upgrade-repo-architecture-redesign.md         ← Decision: Multi-phase pipeline
│   │   └── ADR-003-upgrade-repo-implementation-approach.md       ← Decision: Implementation order
│   └── building/
│       ├── upgrade-repo-architecture-summary.md                  ← Executive summary
│       ├── ARCHITECTURE-DELIVERABLES.md                          ← This file (index)
│       └── fix-flowspec-plan.md                                  ← Root cause analysis (existing)
└── backlog/tasks/
    ├── task-579 - EPIC-Flowspec-Release-Alignment...md          ← Epic task
    └── task-579.XX - P{N}.{M}-{description}.md                   ← 18 subtasks
```

---

## How to Use These Documents

### For Stakeholders / Product Managers

**Read:** `upgrade-repo-architecture-summary.md`
- Penthouse View section: Business impact, organizational context
- Success Metrics: What "done" looks like
- Risk Assessment: What could go wrong and how we'll mitigate

### For Architects / Tech Leads

**Read All ADRs:**
1. ADR-001: Understand agent naming decision
2. ADR-002: Understand overall architecture design
3. ADR-003: Understand implementation approach

**Use:** Architecture diagrams, component designs, data flow diagrams from ADR-002

### For Engineers

**Read:** ADR-003 (Implementation Approach)
- Phase breakdown and dependencies
- Task execution process
- Verification gates
- Testing strategy

**Reference:** ADR-002 for component interfaces when implementing

**Follow:** Task files in `backlog/tasks/task-579.XX*.md` for specific acceptance criteria

### For QA / Testing

**Read:** ADR-003 - Testing Strategy section
- Unit test requirements
- Integration test requirements
- E2E test requirements
- Verification gates

**Use:** Phase 5 verification checklist from ADR-003

---

## Next Steps

1. **Review & Approve ADRs:**
   - Circulate ADR-001, ADR-002, ADR-003 for team review
   - Address feedback and concerns
   - Get formal approval before implementation

2. **Staffing:**
   - Assign 1-2 engineers (2 enables parallelization)
   - Allocate 2-3 weeks (14-18 days solo, 8-10 days with 2)

3. **Kick Off:**
   - Daily standup for coordination
   - Start with task-579.01 (Critical path foundation)
   - Run verification gate after Phase 0

4. **Tracking:**
   - Use backlog tasks for progress tracking
   - Update task status via `backlog task edit` command
   - Monitor critical path daily

5. **Release:**
   - Once Phase 5 complete, release flowspec v0.3.0
   - Phase 4 (documentation) can be post-release if needed

---

## Questions & Clarifications

If you have questions about:

- **Business decisions → Review** ADR-002 Consequences section
- **Technical design → Review** ADR-002 Component Design section
- **Implementation order → Review** ADR-003 Phase Breakdown section
- **Timeline estimates → Review** ADR-003 Critical Path section
- **Risks → Review** upgrade-repo-architecture-summary.md Risk Assessment

For additional clarification, consult:
- `docs/building/fix-flowspec-plan.md` - Original root cause analysis
- `backlog/tasks/task-579*.md` - Detailed task breakdowns

---

**End of Architecture Deliverables**

*All documents follow the Michael Nygard ADR format and Gregor Hohpe's architectural philosophy.*
