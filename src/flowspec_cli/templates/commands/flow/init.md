---
description: Initialize or setup constitution for a project, handling both greenfield (new) and brownfield (existing) projects
loop: setup
# Loop Classification: SETUP
# This is a one-time setup command that runs before any workflow loop. It initializes
# project constitution and configuration but is not part of regular development cycles.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command sets up the project constitution, automatically detecting whether the project is greenfield (new) or brownfield (existing codebase). It analyzes the repository and creates a customized constitution based on the detected tech stack.

### Overview

The `/flow:init` command:
1. Detects project type (greenfield vs brownfield)
2. Analyzes repository for tech stack detection
3. Selects appropriate constitution tier
4. Generates `memory/constitution.md` with customizations
5. Creates `memory/repo-facts.md` with detected technologies
6. Configures workflow if not already done

### Argument Parsing

Parse `$ARGUMENTS` for optional flags:

| Flag | Description |
|------|-------------|
| `--tier {light\|medium\|heavy}` | Force specific constitution tier |
| `--force` | Overwrite existing constitution without prompting |
| `--skip-analysis` | Skip tech stack analysis, use template defaults |
| `--configure-workflow` | Also run workflow configuration (like /flow:reset) |

### Step 1: Project Type Detection

Detect whether this is a greenfield or brownfield project:

**Brownfield Indicators** (existing project):
- `.git` directory exists with commit history
- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or `pom.xml` exists
- `src/`, `lib/`, or `app/` directories with code files exist
- Existing CI/CD configuration (`.github/workflows/`, `.gitlab-ci.yml`)

**Greenfield Indicators** (new project):
- No version control or empty git history
- No package manifests
- Empty or minimal directory structure
- Only spec-kit template files present

```
Project Analysis
─────────────────────────────────────

Project Type: {Greenfield | Brownfield}
Detected Markers:
  {[Y] | [N]} Git repository with history
  {[Y] | [N]} Package manifest (pyproject.toml, package.json, etc.)
  {[Y] | [N]} Source code directories
  {[Y] | [N]} CI/CD configuration
```

### Step 2: Check Existing Constitution

Check if constitution already exists:

```bash
if [ -f "memory/constitution.md" ]; then
  # Constitution exists
  if [ "$FORCE_FLAG" != "true" ]; then
    echo "Warning: Constitution already exists at memory/constitution.md"
    echo "Use --force to overwrite or edit manually"
    # Show current tier
    grep "TIER:" memory/constitution.md
  fi
fi
```

If constitution exists and `--force` is not set:
1. Display current constitution tier
2. Ask if user wants to replace, customize, or abort
3. If customize, suggest editing `memory/constitution.md` directly

### Step 3: Tech Stack Analysis (Brownfield)

For brownfield projects, perform comprehensive tech stack analysis:

#### Languages & Frameworks Detection

| Language | Detection Files | Framework Detection |
|----------|-----------------|---------------------|
| Python | `pyproject.toml`, `requirements.txt`, `setup.py` | Check deps for FastAPI, Django, Flask |
| TypeScript/JS | `package.json`, `tsconfig.json` | Check deps for Next.js, React, Vue, Express |
| Go | `go.mod` | Check imports for Chi, Gin, Echo |
| Rust | `Cargo.toml` | Check deps for Actix, Rocket, Axum |
| Java | `pom.xml`, `build.gradle` | Check deps for Spring Boot, Quarkus |

#### CI/CD Detection

| Platform | Detection Files |
|----------|-----------------|
| GitHub Actions | `.github/workflows/*.yml` |
| GitLab CI | `.gitlab-ci.yml` |
| CircleCI | `.circleci/config.yml` |
| Jenkins | `Jenkinsfile` |

#### Testing Infrastructure Detection

| Language | Test Framework Detection |
|----------|-------------------------|
| Python | pytest in deps, `tests/` directory |
| JavaScript | jest/vitest in deps, `__tests__/` directory |
| Go | `*_test.go` files |
| Rust | `tests/` directory |

#### Code Quality Tools Detection

| Tool Type | Detection |
|-----------|-----------|
| Linting | ruff.toml, .eslintrc, .golangci.yml |
| Formatting | prettier config, black config, rustfmt.toml |
| Type Checking | mypy.ini, tsconfig strict mode |

### Step 4: Tier Auto-Selection (Brownfield)

For brownfield projects without `--tier` flag, calculate tier automatically:

```
SCORE = 0

# Language complexity
languages_detected = count of detected languages
if languages_detected >= 3: SCORE += 3
elif languages_detected == 2: SCORE += 2
elif languages_detected == 1: SCORE += 1

# CI/CD presence
if CI/CD detected: SCORE += 2

# Testing infrastructure
if test_framework detected: SCORE += 1
if coverage_tool detected: SCORE += 1

# Security tools
security_tools_count = count of detected security tools
if security_tools_count >= 3: SCORE += 3
elif security_tools_count >= 1: SCORE += 2

# Container/orchestration
if Kubernetes manifests detected: SCORE += 2
elif Docker detected: SCORE += 1

# Linting/formatting
if linter detected: SCORE += 1
if type_checker detected: SCORE += 1

TIER MAPPING:
- SCORE 0-4: light
- SCORE 5-9: medium
- SCORE 10-14: heavy
```

For greenfield projects: Default to user selection or `medium` tier.

### Step 5: Generate Repository Facts

Create `memory/repo-facts.md` with analysis results:

