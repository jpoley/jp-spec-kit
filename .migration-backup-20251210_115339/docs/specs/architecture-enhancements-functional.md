# Functional Spec: JP Spec Kit Architecture Enhancements

**Related Tasks**: task-079, task-081, task-083, task-084, task-086, task-182, task-243, task-244, task-245, task-246
**PRD Reference**: `docs/prd/architecture-enhancements-prd.md`

---

## Requirements Traceability Matrix

| Task ID | Functional Requirements | Test Scenarios |
|---------|------------------------|----------------|
| task-079 | FR-STACK-001 to FR-STACK-005 | TS-STACK-* |
| task-081 | FR-PLUGIN-001 to FR-PLUGIN-004 | TS-PLUGIN-* |
| task-083 | FR-GATE-001 to FR-GATE-006 | TS-GATE-* |
| task-084 | FR-QUALITY-001 to FR-QUALITY-004 | TS-QUALITY-* |
| task-086 | FR-TIER-001 to FR-TIER-003 | TS-TIER-* |
| task-182 | FR-VALID-001 to FR-VALID-003 | TS-VALID-* |
| task-243 | FR-DETECT-001 | TS-DETECT-* |
| task-244 | FR-LLM-001 to FR-LLM-004 | TS-LLM-* |
| task-245 | FR-GUIDE-001, FR-GUIDE-002 | TS-GUIDE-* |
| task-246 | FR-TEST-001 | TS-TEST-* |

---

## Overview

This functional specification defines behaviors for 10 architecture enhancement tasks organized into 4 domains: Constitution Tiers, Quality Gates, Plugin Distribution, and Stack Selection.

## Functional Requirements

### FR-TIER: Constitution Tiers (task-086, task-182)

**FR-TIER-001**: Light Tier Support
- **Input**: `specify init --tier light` or `--light`
- **Output**: Constitution with ~50 lines, core non-negotiables only
- **Rules**: Skip research phase, 50/100 quality threshold
- **Errors**: Warn if project complexity suggests higher tier

**FR-TIER-002**: Tier Selection UI
- **Input**: `specify init` (no tier flag)
- **Output**: Interactive prompt with tier descriptions
- **Rules**: Default to medium tier, show team size guidance
- **Errors**: Fall back to medium if stdin not available

**FR-TIER-003**: Transition Validation Modes (task-182)
- **Input**: `--validation-mode {NONE|KEYWORD|PULL_REQUEST}`
- **Output**: jpspec_workflow.yml configured with selected mode
- **Rules**: NONE for light tier, KEYWORD for medium, PULL_REQUEST for heavy
- **Errors**: Reject invalid mode for selected tier

### FR-GATE: Quality Gates (task-083)

**FR-GATE-001**: Spec Completeness Check
- **Input**: Feature directory path
- **Output**: Pass/fail with list of NEEDS CLARIFICATION markers
- **Rules**: Fail if any unresolved markers found
- **Errors**: List all marker locations with line numbers

**FR-GATE-002**: Required Files Validation
- **Input**: Feature directory path
- **Output**: Pass/fail with missing file list
- **Rules**: Require spec.md, plan.md, tasks.md (tier-dependent)
- **Errors**: List missing files with expected locations

**FR-GATE-003**: Constitutional Compliance
- **Input**: Feature directory + constitution.md
- **Output**: Pass/fail with compliance violations
- **Rules**: Check test-first, task quality, DCO requirements
- **Errors**: List specific violations with remediation steps

**FR-GATE-004**: Quality Threshold
- **Input**: Spec files + tier configuration
- **Output**: Score 0-100, pass/fail based on tier threshold
- **Rules**: Light=50, Medium=70, Heavy=85
- **Errors**: Show score breakdown by dimension

**FR-GATE-005**: Unresolved Markers Detection
- **Input**: All markdown files in feature directory
- **Output**: List of TODO, FIXME, TBD, PLACEHOLDER markers
- **Rules**: Fail if any found in spec files
- **Errors**: List markers with file:line locations

**FR-GATE-006**: Skip Gates Override
- **Input**: `--skip-quality-gates` flag
- **Output**: Bypass gates with audit log entry
- **Rules**: Log user, timestamp, reason to audit trail
- **Errors**: Warn but proceed

### FR-PLUGIN: Plugin Distribution (task-081)

**FR-PLUGIN-001**: Plugin Manifest
- **Input**: Plugin build command
- **Output**: manifest.json with version, commands, agents
- **Rules**: Follow Claude plugin spec
- **Errors**: Validation errors for malformed manifest

**FR-PLUGIN-002**: Command Bundling
- **Input**: .claude/commands/ directory
- **Output**: All /jpspec:* and /speckit:* commands in plugin
- **Rules**: Preserve command arguments and descriptions
- **Errors**: Skip invalid command files with warning

**FR-PLUGIN-003**: Agent Configuration
- **Input**: .agents/ directory
- **Output**: Agent configs in plugin agents/ directory
- **Rules**: Include all SDD workflow agents
- **Errors**: Warn on missing required agents

**FR-PLUGIN-004**: Update Isolation
- **Input**: Plugin update
- **Output**: Updated commands/agents, unchanged project files
- **Rules**: Never modify user's memory/, docs/, backlog/
- **Errors**: Abort update if project files would change

### FR-STACK: Stack Selection (task-079)

**FR-STACK-001**: Interactive Selection UI
- **Input**: `specify init` (no --stack flag)
- **Output**: Arrow-key navigable stack list
- **Rules**: Show stack name, languages, frameworks
- **Errors**: Fall back to "ALL STACKS" if terminal not interactive

