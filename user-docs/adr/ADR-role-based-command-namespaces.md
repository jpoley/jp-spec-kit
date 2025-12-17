# ADR: Role-Based Command Namespace Architecture

**Status**: Proposed
**Date**: 2025-12-09
**Author**: Enterprise Software Architect
**Related Tasks**: task-357, task-358, task-359, task-360
**Product**: Flowspec (formerly Flowspec)

---

## Context and Problem Statement

Flowspec currently has 18+ slash commands across two flat namespaces (`/flowspec` and `/speckit`). This creates several user experience and discoverability challenges:

### Current Pain Points

1. **Autocomplete Overload**: 18+ commands in VS Code/Copilot autocomplete makes discovery difficult
2. **Scattered Security Commands**: Five security-related commands (`security_fix`, `security_report`, `security_triage`, `security_web`, `security_workflow`) are mixed with general workflow commands
3. **No Logical Grouping**: Commands lack organization by role or persona (PM, Developer, Security Engineer, QA, SRE)
4. **Poor Discoverability**: Users can't easily find commands relevant to their current role
5. **No Role Context**: System doesn't understand which commands are most relevant for which team member

### The Elevator Problem (Gregor Hohpe's Strategic View)

From a **Penthouse perspective** (Strategic IT Transformation):
- **Business Objective**: Reduce cognitive load and improve time-to-productivity for new users
- **Organizational Impact**: Align tool structure with actual team organization and roles
- **Investment Justification**: Better developer experience (DX) leads to faster adoption and reduced training costs

From the **Engine Room perspective** (Technical Execution):
- Need to refactor 18+ commands into logical namespaces
- Must maintain backwards compatibility with existing workflows
- Should enable future extensibility for new roles and commands

---

## Decision Drivers

1. **User Experience**: Reduce cognitive load and improve command discoverability
2. **Team Alignment**: Map commands to actual team roles (PM, Engineer, Security, QA, SRE)
3. **Backwards Compatibility**: Existing workflows and documentation must continue to work
4. **Extensibility**: Easy to add new roles and commands in the future
5. **Platform Consistency**: Work across both Claude Code CLI and VS Code Copilot
6. **Minimal Migration Pain**: Users should be able to adopt gradually

---

## Considered Options

### Option 1: Flat Namespace with Prefixes (Status Quo)
Keep current structure but add prefixes: `/flowspec-pm-*`, `/flowspec-dev-*`, etc.

**Pros**:
- Zero breaking changes
- Minimal implementation effort
- Backwards compatible by default

**Cons**:
- Still clutters autocomplete with all commands
- No real improvement to discoverability
- Doesn't solve the core problem
- Awkward naming convention

**Verdict**: ❌ Rejected - doesn't address the problem

---

### Option 2: Hierarchical Namespaces with Aliases
Create role-based hierarchies: `/pm/*`, `/dev/*`, `/sec/*`, `/qa/*`, `/ops/*` with aliases for backwards compatibility.

**Pros**:
- Clear role-based organization
- Improved discoverability (autocomplete shows role-specific commands)
- Extensible for future roles
- Aliases maintain backwards compatibility
- Aligns with team structure

**Cons**:
- Requires refactoring command file structure
- Duplicate documentation during deprecation period
- Users need to learn new command names

**Verdict**: ✅ **SELECTED** - Best balance of DX improvement and compatibility

---

### Option 3: Tag-Based Filtering
Keep flat namespace but add role tags; let IDE filter by active role.

**Pros**:
- No command name changes
- Fully backwards compatible
- Single source of truth

**Cons**:
- Requires IDE-specific features (not portable)
- Still shows all commands in basic autocomplete
- Doesn't improve CLI discoverability
- Relies on user manually selecting role every time

**Verdict**: ❌ Rejected - too IDE-dependent

---

## Decision Outcome

**Chosen Option**: Option 2 - Hierarchical Namespaces with Aliases

We will transition to role-based command namespaces over a **12-month deprecation period** with the following structure:

---

## Role-Based Namespace Design

### Primary Role Namespaces

| Namespace | Role | Description | Core Verbs |
|-----------|------|-------------|------------|
| `/pm` | Product Manager | Requirements, assessment, market research | `assess`, `define`, `discover` |
| `/arch` | Architect | System design, technical decisions, planning | `design`, `decide`, `plan` |
| `/dev` | Developer | Implementation, coding, debugging | `build`, `code`, `debug` |
| `/sec` | Security Engineer | Vulnerability scanning, triage, remediation | `scan`, `triage`, `fix` |
| `/qa` | QA Engineer | Testing, validation, quality assurance | `test`, `verify`, `review` |
| `/ops` | SRE/DevOps | Deployment, monitoring, operations | `deploy`, `monitor`, `respond` |

