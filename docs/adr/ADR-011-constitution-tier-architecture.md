# ADR-011: Constitution Tier Architecture

**Status**: Accepted
**Date**: 2025-12-04
**Author**: Enterprise Software Architect (Kinsale Host)
**Context**: Tasks 242, 243, 244, 245, 246 - Constitution Template System

---

## Context and Problem Statement

JP Spec Kit currently provides a single, comprehensive constitution template that works well for enterprise projects but creates unnecessary overhead for smaller projects. The template includes extensive sections on git workflow, parallel execution with worktrees, DCO sign-off, PR-task synchronization, and constitutional compliance checks.

**Problems**:
- Small teams/projects feel overwhelmed by 160-line constitution with enterprise-grade requirements
- Constitution becomes "checkbox exercise" rather than living document
- No guidance on what's essential vs. optional for different project scales
- Existing projects lack constitution entirely or have incomplete one
- Manual constitution customization is time-consuming and error-prone
- LLM-generated constitutions need validation markers to prevent blind adoption

**Goal**: Design a tiered constitution system (light/medium/heavy) that right-sizes governance for project complexity while preserving non-negotiable principles across all tiers.

---

## Decision Drivers

1. **Progressive Disclosure**: Introduce complexity only as project needs grow
2. **Non-Negotiables**: Core principles (Test-First, Task Quality, DCO) apply to all tiers
3. **Adoption Ease**: Light tier reduces barrier to entry for SDD methodology
4. **LLM Customization**: Enable intelligent constitution generation from codebase analysis
5. **Validation Safety**: Mark auto-generated sections requiring human review
6. **Upgrade Path**: Clear migration from light → medium → heavy as project matures

---

## Considered Options

### Option 1: Single Template with Optional Sections
**Approach**: Keep one template, mark sections as (OPTIONAL) or (REQUIRED)

**Pros**:
- Single source of truth
- No duplication
- Easy to maintain

**Cons**:
- Still presents overwhelming full template to new users
- Cognitive load remains high
- No clear guidance on when to enable optional sections

### Option 2: Fully Separate Templates (Light/Medium/Heavy)
**Approach**: Three completely independent templates with no shared content

**Pros**:
- Clear separation by project size
- No confusion about optional content
- Optimized for each tier

**Cons**:
- High maintenance burden (update 3 files)
- Risk of divergence (core principles out of sync)
- No shared template base for LLM customization

### Option 3: Tiered Templates with Shared Core + Tier-Specific Extensions
**Approach**: Shared core principles + tiered extensions for workflow complexity

