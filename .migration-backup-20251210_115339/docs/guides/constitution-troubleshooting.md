# Constitution Troubleshooting Guide

Comprehensive troubleshooting for common issues with Constitution distribution, validation, and enforcement in jp-spec-kit.

## Table of Contents

- [LLM Detection Issues](#llm-detection-issues)
- [Validation Issues](#validation-issues)
- [Command Enforcement Issues](#command-enforcement-issues)
- [Upgrade and Migration Issues](#upgrade-and-migration-issues)
- [Tier Selection Issues](#tier-selection-issues)
- [Integration Issues](#integration-issues)

---

## LLM Detection Issues

### Problem: LLM detected wrong languages or frameworks

**Symptoms**:
- Constitution contains incorrect language entries
- Missing languages that are clearly present in codebase
- Framework detection inaccurate (e.g., JavaScript instead of TypeScript)

**Example:**
```markdown
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
- Python 3.11
- JavaScript  ← Should be TypeScript
```

**Cause**:
LLM-based detection analyzes file patterns and package.json/requirements.txt but may:
- Misidentify languages based on limited file scanning
- Miss languages in subdirectories
- Confuse similar languages (JavaScript vs TypeScript)
- Detect build/test dependencies as primary languages

**Resolution**:

1. **Review detected languages carefully:**
   ```bash
   # View constitution
   cat memory/constitution.md | grep -A 10 "Technology Stack"
   ```

2. **Verify against codebase:**
   ```bash
   # Count files by language
   find . -type f -name "*.py" | wc -l    # Python files
   find . -type f -name "*.ts" | wc -l    # TypeScript files
   find . -type f -name "*.go" | wc -l    # Go files

   # Check package managers
   ls package.json pyproject.toml go.mod Cargo.toml 2>/dev/null
   ```

3. **Edit constitution manually:**
   ```bash
   nvim memory/constitution.md
   ```

4. **Correct the languages section:**
   ```markdown
   ## Technology Stack

   ### Primary Languages
   - **Python 3.11+**: FastAPI, pytest, SQLAlchemy
   - **TypeScript 5**: React 18, Next.js 14
   - **Go 1.22+**: CLI tools, system utilities

   ### Supporting Languages
   - **Shell**: Build scripts, automation
   - **SQL**: Database schemas and migrations
   ```

5. **Remove NEEDS_VALIDATION marker** after corrections

6. **Validate changes:**
   ```bash
   specify constitution validate
   # Should show: ✓ Constitution fully validated
   ```

**Prevention**:
- Always review LLM-generated content before removing NEEDS_VALIDATION markers
- Keep package manager files (package.json, pyproject.toml) up to date
- Document language choices in constitution comments

---

### Problem: Linting tools incorrectly detected

**Symptoms**:
- Constitution lists tools not used in project
- Missing actual linting tools in use
- Conflicting tool configurations (e.g., eslint + tslint)

**Example:**
```markdown
## Linting & Formatting
<!-- NEEDS_VALIDATION: Linting tools in use -->
- eslint
- prettier
- pylint  ← Project uses ruff, not pylint
```

**Cause**:
- LLM detected tools from devDependencies but not actual usage
- Legacy tools in package.json not cleaned up
- Configuration files for unused tools still present

**Resolution**:

1. **Check actual linting configuration:**
   ```bash
   # Check which linters are configured
   ls .eslintrc* .prettierrc* ruff.toml pyproject.toml 2>/dev/null

   # Check package.json scripts
   jq '.scripts | with_entries(select(.key | contains("lint")))' package.json

   # Check Python tools
   cat pyproject.toml | grep -A 5 "\[tool.ruff\]"
   ```

2. **Update constitution with actual tools:**
   ```markdown
   ## Linting & Formatting

   ### Python
   - **ruff**: Linting and formatting (replaces black, isort, flake8)
   - Configuration: `pyproject.toml`
   - CI: Runs on all PRs

   ### TypeScript
   - **eslint**: Linting (with TypeScript plugin)
   - **prettier**: Code formatting
   - Configuration: `.eslintrc.js`, `.prettierrc`
   - CI: Runs on all PRs
   ```

3. **Remove NEEDS_VALIDATION marker**

4. **Validate:**
   ```bash
   specify constitution validate
   ```

**Prevention**:
- Keep devDependencies clean (remove unused tools)
- Document tool choices in constitution
- Run `/speckit:constitution` after major tool changes

---

## Validation Issues

### Problem: NEEDS_VALIDATION markers stuck on sections that cannot be populated yet

**Symptoms**:
- Constitution validation fails
- Section exists but content is genuinely unknown (e.g., compliance requirements)
- Cannot start `/jpspec` work (Heavy tier)

**Example:**
```markdown
<!-- NEEDS_VALIDATION: Compliance frameworks applicable to project -->
[COMPLIANCE_FRAMEWORKS]
```

**Cause**:
Constitution requires information not yet determined by team or business requirements.

**Resolution**:

**Option 1: Add placeholder content (Best practice):**

```markdown
## Compliance

This project currently has no compliance requirements.

**Status**: No compliance frameworks applicable as of 2025-12-04.

**Future considerations**:
- Will evaluate SOC 2 requirements if we acquire enterprise customers
- GDPR compliance if we expand to EU markets
- HIPAA if healthcare customers identified

**Review cadence**: Quarterly during security review

Last reviewed: 2025-12-04
Next review: 2026-03-04
```

Remove NEEDS_VALIDATION marker and validate:
```bash
specify constitution validate
# ✓ Constitution fully validated
```

**Option 2: Document as "To Be Determined" (Acceptable):**

```markdown
<!-- NEEDS_VALIDATION: Compliance frameworks - TBD after legal review Q1 2026 -->
## Compliance

**Status**: Pending legal review of applicable compliance frameworks.

**Action items**:
- [ ] Schedule legal consultation (Q1 2026)
- [ ] Review customer compliance requirements
- [ ] Determine applicable frameworks

**Assigned to**: @security-lead
**Due date**: 2026-02-01
```

Leave marker in place with clear documentation. For Light/Medium tiers, this allows work to continue.

**Option 3: Request temporary skip (Heavy tier emergency):**

If Heavy tier blocks work and validation cannot be completed:

```bash
# Document reason in team chat/issue tracker
/jpspec:specify --skip-validation

# Create task to resolve
backlog task create "Validate compliance section in constitution" \
  --ac "Schedule legal review" \
  --ac "Document compliance requirements" \
  --ac "Remove NEEDS_VALIDATION marker" \
  -l documentation -p high
```

**Prevention**:
- Choose appropriate tier for project maturity
- Review constitution template before starting
- Document "TBD" sections clearly with owners and dates

---

### Problem: Cannot find NEEDS_VALIDATION markers that validation reports

**Symptoms**:
```bash
$ specify constitution validate
❌ Constitution has 1 unvalidated section:
  - Technology Stack (line 42)

$ grep -n "NEEDS_VALIDATION" memory/constitution.md
# No output
```

**Cause**:
- Marker may be in different format
- Hidden characters or encoding issues
- Marker in commented section

**Resolution**:

1. **Search with variations:**
   ```bash
   # Case-insensitive search
   grep -ni "needs.validation" memory/constitution.md

   # Show context
   grep -C 3 -i "validation" memory/constitution.md

   # Check for HTML comments
   grep -n "<!--.*-->" memory/constitution.md | head -20
   ```

2. **Go to reported line:**
   ```bash
   # View line 42 and surrounding context
   sed -n '40,45p' memory/constitution.md

   # Or use editor
   nvim +42 memory/constitution.md
   ```

3. **Check for hidden characters:**
   ```bash
   # Show all characters including hidden
   cat -A memory/constitution.md | grep -i validation
   ```

4. **If marker truly missing but validation fails:**
   ```bash
   # Re-validate with verbose output
   specify constitution validate --json | jq .

   # Check constitution format
   specify constitution validate --verbose
   ```

**If issue persists**:
```bash
# Backup current constitution
cp memory/constitution.md memory/constitution.md.backup

# Re-run LLM customization
/speckit:constitution

# Merge your custom content back
```

---

## Command Enforcement Issues

### Problem: /jpspec command blocked by unvalidated constitution (Heavy tier)

**Symptoms**:
```bash
$ /jpspec:specify
❌ Error: Constitution validation required.
Constitution has 1 unvalidated section:
  - Compliance frameworks (line 142)

Cannot proceed with /jpspec commands until validation complete.
```

**Cause**:
Heavy tier enforces hard blocks on /jpspec commands when constitution has unvalidated sections.

**Resolution**:

**Option 1: Validate the constitution (Recommended):**

```bash
# 1. Check what needs validation
specify constitution validate

# Example output:
# ❌ Constitution has 2 unvalidated sections:
#   - Compliance frameworks (line 142)
#   - Security scanning tools (line 203)

# 2. Edit constitution
nvim memory/constitution.md

# 3. Navigate to line 142, 203
# Add content or placeholder (see "NEEDS_VALIDATION markers stuck" above)

# 4. Verify validation passes
specify constitution validate
# ✓ Constitution fully validated

# 5. Now run /jpspec command
/jpspec:specify
```

**Option 2: Emergency skip (Document justification):**

```bash
# Document in team chat, issue tracker, or commit message WHY you're skipping
/jpspec:specify --skip-validation

# Create follow-up task
backlog task create "Complete constitution validation" \
  --ac "Validate compliance section" \
  --ac "Remove --skip-validation usage" \
  -l documentation -p high
```

**Option 3: Downgrade tier temporarily:**

```bash
# If Heavy tier is too strict for current project phase
cp memory/constitution.md memory/constitution.md.heavy-backup
cp templates/constitutions/constitution-medium.md memory/constitution.md

# Merge your custom sections
nvim memory/constitution.md

# Validate
specify constitution validate

# Document tier change
git add memory/constitution.md
git commit -s -m "chore: temporarily downgrade to medium tier

Heavy tier blocking work during early development phase.
Will upgrade back to heavy tier before production release.

Ref: task-123"
```

**Prevention**:
- Choose appropriate tier for project phase
- Validate constitution before starting implementation sprints
- Schedule constitution review as part of sprint planning

---

### Problem: /jpspec command warns but doesn't block (Medium tier) - unclear if safe to proceed

**Symptoms**:
```bash
$ /jpspec:implement
⚠️  Warning: Constitution has 1 unvalidated section:
  - Security scanning tools (line 203)

Proceed anyway? (y/n):
```

**Cause**:
Medium tier uses warnings + confirmation prompts but allows proceeding after acknowledgment.

**Resolution**:

**Decision tree:**

1. **Is the unvalidated section relevant to current work?**

   **No** → Safe to proceed:
   ```bash
   # Example: Implementing frontend feature, compliance section unvalidated
   y  # Proceed

   # Create task to validate later
   backlog task create "Validate compliance section" -l documentation
   ```

   **Yes** → Validate first:
   ```bash
   n  # Don't proceed

   # Validate relevant section
   nvim memory/constitution.md  # Fix security scanning section
   specify constitution validate

   # Now proceed
   /jpspec:implement
   ```

2. **Is this a one-time occurrence or recurring?**

   **One-time** → Proceed and fix later:
   ```bash
   y  # Proceed

   # Document in commit message
   git commit -s -m "feat: implement feature X

   Note: Proceeded with unvalidated constitution section.
   Will validate security scanning section in follow-up.
   Ref: task-456"
   ```

   **Recurring** → Fix root cause:
   ```bash
   # Complete validation to stop warnings
   specify constitution validate
   nvim memory/constitution.md
   specify constitution validate  # Until passes
   ```

**Best practice**:
- Treat Medium tier warnings as "should fix soon" not "ignore forever"
- Track unvalidated sections as technical debt
- Schedule constitution review every sprint or monthly

---

## Upgrade and Migration Issues

### Problem: Constitution version mismatch after `specify upgrade`

**Symptoms**:
- Upgraded JP Spec Kit to new version
- Constitution feels outdated compared to new templates
- New features reference constitution sections that don't exist

**Cause**:
JP Spec Kit upgraded but constitution template not updated. Constitutions are never automatically overwritten to preserve customizations.

**Resolution**:

**Step 1: Identify version mismatch:**

```bash
# Check your constitution version
grep -i "version" memory/constitution.md | head -3

# Example output:
# **Version**: 1.0.0 | **Ratified**: 2025-01-15

# Check latest template version
cat templates/constitutions/constitution-medium.md | grep -i "Template Version"

# Example output:
# Template Version: 2.1.0
```

**Step 2: Compare your constitution with latest template:**

```bash
# Backup current constitution
cp memory/constitution.md memory/constitution.md.backup

# View differences (requires diff tool)
diff -u memory/constitution.md templates/constitutions/constitution-medium.md > constitution.diff

# Review differences
less constitution.diff
```

**Step 3: Manually merge improvements:**

```bash
# Option 1: Edit in place
nvim memory/constitution.md

# Option 2: Side-by-side editing
nvim -O memory/constitution.md templates/constitutions/constitution-medium.md
```

**Step 4: Update version and validate:**

```markdown
**Version**: 2.0.0 | **Last Amended**: 2025-12-04

### Change Log

#### 2.0.0 (2025-12-04)
- Upgraded from constitution template 1.0.0 to 2.1.0
- Added security scanning section
- Updated git workflow best practices
- Improved task quality guidelines
```

```bash
# Validate merged constitution
specify constitution validate

# Commit update
git add memory/constitution.md
git commit -s -m "chore: upgrade constitution to template v2.1.0

Merged improvements from latest template while preserving
team-specific customizations.

Changes:
- Added security scanning requirements
- Updated git workflow section
- Improved task quality standards

Version: 1.0.0 → 2.0.0

Signed-off-by: Your Name <you@example.com>"
```

**Future feature** (not yet available):
```bash
# Automated constitution upgrade (planned)
specify constitution check-updates
specify constitution upgrade --interactive
```

**Prevention**:
- Review release notes when upgrading JP Spec Kit
- Schedule quarterly constitution review
- Track constitution template versions in your project docs

---

### Problem: Lost custom amendments during constitution refresh

**Symptoms**:
- Accidentally overwrote constitution with template
- Custom team rules missing
- Lost compliance or security customizations

**Cause**:
Ran `specify init --here` or manually copied template over existing constitution without merging.

**Resolution**:

**Step 1: Check git history:**

```bash
# View constitution history
git log --oneline -- memory/constitution.md

# View previous version
git show HEAD~1:memory/constitution.md > constitution.previous

# Or specific commit
git show abc123:memory/constitution.md > constitution.previous

# Compare
diff -u constitution.previous memory/constitution.md
```

**Step 2: Restore lost sections:**

```bash
# Extract lost sections
# (Identify custom amendments in constitution.previous)

# Edit current constitution
nvim memory/constitution.md

# Copy custom sections from constitution.previous
# Merge with new template content
```

**Step 3: Validate and commit:**

```bash
# Validate merged constitution
specify constitution validate

# Commit restoration
git add memory/constitution.md
git commit -s -m "fix: restore custom constitution amendments

Restored team-specific rules that were lost during template refresh:
- Custom compliance requirements
- Team-specific git workflow
- Security scanning tools configuration

Signed-off-by: Your Name <you@example.com>"
```

**Prevention**:
- **ALWAYS backup** before modifying constitution: `cp memory/constitution.md memory/constitution.md.backup`
- Use git to track all constitution changes
- Review diffs before committing constitution updates
- Never run `specify init --here` in existing project without backup

---

## Tier Selection Issues

### Problem: Heavy tier too strict, Light tier too permissive

**Symptoms**:
- Heavy tier: Constant validation errors blocking work
- Light tier: No enforcement, team not following practices
- Team frustrated with chosen tier

**Cause**:
Tier selection doesn't match project phase or team culture.

**Resolution**:

**Assess current situation:**

| Indicator | Light Tier | Medium Tier | Heavy Tier |
|-----------|------------|-------------|------------|
| Team size | 1-2 | 3-10 | 10+ |
| Project phase | MVP/prototype | Active development | Production |
| Compliance needs | None | Business | Regulated |
| PR review | Optional | 1 reviewer | 2+ reviewers |
| CI/CD | Basic | Standard | Strict |

**If Heavy is too strict:**

```bash
# Backup Heavy tier constitution
cp memory/constitution.md memory/constitution.md.heavy

# Try Medium tier
cp templates/constitutions/constitution-medium.md memory/constitution.md

# Merge your custom sections
nvim memory/constitution.md

# Validate
specify constitution validate

# Trial period: Use for 2-4 weeks
# Team retrospective: Gather feedback
# Decision: Keep Medium or return to Heavy with adjustments
```

**If Light is too permissive:**

```bash
# Upgrade to Medium tier
cp memory/constitution.md memory/constitution.md.light
cp templates/constitutions/constitution-medium.md memory/constitution.md

# Merge custom sections
nvim memory/constitution.md

# Validate
specify constitution validate

# Document decision
git commit -s -m "chore: upgrade from light to medium tier

Team consensus to adopt more structured workflow:
- Growing team size (now 4 developers)
- Multiple customer deployments
- Need for code review process

Version: 1.0.0 → 2.0.0

Signed-off-by: Your Name <you@example.com>"
```

**If team disagrees on tier:**

1. **Start with Medium** (middle ground)
2. **Trial period** (2-4 weeks)
3. **Retrospective** (gather data on friction vs. value)
4. **Vote** (decide to upgrade or downgrade)
5. **Document decision** (commit message with justification)

**Prevention**:
- Match tier to actual needs, not aspirations
- Review tier choice quarterly
- Be willing to adjust based on team feedback

---

### Problem: Monorepo with multiple languages - constitution is cluttered

**Symptoms**:
- Constitution lists 5-10 languages
- Hard to understand primary vs. supporting languages
- LLM detected every language in subdirectories

**Cause**:
Monorepo structure with multiple projects or services, each with different languages.

**Resolution**:

**Organize by importance:**

```markdown
## Technology Stack

### Primary Languages
Languages used for core application logic and customer-facing features.

- **Python 3.11+**: Backend API services
  - FastAPI (REST API framework)
  - SQLAlchemy (ORM)
  - pytest (testing)
  - ruff (linting/formatting)

- **TypeScript 5**: Frontend applications
  - React 18, Next.js 14 (UI frameworks)
  - Jest, Testing Library (testing)
  - eslint, prettier (linting/formatting)

### Supporting Languages
Languages for tooling, infrastructure, and build systems.

- **Go 1.22+**: CLI tools, system utilities
- **Shell**: Build scripts, CI/CD automation
- **SQL**: Database schemas, migrations
- **HCL**: Terraform infrastructure definitions

### Deprecated/Legacy
Languages being phased out (no new code).

- **JavaScript**: Legacy frontend (migrating to TypeScript)
- **Python 2.7**: Legacy scripts (migrating to Python 3.11+)
```

**Alternative: Per-service constitutions** (advanced):

```markdown
## Technology Stack

This monorepo contains multiple services with different tech stacks:

- **Backend services**: See `services/backend/constitution.md`
- **Frontend applications**: See `services/frontend/constitution.md`
- **CLI tools**: See `tools/constitution.md`

**Shared standards** (apply to all services):
- Git workflow: Feature branches, PR required
- Testing: 70% coverage minimum
- Security: No secrets in code, dependency scanning
```

---

## Integration Issues

### Problem: Constitution not enforced in CI/CD pipeline

**Symptoms**:
- Constitution exists but CI doesn't check it
- PRs merged without constitution compliance
- `/jpspec` commands enforce locally but not in CI

**Cause**:
CI/CD pipeline not configured to validate constitution or check compliance.

**Resolution**:

**Add constitution validation to CI:**

```yaml
# .github/workflows/ci.yml
name: CI

on: [pull_request, push]

jobs:
  validate-constitution:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install JP Spec Kit
        run: |
          pip install uv
          uv tool install jp-spec-kit

      - name: Validate constitution
        run: |
          specify constitution validate

      - name: Check for unvalidated sections
        if: failure()
        run: |
          echo "❌ Constitution has unvalidated sections"
          echo "Run: specify constitution validate"
          echo "Fix issues before merging PR"
          exit 1
```

**Add constitution compliance checks:**

```yaml
# .github/workflows/constitution-compliance.yml
name: Constitution Compliance

on: [pull_request]

jobs:
  check-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check PR has linked task
        run: |
          # Extract task number from PR title or branch
          # Verify task exists in backlog.md
          # (Implementation depends on constitution PR requirements)
```

**Prevention**:
- Add constitution validation to CI early in project
- Include compliance checks in PR template
- Document CI requirements in constitution

---

### Problem: `/speckit:constitution` command not available in Claude

**Symptoms**:
- Typing `/speckit:constitution` does nothing
- Command not in slash command menu
- LLM doesn't customize constitution

**Cause**:
- Slash commands not loaded in Claude environment
- Template files missing
- `.claude/commands/` directory not present

**Resolution**:

**Step 1: Verify project initialization:**

```bash
# Check for .claude directory
ls -la .claude/

# Should contain:
# .claude/commands/
# .claude/commands/speckit/constitution.md

# If missing, initialize:
specify init --here
```

**Step 2: Verify template availability:**

```bash
# Check constitution command template exists
cat .claude/commands/speckit/constitution.md

# Should show slash command implementation
```

**Step 3: Reload Claude environment:**

```bash
# Restart Claude Code session
# Or open new terminal in project directory
```

**Step 4: If still not working:**

```bash
# Manually create command from template
mkdir -p .claude/commands/speckit
cp templates/commands/speckit/constitution.md .claude/commands/speckit/

# Verify
ls -la .claude/commands/speckit/
cat .claude/commands/speckit/constitution.md
```

**Alternative: Manual LLM customization:**

If `/speckit:constitution` unavailable, manually ask LLM:

```
Please analyze my project and customize memory/constitution.md:

1. Scan codebase for languages/frameworks
2. Identify linting tools from package.json/pyproject.toml
3. Update Technology Stack section
4. Update Linting & Formatting section
5. Remove NEEDS_VALIDATION markers after populating
6. Preserve existing custom amendments
```

---

## Best Practices

### Do:
- ✅ Always review LLM-generated content before removing NEEDS_VALIDATION markers
- ✅ Backup constitution before major changes: `cp memory/constitution.md memory/constitution.md.backup`
- ✅ Validate after every constitution edit: `specify constitution validate`
- ✅ Track constitution changes in git with descriptive commit messages
- ✅ Choose tier based on actual team size and project phase, not aspirations
- ✅ Document "TBD" sections with clear owners and review dates
- ✅ Review constitution quarterly or after team/compliance changes

### Don't:
- ❌ Blindly accept LLM language detection without verification
- ❌ Remove NEEDS_VALIDATION markers without adding content or placeholders
- ❌ Use `--skip-validation` without documenting justification
- ❌ Choose Heavy tier "just to be safe" (creates unnecessary friction)
- ❌ Overwrite constitution without backing up custom amendments
- ❌ Ignore warnings from `/jpspec` commands (treat as technical debt)
- ❌ Leave unvalidated sections indefinitely (schedule resolution)

---

## Related Documentation

- [Constitution Distribution User Guide](./constitution-distribution.md) - Complete feature guide
- [Constitution Validation Workflow](./constitution-validation.md) - Validation process details
- [Constitution Distribution PRD](../prd/constitution-distribution-prd.md) - Feature specification
- [Tiered Constitution Templates](../../templates/constitutions/) - Template source files
- [JP Spec Kit CLI Reference](../reference/cli-commands.md) - All CLI commands

---

## Quick Reference

### Common Commands

```bash
# Validation
specify constitution validate              # Check validation status
specify constitution validate --json       # JSON output for scripts
specify constitution validate --verbose    # Detailed output

# Project setup
specify init my-project --constitution medium   # New project with tier
specify init --here                             # Add to existing project

# LLM customization
/speckit:constitution                           # Run LLM detection

# Upgrade
specify upgrade                                 # Upgrade JP Spec Kit

# Search for issues
grep -i "NEEDS_VALIDATION" memory/constitution.md   # Find markers
grep -n "NEEDS_VALIDATION" memory/constitution.md   # With line numbers
```

### Files and Directories

```
memory/constitution.md                  # Your project's constitution
templates/constitutions/                # Template source files
  ├── constitution-light.md
  ├── constitution-medium.md
  └── constitution-heavy.md
.claude/commands/speckit/constitution.md # /speckit:constitution command
```

### Exit Codes

- `0` - Constitution fully validated (success)
- `1` - Unvalidated sections exist (needs action)
- `2` - File not found or critical error

---

## Getting Help

**Still having issues?**

1. **Check verbose output:**
   ```bash
   specify constitution validate --verbose
   ```

2. **Review related guides:**
   - [Constitution Distribution Guide](./constitution-distribution.md)
   - [JP Spec Kit Troubleshooting](./troubleshooting.md)
   - [Backlog Troubleshooting](./backlog-troubleshooting.md)

3. **Search existing issues:**
   ```bash
   # GitHub CLI
   gh issue list --search "constitution"
   ```

4. **Open a new issue:**
   ```bash
   gh issue create --title "Constitution issue: [brief description]" \
                    --body "**Problem**: ...\n**Steps to reproduce**: ...\n**Expected**: ...\n**Actual**: ..."
   ```

5. **Check CLI help:**
   ```bash
   specify constitution --help
   specify constitution validate --help
   ```

**Contributing:**
- See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines
- Constitution templates are in `templates/constitutions/`
- All commits require DCO sign-off: `git commit -s`

---

*Last updated: 2025-12-04*
