# Spec-Kitty Deep Review & Comparison with Flowspec

**Author:** Research Analysis
**Date:** 2025-12-12
**Repository Analyzed:** https://github.com/Priivacy-ai/spec-kitty (v0.6.4)

---

## Executive Summary

**Spec-Kitty** is a community-maintained fork of GitHub's Spec Kit that adds a real-time kanban dashboard, worktree-based feature isolation, and multi-agent orchestration for 11 AI coding assistants. It represents a **visibility-first** approach to Spec-Driven Development, optimizing for real-time progress tracking and parallel feature development.

**Flowspec** is a **depth-first** SDD toolkit that emphasizes comprehensive security scanning, sophisticated state machine workflows, deep backlog integration, and multi-language expertise. It builds on spec-kit as a layered extension with a focus on enterprise-grade governance.

### The Blunt Take

**Spec-Kitty wins on:**
- Real-time visibility (live kanban dashboard)
- Developer experience for parallel work (worktrees)
- Multi-agent breadth (11 agents)
- Simplicity of mental model

**Flowspec wins on:**
- Security depth (5+ scanner types, UFFormat)
- Task management sophistication (Backlog.md + MCP)
- Language expertise (13+ ecosystems)
- Workflow governance (state machine, roles, validation)
- Test coverage and code maturity

**Neither is strictly "better" - they serve different needs.** Spec-Kitty is better for teams wanting visibility and parallel agent orchestration. Flowspec is better for teams needing security compliance, sophisticated task management, and enterprise governance.

---

## 1. Project Overview Comparison

| Aspect | Spec-Kitty | Flowspec |
|--------|-----------|----------|
| **Origin** | Community fork of GitHub Spec Kit | Layered extension of Spec Kit |
| **Version** | 0.6.4 | 0.2.358 |
| **Python** | 3.11+ | 3.11+ |
| **CLI Command** | `spec-kitty` | `specify` |
| **PyPI Package** | `spec-kitty-cli` | `specify-cli` |
| **Primary Focus** | Real-time visibility & multi-agent | Security & workflow governance |
| **Core Innovation** | Live kanban dashboard | Unified security scanning |

---

## 2. What Spec-Kitty Does That Flowspec Doesn't

### 2.1 Real-Time Kanban Dashboard

**This is spec-kitty's killer feature.** A built-in HTTP server provides live visualization:

```python
# spec-kitty starts dashboard automatically on init
spec-kitty init my-project --ai claude
# Dashboard available at http://localhost:9237 (auto-port detection)
```

**Features:**
- 4-lane kanban board (Planned → Doing → For Review → Done)
- Real-time progress updates (filesystem scanning every 1-2 seconds)
- Work package visualization with agent assignments
- Completion metrics and task counts
- Multi-feature overview

**Why this matters:** Flowspec has no visual dashboard. You're working blind in terms of progress visualization. With spec-kitty, you can see exactly what each AI agent is working on, identify bottlenecks, and demonstrate progress to stakeholders.

**Flowspec gap:** No equivalent. Would require building a separate dashboard or integrating with external tools.

### 2.2 Worktree-First Architecture

Spec-kitty uses git worktrees for **true feature isolation**:

```
project/
├── .worktrees/
│   ├── 001-auth-system/     # Feature 1 (isolated checkout)
│   ├── 002-dashboard/       # Feature 2 (work in parallel)
│   └── 003-notifications/   # Feature 3 (no branch switching)
├── kitty-specs/
└── src/ (main branch)
```

**Benefits:**
- No branch switching in main repo - just `cd` between worktrees
- Each feature has complete isolation
- Multiple agents can work on different features simultaneously
- Automatic cleanup after merge

**Flowspec approach:** Traditional branch-based development. You switch branches, not directories. This means:
- Context switching requires `git checkout`
- Can't easily work on multiple features simultaneously
- No automatic worktree management

### 2.3 Mission System (Domain Adapters)

