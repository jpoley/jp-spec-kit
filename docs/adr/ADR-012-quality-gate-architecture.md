# ADR-012: Quality Gate Architecture

**Status**: Accepted
**Date**: 2025-12-04
**Author**: Enterprise Software Architect (Kinsale Host)
**Context**: Tasks 083, 084 - Pre-Implementation Quality Gates and Spec Quality Metrics

---

## Context and Problem Statement

JP Spec Kit's `/jpspec:implement` command currently allows implementation to start regardless of spec quality. This leads to:

**Problems**:
- Implementations starting with incomplete specs (missing required sections)
- Unresolved NEEDS CLARIFICATION markers in specs
- Missing constitutional compliance checks
- No objective quality threshold enforcement
- Vague specs causing misaligned implementations
- Manual quality review bottleneck before implementation

**Current State**: ~30% of implementations discover spec gaps mid-work, causing rework and delays.

**Goal**: Design automated quality gates that enforce spec completeness and quality before `/jpspec:implement` can proceed, reducing mid-implementation spec gaps to <5%.

---

## Decision Drivers

1. **Fail Fast**: Catch spec quality issues before implementation starts
2. **Objective Metrics**: Replace subjective "looks good enough" with measurable thresholds
3. **Remediation Guidance**: Don't just block, tell developers exactly what to fix
4. **Override Capability**: Power users can skip gates when justified
5. **Constitutional Alignment**: Enforce constitutional requirements automatically
6. **Integration**: Gates run as pre-implement hook, zero manual invocation

---

## Considered Options

### Option 1: Manual Quality Review Gate
**Approach**: Human review required before implementation, reviewer signs off

**Pros**:
- High quality bar
- Human judgment handles edge cases
- Mentorship opportunity for junior developers

**Cons**:
- Bottleneck (single reviewer becomes blocker)
- Subjective criteria ("this looks fine to me")
- Slow feedback loop (hours to days)
- Doesn't scale with team growth

### Option 2: Automated Quality Metrics with Hard Threshold
**Approach**: Calculate quality score 0-100, block if below threshold (e.g., 70)

**Pros**:
- Instant feedback
- Objective criteria
- Scales infinitely
- No reviewer bottleneck

**Cons**:
- May block valid edge cases
- Score calculation complexity
- Risk of gaming metrics
- No human judgment in borderline cases

### Option 3: Hybrid Gates (Automated Checks + Manual Review Trigger)
**Approach**: Automated checks catch obvious issues, trigger human review for borderline cases

**Pros**:
- Fast path for high-quality specs (automated)
- Human review for edge cases only
- Best of both worlds
- Reduces reviewer burden 70%+

**Cons**:
- More complex implementation
- Need to define "borderline case" thresholds
- Still has potential bottleneck for borderline specs

---

## Decision Outcome

**Chosen Option**: **Option 2 with Override Escape Hatch**

Automated quality metrics with hard threshold (default 70/100), but allow override with `--skip-quality-gates` flag and justification logging.

### Rationale

- **95% of cases automated**: High-quality specs pass instantly, incomplete specs blocked immediately
- **Override for 5% edge cases**: Power users can bypass with justification
- **Audit trail**: Overrides logged for retrospective analysis
- **Iterative refinement**: Metrics can be tuned based on override patterns
- **No bottleneck**: Zero human intervention in normal flow

---

## Quality Gate Architecture

### Gate Execution Model

```
/jpspec:implement invoked
    ↓
Phase 0: Pre-Implementation Quality Gates (.claude/hooks/pre-implement.sh)
    ├─ Gate 1: Spec Completeness Check
    ├─ Gate 2: Required Files Validation
    ├─ Gate 3: Constitutional Compliance Check
    ├─ Gate 4: Spec Quality Threshold (70/100)
    └─ Gate 5: Unresolved Markers Check
    ↓
All gates passed OR --skip-quality-gates?
    ├─ NO: Block with remediation guidance → Exit 1
    └─ YES: Log approval + proceed to implementation
```

### Hook Integration

**Location**: `.claude/hooks/pre-implement.sh`

**Trigger**: Automatically invoked by `/jpspec:implement` command before agent execution

**Exit Codes**:
- `0`: All gates passed, proceed with implementation
- `1`: One or more gates failed, block implementation
- `2`: Configuration error (missing files, invalid setup)

