---
mode: agent
description: Analyze repository and customize constitution template with detected tech stack and patterns. Supports --tier {light|medium|heavy} override.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This command analyzes the repository's technology stack, tooling, and development practices, then customizes the appropriate constitution tier template with repo-specific details.

## Execution Flow

### Step 1: Parse Arguments

Check for `--tier` flag in the arguments:
- `--tier light` - Use light constitution (minimal controls)
- `--tier medium` - Use medium constitution (balanced governance)
- `--tier heavy` - Use heavy constitution (full production-grade controls)

If no `--tier` flag provided, auto-detect tier based on project complexity (step 2).

### Step 2: Repository Analysis

Scan the repository to detect:

#### Languages and Frameworks

```bash
# Python detection
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ]; then
  echo "Python detected"
  # Check for frameworks
  grep -E "fastapi|flask|django|starlette" pyproject.toml requirements.txt 2>/dev/null
fi

# TypeScript/JavaScript detection
if [ -f "package.json" ]; then
  echo "TypeScript/JavaScript detected"
  # Check for frameworks
  jq -r '.dependencies,.devDependencies | keys[]' package.json 2>/dev/null | \
    grep -E "react|vue|angular|next|express|fastify|nest"
fi

# Go detection
if [ -f "go.mod" ]; then
  echo "Go detected"
  grep -E "gin|echo|chi|fiber" go.mod 2>/dev/null
fi

# Rust detection
if [ -f "Cargo.toml" ]; then
  echo "Rust detected"
  grep -E "actix|rocket|axum|warp" Cargo.toml 2>/dev/null
fi

# Java detection
if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
  echo "Java detected"
  grep -E "spring|quarkus|micronaut" pom.xml build.gradle 2>/dev/null
fi
```

#### Testing Frameworks

```bash
# Python testing
grep -E "pytest|unittest|nose" pyproject.toml requirements.txt 2>/dev/null

# JavaScript testing
jq -r '.devDependencies | keys[]' package.json 2>/dev/null | \
  grep -E "jest|vitest|mocha|jasmine|playwright|cypress"

# Go testing (built-in)
find . -name "*_test.go" -type f 2>/dev/null | head -1

# Rust testing (built-in)
find . -name "tests" -type d 2>/dev/null | head -1
```

#### Linting Tools

```bash
# Python linting
grep -E "ruff|black|flake8|pylint|mypy" pyproject.toml requirements.txt 2>/dev/null
[ -f ".ruff.toml" ] && echo "ruff.toml detected"

# JavaScript linting
jq -r '.devDependencies | keys[]' package.json 2>/dev/null | \
  grep -E "eslint|prettier|biome"
[ -f ".eslintrc.json" ] || [ -f ".prettierrc" ] && echo "ESLint/Prettier configured"

# Go linting
[ -f ".golangci.yml" ] && echo "golangci-lint configured"

# Rust linting (built-in clippy)
grep -E "clippy" Cargo.toml 2>/dev/null
```

#### CI/CD Configuration

```bash
# GitHub Actions
if [ -d ".github/workflows" ]; then
  echo "GitHub Actions detected"
  ls .github/workflows/*.{yml,yaml} 2>/dev/null
fi

# GitLab CI
[ -f ".gitlab-ci.yml" ] && echo "GitLab CI detected"

# Jenkins
[ -f "Jenkinsfile" ] && echo "Jenkins detected"

# CircleCI
[ -f ".circleci/config.yml" ] && echo "CircleCI detected"
```

#### Security Scanning

```bash
# SAST tools
grep -E "semgrep|bandit|gosec|brakeman" .github/workflows/*.yml pyproject.toml 2>/dev/null

# Container scanning
grep -E "trivy|snyk|grype|clair" .github/workflows/*.yml 2>/dev/null

# Dependency scanning
grep -E "dependabot|renovate" .github/ 2>/dev/null
[ -f ".github/dependabot.yml" ] && echo "Dependabot configured"
```

#### Code Review Patterns

```bash
# PR template
[ -f ".github/pull_request_template.md" ] && echo "PR template present"

# CODEOWNERS
[ -f ".github/CODEOWNERS" ] && echo "CODEOWNERS configured"

# Branch protection (infer from docs)
grep -iE "branch protection|protected branch|require review" README.md docs/*.md 2>/dev/null
```

### Step 3: Auto-Detect Tier (if not overridden)

Based on findings, suggest tier:

**Light Tier** - If 3 or fewer indicators:
- Single language
- Basic testing (if any)
- No CI/CD
- No code review process
- No security scanning

