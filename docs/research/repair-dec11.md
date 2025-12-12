# Repository Configuration Repair Report

**Date:** December 11, 2025
**Repository:** fastapi-template
**Scope:** .claude, .github, .vscode, .specify configurations
**Analyst:** Claude Code

---

## Executive Summary

This repository has an extensive configuration framework (Flowspec/Speckit) with 23+ slash commands, 9 agents, 7 skills, and comprehensive memory/documentation. However, **critical configuration gaps prevent the framework from functioning as designed**. The configuration is approximately 60% complete but missing essential deployment steps.

### Severity Distribution

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical** | 8 | Broken functionality, missing essential files |
| **Major** | 6 | Significant gaps reducing effectiveness |
| **Minor** | 5 | Optimization opportunities |
| **Enhancement** | 4 | Nice-to-have improvements |

---

## Critical Issues (Must Fix)

### C1. Skills Not Deployed to .claude/skills/

**Location:** `.claude/skills/` (missing)
**Impact:** Skills cannot be auto-invoked by Claude Code

**Problem:** The documentation at `.specify/memory/claude-skills.md` states skills should be in `.claude/skills/<skill-name>/SKILL.md`, but no `.claude/skills/` directory exists. Skills only exist in `.specify/templates/skills/` as templates.

**Current State:**
```
.specify/templates/skills/
├── architect/SKILL.md
├── constitution-checker/SKILL.md
├── pm-planner/SKILL.md
├── qa-validator/SKILL.md
├── sdd-methodology/SKILL.md
├── security-reporter/SKILL.md
└── security-reviewer/SKILL.md
```

**Fix:**
```bash
# Deploy skills from templates to .claude/skills/
mkdir -p .claude/skills
cp -r .specify/templates/skills/* .claude/skills/
```

**Verification:**
```bash
ls -la .claude/skills/*/SKILL.md
```

---

### C2. No CLAUDE.md at Repository Root

**Location:** `./CLAUDE.md` (missing)
**Impact:** No project-specific instructions for Claude Code

**Problem:** The only `CLAUDE.md` is at `.specify/scripts/CLAUDE.md` which documents scripts, not the project. Claude Code needs a root-level `CLAUDE.md` for project context.

**Fix:** Create `./CLAUDE.md` with:
```markdown
# CLAUDE.md

## Project Overview

FastAPI template with PostgreSQL, SQLModel, Celery/Redis, and JWT authentication.

## Tech Stack

- **Runtime:** Python 3.13
- **Framework:** FastAPI + Uvicorn
- **ORM:** SQLModel (SQLAlchemy wrapper)
- **Database:** PostgreSQL
- **Background Jobs:** Celery + Redis
- **Auth:** JWT tokens
- **Admin:** SQLAdmin

## Development Commands

```bash
# Start development environment
docker compose up -d

# Run tests
docker compose run web pytest

# Database migrations
docker compose run web alembic upgrade head

# Create new migration
docker compose run web alembic revision --autogenerate -m "description"
```

## Project Structure

```
app/
├── main.py          # FastAPI application entry
├── config.py        # Configuration management
├── db.py            # Database connection
├── celery.py        # Celery worker config
├── admin/           # SQLAdmin interface
├── api/             # API routes
├── dependencies/    # Dependency injection
├── interactors/     # Business logic
├── models/          # SQLModel definitions
├── utils/           # Utilities
└── workers/         # Celery tasks
```

## Conventions

- Use SQLModel for all database models
- Business logic in interactors/, not in routes
- All API endpoints in app/api/
- Environment variables via .env (see .env.example)

## Testing

- pytest for all tests
- Tests in tests/ directory
- Run with `docker compose run web pytest`
```

---

### C3. Constitution Contains Unresolved Placeholders

**Location:** `memory/constitution.md`
**Impact:** Project governance undefined

**Problem:** The constitution has multiple `[PLACEHOLDER]` markers that were never populated:
- `[PROJECT_NAME]` - Line 1
- `[LANGUAGES_AND_FRAMEWORKS]` - Line 75
- `[LINTING_TOOLS]` - Line 79
- `[DATE]` - Lines 95, 96