### Utility Namespace

| Namespace | Role | Description | Core Verbs |
|-----------|------|-------------|------------|
| `/speckit` | All Roles | Cross-role utilities, project setup | `init`, `configure`, `sync` |

### Verb Selection Principles

Each role namespace uses **persona-appropriate verbs** that reflect how that role naturally thinks about their work:

- **PM verbs**: Focus on discovery and definition (`assess`, `define`, `discover`, `research`)
- **Architect verbs**: Focus on design and decisions (`design`, `decide`, `plan`, `model`)
- **Developer verbs**: Focus on building (`build`, `code`, `debug`, `refactor`)
- **Security verbs**: Focus on finding and fixing issues (`scan`, `triage`, `fix`, `audit`)
- **QA verbs**: Focus on verification (`test`, `verify`, `review`, `validate`)
- **Ops verbs**: Focus on running systems (`deploy`, `monitor`, `respond`, `scale`)

---

## Command Mapping Matrix

### Product Manager Commands (`/pm`)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:assess` | `/pm:assess` | PM assesses feature viability and complexity |
| `/flow:specify` | `/pm:define` | PM defines requirements (not "specifies" - too technical) |
| `/flow:research` | `/pm:discover` | PM discovers user needs and market gaps |

**Agent Assignment**: `@product-requirements-manager`, `@workflow-assessor`, `@researcher`, `@business-validator`

---

### Architect Commands (`/arch`) **NEW**

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:plan` | `/arch:design` | Architect designs system architecture |
| `/speckit:plan` | `/arch:design-light` | Lightweight design for simpler features |
| *New* | `/arch:decide` | Create Architecture Decision Records (ADRs) |
| *New* | `/arch:model` | Create data models, API contracts, diagrams |

**Agent Assignment**: `@software-architect`, `@platform-engineer`

---

### Developer Commands (`/dev`)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:implement` | `/dev:build` | Developer builds features (action-oriented) |
| `/speckit:implement` | `/dev:build-light` | Lightweight build for simpler features |
| `/flow:prune-branch` | `/dev:cleanup` | Developer cleans up branches |
| *New* | `/dev:debug` | Debugging assistance |
| *New* | `/dev:refactor` | Refactoring guidance |

**Agent Assignment**: `@frontend-engineer`, `@backend-engineer`, `@ai-ml-engineer`, `@frontend-code-reviewer`, `@backend-code-reviewer`

---

### Security Commands (`/sec`)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:security_triage` | `/sec:triage` | Security triages findings by severity |
| `/flow:security_fix` | `/sec:fix` | Security fixes vulnerabilities |
| `/flow:security_report` | `/sec:report` | Security reports on posture |
| `/flow:security_web` | `/sec:scan` | Security scans for vulnerabilities |
| `/flow:security_workflow` | `/sec:audit` | Security audits the workflow |

**Agent Assignment**: `@secure-by-design-engineer`

---

### QA Commands (`/qa`)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:validate` | `/qa:verify` | QA verifies implementation meets requirements |
| `/speckit:checklist` | `/qa:review` | QA reviews against checklist |
| `/speckit:analyze` | `/qa:test` | QA tests code quality and coverage |

**Agent Assignment**: `@quality-guardian`, `@tech-writer`, `@release-manager`

---

### Operations Commands (`/ops`)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:operate` | `/ops:deploy` | Ops deploys to environments |
| *New* | `/ops:monitor` | Ops monitors system health |
| *New* | `/ops:respond` | Ops responds to incidents |
| *New* | `/ops:scale` | Ops scales infrastructure |

**Agent Assignment**: `@sre-agent`

---

### Speckit Utilities (Cross-Role)

| Current Command | New Command | Verb Rationale |
|-----------------|-------------|----------------|
| `/flow:init` | `/speckit:init` | Initialize project (all roles) |
| `/flow:reset` | `/speckit:configure` | Configure workflow settings |
| `/speckit:constitution` | `/speckit:constitution` | Manage project constitution |
| `/speckit:tasks` | `/speckit:tasks` | Manage backlog tasks |
| `/speckit:clarify` | `/speckit:clarify` | Clarify requirements |

---

## Namespace Hierarchy and Naming Conventions

### Hierarchy Rules

```
/{role}:{action}[:{qualifier}]
```