Spec-kitty supports **missions** - workflow configurations for different domains:

**Software Dev Mission:**
- Phases: research → design → implement → test → review
- Artifacts: spec.md, plan.md, tasks.md, data-model.md
- Validation: TDD, tests pass, kanban complete

**Research Mission:**
- Phases: question → methodology → gather → analyze → synthesize → publish
- Artifacts: spec.md (research question), findings.md, sources/
- Validation: sources documented, methodology clear

```yaml
# .kittify/missions/software-dev/mission.yaml
name: "Software Dev Kitty"
workflow:
  phases:
    - name: "research"
    - name: "design"
    - name: "implement"
    - name: "test"
    - name: "review"
```

**Flowspec gap:** No mission system. The workflow is fixed for software development. You can't easily adapt it for research, writing, or other domains without significant customization.

### 2.4 Discovery Gates (Mandatory Interviews)

Before any artifact creation, spec-kitty conducts **structured interviews**:

```markdown
## Discovery Gates

WAITING_FOR_DISCOVERY_INPUT

Before proceeding, please answer:
1. What are the core user personas?
2. What is the primary success metric?
3. Are there regulatory constraints?
```

**Key aspects:**
- Proportional depth (trivial features = 1-2 questions, complex = 5+)
- Blocks work until answers provided
- No assumptions - every decision is explicit or marked `[NEEDS CLARIFICATION: ...]`

**Flowspec approach:** Has questioning via AskUserQuestion tool but it's not as formalized. No `WAITING_FOR_*_INPUT` markers or mandatory interview gates.

### 2.5 Multi-Agent Breadth (11 Agents)

| Agent | Spec-Kitty | Flowspec |
|-------|-----------|----------|
| Claude Code | ✅ | ✅ |
| Cursor | ✅ | ✅ |
| Gemini CLI | ✅ | ✅ |
| GitHub Copilot | ✅ | ✅ |
| Windsurf | ✅ | ✅ |
| Qwen Code | ✅ | ❌ |
| opencode | ✅ | ❌ |
| Kilo Code | ✅ | ❌ |
| Auggie CLI | ✅ | ❌ |
| Roo Code | ✅ | ❌ |
| Codex CLI | ✅ | ❌ |
| Amazon Q | ⚠️ (limited) | ❌ |

**Spec-kitty generates agent-specific commands:**
- Claude: `.claude/commands/spec-kitty-*.md`
- Cursor: `.cursor/commands/spec-kitty-*.md`
- Gemini: `.gemini/commands/spec-kitty-*.toml`
- Copilot: `.github/prompts/spec-kitty-*.md`

### 2.6 Accept/Merge Workflow with Metadata Tracking

Formal acceptance gates with audit trail:

```bash
/spec-kitty.accept
# Validates: kanban complete, metadata present, no clarification markers
# Creates: kitty-specs/<feature>/meta.json

/spec-kitty.merge --push
# Merges to main, removes worktree, deletes branch
```

**meta.json example:**
```json
{
  "accepted_at": "2025-12-12T10:30:00Z",
  "accepted_by": "claude-code",
  "mode": "auto",
  "parent_commit": "abc123",
  "activity_log": [
    {"task": "WP01", "agent": "claude", "shell_pid": "12345", "timestamp": "..."}
  ]
}
```

**Flowspec approach:** Uses backlog task completion but no formal accept/merge workflow with metadata tracking.

---

## 3. What Flowspec Does That Spec-Kitty Doesn't

### 3.1 Comprehensive Security Scanning

Flowspec has **enterprise-grade security** built in:

**5 Scanner Types:**
1. **Semgrep** - SAST code scanning
2. **CodeQL** - GitHub's semantic analysis
3. **DAST** - Dynamic testing (Playwright-based)
4. **Trivy** - Container/IaC scanning
5. **Custom Rules** - Organization-specific patterns

