---
description: Analyze repository and create customized constitution.md based on detected tech stack
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command analyzes the repository structure to detect languages, frameworks, CI/CD systems, testing tools, linting configurations, and security tools. It:
1. Writes findings to `memory/repo-facts.md` for LLM agent reference
2. Auto-selects or accepts a tier (light/medium/heavy) via `--tier` flag
3. Customizes the tier-appropriate constitution template with detected technologies
4. Writes `memory/constitution.md` with NEEDS_VALIDATION markers for user review

### Overview

The `/speckit:constitution` command:
1. Scans repository for technology stack indicators
2. Detects languages, frameworks, tooling, and development practices
3. Writes structured findings to `memory/repo-facts.md`
4. Auto-detects or accepts constitution tier via `--tier` flag
5. Customizes constitution template with detected tech stack
6. Writes `memory/constitution.md` with NEEDS_VALIDATION markers
7. Outputs validation checklist and summary

### Step 1: Repository Structure Analysis

Perform a comprehensive repository scan to detect:

#### Languages & Frameworks

**Detection patterns**:

- **Python**: `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`, `uv.lock`, `poetry.lock`
  - Frameworks: Check dependencies for FastAPI, Django, Flask, SQLAlchemy, Pydantic
  - Package managers: uv, pip, poetry, pipenv

- **Node.js/TypeScript**: `package.json`, `tsconfig.json`, `bun.lockb`, `pnpm-lock.yaml`, `yarn.lock`
  - Frameworks: Check dependencies for Next.js, React, Vue, Express, Fastify, NestJS, Svelte
  - Package managers: pnpm, bun, yarn, npm

- **Go**: `go.mod`, `go.sum`
  - Frameworks: Check imports for Chi, Gin, Echo, Fiber, standard library net/http
  - Build tools: Makefile, mage, Task

- **Rust**: `Cargo.toml`, `Cargo.lock`
  - Frameworks: Check dependencies for Actix, Rocket, Axum, Warp, Tokio

- **Java**: `pom.xml`, `build.gradle`, `build.gradle.kts`
  - Frameworks: Check dependencies for Spring Boot, Quarkus, Micronaut

- **Ruby**: `Gemfile`, `Gemfile.lock`
  - Frameworks: Rails, Sinatra, Hanami

**Analysis approach**:
- Use Read tool to check for presence of manifest files
- Parse manifests to extract framework dependencies
- Determine primary language (most code files) and secondary languages
- Identify package manager by lockfile presence

#### CI/CD Systems

**Detection patterns**:

- **GitHub Actions**: `.github/workflows/*.yml`, `.github/workflows/*.yaml`
- **GitLab CI**: `.gitlab-ci.yml`
- **CircleCI**: `.circleci/config.yml`
- **Jenkins**: `Jenkinsfile`, `jenkins/`
- **Azure Pipelines**: `azure-pipelines.yml`, `.azure/`
- **Buildkite**: `.buildkite/pipeline.yml`
- **Travis CI**: `.travis.yml`

**Analysis approach**:
- Check for workflow/pipeline configuration files
- Identify primary CI/CD platform
- Note if multiple platforms are in use
- Extract workflow names and jobs if simple to parse

#### Testing Infrastructure

**Detection patterns**:

- **Test directories**: `tests/`, `test/`, `__tests__/`, `spec/`, `e2e/`, `src/test/`
- **Python**: `pytest.ini`, `tox.ini`, `.coveragerc`, presence of `pytest` in dependencies
- **JavaScript/TypeScript**: `jest.config.js`, `vitest.config.ts`, `playwright.config.ts`, `cypress.json`
- **Go**: `*_test.go` files, `go test` in Makefile or CI
- **Rust**: `tests/` directory, `#[cfg(test)]` in source
- **Java**: `src/test/`, JUnit/TestNG in dependencies

**Analysis approach**:
- Identify test framework(s) in use
- Check for coverage configuration
- Determine test types present (unit, integration, e2e, contract)
- Note test runners and task definitions

#### Linting & Formatting

**Detection patterns**:

- **Python**:
  - `ruff.toml`, `pyproject.toml [tool.ruff]`
  - `.flake8`, `.pylintrc`, `mypy.ini`, `pyproject.toml [tool.mypy]`
  - `.black`, `pyproject.toml [tool.black]`