**Fix:** Update `memory/constitution.md`:
```markdown
# fastapi-template Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->

## Core Principles
...

## Technology Stack
Python 3.13, FastAPI, SQLModel, PostgreSQL, Celery, Redis

### Linting & Formatting
- Ruff (linting and formatting)
- mypy (type checking)

## Governance
**Version**: 1.0.0
**Ratified**: 2025-12-11
**Last Amended**: 2025-12-11
```

---

### C4. All Hooks Are Disabled

**Location:** `.specify/hooks/hooks.yaml`
**Impact:** No automated quality gates

**Problem:** All 4 defined hooks have `enabled: false`:
- `run-tests` (post-implementation)
- `update-changelog` (on spec creation)
- `lint-code` (on task completion)
- `quality-gate` (before validation)

**Fix:** Enable at least the critical hooks:
```yaml
hooks:
  - name: run-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    description: Run test suite after implementation
    enabled: true  # CHANGED

  - name: lint-code
    events:
      - type: task.completed
    script: lint-code.sh
    description: Run code linter and formatter
    enabled: true  # CHANGED
    timeout: 60

  - name: quality-gate
    events:
      - type: validate.started
    script: quality-gate.sh
    description: Check code quality metrics before validation
    enabled: true  # CHANGED
    fail_mode: stop
```

---

### C5. VSCode Extensions.json Is Empty

**Location:** `.vscode/extensions.json`
**Impact:** Contributors don't get recommended tooling

**Problem:** The `recommendations` array is empty, missing essential Python/FastAPI extensions.

**Fix:** Populate `.vscode/extensions.json`:
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy",
        "charliermarsh.ruff",
        "ms-azuretools.vscode-docker",
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg",
        "redhat.vscode-yaml",
        "tamasfe.even-better-toml",
        "GitHub.copilot",
        "anthropics.claude-code"
    ],
    "unwantedRecommendations": []
}
```

---

### C6. GitHub Prompts Are Stub Files for Speckit Commands

**Location:** `.github/prompts/speckit.*.prompt.md`
**Impact:** GitHub Copilot agents have no instructions

**Problem:** The 9 speckit prompts are near-empty stubs (3-4 lines) that just reference an agent:

```markdown
---
agent: speckit.implement
---
```

Meanwhile, the actual content is in `.claude/commands/speckit.*.md` with 100+ lines of detailed instructions.

**Fix Option A (Symlink):**
```bash
# Replace prompts with symlinks to commands
cd .github/prompts
for file in speckit.*.prompt.md; do
    cmd=$(echo "$file" | sed 's/.prompt.md/.md/')
    rm "$file"
    ln -s "../../.claude/commands/$cmd" "$file"
done
```

**Fix Option B (Duplicate content):**
Copy the full content from `.claude/commands/speckit.*.md` to `.github/prompts/speckit.*.prompt.md`.

**Recommendation:** Use Option A (symlinks) for single-source-of-truth maintenance.

---

### C7. Missing Agents for Non-Speckit Commands

**Location:** `.github/agents/`
**Impact:** 14 commands have no agent automation

**Problem:**
- **Agents exist (9):** speckit.analyze, speckit.checklist, speckit.clarify, speckit.constitution, speckit.implement, speckit.plan, speckit.specify, speckit.tasks, speckit.taskstoissues
- **Prompts exist but NO agents (14):** arch.decide, arch.model, dev.cleanup, dev.debug, dev.refactor, ops.monitor, ops.respond, ops.scale, qa.review, qa.test, sec.fix, sec.report, sec.scan, sec.triage

**Fix:** Create missing agent files. Example for `sec.report.agent.md`:
```markdown
---
description: Generate comprehensive security audit report from scan and triage results using security-reporter skill.
---

## User Input

```text
$ARGUMENTS
```

