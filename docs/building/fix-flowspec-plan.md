# Flowspec Release Alignment Plan

**Created**: 2026-01-06
**Status**: Final - Pass 5/5
**Source Analysis**: auth.poley.dev vs flowspec

## Executive Summary

This document identifies required changes to align flowspec with the target state demonstrated in auth.poley.dev, focusing on VSCode Copilot agent integration, MCP plugin standardization, and command namespace cleanup.

---

## CRITICAL ROOT CAUSE

**`flowspec upgrade-repo` is COMPLETELY BROKEN.**

The user ran `flowspec upgrade-repo` on auth.poley.dev TODAY (2026-01-06) and the resulting state shows:
- Wrong agent filename convention (hyphens vs dots)
- Missing MCP configuration
- Broken `{{INCLUDE:}}` directives referencing non-existent partials
- Outdated workflow config (v1.0 instead of v2.0)
- Missing skills
- Legacy `.specify/` directory not removed
- `/flow:operate` still referenced (MUST BE REMOVED EVERYWHERE)

**ALL discrepancies between flowspec and auth.poley.dev are due to the broken upgrade process.**

The upgrade-repo command is NOT:
- Copying the correct agent templates
- Updating .mcp.json
- Removing deprecated files/directories
- Updating flowspec_workflow.yml to v2.0
- Removing `/flow:operate` references
- Syncing skills

**This is a P0 blocker for the flowspec release.**

---

## Pass 1 Findings: Repository Structure Comparison

### 1. VSCode Copilot Agents (`.github/agents/`)

**auth.poley.dev HAS:**
```
.github/agents/
├── flow.assess.agent.md
├── flow.implement.agent.md
├── flow.plan.agent.md
├── flow.specify.agent.md
├── flow.submit-n-watch-pr.agent.md
└── flow.validate.agent.md
```

**flowspec HAS:**
```
templates/.github/agents/   (templates only, not deployed)
├── flow-implement.agent.md
├── flow-plan.agent.md
├── flow-specify.agent.md
├── flow-submit-n-watch-pr.agent.md
└── flow-validate.agent.md

NO .github/agents/ directory in flowspec itself!
```

**Critical Issue**:
- Flowspec uses HYPHEN notation (`flow-implement.agent.md`)
- auth.poley.dev uses DOT notation (`flow.implement.agent.md`)
- Flowspec templates missing `flow-assess.agent.md`

### 2. Agent File Format Comparison

**auth.poley.dev format (simple):**
```yaml
---
name: FlowAssess
description: Evaluate feature complexity...
---
# Content
```

**flowspec template format (extended):**
```yaml
---
name: "flow-implement"
description: "Execute implementation..."
target: "chat"
tools:
  - "Read"
  - "Write"
  - ...
handoffs:
  - label: "Run Validation"
    agent: "flow-validate"
    ...
---
# Content
```

**Question**: Which format is correct for VSCode Copilot? Need to verify.

### 3. MCP Configuration Gap

**flowspec .mcp.json:**
- github
- serena
- playwright-test
- trivy
- semgrep
- shadcn-ui
- chrome-devtools
- backlog
- flowspec-security

**auth.poley.dev .mcp.json:**
- backlog (only)

**Action Required**: auth.poley.dev needs full MCP config from flowspec

### 4. Command Namespace Issues

**flowspec has `/spec:*` commands that should be REMOVED:**
```
.claude/commands/spec/
├── analyze.md
├── checklist.md
├── clarify.md
├── configure.md
├── constitution.md
├── implement.md
├── init.md
├── plan.md
├── specify.md
└── tasks.md
```

Per user requirement: "NOT having specify commands, only having specific flow commands"

**auth.poley.dev has legacy `.specify/` directory** that should be removed.

### 5. Workflow Configuration Drift

**auth.poley.dev flowspec_workflow.yml:**
- Version 1.0
- Still has `operate` transition (removed in flowspec v2)
- Missing v2.0 features (roles, custom_workflows, agent_loops)

**flowspec flowspec_workflow.yml:**
- Version 2.0
- No `operate` transition
- Has roles, custom_workflows, agent_loops sections

---

## Preliminary Fix List

### HIGH PRIORITY (Blocking Release)

