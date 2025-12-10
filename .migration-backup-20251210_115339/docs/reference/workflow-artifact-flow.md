# JPSpec Workflow Artifact Flow

This document provides comprehensive documentation of the JPSpec workflow pipeline, including all states, transitions, artifacts, and validation modes.

## Workflow Pipeline Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    JPSpec Workflow Pipeline with Artifacts                    │
└──────────────────────────────────────────────────────────────────────────────┘

                              ┌───────────┐
                              │   To Do   │
                              └─────┬─────┘
                                    │ /jpspec:assess
                                    ▼
                              ┌───────────┐
                              │ Assessed  │ → Assessment Report
                              └─────┬─────┘
                                    │ /jpspec:specify
                                    ▼
                              ┌───────────┐
                              │ Specified │ → PRD, Backlog Tasks
                              └─────┬─────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │ /jpspec:research    │                     │
              ▼                     │                     │
        ┌───────────┐               │                     │
        │Researched │ → Research    │                     │
        │           │   Report      │                     │
        └─────┬─────┘               │                     │
              │                     │ (skip research)     │
              └─────────────────────┤                     │
                                    │ /jpspec:plan        │
                                    ▼                     │
                              ┌───────────┐               │
                              │  Planned  │ → ADRs ←──────┘
                              └─────┬─────┘
                                    │ /jpspec:implement
                                    ▼
                              ┌───────────┐
                              │   In      │ → Code, Tests,
                              │Implementa-│   AC Coverage
                              │   tion    │
                              └─────┬─────┘
                                    │ /jpspec:validate
                                    ▼
                              ┌───────────┐
                              │ Validated │ → QA Report,
                              │           │   Security Report
                              └─────┬─────┘
                                    │ /jpspec:operate
                                    ▼
                              ┌───────────┐
                              │ Deployed  │ → Deployment
                              │           │   Manifest
                              └─────┬─────┘
                                    │ (manual)
                                    ▼
                              ┌───────────┐
                              │   Done    │
                              └───────────┘
```

## Workflow States

The JPSpec workflow consists of 9 states:

| # | State | Description |
|---|-------|-------------|
| 1 | **To Do** | Initial state - work has not started |
| 2 | **Assessed** | SDD suitability evaluated via /jpspec:assess |
| 3 | **Specified** | Requirements captured via /jpspec:specify |
| 4 | **Researched** | Technical and business research completed (optional) |
| 5 | **Planned** | Architecture and infrastructure planned |
| 6 | **In Implementation** | Code actively being written |
| 7 | **Validated** | QA, security, and documentation validated |
| 8 | **Deployed** | Released to production |
| 9 | **Done** | Work complete - ready for archive |

## Complete Transition Reference

### Forward Transitions

| # | From State | To State | Command | Description |
|---|------------|----------|---------|-------------|
| 1 | To Do | Assessed | `/jpspec:assess` | Evaluate SDD workflow suitability |
| 2 | Assessed | Specified | `/jpspec:specify` | Create PRD with user stories |
| 3 | Specified | Researched | `/jpspec:research` | Technical/business research (optional) |
| 4 | Specified | Planned | `/jpspec:plan` | Architecture planning (skip research) |
| 5 | Researched | Planned | `/jpspec:plan` | Architecture planning after research |
| 6 | Planned | In Implementation | `/jpspec:implement` | Implementation work started |
| 7 | In Implementation | Validated | `/jpspec:validate` | QA and security validation |
| 8 | Validated | Deployed | `/jpspec:operate` | Production deployment |
| 9 | Deployed | Done | manual | Deployment confirmed successful |

### Rework/Rollback Transitions

| From State | To State | Via | Description |
|------------|----------|-----|-------------|
| In Implementation | Planned | rework | Rework needed based on implementation findings |
| Validated | In Implementation | rework | Rework needed based on validation findings |
| Deployed | Validated | rollback | Rollback from production due to issues |

### Direct-to-Done Transitions

Tasks can be manually marked as Done from these states:
- In Implementation → Done (implementation complete, validation deferred)
- Validated → Done (feature validated but deployment deferred)
- Deployed → Done (production deployment confirmed successful)

## Artifact Specification

### Artifact Location Reference

| Artifact Type | Directory | Filename Pattern | Example |
|---------------|-----------|------------------|---------|
| Assessment Report | `./docs/assess/` | `{feature}-assessment.md` | `user-auth-assessment.md` |
| PRD | `./docs/prd/` | `{feature}.md` | `user-auth.md` |
| Research Report | `./docs/research/` | `{feature}-research.md` | `user-auth-research.md` |
| Business Validation | `./docs/research/` | `{feature}-validation.md` | `user-auth-validation.md` |
| ADR | `./docs/adr/` | `ADR-{NNN}-{slug}.md` | `ADR-001-oauth-strategy.md` |
| Platform Design | `./docs/platform/` | `{feature}-platform.md` | `user-auth-platform.md` |
| Source Code | `./src/` | (varies) | - |
| Tests | `./tests/` | (varies) | - |
| AC Coverage | `./tests/` | `ac-coverage.json` | - |
| QA Report | `./docs/qa/` | `{feature}-qa-report.md` | `user-auth-qa-report.md` |
| Security Report | `./docs/security/` | `{feature}-security.md` | `user-auth-security.md` |
| Deployment Manifest | `./deploy/` | (varies) | - |

### Artifact Path Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{feature}` | Feature name slug | `user-authentication` |
| `{NNN}` | Zero-padded number | `001`, `002`, `042` |
| `{slug}` | Title slug from feature | `oauth-strategy` |