[Copy content from .github/prompts/sec.report.prompt.md]
```

Create agents for all 14 missing commands:
```bash
# Template for creating agent files
for cmd in arch.decide arch.model dev.cleanup dev.debug dev.refactor \
           ops.monitor ops.respond ops.scale qa.review qa.test \
           sec.fix sec.report sec.scan sec.triage; do
    cp ".github/prompts/${cmd}.prompt.md" ".github/agents/${cmd}.agent.md"
done
```

---

### C8. CI/CD Pipeline Missing Critical Steps

**Location:** `.github/workflows/ci-cd.yml`
**Impact:** No linting, type checking, security scanning, or coverage reporting

**Current State (21 lines):**
```yaml
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
      - run: docker compose run web pytest
```

**Fix:** Expand CI pipeline:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --frozen
      - name: Run Ruff linter
        run: uv run ruff check .
      - name: Run Ruff formatter check
        run: uv run ruff format --check .
      - name: Run mypy type checker
        run: uv run mypy app/

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Build docker image
        run: docker compose build
      - name: Run tests with coverage
        run: docker compose run web pytest --cov=app --cov-report=xml --cov-report=term
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## Major Issues (Should Fix)

### M1. VSCode Settings Incomplete

**Location:** `.vscode/settings.json`
**Impact:** Missing Python-specific configuration

**Current State:** Only chat settings configured (14 lines)

**Fix:** Add Python/FastAPI settings:
```json
{
    "chat.promptFiles": true,
    "chat.promptFilesRecommendations": {
        "speckit.constitution": true,
        "speckit.specify": true,
        "speckit.plan": true,
        "speckit.tasks": true,
        "speckit.implement": true
    },
    "chat.tools.terminal.autoApprove": {
        ".specify/scripts/bash/": true,
        ".specify/scripts/powershell/": true
    },
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.analysis.typeCheckingMode": "basic",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        },
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "ruff.lint.run": "onSave",
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.mypy_cache": true,
        "**/*.egg-info": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"]
}
```

---

### M2. No MCP Configuration at Project Level

**Location:** `.mcp.json` (missing)
**Impact:** MCP servers not configured for project-specific needs

**Problem:** MCP configuration documented in `.specify/memory/mcp-configuration.md` but no actual `.mcp.json` exists.

**Fix:** Create `.mcp.json`:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

---

### M3. Workflow Validation Set to NONE for All Transitions

**Location:** `flowspec_workflow.yml`
**Impact:** No quality gates between workflow phases

**Problem:** All 7 transitions use `validation: NONE`:
```yaml
transitions:
  - name: assess
    validation: NONE  # No gate
  - name: research
    validation: NONE  # No gate
  # ... all set to NONE
```

**Fix:** Add validation gates for critical transitions:
```yaml
transitions:
  - name: specify
    from: "Researched"
    to: "Specified"
    validation: KEYWORD["spec-approved"]

  - name: implement
    from: "Planned"
    to: "Implemented"
    validation: KEYWORD["ready-to-implement"]

  - name: validate
    from: "Implemented"
    to: "Validated"
    validation: PULL_REQUEST
```

---

### M4. Command Naming Inconsistency

**Location:** `.claude/commands/`
**Impact:** Confusing command syntax for users

**Problem:** Mixed naming conventions:
- Speckit commands: `speckit.specify`, `speckit.plan` (dot separator)
- Other commands: `sec:report`, `dev:debug`, `qa:test` (colon separator, subdirectory structure)

**Additionally:** The `sec/report.md` file references `/flow:security report` which is not a valid command path.

**Fix Option A (Standardize on colons):**
```bash
# Rename speckit.* to speckit:*
cd .claude/commands
for f in speckit.*.md; do
    mv "$f" "speckit/${f#speckit.}"
