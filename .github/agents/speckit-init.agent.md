---
name: "speckit-init"
description: "Initialize project with constitution and role selection for personalized workflows"
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Grep"
  - "Glob"
  - "mcp__backlog__*"
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command initializes the project constitution and allows the user to select their primary role for personalized command visibility and agent handoffs.

### Overview

The `/speckit:init` command:
1. Detects project type (greenfield vs brownfield)
2. Analyzes repository for tech stack detection
3. Prompts for role selection (pm, arch, dev, sec, qa, ops, all)
4. Selects appropriate constitution tier
5. Generates `memory/constitution.md` with customizations
6. Generates `memory/repo-facts.md` with detected technologies
7. Configures workflow with selected role

### Argument Parsing

Parse `$ARGUMENTS` for optional flags:

| Flag | Description |
|------|-------------|
| `--tier {light\|medium\|heavy}` | Force specific constitution tier |
| `--role {pm\|arch\|dev\|sec\|qa\|ops\|all}` | Force specific role (non-interactive) |
| `--force` | Overwrite existing constitution without prompting |
| `--skip-analysis` | Skip tech stack analysis, use template defaults |
| `--configure-workflow` | Also run workflow configuration |

Environment variable override:
- `FLOWSPEC_PRIMARY_ROLE`: Override role selection (e.g., `export FLOWSPEC_PRIMARY_ROLE=dev`)

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
  {✓ | ✗} Git repository with history
  {✓ | ✗} Package manifest (pyproject.toml, package.json, etc.)
  {✓ | ✗} Source code directories
  {✓ | ✗} CI/CD configuration
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
3. If customize, suggest `/speckit:constitution` for detailed customization

### Step 3: Role Selection Prompt

**Precedence order** for role selection:
1. `FLOWSPEC_PRIMARY_ROLE` environment variable (highest priority)
2. `--role` flag from command line
3. Interactive prompt (if not provided)
4. Default to "all" if non-interactive and no override

If `--role` flag is NOT provided and `FLOWSPEC_PRIMARY_ROLE` env var is NOT set:

Display interactive role selection:

```
╔══════════════════════════════════════════════════════════════╗
║  Select Your Primary Role                                     ║
╚══════════════════════════════════════════════════════════════╝

Choose your role to personalize command suggestions and agent handoffs:

  1. 📋 Product Manager (PM)
     • Focus: Requirements & specifications
     • Commands: /pm:assess, /pm:define, /pm:discover
     • Agents: @product-requirements-manager, @workflow-assessor

  2. 🏗️  Architect (Arch)
     • Focus: System design & architecture decisions
     • Commands: /arch:design, /arch:decide, /arch:model
     • Agents: @software-architect, @platform-engineer

  3. 💻 Developer (Dev) [DEFAULT]
     • Focus: Implementation & code development
     • Commands: /dev:build, /dev:debug, /dev:refactor
     • Agents: @frontend-engineer, @backend-engineer, @ai-ml-engineer

  4. 🔒 Security Engineer (Sec)
     • Focus: Security scanning & vulnerability management
     • Commands: /sec:scan, /sec:triage, /sec:fix, /sec:audit
     • Agents: @secure-by-design-engineer

  5. ✅ QA Engineer (QA)
     • Focus: Testing & quality validation
     • Commands: /qa:test, /qa:verify, /qa:review
     • Agents: @quality-guardian, @release-manager

  6. 🚀 SRE/DevOps (Ops)
     • Focus: Deployment & operations
     • Commands: /ops:deploy, /ops:monitor, /ops:respond, /ops:scale
     • Agents: @sre-agent

  7. 🌐 All Roles
     • Full access to all commands and agents
     • No filtering or personalization

Enter selection [1-7] (default: 3): _
```

**Role Mapping**:
- Input 1 → "pm"
- Input 2 → "arch"
- Input 3 → "dev" (default)
- Input 4 → "sec"
- Input 5 → "qa"
- Input 6 → "ops"
- Input 7 → "all"

Validate input is in range 1-7. If invalid, reprompt.

**Environment Variable Detection**:
If `FLOWSPEC_PRIMARY_ROLE` is set, show:
```
Role auto-selected from environment variable:
  FLOWSPEC_PRIMARY_ROLE={role}
  Selected: {icon} {display_name}

(Override with --role flag if needed)
```

**Non-Interactive Mode**:
If `--role` flag is provided:
```
Role selected via --role flag:
  Selected: {icon} {display_name}
```

### Step 4: Tech Stack Analysis (Brownfield)

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

### Step 5: Tier Auto-Selection (Brownfield)

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

### Step 6: Generate Repository Facts

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

**Generated**: {YYYY-MM-DD} by `/speckit:init` command

This document contains automatically detected repository characteristics.
LLM agents reference this file for project context.

## Languages & Frameworks

### Primary Language
- **{Language Name}**
- Detected via: {manifest files found}
- Package manager: {package manager}

{... additional sections based on detections ...}
```

### Step 7: Generate Constitution

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

### Step 8: Update flowspec_workflow.yml with Role

Check if `flowspec_workflow.yml` exists. If it does, update the `roles.primary` field:

```yaml
roles:
  primary: "{selected_role}"  # Update this field
  show_all_commands: false
  definitions:
    # ... existing role definitions remain unchanged
```

If `flowspec_workflow.yml` does not exist, this will be handled by workflow configuration in the next step.

**IMPORTANT**: Preserve all other fields in the file. Only update `roles.primary`.

### Step 9: Workflow Configuration (Optional)

If `--configure-workflow` flag is provided OR if `flowspec_workflow.yml` doesn't exist:

Prompt for workflow configuration:

```
Would you like to configure workflow validation modes now?
  1. Yes - Configure validation gates for each transition
  2. No - Use defaults (NONE for all transitions)
  3. Later - Run /speckit:configure when ready