- **JavaScript/TypeScript**:
  - `.eslintrc*`, `eslint.config.js`, `eslint.config.mjs`
  - `prettier.config.*`, `.prettierrc*`
  - `tsconfig.json` (check `strict` mode)

- **Go**:
  - `.golangci.yml`, `.golangci.yaml`
  - `gofmt`, `goimports` usage in CI

- **Rust**:
  - `rustfmt.toml`, `clippy.toml`
  - `cargo fmt`, `cargo clippy` in CI

- **Java**:
  - `checkstyle.xml`, `pmd.xml`, `spotbugs.xml`

**Analysis approach**:
- Check for linter configuration files
- Identify formatters (Prettier, Black, rustfmt, gofmt)
- Note type checkers (mypy, TypeScript strict mode, Flow)
- Check for pre-commit hooks (`.pre-commit-config.yaml`)

#### Security Tools

**Detection patterns**:

- **Dependency scanning**:
  - `.github/dependabot.yml`, `dependabot.yml`
  - `.snyk`, `snyk.json`
  - `renovate.json`, `.renovaterc`

- **SAST tools**:
  - `bandit.yaml`, `.bandit` (Python)
  - `gosec.yaml`, `.gosec.json` (Go)
  - `.semgrep.yml`, `semgrep.yaml`
  - `sonar-project.properties` (SonarQube)

- **Container scanning**:
  - `trivy.yaml`, `.trivyignore`
  - `grype.yaml`

- **Secret scanning**:
  - `.gitleaks.toml`, `gitleaks.toml`
  - `trufflehog.yaml`

**Analysis approach**:
- Identify security scanning tools in CI/CD workflows
- Check for security tool configurations
- Note dependency update automation
- Check for pre-commit hooks for security

#### Build & Container Tools

**Detection patterns**:

- **Docker**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- **Kubernetes**: `k8s/`, `kubernetes/`, `manifests/`, `helm/`, `kustomize/`
- **Makefiles**: `Makefile`, `*.mk`
- **Task runners**: `Taskfile.yml`, `justfile`, `mage.go`

**Analysis approach**:
- Check for containerization (Docker, Podman)
- Identify orchestration platforms (Kubernetes, Docker Compose)
- Note build automation tools
- Check for infrastructure as code

### Step 2: Determine Constitution Tier

Parse the `$ARGUMENTS` user input for a `--tier` flag:

**Flag format**: `--tier {light|medium|heavy}`

**If flag is provided**:
- Validate the tier value is one of: `light`, `medium`, `heavy`
- Use the specified tier
- Note in output that tier was user-specified

**If flag is NOT provided (auto-detection)**:

Use this scoring algorithm to determine tier:

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
- SCORE 10+: heavy
```

**Tier characteristics**:

- **light**: Minimal controls for startups/hobby projects
  - Small team (1-2 people)
  - Simple tech stack (1-2 languages)
  - Basic or no CI/CD
  - Minimal tooling

- **medium**: Standard controls for typical business projects
  - Team size 3-10
  - Multiple languages/frameworks
  - CI/CD present
  - Standard testing and linting

- **heavy**: Strict controls for enterprise/regulated environments
  - Large team (10+) or regulatory requirements
  - Complex tech stack
  - Multiple security tools
  - Orchestration platforms (Kubernetes)
  - Comprehensive testing, SAST, dependency scanning

**Output tier decision**:
- Store selected tier in a variable for later use
- Log tier and score to console for transparency

### Step 3: Create Repository Facts Document

Write findings to `memory/repo-facts.md` with YAML frontmatter and structured content:

**File structure**:

```markdown
---
detected_at: YYYY-MM-DD
analysis_version: 1.0.0
primary_language: python
languages:
  - python
  - typescript
frameworks:
  - fastapi
  - react
ci_cd: github-actions
test_framework: pytest
linter: ruff
formatter: ruff
security_tools:
  - dependabot
  - bandit
build_tools:
  - docker
  - uv
---

# Repository Facts

**Generated**: YYYY-MM-DD by `/speckit:constitution` command

This document contains automatically detected repository characteristics. LLM agents reference this file for project context.

## Languages & Frameworks

### Primary Language
- **[Language Name and Version]**
- Detected via: [manifest files found]
- Package manager: [package manager name]

### Secondary Languages
- **[Language Name]**: [Purpose/usage]

