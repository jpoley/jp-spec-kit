# Flowspec Upgrade-Repo Architecture Summary

**Date:** 2026-01-06
**Author:** Enterprise Software Architect
**Status:** Proposed
**Related ADRs:** ADR-001, ADR-002, ADR-003

---

## Executive Summary

The `flowspec upgrade-repo` command is **completely broken**, creating a P0 release blocker. This document provides both strategic (business) and tactical (technical) views of the architecture required to fix it.

**Key Problem:** Running `flowspec upgrade-repo` deploys broken templates that don't work with VSCode Copilot, lack MCP configuration, and leave deprecated artifacts.

**Key Solution:** Redesign upgrade-repo as a multi-phase orchestration pipeline with validation gates, version-aware migrations, and comprehensive artifact synchronization.

**Business Impact:**
- **Blocks flowspec release** - Cannot ship until fixed
- **Affects all downstream projects** - auth.poley.dev, lincoln, axonjet, falcondev
- **Erodes user trust** - Upgrade command produces broken output requiring manual fixes

**Timeline:** 14-18 days (sequential) or 8-10 days (2-person parallel)

---

## The Penthouse View: Strategic Architecture

### Business Context

Flowspec is a spec-driven development toolkit that orchestrates AI agents through slash commands (`/flow:assess`, `/flow:specify`, etc.). The `upgrade-repo` command is supposed to keep downstream projects in sync with the latest flowspec templates and configuration.

**The Broken Promise:**

Users expect `flowspec upgrade-repo` to:
1. Update templates to latest versions
2. Configure VSCode Copilot agents correctly
3. Set up MCP servers for agent tool access
4. Remove deprecated files and commands
5. Upgrade workflow configuration to current version

**The Harsh Reality:**

Currently, `upgrade-repo` only does #1 (partially). It leaves projects in a broken state requiring manual fixes:

| What's Broken | Impact | Manual Fix Required |
|---------------|--------|---------------------|
| Agent naming (hyphens vs dots) | VSCode Copilot can't discover agents | Rename 6 files + fix frontmatter |
| Missing `.mcp.json` update | Agents can't access tools (backlog, github) | Create comprehensive MCP config |
| Outdated `flowspec_workflow.yml` | Workflow orchestration uses old v1.0 | Manually upgrade to v2.0 schema |
| Deprecated `.specify/` directory | Pollutes namespace, confuses users | Delete directory manually |
| Broken `{{INCLUDE:}}` directives | Commands fail to load partials | Remove 28+ broken directives |
| `/flow:operate` references | Command was removed, references remain | Global search-and-replace |
| Missing skills | Only 9/21 skills deployed | Copy 12 missing skill files |

**Organizational Impact:**

- **Developer Productivity Loss**: 2-3 hours per project to manually fix post-upgrade
- **Support Burden**: Users require troubleshooting assistance
- **Adoption Risk**: Broken upgrades discourage flowspec usage
- **Release Blocked**: Cannot publish v0.3+ until this works

### Strategic Decision

**Invest in a robust upgrade pipeline now to prevent ongoing pain.**

**Alternatives Rejected:**

1. **Document manual steps** - Scales poorly, error-prone
2. **Minimal fix only** - Half-fixes erode trust
3. **Destructive replace** - Loses user customizations
4. **External tooling (Ansible)** - Heavyweight dependency

**Chosen Approach:**

Build an **in-process multi-phase orchestration pipeline** that:
- Downloads and merges templates (existing behavior)
- **NEW:** Regenerates computed artifacts (MCP config, workflow config)
- **NEW:** Runs version-aware migrations (v1.0 → v2.0)
- **NEW:** Cleans up deprecated files and content
- **NEW:** Validates the result with actionable error messages

### Success Metrics

**After this fix, `flowspec upgrade-repo` will:**

1. ✅ **Work correctly on first run** - Zero manual intervention required
2. ✅ **VSCode integration works** - All 6 agents appear and function
3. ✅ **MCP servers start** - Comprehensive configuration for all required servers
4. ✅ **Workflow orchestration works** - v2.0 config with roles, custom workflows
5. ✅ **Clean state** - No deprecated files or broken references
6. ✅ **Rollback safety** - Timestamped backups enable easy recovery

