# Flowspec Upgrade-Repo: Visual Architecture Summary

**Date:** 2026-01-06
**Quick Reference:** Visual diagrams and tables for rapid understanding

---

## The Problem (Current State)

```
User runs: flowspec upgrade-repo
    │
    ├─► Downloads templates from GitHub ✅
    ├─► Creates backup ✅
    ├─► Merges base + extension templates ✅
    ├─► Copies templates to project ✅
    │
    └─► STOPS HERE ❌

What's NOT happening:
    ❌ Agent naming wrong (hyphens not dots)
    ❌ MCP config not updated
    ❌ Skills not synced (9/21 missing)
    ❌ Workflow config still v1.0
    ❌ Deprecated files remain
    ❌ Broken {{INCLUDE:}} directives
    ❌ /flow:operate references
```

**Result:** Broken VSCode integration, manual fixes required.

---

## The Solution (Proposed Architecture)

```
User runs: flowspec upgrade-repo
    │
    ├─► Phase 0: Pre-Upgrade Validation
    │   ├─ Detect versions ✅
    │   ├─ Validate structure ✅
    │   └─ Create backup ✅
    │
    ├─► Phase 1: Template Updates
    │   ├─ Download templates ✅
    │   ├─ Merge templates ✅
    │   ├─ Fix agent naming (hyphen→dot) ✅
    │   └─ Deploy templates ✅
    │
    ├─► Phase 2: Configuration Synthesis
    │   ├─ Regenerate .mcp.json ✅
    │   ├─ Upgrade flowspec_workflow.yml to v2.0 ✅
    │   ├─ Sync .claude/skills/ (21 skills) ✅
    │   └─ Update .vscode/extensions.json ✅
    │
    ├─► Phase 3: Cleanup & Migrations
    │   ├─ Remove .specify/ directory ✅
    │   ├─ Remove _DEPRECATED_*.md ✅
    │   ├─ Remove /flow:operate references ✅
    │   └─ Remove {{INCLUDE:}} directives ✅
    │
    ├─► Phase 4: Post-Upgrade Validation
    │   ├─ Verify agent naming ✅
    │   ├─ Verify workflow config v2.0 ✅
    │   ├─ Verify MCP servers configured ✅
    │   └─ Verify skills synced ✅
    │
    └─► Phase 5: Reporting
        ├─ Git diff summary ✅
        ├─ Backup location ✅
        ├─ Validation results ✅
        └─ Next steps guidance ✅
```

**Result:** Fully functional VSCode integration, zero manual fixes.

---

## Component Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    upgrade_repo() Function                     │
│                    (Orchestration Layer)                       │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│  Migration   │   │    Artifact      │   │   Cleanup    │
│   Registry   │   │  Synchronizer    │   │ Orchestrator │
├──────────────┤   ├──────────────────┤   ├──────────────┤
│ - v1.0→v2.0  │   │ - MCP config     │   │ - .specify/  │
│ - Agent name │   │ - Workflow v2.0  │   │ - _DEPRECATED│
│ - Remove ops │   │ - Skills sync    │   │ - {{INCLUDE}}│
│ - Remove inc │   │                  │   │ - /flow:ops  │
└──────────────┘   └──────────────────┘   └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │     Upgrade      │
                    │    Validator     │
                    ├──────────────────┤
                    │ - Agent naming   │
                    │ - Workflow v2.0  │
                    │ - MCP config     │
                    │ - Skills count   │
                    └──────────────────┘
```

---

## Data Flow

```
INPUT: flowspec upgrade-repo
    │
    ▼