**Override Mechanism**:
```bash
# Normal invocation (gates enforced)
/jpspec:implement --feature auth

# Override gates (with justification)
/jpspec:implement --feature auth --skip-quality-gates --reason "Spike/prototype work, spec intentionally light"
```

**Override Logging**:
```json
{
  "timestamp": "2025-12-04T10:30:00Z",
  "feature": "user-authentication",
  "user": "john.doe",
  "gates_skipped": ["spec_quality_threshold", "completeness"],
  "reason": "Spike/prototype work, spec intentionally light",
  "approved_by": "tech-lead"
}
```

---

## Gate Implementations

### Gate 1: Spec Completeness Check

**Purpose**: Verify all required spec sections are present and non-empty

**Required Sections** (varies by spec template):
- Problem Statement
- User Stories or Use Cases
- Acceptance Criteria
- Dependencies
- Out of Scope

**Algorithm**:
```bash
#!/bin/bash
# Gate 1: Spec Completeness Check

required_sections=(
  "## Problem Statement"
  "## User Stories"
  "## Acceptance Criteria"
  "## Dependencies"
  "## Out of Scope"
)

spec_file="memory/spec.md"

for section in "${required_sections[@]}"; do
  if ! grep -q "$section" "$spec_file"; then
    echo "❌ Missing required section: $section"
    exit 1
  fi

  # Check section is not empty (has content beyond just header)
  section_content=$(sed -n "/$section/,/^## /p" "$spec_file" | tail -n +2 | head -n -1)
  if [ -z "$(echo "$section_content" | tr -d '[:space:]')" ]; then
    echo "❌ Empty section: $section"
    exit 1
  fi
done

echo "✓ Spec completeness check passed"
```

**Remediation Guidance**:
```
❌ Gate 1 Failed: Spec Completeness

Missing or empty sections:
  - ## User Stories (missing)
  - ## Acceptance Criteria (empty)

Fix: Add missing sections to memory/spec.md

User Stories should include:
  - Actor (As a...)
  - Action (I want to...)
  - Outcome (So that...)

Acceptance Criteria should include:
  - Testable conditions (Given/When/Then or checklist)
  - Measurable outcomes (quantitative where possible)
```

---

### Gate 2: Required Files Validation

**Purpose**: Ensure necessary artifacts exist before implementation

**Required Files**:
- `memory/spec.md` - Feature specification
- `memory/plan.md` - Implementation plan (if /jpspec:plan ran)
- `memory/tasks.md` - Task breakdown (if /jpspec:specify ran)

**Algorithm**:
```bash
#!/bin/bash
# Gate 2: Required Files Validation

required_files=("memory/spec.md" "memory/plan.md" "memory/tasks.md")
missing_files=()

for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    missing_files+=("$file")
  elif [ ! -s "$file" ]; then  # File exists but empty
    missing_files+=("$file (empty)")
  fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
  echo "❌ Missing required files:"
  printf '  - %s\n' "${missing_files[@]}"
  exit 1
fi

echo "✓ Required files validation passed"
```

**Remediation Guidance**:
```
❌ Gate 2 Failed: Required Files Missing

Missing files:
  - memory/plan.md

Fix: Run /jpspec:plan to generate implementation plan before implementing

Command: /jpspec:plan --feature user-authentication

The plan.md file should include:
  - Architecture decisions
  - Technical approach
  - Risk mitigation strategies
```

---

### Gate 3: Constitutional Compliance Check

**Purpose**: Verify spec adheres to project constitution principles

**Checks**:
- Test-First approach documented (tests mentioned in plan)
- All tasks have acceptance criteria (if tasks.md exists)
- No direct commits to main planned (if Medium/Heavy tier)
- DCO sign-off mentioned in delivery section

