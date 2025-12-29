---
name: "flow-assess"
description: "Evaluate if SDD workflow is appropriate for a feature. Output: Full SDD workflow (complex), Spec-light mode (medium), Skip SDD (simple)."
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
  - label: "Specify Requirements"
    agent: "flow-specify"
    prompt: "The assessment is complete. Based on the assessment, create detailed product requirements."
    send: false
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command is the **mandatory entry point** to the flowspec workflow. It evaluates whether a feature requires the full Spec-Driven Development (SDD) workflow, a lighter specification approach, or can skip SDD entirely.

# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "[Y] Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: flowspec init --here"
  echo "  2. Then: Run /spec:constitution to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `flowspec init --here`
- Continue with command (constitution is recommended but not required)

### 2. If Constitution Exists, Check Validation Status

```bash
# Detect tier from TIER comment (default: Medium if not found)
TIER=$(grep -o "TIER: \(Light\|Medium\|Heavy\)" memory/constitution.md | cut -d' ' -f2)
TIER=${TIER:-Medium}  # Default to Medium if not found

# Count NEEDS_VALIDATION markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md || echo 0)

# Extract section names from NEEDS_VALIDATION markers
SECTIONS=$(grep "NEEDS_VALIDATION" memory/constitution.md | sed 's/.*NEEDS_VALIDATION: /  - /')

echo "Constitution tier: $TIER"
echo "Unvalidated sections: $MARKER_COUNT"
```

### 3. Apply Tier-Based Enforcement

#### Light Tier - Warn Only

If `TIER = Light` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution has N unvalidated sections:
$SECTIONS

Consider running /spec:constitution to customize your constitution.

Proceeding with command...
```

Then continue with the command.

#### Medium Tier - Warn and Confirm

If `TIER = Medium` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
$SECTIONS

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Run /spec:constitution to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` -> Continue with command
- If user responds `n`, `no`, or empty/Enter -> Stop and show:
  ```text
  Command cancelled. Run /spec:constitution to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
[X] Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Run /spec:constitution to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**DO NOT PROCEED** with the command. Exit and wait for user to resolve.

### 4. Skip Validation Flag

If the command was invoked with `--skip-validation`:

```bash
# Check for skip flag in arguments
if [[ "$ARGUMENTS" == *"--skip-validation"* ]]; then
  echo "⚠️ Skipping constitution validation (--skip-validation)"
  # Remove the flag from arguments and continue
  ARGUMENTS="${ARGUMENTS/--skip-validation/}"
fi
```

When skip flag is present:
- Log warning
- Skip all validation checks
- Continue with command
- Note: For emergency use only

### 5. Fully Validated Constitution

If `MARKER_COUNT = 0`:

```text
[Y] Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | [Y] Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | [Y] Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | [Y] Continue |
| Heavy | >0 | [X] Block, require validation |
| Any | >0 + `--skip-validation` | ⚠️ Warn, continue |

## Integration Example

```markdown
---
description: Your command description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

{{INCLUDE:.claude/partials/flow/_workflow-state.md}}

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| `/spec:constitution` | Interactive constitution customization |
| `flowspec constitution validate` | Check validation status and show report |
| `flowspec constitution show` | Display current constitution |


# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### Light Mode Detection

First, check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".flowspec-light-mode" ]; then
  echo "Project is in LIGHT MODE (~60% faster workflow)"
fi
```

**Light Mode Behavior**:
- `/flow:research` -> **SKIPPED** (inform user and suggest `/flow:plan` instead)
- `/flow:plan` -> Uses `plan-light.md` template (high-level only)
- `/flow:specify` -> Uses `spec-light.md` template (combined stories + AC)

If in light mode and the current command is `/flow:research`, inform the user:
```text
ℹ️ This project is in Light Mode

Light mode skips the research phase for faster iteration.
Current state: workflow:Specified

Suggestions:
  - Run /flow:plan to proceed directly to planning
  - To enable research, delete .flowspec-light-mode and use full mode
  - See docs/guides/when-to-use-light-mode.md for details
```

### 1. Get Current Task and State

```bash
# Find the task you're working on
# Option A: If task ID was provided in arguments, use that
# Option B: Look for task currently "In Progress"
backlog task list -s "In Progress" --plain

# Get task details and extract workflow state from labels
TASK_ID="<task-id>"  # Replace with actual task ID
backlog task "$TASK_ID" --plain
```

### 2. Check Workflow State

Extract the `workflow:*` label from the task. The state must match one of the **Required Input States** for this command:

| Command | Required Input States | Output State |
|---------|----------------------|--------------|
| /flow:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /flow:specify | workflow:Assessed | workflow:Specified |
| /flow:research | workflow:Specified | workflow:Researched |
| /flow:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /flow:implement | workflow:Planned | workflow:In Implementation |
| /flow:validate | workflow:In Implementation | workflow:Validated |
| /flow:operate | workflow:Validated | workflow:Deployed |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /flow:<command>

