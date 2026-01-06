# ADR-001: VSCode Copilot Agent Naming Convention

## Status

Accepted

## Context

Flowspec generates VSCode Copilot agent templates that enable developers to invoke specialized workflows (`/flow:assess`, `/flow:specify`, etc.) through GitHub Copilot's agent interface. These agents appear as selectable options in the VSCode agent dropdown menu (e.g., "FlowAssess", "FlowSpecify").

Two competing naming conventions emerged during development:

**Current Convention (Hyphen-based):**
- Filenames: `flow-specify.agent.md`, `flow-implement.agent.md`
- YAML frontmatter name field: `"flow-specify"` (kebab-case string)
- Embedded in: `COPILOT_AGENT_TEMPLATES` dictionary in `src/flowspec_cli/__init__.py`

**Target Convention (Dot-based):**
- Filenames: `flow.specify.agent.md`, `flow.implement.agent.md`
- YAML frontmatter name field: `FlowSpecify` (PascalCase identifier)
- Observed in: Production deployments (auth.poley.dev) that successfully integrate with VSCode

### Problem Statement

The `flowspec upgrade-repo` command is currently broken because it deploys agent templates with the hyphen-based convention, which does not align with VSCode Copilot's agent discovery mechanism. This causes:

1. **Agent discovery failures**: VSCode cannot properly detect or display agents
2. **Menu display issues**: Agent names appear incorrectly formatted in UI
3. **Deployment inconsistencies**: Production repos manually fixed to use dots, but flowspec continues generating hyphens
4. **User confusion**: Developers see discrepancies between documentation and actual behavior

### Forces at Play

1. **VSCode Copilot Agent Discovery**: VSCode uses filename patterns to discover agent files in `.github/agents/`
2. **Menu Presentation**: The `name:` field in YAML frontmatter controls how agents appear in dropdown menus
3. **Convention Consistency**: GitHub Copilot ecosystem conventions favor dot-notation for namespaced agents
4. **Backward Compatibility**: Existing deployed projects may use the old convention
5. **Migration Path**: Transition must be smooth for existing users
6. **Template Embeddedness**: Agent templates are embedded in 360KB `__init__.py` requiring careful refactoring

### Constraints

- Must align with VSCode Copilot's documented agent discovery patterns
- Must not break existing projects during upgrade
- Must support future GitHub Copilot feature extensions (handoffs, tool declarations)
- Must be testable via automated verification

## Decision

**We will standardize on the dot-notation, PascalCase naming convention for all VSCode Copilot agent templates.**

**Specifically:**

1. **Filenames**: Use dot notation: `flow.{command}.agent.md`
   - Examples: `flow.assess.agent.md`, `flow.specify.agent.md`, `flow.implement.agent.md`

2. **YAML Frontmatter `name:` Field**: Use PascalCase identifier (no quotes)
   - Examples: `FlowAssess`, `FlowSpecify`, `FlowImplement`

3. **Agent Discovery Location**: All agents reside in `.github/agents/` directory

4. **Extended Metadata**: Include `tools:`, `handoffs:`, and `target:` fields for future-proofing

**Example Agent Template:**
```yaml
---
name: FlowSpecify
description: "Create or update feature specifications using PM planner agent"
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
handoffs:
  - label: "Create Technical Design"
    agent: "flow.plan"
    prompt: "The specification is complete. Create the technical architecture."
    send: false
---

# /flow:specify - Feature Specification

[Agent instructions...]
```

**Migration Strategy:**

1. **Update `COPILOT_AGENT_TEMPLATES`**: Rename dictionary keys to use dot notation
2. **Rename template files**: `templates/.github/agents/flow-*.agent.md` → `flow.*.agent.md`
3. **Fix embedded templates**: Update all embedded template strings in `__init__.py`
4. **Add missing agent**: Create `flow.assess.agent.md` (currently missing)
5. **Update handoff references**: Change `agent: "flow-plan"` → `agent: "flow.plan"`
6. **Backward compatibility**: `flowspec upgrade-repo` will automatically fix old naming during upgrades

## Consequences

### Positive

1. **VSCode Integration Works**: Agents properly discovered and displayed in VSCode dropdown
2. **Consistent User Experience**: Menu displays clean PascalCase names ("FlowAssess", "FlowImplement")
3. **Aligns with Ecosystem**: Matches GitHub Copilot agent naming conventions
4. **Future-Proof**: Extended metadata enables tool restrictions and agent handoffs
5. **Automated Migration**: `upgrade-repo` command automatically fixes naming in target repos
6. **Testable**: Agent discovery can be verified via integration tests
7. **Professional Appearance**: PascalCase names look cleaner in VSCode UI than kebab-case strings

### Negative

1. **Breaking Change**: Existing projects with hyphen-notation agents will need upgrade
2. **Embedded Template Size**: 360KB `__init__.py` becomes harder to maintain
3. **Migration Complexity**: All agent references (handoffs, documentation) must be updated
4. **Testing Burden**: Need comprehensive tests to verify naming consistency across all agents
5. **Documentation Updates**: All examples and guides must reflect new convention

### Neutral

1. **File Organization**: Dot notation vs hyphen notation is stylistic, but dots are standard for namespacing
2. **Template Count**: Six agents (assess, specify, research, plan, implement, validate) regardless of naming
3. **Template Complexity**: Extended frontmatter adds lines but improves extensibility