**Algorithm**:
```bash
#!/bin/bash
# Gate 3: Constitutional Compliance Check

constitution="memory/constitution.md"
spec="memory/spec.md"
plan="memory/plan.md"
tasks="memory/tasks.md"

# Check Test-First principle
if ! grep -qi "test" "$plan"; then
  echo "❌ Test-First principle not addressed in plan"
  echo "   Add testing strategy to memory/plan.md"
  exit 1
fi

# Check tasks have acceptance criteria (if tasks exist)
if [ -f "$tasks" ]; then
  # Look for task sections without AC markers
  if grep -q "##.*Task" "$tasks" && ! grep -q "Acceptance Criteria" "$tasks"; then
    echo "❌ Tasks in tasks.md missing Acceptance Criteria"
    echo "   Every task must have at least one AC"
    exit 1
  fi
fi

# Check for NEEDS_VALIDATION markers in constitution
if grep -q "NEEDS_VALIDATION" "$constitution"; then
  echo "⚠️  Warning: Constitution has unvalidated sections"
  echo "   Run 'specify constitution validate' to review"
  # Warning only, don't block
fi

echo "✓ Constitutional compliance check passed"
```

**Remediation Guidance**:
```
❌ Gate 3 Failed: Constitutional Compliance

Issues found:
  1. Test-First principle not addressed
     Fix: Add testing strategy to memory/plan.md
     Example: "## Testing Approach
              - Unit tests for all business logic
              - Integration tests for API endpoints
              - E2E tests for critical user flows"

  2. Tasks missing acceptance criteria
     Fix: Add AC to each task in memory/tasks.md
     Example: "### AC
              - [ ] User can register with email/password
              - [ ] Confirmation email sent within 30 seconds"
```

---

### Gate 4: Spec Quality Threshold

**Purpose**: Enforce minimum quality score before implementation

**Quality Dimensions**:
1. **Completeness** (30 points): Required sections present and substantive
2. **Clarity** (25 points): Specific language, no vague terms, measurable criteria
3. **Traceability** (20 points): Clear linkage from user stories → plan → tasks
4. **Testability** (15 points): Acceptance criteria are verifiable
5. **Scoping** (10 points): Clear in-scope vs. out-of-scope boundaries

**Threshold**: 70/100 (configurable via `.specify/quality-config.json`)