**Examples**:
- `/pm:assess` - Simple action
- `/pm:specify` - Simple action
- `/sec:scan-web` - Qualified action (scan type: web)
- `/dev:implement-light` - Qualified action (variant: light mode)

### Naming Standards

1. **Role Prefix**: Short, memorable (2-3 chars preferred): `pm`, `dev`, `sec`, `qa`, `ops`
2. **Action Verb**: Clear, imperative verb: `assess`, `specify`, `implement`, `validate`, `scan`
3. **Qualifiers** (optional): Hyphenated descriptors: `scan-web`, `implement-light`, `fix-critical`
4. **Case**: All lowercase with hyphens (kebab-case)
5. **Length**: Keep command name under 25 characters total

---

## Backwards Compatibility Strategy

### Alias Approach (12-Month Deprecation)

**Phase 1: Months 0-6** (Soft Deprecation)
- Old commands work via aliases to new commands
- Issue deprecation warning when old command used:
  ```
  ⚠️  /flow:assess is deprecated. Use /pm:assess instead.
  Documentation: https://flowspec.dev/migration
  ```
- All documentation updated to show new commands
- Migration guide published

**Phase 2: Months 6-9** (Hard Deprecation Warning)
- Warnings become more prominent
- Count down to removal date shown:
  ```
  ⚠️  /flow:assess will be removed in 3 months. Use /pm:assess instead.
  Auto-migration script: specify migrate-commands
  ```
- Auto-migration tool available

**Phase 3: Months 9-12** (Final Warning)
- Critical warnings issued
- Commands still work but strongly discouraged
- Telemetry tracks usage of deprecated commands

**Phase 4: Month 12+** (Removal)
- Old commands removed
- Helpful error message with migration path:
  ```
  ❌ Command /flow:assess has been removed.
  Use /pm:assess instead. See migration guide: https://flowspec.dev/migration
  ```

### Alias Implementation

Create symbolic links and command wrappers:

```yaml
# .claude/commands/flow/assess.md (OLD)
---
description: "[DEPRECATED] Use /pm:assess instead"
deprecated: true
replacement: "/pm:assess"
removal_date: "2026-12-09"
---
{{INCLUDE:.claude/commands/pm/assess.md}}
```

---

## Role Selection Architecture

### Design: Interactive Role Selection During Init

When users run `/speckit:init` or `/speckit:configure`, they will be prompted to select their primary role:

```
┌─────────────────────────────────────────────────────────┐
│ Select your primary role for command suggestions:      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   1. Product Manager (PM)                              │
│      assess, define, discover                           │
│                                                         │
│   2. Architect (Arch)                                  │
│      design, decide, model                              │
│                                                         │
│   3. Developer (Dev)                                   │
│      build, debug, refactor                             │
│                                                         │
│   4. Security Engineer (Sec)                           │
│      scan, triage, fix                                  │
│                                                         │
│   5. QA Engineer (QA)                                  │
│      test, verify, review                               │
│                                                         │
│   6. SRE/DevOps (Ops)                                  │
│      deploy, monitor, respond                           │
│                                                         │
│   7. All Roles (Show all commands)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

Enter selection [1-7]:
```

### Storage: flowspec_workflow.yml

Role selection is stored in `flowspec_workflow.yml` (renamed from `flowspec_workflow.yml`):

```yaml
# Flowspec Workflow Configuration
version: "2.0"

# Role-based configuration
roles:
  primary: "dev"              # Selected role: pm, arch, dev, sec, qa, ops, all
  show_all_commands: false    # Override to show all namespaces

  # Role definitions (user-customizable)
  definitions:
    pm:
      display_name: "Product Manager"
      icon: "📋"
      commands: ["assess", "define", "discover"]
      agents:
        - "@product-requirements-manager"
        - "@workflow-assessor"
        - "@researcher"
        - "@business-validator"

    arch:
      display_name: "Architect"
      icon: "🏗️"
      commands: ["design", "decide", "model"]
      agents:
        - "@software-architect"
        - "@platform-engineer"

    dev:
      display_name: "Developer"
      icon: "💻"
      commands: ["build", "debug", "refactor"]
      agents:
        - "@frontend-engineer"
        - "@backend-engineer"
        - "@ai-ml-engineer"

    sec:
      display_name: "Security Engineer"
      icon: "🔒"
      commands: ["scan", "triage", "fix", "audit"]
      agents:
        - "@secure-by-design-engineer"

    qa:
      display_name: "QA Engineer"
      icon: "✅"
      commands: ["test", "verify", "review"]
      agents:
        - "@quality-guardian"
        - "@release-manager"

    ops:
      display_name: "SRE/DevOps"
      icon: "🚀"
      commands: ["deploy", "monitor", "respond", "scale"]
      agents:
        - "@sre-agent"
```