Current state: "<current-workflow-label>"
Required states: <list-of-valid-input-states>

Suggestions:
  - Valid workflows for current state: <list-valid-commands>
  - Use --skip-state-check to bypass (not recommended)
```

**DO NOT PROCEED** unless:
- The task is in a valid input state, OR
- User explicitly requests to skip the check

### 4. Update State After Completion

After successful workflow completion, update the task's workflow state:

```bash
# Remove old workflow label and add new one
# Replace <output-state> with the output state from the table above
backlog task edit "$TASK_ID" -l "workflow:<output-state>"
```

## Workflow State Labels Reference

Tasks use labels with the `workflow:` prefix to track their current workflow state:

- `workflow:Assessed` - SDD suitability evaluated (/flow:assess complete)
- `workflow:Specified` - Requirements captured (/flow:specify complete)
- `workflow:Researched` - Technical research completed (/flow:research complete)
- `workflow:Planned` - Architecture planned (/flow:plan complete)
- `workflow:In Implementation` - Code being written (/flow:implement in progress)
- `workflow:Validated` - QA and security validated (/flow:validate complete)
- `workflow:Deployed` - Released to production (/flow:operate complete)

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from flowspec_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/flow:research', '/flow:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.


**For /flow:assess**: This is the workflow entry point. Required input state is `workflow:To Do` or no workflow label. Output state will be `workflow:Assessed`.

If the task already has a workflow state label (e.g., `workflow:Specified`), inform the user:
- Assessment is meant for new features at the start of the workflow
- For re-assessment: use `--skip-state-check` or remove the workflow label first
- Consider whether you need `/flow:specify` or another workflow command instead

### Overview

The assess command:
1. Analyzes feature complexity, risk, and architectural impact
2. Generates a detailed assessment report
3. Recommends workflow path (Full SDD, Spec-Light, or Skip SDD)
4. Transitions workflow state from "To Do" -> "Assessed"
5. Provides specific next-step commands

### Step 1: Feature Analysis

Analyze the feature request along three dimensions (1-10 scale):

#### Complexity Scoring
- **Effort Days** (1-10): Estimated development time
  - 1-2: Single day or less
  - 3-5: Few days, straightforward implementation
  - 6-8: Week or more, moderate complexity
  - 9-10: Multiple weeks, high complexity
- **Component Count** (1-10): Number of modules/services affected
  - 1-2: Single component
  - 3-5: 2-3 components
  - 6-8: 4-6 components
  - 9-10: 7+ components or cross-cutting
- **Integration Points** (1-10): External dependencies
  - 1-2: No external integrations
  - 3-5: 1-2 integrations
  - 6-8: 3-5 integrations
  - 9-10: 6+ integrations or complex orchestration

**Complexity Score = (Effort + Components + Integrations) / 3**

#### Risk Scoring
- **Security Implications** (1-10): Security risk level
  - 1-2: No security concerns
  - 3-5: Minor security considerations
  - 6-8: Moderate security requirements
  - 9-10: Critical security controls required
- **Compliance Requirements** (1-10): Regulatory compliance
  - 1-2: No compliance requirements
  - 3-5: Basic compliance (logging, audit)
  - 6-8: Industry standards (PCI, HIPAA)
  - 9-10: Strict regulatory compliance
- **Data Sensitivity** (1-10): Data handling requirements
  - 1-2: Public/non-sensitive data
  - 3-5: Internal business data
  - 6-8: Customer personal data
  - 9-10: Financial/health/highly sensitive data

**Risk Score = (Security + Compliance + Data) / 3**

#### Architecture Impact Scoring
- **New Patterns** (1-10): Introduction of new patterns
  - 1-2: Uses existing patterns
  - 3-5: Minor pattern variations
  - 6-8: New patterns for team
  - 9-10: Novel architectural patterns
- **Breaking Changes** (1-10): API/contract changes
  - 1-2: No breaking changes
  - 3-5: Internal breaking changes only
  - 6-8: Public API breaking changes
  - 9-10: Major breaking changes across system
- **Dependencies Affected** (1-10): Impact on other systems
  - 1-2: Self-contained
  - 3-5: 1-2 downstream dependencies
  - 6-8: 3-5 downstream dependencies
  - 9-10: Wide-ranging dependency impact

**Architecture Impact Score = (Patterns + Breaking + Dependencies) / 3**

### Step 2: Recommendation Logic

Calculate recommendation based on scores:

# Each score (Complexity, Risk, Architecture Impact) is the average of three sub-scores (range 1-10).
# Total Score = Complexity + Risk + Architecture Impact
# Total Score range: 3 (all scores = 1) to 30 (all scores = 10)
```
Total Score = Complexity + Risk + Architecture Impact