**Unified Finding Format (UFFormat):**
```python
# Scanner-agnostic data model
finding = UFinding(
    id="semgrep-sql-injection-001",
    severity=Severity.CRITICAL,
    confidence=Confidence.HIGH,
    cwe="CWE-89",
    owasp="A03:2021",
    sarif_compatible=True
)
```

**Security Commands:**
```bash
/sec:scan      # Run security scanners
/sec:triage    # Analyze findings
/sec:fix       # Generate patches
/sec:report    # Generate audit report
```

**Spec-kitty gap:** No security scanning. You'd need to integrate external tools.

### 3.2 Deep Backlog.md Integration

Flowspec integrates with backlog.md via **MCP server**:

```bash
# Full task lifecycle management
backlog task create "Implement auth" --ac "AC 1" --ac "AC 2" -l backend
backlog task edit 42 -s "In Progress" -a @myself
backlog task edit 42 --check-ac 1  # Progressive AC completion
backlog task edit 42 -s Done
```

**Features:**
- MCP-based task management (not just markdown files)
- Acceptance criteria tracking with checkmarks
- Dependencies between tasks
- Automated task generation from `/flow:specify`
- Search, filtering, labels

**Spec-kitty approach:** Simple `tasks.md` checklist + `/tasks/` directory with work package prompts. No MCP integration, no progressive AC tracking.

### 3.3 Multi-Language Expertise (13+ Languages)

Flowspec includes **language-specific expertise frameworks**:

```
.languages/
├── python/     # Python 3.11+, FastAPI, pytest patterns
├── go/         # Go idioms, testing, error handling
├── rust/       # Ownership, lifetimes, cargo patterns
├── java/       # Spring Boot, JUnit patterns
├── csharp/     # .NET Core, ASP.NET patterns
├── cpp/        # Modern C++, memory management
├── c/          # Systems programming patterns
├── javascript/ # Node.js, React patterns
├── typescript/ # Type-safe patterns
├── kotlin/     # Android/Kotlin patterns
├── mobile/     # iOS/Android patterns
├── systems/    # Low-level systems programming
└── web/        # Full-stack web patterns
```

Each includes: foundations, resources, principles, agent personas, expert references.

**Spec-kitty gap:** No language-specific expertise. Generic software development guidance only.

### 3.4 Problem Sizing Assessment

Flowspec's `/flow:assess` provides **8-dimension complexity scoring**:

```yaml
# Assessment dimensions
complexity:
  effort: 7/10
  components: 5/10
  integrations: 4/10

risk:
  security: 8/10
  compliance: 6/10
  data_sensitivity: 7/10

architecture:
  patterns: 5/10
  breaking_changes: 3/10
  dependencies: 4/10

# Automated recommendation
workflow_mode: "Full SDD"  # or "Spec-Light" or "Skip SDD"
```

**Spec-kitty gap:** No automated complexity assessment. You decide the workflow manually.

### 3.5 Skills System (18 Skills)

Flowspec has **invocable skills** for specialized tasks:

**Core Skills:**
- `architect` - System design, ADRs
- `pm-planner` - SVPG methodology, requirements
- `qa-validator` - Test coverage, quality gates
- `sdd-methodology` - Workflow guidance
- `security-reviewer` - OWASP, threat modeling

**Security Skills (8):**
- `security-analyst`, `security-codeql`, `security-dast`
- `security-fixer`, `security-reporter`, `security-triage`
- `exploit-researcher`, `fuzzing-strategist`

**Invocation:**
```
# Claude Code automatically invokes skills
Skill: security-reviewer
```

**Spec-kitty gap:** No skills system. Functionality is in slash commands only.

### 3.6 Sophisticated State Machine

Flowspec's workflow is a **formal state machine** with 9 states:

```
To Do → Assessed → Specified → Researched → Planned →
  In Implementation → Validated → Deployed → Done
```

**Features:**
- Role-based command namespaces (dev, arch, sec, qa, ops)
- Artifact validation gates
- Inner/outer loop agent classification
- Backward transitions (rework, rollback)
- Human approval gates

