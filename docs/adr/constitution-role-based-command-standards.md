# For speckit.constitution: Role-Based Command Standards

**Status**: Proposed
**Date**: 2025-12-09
**Author**: Enterprise Software Architect
**Related Tasks**: task-360
**Dependencies**: [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)

---

## Purpose

This document defines the **constitutional standards** for role-based command namespaces in Flowspec. These principles are intended to be incorporated into `/speckit.constitution` as authoritative rules that govern command creation, organization, and evolution.

## What is speckit.constitution?

The **speckit.constitution** is the living document that defines:
- Core architectural principles and constraints
- Design patterns and anti-patterns
- Quality standards and gates
- Command and workflow conventions
- Extensibility guidelines

It serves as the **single source of truth** for how Flowspec should be built and extended.

---

## Constitutional Principles

### 1. Role-Based Organization Mandate

**PRINCIPLE**: All user-facing commands MUST be organized by primary role namespace.

**Rationale**: Reduces cognitive load and improves discoverability by aligning tool structure with team organization.

**Implementation**:
```
/{role}:{action}[:{qualifier}]

Where:
  {role} = pm | dev | sec | qa | ops | speckit
  {action} = imperative verb (assess, implement, validate, scan)
  {qualifier} = optional descriptor (web, light, critical)
```

**Examples**:
- ✅ `/pm:assess` - Clear role and action
- ✅ `/sec:scan-web` - Clear role, action, qualifier
- ❌ `/flow:security_fix` - No role in namespace
- ❌ `/assess` - Missing role context

---

### 2. Namespace Stability Contract

**PRINCIPLE**: Role namespaces are first-class citizens and MUST NOT change without major version bump.

**Rationale**: Ensures API stability and prevents breaking changes in user workflows.

**Rules**:
- ✅ Adding new commands to existing namespace: **minor version**
- ✅ Adding new qualifiers to existing command: **minor version**
- ❌ Renaming namespace (e.g., `/dev` → `/developer`): **major version**
- ❌ Removing namespace: **major version + 12-month deprecation**

**Deprecation Policy**:
- Minimum deprecation period: **12 months**
- Deprecation warnings: **3-phase escalation** (soft → hard → critical)
- Aliases maintained: **Throughout deprecation period**

---

### 3. Role-to-Command Mapping Rules

**PRINCIPLE**: Each command MUST have exactly one primary role namespace.

**Rationale**: Prevents ambiguity and ensures clear ownership.

| Namespace | Role | Agent Assignment |
|-----------|------|------------------|
| `/pm` | Product Manager | @pm-planner, @workflow-assessor, @researcher |
| `/dev` | Developer | @software-architect, @frontend-engineer, @backend-engineer |
| `/sec` | Security Engineer | @secure-by-design-engineer |
| `/qa` | QA Engineer | @quality-guardian, @tech-writer, @release-manager |
| `/ops` | SRE/DevOps | @sre-agent |
| `/speckit` | All Roles (Utilities) | Cross-role agents |

**Cross-Role Commands**:
- Commands needed by multiple roles belong in `/speckit`
- Examples: `/speckit:constitution`, `/speckit:tasks`, `/speckit:clarify`
- These commands do NOT have a single role owner

---

### 4. Naming Convention Standards

#### 4.1 Role Prefix Standards

**REQUIRED**:
- Short, memorable (2-5 characters)
- All lowercase
- No special characters except hyphen
- Must be unique across all namespaces

**Approved Prefixes**:
- `pm` - Product Manager
- `dev` - Developer
- `sec` - Security Engineer
- `qa` - QA Engineer
- `ops` - SRE/DevOps
- `speckit` - Cross-role utilities

**Reserved for Future Use**:
- `data` - Data Engineer
- `design` - UX Designer
- `doc` - Technical Writer (dedicated role)
- `infra` - Infrastructure Engineer (if split from ops)

**Adding New Roles**:
1. Propose role prefix in ADR
2. Get approval from core team
3. Add to `flowspec_workflow.yml` role_config
4. Update this constitution document

---

#### 4.2 Action Verb Standards

**REQUIRED**:
- Imperative form (command, not description)
- Clear intent (user knows what happens)
- Short (1-2 words)
- Consistent across similar actions

**Approved Verbs by Category**:

| Category | Verbs | Examples |
|----------|-------|----------|
| **Creation** | assess, specify, research, plan, init | `/pm:assess`, `/pm:specify` |
| **Execution** | implement, deploy, operate, run | `/dev:implement`, `/ops:deploy` |
| **Validation** | validate, test, scan, check, review | `/qa:validate`, `/sec:scan-web` |
| **Modification** | fix, update, reset, prune | `/sec:fix`, `/dev:reset` |
| **Information** | report, analyze, status, list | `/sec:report`, `/qa:analyze` |
| **Management** | tasks, constitution, clarify | `/speckit:tasks`, `/speckit:clarify` |

**Anti-Patterns**:
- ❌ Passive voice: `/pm:assessed` (should be `/pm:assess`)
- ❌ Gerund form: `/dev:implementing` (should be `/dev:implement`)
- ❌ Question form: `/qa:is-valid` (should be `/qa:validate`)
- ❌ Too specific: `/sec:scan-owasp-top-ten` (should be `/sec:scan-web`)

---

#### 4.3 Qualifier Standards

**OPTIONAL**: Use qualifiers to distinguish command variants

**Rules**:
- Separated by hyphen: `-`
- Only use when variants serve different purposes
- Keep under 15 characters
- Use consistent qualifiers across namespaces

**Common Qualifiers**:
- **Variant**: `-light` (lightweight mode), `-full` (full mode)
- **Target**: `-web` (web scanning), `-api` (API scanning), `-container` (container scanning)
- **Severity**: `-critical` (critical only), `-all` (all severities)
- **Scope**: `-local` (local only), `-remote` (remote only)

**Examples**:
- ✅ `/dev:implement-light` - Lightweight implementation mode
- ✅ `/sec:scan-web` - Web vulnerability scan
- ✅ `/sec:fix-critical` - Fix only critical vulnerabilities
- ❌ `/sec:scan-for-owasp-vulnerabilities` - Too verbose

---

### 5. Command Documentation Standards

**PRINCIPLE**: Every command MUST have comprehensive documentation colocated with definition.

**Required Frontmatter Fields**:
```yaml
---
description: "Brief one-line description (< 80 chars)"
role: "pm"                          # Primary role namespace
agents: ["@pm-planner"]             # Agent assignments
mode: "interactive|agent|batch"     # Execution mode
input_states: ["Assessed"]          # Required workflow states
output_state: "Specified"           # Resulting workflow state
---
```

**Required Documentation Sections**:
1. **User Input** - Arguments and options
2. **Execution Instructions** - Step-by-step workflow
3. **Agent Context** (if mode=agent) - Full agent prompt
4. **Deliverables** - Expected outputs
5. **Examples** - Common usage patterns
6. **Related Commands** - Workflow handoffs

**Example Structure**:
```markdown
---
description: "Assess SDD workflow suitability and complexity"
role: "pm"
agents: ["@workflow-assessor"]
---

## User Input
[Arguments and flags]

## Execution Instructions
[Detailed workflow steps]

## Agent Context
[Full prompt for @workflow-assessor]

## Deliverables
[Expected outputs and artifacts]

## Examples
[Common usage scenarios]

## Related Commands
- `/pm:specify` - Create requirements after assessment
```

---

### 6. Extensibility Guidelines

#### 6.1 Adding New Commands to Existing Role

**Process**:
1. Identify primary role namespace
2. Choose appropriate action verb (see 4.2)
3. Add optional qualifier if needed (see 4.3)
4. Create command file: `.claude/commands/{role}/{action}.md`
5. Add agent assignments in `flowspec_workflow.yml`
6. Generate Copilot agents: `scripts/bash/sync-copilot-agents.sh`
7. Update documentation

**Validation Checklist**:
- [ ] Command follows `/{role}:{action}[:{qualifier}]` format
- [ ] Documentation includes all required sections
- [ ] Agent assignments are correct
- [ ] VS Code Copilot agents generated
- [ ] Examples provided
- [ ] Related commands documented

---

#### 6.2 Adding New Role Namespace

**Process**:
1. **Propose in ADR**:
   - Justify need for new role
   - Define scope and responsibilities
   - Map to existing agents or propose new agents
2. **Update flowspec_workflow.yml**:
   ```yaml
   role_config:
     roles:
       data:  # NEW ROLE
         display_name: "Data Engineer"
         icon: "📊"
         auto_load_agents:
           - "@data-engineer"
   ```