### Future Extensibility: User-Customizable Workflows

The `flowspec_workflow.yml` is designed for **easy user customization**:

1. **Edit Personas**: Users can modify `display_name`, `icon`, and descriptions
2. **Change Commands**: Add/remove commands from each role's `commands` array
3. **Swap Agents**: Assign different agents to roles via the `agents` array
4. **Add Tools**: Future: specify which MCP tools each agent can access
5. **Create Squads**: Future: define multi-agent "squads" for complex workflows

```yaml
# Example: User adds a custom "data" role
roles:
  definitions:
    data:
      display_name: "Data Engineer"
      icon: "📊"
      commands: ["pipeline", "transform", "validate-data"]
      agents:
        - "@data-engineer"
        - "@ai-ml-engineer"
      tools:
        - "mcp__dbt__*"
        - "mcp__airflow__*"
```

### VS Code Copilot Integration

The role selection affects command visibility in VS Code:

1. **Agent Handoffs**: Role-appropriate agents are suggested in handoff buttons
2. **Autocomplete Filtering**: Commands shown prioritize primary role namespace
3. **Context Awareness**: Agents receive role context in their prompt

**Implementation in `.github/agents/*.agent.md`**:

```yaml
name: "pm-assess"
description: "Assess feature complexity and SDD workflow suitability"
target: "flowspec"
tools: [...]
role: "pm"  # NEW FIELD
priority_for_roles: ["pm"]  # Show first for PMs
visible_to_roles: ["pm", "dev", "all"]  # Who can see this
```

---

## Extensibility for Future Roles

### Design Goal: User-Configurable Everything

The architecture is designed so users can easily customize:

| What | Where | How |
|------|-------|-----|
| **Roles** | `flowspec_workflow.yml` | Add/edit role definitions |
| **Commands per Role** | `flowspec_workflow.yml` | Edit `commands` array |
| **Agents per Role** | `flowspec_workflow.yml` | Edit `agents` array |
| **Tools per Agent** | `flowspec_workflow.yml` | Edit `tools` array (future) |
| **Squads** | `flowspec_workflow.yml` | Define multi-agent teams (future) |
| **Handoffs** | `flowspec_workflow.yml` | Define workflow transitions |

### Adding New Roles

To add a new role (e.g., `/data` for Data Engineers):

1. **Create namespace directory**: `.claude/commands/data/`
2. **Add to workflow config** (`flowspec_workflow.yml`):
```yaml
roles:
  definitions:
    data:
      display_name: "Data Engineer"
      icon: "📊"
      commands: ["pipeline", "transform", "validate-data"]
      agents:
        - "@data-engineer"
        - "@ai-ml-engineer"
      tools:
        - "mcp__dbt__*"
        - "mcp__airflow__*"
```
3. **Create command files** in `.claude/commands/data/`
4. **Regenerate agents**: `scripts/bash/sync-copilot-agents.sh`

### Adding New Commands to Existing Role

1. Create command file: `.claude/commands/{role}/{command}.md`
2. Add to role's `commands` array in `flowspec_workflow.yml`
3. Generate Copilot agents: `scripts/bash/sync-copilot-agents.sh`

### Future: Squad Configuration

Multi-agent "squads" can be defined for complex workflows:

```yaml
# flowspec_workflow.yml
squads:
  full-stack:
    name: "Full Stack Development"
    roles: ["arch", "dev", "qa"]
    agents:
      - "@software-architect"
      - "@frontend-engineer"
      - "@backend-engineer"
      - "@quality-guardian"
    handoffs:
      - from: "@software-architect"
        to: ["@frontend-engineer", "@backend-engineer"]
      - from: ["@frontend-engineer", "@backend-engineer"]
        to: "@quality-guardian"

  security-audit:
    name: "Security Audit"
    roles: ["sec", "qa"]
    agents:
      - "@secure-by-design-engineer"
      - "@quality-guardian"
```

---

## Consequences

### Positive

1. **Improved Discoverability**: Users see 3-8 commands instead of 18+
2. **Better Onboarding**: New users can focus on role-relevant commands
3. **Team Alignment**: Tool structure mirrors actual team organization
4. **Reduced Cognitive Load**: Smaller command surface area per role
5. **Extensible**: Easy to add new roles and commands
6. **Platform Agnostic**: Works in both Claude Code CLI and VS Code Copilot

### Negative