┌─────────────────────────────────────┐
│ DETECTION                           │
│ • AI assistant: copilot             │
│ • Current version: v1.0             │
│ • Tech stack: Python + React        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ BACKUP                              │
│ .flowspec-backup-20260106-143022/   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ DOWNLOAD & MERGE                    │
│ base-spec-kit v0.0.20 ──┐           │
│ flowspec v0.3.0 ────────┤           │
│                         ├─► Merged  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ DEPLOY TEMPLATES                    │
│ .github/agents/                     │
│ ├─ flow.assess.agent.md             │
│ ├─ flow.specify.agent.md            │
│ ├─ flow.plan.agent.md               │
│ ├─ flow.implement.agent.md          │
│ ├─ flow.validate.agent.md           │
│ └─ flow.submit-n-watch-pr.agent.md  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ REGENERATE CONFIG                   │
│ .mcp.json                           │
│ ├─ backlog (required)               │
│ ├─ github (required)                │
│ ├─ serena (required)                │
│ ├─ flowspec-security (Python)       │
│ ├─ playwright-test (React)          │
│ ├─ trivy (security)                 │
│ └─ semgrep (security)               │
│                                     │
│ flowspec_workflow.yml               │
│ ├─ version: "2.0"                   │
│ ├─ roles: {...}                     │
│ ├─ custom_workflows: {...}          │
│ └─ agent_loops: {...}               │
│                                     │
│ .claude/skills/ (21 skills)         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ RUN MIGRATIONS                      │
│ ✓ migrate_workflow_v2               │
│ ✓ fix_agent_naming                  │
│ ✓ remove_flow_operate               │
│ ✓ remove_broken_includes            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ CLEANUP                             │
│ ✓ Removed .specify/                 │
│ ✓ Removed _DEPRECATED_*.md          │
│ ✓ Cleaned {{INCLUDE:}} from prompts │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ VALIDATE                            │
│ ✅ Agents: 6 files, dot notation     │
│ ✅ Workflow: v2.0, no operate        │
│ ✅ MCP: 7 servers configured         │
│ ✅ Skills: 21 files present          │
└─────────────────────────────────────┘
    │
    ▼
OUTPUT: Fully functional flowspec integration
```

---

## Implementation Timeline

### Sequential (1 Person)

```
Week 1:  ████████████ Phase 0 (2-3 days)
Week 2:  ████████████████ Phase 1 (3-4 days)
Week 3:  ████████ Phase 2 (2-3 days)
Week 3:  ████ Phase 4 (1-2 days)
Week 4:  ████████ Phase 5 (2-3 days)

Total: 14-18 days
```

### Parallel (2 People)

```
Week 1:
Person A: ████████████ Phase 0 critical path (2 days)
Person B: ████████ Phase 0 parallel tasks (2 days)

Week 2:
Person A: ████████████████ Phase 1 critical path (3 days)
Person B: ████████ Phase 1 parallel tasks (2 days)

Week 2:
Person A: ████████ Phase 2 (2-3 days)
Person B: ████ Phase 4 (1 day)

Week 3:
Both:     ████████ Phase 5 (2 days)

Total: 8-10 days
```

---

## Task Dependencies

```
Phase 0 (Foundation)
    579.01 ──────────────────────┐
    (Remove /flow:operate)       │
                                 ▼
    579.02                   579.05
    (Remove {{INCLUDE:}})    (Update workflow)
                                 │
    579.03                       │
    (Call generate_mcp_json)     │
                                 │
    579.04                       │
    (Sync skills)                │
                                 │
    579.06                       │
    (Remove deprecated)          │
                                 │
                                 ▼
                         Phase 1 (Agents)
                             579.07 ───────┐
                             (Fix filenames)│
                                           ▼
                             579.08        579.12
                             (Fix names)   (Handoffs)
                                           │
                             579.09        │
                             (Add assess)  │
                                           │
                             579.10        │
                             (Add .github) │
                                           │
                             579.11        │
                             (Remove /spec)│
                                           │
                                           ▼
                                 Phase 2 (MCP)
                                     579.13 ─────┐
                                     (Template)  │
                                                 ▼
                                     579.14      579.15
                                     (Generate)  (Health check)
                                                 │
                                                 ▼
                                         Phase 4 (Docs)
                                             579.16
                                             (Update docs)

                                             579.17
                                             (Archive)
                                                 │
                                                 ▼
                                          Phase 5 (Verify)
                                             579.18
                                             (E2E test)
