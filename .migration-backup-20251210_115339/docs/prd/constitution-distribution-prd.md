# PRD: Constitution Distribution to Target Repositories

**Status**: Draft
**Owner**: @pm-planner
**Created**: 2025-12-04
**Last Updated**: 2025-12-04

## Executive Summary

### Problem Statement

JP Spec Kit has a comprehensive constitution (`memory/constitution.md`) that defines critical workflow rules, artifact progression, task quality standards, and development practices. However, this constitution currently exists **only in the jp-spec-kit repository itself**, not in the target repositories that use JP Spec Kit.

This creates a fundamental problem:
- **Workflow rules are invisible** to projects using JP Spec Kit
- **No guidance for users** on artifact progression (PRD → Functional Spec → Technical Spec → ADR → Implementation → Runbook)
- **Workflow mode variations** (light/medium/heavy) are not documented in target repos
- **Committer skill separation** and git commit requirements exist only in jp-spec-kit
- **Task quality standards** (acceptance criteria required) are not enforced in target projects
- **LLM agents lack context** on the project's specific workflow and quality standards

### Solution Overview

Distribute tiered constitution templates (light/medium/heavy) to target repositories during `specify init` and `specify upgrade`, with LLM-powered customization based on repository analysis. The constitution becomes the **single source of truth** for workflow rules, quality standards, and development practices in each project.

### Success Metrics

1. **100% constitution coverage**: Every project initialized with `specify init` has a constitution
2. **Existing project detection**: `specify upgrade` detects and prompts for constitution in repos without one
3. **Tier-appropriate selection**: Users choose appropriate tier (light/medium/heavy) for their project type
4. **LLM customization accuracy**: 90%+ of auto-detected repo facts are correct (languages, frameworks, CI configs)
5. **User validation**: Clear NEEDS_VALIDATION markers guide users to review/approve auto-generated content
6. **Constitution compliance**: /jpspec commands check for constitution existence before executing

## Background

### What Already Exists

**Three Constitution Templates** (task-241 ✅ DONE):
- `templates/constitutions/constitution-light.md` - Minimal controls (startups/hobby projects)
- `templates/constitutions/constitution-medium.md` - Standard controls (typical business)
- `templates/constitutions/constitution-heavy.md` - Strict controls (enterprise/regulated)

All templates have:
- SECTION markers for LLM-targeted customization
- NEEDS_VALIDATION comments for user review
- Placeholder tokens: `[PROJECT_NAME]`, `[LANGUAGES_AND_FRAMEWORKS]`, `[LINTING_TOOLS]`, `[DATE]`

**--constitution flag** (task-242 ✅ DONE):
- `specify init my-project --constitution medium` works
- Templates embedded in `__init__.py` (CONSTITUTION_TEMPLATES dict)
- Interactive selection with arrow keys when flag omitted
- Writes to `memory/constitution.md` in target project

### What Needs to Be Built

1. **Existing project detection** - Detect repos without constitution during `specify init --here` or `specify upgrade`
2. **LLM customization command** - `/speckit:constitution` slash command to analyze repo and customize template
3. **Validation workflow** - Help users review and approve NEEDS_VALIDATION sections
4. **Constitution enforcement** - /jpspec commands verify constitution exists and is validated

### Current User Flow (task-241 + task-242)

```bash
# New project - constitution selection works
specify init my-project --constitution medium
# Result: memory/constitution.md created with medium template

# Existing project - NO constitution handling yet
cd existing-repo
specify init --here
# Result: Constitution NOT created, workflow rules NOT distributed
```

## User Stories

### US-1: New Project Initialization

**As a** developer creating a new project
**I want** to select a constitution tier during `specify init`
**So that** my project has clear workflow rules from day one

**Acceptance Criteria**:
- When I run `specify init my-project`, I'm prompted to select tier (light/medium/heavy)
- When I run `specify init my-project --constitution medium`, tier is pre-selected
- Constitution is written to `memory/constitution.md` with appropriate tier template
- LLM customization can be triggered immediately or deferred to `/speckit:constitution`

### US-2: Existing Project Without Constitution

**As a** developer running `specify init --here` or `specify upgrade` on an existing repo
**I want** to be prompted to add a constitution
**So that** my existing project can benefit from workflow rules and standards

**Acceptance Criteria**:
- CLI detects existing project (`.git`, `package.json`, `pyproject.toml`, etc. exist)
- CLI checks for `memory/constitution.md` existence
- If missing, prompts: "No constitution found. Select tier: light/medium/heavy"
- After tier selection, triggers LLM customization flow
- If constitution exists, skip creation (no duplicate/overwrite)