### Transition Artifact Requirements

#### 1. assess (To Do → Assessed)

**Input Artifacts:** None (entry point)

**Output Artifacts:**
- Assessment Report: `./docs/assess/{feature}-assessment.md` (required)

#### 2. specify (Assessed → Specified)

**Input Artifacts:**
- Assessment Report: `./docs/assess/{feature}-assessment.md` (required)

**Output Artifacts:**
- PRD: `./docs/prd/{feature}.md` (required)
- Backlog Tasks: `./backlog/tasks/*.md` (required, multiple)

#### 3. research (Specified → Researched)

**Input Artifacts:**
- PRD: `./docs/prd/{feature}.md` (required)

**Output Artifacts:**
- Research Report: `./docs/research/{feature}-research.md` (required)
- Business Validation: `./docs/research/{feature}-validation.md` (optional)

#### 4. plan (Specified/Researched → Planned)

**Input Artifacts:**
- PRD: `./docs/prd/{feature}.md` (required)

**Output Artifacts:**
- ADRs: `./docs/adr/ADR-{NNN}-{slug}.md` (required, multiple)
- Platform Design: `./docs/platform/{feature}-platform.md` (optional)

#### 5. implement (Planned → In Implementation)

**Input Artifacts:**
- ADRs: `./docs/adr/ADR-*.md` (required)

**Output Artifacts:**
- Source Code: `./src/` (required)
- Tests: `./tests/` (required)
- AC Coverage: `./tests/ac-coverage.json` (required)

#### 6. validate (In Implementation → Validated)

**Input Artifacts:**
- Tests (required)
- AC Coverage (required)

**Output Artifacts:**
- QA Report: `./docs/qa/{feature}-qa-report.md` (required)
- Security Report: `./docs/security/{feature}-security.md` (required)

#### 7. operate (Validated → Deployed)

**Input Artifacts:**
- QA Report (required)
- Security Report (required)

**Output Artifacts:**
- Deployment Manifest: `./deploy/` (required)

## Validation Modes

Each transition can be configured with a validation mode that gates progression.

### Mode Reference

| Mode | Syntax | Behavior | Use Case |
|------|--------|----------|----------|
| `NONE` | `validation: NONE` | Pass immediately after artifacts created | Default, rapid iteration, solo development |
| `KEYWORD` | `validation: KEYWORD["APPROVED"]` | User must type exact keyword | Human approval without PR overhead |
| `PULL_REQUEST` | `validation: PULL_REQUEST` | PR containing artifacts must be merged | Team review, compliance requirements |

### NONE Mode

No gate enforcement. Transition proceeds immediately after artifacts are created.

```yaml
validation: NONE
```

**Example output:**
```
✓ Artifacts validated
✓ Transitioning to "Specified"
```

### KEYWORD Mode

User must type the exact keyword (case-sensitive) to proceed.

```yaml
validation: KEYWORD["PRD_APPROVED"]
```