done
```

**Fix Option B (Standardize on dots - less work):**
```bash
# Rename sec/* to sec.* etc
cd .claude/commands
for dir in sec qa dev ops arch; do
    for f in "$dir"/*.md; do
        base=$(basename "$f" .md)
        mv "$f" "${dir}.${base}.md"
    done
    rmdir "$dir"
done
```

**Recommendation:** Use subdirectory structure (current for sec/qa/dev/ops/arch) as it scales better. Convert speckit to subdirectory.

---

### M5. Duplicate Content Between Commands and Prompts

**Location:** `.claude/commands/sec/report.md` and `.github/prompts/sec.report.prompt.md`
**Impact:** Maintenance burden, risk of divergence

**Problem:** Both files contain nearly identical 472-line content. Changes must be made in two places.

**Fix:** Use symlinks for single-source-of-truth:
```bash
# Make prompts reference commands
cd .github/prompts
rm sec.report.prompt.md
ln -s ../../.claude/commands/sec/report.md sec.report.prompt.md
```

---

### M6. repo-facts.md Missing Detected Technologies

**Location:** `memory/repo-facts.md`
**Impact:** Incomplete project context

**Current detected:**
- Languages: [Python]
- CI/CD: [GitHub Actions]

**Missing:**
- Frameworks: [FastAPI, SQLModel, Celery]
- Databases: [PostgreSQL, Redis]
- Tools: [Docker, Alembic, pytest]

**Fix:** Update `memory/repo-facts.md`:
```yaml
---
generated: 2025-12-11T15:52:42.437791
languages: [Python]
frameworks: [FastAPI, SQLModel, Celery]
databases: [PostgreSQL, Redis]
cicd: [GitHub Actions]
containerization: [Docker, Docker Compose]
testing: [pytest]
orm_migrations: [Alembic]
git_repo: true
---
```

---

## Minor Issues (Nice to Fix)

### m1. Missing pyproject.toml Scripts Section

**Location:** `pyproject.toml`
**Impact:** No standardized CLI commands

**Fix:** Add scripts section:
```toml
[project.scripts]
dev = "uvicorn app.main:app --reload"
test = "pytest"
lint = "ruff check ."
format = "ruff format ."
typecheck = "mypy app/"
```

---

### m2. No Pre-commit Configuration

**Location:** `.pre-commit-config.yaml` (missing)
**Impact:** Quality checks not automated locally

**Fix:** Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: docker compose run web pytest -x
        language: system
        pass_filenames: false
        always_run: true
```

---

### m3. Missing .env.example Variables

**Location:** `.env.example`
**Impact:** Incomplete environment setup documentation

**Check current `.env.example` and ensure it includes:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

### m4. Test Directory Structure Missing Subdirectories

**Location:** `tests/`
**Impact:** Unclear test organization

**Recommended structure:**
```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_models.py
│   └── test_utils.py
├── integration/          # Integration tests
│   ├── test_api.py
│   └── test_db.py
└── e2e/                  # End-to-end tests
    └── test_flows.py
```

---

### m5. Missing CODEOWNERS File

**Location:** `.github/CODEOWNERS` (missing)
**Impact:** No automatic review assignment

**Fix:** Create `.github/CODEOWNERS`:
```
# Default owner
* @jasonpoley

# Security files
.github/workflows/ @jasonpoley
app/dependencies/auth.py @jasonpoley
```

---

## Enhancement Opportunities

### E1. Add Claude Code Hooks for Workflow Integration

**Location:** `.claude/hooks/` (to create)
**Impact:** Automated workflow enforcement

**Create Claude Code hooks:**

`.claude/hooks/pre-tool-use.sh`:
```bash
#!/bin/bash
# Validate before tool execution
if [[ "$TOOL_NAME" == "Write" && "$FILE_PATH" == *"app/models"* ]]; then
    echo "Remember: Update Alembic migrations after model changes"
fi
```

---

### E2. Add Docker Health Checks

**Location:** `compose.yml`
**Impact:** Better container orchestration

```yaml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

### E3. Add API Documentation Generation

**Location:** `docs/api/` (to create)
**Impact:** Automated API documentation

FastAPI auto-generates OpenAPI docs. Export them:
```bash
# Add to CI
curl http://localhost:8000/openapi.json > docs/api/openapi.json
```

---

### E4. Add Makefile for Common Commands

**Location:** `Makefile` (to create)
**Impact:** Simplified developer experience

```makefile
.PHONY: dev test lint format migrate

dev:
	docker compose up -d

test:
	docker compose run web pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

migrate:
	docker compose run web alembic upgrade head

shell:
	docker compose run web python

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## Agent Consistency Analysis

### Current State

| Tool | Agent Count | Prompt Count | Command Count | Consistency |
|------|-------------|--------------|---------------|-------------|
| Claude Code | N/A | N/A | 23 | N/A |
| GitHub Copilot | 9 | 23 | N/A | **INCONSISTENT** |
| VSCode Chat | N/A | 5 recommended | N/A | Partial |

### Issues

1. **Agent-Prompt Mismatch:** 9 agents exist for speckit commands, but 14 other commands (dev/*, ops/*, qa/*, sec/*, arch/*) have prompts without corresponding agents.

2. **Content Duplication:** Some content exists in both `.claude/commands/` and `.github/prompts/` with no synchronization mechanism.

3. **Missing Skills Deployment:** 7 skills defined in templates but not deployed to `.claude/skills/`.

### Recommendation

Establish single-source-of-truth architecture:

```
.specify/templates/           # Source templates
├── commands/                 # Command definitions
├── agents/                   # Agent definitions
├── prompts/                  # Prompt definitions
└── skills/                   # Skill definitions

.claude/                      # Claude Code (symlinks)
├── commands/ → ../specify/templates/commands/
└── skills/ → ../specify/templates/skills/

.github/                      # GitHub Copilot (symlinks)
├── agents/ → ../specify/templates/agents/
└── prompts/ → ../specify/templates/prompts/
```

---

## Implementation Priority

### Phase 1: Critical (Week 1)
1. [ ] Deploy skills to `.claude/skills/` (C1)
2. [ ] Create root `CLAUDE.md` (C2)
3. [ ] Populate constitution placeholders (C3)
4. [ ] Enable critical hooks (C4)
5. [ ] Populate VSCode extensions (C5)

### Phase 2: Major (Week 2)
6. [ ] Fix GitHub prompt stubs (C6)
7. [ ] Create missing agents (C7)
8. [ ] Expand CI/CD pipeline (C8)
9. [ ] Complete VSCode settings (M1)
10. [ ] Create MCP configuration (M2)

### Phase 3: Minor (Week 3)
11. [ ] Add pre-commit config (m2)
12. [ ] Standardize command naming (M4)
13. [ ] Add workflow validation gates (M3)
14. [ ] Establish symlink architecture (M5)

### Phase 4: Enhancements (Ongoing)
15. [ ] Add Makefile (E4)
16. [ ] Add Docker health checks (E2)
17. [ ] Add CODEOWNERS (m5)
18. [ ] Add API docs generation (E3)

---

## Validation Checklist

After implementing fixes, verify:

```bash
# Skills deployed
ls .claude/skills/*/SKILL.md

# CLAUDE.md exists
cat CLAUDE.md

# Constitution populated
grep -c "PROJECT_NAME" memory/constitution.md  # Should be 0

# Hooks enabled
grep "enabled: true" .specify/hooks/hooks.yaml

# Extensions recommended
jq '.recommendations | length' .vscode/extensions.json  # Should be > 0

# CI has lint job
grep -c "ruff" .github/workflows/ci-cd.yml  # Should be > 0

# All agents have matching prompts
diff <(ls .github/agents/*.md | xargs -n1 basename | sed 's/.agent.md//') \
     <(ls .github/prompts/*.md | xargs -n1 basename | sed 's/.prompt.md//')
```

---

## Conclusion

This repository has a sophisticated configuration framework that is ~60% deployed. The primary issues are:

1. **Skills not deployed** - Templates exist but aren't in `.claude/skills/`
2. **Agent-prompt mismatch** - 9 agents vs 23 prompts
3. **CI/CD minimal** - Missing lint, security, coverage
4. **Constitution incomplete** - Placeholders not filled
5. **Hooks disabled** - All quality gates turned off

Implementing the Phase 1 fixes (estimated 2-4 hours) will enable core functionality. Full implementation of all recommendations would create a production-ready development environment with comprehensive automation.