### US-3: Existing Project With Constitution

**As a** developer running `specify upgrade` on a repo with a constitution
**I want** the constitution to be preserved
**So that** my custom rules and amendments are not lost

**Acceptance Criteria**:
- CLI detects existing `memory/constitution.md`
- CLI skips constitution creation
- CLI outputs: "Constitution already exists at memory/constitution.md"
- No prompt for tier selection
- No automatic overwriting

### US-4: LLM Constitution Customization

**As a** developer who selected a constitution tier
**I want** the LLM to analyze my repo and customize the template
**So that** my constitution reflects my actual tech stack and practices

**Acceptance Criteria**:
- Command: `/speckit:constitution` or automatic after tier selection
- LLM scans repo for: languages, frameworks, linting tools, CI configs, test setup, security scanning
- LLM detects existing patterns: code review requirements, branch protection, etc.
- LLM fills in placeholders: `[PROJECT_NAME]`, `[LANGUAGES_AND_FRAMEWORKS]`, `[LINTING_TOOLS]`, `[DATE]`
- LLM adds NEEDS_VALIDATION markers on auto-generated sections
- Output: "Constitution generated - please review NEEDS_VALIDATION sections"

### US-5: Constitution Validation Workflow

**As a** developer with a newly generated constitution
**I want** clear guidance on what to review and validate
**So that** I can approve the auto-generated content confidently

**Acceptance Criteria**:
- After constitution generation, CLI outputs validation checklist
- Checklist highlights sections with NEEDS_VALIDATION markers
- Command: `specify constitution validate` checks for unvalidated sections
- Output shows: Section name, auto-detected value, validation status
- Users can validate by removing NEEDS_VALIDATION comments manually

### US-6: Constitution Enforcement in Workflow

**As a** developer running `/jpspec` commands
**I want** to be reminded if my constitution has unvalidated sections
**So that** I don't start work based on incorrect assumptions

**Acceptance Criteria**:
- Before executing `/jpspec:specify`, `/jpspec:plan`, etc., check for constitution
- If `memory/constitution.md` missing, warn: "No constitution found - run `specify constitution create`"
- If NEEDS_VALIDATION markers present, warn: "Constitution has unvalidated sections - run `specify constitution validate`"
- User can proceed with `--skip-validation` flag (not recommended)

## DVF+V Risk Assessment

### Desirability Risk: Will users value this?

**Risk Level**: LOW

**Evidence**:
- Users have explicitly requested constitution distribution (user request in this session)
- Constitution contains critical workflow rules (artifact progression, git requirements, task quality)
- Without constitution, users lack guidance on how to use JP Spec Kit correctly

**Mitigation**:
- Make constitution creation opt-in with clear value proposition
- Provide examples of how constitution improves workflow clarity
- Default to light tier for minimal friction

### Usability Risk: Can users successfully use this?

**Risk Level**: MEDIUM

**Concerns**:
- LLM customization may generate incorrect facts
- NEEDS_VALIDATION markers may be unclear
- Validation workflow may be tedious

**Mitigation**:
- Clear NEEDS_VALIDATION format: `<!-- NEEDS_VALIDATION: What to check -->`
- Validation checklist output after generation
- Simple validation command: `specify constitution validate`
- Detailed documentation: `docs/guides/constitution-validation.md`

### Feasibility Risk: Can we build this?

**Risk Level**: LOW

**Evidence**:
- Templates already exist (task-241 ✅)
- --constitution flag works (task-242 ✅)
- LLM integration already exists in JP Spec Kit (slash commands use Claude)
- Detection logic straightforward (check file existence)

**Technical Challenges**:
- LLM prompt engineering for accurate repo analysis
- Handling edge cases (monorepos, multi-language repos)
- Avoiding overwriting user-amended constitutions

**Mitigation**:
- Conservative detection (only override with explicit user confirmation)
- LLM prompt includes examples of good constitution customization
- NEEDS_VALIDATION markers force user review

### Viability Risk: Should we build this?

**Risk Level**: LOW

**Strategic Alignment**:
- Constitution is core to Spec-Driven Development
- Distribution to target repos is essential for adoption
- Tiered approach supports multiple user segments (startup/business/enterprise)

**Concerns**:
- Maintenance burden of three template variants
- Constitution versioning and upgrades

**Mitigation**:
- Templates share common NON-NEGOTIABLE sections (single source of truth)
- Constitution versions tracked (e.g., 1.0.0, 1.1.0)
- `specify upgrade` can offer constitution updates

## Functional Requirements

### FR-1: Constitution Template Selection