IF any individual score >= 7 OR Total Score >= 18:
    Recommendation: Full SDD
    Confidence: High
    Rationale: High complexity/risk/impact requires full workflow

ELSE IF any individual score >= 4 OR Total Score >= 10:
    Recommendation: Spec-Light
    Confidence: Medium
    Rationale: Moderate complexity benefits from lightweight specification

ELSE:
    Recommendation: Skip SDD
    Confidence: High
    Rationale: Low complexity allows direct implementation
```

### Step 3: Generate Assessment Report

Create the assessment report at `./docs/assess/{feature}-assessment.md`:

```markdown
# Feature Assessment: {Feature Name}

**Date**: {YYYY-MM-DD}
**Assessed By**: Claude AI Agent
**Status**: Assessed

## Feature Overview

{Brief description of the feature from user input}

## Scoring Analysis

### Complexity Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Effort Days | {N}/10 | {Explanation} |
| Component Count | {N}/10 | {Explanation} |
| Integration Points | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

### Risk Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Security Implications | {N}/10 | {Explanation} |
| Compliance Requirements | {N}/10 | {Explanation} |
| Data Sensitivity | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

### Architecture Impact Score: {X.X}/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| New Patterns | {N}/10 | {Explanation} |
| Breaking Changes | {N}/10 | {Explanation} |
| Dependencies Affected | {N}/10 | {Explanation} |
| **Average** | **{X.X}/10** | |

## Overall Assessment

**Total Score**: {XX.X}/30
**Recommendation**: {Full SDD | Spec-Light | Skip SDD}
**Confidence**: {High | Medium | Low}

### Rationale

{Detailed explanation of recommendation based on scores}

### Key Factors

- **Complexity**: {Summary}
- **Risk**: {Summary}
- **Impact**: {Summary}

## Next Steps

{Based on recommendation, provide specific commands}

### Full SDD Path
```bash
/flow:specify {feature}
```

### Spec-Light Path
```bash
# Create lightweight spec in ./docs/prd/{feature}-spec.md
# Include: problem statement, key requirements, acceptance criteria
# Then proceed to implementation
```

### Skip SDD Path
```bash
# Proceed directly to implementation
# Document decisions in ADRs as needed
```

## Override

If this assessment doesn't match your needs, you can override:

```bash
# Force full SDD workflow
/flow:assess {feature} --mode full

# Force spec-light mode
/flow:assess {feature} --mode light

# Force skip SDD
/flow:assess {feature} --mode skip
```

---

*Assessment generated by /flow:assess workflow*
```

### Step 4: Support Override Mode

If user provides `--mode {full|light|skip}` flag:
1. Skip scoring analysis
2. Generate assessment report with override noted
3. Proceed with specified workflow path

### Step 5: Output Recommendation

After generating the report, output:

```
## Assessment Complete

**Feature**: {feature name}
**Recommendation**: {Full SDD | Spec-Light | Skip SDD}
**Confidence**: {High | Medium | Low}
**Report**: ./docs/assess/{feature}-assessment.md

### Scoring Summary
- Complexity: {X.X}/10
- Risk: {X.X}/10
- Architecture Impact: {X.X}/10
- **Total**: {XX.X}/30

### Next Command

{Based on recommendation:}

For Full SDD:
    /flow:specify {feature}

For Spec-Light:
    Create lightweight spec at ./docs/prd/{feature}-spec.md then implement

For Skip SDD:
    Proceed to implementation, document in ADRs as needed
```

### Implementation Notes

1. **State Transition**: This command transitions from "To Do" -> "Assessed"
2. **Artifact**: Produces `./docs/assess/{feature}-assessment.md`
3. **Validation Mode**: NONE (automatic transition)
4. **Override Support**: `--mode {full|light|skip}` flag bypasses scoring

### Error Handling

- If `./docs/assess/` directory doesn't exist, create it
- If feature name is ambiguous, ask for clarification
- If assessment already exists, ask whether to overwrite
- If override mode is invalid, show valid options

### Quality Checks

Before completing:
- [ ] Assessment report exists at correct path
- [ ] All scoring dimensions are documented
- [ ] Recommendation is clear and justified
- [ ] Next steps are specific and actionable
- [ ] Override instructions are provided

## Post-Completion: Emit Workflow Event

After successfully completing this command (assessment report generated), emit the workflow event:

```bash
flowspec hooks emit workflow.assessed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/assess/$FEATURE_ID-assessment.md
```

Replace `$FEATURE_ID` with the feature being assessed and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, workflow tracking).