**Algorithm**:
```python
#!/usr/bin/env python3
# Gate 4: Spec Quality Threshold

import re
import sys
from pathlib import Path

def score_completeness(spec_content):
    """Score based on section presence and length."""
    required_sections = [
        "Problem Statement",
        "User Stories",
        "Acceptance Criteria",
        "Dependencies",
        "Out of Scope"
    ]

    score = 0
    for section in required_sections:
        pattern = f"## {section}.*?(?=##|$)"
        match = re.search(pattern, spec_content, re.DOTALL)

        if match:
            content_length = len(match.group(0).strip())
            if content_length > 200:  # Substantive content
                score += 6
            elif content_length > 50:  # Minimal content
                score += 3
        # else: 0 points for missing section

    return score  # Max 30 points

def score_clarity(spec_content):
    """Score based on specificity and measurability."""
    vague_terms = ["should", "might", "possibly", "maybe", "approximately", "some", "various"]
    passive_voice_indicators = ["is done", "will be handled", "can be", "may be"]

    score = 25  # Start with max score

    # Deduct for vague terms (max -10)
    vague_count = sum(len(re.findall(rf'\b{term}\b', spec_content, re.IGNORECASE)) for term in vague_terms)
    score -= min(vague_count, 10)

    # Deduct for passive voice (max -5)
    passive_count = sum(len(re.findall(pattern, spec_content, re.IGNORECASE)) for pattern in passive_voice_indicators)
    score -= min(passive_count, 5)

    # Deduct for missing quantitative criteria (max -10)
    if not re.search(r'\d+\s*(ms|seconds|users|requests|%)', spec_content):
        score -= 10

    return max(score, 0)  # Floor at 0

def score_traceability(spec_content, plan_content, tasks_content):
    """Score based on linkage between spec, plan, and tasks."""
    score = 0

    # Extract user stories from spec
    stories = re.findall(r'- As a .+?, I want .+?(?=\n|$)', spec_content)

    if stories:
        score += 5  # User stories present

        # Check if stories referenced in plan
        for story in stories:
            story_key_terms = re.findall(r'\b\w{5,}\b', story)[:3]  # Extract key terms
            if any(term.lower() in plan_content.lower() for term in story_key_terms):
                score += 3  # Found reference
                break

        # Check if stories referenced in tasks
        for story in stories:
            story_key_terms = re.findall(r'\b\w{5,}\b', story)[:3]
            if any(term.lower() in tasks_content.lower() for term in story_key_terms):
                score += 3  # Found reference
                break

    # Check if plan references tasks
    task_ids = re.findall(r'task-\d+', tasks_content)
    if task_ids:
        score += 4  # Tasks exist
        if any(task_id in plan_content for task_id in task_ids):
            score += 5  # Plan references tasks

    return min(score, 20)  # Cap at 20

def score_testability(spec_content):
    """Score based on testability of acceptance criteria."""
    ac_section = re.search(r'## Acceptance Criteria.*?(?=##|$)', spec_content, re.DOTALL)

    if not ac_section:
        return 0

    ac_content = ac_section.group(0)
    score = 0

    # Given/When/Then format (high quality)
    if re.search(r'Given .+?When .+?Then', ac_content, re.DOTALL):
        score += 8

    # Checklist format with action verbs
    checklist_items = re.findall(r'- \[ \] \w+', ac_content)
    if checklist_items:
        score += len(checklist_items)  # 1 point per item

    # Measurable outcomes
    if re.search(r'\d+\s*(ms|seconds|%|users)', ac_content):
        score += 4

    return min(score, 15)  # Cap at 15

def score_scoping(spec_content):
    """Score based on clarity of scope boundaries."""
    score = 0

    # Out of Scope section present
    if re.search(r'## Out of Scope', spec_content):
        score += 5

        # Out of Scope has content
        oos_section = re.search(r'## Out of Scope.*?(?=##|$)', spec_content, re.DOTALL)
        if oos_section and len(oos_section.group(0).strip()) > 50:
            score += 5

    return score  # Max 10

def calculate_quality_score():
    spec_path = Path("memory/spec.md")
    plan_path = Path("memory/plan.md")
    tasks_path = Path("memory/tasks.md")

    spec_content = spec_path.read_text() if spec_path.exists() else ""
    plan_content = plan_path.read_text() if plan_path.exists() else ""
    tasks_content = tasks_path.read_text() if tasks_path.exists() else ""

    completeness = score_completeness(spec_content)
    clarity = score_clarity(spec_content)
    traceability = score_traceability(spec_content, plan_content, tasks_content)
    testability = score_testability(spec_content)
    scoping = score_scoping(spec_content)

    total = completeness + clarity + traceability + testability + scoping

    return {
        "total": total,
        "dimensions": {
            "completeness": completeness,
            "clarity": clarity,
            "traceability": traceability,
            "testability": testability,
            "scoping": scoping
        }
    }

if __name__ == "__main__":
    threshold = 70  # Configurable via .specify/quality-config.json

    result = calculate_quality_score()
    total_score = result["total"]

    print(f"\n📊 Spec Quality Score: {total_score}/100")
    print(f"   Threshold: {threshold}/100\n")

    print("Dimension Scores:")
    for dimension, score in result["dimensions"].items():
        max_scores = {"completeness": 30, "clarity": 25, "traceability": 20, "testability": 15, "scoping": 10}
        print(f"  {dimension.capitalize():15} {score:2}/{max_scores[dimension]:2}")

    if total_score >= threshold:
        print(f"\n✓ Quality threshold met ({total_score} >= {threshold})")
        sys.exit(0)
    else:
        print(f"\n❌ Quality threshold not met ({total_score} < {threshold})")
        print("\nRecommendations:")

        if result["dimensions"]["completeness"] < 20:
            print("  - Add more detail to required sections (aim for 200+ words each)")
        if result["dimensions"]["clarity"] < 15:
            print("  - Replace vague terms with specific language")
            print("  - Add quantitative criteria (e.g., '< 200ms response time')")
        if result["dimensions"]["traceability"] < 10:
            print("  - Ensure user stories are referenced in plan and tasks")
        if result["dimensions"]["testability"] < 8:
            print("  - Use Given/When/Then format for acceptance criteria")
        if result["dimensions"]["scoping"] < 5:
            print("  - Add or expand '## Out of Scope' section")

        sys.exit(1)
```