1. **Migration Effort**: Existing users must learn new command names
2. **Documentation Debt**: Must maintain dual documentation during deprecation
3. **Breaking Change**: Eventual removal of old commands affects workflows
4. **Increased Complexity**: More namespaces to maintain
5. **Implementation Cost**: Refactoring 18+ commands requires significant effort

### Neutral

1. **Alias Period**: 12-month transition reduces immediate impact
2. **Auto-migration Tool**: Reduces manual migration effort
3. **Gradual Rollout**: Phased approach allows course correction

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users resist change | High | Medium | Clear migration guide, auto-migration tool, gradual deprecation |
| Documentation drift during transition | Medium | High | Automated validation checks, single source of truth |
| Confusion about which command to use | Medium | Medium | Deprecation warnings with clear guidance |
| Breaking existing scripts/workflows | High | High | 12-month deprecation period, aliases remain functional |
| Incomplete migration | Medium | Medium | Telemetry to track usage, targeted outreach to users |

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create role namespace directories
- [ ] Map all commands to new namespaces
- [ ] Implement alias system
- [ ] Update command mapping documentation

### Phase 2: Role Selection (Weeks 3-4)
- [ ] Enhance `/speckit:init` with role selection prompt
- [ ] Update `flowspec_workflow.yml` schema
- [ ] Store role preferences
- [ ] Update VS Code Copilot agent metadata

### Phase 3: Testing (Week 5)
- [ ] Test all aliases work correctly
- [ ] Validate deprecation warnings appear
- [ ] Test role selection in init/reset
- [ ] Verify VS Code integration

### Phase 4: Documentation (Week 6)
- [ ] Publish migration guide
- [ ] Update all documentation to new commands
- [ ] Create video walkthrough
- [ ] Update quickstart guides

### Phase 5: Soft Launch (Month 2)
- [ ] Release with aliases enabled
- [ ] Monitor usage metrics
- [ ] Gather feedback
- [ ] Iterate on UX

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to find command | < 15 seconds | User testing |
| Commands per autocomplete | < 8 per namespace | Count in IDE |
| Migration adoption rate | > 80% by Month 6 | Telemetry |
| User satisfaction | > 4.0/5.0 | Survey |
| Documentation clarity | > 4.5/5.0 | Survey |

---

## Related Documents

- [ADR: Role Selection During Initialization](./ADR-role-selection-during-initialization.md)
- [Design: Command Migration Path](./design-command-migration-path.md)
- [For speckit.constitution: Role-Based Command Standards](./constitution-role-based-command-standards.md)
- [VS Code Copilot Agents Plan](../platform/vscode-copilot-agents-plan.md)
- [Workflow Configuration Reference](../../flowspec_workflow.yml)

---

## Appendix: Complete Command Reference

### Summary by Role

| Role | Namespace | Commands | Verbs |
|------|-----------|----------|-------|
| **PM** | `/pm` | 3 | assess, define, discover |
| **Architect** | `/arch` | 4 | design, decide, model, design-light |
| **Developer** | `/dev` | 5 | build, build-light, cleanup, debug, refactor |
| **Security** | `/sec` | 5 | scan, triage, fix, report, audit |
| **QA** | `/qa` | 3 | test, verify, review |
| **Ops** | `/ops` | 4 | deploy, monitor, respond, scale |
| **Utilities** | `/speckit` | 5 | init, configure, constitution, tasks, clarify |
| **Total** | 7 namespaces | **29 commands** | |

### Migration Quick Reference

| Old Command | New Command | Role |
|-------------|-------------|------|
| `/flow:assess` | `/pm:assess` | PM |
| `/flow:specify` | `/pm:define` | PM |
| `/flow:research` | `/pm:discover` | PM |
| `/flow:plan` | `/arch:design` | Architect |
| `/flow:implement` | `/dev:build` | Developer |
| `/flow:validate` | `/qa:verify` | QA |
| `/flow:operate` | `/ops:deploy` | Ops |
| `/flow:security_*` | `/sec:*` | Security |
| `/flow:init` | `/speckit:init` | Utility |
| `/flow:reset` | `/speckit:configure` | Utility |

---

## References

- Gregor Hohpe's "The Software Architect Elevator" (Strategic IT transformation)
- Gregor Hohpe's "Platform Strategy" (Clarity, Consumption, Credibility)
- VS Code Copilot Agent Documentation
- Claude Code Command Documentation

---

**Reviewers**: @product-requirements-manager, @software-architect, @platform-engineer
**Status**: Awaiting approval
**Next Review Date**: 2025-12-16