### Frameworks
- **[Framework Name]**: [Description/purpose]

## Build & Package Management

### [Language] Tooling
- **Package manager**: [name]
- **Project config**: [file path]
- Virtual environment: [path if applicable]

## Testing Infrastructure

### Test Framework
- **[Framework name]**: [Description]

### Test Organization
- Unit tests: [path]
- Integration tests: [path]
- E2E tests: [path]

### Coverage
- Tool: [coverage tool name]
- Config: [config file path]
- Target: [coverage percentage if detected]

## Code Quality

### Linting
- **[Linter name]**: [Description]
- Config: [config file path]
- Replaces: [tools it replaces, if applicable]

### Formatting
- **[Formatter name]**: [Description]
- Config: [config file path]

### Type Checking
- **[Type checker name]**: [Mode/strictness]
- Config: [config file path]

### Pre-commit Hooks
- File: [.pre-commit-config.yaml or other]
- Hooks: [list of hooks]

## CI/CD

### Platform
- **[Platform name]**

### Workflows
- [workflow file]: [description]

### Required Checks
- [list of checks that must pass]

## Security

### Tools Detected
- **[Tool name]**: [Description]
  - Config: [config file path]
  - Frequency: [if applicable]

### Practices
- [list of detected security practices]

## Container & Orchestration

- **Dockerfile**: [description]
- **docker-compose.yml**: [description if present]
- **Kubernetes**: [manifests location if present]

## Notes

- This document is auto-generated and should be reviewed for accuracy
- Re-run `/speckit:constitution` after major tooling changes
```

**Important guidelines**:
- Use actual detected values, not placeholders
- Omit sections for technologies not detected
- Include file paths for all detected configurations
- Keep descriptions concise and factual
- Use consistent tool naming (official names)

### Step 4: Customize Constitution Template

After creating `memory/repo-facts.md`, customize the constitution template based on the selected tier:

#### 4.1 Read Constitution Template

Read the tier-appropriate template file:
- **light tier**: `templates/constitutions/constitution-light.md`
- **medium tier**: `templates/constitutions/constitution-medium.md`
- **heavy tier**: `templates/constitutions/constitution-heavy.md`

#### 4.2 Detect Project Name

Auto-detect project name from common sources (in priority order):

1. **Node.js**: `package.json` → `name` field
2. **Python**: `pyproject.toml` → `[project].name` or `[tool.poetry].name`
3. **Go**: `go.mod` → module name (last path segment)
4. **Rust**: `Cargo.toml` → `[package].name`
5. **Java**: `pom.xml` → `<artifactId>` or `build.gradle` → `rootProject.name`
6. **Git**: Repository directory name as fallback

**Sanitize and validate the detected project name:**
- Remove or replace special characters that are not alphanumeric, dash (-), or underscore (_).
- Replace spaces with dashes (-) or underscores (_).
- Trim leading and trailing whitespace.
- Ensure the name is suitable for use in a constitution document and does not contain formatting that could cause issues in markdown or automation.
If multiple sources exist, prefer the primary language's package manifest.

#### 4.3 Format Tech Stack Section

Create formatted tech stack content replacing `[LANGUAGES_AND_FRAMEWORKS]`:

**Format**:
```markdown
### Languages & Frameworks
- **[Language]** ([Version if detected])
  - Framework: [Framework Name]
  - Package Manager: [Package Manager]

### Build & Tooling
- **[Tool Category]**: [Tool Names]

### Testing
- **Framework**: [Test Framework]
- **Coverage**: [Coverage Tool]