**Heavy Tier** - If 8+ indicators:
- Multiple languages
- Comprehensive testing (unit + integration)
- CI/CD configured
- Linting and formatting enforced
- Security scanning present
- Code review enforced (CODEOWNERS/branch protection)
- Container scanning
- Dependency management (Dependabot/Renovate)

**Medium Tier** - Everything in between (4-7 indicators)

### Step 4: Read Constitution Template

Read the appropriate template:

```bash
# Based on tier detection or --tier flag
if [ "$TIER" = "light" ]; then
  TEMPLATE="templates/constitutions/constitution-light.md"
elif [ "$TIER" = "heavy" ]; then
  TEMPLATE="templates/constitutions/constitution-heavy.md"
else
  TEMPLATE="templates/constitutions/constitution-medium.md"
fi
```

### Step 5: Customize Template

Replace placeholders with detected values:

| Placeholder | Detection Method |
|-------------|------------------|
| `[PROJECT_NAME]` | Git remote origin URL (parse repo name) or directory name |
| `[LANGUAGES_AND_FRAMEWORKS]` | From step 2: language + framework detection |
| `[LINTING_TOOLS]` | From step 2: linting tool detection |
| `[CI_CD_TOOLS]` | From step 2: CI/CD detection |
| `[DATE]` | Current date in YYYY-MM-DD format |

**Add NEEDS_VALIDATION markers** to sections that were auto-generated:

```markdown
<!-- NEEDS_VALIDATION: Auto-detected from package.json, verify accuracy -->
```

### Step 6: Write Updated Constitution

Write the customized constitution to `memory/constitution.md`:

```bash
# Create memory/ directory if it doesn't exist
mkdir -p memory

# Write customized constitution
# (perform the actual write operation)
```

### Step 6.5: Write Repository Facts

After detecting all repository characteristics, write them to `memory/repo-facts.md` for LLM context:

**File Format** (YAML frontmatter + markdown sections):

```markdown
---
generated: 2025-12-04
updated: 2025-12-04
generator: /speckit:constitution
---

# Repository Facts

## Languages
- Python 3.11
- TypeScript 5.0

## Frameworks
- FastAPI
- React

## Testing
- pytest
- jest

## Linting & Formatting
- ruff
- eslint
- prettier

## CI/CD
- GitHub Actions

## Security Tools
- Dependabot
- Trivy

## Build Tools
- uv
- pnpm

## Notes
[Preserve any existing manual notes from previous runs]
```

**Update Logic**:
1. If `memory/repo-facts.md` exists:
   - Preserve the `Notes` section (everything from "## Notes" to end of file)
   - Update all other sections with fresh detections
   - Update `updated` timestamp in frontmatter
   - Keep original `generated` timestamp

2. If `memory/repo-facts.md` does NOT exist:
   - Create new file with all detected facts
   - Set both `generated` and `updated` to current date
   - Add placeholder text in Notes section

3. Include in detected facts:
   - **Languages**: Python, TypeScript, Go, Rust, Java (with versions if detectable)
   - **Frameworks**: FastAPI, React, Next.js, Express, etc.
   - **Testing**: pytest, jest, vitest, Go testing, etc.
   - **Linting & Formatting**: ruff, black, eslint, prettier, golangci-lint, clippy
   - **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI
   - **Security Tools**: Dependabot, Renovate, Trivy, Snyk, Semgrep, Bandit
   - **Build Tools**: uv, pnpm, npm, cargo, maven, gradle, make, mage

**Write Operation**:

```bash
# Create memory/ directory if it doesn't exist
mkdir -p memory

# Write repo-facts.md (perform the actual write operation)
# Preserve Notes section if file exists
```

### Step 7: Output Validation Checklist

After generating the constitution, output a validation checklist showing:

1. **Detected Configuration**:
   ```
   ✓ Languages detected: Python (FastAPI), TypeScript (React)
   ✓ Testing: pytest, jest
   ✓ Linting: ruff, eslint
   ✓ CI/CD: GitHub Actions
   ✓ Security: Dependabot, Trivy
   ```

2. **Tier Selection**:
   ```
   Tier selected: Medium (7 indicators found)
   Override with: /speckit:constitution --tier {light|medium|heavy}
   ```