**FR-STACK-002**: Stack Definitions
- **Input**: STACK_CONFIG in specify-cli
- **Output**: 9 predefined stacks with file lists
- **Rules**: Include React+Go, React+Python, Full-Stack TS, etc.
- **Errors**: N/A (static configuration)

**FR-STACK-003**: Conditional Scaffolding
- **Input**: Selected stack ID
- **Output**: Only selected stack's template files copied
- **Rules**: Remove unselected stack files from output
- **Errors**: Warn if selected stack missing expected files

**FR-STACK-004**: CI/CD Workflow Selection
- **Input**: Selected stack ID
- **Output**: Stack-specific workflow in .github/workflows/
- **Rules**: Match CI to stack's languages/frameworks
- **Errors**: Use generic workflow if stack-specific missing

**FR-STACK-005**: Non-Interactive Mode
- **Input**: `--stack <id>` flag
- **Output**: Direct stack selection without prompt
- **Rules**: Support `--stack all` and `--no-stack`
- **Errors**: Error if invalid stack ID provided

### FR-DETECT: Existing Project Detection (task-243)

**FR-DETECT-001**: Project Detection
- **Input**: Target directory
- **Output**: Boolean: is existing project
- **Rules**: Check for .git, package.json, pyproject.toml, go.mod
- **Errors**: N/A (detection always succeeds)

### FR-LLM: Constitution Customization (task-244)

**FR-LLM-001**: Repository Scanning
- **Input**: Repository root path
- **Output**: Detected languages, frameworks, CI configs, patterns
- **Rules**: Scan package.json, pyproject.toml, .github/workflows/
- **Errors**: Continue with defaults if scan fails

**FR-LLM-002**: Pattern Detection
- **Input**: Repository files
- **Output**: Existing patterns (testing, security, review)
- **Rules**: Detect pytest, jest, ESLint, Semgrep configs
- **Errors**: Assume no patterns if detection fails

**FR-LLM-003**: Template Customization
- **Input**: Tier template + detected patterns
- **Output**: Customized constitution.md
- **Rules**: Insert repo-specific sections, preserve core non-negotiables
- **Errors**: Fall back to base template if customization fails

**FR-LLM-004**: Validation Markers
- **Input**: LLM-generated sections
- **Output**: NEEDS_VALIDATION markers on auto-generated content
- **Rules**: Mark all LLM additions for human review
- **Errors**: N/A (always add markers)

### FR-GUIDE: Validation Guidance (task-245)

**FR-GUIDE-001**: Validation Prompts
- **Input**: Constitution with NEEDS_VALIDATION markers
- **Output**: Interactive prompts for each marker
- **Rules**: Show context, ask for confirmation/edit
- **Errors**: Skip marker if user cancels

**FR-GUIDE-002**: Guidance Documentation
- **Input**: Constitution template
- **Output**: Inline comments explaining each section
- **Rules**: Explain purpose, customization options, examples
- **Errors**: N/A (static documentation)

### FR-TEST: Integration Tests (task-246)

**FR-TEST-001**: Template System Tests
- **Input**: Test suite execution
- **Output**: Pass/fail for tier combinations
- **Rules**: Test light/medium/heavy tiers, customization, validation
- **Errors**: Detailed failure messages with reproduction steps

### FR-QUALITY: Spec Quality Metrics (task-084)

**FR-QUALITY-001**: Quality Scoring
- **Input**: Spec file path
- **Output**: Score 0-100 with dimension breakdown
- **Rules**: 5 dimensions: completeness, clarity, traceability, testability, scoping
- **Errors**: Explain low-scoring dimensions

**FR-QUALITY-002**: Grade Assignment
- **Input**: Quality score
- **Output**: Letter grade A/B/C/D/F
- **Rules**: A=90+, B=80+, C=70+, D=60+, F=<60
- **Errors**: N/A

**FR-QUALITY-003**: Remediation Suggestions
- **Input**: Low-scoring dimensions
- **Output**: Specific improvement suggestions
- **Rules**: Actionable, dimension-specific advice
- **Errors**: Generic advice if specific unavailable

**FR-QUALITY-004**: JSON Output
- **Input**: `--json` flag
- **Output**: Machine-readable quality report
- **Rules**: Include score, grade, dimensions, suggestions
- **Errors**: Valid JSON even on scoring failure

## Use Cases

### UC-1: Solo Developer Quick Start
**Actor**: Solo developer
**Preconditions**: Empty directory, specify CLI installed
**Flow**:
1. Run `specify init --light`
2. Select stack (or skip)
3. Constitution created with light tier
4. Begin spec-driven development
**Postconditions**: Project initialized with minimal overhead

### UC-2: Quality Gate Enforcement
**Actor**: Developer running /jpspec:implement
**Preconditions**: Feature with spec files
**Flow**:
1. Run `/jpspec:implement`
2. Gates 1-5 run automatically
3. If pass: proceed to implementation
4. If fail: show errors with remediation
**Postconditions**: Implementation only starts with quality specs

### UC-3: Plugin Installation
**Actor**: Claude Code user
**Preconditions**: Claude Code installed
**Flow**:
1. Search "JP Spec Kit" in marketplace
2. Click Install
3. Commands available immediately
**Postconditions**: /jpspec:* commands ready to use

### UC-4: LLM Constitution Customization
**Actor**: Existing repo owner
**Preconditions**: Existing repo without constitution
**Flow**:
1. Run `/speckit:constitution`
2. LLM scans repo, detects patterns
3. Presents customized constitution
4. User reviews NEEDS_VALIDATION markers
5. Confirms or edits
**Postconditions**: Repo-specific constitution created