3. **Create namespace directory**: `.claude/commands/data/`
4. **Define initial commands**
5. **Update init prompt** to include new role
6. **Update this constitution document**

**Minimum Requirements for New Role**:
- At least 3 commands in namespace
- At least 1 dedicated agent
- Clear differentiation from existing roles
- Approved by core team

---

### 7. Backwards Compatibility Requirements

**PRINCIPLE**: Breaking changes to command namespaces MUST follow deprecation protocol.

**Deprecation Protocol** (from design-command-migration-path.md):

1. **Announcement** (Month 0):
   - Publish deprecation notice
   - Add to changelog
   - Update documentation

2. **Soft Deprecation** (Months 0-6):
   - Old commands work with warnings
   - New commands available

3. **Hard Deprecation** (Months 6-9):
   - Urgent warnings with countdown
   - Auto-migration tool available

4. **Final Warning** (Months 9-12):
   - Critical warnings
   - Personal outreach to stragglers

5. **Removal** (Month 12+):
   - Old commands removed
   - Helpful error messages

**Required Artifacts**:
- Migration guide
- Auto-migration tool (`specify migrate-commands`)
- Command mapping matrix
- FAQ document

---

### 8. Quality Gates for Command Changes

**PRINCIPLE**: All command changes MUST pass automated quality gates.

**Pre-Commit Checks**:
```bash
# 1. Validate command naming
scripts/bash/validate-command-names.sh

# 2. Check documentation completeness
scripts/bash/validate-command-docs.sh

# 3. Generate Copilot agents
scripts/bash/sync-copilot-agents.sh

# 4. Run tests
pytest tests/commands/
```

**CI/CD Checks**:
- Command naming conventions (regex validation)
- Documentation completeness (all required sections)
- Agent sync validation (no drift)
- Integration tests (command execution)

**Review Checklist**:
- [ ] Command name follows conventions
- [ ] Documentation complete
- [ ] Agent assignments correct
- [ ] Examples provided
- [ ] Tests added
- [ ] Copilot agents synced
- [ ] No breaking changes (or deprecation plan)

---

## Constitutional Amendment Process

### How to Update These Standards

These constitutional standards are **living principles** that can evolve, but changes require rigorous review:

**Amendment Process**:
1. **Propose ADR** with rationale for change
2. **Community feedback** (Discord, GitHub Discussions)
3. **Core team review** (minimum 2 approvals)
4. **Implementation plan** (migration if breaking)
5. **Update constitution** (this document)
6. **Publish announcement**

**Amendment Categories**:
- **Minor**: Clarifications, typo fixes (no review needed)
- **Major**: New principles, changed rules (ADR required)
- **Breaking**: Namespace changes, removed rules (12-month deprecation)

---

## Enforcement

### Automated Enforcement

Constitutional violations are detected by:
1. **Pre-commit hooks**: Block commits that violate naming conventions
2. **CI/CD pipeline**: Fail builds with documentation gaps
3. **Linter**: Flag style violations in command files

### Manual Enforcement

Code reviewers MUST verify:
- New commands follow namespace conventions
- Documentation meets completeness standards
- Deprecation protocol followed for breaking changes

---

## Summary: Quick Reference

| Principle | Rule | Example |
|-----------|------|---------|
| **Organization** | `/{role}:{action}[:{qualifier}]` | `/pm:assess`, `/sec:scan-web` |
| **Stability** | Major version for namespace changes | `/dev` → `/developer` = v2.0.0 |
| **Ownership** | One primary role per command | `/pm:assess` (not `/dev:assess`) |
| **Naming** | Lowercase, hyphen-separated, imperative | ✅ `/dev:implement` ❌ `/Dev:implementing` |
| **Documentation** | All required sections present | User Input, Instructions, Examples |
| **Extensibility** | 3+ commands for new role | Minimum viable role namespace |
| **Compatibility** | 12-month deprecation period | Soft → Hard → Critical → Removal |
| **Quality** | Pass all automated gates | Linting, tests, agent sync |

---

## Related Documents

- [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)
- [ADR: Role Selection During Initialization](./ADR-role-selection-during-initialization.md)
- [Design: Command Migration Path](./design-command-migration-path.md)
- [Workflow Configuration](../../flowspec_workflow.yml)

---

**Status**: Proposed
**Reviewers**: @product-requirements-manager, @software-architect
**Constitutional Authority**: Core Team
**Next Review Date**: 2025-12-16