### Code Quality
- **Linter**: [Linter Name]
- **Formatter**: [Formatter Name]
- **Type Checker**: [Type Checker if applicable]
```

**For medium and heavy tiers**, also populate:
- `[LINTING_TOOLS]` - List of detected linters and formatters
- `[CI_CD_TOOLS]` - Detected CI/CD platforms

**For heavy tier only**, populate:
- <!-- NEEDS_VALIDATION: [COMPLIANCE_FRAMEWORKS] --> - Leave as NEEDS_VALIDATION placeholder (user must specify)
- <!-- NEEDS_VALIDATION: [RETENTION_PERIOD] --> - Leave as NEEDS_VALIDATION placeholder
- <!-- NEEDS_VALIDATION: [APPROVAL_AUTHORITY] --> - Leave as NEEDS_VALIDATION placeholder
- <!-- NEEDS_VALIDATION: [REPORTING_WINDOW] --> - Leave as NEEDS_VALIDATION placeholder

#### 4.4 Perform Template Replacements

Replace these placeholders in the template:

1. `[PROJECT_NAME]` → Detected project name (from Step 4.2)
2. `[LANGUAGES_AND_FRAMEWORKS]` → Formatted tech stack (from Step 4.3)
3. `[LINTING_TOOLS]` → Linting tools list (medium/heavy only)
4. `[CI_CD_TOOLS]` → CI/CD platform details (heavy only)
5. `[DATE]` → Current date in YYYY-MM-DD format

**IMPORTANT**: For heavy tier, the following placeholders must remain as NEEDS_VALIDATION and should NOT be replaced:
- `[COMPLIANCE_FRAMEWORKS]`
- `[RETENTION_PERIOD]`
- `[APPROVAL_AUTHORITY]`
- `[REPORTING_WINDOW]`
**IMPORTANT**: Keep ALL existing `<!-- NEEDS_VALIDATION: ... -->` markers from the template. Do NOT remove them.

#### 4.5 Write Constitution File

Write the customized content to `memory/constitution.md`:

**Pre-write checks**:
1. Ensure `memory/` directory exists (create if needed)
2. Validate that all placeholders outside of NEEDS_VALIDATION comments have been replaced. Placeholders within NEEDS_VALIDATION comments (e.g., `[COMPLIANCE_FRAMEWORKS]`, `[RETENTION_PERIOD]`) should remain for user review.
3. Verify NEEDS_VALIDATION markers and their contained placeholders are preserved.

**If `memory/constitution.md` already exists**:
- Warn user that existing constitution will be overwritten
- Suggest backing up if it contains custom edits
- Proceed with write (user can restore from git if needed)

### Step 5: Generate Summary Report and Validation Checklist

Output a comprehensive summary to the user with tier information and validation checklist:

```
╔══════════════════════════════════════════════════════════════╗
║         Constitution Generated Successfully                  ║
╚══════════════════════════════════════════════════════════════╝

📊 DETECTED TECHNOLOGIES

Languages:
  ✓ Python 3.11+ (primary)
  ✓ TypeScript (secondary)

Frameworks:
  ✓ FastAPI 0.104+
  ✓ React 18

Build Tools:
  ✓ uv (Python package manager)
  ✓ pnpm (Node.js package manager)

Testing:
  ✓ pytest (test framework)
  ✓ pytest-cov (coverage)

Code Quality:
  ✓ ruff (linting + formatting)
  ✓ mypy (type checking)

Security:
  ✓ Dependabot
  ✓ bandit (SAST)

CI/CD:
  ✓ GitHub Actions (.github/workflows/)

🏛️ CONSTITUTION TIER

Selected Tier: [tier name]
[If auto-detected: Complexity Score: X/15]
[If user-specified: User specified via --tier flag]

Template: templates/constitutions/constitution-[tier].md

📝 OUTPUT

Files Created:
  ✓ memory/repo-facts.md
  ✓ memory/constitution.md

📋 VALIDATION CHECKLIST

Review your constitution at memory/constitution.md and verify:

□ Project name is correct
□ Technology stack is complete and accurate
□ Team size matches your actual team (if mentioned)
□ Deployment frequency is accurate (if mentioned)
□ Quality standards reflect your practices
□ Git workflow matches your process
□ Testing requirements are achievable
□ Security controls are appropriate

Look for NEEDS_VALIDATION markers in the constitution file and resolve them:
- Search for: <!-- NEEDS_VALIDATION:
- Each marker indicates a section requiring manual review

Run this to find all validation markers:
  grep -n "NEEDS_VALIDATION" memory/constitution.md

🎯 NEXT STEPS

1. Review constitution: memory/constitution.md
2. Resolve all NEEDS_VALIDATION markers
3. Adjust tier if needed: Re-run with --tier {light|medium|heavy}
4. Commit both files:

   git add memory/repo-facts.md memory/constitution.md
   git commit -s -m "docs: add constitution and repo facts

   - Auto-detected {light|medium|heavy} tier based on project complexity
   - Customized constitution with detected tech stack
   - Created structured repository facts for LLM agents

   Generated via /speckit:constitution command"