**Measurable Impact:**

- **Time savings**: 2-3 hours saved per upgrade × 5+ projects = 10-15 hours saved
- **Support reduction**: Eliminate upgrade-related support tickets
- **Adoption increase**: Users trust upgrade process, update more frequently
- **Release unblocked**: Enables flowspec v0.3+ launch

---

## The Engine Room View: Technical Architecture

### Current Implementation

**File:** `src/flowspec_cli/__init__.py` (360KB, lines 5654-5977)

```python
def upgrade_repo(...):
    """Upgrade repository templates."""
    # 1. Detect AI assistant (claude, copilot, cursor)
    # 2. Create backup with timestamp
    # 3. Download base-spec-kit templates from GitHub
    # 4. Download flowspec extension templates from GitHub
    # 5. Merge templates (extension overrides base)
    # 6. Apply to project directory
    # 7. Check backlog-md version
```

**What's Missing:**

The function assumes templates are **static content** that can be blindly copied. This breaks with:

- **Computed artifacts**: `.mcp.json` is tech-stack aware, not static
- **Version migrations**: v1.0 → v2.0 requires semantic transformations
- **Cleanup operations**: Deprecated files must be actively removed
- **Naming conventions**: Agent files need intelligent renaming
- **Content transformations**: Broken directives need search-and-replace

### Proposed Architecture

**5-Phase Orchestration Pipeline:**

```
┌─────────────────────────────────────────────────────────┐
│  Phase 0: Pre-Upgrade Validation                       │
│  - Detect versions, validate structure, create backup  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 1: Template Updates                             │
│  - Download, merge, fix naming, deploy templates       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 2: Configuration Synthesis                      │
│  - Regenerate .mcp.json, upgrade workflow, sync skills │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 3: Cleanup & Migrations                         │
│  - Remove deprecated, run version migrations           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 4: Post-Upgrade Validation                      │
│  - Verify agents, workflow, MCP, skills                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 5: Reporting & Next Steps                       │
│  - Git diff, backup location, health check offer       │
└─────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. Migration Registry

**Purpose:** Handle version-specific transformations.

```python
class MigrationRegistry:
    """Registry of version-aware migrations."""

    migrations: dict[str, list[Migration]] = {}

    @classmethod
    def get_migrations(cls, from_version: str, to_version: str) -> list[Migration]:
        """Get all migrations needed between versions."""
        # Returns: [migrate_workflow_v2, fix_agent_naming, remove_flow_operate, ...]
```

**Example Migration:**

```python
def migrate_workflow_config_v2(project_path: Path) -> None:
    """Upgrade flowspec_workflow.yml from v1.0 to v2.0."""
    # Load v1.0 config
    # Add v2.0 sections (roles, custom_workflows, agent_loops)
    # Remove deprecated sections (operate workflow)
    # Update version to "2.0"
    # Write atomically
```

#### 2. Artifact Synchronizer

**Purpose:** Regenerate computed artifacts.

```python
class ArtifactSynchronizer:
    """Synchronize generated artifacts during upgrade."""

    def sync_mcp_config(self) -> bool:
        """Regenerate .mcp.json with comprehensive MCP servers."""
        # Detect tech stack (Python, JavaScript, etc.)
        # Build server config (backlog, github, serena, trivy, semgrep, ...)
        # Add tech-specific servers (flowspec-security for Python)
        # Write atomically

    def sync_skills(self) -> int:
        """Sync .claude/skills/ from templates."""
        # Copy all 21 skills from templates to project
        # Only update if newer or missing
        # Return count of synced skills

    def upgrade_workflow_config(self) -> bool:
        """Upgrade flowspec_workflow.yml to latest version."""
        # Use migration registry
