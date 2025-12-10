# VS Code Role Selection & Integration - Executive Summary

**Date**: 2025-12-09
**Author**: Platform Engineer Agent
**Status**: Design Complete, Ready for Implementation

---

## Overview

This design enables **role-based customization** of VS Code Copilot agents in JP Spec Kit. Users select their primary role (Product Manager, Developer, Security Engineer, QA Engineer, or Full Workflow) during project initialization, and VS Code automatically displays only role-relevant commands and handoffs.

## Business Value

| Benefit | Impact |
|---------|--------|
| **Reduced Cognitive Load** | Users see 5-8 commands instead of 23 |
| **Faster Onboarding** | New team members get role-specific workflows |
| **Better Team Collaboration** | Clear handoffs between PM → Dev → QA → SRE |
| **Increased Adoption** | Improved UX drives VS Code Copilot usage |

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│  /jpspec:init or /jpspec:reset                               │
│  └─> User selects role: PM | Dev | Sec | QA | All           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Configuration Storage (Dual Strategy)                       │
│  ├─> specflow_workflow.yml (team defaults, version-controlled) │
│  └─> .vscode/settings.json (user overrides, gitignored)     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  sync-copilot-agents.sh Enhancement                          │
│  ├─> Read role config from specflow_workflow.yml              │
│  ├─> Add role metadata to agent frontmatter                 │
│  └─> Configure VS Code agent pinning                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  VS Code Copilot Agent Display                               │
│  ├─> Pinned agents (role-specific, top of chat)             │
│  ├─> Role-filtered handoffs (next steps guidance)           │
│  └─> De-prioritized other agents (still accessible)         │
└─────────────────────────────────────────────────────────────┘
```

## Role Definitions

### Product Manager (PM)
**Focus**: Requirements, research, business validation
**Commands**: `/jpspec:assess`, `/jpspec:specify`, `/jpspec:research`
**Handoffs**: PM → Developer (PRD complete → technical design)

### Developer (Dev)
**Focus**: Architecture, implementation, deployment
**Commands**: `/jpspec:plan`, `/jpspec:implement`, `/jpspec:operate`
**Handoffs**: Dev → QA (code complete → validation)

### Security Engineer (Sec)
**Focus**: Security scanning, triage, vulnerability fixes
**Commands**: `/jpspec:security_*`, `/jpspec:validate` (security aspects)
**Handoffs**: Sec → Dev (security issues → fixes)

### QA Engineer (QA)
**Focus**: Testing, documentation, quality validation
**Commands**: `/jpspec:validate`, `/speckit:checklist`
**Handoffs**: QA → SRE (validation passed → deployment)

### Full Workflow (All)
**Focus**: Complete SDD workflow (all phases)
**Commands**: All `/jpspec` and `/speckit` commands
**Handoffs**: Linear progression through all phases

## Configuration Example

### specflow_workflow.yml (Team Defaults)

```yaml
vscode_roles:
  default_role: "all"

  roles:
    pm:
      name: "Product Manager"
      workflows: ["assess", "specify", "research"]
      agents: ["jpspec-assess", "jpspec-specify", "jpspec-research"]

    dev:
      name: "Developer"
      workflows: ["plan", "implement", "operate"]
      agents: ["jpspec-plan", "jpspec-implement", "jpspec-operate"]

    # ... sec, qa, all roles
```

### .vscode/settings.json (User Override)

```json
{
  "jpspec.vscode.role": {
    "primary": "dev",
    "secondary": ["qa", "sec"],
    "visibility": "de-prioritize",
    "mode": "user"
  },

  "chat.agent.pinnedAgents": [
    "jpspec-plan",
    "jpspec-implement",
    "jpspec-operate"
  ]
}
```

## User Experience Flow

### 1. Project Initialization

```bash
specify init --here
```

**Prompt**:
```
Select your primary role for VS Code chat handoffs:
  1. Product Manager (PM)
  2. Developer (Dev)
  3. Security Engineer (Sec)
  4. QA Engineer (QA)
  5. Full Workflow (All) [default]

Choice [5]: 2

Configure for:
  1. This machine only (user-specific)
  2. Entire team (version-controlled)

Mode [1]: 2
```

**Result**: Developer role configured, agents pinned in VS Code

### 2. VS Code Chat Interface

**Before** (All role):
- 23 agents shown alphabetically
- Unclear which to use first
- No workflow guidance

**After** (Developer role):
- 3 pinned agents at top: `jpspec-plan`, `jpspec-implement`, `jpspec-operate`
- Role-specific handoffs: "✓ Planning Complete → Begin Implementation"
- Other agents de-prioritized but accessible

### 3. Cross-Role Handoff

**Scenario**: Developer completes implementation, hands off to QA

```
/jpspec:implement
# → Completes implementation