**Spec-kitty approach:** Linear workflow without formal state machine. Commands are sequential but not enforced by state validation.

### 3.7 Agent Personas with Deep Guidelines

Flowspec's agent definitions are **comprehensive** (4,500-14,000 lines each):

**Backend Engineer Agent:**
- Python patterns (FastAPI, SQLAlchemy, pytest)
- Database design principles
- API endpoint templates
- Error handling patterns
- Async/await best practices

**Security Reviewer Agent:**
- OWASP Top 10 compliance
- SLSA Levels 1-4 verification
- Threat modeling templates
- Supply chain security (SBOM)

**Spec-kitty approach:** Simple `agent_context` string in mission YAML (~15 lines).

### 3.8 Test Suite Depth

| Metric | Flowspec | Spec-Kitty |
|--------|----------|-----------|
| Test Lines | 39,618+ | ~1,000 |
| Coverage | ~80% | Unknown |
| E2E Tests | Yes (memory, hooks, sync) | Minimal |
| Performance Tests | Yes | No |
| Backward Compatibility | Yes | No |

### 3.9 MCP Server Ecosystem

Flowspec configures **6 MCP servers**:

```json
{
  "mcpServers": {
    "github": {...},       // GitHub API integration
    "serena": {...},       // LSP-grade code understanding
    "playwright": {...},   // Browser automation for DAST
    "trivy": {...},        // Container/IaC security
    "semgrep": {...},      // SAST scanning
    "backlog": {...}       // Task management
  }
}
```

**Spec-kitty gap:** No MCP server configuration. External tool integration is manual.

### 3.10 Hook System

Event-driven workflow automation:

```yaml
# .specify/hooks/hooks.yaml
pre_commit:
  - command: "pytest tests/"
  - command: "/sec:scan"

post_workflow:
  - event: "workflow.assessed"
    command: "notify-slack"
```

**Spec-kitty approach:** Basic git hooks only, no workflow event system.

---

## 4. Head-to-Head Feature Comparison

| Feature | Spec-Kitty | Flowspec | Winner |
|---------|-----------|----------|--------|
| **Real-time Dashboard** | ✅ Built-in kanban | ❌ None | **Spec-Kitty** |
| **Worktree Isolation** | ✅ Automatic | ❌ Branch-based | **Spec-Kitty** |
| **AI Agent Count** | ✅ 11 agents | ⚠️ 5 agents | **Spec-Kitty** |
| **Mission System** | ✅ Software/Research | ❌ Fixed workflow | **Spec-Kitty** |
| **Discovery Gates** | ✅ Mandatory | ⚠️ Optional | **Spec-Kitty** |
| **Security Scanning** | ❌ None | ✅ 5+ scanners | **Flowspec** |
| **Task Management** | ⚠️ Simple markdown | ✅ Backlog MCP | **Flowspec** |
| **Language Expertise** | ❌ Generic | ✅ 13+ languages | **Flowspec** |
| **Complexity Assessment** | ❌ Manual | ✅ 8-dimension | **Flowspec** |
| **Skills System** | ❌ None | ✅ 18 skills | **Flowspec** |
| **State Machine** | ⚠️ Linear | ✅ 9 states + roles | **Flowspec** |
| **Agent Depth** | ⚠️ ~15 lines | ✅ 4,500+ lines | **Flowspec** |
| **Test Coverage** | ⚠️ Minimal | ✅ 39K+ lines | **Flowspec** |
| **MCP Integration** | ❌ None | ✅ 6 servers | **Flowspec** |
| **Hook System** | ⚠️ Git hooks only | ✅ Event-driven | **Flowspec** |
| **Documentation** | ✅ Comprehensive | ✅ Comprehensive | Tie |
| **Ease of Setup** | ✅ Single command | ✅ Single command | Tie |

**Score: Spec-Kitty 5, Flowspec 10, Tie 2**

---

## 5. What Each Project Does Better