```

#### 3. Cleanup Orchestrator

**Purpose:** Remove deprecated files and content.

```python
class CleanupOrchestrator:
    """Orchestrate cleanup of deprecated files."""

    DEPRECATED_DIRECTORIES = [".specify/"]
    DEPRECATED_FILES = [".claude/commands/flow/_DEPRECATED_operate.md"]
    DEPRECATED_PATTERNS = ["_DEPRECATED_*.md"]

    def cleanup_directories(self) -> int:
        """Remove deprecated directories."""

    def cleanup_files(self) -> int:
        """Remove deprecated files."""

    def remove_broken_includes(self) -> int:
        """Remove {{INCLUDE:}} directives from prompt files."""
```

#### 4. Validation Framework

**Purpose:** Verify upgrade success.

```python
class UpgradeValidator:
    """Validate upgrade operations."""

    def validate_agent_naming(self) -> ValidationResult:
        """Verify agents use dot notation and PascalCase."""
        # Check for hyphen-notation agents (should be 0)
        # Check for dot-notation agents (should be 6)
        # Check frontmatter names are PascalCase

    def validate_workflow_config(self) -> ValidationResult:
        """Verify workflow config is v2.0 and valid."""
        # Check version == "2.0"
        # Check for deprecated 'operate' workflow (should be absent)
        # Check for v2.0 sections (roles, custom_workflows, agent_loops)

    def validate_mcp_config(self) -> ValidationResult:
        """Verify MCP configuration is complete."""
        # Check for required servers (backlog, github, serena)
        # Return comprehensive status

    def validate_skills(self) -> ValidationResult:
        """Verify skills directory is synced."""
        # Check skill count (should be 21)
```

### Data Flow

```
User Input: flowspec upgrade-repo
    │
    ├─► Detect State
    │   ├─ AI assistant: copilot
    │   ├─ Current version: v1.0
    │   ├─ Tech stack: Python + React
    │   └─ Uncommitted changes: warn if present
    │
    ├─► Create Backup
    │   └─ .flowspec-backup-20260106-143022/
    │
    ├─► Download Templates
    │   ├─ base-spec-kit v0.0.20 (GitHub)
    │   ├─ flowspec v0.3.0 (GitHub)
    │   └─ Merge (flowspec overrides base)
    │
    ├─► Apply Templates
    │   ├─ .github/agents/ (6 agents with dot notation)
    │   ├─ .claude/commands/ (flow commands only)
    │   └─ templates/ (updated)
    │
    ├─► Regenerate Config
    │   ├─ .mcp.json
    │   │   ├─ backlog (required)
    │   │   ├─ github (required)
    │   │   ├─ serena (required)
    │   │   ├─ flowspec-security (Python-specific)
    │   │   ├─ playwright-test (has React)
    │   │   ├─ trivy (security)
    │   │   └─ semgrep (security)
    │   ├─ flowspec_workflow.yml
    │   │   ├─ version: "2.0"
    │   │   ├─ roles: {...}
    │   │   ├─ custom_workflows: {...}
    │   │   └─ agent_loops: {...}
    │   └─ .claude/skills/ (21 skills)
    │
    ├─► Run Migrations
    │   ├─ migrate_workflow_v2
    │   ├─ fix_agent_naming
    │   ├─ remove_flow_operate
    │   └─ remove_broken_includes
    │
    ├─► Cleanup
    │   ├─ Remove .specify/ directory
    │   ├─ Remove _DEPRECATED_*.md files
    │   └─ Clean {{INCLUDE:}} from .github/prompts/
    │
    ├─► Validate
    │   ├─ ✅ Agent naming: 6 agents, dot notation, PascalCase
    │   ├─ ✅ Workflow config: v2.0, no operate, has v2 sections
    │   ├─ ✅ MCP config: 7 servers (3 required + 4 additional)
    │   └─ ✅ Skills: 21 files
    │
    └─► Report
        ├─ ✅ Validation: All checks passed
        ├─ 📁 Backup: .flowspec-backup-20260106-143022/
        ├─ 📊 Changes: git diff shows 47 files changed
        └─ 🚀 Next: Test MCP servers, verify agents in VSCode