```markdown
---
detected_at: {YYYY-MM-DD}
analysis_version: 1.0.0
project_type: {greenfield | brownfield}
primary_language: {language}
languages:
  - {language1}
  - {language2}
frameworks:
  - {framework1}
ci_cd: {platform}
test_framework: {framework}
linter: {tool}
formatter: {tool}
security_tools:
  - {tool1}
build_tools:
  - {tool1}
---

# Repository Facts

**Generated**: {YYYY-MM-DD} by `/flow:init` command

This document contains automatically detected repository characteristics.
LLM agents reference this file for project context.

## Languages & Frameworks

### Primary Language
- **{Language Name}**
- Detected via: {manifest files found}
- Package manager: {package manager}

{... additional sections based on detections ...}
```

### Step 6: Generate Constitution

Read the tier-appropriate template and customize:

1. **Project Name**: Auto-detect from package manifest or directory name
2. **Tech Stack Section**: Populate with detected languages/frameworks
3. **Linting Tools**: Fill with detected linters (medium/heavy tiers)
4. **CI/CD Tools**: Fill with detected CI/CD platform (medium/heavy tiers)
5. **Date**: Current date in YYYY-MM-DD format

**For Heavy Tier**: Preserve NEEDS_VALIDATION markers for:
- Compliance frameworks
- Retention period
- Approval authority
- Reporting window

Write customized constitution to `memory/constitution.md`.

### Step 7: Workflow Configuration (Optional)

If `--configure-workflow` flag is provided OR if `flowspec_workflow.yml` doesn't exist:

Prompt for workflow configuration (same as `/flow:reset`):

```
Would you like to configure workflow validation modes now?
  1. Yes - Configure validation gates for each transition
  2. No - Use defaults (NONE for all transitions)
  3. Later - Run /flow:reset when ready

Choice [2]: _
```

If yes, run the same validation mode prompts as `/flow:reset`.

### Step 8: Generate Summary Report

```
╔══════════════════════════════════════════════════════════════╗
║         Project Constitution Initialized                      ║
╚══════════════════════════════════════════════════════════════╝

📊 PROJECT ANALYSIS

Project Type: Brownfield (existing codebase)
Complexity Score: 8/14

Languages:
  [Y] Python 3.11+ (primary)
  [Y] TypeScript (secondary)

Frameworks:
  [Y] FastAPI 0.104+
  [Y] React 18

Build Tools:
  [Y] uv (Python package manager)
  [Y] pnpm (Node.js package manager)

Testing:
  [Y] pytest (test framework)
  [Y] pytest-cov (coverage)

Code Quality:
  [Y] ruff (linting + formatting)
  [Y] mypy (type checking)

CI/CD:
  [Y] GitHub Actions

🏛️ CONSTITUTION TIER

Selected Tier: medium
Rationale: Complexity score 8/14 suggests standard business project controls

📝 FILES CREATED

  [Y] memory/repo-facts.md (tech stack analysis)
  [Y] memory/constitution.md (governance document)
  {[Y] flowspec_workflow.yml (if --configure-workflow)}

📋 VALIDATION CHECKLIST

Review your constitution at memory/constitution.md and verify:

□ Project name is correct
□ Technology stack is complete and accurate
□ Quality standards reflect your practices
□ Git workflow matches your process
□ Testing requirements are achievable

Look for NEEDS_VALIDATION markers:
  grep -n "NEEDS_VALIDATION" memory/constitution.md

🎯 NEXT STEPS

1. Review constitution: memory/constitution.md
2. Resolve all NEEDS_VALIDATION markers
3. Commit both files:
   git add memory/repo-facts.md memory/constitution.md
   git commit -s -m "docs: add constitution and repo facts"

4. Start your first workflow:
   /flow:assess <feature-name>

💡 TIP: Edit 'memory/constitution.md' for more detailed customization
```

### Greenfield vs Brownfield Differences

| Aspect | Greenfield | Brownfield |
|--------|------------|------------|
| Tech Analysis | Minimal/skip | Full analysis |
| Default Tier | User choice or medium | Auto-calculated |
| Repo Facts | Basic template | Comprehensive |
| Recommendations | Setup guidance | Integration guidance |

### Error Handling

- **No write permissions**: Suggest running with appropriate permissions
- **Constitution locked**: Suggest `--force` or manual editing
- **Detection failure**: Fall back to user prompts for tier selection
- **Invalid tier value**: Show valid options (light, medium, heavy)

### Greenfield Quick Start

For new projects, provide quick start guidance:

```
🌱 Greenfield Project Detected

This appears to be a new project. Recommended setup:

1. Constitution: light tier (can upgrade later)
2. Workflow: Start with NONE validation (faster iteration)
3. First feature: Run /flow:assess to evaluate complexity

Would you like to:
  1. Use recommended settings (fast setup)
  2. Customize settings (guided prompts)
  3. Full enterprise setup (heavy tier + all gates)

Choice [1]: _
```

### Integration with Existing Commands

- **After init**: Run `/flow:assess <feature>` to start workflow
- **To customize more**: Edit `memory/constitution.md` directly
- **To reconfigure workflow**: Run `/flow:reset`
- **CLI equivalent**: `flowspec init --here --constitution {tier}`

### Quality Checks

Before completing:
- [ ] memory/ directory exists (created if needed)
- [ ] memory/repo-facts.md created with analysis
- [ ] memory/constitution.md created with appropriate tier
- [ ] NEEDS_VALIDATION markers preserved where appropriate
- [ ] Summary shows all created files
- [ ] Next steps are clear and actionable

## Important Notes

1. **Non-destructive by default**: Requires `--force` to overwrite existing constitution
2. **Git-safe**: Creates new files, doesn't modify existing tracked files
3. **Idempotent**: Running twice without `--force` is a no-op
4. **Tech stack aware**: Customizes constitution based on actual project technologies
5. **Tier upgradeable**: Start light, upgrade to medium/heavy as project grows