## Alternatives Considered

### Alternative 1: Keep Hyphen Notation, Fix Agent Names Only

**Change only the `name:` field to PascalCase, keep filenames with hyphens.**

- **Pros:**
  - Minimal file changes
  - No filename refactoring in CLI
  - Backward compatible at filesystem level
- **Cons:**
  - Inconsistent with VSCode ecosystem patterns
  - Filenames don't match the namespace structure (flow.specify vs flow-specify)
  - Potential future discovery issues with GitHub Copilot updates
  - Confusion between filename and displayed name
- **Why rejected:** GitHub Copilot's agent discovery may rely on dot-notation for namespaced agents. Mixing conventions creates technical debt.

### Alternative 2: Use Underscore Notation

**Use underscores instead: `flow_specify.agent.md`, `FlowSpecify`**

- **Pros:**
  - Clear visual separation
  - Valid in most filesystems
  - Python-friendly (matches Python module naming)
- **Cons:**
  - Not standard in JavaScript/TypeScript ecosystems
  - GitHub Copilot conventions favor dots for namespacing
  - Inconsistent with existing VSCode Copilot examples
  - Underscores are less common for agent identifiers
- **Why rejected:** Dots are the established convention for namespaced agents in the GitHub Copilot ecosystem.

### Alternative 3: Flat Naming (No Namespace)

**Remove namespace entirely: `assess.agent.md`, `Assess`**

- **Pros:**
  - Shorter names
  - Simpler filenames
  - Reduced cognitive load
- **Cons:**
  - Namespace collision risk (other tools might use "Assess")
  - Loses "flow" brand/context in agent menus
  - Harder to distinguish flowspec agents from project-specific agents
  - Inconsistent with flowspec's command namespace (`/flow:*`)
- **Why rejected:** The `flow.*` namespace clearly identifies flowspec-managed agents and aligns with slash command naming.

### Alternative 4: Keep Current, Document as "Not Recommended"

**Accept hyphen notation as valid but discourage it.**

- **Pros:**
  - No breaking changes
  - Backward compatible
  - Zero migration effort
- **Cons:**
  - Perpetuates broken behavior
  - VSCode integration remains unreliable
  - User confusion when comparing to docs/examples
  - Technical debt grows
  - Blocks flowspec release
- **Why rejected:** The current behavior is broken and must be fixed for release. Documentation cannot fix a fundamental integration issue.

## Implementation Notes

### Files Requiring Changes

**CLI Templates:**
- `src/flowspec_cli/__init__.py` - COPILOT_AGENT_TEMPLATES dictionary (lines 191-551)

**Template Files:**
- `templates/.github/agents/flow-specify.agent.md` → `flow.specify.agent.md`
- `templates/.github/agents/flow-plan.agent.md` → `flow.plan.agent.md`
- `templates/.github/agents/flow-implement.agent.md` → `flow.implement.agent.md`
- `templates/.github/agents/flow-validate.agent.md` → `flow.validate.agent.md`
- `templates/.github/agents/flow-submit-n-watch-pr.agent.md` → `flow.submit-n-watch-pr.agent.md`
- NEW: `templates/.github/agents/flow.assess.agent.md` (currently missing)

**Handoff References:**
- Update all `agent: "flow-*"` → `agent: "flow.*"` in handoff configurations

**Tests:**
- Add integration test: verify agent files created with correct naming
- Add unit test: validate COPILOT_AGENT_TEMPLATES keys use dot notation

**Documentation:**
- Update all examples showing agent filenames
- Update CLAUDE.md references to agent naming

### Verification Checklist

After implementation:

```bash
# 1. Verify template naming
ls templates/.github/agents/*.agent.md
# Should show: flow.assess.agent.md, flow.specify.agent.md, etc.

# 2. Test flowspec init
flowspec init test-project --agent copilot
cd test-project
ls .github/agents/*.agent.md
# Should create dot-notation agents

# 3. Verify VSCode integration
# - Open project in VSCode with Copilot
# - Check agent dropdown shows: FlowAssess, FlowSpecify, FlowPlan, etc.
# - Verify handoffs work between agents

# 4. Test upgrade-repo
# In a project with old naming:
flowspec upgrade-repo
ls .github/agents/*.agent.md
# Should convert hyphen → dot notation
```

### Migration Path for Existing Projects

1. **Automatic via upgrade-repo**: Running `flowspec upgrade-repo` will replace old agents with new naming
2. **Backward compatibility**: No manual intervention required
3. **Rollback**: If issues occur, backup directory contains old agent files
4. **Documentation**: Release notes will explain naming change and benefits

## References

- [Fix Flowspec Plan](../../building/fix-flowspec-plan.md) - Root cause analysis
- [Task 579.07](../../../backlog/tasks/task-579.07%20-%20P1.1-Fix-agent-filename-convention-hyphens-to-dots.md) - Implementation task
- [Flowspec Workflow Config](../../../flowspec_workflow.yml) - Workflow state machine
- [GitHub Copilot Agent Documentation](https://docs.github.com/en/copilot/using-github-copilot/using-extensions/using-github-copilot-extensions-in-your-ide)
- [Michael Nygard ADR Format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

---

*This ADR follows the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).*