1. **Add `.github/agents/` to flowspec** - Required for VSCode helpers
2. **Standardize agent filename convention** - Dots vs hyphens
3. **Remove `/spec:*` commands from flowspec** - Per user requirement
4. **Update flowspec templates with correct agent format**

### MEDIUM PRIORITY (Release Quality)

5. **Create standard MCP config template** for target repos
6. **Update auth.poley.dev flowspec_workflow.yml to v2.0**
7. **Remove `.specify/` directory from auth.poley.dev**
8. **Update auth.poley.dev CLAUDE.md** (still mentions `/flow:operate`)

### LOW PRIORITY (Polish)

9. **Sync skills between repos** (flowspec has 21, auth.poley.dev has 9)
10. **Standardize memory/ directory structure**
11. **Clean up legacy files**

---

## Open Questions

1. What is the correct `.github/agents/*.agent.md` format for VSCode?
2. Should agent names use PascalCase (`FlowAssess`) or kebab-case (`flow-assess`)?
3. Which MCP servers are REQUIRED vs optional for target repos?
4. Should templates include the full handoffs/tools metadata or simple format?

---

## Pass 2 Findings: Deep Dive - auth.poley.dev

### 6. CRITICAL: {{INCLUDE:}} Directives Don't Work

**PR #1125 (Jan 5, 2026)** confirmed:
- `{{INCLUDE:}}` syntax does NOT work in Claude command files
- Only `@import` works in CLAUDE.md files
- These directives were removed from flowspec commands

**auth.poley.dev still has broken `{{INCLUDE:}}` directives:**
```
# In .github/prompts/flow.*.prompt.md files:
{{INCLUDE:.claude/partials/flow/_constitution-check.md}}
{{INCLUDE:.claude/partials/flow/_workflow-state.md}}
{{INCLUDE:.claude/partials/flow/_rigor-rules.md}}
```

**BUT:** auth.poley.dev doesn't even have `.claude/partials/` directory!

**Action Required**:
- Remove all `{{INCLUDE:}}` directives from auth.poley.dev prompts
- OR inline the content from flowspec's templates/partials/

### 7. VSCode Agent Menu Integration

From the user's screenshot, the VSCode agent dropdown shows:
- **FlowSpecify**
- **FlowPlan**
- **FlowImplement**
- **FlowValidate**
- **FlowSubmitPR**
- **FlowAssess**

These map to `.github/agents/*.agent.md` files with `name:` in YAML frontmatter.

**Naming Convention Confirmed:**
- File: `flow.assess.agent.md` (dots, not hyphens)
- Name in frontmatter: `FlowAssess` (PascalCase)

**flowspec templates use wrong format:**
- File: `flow-implement.agent.md` (hyphens - WRONG)
- Name: `"flow-implement"` (kebab-case - WRONG)

### 8. Agent Format Clarification

The extended format with `tools:` and `handoffs:` in flowspec templates may be for future GitHub Copilot features, but for current VSCode integration:

**Minimum Required:**
```yaml
---
name: FlowAssess
description: Brief description for menu tooltip
---
# Agent content/instructions
```

**Extended (future-proof):**
```yaml
---
name: FlowAssess
description: Brief description
target: "chat"
tools: [...]
handoffs: [...]
---
```

### 9. Skills Directory Discrepancy

**flowspec/.claude/skills/ (21 skills):**
- architect, constitution-checker, context-extractor
- exploit-researcher, fuzzing-strategist, gather-learnings
- patch-engineer, pm-planner, qa-validator
- sdd-methodology, security-analyst, security-codeql
- security-custom-rules, security-dast, security-fixer
- security-reporter, security-reviewer, security-triage
- security-workflow, workflow-executor

**auth.poley.dev/.claude/skills/ (9 skills):**
- architect, constitution-checker, pm-planner
- qa-validator, sdd-methodology, security-fixer
- security-reporter, security-reviewer, security-workflow

**Missing from auth.poley.dev:**
- context-extractor
- exploit-researcher, fuzzing-strategist, patch-engineer
- security-analyst, security-codeql, security-custom-rules
- security-dast, security-triage
- gather-learnings, workflow-executor

---

## Pass 3 Findings: Flowspec Deep Dive

### 10. /spec:* Command References

Found 28 files referencing `/spec:*` commands in flowspec:

**In active code paths:**
- `.claude/commands/spec/` (10 files) - Active slash commands
- `templates/commands/spec/` (10 files) - Template sources
- `.claude/commands/flow/init.md` - References `/spec:*`
- `.claude/commands/flow/reset.md` - References `/spec:*`