💡 TIP: If tier seems wrong, override with:
   /speckit:constitution --tier {light|medium|heavy}
```

**Adapt summary to actual findings**:
- Replace example technologies with actually detected ones
- Omit sections with no findings
- Show actual tier and score
- Include tier override tip if auto-detected tier might not fit project needs

### Step 6: Edge Cases & Error Handling

**Scenario: memory/ directory not found**
- Create `memory/` directory automatically
- Proceed with analysis and file creation
- Note in output that directory was created

**Scenario: Ambiguous primary language**
- If multiple languages have similar file counts, list all as co-primary
- Default to alphabetical order if equal weight
- Include note in repo-facts.md explaining ambiguity

**Scenario: No CI/CD detected**
- Note absence in repo-facts.md
- Suggest GitHub Actions for GitHub repos
- Include in recommendations section

**Scenario: Mixed package managers**
- Example: Both `requirements.txt` and `pyproject.toml` found
- Detect which is actively used (check lockfiles, CI references)
- Prefer modern tools (uv > pip, pnpm > npm, bun > npm)
- Document both if both are legitimately used

**Scenario: No test framework detected**
- Note absence in repo-facts.md
- Recommend appropriate framework based on language
- Include in recommendations section

**Scenario: Minimal repository**
- If very few technologies detected, still create repo-facts.md
- Note that analysis found limited tooling
- Default to "light" tier
- Suggest running `/speckit:constitution` again after setup

**Scenario: Invalid --tier flag value**
- If user provides `--tier` with invalid value (not light/medium/heavy)
- Output error message explaining valid values
- Do not proceed with generation
- Example error: "Invalid tier 'basic'. Valid tiers: light, medium, heavy"

**Scenario: Cannot detect project name**
- If no package manifests found
- Use repository directory name
- Add NEEDS_VALIDATION marker to project name in constitution
- Warn user in output to verify project name

**Scenario: Constitution template not found**
- If `templates/constitutions/constitution-{tier}.md` does not exist
- Output clear error message
- Suggest checking JP Spec Kit installation
- Do not create incomplete constitution file

**Scenario: Existing constitution.md present**
- Warn user before overwriting
- Display message: "Existing constitution.md will be overwritten. Backup is available via git history."
- Proceed with write (user controls via git)

**Scenario: templates/ directory not accessible**
- If running outside of JP Spec Kit structure
- Output error explaining command must be run in project with JP Spec Kit installed
- Provide guidance: "Ensure templates/constitutions/ exists in your project or JP Spec Kit installation"

## Important Notes

1. **Dual file output**: Creates both `repo-facts.md` (analysis) and `constitution.md` (governance)
2. **Version sensitivity**: Include version numbers where detected (Python 3.11+, FastAPI 0.104+)
3. **Tool precedence**: Prefer modern tools when conflicts exist
4. **CI/CD awareness**: Check workflow files for additional tool detection
5. **Multi-language projects**: Clearly distinguish primary vs secondary languages
6. **Framework specificity**: Be precise (Next.js vs React, FastAPI vs Flask)
7. **LLM-friendly format**: Structure content for easy parsing by AI agents
8. **NEEDS_VALIDATION markers**: Always preserve markers from templates - never remove them
9. **Tier selection**: Auto-detection is a starting point - users can override with `--tier` flag
10. **Template integrity**: Keep all template sections intact, only replace placeholders

## Validation Before Writing

Before writing `memory/repo-facts.md`:

1. Verify at least one language detected (fail gracefully if not)
2. Ensure YAML frontmatter is valid
3. Check all file paths mentioned actually exist
4. Confirm tool names are official (not aliases or abbreviations)
5. Validate date format (YYYY-MM-DD)

Before writing `memory/constitution.md`:

1. Verify tier is valid (light, medium, or heavy)
2. Confirm template file exists and is readable
3. Ensure all placeholders are replaced (except those in NEEDS_VALIDATION comments)
4. Verify NEEDS_VALIDATION markers are preserved from the template
5. Validate project name was detected or defaults to directory name
6. Check date format is YYYY-MM-DD

## Output Format

- Use consistent formatting across all sections
- Keep descriptions factual and concise
- Include actual file paths for all configs
- Use bullet points for lists
- Use **bold** for tool/technology names
- Use `code formatting` for file paths and commands
