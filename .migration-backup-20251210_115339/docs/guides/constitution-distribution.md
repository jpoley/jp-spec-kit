# Constitution Distribution User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Tier Selection Guide](#tier-selection-guide)
3. [Getting Started](#getting-started)
4. [LLM Customization](#llm-customization)
5. [NEEDS_VALIDATION Markers](#needs_validation-markers)
6. [Validation Workflow](#validation-workflow)
7. [Enforcement in /jpspec Commands](#enforcement-in-jpspec-commands)
8. [CLI Command Reference](#cli-command-reference)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is a Constitution?

A **constitution** is your project's governance document that defines:

- **Development workflow rules** - Git branching, PR requirements, commit standards
- **Quality standards** - Testing coverage, code review requirements, documentation expectations
- **Task management** - Acceptance criteria requirements, task quality standards
- **Technology stack** - Languages, frameworks, linting tools, CI/CD configuration
- **Security practices** - Secrets management, vulnerability handling, access control

The constitution lives at `memory/constitution.md` in your project and serves as the **single source of truth** for how your team works.

### Why Tier Selection Matters

JP Spec Kit provides **three constitution tiers** to match different project needs:

| Tier | Best For | Enforcement Level | Key Characteristics |
|------|----------|-------------------|---------------------|
| **Light** | Solo devs, hobby projects, startups | Warnings only | Minimal controls, fast iteration |
| **Medium** | Small teams, business projects | Warnings + confirmation | Standard PR/review process |
| **Heavy** | Enterprise, regulated environments | Hard blocks | Strict controls, compliance-ready |

Choosing the right tier ensures your constitution **helps** rather than **hinders** your development workflow.

### Workflow Overview

```
1. Choose Tier
   └─> Run `specify init my-project --constitution medium`

2. Customize Constitution
   └─> Run `/speckit:constitution` (LLM detects your tech stack)

3. Validate Auto-Generated Content
   └─> Run `specify constitution validate`
   └─> Review NEEDS_VALIDATION markers
   └─> Update content and remove markers

4. Work with Confidence
   └─> /jpspec commands enforce constitution rules
   └─> Constitution guides team practices
```

---

## Tier Selection Guide

### Light Tier

**When to use:**
- Solo developer or very small team (1-2 people)
- Hobby projects or early-stage startups
- Rapid prototyping or experimentation
- Learning new technologies

**Target audience:**
- Indie developers
- Open source hobby projects
- Personal portfolios
- MVP development

**Key characteristics:**
```markdown
Git Workflow:
- Feature branches encouraged (but optional)
- Direct commits to main allowed ("yolo mode")
- PRs are optional

Code Review:
- Review when time permits
- Self-merge allowed

Testing:
- Tests for critical paths
- No coverage requirements

Task Quality:
- Acceptance criteria when scope is unclear
```

**Enforcement:**
- **Warnings only** - /jpspec commands warn but never block
- You can proceed even with unvalidated constitution
- `--skip-validation` flag available but not required

**Choose Light if:**
- You value speed over process
- You're the only developer
- You want minimal overhead
- You're comfortable with "move fast, fix later"

### Medium Tier

**When to use:**
- Small to medium teams (3-10 people)
- Business applications with users
- Projects with multiple contributors
- Growing startups needing structure

**Target audience:**
- Small business teams
- Growing startups
- Open source projects with community
- Consulting projects

**Key characteristics:**
```markdown
Git Workflow:
- All changes via feature branches
- PRs required for all changes
- No direct commits to main

Code Review:
- Minimum 1 reviewer required
- Code owner approval for sensitive changes

Testing:
- Unit + integration tests
- 70% coverage target
- CI checks required

Task Quality:
- Acceptance criteria required on all tasks
- Task-PR synchronization enforced
```

**Enforcement:**
- **Warnings + confirmation prompts** - /jpspec commands warn and ask for confirmation
- Can proceed after acknowledging warnings
- Constitution validation recommended before starting work

**Choose Medium if:**
- You have multiple developers
- You need code review but not heavy process
- You want CI/CD best practices
- You're building for customers/users

### Heavy Tier

**When to use:**
- Large teams (10+ people)
- Enterprise environments
- Regulated industries (finance, healthcare, government)
- Security-critical applications

**Target audience:**
- Enterprise development teams
- Banks, hospitals, government agencies
- SaaS companies with SOC 2/HIPAA requirements
- Open source projects with security focus

**Key characteristics:**
```markdown
Git Workflow:
- Protected branches with strict rules
- Minimum 2 reviewers required
- Force push disabled
- Conventional commit format enforced

Code Review:
- Minimum 2 reviewers (one senior engineer)
- Security impact assessment
- All comments must be resolved

Testing:
- Unit + integration + E2E tests
- 80% coverage minimum
- Security scans (SAST, DAST, dependency)
- Performance tests for critical paths

Task Quality:
- Acceptance criteria mandatory
- Risk assessment required
- Traceability enforced (task ↔ PR linkage)

Security:
- No secrets in code (hard enforcement)
- Vulnerability SLAs (24h critical, 7d high)
- Audit logging required
- Data encryption enforced
```

**Enforcement:**
- **Hard blocks** - /jpspec commands refuse to proceed with unvalidated constitution
- Constitution validation mandatory before implementation
- `--skip-validation` requires special override (not recommended)

**Choose Heavy if:**
- You have compliance requirements (SOC 2, HIPAA, GDPR)
- Security is paramount
- You need full audit trails
- Multiple teams collaborate on same codebase

---

## Tier Comparison Table

| Feature | Light | Medium | Heavy |
|---------|-------|--------|-------|
| **Feature branches** | Optional | Required | Required |
| **Direct main commits** | Allowed | Blocked | Blocked |
| **PRs required** | No | Yes | Yes |
| **Min reviewers** | 0 | 1 | 2 (1 senior) |
| **Test coverage** | Critical paths | 70% target | 80% minimum |
| **Acceptance criteria** | Optional | Required | Required + validated |
| **DCO sign-off** | Required | Required | Required |
| **Security scans** | Optional | Recommended | Mandatory |
| **Enforcement** | Warn | Warn + confirm | Block |

---

## Getting Started

### New Project Initialization

Create a new project with constitution:

```bash
# Interactive selection - prompts for tier choice
specify init my-project

# Pre-select tier
specify init my-project --constitution medium

# Skip LLM customization (manual customization later)
specify init my-project --constitution light --skip-llm
```

**What happens:**
1. Project directory created
2. Constitution template copied to `memory/constitution.md`
3. LLM customization triggered (unless `--skip-llm`)
4. NEEDS_VALIDATION markers added to auto-generated sections

### Existing Project Setup

Add constitution to an existing project:

```bash
# Navigate to your project
cd /path/to/existing-project

# Initialize in current directory
specify init --here

# Or specify tier explicitly
specify init --here --constitution heavy
```

**Detection logic:**
- JP Spec Kit detects existing project if any of these exist:
  - `.git/` directory
  - `package.json` (Node.js)
  - `pyproject.toml` (Python)
  - `Cargo.toml` (Rust)
  - `go.mod` (Go)
  - `pom.xml` (Java)
- If `memory/constitution.md` already exists, **it is preserved** (no overwrite)
- If missing, you're prompted to select a tier

### Project Upgrade

Update existing JP Spec Kit installation:

```bash
# Upgrade JP Spec Kit
specify upgrade

# If constitution missing, you'll be prompted:
# "No constitution found. Select tier: light/medium/heavy"
```

**Safe behavior:**
- Existing constitutions are **never overwritten** during upgrades
- Only prompts if `memory/constitution.md` is missing
- Constitution version tracking (future feature) will detect outdated templates

---

## LLM Customization

### What Gets Customized?

The LLM analyzes your repository and customizes the constitution template with:

| Placeholder | Detection Method | Example Output |
|-------------|------------------|----------------|
| `[PROJECT_NAME]` | Git remote URL or directory name | `my-awesome-app` |
| `[LANGUAGES_AND_FRAMEWORKS]` | File extensions, config files | `Python 3.11, FastAPI, pytest, ruff` |
| `[LINTING_TOOLS]` | package.json, pyproject.toml, pre-commit | `ruff check, ruff format, mypy` |
| `[CI_CD_TOOLS]` | .github/workflows/, .gitlab-ci.yml | `GitHub Actions (.github/workflows/)` |
| `[DATE]` | Current date | `2025-12-04` |

### Running LLM Customization

#### During Project Initialization

```bash
# Automatic (default behavior)
specify init my-project --constitution medium

# The LLM will:
# 1. Scan your repository
# 2. Detect languages, frameworks, tools
# 3. Fill in placeholders
# 4. Add NEEDS_VALIDATION markers
```

#### Manual Customization

```bash
# Use the slash command
/speckit:constitution

# With tier override
/speckit:constitution --tier heavy
```

**When to use manual customization:**
- After adding new languages/frameworks
- When automatic detection failed
- After upgrading JP Spec Kit
- To refresh constitution with latest repo state

### What Gets Detected

#### Languages

Detected from file extensions:
- `.py` → Python
- `.ts`, `.tsx` → TypeScript
- `.js`, `.jsx` → JavaScript
- `.go` → Go
- `.rs` → Rust
- `.java` → Java
- `.rb` → Ruby
- `.php` → PHP

#### Frameworks

Detected from dependency files:
- Python: `requirements.txt`, `pyproject.toml` (FastAPI, Django, Flask, pytest)
- Node.js: `package.json` (React, Next.js, Express, Jest)
- Go: `go.mod` (Gin, Echo, Chi)
- Rust: `Cargo.toml` (Actix, Rocket, Tokio)

#### Linting Tools

Detected from configuration files:
- Python: `ruff` (ruff.toml), `black` (pyproject.toml), `mypy` (mypy.ini)
- JavaScript/TypeScript: `eslint` (.eslintrc), `prettier` (.prettierrc)
- Go: `golangci-lint` (.golangci.yml)
- Rust: `clippy` (Cargo.toml)

#### CI/CD

Detected from file presence:
- `.github/workflows/` → GitHub Actions
- `.gitlab-ci.yml` → GitLab CI
- `Jenkinsfile` → Jenkins
- `.circleci/config.yml` → CircleCI

#### Testing

Detected from configuration:
- Python: `pytest` (pytest.ini, pyproject.toml)
- JavaScript: `jest` (jest.config.js), `vitest` (vitest.config.js)
- Go: `go test` (standard library)
- Rust: `cargo test` (standard)

### Reviewing Auto-Generated Content

After LLM customization, **always review the output**:

```bash
# Check what needs validation
specify constitution validate

# Example output:
# Constitution Validation Status
# ========================================
#
# ⚠ 3 section(s) need validation:
#
# ✗ Technology Stack
#   Line 74: Populate with detected languages/frameworks
#
# ✗ Linting & Formatting
#   Line 78: Detected linting tools
#
# ✗ Version and dates
#   Line 95: Version and dates
```

**Common issues:**
- Monorepos: May detect too many languages
- Multi-framework projects: May miss secondary frameworks
- Custom tooling: Won't detect non-standard tools

**Solution:** Manually edit `memory/constitution.md` to correct any mistakes before removing NEEDS_VALIDATION markers.

---

## NEEDS_VALIDATION Markers

### Format

```markdown
<!-- NEEDS_VALIDATION: Description of what needs validation -->
```

### Purpose

NEEDS_VALIDATION markers indicate sections that require human review:

1. **Prevent blind acceptance** - Auto-generated content might be incorrect
2. **Explicit review process** - Clear indication of what needs judgment
3. **Quality assurance** - Constitution reflects your actual project
4. **Traceability** - Easy to track which sections have been reviewed

### Common Markers

#### Project Name

```markdown
# [PROJECT_NAME] Constitution
<!-- NEEDS_VALIDATION: Project name -->
```

**What to validate:**
- Verify project name is correct
- Replace `[PROJECT_NAME]` with actual name
- Ensure name matches across constitution

#### Technology Stack

```markdown
## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
```

**What to validate:**
- Review detected languages (Python, TypeScript, Go, etc.)
- Verify frameworks are correct (FastAPI, React, etc.)
- Add missing frameworks the LLM didn't detect
- Specify version requirements (e.g., Python 3.11+)

#### Linting Tools

```markdown
### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]
```

**What to validate:**
- Confirm linting tools are correct (ruff, eslint, etc.)
- Add custom linters not detected
- Document linting configurations
- Specify formatter preferences

#### Version and Dates

```markdown
**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
```

**What to validate:**
- Set initial version (typically `1.0.0`)
- Record ratification date (when constitution is adopted)
- Set last amended date (same as ratification for new constitutions)

#### Quality Standards (Medium/Heavy Tiers)

```markdown
<!-- NEEDS_VALIDATION: Adjust quality principles to team practices -->
- **Test Coverage**: Critical paths must have test coverage
- **Code Review**: All changes require at least one reviewer
- **Documentation**: Public APIs and complex logic must be documented
```

**What to validate:**
- Confirm test coverage targets match team capability
- Verify code review requirements align with team size
- Adjust documentation standards based on project complexity

#### Branch Strategy (Medium/Heavy Tiers)

```markdown
<!-- NEEDS_VALIDATION: Branch strategy matches team workflow -->
- All changes go through feature branches
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Main branch is protected - no direct commits
```

**What to validate:**
- Confirm branch naming convention matches existing practices
- Verify protected branch settings are configured
- Adjust PR requirements for team size

### How to Validate

1. **Read the marker description** - Understand what needs review
2. **Review the content** - Check if auto-generated content is correct
3. **Update if needed** - Correct mistakes or add missing information
4. **Remove the marker** - Delete the entire `<!-- NEEDS_VALIDATION: ... -->` line

**Example: Before validation**
```markdown
## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
- Python 3.11
- FastAPI
```

**Example: After validation**
```markdown
## Technology Stack
- **Python 3.11+**: FastAPI, SQLAlchemy, Pydantic
- **TypeScript 5**: React, Next.js 15
- **PostgreSQL 15**: Primary database
```

Notice the NEEDS_VALIDATION marker is removed, and the content is expanded with correct details.

---

## Validation Workflow

### Step 1: Check Validation Status

```bash
specify constitution validate
```

**Example output:**
```
Constitution Validation Status
========================================

⚠ 3 section(s) need validation:

✗ Technology Stack
  Line 52: Populate with detected languages/frameworks

✗ Linting & Formatting
  Line 88: Detected linting tools

✗ Version and dates
  Line 104: Version and dates

Next steps:
1. Review each section marked with NEEDS_VALIDATION
2. Update the content to match your project needs
3. Remove the <!-- NEEDS_VALIDATION: ... --> comment
4. Run this command again to verify

Edit file: /home/user/my-project/memory/constitution.md
```

### Step 2: Edit Constitution

Open `memory/constitution.md` in your editor:

```bash
# Using your preferred editor
nvim memory/constitution.md
code memory/constitution.md
```

### Step 3: Review Each Marker

For each `<!-- NEEDS_VALIDATION: ... -->` marker:

1. **Understand the requirement** - Read the marker description
2. **Verify auto-generated content** - Check if the LLM detected correctly
3. **Update content** - Add missing information, correct mistakes
4. **Remove the marker** - Delete the comment line

**Example: Technology Stack**

Before:
```markdown
## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
```

After:
```markdown
## Technology Stack
- **Python 3.11+**: FastAPI, SQLAlchemy, Pydantic, pytest
- **PostgreSQL 15**: Primary database
- **Redis**: Caching layer
- **Docker**: Containerization
```

### Step 4: Verify Completion

```bash
specify constitution validate
```

**Success output:**
```
Constitution Validation Status
========================================

✓ Constitution fully validated!

All sections have been reviewed. No NEEDS_VALIDATION markers found.
```

### Validation Checklist

Use this checklist to ensure thorough validation:

- [ ] **Project name** - Correct and consistent
- [ ] **Technology stack** - All languages and frameworks listed
- [ ] **Linting tools** - All linters and formatters documented
- [ ] **CI/CD configuration** - Pipeline details accurate
- [ ] **Testing requirements** - Coverage targets match team capability
- [ ] **Branch strategy** - Naming and protection rules match actual setup
- [ ] **Code review requirements** - Reviewer count appropriate for team size
- [ ] **Version and dates** - Initial version set, ratification date recorded
- [ ] **Quality standards** - Realistic and achievable for team
- [ ] **Security practices** - Appropriate for project sensitivity

### JSON Output for Automation

For CI/CD or scripting:

```bash
specify constitution validate --json
```

**Example output:**
```json
{
  "path": "/home/user/my-project/memory/constitution.md",
  "validated": false,
  "unvalidated_count": 3,
  "markers": [
    {
      "line": 52,
      "section": "Technology Stack",
      "description": "Populate with detected languages/frameworks",
      "context": "<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->"
    },
    {
      "line": 88,
      "section": "Linting & Formatting",
      "description": "Detected linting tools",
      "context": "<!-- NEEDS_VALIDATION: Detected linting tools -->"
    },
    {
      "line": 104,
      "section": "Governance",
      "description": "Version and dates",
      "context": "<!-- NEEDS_VALIDATION: Version and dates -->"
    }
  ]
}
```

### Exit Codes

| Exit Code | Meaning | Use Case |
|-----------|---------|----------|
| `0` | Fully validated | Constitution is ready to use |
| `1` | Unvalidated sections | Review and update required |
| `2` | Error | File not found or read error |

**CI/CD integration:**
```bash
#!/bin/bash
specify constitution validate
if [ $? -eq 1 ]; then
  echo "❌ Constitution has unvalidated sections"
  exit 1
fi
echo "✅ Constitution validated"
```

---

## Enforcement in /jpspec Commands

### How Enforcement Works

Before executing `/jpspec` commands, JP Spec Kit checks:

1. **Constitution exists** - Is `memory/constitution.md` present?
2. **Constitution validated** - Are there NEEDS_VALIDATION markers?
3. **Tier-appropriate action** - Warn, confirm, or block based on tier

### Tier-Specific Behavior

#### Light Tier: Warnings Only

```bash
$ /jpspec:specify

⚠ Warning: Constitution has 2 unvalidated sections.
  Run 'specify constitution validate' to review.

Proceeding with /jpspec:specify...
```

**Behavior:**
- Commands warn but **never block**
- You can proceed immediately
- Constitution validation is recommended but optional

**When to use:**
- Solo development
- Rapid prototyping
- You accept the risk of working with unvalidated constitution

#### Medium Tier: Warnings + Confirmation

```bash
$ /jpspec:specify

⚠ Warning: Constitution has 2 unvalidated sections.
  Run 'specify constitution validate' to review.

Do you want to proceed anyway? [y/N]:
```

**Behavior:**
- Commands warn and **prompt for confirmation**
- Type `y` to proceed, `N` to abort
- Gives you a chance to validate before continuing

**When to use:**
- Small team development
- Business applications
- You want a reminder but retain control

#### Heavy Tier: Hard Block

```bash
$ /jpspec:specify

❌ Error: Constitution validation required.

Constitution has 2 unvalidated sections:
  - Technology Stack (line 52)
  - Version and dates (line 104)

Please run 'specify constitution validate' and resolve all markers before proceeding.

Use '--skip-validation' to override (NOT RECOMMENDED for compliance environments).
```

**Behavior:**
- Commands **refuse to proceed** with unvalidated constitution
- Must validate or use `--skip-validation` override
- Ensures compliance and audit trail

**When to use:**
- Enterprise environments
- Regulated industries
- Compliance requirements (SOC 2, HIPAA)

### Bypassing Validation

For emergencies only:

```bash
# Use --skip-validation flag
/jpspec:specify --skip-validation

⚠ WARNING: Skipping constitution validation. This is NOT recommended for production.

Proceeding with /jpspec:specify...
```

**When to use:**
- Emergency hotfixes
- Temporary overrides with team approval
- Testing workflows

**Heavy tier note:** `--skip-validation` requires special permissions in enterprise environments.

### Which Commands Enforce?

All `/jpspec` workflow commands:

| Command | Checks Constitution | Tier Enforcement |
|---------|---------------------|------------------|
| `/jpspec:assess` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:specify` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:research` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:plan` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:implement` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:validate` | Yes | Light: warn, Medium: confirm, Heavy: block |
| `/jpspec:operate` | Yes | Light: warn, Medium: confirm, Heavy: block |

**Note:** Utility commands (`backlog`, `specify init`, etc.) do not enforce constitution.

---

## CLI Command Reference

### `specify init`

Create new project or initialize existing project with constitution.

**New project:**
```bash
# Interactive tier selection
specify init my-project

# Pre-select tier
specify init my-project --constitution medium

# Skip LLM customization
specify init my-project --constitution light --skip-llm
```

**Existing project:**
```bash
# Initialize in current directory
specify init --here

# With tier selection
specify init --here --constitution heavy
```

**Options:**
- `--constitution {light|medium|heavy}` - Pre-select constitution tier
- `--skip-llm` - Skip automatic LLM customization
- `--here` - Initialize in current directory (existing project)

### `specify constitution validate`

Check constitution for unvalidated sections.

**Basic usage:**
```bash
# Check default constitution location
specify constitution validate

# Check custom location
specify constitution validate --path custom/constitution.md
```

**Options:**
- `--path PATH` - Custom constitution file path
- `--json` - Output in JSON format for automation

**Exit codes:**
- `0` - All validated
- `1` - Unvalidated sections exist
- `2` - File not found or read error

**Examples:**
```bash
# Human-readable output
specify constitution validate

# JSON output for CI/CD
specify constitution validate --json

# Check custom path
specify constitution validate --path docs/governance.md
```

### `specify constitution version`

Show constitution version and metadata (future feature).

**Planned usage:**
```bash
specify constitution version

# Example output:
# Constitution Version: 1.2.0
# Tier: medium
# Template Version: 2.1.0
# Ratified: 2025-01-15
# Last Amended: 2025-03-22
```

### `specify upgrade`

Upgrade JP Spec Kit and handle constitution detection.

**Usage:**
```bash
# Upgrade JP Spec Kit
specify upgrade

# If constitution missing:
# "No constitution found. Select tier: light/medium/heavy"
```

**Behavior:**
- Checks for `memory/constitution.md` existence
- Prompts for tier selection if missing
- Preserves existing constitutions (no overwrite)
- Future: Detects outdated constitutions and offers upgrades

---

## Maintenance

### Updating Your Constitution

Your constitution is a **living document** that evolves with your project.

**When to update:**
- Adding new languages or frameworks
- Changing team size or structure
- Adopting new tools (linters, CI/CD)
- Compliance requirements change
- Team consensus on process improvements

**How to update:**

1. **Edit the file:**
   ```bash
   nvim memory/constitution.md
   ```

2. **Make changes** to the relevant sections

3. **Update version and date:**
   ```markdown
   **Version**: 1.1.0 | **Last Amended**: 2025-12-05
   ```

4. **Commit with description:**
   ```bash
   git add memory/constitution.md
   git commit -s -m "chore: update constitution to add TypeScript linting

   - Added eslint and prettier to linting tools
   - Updated version to 1.1.0

   Signed-off-by: Your Name <you@example.com>"
   ```

### Version Tracking

Constitution versions follow **semantic versioning**:

- **Major (X.0.0)**: Breaking changes to workflow (e.g., tier upgrade)
- **Minor (1.X.0)**: Additive changes (e.g., new tools, practices)
- **Patch (1.1.X)**: Corrections or clarifications

**Example:**
```markdown
## Governance

**Version**: 1.2.1 | **Ratified**: 2025-01-15 | **Last Amended**: 2025-03-22

### Change Log

#### 1.2.1 (2025-03-22)
- Clarified code review requirements
- Fixed typo in branch naming convention

#### 1.2.0 (2025-02-10)
- Added security scanning requirement
- Updated test coverage target to 75%

#### 1.0.0 (2025-01-15)
- Initial ratification
```

### Handling Upgrades

When JP Spec Kit releases new constitution templates:

**Future feature:**
```bash
# Check for constitution updates
specify constitution check-updates

# Example output:
# Constitution template 2.0.0 available (you have 1.0.0)
# Changes:
# - Added security scanning section
# - Updated git workflow best practices
# - Improved task quality guidelines

# Upgrade constitution
specify constitution upgrade

# Interactive merge:
# - Preserve your custom amendments
# - Apply new template sections
# - Output merged constitution for review
```

**Manual upgrade (current):**

1. **Backup current constitution:**
   ```bash
   cp memory/constitution.md memory/constitution.md.backup
   ```

2. **Review new template:**
   ```bash
   # View latest template
   cat templates/constitutions/constitution-medium.md
   ```

3. **Manually merge changes:**
   - Copy relevant new sections
   - Preserve your custom amendments
   - Update version number

4. **Validate merged constitution:**
   ```bash
   specify constitution validate
   ```

---

## Troubleshooting

### "Constitution file not found"

**Problem:** The constitution file doesn't exist.

**Solution:**
```bash
# Create constitution
specify init --here

# Or manually create from template
mkdir -p memory
cp templates/constitutions/constitution-medium.md memory/constitution.md
```

### LLM Generated Incorrect Language Detection

**Problem:** LLM detected wrong languages or missed some.

**Example:**
```markdown
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
- Python 3.11
- JavaScript  ← Should be TypeScript
```

**Solution:**
1. Edit `memory/constitution.md`
2. Correct the detected languages:
   ```markdown
   - Python 3.11+: FastAPI, pytest
   - TypeScript 5: React, Next.js
   ```
3. Remove the NEEDS_VALIDATION marker
4. Run `specify constitution validate` to confirm

### Constitution Validation Stuck

**Problem:** Can't remove NEEDS_VALIDATION marker for a section you can't populate yet.

**Example:**
```markdown
<!-- NEEDS_VALIDATION: Compliance frameworks applicable to project -->
[COMPLIANCE_FRAMEWORKS]
```

**Solution Option 1** (Best practice):
Add placeholder content and remove marker:
```markdown
## Compliance
This project currently has no compliance requirements.
Will be updated when compliance frameworks are determined.
```

**Solution Option 2** (Temporary):
Leave marker in place, document why in a note:
```markdown
<!-- NEEDS_VALIDATION: Compliance frameworks - TBD after legal review -->
## Compliance
Pending legal review of applicable compliance frameworks.
```

### /jpspec Command Blocked by Unvalidated Constitution

**Problem:** Heavy tier blocks /jpspec commands until validation complete.

**Error:**
```
❌ Error: Constitution validation required.
Constitution has 1 unvalidated section:
  - Compliance frameworks (line 142)
```

**Solution Option 1** (Recommended):
Validate the constitution:
```bash
specify constitution validate  # See which sections need validation
nvim memory/constitution.md     # Fix them
specify constitution validate  # Verify all clear
```

**Solution Option 2** (Emergency only):
Use skip flag:
```bash
/jpspec:specify --skip-validation
```

**Note:** Document why you skipped validation in team chat/issue tracker.

### Constitution Version Mismatch After Upgrade

**Problem:** After `specify upgrade`, constitution feels outdated.

**Future feature:**
```bash
specify constitution diff

# Shows differences between your constitution and latest template
# Helps you decide what to update
```

**Current workaround:**
1. Review latest template: `cat templates/constitutions/constitution-medium.md`
2. Manually compare with your `memory/constitution.md`
3. Copy relevant improvements
4. Update version number

### Multiple Languages Detected in Monorepo

**Problem:** Monorepo has many languages, constitution is cluttered.

**Solution:**
Organize by primary vs. supporting languages:

```markdown
## Technology Stack

### Primary Languages
- **Python 3.11+**: Backend services (FastAPI, SQLAlchemy)
- **TypeScript 5**: Frontend applications (React, Next.js)

### Supporting Languages
- **Go 1.22+**: CLI tools
- **Shell**: Build scripts and automation
```

### Team Disagrees on Tier Selection

**Problem:** Some team members want Light, others want Heavy.

**Solution:**

1. **Start conservative:** Choose Medium tier (middle ground)
2. **Trial period:** Use for 2-4 weeks
3. **Retrospective:** Discuss what's working/not working
4. **Adjust:** Upgrade to Heavy or downgrade to Light based on consensus

**Tier upgrade example:**
```bash
# Copy new template
cp templates/constitutions/constitution-heavy.md memory/constitution.md.new

# Merge your custom sections into new template
# Update tier comment at top
# Commit with justification
git commit -s -m "chore: upgrade constitution from medium to heavy tier

Team voted to adopt stricter controls due to:
- Growing team size (now 8 developers)
- Security audit requirements
- Customer compliance requests

Version bumped to 2.0.0 (major change).

Signed-off-by: Your Name <you@example.com>"
```

---

## Best Practices

### Do:
- ✅ Choose tier based on actual team size and needs
- ✅ Validate constitution before starting implementation work
- ✅ Review LLM-generated content carefully
- ✅ Update constitution as project evolves
- ✅ Commit validated constitution to version control
- ✅ Document why you made constitution changes

### Don't:
- ❌ Choose Heavy tier "just to be safe" (creates unnecessary friction)
- ❌ Remove NEEDS_VALIDATION markers without reviewing content
- ❌ Ignore warnings from /jpspec commands
- ❌ Skip validation because "it's just a template"
- ❌ Make constitution changes without team consensus (Medium/Heavy tiers)

---

## Related Documentation

- [Constitution Validation Guide](./constitution-validation.md) - Detailed validation workflow
- [Constitution Distribution PRD](../prd/constitution-distribution-prd.md) - Full feature specification
- [Tiered Constitution Templates](../../templates/constitutions/) - Template source files
- [Case Study: Constitution Templates](../case-studies/02-constitution-templates.md) - Implementation story
- [JP Spec Kit CLI Reference](../reference/cli-commands.md) - All CLI commands

---

## Quick Reference

### Commands

```bash
# Create new project with constitution
specify init my-project --constitution medium

# Add constitution to existing project
specify init --here

# Check validation status
specify constitution validate

# Get JSON output
specify constitution validate --json

# Run LLM customization
/speckit:constitution

# Upgrade JP Spec Kit (detects missing constitutions)
specify upgrade
```

### Files

```
memory/constitution.md          # Your project's constitution
templates/constitutions/        # Template source files
  ├── constitution-light.md     # Light tier template
  ├── constitution-medium.md    # Medium tier template
  └── constitution-heavy.md     # Heavy tier template
```

### NEEDS_VALIDATION Format

```markdown
<!-- NEEDS_VALIDATION: Description of what to validate -->
```

### Exit Codes

- `0` - Constitution fully validated
- `1` - Unvalidated sections exist
- `2` - File not found or error

---

## Getting Help

**Questions or issues?**
- Open an issue: [GitHub Issues](https://github.com/jpoley/jp-spec-kit/issues)
- Check documentation: `docs/guides/`
- Run `specify constitution validate --help`

**Contributing:**
- See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines
- Constitution templates are in `templates/constitutions/`
- All commits require DCO sign-off: `git commit -s`