### 5.1 Spec-Kitty Does Better

1. **Visual Progress Tracking**
   - Live dashboard eliminates "blind" development
   - Stakeholder-friendly progress visualization
   - Bottleneck identification in real-time

2. **Parallel Development Experience**
   - Worktrees mean no context switching
   - Multiple features simultaneously
   - Clean merge workflow

3. **Multi-Agent Orchestration**
   - More agents supported out of the box
   - Agent-specific command generation
   - Team can use different AI tools

4. **Mental Model Simplicity**
   - Linear workflow is easy to understand
   - Mission system for domain switching
   - Clear spec → plan → tasks → implement → review → merge

5. **Discovery Rigor**
   - Forced interviews prevent assumption drift
   - `WAITING_FOR_*_INPUT` is explicit
   - No clarification markers in final artifacts

### 5.2 Flowspec Does Better

1. **Security Compliance**
   - Enterprise-ready scanning infrastructure
   - OWASP Top 10 and SLSA compliance
   - Unified finding format for all scanners
   - Actionable security reports

2. **Task Management Sophistication**
   - Backlog.md is a proper task system, not markdown files
   - Progressive acceptance criteria tracking
   - MCP integration for AI-native task management
   - Dependencies, labels, search

3. **Code Maturity**
   - 39K+ lines of tests indicate production readiness
   - E2E tests for complex scenarios
   - Backward compatibility testing
   - Performance benchmarks

4. **Workflow Governance**
   - State machine prevents invalid transitions
   - Role-based command namespaces
   - Human approval gates where needed
   - Artifact validation at each stage

5. **Extensibility**
   - Skills system for specialized tasks
   - Hook system for custom automation
   - MCP server ecosystem
   - Language-specific expertise

6. **Agent Depth**
   - Detailed agent personas with real patterns
   - Not just instructions but actual code templates
   - SVPG methodology for PM work
   - Inner/outer loop classification

---

## 6. Recommendations

### Use Spec-Kitty When:

1. **You need real-time visibility** into AI agent work
2. **Multiple teams/agents** work on features simultaneously
3. **Parallel feature development** is the norm
4. **You use varied AI tools** (11 agent support)
5. **Stakeholder demos** require live progress tracking
6. **Simplicity** is valued over governance
7. **Research workflows** are part of your process

### Use Flowspec When:

1. **Security compliance** is non-negotiable (SOC2, HIPAA, etc.)
2. **Task management** needs to be sophisticated (not just checklists)
3. **Multi-language projects** need specialized expertise
4. **Workflow governance** is required (state validation, approvals)
5. **Enterprise integration** via MCP servers is needed
6. **Production-grade** code quality is expected
7. **Long-term maintenance** requires comprehensive tests

### Consider Combining Both:

The projects solve different problems. A hybrid approach could:
- Use spec-kitty's dashboard for visibility
- Use flowspec's security scanning
- Use spec-kitty's worktrees with flowspec's backlog
- Cherry-pick the best ideas from each

---

## 7. Feature Gap Analysis

### Features Flowspec Should Consider Adopting

| Feature | Effort | Impact | Priority |
|---------|--------|--------|----------|
| Real-time dashboard | High | High | **P1** |
| Worktree-based isolation | Medium | High | **P1** |
| Mission system | Medium | Medium | P2 |
| Discovery gates (WAITING_FOR markers) | Low | Medium | P2 |
| Additional AI agents (Qwen, Kilo, etc.) | Low | Low | P3 |

### Features Spec-Kitty Should Consider Adopting

| Feature | Effort | Impact | Priority |
|---------|--------|--------|----------|
| Security scanning | High | High | **P1** |
| Backlog.md integration | Medium | High | **P1** |
| Multi-language expertise | Medium | Medium | P2 |
| State machine validation | Medium | Medium | P2 |
| Skills system | High | Medium | P3 |
| MCP server ecosystem | High | Medium | P3 |

---

## 8. Conclusion