```

**Critical Path (longest chain):**
```
579.01 → 579.05 → 579.07 → 579.08 → 579.12 → 579.13 → 579.14 → 579.15 → 579.18
```
Duration: ~10-12 days

---

## Agent Naming Convention

### Before (WRONG)

```yaml
# File: flow-specify.agent.md
---
name: "flow-specify"
description: "Create specs"
---
```

**Problems:**
- Filename uses hyphens (wrong for VSCode)
- Name is kebab-case string (wrong for menu)
- VSCode can't discover agent
- Menu displays incorrectly

### After (CORRECT)

```yaml
# File: flow.specify.agent.md
---
name: FlowSpecify
description: "Create or update feature specifications"
target: "chat"
tools:
  - "Read"
  - "Write"
  - "mcp__backlog__*"
handoffs:
  - label: "Create Technical Design"
    agent: "flow.plan"
---
```

**Benefits:**
- Filename uses dots (VSCode standard)
- Name is PascalCase identifier (menu-friendly)
- VSCode discovers agent correctly
- Menu displays "FlowSpecify" cleanly
- Handoffs work correctly

---

## MCP Configuration

### Before (INCOMPLETE)

```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"]
    }
  }
}
```

**Problems:**
- Only 1 server (need 6+)
- No github (agents can't access PRs)
- No serena (agents can't understand code)
- No security scanners

### After (COMPREHENSIVE)

```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena",
              "serena-mcp-server", "--project", "${PWD}"]
    },
    "flowspec-security": {
      "command": "uv",
      "args": ["--directory", ".", "run", "python",
              "-m", "flowspec_cli.security.mcp_server"]
    },
    "playwright-test": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    },
    "trivy": {
      "command": "npx",
      "args": ["-y", "@aquasecurity/trivy-mcp"]
    },
    "semgrep": {
      "command": "npx",
      "args": ["-y", "@returntocorp/semgrep-mcp"]
    }
  }
}
```

**Benefits:**
- 7 servers (3 required + 4 additional)
- Agents can access all needed tools
- Security scanning integrated
- E2E testing supported

---

## Workflow Config Migration

### Before (v1.0)

```yaml
version: "1.0"

states:
  - "To Do"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"  # REMOVED in v2.0
  - "Done"

workflows:
  operate:  # REMOVED in v2.0
    command: "/flow:operate"
    agents:
      - "sre-agent"
```

**Problems:**
- Version 1.0 schema
- Has "operate" workflow (removed)
- Has "Deployed" state (outer loop)
- Missing v2.0 sections (roles, custom_workflows)

### After (v2.0)

```yaml
version: "2.0"

roles:
  primary: "dev"
  definitions:
    dev: {...}
    arch: {...}
    sec: {...}

states:
  - "To Do"
  - "Assessed"  # NEW in v2.0
  - "Specified"
  - "Researched"  # NEW in v2.0
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Done"
  # "Deployed" removed (outer loop)

workflows:
  assess: {...}  # NEW in v2.0
  specify: {...}
  research: {...}  # NEW in v2.0
  plan: {...}
  implement: {...}
  validate: {...}
  # "operate" removed (outer loop)

custom_workflows:  # NEW in v2.0
  quick_build: {...}
  full_design: {...}

agent_loops:  # NEW in v2.0
  inner: [...]
  outer: [...]
```

**Benefits:**
- Version 2.0 schema
- No "operate" workflow (correctly outer loop)
- Has v2.0 sections (roles, custom_workflows, agent_loops)
- Assessment and research steps added

---

## Validation Gates

### Phase 0 Verification

```bash
# No /flow:operate references
rg "/flow:operate" . | wc -l
# Expected: 0

