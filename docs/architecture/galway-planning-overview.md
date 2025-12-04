# Galway Host: Architectural Planning Overview

**Author:** Enterprise Software Architect (Hohpe Principles Expert)
**Date:** 2025-12-04
**Status:** Proposed
**Purpose:** Comprehensive architectural planning for galway-assigned tasks

---

## Executive Summary

This document provides high-level architectural guidance for implementing **59 tasks** across **9 functional domains** in the JP Spec Kit project. These tasks represent strategic investments in **security, automation, extensibility, and developer experience**.

**Key Architectural Themes:**
1. **Security-First Platform** - AI-powered vulnerability management as first-class workflow phase
2. **Event-Driven Automation** - Backlog.md integration enables reactive workflows
3. **Hierarchical Organization** - Command structure supports scalability and discoverability
4. **Extensibility by Design** - Skills, plugins, and MCP enable third-party innovation

**Total Implementation Effort:** 16-20 weeks (phased delivery)
**Strategic Value:** Foundation for enterprise-grade SDD platform

---

## Domain Architecture Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    JP SPEC KIT PLATFORM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 1: SECURITY (22 tasks)                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  Scanner     │→ │  AI Triage   │→ │    Fix       │   │  │
│  │  │ Orchestrator │  │   Engine     │  │  Generator   │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  │         │                 │                  │            │  │
│  │         └─────────────────┴──────────────────┘            │  │
│  │                           │                                │  │
│  │                  ┌────────▼────────┐                      │  │
│  │                  │  MCP Server     │                      │  │
│  │                  │  (v2.0)         │                      │  │
│  │                  └─────────────────┘                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 2: WORKFLOW/EVENTS (4 tasks)                     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  Git Hook    │  │  CLI Wrapper │  │  Upstream    │   │  │
│  │  │  (Layer 1)   │  │  (Layer 2)   │  │  (Layer 3)   │   │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │  │
│  │         └──────────────────┴──────────────────┘           │  │
│  │                           │                                │  │
│  │                  ┌────────▼────────┐                      │  │
│  │                  │  Hook Runner    │                      │  │
│  │                  │  (Event Dispatch)│                     │  │
│  │                  └─────────────────┘                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 3: COMMAND MIGRATION (4 tasks)                   │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  .claude/commands/jpspec/   (Workflow commands)  │    │  │
│  │  │  .claude/skills/            (Utility skills)     │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 4: CONSTITUTION/INIT (4 tasks)                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │  Detection   │→ │  LLM         │→ │  Validation  │   │  │
│  │  │  Engine      │  │ Customization│  │  Framework   │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 5: ARCHIVE TASKS (5 tasks)                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │  │
│  │  │ archive-     │→ │  GitHub      │→ │  Post-Hook   │   │  │
│  │  │ tasks.sh     │  │  Workflow    │  │  Integration │   │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 6: SKILLS/SUBAGENTS (2 tasks)                    │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  5 Core Skills: pm-planner, architect,          │    │  │
│  │  │  qa-validator, security-reviewer, sdd-methodology│    │  │
│  │  │                                                   │    │  │
│  │  │  4 Subagents: frontend-eng, backend-eng,        │    │  │
│  │  │  platform-eng, code-reviewer                     │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 7: CORE FEATURES (3 tasks)                       │  │
│  │  - Transition validation modes                            │  │
│  │  - permissions.deny security                              │  │
│  │  - Event model schema                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 8: DOCUMENTATION/QUALITY (3 tasks)               │  │
│  │  - Pre-implementation quality gates                       │  │
│  │  - Production case studies                                │  │
│  │  - Diagram integration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  DOMAIN 9: TOOLING/INFRASTRUCTURE (11 tasks)             │  │
│  │  - Stack selection, CI simulation, spec metrics          │  │
│  │  - Plugin architecture, observability                     │  │
│  │  - macOS CI, MCP library docs                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Domain Deep Dives

### Domain 1: Security (22 tasks) - Weeks 1-10

**Strategic Goal:** Establish security scanning as first-class SDD workflow phase

**Architecture:** Layered Security Platform (ADR-011)
- **Scanner Orchestrator** - Parallel execution of Semgrep, Trivy, CodeQL, Playwright DAST
- **AI Triage Engine** - Claude-powered TP/FP/NI classification with >85% accuracy
- **Fix Generator** - Automated patch generation for common vulnerabilities
- **MCP Server** - Cross-tool integration via Model Context Protocol (v2.0)