**Pros**:
- Non-negotiables guaranteed consistent across tiers
- Lower maintenance (update core once)
- Clear upgrade path (add next tier's extensions)
- Supports LLM customization with tier selection
- Progressive disclosure of complexity

**Cons**:
- Requires template composition system
- More complex initial setup
- Need to define tier boundaries clearly

---

## Decision Outcome

**Chosen Option**: **Option 3 - Tiered Templates with Shared Core + Extensions**

### Rationale

This approach provides the best balance of:
- **Consistency**: Core principles (Test-First, Task Quality, DCO) identical across tiers
- **Scalability**: Light tier for prototypes/small projects, heavy tier for enterprises
- **Maintainability**: Update shared core once, affects all tiers
- **Flexibility**: Projects can customize within tier or upgrade to next tier
- **LLM Integration**: `/speckit:constitution` can analyze repo and recommend tier + customizations

---

## Architecture Design

### Tier Definitions

#### Light Tier (Prototypes, Small Teams, Learning SDD)

**Target**: 1-3 developers, <6 month project lifecycle, MVP/prototype phase

**Included**:
- Core Principles (3-5 principles specific to project domain)
- Task Quality (AC requirement, testable criteria)
- Git Commit Requirements (DCO sign-off only)
- Basic Governance (constitution authority, amendment process)

**Excluded**:
- PR-Task Synchronization (manual workflow acceptable)
- Parallel Task Execution (no git worktrees required)
- No Direct Commits to Main (direct commits allowed with DCO)
- Workflow Transition Validation (NONE mode)

**Constitution Length**: ~60-80 lines

**Example Use Case**: Solo developer building API client library, wants SDD discipline without enterprise overhead.

#### Medium Tier (Production Projects, Growing Teams)

**Target**: 4-10 developers, 6-24 month lifecycle, production-ready features

**Included**:
- Everything from Light Tier
- PR-Task Synchronization (required for production releases)
- No Direct Commits to Main (PRs mandatory for main branch)
- Workflow Transition Validation (KEYWORD mode recommended)
- Basic CI/CD Requirements (tests must pass before merge)

**Excluded**:
- Parallel Task Execution (git worktrees optional)
- Advanced Workflow Validation (PULL_REQUEST mode)
- Comprehensive Security/Compliance sections

**Constitution Length**: ~100-130 lines

**Example Use Case**: Startup with growing engineering team, shipping features monthly, needs coordination without bureaucracy.

#### Heavy Tier (Enterprise, Regulated Industries, Large Teams)

**Target**: 10+ developers, multi-year projects, compliance requirements, high coordination needs

**Included**:
- Everything from Medium Tier
- Parallel Task Execution (git worktrees mandatory for parallel work)
- Advanced Workflow Validation (PULL_REQUEST mode for critical transitions)
- Security/Compliance sections (SLSA, vulnerability scanning, audit trails)
- Performance/Observability Requirements
- Disaster Recovery/SLA sections

**Constitution Length**: ~160-200 lines

**Example Use Case**: Fintech company building payment platform, needs SOC2 compliance, multiple teams working in parallel.

---

## Template Structure

### File Organization

```
templates/constitution/
├── core/
│   ├── non-negotiables.md        # Test-First, Task Quality, DCO (shared)
│   ├── governance.md              # Amendment process (shared)
│   └── principles-template.md    # Project-specific principles (3-5 max)
├── tiers/
│   ├── light.md                  # Light-specific sections
│   ├── medium.md                 # Medium-specific sections (includes light)
│   └── heavy.md                  # Heavy-specific sections (includes medium)
└── templates/
    ├── constitution-light.md     # Composed template: core + light
    ├── constitution-medium.md    # Composed template: core + medium
    └── constitution-heavy.md     # Composed template: core + heavy
```

### Tier Composition Rules

**Light Tier** = Core Non-Negotiables + Governance + Project Principles (LLM-customized)

**Medium Tier** = Light Tier + PR-Task Sync + No Direct Commits to Main + CI/CD Gates

**Heavy Tier** = Medium Tier + Parallel Task Execution + Workflow Validation + Security/Compliance

### Template Variables (LLM Customization)

Each template includes variables for LLM-based customization:

```markdown
# [PROJECT_NAME] Constitution
<!-- Detected: jp-spec-kit -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Detected: Library-First (from pyproject.toml structure) -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Auto-generated from repository analysis, NEEDS_VALIDATION -->

### [PRINCIPLE_2_NAME]
<!-- Detected: CLI Interface (from src/specify_cli/ and click dependency) -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Auto-generated from repository analysis, NEEDS_VALIDATION -->

### [PRINCIPLE_3_NAME]
<!-- Mandatory: Test-First (TDD) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Fixed content from core/non-negotiables.md -->
```

### NEEDS_VALIDATION Marker System

All LLM-generated content includes validation markers:

```markdown
### [SECTION_NAME]
<!-- NEEDS_VALIDATION: Auto-generated from [SOURCE] -->
[AUTO_GENERATED_CONTENT]
<!-- /NEEDS_VALIDATION -->
```

**Validation Workflow**:
1. `/speckit:constitution` generates constitution with markers
2. Command outputs: "Constitution generated - please review NEEDS_VALIDATION sections"
3. Developer reviews, modifies, removes markers
4. `specify constitution validate` checks for remaining markers
5. `/jpspec` commands warn if markers still present

---

## Core Non-Negotiables (All Tiers)

The following principles are **MANDATORY** across all tiers and cannot be disabled:

### 1. Test-First (TDD)
```markdown
### Test-First (NON-NEGOTIABLE)
Tests written → User approved → Tests fail → Then implement.
Red-Green-Refactor cycle strictly enforced.
```

**Rationale**: Test-First is the foundation of SDD methodology. Without it, specs become documentation theater.

### 2. Task Quality
```markdown
### Task Quality (NON-NEGOTIABLE)
Every task created in the backlog MUST have:
- **At least one acceptance criterion** - Tasks without ACs are incomplete
- **Clear, testable criteria** - Each AC must be outcome-oriented and verifiable
- **Proper description** - Explains the "why" and context
```

**Rationale**: Tasks without acceptance criteria are unverifiable and lead to scope creep.

### 3. DCO Sign-Off
```markdown
### DCO Sign-Off Required (NON-NEGOTIABLE)
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

Always use `git commit -s` to automatically add the sign-off.

Commits without sign-off will block PRs from being merged.
```

**Rationale**: Legal/IP protection for all contributors, minimal overhead (single flag).

---

## Tier-Specific Sections

### Light Tier Only

**Direct Commits Allowed**:
```markdown
## Git Workflow
Direct commits to main branch are allowed for solo developers.
For team projects, consider upgrading to Medium Tier for PR-based workflow.

All commits MUST include DCO sign-off: `git commit -s`
```

### Medium Tier Additions

**No Direct Commits to Main**:
```markdown
## Git Commit Requirements (NON-NEGOTIABLE)

### No Direct Commits to Main (ABSOLUTE)
NEVER commit directly to the main branch. All changes MUST go through a PR:

1. Create a branch for the task
2. Make changes on the branch
3. Create a PR referencing the backlog task
4. PR must pass CI before merge
5. Task marked Done only after PR is merged

NO EXCEPTIONS.
```

**PR-Task Synchronization**:
```markdown
### PR-Task Synchronization (NON-NEGOTIABLE)
When creating a PR that completes a backlog task:

1. Before PR creation: Mark all completed acceptance criteria
2. With PR creation: Update task status and reference the PR
3. PR-Task coupling: If the PR fails CI or is rejected, revert task status
```

### Heavy Tier Additions

**Parallel Task Execution**:
```markdown
## Parallel Task Execution (NON-NEGOTIABLE)

### Git Worktree Requirements
When executing tasks in parallel, git worktrees MUST be used:

1. Worktree name must match branch name
2. One branch per worktree
3. Clean isolation prevents merge conflicts
```

**Advanced Workflow Validation**:
```markdown
## Workflow Transition Validation
Critical transitions (Planned → In Implementation) require merged PR approval.
Configure validation mode in jpspec_workflow.yml (PULL_REQUEST mode recommended).
```

---

## LLM Customization Workflow

### `/speckit:constitution` Command Flow

```
1. Detect Project Context
   ├─ Scan for .git, package.json, pyproject.toml, go.mod, etc.
   ├─ Identify languages (Python, Go, TypeScript, Rust, etc.)
   ├─ Detect frameworks (Django, React, FastAPI, etc.)
   ├─ Find CI configs (.github/workflows/, .gitlab-ci.yml)
   └─ Check existing constitution (if present, offer upgrade)

2. Recommend Tier
   ├─ Light: Single developer, no CI, <10 files
   ├─ Medium: Multiple developers, CI present, <100 files
   └─ Heavy: >5 contributors in git log, complex CI, >100 files

3. Generate Custom Constitution
   ├─ Load tier template (light/medium/heavy)
   ├─ Analyze codebase for project-specific principles
   │   ├─ Library-First: Detect packages/modules
   │   ├─ CLI Interface: Detect argparse, click, cobra usage
   │   ├─ API-First: Detect REST/GraphQL endpoints
   │   └─ Data Pipeline: Detect ETL/batch processing patterns
   ├─ Customize [PRINCIPLE_NAME] and [DESCRIPTION] sections
   ├─ Add NEEDS_VALIDATION markers to auto-generated content
   └─ Output to memory/constitution.md

4. Validation Prompt
   ├─ Display: "Constitution generated - please review NEEDS_VALIDATION sections"
   ├─ List sections requiring validation
   └─ Recommend: "Run 'specify constitution validate' before using /jpspec commands"
```

### Repository Analysis Heuristics

**Detect Library-First Pattern**:
```python
# Check for library structure
if exists("src/") and exists("tests/") and exists("pyproject.toml"):
    principle = "Library-First"
    description = "Every feature starts as standalone library with clear API"
```

**Detect CLI Interface Pattern**:
```python
# Check for CLI entry points
if exists("src/specify_cli/") or "click" in dependencies or "argparse" in code:
    principle = "CLI Interface"
    description = "Every library exposes functionality via CLI (stdin/stdout protocol)"
```

**Detect Monorepo Pattern**:
```python
# Check for monorepo indicators
if count(package_json_files) > 3 or exists("lerna.json") or exists("nx.json"):
    principle = "Monorepo Organization"
    description = "Shared tooling, independent deployments, clear boundaries"
```

**Detect Microservices Pattern**:
```python
# Check for microservices architecture
if exists("docker-compose.yml") and count(Dockerfile) > 2:
    principle = "Service Independence"
    description = "Each service independently deployable, tested, and versioned"
```

---

## Validation System

### `specify constitution validate` Command

**Purpose**: Detect unvalidated sections before workflow execution

**Algorithm**:
```python
def validate_constitution(constitution_path):
    content = read_file(constitution_path)

    # Check for NEEDS_VALIDATION markers
    markers = re.findall(r'<!-- NEEDS_VALIDATION: (.*?) -->', content)

    if markers:
        print("❌ Constitution has unvalidated sections:")
        for marker in markers:
            print(f"  - {marker}")
        print("\nReview and remove NEEDS_VALIDATION comments after validation.")
        return False

    # Check for required sections (all tiers)
    required = ["Test-First", "Task Quality", "DCO Sign-Off", "Governance"]
    for section in required:
        if section not in content:
            print(f"❌ Missing required section: {section}")
            return False

    print("✅ Constitution validation passed")
    return True
```

**Exit Codes**:
- `0`: Validation passed, no unvalidated sections
- `1`: Unvalidated sections detected
- `2`: Missing required sections

**Integration with `/jpspec` Commands**:
```bash
# Every jpspec command checks constitution validity
if ! specify constitution validate --silent; then
    echo "⚠️  Warning: Constitution has NEEDS_VALIDATION sections."
    echo "Run 'specify constitution validate' for details."
    echo "Proceeding anyway, but recommend validation first."
fi
```

---

## Project Detection and Tier Recommendation

### Detection Heuristics

**Small Project (Light Tier)**:
```python
def is_small_project():
    return (
        git_contributor_count() <= 2 and
        file_count() < 50 and
        not ci_config_exists() and
        not production_deployment_detected()
    )
```

**Medium Project (Medium Tier)**:
```python
def is_medium_project():
    return (
        git_contributor_count() in (3, 10) and
        file_count() in (50, 500) and
        ci_config_exists() and
        has_test_suite()
    )
```

**Large Project (Heavy Tier)**:
```python
def is_large_project():
    return (
        git_contributor_count() > 10 or
        file_count() > 500 or
        parallel_branch_activity() or
        compliance_indicators_present()  # SOC2, HIPAA, PCI-DSS files
    )
```

### Interactive Tier Selection

When `specify init --here` runs on existing project without constitution:

```
Existing project detected: jp-spec-kit
Scanning repository...

Analysis Results:
  Language(s): Python
  Framework(s): Click (CLI), Pytest (Testing)
  Contributors: 3
  Lines of Code: ~8,500
  CI/CD: GitHub Actions detected

Recommended Tier: Medium

Constitution Tiers:
  [1] Light   - Solo developer, prototypes, learning SDD
  [2] Medium  - Production projects, team coordination (RECOMMENDED)
  [3] Heavy   - Enterprise, compliance, parallel development

Select tier (1-3) [2]: 2

Generating Medium tier constitution...
✓ Core principles detected: Library-First, CLI Interface, Test-First
✓ Constitution written to memory/constitution.md
⚠️  Please review NEEDS_VALIDATION sections before using /jpspec commands.

Run 'specify constitution validate' to check validation status.
```

---

## Upgrade Path

### Light → Medium Migration

**Trigger**: Team grows from 1-2 to 3-5 developers, production deployment imminent

**Changes Required**:
1. Enable PR-Task Synchronization
2. Enforce "No Direct Commits to Main"
3. Configure CI/CD gates (tests must pass)
4. Update constitution.md with Medium tier sections

**Migration Command**:
```bash
specify constitution upgrade --to medium
```

**Output**:
```
Upgrading constitution from Light to Medium tier...

Changes to be applied:
  + PR-Task Synchronization (NON-NEGOTIABLE)
  + No Direct Commits to Main (ABSOLUTE)
  + CI/CD Gates (tests must pass before merge)

⚠️  Breaking Changes:
  - Direct commits to main will be blocked (create branch + PR instead)
  - Tasks must reference PRs in implementation notes

Proceed with upgrade? (y/n): y

✓ Constitution upgraded to Medium tier
✓ Updated memory/constitution.md
⚠️  Review changes and commit with DCO sign-off: git commit -s
```

### Medium → Heavy Migration

**Trigger**: Team exceeds 10 developers, parallel feature work common, compliance requirements

**Changes Required**:
1. Mandate git worktrees for parallel task execution
2. Enable PULL_REQUEST workflow validation mode
3. Add Security/Compliance sections
4. Add Observability/SLA sections

**Migration Command**:
```bash
specify constitution upgrade --to heavy
```

---

## Testing Strategy

### Unit Tests (Template Composition)

```python
def test_light_tier_template_composition():
    """Verify light tier includes only core + light sections."""
    template = load_template("constitution-light.md")

    # Must include core non-negotiables
    assert "Test-First (NON-NEGOTIABLE)" in template
    assert "Task Quality (NON-NEGOTIABLE)" in template
    assert "DCO Sign-Off Required" in template

    # Must NOT include medium/heavy sections
    assert "No Direct Commits to Main" not in template
    assert "Git Worktree Requirements" not in template

def test_medium_tier_template_composition():
    """Verify medium tier includes core + light + medium sections."""
    template = load_template("constitution-medium.md")

    # Includes all light tier content
    assert_light_tier_content(template)

    # Adds medium-specific sections
    assert "No Direct Commits to Main (ABSOLUTE)" in template
    assert "PR-Task Synchronization" in template

    # Still excludes heavy sections
    assert "Git Worktree Requirements" not in template

def test_heavy_tier_template_composition():
    """Verify heavy tier includes all tiers."""
    template = load_template("constitution-heavy.md")

    # Includes all medium tier content
    assert_medium_tier_content(template)

    # Adds heavy-specific sections
    assert "Parallel Task Execution (NON-NEGOTIABLE)" in template
    assert "Git Worktree Requirements" in template
```

### Integration Tests (LLM Customization)

```python
def test_llm_customization_python_cli_project():
    """Verify LLM correctly detects Python CLI project patterns."""
    repo_path = create_test_repo(
        files=["src/myapp/cli.py", "pyproject.toml", "tests/"],
        dependencies=["click", "pytest"]
    )

    constitution = generate_constitution(repo_path, tier="medium")

    # Should detect Library-First pattern
    assert "Library-First" in constitution

    # Should detect CLI Interface pattern
    assert "CLI Interface" in constitution

    # Should mark auto-generated sections for validation
    assert "NEEDS_VALIDATION" in constitution

def test_llm_customization_microservices_project():
    """Verify LLM correctly detects microservices patterns."""
    repo_path = create_test_repo(
        files=["auth-service/Dockerfile", "api-service/Dockerfile", "docker-compose.yml"],
        git_contributors=12
    )

    # Should recommend Heavy tier
    recommendation = recommend_tier(repo_path)
    assert recommendation == "heavy"

    constitution = generate_constitution(repo_path, tier="heavy")

    # Should detect Service Independence pattern
    assert "Service Independence" in constitution
    assert "independently deployable" in constitution.lower()
```

### End-to-End Tests (Validation Workflow)

```python
def test_constitution_validation_blocks_jpspec():
    """Verify /jpspec commands warn about unvalidated constitution."""
    # Generate constitution with NEEDS_VALIDATION markers
    generate_constitution("test-project", tier="medium")

    # Attempt to run /jpspec:specify
    result = run_command("/jpspec:specify --feature auth")

    # Should warn but not block
    assert "⚠️  Warning: Constitution has NEEDS_VALIDATION sections" in result.stderr
    assert result.returncode == 0  # Proceeds anyway

def test_constitution_validation_passes_after_review():
    """Verify validation passes after markers removed."""
    # Generate constitution
    constitution_path = generate_constitution("test-project", tier="light")

    # Remove NEEDS_VALIDATION markers (simulating human review)
    content = read_file(constitution_path)
    content = re.sub(r'<!-- NEEDS_VALIDATION:.*?-->', '', content)
    content = re.sub(r'<!-- /NEEDS_VALIDATION -->', '', content)
    write_file(constitution_path, content)

    # Validation should pass
    result = run_command("specify constitution validate")
    assert "✅ Constitution validation passed" in result.stdout
    assert result.returncode == 0
```

---

## Consequences

### Positive

- **Lower Barrier to Entry**: Light tier reduces friction for SDD adoption
- **Right-Sized Governance**: Avoid bureaucracy for small projects, enforce discipline for large ones
- **Progressive Complexity**: Teams can start light and upgrade as needed
- **Intelligent Defaults**: LLM customization reduces manual constitution writing
- **Safety Net**: NEEDS_VALIDATION markers prevent blind acceptance of AI-generated content
- **Consistency**: Core non-negotiables guaranteed across all tiers
- **Upgrade Path**: Clear migration from light → medium → heavy

### Negative

- **Template Maintenance**: Must keep 3 tier templates in sync with core
- **Complexity**: More moving parts than single template
- **Learning Curve**: Developers must understand tier system
- **LLM Dependency**: Constitution quality depends on LLM analysis accuracy
- **Validation Burden**: Humans must review NEEDS_VALIDATION sections

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Light tier too permissive | Technical debt accumulates | Document upgrade triggers, recommend Medium for production |
| Heavy tier too restrictive | Team resists adoption | Make worktrees/validation optional unless explicitly needed |
| LLM generates incorrect principles | Constitution doesn't fit project | NEEDS_VALIDATION markers force human review |
| Tiers diverge over time | Core principles inconsistent | Automated tests verify core content identical across tiers |
| Teams skip validation step | Broken/incomplete constitutions | `/jpspec` commands warn prominently if markers present |

---

## References

- **Task-242**: Define constitution template tiers
- **Task-243**: Detect existing projects without constitution
- **Task-244**: Implement /speckit:constitution LLM customization
- **Task-245**: Add constitution validation guidance
- **Task-246**: Integration tests for constitution system
- **SVPG DVF+V Framework**: Desirability, Viability, Feasibility + Viability risk assessment
- **Developer Certificate of Origin**: https://developercertificate.org/

---

## Appendix: Complete Tier Comparison

| Feature | Light Tier | Medium Tier | Heavy Tier |
|---------|-----------|-------------|------------|
| **Core Principles** | ✅ 3-5 custom | ✅ 3-5 custom | ✅ 3-5 custom |
| **Test-First (TDD)** | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory |
| **Task Quality (ACs)** | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory |
| **DCO Sign-Off** | ✅ Mandatory | ✅ Mandatory | ✅ Mandatory |
| **Direct Commits to Main** | ✅ Allowed | ❌ Blocked | ❌ Blocked |
| **PR-Task Sync** | ❌ Optional | ✅ Required | ✅ Required |
| **CI/CD Gates** | ❌ Optional | ✅ Tests must pass | ✅ Tests + security scans |
| **Git Worktrees** | ❌ Not required | ❌ Optional | ✅ Required for parallel work |
| **Workflow Validation** | NONE mode | KEYWORD mode | PULL_REQUEST mode |
| **Security/Compliance** | ❌ Not included | ❌ Basic only | ✅ Comprehensive |
| **Observability** | ❌ Not included | ❌ Optional | ✅ Required (SLOs, metrics) |
| **Constitution Length** | ~60-80 lines | ~100-130 lines | ~160-200 lines |
| **Target Audience** | Solo, prototypes | Small teams, production | Enterprises, compliance |
| **Typical Project Size** | <50 files | 50-500 files | >500 files |
| **Typical Team Size** | 1-2 developers | 3-10 developers | 10+ developers |

---

**Decision**: The tiered constitution architecture enables SDD methodology adoption across project scales while maintaining consistency in core principles and providing intelligent defaults through LLM customization.
