# Flowspec Framework Repair Report

**Date:** December 11, 2025
**Analyst:** Claude Code (Opus 4.5)
**Scope:** Comprehensive audit of both installed projects AND Flowspec source repository

---

## Executive Summary

This report combines two complementary audits:

1. **Installed Review** - Issues found in a project (fastapi-template) with Flowspec installed via `specify init`
2. **Dev-Setup Review** - Issues found in the Flowspec SOURCE repository used for framework development

| Aspect | Installed Project | Source Repository |
|--------|-------------------|-------------------|
| **Commands** | ✅ N/A (copies) | ✅ 27 symlinks valid |
| **Skills** | ❌ Not deployed | ⚠️ 2 missing from templates |
| **Agents** | ⚠️ 9 vs 23 mismatch | ⚠️ 17 without prompts |
| **Hooks** | ❌ All disabled | ✅ 11 production hooks |
| **CI/CD** | ❌ Minimal (21 lines) | ✅ 15 workflows |
| **Constitution** | ❌ Placeholders | ⚠️ 1 placeholder |
| **Overall** | ~60% deployed | ~85% functional |

---

# Part 1: Installed Project Review

> **Target:** fastapi-template (project with Flowspec installed via `specify init`)
> **Status:** ~60% complete - critical deployment gaps

## Critical Issues (8)

### C1. Skills Not Deployed to .claude/skills/

**Problem:** Skills exist only in `.specify/templates/skills/` as templates but were never deployed to `.claude/skills/` where Claude Code can auto-invoke them.

**7 skills need deployment:**
- architect/SKILL.md
- constitution-checker/SKILL.md
- pm-planner/SKILL.md
- qa-validator/SKILL.md
- sdd-methodology/SKILL.md
- security-reporter/SKILL.md
- security-reviewer/SKILL.md

**Fix:**
```bash
mkdir -p .claude/skills
cp -r .specify/templates/skills/* .claude/skills/
```

---

### C2. No CLAUDE.md at Repository Root

**Problem:** No root-level `CLAUDE.md` exists for project-specific Claude Code instructions.

**Fix:** Create `./CLAUDE.md` with project overview, tech stack (Python 3.13, FastAPI, SQLModel, PostgreSQL, Celery, Redis), development commands, and conventions.

---

### C3. Constitution Contains Unresolved Placeholders

**Problem:** `memory/constitution.md` has multiple `[PLACEHOLDER]` markers:
- `[PROJECT_NAME]` - Line 1
- `[LANGUAGES_AND_FRAMEWORKS]` - Line 75
- `[LINTING_TOOLS]` - Line 79
- `[DATE]` - Lines 95, 96

**Fix:** Replace placeholders with actual project values.

---

### C4. All Hooks Are Disabled

**Problem:** All 4 hooks in `.specify/hooks/hooks.yaml` have `enabled: false`:
- run-tests (post-implementation)
- update-changelog (on spec creation)
- lint-code (on task completion)
- quality-gate (before validation)

**Fix:** Enable at minimum: run-tests, lint-code, quality-gate

---

### C5. VSCode Extensions.json Is Empty

**Problem:** `.vscode/extensions.json` has empty `recommendations` array.

**Fix:** Add recommendations for:
- ms-python.python, ms-python.vscode-pylance
- charliermarsh.ruff, ms-azuretools.vscode-docker
- GitHub.copilot, anthropics.claude-code

---

### C6. GitHub Prompts Are Stub Files

**Problem:** 9 speckit prompts in `.github/prompts/speckit.*.prompt.md` are 3-4 line stubs while full content (100+ lines) exists in `.claude/commands/`.

**Fix:** Create symlinks from prompts to commands for single-source-of-truth.

---

### C7. Missing Agents for Non-Speckit Commands