**Key Integration Points:**
```
/jpspec:security scan   → Scanner Orchestrator
                        → Unified Finding Format (SARIF-inspired JSON)
                        → docs/security/{feature}-scan-results.json

/jpspec:security triage → AI Triage Engine
                        → Risk scoring: (impact × exploitability) / time
                        → Plain-English explanations

/jpspec:security fix    → Fix Generator
                        → git apply patches
                        → Interactive confirmation mode

/jpspec:security report → Audit Report Generator
                        → Compliance-ready PDF/HTML
```

**Dependencies:**
- Claude API access for AI triage
- Scanner installations (Semgrep, Trivy, CodeQL)
- Git for patch application

**Success Metrics:**
- Triage accuracy >85%
- Scan time <5 min (p95) for 50k LOC
- False positive rate <20% post-triage

**See:** ADR-011 for full architecture

---

### Domain 2: Workflow/Events (4 tasks) - Weeks 11-13

**Strategic Goal:** Enable event-driven automation for backlog.md operations

**Architecture:** Three-Layer Event Emission (ADR-012)
- **Layer 1 (Git Hook)** - Detect file changes, emit low-level events
- **Layer 2 (CLI Wrapper)** - Semantic events from backlog CLI operations
- **Layer 3 (Upstream)** - Contribute native event support to backlog.md

**Event Flow:**
```
backlog task create "title"
    ↓
CLI Wrapper (jpspec-backlog)
    ↓
Emit: task.created event
    ↓
Hook Runner (.claude/hooks/hook-runner.sh)
    ↓
Execute: Matching hooks (Slack notify, CI trigger, etc.)
```

**Key Events:**
- `task.created` - New task in backlog
- `task.status_changed` - Status transition (To Do → In Progress → Done)
- `task.completed` - Task marked Done
- `task.ac_checked` - Acceptance criterion completed

**Integration Examples:**
- **Slack Notifications:** Alert team when tasks blocked
- **Workflow Automation:** Trigger `/jpspec:validate` after implementation completes
- **Metrics Collection:** Track task cycle time, velocity

**Dependencies:**
- Git hooks enabled
- Event schema (ADR-005)
- Hook runner infrastructure

**See:** ADR-012 for full architecture

---

### Domain 3: Command Migration (4 tasks) - Weeks 14-15

**Strategic Goal:** Hierarchical command structure for scalability

**Architecture:** Two-Tier Namespace (ADR-013)
- `.claude/commands/jpspec/` - Workflow phase commands
- `.claude/skills/` - Utility skills (model-invoked)

**Migration Strategy:**
1. Create new directories
2. Move commands to new locations
3. Create backward-compatible symlinks
4. 3-month deprecation period
5. Remove symlinks in v1.0.0

**Benefits:**
- **Discoverability:** Commands grouped by purpose
- **Scalability:** Supports 100+ commands without cognitive overload
- **Extensibility:** Plugin namespaces (`.claude/commands/my-plugin/`)

**User Impact:**
- Zero downtime (symlinks preserve functionality)
- Clear migration guide with automated script
- Commands work identically post-migration

**See:** ADR-013 for full architecture

---

### Domain 4: Constitution/Init (4 tasks) - Week 16

**Strategic Goal:** Streamline constitution creation and validation

**Key Features:**
- **Auto-Detection:** Identify projects without constitution
- **LLM Customization:** Interactive prompts for tailored principles
- **Validation Framework:** Check specs against constitutional rules
- **Integration Tests:** Ensure template system stability

**User Flow:**
```
specify init
    ↓
Detect: No constitution.md found
    ↓
Prompt: "Would you like to create a constitution?"
    ↓
LLM: Ask 5 questions about team values, quality standards
    ↓
Generate: .specify/memory/constitution.md
    ↓
Validate: Spec compliance with new constitution
```

---

### Domain 5: Archive Tasks (5 tasks) - Week 17

**Strategic Goal:** Automated task lifecycle management

**Components:**
- **archive-tasks.sh** - Flexible filtering (--all, --done-by DATE)
- **GitHub Workflow** - Scheduled archival (weekly, monthly)
- **Post-Hook** - Agent-triggered archiving after workflow completion

**Use Cases:**
- Retention policies (archive tasks >30 days old)
- Sprint cleanup (archive all Done tasks)
- Demo environments (archive all tasks)

**See:** `docs/adr/archive-tasks-architecture.md` for full design

---

### Domain 6: Skills/Subagents (2 tasks) - Week 18

**Strategic Goal:** Extensible agent system