**Example output:**
```
✓ Artifacts validated
============================================================
KEYWORD VALIDATION REQUIRED: specify
============================================================

To proceed with this transition, type the exact keyword:

  → PRD_APPROVED

(or press Ctrl+C to cancel)

Enter keyword: PRD_APPROVED
✓ Keyword accepted. Proceeding with transition.
```

### PULL_REQUEST Mode

Transition blocked until a PR containing the output artifact(s) is merged.

```yaml
validation: PULL_REQUEST
```

**Example output (blocked):**
```
✓ Artifacts validated
✗ Waiting for PR containing ./docs/adr/ADR-001-*.md to be merged
  Hint: Create PR with: gh pr create --title "ADR: Feature X"
```

**Example output (passed):**
```
✓ Artifacts validated
✓ Found merged PR #42: feat(auth): add OAuth ADRs
✓ Transitioning to "Planned"
```

### Emergency Override

Use `--skip-validation` flag to bypass all validation gates (emergency use only).

```bash
specify workflow transition --to "Planned" --skip-validation
```

**Warning:** This flag bypasses all validation and logs a warning for audit trail. Use only in exceptional circumstances.

## Configuring Validation Modes

Validation modes are configured in `jpspec_workflow.yml`:

```yaml
# Example configuration
transitions:
  - name: assess
    from: "To Do"
    to: "Assessed"
    validation: NONE

  - name: specify
    from: "Assessed"
    to: "Specified"
    validation: KEYWORD["PRD_APPROVED"]

  - name: plan
    from: ["Specified", "Researched"]
    to: "Planned"
    validation: PULL_REQUEST
```

## Troubleshooting

### Missing Artifacts Error

**Error:**
```
Required artifacts missing: prd
Cannot proceed with transition until artifacts are created.
```

**Solution:**
1. Run the appropriate workflow command to generate the artifact
2. Check the artifact path matches the expected pattern
3. Verify file exists: `ls ./docs/prd/{feature}.md`

### KEYWORD Validation Failed

**Error:**
```
Incorrect keyword. Expected 'APPROVED' but got 'approved'
Transition blocked.
```

**Solution:**
- Keywords are case-sensitive
- Type the exact keyword shown in the prompt
- Check `jpspec_workflow.yml` for the configured keyword

### PULL_REQUEST Validation Failed

**Error:**
```
No merged PR found for feature 'auth'.
Create and merge a PR containing the required artifacts to proceed.
```

**Solution:**
1. Create a PR with the artifacts: `gh pr create --title "feat: auth artifacts"`
2. Get PR reviewed and merged
3. Retry the transition

**Error:**
```
GitHub CLI (gh) not found. Install it to use PULL_REQUEST validation mode.
```

**Solution:**
- Install GitHub CLI: https://cli.github.com/
- Authenticate: `gh auth login`

### gh CLI Authentication Error

**Error:**
```
Failed to query GitHub PRs: not authenticated
```

**Solution:**
```bash
gh auth login
gh auth status  # Verify authentication
```

## Programmatic Reference

For programmatic access to workflow configuration, see:

- **Configuration file:** `jpspec_workflow.yml`
- **Python API:** `specify_cli.workflow.WorkflowConfig`
- **Transition schema:** `specify_cli.workflow.transition.WORKFLOW_TRANSITIONS`
- **Validation engine:** `specify_cli.workflow.validation_engine.TransitionValidator`

### Example: Loading Workflow Config

```python
from specify_cli.workflow import WorkflowConfig

config = WorkflowConfig.load()
transitions = config.get_transitions()

for t in transitions:
    print(f"{t['from']} → {t['to']} via {t['via']}")
```

### Example: Validating the Workflow Configuration

```python
from specify_cli.workflow import WorkflowConfig
from specify_cli.workflow.validator import WorkflowValidator

config = WorkflowConfig.load()
validator = WorkflowValidator(config)
result = validator.validate()

if result.passed:
    print("Workflow configuration is valid")
else:
    print(f"Validation failed: {result.message}")
```

## Related Documentation

- [Inner Loop Reference](inner-loop.md) - Fast, local iteration workflow
- [Outer Loop Reference](outer-loop.md) - CI/CD pipeline workflow
- [Agent Loop Classification](agent-loop-classification.md) - Agent execution model
- [Backlog Commands](backlog-commands.md) - Task management CLI