**Remediation Guidance**:
```
❌ Gate 4 Failed: Spec Quality Below Threshold

📊 Spec Quality Score: 58/100
   Threshold: 70/100

Dimension Scores:
  Completeness     18/30  ❌
  Clarity          14/25  ❌
  Traceability     12/20  ✓
  Testability       9/15  ✓
  Scoping           5/10  ✓

Recommendations:
  - Add more detail to required sections (aim for 200+ words each)
    Current: Problem Statement (85 words), User Stories (120 words)
    Expand with: specific examples, edge cases, failure scenarios

  - Replace vague terms with specific language
    Found: "should", "might", "approximately" (12 occurrences)
    Replace with: "must", "will", exact numbers

  - Add quantitative criteria
    Missing: response time SLAs, throughput targets, error rates
    Add: "API responds in <200ms for p95", "Supports 1000 concurrent users"

Run 'specify quality' for detailed analysis.
```

---

### Gate 5: Unresolved Markers Check

**Purpose**: Detect placeholder markers that indicate incomplete spec work

**Marker Types**:
- `NEEDS CLARIFICATION` - Question for product/stakeholders
- `TODO` - Incomplete section
- `TBD` - To be determined
- `XXX` - Needs attention
- `FIXME` - Requires correction

**Algorithm**:
```bash
#!/bin/bash
# Gate 5: Unresolved Markers Check

markers=("NEEDS CLARIFICATION" "TODO" "TBD" "XXX" "FIXME")
files=("memory/spec.md" "memory/plan.md" "memory/tasks.md")

found_markers=false

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    for marker in "${markers[@]}"; do
      if grep -n "$marker" "$file"; then
        found_markers=true
      fi
    done
  fi
done

if [ "$found_markers" = true ]; then
  echo "❌ Unresolved markers found"
  echo "   Resolve all markers before implementing"
  exit 1
fi

echo "✓ No unresolved markers"
```

**Remediation Guidance**:
```
❌ Gate 5 Failed: Unresolved Markers

Found in memory/spec.md:
  Line 45: NEEDS CLARIFICATION: Should we support OAuth or only email/password?
  Line 78: TODO: Add rate limiting requirements

Found in memory/plan.md:
  Line 23: TBD: Database choice (PostgreSQL vs. MongoDB)

Fix: Resolve all markers before implementing
  - NEEDS CLARIFICATION: Get answer from product team
  - TODO: Complete the section with required information
  - TBD: Make architectural decision and document in ADR
```

---

## Integration with `/jpspec:implement`

### Command Flow

**Before Quality Gates**:
```markdown
# .claude/commands/jpspec/implement.md

## Execution Instructions

Use the Task tool to launch frontend and backend engineers in parallel...
```

**After Quality Gates**:
```markdown
# .claude/commands/jpspec/implement.md

## Phase 0: Pre-Implementation Quality Gates

Before launching implementation agents, run quality gates:

```bash
# Check for skip-quality-gates flag
if [ "$SKIP_QUALITY_GATES" = "true" ]; then
    echo "⚠️  Quality gates skipped (--skip-quality-gates flag provided)"
    echo "   Reason: $SKIP_REASON"
    # Log override for audit trail
    specify gate log-skip --feature "$FEATURE" --reason "$SKIP_REASON"
else
    # Run quality gates via hook
    if ! .claude/hooks/pre-implement.sh; then
        echo "❌ Quality gates failed. Fix issues before implementing."
        echo "   Or use --skip-quality-gates --reason '...' to override"
        exit 1
    fi
    echo "✅ Quality gates passed - proceeding with implementation"
fi
```

## Phase 1: Implementation

[Rest of command...]
```

---

## `specify quality` Command (Standalone Analysis)

**Purpose**: Allow developers to check quality score without running `/jpspec:implement`

**Usage**:
```bash
# Full quality analysis with recommendations
specify quality

# JSON output for CI integration
specify quality --json

# Check specific dimension
specify quality --dimension clarity

# Show recommendations only (no score)
specify quality --recommendations
```

**Output Example**:
```
📊 Spec Quality Analysis

Overall Score: 78/100 ✓ (Threshold: 70/100)

┌─────────────────┬───────┬─────┬────────┐
│ Dimension       │ Score │ Max │ Status │
├─────────────────┼───────┼─────┼────────┤
│ Completeness    │ 24    │ 30  │ ✓      │
│ Clarity         │ 18    │ 25  │ ⚠️      │
│ Traceability    │ 16    │ 20  │ ✓      │
│ Testability     │ 12    │ 15  │ ✓      │
│ Scoping         │  8    │ 10  │ ✓      │
├─────────────────┼───────┼─────┼────────┤
│ TOTAL           │ 78    │ 100 │ ✓      │
└─────────────────┴───────┴─────┴────────┘

Recommendations:
  ⚠️  Clarity (18/25) - Improve specificity
     • Replace vague terms: "should" (3x), "might" (2x), "approximately" (1x)
     • Add quantitative SLAs (e.g., response time, throughput)

  ✓ Great work on completeness and traceability!

Implementation ready: YES
Run `/jpspec:implement` to proceed.
```