**5 Core Skills:**
1. **pm-planner** - PRD creation, task breakdown
2. **architect** - ADR creation, system design
3. **qa-validator** - Test plan creation, quality gates
4. **security-reviewer** - Security assessment, threat modeling
5. **sdd-methodology** - Workflow guidance, best practices

**4 Engineering Subagents:**
1. **frontend-engineer** - React/TypeScript implementation
2. **backend-engineer** - API/database implementation
3. **platform-engineer** - CI/CD, infrastructure
4. **code-reviewer** - PR reviews, code quality

**Integration:**
```
/jpspec:specify
    ↓
Invoke: pm-planner skill
    ↓
Generate: docs/prd/{feature}.md
    ↓
Create: backlog tasks with acceptance criteria
```

---

### Domain 7-9: Smaller Domains (Weeks 19-20)

**Core Features (3 tasks):**
- Transition validation modes (strict/flexible/custom)
- permissions.deny for security policies
- Event model schema formalization

**Documentation/Quality (3 tasks):**
- Pre-implementation quality gates (hook)
- Production case studies (5 real-world examples)
- Diagram integration (Mermaid, PlantUML)

**Tooling/Infrastructure (11 tasks):**
- Stack selection wizard during init
- Local CI simulation (`act` integration)
- Spec quality metrics CLI
- macOS CI matrix testing
- Plugin architecture framework

---

## Cross-Domain Integration Patterns

### Pattern 1: Event-Driven Security Workflow

```
Implement Phase Completes
    ↓
Emit: implement.completed event
    ↓
Hook: post-implement.sh
    ↓
Trigger: /jpspec:security scan
    ↓
Emit: security.scan_completed event
    ↓
Hook: post-security.sh
    ↓
Update: backlog task with security findings
```

### Pattern 2: Constitution-Enforced Quality Gates

```
/jpspec:specify
    ↓
Generate: docs/prd/{feature}.md
    ↓
Hook: post-specify.sh (quality gate)
    ↓
Validate: Spec against constitution.md rules
    ↓
If fails: Block /jpspec:implement
    ↓
If passes: Create backlog tasks
```

### Pattern 3: MCP-Enabled Security Dashboard

```
Claude Agent
    ↓
MCP Client: Connect to security-scanner MCP server
    ↓
Query: security://findings?severity=critical
    ↓
Generate: Executive security report
    ↓
Action: Create GitHub issues for critical findings
```

---

## Implementation Phasing Strategy

### Phase 1: Foundation (Weeks 1-5)
**Focus:** Security infrastructure, event model
**Deliverables:**
- Scanner orchestrator with Semgrep/Trivy
- Unified finding format (JSON Schema)
- Event emitter module
- Git hook for backlog events

**Success Criteria:**
- Security scan completes in <5 min
- Events emitted for all backlog operations

---

### Phase 2: Intelligence (Weeks 6-10)
**Focus:** AI triage, automated remediation
**Deliverables:**
- AI triage engine with Claude integration
- Fix generator with 3 strategies
- Benchmark dataset (100 labeled findings)
- CLI wrapper for backlog operations

**Success Criteria:**
- Triage accuracy >85%
- >70% of generated patches apply cleanly

---

### Phase 3: Integration (Weeks 11-15)
**Focus:** MCP server, command migration, upstream contribution
**Deliverables:**
- Security MCP server (tools + resources)
- Hierarchical command structure
- Migration script with dry-run
- Upstream PR for backlog.md events

**Success Criteria:**
- MCP server validates against spec
- Command migration 100% successful
- Zero command discovery regressions

---

### Phase 4: Extensibility (Weeks 16-20)
**Focus:** Skills, constitution, tooling
**Deliverables:**
- 5 core skills + 4 subagents
- Constitution init workflow
- Archive automation
- Quality gates and documentation

**Success Criteria:**
- Skills invokable from all /jpspec commands
- Constitution validation prevents bad specs
- Archive automation reduces manual work by 80%

---

## Risk Management

### High-Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| **AI Triage Accuracy <85%** | High | Few-shot learning, rule-based fallback, active learning loop |
| **Scanner Version Skew** | Medium | Pin versions, adapter compatibility matrix, automated tests |
| **Event Duplication** | Low | Event deduplication, idempotent hooks |
| **Command Migration Breakage** | Medium | Symlinks, 3-month deprecation, automated testing |
| **Upstream Contribution Rejected** | Low | Layers 1&2 work independently, optional feature flag |

### Risk Mitigation Strategies