Choice [2]: _
```

If yes, run the same validation mode prompts as `/speckit:configure` (see configure.md).

### Step 10: Generate Summary Report

```
╔══════════════════════════════════════════════════════════════╗
║         Project Initialization Complete                       ║
╚══════════════════════════════════════════════════════════════╝

🎭 ROLE CONFIGURATION

Selected Role: {icon} {display_name}
Role ID: {role_id}
Selection Date: {YYYY-MM-DD HH:MM:SS}

This role determines:
  • Which commands appear prominently in your IDE
  • Which agents are auto-loaded for handoffs
  • Default workflow entry points

To change your role later, run: /speckit:configure --role <new_role>

📊 PROJECT ANALYSIS

Project Type: {Brownfield | Greenfield}
Complexity Score: {score}/14

Languages:
  ✓ {Language1} (primary)
  {✓ Language2 (secondary)}

Frameworks:
  ✓ {Framework1}
  {✓ Framework2}

Build Tools:
  ✓ {tool1}
  {✓ tool2}

Testing:
  ✓ {test framework}
  {✓ coverage tool}

Code Quality:
  ✓ {linter}
  {✓ formatter}
  {✓ type checker}

CI/CD:
  {✓ | ✗} {platform}

🏛️ CONSTITUTION TIER

Selected Tier: {light | medium | heavy}
Rationale: {reason based on complexity score and project type}

📝 FILES CREATED/UPDATED

  ✓ memory/repo-facts.md (tech stack analysis)
  ✓ memory/constitution.md (governance document)
  ✓ flowspec_workflow.yml (role configuration updated)
  {✓ flowspec_workflow.yml (workflow validation modes) - if --configure-workflow}

📋 VALIDATION CHECKLIST

Review your constitution at memory/constitution.md and verify:

□ Project name is correct
□ Technology stack is complete and accurate
□ Quality standards reflect your practices
□ Git workflow matches your process
□ Testing requirements are achievable
□ Role selection matches your responsibilities

Look for NEEDS_VALIDATION markers:
  grep -n "NEEDS_VALIDATION" memory/constitution.md

🎯 NEXT STEPS

1. Review constitution: memory/constitution.md
2. Review role configuration: flowspec_workflow.yml (roles section)
3. Resolve all NEEDS_VALIDATION markers
4. Commit initialization files:
   git add memory/repo-facts.md memory/constitution.md flowspec_workflow.yml
   git commit -s -m "feat: initialize project with constitution and role"

5. Start your first workflow (based on your role):
   {PM role: /pm:assess <feature-name>}
   {Arch role: /arch:design <component-name>}
   {Dev role: /dev:build <feature-name>}
   {Sec role: /sec:scan}
   {QA role: /qa:verify}
   {Ops role: /ops:deploy}
   {All roles: /pm:assess <feature-name>}

💡 TIPS

• Change role anytime: /speckit:configure --role <new_role>
• Override role per session: export FLOWSPEC_PRIMARY_ROLE=<role>
• See all commands regardless of role: Set show_all_commands: true in flowspec_workflow.yml
• Customize constitution further: /speckit:constitution
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
- **Invalid role value**: Show valid options (pm, arch, dev, sec, qa, ops, all)
- **No flowspec_workflow.yml**: Create one with selected role
- **Invalid FLOWSPEC_PRIMARY_ROLE env var**: Show warning and fall back to prompt

### Greenfield Quick Start

For new projects, provide quick start guidance:

```
🌱 Greenfield Project Detected

This appears to be a new project. Recommended setup:

1. Role: Choose based on your primary responsibility (default: dev)
2. Constitution: light tier (can upgrade later)
3. Workflow: Start with NONE validation (faster iteration)
4. First feature: Run role-appropriate command to start

Would you like to:
  1. Use recommended settings (fast setup)
  2. Customize settings (guided prompts)
  3. Full enterprise setup (heavy tier + all gates)

Choice [1]: _
```

### Integration with Existing Commands

- **After init**: Run role-appropriate workflow command
- **To customize more**: Run `/speckit:constitution` for detailed customization
- **To reconfigure**: Run `/speckit:configure`
- **To change role**: Run `/speckit:configure --role <new_role>`

### Quality Checks

Before completing:
- [ ] memory/ directory exists (created if needed)
- [ ] memory/repo-facts.md created with analysis
- [ ] memory/constitution.md created with appropriate tier
- [ ] flowspec_workflow.yml exists with roles.primary set
- [ ] Selected role is valid (pm, arch, dev, sec, qa, ops, all)
- [ ] NEEDS_VALIDATION markers preserved where appropriate
- [ ] Summary shows selected role with icon
- [ ] Next steps are role-appropriate and actionable

## Important Notes

1. **Role-first experience**: Role selection happens early for personalized setup
2. **Non-destructive by default**: Requires `--force` to overwrite existing constitution
3. **Git-safe**: Creates new files, doesn't modify existing tracked files
4. **Environment variable support**: `FLOWSPEC_PRIMARY_ROLE` allows per-session overrides
5. **Idempotent**: Running twice without `--force` is a no-op
6. **Tech stack aware**: Customizes constitution based on actual project technologies
7. **Tier upgradeable**: Start light, upgrade to medium/heavy as project grows
8. **Role switchable**: Change role anytime with `/speckit:configure --role <new_role>`