3. **Validation Checklist**:
   ```
   Constitution generated at: memory/constitution.md

   Please review and validate:
   [ ] Project name is correct
   [ ] Languages and frameworks list is complete
   [ ] Linting tools match your workflow
   [ ] CI/CD description is accurate
   [ ] Git workflow matches team practices
   [ ] Task management requirements are appropriate
   [ ] Quality standards match project maturity

   Sections marked with NEEDS_VALIDATION require manual review.
   ```

4. **Next Steps**:
   ```
   Next steps:
   1. Review memory/constitution.md
   2. Review memory/repo-facts.md (used for LLM context)
   3. Update any NEEDS_VALIDATION sections
   4. Commit: git commit -s -m "docs: add customized constitution and repo facts"
   5. Share with team for review
   ```

## Detection Logic Summary

### Languages

- **Python**: `pyproject.toml`, `requirements.txt`, `setup.py`, `*.py` files
- **TypeScript/JavaScript**: `package.json`, `tsconfig.json`, `*.ts` files
- **Go**: `go.mod`, `go.sum`, `*.go` files
- **Rust**: `Cargo.toml`, `*.rs` files
- **Java**: `pom.xml`, `build.gradle`, `*.java` files

### Frameworks

- **Python**: fastapi, flask, django, starlette
- **JavaScript/TypeScript**: react, vue, angular, next, express, fastify, nest
- **Go**: gin, echo, chi, fiber
- **Rust**: actix, rocket, axum, warp
- **Java**: spring, quarkus, micronaut

### Testing

- **Python**: pytest, unittest, nose
- **JavaScript**: jest, vitest, mocha, jasmine, playwright, cypress
- **Go**: `*_test.go` files (built-in testing)
- **Rust**: `tests/` directory (built-in testing)
- **Java**: junit, testng

### Linting

- **Python**: ruff, black, flake8, pylint, mypy
- **JavaScript**: eslint, prettier, biome
- **Go**: golangci-lint
- **Rust**: clippy (built-in)
- **Java**: checkstyle, spotbugs

### CI/CD

- GitHub Actions: `.github/workflows/*.yml`
- GitLab CI: `.gitlab-ci.yml`
- Jenkins: `Jenkinsfile`
- CircleCI: `.circleci/config.yml`

### Security

- SAST: semgrep, bandit (Python), gosec (Go), brakeman (Ruby)
- Container Scanning: trivy, snyk, grype, clair
- Dependency Scanning: dependabot, renovate

## Example Output

```
Repository Analysis Complete
============================

Languages Detected:
- Python 3.11 (FastAPI framework)
- TypeScript (React framework)

Testing Frameworks:
- pytest (Python)
- jest (JavaScript)

Linting Tools:
- ruff (Python)
- eslint + prettier (JavaScript)

CI/CD:
- GitHub Actions (.github/workflows/ci.yml, test.yml)

Security:
- Dependabot (dependency scanning)
- Trivy (container scanning)

Code Review:
- PR template configured
- CODEOWNERS file present

Tier Recommendation: Medium (7 indicators)
Template: templates/constitutions/constitution-medium.md

Files generated:
- memory/constitution.md (customized governance rules)
- memory/repo-facts.md (repository characteristics for LLM context)

Validation Checklist:
[ ] Project name: jp-spec-kit (auto-detected from git remote)
[ ] Languages: Python (FastAPI), TypeScript (React) - NEEDS_VALIDATION
[ ] Linting: ruff, eslint - NEEDS_VALIDATION
[ ] CI/CD: GitHub Actions - NEEDS_VALIDATION
[ ] Git workflow: Feature branches required (from medium tier)
[ ] Task requirements: At least one AC required (from medium tier)

Review sections marked with NEEDS_VALIDATION and update as needed.

Next steps:
1. Review memory/constitution.md
2. Update NEEDS_VALIDATION sections
3. Commit changes: git commit -s -m "docs: add customized medium-tier constitution"
4. Share with team for review
```

## Implementation Notes

- All file operations should use relative paths from project root
- Use `grep`, `find`, `jq` for detection (widely available tools)
- Handle missing files gracefully (detection is best-effort)
- NEEDS_VALIDATION markers ensure user reviews auto-generated content
- Tier auto-detection is a suggestion, not a mandate
- Support `--tier` override for explicit control

## Error Handling

If detection fails (empty repo, no recognizable stack):
- Default to **light** tier
- Add NEEDS_VALIDATION to all sections
- Inform user: "Unable to auto-detect configuration, using light tier template. Please review all sections."

If template file missing:
- Error: "Constitution template not found at templates/constitutions/constitution-{tier}.md"
- Suggest: "Run 'specify init' to install templates"