**Technical Debt Prevention:**
- Write ADRs before implementation (done for domains 1-3)
- Implement telemetry for performance monitoring
- Add feature flags for risky features
- Maintain backward compatibility for 2 major versions

**Dependency Management:**
- Pin scanner versions in tool dependency manager
- Use semantic versioning for event schema
- Isolate external API calls (Claude, GitHub) with circuit breakers

---

## Success Metrics (Platform-Level)

### Objective Measures

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| **Security scan adoption** | 0% | >80% of projects | 6 months |
| **Triage time per finding** | 20 min | <5 min | 3 months |
| **Workflow automation rate** | 0% | >50% | 6 months |
| **Command discovery time** | 2 min | <30 sec | 1 month |
| **False positive rate** | 70% | <20% | 6 months |

### Subjective Measures

| Metric | Target | Method |
|--------|--------|--------|
| **Developer Satisfaction (NPS)** | >40 | Quarterly survey |
| **Onboarding Time Reduction** | -20% | New user time tracking |
| **Support Ticket Reduction** | -50% | GitHub Issues analysis |

---

## Architecture Quality Assessment (7 C's)

### 1. Clarity - 9/10
- Clear domain boundaries
- Well-defined integration patterns
- Comprehensive ADRs for major decisions

### 2. Consistency - 10/10
- All domains follow same ADR format
- Consistent event schema across domains
- Unified error handling patterns

### 3. Composability - 10/10
- Event-driven architecture enables decoupling
- MCP integration supports tool composition
- Plugin system enables third-party extensions

### 4. Consumption (DX) - 9/10
- Migration scripts automate transitions
- Clear documentation for each domain
- Backward compatibility preserves workflows

### 5. Correctness - 8/10
- JSON Schema validation for events/findings
- CI validation for structure integrity
- Benchmark datasets for AI accuracy

### 6. Completeness - 8/10
- Covers all 59 tasks across 9 domains
- Missing: cross-domain integration tests (future work)

### 7. Changeability - 10/10
- Phased implementation allows pivots
- Feature flags enable gradual rollout
- Event schema versioning supports evolution

**Overall Platform Score: 9.1/10** - Enterprise-grade architecture

---

## Next Steps

### Immediate Actions (Week 1)

1. **Review ADRs:** Software architects review ADR-011, ADR-012, ADR-013
2. **Setup Infrastructure:** Configure Claude API, scanner tools, CI environment
3. **Create Benchmarks:** Build security finding dataset for triage validation
4. **Team Alignment:** Share architecture overview with all engineers

### Decision Points

**Checkpoint 1 (Week 5):** Evaluate scanner orchestrator performance
- **Go:** Proceed to AI triage if scan time <5 min
- **Pivot:** Optimize orchestrator if performance inadequate

**Checkpoint 2 (Week 10):** Evaluate AI triage accuracy
- **Go:** Proceed to MCP server if accuracy >85%
- **Pivot:** Enhance AI prompts or add more training data

**Checkpoint 3 (Week 15):** Evaluate command migration adoption
- **Go:** Remove symlinks early if adoption >90%
- **Extend:** Maintain symlinks longer if adoption <50%

---

## Conclusion

This architectural plan provides a **solid foundation** for transforming JP Spec Kit into an **enterprise-grade SDD platform**. The phased approach balances **risk** (early validation of AI triage) with **value delivery** (security scanning available in Week 5).

**Key Success Factors:**
1. **AI Triage Accuracy:** Must hit >85% to justify AI investment
2. **Event Infrastructure:** Must be reliable for workflow automation
3. **Developer Experience:** Migration/changes must be frictionless

**Strategic Positioning:**
- **Security-First:** Differentiator in SDD market
- **AI-Augmented:** Leverages Claude for unique capabilities
- **Extensible Platform:** Supports third-party innovation

**Recommended Decision:** **Proceed with phased implementation**, starting with security domain (highest strategic value).

---

## References

### Architecture Decision Records
- **ADR-011:** Security Domain Unified Architecture
- **ADR-012:** Event-Driven Workflow Integration
- **ADR-013:** Command Architecture Restructuring
- **ADR-005:** Event Model Architecture (existing)
- **ADR-008:** Security MCP Server Architecture (existing)

### External References
- [Gregor Hohpe: The Software Architect Elevator](https://architectelevator.com/)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs/)

---

*This architecture follows Hohpe's "Architect Elevator" philosophy: connecting business strategy (penthouse) with technical implementation (engine room) through clear communication and measurable success criteria.*