**Description**: Users select light/medium/heavy tier during project initialization.

**Inputs**:
- `--constitution {light|medium|heavy}` flag (optional)
- Interactive prompt if flag omitted

**Outputs**:
- Selected tier stored for subsequent operations
- Constitution template copied to `memory/constitution.md`

**Business Rules**:
- If flag provided, skip prompt
- If flag omitted, show interactive selector with descriptions:
  - Light: Minimal controls (startups/hobby projects)
  - Medium: Standard controls (typical business projects)
  - Heavy: Strict controls (enterprise/regulated environments)
- Default to light if user provides no input

**Error Conditions**:
- Invalid tier value → show error, list valid options
- `memory/` directory creation fails → show error, abort

### FR-2: Existing Project Detection

**Description**: Detect existing projects without constitution during `specify init --here` or `specify upgrade`.

**Inputs**:
- Current working directory
- File system checks: `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`

**Outputs**:
- Boolean: is_existing_project
- Boolean: has_constitution (checks `memory/constitution.md`)

**Business Rules**:
- Project is "existing" if ANY of: `.git/`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` exists
- Constitution exists if `memory/constitution.md` is present
- If existing project AND no constitution → trigger constitution creation flow
- If constitution exists → skip creation, preserve existing

**Error Conditions**:
- File system read errors → log warning, assume no existing project

### FR-3: LLM Constitution Customization

**Description**: `/speckit:constitution` slash command analyzes repo and customizes template.

**Inputs**:
- Selected tier (light/medium/heavy)
- Repository file system
- Git metadata (if available)

**Outputs**:
- Customized `memory/constitution.md` with:
  - `[PROJECT_NAME]` replaced (from git remote or directory name)
  - `[LANGUAGES_AND_FRAMEWORKS]` filled (detected from file extensions, config files)
  - `[LINTING_TOOLS]` filled (detected from package.json, pyproject.toml, pre-commit config)
  - `[DATE]` filled (current date)
  - NEEDS_VALIDATION markers added for auto-generated sections

**Detection Rules**:

| Fact | Detection Method |
|------|------------------|
| Project Name | Git remote URL > directory name |
| Languages | File extensions (.py → Python, .ts → TypeScript, .go → Go, .rs → Rust) |
| Frameworks | package.json dependencies, requirements.txt, Cargo.toml, go.mod |
| Linting Tools | ruff, eslint, prettier, golangci-lint in configs |
| CI/CD | .github/workflows/, .gitlab-ci.yml, Jenkinsfile |
| Testing | pytest, jest, go test, cargo test in configs |
| Security Scanning | semgrep, trivy, snyk, bandit in CI or pre-commit |

**Business Rules**:
- If detection fails for a section, leave placeholder with NEEDS_VALIDATION marker
- If multiple languages detected, list all
- If no linting tools detected, suggest adding them
- Auto-generated sections MUST have NEEDS_VALIDATION markers

**Error Conditions**:
- LLM timeout → use template placeholders, warn user
- Detection errors → log, continue with partial results

### FR-4: Constitution Validation Command

**Description**: `specify constitution validate` checks for unvalidated sections.

**Inputs**:
- `memory/constitution.md` file

**Outputs**:
- Validation checklist showing:
  - Section name
  - Auto-detected value
  - Validation status (✓ Validated / ⚠ Needs Validation)
- Summary: "X sections validated, Y need review"

**Business Rules**:
- Section "needs validation" if it contains `<!-- NEEDS_VALIDATION: ... -->`
- Validation complete when all NEEDS_VALIDATION markers removed
- Users validate by manually reviewing and removing markers

**Error Conditions**:
- Constitution missing → error: "No constitution found - run `specify constitution create`"
- Malformed constitution → warn user, list parsing errors

### FR-5: Constitution Enforcement in /jpspec Commands

**Description**: /jpspec commands verify constitution exists and is validated before execution.

**Inputs**:
- Current working directory
- `memory/constitution.md` existence
- NEEDS_VALIDATION marker count

**Outputs**:
- Warning if constitution missing or unvalidated
- Proceed/abort decision

**Business Rules**:
- If constitution missing → warn: "No constitution found - run `specify constitution create`"
- If NEEDS_VALIDATION markers present → warn: "Constitution has X unvalidated sections - run `specify constitution validate`"
- User can proceed with `--skip-validation` flag (not recommended)
- Light tier: warning only, can proceed (feature branches encouraged, "yolo mode" allowed)
- Medium tier: warning + confirmation prompt (feature branches required)
- Heavy tier: hard block, cannot proceed without validation (protected branches, 2+ reviewers)

**Error Conditions**:
- Constitution read error → treat as missing

## Non-Functional Requirements

### NFR-1: Performance

- Constitution template selection: < 500ms
- Existing project detection: < 1 second
- LLM constitution customization: < 30 seconds
- Constitution validation check: < 500ms

### NFR-2: Reliability

- Constitution creation must be atomic (all-or-nothing)
- Never overwrite existing constitution without explicit user confirmation
- LLM customization failures must not corrupt constitution file
- Template syntax must be valid markdown

### NFR-3: Usability

- Clear prompts and error messages
- Interactive selector with arrow keys and descriptions
- Validation checklist output is human-readable
- NEEDS_VALIDATION markers are self-explanatory

### NFR-4: Security

- LLM customization does not execute arbitrary code
- Repo scanning only reads files, never modifies
- No secrets or credentials included in constitution
- Constitution validation does not expose sensitive data

### NFR-5: Compatibility

- Works with Python 3.11+
- Cross-platform (Linux, macOS, Windows)
- Compatible with existing `specify init` workflows
- Does not break existing projects using `specify upgrade`

### NFR-6: Maintainability

- Templates are separate files in `templates/constitutions/`
- Embedded templates in `__init__.py` generated from separate files
- LLM prompts are modular and testable
- Constitution version tracking for future upgrades

## Task Breakdown

### Design & Architecture Tasks

**Task: Constitution Detection Architecture Design**
- Owner: @pm-planner
- Description: Design the detection logic for existing projects and constitution presence
- Acceptance Criteria:
  - Define detection rules for existing projects
  - Define file system checks for constitution existence
  - Design user flow diagrams for all scenarios
  - Document decision tree for constitution creation

**Task: LLM Customization Prompt Design**
- Owner: @pm-planner
- Description: Design LLM prompts for repo analysis and constitution customization
- Acceptance Criteria:
  - Prompt template for repo scanning
  - Prompt template for fact extraction (languages, frameworks, tools)
  - Prompt template for constitution content generation
  - Example inputs and expected outputs

**Task: Constitution Validation UX Design**
- Owner: @pm-planner
- Description: Design validation workflow and CLI output
- Acceptance Criteria:
  - Validation checklist format
  - NEEDS_VALIDATION marker format
  - CLI command structure: `specify constitution validate`
  - User guidance text for validation

### Implementation Tasks (Already Created - Update if Needed)

**task-243: Detect existing projects without constitution** (✅ Already Created)
- Status: To Do
- Owner: @kinsale
- Current ACs cover FR-2 requirements
- **NO CHANGES NEEDED**

**task-244: Implement /speckit:constitution LLM customization command** (✅ Already Created)
- Status: To Do
- Owner: @kinsale
- Current ACs cover FR-3 requirements
- **Suggest adding**:
  - AC: Command outputs validation checklist after generation
  - AC: Command supports --tier override flag

**task-245: Add constitution validation guidance and user prompts** (✅ Already Created)
- Status: To Do
- Owner: @kinsale
- Current ACs cover FR-4 and FR-5 requirements
- **NO CHANGES NEEDED**

**task-246: Integration tests for constitution template system** (✅ Already Created)
- Status: To Do
- Owner: @kinsale
- Current ACs adequate
- **NO CHANGES NEEDED**

### New Implementation Tasks (To Be Created)

**Task: Constitution Enforcement in /jpspec Commands**
- Description: Add constitution checks to all /jpspec slash commands
- Acceptance Criteria:
  - Before command execution, check `memory/constitution.md` existence
  - Check for NEEDS_VALIDATION markers
  - Warn if missing or unvalidated
  - Respect tier-specific enforcement (light = warn, medium = confirm, heavy = block)
  - Add `--skip-validation` flag for emergencies
- Labels: slash-command, constitution, validation
- Priority: High
- Dependencies: task-245

**Task: Constitution Version Tracking**
- Description: Add version field to constitution and track changes over time
- Acceptance Criteria:
  - Constitution includes Version, Ratified Date, Last Amended fields
  - `specify constitution version` shows current version
  - `specify upgrade` detects outdated constitutions
  - Upgrade flow prompts user: "Constitution 1.0.0 available, you have 0.9.0. Upgrade?"
- Labels: constitution, versioning, upgrade
- Priority: Medium
- Dependencies: task-244

**Task: Constitution Diff and Merge Tool**
- Description: Help users merge constitution updates with their custom amendments
- Acceptance Criteria:
  - `specify constitution diff` shows changes between user's constitution and latest template
  - `specify constitution merge` runs interactive merge tool
  - Preserve NON-NEGOTIABLE sections from template
  - Preserve user amendments in custom sections
  - Output merged constitution to `memory/constitution-merged.md` for review
- Labels: constitution, upgrade, tooling
- Priority: Low
- Dependencies: task-244, Constitution Version Tracking

**Task: Memory Bank Integration for Repo Facts**
- Description: Store detected repo facts in `memory/repo-facts.md` for LLM context
- Acceptance Criteria:
  - `/speckit:constitution` writes findings to `memory/repo-facts.md`
  - Format: YAML frontmatter + markdown sections
  - Facts include: languages, frameworks, linting tools, CI/CD, test setup, security tools
  - LLM agents can reference repo-facts.md for context in other commands
  - `specify init` and `specify upgrade` update repo-facts.md
- Labels: memory, llm-context, constitution
- Priority: Medium
- Dependencies: task-244

### Documentation Tasks

**Task: Constitution Distribution User Guide**
- Description: Comprehensive guide on constitution setup, validation, and maintenance
- Acceptance Criteria:
  - Guide covers: tier selection, LLM customization, validation workflow, enforcement
  - Includes examples for each tier (light/medium/heavy)
  - Explains NEEDS_VALIDATION markers
  - Provides validation checklist example
  - Documents `specify constitution` subcommands
- Location: `docs/guides/constitution-distribution.md`
- Labels: docs, constitution
- Priority: High
- Dependencies: task-244, task-245

**Task: Constitution Customization Examples**
- Description: Real-world examples of customized constitutions
- Acceptance Criteria:
  - Example: Python project with pytest, ruff, GitHub Actions
  - Example: TypeScript project with jest, eslint, prettier
  - Example: Go project with golangci-lint, Go modules
  - Example: Rust project with cargo, clippy
  - Each example shows before/after LLM customization
- Location: `docs/examples/constitutions/`
- Labels: docs, examples, constitution
- Priority: Medium
- Dependencies: task-244

**Task: Constitution Troubleshooting Guide**
- Description: Help users resolve common constitution issues
- Acceptance Criteria:
  - Issue: LLM generated incorrect language detection
  - Issue: Constitution validation stuck on unresolvable NEEDS_VALIDATION
  - Issue: /jpspec command blocked by unvalidated constitution
  - Issue: Constitution version mismatch after upgrade
  - Each issue includes symptoms, cause, resolution
- Location: `docs/guides/constitution-troubleshooting.md`
- Labels: docs, troubleshooting, constitution
- Priority: Medium
- Dependencies: task-244, task-245

### Testing Tasks

**Task: LLM Customization Accuracy Tests**
- Description: Verify LLM customization generates correct repo facts
- Acceptance Criteria:
  - Test Python project: detects pytest, ruff, GitHub Actions
  - Test TypeScript project: detects jest, eslint, prettier, npm/pnpm
  - Test Go project: detects go test, golangci-lint, Go modules
  - Test multi-language project: detects all languages correctly
  - Test edge case: empty repo with only README
  - Accuracy target: 90%+ correct detections
- Labels: testing, llm, constitution
- Priority: High
- Dependencies: task-244

**Task: Constitution Enforcement Integration Tests**
- Description: Verify /jpspec commands enforce constitution checks
- Acceptance Criteria:
  - Test light tier: /jpspec:specify warns but proceeds
  - Test medium tier: /jpspec:specify prompts for confirmation
  - Test heavy tier: /jpspec:specify blocks execution
  - Test --skip-validation flag bypasses checks
  - Test unvalidated constitution triggers validation warning
- Labels: testing, integration-tests, constitution
- Priority: High
- Dependencies: Constitution Enforcement in /jpspec Commands

## Discovery and Validation Plan

### Phase 1: Template Strategy Validation (Week 1)

**Question**: Should we keep 3 separate complete templates, or use base + overlays?

**Options**:
1. **Current approach**: 3 complete templates (light/medium/heavy)
2. **Base + overlays**: Single base template + tier-specific sections
3. **Modular composition**: Reusable section components that compose into tiers

**Validation Method**:
- Create ADR comparing approaches
- Prototype overlay system
- Measure maintenance burden (lines changed per constitution update)
- User feedback: which is easier to understand?

**Decision Criteria**:
- Maintainability: How many files change per constitution update?
- Clarity: Can users understand tier differences easily?
- Extensibility: Can we add tier 4 (ultra-heavy) later?

**Recommendation**: **Keep 3 complete templates** (current approach)

**Rationale**:
- Users see complete constitution in one file (no mental composition required)
- Tier differences are explicit and obvious
- Maintenance overhead is low (NON-NEGOTIABLE sections are copy-paste across tiers)
- Embedded templates in `__init__.py` work cleanly

### Phase 2: LLM Customization Timing (Week 2)

**Question**: When should LLM customization happen?

**Options**:
1. **During `specify init`** (user waits for LLM)
2. **After `specify init` via `/speckit:constitution`** (async, user triggers manually)
3. **Both**: Auto-trigger during init, allow manual re-run later

**Validation Method**:
- Prototype both flows
- Measure LLM response time (target: < 30 seconds)
- User testing: which flow feels better?
- Test network failure scenarios

**Decision Criteria**:
- User friction: Does waiting for LLM block getting started?
- Accuracy: Does LLM have enough context during init?
- Flexibility: Can users re-run customization later?

**Recommendation**: **Both approaches** (Option 3)

**Rationale**:
- Default: Auto-trigger during `specify init` for best first-run experience
- Fallback: Manual `/speckit:constitution` for re-customization or init failures
- Add `--skip-llm` flag to `specify init` for users who want to customize manually later

### Phase 3: Existing Repo Detection Strategy (Week 3)

**Question**: What triggers constitution creation in existing repos?

**Triggers**:
1. `specify init --here` (initializing in current directory)
2. `specify upgrade` (updating JP Spec Kit)
3. Any `/jpspec` command when constitution missing (just-in-time)

**Validation Method**:
- User interviews: When do they expect constitution to be created?
- Test scenarios:
  - New contributor clones repo without constitution
  - Existing project adds JP Spec Kit
  - Project created before constitution feature existed

**Decision Criteria**:
- User expectations: When should constitution appear?
- Discoverability: Will users know to create constitution?
- Backwards compatibility: Will old projects break?

**Recommendation**: **Triggers 1 & 2 create constitution; Trigger 3 warns only**

**Rationale**:
- `specify init --here` is explicit initialization → create constitution
- `specify upgrade` is maintenance operation → safe to add constitution
- `/jpspec` commands failing is surprising → warn, don't auto-create
- Users can manually run `specify constitution create` if needed

### Phase 4: Memory Bank Integration (Week 4)

**Question**: Should we use `memory/` for storing repo facts?

**Options**:
1. **Store in `memory/repo-facts.md`** (persistent, version-controlled)
2. **Store in `.specify/cache/repo-facts.json`** (ephemeral cache, not version-controlled)
3. **Don't store, re-detect on every LLM customization**

**Validation Method**:
- Prototype repo-facts.md format
- Test LLM context usage in other /jpspec commands
- Measure detection speed (re-detect vs cached)
- User feedback: is repo-facts.md useful to read?

**Decision Criteria**:
- Performance: How much faster is cached detection?
- LLM context: Do other agents benefit from repo-facts.md?
- Version control: Should repo facts be tracked in git?

**Recommendation**: **Store in `memory/repo-facts.md`** (Option 1)

**Rationale**:
- Persistent facts help LLM agents in all /jpspec commands
- Version-controlled facts track project evolution over time
- Human-readable markdown format allows manual edits
- `memory/` is already the designated location for project memory

### Phase 5: Validation Workflow (Week 5)

**Question**: How should users validate NEEDS_VALIDATION sections?

**Options**:
1. **Manual removal** of NEEDS_VALIDATION markers (current plan)
2. **Interactive CLI** (`specify constitution validate --interactive`)
3. **IDE extension** (VSCode/Cursor plugin for guided validation)

**Validation Method**:
- User testing: complete validation workflow
- Measure time to validate (target: < 5 minutes)
- Track validation abandonment rate

**Decision Criteria**:
- Ease of use: How easy is validation?
- Accuracy: Do users validate correctly?
- Friction: Does validation feel tedious?

**Recommendation**: **Start with Manual removal** (Option 1), **Add Interactive CLI** later (Option 2)

**Rationale**:
- Manual removal is simple, requires no new UI
- Interactive CLI is good enhancement for v2
- IDE extension is overengineering for MVP

## Acceptance Criteria

### AC-1: Constitution Template Distribution

- [ ] `specify init my-project` prompts for constitution tier (light/medium/heavy)
- [ ] `specify init my-project --constitution medium` pre-selects tier, skips prompt
- [ ] Constitution written to `memory/constitution.md` in target project
- [ ] All three tiers available and selectable

### AC-2: Existing Project Detection

- [ ] `specify init --here` detects existing project (checks .git, package.json, etc.)
- [ ] If `memory/constitution.md` missing, prompts for tier selection
- [ ] If `memory/constitution.md` exists, skips creation, preserves existing
- [ ] `specify upgrade` triggers same detection logic

### AC-3: LLM Constitution Customization

- [ ] `/speckit:constitution` slash command analyzes repo
- [ ] Command detects: languages, frameworks, linting tools, CI/CD, testing
- [ ] Command customizes template with detected facts
- [ ] Command adds NEEDS_VALIDATION markers on auto-generated sections
- [ ] Command outputs: "Constitution generated - please review NEEDS_VALIDATION sections"
- [ ] Command supports `--tier {light|medium|heavy}` override flag

### AC-4: Constitution Validation

- [ ] `specify constitution validate` checks for NEEDS_VALIDATION markers
- [ ] Command outputs validation checklist showing sections needing review
- [ ] Command summarizes: "X sections validated, Y need review"
- [ ] Users validate by manually removing NEEDS_VALIDATION markers

### AC-5: Constitution Enforcement

- [ ] /jpspec commands check `memory/constitution.md` existence before execution
- [ ] If missing, warn: "No constitution found - run `specify constitution create`"
- [ ] If NEEDS_VALIDATION markers present, warn: "Constitution has X unvalidated sections"
- [ ] Light tier: warning only (can proceed)
- [ ] Medium tier: warning + confirmation prompt
- [ ] Heavy tier: hard block (cannot proceed)
- [ ] `--skip-validation` flag bypasses checks

### AC-6: Documentation and Examples

- [ ] User guide: `docs/guides/constitution-distribution.md` exists and complete
- [ ] Examples: `docs/examples/constitutions/` contains real-world customized constitutions
- [ ] Troubleshooting: `docs/guides/constitution-troubleshooting.md` exists
- [ ] CLAUDE.md references constitution distribution feature

### AC-7: Testing Coverage

- [ ] Unit tests for constitution detection logic
- [ ] Integration tests for `specify init --here` with/without existing constitution
- [ ] LLM customization accuracy tests (90%+ correct detections)
- [ ] Constitution enforcement tests for all /jpspec commands
- [ ] Edge case tests: empty repo, multi-language, monorepo

## Dependencies and Constraints

### Dependencies

**Completed Tasks**:
- ✅ task-241: Constitution templates created
- ✅ task-242: --constitution flag implemented

**In-Progress Tasks**:
- ⏳ task-243: Detect existing projects without constitution
- ⏳ task-244: Implement /speckit:constitution LLM customization
- ⏳ task-245: Constitution validation guidance
- ⏳ task-246: Integration tests

**External Dependencies**:
- Claude LLM API (for constitution customization)
- File system access (for repo scanning)
- Git (for project detection and version control)

### Constraints

**Technical Constraints**:
- Constitution must be valid markdown
- LLM customization must complete in < 30 seconds
- Detection logic must be cross-platform (Linux/macOS/Windows)
- No breaking changes to existing `specify init` behavior

**Business Constraints**:
- Must support all three tiers (light/medium/heavy) equally
- Cannot overwrite user-amended constitutions without confirmation
- Must work with existing projects (backwards compatible)

**Design Constraints**:
- Constitution location: `memory/constitution.md` (established convention)
- Template format: Markdown with HTML comments for markers
- Validation workflow: User-driven (not automated approval)

## Success Metrics

### Adoption Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Constitution coverage (new projects) | 100% | Track `specify init` runs with constitution creation |
| Constitution coverage (existing projects) | 50%+ | Track `specify upgrade` runs with constitution creation |
| Tier distribution | 50% light, 35% medium, 15% heavy | Track tier selection telemetry |

### Quality Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| LLM customization accuracy | 90%+ | Manual review of 100 generated constitutions |
| Validation completion rate | 80%+ | Track NEEDS_VALIDATION marker removal |
| User satisfaction | 4.0+ / 5.0 | Post-feature survey |

### Operational Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Constitution generation time | < 30s | Measure LLM response time |
| Detection logic time | < 1s | Measure file system checks |
| Support tickets (constitution issues) | < 5 / month | Track GitHub issues with `constitution` label |

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)

**Goals**:
- Complete task-243: Existing project detection
- Complete task-244: LLM customization command
- Basic validation workflow

**Deliverables**:
- `specify init --here` detects and prompts for constitution
- `/speckit:constitution` generates customized constitution
- NEEDS_VALIDATION markers in output

### Phase 2: Enforcement (Week 3)

**Goals**:
- Add constitution checks to all /jpspec commands
- Implement tier-specific enforcement (light/medium/heavy)
- Add `--skip-validation` flag

**Deliverables**:
- /jpspec commands enforce constitution existence
- Tier-appropriate warnings/blocks
- User can bypass with flag

### Phase 3: Refinement (Week 4)

**Goals**:
- Complete task-245: Validation guidance
- Complete task-246: Integration tests
- Memory bank integration (repo-facts.md)

**Deliverables**:
- `specify constitution validate` command
- Comprehensive test suite
- `memory/repo-facts.md` for LLM context

### Phase 4: Documentation (Week 5)

**Goals**:
- User guides and examples
- Troubleshooting documentation
- Real-world constitution examples

**Deliverables**:
- `docs/guides/constitution-distribution.md`
- `docs/examples/constitutions/`
- `docs/guides/constitution-troubleshooting.md`

## Open Questions

1. **Template Versioning**: How do we handle constitution template upgrades?
   - Proposal: Add version field to constitution, track in `specify upgrade`
   - Need: Constitution diff/merge tool for user amendments

2. **Multi-Language Repos**: How do we handle monorepos with multiple languages?
   - Proposal: List all detected languages in constitution
   - Need: Guidance on managing polyglot workflows

3. **Custom Tiers**: Should users be able to create custom tier 4, 5, etc.?
   - Proposal: Allow `--constitution custom` with custom template path
   - Need: Template format documentation

4. **Constitution Governance**: Who approves constitution changes in team settings?
   - Proposal: Constitution has "Approved By" field for team sign-off
   - Need: Workflow for team consensus (beyond scope of this PRD)

5. **LLM Fallback**: What happens if LLM is unavailable during customization?
   - Proposal: Use template placeholders, create issue for manual completion
   - Need: Graceful degradation strategy

## Appendix A: NON-NEGOTIABLE Rules (All Tiers)

These rules MUST appear in all constitution tiers:

1. **Artifact Progression**: PRD → Functional Spec → Technical Spec → ADR → Implementation → Runbook
2. **Implementation = Code + Docs + Tests**: All three required for completion
3. **DCO Sign-off**: `git commit -s` on all commits (automated via git hooks)
4. **PR-Task Synchronization**: PRs reference tasks, tasks reference PRs

Note: Git workflow and task quality rules are tier-specific (see Appendix B).

## Appendix B: Tier-Specific Rules

### Light Tier

- **Git**: Feature branches encouraged. Direct commits to main are allowed ("yolo mode"); PRs are optional.
- **Review**: Code review when time permits
- **Testing**: Tests for critical paths
- **Task Quality**: Acceptance criteria when scope is unclear
- **Enforcement**: Warnings only, can proceed

### Medium Tier

- **Git**: All changes must go through Pull Requests (PRs) via feature branches; direct commits to main are not allowed.
- **Review**: Minimum one reviewer required
- **Testing**: Unit + integration tests, 70% coverage target
- **Task Quality**: Acceptance criteria required on all tasks
- **Enforcement**: Warning + confirmation prompt

### Heavy Tier

- **Git**: Protected branches, minimum 2 reviewers, force push disabled
- **Review**: Minimum two reviewers including one senior engineer
- **Testing**: Unit + integration + E2E tests, 80% coverage minimum, security scans required
- **Task Quality**: Acceptance criteria required on all tasks, with validation gates
- **Enforcement**: Hard block, cannot proceed without validation

## Appendix C: Template Placeholder Tokens

| Token | Description | Example Value |
|-------|-------------|---------------|
| `[PROJECT_NAME]` | Project name from git remote or directory | `my-awesome-app` |
| `[LANGUAGES_AND_FRAMEWORKS]` | Detected languages and frameworks | `Python 3.11, FastAPI, pytest, ruff` |
| `[LINTING_TOOLS]` | Detected linting and formatting tools | `ruff check, ruff format, mypy` |
| `[CI_CD_TOOLS]` | Detected CI/CD configuration | `GitHub Actions (.github/workflows/)` |
| `[COMPLIANCE_FRAMEWORKS]` | Applicable compliance frameworks (heavy tier) | `SOC 2, GDPR, HIPAA` |
| `[DATE]` | Current date in YYYY-MM-DD format | `2025-12-04` |

## Appendix D: NEEDS_VALIDATION Marker Format

```markdown
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
Detected languages: Python 3.11, TypeScript 5.0
Detected frameworks: FastAPI, React
Detected tools: ruff, eslint, prettier
<!-- SECTION:TECH_STACK:END -->
```

**Validation Process**:
1. User reviews auto-detected content
2. If correct, removes `<!-- NEEDS_VALIDATION: ... -->` comment
3. If incorrect, edits content then removes comment
4. Section is "validated" once marker removed

---

**End of PRD**