**Problem:** 9 agents exist for speckit commands, but 14 other commands (dev/*, ops/*, qa/*, sec/*, arch/*) have prompts without agents.

**Fix:** Create agent files for all 14 missing commands.

---

### C8. CI/CD Pipeline Missing Critical Steps

**Problem:** CI pipeline is minimal (21 lines) - only checkout, build, pytest.

**Missing:**
- Linting (ruff check)
- Type checking (mypy)
- Security scanning (trivy)
- Coverage reporting (codecov)

**Fix:** Expand CI with lint, test, security jobs.

---

## Major Issues (6)

| ID | Issue | Impact |
|----|-------|--------|
| M1 | VSCode settings incomplete | Missing Python/FastAPI config |
| M2 | No MCP configuration | `.mcp.json` missing |
| M3 | Workflow validation = NONE | No quality gates |
| M4 | Command naming inconsistent | Dots vs colons |
| M5 | Duplicate content | Commands and prompts diverge |
| M6 | repo-facts.md incomplete | Missing frameworks/databases |

## Minor Issues (5)

| ID | Issue | Fix |
|----|-------|-----|
| m1 | Missing pyproject.toml scripts | Add dev, test, lint commands |
| m2 | No pre-commit configuration | Add `.pre-commit-config.yaml` |
| m3 | Missing .env.example variables | Document all env vars |
| m4 | Test directory flat | Organize into unit/integration/e2e |
| m5 | Missing CODEOWNERS | Add `.github/CODEOWNERS` |

## Enhancement Opportunities (4)

- E1: Add Claude Code hooks for workflow integration
- E2: Add Docker health checks
- E3: Add API documentation generation
- E4: Add Makefile for common commands

---

# Part 2: Dev-Setup Review (Source Repository)

> **Target:** Flowspec source repository (github.com/jpoley/flowspec)
> **Status:** ~85% functional - dev-setup validation passes

## Framework Inventory

### Commands: 41 total in templates/

| Namespace | Count | Files |
|-----------|-------|-------|
| flow | 19 | assess, implement, init, operate, plan, research, reset, specify, validate + 5 security + 3 partials |
| speckit | 10 | analyze, checklist, clarify, configure, constitution, implement, init, plan, specify, tasks |
| arch | 2 | decide, model |
| dev | 3 | cleanup, debug, refactor |
| ops | 3 | monitor, respond, scale |
| qa | 2 | review, test |
| sec | 4 | fix, report, scan, triage |

### Skills: 8 in .claude/skills/, 7 in templates/skills/

**Deployed (.claude/skills/):**
- architect, pm-planner, qa-validator, sdd-methodology
- security-fixer, security-reporter, security-reviewer, security-workflow

**Templates (templates/skills/):**
- architect, constitution-checker, pm-planner, qa-validator
- sdd-methodology, security-reporter, security-reviewer

### Agents: 52 total

| Location | Count |
|----------|-------|
| .claude/agents/ | 5 (backend-engineer, frontend-engineer, project-manager-backlog, qa-engineer, security-reviewer) |
| .github/agents/ | 47 (flow, speckit, arch, dev, ops, qa, sec, pm) |

### Prompts: 57 in .github/prompts/

- jpspec.* (16 active)
- specflow.* (31 legacy, 13 DEPRECATED)
- speckit.* (10)

### Hooks: 11 production + 6 test

**Production hooks in .claude/hooks/:**
- permission-auto-approve.py
- post-slash-command-emit.py
- post-tool-use-format-python.sh
- post-tool-use-lint-python.sh
- post-tool-use-task-memory-lifecycle.py
- pre-implement.py, pre-implement.sh
- pre-tool-use-git-safety.py
- pre-tool-use-sensitive-files.py
- session-start.sh
- stop-quality-gate.py

### CI/CD: 15 workflows

ci.yml, dev-setup-validation.yml, docker-publish.yml, docs.yml, labeler.yml, release.yml, role-validation.yml, scorecard.yml, security-parallel.yml, security-scan.yml, security.yml, stale.yml, task-memory-validation.yml, version-check.yml, backlog-flush.yml

---

## Dev-Setup Validation Results

```
✅ Dev-setup validation passed

- Total .md files in .claude/commands/: 27
- All files are symlinks: 27/27
- All symlinks resolve correctly
```

---

## Issues Found in Source Repository

### Critical: None

The dev-setup is functional and validates successfully.

### Major Issues (3)

#### M1. Skills Not in Templates Won't Be Distributed

**Problem:** 2 skills exist in `.claude/skills/` but NOT in `templates/skills/`:
- security-fixer
- security-workflow

**Impact:** Users running `specify init` won't get these skills.

**Fix:** Copy to templates:
```bash
cp -r .claude/skills/security-fixer templates/skills/
cp -r .claude/skills/security-workflow templates/skills/
```

---

#### M2. Agent-Prompt Alignment Gap

**Problem:** 17 agents in `.github/agents/` have no corresponding prompts:

```
Missing prompts for agents:
- arch-decide, arch-design, arch-model
- dev-build, dev-cleanup, dev-debug, dev-refactor
- flow-init, flow-reset
- ops-deploy, ops-monitor, ops-respond, ops-scale
- pm-assess, pm-define, pm-discover
- qa-review, qa-test, qa-verify
- sec-audit, sec-fix, sec-report, sec-scan, sec-triage
```

**Fix:** Create corresponding prompts in `.github/prompts/` or document that these agents are Copilot-only.

---

#### M3. Deprecated Prompts Still Present

**Problem:** 13 deprecated prompts exist in `.github/prompts/`:
```
specflow._DEPRECATED_*.prompt.md (13 files)
```

**Fix:** Remove deprecated files or move to archive:
```bash
mkdir -p .github/prompts/archive
mv .github/prompts/*DEPRECATED* .github/prompts/archive/
```

---

### Minor Issues (4)

#### m1. Skills Structure Inconsistency

**Problem:** Some skills in `.claude/skills/` are standalone `.md` files rather than directories:
- exploit-researcher.md
- fuzzing-strategist.md
- patch-engineer.md
- security-analyst.md
- security-codeql.md
- security-custom-rules.md
- security-dast.md
- security-triage.md

**Expected:** Each skill should be `skill-name/SKILL.md`

**Fix:** Restructure or document that both formats are valid.

---

#### m2. Constitution Placeholder

**Problem:** 1 `[PROJECT` placeholder found in `memory/constitution.md`

**Fix:** Verify if intentional (for templates) or needs resolution.

---

#### m3. Stale Prompt Naming

**Problem:** GitHub prompts use mixed naming:
- jpspec.* (current)
- specflow.* (legacy)
- speckit.* (current)

**Fix:** Standardize on consistent naming or document mapping.

---

#### m4. Extra Skills Not Documented

**Problem:** 8 standalone skill files in `.claude/skills/` are undocumented:
- exploit-researcher.md, fuzzing-strategist.md, patch-engineer.md
- security-analyst.md, security-codeql.md, security-custom-rules.md
- security-dast.md, security-triage.md

**Fix:** Add to CLAUDE.md or create proper SKILL.md structure.

---

## Implementation Priority

### Phase 1: Critical (Immediate)

**For Installed Projects:**
1. Deploy skills to `.claude/skills/`
2. Create root `CLAUDE.md`
3. Populate constitution placeholders
4. Enable critical hooks

**For Source Repository:**
1. Copy security-fixer and security-workflow to templates/skills/
2. Remove deprecated prompts

### Phase 2: Major (This Week)

**For Installed Projects:**
5. Populate VSCode extensions
6. Fix GitHub prompt stubs
7. Create missing agents
8. Expand CI/CD pipeline

**For Source Repository:**
3. Create missing prompts for agents OR document Copilot-only
4. Standardize skill structure

### Phase 3: Minor (Next Week)

- Command naming standardization
- Complete agent-prompt alignment
- Add missing documentation

---

## Validation Commands

### For Installed Projects
```bash
# Verify skills deployed
ls .claude/skills/*/SKILL.md

# Verify CLAUDE.md exists
cat CLAUDE.md | head -20

# Check for placeholders
grep -r '\[PROJECT' memory/

# Check hooks enabled
grep "enabled: true" .specify/hooks/hooks.yaml
```

### For Source Repository
```bash
# Validate dev-setup
make dev-validate

# Check skill coverage
diff <(ls templates/skills/) <(ls .claude/skills/)

# Check for deprecated content
find .github/prompts -name "*DEPRECATED*"

# Agent-prompt alignment
diff <(ls .github/agents/*.md | xargs -n1 basename | sed 's/.agent.md//' | sort) \
     <(ls .github/prompts/*.md | xargs -n1 basename | sed 's/.prompt.md//' | sort)
```

---

## Conclusion

### Installed Projects (via `specify init`)
- **Status:** ~60% deployed
- **Primary gaps:** Skills not deployed, hooks disabled, CI minimal
- **Root cause:** `specify init` doesn't complete full deployment
- **Recommendation:** Create `specify init --complete` that enables all features

### Source Repository (Flowspec)
- **Status:** ~85% functional
- **Primary gaps:** 2 skills not in templates, agent-prompt mismatch
- **Root cause:** Organic growth without sync validation
- **Recommendation:** Add CI check for template-deployment parity

### Cross-Cutting Recommendations

1. **Single Source of Truth:** Use symlinks for prompts→commands, agents→templates
2. **Automated Validation:** Add CI checks for all component alignments
3. **Documentation:** Document expected file counts and structures
4. **init Enhancements:** Have `specify init` report deployment completeness

---

**Document Version:** 1.0.0
**Generated:** 2025-12-11
**Next Review:** After implementing Phase 1 fixes
