# Constitution Troubleshooting Guide

Comprehensive troubleshooting for common issues with JP Spec Kit constitution system.

## Table of Contents

- [LLM Detection Issues](#llm-detection-issues)
- [Validation Issues](#validation-issues)
- [Command Enforcement Issues](#command-enforcement-issues)
- [Version and Upgrade Issues](#version-and-upgrade-issues)
- [Customization Issues](#customization-issues)
- [Tier Selection Issues](#tier-selection-issues)
- [Getting Help](#getting-help)

## LLM Detection Issues

### Problem: LLM Detected Incorrect Primary Language

**Symptoms**:
- Wrong language listed as primary in constitution
- Framework/tools misidentified
- Missing a language that's clearly present in repository

**Example**:
```markdown
## Technology Stack

<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
- JavaScript  ← Should be TypeScript
- PHP         ← Project doesn't use PHP
```

**Causes**:
1. Unusual file structure confusing detection heuristics
2. Non-standard configuration files (e.g., `tsconfig.json` in subdirectory)
3. Mixed-language monorepo with unclear primary language
4. Legacy code in repo that's not actively maintained

**Solutions**:

**Solution 1: Manually correct the constitution**
```bash
# Edit constitution
nvim memory/constitution.md

# Correct the technology stack section:
```
```markdown
## Technology Stack

### Primary Languages
- **Python 3.11+**: Backend services (FastAPI, pytest)
- **TypeScript 5**: Frontend (React, Next.js)

### Supporting Languages
- **Shell**: Build scripts and automation
```
```bash
# Remove NEEDS_VALIDATION marker
# Validate
specify constitution validate
```

**Solution 2: Provide hints to LLM during `/speckit:constitution`**

Before running the command, create a hint file:
```bash
# Create hints file
cat > .constitution-hints.md <<EOF
Primary languages:
- TypeScript (not JavaScript) - see tsconfig.json
- Python 3.11+ with FastAPI

Frameworks:
- React 18 for frontend
- FastAPI for backend
- pytest for testing

Ignore:
- /legacy/php/ directory (deprecated)
EOF

# Run LLM command with hints
/speckit:constitution
# Reference the hints file in your prompt
```

**Solution 3: Check repo structure**

Verify your repo structure is conventional:
```bash
# Check for standard config files
ls -la | grep -E "package.json|tsconfig.json|requirements.txt|go.mod"

# Move config files to root if buried
mv src/frontend/tsconfig.json ./tsconfig.json
mv src/backend/requirements.txt ./requirements.txt

# Re-run LLM detection
/speckit:constitution
```

---

### Problem: Multiple Languages in Monorepo Creates Cluttered Constitution

**Symptoms**:
- Constitution lists 5+ languages
- Unclear which are primary vs. supporting
- Testing/linting sections become unwieldy

**Causes**:
1. True monorepo with many equal-weight services
2. Supporting tools (build scripts, infra code) detected as primary
3. Frontend + backend + CLI + infra = many languages

**Solutions**:

**Solution 1: Organize by primary vs. supporting**
```markdown
## Technology Stack

### Primary Languages
- **Python 3.11+**: Backend services
  - FastAPI, SQLAlchemy, pytest
- **TypeScript 5**: Frontend applications
  - React, Next.js, Vitest

### Supporting Languages
- **Go 1.22+**: CLI tools
- **Shell**: Build automation and scripts
- **HCL**: Terraform infrastructure

### Development Tools
- Docker for local environments
- GitHub Actions for CI/CD
```

**Solution 2: Split into sub-project constitutions (advanced)**

For very large monorepos:
```bash
# Create sub-constitutions
mkdir -p backend/memory
mkdir -p frontend/memory

cp memory/constitution.md backend/memory/constitution.md
cp memory/constitution.md frontend/memory/constitution.md

# Edit each to focus on that sub-project
nvim backend/memory/constitution.md   # Focus on Python
nvim frontend/memory/constitution.md  # Focus on TypeScript

# Root constitution references sub-constitutions
echo "See sub-project constitutions in backend/ and frontend/" >> memory/constitution.md
```

**Solution 3: Use N/A for irrelevant sections**
```markdown
## Technology Stack

### Backend (Python)
- Python 3.11+: FastAPI, pytest
- Linting: ruff, mypy

### Frontend (TypeScript)
- TypeScript 5: React, Next.js
- Linting: eslint, prettier

### Build Tools (Go)
- Go 1.22+: CLI tooling only
- Testing: Standard `go test`
- Linting: golangci-lint

**Note**: Each language has independent test/lint configurations.
```

---

## Validation Issues

### Problem: NEEDS_VALIDATION Marker Stuck - Don't Know What Value to Use

**Symptoms**:
- Can't decide on coverage percentage
- Unsure about SLA targets
- Don't know compliance frameworks yet

**Example**:
```markdown
<!-- NEEDS_VALIDATION: Define test coverage target -->
**Test Coverage**: [COVERAGE_TARGET]%

<!-- NEEDS_VALIDATION: Define critical bug SLA -->
**Critical Bug SLA**: [DAYS] days
```

**Causes**:
1. Value requires team decision
2. Unfamiliar with industry best practices
3. Project too early to commit to specific numbers

**Solutions**:

**Solution 1: Use industry standard defaults**

Common defaults you can safely use:
```markdown
## Quality Standards

**Test Coverage**: 70% (unit + integration)
  - Increase to 80% for critical business logic
  - 60% acceptable for prototypes

**Code Review**: Minimum 1 reviewer
  - 2 reviewers for security-sensitive code

**Critical Bug SLA**: 7 days
  - P0 (outage): 24 hours
  - P1 (critical): 7 days
  - P2 (major): 30 days

**Security Vulnerabilities**:
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days
```

**Solution 2: Use "TBD" with timeline**
```markdown
<!-- Coverage target TBD after Q1 2025 -->
**Test Coverage**: To be determined after baseline measurement
  - Will be set in Q1 2025 based on current coverage
  - Target: Establish baseline, then improve 10% per quarter
```

**Solution 3: Make it explicit that you're starting loose**
```markdown
## Quality Standards (Bootstrap Phase)

**Note**: This project is in bootstrap phase (Light tier).
Quality standards will be formalized as the team and codebase mature.

**Test Coverage**: Tests for critical paths only
  - No coverage target during bootstrap
  - Will establish target at 1.0.0 release

**Code Review**: Optional during rapid iteration
  - Required once we have multiple active contributors
```

---

### Problem: Can't Remove NEEDS_VALIDATION - Section Not Applicable

**Symptoms**:
- Constitution template has section you don't need
- Example: Compliance section, but no compliance requirements
- Example: Security scanning, but solo project

**Causes**:
1. Template designed for enterprise use, you're a solo dev
2. Heavy tier template, but you need Medium tier features
3. Future requirement, not current requirement

**Solutions**:

**Solution 1: Replace with N/A statement**
```markdown
## Compliance

This project has no compliance requirements.

**Applicable Frameworks**: None

If compliance requirements emerge in the future, this section will be updated with:
- Framework names (SOC 2, HIPAA, etc.)
- Required controls
- Audit schedules
```

**Solution 2: Use "Not Applicable" heading**
```markdown
## Security Scanning

**Status**: Not applicable (solo project, no external users)

Security scanning will be enabled when:
- Project accepts external contributions
- Application is deployed to production
- Sensitive data is processed

**Revisit**: When project reaches alpha release
```

**Solution 3: Remove the entire section**

If truly not needed:
```bash
nvim memory/constitution.md

# Delete the entire section
# dd (in vim) to delete lines

# Ensure you're not breaking document structure
# Check that remaining sections still make sense

# Validate
specify constitution validate
```

**Note**: Document *why* you removed it in commit message:
```bash
git commit -s -m "chore: remove compliance section from constitution

Compliance section not applicable to this project:
- Solo developer
- Open source hobby project
- No regulatory requirements

Will add back if project commercializes.

Signed-off-by: Your Name <you@example.com>"
```

---

### Problem: specify constitution validate Returns Non-Zero Exit Code

**Symptoms**:
```bash
specify constitution validate
echo $?
# Output: 1
```

**Causes**:
1. Unvalidated sections still exist (expected behavior)
2. Constitution file has syntax errors
3. File not found at expected location

**Solutions**:

**Solution 1: Check validation output**
```bash
# See which markers remain
specify constitution validate

# Example output:
# ❌ Constitution has unvalidated sections:
#   - Line 52: Technology Stack
#   - Line 104: Version and dates
```

Fix the identified sections, then re-run.

**Solution 2: Check file exists**
```bash
# Verify file location
ls -la memory/constitution.md

# If not found, check alternate locations
ls -la .specify/constitution.md
ls -la constitution.md

# Create if missing
specify init --here
```

**Solution 3: Validate syntax manually**
```bash
# Check for common Markdown issues
grep -n "NEEDS_VALIDATION" memory/constitution.md

# Verify marker format is correct
# Correct: <!-- NEEDS_VALIDATION: Description -->
# Incorrect: <!-- NEEDS_VALIDATION Description -->
# Incorrect: <!-- VALIDATE: Description -->
```

**Solution 4: Use JSON output for debugging**
```bash
# Get detailed JSON output
specify constitution validate --json | jq .

# Example:
# {
#   "valid": false,
#   "unvalidated_sections": [
#     {
#       "line": 52,
#       "description": "Technology Stack"
#     }
#   ]
# }
```

---

## Command Enforcement Issues

### Problem: /jpspec Command Blocked by Unvalidated Constitution (Heavy Tier)

**Symptoms**:
```
❌ Error: Constitution validation required.

Constitution has 2 unvalidated sections:
  - Technology Stack (line 52)
  - Version and dates (line 104)

Please run 'specify constitution validate' and resolve all markers before proceeding.

Use '--skip-validation' to override (NOT RECOMMENDED for compliance environments).
```

**Causes**:
1. Heavy tier enforces hard blocks on unvalidated constitutions
2. Constitution was not validated after initial creation
3. New NEEDS_VALIDATION markers added during updates

**Solutions**:

**Solution 1: Validate the constitution (recommended)**
```bash
# 1. Check what needs validation
specify constitution validate

# 2. Edit and fix each section
nvim memory/constitution.md

# 3. Verify all clear
specify constitution validate
# ✅ Constitution validated

# 4. Now /jpspec commands will work
/jpspec:specify
```

**Solution 2: Emergency override with --skip-validation**
```bash
# Use ONLY for emergencies (hotfixes, blockers)
/jpspec:specify --skip-validation

⚠ WARNING: Skipping constitution validation. NOT recommended for production.

# Document why you skipped validation
# In team chat, issue tracker, or commit message
```

**Solution 3: Temporarily downgrade to Medium tier**

If you need to move fast but Heavy tier is blocking:
```bash
# 1. Backup current constitution
cp memory/constitution.md memory/constitution.md.heavy

# 2. Change tier comment at top
nvim memory/constitution.md
# Change: <!-- CONSTITUTION_TIER: heavy -->
# To:     <!-- CONSTITUTION_TIER: medium -->

# 3. Now commands prompt instead of block
/jpspec:specify
# Do you want to proceed anyway? [y/N]: y

# 4. Restore Heavy tier after emergency
cp memory/constitution.md.heavy memory/constitution.md
```

**Solution 4: Use Light tier for prototyping**

If you're in early-stage prototyping:
```bash
# Re-initialize with Light tier
mv memory/constitution.md memory/constitution.md.heavy
specify init --here --constitution light

# Light tier: warnings only, no blocks
/jpspec:specify
# ⚠ Warning: Constitution has 2 unvalidated sections.
# Proceeding with /jpspec:specify...

# Restore Heavy tier when ready for production
```

---

### Problem: Medium Tier Prompts Are Annoying During Development

**Symptoms**:
- Every `/jpspec` command prompts: "Do you want to proceed anyway? [y/N]"
- Slows down development flow
- Confirmation prompt after every validation warning

**Causes**:
1. Medium tier is designed for team discipline
2. Constitution has unvalidated sections
3. Tier selection doesn't match development phase

**Solutions**:

**Solution 1: Validate the constitution once**
```bash
# Just fix it once, then no more prompts
specify constitution validate
nvim memory/constitution.md
# Fix all NEEDS_VALIDATION markers
specify constitution validate
# ✅ Constitution validated

# No more prompts!
/jpspec:specify
# Proceeding with /jpspec:specify...
```

**Solution 2: Use Light tier during active development**
```bash
# Temporarily use Light tier
nvim memory/constitution.md
# Change: <!-- CONSTITUTION_TIER: medium -->
# To:     <!-- CONSTITUTION_TIER: light -->

# Or use downgrade command (future feature)
specify constitution downgrade --tier light

# Before PR, upgrade back to Medium
specify constitution upgrade --tier medium
```

**Solution 3: Add a development mode alias**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias jpspec-dev='JPSPEC_SKIP_VALIDATION=1 jpspec'

# Use during development
jpspec-dev specify
# No prompts

# Use normal command for production work
/jpspec:specify
# Full validation enforced
```

---

## Version and Upgrade Issues

### Problem: Constitution Version Mismatch After JP Spec Kit Upgrade

**Symptoms**:
- After `uv tool install . --force`, constitution feels outdated
- Warning messages mention "constitution template 2.0 available (you have 1.0)"
- New features reference sections not in your constitution

**Causes**:
1. JP Spec Kit updated constitution templates
2. Your project's constitution wasn't updated
3. Template has new sections (e.g., security scanning)

**Solutions**:

**Solution 1: Check for template differences**
```bash
# Compare your constitution to latest template
diff memory/constitution.md templates/constitutions/constitution-medium.md

# Or use git diff if templates are committed
git diff HEAD templates/constitutions/constitution-medium.md
```

**Solution 2: Manual upgrade**
```bash
# 1. Backup current constitution
cp memory/constitution.md memory/constitution.md.backup.$(date +%Y%m%d)

# 2. View new template
cat templates/constitutions/constitution-medium.md

# 3. Identify new sections
# - Security scanning
# - Deployment process
# - Observability requirements

# 4. Copy relevant sections into your constitution
nvim memory/constitution.md
# Add new sections, preserving your customizations

# 5. Update version number
# Change: **Version**: 1.0.0
# To:     **Version**: 2.0.0

# 6. Add changelog entry
```
```markdown
### Change Log

#### 2.0.0 (2025-12-04)
- Upgraded to JP Spec Kit template 2.0
- Added security scanning requirements
- Added deployment process section
- Preserved custom git workflow amendments
```
```bash
# 7. Validate
specify constitution validate

# 8. Commit
git add memory/constitution.md
git commit -s -m "chore: upgrade constitution to template 2.0

Merged new sections from JP Spec Kit template 2.0:
- Security scanning requirements
- Deployment process guidelines
- Observability standards

Preserved all custom amendments from 1.0.0.

Version bumped to 2.0.0 (major change).

Signed-off-by: Your Name <you@example.com>"
```

**Solution 3: Use future upgrade command**

When implemented:
```bash
# Check for updates
specify constitution check-updates

# Output:
# Constitution template 2.0.0 available (you have 1.0.0)
# Changes:
# - Added security scanning section
# - Updated git workflow best practices

# Upgrade with merge
specify constitution upgrade --interactive

# Choose which new sections to add
# Preserves your custom amendments
# Outputs merged constitution for review
```

**Solution 4: Ignore upgrade if not needed**

If new template sections don't apply:
```bash
# Add note in constitution why you're not upgrading
nvim memory/constitution.md
```
```markdown
## Governance

**Version**: 1.0.0 | **Last Amended**: 2025-12-04
**Template Version**: 1.0.0 (not upgrading to 2.0 - see note)

**Note**: JP Spec Kit template 2.0 adds security scanning and deployment
sections. These are not applicable to this project (solo hobby project).
We will upgrade when project reaches production deployment.
```

---

### Problem: Don't Know My Constitution Version

**Symptoms**:
- Not sure which template version you started from
- Can't remember if you've upgraded
- No version number in constitution

**Causes**:
1. Old constitution without version tracking
2. Manually created constitution
3. Version section was deleted

**Solutions**:

**Solution 1: Check Git history**
```bash
# See when constitution was created
git log --oneline memory/constitution.md

# View first commit
git log --reverse memory/constitution.md | head -20

# Check specific commit
git show <commit-hash>:memory/constitution.md | grep -A 5 "Version"
```

**Solution 2: Add version tracking now**
```bash
nvim memory/constitution.md

# Add governance section at top
```
```markdown
# Development Constitution

**Tier**: Medium | **Version**: 1.0.0 | **Last Amended**: 2025-12-04

## Governance

### Version History

#### 1.0.0 (2025-12-04)
- Added version tracking (retroactive)
- Based on JP Spec Kit template (estimated 1.0.0)
- Custom amendments: [list your customizations]
```
```bash
# Commit
git commit -s -m "chore: add version tracking to constitution"
```

**Solution 3: Compare to known templates**
```bash
# Compare to Light tier
diff -u memory/constitution.md templates/constitutions/constitution-light.md | less

# Compare to Medium tier
diff -u memory/constitution.md templates/constitutions/constitution-medium.md | less

# Compare to Heavy tier
diff -u memory/constitution.md templates/constitutions/constitution-heavy.md | less

# Whichever has fewest differences is likely your base template
```

---

## Customization Issues

### Problem: Team Disagrees on Tier Selection

**Symptoms**:
- Some developers want Light tier (fast iteration)
- Others want Heavy tier (production-grade)
- Constant friction about process vs. velocity

**Causes**:
1. Different team members have different risk tolerances
2. Project phase (prototype vs. production) unclear
3. External requirements (compliance) not communicated

**Solutions**:

**Solution 1: Start with Medium tier (middle ground)**
```bash
# Initialize with Medium
specify init --here --constitution medium

# Trial period: 2-4 weeks
# Document decision
cat >> memory/DECISIONS.md <<EOF
## Constitution Tier Selection

**Date**: 2025-12-04
**Decision**: Medium tier (2-4 week trial)

**Rationale**:
- Team split on Light vs. Heavy
- Medium tier provides balance
- Will evaluate at end of trial period

**Success criteria for Heavy tier upgrade**:
- Team votes 75%+ in favor
- No more than 1 blocker incident per week
- Improved code quality metrics

**Success criteria for Light tier downgrade**:
- Medium tier blocking urgent work
- Team velocity down >20%
- No production incidents
EOF
```

**Solution 2: Use tier for specific workflows**
```bash
# Light tier during feature development
specify constitution downgrade --tier light

# Heavy tier for production releases
specify constitution upgrade --tier heavy

# Medium tier for regular work
specify constitution upgrade --tier medium
```

**Solution 3: Hold retrospective to decide**
```markdown
## Retrospective: Tier Selection

**Current Pain Points**:
- [ ] Process too heavy / slowing down development
- [ ] Not enough oversight / bugs slipping through
- [ ] Unclear when to follow rules
- [ ] Too many approval steps

**What's Working**:
- [ ] Quality standards
- [ ] Code review process
- [ ] Branch naming conventions

**Vote** (after 2-4 week trial):
- Light:  ___ votes (favor speed)
- Medium: ___ votes (balanced)
- Heavy:  ___ votes (favor quality)

**Decision**: [Record consensus]
**Next review**: [Date in 1-2 months]
```

**Solution 4: Split by project phase**
```bash
# Document in constitution
nvim memory/constitution.md
```
```markdown
## Tier Selection by Phase

This project uses different constitution tiers based on development phase:

| Phase | Tier | Rationale |
|-------|------|-----------|
| **Prototype** (v0.x) | Light | Fast iteration, solo dev |
| **Alpha** (v0.8-0.9) | Medium | Multiple contributors, users testing |
| **Beta** (v0.9-0.99) | Heavy | Pre-production, security review |
| **Production** (v1.0+) | Heavy | Customer data, SLAs, compliance |

**Current Phase**: Alpha (v0.8.0)
**Current Tier**: Medium
```

---

## Tier Selection Issues

### Problem: Chose Heavy Tier, Now Regretting It

**Symptoms**:
- Every `/jpspec` command blocked by minor issues
- Can't iterate quickly
- Team frustrated with process overhead

**Causes**:
1. Heavy tier too strict for current project phase
2. Team size doesn't match tier (solo dev with Heavy tier)
3. Chose Heavy "just to be safe" without understanding trade-offs

**Solutions**:

**Solution 1: Downgrade to Medium tier**
```bash
# 1. Backup Heavy tier constitution
cp memory/constitution.md memory/constitution.md.heavy

# 2. Replace with Medium tier template
cp templates/constitutions/constitution-medium.md memory/constitution.md

# 3. Port your custom sections from Heavy
nvim memory/constitution.md
# Copy technology stack, custom workflows, etc. from .heavy file

# 4. Update version
```
```markdown
**Version**: 2.0.0 | **Last Amended**: 2025-12-04

### Change Log

#### 2.0.0 (2025-12-04)
- **MAJOR CHANGE**: Downgraded from Heavy to Medium tier
- Rationale: Heavy tier causing development friction
- Team size (2 devs) doesn't require Heavy controls
- Will revisit when team grows to 5+ developers

#### 1.0.0 (2025-11-01)
- Initial Heavy tier adoption
```
```bash
# 5. Commit with clear rationale
git add memory/constitution.md
git commit -s -m "chore: downgrade constitution from heavy to medium tier

Heavy tier causing excessive friction:
- Blocking legitimate work with validation requirements
- Team size (2 devs) doesn't require heavy controls
- Project phase (alpha) needs faster iteration

Version bumped to 2.0.0 (major change).
Will revisit Heavy tier when:
- Team grows to 5+ developers
- Project reaches production
- Compliance requirements emerge

Signed-off-by: Your Name <you@example.com>"
```

**Solution 2: Use --skip-validation flag temporarily**
```bash
# While you work on downgrading, unblock current work
/jpspec:implement --skip-validation

# Document that this is temporary
echo "Using --skip-validation during Heavy→Medium transition" >> .notes
```

**Solution 3: Keep Heavy tier but adjust sections**
```bash
# Reduce strictness in specific areas
nvim memory/constitution.md
```
```markdown
## Code Review (Adjusted for Small Team)

**Minimum Reviewers**: 1 (reduced from 2)
  - 2 reviewers still required for:
    - Security-sensitive changes
    - Database migrations
    - CI/CD changes

**Review SLA**: 48 hours (relaxed from 24)
  - Allows for async work across timezones

**Self-merge allowed** (exception to Heavy tier):
  - For non-critical changes
  - After 48 hours with no reviewer response
  - Must document rationale in PR
```

---

### Problem: Light Tier Too Loose, Bugs Slipping Through

**Symptoms**:
- No code review catching bugs
- Tests not being written
- Production incidents increasing

**Causes**:
1. Light tier warnings ignored
2. Solo dev now has team members
3. Project reached production without tier upgrade

**Solutions**:

**Solution 1: Upgrade to Medium tier**
```bash
# 1. Backup Light tier
cp memory/constitution.md memory/constitution.md.light

# 2. Use Medium tier template
cp templates/constitutions/constitution-medium.md memory/constitution.md

# 3. Port customizations
nvim memory/constitution.md

# 4. Update version
```
```markdown
**Version**: 2.0.0 | **Last Amended**: 2025-12-04

### Change Log

#### 2.0.0 (2025-12-04)
- **MAJOR CHANGE**: Upgraded from Light to Medium tier
- Rationale: Production incidents increasing
- Now 3 team members (was solo dev)
- Added code review requirements
- Added test coverage targets

#### 1.0.0 (2025-09-01)
- Initial Light tier constitution
```

**Solution 2: Add specific controls while keeping Light tier**

If you want to stay Light but add structure:
```bash
nvim memory/constitution.md
```
```markdown
## Light Tier with Targeted Controls

This project uses Light tier as base, with selective controls:

### Exceptions (Enforced)
1. **Code Review**: Required for `main` branch
   - Branch protection enabled
   - Cannot be skipped

2. **Testing**: CI must pass before merge
   - Unit tests for new features
   - Coverage reported but not enforced

3. **Security**: Dependabot auto-merge disabled
   - Manual review of dependency updates
   - SAST scans in CI

### Kept from Light Tier
- Self-merge allowed (after review)
- No coverage targets
- Flexible branch naming
```

**Solution 3: Hold team meeting on quality standards**
```markdown
## Team Agreement: Quality Standards

**Date**: 2025-12-04
**Attendees**: [List team members]

**Pain Points**:
- Production bug last week (critical severity)
- 3 bugs found in PR review that should have been caught by tests
- Unclear when to ask for review

**New Standards** (Light tier + exceptions):
1. **MUST review**: All changes touching auth, database, payments
2. **MUST test**: All new API endpoints, critical business logic
3. **SHOULD review**: Everything else (but not blocked)

**Not Changing**:
- Keep Light tier (warnings only)
- Keep flexible git workflow
- Keep optional ACs

**Review**: 1 month from now (2025-01-04)
```

---

## Getting Help

### Check Existing Documentation

Before filing an issue:

1. **Constitution Distribution Guide**: [constitution-distribution.md](./constitution-distribution.md)
   - Full feature overview
   - Tier selection guidance
   - Validation workflow

2. **CLI Commands Reference**: [cli-commands.md](../reference/cli-commands.md)
   - All `specify constitution` commands
   - Exit codes and options

3. **Case Study**: [02-constitution-templates.md](../case-studies/02-constitution-templates.md)
   - Real-world implementation examples

### Enable Debug Output

```bash
# If available, enable verbose output
export SPECIFY_DEBUG=1
specify constitution validate

# Or use verbose flag
specify constitution validate --verbose

# Capture output for issue report
specify constitution validate --verbose > debug.txt 2>&1
```

### Common Issues Quick Reference

| Issue | Quick Fix | Details |
|-------|-----------|---------|
| Wrong language detected | Manually edit constitution | [LLM Detection Issues](#llm-detection-issues) |
| NEEDS_VALIDATION stuck | Use defaults or N/A | [Validation Issues](#validation-issues) |
| Heavy tier blocking | Validate or use --skip-validation | [Command Enforcement](#command-enforcement-issues) |
| Version mismatch | Manual upgrade or ignore | [Version Issues](#version-and-upgrade-issues) |
| Team disagrees on tier | Start with Medium, trial period | [Tier Selection](#tier-selection-issues) |

### Report Issues

If troubleshooting doesn't resolve your problem:

**1. Create minimal reproduction:**
```bash
# Simplify constitution to smallest failing case
cp memory/constitution.md /tmp/constitution-minimal.md
# Edit /tmp/constitution-minimal.md to remove custom sections
specify constitution validate --path /tmp/constitution-minimal.md
```

**2. Gather diagnostic information:**
```bash
# JP Spec Kit version
specify --version

# Constitution tier
grep "CONSTITUTION_TIER" memory/constitution.md

# Validation output
specify constitution validate > validation-output.txt 2>&1
```

**3. Open GitHub issue:**
- **Title**: Descriptive error message
- **Body**: Include:
  - JP Spec Kit version
  - Constitution tier
  - Steps to reproduce
  - Validation output
  - Minimal constitution.md (anonymized)

**4. Check existing issues:**
```bash
# Search GitHub issues
gh issue list --search "constitution"
```

### Community Support

- **GitHub Discussions**: Ask questions
- **GitHub Issues**: Report bugs
- **Pull Requests**: Contribute fixes

---

## Prevention Best Practices

### Do:
- ✅ Choose tier matching your team size and phase
- ✅ Validate constitution immediately after `/speckit:constitution`
- ✅ Review LLM-generated content carefully before removing markers
- ✅ Version your constitution and track changes
- ✅ Document why you made constitution decisions
- ✅ Use industry standard defaults for unknowns
- ✅ Commit validated constitution to Git
- ✅ Re-evaluate tier quarterly or when team grows

### Don't:
- ❌ Choose Heavy tier "just to be safe" without understanding trade-offs
- ❌ Remove NEEDS_VALIDATION markers without reading content
- ❌ Ignore validation warnings from /jpspec commands
- ❌ Skip validation because "it's just a template"
- ❌ Make tier changes without team consensus (Medium/Heavy)
- ❌ Leave unvalidated constitution in production projects
- ❌ Mix prototype-phase Light tier with production deployment

---

## Summary

**Most Common Issues**:
1. **Wrong language detected** → Manually correct and remove NEEDS_VALIDATION
2. **NEEDS_VALIDATION stuck** → Use industry defaults or N/A
3. **Heavy tier blocking** → Validate constitution or temporarily use --skip-validation
4. **Version mismatch** → Manually merge new template sections
5. **Wrong tier chosen** → Downgrade/upgrade tier, document rationale

**Quick Diagnostic Steps**:
1. Run `specify constitution validate`
2. Check `grep "NEEDS_VALIDATION" memory/constitution.md`
3. Verify tier matches team size: `grep "CONSTITUTION_TIER" memory/constitution.md`
4. Review recent changes: `git log memory/constitution.md`

**Emergency Procedures**:
- **Heavy tier blocking critical work** → Use `--skip-validation` flag
- **Constitution completely wrong** → Restore from Git: `git checkout HEAD~1 memory/constitution.md`
- **Need to change tier fast** → Edit tier comment, commit with rationale

**Prevention**:
- Validate immediately after LLM generation
- Review quarterly as project evolves
- Document all changes with rationale
- Test tier selection with trial periods

---

## Related Documentation

- [Constitution Distribution Guide](./constitution-distribution.md) - Full feature overview
- [Constitution Validation Guide](./constitution-validation.md) - Detailed validation workflow
- [JP Spec Kit CLI Reference](../reference/cli-commands.md) - Command reference
- [Case Study: Constitution Templates](../case-studies/02-constitution-templates.md) - Implementation examples