# No {{INCLUDE:}} directives
rg "{{INCLUDE:" templates/ | wc -l
# Expected: 0

# upgrade-repo has new logic
rg "generate_mcp_json|sync_skills" src/flowspec_cli/__init__.py | wc -l
# Expected: >= 3
```

### Phase 1 Verification

```bash
# All agents use dot notation
ls templates/.github/agents/*.agent.md | grep "flow\." | wc -l
# Expected: 6

# All agent names are PascalCase
rg '^name: Flow[A-Z]' templates/.github/agents/*.agent.md | wc -l
# Expected: 6

# Assess agent exists
[ -f templates/.github/agents/flow.assess.agent.md ] && echo "OK"
# Expected: OK
```

### Phase 2 Verification

```bash
# Template has required servers
jq '.mcpServers | keys | length' templates/.mcp.json
# Expected: >= 6

# generate_mcp_json updated
rg "trivy|semgrep|serena" src/flowspec_cli/__init__.py | wc -l
# Expected: >= 3
```

### Phase 5 Verification (E2E)

**Manual Checks in VSCode:**
- [ ] Open agent dropdown in VSCode Copilot
- [ ] Verify 6 agents visible: FlowAssess, FlowSpecify, FlowPlan, FlowImplement, FlowValidate, FlowSubmitPR
- [ ] Run `/flow:assess` command
- [ ] Verify agent handoff to `/flow:specify` works
- [ ] Check MCP servers start: `./scripts/check-mcp-servers.sh`
- [ ] Verify no deprecated files: `ls .specify/` (should fail)
- [ ] Verify workflow v2.0: `yq '.version' flowspec_workflow.yml` (should show "2.0")

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Critical path delays** | Medium | High | Daily tracking, pair programming |
| **Integration failures** | Medium | High | Phase-level validation gates |
| **Scope creep** | Low | Medium | Strict AC adherence |
| **Regression bugs** | Medium | High | Comprehensive test suite |
| **360KB __init__.py** | High | Medium | Optional Phase 3 refactoring |
| **User customizations** | Low | Medium | Backup/rollback strategy |

**Overall Risk Level:** MEDIUM (with mitigation strategies in place)

---

## Success Criteria Checklist

**Before Release:**

- [ ] All Phase 0-2 tasks complete
- [ ] Phase 5 E2E test passes on auth.poley.dev
- [ ] `flowspec upgrade-repo` on test project produces:
  - [ ] 6 agents with dot notation (flow.*.agent.md)
  - [ ] Agent names in PascalCase (FlowAssess, FlowSpecify, etc.)
  - [ ] `.mcp.json` with 6+ servers
  - [ ] `flowspec_workflow.yml` v2.0
  - [ ] `.claude/skills/` with 21 skills
  - [ ] No `.specify/` directory
  - [ ] No `_DEPRECATED_*.md` files
  - [ ] No `/flow:operate` references
  - [ ] No `{{INCLUDE:}}` directives
- [ ] VSCode Copilot shows all 6 agents correctly
- [ ] MCP servers start without errors
- [ ] All tests pass (unit, integration, E2E)

**Then:** Ship flowspec v0.3.0 with confidence.

---

## Quick Links

- **ADR-001:** Agent Naming Convention - `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-001-vscode-copilot-agent-naming-convention.md`
- **ADR-002:** Architecture Redesign - `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-002-upgrade-repo-architecture-redesign.md`
- **ADR-003:** Implementation Approach - `/Users/jasonpoley/prj/jp/flowspec/docs/adr/ADR-003-upgrade-repo-implementation-approach.md`
- **Summary:** Architecture Summary - `/Users/jasonpoley/prj/jp/flowspec/docs/building/upgrade-repo-architecture-summary.md`
- **Epic Task:** task-579 - `/Users/jasonpoley/prj/jp/flowspec/backlog/tasks/task-579 - EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md`

---

*This visual summary provides quick-reference diagrams and tables. For detailed rationale, see the ADRs.*
