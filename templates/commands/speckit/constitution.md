---
description: Analyze repository and write findings to memory/repo-facts.md with detected tech stack
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command analyzes the repository structure to detect languages, frameworks, CI/CD systems, testing tools, linting configurations, and security tools. It writes findings to `memory/repo-facts.md` in a structured format that LLM agents can reference for project context.

### Overview

The `/speckit:constitution` command:
1. Scans repository for technology stack indicators
2. Detects languages, frameworks, tooling, and development practices
3. Writes structured findings to `memory/repo-facts.md`
4. Outputs clear summary of detected technologies

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

### Step 2: Create Repository Facts Document

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

### Step 3: Generate Summary Report

Output a comprehensive summary to the user:

```
╔══════════════════════════════════════════════════════════════╗
║         Repository Analysis Complete                         ║
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

📝 OUTPUT

Files Created:
  ✓ memory/repo-facts.md

🎯 NEXT STEPS

1. Review findings: memory/repo-facts.md
2. Validate detected technologies are accurate
3. Update if tools were missed or misidentified
4. Commit changes:

   git add memory/repo-facts.md
   git commit -s -m "docs: add repo facts from constitution analysis

   - Detected languages, frameworks, and tooling
   - Documented testing, CI/CD, and security setup
   - Created structured reference for LLM agents

   Generated via /speckit:constitution command"
```

### Step 4: Edge Cases & Error Handling

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
- Suggest running `/speckit:constitution` again after setup

## Important Notes

1. **Read-only analysis**: This command analyzes but does not modify code or configs
2. **Version sensitivity**: Include version numbers where detected (Python 3.11+, FastAPI 0.104+)
3. **Tool precedence**: Prefer modern tools when conflicts exist
4. **CI/CD awareness**: Check workflow files for additional tool detection
5. **Multi-language projects**: Clearly distinguish primary vs secondary languages
6. **Framework specificity**: Be precise (Next.js vs React, FastAPI vs Flask)
7. **LLM-friendly format**: Structure content for easy parsing by AI agents

## Validation Before Writing

Before writing `memory/repo-facts.md`:

1. Verify at least one language detected (fail gracefully if not)
2. Ensure YAML frontmatter is valid
3. Check all file paths mentioned actually exist
4. Confirm tool names are official (not aliases or abbreviations)
5. Validate date format (YYYY-MM-DD)

## Output Format

- Use consistent formatting across all sections
- Keep descriptions factual and concise
- Include actual file paths for all configs
- Use bullet points for lists
- Use **bold** for tool/technology names
- Use `code formatting` for file paths and commands