**In documentation/tests:**
- `tests/test_*.py` - Test files
- `templates/skills/constitution-checker/` - Skill references
- `user-docs/guides/` - User documentation
- `build-docs/` - Build documentation

**Removal Impact Analysis:**
- Need to update `/flow:init` and `/flow:reset` to not reference `/spec:*`
- Tests referencing `/spec:*` need updating or removal
- Documentation needs updating

### 11. Template vs Deployed Commands

**flowspec has BOTH:**
1. `templates/commands/` - Source templates (copied during init)
2. `.claude/commands/` - Deployed commands (for flowspec repo itself)

**Template purpose:**
- `flowspec init` copies templates to target repos
- Templates should NOT have `/spec:*` namespace

**Deployed purpose:**
- Used by flowspec repo itself for development
- May keep `/spec:*` for internal use IF needed

**Decision Point:** Should `/spec:*` be removed entirely or just from templates?

### 12. Flowspec Init Behavior

From `src/flowspec_cli/__init__.py` (360KB file):
- Contains embedded `COPILOT_AGENT_TEMPLATES`
- `flowspec init` writes agents from these templates
- Templates use hyphen naming (flow-implement.agent.md)

**This is the source of the naming mismatch!**

The CLI embeds templates with wrong naming convention that gets deployed to target repos.

### 13. Command Files Structure

**flowspec flow commands (18 files):**
```
.claude/commands/flow/
├── _DEPRECATED_operate.md  (marked deprecated)
├── assess.md
├── custom.md
├── generate-prp.md
├── implement.md
├── init.md
├── intake.md
├── map-codebase.md
├── plan.md
├── research.md
├── reset.md
├── security_fix.md
├── security_report.md
├── security_triage.md
├── security_web.md
├── security_workflow.md
├── specify.md
├── submit-n-watch-pr.md
└── validate.md
```

**auth.poley.dev flow commands (19 files):**
Same structure but ALSO has the deprecated operate file

---

## Pass 4 Findings: Plugin/MCP Requirements

### 14. Required MCP Servers for Target Repos

Based on flowspec's functionality, target repos should have these MCP servers:

**REQUIRED (Core Functionality):**
| Server | Purpose | Required For |
|--------|---------|--------------|
| `backlog` | Task management | All workflows |
| `github` | PR/Issue/Code operations | /flow:submit-n-watch-pr |
| `serena` | Code understanding & edits | /flow:implement, /flow:validate |

**RECOMMENDED (Enhanced Features):**
| Server | Purpose | Required For |
|--------|---------|--------------|
| `playwright-test` | Browser automation | E2E testing in /flow:validate |
| `trivy` | Security scanning | /sec:* commands |
| `semgrep` | SAST scanning | /sec:* commands |

**OPTIONAL (UI Development):**
| Server | Purpose | Required For |
|--------|---------|--------------|
| `shadcn-ui` | Component library | Frontend projects |
| `chrome-devtools` | Browser inspection | Frontend debugging |

**INTERNAL (Flowspec Only):**
| Server | Purpose |
|--------|---------|
| `flowspec-security` | Security MCP server (flowspec-specific) |

### 15. Agent Template MCP Dependencies

The flowspec agent templates reference these MCP tool patterns:
```yaml
tools:
  - "mcp__github__*"     # GitHub operations
  - "mcp__backlog__*"    # Task management
  - "mcp__serena__*"     # Code understanding
```

**This means target repos MUST have these MCP servers configured for agents to work!**

### 16. Standard MCP Config Template

Proposed `.mcp.json` for target repos:

```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"],
      "description": "Backlog.md task management"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "description": "GitHub API operations"
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server", "--project", "${PWD}"],
      "description": "LSP-grade code understanding"
    },
    "playwright-test": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"],
      "description": "Browser automation for E2E tests"
    },
    "trivy": {
      "command": "npx",
      "args": ["-y", "@aquasecurity/trivy-mcp"],
      "description": "Security scanning"
    },
    "semgrep": {
      "command": "npx",
      "args": ["-y", "@returntocorp/semgrep-mcp"],
      "description": "SAST code scanning"
    }
  }
}
```

---

## Pass 5 Findings: Final Consolidation & Action Plan