```

### Integration Points

**With Existing Code:**

1. **`download_and_extract_two_stage()`** - Keep existing template download logic
2. **`generate_mcp_json()`** - Enhance with comprehensive server list
3. **`detect_tech_stack()`** - Already exists, use for MCP config
4. **`create_backup()`** - Already exists, use for rollback safety

**New Functions:**

1. **`run_migrations(project_path, from_version, to_version)`** - Migration orchestration
2. **`sync_artifacts(project_path)`** - Artifact regeneration
3. **`cleanup_deprecated(project_path)`** - Deprecated file removal
4. **`validate_upgrade(project_path)`** - Post-upgrade validation

### Technology Stack

**No New Dependencies Required:**

- **YAML parsing**: `PyYAML` (already used)
- **JSON handling**: `json` (stdlib)
- **File operations**: `pathlib`, `shutil` (stdlib)
- **HTTP requests**: `httpx` (already used)
- **Regex**: `re` (stdlib)

**Code Organization:**

```
src/flowspec_cli/
├── __init__.py              # Main CLI (keep upgrade_repo here)
├── migrations/              # NEW: Migration registry
│   ├── __init__.py
│   ├── registry.py
│   └── v2_0/
│       ├── workflow_config.py
│       ├── agent_naming.py
│       └── cleanup.py
├── synchronizers/           # NEW: Artifact synchronizers
│   ├── __init__.py
│   ├── mcp_config.py
│   ├── skills.py
│   └── workflow_config.py
├── validators/              # NEW: Validation framework
│   ├── __init__.py
│   ├── agents.py
│   ├── workflow.py
│   └── mcp.py
└── cleanup/                 # NEW: Cleanup orchestrators
    ├── __init__.py
    └── deprecated.py
```

**Note:** Initial implementation can keep everything in `__init__.py`. Refactoring to modules is optional (Phase 3).

---

## Implementation Approach

### Phase Breakdown

| Phase | Priority | Duration | Dependencies | Blocking |
|-------|----------|----------|--------------|----------|
| **Phase 0: Foundation** | P0 | 2-3 days | None | Phase 1, 2 |
| **Phase 1: Agent Templates** | P1 | 3-4 days | Phase 0 | Phase 2 |
| **Phase 2: MCP Config** | P2 | 2-3 days | Phase 1 | Phase 5 |
| **Phase 4: Documentation** | P4 | 1-2 days | Phase 2 | None |
| **Phase 5: Verification** | P5 | 2-3 days | Phase 2 | Release |

**Total Sequential Duration:** 14-18 days
**With 2-Person Parallelization:** 8-10 days

### Critical Path

```
Phase 0 (Remove /flow:operate)
    ↓
Phase 0 (Update workflow config in upgrade-repo)
    ↓
Phase 1 (Fix agent filenames: hyphen→dot)
    ↓
Phase 1 (Fix agent names: kebab→PascalCase)
    ↓
Phase 1 (Update handoffs to new naming)
    ↓
Phase 2 (Create .mcp.json template)
    ↓
Phase 2 (Update generate_mcp_json for comprehensive config)
    ↓
Phase 2 (Add MCP health check)
    ↓