---

## Customizable Quality Configuration

**File**: `.specify/quality-config.json`

**Purpose**: Allow teams to customize quality thresholds and dimension weights

**Default Configuration**:
```json
{
  "version": "1.0",
  "threshold": 70,
  "dimensions": {
    "completeness": {
      "enabled": true,
      "weight": 30,
      "required_sections": [
        "Problem Statement",
        "User Stories",
        "Acceptance Criteria",
        "Dependencies",
        "Out of Scope"
      ],
      "min_section_length": 200
    },
    "clarity": {
      "enabled": true,
      "weight": 25,
      "vague_terms": ["should", "might", "possibly", "maybe", "approximately"],
      "require_quantitative": true,
      "max_passive_voice": 5
    },
    "traceability": {
      "enabled": true,
      "weight": 20,
      "require_story_to_plan_linkage": true,
      "require_plan_to_task_linkage": true
    },
    "testability": {
      "enabled": true,
      "weight": 15,
      "prefer_given_when_then": true,
      "require_measurable_outcomes": true
    },
    "scoping": {
      "enabled": true,
      "weight": 10,
      "require_out_of_scope": true,
      "min_out_of_scope_length": 50
    }
  },
  "gates": {
    "spec_completeness": true,
    "required_files": true,
    "constitutional_compliance": true,
    "quality_threshold": true,
    "unresolved_markers": true
  }
}
```

**Customization Examples**:

**Relaxed Thresholds (Prototypes)**:
```json
{
  "threshold": 50,
  "dimensions": {
    "completeness": { "weight": 40 },
    "traceability": { "enabled": false },
    "scoping": { "enabled": false }
  }
}
```

**Strict Thresholds (Production Systems)**:
```json
{
  "threshold": 85,
  "dimensions": {
    "clarity": { "weight": 30, "max_passive_voice": 2 },
    "testability": { "weight": 20, "require_measurable_outcomes": true }
  }
}
```

---

## Testing Strategy

### Unit Tests (Individual Gates)

```python
def test_spec_completeness_gate_passes():
    """Verify completeness gate passes with all required sections."""
    spec_content = """
    ## Problem Statement
    [200+ words of context]

    ## User Stories
    - As a user, I want to...
    [More stories]

    ## Acceptance Criteria
    - [ ] Criterion 1
    - [ ] Criterion 2

    ## Dependencies
    - External API X

    ## Out of Scope
    - Feature Y (deferred to v2)
    """

    result = run_gate("spec_completeness", spec_content)
    assert result.passed
    assert result.exit_code == 0

def test_quality_threshold_gate_blocks_low_score():
    """Verify quality gate blocks spec with score below 70."""
    spec_content = """
    ## Problem Statement
    We should build something.  # Vague, short

    ## User Stories
    Users might want this.  # Vague

    ## Acceptance Criteria
    It should work.  # Not testable
    """

    result = run_gate("quality_threshold", spec_content)
    assert not result.passed
    assert result.score < 70
    assert result.exit_code == 1
    assert "clarity" in result.recommendations
```

### Integration Tests (Full Gate Pipeline)

```python
def test_pre_implement_hook_blocks_incomplete_spec():
    """Verify pre-implement.sh blocks with incomplete spec."""
    # Create minimal spec (missing sections)
    create_spec("memory/spec.md", sections=["Problem Statement"])

    # Run pre-implement hook
    result = subprocess.run([".claude/hooks/pre-implement.sh"], capture_output=True)

    # Should block
    assert result.returncode == 1
    assert "Missing required section" in result.stderr

def test_pre_implement_hook_allows_override():
    """Verify --skip-quality-gates flag bypasses gates."""
    # Create low-quality spec
    create_spec("memory/spec.md", quality_score=45)

    # Run with override
    result = subprocess.run([
        "/jpspec:implement",
        "--feature", "auth",
        "--skip-quality-gates",
        "--reason", "Prototype spike"
    ], capture_output=True)

    # Should succeed with warning
    assert result.returncode == 0
    assert "Quality gates skipped" in result.stdout
    assert "Prototype spike" in result.stdout
```