### 17. Answers to Open Questions

1. **What is the correct `.github/agents/*.agent.md` format for VSCode?**
   - File naming: `flow.{command}.agent.md` (dots, not hyphens)
   - Name in frontmatter: PascalCase (`FlowAssess`, `FlowImplement`)
   - Minimum required: `name` and `description` fields
   - Extended fields (`tools`, `handoffs`, `target`) are optional

2. **Should agent names use PascalCase or kebab-case?**
   - **PascalCase** for the `name:` field (what shows in VSCode menu)
   - Dot notation for filenames

3. **Which MCP servers are REQUIRED vs optional?**
   - REQUIRED: `backlog`, `github`, `serena`
   - RECOMMENDED: `playwright-test`, `trivy`, `semgrep`
   - OPTIONAL: `shadcn-ui`, `chrome-devtools`

4. **Should templates include full handoffs/tools metadata?**
   - YES - include for future-proofing and GitHub Copilot extensibility
   - Current VSCode integration uses minimal format but extended is harmless

---

## CONSOLIDATED ACTION PLAN

### Phase 0: FIX UPGRADE-REPO (ROOT CAUSE)

| # | Task | Priority | Files Affected |
|---|------|----------|----------------|
| 0.1 | **FIX `flowspec upgrade-repo` command** | P0 | `src/flowspec_cli/__init__.py` or upgrade module |
| 0.2 | Upgrade-repo MUST: copy correct agents | P0 | Agent templates with dot naming |
| 0.3 | Upgrade-repo MUST: update .mcp.json | P0 | Standard MCP config |
| 0.4 | Upgrade-repo MUST: update flowspec_workflow.yml | P0 | v2.0 workflow config |
| 0.5 | Upgrade-repo MUST: remove deprecated files | P0 | `.specify/`, `_DEPRECATED_*.md` |
| 0.6 | Upgrade-repo MUST: sync skills | P0 | `.claude/skills/` |
| 0.7 | **REMOVE `/flow:operate` EVERYWHERE** | P0 | ALL files in flowspec AND templates |

### Phase 1: Flowspec Core Fixes (BLOCKING RELEASE)

| # | Task | Priority | Files Affected |
|---|------|----------|----------------|
| 1.1 | Fix agent filename convention in CLI | P0 | `src/flowspec_cli/__init__.py` (COPILOT_AGENT_TEMPLATES) |
| 1.2 | Rename template agents: hyphen → dot | P0 | `templates/.github/agents/*.agent.md` |
| 1.3 | Add `flow.assess.agent.md` template | P0 | `templates/.github/agents/` |
| 1.4 | Fix agent names: kebab-case → PascalCase | P0 | All agent template frontmatter |
| 1.5 | Add `.github/agents/` to flowspec itself | P0 | Create `.github/agents/` directory |
| 1.6 | Remove `/spec:*` from templates | P0 | `templates/commands/spec/` (delete or move to archive) |
| 1.7 | Update `/flow:init` references to `/spec:*` | P0 | `.claude/commands/flow/init.md`, `/flow/reset.md` |
| 1.8 | **Remove ALL `/flow:operate` references** | P0 | Search and destroy in all files |

### Phase 2: Template MCP Configuration (RELEASE QUALITY)

| # | Task | Priority | Files Affected |
|---|------|----------|----------------|
| 2.1 | Create standard `.mcp.json` template | P1 | `templates/.mcp.json` |
| 2.2 | Update `flowspec init` to copy MCP config | P1 | `src/flowspec_cli/__init__.py` |
| 2.3 | Add MCP health check to init | P2 | `src/flowspec_cli/__init__.py` |

### Phase 3: auth.poley.dev Fixes (TARGET REPO)

| # | Task | Priority | Files Affected |
|---|------|----------|----------------|
| 3.1 | Update `.mcp.json` with full config | P1 | `.mcp.json` |
| 3.2 | Update `flowspec_workflow.yml` to v2.0 | P1 | `flowspec_workflow.yml` |
| 3.3 | Remove broken `{{INCLUDE:}}` directives | P1 | `.github/prompts/*.prompt.md` |
| 3.4 | Remove `.specify/` directory | P2 | Delete `.specify/` |
| 3.5 | Update CLAUDE.md (remove `/flow:operate`) | P2 | `CLAUDE.md` |
| 3.6 | Sync missing skills | P3 | `.claude/skills/` |

