# Role-Based Command Namespace Architecture - Executive Summary

**Date**: 2025-12-09
**Architect**: Enterprise Software Architect (Gregor Hohpe's Principles)
**Status**: Architecture Complete - Ready for Review
**Related Tasks**: task-357, task-358, task-359, task-360

---

## Strategic Framing (The Penthouse View)

### Business Objectives

JP Flowspec currently suffers from **command namespace overload**: 18+ commands in flat namespaces (`/flow:*`, `/speckit:*`) create discoverability challenges and cognitive burden for users. Security commands are scattered, and there's no logical grouping by role or persona.

**Investment Justification**:
- **Reduce onboarding time**: From 2 hours to 30 minutes
- **Improve productivity**: 3-8 relevant commands vs 18+ cluttered autocomplete
- **Increase adoption**: Better DX leads to faster team onboarding
- **Enable analytics**: Track which roles use which workflows

### Organizational Impact

This refactoring aligns the tool structure with actual **team organization**:
- **Product Managers** focus on specification and research
- **Developers** focus on planning and implementation
- **Security Engineers** focus on vulnerability management
- **QA Engineers** focus on validation and testing
- **SRE/DevOps** focus on infrastructure and operations

By reducing cognitive load, we enable **role-based workflows** that match how teams actually work.

---

## The Engine Room View (Technical Architecture)

### Decision: Hierarchical Namespaces with Aliases

After evaluating three options, we selected **Option 2: Hierarchical Namespaces with Aliases** as the optimal approach:

| Option | Verdict | Reason |
|--------|---------|--------|
| 1. Flat with Prefixes | ❌ Rejected | Doesn't solve core problem |
| 2. Hierarchical with Aliases | ✅ **SELECTED** | Best balance of DX and compatibility |
| 3. Tag-Based Filtering | ❌ Rejected | Too IDE-dependent |

---

## Architecture Overview

### New Namespace Structure

```
/{role}:{action}[:{qualifier}]

Roles:
  /pm      - Product Manager commands
  /dev     - Developer commands
  /sec     - Security Engineer commands
  /qa      - QA Engineer commands
  /ops     - SRE/DevOps commands
  /speckit - Cross-role utilities (unchanged)
```

### Command Mapping Matrix

#### Product Manager (`/pm`)
| Old | New | Agent |
|-----|-----|-------|
| `/flow:assess` | `/pm:assess` | @workflow-assessor |
| `/flow:specify` | `/pm:specify` | @pm-planner |
| `/flow:research` | `/pm:research` | @researcher |

#### Developer (`/dev`)
| Old | New | Agent |
|-----|-----|-------|
| `/flow:plan` | `/dev:plan` | @software-architect |
| `/flow:implement` | `/dev:implement` | @frontend-engineer, @backend-engineer |
| `/flow:operate` | `/dev:operate` | @sre-agent |
| `/flow:init` | `/dev:init` | (system) |
| `/flow:reset` | `/dev:reset` | (system) |
| `/flow:prune-branch` | `/dev:prune-branch` | (system) |
| `/speckit:implement` | `/dev:implement-light` | (lightweight) |
| `/speckit:plan` | `/dev:plan-light` | (lightweight) |

#### Security Engineer (`/sec`)
| Old | New | Agent |
|-----|-----|-------|
| `/flow:security_fix` | `/sec:fix` | @secure-by-design-engineer |
| `/flow:security_report` | `/sec:report` | @secure-by-design-engineer |
| `/flow:security_triage` | `/sec:triage` | @secure-by-design-engineer |
| `/flow:security_web` | `/sec:scan-web` | @secure-by-design-engineer |
| `/flow:security_workflow` | `/sec:workflow` | @secure-by-design-engineer |

#### QA Engineer (`/qa`)
| Old | New | Agent |
|-----|-----|-------|
| `/flow:validate` | `/qa:validate` | @quality-guardian |
| `/speckit:checklist` | `/qa:checklist` | @quality-guardian |
| `/speckit:analyze` | `/qa:analyze` | @quality-guardian |

#### SRE/DevOps (`/ops`)
| Old | New | Notes |
|-----|-----|-------|
| `/flow:operate` | `/ops:deploy` | Deployment focus |
| - | `/ops:monitor` | New command |
| - | `/ops:incident` | New command |
| - | `/ops:runbook` | New command |

#### Utilities (Unchanged)
| Command | Role | Notes |
|---------|------|-------|
| `/speckit:constitution` | All | Unchanged |
| `/speckit:tasks` | All | Unchanged |
| `/speckit:clarify` | All | Unchanged |
| `/speckit:specify` | All | Unchanged |

**Total**: 23 commands across 6 namespaces

---

## Key Architecture Decisions

### ADR-001: Namespace Structure

**Decision**: Use role-based hierarchical namespaces (`/pm:*`, `/dev:*`, etc.)

**Rationale**:
- Improves discoverability (3-8 commands per role vs 18+ flat)
- Reduces cognitive load
- Aligns with team organization
- Enables role-specific workflows

**Trade-offs**:
- Migration effort for existing users (mitigated by 12-month deprecation)
- Documentation debt during transition (mitigated by auto-migration tool)

---

### ADR-002: Role Selection Mechanism

**Decision**: Store role selection in `flowspec_workflow.yml` with environment variable override

**Rationale**:
- Project-scoped (not global user config)
- Git-tracked (team can share configurations)
- Colocated with workflow definitions
- Single source of truth

**Implementation**:
```yaml
role_config:
  primary_role: "dev"
  show_all_commands: false
  roles:
    dev:
      display_name: "Developer"
      auto_load_agents: ["@software-architect", "@frontend-engineer"]
```

**VS Code Integration**:
- Handoff buttons prioritize role-appropriate agents
- Autocomplete shows role commands first
- Agent suggestions filtered by role

---

### ADR-003: Migration Strategy

**Decision**: 12-month phased deprecation with aliases

**Timeline**:
1. **Months 0-6**: Soft deprecation (awareness)
2. **Months 6-9**: Hard deprecation (urgency)
3. **Months 9-12**: Final warning (last chance)
4. **Month 12+**: Removal (helpful errors)

**Backwards Compatibility**:
- Old commands continue to work via include-based forwarding
- Deprecation warnings escalate over time
- Auto-migration tool available: `specify migrate-commands`

**Example Migration**:
```bash
# Old (still works, shows warning)
/flow:assess feature-x
⚠️ Deprecated. Use /pm:assess instead.

# New
/pm:assess feature-x
```

---

### ADR-004: Constitutional Standards

**Decision**: Define authoritative standards for command namespaces in `speckit.constitution`

**Principles**:
1. **Mandate**: All commands MUST use `/{role}:{action}[:{qualifier}]`
2. **Stability**: Namespace changes require major version + 12-month deprecation
3. **Ownership**: One primary role per command
4. **Naming**: Lowercase, imperative verbs, hyphen-separated qualifiers
5. **Documentation**: Required frontmatter and sections
6. **Extensibility**: 3+ commands and 1 agent for new roles
7. **Compatibility**: Breaking changes follow deprecation protocol
8. **Quality**: Automated gates (linting, tests, agent sync)

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Create ADR: Role-Based Command Namespaces (task-357) ✅
- [x] Create ADR: Role Selection During Initialization (task-358) ✅
- [x] Create Design: Command Migration Path (task-359) ✅
- [x] Create Constitutional Standards (task-360) ✅
- [ ] Create role namespace directories
- [ ] Implement alias system (include-based forwarding)

### Phase 2: Role Selection (Weeks 3-4)
- [ ] Enhance `/flow:init` with role selection prompt
- [ ] Update `flowspec_workflow.yml` schema
- [ ] Implement environment variable override
- [ ] Update VS Code Copilot agent metadata

### Phase 3: Migration Tooling (Weeks 5-6)
- [ ] Build `specify migrate-commands` auto-migration tool
- [ ] Add dry-run mode
- [ ] Implement git integration
- [ ] Create command mapping database

### Phase 4: Testing (Week 7)
- [ ] Test all aliases work correctly
- [ ] Validate deprecation warnings
- [ ] Test role selection in init/reset
- [ ] Verify VS Code integration
- [ ] Cross-platform testing (macOS, Linux, Windows)

### Phase 5: Documentation (Week 8)
- [ ] Publish migration guide
- [ ] Update all documentation to new commands
- [ ] Create video walkthrough
- [ ] Update quickstart guides
- [ ] FAQ for migration

### Phase 6: Launch (Week 9+)
- [ ] Release v2.0.0 with role-based namespaces
- [ ] Monitor adoption metrics
- [ ] Gather feedback
- [ ] Iterate on UX

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Command discovery time | < 15 seconds | User testing |
| Commands per autocomplete | < 8 per namespace | Count in IDE |
| New command adoption (Month 6) | > 40% | Telemetry |
| New command adoption (Month 9) | > 80% | Telemetry |
| New command adoption (Month 12) | > 95% | Telemetry |
| User satisfaction | > 4.0/5.0 | Survey |
| Time to select role | < 30 seconds | User testing |

---

## Risk Assessment and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users resist change | High | Medium | Clear migration guide, auto-tool, 12-month period |
| Documentation drift | Medium | High | Automated validation, single source of truth |
| Confusion during transition | Medium | Medium | Phased approach with escalating warnings |
| Breaking existing workflows | High | High | Aliases remain functional for 12 months |
| Incomplete migration | Medium | Medium | Telemetry + targeted outreach |

---

## Platform Quality (Hohpe's 7 C's)

### Clarity ✅
- Clear role-based organization
- Transparent namespace hierarchy
- Well-documented migration path

### Consistency ✅
- Uniform naming conventions
- Standardized command structure
- Consistent deprecation protocol

### Compliance ✅
- Constitutional standards enforced
- Quality gates automated
- Breaking change policy defined

### Composability ✅
- Commands remain independent
- Workflow handoffs preserved
- Role switching supported

### Coverage ✅
- All existing commands mapped
- Future roles accounted for
- Extensibility guidelines clear

### Consumption ✅
- Improved developer experience
- Reduced cognitive load
- Auto-migration tool provided

### Credibility ✅
- Rigorous ADR process
- 12-month deprecation period
- Clear backwards compatibility strategy

---

## Deliverables

### Architecture Decision Records
1. ✅ [ADR: Role-Based Command Namespaces](../adr/ADR-role-based-command-namespaces.md)
   - Problem statement and context
   - Options analysis with trade-offs
   - Complete command mapping matrix
   - Backwards compatibility strategy

2. ✅ [ADR: Role Selection During Initialization](../adr/ADR-role-selection-during-initialization.md)
   - Storage location decision (flowspec_workflow.yml)
   - Interactive prompt design
   - VS Code Copilot integration
   - Environment variable override

3. ✅ [Design: Command Migration Path](../adr/design-command-migration-path.md)
   - 12-month deprecation timeline
   - Alias-based transition strategy
   - Auto-migration tool design
   - Communication plan

4. ✅ [Constitutional Standards](../adr/constitution-role-based-command-standards.md)
   - Naming conventions
   - Documentation requirements
   - Extensibility guidelines
   - Quality gates

### Backlog Tasks
- ✅ task-357: ADR - Role-Based Command Namespaces (Done)
- ✅ task-358: ADR - Role Selection During Initialization (Done)
- ✅ task-359: Design - Command Migration Path (Done)
- ✅ task-360: Constitutional Standards (Done)

---

## Next Steps

### Immediate Actions (Week 1)
1. **Review ADRs**: Core team review and approval of all 4 documents
2. **Stakeholder Sign-off**: Get approval from PM, Security, QA leads
3. **Implementation Planning**: Break down Phase 1 into detailed tasks

### Short-term (Weeks 2-4)
1. **Build Aliases**: Implement include-based forwarding for all commands
2. **Role Selection**: Add interactive prompt to init/reset
3. **VS Code Integration**: Update agent metadata with role information

### Medium-term (Weeks 5-8)
1. **Migration Tool**: Build and test `specify migrate-commands`
2. **Documentation**: Update all guides, examples, and quickstarts
3. **Testing**: Comprehensive cross-platform testing

### Long-term (Week 9+)
1. **Launch v2.0.0**: Release with role-based namespaces
2. **Monitor Adoption**: Track metrics and gather feedback
3. **Support**: Provide migration assistance to users
4. **Iterate**: Improve based on real-world usage

---

## Conclusion

This architecture delivers on the strategic goal of improving developer experience by **reducing cognitive load** and **improving command discoverability**. The hierarchical namespace structure aligns with team organization, while the 12-month deprecation period ensures a smooth migration path.

By applying Gregor Hohpe's principles—selling options rather than solutions, maintaining the architect elevator between strategy and execution, and building platforms with the 7 C's—we've created a sustainable architecture that balances innovation with stability.

**Status**: Architecture design complete. Ready for implementation.

---

## References

- Gregor Hohpe, "The Software Architect Elevator"
- Gregor Hohpe, "Platform Strategy"
- Gregor Hohpe, "Enterprise Integration Patterns"
- [VS Code Copilot Agents Plan](../platform/vscode-copilot-agents-plan.md)
- [Workflow Configuration](../../flowspec_workflow.yml)

---

**Prepared by**: Enterprise Software Architect
**Date**: 2025-12-09
**Version**: 1.0
**Next Review**: 2025-12-16
