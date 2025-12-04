# Constitution Check

Before executing any /jpspec command, verify project constitutional compliance.

## Purpose

Ensures that projects define and validate their constitutional principles before executing workflow commands. This prevents running workflows without proper project-specific rules and constraints.

## Check Steps

### 1. Constitution Existence Check

```bash
# Check if constitution exists
if [ ! -f "memory/constitution.md" ]; then
  echo "WARNING: Constitution not found"
fi
```

**If missing**:
```text
⚠️ No constitution found at memory/constitution.md

The constitution defines project-specific rules, quality standards, and workflow constraints.

To create one:
  specify init --here

After creating, customize memory/constitution.md with your project's principles.
```

### 2. Validation Status Check

If constitution exists, check for unvalidated sections:

```bash
# Count NEEDS_VALIDATION markers
grep -c "NEEDS_VALIDATION" memory/constitution.md || echo "0"
```

**If unvalidated sections found**:
```text
⚠️ Constitution has X unvalidated sections

Unvalidated sections may contain placeholder or incomplete rules.

To validate:
  1. Review memory/constitution.md
  2. Replace [PLACEHOLDER] values with actual project rules
  3. Remove NEEDS_VALIDATION markers when complete

Alternatively:
  specify constitution validate  # Interactive validation
```

### 3. Tier Detection

Read the first 10 lines of the constitution to detect enforcement tier:

```bash
# Extract tier from constitution
head -10 memory/constitution.md | grep -oP '<!-- TIER: \K(Light|Medium|Heavy)' || echo "Medium"
```

**Tier behaviors**:

| Tier | Enforcement Level | Behavior |
|------|------------------|----------|
| **Light** | Warn only | Show warning, proceed automatically |
| **Medium** | Warn and confirm | Show warning, ask user to confirm |
| **Heavy** | Block until validated | Block execution until all sections validated |

### 4. Tier-Specific Enforcement

#### Light Tier (Default for Experiments)
```text
ℹ️ Constitution status: X unvalidated sections (Light tier)

Light tier - proceeding with workflow.

Consider validating before production use.
```

#### Medium Tier (Default)
```text
⚠️ Constitution status: X unvalidated sections (Medium tier)

Medium tier requires confirmation to proceed.

Continue with this workflow? [Y/n]
```

Wait for user response:
- `Y` or `Enter`: Proceed
- `n` or `N`: Abort

#### Heavy Tier (Production/Regulated)
```text
🛑 Constitution validation required (Heavy tier)

Heavy tier blocks workflow execution until all constitution sections are validated.

Current status: X unvalidated sections

To proceed:
  1. Review and validate memory/constitution.md
  2. Remove all NEEDS_VALIDATION markers
  3. Re-run this command

Or skip validation (NOT RECOMMENDED):
  /jpspec:<command> --skip-validation
```

**Do not proceed** unless:
- All sections are validated (no NEEDS_VALIDATION markers), OR
- User explicitly requests `--skip-validation`

### 5. Skip Validation Flag

If user provides `--skip-validation` flag:

```text
⚠️ SKIPPING CONSTITUTION VALIDATION

This bypasses constitutional checks. Use only in emergencies.

Proceeding with workflow...
```

Log the skip event and proceed.

## Implementation Template

Use this template in /jpspec commands:

```markdown
## Step 0.1: Constitution Check (REQUIRED)

@import .claude/skills/constitution-check.md

If constitution check fails and no --skip-validation flag:
  - STOP execution
  - Show appropriate error/warning based on tier
  - Provide remediation instructions

If check passes or --skip-validation provided:
  - Log check result
  - Proceed to workflow execution
```

## Error Messages Reference

### Missing Constitution
```text
⚠️ No constitution found at memory/constitution.md

The constitution defines project-specific rules, quality standards, and workflow constraints.

To create one:
  specify init --here

After creating, customize memory/constitution.md with your project's principles.

For help: docs/guides/constitution-guide.md
```

### Unvalidated Sections (Light)
```text
ℹ️ Constitution has 3 unvalidated sections (Light tier)

Unvalidated:
  - [PRINCIPLE_1_NAME] (line 6)
  - [SECTION_2_NAME] (line 954)
  - [GOVERNANCE_RULES] (line 969)

Light tier - proceeding with workflow.

To validate: Review memory/constitution.md and remove NEEDS_VALIDATION markers.
```

### Unvalidated Sections (Medium)
```text
⚠️ Constitution has 3 unvalidated sections (Medium tier)

Unvalidated:
  - [PRINCIPLE_1_NAME] (line 6)
  - [SECTION_2_NAME] (line 954)
  - [GOVERNANCE_RULES] (line 969)

Medium tier requires confirmation to proceed.

Continue? [Y/n]:
```

### Unvalidated Sections (Heavy)
```text
🛑 Constitution validation required (Heavy tier)

Unvalidated:
  - [PRINCIPLE_1_NAME] (line 6)
  - [SECTION_2_NAME] (line 954)
  - [GOVERNANCE_RULES] (line 969)

Heavy tier blocks execution until all sections are validated.

To proceed:
  1. Review memory/constitution.md
  2. Replace [PLACEHOLDER] with actual values
  3. Remove NEEDS_VALIDATION markers
  4. Re-run this command

Or skip validation (NOT RECOMMENDED):
  /jpspec:<command> --skip-validation
```

### Validation Skipped Warning
```text
⚠️ CONSTITUTION VALIDATION SKIPPED

--skip-validation flag provided. Bypassing constitutional checks.

This should only be used in emergencies. Consider validating after completion.

Proceeding with workflow...
```

## Detection Logic

```bash
# Full detection script (example)
CONSTITUTION="memory/constitution.md"

# Check existence
if [ ! -f "$CONSTITUTION" ]; then
  echo "ERROR: No constitution found"
  exit 1
fi

# Detect tier
TIER=$(head -10 "$CONSTITUTION" | grep -oP '<!-- TIER: \K(Light|Medium|Heavy)' || echo "Medium")

# Count unvalidated sections
UNVALIDATED=$(grep -c "NEEDS_VALIDATION" "$CONSTITUTION" || echo "0")

# Show status
echo "Constitution tier: $TIER"
echo "Unvalidated sections: $UNVALIDATED"

# Enforce based on tier
if [ "$UNVALIDATED" -gt 0 ]; then
  case "$TIER" in
    Light)
      echo "ℹ️ Proceeding (Light tier)"
      ;;
    Medium)
      echo "⚠️ Confirm to proceed (Medium tier)"
      read -p "Continue? [Y/n]: " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 1
      fi
      ;;
    Heavy)
      echo "🛑 Validation required (Heavy tier)"
      exit 1
      ;;
  esac
fi
```

## Integration Points

This skill is invoked by:
- `/jpspec:assess` - Before assessment begins
- `/jpspec:specify` - Before PRD creation
- `/jpspec:research` - Before research phase
- `/jpspec:plan` - Before architecture planning
- `/jpspec:implement` - Before code implementation
- `/jpspec:validate` - Before QA validation
- `/jpspec:operate` - Before deployment

**All /jpspec commands must check constitution before execution.**

## Related Documents

- `memory/constitution.md` - Project constitution template
- `docs/guides/constitution-guide.md` - Constitution authoring guide
- `docs/reference/tier-enforcement.md` - Tier enforcement details