### Phase 4: Documentation Updates

| # | Task | Priority | Files Affected |
|---|------|----------|----------------|
| 4.1 | Update user docs for command namespaces | P2 | `user-docs/guides/` |
| 4.2 | Update test references to `/spec:*` | P2 | `tests/test_*.py` |
| 4.3 | Archive build-docs with `/spec:*` refs | P3 | `build-docs/` |

---

## IMPLEMENTATION ORDER

```
IMMEDIATE: Phase 0 (ROOT CAUSE - BROKEN UPGRADE-REPO)
  0.7 → Remove /flow:operate EVERYWHERE first
  0.1 → Fix upgrade-repo command logic
  0.2 → 0.6 → Ensure upgrade-repo handles all artifacts

Week 1: Phase 1 (P0 items)
  1.8 → Verify /flow:operate completely gone
  1.1 → 1.2 → 1.3 → 1.4 → 1.5 (agent fixes)
  1.6 → 1.7 (spec removal)

Week 2: Phase 2 + Phase 3 (P1 items)
  2.1 → 2.2 (MCP templates)
  3.1 → 3.2 → 3.3 (auth.poley.dev - RE-RUN upgrade-repo after fixes)

Week 3: Phase 3 + Phase 4 (P2/P3 items)
  3.4 → 3.5 → 3.6 (auth.poley.dev cleanup - should be handled by fixed upgrade-repo)
  4.1 → 4.2 → 4.3 (documentation)
```

**KEY INSIGHT:** Once upgrade-repo is fixed, re-running it on auth.poley.dev should automatically fix most Phase 3 items.

---

## VERIFICATION CHECKLIST

After implementation, verify:

**Phase 0 Verification (CRITICAL):**
- [ ] `grep -r "operate" .` returns ZERO matches for `/flow:operate` in flowspec
- [ ] `grep -r "operate" .` returns ZERO matches for `/flow:operate` in templates
- [ ] `flowspec upgrade-repo` on a test repo produces correct output

**Phase 1 Verification:**
- [ ] `flowspec init` creates agents with dot-naming (`flow.assess.agent.md`)
- [ ] Agent names appear in VSCode as PascalCase (`FlowAssess`)
- [ ] VSCode shows exactly 6 flow agents: Assess, Specify, Plan, Implement, Validate, SubmitPR
- [ ] No `/spec:*` commands visible in target repos

**Phase 2/3 Verification:**
- [ ] MCP servers start correctly: `./scripts/check-mcp-servers.sh`
- [ ] auth.poley.dev passes `flowspec gate` validation
- [ ] Re-running `flowspec upgrade-repo` on auth.poley.dev fixes all issues

---

## RISK ASSESSMENT

| Risk | Impact | Mitigation |
|------|--------|------------|
| **BROKEN upgrade-repo causing bad deployments** | **CRITICAL** | **FIX IMMEDIATELY - Phase 0** |
| `/flow:operate` references remaining | High | Grep-verify ZERO matches before release |
| Breaking existing `/spec:*` users | High | Document migration path in release notes |
| Agent naming change breaks CI | Medium | Update CI to use new naming |
| MCP config breaks on systems without deps | Medium | Add graceful degradation |
| 360KB __init__.py is hard to maintain | Low | Consider refactoring embedded templates |

---

## APPENDIX: Files Changed Summary

**flowspec repository:**
- `src/flowspec_cli/__init__.py` - Agent templates and init logic
- `templates/.github/agents/` - Agent template files (rename + add assess)
- `templates/commands/spec/` - Remove or archive
- `.claude/commands/flow/init.md` - Remove `/spec:*` references
- `.claude/commands/flow/reset.md` - Remove `/spec:*` references
- `.github/agents/` - NEW: Add deployed agents
- `templates/.mcp.json` - NEW: Standard MCP config

**auth.poley.dev repository:**
- `.mcp.json` - Expand from 1 to 6+ servers
- `flowspec_workflow.yml` - Upgrade v1.0 → v2.0
- `.github/prompts/*.prompt.md` - Remove `{{INCLUDE:}}` directives
- `.specify/` - DELETE
- `CLAUDE.md` - Remove `/flow:operate` reference
- `.claude/skills/` - Add missing skills

---

*Document complete. Pass 5/5 finished.*
