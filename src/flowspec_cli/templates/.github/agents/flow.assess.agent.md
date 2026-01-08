---
name: FlowAssess
description: "Evaluate feature complexity and determine SDD workflow approach (full SDD, spec-light, or skip)."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Create Specification"
    agent: "flow.specify"
    prompt: "Assessment complete. Create the feature specification and PRD."
    send: false
---

# /flow:assess - Feature Assessment

Evaluate feature complexity and recommend the appropriate SDD workflow mode.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Instructions

This command evaluates whether a feature requires the full SDD workflow, a lighter approach, or can skip formal specification entirely.

**Purpose:**
- Analyze feature complexity and scope
- Recommend appropriate workflow mode
- Create initial backlog task for tracking

**Workflow Modes:**

| Mode | When to Use | Artifacts |
|------|-------------|-----------|
| **Full SDD** | Complex features, multiple components, significant risk | PRD, ADRs, full spec |
| **Spec-Light** | Medium complexity, clear requirements | Light spec, tasks |
| **Skip SDD** | Simple changes, bug fixes, trivial updates | Just tasks |

**Assessment Criteria:**
1. **Scope**: How many files/components affected?
2. **Risk**: Security, data, or user-facing impact?
3. **Complexity**: New patterns, integrations, or dependencies?
4. **Clarity**: Are requirements well-defined?
5. **Duration**: Single session or multi-session work?

**Workflow:**
1. Gather feature description from user
2. Search codebase for related code and patterns
3. Assess complexity using criteria above
4. Recommend workflow mode with rationale
5. Create initial backlog task

**Key Commands:**
```bash
# Search for related code
grep -r "feature_keyword" src/

# Check existing tasks
backlog search "$ARGUMENTS" --plain

# Create assessment task
backlog task create "Assess: [Feature Name]" \
  -d "Complexity assessment for feature" \
  --ac "Determine workflow mode" \
  --ac "Create initial task structure" \
  -l assess \
  --priority medium
```

**Output:**
- Assessment report with recommended mode
- Initial backlog task created
- Workflow state set to `Assessed`

After assessment, suggest running `/flow:specify` for Full SDD or Spec-Light modes.