**Spec-Kitty** and **Flowspec** represent two valid philosophies for Spec-Driven Development:

**Spec-Kitty's philosophy:** "Development is chaos; visibility is control."
- Real-time dashboards
- Parallel worktrees
- Multi-agent breadth
- Simple mental model

**Flowspec's philosophy:** "Quality requires governance; depth enables reliability."
- Security scanning
- Sophisticated task management
- Deep agent expertise
- Formal state machine

Neither is inherently superior. The choice depends on your team's needs:

- **Choose visibility** → Spec-Kitty
- **Choose governance** → Flowspec
- **Need both** → Consider integrating ideas from both

The SDD space benefits from having both approaches available. Competition drives innovation, and users win when they can pick the tool that fits their workflow.

---

## Appendix A: Command Comparison

| Spec-Kitty Command | Flowspec Equivalent | Notes |
|-------------------|---------------------|-------|
| `/spec-kitty.constitution` | `/flow:init` | Similar purpose |
| `/spec-kitty.specify` | `/flow:specify` | Both create specs |
| `/spec-kitty.plan` | `/flow:plan` | Both create plans |
| `/spec-kitty.research` | `/flow:research` | Both support research |
| `/spec-kitty.tasks` | (part of `/flow:specify`) | Flowspec creates tasks in specify |
| `/spec-kitty.implement` | `/flow:implement` | Both execute implementation |
| `/spec-kitty.review` | (part of `/flow:validate`) | Flowspec has broader validation |
| `/spec-kitty.accept` | (manual backlog completion) | No formal accept command |
| `/spec-kitty.merge` | (git commands) | No formal merge workflow |
| `/spec-kitty.dashboard` | ❌ None | Gap in Flowspec |
| `/spec-kitty.clarify` | `/speckit:clarify` | Similar |
| `/spec-kitty.analyze` | `/speckit:analyze` | Similar |
| `/spec-kitty.checklist` | `/speckit:checklist` | Similar |
| ❌ None | `/flow:assess` | Gap in Spec-Kitty |
| ❌ None | `/sec:scan` | Gap in Spec-Kitty |
| ❌ None | `/sec:fix` | Gap in Spec-Kitty |
| ❌ None | `/sec:report` | Gap in Spec-Kitty |

## Appendix B: Architecture Comparison

```
SPEC-KITTY ARCHITECTURE:

┌─────────────────────────────────────────────────────────┐
│                    Dashboard (HTTP)                      │
│  ┌───────────┬───────────┬───────────┬───────────┐     │
│  │  Planned  │   Doing   │ Review    │   Done    │     │
│  └───────────┴───────────┴───────────┴───────────┘     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 .worktrees/ (Isolation)                  │
│  ┌─────────────────┐  ┌─────────────────┐               │
│  │ 001-feature-a/  │  │ 002-feature-b/  │  ...          │
│  └─────────────────┘  └─────────────────┘               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Mission System (Domain Adapter)             │
│  ┌─────────────────┐  ┌─────────────────┐               │
│  │  software-dev   │  │    research     │  ...          │
│  └─────────────────┘  └─────────────────┘               │
└─────────────────────────────────────────────────────────┘


FLOWSPEC ARCHITECTURE:

┌─────────────────────────────────────────────────────────┐
│                  Backlog.md (MCP Server)                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Tasks + Acceptance Criteria + Dependencies      │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          State Machine (9 States + Validation)           │
│  To Do → Assessed → Specified → Planned → Impl → ...    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               Security Scanning Layer                    │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐   │
│  │ Semgrep │ CodeQL  │  DAST   │  Trivy  │ Custom  │   │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                MCP Server Ecosystem (6)                  │
│  GitHub + Serena + Playwright + Trivy + Semgrep + BL    │
└─────────────────────────────────────────────────────────┘
```

---

*This analysis was conducted by examining the full source code of both repositories, including CLI implementations, templates, agent definitions, and documentation. No modifications were made to either codebase.*