Phase 5 (E2E test on auth.poley.dev)
```

**Critical Path Duration:** 9 tasks, ~10-12 days

### Parallel Work Opportunities

**Phase 0:**
- Task 579.01 (Remove /flow:operate) must be first
- Tasks 579.02, 579.03, 579.04, 579.06 can run in parallel
- Task 579.05 depends on 579.01

**Phase 1:**
- Tasks 579.09, 579.10, 579.11 can run in parallel
- Tasks 579.07 → 579.08 → 579.12 must be sequential

**Optimal 2-Person Team:**
- **Person A (Critical Path):** 579.01 → 579.05 → 579.07 → 579.08 → 579.12 → 579.13 → 579.14 → 579.15
- **Person B (Parallel Tasks):** 579.02, 579.03, 579.04, 579.06, 579.09, 579.10, 579.11, 579.16, 579.17

### Validation Gates

**After Phase 0:**
```bash
rg "/flow:operate" . | wc -l  # Should be 0
rg "{{INCLUDE:" templates/ | wc -l  # Should be 0
```

**After Phase 1:**
```bash
ls templates/.github/agents/*.agent.md | grep "flow\." | wc -l  # Should be 6
rg '^name: Flow[A-Z]' templates/.github/agents/*.agent.md | wc -l  # Should be 6
```

**After Phase 2:**
```bash
jq '.mcpServers | keys | length' templates/.mcp.json  # Should be >= 6
```

**After Phase 5:**
- VSCode Copilot shows 6 agents: FlowAssess, FlowSpecify, FlowPlan, FlowImplement, FlowValidate, FlowSubmitPR
- `flowspec gate` passes
- MCP servers start successfully

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Critical path delays** | Medium | High | Daily standups, blocker identification |
| **Integration failures** | Medium | High | Phase-level validation gates |
| **Scope creep** | Low | Medium | Strict AC adherence, defer Phase 3 |
| **Regression bugs** | Medium | High | Comprehensive test coverage |
| **360KB __init__.py complexity** | High | Medium | Optional Phase 3 refactoring |
| **User customization conflicts** | Low | Medium | Backup/rollback strategy |

### Mitigation Details

**Critical Path Delays:**
- Track 579.01 → 579.05 → 579.07 → 579.08 → 579.12 daily
- Identify blockers in standup, escalate immediately
- Consider pair programming on critical tasks

**Integration Failures:**
- Run integration tests after each phase
- Don't proceed to next phase if validation gate fails
- Use backup/rollback for safe experimentation

**Scope Creep:**
- Phase 3 (refactoring) is explicitly deferred
- Documentation (Phase 4) can be post-release if needed
- Focus on P0/P1 tasks only

---

## Architectural Decision Records

This architecture is documented in three ADRs:

1. **[ADR-001: VSCode Copilot Agent Naming Convention](../adr/ADR-001-vscode-copilot-agent-naming-convention.md)**
   - Decision: Use dot notation (`flow.specify.agent.md`) and PascalCase (`FlowSpecify`)
   - Context: Agent discovery and VSCode integration requirements
   - Consequences: Breaking change requiring migration

2. **[ADR-002: Upgrade-Repo Architecture Redesign](../adr/ADR-002-upgrade-repo-architecture-redesign.md)**
   - Decision: Multi-phase orchestration with validation gates
   - Context: Current upgrade-repo is broken, P0 release blocker
   - Consequences: Robust upgrade process, increased complexity

3. **[ADR-003: Upgrade-Repo Implementation Approach](../adr/ADR-003-upgrade-repo-implementation-approach.md)**
   - Decision: Strict dependency-ordered implementation with phases
   - Context: 18 subtasks requiring careful sequencing
   - Consequences: Predictable timeline, incremental progress

---

## Conclusion

### Key Takeaways

**Strategic:**
- Broken upgrade-repo is a **P0 release blocker** affecting all downstream projects
- Investment in robust upgrade pipeline prevents ongoing support burden
- Success unlocks flowspec v0.3+ release and improves user trust

**Tactical:**
- Multi-phase orchestration handles templates, config, migrations, cleanup, validation
- Migration registry enables version-aware transformations
- Validation framework catches issues before they impact users
- 14-18 day timeline (or 8-10 with parallelization)

### Next Steps

1. **Review ADRs:** Approve ADR-001, ADR-002, ADR-003
2. **Create backlog tasks:** Already exists (task-579 epic with 18 subtasks)
3. **Assign resources:** Allocate 1-2 engineers for 2-3 weeks
4. **Set up validation gates:** Define pass/fail criteria for each phase
5. **Begin Phase 0:** Start with task-579.01 (Remove /flow:operate references)

### Success Criteria

**Release-Ready When:**
- ✅ All Phase 0-2 tasks complete
- ✅ Phase 5 E2E test passes on auth.poley.dev
- ✅ `flowspec upgrade-repo` produces fully functional integration
- ✅ VSCode Copilot agents work correctly
- ✅ MCP servers start without errors
- ✅ All validation gates pass

**Then:** Ship flowspec v0.3.0 with confidence.

---

*For detailed architecture, see ADR-001, ADR-002, ADR-003 in `/Users/jasonpoley/prj/jp/flowspec/docs/adr/`*