# VS Code shows handoff button:
"🔀 Hand off to QA → Run Validation"
# → Clicking opens jpspec-validate with context
```

## Implementation Phases

### Phase 1: Foundation (2-3 days)
- [ ] Add `vscode_roles` schema to `specflow_workflow.yml`
- [ ] Implement role selection in `init.md` and `reset.md`
- [ ] Generate `.vscode/settings.json` with role config

### Phase 2: Agent Metadata (2 days)
- [ ] Enhance `sync-copilot-agents.sh` with `get_role_metadata()`
- [ ] Add role and priority fields to agent frontmatter
- [ ] Regenerate all 23 agents with metadata

### Phase 3: Advanced Features (3-4 days)
- [ ] Implement role switching (`specify config set vscode.role`)
- [ ] Add CI/CD role validation workflows
- [ ] Implement telemetry (privacy-preserving)

### Phase 4: Documentation (1-2 days)
- [ ] Update user guides with role examples
- [ ] Create troubleshooting guide
- [ ] Add VS Code integration screenshots

**Total Estimated Effort**: 8-11 days

## Success Metrics

### Technical
- ✅ Role selection completes in < 5 seconds
- ✅ Agent generation with metadata < 2 seconds
- ✅ All 5 roles have correct agent mappings
- ✅ Team mode prevents `.vscode/settings.json` commits
- ✅ User mode allows local overrides

### User Experience
- ✅ PM users see only 3-5 relevant agents prominently
- ✅ Dev users get clear handoff chains
- ✅ Cross-role handoffs marked with 🔀 icon
- ✅ Role switching works without regeneration
- ✅ Documentation clear for all roles

### Adoption
- 📈 Target: 70% of users select a specific role (not "all")
- 📈 Target: 90% handoff click-through rate
- 📈 Target: <5% support requests about role selection

## Key Design Decisions

### 1. Configuration Storage: Dual Strategy ✅
**Decision**: Use both `specflow_workflow.yml` (team) and `.vscode/settings.json` (user)

**Rationale**:
- Team defaults in git enable consistent onboarding
- User overrides respect individual preferences
- VS Code native settings.json integration

### 2. Agent Visibility: De-prioritize ✅
**Decision**: De-prioritize (not hide) non-role agents

**Rationale**:
- Flexibility for users who need cross-role commands
- Discoverability preserved
- Gradual UX improvement vs hard restriction

### 3. Multi-Role Support: Primary + Secondary ✅
**Decision**: Support 1 primary + N secondary roles

**Rationale**:
- Real teams wear multiple hats (e.g., Dev + QA)
- Primary determines pinning, secondary adds visibility
- Complexity balanced with flexibility

### 4. Handoff Approval: Manual ✅
**Decision**: Cross-role handoffs require manual approval (`send: false`)

**Rationale**:
- Prevents accidental workflow progression
- Encourages communication between roles
- Aligns with human approval gates in SDD

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| VS Code API changes | Monitor release notes, fallback to priority metadata |
| User confusion | Clear defaults (role: "all"), comprehensive docs |
| Team vs user conflicts | Explicit override hierarchy documented |
| Privacy concerns | Telemetry opt-in only, hash all sensitive data |

## Next Steps

1. **Review**: Platform team reviews this design (approval gate)
2. **Spike**: Prototype VS Code agent pinning (1 day)
3. **Implement Phase 1**: Foundation tasks (task-361, task-364)
4. **User Testing**: Early feedback from each role (PM, Dev, QA, Sec)
5. **Iterate**: Refine based on feedback
6. **Document**: Comprehensive user guide and examples
7. **Release**: Announce via changelog and demo video

## Related Documentation

- **Full Design**: `docs/platform/vscode-role-selection-design.md` (13,000+ words)
- **VS Code Integration Plan**: `docs/platform/vscode-copilot-agents-plan.md`
- **Workflow Architecture**: `docs/guides/workflow-architecture.md`
- **Agent Loop Classification**: `docs/reference/agent-loop-classification.md`

## Implementation Tasks

Created in backlog:
- `task-361`: Role selection in init/reset commands (HIGH)
- `task-362`: VS Code role integration architecture (HIGH)
- `task-363`: sync-copilot-agents.sh enhancements (MEDIUM)
- `task-364`: specflow_workflow.yml schema extension (HIGH)
- `task-365`: CI/CD role validation workflows (MEDIUM)
- `task-366`: Telemetry framework (LOW)

**View tasks**:
```bash
backlog task list -l vscode --plain
backlog task list -l infrastructure --plain
```

---

**Platform Engineer Sign-off**: Design complete and ready for implementation. Recommend starting with Phase 1 (Foundation) to validate UX assumptions before investing in advanced features.

*Generated by Platform Engineer Agent on 2025-12-09*