### End-to-End Tests (Workflow Integration)

```python
def test_quality_improvement_workflow():
    """Verify developer can fix issues and pass gates."""
    # Start with low-quality spec
    create_spec("memory/spec.md", quality_score=55)

    # Run specify quality to get recommendations
    result = subprocess.run(["specify", "quality"], capture_output=True)
    assert "Replace vague terms" in result.stdout

    # Improve spec based on recommendations
    improve_spec("memory/spec.md", fixes=["add_quantitative_criteria", "remove_vague_terms"])

    # Re-run quality check
    result = subprocess.run(["specify", "quality"], capture_output=True)
    assert "78/100" in result.stdout  # Score improved

    # Gates should now pass
    result = subprocess.run([".claude/hooks/pre-implement.sh"], capture_output=True)
    assert result.returncode == 0
```

---

## Consequences

### Positive

- **Reduced Rework**: Catch spec gaps before implementation (target: <5% mid-implementation spec issues)
- **Objective Standards**: Replace "looks good" with measurable quality score
- **Instant Feedback**: Developers know immediately what to fix
- **Scalability**: No human reviewer bottleneck
- **Continuous Improvement**: Override patterns inform metric refinement
- **Constitutional Enforcement**: Automate compliance checks
- **Customizable**: Teams can tune thresholds for their context

### Negative

- **False Positives**: May block valid edge cases (mitigated by override)
- **Metric Gaming**: Developers might optimize for score vs. true quality
- **Maintenance**: Quality scoring logic needs tuning over time
- **Learning Curve**: Developers must understand quality dimensions
- **Initial Friction**: Teams may resist gates initially

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Gates too strict | Blocks legitimate work | Lower threshold to 60, analyze overrides quarterly |
| Developers abuse overrides | Gates become meaningless | Require approval for overrides, track override rates |
| Quality score doesn't correlate with outcome | Wrong proxy metric | A/B test: track implementation rework rate with/without gates |
| Custom configs diverge | Inconsistent quality across teams | Provide recommended configs per project type |
| Gate execution slow | Developer friction | Optimize scoring (target <5s for full analysis) |

---

## Future Enhancements

### Machine Learning-Based Scoring

Replace heuristic scoring with ML model trained on historical spec → outcome data:

```python
# Train on historical data: (spec features) → (implementation success)
model = train_spec_quality_model(
    features=["section_lengths", "vague_term_count", "ac_count", "traceability_score"],
    labels=["no_rework", "minor_rework", "major_rework"]
)

# Predict quality for new spec
quality_score = model.predict(extract_features("memory/spec.md"))
```

**Benefits**: Scores correlate better with actual implementation outcomes

**Challenge**: Requires 50+ labeled examples to train effectively

### LLM-Assisted Spec Improvement

Instead of just blocking, suggest specific improvements:

```
❌ Clarity score low (14/25)

Suggested improvements:
  Line 23: "The system should handle errors gracefully"
  → "The system must return HTTP 4xx/5xx with error details within 100ms"

  Line 45: "Users might want to filter results"
  → "Users can filter results by date range, status, and priority"
```

### Team-Specific Quality Profiles

Learn team quality patterns and customize scoring:

```json
{
  "team": "backend-team-alpha",
  "learned_preferences": {
    "prefers_detailed_arc": true,
    "avg_section_length": 350,
    "clarity_term_whitelist": ["should"] // Team uses "should" appropriately
  }
}
```

---

## References

- **Task-083**: Pre-Implementation Quality Gates
- **Task-084**: Spec Quality Metrics Command
- **Hohpe's Gregor "The Software Architect Elevator"**: Quality attributes as first-class architectural concerns
- **Google's Test-Certified Program**: Quality gates before release
- **DORA Metrics**: Lead time and change failure rate correlation

---

**Decision**: The automated quality gate architecture with override escape hatch provides objective, instant feedback on spec quality while preserving flexibility for edge cases, reducing mid-implementation rework to <5%.
